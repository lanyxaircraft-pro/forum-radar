import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import radar

class RedditSafeguards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();radar.DATA=Path(self.tmp.name);radar.init()
        self.w=radar.validate_watch(dict(name='Selected discussion',source='reddit',kind='thread',
          target='abc',content_allowed=True,access_allowed=True,ai_allowed=True,interval=30))
        self.e=dict(id='t1_xyz',thread='abc',author='FictionalAuthor',board='flying',
          title='DO NOT EXPORT TITLE',body='DO NOT EXPORT BODY',tags=[],url='https://www.reddit.com/r/flying/comments/abc/example/xyz/')
        with radar.db() as c:c.execute("INSERT INTO watches(id,config,state) VALUES('w',?,'active')",(json.dumps(self.w),))
    def tearDown(self):self.tmp.cleanup()
    def seed(self):
        radar.ingest('w',[self.e],'fixture')
        radar.ingest('w',[dict(self.e,id='t1_zzz')],'fixture')
    def listing(self,author='FictionalAuthor',body='DO NOT EXPORT BODY'):
        return json.dumps({'data':{'children':[{'data':dict(name=eid,author=author,body=body)} for eid in ('t1_xyz','t1_zzz')]}}).encode()
    def test_hourly_minimum(self):self.assertEqual(self.w['interval'],60)
    def test_broad_discovery_disabled_before_network(self):
        with patch('radar.request',side_effect=AssertionError('network')):
            for kind in ('user','board','tag'):
                with self.assertRaises(ValueError):radar.reddit(dict(self.w,kind=kind,board='flying'))
    def test_unlisted_subreddit_disabled_before_network(self):
        with patch('radar.request',side_effect=AssertionError('network')):
            with self.assertRaises(ValueError):radar.reddit(dict(self.w,board='unapprovedcommunity'))
    def test_ai_reddit_excluded_even_when_all_switches_on(self):
        s=radar.settings();s['ai']['enabled']=True;radar.save_settings(s)
        with patch('radar.request',side_effect=AssertionError('must not send')):
            self.assertEqual(radar.ai_summary([{'config':self.w,'event':self.e}]),'')
    def test_no_approval_never_opens_network(self):
        with patch.dict(os.environ,{},clear=True),patch('radar.ur.build_opener',side_effect=AssertionError('network')):
            with self.assertRaises(ValueError):radar.reddit(self.w)
    def test_digest_is_links_and_counts_only(self):
        self.seed()
        with patch('radar.reddit_headers',return_value={}),patch('radar.request',return_value=self.listing()):
            oid=radar.prepare_digest()
        self.assertTrue(oid);text=radar.state()['outbox'][0]['text']
        for v in ('DO NOT EXPORT TITLE','DO NOT EXPORT BODY','FictionalAuthor'):self.assertNotIn(v,text)
        self.assertIn('https://www.reddit.com/',text)
    def test_failed_revalidation_blocks_reddit_digest(self):
        self.seed()
        with patch('radar.reddit_headers',side_effect=ValueError('offline')):
            self.assertIsNone(radar.prepare_digest())
    def test_deleted_or_missing_item_purges_derived_data(self):
        self.seed()
        with patch('radar.reddit_headers',return_value={}),patch('radar.request',return_value=self.listing()):radar.prepare_digest()
        with patch('radar.reddit_headers',return_value={}),patch('radar.request',return_value=b'{"data":{"children":[]}}'):
            radar.refresh_reddit_deletions()
        with radar.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM events').fetchone()[0],0)
        self.assertEqual(radar.state()['outbox'][0]['state'],'cancelled')
        self.assertNotIn('https://www.reddit.com/',radar.state()['outbox'][0]['text'])
    def test_deleted_account_purges_author_reference(self):
        self.seed()
        with patch('radar.reddit_headers',return_value={}),patch('radar.request',return_value=self.listing(author='[deleted]')):
            radar.refresh_reddit_deletions()
        with radar.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM events').fetchone()[0],0)
    def test_unchanged_reads_do_not_extend_24h_ttl(self):
        radar.ingest('w',[self.e],'fixture')
        old=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=25)).isoformat()
        with radar.db() as c:c.execute('UPDATE events SET seen=?',(old,))
        radar.ingest('w',[self.e],'fixture');radar.purge_reddit_expired()
        with radar.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM events').fetchone()[0],0)
    def test_forbidden_response_stops_subsequent_requests(self):
        env={'RADAR_REDDIT_TOKEN':'fixture-token','RADAR_REDDIT_CONTACT':'FixtureAccount',
             'RADAR_REDDIT_APPROVAL_REF':'fixture-only-not-approval'}
        err=urllib.error.HTTPError('https://oauth.reddit.com/api/info',403,'Forbidden',{},None)
        with patch.dict(os.environ,env),patch('radar.ur.build_opener') as opener:
            opener.return_value.open.side_effect=err
            for _ in range(2):
                with self.assertRaises(ValueError):radar.request('https://oauth.reddit.com/api/info')
            self.assertEqual(opener.return_value.open.call_count,1)

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import radar

class RadarTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); radar.DATA=Path(self.temp.name); radar.init()
        self.w=radar.validate_watch(dict(name='机主在维修版',source='poa',kind='user',
          target='Alice',board='maintenance-bay.8',transport='import',keywords='overhaul',
          content_allowed=True,ai_allowed=False))
        self.e=dict(id='p1',thread='https://www.pilotsofamerica.com/community/threads/test.1/',
          author='Alice',board='maintenance-bay.8',title='Engine overhaul',body='Actual quote',
          tags=[],url='https://www.pilotsofamerica.com/community/threads/test.1/#post-1')
        self.add()
    def tearDown(self): self.temp.cleanup()
    def add(self):
        with radar.db() as c:
            c.execute("INSERT INTO watches(id,config,state) VALUES('w',?,'active')",(json.dumps(self.w),))
    def count(self):
        return radar.state()['pending']
    def ingest(self,e=None): return radar.ingest('w',e or [self.e],'test fixture')
    def delta(self):
        self.ingest(); e=dict(self.e,id='p2',body='New experience'); self.ingest([e])
    def lifecycle(self,state):
        h=object.__new__(radar.Handler); h.path='/api/lifecycle'; h.action({'id':'w','state':state})
    def test_author_board_and_keyword_are_conjunctive(self):
        self.assertTrue(radar.matches(self.w,self.e))
        for k,v in [('author','Bob'),('board','training.5'),('title','Unrelated')]:
            e=dict(self.e); e[k]=v
            self.assertFalse(radar.matches(self.w,e))
    def test_first_run_no_history_and_dedup(self):
        self.assertEqual(self.ingest(),0); self.assertEqual(self.ingest(),0)
        self.assertEqual(self.count(),0)
    def test_new_and_edited(self):
        self.delta(); self.assertEqual(self.count(),1)
        self.ingest([dict(self.e,body='Edited quote')]); self.assertEqual(self.count(),2)
    def test_pause_stops_ingest_and_resume_rebases(self):
        self.delta(); self.lifecycle('paused'); self.assertEqual(self.count(),0)
        self.ingest([dict(self.e,id='p3')]); self.assertEqual(self.count(),0)
        self.lifecycle('active'); self.ingest([dict(self.e,id='p4')]); self.assertEqual(self.count(),0)
    def test_stop_invalidates_prepared_digest(self):
        self.delta(); oid=radar.prepare_digest(); self.lifecycle('stopped')
        self.assertEqual(radar.state()['outbox'][0]['state'],'cancelled')
        self.assertEqual(self.count(),0)
        with self.assertRaises(ValueError): self.lifecycle('active')
    def test_expiration_invalidates_digest(self):
        self.delta(); radar.prepare_digest(); w=dict(self.w,expires='2000-01-01')
        with radar.db() as c: c.execute('UPDATE watches SET config=?',(json.dumps(w),))
        self.assertEqual(radar.state()['outbox'][0]['state'],'cancelled')
    def test_zero_cost_never_calls_ai(self):
        self.delta()
        with patch('radar.request',side_effect=AssertionError('network forbidden')):
            self.assertIsNotNone(radar.prepare_digest())
    def test_daily_budget_reserves_before_request(self):
        radar.use('fetch',1)
        with self.assertRaises(ValueError): radar.use('fetch',1)
    def test_daily_watch_cap_leaves_backlog(self):
        self.w['daily_limit']=1
        with radar.db() as c: c.execute('UPDATE watches SET config=?',(json.dumps(self.w),))
        self.delta(); self.ingest([dict(self.e,id='p3')])
        radar.prepare_digest(); self.assertEqual(self.count(),1)
        self.assertIsNone(radar.prepare_digest())
    def test_no_ai_for_nonconsenting_watch(self):
        s=radar.settings(); s['ai']['enabled']=True; radar.save_settings(s)
        with patch('radar.request',side_effect=AssertionError('network forbidden')):
            self.assertEqual(radar.ai_summary([{'config':self.w,'event':self.e}]),'')
    def test_unapproved_reddit_never_requests(self):
        with patch('radar.request',side_effect=AssertionError('network forbidden')):
            with self.assertRaises(ValueError): radar.reddit({'access_allowed':False})
    def test_tags_require_scope(self):
        with self.assertRaises(ValueError): radar.validate_watch(dict(self.w,kind='tag',board=''))
    def test_url_boundaries(self):
        for url in ['http://www.pilotsofamerica.com/','https://evil.test/feed','https://x:y@oauth.reddit.com/']:
            with self.assertRaises(ValueError): radar.validate_url(url)
    def test_plain_parser_omits_quote_and_signature(self):
        raw='''<h1>Overhaul</h1><a href="/community/forums/maintenance-bay.8/">Board</a>
        <article data-content="post-1" data-author="Alice"><div class="bbWrapper">Actual price
        <blockquote>Repeated quote</blockquote></div><div class="message-signature">Signature</div></article>'''
        es=radar.parse_xenforo(raw,self.e['thread'])
        self.assertEqual(es[0]['author'],'Alice'); self.assertNotIn('Repeated',es[0]['body'])
        self.assertNotIn('Signature',es[0]['body']); self.assertEqual(es[0]['board'],'maintenance-bay.8')
    def test_rss_does_not_invent_author(self):
        xml=b'<rss><channel><item><guid>1</guid><title>T</title><link>https://www.pilotsofamerica.com/a/</link></item></channel></rss>'
        es,_=radar.rss(self.w,xml); self.assertEqual(es[0]['author'],'')
        self.assertFalse(radar.matches(self.w,es[0]))
    def test_content_free_mode_does_not_retain_body(self):
        with radar.db() as c: c.execute('UPDATE watches SET config=?',(json.dumps(dict(self.w,content_allowed=False)),))
        self.ingest()
        with radar.db() as c: stored=json.loads(c.execute('SELECT payload FROM events').fetchone()[0])
        self.assertEqual(stored['body'],'')

if __name__=='__main__': unittest.main()

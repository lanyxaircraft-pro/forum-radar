import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
import urllib.request as ur
import urllib.error
from http.server import HTTPServer
import radar

class HttpFlow(unittest.TestCase):
    def test_selected_author_to_digest_and_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            radar.DATA=Path(tmp);radar.init()
            server=HTTPServer(('127.0.0.1',0),radar.Handler)
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                base=f'http://127.0.0.1:{server.server_port}'
                page=ur.urlopen(base).read().decode()
                token=re.search("const csrf='([^']+)'",page)[1]
                def post(path,data,auth=True):
                    headers={'Content-Type':'application/json'}
                    if auth:headers['X-Radar-Token']=token
                    return json.load(ur.urlopen(ur.Request(base+'/api/'+path,
                      data=json.dumps(data).encode(),headers=headers)))
                wid=post('watch',dict(name='Demo',source='poa',kind='user',target='Alice',
                  board='maintenance-bay.8',transport='import',content_allowed=True))['id']
                post('lifecycle',dict(id=wid,state='active'))
                a=json.loads((radar.ROOT/'docs/sample-baseline.json').read_text())
                b=json.loads((radar.ROOT/'docs/sample-update.json').read_text())
                self.assertEqual(post('import',dict(id=wid,events=a))['count'],0)
                self.assertEqual(post('import',dict(id=wid,events=b))['count'],1)
                self.assertTrue(post('digest',{})['id'])
                post('lifecycle',dict(id=wid,state='stopped'))
                s=json.load(ur.urlopen(base+'/api/state'))
                self.assertEqual(s['outbox'][0]['state'],'cancelled')
                with self.assertRaises(urllib.error.HTTPError) as caught:post('digest',{},False)
                self.assertEqual(caught.exception.code,403)
            finally:
                server.shutdown();server.server_close();worker.join()

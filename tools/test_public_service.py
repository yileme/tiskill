import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
P=Path(__file__).resolve().parents[1]/'skills/tis-public-service-english/scripts/public_service.py'
spec=importlib.util.spec_from_file_location('public_service',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PublicServiceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def test_spans(self):
  t=m.Table();t.feed('<table><tr><td rowspan="2">1</td><td colspan="2">x</td></tr><tr><td>y</td><td>z</td></tr></table>');self.assertEqual(t.rows,[['1','x','x'],['1','y','z']])
 def test_paths(self):
  for x in ['../escape','/absolute']:
   with self.assertRaises(ValueError):m.safe(self.root,x)
  (self.root/'link').symlink_to(self.root)
  with self.assertRaises(ValueError):m.safe(self.root,'link/a')
 def test_missing_registry(self):
  with self.assertRaisesRegex(ValueError,'missing_local_registry'):m.load_root(self.root/'absent')
 def test_exclusive(self):
  p=self.root/'out.json';m.exclusive(p,{'first':1})
  with self.assertRaises(FileExistsError):m.exclusive(p,{'second':2})
  self.assertEqual(json.loads(p.read_text()),{'first':1})
 def test_batch(self):
  row={'id':'a','source':'示例','domain':'教育','scenario':'门口','initialTranslation':'Example','notes':'test'}
  data={'rows':[row],'clientConditions':{'existingTermMap':{'示例':'Client Example'}}};out=m.batch(data)
  self.assertEqual(out['rowCount'],1);self.assertEqual(out['rows'][0]['input'],row);self.assertIsNone(out['rows'][0]['proposedTranslation']);self.assertIn('jurisdiction',out['rows'][0]['pendingConditions']);self.assertEqual(out['rows'][0]['clientConditions'],data['clientConditions'])
  with self.assertRaisesRegex(ValueError,'duplicate'):m.batch({'rows':[row,row]})
 def fixture(self):
  (self.root/'one').mkdir();(self.root/'one/full.md').write_text('Synthetic only')
  (self.root/'source-index.csv').write_text('part,domain,standard_id,sha256,md\n1,通则,SYNTHETIC,abc,one/full.md\n')
  data=[{'type':'table','page_idx':0,'table_body':'<table><tr><td>1</td><td>示例</td><td>Example</td></tr></table>','table_caption':['Synthetic A'],'bbox':[0,0,100,100]}]
  (self.root/'one/test_content_list.json').write_text(json.dumps(data));return m.extract(self.root)[0][0]
 def test_stale_review(self):
  row=self.fixture();review={k:row[k] for k in ['id','zh','en','source_sha256','content_sha256']};review.update(status='verified',reviewer='fixture',method='test',en='different')
  (self.root/'derived-public-service-v1').mkdir();(self.root/'derived-public-service-v1/row-reviews.json').write_text(json.dumps([review]))
  with self.assertRaisesRegex(ValueError,'stale review'):m.build(self.root,'bad')
 def test_build_search_provenance(self):
  row=self.fixture();preview=m.build(self.root,'preview');self.assertFalse((self.root/'public-service-index').exists());self.assertEqual(preview['verified'],0)
  m.build(self.root,'v1',True);self.assertEqual(m.search(self.root,'v1','示例','通则')['count'],0);self.assertEqual(m.search(self.root,'v1','示例','通则',True)['count'],1);self.assertEqual(m.search(self.root,'v1','示例','教育',True)['count'],0)
  review={k:row[k] for k in ['id','zh','en','source_sha256','content_sha256']};review.update(status='verified',reviewer='synthetic test',method='fixture assertion')
  (self.root/'derived-public-service-v1').mkdir();(self.root/'derived-public-service-v1/row-reviews.json').write_text(json.dumps([review]));m.build(self.root,'v2',True)
  result=m.search(self.root,'v2','示例','通则');self.assertEqual(result['verified_count'],1);self.assertEqual(result['matches'][0]['source_version'],2013)
  with self.assertRaises(FileExistsError):m.build(self.root,'v2',True)
  (self.root/'one/test_content_list.json').write_text('[]')
  with self.assertRaisesRegex(ValueError,'stale'):m.search(self.root,'v2','示例','通则')
if __name__=='__main__':unittest.main()

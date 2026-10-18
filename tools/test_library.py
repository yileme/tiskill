import json
from pathlib import Path
import tempfile
import unittest
from tools import library, legacy_evidence

CARD = dict(expression="fixture", context="test only", quotation="fixture quote", url="https://example.com/test", explanation="Not real evidence")

class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "vault"; self.root.mkdir()
        self.data = dict(CARD, type="evidence", title="测试", id="fixture")

    def test_confirmation_validation_and_collisions(self):
        with self.assertRaises(ValueError): library.save(self.root, self.data)
        for patch in [{"title":"../escape"}, {"id":"../escape"}, {"url":"javascript:alert(1)"}, {"url":"https://u:p@example.com"}, {"url":"https://example.com\n/x"}, {"verification":"text_read"}, {"date":"2026-99-99"}, {"snapshot":{}}, {"verification":[]}, {"type":[]}, {"url":123}, {"id":123}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError): library.save(self.root,{**self.data,**patch},True)
        p = library.save(self.root,self.data,True)
        self.assertTrue(p.name.endswith('_测试_V01.md'))
        with self.assertRaises(ValueError): library.save(self.root,self.data,True)
        q = library.save(self.root,{**self.data,"id":"other"},True)
        self.assertTrue(q.name.endswith('_测试_V02.md'))
        self.assertEqual(library.payload(p)["verification"],"unverified")
        checked = library.save(self.root,{**self.data,"id":"checked","verification":"text_read","userConfirmed":True},True)
        self.assertEqual(library.payload(checked)["verificationBy"],"user")

    def test_practice_snapshot_and_safe_folder(self):
        p=library.save(self.root,self.data,True)
        attempt=dict(type="practice",title="复盘",kind="retelling",response="Actual answer",selfReview="Self report",sourceId="fixture")
        q=library.save(self.root,attempt,True)
        self.assertEqual(library.payload(q)["snapshot"],library.payload(p))
        self.assertIn('[[01-查证记录/',q.read_text())
        with self.assertRaises(ValueError): library.save(self.root,{**attempt,"sourceId":"missing"},True)
        (self.root/'02-表达积累').symlink_to(self.root.parent,target_is_directory=True)
        with self.assertRaises(ValueError): library.save(self.root,{**self.data,"type":"expression","id":"bad"},True)

    def test_migration_all_rows_and_retry(self):
        old=self.root.parent/'old'
        card=legacy_evidence.save(old,CARD,'POST')['item']
        attempt=legacy_evidence.practice(old,dict(cardId=card['id'],expectedVersion=1,kind='recall',response='answer',selfReview='review'))['item']
        legacy_evidence.save(old,{**card,'expectedVersion':1,'expression':'edited'},'PATCH')
        other=legacy_evidence.save(old,CARD,'POST')['item']
        orphan=legacy_evidence.practice(old,dict(cardId=other['id'],expectedVersion=1,kind='transfer',response='orphan answer',selfReview='review'))['item']
        legacy_evidence.save(old,dict(id=other['id'],expectedVersion=1),'DELETE')
        db=old/'evidence.sqlite3'; before=db.read_bytes()
        result=library.migrate(self.root,db,self.root.parent/'backup',True)
        self.assertEqual((result['cards'],result['attempts'],result['saved']),(1,2,3))
        self.assertEqual(db.read_bytes(),before)
        self.assertTrue(Path(result['backup']).is_file())
        items=[v[1] for v in library.records(self.root).values()]
        practices=[x for x in items if x['type']=='practice']
        self.assertCountEqual([x['snapshot'] for x in practices],[attempt['snapshot'],orphan['snapshot']])
        for item in items:
            self.assertEqual(json.loads(item['legacyRow']['data'])['id'],item['legacyId'])
        retry=library.migrate(self.root,db,self.root.parent/'backup',True)
        self.assertEqual((retry['saved'],retry['skipped']),(0,3))

    def test_cli_config_save_and_confirmation(self):
        import subprocess, sys
        config=self.root.parent/'library.json'; config.write_text(json.dumps({"path":str(self.root)}))
        source=self.root.parent/'input.json'; source.write_text(json.dumps(self.data))
        command=[sys.executable,str(Path(library.__file__)),"--config",str(config),"save","--input",str(source)]
        refused=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(refused.returncode,2)
        saved=subprocess.run(command+["--confirm"],capture_output=True,text=True)
        self.assertEqual(saved.returncode,0,saved.stderr)
        self.assertTrue(Path(json.loads(saved.stdout)).exists())

    def test_empty_migration(self):
        old=self.root.parent/'empty'
        with legacy_evidence.database(old): pass
        result=library.migrate(self.root,old/'evidence.sqlite3',self.root.parent/'backup',True)
        self.assertEqual((result['cards'],result['attempts'],result['saved']),(0,0,0))
        self.assertEqual(library.records(self.root),{})

if __name__=='__main__': unittest.main()

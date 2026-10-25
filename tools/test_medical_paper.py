import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("medical_lookup", Path(__file__).resolve().parents[1]/"skills/tis-medical-paper/scripts/lookup.py")
lookup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lookup)

class LookupTests(unittest.TestCase):
    def test_mapping_and_candidate_status(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"manifest.json").write_text(json.dumps({"source_sha256":"synthetic", "edition":"11"}))
            (root/"p.txt").write_text("OR 0.72; 95% CI, 0.51–1.01; not statistically significant")
            (root/"page-map.json").write_text(json.dumps([{"physical_page":1005,"printed_page":982,"batch":"physical0901-1080","batch_page":105,"text_file":"p.txt"}]))
            result = lookup.search(root,"95% CI",1)["results"][0]
            self.assertEqual((result["physical_page"],result["printed_page"],result["batch_page"]),(1005,982,105))
            self.assertEqual(result["status"],"extraction_candidate")
            self.assertIn("OR 0.72",result["excerpt"])
            self.assertEqual(lookup.search(root,"unavailable")["status"],"no_match")
    def test_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for pointer in ("../secret","/tmp/secret"):
                with self.assertRaises(ValueError): lookup.inside(root,pointer)
            (root/"link").symlink_to("/tmp")
            with self.assertRaises(ValueError): lookup.inside(root,"link/file")
    def test_input_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            for query,limit in (("",3),("x",11),("x",0)):
                with self.assertRaises(ValueError): lookup.search(Path(d),query,limit)

if __name__ == "__main__": unittest.main()

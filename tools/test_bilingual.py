"""Offline regressions only; fixtures are not linguistic evidence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch
from tools import library

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/tis-usage-evidence/scripts/bilingual_queries.py"
spec = importlib.util.spec_from_file_location("bilingual_queries", SCRIPT)
queries = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queries)

class BilingualTest(unittest.TestCase):
    def test_encoded_queries_and_hosts(self):
        for phrase in ["人民当家作主", "law & order + 50% # / ?", "法", "café — 条件"]:
            for source, config in queries.SOURCES.items():
                with self.subTest(phrase=phrase, source=source):
                    result = queries.build(phrase, source)
                    self.assertEqual(result["status"], "not_requested")
                    for engine, host in [("google", "www.google.com"), ("bing", "www.bing.com")]:
                        url = urlsplit(result[engine])
                        self.assertEqual((url.scheme, url.hostname, url.fragment), ("https", host, ""))
                        self.assertEqual(parse_qs(url.query), {"q": ['site:' + config["host"] + ' "' + phrase + '"']})
                        self.assertNotIn(" ", result[engine])
                    self.assertEqual(parse_qs(urlsplit(result["linguee"]).query), {"query": [phrase]})
                    self.assertIn(urlsplit(result["site"]).hostname.removeprefix("www."), queries.HOSTS)

    def test_rejections_and_no_error_echo(self):
        for text in ["", " ", "x" * 501, 'a" OR site:evil.example', "secret\nquery", "secret\x00", "x\x7f"]:
            with self.assertRaises(ValueError): queries.build(text)
        with self.assertRaises(ValueError): queries.build("public", "evil.example")
        proc = subprocess.run([sys.executable, str(SCRIPT)], input="PRIVATE_FIXTURE\x00", text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("PRIVATE_FIXTURE", proc.stdout + proc.stderr)

    def test_offline_and_cli(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            self.assertEqual(queries.build("法")["status"], "not_requested")
        proc = subprocess.run([sys.executable, str(SCRIPT), "--source", "linguee"], input="法\n", text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), queries.build("法", "linguee"))

    def test_skell_fragment_and_cli(self):
        for phrase in ["status quo", "中文 café", "law & order + 50% # / ? = 😀"]:
            with patch("socket.socket", side_effect=AssertionError("network forbidden")):
                result = queries.build(phrase, "skell")
            url = urlsplit(result["skell"])
            self.assertEqual((url.scheme, url.netloc, url.query), ("https", "skell.sketchengine.eu", ""))
            self.assertEqual(parse_qs(url.fragment.split("?", 1)[1]),
                             {"f": ["concordance"], "lang": ["en"], "query": [phrase]})
            self.assertEqual(result["status"], "not_requested")
            self.assertNotIn("google", result)
            self.assertNotIn(" ", result["skell"])
            self.assertNotIn("+", result["skell"])
        proc = subprocess.run([sys.executable, str(SCRIPT), "--source", "skell"],
                              input="status quo\n", text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), queries.build("status quo", "skell"))
        for phrase in ["", "x" * 501, "x\x00", 'a"b']:
            with self.assertRaises(ValueError): queries.build(phrase, "skell")

    def test_actual_disposable_save_and_snapshot(self):
        pair = dict(sourceText="测试句。", targetText="A test sentence.", sourceLanguage="zh", targetLanguage="en",
                    translationDirection="unknown", directionBasis="Synthetic fixture only",
                    aggregator={"name":"Fixture aggregator", "url":"https://example.org/copy", "publishedAt":"2020-02-01"},
                    original={"publisher":"Fixture publisher", "sourceUrl":"https://example.org/original", "targetUrl":None,
                              "documentId":"fixture-1", "publishedAt":"2020-01-01", "sourceLine":"来源：测试（原样）。", "locator":"paragraph 1"},
                    originalVerification="unverified", reading={"aggregator":"not_requested", "original":"not_requested"},
                    alignment={"status":"unverified"}, applicability={"limitations":"Not real evidence"}, dedupeKey="fixture-1")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = dict(type="evidence", title="双语测试", id="pair", expression="test", context="Offline fixture",
                          quotation="测试句。 ↔ A test sentence.", url="https://example.org/copy", explanation="Not real evidence", bilingual=pair)
            with self.assertRaises(ValueError): library.save(root, record)
            path = library.save(root, record, True)
            self.assertTrue(path.is_file())
            stored = library.payload(path)
            self.assertEqual(stored["bilingual"], pair)
            self.assertEqual(stored["verification"], "unverified")
            self.assertIsNone(stored["verificationBy"])
            self.assertIn("来源：测试（原样）。", path.read_text())
            practice = library.save(root, dict(type="practice",title="复盘测试",kind="translation",response="Fixture response",
                                    selfReview="Fixture review",sourceId="pair"),True)
            self.assertEqual(library.payload(practice)["snapshot"], stored)
            # Reading metadata must not bypass the existing user-confirmation rule.
            with self.assertRaises(ValueError): library.save(root, {**record,"id":"bad","verification":"text_read"}, True)

if __name__ == "__main__": unittest.main()

"""Standalone resource store contract tests; no real user data is touched."""
from concurrent.futures import ThreadPoolExecutor
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cat import resources


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.term = dict(kind="terms", source="术语", target="term", sourceLocale="zh-CN", targetLocale="en")

    def add(self, payload=None, **kwargs):
        return resources.add_resource(self.directory, payload or self.term, **kwargs)

    def search(self, **kwargs):
        return resources.search_resources(self.directory, **{**dict(kind="terms", sourceLocale="zh-CN", targetLocale="en"), **kwargs})

    def tm(self, source="Hello world", target="你好", **overrides):
        segment = dict(id="1", version=2, source=source, target=target, status="confirmed")
        payload = dict(kind="tm", source=source, target=target, sourceLocale="en", targetLocale="zh-CN", segmentId="1", expectedVersion=2)
        payload.update(overrides)
        return payload, segment

    def test_empty_does_not_create_file(self):
        self.assertEqual(self.search()["items"], [])
        self.assertFalse((self.directory / "resources.json").exists())

    def test_persistence_and_idempotence(self):
        first = self.add()
        self.assertTrue(first["created"])
        self.assertEqual(first["item"], self.add()["item"])
        self.assertFalse(self.add()["created"])
        self.assertEqual(len(list(csv.DictReader(io.StringIO((self.directory / "terms.csv").read_text(encoding="utf-8-sig"))))), 1)
        self.assertEqual(self.search()["items"][0]["match"], "stored")

    def test_mandatory_fields_and_locales(self):
        for field in ("kind", "source", "target", "sourceLocale", "targetLocale"):
            for value in (None, "", "   ", 12):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.add({**self.term, field: value})
        with self.assertRaises(ValueError):
            self.add({**self.term, "sourceLocale": "zh_CN"})
        self.assertFalse((self.directory / "resources.json").exists())

    def test_term_substrings_and_language_isolation(self):
        self.add()
        self.assertEqual(self.search(query="本句包含术语")["total"], 1)
        self.assertEqual(self.search(query="TERM")["total"], 1)
        self.assertEqual(self.search(sourceLocale="ZH-cn")["total"], 1)
        self.assertEqual(self.search(sourceLocale="en", targetLocale="zh-CN")["total"], 0)
        self.assertEqual(self.search(targetLocale="en-US")["total"], 0)
        self.assertEqual(self.search(query="unrelated")["total"], 0)

    def test_tm_needs_authoritative_confirmation_and_exact_snapshot(self):
        payload, segment = self.tm()
        with self.assertRaises(ValueError):
            self.add({**payload, "status": "confirmed"})
        for changes in ({"status": "draft"}, {"version": 3}, {"id": "2"}, {"target": "changed"}, {"source": "changed"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.add(payload, segment={**segment, **changes})
        with self.assertRaises(ValueError):
            self.add({**payload, "expectedVersion": True}, segment=segment)
        self.assertTrue(self.add(payload, segment=segment)["created"])

    def test_exact_normalized_fuzzy_and_honest_empty_results(self):
        for source in ("Hello world", "Hello worlds", "zzzzz"):
            payload, segment = self.tm(source)
            self.add(payload, segment=segment)
        result = self.search(kind="tm", sourceLocale="en", targetLocale="zh-CN", query="  ＨＥＬＬＯ   WORLD ")
        self.assertEqual(result["metric"], "normalized-character-similarity")
        self.assertEqual([x["match"] for x in result["items"]], ["exact", "fuzzy"])
        self.assertEqual(result["items"][0]["similarity"], 1)
        self.assertLess(result["items"][1]["similarity"], 1)
        listed = self.search(kind="tm", sourceLocale="en", targetLocale="zh-CN")
        self.assertTrue(all(x["similarity"] is None and x["match"] == "stored" for x in listed["items"]))

    def test_limits_and_validation(self):
        for n in range(3):
            self.add({**self.term, "source": str(n)})
        result = self.search(limit=2)
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(result["items"]), 2)
        for limit in (0, 101, True, "2"):
            with self.assertRaises(ValueError):
                self.search(limit=limit)
        with self.assertRaises(ValueError):
            self.search(query=None)

    def test_corrupt_store_is_not_overwritten(self):
        path = self.directory / "resources.json"
        for content in ('broken', '{"version": 2, "items": []}', '{"version": 1, "items": [null]}'):
            path.write_text(content)
            with self.assertRaises(ValueError):
                self.add()
            self.assertEqual(path.read_text(), content)

    def test_failed_replace_keeps_original_and_cleans_temp(self):
        self.add()
        path = self.directory / "terms.csv"
        original = path.read_bytes()
        with patch.object(resources.os, "replace", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                self.add({**self.term, "target": "other"})
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(self.directory.glob(".resources-*")), [])

    def test_concurrent_writes_do_not_lose_entries(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda n: self.add({**self.term, "source": str(n)}), range(30)))
        self.assertEqual(self.search()["total"], 30)

    def test_migration_is_once_and_preserves_json(self):
        old = {"id": "old", **self.term, "createdAt": "2025-01-01T00:00:00Z"}
        path = self.directory / "resources.json"
        original = json.dumps({"version": 1, "items": [old]}).encode()
        path.write_bytes(original)
        item = self.search()["items"][0]
        self.assertEqual(item["id"], "old")
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue((self.directory / "tm.csv").read_bytes().startswith(b"\xef\xbb\xbf"))
        resources.update_resource(self.directory, {"id": "old", "target": "edited", "expectedVersion": 1})
        self.assertEqual(self.search()["items"][0]["target"], "edited")
        self.assertEqual(path.read_bytes(), original)

    def test_quotes_newlines_and_export_roundtrip(self):
        item = self.add({**self.term, "source": '术语,"quoted"\nnext', "target": 'term,"word"\nline'})["item"]
        body = resources.export_library(self.directory, "terms")
        self.assertTrue(body.startswith(b"\xef\xbb\xbf"))
        mounted = resources.mount_library(self.directory, {"name": "Round trip", "kind": "terms", "csvContent": body}, project="A")
        self.assertEqual(mounted["library"]["count"], 1)
        self.assertEqual(self.search(project="A")["items"][0]["source"], item["source"])
        self.assertEqual(resources.export_library(self.directory, mounted["library"]["id"], "A"), body)

    def test_edit_guard_and_pair_isolation(self):
        first = self.add()["item"]
        other = self.add({**self.term, "targetLocale": "fr", "target": "terme"})["item"]
        result = resources.update_resource(self.directory, {"id": first["id"], "target": "new", "expectedVersion": 1, "expectedUpdatedAt": first["updatedAt"]})["item"]
        self.assertEqual(result["version"], 2)
        for guard in ({"expectedVersion": 1}, {"expectedUpdatedAt": first["updatedAt"]}, {"expectedTarget": "term"}, {"expectedVersion": True}):
            with self.assertRaises(resources.ResourceConflict):
                resources.update_resource(self.directory, {"id": first["id"], "target": "stale", **guard})
        with self.assertRaises(ValueError):
            resources.update_resource(self.directory, {"id": first["id"], "target": "unguarded"})
        self.assertEqual(self.search(targetLocale="fr")["items"][0]["target"], other["target"])
        self.assertEqual(self.search()["items"][0]["target"], "new")

    def test_mounts_are_isolated_by_stable_project_id(self):
        self.add()
        payload = {"name": "Medical", "kind": "terms", "csvContent": "source,target,sourceLocale,targetLocale\r\n药,drug,zh-CN,en\r\n"}
        lib = resources.mount_library(self.directory, payload, {"id": "A", "title": "same"})["library"]
        self.assertEqual(self.search(project={"id": "A", "title": "renamed"})["total"], 2)
        self.assertEqual(self.search(project={"id": "B", "title": "same"})["total"], 1)
        self.assertEqual(self.search()["total"], 1)
        with self.assertRaises(ValueError):
            resources.export_library(self.directory, lib["id"], "B")
        with self.assertRaises(ValueError):
            self.add({**self.term, "libraryId": lib["id"]}, project="B")
        resources.mount_library(self.directory, {"libraryId": lib["id"]}, "B")
        resources.mount_library(self.directory, {"libraryId": "terms", "mounted": False}, "A")
        self.assertEqual(self.search(project="A")["total"], 1)
        self.assertEqual(self.search(project="B")["total"], 2)
        self.assertFalse(next(x for x in resources.list_libraries(self.directory, "A")["items"] if x["id"] == "terms")["mounted"])

    def test_malformed_external_csv_never_overwritten(self):
        self.add()
        path = self.directory / "terms.csv"
        for content in (b"wrong,headers\n", b"\xff", resources.export_library(self.directory, "terms") + b'"unfinished'):
            path.write_bytes(content)
            with self.assertRaises(ValueError):
                self.add({**self.term, "target": "other"})
            self.assertEqual(path.read_bytes(), content)

    def test_import_rejects_paths_and_bad_rows(self):
        for fields in ({"path": "/tmp/secret"}, {"csvContent": "source,target,sourceLocale,targetLocale\na,b,en\n"}, {"csvContent": "garbage"}):
            with self.assertRaises(ValueError):
                resources.mount_library(self.directory, {"name": "bad", "kind": "terms", **fields}, "A")
        self.assertFalse((self.directory / "libraries.json").exists())

    def test_migration_validates_both_files_before_writing(self):
        (self.directory / "resources.json").write_text(json.dumps({"version": 1, "items": [{"id": "old", **self.term, "createdAt": "then"}]}))
        (self.directory / "tm.csv").write_bytes(b"malformed")
        with self.assertRaises(ValueError):
            self.search()
        self.assertFalse((self.directory / "terms.csv").exists())
        self.assertEqual((self.directory / "tm.csv").read_bytes(), b"malformed")

    def test_failed_migration_retries_without_duplicates(self):
        (self.directory / "resources.json").write_text(json.dumps({"version": 1, "items": [{"id": "old", **self.term, "createdAt": "then"}]}))
        replace = resources.os.replace
        def fail_tm(source, target):
            if Path(target).name == "tm.csv":
                raise OSError("interruption")
            return replace(source, target)
        with patch.object(resources.os, "replace", side_effect=fail_tm):
            with self.assertRaises(OSError):
                self.search()
        self.assertEqual(self.search()["total"], 1)
        self.assertEqual(self.search()["total"], 1)


if __name__ == "__main__":
    unittest.main()

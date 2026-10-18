import json
from pathlib import Path
import tempfile
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase
from tools import legacy_evidence as evidence

CARD = dict(expression="take stock", context="Review a project", quotation="Time to take stock.",
            url="https://example.com/source", explanation="Review the situation; illustrative fixture, not researched evidence.",
            domain="work", register="neutral", timestamp="", verification="unverified")

class EvidenceTest(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def create(self, **extra):
        return evidence.save(self.root, {**CARD, **extra}, "POST")["item"]

    def test_crud_search_conflict_and_independence(self):
        sentinel = b"user project untouched"
        (self.root / "project.json").write_bytes(sentinel)
        item = self.create()
        self.assertEqual(evidence.cards(self.root, "STOCK")["items"], [item])
        self.assertEqual(evidence.cards(self.root, "missing")["items"], [])
        edit = {**item, "expectedVersion": 1, "expression": "updated"}
        saved = evidence.save(self.root, edit, "PATCH")["item"]
        self.assertEqual(saved["version"], 2)
        for method in ["PATCH", "DELETE"]:
            with self.assertRaises(evidence.Conflict): evidence.save(self.root, edit, method)
        evidence.save(self.root, {"id": item["id"], "expectedVersion": 2}, "DELETE")
        self.assertEqual(evidence.cards(self.root)["items"], [])
        self.assertEqual((self.root / "project.json").read_bytes(), sentinel)
        self.assertFalse((self.root / "terms.csv").exists())

    def test_url_validation_and_manual_confirmation(self):
        for url in ["javascript:alert(1)", "data:text/html,x", "//example.com", "file:///tmp/x", "https://", "https://user:pass@example.com", "https://example.com\n/evil", "https://example.com\\evil", "https://example.com:bad"]:
            with self.subTest(url=url), self.assertRaises(ValueError): self.create(url=url)
        for state in ["text_read", "audio_checked"]:
            with self.assertRaises(ValueError): self.create(verification=state)
            item = self.create(verification=state, userConfirmed=True)
            self.assertEqual(item["verificationBy"], "user")
            with self.assertRaises(ValueError): evidence.save(self.root, {**item, "expectedVersion":1, "quotation":"Changed"}, "PATCH")
        self.assertEqual(self.create()["verification"], "unverified")
        with self.assertRaises(ValueError): self.create(timestamp="invented")
        self.assertEqual(self.create(timestamp="01:12")["timestamp"], "01:12")

    def test_practice_snapshot_survives_edit_delete(self):
        item = self.create()
        for kind in evidence.KINDS:
            attempt = evidence.practice(self.root, dict(cardId=item["id"], expectedVersion=1, kind=kind, response="My answer", selfReview="Need context"))["item"]
            self.assertEqual(attempt["snapshot"], item)
            self.assertEqual(attempt["assessment"], "self")
            self.assertTrue(attempt["createdAt"])
        saved = evidence.save(self.root, {**item,"expectedVersion":1,"quotation":"New quote"}, "PATCH")["item"]
        with self.assertRaises(evidence.Conflict): evidence.practice(self.root, dict(cardId=item["id"],expectedVersion=1,kind="recall",response="x",selfReview="y"))
        evidence.save(self.root, {"id":item["id"],"expectedVersion":saved["version"]}, "DELETE")
        attempts = evidence.attempts(self.root, item["id"])["items"]
        self.assertEqual(len(attempts), 3)
        self.assertTrue(all(x["snapshot"] == item for x in attempts))

    def test_concurrent_edit_has_one_winner(self):
        item = self.create()
        def edit(value):
            try:
                evidence.save(self.root, {**item,"expectedVersion":1,"explanation":value}, "PATCH")
                return "saved"
            except evidence.Conflict:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(edit, ["first", "second"])), ["saved", "conflict"])

    def test_invalid_input_does_not_change_card(self):
        item = self.create()
        for patch in [{"expression":""},{"quotation":"x"*1201},{"verification":"verified"},{"timestamp":"99:99"}]:
            with self.assertRaises(ValueError): evidence.save(self.root,{**item,"expectedVersion":1,**patch},"PATCH")
        self.assertEqual(evidence.cards(self.root)["items"], [item])
        with self.assertRaises(ValueError): self.create(id=item["id"])

"""Regression tests for mistakes that would weaken catalogue quality."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from validate import validate_entries, valid_url, check_links, check_headline_counts


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads((Path(__file__).resolve().parents[1] / "data/treasures.json").read_text(encoding="utf-8"))

    def changed(self, **changes):
        entries = copy.deepcopy(self.entries)
        entries[0].update(changes)
        return validate_entries(entries)

    def test_accepts_catalogue(self):
        self.assertEqual(validate_entries(self.entries), [])

    def test_rejects_missing_evidence(self):
        self.assertTrue(self.changed(rights_evidence=""))

    def test_rejects_open_license_as_public_domain(self):
        self.assertTrue(self.changed(rights_status="CC BY"))

    def test_rejects_duplicate_ids(self):
        data = copy.deepcopy(self.entries)
        data[1]["id"] = data[0]["id"]
        self.assertTrue(any("duplicate id" in e for e in validate_entries(data)))

    def test_rejects_duplicate_record_fragments(self):
        data = copy.deepcopy(self.entries)
        data[1]["item_url"] = data[0]["item_url"] + "#view"
        self.assertTrue(any("duplicate item URL" in e for e in validate_entries(data)))

    def test_rejects_invalid_dates_and_categories(self):
        self.assertTrue(self.changed(date_verified="2026-02-30"))
        self.assertTrue(self.changed(category="Interesting things"))

    def test_malformed_category_types_fail_cleanly(self):
        for category in ([], {}, None, 42):
            with self.subTest(category=category):
                self.assertTrue(self.changed(category=category))

    def test_rejects_hyphenated_tags(self):
        self.assertTrue(self.changed(tags=["court-art"]))

    def test_headline_counts_must_match_data(self):
        readme = "**68 individually researched treasures in 12 categories**"
        self.assertEqual(check_headline_counts(readme, self.entries), [])
        self.assertTrue(check_headline_counts(readme.replace("68", "70"), self.entries))
        self.assertTrue(check_headline_counts("no count here", self.entries))

    def test_url_validation(self):
        for bad in ["http://example.org/a", "https://", "https://user:password@example.org", "https://example.org/a b", "https://example.org:bad"]:
            with self.subTest(url=bad):
                self.assertFalse(valid_url(bad))
        self.assertTrue(valid_url("https://example.org/record/42?view=json"))

    def test_relative_links_and_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Home\n\n[Good](other.md#chapter)\n", encoding="utf-8")
            (root / "other.md").write_text("# Chapter\n", encoding="utf-8")
            self.assertEqual(check_links(root), [])
            (root / "README.md").write_text("[Bad](other.md#missing)\n[Gone](gone.md)\n", encoding="utf-8")
            self.assertEqual(len(check_links(root)), 2)


if __name__ == "__main__":
    unittest.main()

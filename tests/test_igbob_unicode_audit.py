from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from builder.igbob_unicode_audit import (
    _classify_cluster,
    _clusters,
    _grapheme_is_allowed,
    generate_audit,
)


class IgboUnicodeAuditTests(unittest.TestCase):
    def test_raw_graphemes_are_kept_distinct_and_tone_letters_are_allowlisted(self):
        self.assertEqual(_clusters("b\u0355 a\u0304 ị ọ\u0301"), ["b\u0355", " ", "a\u0304", " ", "ị", " ", "ọ\u0301"])
        self.assertTrue(_grapheme_is_allowed("á"))
        self.assertTrue(_grapheme_is_allowed("ọ\u0301"))
        self.assertTrue(_grapheme_is_allowed("ǹ"))
        self.assertFalse(_grapheme_is_allowed("ē"))
        self.assertEqual(_classify_cluster("ē"), "MORPHOLOGICAL_ORTHOGRAPHY")
        self.assertEqual(_classify_cluster("b\u0355"), "SYSTEMATIC_CHARACTER_MAPPING")

    def test_audit_counts_marks_without_normalizing_or_editing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE verses (verse_id TEXT PRIMARY KEY, content TEXT NOT NULL)")
                db.executemany("INSERT INTO verses VALUES (?, ?)", [
                    ("gen-1-1", "b\u0355ara ē á ọ\u0301"),
                    ("exo-1-1", "B\u0355ara b\u0355ara n'anyị"),
                ])
            before = sqlite3.connect(source).execute("SELECT verse_id, content FROM verses ORDER BY verse_id").fetchall()
            report = generate_audit(source, root / "audit.json", root / "clusters.csv")
            after = sqlite3.connect(source).execute("SELECT verse_id, content FROM verses ORDER BY verse_id").fetchall()
            self.assertEqual(before, after)
            self.assertFalse(report["unicode_normalization_applied"])
            self.assertEqual(report["totals"]["marked_b_glyph_occurrences"], 3)
            self.assertEqual(report["totals"]["marked_b_affected_verses"], 2)
            self.assertEqual(report["totals"]["macron_automatic_replacements"], 0)
            self.assertNotIn("'", {row["character"] for row in report["embedded_nonstandard_punctuation"]})
            b_entry = next(row for row in report["combining_grapheme_inventory"] if row["sequence"] == "b\u0355")
            self.assertEqual((b_entry["occurrences"], b_entry["unique_words"], b_entry["affected_verses"]), (2, 1, 2))


if __name__ == "__main__":
    unittest.main()

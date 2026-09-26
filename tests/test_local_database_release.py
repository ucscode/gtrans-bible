from __future__ import annotations

import json
import sqlite3
import unittest
from pathlib import Path

from builder.android_database import validate_database_directory
from builder.data_paths import database_path, generated_path


EXPECTED_CONTENT_SHA256 = "11cc6bcbb330c2c1f3843cfc74d227c13dfd8f43d8de503f16fad0e02362ac89"


@unittest.skipUnless(
    database_path("bible.sqlite").is_file()
    and database_path("igbob.sqlite").is_file()
    and database_path("igbob-modern.sqlite").is_file(),
    "full local IGBOB corpus artifacts are not installed",
)
class LocalDatabaseReleaseTests(unittest.TestCase):
    def test_slim_modern_edition_matches_frozen_v0_5_content_and_external_audit(self):
        modern_path = database_path("igbob-modern.sqlite")
        source_path = database_path("igbob.sqlite")
        with sqlite3.connect(f"file:{modern_path.resolve()}?mode=ro", uri=True) as modern:
            self.assertEqual(modern.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(modern.execute("SELECT COUNT(*) FROM verses").fetchone()[0], 31103)
            self.assertEqual(
                {row[1] for row in modern.execute("PRAGMA table_info(verses)")},
                {"verse_id", "content"},
            )
            metadata = dict(modern.execute("SELECT key,value FROM metadata"))
            modern_text = dict(modern.execute("SELECT verse_id,content FROM verses"))
        with sqlite3.connect(f"file:{source_path.resolve()}?mode=ro", uri=True) as source:
            historical_text = dict(source.execute("SELECT verse_id,content FROM verses"))
        self.assertEqual(set(historical_text), set(modern_text))
        self.assertEqual(metadata["normalization_ruleset_version"], "0.5.0")
        self.assertEqual(metadata["transformation_count"], "51143")
        self.assertEqual(metadata["changed_verse_count"], "21832")
        self.assertEqual(metadata["unchanged_verse_count"], "9271")
        self.assertEqual(metadata["content_sha256"], EXPECTED_CONTENT_SHA256)

        audit_path = generated_path("igbob-normalization-audit-v0.5.0.json")
        residual_path = generated_path("igbob-residual-review-pack-v0.5.0.json")
        self.assertTrue(audit_path.is_file())
        self.assertTrue(residual_path.is_file())
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        audit_by_verse = {row["verse_id"]: row for row in audit["changed_verses"]}
        changed_ids = {ref for ref in modern_text if modern_text[ref] != historical_text[ref]}
        self.assertEqual(len(changed_ids), 21832)
        self.assertEqual(set(audit_by_verse), changed_ids)
        self.assertEqual(sum(len(row["transformations"]) for row in audit["changed_verses"]), 51143)
        self.assertEqual(audit["rebuild_validation"]["verse_ids_compared"], 31103)
        self.assertEqual(audit["rebuild_validation"]["missing_ids"], 0)
        self.assertEqual(audit["rebuild_validation"]["extra_ids"], 0)
        self.assertEqual(audit["rebuild_validation"]["content_differences"], 0)
        for verse_id in changed_ids:
            reconstructed = historical_text[verse_id]
            for item in sorted(audit_by_verse[verse_id]["transformations"], key=lambda item: item["start"], reverse=True):
                self.assertEqual(
                    reconstructed[item["start"]:item["end"]],
                    item["historical_form"],
                    verse_id,
                )
                reconstructed = (
                    reconstructed[:item["start"]]
                    + item["modern_form"]
                    + reconstructed[item["end"]:]
                )
                self.assertEqual(item["rule_version"], audit["rule_catalog"][item["rule_id"]]["version"])
            self.assertEqual(reconstructed, modern_text[verse_id], verse_id)
        self.assertTrue(audit["unresolved_forms_artifact"]["sha256"])
        self.assertEqual(validate_database_directory(modern_path.parent), [])


if __name__ == "__main__":
    unittest.main()

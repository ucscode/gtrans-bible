from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from builder.books import CANONICAL_BOOK_CODES, book_id
from builder.editions import build_edition_database, compare_edition_content, normalize_edition_database
from builder.mobobi_import import MOBOBI_BOOK_ASSETS, import_mobobi_apk, parse_mobobi_book
from builder.normalization import Normalizer


class MobobiImporterTests(unittest.TestCase):
    def test_utf16_markup_entities_and_historical_unicode_are_preserved(self) -> None:
        asset, _, _ = MOBOBI_BOOK_ASSETS["JDG"]
        text = "<p>NDI-IKPE 1</p><p>1 <strong>Ọ bụ</strong> b͕e aṅu-kwa-la nēme &amp; ọzọ.</p>"
        parsed = parse_mobobi_book(asset, b"\xff\xfe" + text.encode("utf-16-le"), "JDG")
        self.assertEqual(parsed.chapter_numbers, (1,))
        self.assertEqual(parsed.verses, {"jdg-1-1": "Ọ bụ b͕e aṅu-kwa-la nēme & ọzọ."})
        self.assertEqual(parsed.markup, {"p": 4, "strong": 2})
        self.assertEqual(parsed.entities, 1)

    def test_duplicate_and_missing_verse_markers_are_not_relabelled(self) -> None:
        asset, _, _ = MOBOBI_BOOK_ASSETS["JDG"]
        text = "<p>NDI-IKPE 1</p><p>1 First</p><p>1 Duplicate</p>"
        parsed = parse_mobobi_book(asset, text.encode("utf-16"), "JDG")
        self.assertEqual(list(parsed.verses), ["jdg-1-1"])
        self.assertEqual(parsed.duplicate_ids, ("jdg-1-1",))
        self.assertFalse(any(ref.endswith("-2") for ref in parsed.verses))

    def test_full_book_map_reports_gaps_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical = root / "bible.sqlite"
            with sqlite3.connect(canonical) as connection:
                connection.executescript("""
                    CREATE TABLE books(id TEXT PRIMARY KEY, position INTEGER NOT NULL);
                    CREATE TABLE chapters(id TEXT PRIMARY KEY, book_id TEXT NOT NULL, number INTEGER NOT NULL);
                    CREATE TABLE verses(id TEXT PRIMARY KEY, chapter_id TEXT NOT NULL, number INTEGER NOT NULL);
                """)
                for position, code in enumerate(CANONICAL_BOOK_CODES, 1):
                    bid = book_id(code)
                    connection.execute("INSERT INTO books VALUES (?,?)", (bid, position))
                    connection.execute("INSERT INTO chapters VALUES (?,?,1)", (f"{bid}-1", bid))
                    connection.execute("INSERT INTO verses VALUES (?,?,1)", (f"{bid}-1-1", f"{bid}-1"))
                    if code == "JDG":
                        connection.execute("INSERT INTO verses VALUES (?,?,2)", ("jdg-1-2", "jdg-1"))

            apk = root / "synthetic.apk"
            with ZipFile(apk, "w") as archive:
                for index, code in enumerate(CANONICAL_BOOK_CODES):
                    asset, heading, _ = MOBOBI_BOOK_ASSETS[code]
                    body = "duplicate witness" if code in {"2JN", "3JN"} else f"witness {chr(65 + index)}"
                    archive.writestr(asset, f"<p>{heading} 1</p><p>1 {body}</p>".encode("utf-16"))
            first_report = import_mobobi_apk(apk, canonical, root / "one.sqlite")
            second_report = import_mobobi_apk(apk, canonical, root / "two.sqlite")
            self.assertEqual(first_report, second_report)
            self.assertEqual(first_report["expected_books"], first_report["imported_books"])
            self.assertEqual(first_report["expected_books"], 66)
            self.assertEqual(first_report["missing_verse_ids"], ["3jn-1-1", "jdg-1-2"])
            self.assertEqual(first_report["quarantined_verses"], 1)
            self.assertTrue(str(first_report["coverage_status"]).startswith("incomplete"))
            with sqlite3.connect(root / "one.sqlite") as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0], 65)

    def test_duplicate_3_john_asset_is_quarantined_and_recovery_has_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical = root / "bible.sqlite"
            with sqlite3.connect(canonical) as connection:
                connection.executescript("""
                    CREATE TABLE books(id TEXT PRIMARY KEY, position INTEGER NOT NULL);
                    CREATE TABLE chapters(id TEXT PRIMARY KEY, book_id TEXT NOT NULL, number INTEGER NOT NULL);
                    CREATE TABLE verses(id TEXT PRIMARY KEY, chapter_id TEXT NOT NULL, number INTEGER NOT NULL);
                """)
                for position, code in enumerate(CANONICAL_BOOK_CODES, 1):
                    bid = book_id(code)
                    connection.execute("INSERT INTO books VALUES (?,?)", (bid, position))
                    connection.execute("INSERT INTO chapters VALUES (?,?,1)", (f"{bid}-1", bid))
                    connection.execute("INSERT INTO verses VALUES (?,?,1)", (f"{bid}-1-1", f"{bid}-1"))
            apk = root / "synthetic.apk"
            with ZipFile(apk, "w") as archive:
                for index, code in enumerate(CANONICAL_BOOK_CODES):
                    asset, heading, _ = MOBOBI_BOOK_ASSETS[code]
                    body = "same 2 John text" if code in {"2JN", "3JN"} else f"unique {chr(65 + index)} text"
                    archive.writestr(asset, f"<p>{heading} 1</p><p>1 {body}</p>".encode("utf-16"))
            recovery = root / "recovery.json"
            recovery.write_text('{"verses":{"3jn-1-1":{"text":"print recovered text","source_witness":"print"}}}', encoding="utf-8")
            report = import_mobobi_apk(apk, canonical, root / "recovered.sqlite", recovery_path=recovery)
            self.assertEqual(report["coverage_status"], "complete")
            self.assertEqual(report["quarantined_verses"], 1)
            self.assertEqual(report["recovered_verses"], 1)
            self.assertEqual(report["recovery_source_counts"], {"print": 1})
            with sqlite3.connect(root / "recovered.sqlite") as connection:
                self.assertEqual(connection.execute("SELECT content FROM verses WHERE verse_id='3jn-1-1'").fetchone()[0], "print recovered text")
                metadata = dict(connection.execute("SELECT key,value FROM metadata"))
            self.assertIn('"3jn-1-1": "print"', metadata["verse_source_provenance_json"])

    def test_modern_edition_carries_source_and_ruleset_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "igbob.sqlite"
            build_edition_database(source, {
                "id": "igbob", "source": "Mobobi IGBOB research transcription",
                "source_package": "com.mobobi.igbobible", "source_asset_sha256": "asset-hash",
                "distribution_status": "research/local only", "redistribution_rights": "unresolved",
            }, {"jdg": "Ndi-Ikpe"}, {"jdg-13-2": "tọb͕ọrọ"})
            modern = root / "igbob-modern.sqlite"
            baseline = root / "validated-0.5.0-modern.sqlite"
            with sqlite3.connect(baseline) as connection:
                connection.execute("CREATE TABLE verses(verse_id TEXT PRIMARY KEY, content TEXT NOT NULL)")
                connection.execute("INSERT INTO verses VALUES ('jdg-13-2','tọgbọrọ')")
            audit = root / "generated" / "igbob-normalization-audit-v0.5.0.json"
            unresolved = root / "generated" / "residual-review-pack.json"
            unresolved.parent.mkdir(parents=True)
            unresolved.write_text(json.dumps({
                "remaining_macron_summary": {
                    "codepoint_occurrences": 567,
                    "token_occurrences": 565,
                    "unique_forms": 201,
                    "affected_verses": 521,
                },
                "suspicious_symbols": {"occurrences": 430},
            }), encoding="utf-8")
            normalize_edition_database(source, modern, audit, unresolved)
            with sqlite3.connect(modern) as connection:
                metadata = dict(connection.execute("SELECT key,value FROM metadata"))
                verse_columns = {row[1] for row in connection.execute("PRAGMA table_info(verses)")}
            self.assertEqual(metadata["source_edition"], "igbob")
            self.assertEqual(metadata["source"], "Mobobi IGBOB research transcription")
            self.assertEqual(metadata["source_package"], "com.mobobi.igbobible")
            self.assertEqual(metadata["redistribution_rights"], "unresolved")
            self.assertEqual(metadata["normalization_ruleset_version"], Normalizer().ruleset_version)
            self.assertEqual(metadata["reviewed_lexicon_version"], Normalizer().lexicon_version)
            self.assertTrue(metadata["source_database_sha256"])
            self.assertEqual(verse_columns, {"verse_id", "content"})
            self.assertNotIn("original_content", verse_columns)
            equivalence = compare_edition_content(baseline, modern)
            self.assertEqual(equivalence["first_count"], 1)
            self.assertEqual(equivalence["missing_from_second"], [])
            self.assertEqual(equivalence["extra_in_second"], [])
            self.assertEqual(equivalence["content_differences"], [])
            audit_report = json.loads(audit.read_text(encoding="utf-8"))
            self.assertEqual(audit_report["release_version"], "0.5.0")
            self.assertEqual(audit_report["changed_verse_count"], 1)
            self.assertEqual(audit_report["transformation_count"], 1)
            transformation = audit_report["changed_verses"][0]["transformations"][0]
            self.assertEqual(transformation["rule_version"], "0.2.0")
            self.assertEqual(audit_report["unresolved_forms_artifact"]["macron_forms"], 201)


if __name__ == "__main__":
    unittest.main()

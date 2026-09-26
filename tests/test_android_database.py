from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from builder.android_database import (
    fetch_parallel_chapter,
    generate_database_manifest,
    validate_runtime_databases,
)


class AndroidDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paths = {
            "canonical": self.root / "bible.sqlite",
            "igbob": self.root / "igbob.sqlite",
            "igbob-modern": self.root / "igbob-modern.sqlite",
            "kjv": self.root / "kjv.sqlite",
        }
        self._create_canonical()
        self._create_edition(
            "igbob", "IGBOB research transcription", "ig", "source edition text", None,
            {"gen-1-1": "Akụkọ mbụ", "gen-1-2": "Akụkọ nke abụọ", "psa-1-1": "Abụ mbụ"},
        )
        self._create_edition(
            "igbob-modern", "Modernized IGBOB", "ig", "source edition text", "0.5.0",
            {"gen-1-1": "Akụkọ mbụ", "gen-1-2": "Akụkọ abụọ", "psa-1-1": "Abụ mbụ"}, modern=True,
        )
        self._create_edition(
            "kjv", "King James Version", "en", "eBible KJV source", None,
            {"gen-1-1": "In the beginning", "gen-1-2": "The earth", "psa-1-1": "Blessed"},
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _create_canonical(self) -> None:
        with sqlite3.connect(self.paths["canonical"]) as db:
            db.executescript(
                "CREATE TABLE books(id TEXT PRIMARY KEY, position INTEGER NOT NULL);"
                "CREATE TABLE chapters(id TEXT PRIMARY KEY, book_id TEXT NOT NULL, number INTEGER NOT NULL);"
                "CREATE TABLE verses(id TEXT PRIMARY KEY, chapter_id TEXT NOT NULL, number INTEGER NOT NULL);"
                "INSERT INTO books VALUES ('gen',1),('psa',2);"
                "INSERT INTO chapters VALUES ('gen-1','gen',1),('psa-1','psa',1);"
                "INSERT INTO verses VALUES ('gen-1-1','gen-1',1),('gen-1-2','gen-1',2),('psa-1-1','psa-1',1);"
            )

    def _create_edition(self, edition_id, name, language, source, version, verses, modern=False):
        with sqlite3.connect(self.paths[edition_id]) as db:
            db.executescript(
                "CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);"
                "CREATE TABLE books(book_id TEXT PRIMARY KEY,name TEXT NOT NULL);"
                "CREATE TABLE verses(verse_id TEXT PRIMARY KEY,content TEXT NOT NULL"+
                (",original_content TEXT NOT NULL,ruleset_version TEXT NOT NULL,lexicon_version TEXT NOT NULL,audit_json TEXT NOT NULL" if modern else "")+
                ");"
            )
            metadata = {"id": edition_id, "name": name, "language": language, "source": source}
            if version is not None:
                metadata["normalization_ruleset_version"] = version
                metadata["ruleset_version"] = version
                metadata["lexicon_version"] = version
            db.executemany("INSERT INTO metadata VALUES (?,?)", metadata.items())
            db.executemany("INSERT INTO books VALUES (?,?)", [("gen", "Jenesis"), ("psa", "Abụ Ọma")])
            if modern:
                originals = {
                    "gen-1-1": "Akụkọ mbụ",
                    "gen-1-2": "Akụkọ nke abụọ",
                    "psa-1-1": "Abụ mbụ",
                }
                db.executemany(
                    "INSERT INTO verses VALUES (?,?,?,?,?,?)",
                    [
                        (ref, text, originals[ref], version, version, "{}")
                        for ref, text in verses.items()
                    ],
                )
            else:
                db.executemany("INSERT INTO verses VALUES (?,?)", verses.items())

    def test_cross_database_ids_and_modern_historical_pairing(self):
        report = validate_runtime_databases(self.paths, require_full_canon=False)
        self.assertTrue(report["valid"])
        self.assertEqual(report["canonical_relationship_errors"], [])
        for edition in ("igbob", "igbob-modern", "kjv"):
            check = report["edition_consistency"][edition]
            self.assertEqual(check["missing_ids"], [])
            self.assertEqual(check["extra_ids"], [])
            self.assertEqual(check["duplicate_ids"], 0)
            self.assertEqual(check["mismatched_chapter_book_relationships"], 0)
        self.assertEqual(report["igbob_parallelism"]["changed_verses"], 1)
        self.assertEqual(report["igbob_parallelism"]["unchanged_verses"], 2)
        self.assertEqual(report["igbob_parallelism"]["missing_pairings"], [])
        self.assertTrue(report["kjv_complete"])

    def test_manifest_contains_edition_metadata_and_file_hashes(self):
        output = self.root / "out" / "manifest.json"
        manifest = generate_database_manifest(self.paths, output)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), manifest)
        self.assertEqual([row["edition_id"] for row in manifest["databases"]],
                         ["canonical", "igbob", "igbob-modern", "kjv"])
        entries = {row["edition_id"]: row for row in manifest["databases"]}
        self.assertIsNone(entries["canonical"]["language"])
        self.assertEqual(entries["canonical"]["verse_count"], 3)
        self.assertEqual(entries["igbob"]["language"], "ig")
        self.assertEqual(entries["igbob"]["version"], None)
        self.assertIsNone(entries["igbob"]["version_basis"])
        self.assertEqual(entries["igbob-modern"]["normalization_version"], "0.5.0")
        self.assertEqual(entries["igbob-modern"]["version_basis"], "normalization_ruleset_version")
        self.assertEqual(entries["igbob-modern"]["path"], "databases/igbob-modern.sqlite")
        self.assertEqual(entries["kjv"]["language"], "en")
        for edition, row in entries.items():
            self.assertEqual(row["sha256"], hashlib.sha256(self.paths[edition].read_bytes()).hexdigest())

    def test_parallel_chapter_query_pairs_all_text_by_canonical_verse_id(self):
        rows = fetch_parallel_chapter(self.paths, "gen", 1)
        self.assertEqual([row["verse_id"] for row in rows], ["gen-1-1", "gen-1-2"])
        self.assertEqual(rows[0]["historical_igbo"], "Akụkọ mbụ")
        self.assertEqual(rows[1]["modern_igbo"], "Akụkọ abụọ")
        self.assertEqual(rows[0]["kjv"], "In the beginning")

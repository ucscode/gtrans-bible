import sqlite3
import tempfile
import unittest
from pathlib import Path

from builder.database import build_databases, validate_oicb_database, validate_structure_database
from builder.usfm import ParseError
from builder.models import BibleData, Book, Chapter, Verse


class DatabaseTests(unittest.TestCase):
    def _data(self):
        return BibleData(
            books=(Book("tst", "Nnwale", 1),),
            chapters=(Chapter("tst-1", "tst", 1),),
            verses=(
                Verse("tst-1-1", "tst-1", 1, "Nke mbụ."),
                Verse("tst-1-2", "tst-1", 2, "Nke abụọ."),
            ),
            source_verse_count=2,
        )

    def test_sqlite_generation_foreign_keys_and_determinism(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first-bible.sqlite"
            first_oicb = Path(directory) / "first-oicb.sqlite"
            second = Path(directory) / "second-bible.sqlite"
            second_oicb = Path(directory) / "second-oicb.sqlite"
            data = self._data()
            build_databases(data, first, first_oicb, require_oicb=False)
            build_databases(data, second, second_oicb, require_oicb=False)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first_oicb.read_bytes(), second_oicb.read_bytes())
            with sqlite3.connect(first) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM books").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM pragma_table_info('books') WHERE name = 'name'").fetchone()[0], 0)
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(connection.execute("SELECT name FROM sqlite_master WHERE type = 'index' AND name = 'idx_verses_chapter_id'").fetchone()[0], "idx_verses_chapter_id")
            with sqlite3.connect(first_oicb) as connection:
                self.assertEqual(connection.execute("SELECT name FROM books WHERE book_id = 'tst'").fetchone()[0], "Nnwale")
                self.assertEqual(connection.execute("SELECT content FROM verses WHERE verse_id = 'tst-1-2'").fetchone()[0], "Nke abụọ.")
            validate_structure_database(first, data, require_oicb=False)
            validate_oicb_database(first_oicb, first, data, require_oicb=False)

    def test_attached_structure_edition_and_english_layers_join(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bible = root / "bible.sqlite"
            oicb = root / "oicb.sqlite"
            english = root / "english.sqlite"
            data = self._data()
            build_databases(data, bible, oicb, require_oicb=False)
            with sqlite3.connect(english) as connection:
                connection.execute("CREATE TABLE verses(verse_id TEXT PRIMARY KEY, content TEXT NOT NULL, source_sha256 TEXT NOT NULL)")
                connection.execute("INSERT INTO verses VALUES ('tst-1-1', 'English one', 'hash')")
            with sqlite3.connect(bible) as connection:
                connection.execute("ATTACH DATABASE ? AS oicb", (str(oicb),))
                connection.execute("ATTACH DATABASE ? AS english", (str(english),))
                row = connection.execute(
                    "SELECT v.id, v.number, o.content, e.content "
                    "FROM verses v "
                    "LEFT JOIN oicb.verses o ON o.verse_id = v.id "
                    "LEFT JOIN english.verses e ON e.verse_id = v.id "
                    "WHERE v.chapter_id = 'tst-1' ORDER BY v.number"
                ).fetchall()
                connection.execute("DETACH DATABASE english")
                connection.execute("DETACH DATABASE oicb")
            self.assertEqual([(item[0], item[1], item[2] is not None, item[3]) for item in row], [
                ("tst-1-1", 1, True, "English one"),
                ("tst-1-2", 2, True, None),
            ])

    def test_orphan_oicb_verse_fails_cross_database_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bible = root / "bible.sqlite"
            oicb = root / "oicb.sqlite"
            data = self._data()
            build_databases(data, bible, oicb, require_oicb=False)
            with sqlite3.connect(oicb) as connection:
                connection.execute("INSERT INTO verses VALUES ('unknown-1-1', 'orphan')")
            with self.assertRaises(ParseError):
                validate_oicb_database(oicb, bible, require_oicb=False)

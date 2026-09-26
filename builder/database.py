"""Build and validate the canonical Bible and OICB edition databases."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

from .models import BibleData
from .usfm import ParseError, validate_bible


STRUCTURE_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE books (
    id TEXT PRIMARY KEY,
    position INTEGER NOT NULL UNIQUE
);

CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id),
    UNIQUE(book_id, number)
);

CREATE TABLE verses (
    id TEXT PRIMARY KEY,
    chapter_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id),
    UNIQUE(chapter_id, number)
);

CREATE INDEX idx_chapters_book_id ON chapters(book_id);
CREATE INDEX idx_verses_chapter_id ON verses(chapter_id);
"""

OICB_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE books (
    book_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE verses (
    verse_id TEXT PRIMARY KEY,
    content TEXT NOT NULL
);
"""

OICB_METADATA = {
    "id": "oicb",
    "name": "Biblica Open Igbo Contemporary Bible 2020",
    "language": "ig",
    "source": "Biblica, Inc.; Open.Bible OICB 2020",
    "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
}


def _atomic_database(destination: Path, schema: str, populate) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w+b", delete=False, dir=destination.parent, prefix=f".{destination.name}.") as handle:
        temporary = Path(handle.name)
    try:
        connection = sqlite3.connect(temporary)
        try:
            connection.executescript(schema)
            populate(connection)
            connection.commit()
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise ParseError(f"SQLite integrity check failed: {integrity}")
            foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_errors:
                raise ParseError(f"SQLite foreign-key check failed: {foreign_key_errors}")
        finally:
            connection.close()
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _user_tables(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }


def _assert_columns(connection: sqlite3.Connection, table: str, expected: set[str]) -> None:
    actual = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    if actual != expected:
        raise ParseError(f"{table} columns {sorted(actual)} do not match expected {sorted(expected)}")


def build_structure_database(data: BibleData, destination: Path, require_oicb: bool = True) -> dict[str, int | str]:
    """Write only canonical IDs, positions, and relationships."""

    validate_bible(data, require_oicb=require_oicb)

    def populate(connection: sqlite3.Connection) -> None:
        connection.executemany("INSERT INTO books(id, position) VALUES (?, ?)", (
            (book.id, book.position) for book in data.books
        ))
        connection.executemany("INSERT INTO chapters(id, book_id, number) VALUES (?, ?, ?)", (
            (chapter.id, chapter.book_id, chapter.number) for chapter in data.chapters
        ))
        connection.executemany("INSERT INTO verses(id, chapter_id, number) VALUES (?, ?, ?)", (
            (verse.id, verse.chapter_id, verse.number) for verse in data.verses
        ))

    _atomic_database(destination, STRUCTURE_SCHEMA, populate)
    return {"books": len(data.books), "chapters": len(data.chapters), "verses": len(data.verses), "database": str(destination)}


def build_oicb_database(data: BibleData, destination: Path, require_oicb: bool = True) -> dict[str, int | str]:
    """Write only OICB metadata, Igbo book names, and verse content."""

    validate_bible(data, require_oicb=require_oicb)

    def populate(connection: sqlite3.Connection) -> None:
        connection.executemany("INSERT INTO metadata(key, value) VALUES (?, ?)", OICB_METADATA.items())
        connection.executemany("INSERT INTO books(book_id, name) VALUES (?, ?)", (
            (book.id, book.name) for book in data.books
        ))
        connection.executemany("INSERT INTO verses(verse_id, content) VALUES (?, ?)", (
            (verse.id, verse.content) for verse in data.verses
        ))

    _atomic_database(destination, OICB_SCHEMA, populate)
    return {"books": len(data.books), "chapters": len(data.chapters), "verses": len(data.verses), "database": str(destination)}


def validate_structure_database(path: Path, expected: BibleData | None = None, require_oicb: bool = True) -> None:
    if not path.exists():
        raise ParseError(f"canonical database not found: {path}")
    with sqlite3.connect(path) as connection:
        if _user_tables(connection) != {"books", "chapters", "verses"}:
            raise ParseError("bible.sqlite contains unexpected or missing user tables")
        _assert_columns(connection, "books", {"id", "position"})
        _assert_columns(connection, "chapters", {"id", "book_id", "number"})
        _assert_columns(connection, "verses", {"id", "chapter_id", "number"})
        connection.execute("PRAGMA foreign_keys = ON")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ParseError("bible.sqlite foreign-key check failed")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ParseError(f"bible.sqlite integrity check failed: {integrity}")
        counts = tuple(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("books", "chapters", "verses"))
        if expected is not None:
            actual_counts = (len(expected.books), len(expected.chapters), len(expected.verses))
            if counts != actual_counts:
                raise ParseError(f"bible.sqlite counts {counts} do not match parsed data {actual_counts}")
            expected_book_ids = tuple(book.id for book in expected.books)
            actual_book_ids = tuple(row[0] for row in connection.execute("SELECT id FROM books ORDER BY position"))
            if actual_book_ids != expected_book_ids:
                raise ParseError("bible.sqlite books do not match deterministic parsed order")
            expected_chapter_ids = {chapter.id for chapter in expected.chapters}
            actual_chapter_ids = {row[0] for row in connection.execute("SELECT id FROM chapters")}
            if actual_chapter_ids != expected_chapter_ids:
                raise ParseError("bible.sqlite chapter IDs do not match parsed data")
            expected_verse_ids = {verse.id for verse in expected.verses}
            actual_verse_ids = {row[0] for row in connection.execute("SELECT id FROM verses")}
            if actual_verse_ids != expected_verse_ids:
                raise ParseError("bible.sqlite verse IDs do not match parsed data")
        if require_oicb and counts != (66, 1189, 31103):
            raise ParseError(f"unexpected OICB-derived structure counts: {counts}")


def validate_oicb_database(path: Path, canonical_path: Path, expected: BibleData | None = None, require_oicb: bool = True) -> None:
    """Validate edition rows and cross-database ID integrity via ATTACH."""

    if not path.exists():
        raise ParseError(f"OICB database not found: {path}")
    if not canonical_path.exists():
        raise ParseError(f"canonical database not found: {canonical_path}")
    with sqlite3.connect(path) as connection:
        if _user_tables(connection) != {"metadata", "books", "verses"}:
            raise ParseError("oicb.sqlite contains unexpected or missing user tables")
        _assert_columns(connection, "metadata", {"key", "value"})
        _assert_columns(connection, "books", {"book_id", "name"})
        _assert_columns(connection, "verses", {"verse_id", "content"})
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        for key in ("id", "name", "language", "source", "license"):
            if not metadata.get(key):
                raise ParseError(f"oicb.sqlite metadata missing {key!r}")
        if require_oicb and metadata.get("id") != "oicb":
            raise ParseError("oicb.sqlite metadata ID is not oicb")
        if connection.execute("SELECT COUNT(*) FROM books WHERE NOT TRIM(name) = ''").fetchone()[0] != connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]:
            raise ParseError("oicb.sqlite contains an empty book name")
        if connection.execute("SELECT COUNT(*) FROM verses WHERE NOT TRIM(content) = ''").fetchone()[0] != connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0]:
            raise ParseError("oicb.sqlite contains empty verse content")
        connection.execute("ATTACH DATABASE ? AS canonical", (str(canonical_path.resolve()),))
        try:
            orphan_books = connection.execute(
                "SELECT b.book_id FROM books b LEFT JOIN canonical.books c ON c.id = b.book_id WHERE c.id IS NULL"
            ).fetchall()
            orphan_verses = connection.execute(
                "SELECT v.verse_id FROM verses v LEFT JOIN canonical.verses c ON c.id = v.verse_id WHERE c.id IS NULL"
            ).fetchall()
            if orphan_books:
                raise ParseError(f"oicb.sqlite has unknown canonical book IDs: {orphan_books[:5]}")
            if orphan_verses:
                raise ParseError(f"oicb.sqlite has unknown canonical verse IDs: {orphan_verses[:5]}")
            canonical_counts = tuple(connection.execute(f"SELECT COUNT(*) FROM canonical.{table}").fetchone()[0] for table in ("books", "chapters", "verses"))
            edition_counts = (
                connection.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0],
            )
            if edition_counts != (canonical_counts[0], canonical_counts[2]):
                raise ParseError(f"oicb.sqlite counts {edition_counts} do not match canonical IDs {canonical_counts}")
        finally:
            connection.execute("DETACH DATABASE canonical")
        if expected is not None:
            if tuple(row[0] for row in connection.execute("SELECT book_id FROM books ORDER BY rowid")) != tuple(book.id for book in expected.books):
                raise ParseError("oicb.sqlite book IDs do not match parsed OICB books")
            if {row[0] for row in connection.execute("SELECT verse_id FROM verses")} != {verse.id for verse in expected.verses}:
                raise ParseError("oicb.sqlite verse IDs do not match parsed OICB verses")
        connection.execute("PRAGMA foreign_keys = ON")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ParseError("oicb.sqlite foreign-key check failed")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ParseError(f"oicb.sqlite integrity check failed: {integrity}")


def build_databases(
    data: BibleData,
    canonical_destination: Path,
    oicb_destination: Path,
    require_oicb: bool = True,
) -> dict[str, int | str]:
    """Fan out one parsed OICB result into both corrected storage layers."""

    validate_bible(data, require_oicb=require_oicb)
    build_structure_database(data, canonical_destination, require_oicb=require_oicb)
    build_oicb_database(data, oicb_destination, require_oicb=require_oicb)
    validate_structure_database(canonical_destination, expected=data, require_oicb=require_oicb)
    validate_oicb_database(oicb_destination, canonical_destination, expected=data, require_oicb=require_oicb)
    return {
        "books": len(data.books),
        "chapters": len(data.chapters),
        "verses": len(data.verses),
        "bible_database": str(canonical_destination),
        "oicb_database": str(oicb_destination),
        "validation": "PASS",
    }

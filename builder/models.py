from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Book:
    id: str
    name: str
    position: int


@dataclass(frozen=True)
class Chapter:
    id: str
    book_id: str
    number: int


@dataclass(frozen=True)
class Verse:
    id: str
    chapter_id: str
    number: int
    content: str


@dataclass(frozen=True)
class ParsedBook:
    code: str
    book: Book
    chapters: tuple[Chapter, ...]
    verses: tuple[Verse, ...]
    source_path: Path | None = None
    source_verse_count: int = 0


@dataclass(frozen=True)
class BibleData:
    books: tuple[Book, ...]
    chapters: tuple[Chapter, ...]
    verses: tuple[Verse, ...]
    source_verse_count: int

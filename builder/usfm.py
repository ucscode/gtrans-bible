"""Small, source-driven USFM reader for the OICB release."""

from __future__ import annotations

import re
from pathlib import Path

from .books import CANONICAL_BOOK_CODES, CANONICAL_POSITION, book_id, chapter_id, verse_id
from .models import BibleData, Book, Chapter, ParsedBook, Verse


class ParseError(ValueError):
    """Raised when source USFM cannot be safely represented by the OICB schema."""


_LINE_MARKER = re.compile(r"^\\(?P<marker>[A-Za-z][A-Za-z0-9-]*)(?:\s+(?P<rest>.*))?$", re.DOTALL)
_VERSE_LINE = re.compile(r"^\\v\s+(?P<number>\S+)(?:\s+(?P<rest>.*))?$", re.DOTALL)
_INLINE_MARKER = re.compile(r"\\(?:\+)?(?P<name>[A-Za-z][A-Za-z0-9-]*)(?P<close>\*)?")

# These markers are structural or editorial metadata. Text following a
# heading/metadata marker must not be treated as Bible verse content.
_SKIP_LINE_MARKERS = {
    "id", "h", "toc1", "toc2", "toc3", "mt", "mt1", "mt2", "mt3",
    "mte", "ms", "ms1", "ms2", "ms3", "s", "s1", "s2", "s3", "r",
    "sr", "mr", "d", "sp", "cl", "iex", "ip", "im", "imi", "ili",
    "rem", "restore", "tr", "table", "th1", "th2", "th3", "th4",
}


def _marker_line(line: str) -> tuple[str, str] | None:
    match = _LINE_MARKER.match(line)
    if not match:
        return None
    return match.group("marker"), match.group("rest") or ""


def _clean_inline_text(raw: str) -> str:
    """Remove USFM controls while retaining readable inline text.

    Footnotes and cross-references are skipped as complete blocks, including
    their nested markers. Other inline markers (for example ``\\nd`` and
    ``\\wj``) are controls only, so their enclosed text remains.
    """

    result: list[str] = []
    index = 0
    while index < len(raw):
        if raw[index] != "\\":
            result.append(raw[index])
            index += 1
            continue

        marker = _INLINE_MARKER.match(raw, index)
        if marker is None:
            # A literal backslash is not expected in OICB, but retaining it
            # makes malformed input visible to validation instead of silently
            # deleting source text.
            result.append(raw[index])
            index += 1
            continue

        name = marker.group("name")
        is_close = marker.group("close") is not None
        index = marker.end()
        if not is_close and name in {"f", "x"}:
            close = re.search(rf"\\{re.escape(name)}\*", raw[index:])
            if close is None:
                raise ParseError(f"unterminated \\{name} note in verse content")
            index += close.end()

    # Marker removal can leave control-adjacent whitespace doubled. This is
    # structural whitespace cleanup only; Unicode code points are untouched.
    return re.sub(r"[ \t\r\n]+", " ", "".join(result)).strip()


def _parse_verse_number(token: str, source_name: str) -> int:
    if not token.isdigit() or int(token) < 1:
        raise ParseError(
            f"{source_name}: unsupported verse marker {token!r}; "
            "OICB's SQLite schema requires positive integer verse numbers"
        )
    return int(token)


def parse_book_text(text: str, source_name: str = "<memory>", source_path: Path | None = None) -> ParsedBook:
    """Parse one USFM book while preserving only readable verse content."""

    code: str | None = None
    name: str | None = None
    current_chapter: int | None = None
    current_verse_number: int | None = None
    current_parts: list[str] = []
    chapters: list[Chapter] = []
    verses: list[Verse] = []
    source_verse_count = 0

    def finish_verse() -> None:
        nonlocal current_verse_number, current_parts
        if current_verse_number is None:
            return
        if code is None or current_chapter is None:
            raise ParseError(f"{source_name}: verse appears before book/chapter metadata")
        content = _clean_inline_text(" ".join(current_parts))
        if not content:
            raise ParseError(f"{source_name}: verse {current_chapter}:{current_verse_number} is empty")
        chapter_ref = chapter_id(code, current_chapter)
        verses.append(Verse(
            id=verse_id(code, current_chapter, current_verse_number),
            chapter_id=chapter_ref,
            number=current_verse_number,
            content=content,
        ))
        current_verse_number = None
        current_parts = []

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.rstrip("\r")
        verse_match = _VERSE_LINE.match(line)
        if verse_match:
            finish_verse()
            if code is None or current_chapter is None:
                raise ParseError(f"{source_name}:{line_number}: verse appears before book/chapter metadata")
            current_verse_number = _parse_verse_number(verse_match.group("number"), source_name)
            source_verse_count += 1
            rest = verse_match.group("rest") or ""
            if rest:
                current_parts.append(rest)
            continue

        parsed_marker = _marker_line(line)
        if parsed_marker is not None:
            marker, rest = parsed_marker
            if marker == "id":
                header_code = rest.split(None, 1)[0] if rest else ""
                if not header_code:
                    raise ParseError(f"{source_name}:{line_number}: missing \\id code")
                if code is not None and code != header_code:
                    raise ParseError(f"{source_name}:{line_number}: multiple \\id codes")
                code = header_code
                continue
            if marker in {"toc1", "h"} and rest and name is None:
                name = rest
                continue
            if marker == "c":
                finish_verse()
                if not rest.split(None, 1)[0].isdigit():
                    raise ParseError(f"{source_name}:{line_number}: invalid chapter marker {rest!r}")
                current_chapter = int(rest.split(None, 1)[0])
                if code is None:
                    raise ParseError(f"{source_name}:{line_number}: chapter appears before \\id")
                chapters.append(Chapter(
                    id=chapter_id(code, current_chapter),
                    book_id=book_id(code),
                    number=current_chapter,
                ))
                continue
            if marker in _SKIP_LINE_MARKERS:
                # A heading ends the previous verse; later paragraph/list
                # markers can safely resume only once another \v is seen.
                finish_verse()
                continue
            # Paragraph, poetry, list, and break markers are structural. If
            # they carry text while a verse is active, that text is a
            # continuation of the current verse (as in EXO 1:4).
            if current_verse_number is not None and rest:
                current_parts.append(rest)
            continue

        if current_verse_number is not None and line.strip():
            # USFM permits a verse's readable text to continue on an ordinary
            # line, so retain it as a continuation.
            current_parts.append(line)

    finish_verse()
    if code is None:
        raise ParseError(f"{source_name}: no \\id marker")
    if name is None:
        raise ParseError(f"{source_name}: no \\toc1 or \\h book name")
    if not chapters:
        raise ParseError(f"{source_name}: no chapters")

    return ParsedBook(
        code=code,
        book=Book(id=book_id(code), name=name, position=CANONICAL_POSITION.get(code, 0)),
        chapters=tuple(chapters),
        verses=tuple(verses),
        source_path=source_path,
        source_verse_count=source_verse_count,
    )


def parse_book_file(path: Path) -> ParsedBook:
    return parse_book_text(path.read_text(encoding="utf-8-sig"), str(path), path)


def parse_source_directory(source_dir: Path) -> BibleData:
    """Parse the official OICB USFM directory in canonical order."""

    paths = sorted(source_dir.glob("*.usfm"))
    if not paths:
        raise ParseError(f"no .usfm files found in {source_dir}")

    parsed_by_code: dict[str, ParsedBook] = {}
    for path in paths:
        parsed = parse_book_file(path)
        if parsed.code in parsed_by_code:
            raise ParseError(f"duplicate book code {parsed.code} in {path}")
        parsed_by_code[parsed.code] = parsed

    expected = set(CANONICAL_BOOK_CODES)
    actual = set(parsed_by_code)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if unexpected:
            details.append(f"unexpected={unexpected}")
        raise ParseError("OICB book set mismatch: " + ", ".join(details))

    ordered = [parsed_by_code[code] for code in CANONICAL_BOOK_CODES]
    books = tuple(parsed.book for parsed in ordered)
    chapters = tuple(chapter for parsed in ordered for chapter in parsed.chapters)
    verses = tuple(verse for parsed in ordered for verse in parsed.verses)
    return BibleData(
        books=books,
        chapters=chapters,
        verses=verses,
        source_verse_count=sum(parsed.source_verse_count for parsed in ordered),
    )


def validate_bible(data: BibleData, require_oicb: bool = True) -> None:
    """Validate referential, structural, and content invariants."""

    if require_oicb and tuple(book.id.upper() for book in data.books) != tuple(code.lower().upper() for code in CANONICAL_BOOK_CODES):
        raise ParseError("books are not in the expected deterministic OICB order")
    if len({book.id for book in data.books}) != len(data.books):
        raise ParseError("book IDs are not unique")
    book_ids = {book.id for book in data.books}
    chapter_ids: set[str] = set()
    chapter_pairs: set[tuple[str, int]] = set()
    for chapter in data.chapters:
        if chapter.book_id not in book_ids:
            raise ParseError(f"chapter {chapter.id} references unknown book {chapter.book_id}")
        if chapter.id in chapter_ids:
            raise ParseError(f"duplicate chapter ID {chapter.id}")
        pair = (chapter.book_id, chapter.number)
        if pair in chapter_pairs:
            raise ParseError(f"duplicate book/chapter relationship {pair}")
        chapter_ids.add(chapter.id)
        chapter_pairs.add(pair)

    verse_ids: set[str] = set()
    verse_pairs: set[tuple[str, int]] = set()
    for verse in data.verses:
        if verse.chapter_id not in chapter_ids:
            raise ParseError(f"verse {verse.id} references unknown chapter {verse.chapter_id}")
        if verse.id in verse_ids:
            raise ParseError(f"duplicate verse ID {verse.id}")
        pair = (verse.chapter_id, verse.number)
        if pair in verse_pairs:
            raise ParseError(f"duplicate chapter/verse relationship {pair}")
        if not verse.content.strip():
            raise ParseError(f"empty verse content: {verse.id}")
        if re.search(r"\\[A-Za-z+]", verse.content):
            raise ParseError(f"USFM control markup remains in {verse.id}")
        verse_ids.add(verse.id)
        verse_pairs.add(pair)

    if data.source_verse_count != len(data.verses):
        raise ParseError(
            f"source verse markers ({data.source_verse_count}) do not reconcile "
            f"with generated verses ({len(data.verses)})"
        )

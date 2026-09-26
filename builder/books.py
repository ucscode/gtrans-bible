"""The OICB canonical book order and reference helpers."""

from __future__ import annotations


# OICB is a 66-book Protestant Bible. The source archive is alphabetically
# named, so this explicit order is what makes positions deterministic.
CANONICAL_BOOK_CODES: tuple[str, ...] = (
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT",
    "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH",
    "EST", "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER",
    "LAM", "EZK", "DAN", "HOS", "JOL", "AMO", "OBA", "JON",
    "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL", "MAT",
    "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL",
    "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT",
    "PHM", "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN",
    "JUD", "REV",
)

CANONICAL_POSITION = {code: position for position, code in enumerate(CANONICAL_BOOK_CODES, 1)}


def book_id(code: str) -> str:
    """Return the stable human-readable book ID used by SQLite."""

    return code.lower()


def chapter_id(code: str, chapter_number: int) -> str:
    return f"{book_id(code)}-{chapter_number}"


def verse_id(code: str, chapter_number: int, verse_number: int) -> str:
    return f"{chapter_id(code, chapter_number)}-{verse_number}"

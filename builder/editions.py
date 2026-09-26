"""Import development editions without changing canonical Bible structure.

The IGBOB source is an IA scan with OCR, so this importer keeps the raw IA
files as its source of record and exposes page/word confidence for review.
It does not repair OCR or infer missing Igbo diacritics.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from .books import CANONICAL_BOOK_CODES, book_id
from .database import _atomic_database
from .normalization import Normalizer, NormalizationResult
from .usfm import ParseError, parse_book_text


EDITION_SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE books (book_id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE verses (verse_id TEXT PRIMARY KEY, content TEXT NOT NULL);
"""

MODERN_SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE books (book_id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE verses (verse_id TEXT PRIMARY KEY, content TEXT NOT NULL);
"""

METADATA = {
    "igbob": {
        "id": "igbob", "name": "IGBOB (IA scanned-print OCR)", "language": "ig",
        "source_url": "https://archive.org/details/igbo-bible-print",
        "source_status": "development source; redistribution rights not established",
    },
    "kjv": {
        "id": "kjv", "name": "King James Version (eBible USFM)", "language": "en",
        "source_url": "https://ebible.org/bible/details.php?id=eng-kjv2006",
        "license": "Public domain (source statement)",
    },
}

_RANGE = re.compile(r"(?<!\d)(\d{1,3})\s*\.\s*(\d{1,3})\s*[-—–]{1,2}\s*(?:(\d{1,3})\s*\.\s*)?(\d{1,3})(?!\d)")
_SINGLE_REF = re.compile(r"(?<!\d)(\d{1,3})\s*\.\s*(\d{1,3})(?!\d)")
_DIGIT = re.compile(r"^\d{1,3}[.,;:]?$")


@dataclass(frozen=True)
class OCRWord:
    text: str
    page: str
    height: int
    confidence: int | None
    line: int
    is_header: bool = False


@dataclass(frozen=True)
class ImportedVerse:
    verse_id: str
    content: str
    page_start: str
    page_end: str
    minimum_ocr_confidence: int | None


@dataclass(frozen=True)
class IgboParseReport:
    verses: tuple[ImportedVerse, ...]
    page_count: int
    page_reference_headers: int
    missing_reference_ids: tuple[str, ...]
    duplicate_reference_ids: tuple[str, ...]
    unanchored_pages: tuple[str, ...]
    low_confidence_words: int
    scanned_word_count: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _content_sha256(verses: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for verse_id, content in sorted(verses.items()):
        ref_bytes = verse_id.encode("utf-8")
        content_bytes = content.encode("utf-8")
        digest.update(len(ref_bytes).to_bytes(8, "big"))
        digest.update(ref_bytes)
        digest.update(len(content_bytes).to_bytes(8, "big"))
        digest.update(content_bytes)
    return digest.hexdigest()


def _write_json_atomic(destination: Path, data: dict[str, object]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=destination.parent,
        prefix=f".{destination.name}.",
    ) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, destination)


def _normalization_audit_report(
    normalized: dict[str, NormalizationResult],
    *,
    release_version: str,
    source_database_sha256: str,
    source_edition: str,
    content_sha256: str,
    normalizer: Normalizer,
    unresolved_forms_path: Path | None,
) -> dict[str, object]:
    changed: list[dict[str, object]] = []
    unresolved_by_verse: list[dict[str, object]] = []
    transformation_count = 0
    used_rule_ids: set[str] = set()
    for verse_id, result in sorted(normalized.items()):
        if result.normalized_text != result.original_text:
            transformations = [
                {
                    "rule_id": item.rule_id,
                    "rule_version": item.version,
                    "category": item.category,
                    "historical_form": item.original,
                    "modern_form": item.replacement,
                    "start": item.start,
                    "end": item.end,
                }
                for item in result.transformations
            ]
            used_rule_ids.update(item["rule_id"] for item in transformations)
            transformation_count += len(transformations)
            changed.append({
                "verse_id": verse_id,
                "transformations": transformations,
            })
        review = [
            {"kind": "review", **item.__dict__} for item in result.review_items
        ] + [
            {"kind": "unknown", **item.__dict__} for item in result.unknown_items
        ] + [
            {"kind": "integrity", **item.__dict__} for item in result.integrity_issues
        ]
        if review:
            unresolved_by_verse.append({"verse_id": verse_id, "items": review})

    unresolved_artifact = None
    if unresolved_forms_path is not None and unresolved_forms_path.is_file():
        unresolved_json = json.loads(unresolved_forms_path.read_text(encoding="utf-8"))
        summary = unresolved_json.get("remaining_macron_summary", {})
        unresolved_artifact = {
            "path": str(unresolved_forms_path),
            "sha256": sha256_file(unresolved_forms_path),
            "macron_codepoints": summary.get("codepoint_occurrences"),
            "macron_token_occurrences": summary.get("token_occurrences"),
            "macron_forms": summary.get("unique_forms"),
            "macron_affected_verses": summary.get("affected_verses"),
            "suspicious_symbol_occurrences": unresolved_json.get("suspicious_symbols", {}).get("occurrences"),
        }
    return {
        "artifact_type": "igbob-normalization-transformation-audit",
        "release_version": release_version,
        "source_edition": source_edition,
        "source_database_sha256": source_database_sha256,
        "modern_content_sha256": content_sha256,
        "changed_verse_count": len(changed),
        "transformation_count": transformation_count,
        "rule_catalog": {
            rule.rule_id: {
                "category": rule.category,
                "description": rule.description,
                "source": rule.source,
                "version": rule.version,
            }
            for rule in normalizer.rules if rule.rule_id in used_rule_ids
        },
        "changed_verses": changed,
        "unresolved_by_verse": unresolved_by_verse,
        "unresolved_forms_artifact": unresolved_artifact,
    }


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _word_height(word: ET.Element) -> int:
    try:
        _, top, _, bottom = (int(value) for value in word.attrib["coords"].split(","))
        return max(0, top - bottom)
    except (KeyError, ValueError):
        return 0


def _page_words(page: ET.Element, page_id: str) -> list[OCRWord]:
    words: list[OCRWord] = []
    line_number = 0
    for line in page.iter():
        if _local_name(line.tag) != "LINE":
            continue
        line_number += 1
        header = line.attrib.get("x-struct") == "header"
        for word in line.iter():
            if _local_name(word.tag) != "WORD":
                continue
            value = "".join(word.itertext()).strip()
            if not value:
                continue
            confidence = word.attrib.get("x-confidence")
            words.append(OCRWord(
                value, page_id, _word_height(word),
                int(confidence) if confidence and confidence.isdigit() else None,
                line_number, header,
            ))
    return words


def _page_reference(words: list[OCRWord]) -> tuple[tuple[int, int, int, int] | None, set[int]]:
    # IA places the running reference near the top, often split into separate
    # OCR words. Detect it within a single line so body text cannot manufacture
    # a page anchor by putting unrelated numbers near one another.
    lines: dict[int, list[str]] = {}
    for word in words:
        lines.setdefault(word.line, []).append(word.text)
    for line_number in sorted(lines):
        if line_number > 6:
            break
        text = " ".join(lines[line_number])
        match = _RANGE.search(text)
        if match:
            start_ch, start_v, explicit_end_ch, end_v = match.groups()
            return (int(start_ch), int(start_v), int(explicit_end_ch or start_ch), int(end_v)), {line_number}
        match = _SINGLE_REF.search(text)
        if match:
            chapter, verse = map(int, match.groups())
            return (chapter, verse, chapter, verse), {line_number}
    return None, set()


def _canonical_refs(canonical_path: Path) -> tuple[list[str], dict[str, list[tuple[int, str]]], dict[str, int]]:
    with sqlite3.connect(canonical_path) as connection:
        codes = [row[0].upper() for row in connection.execute("SELECT id FROM books ORDER BY position")]
        refs_by_book: dict[str, list[tuple[int, str]]] = {}
        chapter_counts: dict[str, int] = {}
        for code in codes:
            bid = book_id(code)
            refs: list[tuple[int, str]] = []
            chapters = connection.execute("SELECT id, number FROM chapters WHERE book_id=? ORDER BY number", (bid,)).fetchall()
            chapter_counts[bid] = len(chapters)
            for chapter, chapter_number in chapters:
                verses = connection.execute("SELECT id FROM verses WHERE chapter_id=? ORDER BY number", (chapter,)).fetchall()
                refs.extend((chapter_number, row[0]) for row in verses)
            refs_by_book[bid] = refs
        return codes, refs_by_book, chapter_counts


def diagnose_igbob_djvu_xml(xml_path: Path, canonical_path: Path) -> IgboParseReport:
    """Diagnose OCR marker coverage using scan page-reference headers.

    This heuristic pass is not accepted as an edition importer. Its records
    are suitable only for measuring where page/verse alignment breaks. Words
    are retained as recognized; OCR numbers that cannot be anchored are
    reported rather than guessed.
    """
    codes, refs_by_book, chapter_counts = _canonical_refs(canonical_path)
    book_index = 0
    active_book = book_id(codes[book_index])
    active_index = 0
    current_id: str | None = None
    current_words: list[str] = []
    current_confidences: list[int] = []
    current_start_page = ""
    records: dict[str, ImportedVerse] = {}
    missing: list[str] = []
    duplicates: list[str] = []
    unanchored: list[str] = []
    header_pages = 0
    page_count = 0
    low_confidence = 0
    scanned_words = 0

    def flush(page: str) -> None:
        nonlocal current_id, current_words, current_confidences, current_start_page
        if current_id is None:
            return
        content = " ".join(current_words).strip()
        if content:
            prior = records.get(current_id)
            if prior is not None:
                duplicates.append(current_id)
                records[current_id] = ImportedVerse(
                    current_id, (prior.content + " " + content).strip(), prior.page_start,
                    page, min(x for x in (prior.minimum_ocr_confidence,
                                           min(current_confidences) if current_confidences else None)
                              if x is not None) if (prior.minimum_ocr_confidence is not None or current_confidences) else None,
                )
            else:
                records[current_id] = ImportedVerse(
                    current_id, content, current_start_page, page,
                    min(current_confidences) if current_confidences else None,
                )
        current_id, current_words, current_confidences, current_start_page = None, [], [], ""

    def set_reference(book: str, ref_index: int, page: str) -> None:
        nonlocal current_id, current_words, current_confidences, current_start_page
        flush(page)
        refs = refs_by_book[book]
        if not 0 <= ref_index < len(refs):
            return
        current_id = refs[ref_index][1]
        current_start_page = page
        current_words = []
        current_confidences = []

    def reference_index(book: str, chapter: int, verse: int) -> int | None:
        refs = refs_by_book[book]
        for index, (ch, ref) in enumerate(refs):
            if ch == chapter and ref.endswith(f"-{chapter}-{verse}"):
                return index
        return None

    context = ET.iterparse(xml_path, events=("end",))
    for _, page_element in context:
        if _local_name(page_element.tag) != "OBJECT":
            continue
        page_id = "unknown"
        for param in page_element.iter():
            if _local_name(param.tag) == "PARAM" and param.attrib.get("name") == "PAGE":
                page_id = param.attrib.get("value", page_id)
                break
        page_count += 1
        words = _page_words(page_element, page_id)
        scanned_words += len(words)
        low_confidence += sum(1 for word in words if word.confidence is not None and word.confidence < 50)
        page_ref, page_ref_lines = _page_reference(words)
        line_text: dict[int, list[str]] = {}
        for word in words:
            line_text.setdefault(word.line, []).append(word.text)
        title_lines = {
            line_number for line_number, line_words in line_text.items()
            if (letters := [char for token in line_words for char in token if char.isalpha()])
            and all(char.isupper() for char in letters)
        }
        if page_ref:
            header_pages += 1
            start_ch, start_v, end_ch, end_v = page_ref
            refs = refs_by_book[active_book]
            active_chapter = refs[min(active_index, len(refs) - 1)][0] if refs else 1
            # Chapter-number reset signals a book boundary; one-chapter books
            # are handled by the verse cursor resetting to 1 after their end.
            if start_ch < active_chapter or (
                start_ch == active_chapter == 1 and start_v == 1 and active_index > 0
                and active_index >= len(refs)
            ):
                if book_index + 1 < len(codes):
                    book_index += 1
                    active_book = book_id(codes[book_index])
                    active_index = 0
                    refs = refs_by_book[active_book]
            anchored = reference_index(active_book, start_ch, start_v)
            if anchored is None:
                # Bad OCR in a page header can make a chapter reset look like
                # two book transitions. Recover only when the exact reference
                # exists in an immediately preceding canonical book.
                for candidate in range(book_index - 1, max(-1, book_index - 4), -1):
                    candidate_book = book_id(codes[candidate])
                    candidate_index = reference_index(candidate_book, start_ch, start_v)
                    if candidate_index is not None:
                        book_index, active_book, anchored = candidate, candidate_book, candidate_index
                        break
            if anchored is not None:
                if current_id is not None:
                    flush(page_id)
                active_index = anchored
                # Page text can begin mid-verse; the header is the authoritative
                # first reference, and the page's first segment belongs there.
                set_reference(active_book, active_index, page_id)
            else:
                active_ch = refs[min(active_index, len(refs) - 1)][0] if refs else 0
                unanchored.append(f"{page_id}: {active_book} at chapter {active_ch}, header {start_ch}.{start_v}-{end_ch}.{end_v}")

        refs = refs_by_book[active_book]
        page_end = reference_index(active_book, page_ref[2], page_ref[3]) if page_ref else None
        page_limit = page_end if page_end is not None else None
        for word in words:
            if word.is_header or word.line in page_ref_lines:
                continue
            if word.line in title_lines:
                continue
            # Do not import running heads/reference ranges or all-caps book
            # headings as scripture. Their text remains in the retained source.
            if _DIGIT.fullmatch(word.text) and word.line <= 5 and word.height > 28:
                continue
            normalized_word = word.text.rstrip(".,;:")
            if _DIGIT.fullmatch(word.text):
                number = int(normalized_word)
                if word.height > 40:  # enlarged chapter numeral, not a verse marker
                    continue
                if active_index < len(refs):
                    expected_ch, expected_id = refs[active_index]
                    expected_v = int(expected_id.rsplit("-", 1)[1])
                    if number == expected_v and (page_limit is None or active_index <= page_limit):
                        if current_id != expected_id:
                            flush(page_id)
                        current_id = expected_id
                        current_start_page = page_id
                        active_index += 1
                        continue
                    # A following verse number in the same chapter exposes an
                    # OCR-lost marker. Keep the gap explicit; never synthesize
                    # the missing verse's text.
                    if number > expected_v and active_index < len(refs):
                        next_index = active_index
                        while next_index < len(refs) and refs[next_index][0] == expected_ch and int(refs[next_index][1].rsplit("-", 1)[1]) < number:
                            next_index += 1
                        if next_index < len(refs) and refs[next_index][0] == expected_ch and int(refs[next_index][1].rsplit("-", 1)[1]) == number:
                            missing.extend(row[1] for row in refs[active_index:next_index])
                            flush(page_id)
                            active_index = next_index + 1
                            current_id = refs[next_index][1]
                            current_start_page = page_id
                            continue
            if current_id is not None:
                current_words.append(word.text)
                if word.confidence is not None:
                    current_confidences.append(word.confidence)
        flush(page_id)
        if page_limit is not None and active_index <= page_limit:
            # The page-range end gives a checkable boundary even if a marker
            # was not recognized. Report all absent refs on this page.
            missing.extend(ref_id for _, ref_id in refs[active_index:page_limit + 1])
            active_index = page_limit + 1
        page_element.clear()

    # Preserve missing IDs once; they are useful import diagnostics.
    missing_unique = tuple(dict.fromkeys(missing))
    return IgboParseReport(
        tuple(records[ref] for ref in sorted(records, key=lambda x: (
            CANONICAL_BOOK_CODES.index(x.split("-", 1)[0].upper()),
            int(x.split("-")[1]), int(x.split("-")[2]),
        ))), page_count, header_pages, missing_unique,
        tuple(dict.fromkeys(duplicates)), tuple(dict.fromkeys(unanchored)),
        low_confidence, scanned_words,
    )


def _clean_kjv_usfm(text: str) -> str:
    # eBible's USFM includes Strong's word attributes outside the displayed
    # wording. Strip only the machine-readable |strong="..." annotations.
    return re.sub(r'\|strong="[^"]*"', "", text)


def parse_kjv_directory(source_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    books: dict[str, str] = {}
    verses: dict[str, str] = {}
    for path in sorted(source_dir.rglob("*.usfm")):
        parsed = parse_book_text(_clean_kjv_usfm(path.read_text(encoding="utf-8")), str(path), path)
        bid = book_id(parsed.code)
        if bid in books:
            raise ParseError(f"duplicate KJV book code {parsed.code} in {path}")
        books[bid] = parsed.book.name
        for verse in parsed.verses:
            if verse.id in verses:
                raise ParseError(f"duplicate KJV verse {verse.id}")
            if verse.id == "3jn-1-14" and " Peace be to thee." in verse.content:
                # The eBible KJV file joins the traditional 3 John 1:14–15
                # at verse 14. Split only at the verbatim KJV sentence start
                # so edition rows still use the repository's canonical IDs.
                first, second = verse.content.split(" Peace be to thee.", 1)
                verses[verse.id] = first
                verses["3jn-1-15"] = "Peace be to thee." + second
            else:
                verses[verse.id] = verse.content
    return books, verses


def build_edition_database(
    destination: Path,
    metadata: dict[str, str],
    books: dict[str, str],
    verses: dict[str, str],
) -> None:
    def populate(connection: sqlite3.Connection) -> None:
        connection.executemany("INSERT INTO metadata(key,value) VALUES (?,?)", sorted(metadata.items()))
        connection.executemany("INSERT INTO books(book_id,name) VALUES (?,?)", sorted(books.items()))
        connection.executemany("INSERT INTO verses(verse_id,content) VALUES (?,?)", sorted(verses.items()))
    _atomic_database(destination, EDITION_SCHEMA, populate)


def validate_edition_database(path: Path, canonical_path: Path, require_complete: bool = False) -> dict[str, object]:
    with sqlite3.connect(path) as connection:
        meta = dict(connection.execute("SELECT key,value FROM metadata"))
        books = dict(connection.execute("SELECT book_id,name FROM books"))
        rows = dict(connection.execute("SELECT verse_id,content FROM verses"))
    with sqlite3.connect(canonical_path) as canonical:
        canonical_books = {r[0] for r in canonical.execute("SELECT id FROM books")}
        canonical_verses = {r[0] for r in canonical.execute("SELECT id FROM verses")}
    unknown_books = sorted(set(books) - canonical_books)
    unknown_verses = sorted(set(rows) - canonical_verses)
    missing_verses = sorted(canonical_verses - set(rows))
    empty_verses = sorted(verse for verse, text in rows.items() if not text.strip())
    if unknown_books or unknown_verses or empty_verses or (require_complete and missing_verses):
        raise ParseError(f"edition validation failed: unknown_books={unknown_books[:5]}, unknown_verses={unknown_verses[:5]}, empty={empty_verses[:5]}, missing={len(missing_verses)}")
    return {
        "edition_id": meta.get("id"), "books": len(books), "chapters_represented": len({v.rsplit('-', 1)[0] for v in rows}),
        "verses": len(rows), "missing_verses": len(missing_verses), "duplicate_verses": 0,
        "unknown_books": unknown_books, "unknown_verses": unknown_verses, "empty_verses": empty_verses,
    }


def compare_edition_content(first_path: Path, second_path: Path) -> dict[str, object]:
    """Compare complete verse-ID/content maps across edition databases."""

    def read(path: Path) -> dict[str, str]:
        uri = f"file:{quote(str(Path(path).resolve()), safe='/')}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            return dict(connection.execute("SELECT verse_id,content FROM verses"))

    first = read(first_path)
    second = read(second_path)
    first_ids = set(first)
    second_ids = set(second)
    return {
        "first_count": len(first),
        "second_count": len(second),
        "missing_from_second": sorted(first_ids - second_ids),
        "extra_in_second": sorted(second_ids - first_ids),
        "content_differences": sorted(
            verse_id for verse_id in first_ids & second_ids if first[verse_id] != second[verse_id]
        ),
    }


def build_modern_database(
    destination: Path,
    books: dict[str, str],
    source_verses: dict[str, str],
    normalizer: Normalizer | None = None,
    source_metadata: dict[str, str] | None = None,
    audit_report_path: Path | None = None,
    unresolved_forms_path: Path | None = None,
) -> dict[str, int]:
    normalizer = normalizer or Normalizer()
    normalized = {verse_id: normalizer.normalize(text) for verse_id, text in source_verses.items()}
    source_metadata = source_metadata or {}
    output_verses = {verse_id: result.normalized_text for verse_id, result in normalized.items()}
    content_hash = _content_sha256(output_verses)
    source_hash = source_metadata.get("source_database_sha256", "unavailable")
    transformation_count = sum(len(result.transformations) for result in normalized.values())
    changed_count = sum(result.normalized_text != result.original_text for result in normalized.values())
    build_digest = hashlib.sha256()
    for value in (source_hash, normalizer.ruleset_version, normalizer.lexicon_version, content_hash):
        build_digest.update(value.encode("utf-8"))
        build_digest.update(b"\0")
    metadata = {
        "source": (
            source_metadata.get("source")
            or source_metadata.get("source_status")
            or source_metadata.get("source_url")
            or "Source provenance is recorded in the historical edition database."
        ),
        **{key: source_metadata[key] for key in (
            "source_package", "source_package_version", "distribution_status", "redistribution_rights"
        ) if key in source_metadata},
        "id": "igbob-modern", "name": "Modernized IGBOB (local research edition)",
        "language": source_metadata.get("language", "ig"),
        "ruleset_version": normalizer.ruleset_version,
        "lexicon_version": normalizer.lexicon_version,
        "normalization_ruleset_version": normalizer.ruleset_version,
        "reviewed_lexicon_version": normalizer.lexicon_version,
        "source_edition": "igbob",
        "source_database_sha256": source_hash,
        "verse_count": str(len(output_verses)),
        "changed_verse_count": str(changed_count),
        "unchanged_verse_count": str(len(output_verses) - changed_count),
        "transformation_count": str(transformation_count),
        "content_sha256": content_hash,
        "build_sha256": build_digest.hexdigest(),
    }
    def populate(connection: sqlite3.Connection) -> None:
        connection.executemany("INSERT INTO metadata(key,value) VALUES (?,?)", sorted(metadata.items()))
        connection.executemany("INSERT INTO books(book_id,name) VALUES (?,?)", sorted(books.items()))
        connection.executemany(
            "INSERT INTO verses(verse_id,content) VALUES (?,?)",
            sorted(output_verses.items()),
        )
    _atomic_database(destination, MODERN_SCHEMA, populate)
    if audit_report_path is not None:
        audit_report = _normalization_audit_report(
            normalized,
            release_version=normalizer.ruleset_version,
            source_database_sha256=source_hash,
            source_edition="igbob",
            content_sha256=content_hash,
            normalizer=normalizer,
            unresolved_forms_path=unresolved_forms_path,
        )
        _write_json_atomic(Path(audit_report_path), audit_report)
    return {
        "verses": len(normalized),
        "changed_verses": changed_count,
        "transformations": transformation_count,
        "review_items": sum(len(result.review_items) for result in normalized.values()),
        "unknown_items": sum(len(result.unknown_items) for result in normalized.values()),
        "integrity_issues": sum(len(result.integrity_issues) for result in normalized.values()),
    }


def import_kjv_dataset(source_dir: Path, canonical_path: Path, destination: Path) -> dict[str, object]:
    books, verses = parse_kjv_directory(source_dir)
    build_edition_database(destination, METADATA["kjv"], books, verses)
    return validate_edition_database(destination, canonical_path, require_complete=True)


def import_reviewed_igbob_json(source_path: Path, canonical_path: Path, destination: Path) -> dict[str, object]:
    """Build IGBOB only from a scan-reviewed reference transcription.

    The experimental whole-scan OCR parser is intentionally not a database
    input. A reviewed JSON manifest makes human collation a visible boundary.
    """
    data = json.loads(source_path.read_text(encoding="utf-8"))
    verses = data.get("verses")
    book_id_value = data.get("book_id")
    book_name = data.get("book_name")
    if not isinstance(verses, dict) or not verses or not isinstance(book_id_value, str) or not isinstance(book_name, str):
        raise ParseError("reviewed IGBOB manifest must include book_id, book_name, and a non-empty verses object")
    for ref, content in verses.items():
        if not isinstance(ref, str) or not isinstance(content, str) or not content.strip():
            raise ParseError(f"reviewed IGBOB manifest has malformed or empty verse {ref!r}")
        if not re.fullmatch(r"[a-z0-9]+-\d+-\d+", ref):
            raise ParseError(f"reviewed IGBOB manifest has malformed reference {ref!r}")
    metadata = {
        **METADATA["igbob"],
        "source_status": "partial, scan-reviewed development transcription",
        "source_pdf_sha256": sha256_file(source_path.parent / "Igbo-Bible-print.pdf"),
        "transcription_manifest_sha256": sha256_file(source_path),
    }
    build_edition_database(destination, metadata, {book_id_value: book_name}, verses)
    return validate_edition_database(destination, canonical_path, require_complete=False)


def normalize_edition_database(
    source_path: Path,
    destination: Path,
    audit_report_path: Path | None = None,
    unresolved_forms_path: Path | None = None,
    normalizer: Normalizer | None = None,
) -> dict[str, int]:
    with sqlite3.connect(source_path) as connection:
        books = dict(connection.execute("SELECT book_id,name FROM books"))
        verses = dict(connection.execute("SELECT verse_id,content FROM verses"))
        source_metadata = dict(connection.execute("SELECT key,value FROM metadata"))
    source_metadata["source_database_sha256"] = sha256_file(source_path)
    return build_modern_database(
        destination,
        books,
        verses,
        normalizer=normalizer,
        source_metadata=source_metadata,
        audit_report_path=audit_report_path,
        unresolved_forms_path=unresolved_forms_path,
    )

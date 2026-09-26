"""Local-only parser/importer for the Mobobi IGBOB research witness.

The APK is an input supplied by the operator and is never copied into the
repository. Parsing removes its lightweight HTML markup while preserving the
decoded visible text and all Igbo code points. No orthographic normalization
is performed here.
"""

from __future__ import annotations

import argparse
import html.parser
import json
import re
import sqlite3
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .books import CANONICAL_BOOK_CODES, book_id
from .data_paths import database_path, generated_path
from .editions import build_edition_database, sha256_file, validate_edition_database
from .usfm import ParseError


# Canonical book code -> (APK asset path, chapter-heading label, display name).
# Asset names containing mojibake reflect the ZIP's legacy filename encoding;
# the bytes inside each asset decode cleanly as UTF-16.
MOBOBI_BOOK_ASSETS: dict[str, tuple[str, str, str]] = {
    "GEN": ("assets/JENESIS.txt", "JENESIS", "JENESIS"),
    "EXO": ("assets/ß╗îPUPU.txt", "ỌPUPU", "ỌPUPU"),
    "LEV": ("assets/LEVITIKß╗îS.txt", "LEVITIKỌS", "LEVITIKỌS"),
    "NUM": ("assets/ß╗îNU-ß╗îGUGU.txt", "ỌNU-ỌGUGU", "ỌNU-ỌGUGU"),
    "DEU": ("assets/DEUTERONOMI.txt", "DEUTERONOMI", "DEUTERONOMI"),
    "JOS": ("assets/JOSHUA.txt", "JOSHUA", "JOSHUA"),
    "JDG": ("assets/NDI-IKPE.txt", "NDI-IKPE", "NDI-IKPE"),
    "RUT": ("assets/Rut.txt", "Rut", "Rut"),
    "1SA": ("assets/I. SAMUEL.txt", "I. SAMUEL", "I. SAMUEL"),
    "2SA": ("assets/II. SAMUEL.txt", "II. SAMUEL", "II. SAMUEL"),
    "1KI": ("assets/I. NDI-EZE.txt", "I. NDI-EZE", "I. NDI-EZE"),
    "2KI": ("assets/II. NDI-EZE.txt", "II. NDI-EZE", "II. NDI-EZE"),
    "1CH": ("assets/I. IHE EMERE.txt", "I. IHE EMERE", "I. IHE EMERE"),
    "2CH": ("assets/II. IHE EMERE.txt", "II. IHE EMERE", "II. IHE EMERE"),
    "EZR": ("assets/EZRA.txt", "EZRA", "EZRA"),
    "NEH": ("assets/NEHEMAIA.txt", "NEHEMAIA", "NEHEMAIA"),
    "EST": ("assets/ESTA.txt", "ESTA", "ESTA"),
    "JOB": ("assets/Job.txt", "Job", "Job"),
    "PSA": ("assets/AB├Ö ß╗îMA.txt", "ABÙ ỌMA", "ABÙ ỌMA"),
    "PRO": ("assets/ILU.txt", "ILU", "ILU"),
    "ECC": ("assets/EKLISIASTIS.txt", "EKLISIASTIS", "EKLISIASTIS"),
    "SNG": ("assets/AB├Ö NKE AB├Ö.txt", "ABÙ NKE ABÙ", "ABÙ NKE ABÙ"),
    "ISA": ("assets/AISAIA.txt", "AISAIA", "AISAIA"),
    "JER": ("assets/JEREMAIA.txt", "JEREMAIA", "JEREMAIA"),
    "LAM": ("assets/AB├Ö-├üKW├ü.txt", "ABÙ-ÁKWÁ", "ABÙ-ÁKWÁ"),
    "EZK": ("assets/EZIKIEL.txt", "EZIKIEL", "EZIKIEL"),
    "DAN": ("assets/Daniel.txt", "Daniel", "Daniel"),
    "HOS": ("assets/Hosea.txt", "Hosea", "Hosea"),
    "JOL": ("assets/JOEL.txt", "JOEL", "JOEL"),
    "AMO": ("assets/EMOS.txt", "EMOS", "EMOS"),
    "OBA": ("assets/OBADAIA.txt", "OBADAIA", "OBADAIA"),
    "JON": ("assets/JONA.txt", "JONA", "JONA"),
    "MIC": ("assets/MAIKA.txt", "MAIKA", "MAIKA"),
    "NAM": ("assets/NEHUM.txt", "NEHUM", "NEHUM"),
    "HAB": ("assets/Habakuk.txt", "Habakuk", "Habakuk"),
    "ZEP": ("assets/ZEFANAIA.txt", "ZEFANAIA", "ZEFANAIA"),
    "HAG": ("assets/Hagai.txt", "Hagai", "Hagai"),
    "ZEC": ("assets/ZEKARAIA.txt", "ZEKARAIA", "ZEKARAIA"),
    "MAL": ("assets/MALAKAI.txt", "MALAKAI", "MALAKAI"),
    "MAT": ("assets/MATIU.txt", "MATIU", "MATIU"),
    "MRK": ("assets/MAK.txt", "MAK", "MAK"),
    "LUK": ("assets/LUK.txt", "LUK", "LUK"),
    "JHN": ("assets/Jß╗îN.txt", "JỌN", "JỌN"),
    "ACT": ("assets/ß╗îLU NDI-OZI.txt", "ỌLU NDI-OZI", "ỌLU NDI-OZI"),
    "ROM": ("assets/NDI ROM.txt", "NDI ROM", "NDI ROM"),
    "1CO": ("assets/I. NDI Kß╗îRINT.txt", "I. NDI KỌRINT", "I. NDI KỌRINT"),
    "2CO": ("assets/II. NDI Kß╗îRINT.txt", "II. NDI KỌRINT", "II. NDI KỌRINT"),
    "GAL": ("assets/NDI GALETIA.txt", "NDI GALETIA", "NDI GALETIA"),
    "EPH": ("assets/NDI EFESß╗îS.txt", "NDI EFESỌS", "NDI EFESỌS"),
    "PHP": ("assets/NDI FILIPAI.txt", "NDI FILIPAI", "NDI FILIPAI"),
    "COL": ("assets/NDI Kß╗îLß╗îSI.txt", "NDI KỌLỌSI", "NDI KỌLỌSI"),
    "1TH": ("assets/I. NDI TESALß╗îNAIKA.txt", "I. NDI TESALỌNAIKA", "I. NDI TESALỌNAIKA"),
    "2TH": ("assets/II. NDI TESALß╗îNAIKA.txt", "II. NDI TESALỌNAIKA", "II. NDI TESALỌNAIKA"),
    "1TI": ("assets/I. TIMß╗îTI.txt", "I. TIMỌTI", "I. TIMỌTI"),
    "2TI": ("assets/II. TIMß╗îTI.txt", "II. TIMỌTI", "II. TIMỌTI"),
    "TIT": ("assets/TAITß╗îS.txt", "TAITỌS", "TAITỌS"),
    "PHM": ("assets/FAILIMON.txt", "FAILIMON", "FAILIMON"),
    "HEB": ("assets/NDI-HIBRU.txt", "NDI-HIBRU", "NDI-HIBRU"),
    "JAS": ("assets/JEMES.txt", "JEMES", "JEMES"),
    "1PE": ("assets/I. PITA.txt", "I. PITA", "I. PITA"),
    "2PE": ("assets/II. PITA.txt", "II. PITA", "II. PITA"),
    "1JN": ("assets/I. Jß╗îN.txt", "I. JỌN", "I. JỌN"),
    "2JN": ("assets/II. Jß╗îN.txt", "II. JỌN", "II. JỌN"),
    "3JN": ("assets/III. Jß╗îN.txt", "III. JỌN", "III. JỌN"),
    "JUD": ("assets/JUD.txt", "JUD", "JUD"),
    "REV": ("assets/NKPUGHE.txt", "NKPUGHE", "NKPUGHE"),
}

if tuple(MOBOBI_BOOK_ASSETS) != CANONICAL_BOOK_CODES:
    raise RuntimeError("Mobobi asset map must cover canonical books in canonical order")


class _VisibleTextParser(html.parser.HTMLParser):
    """Recover text nodes, creating boundaries only for block/line markup."""

    BLOCK_TAGS = {"p", "div", "li", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\u0000")
        elif tag.lower() == "br":
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\u0000")
        elif tag.lower() == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\u0000")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


@dataclass(frozen=True)
class ParsedBook:
    book_id: str
    book_name: str
    verses: dict[str, str]
    malformed: tuple[str, ...]
    non_verse_blocks: tuple[str, ...]
    duplicate_ids: tuple[str, ...]
    repairs: tuple[str, ...]
    empty_verses: tuple[str, ...]
    chapter_numbers: tuple[int, ...]
    markup: dict[str, int]
    entities: int


def _visible_blocks(text: str) -> tuple[list[str], dict[str, int], int]:
    parser = _VisibleTextParser()
    parser.feed(text)
    parser.close()
    visible = "".join(parser.parts)
    blocks = [block.replace("\r\n", "\n").replace("\r", "\n").strip()
              for paragraph in visible.split("\u0000") for block in paragraph.split("\n")]
    blocks = [block for block in blocks if block]
    tags = Counter(match.group(1).lower() for match in re.finditer(r"<\s*/?\s*([a-zA-Z][\w:-]*)\b", text))
    entity_count = len(re.findall(r"&(?:#[xX]?[\da-fA-F]+|[A-Za-z][A-Za-z\d]+);", text))
    return blocks, dict(sorted(tags.items())), entity_count


def _compact_visible_text(text: str) -> str:
    """Collapse layout whitespace without changing visible characters."""
    return re.sub(r"\s+", " ", text).strip()


def parse_mobobi_book(asset_name: str, raw: bytes, code: str) -> ParsedBook:
    """Parse one known Mobobi UTF-16 asset into canonical verse IDs."""
    if code not in MOBOBI_BOOK_ASSETS or asset_name != MOBOBI_BOOK_ASSETS[code][0]:
        raise ParseError(f"unmapped Mobobi asset {asset_name!r} for {code!r}")
    try:
        decoded = raw.decode("utf-16")
    except UnicodeDecodeError as exc:
        raise ParseError(f"{asset_name}: invalid UTF-16: {exc}") from exc
    blocks, markup, entities = _visible_blocks(decoded)
    _, heading, display_name = MOBOBI_BOOK_ASSETS[code]
    heading_re = re.compile(rf"^{re.escape(heading)}\s+(\d{{1,3}})$", re.IGNORECASE)
    chapter = 0
    chapter_numbers: list[int] = []
    verses: dict[str, str] = {}
    malformed: list[str] = []
    non_verse_blocks: list[str] = []
    duplicate_ids: list[str] = []
    repairs: list[str] = []
    empty_verses: list[str] = []
    expected_next_verse = 1
    pending_verse: int | None = None

    for block_index, block in enumerate(blocks, 1):
        block = block.strip()
        chapter_match = heading_re.fullmatch(block)
        if chapter_match:
            chapter = int(chapter_match.group(1))
            if chapter in chapter_numbers or chapter != len(chapter_numbers) + 1:
                malformed.append(f"block {block_index}: non-sequential chapter heading {chapter}")
            chapter_numbers.append(chapter)
            expected_next_verse = 1
            pending_verse = None
            continue
        if re.fullmatch(r"X-X-X[-.]*", block):
            continue
        # A chapter-like uppercase heading for another/unknown book is a hard
        # parse error, not Bible text to be silently attached to the previous verse.
        if not chapter and block_index == 1:
            malformed.append(f"first visible block is not chapter 1: {block!r}")
            continue
        if chapter == 0:
            continue
        standalone_number = re.fullmatch(r"(\d{1,3})", block)
        if standalone_number:
            number = int(standalone_number.group(1))
            # Some assets repeat the chapter number on a separate line before
            # verse 1 (notably Psalms and 1 Samuel); it is a heading artifact.
            if number == chapter and expected_next_verse == 1:
                continue
            if number != expected_next_verse:
                malformed.append(f"chapter {chapter}: expected verse {expected_next_verse}, found standalone {number}")
            pending_verse = number
            expected_next_verse = number + 1
            continue

        # One malformed tag begins 2 Chronicles 14 verse 1 as ``<1 ...``.
        # Restore the visibly intended numeral only in this known marker shape.
        if block.startswith(f"<{expected_next_verse} "):
            block = block[1:]
            repairs.append(f"chapter {chapter}: removed stray '<' before verse marker {expected_next_verse}")
        marker_re = re.compile(r"(?<!\w)(\d{1,3})(?=[ \t]+|[A-ZỌỊỤÁÉÍÓÚÀÈÌÒÙ])")
        matches = []
        for candidate in marker_re.finditer(block):
            start = candidate.start(1)
            prefix = block[:start]
            anticipated_next = int(matches[-1].group(1)) + 1 if matches else expected_next_verse
            boundary = (
                not prefix.strip()
                or prefix.endswith(("\n\n", "  "))
                or (candidate.group(1) == str(anticipated_next)
                    and prefix.endswith((" ", "\t"))
                    and candidate.end() < len(block)
                    and block[candidate.end()].isupper())
            )
            if boundary:
                if (prefix.strip() and candidate.group(1) == str(anticipated_next)
                        and prefix.endswith((" ", "\t")) and block[candidate.end():candidate.end() + 1].isupper()):
                    repairs.append(
                        f"chapter {chapter}: recognized fused verse marker {candidate.group(1)} before "
                        f"{block[candidate.end():candidate.end() + 18]!r}"
                    )
                matches.append(candidate)
        if pending_verse is not None and not matches:
            ref = f"{book_id(code)}-{chapter}-{pending_verse}"
            content = _compact_visible_text(block)
            if content:
                verses[ref] = content
            else:
                empty_verses.append(ref)
            pending_verse = None
            continue
        if not matches:
            non_verse_blocks.append(block)
            continue
        # Every numbered marker starts a verse only when the preceding segment
        # is empty; inside-verse numerals remain ordinary visible text.
        if matches[0].start() != 0:
            malformed.append(f"block {block_index} has unparsed prefix: {block[:90]!r}")
            continue
        for marker_index, match in enumerate(matches):
            number = int(match.group(1))
            end = matches[marker_index + 1].start() if marker_index + 1 < len(matches) else len(block)
            body = _compact_visible_text(block[match.end():end])
            if number != expected_next_verse:
                malformed.append(
                    f"chapter {chapter}: expected verse {expected_next_verse}, found {number} in block {block_index}"
                )
            expected_next_verse = number + 1
            ref = f"{book_id(code)}-{chapter}-{number}"
            if ref in verses:
                malformed.append(f"duplicate verse ID {ref}")
                duplicate_ids.append(ref)
                continue
            if not body:
                empty_verses.append(ref)
            verses[ref] = body

    if not chapter_numbers:
        malformed.append("no chapter headings found")
    return ParsedBook(book_id(code), display_name, verses, tuple(malformed), tuple(non_verse_blocks),
                      tuple(duplicate_ids), tuple(repairs),
                      tuple(empty_verses), tuple(chapter_numbers), markup, entities)


def _canonical_references(canonical_path: Path) -> tuple[set[str], dict[str, int], dict[str, int]]:
    with sqlite3.connect(canonical_path) as connection:
        books = {row[0]: row[1] for row in connection.execute("SELECT id, position FROM books")}
        chapters = dict(connection.execute("SELECT book_id, COUNT(*) FROM chapters GROUP BY book_id"))
        counts = dict(connection.execute(
            "SELECT c.book_id, COUNT(v.id) FROM chapters c JOIN verses v ON v.chapter_id=c.id GROUP BY c.book_id"
        ))
        refs = {row[0] for row in connection.execute("SELECT id FROM verses")}
    return refs, {str(k): int(v) for k, v in chapters.items()}, {str(k): int(v) for k, v in counts.items()}


def import_mobobi_apk(apk_path: Path, canonical_path: Path, destination: Path,
                      report_path: Path | None = None,
                      kjv_path: Path | None = None,
                      recovery_path: Path | None = None) -> dict[str, object]:
    """Build the local research-only historical edition from a supplied APK."""
    apk_path = Path(apk_path)
    canonical_path = Path(canonical_path)
    destination = Path(destination)
    expected_refs, expected_chapters, expected_verses = _canonical_references(canonical_path)
    source_verses: dict[str, str] = {}
    books: dict[str, str] = {}
    book_reports: list[dict[str, object]] = []
    duplicate_ids: list[str] = []
    duplicate_book_content: list[dict[str, object]] = []
    quarantined_books: dict[str, int] = {}
    malformed: list[str] = []
    empty: list[str] = []
    repairs: list[str] = []
    with zipfile.ZipFile(apk_path) as archive:
        names = set(archive.namelist())
        expected_assets = {spec[0] for spec in MOBOBI_BOOK_ASSETS.values()}
        missing_assets = sorted(expected_assets - names)
        if missing_assets:
            raise ParseError(f"APK is missing mapped Igbo book assets: {missing_assets}")
        igbo_txt = {name for name in names if name.startswith("assets/") and name.lower().endswith(".txt")
                    and not name.rsplit("/", 1)[-1].startswith("(English)")}
        unmapped_assets = sorted(igbo_txt - expected_assets)
        parsed_by_code: dict[str, ParsedBook] = {}
        for code in CANONICAL_BOOK_CODES:
            asset, _, _ = MOBOBI_BOOK_ASSETS[code]
            parsed = parse_mobobi_book(asset, archive.read(asset), code)
            books[parsed.book_id] = parsed.book_name
            malformed.extend(f"{parsed.book_id}: {issue}" for issue in parsed.malformed)
            repairs.extend(f"{parsed.book_id}: {repair}" for repair in parsed.repairs)
            duplicate_ids.extend(f"{parsed.book_id}:{ref}" for ref in parsed.duplicate_ids)
            empty.extend(parsed.empty_verses)
            # A complete book asset can still be mislabeled or duplicated.
            # The APK's III JỌN asset is an exact verse-text duplicate of II JỌN
            # (the 2 John letter), so quarantine it rather than assigning that
            # unrelated text to canonical 3 John IDs.
            duplicate_of = next((prior_code for prior_code in CANONICAL_BOOK_CODES
                                 if prior_code in parsed_by_code
                                 and list(parsed_by_code[prior_code].verses.values())
                                 == list(parsed.verses.values())), None)
            parsed_by_code[code] = parsed
            if duplicate_of is not None and parsed.verses:
                duplicate_book_content.append({
                    "book_id": parsed.book_id,
                    "asset": asset,
                    "duplicate_of_book_id": book_id(duplicate_of),
                    "quarantined_verses": len(parsed.verses),
                    "reason": "entire verse-text sequence duplicates an earlier book asset",
                })
                quarantined_books[parsed.book_id] = len(parsed.verses)
                parsed_verses = {}
            else:
                parsed_verses = parsed.verses
            for ref, content in parsed_verses.items():
                if ref in source_verses:
                    duplicate_ids.append(ref)
                source_verses[ref] = content
            book_reports.append({
                "book_id": parsed.book_id,
                "asset": asset,
                "chapters": len(parsed.chapter_numbers),
                "verses": len(parsed_verses),
                "source_verses_parsed": len(parsed.verses),
                "quarantined_duplicate_book_content": len(parsed.verses) if duplicate_of is not None else 0,
                "expected_chapters": expected_chapters.get(parsed.book_id, 0),
                "expected_verses": expected_verses.get(parsed.book_id, 0),
                "chapter_numbers": list(parsed.chapter_numbers),
                "markup_tags": parsed.markup,
                "html_entity_count": parsed.entities,
                "malformed": list(parsed.malformed),
                "non_verse_blocks": list(parsed.non_verse_blocks),
                "duplicate_verse_ids": list(parsed.duplicate_ids),
                "visible_text_repairs": list(parsed.repairs),
                "empty_verses": list(parsed.empty_verses),
            })

    recovery_provenance: dict[str, str] = {}
    recovery_source_urls: dict[str, object] = {}
    if recovery_path is not None:
        recovery = json.loads(Path(recovery_path).read_text(encoding="utf-8"))
        entries = recovery.get("verses", {})
        raw_source_urls = recovery.get("witness_urls", {})
        if not isinstance(raw_source_urls, dict) or any(
            not isinstance(key, str)
            or not (isinstance(value, str) or (isinstance(value, list) and all(isinstance(url, str) for url in value)))
            for key, value in raw_source_urls.items()
        ):
            raise ParseError("recovery JSON 'witness_urls' must map source identifiers to URL strings or string lists")
        recovery_source_urls = raw_source_urls
        if not isinstance(entries, dict):
            raise ParseError("recovery JSON 'verses' must be an object keyed by canonical verse ID")
        for ref, entry in entries.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("text"), str) or not entry["text"].strip():
                raise ParseError(f"invalid recovery entry for {ref!r}")
            witness = entry.get("source_witness")
            if not isinstance(witness, str) or not witness.strip():
                raise ParseError(f"recovery entry {ref!r} has no source_witness")
            source_verses[ref] = entry["text"].strip()
            recovery_provenance[ref] = witness

    imported_refs = set(source_verses)
    missing_refs = sorted(expected_refs - imported_refs)
    extra_refs = sorted(imported_refs - expected_refs)
    with sqlite3.connect(canonical_path) as connection:
        canonical_books = {row[0] for row in connection.execute("SELECT id FROM books")}
    extra_books = sorted(set(books) - canonical_books)
    metadata = {
        "id": "igbob",
        "name": "IGBOB (Mobobi research transcription)",
        "language": "ig",
        "source": "Mobobi IGBOB research transcription",
        "source_package": "com.mobobi.igbobible",
        "source_package_version": "2.0",
        "source_asset_format": "APK per-book UTF-16 HTML-like text assets",
        "source_asset_sha256": sha256_file(apk_path),
        "importer_version": "1.0.0",
        "distribution_status": "research/local only",
        "redistribution_rights": "unresolved",
        "source_status": "incomplete local research transcription witness; canonical structural gaps remain",
    }
    if recovery_provenance:
        metadata["name"] = "IGBOB (composite Union-family research transcription)"
        metadata["source"] = "Mobobi IGBOB research transcription plus attributed Union witness gap recovery"
        metadata["source_status"] = "composite local research corpus; Mobobi plus explicitly attributed gap recovery"
        metadata["verse_source_provenance_json"] = json.dumps(recovery_provenance, ensure_ascii=False, sort_keys=True)
        metadata["source_provenance_counts_json"] = json.dumps({
            "mobobi_direct_after_quarantine": len(imported_refs) - len(recovery_provenance),
            "other_witness_supplied": len(recovery_provenance),
        }, sort_keys=True)
        metadata["recovery_source_counts_json"] = json.dumps(
            dict(sorted(Counter(recovery_provenance.values()).items())), sort_keys=True
        )
        metadata["recovery_source_urls_json"] = json.dumps(recovery_source_urls, sort_keys=True)
        metadata["quarantined_source_anomalies_json"] = json.dumps(
            duplicate_book_content, ensure_ascii=False, sort_keys=True
        )
    build_edition_database(destination, metadata, books, source_verses)
    if extra_books or extra_refs or empty:
        validation = {
            "edition_id": metadata["id"],
            "books": len(books),
            "chapters_represented": len({ref.rsplit("-", 1)[0] for ref in source_verses}),
            "verses": len(source_verses),
            "missing_verses": len(missing_refs),
            "duplicate_verses": len(duplicate_ids),
            "unknown_books": extra_books,
            "unknown_verses": extra_refs,
            "empty_verses": empty,
        }
    else:
        validation = validate_edition_database(destination, canonical_path, require_complete=False)
    chapter_total = sum(int(book["chapters"]) for book in book_reports)
    report: dict[str, object] = {
        "schema_version": 1,
        "source_package": metadata["source_package"],
        "source_sha256": metadata["source_asset_sha256"],
        "encoding": "UTF-16 with BOM (utf-16 decode); invalid code units rejected",
        "text_handling": "HTMLParser converts character references and removes tags; block tags become line boundaries; intra-verse whitespace collapses to one space; punctuation and Unicode code points otherwise retained",
        "expected_books": len(CANONICAL_BOOK_CODES),
        "imported_books": len(books),
        "expected_chapters": sum(expected_chapters.values()),
        "imported_chapters": chapter_total,
        "expected_verses": len(expected_refs),
        "imported_verses": len(source_verses),
        "coverage_status": "complete" if not missing_refs and not extra_refs and not duplicate_ids and not malformed and not empty else "incomplete; do not promote to final edition",
        "missing_verses": len(missing_refs),
        "missing_verse_ids": missing_refs,
        "duplicate_verse_ids": sorted(duplicate_ids),
        "duplicate_book_content": duplicate_book_content,
        "quarantined_verses": sum(quarantined_books.values()),
        "recovered_verses": len(recovery_provenance),
        "recovery_source_counts": dict(sorted(Counter(recovery_provenance.values()).items())),
        "extra_or_unmapped_verses": extra_refs,
        "extra_or_unmapped_books": extra_books,
        "unmapped_igbo_assets": unmapped_assets,
        "malformed_references": malformed,
        "empty_verses": empty,
        "mechanical_marker_repairs": repairs,
        "database_validation": validation,
        "books": book_reports,
    }
    imported_by_chapter = Counter(ref.rsplit("-", 1)[0] for ref in imported_refs)
    canonical_by_chapter: dict[str, int] = {}
    with sqlite3.connect(canonical_path) as connection:
        canonical_by_chapter = dict(connection.execute(
            "SELECT c.id, COUNT(v.id) FROM chapters c JOIN verses v ON v.chapter_id=c.id GROUP BY c.id"
        ))
    report["chapter_coverage_differences"] = [
        {"chapter_id": chapter_id_value,
         "expected_verses": int(canonical_by_chapter.get(chapter_id_value, 0)),
         "imported_verses": int(imported_by_chapter.get(chapter_id_value, 0))}
        for chapter_id_value in sorted(set(canonical_by_chapter) | set(imported_by_chapter))
        if int(canonical_by_chapter.get(chapter_id_value, 0)) != int(imported_by_chapter.get(chapter_id_value, 0))
    ]
    if kjv_path is not None:
        with sqlite3.connect(kjv_path) as connection:
            kjv_refs = {row[0] for row in connection.execute("SELECT verse_id FROM verses")}
        report["kjv_structure_crosscheck"] = {
            "checked_references_only": True,
            "canonical_verse_count": len(expected_refs),
            "kjv_verse_count": len(kjv_refs),
            "canonical_missing_from_kjv": sorted(expected_refs - kjv_refs),
            "kjv_extra_vs_canonical": sorted(kjv_refs - expected_refs),
            "mobobi_missing_but_present_in_kjv": sorted((expected_refs - imported_refs) & kjv_refs),
        }
    if report_path is not None:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a local-only Mobobi IGBOB research candidate database.")
    parser.add_argument("--apk", required=True, type=Path, help="locally available com.mobobi.igbobible APK")
    parser.add_argument("--canonical", type=Path, default=database_path("bible.sqlite"))
    parser.add_argument("--kjv", type=Path, default=database_path("kjv.sqlite"),
                        help="KJV database used for verse IDs only")
    parser.add_argument("--output", type=Path,
                        default=database_path("igbob-mobobi-candidate.sqlite"),
                        help="local ignored output; incomplete coverage remains marked in metadata")
    parser.add_argument("--report", type=Path,
                        default=generated_path("igbob-mobobi-import-report.json"))
    parser.add_argument("--recovery-json", type=Path,
                        help="optional local JSON overlay; each verse requires text and source_witness")
    args = parser.parse_args(argv)
    report = import_mobobi_apk(args.apk, args.canonical, args.output, args.report, args.kjv, args.recovery_json)
    print(json.dumps({key: report[key] for key in (
        "coverage_status", "expected_books", "imported_books", "expected_chapters",
        "imported_chapters", "expected_verses", "imported_verses", "missing_verses",
        "duplicate_verse_ids", "extra_or_unmapped_verses", "malformed_references", "empty_verses",
    )}, ensure_ascii=False, indent=2))
    return 0 if report["coverage_status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

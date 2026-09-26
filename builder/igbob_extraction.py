"""Page-aware local diagnostics for the scanned IGBOB source.

This module keeps IA DjVu XML provenance intact. Its output is a candidate
transcription aid; OCR words are never promoted into an edition database by
this code.
"""

from __future__ import annotations

import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


@dataclass(frozen=True)
class SourceWord:
    text: str
    page: str
    page_number: int | None
    column: int
    region: int
    line: int
    word: int
    bbox: tuple[int, int, int, int] | None
    ocr_confidence: int | None


@dataclass(frozen=True)
class SourceLine:
    page: str
    page_number: int | None
    column: int
    region: int
    line: int
    structure: str | None
    words: tuple[SourceWord, ...]

    @property
    def text(self) -> str:
        return " ".join(word.text for word in self.words)


@dataclass(frozen=True)
class PageAudit:
    page: str
    page_number: int | None
    pagecolumn_blocks: int
    lines: int
    words: int
    low_confidence_words: int
    missing_confidence_words: int
    standalone_number_tokens: int
    attached_number_tokens: int
    suspicious_unicode_words: int
    non_latin_letter_words: int
    reference_header: str | None
    anomaly_reasons: tuple[str, ...]


def _page_number(page_id: str) -> int | None:
    match = re.search(r"_(\d{4})\.djvu$", page_id)
    return int(match.group(1)) if match else None


def _bbox(element: ET.Element) -> tuple[int, int, int, int] | None:
    try:
        values = tuple(int(value) for value in element.attrib["coords"].split(","))
    except (KeyError, ValueError):
        return None
    return values if len(values) == 4 else None


def _element_words(element: ET.Element) -> list[ET.Element]:
    return [node for node in element.iter() if _tag(node) == "WORD"]


def iter_source_pages(path: Path):
    """Yield ordered OCR lines per page with page/column/line/word provenance.

    DjVu XML PAGECOLUMN and nested REGION/PARAGRAPH order is retained exactly
    as emitted by IA. This preserves the two-column reading order that is lost
    when the document is reduced to a flat string.
    """
    for _, page in ET.iterparse(path, events=("end",)):
        if _tag(page) != "OBJECT":
            continue
        page_id = next((node.attrib.get("value", "unknown") for node in page.iter()
                        if _tag(node) == "PARAM" and node.attrib.get("name") == "PAGE"), "unknown")
        number = _page_number(page_id)
        result: list[SourceLine] = []
        columns = [node for node in page.iter() if _tag(node) == "PAGECOLUMN"]
        parents = {child: parent for parent in page.iter() for child in parent}
        column_ids = {id(column): index for index, column in enumerate(columns)}
        region_ids = {id(region): index for column in columns
                      for index, region in enumerate(node for node in column.iter() if _tag(node) == "REGION")}
        line_counters: dict[tuple[int, int], int] = {}
        for line in (node for node in page.iter() if _tag(node) == "LINE"):
            ancestor = parents.get(line)
            column_index = region_index = -1
            while ancestor is not None:
                if _tag(ancestor) == "REGION":
                    region_index = region_ids.get(id(ancestor), -1)
                if _tag(ancestor) == "PAGECOLUMN":
                    column_index = column_ids.get(id(ancestor), -1)
                    break
                ancestor = parents.get(ancestor)
            key = (column_index, region_index)
            line_counters[key] = line_counters.get(key, 0) + 1
            line_index = line_counters[key]
            words: list[SourceWord] = []
            for word_index, word in enumerate(_element_words(line), 1):
                text = "".join(word.itertext()).strip()
                if not text:
                    continue
                raw_confidence = word.attrib.get("x-confidence")
                confidence = int(raw_confidence) if raw_confidence and raw_confidence.isdigit() else None
                words.append(SourceWord(text, page_id, number, column_index,
                                        region_index, line_index, word_index,
                                        _bbox(word), confidence))
            if words:
                result.append(SourceLine(page_id, number, column_index,
                                         region_index, line_index,
                                         line.attrib.get("x-struct"), tuple(words)))
        yield page_id, tuple(result), len(columns)
        page.clear()


_PAGE_RANGE = re.compile(r"(?<!\d)(\d{1,3})\s*\.\s*(\d{1,3})\s*[-—–]{1,2}\s*(?:(\d{1,3})\s*\.\s*)?(\d{1,3})(?!\d)")
_ATTACHED_NUMBER = re.compile(r"(?<!\w)\d{1,3}[A-Za-zỌọỤụỊị][\wỌọỤụỊị-]*")


def audit_page(page_id: str, lines: tuple[SourceLine, ...], column_count: int) -> PageAudit:
    page_number = _page_number(page_id)
    words = [word for line in lines for word in line.words]
    header = None
    for line in lines[:8]:
        match = _PAGE_RANGE.search(line.text)
        if match:
            header = match.group(0)
            break
    low = sum(word.ocr_confidence is not None and word.ocr_confidence < 50 for word in words)
    missing_conf = sum(word.ocr_confidence is None for word in words)
    numbers = sum(bool(re.fullmatch(r"\d{1,3}[.,;:]?", word.text)) for word in words)
    attached = sum(bool(_ATTACHED_NUMBER.fullmatch(word.text)) for word in words)
    suspicious = sum(any(unicodedata.category(char) in {"Cs", "Co"} or char == "\ufffd"
                         for char in word.text) for word in words)
    non_latin = sum(any(unicodedata.category(char).startswith("L")
                        and "LATIN" not in unicodedata.name(char, "")
                        for char in word.text) for word in words)
    reasons: list[str] = []
    if header is None:
        reasons.append("no OCR page-range anchor")
    if low:
        reasons.append(f"{low} OCR words below 50 confidence")
    if missing_conf:
        reasons.append(f"{missing_conf} words lack OCR confidence")
    if attached:
        reasons.append(f"{attached} digit-plus-word tokens may hide verse markers")
    if suspicious:
        reasons.append(f"{suspicious} words contain suspicious Unicode")
    if non_latin:
        reasons.append(f"{non_latin} words contain non-Latin letters (often OCR homoglyphs)")
    return PageAudit(page_id, page_number, column_count, len(lines), len(words),
                     low, missing_conf, numbers, attached, suspicious, non_latin,
                     header, tuple(reasons))


def build_source_audit(xml_path: Path) -> dict[str, object]:
    pages = [audit_page(pid, lines, columns) for pid, lines, columns in iter_source_pages(xml_path)]
    total_words = sum(page.words for page in pages)
    low = sum(page.low_confidence_words for page in pages)
    missing_conf = sum(page.missing_confidence_words for page in pages)
    return {
        "schema_version": 1,
        "source": "Internet Archive DjVu XML; candidate text only, not accepted as transcription",
        "page_count": len(pages),
        "pages_with_reference_header": sum(page.reference_header is not None for page in pages),
        "pages_with_review_anomalies": sum(bool(page.anomaly_reasons) for page in pages),
        "word_count": total_words,
        "low_confidence_ocr_words": low,
        "low_confidence_ocr_word_percent": round(100 * low / total_words, 3) if total_words else 0,
        "words_without_ocr_confidence": missing_conf,
        "standalone_number_tokens": sum(page.standalone_number_tokens for page in pages),
        "attached_number_tokens": sum(page.attached_number_tokens for page in pages),
        "non_latin_letter_words": sum(page.non_latin_letter_words for page in pages),
        "pages": [asdict(page) for page in pages],
    }


def write_source_audit(xml_path: Path, destination: Path) -> dict[str, object]:
    report = build_source_audit(xml_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

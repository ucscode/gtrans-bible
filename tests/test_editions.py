from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from builder.editions import (
    _clean_kjv_usfm,
    _page_reference,
    build_edition_database,
    build_modern_database,
    parse_kjv_directory,
    validate_edition_database,
)
from builder.normalization import Normalizer
from builder.usfm import parse_book_text


def _canonical(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            CREATE TABLE books(id TEXT PRIMARY KEY, position INTEGER);
            CREATE TABLE chapters(id TEXT PRIMARY KEY, book_id TEXT, number INTEGER);
            CREATE TABLE verses(id TEXT PRIMARY KEY, chapter_id TEXT, number INTEGER);
            INSERT INTO books VALUES ('jdg', 7);
            INSERT INTO chapters VALUES ('jdg-13', 'jdg', 13);
            INSERT INTO verses VALUES ('jdg-13-1', 'jdg-13', 1);
            INSERT INTO verses VALUES ('jdg-13-2', 'jdg-13', 2);
        """)


def test_kjv_word_attributes_are_removed_without_changing_wording() -> None:
    source = r'\v 1 In the \w beginning|strong="H7225"\w*.'
    cleaned = _clean_kjv_usfm(source)
    parsed = parse_book_text("\\id GEN Genesis\n\\h Genesis\n\\c 1\n" + cleaned)
    assert parsed.verses[0].content == "In the beginning."


def test_kjv_import_maps_complete_structured_usfm(tmp_path: Path) -> None:
    source = tmp_path / "usfm"
    source.mkdir()
    (source / "08-JDG.usfm").write_text(
        "\\id JDG Judges\n\\h Judges\n\\toc1 Judges\n\\c 13\n"
        "\\p\n\\v 1 The LORD did good.\n\\v 2 The LORD said.\n",
        encoding="utf-8",
    )
    books, verses = parse_kjv_directory(source)
    assert books == {"jdg": "Judges"}
    assert verses == {"jdg-13-1": "The LORD did good.", "jdg-13-2": "The LORD said."}


def test_edition_database_reports_missing_verses_explicitly(tmp_path: Path) -> None:
    canonical = tmp_path / "bible.sqlite"
    _canonical(canonical)
    edition = tmp_path / "edition.sqlite"
    build_edition_database(edition, {"id": "igbob", "name": "IGBOB"}, {"jdg": "Ndi-Ikpe"}, {
        "jdg-13-1": "Historical text.",
    })
    result = validate_edition_database(edition, canonical)
    assert result["verses"] == 1
    assert result["missing_verses"] == 1


def test_reviewed_lexical_mapping_and_unresolved_forms(tmp_path: Path) -> None:
    normalizer = Normalizer()
    result = normalizer.normalize("n'aburu nēme")
    assert result.normalized_text == "n'aburu na-eme"
    assert [item.rule_id for item in result.transformations] == [
        "historical.na-e-participle-to-onwu-na-e"
    ]
    assert any(item.text == "n'aburu" for item in result.review_items)
    assert not any(item.text == "nēme" for item in result.review_items)
    # Ordinary historical spelling and dotted vowels remain unchanged.
    assert normalizer.normalize("aburu ogu").normalized_text == "aburu ogu"
    assert normalizer.normalize("ab͕uru").normalized_text == "agburu"
    assert normalizer.normalize(result.normalized_text).normalized_text == result.normalized_text


def test_modern_edition_has_slim_schema_and_external_audit(tmp_path: Path) -> None:
    database = tmp_path / "modern.sqlite"
    audit_path = tmp_path / "generated" / "audit.json"
    summary = build_modern_database(
        database, {"jdg": "Ndi-Ikpe"}, {"jdg-13-2": "ab͕uru"},
        source_metadata={
            "source": "fixture historical edition",
            "redistribution_rights": "unresolved",
        },
        audit_report_path=audit_path,
    )
    assert summary["changed_verses"] == 1
    with sqlite3.connect(database) as connection:
        row = connection.execute("SELECT content FROM verses").fetchone()
        verse_columns = {r[1] for r in connection.execute("PRAGMA table_info(verses)")}
    assert row == ("agburu",)
    assert verse_columns == {"verse_id", "content"}
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    change = audit["changed_verses"][0]
    assert change["verse_id"] == "jdg-13-2"
    assert change["transformations"][0]["historical_form"] == "b͕"
    assert change["transformations"][0]["modern_form"] == "gb"
    assert change["transformations"][0]["rule_version"] == "0.2.0"
    assert audit["rule_catalog"][change["transformations"][0]["rule_id"]]["version"] == "0.2.0"
    with sqlite3.connect(database) as connection:
        assert {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")} == {
            "metadata", "books", "verses"
        }
        metadata = dict(connection.execute("SELECT key,value FROM metadata"))
        assert metadata["redistribution_rights"] == "unresolved"
        assert metadata["normalization_ruleset_version"] == "0.5.0"
        assert metadata["source"] == "fixture historical edition"


def test_modern_edition_builds_complete_verse_set_without_id_drift(tmp_path: Path) -> None:
    database = tmp_path / "complete-modern.sqlite"
    books = {f"b{i:02d}": f"Book {i}" for i in range(66)}
    ids = [f"b{i % 66:02d}-{i // 66 + 1}-{i + 1}" for i in range(31103)]
    verses = {verse_id: "mb\u0355e." if index % 7 == 0 else "Unchanged." for index, verse_id in enumerate(ids)}
    summary = build_modern_database(database, books, verses)
    assert summary["verses"] == 31103
    with sqlite3.connect(database) as connection:
        output_ids = {row[0] for row in connection.execute("SELECT verse_id FROM verses")}
        assert connection.execute("SELECT count(*) FROM books").fetchone()[0] == 66
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert output_ids == set(ids)


def test_ocr_page_reference_supports_shorthand_end_chapter() -> None:
    from builder.editions import OCRWord

    words = [
        OCRWord("24.", "p", 20, 90, 1),
        OCRWord("44—25.", "p", 20, 90, 1),
        OCRWord("12", "p", 20, 90, 1),
    ]
    assert _page_reference(words) == ((24, 44, 25, 12), {1})


def test_page_aware_source_reader_keeps_reading_order_and_provenance(tmp_path: Path) -> None:
    from builder.igbob_extraction import iter_source_pages

    xml = tmp_path / "tiny.xml"
    xml.write_text('''<HTML><BODY><OBJECT><PARAM name="PAGE" value="sample_0029.djvu"/>
      <PAGECOLUMN><REGION><PARAGRAPH><LINE x-struct="header"><WORD coords="1,2,3,4" x-confidence="91">13.1—13.4</WORD></LINE>
      <LINE><WORD coords="10,20,30,40" x-confidence="42">Umu</WORD><WORD coords="31,20,40,40">Israel</WORD></LINE></PARAGRAPH></REGION></PAGECOLUMN>
      <PAGECOLUMN><REGION><PARAGRAPH><LINE><WORD coords="1,50,4,60" x-confidence="98">2</WORD><WORD coords="5,50,20,60" x-confidence="88">Jehova</WORD></LINE></PARAGRAPH></REGION></PAGECOLUMN>
      </OBJECT></BODY></HTML>''', encoding="utf-8")
    page_id, lines, block_count = next(iter_source_pages(xml))
    assert page_id == "sample_0029.djvu"
    assert block_count == 2
    assert [line.text for line in lines] == ["13.1—13.4", "Umu Israel", "2 Jehova"]
    assert lines[1].words[0].ocr_confidence == 42
    assert lines[1].words[0].bbox == (10, 20, 30, 40)
    assert (lines[1].words[0].page_number, lines[1].words[0].column, lines[1].words[0].line) == (29, 0, 2)


def test_page_audit_separates_marker_and_ocr_quality_signals() -> None:
    from builder.igbob_extraction import SourceLine, SourceWord, audit_page

    words = (
        SourceWord("13.1—13.4", "scan_0029.djvu", 29, 0, 0, 1, 1, None, 90),
        SourceWord("Umu", "scan_0029.djvu", 29, 0, 0, 2, 1, None, 42),
        SourceWord("рara", "scan_0029.djvu", 29, 0, 0, 2, 2, None, 88),
        SourceWord("2Jehova", "scan_0029.djvu", 29, 0, 0, 2, 3, None, 88),
    )
    lines = (
        SourceLine("scan_0029.djvu", 29, 0, 0, 1, "header", words[:1]),
        SourceLine("scan_0029.djvu", 29, 0, 0, 2, None, words[1:]),
    )
    page = audit_page("scan_0029.djvu", lines, 2)
    assert page.reference_header == "13.1—13.4"
    assert page.low_confidence_words == 1
    assert page.standalone_number_tokens == 0
    assert page.attached_number_tokens == 1
    assert page.non_latin_letter_words == 1
    assert "OCR words below 50 confidence" in " ".join(page.anomaly_reasons)


def test_source_audit_is_deterministic_for_same_xml(tmp_path: Path) -> None:
    from builder.igbob_extraction import build_source_audit

    xml = tmp_path / "tiny.xml"
    xml.write_text('''<HTML><BODY><OBJECT><PARAM name="PAGE" value="sample_0001.djvu"/>
      <PAGECOLUMN><REGION><LINE><WORD coords="1,2,3,4" x-confidence="90">Igbo</WORD></LINE></REGION></PAGECOLUMN>
      </OBJECT></BODY></HTML>''', encoding="utf-8")
    assert build_source_audit(xml) == build_source_audit(xml)

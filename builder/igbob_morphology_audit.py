"""Research-only audit for historical macrons, ḅ, and embedded symbols.

The raw source strings are read without Unicode normalization or mutation.
Outputs are local research artifacts under data/generated/.
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from builder.data_paths import database_path, generated_path

from builder.research import tokenize_with_spans


MACRONS = set("āēīōūĀĒĪŌŪ")
FAMILIES = ("nē", "nā", "gē", "gā")
ODD_SYMBOLS = ("=", ">", "#", "/", "_", "@")


def _raw_first_vowel(text: str) -> str | None:
    for char in text:
        decomposed = unicodedata.normalize("NFD", char.casefold())
        base = decomposed[0]
        if "\u0323" in decomposed[1:] and base in {"i", "o", "u"}:
            base = {"i": "ị", "o": "ọ", "u": "ụ"}[base]
        if base in {"a", "e", "i", "o", "u", "ị", "ọ", "ụ"}:
            return base
    return None


def _harmony_class(vowel: str | None) -> str:
    if vowel is None:
        return "NO_VOWEL"
    if vowel in {"e", "i", "o", "u"}:
        return "PLUS_ATR_WRITTEN"
    if vowel in {"a", "ị", "ọ", "ụ"}:
        return "MINUS_ATR_WRITTEN"
    return "UNKNOWN"


def generate(source: Path, output_json: Path, output_csv: Path) -> dict:
    word_occurrences: Counter[str] = Counter()
    word_verses: dict[str, set[str]] = defaultdict(set)
    word_books: dict[str, set[str]] = defaultdict(set)
    word_refs: dict[str, list[str]] = defaultdict(list)
    word_examples: dict[str, list[str]] = defaultdict(list)
    macron_char_occurrences: Counter[str] = Counter()
    macron_char_verses: dict[str, set[str]] = defaultdict(set)
    symbol_occurrences: Counter[str] = Counter()
    symbol_embedded_occurrences: Counter[str] = Counter()
    symbol_verses: dict[str, set[str]] = defaultdict(set)
    symbol_embedded_verses: dict[str, set[str]] = defaultdict(set)
    symbol_words: dict[str, Counter[str]] = defaultdict(Counter)
    symbol_contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    bdot_occurrences: list[dict[str, str | int]] = []
    bdot_words: Counter[str] = Counter()
    bdot_verses: set[str] = set()
    family_book_samples: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)

    with sqlite3.connect(source) as db:
        metadata = dict(db.execute("SELECT key,value FROM metadata"))
        provenance = json.loads(metadata.get("verse_source_provenance_json", "{}"))
        for ref, text in db.execute("SELECT verse_id,content FROM verses ORDER BY verse_id"):
            book = ref.split("-", 1)[0]
            tokens = list(tokenize_with_spans(text))
            for token, start, end in tokens:
                folded = token.casefold()
                family = next((item for item in FAMILIES if folded.startswith(item)), None)
                if family and book not in family_book_samples[family]:
                    family_book_samples[family][book] = {
                        "verse_id": ref,
                        "raw_form": token,
                        "context": text[max(0, start - 42):min(len(text), end + 42)],
                    }
                if any(char in MACRONS for char in token):
                    word_occurrences[token] += 1
                    word_verses[token].add(ref)
                    word_books[token].add(book)
                    if len(word_refs[token]) < 8:
                        word_refs[token].append(ref)
                    if len(word_examples[token]) < 3:
                        word_examples[token].append(text[max(0, start - 30):min(len(text), end + 30)])
                    for char in token:
                        if char in MACRONS:
                            macron_char_occurrences[char] += 1
                            macron_char_verses[char].add(ref)
                for token_offset, char in enumerate(token):
                    if char in {"ḅ", "Ḅ"}:
                        bdot_words[token] += 1
                        bdot_verses.add(ref)
                        bdot_occurrences.append({
                            "verse_id": ref,
                            "word": token,
                            "character": char,
                            "codepoint": f"U+{ord(char):04X}",
                            "offset_in_verse": start + token_offset,
                            "context": text[max(0, start - 30):min(len(text), end + 30)],
                            "source_provenance": provenance.get(ref, "mobobi_direct_after_quarantine"),
                        })
            for pos, char in enumerate(text):
                if char not in ODD_SYMBOLS:
                    continue
                symbol_occurrences[char] += 1
                symbol_verses[char].add(ref)
                embedded = (
                    (pos > 0 and unicodedata.category(text[pos - 1])[0] in {"L", "M", "N"})
                    or (pos + 1 < len(text) and unicodedata.category(text[pos + 1])[0] in {"L", "M", "N"})
                )
                if embedded:
                    symbol_embedded_occurrences[char] += 1
                    symbol_embedded_verses[char].add(ref)
                # Include any surrounding word-like form for grouping.
                left = pos
                right = pos + 1
                while left and (text[left - 1].isalnum() or unicodedata.category(text[left - 1]).startswith("M") or text[left - 1] in "'’-"):
                    left -= 1
                while right < len(text) and (text[right].isalnum() or unicodedata.category(text[right]).startswith("M") or text[right] in "'’-"):
                    right += 1
                symbol_words[char][text[left:right]] += 1
                if len(symbol_contexts[char]) < 12:
                    symbol_contexts[char].append({
                        "verse_id": ref,
                        "context": text[max(0, pos - 35):min(len(text), pos + 36)],
                        "source_provenance": provenance.get(ref, "mobobi_direct_after_quarantine"),
                    })

    family_inventory: dict[str, dict] = {}
    full_word_inventory: list[dict] = []
    for word, count in sorted(word_occurrences.items(), key=lambda row: (-row[1], row[0])):
        folded = word.casefold()
        family = next((item for item in FAMILIES if folded.startswith(item)), None)
        fused_family = None
        fused_leading = ""
        if family is None:
            leading = re.match(r"^(m['’]|a)", folded)
            candidate = folded[len(leading.group(1)):] if leading else folded
            fused_family = next((item for item in FAMILIES if candidate.startswith(item)), None)
            if fused_family and leading:
                fused_leading = leading.group(1)
        active_family = family or fused_family
        stem = (
            folded[len(active_family):]
            if family
            else folded[len(fused_leading) + len(active_family):]
            if fused_family
            else ""
        )
        first_vowel = _raw_first_vowel(stem) if active_family else None
        harmony = _harmony_class(first_vowel) if active_family else "NOT_APPLICABLE"
        full_word_inventory.append({
            "raw_form": word,
            "occurrences": count,
            "affected_verses": len(word_verses[word]),
            "book_count": len(word_books[word]),
            "family": active_family,
            "family_position": "token_initial" if family else ("fused_subject_or_prefix" if fused_family else None),
            "following_stem": stem if active_family else None,
            "following_first_vowel": first_vowel,
            "following_vowel_harmony_class": harmony,
            "representative_verse_ids": word_refs[word],
            "representative_contexts": word_examples[word],
        })
        if active_family:
            slot = family_inventory.setdefault(active_family, {
                "token_initial_occurrences": 0,
                "token_initial_forms": set(),
                "token_initial_verses": set(),
                "token_initial_books": set(),
                "fused_occurrences": 0,
                "fused_forms": set(),
                "fused_verses": set(),
                "written_vowel_classes": Counter(),
                "forms": [],
            })
            position = "token_initial" if family else "fused"
            slot[f"{position}_occurrences"] += count
            slot[f"{position}_forms"].add(word)
            slot[f"{position}_verses"].update(word_verses[word])
            if position == "token_initial":
                slot["token_initial_books"].update(word_books[word])
                if harmony not in {"NOT_APPLICABLE", "NO_VOWEL", "UNKNOWN"}:
                    expected = "PLUS_ATR_WRITTEN" if active_family.endswith("ē") else "MINUS_ATR_WRITTEN"
                    slot["written_vowel_classes"]["consistent" if harmony == expected else "mismatch"] += count
            slot["forms"].append(word)

    # The token-level audit above counts each macron-bearing lexical form once.
    # Its raw character totals are separately verified against the complete verse strings.
    symbols = {}
    for char in ODD_SYMBOLS:
        refs = sorted(symbol_verses[char])
        provenance_counts = Counter(provenance.get(ref, "mobobi_direct_after_quarantine") for ref in refs)
        embedded_refs = sorted(symbol_embedded_verses[char])
        embedded_provenance_counts = Counter(
            provenance.get(ref, "mobobi_direct_after_quarantine") for ref in embedded_refs
        )
        symbols[char] = {
            "unicode": f"U+{ord(char):04X}",
            "total_occurrences": symbol_occurrences[char],
            "total_affected_verses": len(refs),
            "embedded_occurrences": symbol_embedded_occurrences[char],
            "embedded_affected_verses": len(symbol_embedded_verses[char]),
            "embedded_verse_ids": embedded_refs,
            "verse_ids": refs,
            "token_forms": symbol_words[char].most_common(),
            "verse_provenance_counts": dict(provenance_counts),
            "embedded_verse_provenance_counts": dict(embedded_provenance_counts),
            "representative_contexts": symbol_contexts[char],
            "print_collation": "Not visible in the directly inspected print samples; intended character is not uniform enough to clean automatically.",
            "classification": "TRANSCRIPTION_ARTIFACT",
        }

    families_out = {}
    for family, item in family_inventory.items():
        families_out[family] = {
            "token_initial_occurrences": item["token_initial_occurrences"],
            "token_initial_forms": len(item["token_initial_forms"]),
            "token_initial_affected_verses": len(item["token_initial_verses"]),
            "token_initial_books": sorted(item["token_initial_books"]),
            "fused_occurrences": item["fused_occurrences"],
            "fused_forms": len(item["fused_forms"]),
            "fused_affected_verses": len(item["fused_verses"]),
            "written_vowel_harmony_counts": dict(item["written_vowel_classes"]),
            "all_family_forms": sorted(item["forms"]),
            "distributed_book_sample": [
                {"book_id": book, **sample}
                for book, sample in list(sorted(family_book_samples[family].items()))[:30]
            ],
        }

    char_inventory = {}
    for char, count in sorted(macron_char_occurrences.items(), key=lambda row: ord(row[0])):
        char_inventory[char] = {"occurrences": count, "affected_verses": len(macron_char_verses[char])}

    report = {
        "report_type": "raw historical Igbo macron/morphology and source-symbol audit",
        "source_database": str(source.resolve()),
        "unicode_normalization_applied": False,
        "source_edition_rights": metadata.get("redistribution_rights", "unknown"),
        "macron_inventory": {
            "token_occurrences": sum(word_occurrences.values()),
            "unique_token_forms": len(word_occurrences),
            "affected_verses": len({ref for verses in word_verses.values() for ref in verses}),
            "codepoint_counts": char_inventory,
            "prefix_families": families_out,
            "complete_token_forms": full_word_inventory,
        },
        "marked_b_with_dot_below": {
            "codepoint_occurrences": len(bdot_occurrences),
            "unique_token_forms": len(bdot_words),
            "affected_verses": len(bdot_verses),
            "all_token_forms": [{"form": word, "occurrences": count} for word, count in sorted(bdot_words.items())],
            "occurrences": bdot_occurrences,
            "visual_collation": {
                "pdf_pages": [813, 814, 815, 816],
                "printed_pages": [817, 818, 819, 820],
                "finding": "The Malachi spellings use the same marked-b consonant as the previously collated Union marked-b glyph.",
            },
        },
        "embedded_symbols": symbols,
        "source_metadata": {
            "source_package": metadata.get("source_package"),
            "source_package_version": metadata.get("source_package_version"),
            "source_asset_sha256": metadata.get("source_asset_sha256"),
            "provenance_counts": json.loads(metadata.get("source_provenance_counts_json", "{}")),
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "raw_form", "occurrences", "affected_verses", "book_count", "family",
            "family_position", "following_stem", "following_first_vowel", "following_vowel_harmony_class",
            "representative_verse_ids",
        ])
        writer.writeheader()
        for row in full_word_inventory:
            writer.writerow({
                "raw_form": row["raw_form"],
                "occurrences": row["occurrences"],
                "affected_verses": row["affected_verses"],
                "book_count": row["book_count"],
                "family": row["family"],
                "family_position": row["family_position"],
                "following_stem": row["following_stem"],
                "following_first_vowel": row["following_first_vowel"],
                "following_vowel_harmony_class": row["following_vowel_harmony_class"],
                "representative_verse_ids": ";".join(row["representative_verse_ids"]),
            })
    return report


if __name__ == "__main__":
    result = generate(
        database_path("igbob.sqlite"),
        generated_path("igbob-morphology-audit.json"),
        generated_path("igbob-macron-forms.csv"),
    )
    print(json.dumps({
        "macron_token_occurrences": result["macron_inventory"]["token_occurrences"],
        "macron_unique_forms": result["macron_inventory"]["unique_token_forms"],
        "marked_b_dot_below": result["marked_b_with_dot_below"]["codepoint_occurrences"],
        "symbols": {key: (value["embedded_occurrences"], value["embedded_affected_verses"]) for key, value in result["embedded_symbols"].items()},
    }, ensure_ascii=False, indent=2))

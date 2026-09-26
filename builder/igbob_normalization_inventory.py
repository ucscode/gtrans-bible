"""Generate a full-corpus, read-only orthography inventory for local IGBOB.

The output is research material only. This module never edits source verses.
"""

from __future__ import annotations

import csv
import json
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from builder.data_paths import database_path, generated_path

from builder.research import tokenize_with_spans


MACRON_CHARS = set("āēīōūĀĒĪŌŪ")
DOT_BELOW = "\u0323"
MARKED_B = "\u0355"
APOSTROPHES = {"'", "’", "‘", "ʼ"}
HYPHENS = {"-", "‐", "‑", "‒", "–", "—"}


def _flags(token: str) -> list[str]:
    flags: list[str] = []
    lowered = token.casefold()
    if "b" + MARKED_B in lowered:
        flags.append("marked-b")
    if any(char in token for char in MACRON_CHARS) or "\u0304" in token:
        flags.append("macron")
    if DOT_BELOW in token or any(char in token for char in "ịọụṅỊỌỤṄ"):
        flags.append("underdot-or-combining-dot")
    if any(char in token for char in APOSTROPHES):
        flags.append("apostrophe-or-elision")
    if any(char in token for char in HYPHENS):
        flags.append("hyphenation")
    if any(unicodedata.category(char).startswith("M") for char in token):
        flags.append("other-combining-mark")
    if any(char.isdigit() for char in token):
        flags.append("digit-or-verse-marker")
    if not flags:
        flags.append("plain-lexical-form-review")
    return flags


def _classification(flags: list[str]) -> str:
    if "marked-b" in flags:
        return "SYSTEMATIC: historical marked consonant; approved gb mapping"
    if "macron" in flags:
        return "CONTEXT_DEPENDENT/UNKNOWN: macron-bearing form"
    if "apostrophe-or-elision" in flags or "hyphenation" in flags:
        return "TYPOGRAPHIC_ONLY/UNKNOWN: inspect grammatical boundary"
    if "underdot-or-combining-dot" in flags or "other-combining-mark" in flags:
        return "UNKNOWN: preserve diacritics; lexical review"
    if "digit-or-verse-marker" in flags:
        return "TYPOGRAPHIC_ONLY: likely numbering/layout"
    return "UNKNOWN: lexical/archaic status not determined by frequency"


def generate_inventory(source: Path, csv_path: Path, json_path: Path) -> dict:
    """Write one row for every distinct corpus token, preserving source forms."""
    token_counts: Counter[str] = Counter()
    verse_sets: dict[str, set[str]] = defaultdict(set)
    contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    feature_occurrences: Counter[str] = Counter()
    feature_verses: dict[str, set[str]] = defaultdict(set)
    punctuation_counts: Counter[str] = Counter()
    whitespace_counts: Counter[str] = Counter()
    total_tokens = total_chars = 0
    total_verses = 0
    with sqlite3.connect(source) as connection:
        rows = connection.execute("SELECT verse_id, content FROM verses ORDER BY verse_id")
        for verse_id, text in rows:
            total_verses += 1
            total_chars += len(text)
            punctuation_counts.update(char for char in text if unicodedata.category(char).startswith("P"))
            whitespace_counts.update(char for char in text if char.isspace())
            for token, start, end in tokenize_with_spans(text):
                total_tokens += 1
                token_counts[token] += 1
                verse_sets[token].add(verse_id)
                if len(contexts[token]) < 3:
                    context = " ".join(text[max(0, start - 55): min(len(text), end + 55)].split())
                    contexts[token].append({"verse_id": verse_id, "context": context})
                for flag in _flags(token):
                    feature_occurrences[flag] += 1
                    feature_verses[flag].add(verse_id)

    fieldnames = [
        "raw_form", "casefold_lookup_form", "occurrence_count", "verses_affected",
        "representative_verse_ids", "representative_contexts", "candidate_features",
        "suspected_modernization_category",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for token, count in sorted(token_counts.items(), key=lambda item: (-item[1], item[0])):
            flags = _flags(token)
            refs = sorted(verse_sets[token])
            writer.writerow({
                "raw_form": token,
                "casefold_lookup_form": unicodedata.normalize("NFC", token).casefold(),
                "occurrence_count": count,
                "verses_affected": len(refs),
                "representative_verse_ids": ";".join(refs[:8]),
                "representative_contexts": json.dumps(contexts[token], ensure_ascii=False),
                "candidate_features": ";".join(flags),
                "suspected_modernization_category": _classification(flags),
            })

    marked_forms = [token for token in token_counts if "marked-b" in _flags(token)]
    macron_forms = [token for token in token_counts if "macron" in _flags(token)]
    data = {
        "report_type": "full-corpus historical orthography inventory",
        "source_database": str(source),
        "source_scope": "local research-only composite Union-family corpus; no source text modified",
        "tokenization": "Unicode letters/marks/numbers, preserving internal apostrophes and hyphens; no NFC/NFD applied to raw forms",
        "totals": {
            "verses": total_verses,
            "tokens": total_tokens,
            "unique_raw_forms": len(token_counts),
            "characters": total_chars,
            "distinct_marked_b_forms": len(marked_forms),
            "marked_b_token_occurrences": sum(token_counts[t] for t in marked_forms),
            "marked_b_glyph_occurrences": sum(
                token_counts[t] * (t.count("b" + MARKED_B) + t.count("B" + MARKED_B))
                for t in marked_forms
            ),
            "verses_with_marked_b": len(feature_verses["marked-b"]),
            "distinct_macron_forms": len(macron_forms),
            "macron_token_occurrences": sum(token_counts[t] for t in macron_forms),
        },
        "feature_inventory": [
            {"feature": feature, "token_occurrences": count,
             "verses_affected": len(feature_verses[feature])}
            for feature, count in feature_occurrences.most_common()
        ],
        "punctuation_inventory": [
            {"character": char, "codepoint": f"U+{ord(char):04X}",
             "unicode_name": unicodedata.name(char, "UNNAMED"), "occurrences": count}
            for char, count in punctuation_counts.most_common()
        ],
        "whitespace_inventory": [
            {"character": char, "codepoint": f"U+{ord(char):04X}",
             "unicode_name": unicodedata.name(char, "UNNAMED"), "occurrences": count}
            for char, count in whitespace_counts.most_common()
        ],
        "top_marked_b_forms": [
            {"raw_form": token, "occurrences": token_counts[token],
             "verses_affected": len(verse_sets[token]), "examples": contexts[token]}
            for token in sorted(marked_forms, key=lambda t: (-token_counts[t], t))[:100]
        ],
        "top_macron_forms": [
            {"raw_form": token, "occurrences": token_counts[token],
             "verses_affected": len(verse_sets[token]), "examples": contexts[token]}
            for token in sorted(macron_forms, key=lambda t: (-token_counts[t], t))[:100]
        ],
        "top_forms_overall": [
            {"raw_form": token, "occurrences": count, "verses_affected": len(verse_sets[token]),
             "candidate_features": _flags(token), "examples": contexts[token]}
            for token, count in token_counts.most_common(100)
        ],
        "classification_limit": "Frequency and surface patterns identify review candidates; plain lexical forms are not automatically labeled archaic or modernized.",
    }
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    report = generate_inventory(
        database_path("igbob.sqlite"),
        generated_path("igbob-normalization-inventory.csv"),
        generated_path("igbob-normalization-inventory.json"),
    )
    print(json.dumps(report["totals"], ensure_ascii=False, indent=2))

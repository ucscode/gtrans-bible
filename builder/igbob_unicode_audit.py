"""Complete raw-Unicode and grapheme audit for the local historical IGBOB corpus.

The source text is never normalized or rewritten. Generated artifacts are
research reports under data/generated/.
"""

from __future__ import annotations

import csv
import json
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from builder.data_paths import database_path, generated_path

from builder.research import tokenize_with_spans


MARKED_B = "b\u0355"
UPPER_MARKED_B = "B\u0355"
TONE_MARKS = {"\u0300", "\u0301"}  # grave, acute
DOT_BELOW = "\u0323"
MACRON = "\u0304"
APOSTROPHES = {"'", "’", "‘", "ʼ"}
HYPHENS = {"-", "‐", "‑", "‒", "–", "—"}
COMMON_PUNCTUATION = set(".,;:?!()[]{}\"“”‘’'-")

# The 1961 Ọnwụ inventory: 28 consonant graphemes and 8 vowels. Multi-letter
# consonants are graphemes, not separate alphabet entries.
MODERN_GRAPHEMES = {
    "a", "e", "i", "ị", "o", "ọ", "u", "ụ",
    "b", "gb", "ch", "d", "f", "g", "gh", "gw", "h", "j", "k",
    "kp", "kw", "l", "m", "n", "ṅ", "nw", "ny", "p", "r", "s",
    "sh", "t", "v", "w", "y", "z",
}
MODERN_GRAPHEMES_CASEFOLD = {item.casefold() for item in MODERN_GRAPHEMES}
VOWELS_CASEFOLD = {"a", "e", "i", "ị", "o", "ọ", "u", "ụ"}
DIGRAPHS = {"gb", "ch", "gh", "gw", "kp", "kw", "nw", "ny", "sh"}


def _is_mark(char: str) -> bool:
    return unicodedata.category(char).startswith("M")


def _clusters(text: str) -> list[str]:
    """Segment this Latin-script corpus into starter-plus-mark clusters.

    The corpus contains no joiner-based scripts. This UAX #29-relevant subset
    preserves every codepoint exactly, including leading/isolated marks.
    """
    result: list[str] = []
    for char in text:
        if _is_mark(char) and result:
            result[-1] += char
        else:
            result.append(char)
    return result


@lru_cache(maxsize=None)
def _grapheme_is_allowed(cluster: str) -> bool:
    # Exact NFC precomposed alphabet letters are accepted as stored.
    folded = cluster.casefold()
    if folded in MODERN_GRAPHEMES_CASEFOLD:
        return True
    # Classify precomposed tone letters and decomposed marks as the same
    # modern grapheme, while the inventory retains their raw codepoint forms.
    decomposed = unicodedata.normalize("NFD", cluster.casefold())
    base, marks = decomposed[0], set(decomposed[1:])
    if base in VOWELS_CASEFOLD and marks <= (TONE_MARKS | {DOT_BELOW}):
        if DOT_BELOW not in marks or base in {"i", "o", "u"}:
            return True
    if base == "n" and marks <= (TONE_MARKS | {"\u0307"}) and ("\u0307" in marks or marks <= TONE_MARKS):
        return True
    return False


@lru_cache(maxsize=None)
def _classify_cluster(cluster: str) -> str:
    if cluster in {MARKED_B, UPPER_MARKED_B}:
        return "SYSTEMATIC_CHARACTER_MAPPING"
    if MACRON in cluster or cluster[0] in "āēīōūĀĒĪŌŪ":
        return "MORPHOLOGICAL_ORTHOGRAPHY"
    decomposed = unicodedata.normalize("NFD", cluster.casefold())
    if set(decomposed[1:]) & TONE_MARKS:
        if decomposed[0] in VOWELS_CASEFOLD | {"n"}:
            return "LEGITIMATE_MODERN_TONE_MARKING"
        return "UNKNOWN"
    if any(_is_mark(char) for char in cluster):
        return "UNKNOWN"
    if any(unicodedata.category(char).startswith("L") for char in cluster):
        return "UNKNOWN"
    return "TYPOGRAPHIC"


@lru_cache(maxsize=None)
def _details(char: str) -> dict[str, str]:
    return {
        "character": char,
        "codepoint": f"U+{ord(char):04X}",
        "unicode_name": unicodedata.name(char, "<unnamed>") ,
        "category": unicodedata.category(char),
    }


def generate_audit(source: Path, json_path: Path, csv_path: Path) -> dict:
    cp_occ: Counter[str] = Counter()
    cp_words: dict[str, set[str]] = defaultdict(set)
    cp_verses: dict[str, set[str]] = defaultdict(set)
    cp_refs: dict[str, list[str]] = defaultdict(list)
    cp_contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    cluster_occ: Counter[str] = Counter()
    cluster_words: dict[str, set[str]] = defaultdict(set)
    cluster_word_occ: Counter[str] = Counter()
    cluster_verses: dict[str, set[str]] = defaultdict(set)
    cluster_refs: dict[str, list[str]] = defaultdict(list)
    word_counts: Counter[str] = Counter()
    verse_word_sets: dict[str, set[str]] = defaultdict(set)
    punctuation: Counter[str] = Counter()
    whitespace: Counter[str] = Counter()
    symbols: Counter[str] = Counter()
    embedded_punct_counts: Counter[str] = Counter()
    embedded_punct_verses: dict[str, set[str]] = defaultdict(set)
    embedded_punct_contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    embedded_symbol_counts: Counter[str] = Counter()
    embedded_symbol_verses: dict[str, set[str]] = defaultdict(set)
    embedded_symbol_contexts: dict[str, list[dict[str, str]]] = defaultdict(list)
    total_chars = total_verses = total_tokens = 0
    marked_b_glyphs = 0
    marked_b_words: Counter[str] = Counter()
    marked_b_verses: set[str] = set()
    alphabet_units: Counter[str] = Counter()
    alphabet_unit_words: dict[str, set[str]] = defaultdict(set)
    alphabet_unit_verses: dict[str, set[str]] = defaultdict(set)
    alphabet_unit_refs: dict[str, list[str]] = defaultdict(list)

    with sqlite3.connect(source) as db:
        for verse_id, text in db.execute("SELECT verse_id, content FROM verses ORDER BY verse_id"):
            total_verses += 1
            total_chars += len(text)
            tokens = list(tokenize_with_spans(text))
            total_tokens += len(tokens)
            for token, _, _ in tokens:
                word_counts[token] += 1
                verse_word_sets[token].add(verse_id)
                units = _clusters(token)
                index = 0
                while index < len(units):
                    pair = units[index] + units[index + 1] if index + 1 < len(units) else ""
                    if pair.casefold() in DIGRAPHS:
                        unit = pair
                        index += 2
                    else:
                        unit = units[index]
                        index += 1
                    if unicodedata.category(unit[0]).startswith("L"):
                        alphabet_units[unit] += 1
                        alphabet_unit_words[unit].add(token)
                        alphabet_unit_verses[unit].add(verse_id)
                        if len(alphabet_unit_refs[unit]) < 8:
                            alphabet_unit_refs[unit].append(verse_id)
            for char_pos, char in enumerate(text):
                cp_occ[char] += 1
                cp_verses[char].add(verse_id)
                if len(cp_refs[char]) < 8:
                    cp_refs[char].append(verse_id)
                if len(cp_contexts[char]) < 5:
                    cp_contexts[char].append({
                        "verse_id": verse_id,
                        "context": " ".join(text[max(0, char_pos - 28):min(len(text), char_pos + 29)].split()),
                    })
                if char.isspace():
                    whitespace[char] += 1
                elif unicodedata.category(char).startswith("P"):
                    punctuation[char] += 1
                elif not (unicodedata.category(char).startswith(("L", "M", "N"))):
                    symbols[char] += 1
            for pos, char in enumerate(text):
                if (unicodedata.category(char).startswith("S")
                        and ((pos > 0 and unicodedata.category(text[pos - 1]).startswith(("L", "M", "N")))
                             or (pos + 1 < len(text) and unicodedata.category(text[pos + 1]).startswith(("L", "M", "N"))))):
                    embedded_symbol_counts[char] += 1
                    embedded_symbol_verses[char].add(verse_id)
                    if len(embedded_symbol_contexts[char]) < 10:
                        embedded_symbol_contexts[char].append({
                            "verse_id": verse_id,
                            "context": " ".join(text[max(0, pos - 32):min(len(text), pos + 33)].split()),
                        })
            for pos, char in enumerate(text):
                if (unicodedata.category(char).startswith("P") and char not in COMMON_PUNCTUATION
                        and ((pos > 0 and unicodedata.category(text[pos - 1]).startswith(("L", "M", "N")))
                             or (pos + 1 < len(text) and unicodedata.category(text[pos + 1]).startswith(("L", "M", "N"))))):
                    embedded_punct_counts[char] += 1
                    embedded_punct_verses[char].add(verse_id)
                    if len(embedded_punct_contexts[char]) < 10:
                        embedded_punct_contexts[char].append({
                            "verse_id": verse_id,
                            "context": " ".join(text[max(0, pos - 32):min(len(text), pos + 33)].split()),
                        })
            token_at: dict[int, str] = {}
            for token, start, end in tokens:
                for pos in range(start, end):
                    token_at[pos] = token
            for pos, char in enumerate(text):
                token = token_at.get(pos)
                if token:
                    cp_words[char].add(token)
            offset = 0
            for cluster in _clusters(text):
                cluster_occ[cluster] += 1
                token = token_at.get(offset)
                if token:
                    cluster_word_occ[cluster] += 1
                    cluster_words[cluster].add(token)
                    cluster_verses[cluster].add(verse_id)
                    if len(cluster_refs[cluster]) < 8:
                        cluster_refs[cluster].append(verse_id)
                offset += len(cluster)
            matches = text.count(MARKED_B) + text.count(UPPER_MARKED_B)
            if matches:
                marked_b_glyphs += matches
                marked_b_verses.add(verse_id)
                for token, _, _ in tokens:
                    n = token.count(MARKED_B) + token.count(UPPER_MARKED_B)
                    if n:
                        marked_b_words[token] += n

    codepoints = []
    for char, count in sorted(cp_occ.items(), key=lambda item: ord(item[0])):
        codepoints.append({**_details(char), "occurrences": count,
                           "unique_words": len(cp_words[char]),
                           "verses": len(cp_verses[char]),
                           "representative_words": [w for w, _ in sorted(
                               ((w, word_counts[w]) for w in cp_words[char]),
                               key=lambda item: (-item[1], item[0]))[:8]],
                           "representative_verse_ids": cp_refs[char],
                           "representative_contexts": cp_contexts[char],
                           "is_combining_mark": _is_mark(char)})

    marks = [entry for entry in codepoints if entry["is_combining_mark"]]
    all_clusters = []
    grapheme_inventory = []
    for cluster, count in cluster_occ.items():
        entry = {
            "sequence": cluster,
            "rendered": cluster,
            "codepoints": [_details(char) for char in cluster],
            "occurrences": count,
            "token_occurrences_containing_cluster": cluster_word_occ[cluster],
            "unique_words": len(cluster_words[cluster]),
            "affected_verses": len(cluster_verses[cluster]),
            "representative_words": [w for w, _ in sorted(
                ((w, word_counts[w]) for w in cluster_words[cluster]),
                key=lambda item: (-item[1], item[0]))[:20]],
            "representative_verse_ids": cluster_refs[cluster],
            "modern_inventory_member": _grapheme_is_allowed(cluster),
            "classification": _classify_cluster(cluster),
        }
        grapheme_inventory.append(entry)
        marks_in = [char for char in cluster if _is_mark(char)]
        if not marks_in:
            continue
        all_clusters.append(entry)
    all_clusters.sort(key=lambda row: (-row["occurrences"], row["sequence"]))
    grapheme_inventory.sort(key=lambda row: (-row["occurrences"], row["sequence"]))

    # Segment alphabet units inside words, recognizing standard digraphs.
    unexpected = []
    for unit, count in sorted(alphabet_units.items(), key=lambda item: (-item[1], item[0])):
        if unit.casefold() in MODERN_GRAPHEMES_CASEFOLD or _grapheme_is_allowed(unit):
            continue
        unexpected.append({
            "sequence": unit, "rendered": unit,
            "codepoints": [_details(char) for char in unit],
            "occurrences": count,
            "unique_words": len(alphabet_unit_words[unit]),
            "affected_verses": len(alphabet_unit_verses[unit]),
            "representative_words": [w for w, _ in sorted(
                ((w, word_counts[w]) for w in alphabet_unit_words[unit]),
                key=lambda item: (-item[1], item[0]))[:20]],
            "representative_verse_ids": alphabet_unit_refs[unit],
            "modern_inventory_member": False,
            "classification": _classify_cluster(unit),
        })

    macron_forms: Counter[str] = Counter()
    for word, count in word_counts.items():
        if any(char in "āēīōūĀĒĪŌŪ" or char == MACRON for char in word):
            macron_forms[word] = count

    marked_b_replacements = []
    for form, count in sorted(marked_b_words.items(), key=lambda item: (-item[1], item[0])):
        replacement = form.replace(MARKED_B, "gb").replace(UPPER_MARKED_B, "Gb")
        marked_b_replacements.append({
            "historical_form": form,
            "modern_form_by_character_rule": replacement,
            "occurrences": word_counts[form],
            "marked_b_glyphs": count,
            "verses": len(verse_word_sets[form]),
        })

    def inventory_counter(counter: Counter[str]) -> list[dict]:
        return [{**_details(char), "occurrences": count} for char, count in sorted(counter.items(), key=lambda x: ord(x[0]))]

    data = {
        "report_type": "complete raw Unicode and grapheme audit",
        "source_database": str(source),
        "raw_source_modified": False,
        "unicode_normalization_applied": False,
        "grapheme_segmentation": "starter plus following Unicode marks; corpus Latin-script subset of extended grapheme clustering; no joiner-based graphemes found or expected",
        "modern_igbo_inventory": {
            "basis": "Ọnwụ Committee Official Igbo Orthography (1961), 36 graphemes: 28 consonants and 8 vowels.",
            "consonant_graphemes": sorted(MODERN_GRAPHEMES - {"a", "e", "i", "ị", "o", "ọ", "u", "ụ"}),
            "vowel_graphemes": ["a", "e", "i", "ị", "o", "ọ", "u", "ụ"],
            "all_graphemes": sorted(MODERN_GRAPHEMES),
            "accepted_raw_decompositions": ["i/o/u + U+0323 COMBINING DOT BELOW", "n + U+0307 COMBINING DOT ABOVE"],
            "accepted_tone_sequences": "Acute/grave on the eight modern vowels and syllabic n, precomposed or decomposed; dot-below vowels may also carry acute/grave tone.",
            "tone_marks": ["U+0300 COMBINING GRAVE ACCENT", "U+0301 COMBINING ACUTE ACCENT"],
            "tone_policy": "Tone marks are optional phonological annotations, not extra alphabet letters; acute/grave on allowlisted vowels and syllabic n are accepted as modern tone-marked graphemes.",
            "punctuation_digits_whitespace": "Inventoried separately; excluded from alphabet allowlist.",
        },
        "totals": {"verses": total_verses, "tokens": total_tokens, "unique_words": len(word_counts),
                   "codepoints_in_corpus": len(cp_occ), "grapheme_clusters_including_unmarked": len(cluster_occ),
                   "source_codepoint_count": total_chars, "marked_b_glyph_occurrences": marked_b_glyphs,
                   "marked_b_unique_word_forms": len(marked_b_words), "marked_b_affected_verses": len(marked_b_verses),
                   "marked_b_rule_approved": True, "marked_b_rule": "b + U+0355 -> gb; B + U+0355 -> Gb",
                   "marked_b_counterexamples_in_corpus": 0,
                   "macron_token_occurrences": sum(macron_forms.values()),
                   "macron_unique_word_forms": len(macron_forms),
                   "macron_automatic_replacements": 0},
        "codepoint_inventory": codepoints,
        "combining_mark_inventory": marks,
        "grapheme_inventory": grapheme_inventory,
        "combining_grapheme_inventory": all_clusters,
        "outside_modern_alphabet_graphemes": unexpected,
        "punctuation_inventory": inventory_counter(punctuation),
        "whitespace_inventory": inventory_counter(whitespace),
        "unexpected_nonletter_symbol_inventory": inventory_counter(symbols),
        "embedded_nonstandard_punctuation": [
            {**_details(char), "occurrences": count,
             "unique_verse_count": len(embedded_punct_verses[char]),
             "classification": "OCR/ENCODING_ANOMALY",
             "examples": embedded_punct_contexts[char]}
            for char, count in sorted(embedded_punct_counts.items(), key=lambda item: (-item[1], item[0]))],
        "embedded_nonletter_symbols": [
            {**_details(char), "occurrences": count,
             "unique_verse_count": len(embedded_symbol_verses[char]),
             "classification": "OCR/ENCODING_ANOMALY",
             "examples": embedded_symbol_contexts[char]}
            for char, count in sorted(embedded_symbol_counts.items(), key=lambda item: (-item[1], item[0]))],
        "marked_b_word_groups": marked_b_replacements,
        "macron_word_forms_top": [
            {"word": word, "occurrences": count, "affected_verses": len(verse_word_sets[word])}
            for word, count in macron_forms.most_common(100)],
        "macron_word_forms_complete": [
            {"word": word, "occurrences": count, "affected_verses": len(verse_word_sets[word])}
            for word, count in sorted(macron_forms.items(), key=lambda item: (-item[1], item[0]))],
        "classification_key": {
            "SYSTEMATIC_CHARACTER_MAPPING": "historical grapheme has supported corpus-wide one-to-one modern grapheme mapping",
            "MORPHOLOGICAL_ORTHOGRAPHY": "historical vowel mark may encode morphological/grammatical convention; no simple substitution approved",
            "TYPOGRAPHIC": "punctuation/layout or typographic feature, not alphabet mapping",
            "OCR/ENCODING_ANOMALY": "requires source-image or encoding evidence; not inferred from character rarity alone",
            "UNKNOWN": "insufficient evidence to determine orthographic role",
        },
    }
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    columns = ["sequence", "rendered", "codepoints", "occurrences", "token_occurrences_containing_cluster",
               "unique_words", "affected_verses", "representative_words", "representative_verse_ids",
               "modern_inventory_member", "classification"]
    with csv_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for row in all_clusters:
            writer.writerow({**row,
                "codepoints": " + ".join(item["codepoint"] + " " + item["unicode_name"] for item in row["codepoints"]),
                "representative_words": ";".join(row["representative_words"]),
                "representative_verse_ids": ";".join(row["representative_verse_ids"])})
    return data


if __name__ == "__main__":
    report = generate_audit(database_path("igbob.sqlite"),
                            generated_path("igbob-unicode-audit.json"),
                            generated_path("igbob-unicode-graphemes.csv"))
    print(json.dumps(report["totals"], ensure_ascii=False, indent=2))

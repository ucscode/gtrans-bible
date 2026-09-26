"""Local-only analysis helpers for historical Igbo research corpora.

This module deliberately has no imports from the production Bible parser or
database builder. It produces report files only; it cannot build an edition
database.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator


DEFAULT_IA_OCR_URL = (
    "https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29_djvu.xml"
)
DEFAULT_RESEARCH_ROOT = Path("data/research")
ANALYSIS_VERSION = 1

APOSTROPHES = frozenset("'’ʼʹ‘ʻ＇")
HYPHENS = frozenset("-‐‑‒–—﹘﹣－")
VOWELS = "aeiouAEIOU"
MACRON_LETTERS = frozenset("āēīōūĀĒĪŌŪ")
KNOWN_MARKS = frozenset(
    "\u0300\u0301\u0304\u0307\u0308\u030c\u0323\u0327\u0355"
)
WORD_SEPARATORS = APOSTROPHES | HYPHENS
CONTROL_NAMES = {"\n": "LINE FEED", "\r": "CARRIAGE RETURN", "\t": "CHARACTER TABULATION"}


def _unicode_name(character: str) -> str:
    return unicodedata.name(character, CONTROL_NAMES.get(character, "<unnamed>"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_research_source(url: str, destination: Path, force: bool = False) -> str:
    """Download OCR atomically to the caller-selected research path."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size and not force:
        return sha256_file(destination)

    request = urllib.request.Request(url, headers={"User-Agent": "igbo-corpus-research/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response:
        with tempfile.NamedTemporaryFile(
            "wb", delete=False, dir=destination.parent, prefix=".ocr-download-"
        ) as handle:
            temporary = Path(handle.name)
            try:
                while chunk := response.read(1024 * 1024):
                    handle.write(chunk)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    os.replace(temporary, destination)
    return sha256_file(destination)


def copy_research_source(source: Path, destination: Path, force: bool = False) -> str:
    """Copy an existing OCR file into ignored research storage atomically."""

    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size and not force:
        return sha256_file(destination)
    with source.open("rb") as input_file, tempfile.NamedTemporaryFile(
        "wb", delete=False, dir=destination.parent, prefix=".ocr-copy-"
    ) as output_file:
        temporary = Path(output_file.name)
        try:
            while chunk := input_file.read(1024 * 1024):
                output_file.write(chunk)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
    os.replace(temporary, destination)
    return sha256_file(destination)


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def iter_djvu_lines(path: Path) -> Iterator[tuple[str, str, tuple[int, ...]]]:
    """Yield ``(page-id, line-text, word-confidence-values)`` from IA DjVu XML."""

    for _, page in ET.iterparse(path, events=("end",)):
        if _tag(page) != "OBJECT":
            continue
        page_id = "unknown"
        for param in page.iter():
            if _tag(param) == "PARAM" and param.attrib.get("name") == "PAGE":
                page_id = param.attrib.get("value", "unknown")
                break
        for line in page.iter():
            if _tag(line) != "LINE":
                continue
            words: list[str] = []
            confidences: list[int] = []
            for word in line.iter():
                if _tag(word) != "WORD":
                    continue
                value = "".join(word.itertext()).strip()
                if value:
                    words.append(value)
                confidence = word.attrib.get("x-confidence")
                if confidence and confidence.isdigit():
                    confidences.append(int(confidence))
            if words:
                yield page_id, " ".join(words), tuple(confidences)
        page.clear()


def iter_text_lines(path: Path) -> Iterator[tuple[str, str, tuple[int, ...]]]:
    with path.open("r", encoding="utf-8", errors="replace") as source:
        for line_number, line in enumerate(source, start=1):
            yield f"line-{line_number}", line.rstrip("\r\n"), ()


def _is_word_char(character: str) -> bool:
    return unicodedata.category(character)[0] in {"L", "M", "N"}


def tokenize_with_spans(text: str) -> Iterator[tuple[str, int, int]]:
    """Unicode-aware word tokenizer retaining apostrophe/hyphen joins."""

    index = 0
    while index < len(text):
        if not _is_word_char(text[index]):
            index += 1
            continue
        start = index
        index += 1
        while index < len(text):
            character = text[index]
            if _is_word_char(character):
                index += 1
                continue
            if (
                character in WORD_SEPARATORS
                and index + 1 < len(text)
                and _is_word_char(text[index - 1])
                and _is_word_char(text[index + 1])
            ):
                index += 1
                continue
            break
        yield text[start:index], start, index


def _macron_positions(token: str) -> list[int]:
    positions: list[int] = []
    for index, character in enumerate(token):
        if character in MACRON_LETTERS:
            positions.append(index)
        elif character == "\u0304" and index > 0 and token[index - 1] in VOWELS:
            positions.append(index - 1)
    return positions


def _nfc_changed_input_characters(text: str) -> int:
    """Count input codepoints in base-plus-mark clusters changed by NFC."""

    changed = 0
    cluster = ""
    for character in text:
        if unicodedata.category(character).startswith("M"):
            cluster += character
            continue
        if cluster and unicodedata.normalize("NFC", cluster) != cluster:
            changed += len(cluster)
        cluster = character
    if cluster and unicodedata.normalize("NFC", cluster) != cluster:
        changed += len(cluster)
    return changed


def _marked_b_sequences(token: str) -> list[tuple[str, int]]:
    sequences: list[tuple[str, int]] = []
    index = 0
    while index < len(token):
        if token[index] not in "bB":
            index += 1
            continue
        end = index + 1
        while end < len(token) and unicodedata.category(token[end]).startswith("M"):
            end += 1
        if end > index + 1:
            sequences.append((token[index:end], index))
            index = end
        else:
            index += 1
    return sequences


def _pattern_key(token: str) -> str:
    normalized = unicodedata.normalize("NFC", token).casefold()
    normalized = normalized.replace("’", "'").replace("‘", "'")
    prefixes = ("nā", "nē", "gā", "gē")
    for prefix in prefixes:
        if normalized.startswith(prefix):
            return prefix + "…"
    for leader, label in (("a", "a+"), ("m'", "m’+"), ("ga", "ga+")):
        for prefix in prefixes:
            if normalized.startswith(leader + prefix):
                return label + prefix + "…"
    positions = _macron_positions(token)
    if not positions:
        return "no-macron"
    first = positions[0]
    if first == 0:
        return "initial-macron-other"
    if first == len(token) - 1:
        return "final-macron"
    return "medial-macron-other"


def _is_candidate_prefix_pattern(pattern: str) -> bool:
    return any(
        pattern.startswith(prefix)
        for prefix in ("nā…", "nē…", "gā…", "gē…", "a+", "m’+", "ga+")
    )


def _candidate_family(pattern: str) -> str | None:
    for family in ("nā", "nē", "gā", "gē"):
        if family + "…" in pattern:
            return family
    return None


def _short_context(line: str, start: int, end: int, limit: int = 150) -> str:
    left = max(0, start - limit // 2)
    right = min(len(line), end + limit // 2)
    snippet = " ".join(line[left:right].split())
    if len(snippet) > limit:
        snippet = snippet[: limit - 1] + "…"
    return snippet


def analyze_lines(
    lines: Iterable[tuple[str, str, tuple[int, ...]]],
    *,
    source_sha256: str | None = None,
    source_name: str | None = None,
) -> dict:
    """Analyze OCR text without modifying or normalizing the source."""

    codepoints: Counter[str] = Counter()
    mark_counts: Counter[str] = Counter()
    mark_bases: dict[str, Counter[str]] = defaultdict(Counter)
    token_counts: Counter[str] = Counter()
    normalized_variants: Counter[tuple[str, str]] = Counter()
    macron_token_counts: Counter[str] = Counter()
    macron_token_neighbors: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {"preceding": Counter(), "following": Counter(), "marked_characters": Counter()}
    )
    macron_groups: dict[str, Counter[str]] = defaultdict(Counter)
    macron_samples: dict[str, list[dict]] = defaultdict(list)
    marked_b_counts: Counter[str] = Counter()
    marked_b_sequences: Counter[str] = Counter()
    marked_b_neighbors: dict[str, Counter[str]] = defaultdict(Counter)
    marked_b_samples: dict[str, list[dict]] = defaultdict(list)
    apostrophe_counts: Counter[str] = Counter()
    apostrophe_roles: dict[str, Counter[str]] = defaultdict(Counter)
    hyphen_counts: Counter[str] = Counter()
    hyphen_roles: dict[str, Counter[str]] = defaultdict(Counter)
    hyphenated_tokens: Counter[str] = Counter()
    auxiliary_prefix_tokens: dict[str, Counter[str]] = defaultdict(Counter)
    suspicious_chars: Counter[str] = Counter()
    suspicious_sequences: Counter[str] = Counter()
    low_confidence_tokens: Counter[str] = Counter()
    confidence_values: Counter[int] = Counter()
    page_count_ids: set[str] = set()

    total_chars = total_lines = total_tokens = total_word_chars = 0
    tokens_with_macron = tokens_with_marked_b = 0
    macron_occurrences = marked_b_occurrences = 0
    normalization_changed_chars = 0
    nfc_total_chars = nfd_total_chars = 0
    low_confidence_occurrences = confidence_count = aligned_confidence_tokens = 0

    for page_id, line, confidences in lines:
        total_lines += 1
        page_count_ids.add(page_id)
        # Include one newline between OCR lines in the corpus character totals.
        corpus_line = line + "\n"
        total_chars += len(corpus_line)
        codepoints.update(corpus_line)
        nfc_line = unicodedata.normalize("NFC", corpus_line)
        nfd_line = unicodedata.normalize("NFD", corpus_line)
        nfc_total_chars += len(nfc_line)
        nfd_total_chars += len(nfd_line)
        normalization_changed_chars += _nfc_changed_input_characters(corpus_line)

        for confidence in confidences:
            confidence_values[confidence] += 1
            confidence_count += 1

        for index, character in enumerate(line):
            if character in APOSTROPHES:
                apostrophe_counts[character] += 1
                left = index > 0 and _is_word_char(line[index - 1])
                right = index + 1 < len(line) and _is_word_char(line[index + 1])
                role = "internal" if left and right else "edge-or-punctuation"
                apostrophe_roles[character][role] += 1
            if character in HYPHENS:
                hyphen_counts[character] += 1
                left = index > 0 and _is_word_char(line[index - 1])
                right = index + 1 < len(line) and _is_word_char(line[index + 1])
                role = "internal" if left and right else "edge-or-punctuation"
                hyphen_roles[character][role] += 1

        tokens = list(tokenize_with_spans(line))
        total_tokens += len(tokens)
        total_word_chars += sum(len(token) for token, _, _ in tokens)
        confidence_alignment = len(confidences) == len(tokens)
        if confidence_alignment:
            aligned_confidence_tokens += len(tokens)
        for token_index, (token, start, end) in enumerate(tokens):
            token_counts[token] += 1
            nfc_token = unicodedata.normalize("NFC", token)
            if nfc_token != token:
                normalized_variants[(nfc_token, token)] += 1

            token_confidence = confidences[token_index] if confidence_alignment else None
            if token_confidence is not None and token_confidence < 70:
                low_confidence_tokens[token] += 1
                low_confidence_occurrences += 1

            for index, character in enumerate(token):
                if unicodedata.category(character).startswith("M"):
                    mark_counts[character] += 1
                    base_index = index - 1
                    while base_index >= 0 and unicodedata.category(token[base_index]).startswith("M"):
                        base_index -= 1
                    base = token[base_index] if base_index >= 0 else "<no-base>"
                    mark_bases[character][base] += 1
                    if character not in KNOWN_MARKS:
                        suspicious_sequences[base + character] += 1
                category = unicodedata.category(character)
                if category in {"Cc", "Cf", "Cs", "Co", "Cn"} or character == "\ufffd":
                    suspicious_chars[character] += 1

            marks = _macron_positions(token)
            if marks:
                macron_token_counts[token] += 1
                tokens_with_macron += 1
                macron_occurrences += len(marks)
                group = _pattern_key(token)
                macron_groups[group][token] += 1
                for mark_position in marks:
                    marked_character = token[mark_position]
                    preceding = token[mark_position - 1] if mark_position > 0 else "<word-start>"
                    following_position = mark_position + 1
                    following = token[following_position] if following_position < len(token) else "<word-end>"
                    macron_token_neighbors[token]["marked_characters"][marked_character] += 1
                    macron_token_neighbors[token]["preceding"][preceding] += 1
                    macron_token_neighbors[token]["following"][following] += 1
                if len(macron_samples[group]) < 5:
                    first_mark = marks[0]
                    macron_samples[group].append(
                        {
                            "token": token,
                            "marked_character": token[first_mark],
                            "preceding_character": token[first_mark - 1] if first_mark > 0 else "<word-start>",
                            "following_character": token[first_mark + 1] if first_mark + 1 < len(token) else "<word-end>",
                            "page": page_id,
                            "context": _short_context(line, start, end),
                        }
                    )

            b_sequences = _marked_b_sequences(token)
            if b_sequences:
                marked_b_counts[token] += 1
                tokens_with_marked_b += 1
                marked_b_occurrences += len(b_sequences)
                for sequence, index in b_sequences:
                    marked_b_sequences[sequence] += 1
                    before = token[index - 1] if index > 0 else "<word-start>"
                    after_index = index + len(sequence)
                    after = token[after_index] if after_index < len(token) else "<word-end>"
                    marked_b_neighbors[sequence][before + "_" + after] += 1
                    if len(marked_b_samples[sequence]) < 8:
                        marked_b_samples[sequence].append(
                            {
                                "token": token,
                                "page": page_id,
                                "left": before,
                                "right": after,
                                "confidence": token_confidence,
                                "context": _short_context(line, start, end),
                            }
                        )

            prefix_pattern = _pattern_key(token)
            if prefix_pattern != "no-macron" and _is_candidate_prefix_pattern(prefix_pattern):
                auxiliary_prefix_tokens[prefix_pattern][token] += 1

            if any(character in HYPHENS for character in token):
                hyphenated_tokens[token] += 1

    # Suspicious codepoints in corpus text can also occur outside words.
    for character, count in codepoints.items():
        category = unicodedata.category(character)
        if (category in {"Cc", "Cf", "Cs", "Co", "Cn"} and character not in "\n\r\t") or character == "\ufffd":
            suspicious_chars[character] = count

    def pct(numerator: int, denominator: int) -> float:
        return round(100 * numerator / denominator, 4) if denominator else 0.0

    unique_marked_b = len(marked_b_counts)
    unique_macron_tokens = len(macron_token_counts)
    distinct_suspicious_sequences = len(suspicious_sequences)
    macron_group_report = []
    for group, forms in sorted(macron_groups.items(), key=lambda item: (-sum(item[1].values()), item[0])):
        count = sum(forms.values())
        if _is_candidate_prefix_pattern(group):
            category = "candidate historical auxiliary/verb-prefix family; syntax must confirm"
            confidence = "medium"
        elif group == "medial-macron-other":
            category = "lexical/quantity or unresolved morphology; lexical review"
            confidence = "low"
        else:
            category = "position-based pattern; linguistic category unresolved"
            confidence = "low"
        family = _candidate_family(group)
        hyphenated_forms = [
            (token, form_count)
            for token, form_count in forms.items()
            if any(character in HYPHENS for character in token)
        ]
        immediate_hyphen_count = 0
        if family:
            for token, form_count in forms.items():
                normalized = unicodedata.normalize("NFC", token).casefold().replace("’", "'").replace("‘", "'")
                family_index = normalized.find(family)
                after_family = family_index + len(family)
                if family_index >= 0 and after_family < len(normalized) and normalized[after_family] in HYPHENS:
                    immediate_hyphen_count += form_count
        macron_group_report.append(
            {
                "pattern": group,
                "token_occurrences": count,
                "unique_forms": len(forms),
                "percent_of_macron_bearing_tokens": pct(count, tokens_with_macron),
                "likely_category": category,
                "confidence": confidence,
                "hyphenated_token_occurrences": sum(n for _, n in hyphenated_forms),
                "family_immediately_followed_by_hyphen_occurrences": immediate_hyphen_count,
                "top_hyphenated_forms": [
                    {"token": token, "count": n}
                    for token, n in sorted(hyphenated_forms, key=lambda item: (-item[1], item[0]))[:20]
                ],
                "top_forms": [
                    {"token": token, "count": n}
                    for token, n in forms.most_common(20)
                ],
                "short_context_samples": macron_samples[group],
            }
        )

    return {
        "analysis_version": ANALYSIS_VERSION,
        "source": {"name": source_name, "sha256": source_sha256},
        "rights_notice": "Research-only OCR; not cleared for redistribution or edition database use.",
        "corpus": {
            "ocr_lines": total_lines,
            "pages_with_ocr": len(page_count_ids),
            "characters_including_line_breaks": total_chars,
            "word_characters": total_word_chars,
            "tokens": total_tokens,
            "unique_tokens": len(token_counts),
            "tokens_with_macron": tokens_with_macron,
            "percent_tokens_with_macron": pct(tokens_with_macron, total_tokens),
            "unique_macron_bearing_forms": unique_macron_tokens,
            "macron_codepoint_occurrences": macron_occurrences,
            "tokens_with_marked_b": tokens_with_marked_b,
            "percent_tokens_with_marked_b": pct(tokens_with_marked_b, total_tokens),
            "unique_marked_b_forms": unique_marked_b,
            "marked_b_occurrences": marked_b_occurrences,
            "normalization_changed_characters_nfc": normalization_changed_chars,
            "nfc_character_length": nfc_total_chars,
            "nfd_character_length": nfd_total_chars,
            "tokens_with_low_ocr_confidence_below_70": low_confidence_occurrences,
            "percent_low_confidence_tokens_with_confidence": pct(low_confidence_occurrences, aligned_confidence_tokens),
            "ocr_words_with_confidence": confidence_count,
            "tokens_aligned_to_word_confidence": aligned_confidence_tokens,
            "distinct_suspicious_unicode_sequences": distinct_suspicious_sequences,
            "suspicious_unicode_sequence_occurrences": sum(suspicious_sequences.values()),
        },
        "unicode": {
            "codepoint_inventory": [
                {
                    "character": character,
                    "codepoint": f"U+{ord(character):04X}",
                    "name": _unicode_name(character),
                    "category": unicodedata.category(character),
                    "count": count,
                }
                for character, count in sorted(codepoints.items(), key=lambda item: ord(item[0]))
            ],
            "combining_marks": [
                {
                    "mark": character,
                    "codepoint": f"U+{ord(character):04X}",
                    "name": _unicode_name(character),
                    "count": count,
                    "base_characters": [
                        {"base": base, "count": n}
                        for base, n in mark_bases[character].most_common()
                    ],
                }
                for character, count in sorted(mark_counts.items(), key=lambda item: ord(item[0]))
            ],
            "normalization": {
                "nfc_equals_source": normalization_changed_chars == 0,
                "source_characters": total_chars,
                "nfc_characters": nfc_total_chars,
                "nfd_characters": nfd_total_chars,
                "changed_character_count_nfc": normalization_changed_chars,
                "distinct_raw_to_nfc_token_variants": len(normalized_variants),
            },
            "suspicious_codepoints": [
                {
                    "character": character,
                    "codepoint": f"U+{ord(character):04X}",
                    "name": _unicode_name(character),
                    "category": unicodedata.category(character),
                    "count": count,
                }
                for character, count in sorted(suspicious_chars.items(), key=lambda item: (-item[1], ord(item[0])))
            ],
            "suspicious_mark_sequences": [
                {"sequence": sequence, "codepoints": [f"U+{ord(c):04X}" for c in sequence], "count": count}
                for sequence, count in suspicious_sequences.most_common()
            ],
        },
        "macrons": {
            "target_letters": sorted(MACRON_LETTERS),
            "bearing_token_occurrences": tokens_with_macron,
            "unique_bearing_forms": unique_macron_tokens,
            "mark_occurrences": macron_occurrences,
            "patterns": macron_group_report,
        },
        "marked_b": {
            "bearing_token_occurrences": tokens_with_marked_b,
            "unique_forms": unique_marked_b,
            "mark_occurrences": marked_b_occurrences,
            "sequences": [
                {
                    "sequence": sequence,
                    "codepoints": [f"U+{ord(c):04X}" for c in sequence],
                    "count": count,
                    "adjacent_grapheme_pairs": [
                        {"pair": pair, "count": n}
                        for pair, n in marked_b_neighbors[sequence].most_common()
                    ],
                    "short_context_samples": marked_b_samples[sequence],
                }
                for sequence, count in marked_b_sequences.most_common()
            ],
        },
        "punctuation": {
            "apostrophes": [
                {
                    "character": character,
                    "codepoint": f"U+{ord(character):04X}",
                    "name": _unicode_name(character),
                    "count": count,
                    "roles": dict(sorted(apostrophe_roles[character].items())),
                }
                for character, count in apostrophe_counts.most_common()
            ],
            "hyphens_and_dashes": [
                {
                    "character": character,
                    "codepoint": f"U+{ord(character):04X}",
                    "name": _unicode_name(character),
                    "count": count,
                    "roles": dict(sorted(hyphen_roles[character].items())),
                }
                for character, count in hyphen_counts.most_common()
            ],
            "hyphenated_token_occurrences": sum(hyphenated_tokens.values()),
            "top_hyphenated_tokens": [
                {"token": token, "count": count} for token, count in hyphenated_tokens.most_common(100)
            ],
        },
        "auxiliary_prefix_candidates": [
            {
                "prefix": prefix,
                "token_occurrences": sum(forms.values()),
                "unique_forms": len(forms),
                "hyphenated_token_occurrences": sum(
                    count for token, count in forms.items() if any(character in HYPHENS for character in token)
                ),
                "family_immediately_followed_by_hyphen_occurrences": sum(
                    count
                    for token, count in forms.items()
                    if (family := _candidate_family(prefix))
                    and (position := unicodedata.normalize("NFC", token).casefold().replace("’", "'").find(family)) >= 0
                    and position + len(family) < len(token)
                    and token[position + len(family)] in HYPHENS
                ),
                "top_forms": [{"token": token, "count": count} for token, count in forms.most_common(100)],
            }
            for prefix, forms in sorted(auxiliary_prefix_tokens.items())
        ],
        "ocr_quality": {
            "confidence_threshold": 70,
            "confidence_distribution": [
                {"confidence": value, "count": count}
                for value, count in sorted(confidence_values.items())
            ],
            "low_confidence_token_samples": [
                {"token": token, "count": count} for token, count in low_confidence_tokens.most_common(100)
            ],
            "note": "OCR confidence is a vendor signal, not a linguistic or orthographic judgment.",
        },
        "estimates": {
            "mechanically_promising_macron_token_occurrences": sum(
                sum(forms.values())
                for group, forms in macron_groups.items()
                if _is_candidate_prefix_pattern(group)
            ),
            "mechanically_promising_denominator": tokens_with_macron,
            "mechanically_promising_percent_of_macron_bearing_tokens": pct(
                sum(
                    sum(forms.values())
                    for group, forms in macron_groups.items()
                    if _is_candidate_prefix_pattern(group)
                ),
                tokens_with_macron,
            ),
            "lexical_or_context_review_percent_of_macron_bearing_tokens": pct(
                sum(
                    sum(forms.values())
                    for group, forms in macron_groups.items()
                    if not _is_candidate_prefix_pattern(group)
                ),
                tokens_with_macron,
            ),
            "unexplained_percent_of_all_tokens": None,
            "non_candidate_percent_of_macron_bearing_tokens": pct(
                sum(
                    sum(forms.values())
                    for group, forms in macron_groups.items()
                    if not _is_candidate_prefix_pattern(group)
                ),
                tokens_with_macron,
            ),
            "caveat": (
                "These are pattern-frequency estimates, not automatic-normalization coverage. "
                "Candidate auxiliary families require syntax/lemma checks; OCR errors are included."
            ),
        },
        "_report_data": {
            "token_counts": token_counts,
            "macron_token_counts": macron_token_counts,
            "macron_token_neighbors": macron_token_neighbors,
            "marked_b_counts": marked_b_counts,
            "normalized_variants": normalized_variants,
            "page_ids": sorted(page_count_ids),
        },
    }


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_reports(result: dict, output_dir: Path) -> None:
    """Write deterministic research reports under a caller-validated directory."""

    output_dir.mkdir(parents=True, exist_ok=True)
    private = result.pop("_report_data")
    try:
        summary_path = output_dir / "summary.json"
        summary_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _write_csv(
            output_dir / "unicode-codepoints.csv",
            ["character", "codepoint", "unicode_name", "category", "count"],
            (
                {
                    "character": row["character"],
                    "codepoint": row["codepoint"],
                    "unicode_name": row["name"],
                    "category": row["category"],
                    "count": row["count"],
                }
                for row in result["unicode"]["codepoint_inventory"]
            ),
        )
        _write_csv(
            output_dir / "combining-marks.csv",
            ["mark", "codepoint", "unicode_name", "count", "base_characters_json"],
            (
                {
                    "mark": row["mark"],
                    "codepoint": row["codepoint"],
                    "unicode_name": row["name"],
                    "count": row["count"],
                    "base_characters_json": json.dumps(row["base_characters"], ensure_ascii=False, sort_keys=True),
                }
                for row in result["unicode"]["combining_marks"]
            ),
        )
        _write_csv(
            output_dir / "token-frequencies.csv",
            ["token", "count"],
            ({"token": token, "count": count} for token, count in sorted(private["token_counts"].items(), key=lambda item: (-item[1], item[0]))),
        )
        _write_csv(
            output_dir / "macron-token-frequencies.csv",
            [
                "token",
                "count",
                "pattern",
                "marked_characters_json",
                "preceding_characters_json",
                "following_characters_json",
            ],
            (
                {
                    "token": token,
                    "count": count,
                    "pattern": _pattern_key(token),
                    "marked_characters_json": json.dumps(
                        private["macron_token_neighbors"][token]["marked_characters"],
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "preceding_characters_json": json.dumps(
                        private["macron_token_neighbors"][token]["preceding"],
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "following_characters_json": json.dumps(
                        private["macron_token_neighbors"][token]["following"],
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
                for token, count in sorted(private["macron_token_counts"].items(), key=lambda item: (-item[1], item[0]))
            ),
        )
        _write_csv(
            output_dir / "marked-b-token-frequencies.csv",
            ["token", "count"],
            ({"token": token, "count": count} for token, count in sorted(private["marked_b_counts"].items(), key=lambda item: (-item[1], item[0]))),
        )
        _write_csv(
            output_dir / "normalization-variants.csv",
            ["nfc_form", "observed_form", "count"],
            (
                {"nfc_form": nfc, "observed_form": raw, "count": count}
                for (nfc, raw), count in sorted(private["normalized_variants"].items(), key=lambda item: (item[0][0], item[0][1]))
            ),
        )
    finally:
        result["_report_data"] = private


def analyze_source(path: Path, *, source_url: str | None = None) -> dict:
    path = path.expanduser().resolve()
    if path.suffix.lower() == ".xml":
        lines = iter_djvu_lines(path)
    else:
        lines = iter_text_lines(path)
    return analyze_lines(lines, source_sha256=sha256_file(path), source_name=source_url or path.name)


def validate_research_output(path: Path, repository_root: Path) -> Path:
    """Prevent reports from being written into production or tracked paths."""

    root = (repository_root / DEFAULT_RESEARCH_ROOT).resolve()
    candidate = (repository_root / path).resolve() if not path.is_absolute() else path.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"research output must be inside {root}")
    return candidate


def corpus_report_lines(result: dict) -> list[str]:
    corpus = result["corpus"]
    estimate = result["estimates"]
    return [
        f"OCR characters: {corpus['characters_including_line_breaks']:,}",
        f"Tokens: {corpus['tokens']:,}",
        f"Unique tokens: {corpus['unique_tokens']:,}",
        f"Macron-bearing tokens: {corpus['tokens_with_macron']:,} ({corpus['percent_tokens_with_macron']}% of all tokens)",
        f"Marked-b tokens: {corpus['tokens_with_marked_b']:,} ({corpus['percent_tokens_with_marked_b']}% of all tokens)",
        f"Unique marked-b forms: {corpus['unique_marked_b_forms']:,}",
        f"Suspicious Unicode sequences: {corpus['distinct_suspicious_unicode_sequences']:,} distinct / {corpus['suspicious_unicode_sequence_occurrences']:,} occurrences",
        f"Candidate auxiliary-pattern share: {estimate['mechanically_promising_percent_of_macron_bearing_tokens']}% of macron-bearing token occurrences (not total Bible text)",
    ]

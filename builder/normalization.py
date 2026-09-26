"""Auditable, conservative orthographic normalization for supplied text.

This module is independent of the Bible parsers, databases, translation code,
and research corpus. Unapproved hypotheses are inspection-only.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Pattern


RULESET_VERSION = "0.1.0"
DEFAULT_RULESET = Path(__file__).resolve().parent.parent / "data/normalization/rules.json"
DEFAULT_LEXICON = Path(__file__).resolve().parent.parent / "data/normalization/reviewed-lexicon.json"

RULE_CATEGORIES = {
    "safe_character",
    "morphological_context",
    "lexical",
    "phrase",
    "review",
}
CONFIDENCE_LEVELS = {"PROVEN", "STRONGLY SUPPORTED", "TENTATIVE", "UNRESOLVED"}
RULE_STATUSES = {"APPROVED", "PENDING", "REJECTED"}


class NormalizationConfigurationError(ValueError):
    """Raised when normalization rule data is invalid or unsafe to apply."""


@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: str
    description: str
    confidence: str
    source: str
    version: str
    status: str
    find: str
    replacement: str
    priority: int = 0
    regex: bool = False

    @property
    def approved(self) -> bool:
        # Research confidence alone can never authorize a change.
        return self.status == "APPROVED" and self.confidence == "PROVEN"

    @lru_cache(maxsize=512)
    def matcher(self) -> Pattern[str]:
        if self.regex:
            try:
                return re.compile(self.find)
            except re.error as exc:
                raise NormalizationConfigurationError(
                    f"invalid regex in rule {self.rule_id}: {exc}"
                ) from exc
        return re.compile(re.escape(self.find))


@dataclass(frozen=True)
class ReviewDetector:
    detector_id: str
    description: str
    phenomenon: str
    source: str
    version: str
    pattern: str

    @lru_cache(maxsize=512)
    def matcher(self) -> Pattern[str]:
        try:
            return re.compile(self.pattern, re.IGNORECASE)
        except re.error as exc:
            raise NormalizationConfigurationError(
                f"invalid regex in detector {self.detector_id}: {exc}"
            ) from exc


@dataclass(frozen=True)
class LexiconEntry:
    historical: str
    modern: str
    status: str
    confidence: str
    evidence: str
    notes: str
    version: str


@dataclass(frozen=True)
class Transformation:
    rule_id: str
    category: str
    original: str
    replacement: str
    start: int
    end: int
    description: str
    source: str
    version: str


@dataclass(frozen=True)
class ReviewItem:
    rule_id: str
    phenomenon: str
    text: str
    start: int
    end: int
    description: str
    source: str


@dataclass(frozen=True)
class UnknownItem:
    text: str
    start: int
    end: int
    reason: str


@dataclass(frozen=True)
class IntegrityIssue:
    code: str
    message: str
    start: int | None = None
    end: int | None = None


@dataclass(frozen=True)
class SourceIntegrityProfile:
    """Optional external expectations for known source graphemes.

    Counts must come from a trusted source specification or visual collation;
    the normalizer never infers expected marks from ordinary b/o spellings.
    """

    expected_minimum_sequences: tuple[tuple[str, int], ...] = ()
    profile_id: str = "unspecified"


@dataclass(frozen=True)
class NormalizationResult:
    original_text: str
    normalized_text: str
    ruleset_version: str
    lexicon_version: str
    transformations: tuple[Transformation, ...]
    review_items: tuple[ReviewItem, ...]
    unknown_items: tuple[UnknownItem, ...]
    integrity_issues: tuple[IntegrityIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_text": self.original_text,
            "normalized_text": self.normalized_text,
            "ruleset_version": self.ruleset_version,
            "lexicon_version": self.lexicon_version,
            "transformations": [asdict(item) for item in self.transformations],
            "review_items": [asdict(item) for item in self.review_items],
            "unknown_items": [asdict(item) for item in self.unknown_items],
            "integrity_issues": [asdict(item) for item in self.integrity_issues],
        }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NormalizationConfigurationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise NormalizationConfigurationError(f"{path} must contain a JSON object")
    return value


def _required_text(row: dict[str, Any], field: str, context: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise NormalizationConfigurationError(f"{context}.{field} must be a non-empty string")
    return value


def _validate_confidence(value: str, context: str) -> None:
    if value not in CONFIDENCE_LEVELS:
        raise NormalizationConfigurationError(f"{context} has unsupported confidence {value!r}")


def _is_word_character(character: str) -> bool:
    return bool(character) and unicodedata.category(character)[0] in {"L", "M", "N"}


def _is_token_character_at(text: str, index: int) -> bool:
    character = text[index]
    if _is_word_character(character):
        return True
    if character in {"'", "’", "‘", "ʼ", "-", "‐", "‑", "‒", "–", "—"}:
        return (
            index > 0
            and index + 1 < len(text)
            and _is_word_character(text[index - 1])
            and _is_word_character(text[index + 1])
        )
    return False


def _has_token_boundaries(text: str, start: int, end: int) -> bool:
    before_is_token = start > 0 and _is_token_character_at(text, start - 1)
    after_is_token = end < len(text) and _is_token_character_at(text, end)
    return not before_is_token and not after_is_token


def _validate_unicode(text: str) -> None:
    for index, character in enumerate(text):
        if 0xD800 <= ord(character) <= 0xDFFF:
            raise ValueError(f"input contains an invalid Unicode surrogate at offset {index}")


class Normalizer:
    """Apply only explicitly approved, PROVEN transformations."""

    def __init__(
        self,
        ruleset_path: Path = DEFAULT_RULESET,
        lexicon_path: Path = DEFAULT_LEXICON,
    ) -> None:
        self.ruleset_path = Path(ruleset_path)
        self.lexicon_path = Path(lexicon_path)
        ruleset_data = _read_json(self.ruleset_path)
        self.ruleset_version = _required_text(ruleset_data, "version", "ruleset")
        self.rules = tuple(self._parse_rule(row, i) for i, row in enumerate(ruleset_data.get("rules", [])))
        self.detectors = tuple(
            self._parse_detector(row, i)
            for i, row in enumerate(ruleset_data.get("review_detectors", []))
        )
        self.lexicon_entries = self._load_lexicon()
        self.rules += tuple(self._lexicon_rule(entry, index) for index, entry in enumerate(self.lexicon_entries))
        ids = [rule.rule_id for rule in self.rules] + [det.detector_id for det in self.detectors]
        if len(ids) != len(set(ids)):
            raise NormalizationConfigurationError("rule and detector ids must be unique")
        self._validate_rules()

    def _parse_rule(self, row: dict[str, Any], index: int) -> Rule:
        if not isinstance(row, dict):
            raise NormalizationConfigurationError(f"rules[{index}] must be an object")
        context = f"rules[{index}]"
        rule_id = _required_text(row, "rule_id", context)
        category = _required_text(row, "category", context)
        if category not in RULE_CATEGORIES - {"review"}:
            raise NormalizationConfigurationError(f"{context} has unsupported transforming category {category!r}")
        confidence = _required_text(row, "confidence", context)
        _validate_confidence(confidence, context)
        status = _required_text(row, "status", context)
        if status not in RULE_STATUSES:
            raise NormalizationConfigurationError(f"{context} has unsupported status {status!r}")
        find = _required_text(row, "find", context)
        replacement = row.get("replacement")
        if not isinstance(replacement, str):
            raise NormalizationConfigurationError(f"{context}.replacement must be a string")
        regex = row.get("regex", False)
        if not isinstance(regex, bool):
            raise NormalizationConfigurationError(f"{context}.regex must be boolean")
        priority = row.get("priority", 0)
        if not isinstance(priority, int):
            raise NormalizationConfigurationError(f"{context}.priority must be an integer")
        if category == "morphological_context" and not regex:
            raise NormalizationConfigurationError(f"{context} must use regex=true")
        if category != "morphological_context" and regex:
            raise NormalizationConfigurationError(f"{context} regex is only supported for morphological_context")
        Rule(
            rule_id,
            category,
            _required_text(row, "description", context),
            confidence,
            _required_text(row, "source", context),
            _required_text(row, "version", context),
            status,
            find,
            replacement,
            priority,
            regex,
        ).matcher()
        return Rule(
            rule_id, category, row["description"], confidence, row["source"],
            row["version"], status, find, replacement, priority, regex
        )

    def _parse_detector(self, row: dict[str, Any], index: int) -> ReviewDetector:
        if not isinstance(row, dict):
            raise NormalizationConfigurationError(f"review_detectors[{index}] must be an object")
        context = f"review_detectors[{index}]"
        detector = ReviewDetector(
            _required_text(row, "detector_id", context),
            _required_text(row, "description", context),
            _required_text(row, "phenomenon", context),
            _required_text(row, "source", context),
            _required_text(row, "version", context),
            _required_text(row, "pattern", context),
        )
        detector.matcher()
        return detector

    def _load_lexicon(self) -> tuple[LexiconEntry, ...]:
        data = _read_json(self.lexicon_path)
        self.lexicon_version = _required_text(data, "version", "lexicon")
        rows = data.get("entries", [])
        if not isinstance(rows, list):
            raise NormalizationConfigurationError("lexicon.entries must be a list")
        entries = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise NormalizationConfigurationError(f"lexicon.entries[{index}] must be an object")
            context = f"lexicon.entries[{index}]"
            status = _required_text(row, "status", context)
            if status not in RULE_STATUSES:
                raise NormalizationConfigurationError(f"{context} has unsupported status {status!r}")
            confidence = _required_text(row, "confidence", context)
            _validate_confidence(confidence, context)
            entries.append(
                LexiconEntry(
                    _required_text(row, "historical", context),
                    _required_text(row, "modern", context),
                    status,
                    confidence,
                    _required_text(row, "evidence", context),
                    str(row.get("notes", "")),
                    _required_text(row, "version", context),
                )
            )
        return tuple(entries)

    @staticmethod
    def _lexicon_rule(entry: LexiconEntry, index: int) -> Rule:
        return Rule(
            rule_id=f"lexicon:{index}:{entry.historical}",
            category="lexical",
            description=entry.notes or f"Reviewed lexical mapping for {entry.historical}",
            confidence=entry.confidence,
            source=entry.evidence,
            version=entry.version,
            status=entry.status,
            find=entry.historical,
            replacement=entry.modern,
        )

    def _validate_rules(self) -> None:
        transforming = [rule for rule in self.rules if rule.category != "review"]
        if any(not rule.find for rule in transforming):
            raise NormalizationConfigurationError("transforming rules cannot match an empty string")
        for rule in transforming:
            matcher = rule.matcher()
            if rule.regex and matcher.match("") is not None:
                raise NormalizationConfigurationError(f"rule {rule.rule_id} may not match an empty string")
        # Reject direct rewrite chains that would make a second pass change output.
        approved = [rule for rule in transforming if rule.approved]
        for source_rule in approved:
            replacement = source_rule.replacement
            for target_rule in approved:
                for match in target_rule.matcher().finditer(replacement):
                    if target_rule.category != "lexical" or _has_token_boundaries(replacement, match.start(), match.end()):
                        raise NormalizationConfigurationError(
                            f"approved replacement from {source_rule.rule_id} would trigger {target_rule.rule_id}; "
                            "ruleset would not be idempotent"
                        )

    def normalize(self, text: str, source_profile: SourceIntegrityProfile | None = None) -> NormalizationResult:
        _validate_unicode(text)
        normalized, transformations = self._normalize_once(text)
        # Cross-boundary rewrite chains may only appear after adjacent matches.
        second_pass, _ = self._normalize_once(normalized)
        if second_pass != normalized:
            raise NormalizationConfigurationError("approved rules produced non-idempotent output")
        # Review/unknown findings describe what remains unresolved in the
        # normalized output. Source text is still preserved separately and all
        # transformations retain offsets into that original input.
        reviews = self._find_reviews(normalized)
        unknown = self._find_unknowns(normalized, reviews)
        issues = self.validate_source_integrity(text, source_profile)
        return NormalizationResult(
            original_text=text,
            normalized_text=normalized,
            ruleset_version=self.ruleset_version,
            lexicon_version=self.lexicon_version,
            transformations=tuple(transformations),
            review_items=tuple(reviews),
            unknown_items=tuple(unknown),
            integrity_issues=tuple(issues),
        )

    def _normalize_once(self, text: str) -> tuple[str, list[Transformation]]:
        active = [rule for rule in self.rules if rule.approved and rule.category != "review"]
        matches_by_start: dict[int, list[tuple[Rule, re.Match[str]]]] = defaultdict(list)
        for rule in active:
            for match in rule.matcher().finditer(text):
                if rule.category == "lexical" and not _has_token_boundaries(text, match.start(), match.end()):
                    continue
                matches_by_start[match.start()].append((rule, match))
        output: list[str] = []
        audit: list[Transformation] = []
        cursor = 0
        while cursor < len(text):
            candidates = matches_by_start.get(cursor, [])
            if not candidates:
                output.append(text[cursor])
                cursor += 1
                continue
            rule, match = min(
                candidates,
                key=lambda candidate: (
                    -(candidate[1].end() - candidate[1].start()),
                    -candidate[0].priority,
                    candidate[0].rule_id,
                ),
            )
            if match.end() == cursor:
                raise NormalizationConfigurationError(f"rule {rule.rule_id} matched zero characters")
            replacement = match.expand(rule.replacement) if rule.regex else rule.replacement
            original = text[match.start():match.end()]
            output.append(replacement)
            audit.append(
                Transformation(
                    rule_id=rule.rule_id,
                    category=rule.category,
                    original=original,
                    replacement=replacement,
                    start=match.start(),
                    end=match.end(),
                    description=rule.description,
                    source=rule.source,
                    version=rule.version,
                )
            )
            cursor = match.end()
        return "".join(output), audit

    def _find_reviews(self, text: str) -> list[ReviewItem]:
        found: list[ReviewItem] = []
        for rule in self.rules:
            if rule.approved or rule.status == "REJECTED":
                continue
            for match in rule.matcher().finditer(text):
                if rule.category == "lexical" and not _has_token_boundaries(text, match.start(), match.end()):
                    continue
                found.append(
                    ReviewItem(
                        rule.rule_id,
                        rule.category,
                        match.group(0),
                        match.start(),
                        match.end(),
                        f"Not transformed: rule is {rule.status.lower()} or confidence is not PROVEN. {rule.description}",
                        rule.source,
                    )
                )
        for detector in self.detectors:
            for match in detector.matcher().finditer(text):
                found.append(
                    ReviewItem(
                        detector.detector_id,
                        detector.phenomenon,
                        match.group(0),
                        match.start(),
                        match.end(),
                        detector.description,
                        detector.source,
                    )
                )
        found.sort(key=lambda item: (item.start, item.end, item.rule_id))
        return found

    @staticmethod
    def _is_historical_marker(character: str) -> bool:
        return character in "āēīōūĀĒĪŌŪ\u0355" or unicodedata.category(character) == "Mn"

    def _find_unknowns(self, text: str, reviews: list[ReviewItem]) -> list[UnknownItem]:
        known_spans = [(item.start, item.end) for item in reviews]
        found = []
        index = 0
        while index < len(text):
            if not self._is_historical_marker(text[index]):
                index += 1
                continue
            start = index
            while start > 0 and _is_word_character(text[start - 1]):
                start -= 1
            end = index + 1
            while end < len(text) and _is_word_character(text[end]):
                end += 1
            if not any(left <= index < right for left, right in known_spans):
                found.append(
                    UnknownItem(
                        text=text[start:end],
                        start=start,
                        end=end,
                        reason="contains a historical-looking diacritic/grapheme not covered by a review detector",
                    )
                )
            index = max(index + 1, end)
        return found

    @staticmethod
    def validate_source_integrity(
        text: str,
        profile: SourceIntegrityProfile | None = None,
    ) -> list[IntegrityIssue]:
        issues = []
        for index, character in enumerate(text):
            if character == "\ufffd":
                issues.append(IntegrityIssue("replacement_character", "input contains Unicode replacement character", index, index + 1))
        if profile is not None:
            for sequence, expected in profile.expected_minimum_sequences:
                if expected < 0 or not sequence:
                    raise ValueError("source profile counts must be non-negative and sequences non-empty")
                observed = text.count(sequence)
                if observed < expected:
                    issues.append(
                        IntegrityIssue(
                            "expected_sequence_missing",
                            f"profile {profile.profile_id!r} expects at least {expected} occurrence(s) of "
                            f"{sequence!r}; observed {observed}. Input may have lost source distinctions.",
                        )
                    )
        return issues


def normalize(
    text: str,
    *,
    ruleset_path: Path = DEFAULT_RULESET,
    lexicon_path: Path = DEFAULT_LEXICON,
    source_profile: SourceIntegrityProfile | None = None,
) -> NormalizationResult:
    """Convenience API using the project's current ruleset and lexicon."""

    return Normalizer(ruleset_path=ruleset_path, lexicon_path=lexicon_path).normalize(
        text,
        source_profile=source_profile,
    )

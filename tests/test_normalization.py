from __future__ import annotations

import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from builder.normalization import (
    NormalizationConfigurationError,
    Normalizer,
    SourceIntegrityProfile,
    normalize,
)
from builder.cli import main as cli_main


class NormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.rules_path = self.root / "rules.json"
        self.lexicon_path = self.root / "lexicon.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def configure(self, rules=None, entries=None, detectors=None) -> Normalizer:
        self.rules_path.write_text(
            json.dumps(
                {
                    "version": "test-1",
                    "rules": rules or [],
                    "review_detectors": detectors or [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.lexicon_path.write_text(
            json.dumps({"version": "lex-test-1", "entries": entries or []}, ensure_ascii=False),
            encoding="utf-8",
        )
        return Normalizer(self.rules_path, self.lexicon_path)

    @staticmethod
    def entry(historical: str, modern: str, status="APPROVED", confidence="PROVEN") -> dict:
        return {
            "historical": historical,
            "modern": modern,
            "status": status,
            "confidence": confidence,
            "evidence": "synthetic fixture source",
            "notes": "synthetic test mapping",
            "version": "lex-test-1",
        }

    @staticmethod
    def rule(rule_id, category, find, replacement, *, priority=0, regex=False, status="APPROVED", confidence="PROVEN"):
        return {
            "rule_id": rule_id,
            "category": category,
            "description": "synthetic fixture rule",
            "confidence": confidence,
            "source": "synthetic fixture source",
            "version": "test-1",
            "status": status,
            "find": find,
            "replacement": replacement,
            "priority": priority,
            "regex": regex,
        }

    def test_approved_lexicon_mapping_transforms_and_is_audited(self):
        normalizer = self.configure(entries=[self.entry("histword", "modernword")])
        result = normalizer.normalize("(histword), histword!")
        self.assertEqual(result.normalized_text, "(modernword), modernword!")
        self.assertEqual(len(result.transformations), 2)
        first = result.transformations[0]
        self.assertEqual((first.original, first.replacement, first.start, first.end), ("histword", "modernword", 1, 9))
        self.assertEqual(first.rule_id, "lexicon:0:histword")
        self.assertEqual(first.source, "synthetic fixture source")

    def test_pending_and_non_proven_lexicon_entries_do_not_transform(self):
        normalizer = self.configure(
            entries=[
                self.entry("pendingword", "newword", status="PENDING"),
                self.entry("hypothesis", "newform", confidence="STRONGLY SUPPORTED"),
            ]
        )
        result = normalizer.normalize("pendingword hypothesis")
        self.assertEqual(result.normalized_text, "pendingword hypothesis")
        self.assertEqual(result.transformations, ())
        self.assertEqual(len(result.review_items), 2)

    def test_approved_morphology_and_b_variants_normalize_conservatively(self):
        source = "nēme nākpọ gēme gābu ab\u0355uru mḅe"
        result = normalize(source)
        self.assertEqual(result.normalized_text, "na-eme na-akpọ ga-eme ga-abu agburu mgbe")
        self.assertEqual(
            {item.rule_id for item in result.transformations},
            {
                "historical.na-e-participle-to-onwu-na-e",
                "historical.na-a-participle-to-onwu-na-a",
                "historical.ga-e-participle-to-onwu-ga-e",
                "historical.ga-a-participle-to-onwu-ga-a",
                "union.implosive-b-to-onwu-gb",
                "union.implosive-b-dot-below-to-onwu-gb",
            },
        )
        self.assertEqual(result.unknown_items, ())

    def test_macron_expansion_preserves_stem_and_excludes_fused_or_exception_forms(self):
        source = "nēme nākpa gēme gāṅu nēkasa anēme M'gēme n'ala ga-azụ"
        result = normalize(source)
        self.assertEqual(result.normalized_text, "na-eme na-akpa ga-eme ga-aṅu nēkasa a na-eme M ga-eme n'ala ga-azụ")
        self.assertEqual(
            [item.rule_id for item in result.transformations],
            [
                "historical.na-e-participle-to-onwu-na-e",
                "historical.na-a-participle-to-onwu-na-a",
                "historical.ga-e-participle-to-onwu-ga-e",
                "historical.ga-a-participle-to-onwu-ga-a",
                "historical.fused-impersonal-n-e-to-separated",
                "historical.fused-first-person-g-e-to-separated",
            ],
        )
        self.assertTrue(any(item.text == "nēkasa" for item in result.review_items))
        self.assertFalse(any(item.text in {"anēme", "M'gēme"} for item in result.review_items))


    def test_fused_subject_and_future_progressive_macrons_split_with_standard_boundaries(self):
        normalizer = Normalizer()
        source = "M'nēme m'nākpa M'gēme M'gābu, a nēme anākpọ Agēme ganēme ganākpọ M'ganēme m'ganākpọ Aganēsi aganāchọta."
        expected = "M na-eme m na-akpa M ga-eme M ga-abu, a na-eme a na-akpọ A ga-eme ga na-eme ga na-akpọ M ga na-eme m ga na-akpọ A ga na-esi a ga na-achọta."
        result = normalizer.normalize(source)
        self.assertEqual(result.normalized_text, expected)
        self.assertEqual(normalizer.normalize(result.normalized_text).normalized_text, expected)
        self.assertEqual(result.to_dict(), normalizer.normalize(source).to_dict())
        self.assertEqual(len(result.transformations), 13)

    def test_fused_macron_rules_respect_token_edges_hyphens_apostrophes_and_stems(self):
        normalizer = Normalizer()
        source = "xM'gēme M'gēme-ya n'M'gēme nēkasa ganēme #M'gēme"
        result = normalizer.normalize(source)
        self.assertEqual(result.normalized_text, "xM'gēme M ga-eme-ya n'M'gēme nēkasa ga na-eme #M ga-eme")
        self.assertEqual(normalizer.normalize(result.normalized_text).normalized_text, result.normalized_text)
        self.assertTrue(any(item.text == "nēkasa" for item in result.review_items))

    def test_marked_b_dot_below_maps_but_vowels_and_syllabic_ng_are_preserved(self):
        result = normalize("ḅa Ḅa nēhụ gāhụ ṅ ṅụ ị ọ ụ")
        self.assertEqual(result.normalized_text, "gba Gba na-ehụ ga-ahụ ṅ ṅụ ị ọ ụ")

    def test_marked_b_rule_boundaries_case_punctuation_repeats_and_audit(self):
        normalizer = Normalizer()
        source = "Mb\u0355e mb\u0355e, b\u0355a! B\u0355a; plain b, gb; ab\u0355uru n'ab\u0355uru."
        result = normalizer.normalize(source)
        self.assertEqual(result.normalized_text, "Mgbe mgbe, gba! Gba; plain b, gb; agburu n'agburu.")
        self.assertEqual(len(result.transformations), 6)
        self.assertEqual(
            [item.rule_id for item in result.transformations],
            [
                "union.implosive-b-to-onwu-gb",
                "union.implosive-b-to-onwu-gb",
                "union.implosive-b-to-onwu-gb",
                "union.implosive-B-to-onwu-Gb",
                "union.implosive-b-to-onwu-gb",
                "union.implosive-b-to-onwu-gb",
            ],
        )
        self.assertEqual(result.to_dict(), normalizer.normalize(source).to_dict())
        self.assertEqual(normalizer.normalize(result.normalized_text).normalized_text, result.normalized_text)

    def test_marked_b_rule_and_proven_macron_prefix_preserve_other_text(self):
        normalizer = Normalizer()
        result = normalizer.normalize("tib\u0355uru nēme b mb\u0355e")
        self.assertEqual(result.normalized_text, "tigburu na-eme b mgbe")
        self.assertEqual(len(result.transformations), 3)
        self.assertEqual(result.review_items, ())

    def test_reviewed_ulo_ikwu_macron_family_maps_to_doubled_u_only(self):
        normalizer = Normalizer()
        family = [
            entry for entry in normalizer.lexicon_entries
            if entry.version == "0.5.0" and "ulo-ikwū" in entry.historical.lower()
        ]
        self.assertEqual(len(family), 43)
        source = " ".join(entry.historical for entry in family)
        expected = " ".join(entry.modern for entry in family)
        first = normalizer.normalize(source)
        second = normalizer.normalize(source)
        self.assertEqual(first.normalized_text, expected)
        self.assertEqual(len(first.transformations), 43)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(normalizer.normalize(first.normalized_text).normalized_text, expected)

        punctuated = normalizer.normalize("(ulo-ikwū), n'ulo-ikwū-ya; Ulo-ikwū!")
        self.assertEqual(punctuated.normalized_text, "(ulo-ikwuu), n'ulo-ikwuu-ya; Ulo-ikwuu!")
        self.assertEqual(normalizer.normalize("ikwū ūlọ-ikwū n'ulu-ikwū-gi").normalized_text,
                         "ikwū ūlọ-ikwū n'ulu-ikwū-gi")

    def test_exact_lexicon_entry_does_not_split_hyphenated_or_apostrophe_tokens(self):
        normalizer = Normalizer()
        result = normalizer.normalize("ab\u0355uru-ya n'ab\u0355uru")
        self.assertEqual(result.normalized_text, "agburu-ya n'agburu")
        self.assertEqual([item.rule_id for item in result.transformations], [
            "union.implosive-b-to-onwu-gb", "union.implosive-b-to-onwu-gb"
        ])

    def test_unknown_marked_text_and_unmatched_text_are_preserved(self):
        source = "A hū, unknown exactly!"
        result = normalize(source)
        self.assertEqual(result.normalized_text, source)
        self.assertEqual(result.unknown_items[0].text, "hū")
        self.assertEqual(result.unknown_items[0].start, 2)

    def test_safe_character_phrase_and_morphological_rules_are_supported(self):
        normalizer = self.configure(
            rules=[
                self.rule("char.map", "safe_character", "x", "y"),
                self.rule("phrase.map", "phrase", "old phrase", "new phrase"),
                self.rule("morph.map", "morphological_context", r"(?<!\w)old-(\w+)", r"new-\1", regex=True),
            ]
        )
        result = normalizer.normalize("x old phrase old-word")
        self.assertEqual(result.normalized_text, "y new phrase new-word")
        self.assertEqual([item.rule_id for item in result.transformations], ["char.map", "phrase.map", "morph.map"])

    def test_review_detector_flags_without_change(self):
        normalizer = self.configure(
            detectors=[{
                "detector_id": "review.fixture",
                "description": "inspect this token",
                "phenomenon": "fixture pattern",
                "source": "fixture reference",
                "version": "test-1",
                "pattern": r"oldform",
            }]
        )
        result = normalizer.normalize("oldform stays")
        self.assertEqual(result.normalized_text, "oldform stays")
        self.assertEqual(result.review_items[0].text, "oldform")

    def test_deterministic_output_and_idempotence(self):
        normalizer = self.configure(entries=[self.entry("before", "after")])
        first = normalizer.normalize("before and before")
        second = normalizer.normalize("before and before")
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(normalizer.normalize(first.normalized_text).normalized_text, first.normalized_text)

    def test_overlapping_rules_use_longest_match_then_priority(self):
        normalizer = self.configure(
            rules=[
                self.rule("short", "phrase", "ab", "X", priority=100),
                self.rule("long", "phrase", "abc", "Y"),
            ]
        )
        result = normalizer.normalize("abc ab")
        self.assertEqual(result.normalized_text, "Y X")
        self.assertEqual([item.rule_id for item in result.transformations], ["long", "short"])

    def test_unicode_is_preserved_and_surrogates_are_rejected(self):
        source = "Ị́gbō — ḃ"
        result = normalize(source)
        self.assertEqual(result.normalized_text, source)
        self.assertTrue(result.unknown_items)
        with self.assertRaises(ValueError):
            normalize("bad\ud800text")

    def test_punctuation_and_whitespace_are_untouched(self):
        normalizer = self.configure(entries=[self.entry("token", "word")])
        source = "  ‘token’,\n\ttoken!  "
        result = normalizer.normalize(source)
        self.assertEqual(result.normalized_text, "  ‘word’,\n\tword!  ")

    def test_no_lossy_ocr_reconstruction_for_plain_b_or_o(self):
        source = "b o boro obodo"
        result = normalize(source)
        self.assertEqual(result.normalized_text, source)
        self.assertEqual(result.transformations, ())

    def test_integrity_profile_reports_expected_mark_loss(self):
        result = normalize(
            "plain text",
            source_profile=SourceIntegrityProfile(
                expected_minimum_sequences=(("b\u0355", 2),),
                profile_id="collated-fixture",
            ),
        )
        self.assertEqual(result.normalized_text, "plain text")
        self.assertEqual(result.integrity_issues[0].code, "expected_sequence_missing")

    def test_non_idempotent_rule_chains_are_rejected(self):
        with self.assertRaises(NormalizationConfigurationError):
            self.configure(
                rules=[
                    self.rule("first", "safe_character", "a", "b"),
                    self.rule("second", "safe_character", "b", "c"),
                ]
            )

    def test_default_ruleset_applies_proven_marked_b_and_morphological_rules(self):
        result = normalize("nēme nākpọ gēme gābu ab\u0355uru b o")
        self.assertEqual(result.normalized_text, "na-eme na-akpọ ga-eme ga-abu agburu b o")
        self.assertEqual(len(result.transformations), 5)
        self.assertEqual(result.review_items, ())

    def test_cli_direct_text_report_is_database_free_and_read_only(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = cli_main(["normalize", "--text", "nēme", "--dry-run", "--report"])
        report = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(report["normalized_text"], "na-eme")
        self.assertEqual(len(report["transformations"]), 1)
        self.assertFalse(report["review_items"])


if __name__ == "__main__":
    unittest.main()

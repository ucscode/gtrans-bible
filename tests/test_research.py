import tempfile
import unittest
from pathlib import Path

from builder.research import analyze_lines, validate_research_output, write_reports


def analyze(text: str) -> dict:
    lines = [(f"page-{index}", line, ()) for index, line in enumerate(text.splitlines(), start=1)]
    return analyze_lines(lines, source_sha256="fixture-sha256", source_name="synthetic fixture")


class ResearchAnalysisTests(unittest.TestCase):
    def test_inventory_combining_sequences_and_marked_b(self):
        result = analyze("nēme ab\u0355uru a\u0304")
        inventory = {row["codepoint"]: row["count"] for row in result["unicode"]["codepoint_inventory"]}
        self.assertEqual(inventory["U+0355"], 1)
        self.assertEqual(inventory["U+0304"], 1)
        marks = {row["codepoint"]: row for row in result["unicode"]["combining_marks"]}
        self.assertEqual(marks["U+0355"]["base_characters"][0]["base"], "b")
        self.assertEqual(result["corpus"]["tokens"], 3)
        self.assertEqual(result["corpus"]["tokens_with_marked_b"], 1)
        self.assertEqual(result["corpus"]["unique_marked_b_forms"], 1)
        self.assertEqual(result["marked_b"]["sequences"][0]["sequence"], "b\u0355")

    def test_unicode_normalization_variants(self):
        result = analyze("ọ o\u0323")
        self.assertFalse(result["unicode"]["normalization"]["nfc_equals_source"])
        self.assertEqual(result["unicode"]["normalization"]["distinct_raw_to_nfc_token_variants"], 1)
        self.assertGreater(result["unicode"]["normalization"]["changed_character_count_nfc"], 0)

    def test_macron_groups_are_structural_and_denominator_is_explicit(self):
        result = analyze("nābia nābia gābu ikwū ā agēme anēme M’gēme")
        self.assertEqual(result["corpus"]["tokens_with_macron"], 8)
        patterns = {row["pattern"]: row for row in result["macrons"]["patterns"]}
        self.assertEqual(patterns["nā…"]["token_occurrences"], 2)
        self.assertEqual(patterns["gā…"]["token_occurrences"], 1)
        self.assertEqual(patterns["a+gē…"]["token_occurrences"], 1)
        self.assertEqual(patterns["a+nē…"]["token_occurrences"], 1)
        self.assertEqual(patterns["m’+gē…"]["token_occurrences"], 1)
        sample = patterns["nā…"]["short_context_samples"][0]
        self.assertIn("marked_character", sample)
        self.assertIn("preceding_character", sample)
        self.assertIn("following_character", sample)
        self.assertEqual(
            result["estimates"]["mechanically_promising_denominator"],
            result["corpus"]["tokens_with_macron"],
        )
        self.assertEqual(result["estimates"]["mechanically_promising_percent_of_macron_bearing_tokens"], 75.0)

    def test_token_count_apostrophes_hyphens_and_confidence(self):
        lines = [("page-1", "n'ab͕uru na-abịa n'ab͕uru", (90, 50, 99))]
        result = analyze_lines(lines, source_name="fixture")
        self.assertEqual(result["corpus"]["tokens"], 3)
        self.assertEqual(result["corpus"]["tokens_with_marked_b"], 2)
        apostrophes = {row["character"]: row["count"] for row in result["punctuation"]["apostrophes"]}
        hyphens = {row["character"]: row["count"] for row in result["punctuation"]["hyphens_and_dashes"]}
        self.assertEqual(apostrophes["'"], 2)
        self.assertEqual(hyphens["-"], 1)
        self.assertEqual(result["corpus"]["tokens_with_low_ocr_confidence_below_70"], 1)

    def test_auxiliary_pattern_reports_hyphen_boundaries(self):
        result = analyze("gā-bu-kwa-ra gābu-kwa-ra")
        pattern = next(row for row in result["macrons"]["patterns"] if row["pattern"] == "gā…")
        self.assertEqual(pattern["hyphenated_token_occurrences"], 2)
        self.assertEqual(pattern["family_immediately_followed_by_hyphen_occurrences"], 1)

    def test_report_files_are_deterministic_and_output_is_restricted(self):
        result = analyze("nēme ab\u0355uru")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            write_reports(result, first)
            write_reports(result, second)
            names = {path.name for path in first.iterdir()}
            self.assertIn("summary.json", names)
            self.assertIn("token-frequencies.csv", names)
            self.assertIn("combining-marks.csv", names)
            for name in names:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(
                validate_research_output(Path("data/research/run"), root),
                (root / "data/research/run").resolve(),
            )
            with self.assertRaises(ValueError):
                validate_research_output(Path("data/generated"), root)


if __name__ == "__main__":
    unittest.main()

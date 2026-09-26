import unittest

from builder.books import chapter_id, verse_id
from builder.usfm import parse_book_text


class UsfmParsingTests(unittest.TestCase):
    def test_reference_ids(self):
        self.assertEqual(chapter_id("EXO", 13), "exo-13")
        self.assertEqual(verse_id("EXO", 13, 5), "exo-13-5")

    def test_multiline_unicode_and_markup(self):
        parsed = parse_book_text(
            """\\id TST - Fixture
\\toc1 Nnwale
\\c 1
\\s1 Isiokwu a abụghị amaokwu
\\p
\\v 1 Nke a bụ Igbo nʼederede\\f + \\fr 1:1 \\ft Ihe ọmụma\\f* gara nʼihu.
Nke a bụ ahịrị na-aga nʼihu.
\\v 2 Okwu \\nd pụrụ iche\\nd* na akụkụ ọzọ.
\\li1 Nke a bụkwa akụkụ amaokwu abụọ.
""",
            "fixture.usfm",
        )

        self.assertEqual(parsed.book.id, "tst")
        self.assertEqual(parsed.book.name, "Nnwale")
        self.assertEqual(parsed.source_verse_count, 2)
        self.assertEqual([verse.id for verse in parsed.verses], ["tst-1-1", "tst-1-2"])
        self.assertEqual(
            parsed.verses[0].content,
            "Nke a bụ Igbo nʼederede gara nʼihu. Nke a bụ ahịrị na-aga nʼihu.",
        )
        self.assertEqual(parsed.verses[1].content, "Okwu pụrụ iche na akụkụ ọzọ. Nke a bụkwa akụkụ amaokwu abụọ.")
        self.assertNotIn("\\f", parsed.verses[0].content)
        self.assertIn("nʼ", parsed.verses[0].content)

import sqlite3
import tempfile
import unittest
from pathlib import Path

from builder.database import build_databases
from builder.models import BibleData, Book, Chapter, Verse
from builder.translation import (
    TranslationError,
    translate_dataset,
    translation_status,
    validate_translation,
    source_hash,
)


class FakeTranslator:
    def __init__(self, prefix="EN:", fail_on_call=None):
        self.prefix = prefix
        self.fail_on_call = fail_on_call
        self.calls = []

    def translate(self, texts):
        self.calls.append(list(texts))
        if self.fail_on_call == len(self.calls):
            raise TranslationError("simulated API failure")
        return [self.prefix + text for text in texts]


class TranslationTests(unittest.TestCase):
    def _source(self, path, contents=("Nke mbụ nʼIgbo.", "Nke abụọ.")):
        canonical_path = path.parent / "bible.sqlite"
        data = BibleData(
            books=(Book("tst", "Nnwale", 1),),
            chapters=(Chapter("tst-1", "tst", 1),),
            verses=tuple(
                Verse(f"tst-1-{number}", "tst-1", number, content)
                for number, content in enumerate(contents, 1)
            ),
            source_verse_count=len(contents),
        )
        build_databases(data, canonical_path, path, require_oicb=False)
        return canonical_path

    def test_fresh_translation_resume_and_unicode_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "oicb.sqlite"
            target = Path(directory) / "english.sqlite"
            canonical = self._source(source)
            fake = FakeTranslator()

            first = translate_dataset(source, target, fake, canonical_path=canonical, require_oicb=False)
            self.assertEqual(first.translated_this_run, 2)
            self.assertEqual(fake.calls[0][0], "Nke mbụ nʼIgbo.")
            self.assertEqual(translation_status(source, target, canonical, require_oicb=False).missing_count, 0)
            with sqlite3.connect(target) as connection:
                self.assertEqual(connection.execute("SELECT content FROM verses WHERE verse_id = 'tst-1-1'").fetchone()[0], "EN:Nke mbụ nʼIgbo.")
                self.assertEqual(connection.execute("SELECT source_sha256 FROM verses WHERE verse_id = 'tst-1-1'").fetchone()[0], source_hash("Nke mbụ nʼIgbo."))

            resume_fake = FakeTranslator()
            resumed = translate_dataset(source, target, resume_fake, canonical_path=canonical, require_oicb=False)
            self.assertEqual(resumed.translated_this_run, 0)
            self.assertEqual(resume_fake.calls, [])
            self.assertEqual(validate_translation(source, target, canonical, require_oicb=False).completed_count, 2)

    def test_source_change_makes_only_stale_verse_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "oicb.sqlite"
            target = Path(directory) / "english.sqlite"
            canonical = self._source(source)
            translate_dataset(source, target, FakeTranslator(), canonical_path=canonical, require_oicb=False)
            self._source(source, ("Nke gbanwere.", "Nke abụọ."))

            status = translation_status(source, target, canonical, require_oicb=False)
            self.assertEqual(status.stale_count, 1)
            fake = FakeTranslator()
            translate_dataset(source, target, fake, canonical_path=canonical, require_oicb=False)
            self.assertEqual(fake.calls, [["Nke gbanwere."]])
            self.assertEqual(translation_status(source, target, canonical, require_oicb=False).stale_count, 0)

    def test_character_budget_and_max_verses_stop_before_request(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "oicb.sqlite"
            target = Path(directory) / "english.sqlite"
            canonical = self._source(source, ("12345", "67890"))
            fake = FakeTranslator()
            result = translate_dataset(source, target, fake, canonical_path=canonical, max_characters=5, require_oicb=False)
            self.assertEqual(result.characters_submitted_this_run, 5)
            self.assertEqual(fake.calls, [["12345"]])
            self.assertEqual(translation_status(source, target, canonical, require_oicb=False).missing_count, 1)

            target.unlink()
            fake = FakeTranslator()
            result = translate_dataset(source, target, fake, canonical_path=canonical, max_verses=1, require_oicb=False)
            self.assertEqual(result.translated_this_run, 1)
            self.assertEqual(len(fake.calls[0]), 1)

    def test_dry_run_has_no_client_call_or_write(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "oicb.sqlite"
            target = Path(directory) / "english.sqlite"
            canonical = self._source(source)
            fake = FakeTranslator()
            result = translate_dataset(source, target, fake, canonical_path=canonical, max_verses=1, dry_run=True, require_oicb=False)
            self.assertEqual(result.planned_count, 1)
            self.assertEqual(result.planned_characters, len("Nke mbụ nʼIgbo."))
            self.assertEqual(fake.calls, [])
            self.assertFalse(target.exists())

    def test_partial_failure_keeps_completed_batches(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "oicb.sqlite"
            target = Path(directory) / "english.sqlite"
            canonical = self._source(source, tuple(f"Amaokwu {number}" for number in range(1, 102)))
            fake = FakeTranslator(fail_on_call=2)
            with self.assertRaises(TranslationError):
                translate_dataset(source, target, fake, canonical_path=canonical, require_oicb=False)
            status = translation_status(source, target, canonical, require_oicb=False)
            self.assertEqual(status.completed_count, 100)
            self.assertEqual(status.missing_count, 1)

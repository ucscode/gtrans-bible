"""Resumable, build-time Google translation for the OICB SQLite dataset."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol, Sequence

from .config import load_repository_env, resolve_project_id
from .database import validate_oicb_database

SOURCE_LANGUAGE = "ig"
TARGET_LANGUAGE = "en"
MODEL_ID = "general/nmt"
DEFAULT_LOCATION = "global"

# Cloud Translation recommends less than 30,000 Unicode code points for a
# synchronous translateText request. OICB verses are all below the documented
# per-content 1,024-codepoint limit, and this lower batch cap leaves headroom.
MAX_BATCH_CODEPOINTS = 25_000
MAX_BATCH_VERSES = 100
MAX_CONTENT_CODEPOINTS = 1_024

TRANSLATION_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verses (
    verse_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    source_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS translation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'interrupted')),
    max_characters INTEGER,
    max_verses INTEGER,
    characters_submitted INTEGER NOT NULL DEFAULT 0,
    verses_translated INTEGER NOT NULL DEFAULT 0,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_translation_runs_status ON translation_runs(status);
"""


class TranslationError(RuntimeError):
    """Base class for translation configuration, API, and dataset errors."""


class TranslationConfigurationError(TranslationError):
    """Raised when the Google translation client cannot be configured."""


class Translator(Protocol):
    def translate(self, texts: Sequence[str]) -> list[str]:
        """Translate texts independently, preserving input order and length."""


class GoogleNmtTranslator:
    """Thin adapter around the official Google Cloud Translation v3 client."""

    def __init__(self, project_id: str | None = None, location: str = DEFAULT_LOCATION):
        load_repository_env()
        try:
            import google.auth
            from google.auth.exceptions import DefaultCredentialsError
            from google.cloud import translate_v3
        except ImportError as exc:
            raise TranslationConfigurationError(
                "Google translation requires the optional dependency; install "
                "with `python3 -m pip install -e '.[translate]'`"
            ) from exc

        try:
            credentials, detected_project = google.auth.default()
        except DefaultCredentialsError as exc:
            raise TranslationConfigurationError(
                "Google Application Default Credentials were not found. Set "
                "GOOGLE_APPLICATION_CREDENTIALS or run `gcloud auth "
                "application-default login`."
            ) from exc

        resolved_project = resolve_project_id(project_id) or detected_project
        if not resolved_project:
            raise TranslationConfigurationError(
                "Google Cloud project is not configured. Set GOOGLE_CLOUD_PROJECT "
                "or pass --project-id."
            )
        if not location:
            raise TranslationConfigurationError("Google Translation location cannot be empty")

        self.project_id = resolved_project
        self.location = location
        self.parent = f"projects/{resolved_project}/locations/{location}"
        self.model = f"{self.parent}/models/{MODEL_ID}"
        self._client = translate_v3.TranslationServiceClient(credentials=credentials)

    def translate(self, texts: Sequence[str]) -> list[str]:
        if not texts:
            return []
        if any(len(text) > MAX_CONTENT_CODEPOINTS for text in texts):
            raise TranslationError(
                f"a verse exceeds Google's {MAX_CONTENT_CODEPOINTS}-codepoint "
                "per-content limit; refusing to split a verse"
            )
        try:
            response = self._client.translate_text(
                contents=list(texts),
                mime_type="text/plain",
                source_language_code=SOURCE_LANGUAGE,
                target_language_code=TARGET_LANGUAGE,
                parent=self.parent,
                model=self.model,
            )
        except Exception as exc:
            raise TranslationError(f"Google Cloud Translation request failed: {exc}") from exc
        translations = [item.translated_text for item in response.translations]
        if len(translations) != len(texts):
            raise TranslationError(
                f"Google returned {len(translations)} translations for {len(texts)} inputs; "
                "the batch was not written"
            )
        if any(not value.strip() for value in translations):
            raise TranslationError("Google returned empty translated content; the batch was not written")
        return translations


@dataclass(frozen=True)
class SourceVerse:
    verse_id: str
    content: str
    source_sha256: str


@dataclass(frozen=True)
class TranslationStatus:
    source_count: int
    translated_count: int
    completed_count: int
    missing_count: int
    stale_count: int
    orphaned_count: int
    empty_count: int
    source_characters_remaining: int

    @property
    def eligible_count(self) -> int:
        return self.missing_count + self.stale_count

    @property
    def valid(self) -> bool:
        return self.stale_count == 0 and self.orphaned_count == 0 and self.empty_count == 0


@dataclass(frozen=True)
class TranslationSummary:
    status: TranslationStatus
    translated_this_run: int
    characters_submitted_this_run: int
    planned_count: int
    planned_characters: int
    stopped_reason: str | None = None


def source_hash(content: str) -> str:
    """Hash the exact Unicode content as UTF-8 without normalization."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _readonly_connection(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise TranslationError(f"database not found: {path}")
    connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _source_verses(source_db: Path) -> list[SourceVerse]:
    with _readonly_connection(source_db) as connection:
        try:
            rows = connection.execute(
                "SELECT verse_id, content FROM verses ORDER BY rowid"
            ).fetchall()
        except sqlite3.Error as exc:
            raise TranslationError(f"invalid OICB source database schema: {exc}") from exc
    return [SourceVerse(row["verse_id"], row["content"], source_hash(row["content"])) for row in rows]


def _ensure_translation_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(TRANSLATION_SCHEMA)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(verses)")}
    if "source_sha256" not in columns:
        raise TranslationError(
            "translation database has an incompatible verses table; "
            "source hashes are required for stale-source detection"
        )


class TranslationStore:
    """SQLite checkpoint store. Each successful API batch is one transaction."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        _ensure_translation_schema(self.connection)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def existing(self) -> dict[str, tuple[str, str]]:
        return {
            row[0]: (row[1], row[2])
            for row in self.connection.execute("SELECT verse_id, content, source_sha256 FROM verses")
        }

    def set_metadata(self, values: dict[str, str]) -> None:
        self.connection.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            values.items(),
        )
        self.connection.commit()

    def start_run(self, max_characters: int | None, max_verses: int | None) -> int:
        cursor = self.connection.execute(
            "INSERT INTO translation_runs(started_at, status, max_characters, max_verses) VALUES (?, 'running', ?, ?)",
            (_now(), max_characters, max_verses),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def save_batch(self, rows: Sequence[tuple[str, str, str]]) -> None:
        # A single small transaction means either every response in the batch
        # is checkpointed or none is. Earlier batches remain committed.
        with self.connection:
            self.connection.executemany(
                "INSERT INTO verses(verse_id, content, source_sha256) VALUES (?, ?, ?) "
                "ON CONFLICT(verse_id) DO UPDATE SET content=excluded.content, source_sha256=excluded.source_sha256",
                rows,
            )

    def update_run(self, run_id: int, characters: int, verses: int, status: str | None = None, error: str | None = None) -> None:
        if status is None:
            self.connection.execute(
                "UPDATE translation_runs SET characters_submitted = ?, verses_translated = ? WHERE id = ?",
                (characters, verses, run_id),
            )
        else:
            self.connection.execute(
                "UPDATE translation_runs SET finished_at = ?, status = ?, characters_submitted = ?, verses_translated = ?, error = ? WHERE id = ?",
                (_now(), status, characters, verses, error, run_id),
            )
        self.connection.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def translation_status(
    source_db: Path,
    translation_db: Path,
    canonical_path: Path | None = None,
    require_oicb: bool = True,
) -> TranslationStatus:
    if canonical_path is not None:
        validate_oicb_database(source_db, canonical_path, require_oicb=require_oicb)
    source = _source_verses(source_db)
    source_by_id = {verse.verse_id: verse for verse in source}
    if not translation_db.exists():
        return TranslationStatus(
            source_count=len(source), translated_count=0, completed_count=0,
            missing_count=len(source), stale_count=0, orphaned_count=0,
            empty_count=0, source_characters_remaining=sum(len(v.content) for v in source),
        )
    with _readonly_connection(translation_db) as connection:
        try:
            translated = connection.execute("SELECT verse_id, content, source_sha256 FROM verses").fetchall()
        except sqlite3.Error as exc:
            raise TranslationError(f"invalid translation database schema: {exc}") from exc
    translated_by_id = {row[0]: row for row in translated}
    missing = [verse for verse in source if verse.verse_id not in translated_by_id]
    stale = [verse for verse in source if verse.verse_id in translated_by_id and translated_by_id[verse.verse_id][2] != verse.source_sha256]
    orphaned = [row for row in translated if row[0] not in source_by_id]
    empty_count = sum(1 for row in translated if not str(row[1]).strip())
    return TranslationStatus(
        source_count=len(source),
        translated_count=len(translated),
        completed_count=len(source) - len(missing) - len(stale),
        missing_count=len(missing),
        stale_count=len(stale),
        orphaned_count=len(orphaned),
        empty_count=empty_count,
        source_characters_remaining=sum(len(v.content) for v in (*missing, *stale)),
    )


def _plan_batches(
    candidates: Sequence[SourceVerse],
    max_characters: int | None,
    max_verses: int | None,
) -> tuple[list[list[SourceVerse]], int, int, str | None]:
    if max_characters is not None and max_characters < 0:
        raise TranslationError("--max-characters must be non-negative")
    if max_verses is not None and max_verses < 0:
        raise TranslationError("--max-verses must be non-negative")
    selected = list(candidates[:max_verses] if max_verses is not None else candidates)
    batches: list[list[SourceVerse]] = []
    selected_count = 0
    selected_characters = 0
    reason = None
    for verse in selected:
        length = len(verse.content)
        if length > MAX_CONTENT_CODEPOINTS:
            raise TranslationError(
                f"{verse.verse_id} has {length} code points, over the "
                f"{MAX_CONTENT_CODEPOINTS}-codepoint API limit; refusing to split it"
            )
        if max_characters is not None and selected_characters + length > max_characters:
            reason = "character budget reached before next request"
            break
        if not batches or len(batches[-1]) >= MAX_BATCH_VERSES or sum(len(item.content) for item in batches[-1]) + length > MAX_BATCH_CODEPOINTS:
            batches.append([])
        batches[-1].append(verse)
        selected_count += 1
        selected_characters += length
    if max_verses is not None and selected_count >= max_verses and selected_count < len(candidates):
        reason = "max-verses reached"
    return batches, selected_count, selected_characters, reason


def _candidates(source: Sequence[SourceVerse], existing: dict[str, tuple[str, str]]) -> list[SourceVerse]:
    return [verse for verse in source if verse.verse_id not in existing or existing[verse.verse_id][1] != verse.source_sha256]


def _status_from_data(source: Sequence[SourceVerse], translated: dict[str, tuple[str, str]]) -> TranslationStatus:
    source_by_id = {verse.verse_id: verse for verse in source}
    missing = [verse for verse in source if verse.verse_id not in translated]
    stale = [verse for verse in source if verse.verse_id in translated and translated[verse.verse_id][1] != verse.source_sha256]
    orphaned = [verse_id for verse_id in translated if verse_id not in source_by_id]
    empty_count = sum(1 for content, _ in translated.values() if not content.strip())
    return TranslationStatus(
        source_count=len(source), translated_count=len(translated),
        completed_count=len(source) - len(missing) - len(stale),
        missing_count=len(missing), stale_count=len(stale), orphaned_count=len(orphaned),
        empty_count=empty_count,
        source_characters_remaining=sum(len(v.content) for v in (*missing, *stale)),
    )


def translate_dataset(
    source_db: Path,
    translation_db: Path,
    translator: Translator | None,
    max_characters: int | None = None,
    max_verses: int | None = None,
    dry_run: bool = False,
    progress: Callable[[int, int, int, int], None] | None = None,
    *,
    canonical_path: Path | None = None,
    require_oicb: bool = True,
) -> TranslationSummary:
    """Translate eligible verses, checkpointing every successful batch."""

    if canonical_path is not None:
        validate_oicb_database(source_db, canonical_path, require_oicb=require_oicb)
    source = _source_verses(source_db)
    if dry_run:
        existing: dict[str, tuple[str, str]] = {}
        if translation_db.exists():
            with _readonly_connection(translation_db) as connection:
                existing = {row[0]: (row[1], row[2]) for row in connection.execute("SELECT verse_id, content, source_sha256 FROM verses")}
        before = _status_from_data(source, existing)
    else:
        store = TranslationStore(translation_db)
        existing = store.existing()
        before = _status_from_data(source, existing)

    eligible = _candidates(source, existing)
    batches, planned_count, planned_characters, stopped_reason = _plan_batches(eligible, max_characters, max_verses)
    if dry_run:
        return TranslationSummary(before, 0, 0, planned_count, planned_characters, stopped_reason)
    if translator is None:
        raise TranslationConfigurationError("a translation client is required unless --dry-run is used")

    store.set_metadata({
        "source_language": SOURCE_LANGUAGE,
        "target_language": TARGET_LANGUAGE,
        "model": MODEL_ID,
        "provider": "Google Cloud Translation Advanced v3",
        "source_database": source_db.name,
    })
    run_id = store.start_run(max_characters, max_verses)
    translated_count = 0
    submitted_characters = 0
    try:
        for batch in batches:
            texts = [verse.content for verse in batch]
            translated = translator.translate(texts)
            if len(translated) != len(batch):
                raise TranslationError("translator returned the wrong number of results; batch was not written")
            rows = [(verse.verse_id, english, verse.source_sha256) for verse, english in zip(batch, translated)]
            store.save_batch(rows)
            translated_count += len(batch)
            submitted_characters += sum(len(text) for text in texts)
            store.update_run(run_id, submitted_characters, translated_count)
            if progress is not None:
                current = dict(existing)
                current.update({verse.verse_id: (english, verse.source_sha256) for verse, english in zip(batch, translated)})
                current_status = _status_from_data(source, current)
                progress(translated_count, current_status.eligible_count, submitted_characters, current_status.source_characters_remaining)
        store.update_run(run_id, submitted_characters, translated_count, status="completed")
        after = translation_status(source_db, translation_db, canonical_path, require_oicb=require_oicb)
        return TranslationSummary(after, translated_count, submitted_characters, planned_count, planned_characters, stopped_reason)
    except KeyboardInterrupt as exc:
        store.update_run(run_id, submitted_characters, translated_count, status="interrupted", error="KeyboardInterrupt")
        raise exc
    except Exception as exc:
        store.update_run(run_id, submitted_characters, translated_count, status="failed", error=str(exc))
        raise
    finally:
        store.close()


def validate_translation(
    source_db: Path,
    translation_db: Path,
    canonical_path: Path | None = None,
    require_oicb: bool = True,
) -> TranslationStatus:
    """Validate alignment and content; raise on any incomplete/invalid state."""

    if not translation_db.exists():
        raise TranslationError(f"translation database not found: {translation_db}")
    status = translation_status(source_db, translation_db, canonical_path, require_oicb=require_oicb)
    with _readonly_connection(translation_db) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise TranslationError(f"translation SQLite integrity check failed: {integrity}")
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise TranslationError(f"translation SQLite foreign-key check failed: {foreign_keys}")
    if not status.valid or status.missing_count:
        raise TranslationError(
            "translation validation failed: "
            f"missing={status.missing_count}, stale={status.stale_count}, "
            f"orphaned={status.orphaned_count}, empty={status.empty_count}"
        )
    return status

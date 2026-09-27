# OICB builder guidance

## Scope

This repository contains the Bible dataset builder and a native Android client
under `android/`. Do not put runtime translation or Android source inside the
Python builder. The Android client must consume the documented SQLite contract
without changing the builder's edition schema or publication boundary.

## Storage architecture

The parsed OICB USFM is processed once and produces two independent SQLite
layers:

- All SQLite database artifacts live directly under ignored `data/databases/`.
  Generated JSON, CSV, and other reports remain under ignored `data/generated/`.
- `data/databases/bible.sqlite` is canonical structure only: `books(id,
  position)`, `chapters(id, book_id, number)`, and `verses(id, chapter_id,
  number)`.
- `data/databases/oicb.sqlite` is OICB edition data only: `metadata`,
  `books(book_id, name)`, and `verses(verse_id, content)`.
- `data/databases/oicb-google-en.sqlite` is a separate translated content
  layer keyed by the same canonical verse IDs.
- Historical, modernized, candidate, and other edition databases use the same
  flat directory and only the `.sqlite` file extension belongs there. Runtime
  edition schemas stay compact; normalization traces belong in generated
  research reports.

Names, language metadata, and Bible content must not be added to
`bible.sqlite`. Do not duplicate chapter or book structure in edition or
translation rows. Cross-database IDs are validated with SQLite `ATTACH`; they
cannot be ordinary foreign keys across files.

## Change rules

- Preserve the validated downloader and USFM parser unless a concrete source
  defect requires a change.
- Build both structure and OICB edition databases from one parsed result.
- Keep database rebuilds atomic, deterministic, and safe to rerun.
- Keep all downloaded, extracted, and generated data under ignored `data/`
  paths. Never commit Bible archives, extracted USFM, SQLite outputs, `.env`,
  or credentials.
- Keep SQLite files and staged private Bible assets out of Git. Android debug
  data staging belongs under ignored build output; never bundle local research
  Bible editions in a release variant.
- Google translation is build-time only, resumable, hash-checked, budgeted,
  and must be tested with injected fakes rather than live API calls.

## Configuration

The repository-root `.env` is loaded automatically when present without
overwriting existing process environment variables. Precedence is:

```text
CLI argument > existing process environment > .env > code default
```

Relative `GOOGLE_APPLICATION_CREDENTIALS` paths are resolved relative to the
repository root, not the caller's current working directory. Never print or
inspect credential contents.

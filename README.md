# OICB Bible dataset builder

This repository contains the ingestion component and an initial native Android
reader for the offline-first Bible project. `builder/` downloads the official Biblica
Open Igbo Contemporary Bible 2020 (OICB), extracts its USFM source, parses
readable verse text, validates the result, and writes a deterministic SQLite
database. The Android app under `android/` reads locally staged Bible files in
debug builds only. Google Cloud Translation remains a build-time tool.

## Source and license

The authoritative source used here is the OICB product page on
[Open.Bible](https://www.open.bible/bibles/igbo-biblica-text-bible),
provided by Biblica, Inc. The page publishes both USX and Paratext (USFM)
downloads and identifies this translation as CC BY-SA. The builder uses the
published Paratext (USFM) artifact:

`https://openbible-api-1.biblica.com/artifactContent/64c02602a4e86765a266c7a4`

The URL is an opaque, stable artifact URL exposed by the official product page;
it is intentionally configurable with `--url` in case Biblica publishes a
replacement artifact. The downloaded archive inspected during repository setup
contains 66 files at `release/USX_2/*.usfm`, encoded as UTF-8. Its observed
SHA-256 is:

`8909c1b38e5e5ff7f7ec625bd64889cfc78b937e2ed0daf1a53e2cb20655d765`

The source is made available under the
[Creative Commons Attribution-ShareAlike 4.0 International license](https://creativecommons.org/licenses/by-sa/4.0/).
Redistributions and adaptations must include the source/copyright notice,
attribute Biblica, Inc., identify changes, and make contributions available
under the same license. The Biblica trademark requires written permission; if
this project creates a derivative translation, remove the Biblica trademark
from that derivative and include the attribution specified by the source
notice. See the [OICB copyright notice](https://ebible.org/ibo/copyright.htm)
for the exact required wording and conditions.

The source archive is not part of this repository. Confirm the current license
and attribution terms before distributing a build artifact.

## Requirements and setup

Python 3.10 or newer is required. Runtime dependencies are standard-library
only: `argparse`, `sqlite3`, `urllib`, and `zipfile` are sufficient for the
pipeline. A virtual environment is optional.

Run from the repository root:

```sh
python3 -m builder --help
python3 -m unittest discover -s tests
```

## Commands

The complete pipeline is one command:

```sh
python3 -m builder all
```

Individual stages are available for inspection and debugging:

```sh
python3 -m builder download
python3 -m builder extract
python3 -m builder parse
python3 -m builder validate
python3 -m builder build
```

Use `--data-dir PATH` before the subcommand to change the artifact root. Use
`download --force` or `all --force` to replace an existing archive. The source
URL can be overridden with `download --url URL` or `all --url URL`.

The normal output locations are:

```text
data/downloads/oicb-usfm.zip
data/extracted/oicb/release/USX_2/*.usfm
data/databases/bible.sqlite
data/databases/oicb.sqlite
```

All SQLite outputs are kept in `data/databases/`. JSON, CSV, and other generated
reports stay in `data/generated/`; that directory is not a database output
directory. Both locations are ignored by Git. Do not commit downloaded
archives, extracted source files, research databases, or generated reports.

## Parsing and validation

The parser follows the constructs present in the inspected OICB source: book
metadata, chapter and verse markers, paragraph/poetry/list continuation lines,
headings, inline formatting markers, and footnote/cross-reference blocks.
Footnotes and cross-references are excluded from verse content; inline
formatting controls are removed while their readable text is retained. OICB's
published USFM has positive integer verse markers, so the schema intentionally
rejects unsupported non-integer verse numbering rather than silently mapping it
to a potentially incorrect ID.

Validation checks the 66-book set and canonical order, referential relationships,
ID and relationship uniqueness, non-empty Unicode content, absence of remaining
USFM controls, SQLite foreign keys/integrity, and reconciliation between source
`\\v` markers and generated verses. A successful build prints, for example:

```text
Books: 66
Chapters: 1189
Verses: 31103
Bible database: data/databases/bible.sqlite
OICB database: data/databases/oicb.sqlite
Validation: PASS
```

## Database architecture

The parsed OICB source is fanned out once into separate structural and edition
layers:

```text
OICB USFM
    |
    +----> bible.sqlite
    |       books / chapters / verses (structure only)
    |
    +----> oicb.sqlite
            books (Igbo names)
            verses (Igbo content)

oicb.sqlite
    |
    +---- build-time Google translation
                |
                v
        oicb-google-en.sqlite
            verses (English content)
```

`bible.sqlite` says which canonical books, chapters, and verses exist. It has
no names or Bible content:

```sql
books (
  id TEXT PRIMARY KEY,       -- exo
  position INTEGER NOT NULL UNIQUE
)

chapters (
  id TEXT PRIMARY KEY,       -- exo-13
  book_id TEXT NOT NULL REFERENCES books(id),
  number INTEGER NOT NULL,
  UNIQUE(book_id, number)
)

verses (
  id TEXT PRIMARY KEY,       -- exo-13-5
  chapter_id TEXT NOT NULL REFERENCES chapters(id),
  number INTEGER NOT NULL,
  UNIQUE(chapter_id, number)
)
```

`oicb.sqlite` contains only OICB metadata, Igbo book names, and Igbo verse
content. Its IDs are validated against `bible.sqlite` with an ATTACH query
because SQLite cannot enforce foreign keys across separate database files:

```sql
metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)
books(book_id TEXT PRIMARY KEY, name TEXT NOT NULL)
verses(verse_id TEXT PRIMARY KEY, content TEXT NOT NULL)
```

For example, a chapter can be composed from all three layers:

```sql
ATTACH DATABASE 'data/databases/oicb.sqlite' AS oicb;
ATTACH DATABASE 'data/databases/oicb-google-en.sqlite' AS english;

SELECT v.id, v.number, o.content AS igbo, e.content AS english
FROM verses v
LEFT JOIN oicb.verses o ON o.verse_id = v.id
LEFT JOIN english.verses e ON e.verse_id = v.id
WHERE v.chapter_id = 'jdg-13'
ORDER BY v.number;
```

Generated databases are reproducible build artifacts and are not committed to
Git. `bible.sqlite` and `oicb.sqlite` are rebuilt together from one parsed
source result; the parser is not run twice.

## Reproducible database recovery

SQLite databases, downloaded archives, extracted source files, generated
reports, and historical IGBOB materials are intentionally excluded from public
Git. The Mobobi-derived IGBOB and its 72 manually recovered gap verses have
unresolved redistribution rights, so the APK, recovery manifest, and resulting
historical/modern databases must stay in private storage.

The [source lock](data/sources/source-lock.json) is metadata-only and should be
committed; it records source identifiers, retrieval details, exact SHA-256
digests, and derivations without including Bible text. The [IGBOB 0.5.0 release
lock](data/releases/igbob-modern-v0.5.0.json) should also be committed and
records the expected logical content hash and database artifact hashes. Keep
private backups described in [the backup guide](docs/private-source-backup.md).
Restore the files at their locked paths under `data/`, then create and review a
local checksum inventory:

```sh
python3 -m builder --data-dir data prepare-private-backup
```

The helper only writes an ignored manifest; it does not copy or upload files.
After all required source files are restored, rebuild from the exact locked
inputs and verify the release:

```sh
python3 -m builder --data-dir data rebuild-release igbob-modern --version 0.5.0
```

The command verifies source hashes before building in a temporary directory,
validates SQLite integrity and verse IDs, and requires the modern logical
content hash to match the release lock. For IGBOB modernization release 0.5.0,
the expected logical SHA-256 is:

`11cc6bcbb330c2c1f3843cfc74d227c13dfd8f43d8de503f16fad0e02362ac89`

Binary SQLite hashes are also reported;
logical content/structure hashes are the release identity because SQLite build
details may affect file bytes. The exact locked Mobobi APK has been restored to
the ignored private-source path. See the [publication audit](docs/publication-audit.md)
before publishing the repository or configuring a remote.

## Build-time Google English dataset

Translation is an optional build-time operation. It uses the official Google
Cloud Translation Advanced v3 Python client, the general Neural Machine
Translation model (`general/nmt`), and independent `contents[]` strings with
`source_language_code=ig` and `target_language_code=en`. The default NMT model
is the appropriate straightforward Igbo-to-English neural translation choice;
no scraping library, LLM rewriting, Bible substitution, glossary, or runtime
translation is used.

Install the optional client only when translating:

```sh
python3 -m pip install -e '.[translate]'
```

Authentication uses Google Application Default Credentials (ADC). For local
development, run `gcloud auth application-default login`, or set
`GOOGLE_APPLICATION_CREDENTIALS` to a service-account JSON path and set
`GOOGLE_CLOUD_PROJECT` (or pass `--project-id`). Never commit credentials;
`.env`, service-account JSON names, and `credentials/` are ignored. See
[Google authentication](https://docs.cloud.google.com/translate/docs/authentication)
for the supported ADC flow.

Check the checkpoint without credentials:

```sh
python3 -m builder --data-dir data translate-status
```

Plan five verses without API calls or writes:

```sh
python3 -m builder --data-dir data translate --max-verses 5 --dry-run
```

Translate a bounded run, then resume later with the same command (omitting the
bound when ready):

```sh
python3 -m builder --data-dir data translate --max-verses 5
python3 -m builder --data-dir data translate --max-characters 450000
python3 -m builder --data-dir data translate
python3 -m builder --data-dir data validate-translation
```

Each successful batch is committed immediately. On restart, missing and stale
verse IDs are selected from the source database; completed IDs whose stored
`source_sha256` still matches are never sent again. If source content changes,
the affected English row becomes stale and is retranslated. Orphaned rows and
stale hashes are reported by status and fail translation validation.

The translation database is `data/databases/oicb-google-en.sqlite` and contains
no copied book/chapter structure:

```sql
metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
)

verses (
  verse_id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  source_sha256 TEXT NOT NULL
)

translation_runs (
  id INTEGER PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  max_characters INTEGER,
  max_verses INTEGER,
  characters_submitted INTEGER NOT NULL,
  verses_translated INTEGER NOT NULL,
  error TEXT
)
```

The local character budget counts Python Unicode code points in the exact
strings submitted. It is an operator safety limit, not Google's authoritative
billing meter. Google documents that text translation is charged per character
code point sent and that the first 500,000 characters per month are currently
covered by a monthly credit; that pricing can change, so the builder does not
hard-code it as a project limit. See [official pricing](https://cloud.google.com/products/translate/pricing).

Synchronous `translateText` requests are batched at most 100 verses and 25,000
code points locally, below Google's documented recommendation of less than
30,000 code points per request. OICB verses are kept as separate request
contents and response order is checked, so boundaries and IDs cannot be
reconstructed by splitting translated prose. Each content is also checked
against the documented 1,024-character field limit. See Google's
[translateText reference](https://docs.cloud.google.com/translate/docs/reference/rest/v3/projects/translateText)
and [quotas](https://docs.cloud.google.com/translate/docs/quotas).

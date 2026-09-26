# GitHub publication boundary audit

Audit date: 2026-09-26. The publication boundary was reviewed before local Git
initialization. This document records the reviewed tree and explicit staging
allowlist; it does not authorize publishing a remote repository or pushing.

## SAFE TO COMMIT

- `builder/` source, including import, normalization, and reproducibility code.
- `tests/` regression and validation tests.
- `data/normalization/rules.json` and `data/normalization/reviewed-lexicon.json`.
- `data/sources/source-lock.json` and `data/releases/igbob-modern-v0.5.0.json`. These contain metadata and digests, not verse text.
- `README.md`, `AGENTS.md`, `.env.example` (empty credential placeholders only), `pyproject.toml`, `.gitignore`, `docs/private-source-backup.md`, `docs/publication-audit.md`, and `docs/android-database-contract.md`. The Android contract is documentation only; no Android app or build files are part of this task.
- `docs/igbo-normalization.md`, after checking that examples remain short lexical snippets rather than extended source passages.
- `docs/igbob-research.md`, after removing copied Judges 13 wording and other Bible clause excerpts. The document retains findings, verse references, source URLs, counts, and brief lexical examples; it does not include full verse text or corpus dumps.

The exact intended staged set is the files in the bullets above, all Python
source files under `builder/` and `tests/`, the two JSON files under
`data/normalization/`, `data/sources/source-lock.json`, and
`data/releases/igbob-modern-v0.5.0.json`. No wildcard staging of the full
repository or `data/` tree is permitted.

## MUST REMAIN PRIVATE

- Every `data/databases/*.sqlite` file, including the four primary databases,
  `oicb.sqlite`, and the incomplete Mobobi candidate database. They contain
  substantial Bible text; IGBOB rights are unresolved.
- `data/private-source/`, including the recovered Mobobi APK.
- `data/downloads/` and `data/extracted/`, including OICB/KJV source packages
  and extracted USFM. These are source payloads, not lock metadata.
- `data/research/`, including the scan PDF, DjVu OCR text/XML, recovery JSON,
  scan-reviewed verse manifests, OCR evaluation images, and research corpus.
- `.env`, credentials, service-account files, and any future APKs.

## GENERATED / OPTIONAL

The files below were reviewed individually by their report shape and column
headers. Every file remains ignored; short words, verse IDs, provenance, or
hashes can still expose source material or private holdings.

| Files | Content assessment |
| --- | --- |
| `igbob-judges13-comparison.csv`, `igbob-mobobi-distributed-scan-collation.csv`, `igbob-mobobi-judges13-comparison.csv`, `igbob-normalization-samples.csv`, `igbob-normalization-review-samples.json` | Include complete or representative historical/modern verse passages. Must remain private. |
| `igbob-normalization-audit-v0.5.0.json`, `igbob-normalization-inventory.csv`, `igbob-macron-residual-forms.csv`, `igbob-strange-symbol-occurrences.csv`, `igbob-mobobi-normalization-candidates.csv`, `igbob-residual-review-pack-v0.4.0.json`, `igbob-residual-review-pack-v0.5.0.json`, `igbob-ulo-ikwu-review-v0.5.0.json` | Include per-verse transformations, contexts, snippets, or extensive source-derived lexical forms. Must remain private. |
| `igbob-macron-forms.csv`, `igbob-macron-residual-report.json`, `igbob-mobobi-normalization-inventory.json`, `igbob-morphology-audit.json`, `igbob-normalization-inventory.json`, `igbob-source-page-audit.json`, `igbob-strange-symbol-occurrences.json`, `igbob-unicode-audit.json`, `igbob-unicode-graphemes.csv` | Mostly aggregate counts, word forms, page references, and representative IDs; safe for local research but optional and ignored to keep a clear data boundary. |
| `igbob-composite-import-report.json`, `igbob-extraction-report.json`, `igbob-mobobi-import-report.json`, `igbob-quality-report.json`, `igbob-normalization-quality-report.json`, `database-manifest.json` | Build/validation summaries and hashes; no full verse payload expected. Optional generated outputs; rebuild or regenerate locally. |
| `private-backup-manifest.json` | Metadata-only local inventory, but it names private source paths and holdings. Keep ignored. |

These entries cover the current `data/generated/` directory. Future generated
files must be reviewed by content before being added to a commit; the
directory-wide ignore prevents accidental publication in the meantime.

## UNCERTAIN

- Any future export, screenshot, test fixture, or documentation excerpt that
  includes more than a short identifying Bible phrase. Classify by content,
  not extension or directory.
- Any file not covered by the explicit safe/private/generated lists above.

## Ignore policy

The current `.gitignore` excludes downloads, extracted files, all database
artifacts, generated reports, the research tree, private-source inputs, APKs,
Python caches, virtual environments, `.env`, and credential files. Source and
release lock metadata live outside ignored directories and remain visible as
commit candidates. After initialization, validate the ignore rules and compare
the staged paths against the explicit allowlist before committing.

# Private source and release backups

This inventory corresponds to `data/sources/source-lock.json`. Paths below are
relative to the repository's `data/` directory. Never add these files to public
Git or upload them automatically. The checksum helper writes only an ignored
manifest and reports missing files:

```sh
python3 -m builder --data-dir data prepare-private-backup
```

The helper writes `data/generated/private-backup-manifest.json`. It includes
relative paths, byte sizes, checksums, purposes, and whether the local source
lock marks each file as required. Review it and copy present files to approved
private external storage yourself.

## A. Irreplaceable or should back up

| Path | Status | Why it matters |
| --- | --- | --- |
| `private-source/com.mobobi.igbobible-2.0.apk` | Present; required; 11,221,240 bytes | Exact package input for the 66-book transcription. Recovered from APKPure version 2.0 and verified against the locked SHA-256. The importer extracts mapped UTF-16 assets directly from the APK; it is not safe to substitute another package version. |
| `research/igbob-source/mobobi-gap-recovery.json` | Present; required | Fixed, manually reviewed text and provenance for 72 missing verses (47 Numbers, 10 Job, 15 3 John). Rights are unresolved. A rebuild must not scrape live websites instead. |
| `research/igbob-source/Igbo-Bible-print.pdf` | Present; recommended private evidence | Exact scan used for source verification and OCR evaluation. It is not consumed by the current build, but replacement or later disappearance could prevent repeating the visual checks. |
| `databases/igbob.sqlite` | Present; backup | Generated composite historical corpus. It can be rebuilt only when the exact APK and recovery manifest are restored. |
| `databases/igbob-modern.sqlite` | Present; backup | Generated v0.5.0 release. It is reproducible from the historical database plus committed rules and lexicon, but is a useful recovery checkpoint. |

The APK's mapped book assets are read from the ZIP directly using the fixed
asset map in `builder/mobobi_import.py`, decoded as UTF-16, and parsed without
normalization. No manual extraction steps are required, so extracted assets do
not need a separate backup if the exact APK is safely preserved and its locked
hash verifies.

## B. Re-downloadable, but still recommended to back up

| Path | Why it matters |
| --- | --- |
| `downloads/oicb-usfm.zip` | Exact source for canonical structure and OICB; its archive URL is opaque and a future artifact may change. |
| `downloads/kjv/eng-kjv2006_usfm.zip` | Exact KJV source archive used to build `kjv.sqlite`; upstream packages can change. |

The archive SHA-256 values and upstream URLs are in the source lock. Rebuilds
verify the saved copies; they do not silently fetch replacements.

## C. Fully regenerable when the listed sources are preserved

| Artifact | Regeneration inputs |
| --- | --- |
| `databases/bible.sqlite`, `databases/oicb.sqlite` | Locked OICB USFM archive and committed parser/builder. |
| `databases/kjv.sqlite` | Locked KJV archive, canonical structure, and committed importer. |
| `databases/igbob.sqlite` | Exact Mobobi APK, exact recovery JSON, canonical structure, and committed importer. |
| `databases/igbob-modern.sqlite` | Historical database plus committed v0.5.0 rules, reviewed lexicon, and normalization engine. |
| `extracted/`, `generated/`, `research/igbo-union/` | Source archives or primary source inputs and the applicable committed tooling. Generated reports may contain substantial Bible text and stay ignored even when reproducible. |

`data/normalization/rules.json`, `data/normalization/reviewed-lexicon.json`,
the normalization engine, and regression tests are public rebuild inputs and
must be committed. They are not private backups.

## Recovery verification

The APKPure version 2.0 candidate matched the locked SHA-256 exactly and was
copied into `private-source/`. Direct import found all 66 mapped assets and
reproduced 31,031 Mobobi verses plus the 72 recovery entries. A clean staged
rebuild from source archives, the APK, recovery manifest, and committed
normalization metadata matched the existing canonical, KJV, and historical
database hashes and logical content. Modern IGBOB matched all locked logical
counts and its content SHA-256. Its generated SQLite binary hash differed from
the recorded artifact hash, while the modern logical content hash matched; the
release lock treats SQLite binary hashes as identifying metadata and logical
content as authoritative. The existing validated databases were left in place.

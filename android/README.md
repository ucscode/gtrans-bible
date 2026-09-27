# Android development app

This is a local, offline Android reader for modernized Igbo Bible text with
KJV alongside it. It uses Kotlin, AndroidX, XML layouts, RecyclerView, and the
Android SQLite APIs.

## App identity and SDK levels

- Development application ID: `com.ucscode.gtransbible.dev`. This is a local
  development identity, not a publishing or Play Store decision.
- `minSdk 23` (Android 6.0) keeps support broad for lower-cost devices; current
  AppCompat 1.8.0 supports API 23 and later.
- `compileSdk 36`, `targetSdk 36` use the stable Android 16 platform.
- AGP 9.4.0, Gradle Wrapper 9.8.0, JDK 17. Kotlin compilation uses AGP's
  built-in Kotlin support; no separate Kotlin Gradle plugin is applied.
- AppCompat 1.8.0 and RecyclerView 1.4.0 are pinned stable AndroidX versions.

The first milestone deliberately has no Android Studio or emulator dependency.
The Gradle Wrapper is the only Gradle entry point. From this directory:

```sh
./gradlew test
./gradlew assembleDebug
./gradlew assembleDebugAndroidTest
./gradlew lint
```

## Local Bible data boundary

The app stages only these local files for the **debug** variant:

- `data/databases/bible.sqlite`
- `data/databases/igbob-modern.sqlite`
- `data/databases/kjv.sqlite`

`prepareLocalBibleData` checks the existing generated database manifest and
each file's SHA-256 before copying to ignored `android/app/build/` output. It
does not fetch data. Restore/build the local databases and regenerate
`data/generated/database-manifest.json` if they are missing or hashes differ.
The historical `igbob.sqlite` is not staged. Do not put any SQLite files or
generated Bible assets under a tracked source directory.

On first run, the app copies each bundled debug database to its internal
`files/databases` directory using a temporary file, checksum verification, and
rename. It makes installed database files read-only before attaching them to
the canonical SQLite connection. Unchanged files are hash-checked and kept in
place; the manifest version, edition versions, and checksums are stored in
private preferences. No `INTERNET` permission is declared.

Release sources do not include the debug asset directory. Do not create or
publish a release APK from this local research corpus while redistribution
rights remain unresolved. A debug APK containing the private files must also
remain local and ignored.

## Reader behavior

The database contract in `../docs/android-database-contract.md` remains the
source of truth for canonical structure and edition schemas. `bible.sqlite` is
opened read-only, with modern Igbo and KJV attached on the same connection.
Books and chapters are read in canonical order; one query loads a complete
paired chapter. The same in-memory chapter feeds:

- Plain: modern Igbo by default, with a toggle to KJV.
- Side by side: Igbo left and KJV right in each verse row.
- Follow up: Igbo first and KJV directly beneath it.

Reader layout and Plain edition preferences are local. Text is passed to
Android's system sans-serif font unchanged, including Igbo Unicode marks.
There is no network access, search, historical edition UI, or release signing
configuration in this milestone.

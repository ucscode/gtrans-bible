# Android Bible database contract

The builder produces four separate SQLite files. A future client can consume
them as separate databases and join edition content to the canonical
structure by verse ID. `bible.sqlite` owns book order, chapters, verse
numbering, and the canonical verse IDs. Edition databases own their display
names and text.

| File | Database ID | Contents |
| --- | --- | --- |
| `data/databases/bible.sqlite` | `canonical` | Canonical books, chapters, verses, and ordering |
| `data/databases/igbob.sqlite` | `igbob` | Historical IGBOB local research edition |
| `data/databases/igbob-modern.sqlite` | `igbob-modern` | Modernized IGBOB local research edition |
| `data/databases/kjv.sqlite` | `kjv` | KJV text |

The IGBOB files are local research artifacts. Keep them out of published
packages and release APKs until redistribution rights are resolved. This
contract makes no redistribution claim for any edition. The generated
manifest contains provenance labels and checksums, not license determinations.

## Opening and attaching databases

Open `bible.sqlite` as the main database, then attach the edition files on the
same connection. Keep that connection open for the queries below. Use fixed
schema aliases and bind the file paths; SQLite identifiers cannot be bound as
parameters.

```sql
ATTACH DATABASE ? AS igbob;
ATTACH DATABASE ? AS igbob_modern;
ATTACH DATABASE ? AS kjv;
```

For Android's `SQLiteDatabase`, the equivalent call is:

```java
db.execSQL("ATTACH DATABASE ? AS igbob", new Object[] { historicalPath });
db.execSQL("ATTACH DATABASE ? AS igbob_modern", new Object[] { modernPath });
db.execSQL("ATTACH DATABASE ? AS kjv", new Object[] { kjvPath });
```

The app should copy developer-supplied database files into app-private storage
before opening them. Verify each copied file against
`database-manifest.json` before use. A changed database requires a
matching regenerated manifest. Do not use a single merged database; the
canonical and edition layers remain independent.

## Queries

List books in canonical order with each edition's own book name:

```sql
SELECT b.id AS book_id, b.position,
       h.name AS historical_name,
       m.name AS modern_name,
       k.name AS kjv_name
FROM main.books AS b
LEFT JOIN igbob.books AS h ON h.book_id = b.id
LEFT JOIN igbob_modern.books AS m ON m.book_id = b.id
LEFT JOIN kjv.books AS k ON k.book_id = b.id
ORDER BY b.position;
```

List chapters for a selected book:

```sql
SELECT id AS chapter_id, number
FROM main.chapters
WHERE book_id = ?
ORDER BY number;
```

Fetch modern Igbo verses for one chapter:

```sql
SELECT v.id AS verse_id, v.number AS verse_number, m.content
FROM main.chapters AS c
JOIN main.verses AS v ON v.chapter_id = c.id
JOIN igbob_modern.verses AS m ON m.verse_id = v.id
WHERE c.book_id = ? AND c.number = ?
ORDER BY v.number;
```

Pair modern Igbo and KJV by canonical verse ID:

```sql
SELECT v.id AS verse_id, v.number AS verse_number,
       m.content AS modern_igbo, k.content AS kjv
FROM main.chapters AS c
JOIN main.verses AS v ON v.chapter_id = c.id
JOIN igbob_modern.verses AS m ON m.verse_id = v.id
JOIN kjv.verses AS k ON k.verse_id = v.id
WHERE c.book_id = ? AND c.number = ?
ORDER BY v.number;
```

Pair historical Igbo, modern Igbo, and KJV, for optional display of the
historical wording:

```sql
SELECT v.id AS verse_id, v.number AS verse_number,
       h.content AS historical_igbo,
       m.content AS modern_igbo,
       k.content AS kjv
FROM main.chapters AS c
JOIN main.verses AS v ON v.chapter_id = c.id
JOIN igbob.verses AS h ON h.verse_id = v.id
JOIN igbob_modern.verses AS m ON m.verse_id = v.id
JOIN kjv.verses AS k ON k.verse_id = v.id
WHERE c.book_id = ? AND c.number = ?
ORDER BY v.number;
```

Use a `LEFT JOIN` for an optional edition; use an `INNER JOIN` when the
selected view requires every edition in the result. Edition names come from
the edition's own `books` table, while canonical order and chapter/verse
relationships always come from `main`.

## Manifest and version fields

`python3 -m builder.android_database` validates the four files and writes
`data/generated/database-manifest.json`. Each entry records the relative file
path under `data/databases/`, database ID, display name, language, version (when recorded), version
basis, verse count, SHA-256, provenance label, and normalization version when
applicable. In particular, IGBOB's source package version is not a Bible
publication date; the modern edition's `0.5.0` is its normalization ruleset
version. A null version means the database metadata does not record one.

The canonical database intentionally has no edition metadata or book names.
Historical and modern IGBOB book names are edition-specific. The 31,103
canonical verse IDs are the shared key used to pair content across files.

package com.ucscode.gtransbible.daily

import java.util.Locale

/** Parses a Bible reference and deliberately resolves ranges to their first verse. */
object BibleReferenceParser {
    private data class Book(val id: String, val canonicalName: String, val aliases: List<String> = emptyList())

    private val books = listOf(
        Book("gen", "Genesis", listOf("Gen")),
        Book("exo", "Exodus", listOf("Exod")),
        Book("lev", "Leviticus", listOf("Lev")),
        Book("num", "Numbers", listOf("Num")),
        Book("deu", "Deuteronomy", listOf("Deut")),
        Book("jos", "Joshua"),
        Book("jdg", "Judges"),
        Book("rut", "Ruth"),
        Book("1sa", "1 Samuel", listOf("I Samuel", "1 Sam", "I Sam")),
        Book("2sa", "2 Samuel", listOf("II Samuel", "2 Sam", "II Sam")),
        Book("1ki", "1 Kings", listOf("I Kings", "1 Kgs", "I Kgs")),
        Book("2ki", "2 Kings", listOf("II Kings", "2 Kgs", "II Kgs")),
        Book("1ch", "1 Chronicles", listOf("I Chronicles", "1 Chron", "I Chron")),
        Book("2ch", "2 Chronicles", listOf("II Chronicles", "2 Chron", "II Chron")),
        Book("ezr", "Ezra"),
        Book("neh", "Nehemiah", listOf("Neh")),
        Book("est", "Esther", listOf("Est")),
        Book("job", "Job"),
        Book("psa", "Psalms", listOf("Psalm", "Psalms", "Ps")),
        Book("pro", "Proverbs", listOf("Prov")),
        Book("ecc", "Ecclesiastes", listOf("Qoheleth")),
        Book("sng", "Song of Solomon", listOf("Song of Songs", "Canticles")),
        Book("isa", "Isaiah", listOf("Isa")),
        Book("jer", "Jeremiah", listOf("Jer")),
        Book("lam", "Lamentations", listOf("Lam")),
        Book("ezk", "Ezekiel", listOf("Ezek")),
        Book("dan", "Daniel", listOf("Dan")),
        Book("hos", "Hosea"),
        Book("jol", "Joel"),
        Book("amo", "Amos"),
        Book("oba", "Obadiah", listOf("Obad")),
        Book("jon", "Jonah"),
        Book("mic", "Micah", listOf("Mic")),
        Book("nam", "Nahum", listOf("Nah")),
        Book("hab", "Habakkuk", listOf("Hab")),
        Book("zep", "Zephaniah", listOf("Zeph")),
        Book("hag", "Haggai"),
        Book("zec", "Zechariah", listOf("Zech")),
        Book("mal", "Malachi", listOf("Mal")),
        Book("mat", "Matthew", listOf("Matt")),
        Book("mrk", "Mark"),
        Book("luk", "Luke"),
        Book("jhn", "John"),
        Book("act", "Acts"),
        Book("rom", "Romans", listOf("Rom")),
        Book("1co", "1 Corinthians", listOf("I Corinthians", "1 Cor", "I Cor")),
        Book("2co", "2 Corinthians", listOf("II Corinthians", "2 Cor", "II Cor")),
        Book("gal", "Galatians", listOf("Gal")),
        Book("eph", "Ephesians", listOf("Eph")),
        Book("php", "Philippians", listOf("Phil")),
        Book("col", "Colossians", listOf("Col")),
        Book("1th", "1 Thessalonians", listOf("I Thessalonians", "1 Thess", "I Thess")),
        Book("2th", "2 Thessalonians", listOf("II Thessalonians", "2 Thess", "II Thess")),
        Book("1ti", "1 Timothy", listOf("I Timothy", "1 Tim", "I Tim")),
        Book("2ti", "2 Timothy", listOf("II Timothy", "2 Tim", "II Tim")),
        Book("tit", "Titus"),
        Book("phm", "Philemon", listOf("Philem")),
        Book("heb", "Hebrews", listOf("Heb")),
        Book("jas", "James", listOf("Jas")),
        Book("1pe", "1 Peter", listOf("I Peter", "1 Pet", "I Pet")),
        Book("2pe", "2 Peter", listOf("II Peter", "2 Pet", "II Pet")),
        Book("1jn", "1 John", listOf("I John", "1 Jn", "I Jn")),
        Book("2jn", "2 John", listOf("II John", "2 Jn", "II Jn")),
        Book("3jn", "3 John", listOf("III John", "3 Jn", "III Jn")),
        Book("jud", "Jude"),
        Book("rev", "Revelation", listOf("Revelations", "Rev")),
    )

    private val booksByName = buildMap {
        books.forEach { book ->
            (book.aliases + book.canonicalName).forEach { alias -> put(normalizeBookName(alias), book) }
        }
    }
    private val referencePattern = Regex(
        """^(.+?)\s+(\d+)\s*:\s*(\d+)(?:\s*-\s*(?:\d+\s*:\s*)?\d+)?$""",
    )

    fun parse(value: String): VerseReference? {
        val match = referencePattern.matchEntire(value.trim()) ?: return null
        val book = booksByName[normalizeBookName(match.groupValues[1])] ?: return null
        val chapter = match.groupValues[2].toIntOrNull()?.takeIf { it > 0 } ?: return null
        val verse = match.groupValues[3].toIntOrNull()?.takeIf { it > 0 } ?: return null
        return VerseReference(book.id, chapter, verse, book.canonicalName)
    }

    fun canonicalVerseId(value: String): String? = parse(value)?.verseId

    private fun normalizeBookName(value: String): String = value.trim()
        .lowercase(Locale.ROOT)
        .replace(".", "")
        .replace(Regex("\\s+"), " ")
}

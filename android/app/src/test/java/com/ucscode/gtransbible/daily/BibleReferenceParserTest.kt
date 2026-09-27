package com.ucscode.gtransbible.daily

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class BibleReferenceParserTest {
    @Test
    fun parsesAllSixtySixCanonicalBooks() {
        val references = listOf(
            "Genesis" to "gen", "Exodus" to "exo", "Leviticus" to "lev", "Numbers" to "num",
            "Deuteronomy" to "deu", "Joshua" to "jos", "Judges" to "jdg", "Ruth" to "rut",
            "1 Samuel" to "1sa", "2 Samuel" to "2sa", "1 Kings" to "1ki", "2 Kings" to "2ki",
            "1 Chronicles" to "1ch", "2 Chronicles" to "2ch", "Ezra" to "ezr", "Nehemiah" to "neh",
            "Esther" to "est", "Job" to "job", "Psalms" to "psa", "Proverbs" to "pro",
            "Ecclesiastes" to "ecc", "Song of Solomon" to "sng", "Isaiah" to "isa", "Jeremiah" to "jer",
            "Lamentations" to "lam", "Ezekiel" to "ezk", "Daniel" to "dan", "Hosea" to "hos",
            "Joel" to "jol", "Amos" to "amo", "Obadiah" to "oba", "Jonah" to "jon", "Micah" to "mic",
            "Nahum" to "nam", "Habakkuk" to "hab", "Zephaniah" to "zep", "Haggai" to "hag",
            "Zechariah" to "zec", "Malachi" to "mal", "Matthew" to "mat", "Mark" to "mrk", "Luke" to "luk",
            "John" to "jhn", "Acts" to "act", "Romans" to "rom", "1 Corinthians" to "1co",
            "2 Corinthians" to "2co", "Galatians" to "gal", "Ephesians" to "eph", "Philippians" to "php",
            "Colossians" to "col", "1 Thessalonians" to "1th", "2 Thessalonians" to "2th",
            "1 Timothy" to "1ti", "2 Timothy" to "2ti", "Titus" to "tit", "Philemon" to "phm",
            "Hebrews" to "heb", "James" to "jas", "1 Peter" to "1pe", "2 Peter" to "2pe",
            "1 John" to "1jn", "2 John" to "2jn", "3 John" to "3jn", "Jude" to "jud", "Revelation" to "rev",
        )
        references.forEach { (book, id) -> assertEquals(id, BibleReferenceParser.parse("$book 1:1")?.bookId) }
        assertEquals(66, references.size)
    }

    @Test
    fun resolvesAliasesAndRangesToFirstVerse() {
        assertEquals("1sa-3-4", BibleReferenceParser.canonicalVerseId("I Sam. 3:4-6"))
        assertEquals("psa-119-1", BibleReferenceParser.canonicalVerseId("Psalm 119:1-8"))
        assertEquals("sng-2-3", BibleReferenceParser.canonicalVerseId("Song of Songs 2:3"))
        assertNull(BibleReferenceParser.parse("Unknown 1:1"))
        assertNull(BibleReferenceParser.parse("John 0:1"))
    }
}

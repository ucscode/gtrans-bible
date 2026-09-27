package com.ucscode.gtransbible.data

data class BibleBook(val id: String, val name: String, val englishName: String, val position: Int)

data class BibleChapter(val id: String, val number: Int)

data class ChapterVerse(
    val verseId: String,
    val verseNumber: Int,
    val igbo: String,
    val english: String,
)

enum class ReaderLayout { PLAIN, SIDE_BY_SIDE, FOLLOW_UP }
enum class PlainEdition { MODERN_IGBO, KJV }
enum class Testament { OLD, NEW }

/** Horizontal page-motion direction for moving between adjacent chapters. */
enum class ChapterTransition(val outgoingSign: Float, val incomingSign: Float) {
    NEXT(-1f, 1f),
    PREVIOUS(1f, -1f);

    companion object {
        fun fromDirection(direction: Int): ChapterTransition = when (direction) {
            1 -> NEXT
            -1 -> PREVIOUS
            else -> throw IllegalArgumentException("Chapter direction must be -1 or 1")
        }
    }
}

data class ChapterLocation(val bookId: String, val bookName: String, val chapter: Int)

/** Testament membership follows the canonical database's ordered position. */
fun BibleBook.belongsTo(testament: Testament): Boolean = when (testament) {
    Testament.OLD -> position <= 39
    Testament.NEW -> position > 39
}

/** Makes source labels readable while preserving Igbo diacritics and Roman numerals. */
fun displayIgboBookName(name: String): String = name.trim().lowercase()
    .split(Regex("\\s+"))
    .joinToString(" ") { part ->
        if (part.matches(Regex("[ivxlcdm]+\\.?"))) part.uppercase()
        else part.replaceFirstChar { it.titlecase() }
    }

/** Pure presentation contract shared by reader controls and tests. */
data class ReaderPresentation(
    val layout: ReaderLayout,
    val plainEdition: PlainEdition,
) {
    fun orderedTexts(verse: ChapterVerse): List<String> = when (layout) {
        ReaderLayout.PLAIN -> listOf(if (plainEdition == PlainEdition.MODERN_IGBO) verse.igbo else verse.english)
        ReaderLayout.SIDE_BY_SIDE, ReaderLayout.FOLLOW_UP -> listOf(verse.igbo, verse.english)
    }
}

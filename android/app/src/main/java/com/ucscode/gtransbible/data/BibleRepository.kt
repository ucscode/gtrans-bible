package com.ucscode.gtransbible.data

import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import java.io.File

class BibleRepository(private val directory: File) : AutoCloseable {
    private val database: SQLiteDatabase

    init {
        val canonical = File(directory, "bible.sqlite")
        check(canonical.isFile) { "Canonical Bible structure is not installed" }
        database = SQLiteDatabase.openDatabase(canonical.absolutePath, null, SQLiteDatabase.OPEN_READONLY)
        try {
            attach("igbob_modern", File(directory, "igbob-modern.sqlite"))
            attach("kjv", File(directory, "kjv.sqlite"))
        } catch (failure: Exception) {
            database.close()
            throw failure
        }
    }

    private fun attach(alias: String, file: File) {
        check(file.isFile) { "Required Bible edition is not installed: ${file.name}" }
        check(!file.canWrite()) { "Bible edition must be read-only before opening: ${file.name}" }
        database.execSQL("ATTACH DATABASE ? AS $alias", arrayOf(file.absolutePath))
    }

    fun getBooks(): List<BibleBook> = database.rawQuery(
        """SELECT b.id, COALESCE(m.name, b.id), COALESCE(k.name, b.id), b.position
           FROM main.books b
           LEFT JOIN igbob_modern.books m ON m.book_id = b.id
           LEFT JOIN kjv.books k ON k.book_id = b.id
           ORDER BY b.position""".trimIndent(), null,
    ).use { cursor -> cursor.map { BibleBook(it.getString(0), it.getString(1), it.getString(2).trim(), it.getInt(3)) } }

    fun getChapters(bookId: String): List<BibleChapter> = database.rawQuery(
        "SELECT id, number FROM main.chapters WHERE book_id = ? ORDER BY number",
        arrayOf(bookId),
    ).use { cursor -> cursor.map { BibleChapter(it.getString(0), it.getInt(1)) } }

    /** Finds the adjacent chapter in canonical book/chapter order; null marks a Bible boundary. */
    fun getAdjacentChapter(bookId: String, chapterNumber: Int, direction: Int): ChapterLocation? {
        require(direction == -1 || direction == 1)
        val currentPosition = database.rawQuery(
            "SELECT position FROM main.books WHERE id = ?", arrayOf(bookId),
        ).use { cursor -> if (cursor.moveToFirst()) cursor.getInt(0) else return null }
        val comparison = if (direction > 0) ">" else "<"
        val order = if (direction > 0) "ASC" else "DESC"
        return database.rawQuery(
            """SELECT c.book_id, COALESCE(m.name, c.book_id), c.number
               FROM main.chapters c
               JOIN main.books b ON b.id = c.book_id
               LEFT JOIN igbob_modern.books m ON m.book_id = c.book_id
               WHERE b.position $comparison ? OR (b.position = ? AND c.number $comparison ?)
               ORDER BY b.position $order, c.number $order LIMIT 1""".trimIndent(),
            arrayOf(currentPosition.toString(), currentPosition.toString(), chapterNumber.toString()),
        ).use { cursor ->
            if (cursor.moveToFirst()) ChapterLocation(cursor.getString(0), cursor.getString(1), cursor.getInt(2)) else null
        }
    }

    fun getParallelChapter(bookId: String, chapterNumber: Int): List<ChapterVerse> = database.rawQuery(
        """SELECT v.id, v.number, m.content, k.content
           FROM main.chapters c
           JOIN main.verses v ON v.chapter_id = c.id
           JOIN igbob_modern.verses m ON m.verse_id = v.id
           JOIN kjv.verses k ON k.verse_id = v.id
           WHERE c.book_id = ? AND c.number = ?
           ORDER BY v.number""".trimIndent(),
        arrayOf(bookId, chapterNumber.toString()),
    ).use { cursor ->
        cursor.map { ChapterVerse(it.getString(0), it.getInt(1), it.getString(2), it.getString(3)) }
    }

    override fun close() = database.close()

    private inline fun <T> Cursor.map(transform: (Cursor) -> T): List<T> = buildList {
        while (moveToNext()) add(transform(this@map))
    }
}

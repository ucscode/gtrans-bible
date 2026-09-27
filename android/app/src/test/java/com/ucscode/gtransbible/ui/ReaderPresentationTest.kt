package com.ucscode.gtransbible.ui

import com.ucscode.gtransbible.data.ChapterVerse
import com.ucscode.gtransbible.data.PlainEdition
import com.ucscode.gtransbible.data.ReaderLayout
import com.ucscode.gtransbible.data.ReaderPresentation
import com.ucscode.gtransbible.data.BibleBook
import com.ucscode.gtransbible.data.ChapterTransition
import com.ucscode.gtransbible.data.Testament
import com.ucscode.gtransbible.data.belongsTo
import com.ucscode.gtransbible.data.displayIgboBookName
import org.junit.Assert.assertEquals
import org.junit.Test

class ReaderPresentationTest {
    private val verse = ChapterVerse("gen-1-1", 1, "Igbo ọ́rụ̀ ụ́zọ̀", "English first verse")

    @Test fun plainEditionSelectsOnlyItsText() {
        assertEquals(listOf(verse.igbo), ReaderPresentation(ReaderLayout.PLAIN, PlainEdition.MODERN_IGBO).orderedTexts(verse))
        assertEquals(listOf(verse.english), ReaderPresentation(ReaderLayout.PLAIN, PlainEdition.KJV).orderedTexts(verse))
    }

    @Test fun pairedLayoutsKeepIgboBeforeEnglish() {
        assertEquals(listOf(verse.igbo, verse.english), ReaderPresentation(ReaderLayout.SIDE_BY_SIDE, PlainEdition.KJV).orderedTexts(verse))
        assertEquals(listOf(verse.igbo, verse.english), ReaderPresentation(ReaderLayout.FOLLOW_UP, PlainEdition.KJV).orderedTexts(verse))
    }

    @Test fun canonicalPositionSplitsOldAndNewTestamentsWithoutReorderingBooks() {
        val canonical = (1..66).map { position ->
            BibleBook("book-$position", "Igbo $position", "English $position", position)
        }
        assertEquals((1..39).toList(), canonical.filter { it.belongsTo(Testament.OLD) }.map { it.position })
        assertEquals((40..66).toList(), canonical.filter { it.belongsTo(Testament.NEW) }.map { it.position })
    }

    @Test fun bookNamePresentationKeepsIgboMarksAndRomanNumerals() {
        assertEquals("Jenesis", displayIgboBookName("JENESIS"))
        assertEquals("Ọpupu", displayIgboBookName("ỌPUPU"))
        assertEquals("Abù Ọma", displayIgboBookName("ABÙ ỌMA"))
        assertEquals("II. Samuel", displayIgboBookName("II. SAMUEL"))
    }

    @Test fun chapterTransitionDirectionsMoveOutAndEnterFromOppositeSides() {
        assertEquals(ChapterTransition.NEXT, ChapterTransition.fromDirection(1))
        assertEquals(-1f, ChapterTransition.NEXT.outgoingSign)
        assertEquals(1f, ChapterTransition.NEXT.incomingSign)
        assertEquals(ChapterTransition.PREVIOUS, ChapterTransition.fromDirection(-1))
        assertEquals(1f, ChapterTransition.PREVIOUS.outgoingSign)
        assertEquals(-1f, ChapterTransition.PREVIOUS.incomingSign)
    }
}

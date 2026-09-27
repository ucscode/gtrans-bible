package com.ucscode.gtransbible.data

import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class LocalBibleInstrumentedTest {
    @Test fun localInstallIsVerifiedAndChapterDataIsPairedInCanonicalOrder() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val installer = DatabaseInstaller(context)
        installer.install()
        val secondInstall = installer.install()
        assertTrue("unchanged databases should not be recopied", secondInstall.copiedFiles.isEmpty())
        assertEquals(DatabaseInstaller.REQUIRED_DATABASES, secondInstall.hashes.keys)
        DatabaseInstaller.REQUIRED_DATABASES.forEach { filename ->
            assertFalse(File(context.filesDir, "databases/$filename").canWrite())
        }

        BibleRepository(File(context.filesDir, "databases")).use { repository ->
            val books = repository.getBooks()
            assertEquals(66, books.size)
            assertEquals("gen", books.first().id)
            assertEquals(1, books.first().position)
            assertEquals("Genesis", books.first().englishName)
            assertEquals("JENESIS", books.first().name)
            assertEquals(39, books.count { it.position <= 39 })
            assertEquals(27, books.count { it.position > 39 })
            val expectedNames = mapOf(
                "gen" to ("JENESIS" to "Genesis"), "exo" to ("ỌPUPU" to "Exodus"),
                "jdg" to ("NDI-IKPE" to "Judges"), "psa" to ("ABÙ ỌMA" to "Psalms"),
                "mat" to ("MATIU" to "Matthew"), "jhn" to ("JỌN" to "John"),
                "rom" to ("NDI ROM" to "Romans"), "rev" to ("NKPUGHE" to "Revelation"),
            )
            expectedNames.forEach { (id, names) ->
                val book = books.single { it.id == id }
                assertEquals("Igbo label for $id", names.first, book.name)
                assertEquals("KJV label for $id", names.second, book.englishName)
            }
            assertEquals(ChapterLocation("mat", "MATIU", 6), repository.getAdjacentChapter("mat", 5, 1))
            assertEquals(ChapterLocation("mrk", "MAK", 1), repository.getAdjacentChapter("mat", 28, 1))
            assertEquals(ChapterLocation("mat", "MATIU", 28), repository.getAdjacentChapter("mrk", 1, -1))
            assertEquals(null, repository.getAdjacentChapter("gen", 1, -1))
            assertEquals(null, repository.getAdjacentChapter("rev", 22, 1))
            assertEquals(50, repository.getChapters("gen").size)
            assertEquals(28, repository.getChapters("mat").size)
            assertEquals(150, repository.getChapters("psa").size)
            assertEquals(1, repository.getChapters("jud").size)
            assertEquals(176, repository.getChapters("psa").first { it.number == 119 }.let { repository.getParallelChapter("psa", it.number).size })

            val genesis = repository.getParallelChapter("gen", 1)
            assertEquals(31, genesis.size)
            assertEquals((1..31).toList(), genesis.map { it.verseNumber })
            assertTrue(genesis.all { it.verseId.startsWith("gen-1-") && it.igbo.isNotBlank() && it.english.isNotBlank() })
            assertTrue("Igbo Unicode diacritics should remain intact", genesis.any { verse -> verse.igbo.any { it in "ịọụṅ" } })
        }
        assertEquals("com.ucscode.gtransbible.dev", context.packageName)
    }
}

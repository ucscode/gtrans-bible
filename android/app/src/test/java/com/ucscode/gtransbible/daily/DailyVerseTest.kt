package com.ucscode.gtransbible.daily

import com.ucscode.gtransbible.data.ChapterVerse
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Calendar
import java.util.GregorianCalendar
import java.util.TimeZone

class DailyVerseTest {
    @Test
    fun responseParserUsesReferenceAndVersionButNotReturnedText() {
        val result = OurMannaDailyVerseApi.parseResponse(
            """{"verse":{"details":{"reference":"John 3:16-17","version":"kjv","text":"must not be imported"}}}""",
        )
        assertEquals("John 3:16-17", result.reference)
        assertEquals("ourmanna:kjv", result.sourceId)
    }

    @Test
    fun malformedOrReferenceLessResponseIsRejected() {
        assertTrue(runCatching { OurMannaDailyVerseApi.parseResponse("not json") }.isFailure)
        assertTrue(runCatching {
            OurMannaDailyVerseApi.parseResponse("""{"verse":{"details":{"text":"ignored"}}}""")
        }.isFailure)
    }

    @Test
    fun cacheIsSharedBetweenHomeAndNotificationLoads() {
        val cache = MemoryCache()
        val verse = ChapterVerse("jhn-3-16", 16, "N'ihi na Chineke hụrụ ụwa n'anya", "For God so loved the world")
        var apiCalls = 0
        val repository = DailyVerseRepository(
            cache,
            DailyVerseApi { apiCalls++; ApiDailyVerse("John 3:16", "test") },
            { id -> verse.takeIf { id == verse.verseId } },
            { instant(2026, Calendar.SEPTEMBER, 27, 9) },
            { _, _ -> },
        )
        val home = repository.loadForHome()
        val notification = repository.loadForNotification()
        assertNotNull(home)
        assertNotNull(notification)
        assertEquals(1, apiCalls)
        assertEquals("jhn-3-16", home?.verse?.verseId)
        assertTrue(notification?.isToday == true)
    }

    @Test
    fun failedFetchUsesPreviousCachedVerseAndDoesNotExposeApiText() {
        val cache = MemoryCache().apply {
            saveVerse(CachedDailyVerse("2026-09-26", "John 3:16", "jhn-3-16", "test", 1L))
        }
        val verse = ChapterVerse("jhn-3-16", 16, "local Igbo", "local KJV")
        val repository = DailyVerseRepository(
            cache,
            DailyVerseApi { error("offline") },
            { verse },
            { instant(2026, Calendar.SEPTEMBER, 27, 9) },
            { _, _ -> },
        )
        val result = repository.loadForHome()
        assertNotNull(result)
        assertFalse(result!!.isToday)
        assertEquals("local Igbo", result.verse.igbo)
    }

    @Test
    fun unknownReferencesAndMissingLocalVersesAreNotCached() {
        val cache = MemoryCache()
        val result = DailyVerseRepository(
            cache,
            DailyVerseApi { ApiDailyVerse("Unknown 3:16", "test") },
            { null },
            { instant(2026, Calendar.SEPTEMBER, 27, 9) },
            { _, _ -> },
        ).loadForHome()
        assertNull(result)
        assertNull(cache.cachedVerse())
    }

    @Test
    fun notificationsRequireBothOptInAndPermissionAndTargetLocalEightAm() {
        assertFalse(DailyVerseNotificationPolicy.shouldSchedule(false, true))
        assertFalse(DailyVerseNotificationPolicy.shouldSchedule(true, false))
        assertTrue(DailyVerseNotificationPolicy.shouldSchedule(true, true))
        val zone = TimeZone.getTimeZone("Africa/Lagos")
        assertEquals(60 * 60 * 1000L, DailyVerseNotificationPolicy.initialDelayMillis(instant(2026, Calendar.SEPTEMBER, 27, 7), zone))
        assertEquals(23 * 60 * 60 * 1000L, DailyVerseNotificationPolicy.initialDelayMillis(instant(2026, Calendar.SEPTEMBER, 27, 9), zone))
    }

    private fun instant(year: Int, month: Int, day: Int, hour: Int): Long = GregorianCalendar(
        TimeZone.getTimeZone("Africa/Lagos"),
    ).apply {
        set(year, month, day, hour, 0, 0)
        set(Calendar.MILLISECOND, 0)
    }.timeInMillis

    private class MemoryCache : DailyVerseCacheStore {
        private var cached: CachedDailyVerse? = null
        private var homeAttempt: String? = null
        private var notificationAttempt: String? = null
        private var enabled = false
        override fun cachedVerse() = cached
        override fun saveVerse(value: CachedDailyVerse) { cached = value }
        override fun homeAttemptDate() = homeAttempt
        override fun setHomeAttemptDate(date: String) { homeAttempt = date }
        override fun notificationAttemptDate() = notificationAttempt
        override fun setNotificationAttemptDate(date: String) { notificationAttempt = date }
        override fun notificationsEnabled() = enabled
        override fun setNotificationsEnabled(enabled: Boolean) { this.enabled = enabled }
    }
}

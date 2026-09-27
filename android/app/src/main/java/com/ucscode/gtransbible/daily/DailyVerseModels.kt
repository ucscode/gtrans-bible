package com.ucscode.gtransbible.daily

import com.ucscode.gtransbible.data.ChapterVerse
import java.util.Calendar
import java.util.Locale
import java.util.TimeZone

data class VerseReference(
    val bookId: String,
    val chapter: Int,
    val verse: Int,
    val canonicalBookName: String,
) {
    val verseId: String get() = "$bookId-$chapter-$verse"
    val displayReference: String get() = "$canonicalBookName $chapter:$verse"
}

data class ApiDailyVerse(val reference: String, val sourceId: String)

data class CachedDailyVerse(
    val date: String,
    val reference: String,
    val verseId: String,
    val sourceId: String,
    val fetchedAtMillis: Long,
)

data class DailyVerseDisplay(
    val reference: VerseReference,
    val verse: ChapterVerse,
    val isToday: Boolean,
    val cacheDate: String,
)

fun interface DailyVerseApi {
    fun fetchDailyVerse(): ApiDailyVerse
}

interface DailyVerseCacheStore {
    fun cachedVerse(): CachedDailyVerse?
    fun saveVerse(value: CachedDailyVerse)
    fun homeAttemptDate(): String?
    fun setHomeAttemptDate(date: String)
    fun notificationAttemptDate(): String?
    fun setNotificationAttemptDate(date: String)
    fun notificationsEnabled(): Boolean
    fun setNotificationsEnabled(enabled: Boolean)
}

fun localDateKey(nowMillis: Long, timeZone: TimeZone = TimeZone.getDefault()): String {
    val calendar = Calendar.getInstance(timeZone, Locale.ROOT).apply { timeInMillis = nowMillis }
    return "%04d-%02d-%02d".format(
        Locale.ROOT,
        calendar.get(Calendar.YEAR),
        calendar.get(Calendar.MONTH) + 1,
        calendar.get(Calendar.DAY_OF_MONTH),
    )
}

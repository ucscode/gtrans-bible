package com.ucscode.gtransbible.daily

import android.util.Log
import com.ucscode.gtransbible.BuildConfig
import com.ucscode.gtransbible.data.ChapterVerse

/** Shared Home/notification fetch and cache path. Call on a background thread. */
class DailyVerseRepository(
    private val cache: DailyVerseCacheStore,
    private val api: DailyVerseApi,
    private val lookupVerse: (String) -> ChapterVerse?,
    private val nowMillis: () -> Long = System::currentTimeMillis,
    private val diagnosticLog: (String, Throwable?) -> Unit = { message, failure ->
        if (failure == null) Log.d(TAG, message) else Log.w(TAG, message, failure)
    },
) {
    fun loadForHome(): DailyVerseDisplay? = load(isNotificationAttempt = false)

    fun loadForNotification(): DailyVerseDisplay? = load(isNotificationAttempt = true)

    private fun load(isNotificationAttempt: Boolean): DailyVerseDisplay? {
        val now = nowMillis()
        val today = localDateKey(now)
        val cached = cache.cachedVerse()
        if (cached != null && cached.date == today) return resolve(cached, today)

        val attemptedDate = if (isNotificationAttempt) cache.notificationAttemptDate() else cache.homeAttemptDate()
        if (attemptedDate == today) return cached?.let { resolve(it, today) }
        if (isNotificationAttempt) cache.setNotificationAttemptDate(today) else cache.setHomeAttemptDate(today)

        if (BuildConfig.DEBUG) diagnosticLog("Verse of the Day fetch attempted for $today (notification=$isNotificationAttempt)", null)
        val fresh = runCatching {
            val candidate = api.fetchDailyVerse()
            val reference = BibleReferenceParser.parse(candidate.reference)
                ?: throw IllegalArgumentException("OurManna returned an unsupported Bible reference")
            val localVerse = lookupVerse(reference.verseId)
                ?: throw IllegalArgumentException("OurManna reference is absent from the local editions")
            val entry = CachedDailyVerse(
                date = today,
                reference = reference.displayReference,
                verseId = reference.verseId,
                sourceId = candidate.sourceId,
                fetchedAtMillis = now,
            )
            cache.saveVerse(entry)
            if (BuildConfig.DEBUG) diagnosticLog("Verse of the Day cached: ${reference.verseId} on $today", null)
            DailyVerseDisplay(reference, localVerse, isToday = true, cacheDate = today)
        }.onFailure { failure ->
            if (BuildConfig.DEBUG) diagnosticLog("Verse of the Day unavailable for $today (${failure.javaClass.simpleName})", failure)
        }.getOrNull()
        return fresh ?: cached?.let { resolve(it, today) }
    }

    private fun resolve(cached: CachedDailyVerse, today: String): DailyVerseDisplay? {
        val reference = BibleReferenceParser.parse(cached.reference) ?: return null
        val localVerse = lookupVerse(cached.verseId) ?: return null
        return DailyVerseDisplay(reference, localVerse, isToday = cached.date == today, cacheDate = cached.date)
    }

    private companion object {
        const val TAG = "DailyVerse"
    }
}

package com.ucscode.gtransbible.daily

import android.content.Context
import androidx.core.content.edit

class SharedPreferencesDailyVerseStore(context: Context) : DailyVerseCacheStore {
    private val preferences = context.applicationContext.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)

    override fun cachedVerse(): CachedDailyVerse? {
        val date = preferences.getString(KEY_DATE, null) ?: return null
        val reference = preferences.getString(KEY_REFERENCE, null) ?: return null
        val verseId = preferences.getString(KEY_VERSE_ID, null) ?: return null
        val source = preferences.getString(KEY_SOURCE_ID, null) ?: SOURCE_OURMANNA
        return CachedDailyVerse(date, reference, verseId, source, preferences.getLong(KEY_FETCHED_AT, 0L))
    }

    override fun saveVerse(value: CachedDailyVerse) {
        preferences.edit {
            putString(KEY_DATE, value.date)
            putString(KEY_REFERENCE, value.reference)
            putString(KEY_VERSE_ID, value.verseId)
            putString(KEY_SOURCE_ID, value.sourceId)
            putLong(KEY_FETCHED_AT, value.fetchedAtMillis)
        }
    }

    override fun homeAttemptDate(): String? = preferences.getString(KEY_HOME_ATTEMPT_DATE, null)
    override fun setHomeAttemptDate(date: String) = preferences.edit { putString(KEY_HOME_ATTEMPT_DATE, date) }
    override fun notificationAttemptDate(): String? = preferences.getString(KEY_NOTIFICATION_ATTEMPT_DATE, null)
    override fun setNotificationAttemptDate(date: String) = preferences.edit { putString(KEY_NOTIFICATION_ATTEMPT_DATE, date) }
    override fun notificationsEnabled(): Boolean = preferences.getBoolean(KEY_NOTIFICATIONS_ENABLED, DEFAULT_NOTIFICATIONS_ENABLED)
    override fun setNotificationsEnabled(enabled: Boolean) = preferences.edit { putBoolean(KEY_NOTIFICATIONS_ENABLED, enabled) }

    companion object {
        const val DEFAULT_NOTIFICATIONS_ENABLED = false

        private const val PREFERENCES_NAME = "daily_verse_preferences"
        private const val KEY_DATE = "cached_date"
        private const val KEY_REFERENCE = "cached_reference"
        private const val KEY_VERSE_ID = "cached_verse_id"
        private const val KEY_SOURCE_ID = "cached_source_id"
        private const val KEY_FETCHED_AT = "cached_fetched_at"
        private const val KEY_HOME_ATTEMPT_DATE = "home_attempt_date"
        private const val KEY_NOTIFICATION_ATTEMPT_DATE = "notification_attempt_date"
        private const val KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
        private const val SOURCE_OURMANNA = "ourmanna"
    }
}

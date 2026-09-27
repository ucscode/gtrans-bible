package com.ucscode.gtransbible.daily

import android.Manifest
import android.annotation.SuppressLint
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import com.ucscode.gtransbible.BuildConfig
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.data.BibleRepository
import com.ucscode.gtransbible.ui.MainActivity
import java.io.File
import java.util.Calendar
import java.util.TimeZone
import java.util.concurrent.TimeUnit

object DailyVerseNotificationPolicy {
    const val DEFAULT_HOUR = 8
    const val DEFAULT_MINUTE = 0

    fun shouldSchedule(optedIn: Boolean, permissionGranted: Boolean): Boolean = optedIn && permissionGranted

    fun initialDelayMillis(nowMillis: Long, timeZone: TimeZone = TimeZone.getDefault()): Long {
        val now = Calendar.getInstance(timeZone).apply { timeInMillis = nowMillis }
        val next = (now.clone() as Calendar).apply {
            set(Calendar.HOUR_OF_DAY, DEFAULT_HOUR)
            set(Calendar.MINUTE, DEFAULT_MINUTE)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
            if (timeInMillis <= nowMillis) add(Calendar.DAY_OF_YEAR, 1)
        }
        return (next.timeInMillis - nowMillis).coerceAtLeast(0L)
    }
}

object DailyVerseNotificationScheduler {
    const val UNIQUE_WORK_NAME = "daily_verse_notification"

    fun schedule(context: Context) {
        val appContext = context.applicationContext
        if (!DailyVerseNotificationPolicy.shouldSchedule(
                optedIn = SharedPreferencesDailyVerseStore(appContext).notificationsEnabled(),
                permissionGranted = hasPermission(appContext),
            )
        ) {
            cancel(appContext)
            return
        }
        val request = PeriodicWorkRequestBuilder<DailyVerseNotificationWorker>(1, TimeUnit.DAYS)
            .setInitialDelay(DailyVerseNotificationPolicy.initialDelayMillis(System.currentTimeMillis()), TimeUnit.MILLISECONDS)
            .build()
        WorkManager.getInstance(appContext).enqueueUniquePeriodicWork(
            UNIQUE_WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request,
        )
        if (BuildConfig.DEBUG) Log.d(TAG, "Daily Verse notification scheduled for the next local 8:00 AM window")
    }

    fun cancel(context: Context) {
        WorkManager.getInstance(context.applicationContext).cancelUniqueWork(UNIQUE_WORK_NAME)
        if (BuildConfig.DEBUG) Log.d(TAG, "Daily Verse notification schedule cancelled")
    }

    fun hasPermission(context: Context): Boolean = Build.VERSION.SDK_INT < 33 ||
        ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    private const val TAG = "DailyVerse"
}

class DailyVerseNotificationWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        val cache = SharedPreferencesDailyVerseStore(applicationContext)
        if (!cache.notificationsEnabled() || !DailyVerseNotificationScheduler.hasPermission(applicationContext)) {
            cache.setNotificationsEnabled(false)
            if (BuildConfig.DEBUG) Log.d(TAG, "Notification worker skipped: opt-in or permission is unavailable")
            return Result.success()
        }

        return try {
            val display = BibleRepository(File(applicationContext.filesDir, "databases")).use { bible ->
                DailyVerseRepository(cache, OurMannaDailyVerseApi(), bible::getParallelVerse).loadForNotification()
            } ?: return Result.success()
            if (!display.isToday) {
                if (BuildConfig.DEBUG) Log.d(TAG, "Notification worker skipped: no current-day verse is available")
                return Result.success()
            }
            showNotification(display)
            Result.success()
        } catch (failure: Exception) {
            if (BuildConfig.DEBUG) Log.w(TAG, "Daily Verse notification skipped (${failure.javaClass.simpleName})")
            Result.success()
        }
    }

    private fun showNotification(display: DailyVerseDisplay) {
        val manager = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= 26) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, applicationContext.getString(R.string.daily_verse_channel), NotificationManager.IMPORTANCE_DEFAULT),
            )
        }
        val reference = display.reference.displayReference
        val snippet = truncate(display.verse.igbo)
        val launchIntent = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra(MainActivity.EXTRA_DAILY_BOOK_ID, display.reference.bookId)
            putExtra(MainActivity.EXTRA_DAILY_CHAPTER, display.reference.chapter)
            putExtra(MainActivity.EXTRA_DAILY_VERSE, display.reference.verse)
        }
        val contentIntent = PendingIntent.getActivity(
            applicationContext,
            NOTIFICATION_REQUEST_CODE,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_bible)
            .setContentTitle(applicationContext.getString(R.string.daily_verse_notification_title))
            .setContentText(snippet)
            .setStyle(NotificationCompat.BigTextStyle().bigText("$snippet\n$reference"))
            .setContentIntent(contentIntent)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        val posted = try {
            notifyIfPermissionGranted(notification)
        } catch (failure: SecurityException) {
            if (BuildConfig.DEBUG) Log.w(TAG, "Notification permission was revoked before posting")
            false
        }
        if (posted && BuildConfig.DEBUG) Log.d(TAG, "Daily Verse notification posted for ${display.reference.verseId}")
    }

    @SuppressLint("MissingPermission")
    private fun notifyIfPermissionGranted(notification: android.app.Notification): Boolean {
        if (!DailyVerseNotificationScheduler.hasPermission(applicationContext)) return false
        NotificationManagerCompat.from(applicationContext).notify(NOTIFICATION_TAG, NOTIFICATION_ID, notification)
        return true
    }

    private fun truncate(text: String): String {
        val clean = text.trim().replace(Regex("\\s+"), " ")
        return if (clean.length <= NOTIFICATION_TEXT_LIMIT) clean else clean.take(NOTIFICATION_TEXT_LIMIT - 1).trimEnd() + "…"
    }

    private companion object {
        const val TAG = "DailyVerse"
        const val CHANNEL_ID = "daily_verse"
        const val NOTIFICATION_ID = 1
        const val NOTIFICATION_TAG = "verse-of-the-day"
        const val NOTIFICATION_REQUEST_CODE = 831
        const val NOTIFICATION_TEXT_LIMIT = 100
    }
}

package com.ucscode.gtransbible.daily

import android.content.Context
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import java.util.UUID

/** Test-only trigger for instrumentation/debugging; this class is absent from release variants. */
object DebugDailyVerseNotificationTrigger {
    fun enqueueNow(context: Context): UUID {
        val request = OneTimeWorkRequestBuilder<DailyVerseNotificationWorker>().build()
        WorkManager.getInstance(context.applicationContext).enqueue(request)
        return request.id
    }
}

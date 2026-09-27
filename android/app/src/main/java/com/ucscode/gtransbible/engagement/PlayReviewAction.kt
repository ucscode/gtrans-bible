package com.ucscode.gtransbible.engagement

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import com.google.android.play.core.review.ReviewManagerFactory

object PlayReviewAction {
    internal fun runSafely(request: () -> Unit, onUnavailable: () -> Unit) {
        try {
            request()
        } catch (_: Exception) {
            runCatching(onUnavailable)
        }
    }

    fun request(activity: Activity) {
        runSafely(request = {
            val manager = ReviewManagerFactory.create(activity)
            manager.requestReviewFlow().addOnCompleteListener(activity) { request ->
                if (!request.isSuccessful) {
                    openStoreFallback(activity)
                    return@addOnCompleteListener
                }
                runCatching {
                    manager.launchReviewFlow(activity, request.result)
                        .addOnCompleteListener(activity) { }
                }.onFailure { openStoreFallback(activity) }
            }
        }, onUnavailable = { openStoreFallback(activity) })
    }

    private fun openStoreFallback(activity: Activity) {
        val urls = AppStoreConfig.fallbackUrls()
        if (urls.isEmpty()) return
        val appId = AppStoreConfig.PRODUCTION_APPLICATION_ID ?: return
        if (appId == activity.packageName) return

        for (url in urls) {
            try {
                activity.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                return
            } catch (_: ActivityNotFoundException) {
                // Try the web listing after the Play Store URI.
            } catch (_: Exception) {
                // Store fallback is best effort and must never interrupt reading.
            }
        }
    }
}

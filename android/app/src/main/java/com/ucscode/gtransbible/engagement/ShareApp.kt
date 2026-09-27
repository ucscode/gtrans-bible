package com.ucscode.gtransbible.engagement

import android.content.Context
import android.content.Intent

object ShareApp {
    const val APP_NAME = "Igbo Bible & English KJV"
    const val DESCRIPTION = "Read IGBOB (mod) alongside the English KJV."

    fun content(playStoreUrl: String? = AppStoreConfig.configuredPlayStoreUrl()): String = buildString {
        appendLine(APP_NAME)
        append(DESCRIPTION)
        playStoreUrl?.takeIf(String::isNotBlank)?.let {
            appendLine()
            append(it)
        }
    }

    fun createSendIntent(playStoreUrl: String? = AppStoreConfig.configuredPlayStoreUrl()): Intent =
        Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, content(playStoreUrl))
        }

    fun createChooserIntent(playStoreUrl: String? = AppStoreConfig.configuredPlayStoreUrl()): Intent =
        Intent.createChooser(createSendIntent(playStoreUrl), null)

    fun launchChooser(context: Context, playStoreUrl: String? = AppStoreConfig.configuredPlayStoreUrl()) {
        context.startActivity(createChooserIntent(playStoreUrl))
    }
}

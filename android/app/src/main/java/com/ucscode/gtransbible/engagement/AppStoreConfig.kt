package com.ucscode.gtransbible.engagement

/** Store metadata is intentionally empty until the production listing is known. */
object AppStoreConfig {
    private const val DEVELOPMENT_APPLICATION_ID = "com.ucscode.gtransbible.dev"
    val PRODUCTION_APPLICATION_ID: String? = null
    val PLAY_STORE_URL: String? = null

    fun configuredPlayStoreUrl(): String? = PLAY_STORE_URL
        ?.takeIf(String::isNotBlank)
        ?: PRODUCTION_APPLICATION_ID
            ?.takeIf { it.isNotBlank() && it != DEVELOPMENT_APPLICATION_ID }
            ?.let(::playStoreUrlFor)

    fun fallbackUrls(): List<String> {
        val appId = PRODUCTION_APPLICATION_ID
            ?.takeIf { it.isNotBlank() && it != DEVELOPMENT_APPLICATION_ID }
            ?: return emptyList()
        return playStoreFallbackUrls(appId, PLAY_STORE_URL)
    }
}

fun playStoreUrlFor(packageId: String): String =
    "https://play.google.com/store/apps/details?id=$packageId"

fun playStoreFallbackUrls(packageId: String, playStoreUrl: String? = null): List<String> = listOf(
    "market://details?id=$packageId",
    playStoreUrl?.takeIf(String::isNotBlank) ?: playStoreUrlFor(packageId),
)

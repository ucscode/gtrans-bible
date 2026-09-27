package com.ucscode.gtransbible.ads

enum class AdPlacement {
    HOME,
    BOOKS,
    CHAPTERS,
    READER,
    ABOUT,
    NONE,
}

object AdPolicy {
    const val APP_OPEN_COOLDOWN_MS = 5 * 60 * 1000L
    const val MIN_BACKGROUND_FOR_APP_OPEN_MS = 30 * 1000L

    fun allowsBanner(adsEnabled: Boolean, placement: AdPlacement): Boolean =
        adsEnabled && placement in setOf(
            AdPlacement.HOME,
            AdPlacement.BOOKS,
            AdPlacement.CHAPTERS,
            AdPlacement.READER,
        )

    fun shouldShowBannerSlot(placementAllowsBanner: Boolean, adLoaded: Boolean): Boolean =
        placementAllowsBanner && adLoaded

    fun canShowAppOpen(
        adsEnabled: Boolean,
        firstEverLaunch: Boolean,
        adLoaded: Boolean,
        adAlreadyShowing: Boolean,
        backgroundDurationMs: Long,
        lastShownAtMs: Long,
        nowMs: Long,
    ): Boolean {
        if (!adsEnabled || firstEverLaunch || !adLoaded || adAlreadyShowing) return false
        if (backgroundDurationMs < MIN_BACKGROUND_FOR_APP_OPEN_MS) return false
        if (lastShownAtMs == 0L) return true
        if (nowMs < lastShownAtMs) return false
        return nowMs - lastShownAtMs >= APP_OPEN_COOLDOWN_MS
    }
}

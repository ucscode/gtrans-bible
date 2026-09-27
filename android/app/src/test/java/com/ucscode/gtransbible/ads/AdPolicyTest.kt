package com.ucscode.gtransbible.ads

import com.ucscode.gtransbible.BuildConfig
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AdPolicyTest {
    @Test
    fun firstEverLaunchNeverShowsAppOpenAd() {
        assertFalse(canShow(firstEverLaunch = true))
    }

    @Test
    fun laterEligibleLaunchCanShowLoadedAppOpenAd() {
        assertTrue(canShow(firstEverLaunch = false))
    }

    @Test
    fun appOpenCooldownPreventsImmediateRepeat() {
        val now = 1_000_000L
        assertFalse(
            AdPolicy.canShowAppOpen(
                adsEnabled = true,
                firstEverLaunch = false,
                adLoaded = true,
                adAlreadyShowing = false,
                backgroundDurationMs = AdPolicy.MIN_BACKGROUND_FOR_APP_OPEN_MS,
                lastShownAtMs = now - 60_000L,
                nowMs = now,
            ),
        )
    }

    @Test
    fun shortBackgroundDoesNotCountAsMeaningfulReturn() {
        assertFalse(canShow(firstEverLaunch = false, backgroundDuration = 5_000L))
    }

    @Test
    fun fullscreenAdCannotStack() {
        assertFalse(canShow(firstEverLaunch = false, adAlreadyShowing = true))
    }

    @Test
    fun homeBooksChaptersReaderAndDailyVerseAllowBannersButAboutDoesNot() {
        assertTrue(AdPolicy.allowsBanner(true, AdPlacement.HOME))
        assertTrue(AdPolicy.allowsBanner(true, AdPlacement.BOOKS))
        assertTrue(AdPolicy.allowsBanner(true, AdPlacement.CHAPTERS))
        assertTrue(AdPolicy.allowsBanner(true, AdPlacement.READER))
        assertTrue(AdPolicy.allowsBanner(true, AdPlacement.DAILY_VERSE))
        assertFalse(AdPolicy.allowsBanner(true, AdPlacement.ABOUT))
        assertFalse(AdPolicy.allowsBanner(false, AdPlacement.HOME))
        assertFalse(AdPolicy.allowsBanner(false, AdPlacement.READER))
    }

    @Test
    fun emptyOrIneligibleBannerSlotStaysHidden() {
        assertFalse(AdPolicy.shouldShowBannerSlot(placementAllowsBanner = true, adLoaded = false))
        assertFalse(AdPolicy.shouldShowBannerSlot(placementAllowsBanner = false, adLoaded = true))
        assertTrue(AdPolicy.shouldShowBannerSlot(placementAllowsBanner = true, adLoaded = true))
    }

    @Test
    fun debugBuildUsesGoogleTestIdentifiers() {
        assertEquals("TEST", BuildConfig.ADMOB_MODE)
        assertEquals("ca-app-pub-3940256099942544~3347511713", BuildConfig.ADMOB_APP_ID)
        assertEquals("ca-app-pub-3940256099942544/9257395921", BuildConfig.ADMOB_APP_OPEN_UNIT_ID)
        assertEquals("ca-app-pub-3940256099942544/9214589741", BuildConfig.ADMOB_BANNER_UNIT_ID)
    }

    private fun canShow(
        firstEverLaunch: Boolean,
        backgroundDuration: Long = Long.MAX_VALUE,
        adAlreadyShowing: Boolean = false,
    ): Boolean = AdPolicy.canShowAppOpen(
        adsEnabled = true,
        firstEverLaunch = firstEverLaunch,
        adLoaded = true,
        adAlreadyShowing = adAlreadyShowing,
        backgroundDurationMs = backgroundDuration,
        lastShownAtMs = 0L,
        nowMs = 10_000_000L,
    )
}

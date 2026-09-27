package com.ucscode.gtransbible.engagement

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class EngagementTest {
    @Test fun shareTextHasProductNameAndDescriptionWithoutUnconfiguredStoreUrl() {
        val text = ShareApp.content(playStoreUrl = null)

        assertTrue(text.contains("Igbo Bible & English KJV"))
        assertTrue(text.contains("Read IGBOB (mod) alongside the English KJV."))
        assertFalse(text.contains("play.google.com"))
        assertFalse(text.contains("localhost"))
    }

    @Test fun configuredStoreUrlIsIncludedInShareText() {
        val url = "https://play.google.com/store/apps/details?id=com.example.igbob"

        assertTrue(ShareApp.content(url).contains(url))
    }

    @Test fun fallbackUrlsUseTheConfiguredPackageMetadata() {
        val url = "https://play.google.com/store/apps/details?id=com.example.igbob"
        assertEquals(
            listOf(
                "market://details?id=com.example.igbob",
                "https://play.google.com/store/apps/details?id=com.example.igbob",
            ),
            playStoreFallbackUrls("com.example.igbob"),
        )
        assertEquals(null, AppStoreConfig.PRODUCTION_APPLICATION_ID)
        assertEquals(null, AppStoreConfig.configuredPlayStoreUrl())
        assertTrue(AppStoreConfig.fallbackUrls().isEmpty())
        assertEquals(
            listOf("market://details?id=com.example.igbob", url),
            playStoreFallbackUrls("com.example.igbob", url),
        )
    }

    @Test fun unavailableReviewRequestFailsSilentlyAndRunsBestEffortFallback() {
        var fallbackCalled = false

        PlayReviewAction.runSafely(
            request = { throw IllegalStateException("Review API unavailable") },
            onUnavailable = { fallbackCalled = true },
        )

        assertTrue(fallbackCalled)
    }

    @Test fun failedFallbackDoesNotEscapeReviewAction() {
        PlayReviewAction.runSafely(
            request = { throw IllegalStateException("Review API unavailable") },
            onUnavailable = { throw IllegalStateException("No store handler") },
        )
    }
}

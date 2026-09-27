package com.ucscode.gtransbible.ui

import android.view.View
import android.widget.TextView
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.engagement.ShareApp
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class RateAndShareInstrumentedTest {
    @Test fun sidebarShowsBothActionsAndRateUsCanBeTappedSafely() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            awaitAbout(scenario)
            openDrawer(scenario)
            scenario.onActivity { activity ->
                val rateRow = activity.findViewById<View>(R.id.navRateUs)
                val shareRow = activity.findViewById<View>(R.id.navShareApp)
                val rate = (rateRow as android.view.ViewGroup).getChildAt(1) as TextView
                val share = (shareRow as android.view.ViewGroup).getChildAt(1) as TextView
                assertEquals("Rate Us", rate.text.toString())
                assertEquals("Share App", share.text.toString())
                assertTrue(rateRow.isClickable)
                assertTrue(shareRow.isClickable)
                rateRow.performClick()
                assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.aboutScreen).visibility)
            }
        } finally {
            scenario.close()
        }
    }

    @Test fun shareActionOpensChooserWithPlainTextProductMessageAndNoUnpublishedUrl() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            awaitAbout(scenario)
            openDrawer(scenario)
            scenario.onActivity { it.findViewById<View>(R.id.navShareApp).performClick() }

            val chooser = ShareApp.createChooserIntent()
            assertEquals(android.content.Intent.ACTION_CHOOSER, chooser.action)
            @Suppress("DEPRECATION")
            val sendIntent = chooser.getParcelableExtra(android.content.Intent.EXTRA_INTENT) as? android.content.Intent
            assertNotNull(sendIntent)
            assertEquals(android.content.Intent.ACTION_SEND, sendIntent?.action)
            assertEquals("text/plain", sendIntent?.type)
            val message = sendIntent?.getStringExtra(android.content.Intent.EXTRA_TEXT).orEmpty()
            assertTrue(message.contains("Igbo Bible & English KJV"))
            assertTrue(message.contains("Read IGBOB (mod) alongside the English KJV."))
            assertTrue(!message.contains("play.google.com"))
        } finally {
            scenario.close()
        }
    }

    private fun openDrawer(scenario: ActivityScenario<MainActivity>) {
        scenario.onActivity { activity -> activity.findViewById<View>(R.id.navigationButton).performClick() }
        val deadline = System.currentTimeMillis() + 5_000
        while (System.currentTimeMillis() < deadline) {
            var open = false
            scenario.onActivity { activity ->
                open = activity.findViewById<DrawerLayout>(R.id.drawerLayout).isDrawerOpen(GravityCompat.START)
            }
            if (open) return
            Thread.sleep(50)
        }
        throw AssertionError("Navigation drawer did not open")
    }

    private fun awaitAbout(scenario: ActivityScenario<MainActivity>) {
        val deadline = System.currentTimeMillis() + 15_000
        while (System.currentTimeMillis() < deadline) {
            var ready = false
            scenario.onActivity { activity ->
                val about = activity.findViewById<View>(R.id.aboutScreen)
                if (about.visibility == View.VISIBLE) {
                    ready = true
                } else if (activity.findViewById<View>(R.id.navAbout).isShown) {
                    activity.findViewById<View>(R.id.navAbout).performClick()
                } else {
                    activity.findViewById<View>(R.id.navigationButton).performClick()
                }
            }
            if (ready) return
            Thread.sleep(100)
        }
        throw AssertionError("About screen did not become visible")
    }
}

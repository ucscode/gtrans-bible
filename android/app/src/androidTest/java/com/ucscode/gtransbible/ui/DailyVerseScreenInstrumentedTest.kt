package com.ucscode.gtransbible.ui

import android.view.View
import android.widget.FrameLayout
import android.widget.TextView
import androidx.core.widget.NestedScrollView
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.ads.AdPlacement
import com.ucscode.gtransbible.ads.AdPolicy
import com.ucscode.gtransbible.ads.BibleApplication
import com.ucscode.gtransbible.daily.localDateKey
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DailyVerseScreenInstrumentedTest {
    @Test
    fun dedicatedDestinationShowsCachedVerseAndOpensTheExactReaderVerse() {
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        seedTodayVerse(appContext)
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            await(scenario) { it.findViewById<View>(R.id.booksControls).visibility == View.VISIBLE }
            scenario.onActivity { activity ->
                (activity.application as BibleApplication).adsController.adsEnabled = false
                val drawer = activity.findViewById<View>(R.id.navigationButton)
                drawer.performClick()
                val dailyDestination = activity.findViewById<android.view.ViewGroup>(R.id.navDailyVerse)
                assertEquals("Daily Verse", (dailyDestination.getChildAt(1) as TextView).text.toString())
                activity.findViewById<View>(R.id.navDailyVerse).performClick()
            }
            await(scenario) {
                it.findViewById<View>(R.id.dailyVerseScreen).visibility == View.VISIBLE &&
                    it.findViewById<View>(R.id.dailyVerseCard).visibility == View.VISIBLE
            }
            scenario.onActivity { activity ->
                assertEquals("Daily Verse", activity.findViewById<TextView>(R.id.screenTitle).text.toString())
                assertTrue(activity.findViewById<View>(R.id.navDailyVerse).isSelected)
                assertFalse(activity.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.dailyVerseNotificationsSwitch).isChecked)
                val content = activity.findViewById<View>(R.id.mainContent) as android.view.ViewGroup
                val page = activity.findViewById<View>(R.id.dailyVerseScroll)
                val footer = activity.findViewById<View>(R.id.bottomAdSlot)
                assertTrue(content.indexOfChild(page) < content.indexOfChild(footer))
                assertTrue(AdPolicy.allowsBanner(true, AdPlacement.DAILY_VERSE))
                assertTrue(activity.findViewById<TextView>(R.id.dailyVerseIgbo).text.isNotBlank())
                assertTrue(activity.findViewById<TextView>(R.id.dailyVerseEnglish).text.isNotBlank())
                assertEquals("John 3:16", activity.findViewById<TextView>(R.id.dailyVerseReference).text.toString())
                activity.findViewById<View>(R.id.dailyVerseCard).performClick()
            }
            await(scenario) {
                it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE &&
                    it.findViewById<TextView>(R.id.screenTitle).text.toString().endsWith("3")
            }
            scenario.onActivity { activity ->
                val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                assertEquals(15, (list.layoutManager as androidx.recyclerview.widget.LinearLayoutManager).findFirstVisibleItemPosition())
                val target = list.findViewHolderForAdapterPosition(15)!!.itemView.findViewById<TextView>(R.id.verseNumber)
                assertEquals("16", target.text.toString())
                assertTrue(activity.findViewById<View>(R.id.navBooks).isSelected)
            }
        } finally {
            scenario.close()
            appContext.getSharedPreferences("daily_verse_preferences", 0).edit().clear().commit()
        }
    }

    @Test
    fun homeScrollsAboveItsFixedFooterWhenTheViewportIsShortened() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            await(scenario) { it.findViewById<View>(R.id.booksControls).visibility == View.VISIBLE }
            scenario.onActivity { activity ->
                (activity.application as BibleApplication).adsController.adsEnabled = false
                activity.findViewById<View>(R.id.navigationButton).performClick()
                activity.findViewById<View>(R.id.navHome).performClick()
            }
            await(scenario) { it.findViewById<View>(R.id.homeScroll).visibility == View.VISIBLE }
            scenario.onActivity { activity ->
                val content = activity.findViewById<View>(R.id.mainContent) as android.view.ViewGroup
                val scroll = activity.findViewById<NestedScrollView>(R.id.homeScroll)
                val slot = activity.findViewById<FrameLayout>(R.id.bottomAdSlot)
                assertTrue(scroll.parent === content)
                assertTrue(content.indexOfChild(scroll) < content.indexOfChild(slot))
                assertNull(activity.findViewById<View>(R.id.homeScreen).findViewById<View>(R.id.dailyVerseCard))
                slot.removeAllViews()
                slot.addView(View(activity), FrameLayout.LayoutParams(-1, (250 * activity.resources.displayMetrics.density).toInt()))
                slot.visibility = View.VISIBLE
                scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
            }
            await(scenario) {
                val scroll = it.findViewById<NestedScrollView>(R.id.homeScroll)
                !scroll.canScrollVertically(1)
            }
            scenario.onActivity { activity ->
                val scroll = activity.findViewById<NestedScrollView>(R.id.homeScroll)
                val slot = activity.findViewById<View>(R.id.bottomAdSlot)
                val scrollPosition = IntArray(2)
                val slotPosition = IntArray(2)
                scroll.getLocationOnScreen(scrollPosition)
                slot.getLocationOnScreen(slotPosition)
                assertTrue(scrollPosition[1] + scroll.height <= slotPosition[1])
                listOf(R.id.continueButton, R.id.browseButton).forEach { id ->
                    val button = activity.findViewById<View>(id)
                    val position = IntArray(2)
                    button.getLocationOnScreen(position)
                    assertTrue("Home button must remain in the scroll viewport", position[1] >= scrollPosition[1])
                    assertTrue("Home button must remain above the fixed footer", position[1] + button.height <= slotPosition[1])
                }
                assertTrue(AdPolicy.allowsBanner(true, AdPlacement.HOME))
            }
        } finally {
            scenario.close()
        }
    }

    private fun seedTodayVerse(context: android.content.Context) {
        context.getSharedPreferences("daily_verse_preferences", 0).edit()
            .putString("cached_date", localDateKey(System.currentTimeMillis()))
            .putString("cached_reference", "John 3:16")
            .putString("cached_verse_id", "jhn-3-16")
            .putString("cached_source_id", "instrumentation")
            .putLong("cached_fetched_at", System.currentTimeMillis())
            .putBoolean("notifications_enabled", false)
            .commit()
    }

    private fun await(scenario: ActivityScenario<MainActivity>, condition: (MainActivity) -> Boolean) {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        repeat(100) {
            instrumentation.waitForIdleSync()
            var ready = false
            scenario.onActivity { ready = condition(it) }
            if (ready) return
            Thread.sleep(100)
        }
        throw AssertionError("Timed out waiting for the Verse of the Day screen")
    }
}

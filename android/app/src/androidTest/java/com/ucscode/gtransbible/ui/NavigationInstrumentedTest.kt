package com.ucscode.gtransbible.ui

import android.view.View
import android.view.MotionEvent
import android.os.SystemClock
import android.widget.FrameLayout
import android.widget.TextView
import androidx.recyclerview.widget.GridLayoutManager
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.ads.BibleApplication
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NavigationInstrumentedTest {
    @Suppress("DEPRECATION")
    @Test fun booksStartupHomeDrawerTestamentNamesReaderLayoutAndContinueReading() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            scenario.onActivity { (it.application as BibleApplication).adsController.adsEnabled = false }
            await(scenario) {
                it.findViewById<View>(R.id.booksControls).visibility == View.VISIBLE &&
                    it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39
            }
            scenario.onActivity { activity ->
                assertEquals(View.GONE, activity.findViewById<View>(R.id.homeScreen).visibility)
                assertTrue(activity.findViewById<View>(R.id.navBooks).isSelected)
                val adSlot = activity.findViewById<View>(R.id.bottomAdSlot)
                assertEquals(View.GONE, adSlot.visibility)
                assertEquals(0, adSlot.height)
                assertEquals(android.graphics.Color.TRANSPARENT, activity.window.statusBarColor)
                val root = activity.findViewById<View>(R.id.drawerLayout)
                val insets = ViewCompat.getRootWindowInsets(root)!!
                assertEquals(
                    insets.getInsets(WindowInsetsCompat.Type.statusBars()).top,
                    activity.findViewById<View>(R.id.appBar).paddingTop,
                )
                val safeArea = insets.getInsets(
                    WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout(),
                )
                assertEquals(
                    safeArea.left,
                    activity.findViewById<View>(R.id.mainContent).paddingLeft,
                )
                assertEquals(
                    safeArea.right,
                    activity.findViewById<View>(R.id.mainContent).paddingRight,
                )
                assertEquals(
                    safeArea.bottom,
                    activity.findViewById<View>(R.id.mainContent).paddingBottom,
                )
                activity.findViewById<View>(R.id.navigationButton).performClick()
                activity.findViewById<View>(R.id.navHome).performClick()
            }
            await(scenario) { it.findViewById<View>(R.id.homeScreen).visibility == View.VISIBLE }
            scenario.onActivity { assertTrue(it.findViewById<View>(R.id.navHome).isSelected) }

            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.drawerlayout.widget.DrawerLayout>(R.id.drawerLayout).isDrawerOpen(androidx.core.view.GravityCompat.START) }
            scenario.onActivity { it.findViewById<View>(R.id.navBooks).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39 }

            scenario.onActivity { activity ->
                val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                val holder = list.findViewHolderForAdapterPosition(0)!!
                assertEquals("Jenesis", holder.itemView.findViewById<TextView>(R.id.bookName).text.toString())
                assertEquals("Genesis", holder.itemView.findViewById<TextView>(R.id.bookEnglishName).text.toString())
                activity.findViewById<View>(R.id.newTestamentButton).performClick()
            }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 27 }
            scenario.onActivity { activity ->
                val holder = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                assertEquals("Matiu", holder.itemView.findViewById<TextView>(R.id.bookName).text.toString())
                assertEquals("Matthew", holder.itemView.findViewById<TextView>(R.id.bookEnglishName).text.toString())
                activity.findViewById<View>(R.id.navAbout).performClick()
            }
            await(scenario) { it.findViewById<View>(R.id.aboutScreen).visibility == View.VISIBLE }
            scenario.onActivity { activity ->
                assertTrue(activity.findViewById<View>(R.id.navAbout).isSelected)
                assertEquals(View.GONE, activity.findViewById<View>(R.id.bottomAdSlot).visibility)
                assertEquals(
                    "Built by Ucscode, a software studio focused on practical digital products.",
                    activity.findViewById<TextView>(R.id.aboutCreatorDescription).text.toString(),
                )
                assertEquals(
                    "The Igbo text preserves the historic IGBOB translation while updating historical orthography for readability.",
                    activity.findViewById<TextView>(R.id.aboutTranslationNote).text.toString(),
                )
                assertEquals("ucscode.com", activity.findViewById<TextView>(R.id.websiteText).text.toString())
            }

            scenario.onActivity { it.findViewById<View>(R.id.navHome).performClick() }
            await(scenario) { it.findViewById<View>(R.id.homeScreen).visibility == View.VISIBLE }
            scenario.onActivity {
                it.findViewById<View>(R.id.browseButton).performClick()
                it.findViewById<View>(R.id.oldTestamentButton).performClick()
            }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39 }
            scenario.onActivity { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).getChildAt(0).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 50 }
            scenario.onActivity { activity ->
                assertEquals("Jenesis", activity.findViewById<TextView>(R.id.screenTitle).text.toString())
                assertEquals("Genesis", activity.findViewById<TextView>(R.id.chapterEnglishTitle).text.toString())
                val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                assertTrue((list.layoutManager as GridLayoutManager).spanCount in 4..5)
                val chapterSidePadding = (10 * activity.resources.displayMetrics.density).toInt()
                assertEquals(chapterSidePadding, list.paddingLeft)
                assertEquals(chapterSidePadding, list.paddingRight)
                val tile = list.findViewHolderForAdapterPosition(0)!!.itemView
                assertTrue(tile is ChapterTileView)
                assertTrue(kotlin.math.abs(tile.width - tile.height) <= 1)
                assertTrue(tile.isClickable && tile.isFocusable)
            }
            scenario.onActivity { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).getChildAt(0).performClick() }
            await(scenario) {
                it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Jenesis 1" &&
                    it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE &&
                    it.findViewById<View>(R.id.bottomAdSlot).visibility == View.GONE &&
                    it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount?.let { count -> count > 0 } == true
            }

            assertReaderFooterResizesContent(scenario, R.id.plainButton, R.id.plainText)
            assertReaderFooterResizesContent(scenario, R.id.sideButton, R.id.sideIgbo)
            assertReaderFooterResizesContent(scenario, R.id.followButton, R.id.followIgbo)

            val retainedLayout = BooleanArray(3)
            scenario.onActivity { activity ->
                retainedLayout[0] = activity.findViewById<View>(R.id.plainButton).isSelected
                retainedLayout[1] = activity.findViewById<View>(R.id.sideButton).isSelected
                retainedLayout[2] = activity.findViewById<View>(R.id.followButton).isSelected
                val title = activity.findViewById<View>(R.id.screenTitleRow)
                assertTrue(title.isClickable && title.isFocusable)
                assertEquals("Choose book, currently reading Jenesis 1", title.contentDescription.toString())
                assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.screenTitleDropdown).visibility)
                title.performClick()
            }
            await(scenario) { it.bookPickerDialog?.listView?.count == 66 }
            scenario.onActivity { activity ->
                val picker = activity.bookPickerDialog!!.listView
                assertEquals(66, picker.count)
                assertEquals(0, picker.checkedItemPosition)
                picker.performItemClick(picker.getChildAt(0), 0, picker.adapter.getItemId(0))
            }
            await(scenario) {
                it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 50 &&
                    it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).layoutManager is GridLayoutManager
            }
            scenario.onActivity { activity ->
                val chapters = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                assertTrue((chapters.layoutManager as GridLayoutManager).spanCount in 4..5)
                chapters.findViewHolderForAdapterPosition(9)!!.itemView.performClick()
            }
            await(scenario) {
                it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Jenesis 10" &&
                    it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE &&
                    it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount?.let { count -> count > 0 } == true
            }
            scenario.onActivity { activity ->
                assertEquals(retainedLayout[0], activity.findViewById<View>(R.id.plainButton).isSelected)
                assertEquals(retainedLayout[1], activity.findViewById<View>(R.id.sideButton).isSelected)
                assertEquals(retainedLayout[2], activity.findViewById<View>(R.id.followButton).isSelected)
                activity.findViewById<View>(R.id.chapterNavigationLabel).performClick()
            }
            await(scenario) { it.chapterPickerDialog?.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)?.adapter?.itemCount == 50 }
            scenario.onActivity { activity ->
                val picker = activity.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                picker.scrollToPosition(9)
            }
            await(scenario) {
                it.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                    .findViewHolderForAdapterPosition(9)?.itemView?.isSelected == true
            }
            scenario.onActivity { activity ->
                val picker = activity.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                picker.scrollToPosition(0)
                picker.post { picker.findViewHolderForAdapterPosition(0)?.itemView?.performClick() }
            }
            await(scenario) {
                it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Jenesis 1" &&
                    it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE
            }

            scenario.onActivity { activity ->
                val verse = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                assertTrue(verse.itemView.findViewById<TextView>(R.id.plainText).isTextSelectable)
                activity.findViewById<View>(R.id.plainButton).performClick()
                val igboEdition = activity.findViewById<TextView>(R.id.editionIgboButton)
                val kjvEdition = activity.findViewById<TextView>(R.id.editionKjvButton)
                assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.plainEditionSelector).visibility)
                assertEquals("IGBOB (mod)", igboEdition.text.toString())
                assertEquals("KJV", kjvEdition.text.toString())
                assertTrue(igboEdition.isClickable)
                assertTrue(kjvEdition.isClickable)
                val wasIgboSelected = igboEdition.isSelected
                assertTrue(wasIgboSelected || kjvEdition.isSelected)
                if (wasIgboSelected) kjvEdition.performClick() else igboEdition.performClick()
                assertTrue(igboEdition.isSelected != wasIgboSelected)
                assertEquals(igboEdition.isSelected, activity.getSharedPreferences("reader_preferences", 0)
                    .getString("plain_edition", null) == "MODERN_IGBO")
                if (wasIgboSelected) igboEdition.performClick() else kjvEdition.performClick()
                assertEquals(wasIgboSelected, igboEdition.isSelected)
                activity.findViewById<View>(R.id.sideButton).performClick()
                assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.sideIndicator).visibility)
                assertEquals(View.GONE, activity.findViewById<View>(R.id.plainIndicator).visibility)
            }
            await(scenario) {
                val verse = it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                verse.itemView.findViewById<View>(R.id.sideBySide).visibility == View.VISIBLE
            }
            scenario.onActivity { activity ->
                assertEquals(View.GONE, activity.findViewById<View>(R.id.bottomAdSlot).visibility)
            }
            scenario.onActivity { activity ->
                val verse = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                assertTrue(verse.itemView.findViewById<TextView>(R.id.sideIgbo).isTextSelectable)
                assertTrue(verse.itemView.findViewById<TextView>(R.id.sideEnglish).isTextSelectable)
                activity.findViewById<View>(R.id.followButton).performClick()
            }
            await(scenario) {
                val verse = it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                verse.itemView.findViewById<View>(R.id.followUp).visibility == View.VISIBLE
            }
            scenario.onActivity { activity ->
                val verse = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                val followUp = verse.itemView.findViewById<View>(R.id.followUp) as android.widget.LinearLayout
                val igbo = verse.itemView.findViewById<TextView>(R.id.followIgbo)
                val english = verse.itemView.findViewById<TextView>(R.id.followEnglish)
                assertTrue(followUp.indexOfChild(igbo) < followUp.indexOfChild(english))
                assertTrue(igbo.isTextSelectable && english.isTextSelectable)
                assertEquals(activity.getColor(R.color.reader_english_secondary), english.currentTextColor)
                activity.findViewById<View>(R.id.sideButton).performClick()
            }
            await(scenario) {
                val verse = it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                verse.itemView.findViewById<View>(R.id.sideBySide).visibility == View.VISIBLE
            }
            scenario.recreate()
            awaitReaderChapter(scenario, "Jenesis 1")
            scenario.onActivity { activity ->
                assertTrue(activity.findViewById<View>(R.id.sideButton).isSelected)
                assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.sideIndicator).visibility)
                val verse = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(0)!!
                assertTrue(verse.itemView.findViewById<View>(R.id.sideBySide).visibility == View.VISIBLE)
            }
            scenario.onActivity { it.findViewById<View>(R.id.nextChapterButton).performClick() }
            awaitReaderChapter(scenario, "Jenesis 2")
            scenario.onActivity { activity ->
                assertTrue(activity.findViewById<View>(R.id.sideButton).isSelected)
            }
            swipeReader(scenario, left = true, horizontal = true)
            awaitReaderChapter(scenario, "Jenesis 3")
            swipeReader(scenario, left = false, horizontal = false)
            await(scenario) { it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Jenesis 3" }
            swipeReader(scenario, left = false, horizontal = true)
            awaitReaderChapter(scenario, "Jenesis 2")
            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 50 }
            scenario.onActivity { activity ->
                val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                val chapter = (list.adapter as ChapterAdapter)
                assertEquals(50, chapter.itemCount)
                assertTrue(list.findViewHolderForAdapterPosition(1)!!.itemView.isSelected)
            }
            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39 }
            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.drawerlayout.widget.DrawerLayout>(R.id.drawerLayout).isDrawerOpen(androidx.core.view.GravityCompat.START) }
            scenario.onActivity { it.findViewById<View>(R.id.navHome).performClick() }
            await(scenario) { it.findViewById<View>(R.id.homeScreen).visibility == View.VISIBLE }
            scenario.onActivity { activity ->
                assertTrue(activity.findViewById<TextView>(R.id.continueButton).text.toString().contains("Jenesis 2"))
                activity.findViewById<View>(R.id.continueButton).performClick()
            }
            await(scenario) { it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Jenesis 2" }

            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 50 }
            scenario.onActivity { it.findViewById<View>(R.id.navigationButton).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39 }
            scenario.onActivity { it.findViewById<View>(R.id.newTestamentButton).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 27 }
            scenario.onActivity { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).getChildAt(0).performClick() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 28 }
            scenario.onActivity { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).scrollToPosition(27) }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).findViewHolderForAdapterPosition(27) != null }
            scenario.onActivity { activity ->
                val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                list.findViewHolderForAdapterPosition(27)!!.itemView.performClick()
            }
            await(scenario) { it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Matiu 28" }
            scenario.onActivity { it.findViewById<View>(R.id.nextChapterButton).performClick() }
            await(scenario) { it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Mak 1" }
            scenario.onActivity { it.findViewById<View>(R.id.previousChapterButton).performClick() }
            await(scenario) { it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Matiu 28" }
            scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 28 }
            scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
            await(scenario) { it.findViewById<View>(R.id.booksControls).visibility == View.VISIBLE }
            scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
            await(scenario) { it.isFinishing }
        } finally {
            scenario.close()
        }
    }

    @Test fun psalmsChapterPickerShowsScrollableSquareTilesAndCurrentSelection() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        try {
            await(scenario) { it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).adapter?.itemCount == 39 }
            scenario.onActivity { activity ->
                val books = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                books.scrollToPosition(18)
                books.post { books.findViewHolderForAdapterPosition(18)?.itemView?.performClick() }
            }
            await(scenario) {
                val list = it.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                list.layoutManager is GridLayoutManager && list.adapter?.itemCount == 150
            }
            scenario.onActivity { activity ->
                val chapters = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
                assertTrue((chapters.layoutManager as GridLayoutManager).spanCount in 4..5)
                val tile = chapters.findViewHolderForAdapterPosition(0)!!.itemView
                assertTrue(tile is ChapterTileView)
                assertTrue(kotlin.math.abs(tile.width - tile.height) <= 1)
                tile.performClick()
            }
            await(scenario) {
                it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Abù Ọma 1" &&
                    it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE
            }
            scenario.onActivity { it.findViewById<View>(R.id.chapterNavigationLabel).performClick() }
            await(scenario) {
                it.chapterPickerDialog?.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)?.adapter?.itemCount == 150
            }
            scenario.onActivity { activity ->
                val picker = activity.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                assertTrue((picker.layoutManager as GridLayoutManager).spanCount in 4..5)
                assertTrue(picker.isVerticalScrollBarEnabled)
                assertTrue(!picker.isScrollbarFadingEnabled)
                assertTrue(picker.height < activity.resources.displayMetrics.heightPixels * 0.82f)
                assertTrue(picker.findViewHolderForAdapterPosition(0)!!.itemView.isSelected)
                picker.scrollToPosition(149)
            }
            await(scenario) {
                it.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                    .findViewHolderForAdapterPosition(149) != null
            }
            scenario.onActivity { activity ->
                val picker = activity.chapterPickerDialog!!.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.chapterPickerList)!!
                picker.findViewHolderForAdapterPosition(149)!!.itemView.performClick()
            }
            await(scenario) {
                it.findViewById<TextView>(R.id.screenTitle).text.toString() == "Abù Ọma 150" &&
                    it.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE
            }
        } finally {
            scenario.close()
        }
    }

    private fun await(scenario: ActivityScenario<MainActivity>, condition: (MainActivity) -> Boolean) {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        repeat(100) {
            instrumentation.waitForIdleSync()
            var satisfied = false
            scenario.onActivity { satisfied = condition(it) }
            if (satisfied) return
            Thread.sleep(100)
        }
        throw AssertionError("Timed out waiting for the expected app screen state")
    }

    private fun awaitReaderChapter(scenario: ActivityScenario<MainActivity>, title: String) = await(scenario) { activity ->
        activity.findViewById<TextView>(R.id.screenTitle).text.toString() == title &&
            activity.findViewById<View>(R.id.readerControls).visibility == View.VISIBLE &&
            kotlin.math.abs(activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list).translationX) < 1f
    }

    private fun assertReaderFooterResizesContent(
        scenario: ActivityScenario<MainActivity>,
        modeButtonId: Int,
        verseTextId: Int,
    ) {
        scenario.onActivity { activity ->
            activity.findViewById<View>(modeButtonId).performClick()
            val slot = activity.findViewById<FrameLayout>(R.id.bottomAdSlot)
            slot.removeAllViews()
            slot.addView(
                View(activity),
                FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    (56 * activity.resources.displayMetrics.density).toInt(),
                ),
            )
            slot.visibility = View.VISIBLE
            val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
            list.scrollToPosition(list.adapter!!.itemCount - 1)
            list.post { list.scrollBy(0, Int.MAX_VALUE) }
        }

        await(scenario) { activity ->
            val slot = activity.findViewById<FrameLayout>(R.id.bottomAdSlot)
            val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
            slot.visibility == View.VISIBLE &&
                !list.canScrollVertically(1) &&
                list.findViewHolderForAdapterPosition(list.adapter!!.itemCount - 1) != null
        }
        scenario.onActivity { activity ->
            val slot = activity.findViewById<FrameLayout>(R.id.bottomAdSlot)
            val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
            val lastVerse = list.findViewHolderForAdapterPosition(list.adapter!!.itemCount - 1)!!.itemView
            val modeText = lastVerse.findViewById<View>(verseTextId)
            val listPosition = IntArray(2)
            val slotPosition = IntArray(2)
            list.getLocationOnScreen(listPosition)
            slot.getLocationOnScreen(slotPosition)

            assertEquals(View.VISIBLE, modeText.visibility)
            assertTrue("Reader list must resize above its footer", listPosition[1] + list.height <= slotPosition[1])
            assertTrue("Last verse must remain inside the scrolling content", lastVerse.bottom <= list.height)
            assertFalse("The last verse must be reachable above the footer", list.canScrollVertically(1))

            slot.removeAllViews()
            slot.visibility = View.GONE
            list.scrollToPosition(0)
            assertEquals(View.GONE, slot.visibility)
        }
        await(scenario) {
            it.findViewById<View>(R.id.bottomAdSlot).visibility == View.GONE
        }
    }

    private fun swipeReader(scenario: ActivityScenario<MainActivity>, left: Boolean, horizontal: Boolean) {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val bounds = IntArray(2)
        var width = 0
        var height = 0
        scenario.onActivity { activity ->
            val list = activity.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.list)
            list.getLocationOnScreen(bounds)
            width = list.width
            height = list.height
        }
        val startX: Float
        val endX: Float
        val startY: Float
        val endY: Float
        if (horizontal) {
            startX = bounds[0] + width * if (left) 0.88f else 0.12f
            endX = bounds[0] + width * if (left) 0.12f else 0.88f
            startY = bounds[1] + height * 0.55f
            endY = startY + 4f
        } else {
            startX = bounds[0] + width * 0.5f
            endX = startX + 8f
            startY = bounds[1] + height * 0.78f
            endY = bounds[1] + height * 0.28f
        }
        val downTime = SystemClock.uptimeMillis()
        instrumentation.sendPointerSync(MotionEvent.obtain(downTime, downTime, MotionEvent.ACTION_DOWN, startX, startY, 0))
        val moveTime = downTime + 120
        instrumentation.sendPointerSync(MotionEvent.obtain(downTime, moveTime, MotionEvent.ACTION_MOVE, endX, endY, 0))
        instrumentation.sendPointerSync(MotionEvent.obtain(downTime, moveTime + 120, MotionEvent.ACTION_UP, endX, endY, 0))
    }
}

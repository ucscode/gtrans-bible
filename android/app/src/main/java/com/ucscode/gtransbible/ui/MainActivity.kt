package com.ucscode.gtransbible.ui

import android.os.Bundle
import android.content.Intent
import android.text.Selection
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.ViewConfiguration
import android.content.res.Configuration
import android.widget.ImageView
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.content.ContextCompat
import androidx.core.net.toUri
import androidx.core.view.GravityCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.ViewCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.data.BibleBook
import com.ucscode.gtransbible.data.BibleChapter
import com.ucscode.gtransbible.data.BibleRepository
import com.ucscode.gtransbible.data.ChapterTransition
import com.ucscode.gtransbible.data.DatabaseInstaller
import com.ucscode.gtransbible.data.PlainEdition
import com.ucscode.gtransbible.data.ReaderLayout
import com.ucscode.gtransbible.data.Testament
import com.ucscode.gtransbible.data.displayIgboBookName
import java.io.File
import java.util.concurrent.Executors
import kotlin.math.abs

class MainActivity : AppCompatActivity() {
    private enum class Screen { HOME, BOOKS, CHAPTERS, READER, ABOUT }

    private val worker = Executors.newSingleThreadExecutor()
    private lateinit var drawer: DrawerLayout
    private lateinit var navigationButton: ImageButton
    private lateinit var list: RecyclerView
    private lateinit var screenTitle: TextView
    private lateinit var chapterEnglishTitle: TextView
    private lateinit var statusText: TextView
    private lateinit var homeScreen: View
    private lateinit var booksControls: View
    private lateinit var aboutScreen: View
    private lateinit var readerControls: View
    private lateinit var backButton: View
    private lateinit var homeContinueButton: Button
    private lateinit var oldTestamentButton: Button
    private lateinit var newTestamentButton: Button
    private lateinit var previousChapterButton: ImageButton
    private lateinit var nextChapterButton: ImageButton
    private lateinit var plainButton: Button
    private lateinit var sideButton: Button
    private lateinit var followButton: Button
    private lateinit var plainEditionSelector: View
    private lateinit var editionIgboButton: TextView
    private lateinit var editionKjvButton: TextView
    private lateinit var chapterNavigationLabel: TextView
    private lateinit var indicators: Map<ReaderLayout, View>
    private lateinit var navDestinations: Map<Screen, View>
    private lateinit var bookAdapter: BookAdapter
    private lateinit var chapterAdapter: ChapterAdapter
    private lateinit var readerAdapter: ReaderAdapter
    private var repository: BibleRepository? = null
    private var screen = Screen.BOOKS
    private var books: List<BibleBook> = emptyList()
    private var selectedBook: BibleBook? = null
    private var selectedChapter: BibleChapter? = null
    private var selectedTestament = Testament.OLD
    private var readerLayout = ReaderLayout.PLAIN
    private var plainEdition = PlainEdition.MODERN_IGBO
    private var navigationGeneration = 0
    private var startupComplete = false
    internal var chapterPickerDialog: AlertDialog? = null
        private set

    private val preferences by lazy { getSharedPreferences("reader_preferences", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = android.graphics.Color.TRANSPARENT
        window.navigationBarColor = android.graphics.Color.TRANSPARENT
        WindowCompat.getInsetsController(window, window.decorView).apply {
            val isLightTheme =
                resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK != Configuration.UI_MODE_NIGHT_YES
            isAppearanceLightStatusBars = isLightTheme
            isAppearanceLightNavigationBars = isLightTheme
        }
        splashScreen.setKeepOnScreenCondition { !startupComplete }
        val restoredScreen = savedInstanceState?.getString(STATE_SCREEN)
            ?.let { runCatching { Screen.valueOf(it) }.getOrNull() } ?: Screen.BOOKS
        selectedTestament = savedInstanceState?.getString(STATE_TESTAMENT)
            ?.let { runCatching { Testament.valueOf(it) }.getOrNull() } ?: Testament.OLD
        val restoredBookId = savedInstanceState?.getString(STATE_BOOK_ID)
        val restoredChapterNumber = savedInstanceState?.getInt(STATE_CHAPTER_NUMBER)?.takeIf { it > 0 }
        setContentView(R.layout.activity_main)
        bindViews()
        applySystemBarInsets()
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (drawer.isDrawerOpen(GravityCompat.START)) drawer.closeDrawer(GravityCompat.START)
                else when (screen) {
                    Screen.BOOKS -> finish()
                    Screen.HOME, Screen.ABOUT -> showBooks()
                    Screen.CHAPTERS -> showBooks()
                    Screen.READER -> selectedBook?.let { selectBook(it) } ?: showBooks()
                }
            }
        })
        readerLayout = runCatching { ReaderLayout.valueOf(preferences.getString("layout", "PLAIN")!!) }.getOrDefault(ReaderLayout.PLAIN)
        plainEdition = runCatching { PlainEdition.valueOf(preferences.getString("plain_edition", "MODERN_IGBO")!!) }.getOrDefault(PlainEdition.MODERN_IGBO)
        configureAdapters()
        showLoading()

        worker.execute {
            try {
                DatabaseInstaller(this).install()
                val dataRepository = BibleRepository(File(filesDir, "databases"))
                val loadedBooks = dataRepository.getBooks()
                runOnUiThread {
                    repository = dataRepository
                    books = loadedBooks
                    bookAdapter.submit(books)
                    when {
                        restoredScreen == Screen.READER && restoredBookId != null && restoredChapterNumber != null ->
                            books.firstOrNull { it.id == restoredBookId }?.let { loadChapter(it, restoredChapterNumber) } ?: showBooks()
                        restoredScreen == Screen.CHAPTERS && restoredBookId != null ->
                            books.firstOrNull { it.id == restoredBookId }?.let { selectBook(it) } ?: showBooks()
                        restoredScreen == Screen.BOOKS -> showBooks()
                        restoredScreen == Screen.HOME -> showHome()
                        restoredScreen == Screen.ABOUT -> showAbout()
                        else -> showBooks()
                    }
                    updateContinueButton()
                    startupComplete = true
                }
            } catch (failure: Exception) {
                runOnUiThread {
                    hideScreens()
                    statusText.visibility = View.VISIBLE
                    statusText.text = getString(R.string.install_error_detail, getString(R.string.install_error), failure.message ?: failure.javaClass.simpleName)
                    startupComplete = true
                }
            }
        }
    }

    private fun bindViews() {
        drawer = findViewById(R.id.drawerLayout)
        navigationButton = findViewById(R.id.navigationButton)
        list = findViewById(R.id.list)
        screenTitle = findViewById(R.id.screenTitle)
        chapterEnglishTitle = findViewById(R.id.chapterEnglishTitle)
        statusText = findViewById(R.id.statusText)
        homeScreen = findViewById(R.id.homeScreen)
        booksControls = findViewById(R.id.booksControls)
        aboutScreen = findViewById(R.id.aboutScreen)
        readerControls = findViewById(R.id.readerControls)
        backButton = navigationButton
        homeContinueButton = findViewById(R.id.continueButton)
        oldTestamentButton = findViewById(R.id.oldTestamentButton)
        newTestamentButton = findViewById(R.id.newTestamentButton)
        previousChapterButton = findViewById(R.id.previousChapterButton)
        nextChapterButton = findViewById(R.id.nextChapterButton)
        plainButton = findViewById(R.id.plainButton)
        sideButton = findViewById(R.id.sideButton)
        followButton = findViewById(R.id.followButton)
        plainEditionSelector = findViewById(R.id.plainEditionSelector)
        editionIgboButton = findViewById(R.id.editionIgboButton)
        editionKjvButton = findViewById(R.id.editionKjvButton)
        chapterNavigationLabel = findViewById(R.id.chapterNavigationLabel)
        indicators = mapOf(
            ReaderLayout.PLAIN to findViewById(R.id.plainIndicator),
            ReaderLayout.SIDE_BY_SIDE to findViewById(R.id.sideIndicator),
            ReaderLayout.FOLLOW_UP to findViewById(R.id.followIndicator),
        )
        navDestinations = mapOf(
            Screen.HOME to findViewById(R.id.navHome),
            Screen.BOOKS to findViewById(R.id.navBooks),
            Screen.ABOUT to findViewById(R.id.navAbout),
        )

        navigationButton.setOnClickListener {
            if (screen == Screen.CHAPTERS || screen == Screen.READER) navigateBack()
            else drawer.openDrawer(GravityCompat.START)
        }
        findViewById<View>(R.id.navHome).setOnClickListener { drawer.closeDrawer(GravityCompat.START); showHome() }
        findViewById<View>(R.id.navBooks).setOnClickListener { drawer.closeDrawer(GravityCompat.START); showBooks() }
        findViewById<View>(R.id.navAbout).setOnClickListener { drawer.closeDrawer(GravityCompat.START); showAbout() }
        findViewById<View>(R.id.browseButton).setOnClickListener { showBooks() }
        homeContinueButton.setOnClickListener { continueReading() }
        oldTestamentButton.setOnClickListener { setTestament(Testament.OLD) }
        newTestamentButton.setOnClickListener { setTestament(Testament.NEW) }
        previousChapterButton.setOnClickListener { navigateChapter(-1) }
        nextChapterButton.setOnClickListener { navigateChapter(1) }
        plainButton.setOnClickListener { setLayout(ReaderLayout.PLAIN) }
        sideButton.setOnClickListener { setLayout(ReaderLayout.SIDE_BY_SIDE) }
        followButton.setOnClickListener { setLayout(ReaderLayout.FOLLOW_UP) }
        chapterNavigationLabel.setOnClickListener { openChapterPicker() }
        findViewById<TextView>(R.id.websiteText).apply {
            paintFlags = paintFlags or android.graphics.Paint.UNDERLINE_TEXT_FLAG
            setOnClickListener {
                startActivity(Intent(Intent.ACTION_VIEW, "https://ucscode.com".toUri()))
            }
        }
        editionIgboButton.setOnClickListener { setPlainEdition(PlainEdition.MODERN_IGBO) }
        editionKjvButton.setOnClickListener { setPlainEdition(PlainEdition.KJV) }
        val packageInfo = packageManager.getPackageInfo(packageName, 0)
        @Suppress("DEPRECATION")
        val versionCode = packageInfo.versionCode
        findViewById<TextView>(R.id.versionText).text = getString(R.string.version_format, packageInfo.versionName ?: "0", versionCode)
        installChapterSwipeNavigation()
        drawer.setDrawerLockMode(DrawerLayout.LOCK_MODE_UNLOCKED, GravityCompat.START)
    }

    private fun applySystemBarInsets() {
        val appBar = findViewById<View>(R.id.appBar)
        val mainContent = findViewById<View>(R.id.mainContent)
        val navigationDrawer = findViewById<View>(R.id.navigationDrawer)
        val appBarTop = appBar.paddingTop
        val contentLeft = mainContent.paddingLeft
        val contentRight = mainContent.paddingRight
        val contentBottom = mainContent.paddingBottom
        val drawerTop = navigationDrawer.paddingTop
        val drawerLeft = navigationDrawer.paddingLeft
        val drawerRight = navigationDrawer.paddingRight
        val drawerBottom = navigationDrawer.paddingBottom

        ViewCompat.setOnApplyWindowInsetsListener(drawer) { _, insets ->
            val safeArea = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout(),
            )
            appBar.setPadding(
                appBar.paddingLeft,
                appBarTop + safeArea.top,
                appBar.paddingRight,
                appBar.paddingBottom,
            )
            mainContent.setPadding(
                contentLeft + safeArea.left,
                mainContent.paddingTop,
                contentRight + safeArea.right,
                contentBottom + safeArea.bottom,
            )
            navigationDrawer.setPadding(
                drawerLeft + safeArea.left,
                drawerTop + safeArea.top,
                drawerRight + safeArea.right,
                drawerBottom + safeArea.bottom,
            )
            insets
        }
        ViewCompat.requestApplyInsets(drawer)
    }

    private fun configureAdapters() {
        list.layoutManager = LinearLayoutManager(this)
        bookAdapter = BookAdapter { book -> selectBook(book) }
        chapterAdapter = ChapterAdapter { chapter -> selectChapter(chapter) }
        readerAdapter = ReaderAdapter()
        list.adapter = bookAdapter
    }

    private fun showLoading() {
        hideScreens()
        screenTitle.text = getString(R.string.app_name)
        statusText.visibility = View.VISIBLE
        statusText.text = getString(R.string.loading)
    }

    private fun hideScreens() {
        homeScreen.visibility = View.GONE
        booksControls.visibility = View.GONE
        aboutScreen.visibility = View.GONE
        readerControls.visibility = View.GONE
        list.visibility = View.GONE
        statusText.visibility = View.GONE
    }

    private fun showHome() {
        screen = Screen.HOME
        selectedBook = null
        selectedChapter = null
        hideScreens()
        screenTitle.text = getString(R.string.app_name)
        chapterEnglishTitle.visibility = View.GONE
        updateDrawerSelection(Screen.HOME)
        navigationButton.setImageResource(R.drawable.ic_menu)
        navigationButton.contentDescription = getString(R.string.open_navigation)
        homeScreen.visibility = View.VISIBLE
        updateContinueButton()
    }

    private fun showBooks() {
        screen = Screen.BOOKS
        selectedBook = null
        selectedChapter = null
        hideScreens()
        screenTitle.text = getString(R.string.books_title)
        chapterEnglishTitle.visibility = View.GONE
        updateDrawerSelection(Screen.BOOKS)
        navigationButton.setImageResource(R.drawable.ic_menu)
        navigationButton.contentDescription = getString(R.string.open_navigation)
        booksControls.visibility = View.VISIBLE
        list.visibility = View.VISIBLE
        setChapterGridSidePadding(0)
        list.layoutManager = LinearLayoutManager(this)
        list.adapter = bookAdapter
        updateTestamentButtons()
    }

    private fun showAbout() {
        screen = Screen.ABOUT
        hideScreens()
        screenTitle.text = getString(R.string.about)
        chapterEnglishTitle.visibility = View.GONE
        updateDrawerSelection(Screen.ABOUT)
        navigationButton.setImageResource(R.drawable.ic_menu)
        navigationButton.contentDescription = getString(R.string.open_navigation)
        aboutScreen.visibility = View.VISIBLE
    }

    private fun setTestament(testament: Testament) {
        selectedTestament = testament
        bookAdapter.setTestament(testament)
        list.scrollToPosition(0)
        updateTestamentButtons()
    }

    private fun updateTestamentButtons() {
        listOf(oldTestamentButton to (selectedTestament == Testament.OLD), newTestamentButton to (selectedTestament == Testament.NEW))
            .forEach { (button, selected) ->
                button.isSelected = selected
                button.setTextColor(getColor(if (selected) R.color.reader_control_selected else R.color.reader_control_unselected))
                button.setTypeface(null, if (selected) android.graphics.Typeface.BOLD else android.graphics.Typeface.NORMAL)
            }
    }

    private fun updateDrawerSelection(destination: Screen) {
        navDestinations.forEach { (screen, item) ->
            val selected = screen == destination
            item.isSelected = selected
            val color = ContextCompat.getColor(this, if (selected) R.color.drawer_selected_text else R.color.drawer_normal_text)
            (item as ViewGroup).let { group ->
                group.getChildAt(0).let { icon ->
                    if (icon is ImageView) icon.imageTintList = android.content.res.ColorStateList.valueOf(color)
                }
                group.getChildAt(1).let { label -> if (label is TextView) label.setTextColor(color) }
            }
        }
    }

    private fun selectBook(book: BibleBook) {
        val retainedChapter = selectedBook?.takeIf { it.id == book.id }?.let { selectedChapter?.number }
        selectedBook = book
        selectedChapter = retainedChapter?.let { BibleChapter("${book.id}-$it", it) }
        screen = Screen.CHAPTERS
        navigationButton.setImageResource(R.drawable.ic_arrow_back)
        navigationButton.contentDescription = getString(R.string.go_back)
        hideScreens()
        screenTitle.text = displayIgboBookName(book.name)
        chapterEnglishTitle.text = book.englishName
        chapterEnglishTitle.visibility = View.VISIBLE
        updateDrawerSelection(Screen.BOOKS)
        statusText.visibility = View.VISIBLE
        statusText.text = getString(R.string.loading)
        val request = ++navigationGeneration
        worker.execute {
            val chapters = runCatching { repository?.getChapters(book.id).orEmpty() }
            runOnUiThread {
                if (request != navigationGeneration || screen != Screen.CHAPTERS) return@runOnUiThread
                chapters.onSuccess {
                    chapterAdapter.submit(it, selectedChapter?.number)
                    setChapterGridSidePadding(dp(CHAPTER_GRID_SIDE_PADDING_DP))
                    val availableWidth = (list.width - list.paddingLeft - list.paddingRight)
                        .takeIf { it > 0 }
                        ?: (resources.displayMetrics.widthPixels - dp(CHAPTER_GRID_SIDE_PADDING_DP * 2))
                    list.layoutManager = GridLayoutManager(this, chapterGridColumns(availableWidth))
                    list.adapter = chapterAdapter
                    list.visibility = View.VISIBLE
                    statusText.visibility = View.GONE
                }.onFailure { showError(it.message ?: getString(R.string.install_error)) }
            }
        }
    }

    private fun selectChapter(chapter: BibleChapter) {
        selectedBook?.let { loadChapter(it, chapter.number) }
    }

    private fun loadChapter(book: BibleBook, chapterNumber: Int, transition: ChapterTransition? = null) {
        val repository = repository ?: return
        val request = ++navigationGeneration
        selectedBook = book
        selectedChapter = BibleChapter("${book.id}-$chapterNumber", chapterNumber)
        screen = Screen.READER
        if (transition == null) hideScreens()
        navigationButton.setImageResource(R.drawable.ic_arrow_back)
        navigationButton.contentDescription = getString(R.string.go_back)
        screenTitle.text = getString(R.string.reader_title, displayIgboBookName(book.name), chapterNumber)
        chapterEnglishTitle.visibility = View.GONE
        updateDrawerSelection(Screen.BOOKS)
        if (transition == null) {
            statusText.visibility = View.VISIBLE
            statusText.text = getString(R.string.loading)
        }
        preferences.edit {
            putString(PREF_LAST_BOOK, book.id)
            putInt(PREF_LAST_CHAPTER, chapterNumber)
        }
        updateContinueButton()
        worker.execute {
            val verses = runCatching { repository.getParallelChapter(book.id, chapterNumber) }
            val previous = runCatching { repository.getAdjacentChapter(book.id, chapterNumber, -1) }
            val next = runCatching { repository.getAdjacentChapter(book.id, chapterNumber, 1) }
            runOnUiThread {
                if (request != navigationGeneration || screen != Screen.READER) return@runOnUiThread
                verses.onSuccess { items ->
                    list.animate().cancel()
                    readerAdapter.submit(items)
                    readerAdapter.setPresentation(readerLayout, plainEdition)
                    setChapterGridSidePadding(0)
                    list.layoutManager = LinearLayoutManager(this)
                    list.adapter = readerAdapter
                    list.visibility = View.VISIBLE
                    list.itemAnimator = null
                    list.scrollToPosition(0)
                    if (transition != null) {
                        list.translationX = list.width * transition.incomingSign
                        list.animate().translationX(0f).setDuration(CHAPTER_TRANSITION_MS).start()
                    } else list.translationX = 0f
                    statusText.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
                    if (items.isEmpty()) statusText.text = getString(R.string.empty_chapter)
                    readerControls.visibility = View.VISIBLE
                    previousChapterButton.isEnabled = previous.getOrNull() != null
                    nextChapterButton.isEnabled = next.getOrNull() != null
                    previousChapterButton.alpha = if (previousChapterButton.isEnabled) 1f else 0.38f
                    nextChapterButton.alpha = if (nextChapterButton.isEnabled) 1f else 0.38f
                    chapterNavigationLabel.text = getString(R.string.chapter_content_description, chapterNumber)
                    updateReaderControls()
                }.onFailure { showError(it.message ?: getString(R.string.install_error)) }
            }
        }
    }

    private fun navigateChapter(direction: Int) {
        val book = selectedBook ?: return
        val chapter = selectedChapter ?: return
        val dataRepository = repository ?: return
        val request = ++navigationGeneration
        previousChapterButton.isEnabled = false
        nextChapterButton.isEnabled = false
        worker.execute {
            val adjacent = runCatching { dataRepository.getAdjacentChapter(book.id, chapter.number, direction) }
            runOnUiThread {
                if (request != navigationGeneration || screen != Screen.READER) return@runOnUiThread
                val location = adjacent.getOrNull()
                if (location != null) {
                    val targetBook = books.firstOrNull { it.id == location.bookId }
                    if (targetBook != null) {
                        val transition = ChapterTransition.fromDirection(direction)
                        list.animate().cancel()
                        val distance = if (list.width > 0) list.width.toFloat() else resources.displayMetrics.widthPixels.toFloat()
                        list.animate().translationX(distance * transition.outgoingSign)
                            .setDuration(CHAPTER_TRANSITION_MS)
                            .withEndAction { if (request == navigationGeneration && screen == Screen.READER) loadChapter(targetBook, location.chapter, transition) }
                            .start()
                    }
                } else {
                    previousChapterButton.isEnabled = direction > 0
                    nextChapterButton.isEnabled = direction < 0
                }
            }
        }
    }

    private fun continueReading() {
        val bookId = preferences.getString(PREF_LAST_BOOK, null) ?: return showBooks()
        val chapter = preferences.getInt(PREF_LAST_CHAPTER, 0)
        val book = books.firstOrNull { it.id == bookId }
        if (book != null && chapter > 0) loadChapter(book, chapter) else showBooks()
    }

    private fun updateContinueButton() {
        val bookId = preferences.getString(PREF_LAST_BOOK, null)
        val chapter = preferences.getInt(PREF_LAST_CHAPTER, 0)
        val book = books.firstOrNull { it.id == bookId }
        if (book != null && chapter > 0) {
            val name = displayIgboBookName(book.name)
            homeContinueButton.text = getString(R.string.continue_reading_format, name, chapter)
            homeContinueButton.isEnabled = true
        } else {
            homeContinueButton.text = getString(R.string.continue_reading)
            homeContinueButton.isEnabled = false
        }
        homeContinueButton.visibility = if (book != null && chapter > 0) View.VISIBLE else View.GONE
    }

    private fun setLayout(layout: ReaderLayout) {
        readerLayout = layout
        preferences.edit { putString("layout", layout.name) }
        updateReaderControls()
        readerAdapter.setPresentation(layout, plainEdition)
    }

    private fun setPlainEdition(edition: PlainEdition) {
        if (plainEdition == edition) return
        plainEdition = edition
        preferences.edit { putString("plain_edition", plainEdition.name) }
        updateReaderControls()
        readerAdapter.setPresentation(readerLayout, plainEdition)
    }

    private fun updateReaderControls() {
        listOf(
            plainButton to (readerLayout == ReaderLayout.PLAIN),
            sideButton to (readerLayout == ReaderLayout.SIDE_BY_SIDE),
            followButton to (readerLayout == ReaderLayout.FOLLOW_UP),
        ).forEach { (button, selected) ->
            button.isSelected = selected
            button.setTextColor(getColor(if (selected) R.color.reader_control_selected else R.color.reader_control_unselected))
            button.setTypeface(null, android.graphics.Typeface.NORMAL)
        }
        indicators.forEach { (layout, indicator) -> indicator.visibility = if (layout == readerLayout) View.VISIBLE else View.GONE }
        plainEditionSelector.visibility = if (readerLayout == ReaderLayout.PLAIN) View.VISIBLE else View.GONE
        listOf(
            editionIgboButton to (plainEdition == PlainEdition.MODERN_IGBO),
            editionKjvButton to (plainEdition == PlainEdition.KJV),
        ).forEach { (button, selected) ->
            button.isSelected = selected
            button.setTextColor(getColor(if (selected) R.color.reader_control_selected else R.color.reader_control_unselected))
        }
    }

    private fun navigateBack() {
        when (screen) {
            Screen.READER -> selectedBook?.let { selectBook(it) }
            Screen.CHAPTERS -> showBooks()
            Screen.BOOKS, Screen.HOME, Screen.ABOUT -> showBooks()
        }
    }

    private fun openChapterPicker() {
        val book = selectedBook ?: return
        val dataRepository = repository ?: return
        worker.execute {
            val chapters = runCatching { dataRepository.getChapters(book.id) }
            runOnUiThread {
                if (screen != Screen.READER || selectedBook?.id != book.id) return@runOnUiThread
                chapters.onSuccess { items ->
                    lateinit var dialog: AlertDialog
                    val picker = layoutInflater.inflate(R.layout.dialog_chapter_picker, null) as RecyclerView
                    val pickerPadding = resources.getDimensionPixelSize(R.dimen.chapter_picker_padding)
                    val dialogContentWidth = (
                        resources.displayMetrics.widthPixels -
                            dp(DIALOG_CONTENT_INSET_DP) -
                            pickerPadding * 2
                    ).coerceAtLeast(dp(CHAPTER_GRID_MIN_COLUMNS * CHAPTER_GRID_TARGET_CELL_DP))
                    val columns = chapterGridColumns(dialogContentWidth)
                    picker.apply {
                        layoutManager = GridLayoutManager(this@MainActivity, columns)
                        setPadding(pickerPadding, pickerPadding, pickerPadding, pickerPadding)
                        clipToPadding = false
                        adapter = ChapterAdapter { chapter ->
                            dialog.dismiss()
                            loadChapter(book, chapter.number)
                        }.also { it.submit(items, selectedChapter?.number) }
                    }
                    val rows = (items.size + columns - 1) / columns
                    val rowHeightPx = dialogContentWidth / columns
                    val maxDialogHeight = minOf(dp(640), (resources.displayMetrics.heightPixels * 0.82f).toInt())
                    val maxListHeight = (maxDialogHeight - dp(DIALOG_CHROME_HEIGHT_DP)).coerceAtLeast(dp(64))
                    val contentHeight = rows * rowHeightPx + pickerPadding * 2
                    val pickerHeight = minOf(maxListHeight, contentHeight)
                    picker.isVerticalScrollBarEnabled = contentHeight > maxListHeight
                    picker.layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, pickerHeight)
                    dialog = AlertDialog.Builder(this)
                        .setTitle(getString(R.string.choose_chapter, displayIgboBookName(book.name)))
                        .setView(picker)
                        .setNegativeButton(R.string.cancel, null)
                        .create()
                    chapterPickerDialog = dialog
                    dialog.setOnDismissListener { chapterPickerDialog = null }
                    dialog.setOnShowListener {
                        dialog.window?.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, pickerHeight + dp(DIALOG_CHROME_HEIGHT_DP))
                    }
                    dialog.show()
                }.onFailure { showError(it.message ?: getString(R.string.install_error)) }
            }
        }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private fun setChapterGridSidePadding(padding: Int) {
        list.setPadding(padding, list.paddingTop, padding, list.paddingBottom)
        list.clipToPadding = false
    }

    private fun chapterGridColumns(availableWidthPx: Int): Int =
        (availableWidthPx / dp(CHAPTER_GRID_TARGET_CELL_DP))
            .coerceIn(CHAPTER_GRID_MIN_COLUMNS, CHAPTER_GRID_MAX_COLUMNS)

    private fun showError(message: String) {
        hideScreens()
        statusText.visibility = View.VISIBLE
        statusText.text = message
    }

    private fun installChapterSwipeNavigation() {
        val threshold = 72 * resources.displayMetrics.density
        list.addOnItemTouchListener(object : RecyclerView.SimpleOnItemTouchListener() {
            private var downX = 0f
            private var downY = 0f
            private var claimed = false
            private var downTime = 0L

            override fun onInterceptTouchEvent(rv: RecyclerView, event: MotionEvent): Boolean {
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> { downX = event.x; downY = event.y; downTime = event.eventTime; claimed = false }
                    MotionEvent.ACTION_MOVE -> {
                        val dx = event.x - downX
                        val dy = event.y - downY
                        val quickGesture = event.eventTime - downTime < ViewConfiguration.getLongPressTimeout()
                        if (screen == Screen.READER && quickGesture && !hasActiveTextSelection() && abs(dx) >= threshold && abs(dx) > abs(dy) * 1.5f) {
                            claimed = true
                            rv.parent?.requestDisallowInterceptTouchEvent(true)
                            return true
                        }
                    }
                    MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                        val dx = event.x - downX
                        val dy = event.y - downY
                        val quickGesture = event.eventTime - downTime < ViewConfiguration.getLongPressTimeout()
                        if (screen == Screen.READER && quickGesture && !hasActiveTextSelection() && abs(dx) >= threshold && abs(dx) > abs(dy) * 1.5f) {
                            claimed = true
                            return true
                        }
                    }
                }
                return false
            }

            override fun onTouchEvent(rv: RecyclerView, event: MotionEvent) {
                if (event.actionMasked == MotionEvent.ACTION_UP && claimed) {
                    val dx = event.x - downX
                    navigateChapter(if (dx < 0) 1 else -1)
                    claimed = false
                    rv.parent?.requestDisallowInterceptTouchEvent(false)
                } else if (event.actionMasked == MotionEvent.ACTION_CANCEL) {
                    claimed = false
                    rv.parent?.requestDisallowInterceptTouchEvent(false)
                }
            }
        })
    }

    private fun hasActiveTextSelection(): Boolean {
        fun selected(view: View): Boolean {
            if (view is TextView && view.isTextSelectable) {
                val text = view.text
                val start = Selection.getSelectionStart(text)
                val end = Selection.getSelectionEnd(text)
                if (start >= 0 && end > start) return true
            }
            if (view is ViewGroup) for (index in 0 until view.childCount) if (selected(view.getChildAt(index))) return true
            return false
        }
        for (index in 0 until list.childCount) if (selected(list.getChildAt(index))) return true
        return false
    }

    override fun onDestroy() {
        if (!worker.isShutdown) worker.execute { repository?.close() }
        worker.shutdown()
        super.onDestroy()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString(STATE_SCREEN, screen.name)
        outState.putString(STATE_TESTAMENT, selectedTestament.name)
        selectedBook?.let { outState.putString(STATE_BOOK_ID, it.id) }
        selectedChapter?.let { outState.putInt(STATE_CHAPTER_NUMBER, it.number) }
        super.onSaveInstanceState(outState)
    }

    private companion object {
        const val STATE_SCREEN = "screen"
        const val STATE_TESTAMENT = "testament"
        const val STATE_BOOK_ID = "book_id"
        const val STATE_CHAPTER_NUMBER = "chapter_number"
        const val PREF_LAST_BOOK = "last_book"
        const val PREF_LAST_CHAPTER = "last_chapter"
        const val CHAPTER_GRID_MIN_COLUMNS = 4
        const val CHAPTER_GRID_MAX_COLUMNS = 12
        const val CHAPTER_GRID_TARGET_CELL_DP = 80
        const val CHAPTER_GRID_SIDE_PADDING_DP = 12
        const val DIALOG_CONTENT_INSET_DP = 32
        const val DIALOG_CHROME_HEIGHT_DP = 132
        const val CHAPTER_TRANSITION_MS = 180L
    }
}

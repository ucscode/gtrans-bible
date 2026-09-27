package com.ucscode.gtransbible.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.data.BibleBook
import com.ucscode.gtransbible.data.BibleChapter
import com.ucscode.gtransbible.data.ChapterVerse
import com.ucscode.gtransbible.data.PlainEdition
import com.ucscode.gtransbible.data.ReaderLayout
import com.ucscode.gtransbible.data.Testament
import com.ucscode.gtransbible.data.belongsTo
import com.ucscode.gtransbible.data.displayIgboBookName
import java.text.NumberFormat

class BookAdapter(
    private val onBookSelected: (BibleBook) -> Unit,
) : RecyclerView.Adapter<BookAdapter.Holder>() {
    private var books: List<BibleBook> = emptyList()
    private var visibleBooks: List<BibleBook> = emptyList()
    private var testament: Testament = Testament.OLD

    fun setTestament(value: Testament) {
        if (testament == value) return
        testament = value
        updateVisibleBooks()
    }

    fun submit(items: List<BibleBook>) {
        books = items
        updateVisibleBooks()
    }

    private fun updateVisibleBooks() {
        val updated = books.filter { it.belongsTo(testament) }
        val diff = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = visibleBooks.size
            override fun getNewListSize() = updated.size
            override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                visibleBooks[oldItemPosition].id == updated[newItemPosition].id
            override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                visibleBooks[oldItemPosition] == updated[newItemPosition]
        })
        visibleBooks = updated
        diff.dispatchUpdatesTo(this)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder = Holder(
        LayoutInflater.from(parent.context).inflate(R.layout.row_book, parent, false), onBookSelected,
    )

    override fun onBindViewHolder(holder: Holder, position: Int) = holder.bind(visibleBooks[position])
    override fun getItemCount() = visibleBooks.size

    class Holder(itemView: View, private val onSelected: (BibleBook) -> Unit) : RecyclerView.ViewHolder(itemView) {
        private val name = itemView.findViewById<TextView>(R.id.bookName)
        private val englishName = itemView.findViewById<TextView>(R.id.bookEnglishName)
        fun bind(book: BibleBook) {
            name.text = displayIgboBookName(book.name)
            englishName.text = book.englishName
            itemView.contentDescription = "${name.text}, ${book.englishName}"
            itemView.setOnClickListener { onSelected(book) }
        }
    }
}

class ChapterAdapter(
    private val onChapterSelected: (BibleChapter) -> Unit,
) : RecyclerView.Adapter<ChapterAdapter.Holder>() {
    private var chapters: List<BibleChapter> = emptyList()

    fun submit(items: List<BibleChapter>) {
        val diff = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = chapters.size
            override fun getNewListSize() = items.size
            override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                chapters[oldItemPosition].id == items[newItemPosition].id
            override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                chapters[oldItemPosition] == items[newItemPosition]
        })
        chapters = items
        diff.dispatchUpdatesTo(this)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder = Holder(
        LayoutInflater.from(parent.context).inflate(R.layout.row_chapter, parent, false), onChapterSelected,
    )

    override fun onBindViewHolder(holder: Holder, position: Int) = holder.bind(chapters[position])
    override fun getItemCount() = chapters.size

    class Holder(itemView: View, private val onSelected: (BibleChapter) -> Unit) : RecyclerView.ViewHolder(itemView) {
        private val number = itemView.findViewById<TextView>(R.id.chapterNumber)
        fun bind(chapter: BibleChapter) {
            number.text = NumberFormat.getIntegerInstance().format(chapter.number)
            number.contentDescription = itemView.context.getString(R.string.chapter_content_description, chapter.number)
            itemView.setOnClickListener { onSelected(chapter) }
        }
    }
}

class ReaderAdapter : RecyclerView.Adapter<ReaderAdapter.Holder>() {
    private var verses: List<ChapterVerse> = emptyList()
    private var layout = ReaderLayout.PLAIN
    private var plainEdition = PlainEdition.MODERN_IGBO

    fun submit(items: List<ChapterVerse>) {
        val diff = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = verses.size
            override fun getNewListSize() = items.size
            override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                verses[oldItemPosition].verseId == items[newItemPosition].verseId
            override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int) =
                verses[oldItemPosition] == items[newItemPosition]
        })
        verses = items
        diff.dispatchUpdatesTo(this)
    }

    fun setPresentation(newLayout: ReaderLayout, newPlainEdition: PlainEdition) {
        layout = newLayout
        plainEdition = newPlainEdition
        if (itemCount > 0) notifyItemRangeChanged(0, itemCount, PRESENTATION_PAYLOAD)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder = Holder(
        LayoutInflater.from(parent.context).inflate(R.layout.row_verse, parent, false),
    )

    override fun onBindViewHolder(holder: Holder, position: Int) = holder.bind(verses[position], layout, plainEdition)
    override fun getItemCount() = verses.size

    class Holder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val verseNumber = itemView.findViewById<TextView>(R.id.verseNumber)
        private val plainText = itemView.findViewById<TextView>(R.id.plainText)
        private val sideBySide = itemView.findViewById<View>(R.id.sideBySide)
        private val sideIgbo = itemView.findViewById<TextView>(R.id.sideIgbo)
        private val sideEnglish = itemView.findViewById<TextView>(R.id.sideEnglish)
        private val followUp = itemView.findViewById<View>(R.id.followUp)
        private val followIgbo = itemView.findViewById<TextView>(R.id.followIgbo)
        private val followEnglish = itemView.findViewById<TextView>(R.id.followEnglish)

        fun bind(verse: ChapterVerse, layout: ReaderLayout, plainEdition: PlainEdition) {
            verseNumber.text = NumberFormat.getIntegerInstance().format(verse.verseNumber)
            plainText.visibility = if (layout == ReaderLayout.PLAIN) View.VISIBLE else View.GONE
            sideBySide.visibility = if (layout == ReaderLayout.SIDE_BY_SIDE) View.VISIBLE else View.GONE
            followUp.visibility = if (layout == ReaderLayout.FOLLOW_UP) View.VISIBLE else View.GONE
            when (layout) {
                ReaderLayout.PLAIN -> plainText.text = if (plainEdition == PlainEdition.MODERN_IGBO) verse.igbo else verse.english
                ReaderLayout.SIDE_BY_SIDE -> {
                    sideIgbo.text = verse.igbo
                    sideEnglish.text = verse.english
                }
                ReaderLayout.FOLLOW_UP -> {
                    followIgbo.text = verse.igbo
                    followEnglish.text = verse.english
                }
            }
        }
    }

    private companion object {
        const val PRESENTATION_PAYLOAD = "presentation"
    }
}

# IGBOB source and orthography investigation

**Status:** research and local normalization evidence report, 2026-09-26. Generated corpus/database artifacts remain local under ignored `data/`; redistribution rights are unresolved.

**Historical snapshot notice:** The preceding 2026-09-25 findings record earlier milestones. They are superseded where they say no complete corpus/modern database exists or that marked-b remains unresolved. The complete local-only corpus, the approved marked-b correspondence, and current database/report counts are documented in [Full-corpus orthographic modernization milestone (2026-09-26)](#full-corpus-orthographic-modernization-milestone-2026-09-26). Redistribution rights remain unresolved.

## Findings in brief

The repository already builds OICB into its established canonical and edition SQLite layers and has a separate resumable Google translation workflow. The existing pipeline is usable as a model for another edition, subject to adapting source metadata and validation rather than changing the canonical database.

The IGBOB identified by Bible Society of Nigeria (BSN) on YouVersion is labeled “Bible Nso” / `IGBOB`, publisher BSN, and displays “Igbo Bible © Bible Society of Nigeria © 1906, 2006.” This establishes a rights notice, not permission to redistribute or adapt the full corpus. The public product page does not provide a structured corpus download or a license grant. The exact relationship between the YouVersion text and a particular print revision is not stated there.

The 1913 Union Igbo Bible is a historically important related edition. A scholarly article documents its presentation in 1913 and the resulting orthography/standardization debate. That history alone does not establish that a modern digital `IGBOB` text is byte-for-byte or textually the 1913 edition. The sources found describe the Bible Nso as retaining/having connections to the Union tradition, but the exact base text, revision lineage, and changes need confirmation from BSN or the edition's title/copyright pages.

Bible.com exposes the requested Judges 13 passage publicly. The displayed opening verse was used as the textual fingerprint; its wording is not reproduced here.

The page also displays forms such as `ab͕uru`, `Mb͕e`, `nē-`, and `gā-`. In the rendered `b͕` example, the mark is Unicode U+0355 COMBINING RIGHT ARROWHEAD BELOW. Unicode identifies the mark's character identity only; it does not explain its linguistic function in this edition. The displayed forms confirm that unusual marks and older-looking morphology occur in at least these passages, not how often they occur across the canon.

## Source, identity, rights, and format

| Question | Finding | Evidence and limit |
|---|---|---|
| Exact online edition | Bible Nso, abbreviation `IGBOB`, publisher Bible Society of Nigeria | [YouVersion IGBOB listing](https://www.bible.com/versions/77); it states copyright © BSN © 1906, 2006. It does not state which revision those years represent. |
| Historical title/date | The Union Igbo Bible was published/presented in 1913; early Bible history is associated with T. J. Dennis | [Igwe and Obiakor, “The historical emergence of ‘Union Igbo Bible’”](https://www.nigerianjournalsonline.com/index.php/published_Articles/article/view/2810). Secondary historical research; it does not establish the identity or license of the current digital IGBOB corpus. [WorldCat catalog record](https://search.worldcat.org/title/29150006) catalogs a 1913 Bible Nso̦ print edition from the British and Foreign Bible Society. |
| Copyright/license | The current IGBOB page asserts BSN copyright (1906, 2006). No public-domain, Creative Commons, or other redistribution license was found for this digital text. Treat redistribution/adaptation rights as unconfirmed. | [YouVersion listing](https://www.bible.com/versions/77). The appearance of a 1906 date does not by itself establish public-domain status for a revised 2006 text. Obtain written clarification/permission from BSN for the exact digital edition and intended use. |
| Readable text | Yes, chapter pages are publicly readable, including [Judges 13](https://www.bible.com/bible/77/JDG.13.IGBOB). | Public display is not a redistribution grant. This investigation did not scrape or export the site. |
| Structured machine-readable source | No authoritative, licensed USFM/USX/OSIS/JSON/XML/plain-text download for this IGBOB edition was located. | BSN's [YouVersion versions page](https://www.biblesociety-nigeria.org/youversion-bibles/) confirms `IGBOB` is its version listing. The YouVersion page offers reading/copy UI, not a corpus download/license. Third-party mirrors and PDFs surfaced in search but are not adequate rights or provenance authority. |
| Versification | IGBOB displays standard chapter and verse labels in the sample, and Judges 13:1 corresponds to the supplied reference. Full-canon verse-ID mapping has not been measured. | Requires a permitted structured source or explicit rights-cleared corpus access. Do not infer complete alignment from the sample. |

**Conclusion on A:** The exact publicly identified source is BSN's YouVersion Bible Nso (`IGBOB`), with a copyright notice naming BSN and 1906/2006. It is technically readable online, but a legal and technically suitable bulk source has not been established. The 1913 Union edition is a historically related candidate, not a proven substitute. No text has been imported.

## KJV candidate

The [eBible.org King James (Authorized) Version page](https://ebible.org/bible/details.php?id=eng-kjv2006) identifies its text as the 1769 standardized KJV, describes it as public domain, and offers USFM, USFX, and other downloads. It notes a UK printing/import patent caveat; confirm territorial implications for intended distribution. The published package is protocanon-only (66 books), making it structurally compatible in book coverage with this repository's 66-book structure, subject to measuring verse-level differences before alignment.

The eBible Judges 13:1 reference is [here](https://ebible.org/eng-kjv2006/JDG13.htm) (if the page path changes, use the KJV page's Browser Bible link). The provided Igbo example follows a sentence structure and clauses similar to KJV Judges 13:1. This is a single-verse observation only. KJV remains an independent edition and is not evidence for changing Igbo.

## Orthography evidence and limits

A scholarly account describes the 1913 Union Igbo Bible as a major standardization event followed by an extended orthography debate: [Igwe and Obiakor](https://www.nigerianjournalsonline.com/index.php/published_Articles/article/view/2810). A dissertation account discusses later revision goals that included more current orthography and restructuring some sentences; it is secondary evidence and should be checked against primary editorial records: [Nnamdi Azikiwe University dissertation](https://phd-dissertations.unizik.edu.ng/repos/81131862600_134678891916.pdf).

The sample passage visible on [YouVersion Judges 13](https://www.bible.com/bible/77/JDG.13.IGBOB) contains `b͕` (U+0062 LATIN SMALL LETTER B followed by U+0355 COMBINING RIGHT ARROWHEAD BELOW) in `ab͕uru` and `n'ab͕uru`, along with forms such as `nābà`, `nē-`, and `gā-`. The Unicode name for U+0355 is confirmed by the [Unicode names list](https://unicode.org/charts/nameslist/n_0300.html). This does **not** prove a mapping from `b͕` to modern `gb`, or a general rule for macrons. Unicode names are not linguistic descriptions, and one verse cannot establish a corpus-wide correspondence.

No actual IGBOB corpus was available for the requested code-point inventory. Therefore these are sample observations, not counts or a representative inventory:

- Precomposed/decomposed code-point frequencies: unknown.
- Full set/frequency of combining marks, macrons, underdots, apostrophes, dashes, and whitespace: unknown.
- Distinct word forms and representative contexts: unknown beyond displayed passages.
- Meaning/function of macrons in this edition: unresolved.
- Function and modern spelling correspondence of `b͕`: unresolved.
- Whether word separation/hyphenation changes are predictable: unresolved.
- Safe context-free historical spelling transformations: none established from available evidence.
- Lexical/contextual or ambiguous transformations: cannot be enumerated without corpus and linguistic review.
- Estimated automatic modernization coverage: not responsibly estimable.

NFC canonical Unicode normalization can make canonically equivalent encodings deterministic, but the implementation should preserve the exact source string separately and verify the corpus's normalization behavior before transforming published text. Do not remove combining marks or macrons. No normalization rule has been implemented.

## Repository audit and reuse

- `builder/cli.py` exposes `download`, `extract`, `parse`, `validate`, `build`, `all`, `translate`, `translate-status`, and `validate-translation`.
- `builder/pipeline.py` downloads the configured Biblica OICB USFM archive atomically and safely extracts its expected source directory.
- `builder/usfm.py` parses OICB USFM, rejects unsupported verse marker forms, validates its 66-book canon and source verse reconciliation, and retains readable text while excluding notes and markup.
- `builder/database.py` creates `bible.sqlite` and `oicb.sqlite` atomically from one parsed `BibleData` result. Edition IDs are cross-checked against canonical IDs with SQLite `ATTACH`.
- `builder/translation.py` implements optional Google NMT build-time translation, hashes source content, resumes in batches, applies input budgets, and exposes injectable translator protocol/fakes in tests. It should remain independent from any future IGBOB normalization pipeline.
- Existing tables match the stated storage contract: canonical `books`, `chapters`, `verses`; OICB edition `metadata`, `books`, `verses`. OICB names/content are not present in the canonical DB.
- Extracted OICB is available locally under ignored `data/extracted/oicb/`; generated DBs are under ignored `data/generated/`. No IGBOB artifacts are present.
- Existing OICB parse/validation reported 66 books, 1,189 chapters, and 31,103 verses; source markers also total 31,103. Existing test suite: 12 tests passed.
- The working directory does not contain a `.git` repository, so there is no Git status/history available here. No commit or push was made.

## Design decision and next step

Do not add an IGBOB downloader, corpus database, word-level rule set, or modernization command until BSN (or another rights holder) confirms the exact edition, permitted acquisition method, and redistribution/adaptation rights. A public read page or a third-party mirror is insufficient for importing the full text.

Once permission and a source are secured, first acquire only into ignored `data/` paths and create a read-only audit report with source hash, per-book/chapter/verse counts, Unicode code-point/category/NFC statistics, unusual punctuation/whitespace inventory, frequency-ranked forms, and verse contexts. Then have an Igbo orthography specialist review proposed mappings against the actual edition. Preserve raw verse strings and make transformations individually attributable; ambiguous cases should remain flagged and unchanged. Compare versification with KJV independently by canonical IDs before building either edition database.

**Recommended immediate next step:** ask BSN to identify the precise IGBOB source revision and supply or authorize a machine-readable source under terms that permit local processing and the intended redistribution of both original and normalized text. In parallel, obtain a rights-cleared copy of the exact historical/Union text if it is a separate candidate. No implementation rule is safe enough to ship before that evidence exists.

## Historical source lineage and digitized copies (follow-up)

### Editions and portions documented before 1929

The historical record distinguishes several dialectal/translation projects; they should not be conflated as one “old Bible.” The following chronology is supported by the cited histories and surviving cataloged copies:

| Date | Edition/work | Extent/status | Evidence |
|---|---|---|---|
| 1860, 1866 | Isuama Igbo portions translated by J. C. Taylor (Matthew; later Acts and selected Pauline letters) | Portions only, not a whole Bible or complete New Testament | The scholarly dissertation/source synthesis [Bible Translation and Language Elaboration: The Igbo Experience](https://epub.uni-bayreuth.de/4298/1/Bible%20Translation%20and%20Language%20Elaboration%20%E2%80%93%20The%20Igbo%20Experience.pdf) distinguishes these from later Niger and Union versions. |
| 1892–1893 | Bonny/Lower-Igbo portions associated with Dandeson Crowther | Gospel of John and selected epistles/other portions; not a complete Bible | [Kilgour, *The Bible Throughout the World*](https://missiology.org.uk/pdf/e-books/kilgour-r/bible-throughout-the-world_kilgour.pdf) gives a historical summary; the dissertation above discusses the local dialect translation work. |
| 1898–1900 | Niger/Onitsha Igbo New Testament | A complete published New Testament (not a whole Bible) | The dissertation above dates the Niger Igbo New Testament to 1900; its bibliographic survey separates it from the Union NT and 1913 Union Bible. |
| 1905 | *Jenesis* (Genesis) | A surviving seven-image scan; not a whole Bible | [Internet Archive: rosettaproject_ibo_gen-2](https://archive.org/details/rosettaproject_ibo_gen-2), cataloged 1905, BFBS, London. |
| 1906 | Niger/Onitsha Bible claim; status disputed | Some secondary sources call a 1906 Igbo Bible complete, while other scholarship dates the first complete *published* Bible to 1913 and describes 1906 as the beginning of Dennis’s Union project. No cataloged complete 1906 edition or full scan was located. | The date may conflate translation work, the earlier Niger/Onitsha line, and the Union project. The evidence presently does not establish a distinct complete 1906 edition. The located [1906 Job–Malachi scan](https://archive.org/details/agbaociejobmala00unkngoog) is a section, not a complete Bible; Archive metadata’s “NOT_IN_COPYRIGHT” label applies to the U.S. only. |
| 1908 (some sources report 1910 for the Union NT’s release) | *Testament ohu nke Jisus Kraist* (Union Igbo New Testament) | Complete New Testament, not whole Bible | [Google Books item](https://books.google.com/books?id=AdMpAAAAYAAJ) gives Jan. 1908 and BFBS. Academic accounts describe Union NT work/printing as 1908 or 1910; the publication date varies by account and should be checked against its title page. |
| 1913 | *Bible Nsọ* / Union Igbo Bible, credited to Dennis and collaborators, BFBS | Complete Old and New Testaments; a distinct “Union” translation edition | [WorldCat catalog record](https://search.worldcat.org/title/29150006) identifies a 1913 complete print Bible by Thomas John Dennis and BFBS, London, and calls it the Union version. [Igwe and Obiakor](https://www.nigerianjournalsonline.com/index.php/published_Articles/article/view/2810) describe the 1913 publication and its language-standardization significance. |

The only complete pre-1929 edition firmly established by the reviewed catalog evidence is the 1913 Union Bible. A separate complete Onitsha/Niger Bible in 1906 is claimed by some secondary sources but remains unverified and is disputed by scholarship that identifies 1913 as the first complete published Igbo Bible; see the source-acquisition update below. The earlier Isuama and Bonny projects located here are portions; the 1900 and 1908/1910 works are New Testaments. Later reprints/revisions do not become public domain merely because the underlying translation is old.

### What scans and transcriptions are actually available

1. **1913 Union:** Internet Archive has an actual [1913 scan titled *N’Asusu Ibo*](https://archive.org/details/rosettaproject_ibo_gen-1), published by BFBS. Its IA metadata reports only **four page images** and the PDF/OCR contains a Genesis portion. It is not the complete 1913 Bible and contains no Judges 13. This is the only directly located scan demonstrably dated 1913; it cannot provide the requested textual fingerprint.
2. **1905/1906 Niger/Onitsha:** Archive has [1905 Genesis](https://archive.org/details/rosettaproject_ibo_gen-2) and a Google-digitized [1906 Job–Malachi volume](https://archive.org/details/agbaociejobmala00unkngoog). Neither contains Judges. I did not locate a complete scan of the reported 1906 whole Bible.
3. **1982 / 1988 Union-family material:** [Find.Bible’s “Igbo Union Version” record](https://find.bible/bibles/IBOILB/) lists a copyright date of 1988, BSN copyright, and historic scan links. The linked complete print scan in IA is cataloged as **1982 Genesis Portion** for one item, and separate John/New Testament scans are listed. This is not a cleanly identified 1913 scan or an open-licensed full transcription.
4. **Full 2006 print scan:** [Internet Archive `igbo-bible-print`](https://archive.org/details/igbo-bible-print) has a complete, 1,067-leaf print scan with OCR. Its Archive metadata says “Published: 2006” and sets a `Public Domain Mark 1.0` license URL; this is uploader/archive metadata, not a rights-holder grant. The YouVersion IGBOB edition carries BSN’s 1906/2006 copyright statement. Because the rights assertions conflict and the scanned item’s front matter is absent, **do not redistribute or treat this scan/OCR as a cleared public-domain text**. It is useful here only for visual comparison.
5. I found no machine-readable transcription of the complete 1913 Union Bible with independently verified public-domain provenance. The IA OCR attached to partial scans is machine output, not a verified edition transcription. Online copies hosted by mirrors and app vendors do not establish provenance or license.

**Scan inspection:** I inspected IA book leaves `n228` and `n229` (printed pages 33–34, Judges 13:1–25 and continuation) in the 2006 full print scan. [Open the scan at leaf 228](https://archive.org/stream/igbo-bible-print/igbo-bible-print#page/n228/mode/1up) and [leaf 229](https://archive.org/stream/igbo-bible-print/igbo-bible-print#page/n229/mode/1up). The printed line at 13:1 matches the supplied fingerprint in clause order and distinctive wording. OCR is noisy, so this comparison was made against the page image, not by treating OCR characters as authoritative. The verse text is not reproduced here.

Across Judges 13:1–10, this 2006 scan preserves the same clause order, vocabulary, and sentence construction as the YouVersion IGBOB text inspected earlier. The differences visible are spelling/diacritic rendering, word separation/hyphenation, punctuation, and typesetting; no substantive sentence or verse-structure change was observed in these ten verses. **For the 2006 print scan versus displayed IGBOB, classify the sample as B (same underlying translation with orthographic/typesetting variation), very close to A for wording.** This is strong fingerprint evidence for continuity of the modern IGBOB text with the Union tradition, but not proof that the current text is identical to the 1913 printing. The actual 1913 Judges pages remain unavailable for direct comparison.

### Rights and transcription/OCR assessment

- **1913 work:** The 1913 London BFBS printing is over a century old, and Thomas John Dennis died in 1917. Nigeria’s Copyright Act 2022 generally gives literary works a term of 70 years after the author’s death and uses the last surviving author for joint authorship ([official Nigerian Act](https://www.copyright.gov.ng/wp-content/uploads/2023/04/CopyrightAct2023FinalPublication1.pdf), section 19). UK guidance likewise generally uses life plus 70 years ([GOV.UK duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts)). However, historical accounts identify collaborators (including G. N. Anyaegbunam and other Igbo committee members), and the last-surviving joint author/death date and legal authorship of the collective translation have not been established. Thus the 1913 text is a **strong public-domain candidate**, not a source whose Nigeria/UK status has been conclusively cleared from the records found.
- **United States:** The U.S. Copyright Office states that works published in the United States before January 1, 1931 are public domain ([Copyright Office](https://www.copyright.gov/what-is-copyright/)). The 1913 Bible was published in London, so that simple U.S.-publication rule does not alone decide its status. The Google scan of the 1906 Job–Malachi volume is specifically labeled not-in-copyright for the U.S., but that does not establish Nigeria/UK rights or rights for the 1913 Union edition.
- **Making a transcription from a scan:** If the underlying 1913 text is confirmed public domain in the distribution territories, an independently prepared faithful OCR/manual transcription can generally reproduce that public-domain expression; a scan or OCR vendor label is not a substitute for checking the underlying rights, scan terms, and any separately protected modern edition/layout. Rights for publication must be assessed territory by territory. The accessible four-page 1913 scan is only Genesis, so it cannot produce a complete Bible transcription.
- **Actual printed marks:** On the inspected 2006 printed Judges pages, macron-like strokes are visibly printed over vowels in forms such as `gā-` / `nē-`. The word around current digital `n'ab͕uru` is printed with a visibly marked `b`, not as an unmarked `b` created only by web Unicode conversion. The scan therefore rules out the hypothesis that these marks were invented solely by a modern web transcriber for this 2006 printing. However, the scan is low resolution and dated 2006, not 1913: it does not prove the exact 1913 typeface/glyph or the mark’s linguistic interpretation.
- U+0355 specifically is Unicode’s **COMBINING RIGHT ARROWHEAD BELOW**, but that is the Unicode character name, not the name of the historical Igbo letter. The 1913 Genesis sample scan is too limited to check the `b` glyph in Judges contexts, and no primary orthography key for the print convention was located. A plausible phonetic relation is that a marked `b` represents a bilabial implosive historically written distinctly and often represented in standard Igbo orthography as `gb`; Peter Ladefoged’s phonetic work describes an Igbo bilabial implosive and its local orthographic spelling as `gb` ([Cambridge excerpt](https://assets.cambridge.org/97805211/16237/excerpt/9780521116237_excerpt.pdf)). That phonetic fact does **not** prove every marked `b` maps mechanically to `gb`, nor that modern word segmentation follows automatically. Treat the consonant mapping as a research hypothesis pending primary orthography documentation and a corpus review.

### Answer to the central question

**Not yet, on evidence sufficient for release.** The historical lineage is promising: the 1913 Union Bible is a complete work; the displayed IGBOB and the available 2006 print scan match closely in Judges 13:1–10; and some pre-1929 Bible portions/scans are genuinely available. But I did not locate a complete 1913 scan or transcription, could not compare Judges 13 in the 1913 original, and could not conclusively clear rights across Nigeria/UK because joint authorship details are incomplete. The complete 2006 scan is not a safe fallback because its archive public-domain label conflicts with BSN’s copyright notice.

**Best next step:** locate a library holding a complete 1913 copy (WorldCat identifies the edition) and get the title/copyright pages plus Judges 13 images for research; establish the authorship/death record and rights status with BFBS/BSN/archive staff; then, if the text is cleared, create a source-hashed OCR transcription and compare it against the current IGBOB only as a fingerprint. No copyrighted IGBOB has been imported, and no normalization or code/schema/CLI changes were made.

## Historical Orthography Analysis

**Scope and evidence.** This section analyzes orthography, not the legality or acquisition of the 2006 text. The complete [Internet Archive 2006 print scan](https://archive.org/details/igbo-bible-print) was used only as a research witness; Judges 13 is on printed pp. 33–34 ([scan page 33](https://archive.org/stream/igbo-bible-print/igbo-bible-print#page/n228/mode/1up), [scan page 34](https://archive.org/stream/igbo-bible-print/igbo-bible-print#page/n229/mode/1up)). The archive OCR is error-prone and is not included here or in the project. The original 1913 Union printing has not been inspected at these passages, so the 2006 print cannot prove that every glyph convention is unchanged from 1913.

The historical lineage matters: an academic account says Lepsius’s alphabet was adapted for Igbo and used by missionaries in Igboland until the 1930 orthographic change ([Witzlack-Makarevich, *Bible Translation and Language Elaboration: The Igbo Experience*, pp. 99–101](https://epub.uni-bayreuth.de/id/eprint/4298/1/Bible%20Translation%20and%20Language%20Elaboration%20%E2%80%93%20The%20Igbo%20Experience.pdf)). In the primary 1863 alphabet, Lepsius says vowel length is represented by a line over the vowel, while a breve can mark shortness (p. 59; [scan at the Library of Congress](https://www.loc.gov/item/11010936/), [Internet Archive scan/text](https://archive.org/details/standardalphabe00lepsgoog)). This establishes quantity as the general value of the overline, but not how this Bible’s editors applied it in every grammatical context; some recurring forms may encode contraction or editorial spelling as well. Kemp’s academic edition notes that missionary orthography also allowed digraphs `gb` and `kp` for African double articulations ([Kemp, ed., *Standard Alphabet*, 1981, p. 27 preview](https://api.pageplace.de/preview/DT0400.9789027280961_A24761183/preview-9789027280961_A24761183.pdf)). None of that establishes the value of this Bible’s visibly different under-mark on `b`; the exact 1913/2006 Bible orthography key has not been found.

### Symbol and construction findings

| Pattern | Digital form / printed evidence | Best-supported historical interpretation | Contemporary Standard Igbo representation | Safety |
|---|---|---|---|---|
| `b͕` | The displayed digital sequence is U+0062 LATIN SMALL LETTER B + U+0355 COMBINING RIGHT ARROWHEAD BELOW. The 2006 scan visibly prints a distinct mark below/at the foot of `b`; the Unicode character name describes the digital combining mark, not the historical letter’s linguistic name. | **Likely a marked consonant, possibly an implosive, but unknown for this exact Bible glyph.** Phonetic research reports an Igbo bilabial implosive realization and says the sound is written `gb` in local orthography ([Ladefoged, Cambridge excerpt](https://assets.cambridge.org/97805211/16237/excerpt/9780521116237_excerpt.pdf)). The 1961 Ọnwụ alphabet lists plain `b` and digraph `gb` separately; Kemp’s account of missionary orthography describes `gb`/`kp` as double-articulation digraphs. These facts make a relationship plausible; they do not prove a universal `b͕` → `gb` conversion, particularly across dialects and lexical items. The historical Lepsius vowel-length mark is an overline, whereas this scan’s `b` mark is visibly below the letter; the two should not be conflated without a Bible-specific key. | Plain `b` and `gb` remain distinct graphemes in the Ọnwụ inventory. The appropriate modern spelling must be checked word by word. In Judges 13:2, the printed/OCR form `ab͕uru` is plausibly related to the standard lexical form `agbụrụ` (“clan/tribe”); the contemporary dictionary entry records `agbụrụ` with meanings including race/ethnic group and gives `n’agbụrụ ndị Igbo` (“from the Igbo group”) as an example ([Nkọwa okwu, `agbụrụ`](https://nkowaokwu.com/word?word=agburu)). This supports the lexical candidate but not a global sound law. | **LEXICAL/DICTIONARY DEPENDENT** until the exact mark is keyed and the historical lexeme is verified. Never replace all marked `b` with `gb` blindly. |
| `ā`, `ē`, `ī`, `ō`, `ū` | In digital text, these are respectively U+0101, U+0113, U+012B, U+014D, U+016B; equivalent decomposed strings use the vowel followed by U+0304 COMBINING MACRON. The 2006 scan visibly has a horizontal mark over the vowel. | Lepsius’s general convention assigns a macron to vowel length/quantity. In the Bible, many macrons occur in recurrent verb constructions (`nēme`, `nāba`, `gēme`, `gābu`) where vowel coalescence and a hidden morpheme boundary are plausible. The Bible’s own orthography legend was not located, so it is not established that every macron is purely quantity, tone, or the same thing in every environment. Do not confuse these with modern linguistic publications that use macron to denote downstep: Igbo tone notation varies by author; Nwachukwu explicitly describes and rejects macron as a downstep symbol in his chosen convention ([“Tone in Igbo Syntax”](https://manfredi.mayfirst.org/Nwachukwu1995Tone.pdf)). | Ordinary Ọnwụ spelling does not retain these macrons. Contemporary grammatical writing can use tone diacritics for special purposes, but macron meaning must be interpreted under that author’s transcription key. When macron-bearing text is a fused auxiliary-plus-vowel-initial-verb form, modern spelling restores the morpheme boundary and the normal verb spelling instead of simply deleting the macron. | **UNKNOWN** as a blanket character-level change; **CONTEXTUALLY SAFE** only where syntax and a verified verb parse establish the components. |
| `nā-…`, `nē-…` | In print the macron is on the vowel in `nā…` / `nē…`; examples in the scan/OCR include `nāba`, `nēme`, `nābia`, `nēje`. | Often consistent with an auxiliary/prefix followed by a vowel-initial verb whose adjacent vowels have contracted or whose prefix vowel is represented harmonically. The repeated forms make a grammatical construction more likely than a lexical long vowel in many tokens; `nē` is not itself proof of modern `ne`. | The 1961 Ọnwụ teaching notes explicitly distinguish (1) preposition `na`, written `n’` before a vowel, from (2) auxiliary `na-`, written with a hyphen. They give contemporary examples such as `Ada na-esi ji` (“Ada is cooking yam”) and `Echere m na ọ ga-abịa echi` (“I think he will come tomorrow”). Harvard’s Igbo teaching materials also give `na-abịa`, `na-aga`, and `na-arụ ọrụ` for the progressive ([ELIAS, Unit 15](https://elias.fas.harvard.edu/languages/igbo/beginning/15/making-plans-future)). | **CONTEXTUALLY SAFE** only with syntactic parsing and the verb’s full vowel/dot spelling verified. Do not globally expand every `nā` / `nē` string. |
| `gā-…`, `gē-…` | Scan/OCR examples include `gābu`, `gābia`, `gēme`, `gēje`. | Often consistent with a future auxiliary plus a vowel-initial verb, with historical contraction and possibly vowel-harmony conventions obscuring the boundary. A macron is not itself the future morpheme; sentence grammar identifies that function. | Ọnwụ-era teaching explicitly writes future `ga-` with a hyphen before the verb, for example `ga-abịa`; Harvard teaching similarly says `ga` joins to a verb with a hyphen and gives `ga-abịa`, `ga-aga` ([ELIAS, Unit 15](https://elias.fas.harvard.edu/languages/igbo/beginning/15/making-plans-future)). Thus `gābu` is a plausible `ga-abụ` (“will be”) analysis, but verify the lexical verb and context before changing the word. | **CONTEXTUALLY SAFE** after a future construction and verb parse are confirmed; unsafe as `ā/ē` substitution alone. |
| `n'…` before a vowel, e.g. `n'ab͕uru` | The apostrophe is visible in the print. It does not turn `n` into a syllabic nasal. | In the official 1961 notes, the **preposition** `na` is written `n’` before a vowel, with examples `n’ụlọ`, `n’ala`, `n'ime`; the auxiliary is a separate `na-` construction. So the likely parse of `n'ab͕uru` is prepositional `n'` + a vowel-initial noun, not the syllabic nasal and not an auxiliary prefix. | Keep the prepositional apostrophe where standard spelling requires it. If lexical verification supports the marked-b mapping in this word, the likely form is `n’agbụrụ`. The apostrophe does not license dropping `n`, changing it to `m`, or joining arbitrary following material. | **CONTEXTUALLY SAFE** once the preposition and following lexical item are identified. |
| Syllabic `m` / `n` | Modern spelling can have a nasal as a syllable nucleus, e.g. `mpe`, `nkịta`, `mgba`; this is distinct from the preposition `n’` before a vowel. Scholarly phonetic transcriptions may add tone marks, but those marks must follow the source’s transcription key. | Igbo permits syllabic nasals, which can bear tone; the nasal may be homorganic with a following consonant. A bare OCR `m` or `n` does not reveal whether a nasal is syllabic, a consonant in a cluster, or part of an elided preposition. A linguistic study describes syllabic nasals as possible syllable nuclei and tone bearers and quotes Emenanjo on word-final `m` and homorganic nasals before consonants ([Unegbu, “A contrastive analysis of English and Igbo syllable structures,” AJILL 10, pp. 89–90](https://journals.unizik.edu.ng/index.php/ajill/article/download/160/142/306)). Obi’s SOAS dissertation treats vowel assimilation/contraction and tone as part of the standard dialect’s phonology ([Obi, 1979, repository record](https://soas-repository.worktribe.com/output/404114/the-phonetics-and-phonology-of-the-standard-dialect-of-igbo)). | Retain the standard letters `m` and `n`; use tone marks only when the project’s transcription convention calls for them. Do not convert a nasal to apostrophe spelling or remove it as punctuation. | **CONTEXT-SENSITIVE** where morphology or syllabification is uncertain; otherwise the nasal segment itself is not a normalization target. |
| `n`, `m`, apostrophe, hyphen, joined forms | OCR and print show multiple joins and punctuation patterns. The 2006 OCR is too noisy to count these reliably. | A short nasal-looking sequence can be a syllabic nasal, preposition elision, an auxiliary, a verb prefix, or lexical material; word division can encode syntax. | Ọnwụ’s notes say subject pronouns are written separately; a verbal vowel prefix harmonizes with the verb and is joined; auxiliaries use a hyphen; the preposition `na` contracts to `n’` before vowels; and suffixes join to verbs. They also warn that distinct `na` constructions can differ in tone/syntax even when their spelling is the same. | **CONTEXT-SENSITIVE**. Preserve boundaries except for rules supported by a grammatical parse. |

The primary modern reference used here is the [1961 *Official Igbo Orthography as Recommended by the Ọnwụ Committee: Notes on Script and Spelling for Teachers*](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf). It identifies the eight-vowel inventory and uses subdots for the relevant vowel contrasts; it lists `b` and `gb` separately; and it explicitly explains pronoun spacing, the joined verbal vowel prefix, `na-` as an auxiliary, `n’` as the preposition before a vowel, and hyphenation. This is more authoritative for the modern target than a verse-level analogy with OICB.

### Proposed normalization ruleset (proposal only)

**A. SAFE AUTOMATIC RULES**

- Unicode-normalize to NFC for consistent comparison while preserving the original source string and a reversible change log. NFC does not decide linguistic meaning.
- Convert only verified, purely typographic forms such as straight/curly apostrophe variants and redundant spaces; do not change apostrophe placement or hyphens in this step.
- Preserve modern vowel-quality distinctions already represented unambiguously by the source (`ọ`, `ị`, `ụ`) and avoid folding dotted and undotted vowels together.

**B. CONTEXT-SENSITIVE RULES**

- Parse a verified `gā/gē + vowel-initial verb` future pattern and render the modern auxiliary construction (`ga-` + verb), e.g. candidate `gābu` → `ga-abụ`. The change must be reversible and supported by syntax plus an identified verb lemma.
- Parse a verified `nā/nē + vowel-initial verb` progressive/auxiliary pattern and render `na-` + verb with current standard vowels, e.g. candidate `nābia` → `na-abịa`; do not infer the aspect from the letters alone.
- Preserve and modernize prepositional `n'` forms separately from auxiliary `na-`; use the modern standard apostrophe form only when the syntax identifies the preposition.
- Re-segment only constructions whose category is established (pronoun, auxiliary, verbal prefix, suffix, compound verb). The 1961 guide demonstrates that these word-boundary choices are grammatical, not cosmetic.

**C. LEXICAL REVIEW RULES**

- Review every `b͕` token against a historical alphabet key and a contemporary Igbo lexicon before mapping it to `b`, `gb`, or another form. The one apparent `ab͕uru` / `agbụrụ` match is a candidate, not permission for a global replacement.
- Review exceptional vowel sequences and macrons inside lexical roots, names, dialect forms, quotations, and compounds; do not strip all macrons as decoration.
- Confirm old spellings against the exact standard target dictionary when vowel quality or lexical identity depends on the source’s six-vowel spelling.

**D. UNRESOLVED PATTERNS**

- Exact historical value and scope of the under-mark represented digitally as U+0355 in `b͕`; whether it denotes an implosive or another consonant distinction, and whether it derives from any Lepsius sign or another printer/editor convention.
- Whether every macron in the 2006 edition marks vowel quantity/contraction, whether some are tonal or editorial, and which conventions were present in the 1913 print.
- Individual `gē-`, `nē-`, and macron-internal-root parses without a full syntax-aware grammar and token-level review.
- Dialect and lexical cases where contemporary `gb` has phonetic realizations that are not one-to-one with the historical marked consonant.
- Exact modern tone marking: everyday standard prose usually omits tone marks, while grammars/transcriptions may use acute, grave, macron, or other conventions with author-specific values. A normalizer cannot safely treat all macrons as tone marks or all of them as non-tonal.

### Corpus sample and determinism estimate

A one-off read-only in-memory count was run over the existing research XML for the complete Archive 2006 scan; no script, data, OCR, or normalized output was added to the repository. It contains **765,671 OCR word tokens**. **7,568 tokens (0.99%)** contain at least one precomposed vowel macron; the OCR reports 7,570 macron characters total. Of those marked tokens, **6,256 (82.7%)** begin with one of the recurring `nē-`, `nā-`, `gē-`, or `gā-` sequences. Those four candidate construction families therefore touch about **0.82% of all OCR word tokens**. The most frequent observed forms include `nēme`, `gēme`, and `gābu` (counts reflect OCR tokens, not verified linguistic attestations). The remaining macrons include examples such as `būru`, `jū`, and `ikwū`, where an automatic grammatical split is not established.

This yields a **provisional pattern-level estimate**: roughly **80–83% of macron-marked OCR tokens** appear to belong to recurring auxiliary/prefix families that could be handled deterministically *after a syntax and verb-lemma check*. That is not a claim that 83% of all modernization is deterministic: the marked-b sign was not recognized by OCR at all, the scan OCR contains substantial character substitutions and segmentation errors, and spelling, tone, and word-boundary changes affect uncounted tokens. The true corpus-wide deterministic share remains **unmeasured**; any higher percentage would be false precision from this OCR.

### Answer to the central question

**Not as a single blind character-replacement pass.** The evidence supports a hybrid route: use deterministic rules for clearly parsed grammatical constructions and reversible typographic cleanup; use lexical review for the marked consonant and uncertain vowels; retain unresolved cases. This could preserve wording if each transformation records its analysis and does not translate or paraphrase the text. The marked-b value, macron key, tone conventions, and 1913-to-2006 continuity still need primary confirmation before a production normalizer can claim reliable conversion.

## Complete historical source acquisition update (2026-09-25)

This update addresses source availability, the Judges 13 fingerprint, and the rights/holding trail. It does not extend the orthography analysis above.

### 1913 edition identity and actual scan status

The complete 1913 Union Bible is bibliographically established. [WorldCat OCLC 29150006](https://search.worldcat.org/title/29150006) records *Bible Nsọ nke nānagide Testament Ochie na Testament Ọhu*, an Igbo print Bible published by the British and Foreign Bible Society (BFBS), London, in 1913. Its notes identify the spine title *Bible Nso*, the title-verso wording “The Holy Bible in Ibo (Union version),” and say the revision was prepared by “T.J. Dennis et al.” The record describes 779 pages for the Old Testament and 245 for the separately titled New Testament. Witzlack-Makarevich/Oyali’s historical thesis says the first complete Igbo Bible was the 1913 Union Bible and distinguishes the earlier complete Niger Igbo New Testament from it.

I inspected the actual Internet Archive item that can be mistaken for the full 1913 source: [*N’Asusu Ibo*, IA `rosettaproject_ibo_gen-1`](https://archive.org/details/rosettaproject_ibo_gen-1), [PDF](https://archive.org/download/rosettaproject_ibo_gen-1/rosettaproject_ibo_gen-1.pdf). It is **three PDF pages**, not a whole Bible: a title leaf and a short Genesis extract (printed pages 5–7). It has no Judges. The title leaf names the Foreign Bible Society and 1913, but the item is just a Genesis sample. Its OCR is likewise only a fragment. I found no complete scan or complete machine-readable transcription of the 1913 edition in Internet Archive, Google Books, HathiTrust, the searched library/missions indexes, or Bible text repositories. Catalog records are not evidence that a digitized copy is online.

Other pre-1929 complete-edition evidence is limited, and the alleged 1906 complete edition is **not established**. Some secondary summaries say “complete Bible” or “whole Bible” in Igbo appeared in 1906. But the academic account [*Bible Translation and Language Elaboration: The Igbo Experience*](https://epub.uni-bayreuth.de/id/eprint/4298/1/Bible%20Translation%20and%20Language%20Elaboration%20%E2%80%93%20The%20Igbo%20Experience.pdf) describes the 1906 Onitsha material as the beginning of Union Igbo work and identifies 1913 as the first complete published translation; another academic historical account dates Union translation work to 1906–1912 and presentation/publication to 1913. The located records do not establish whether “1906 complete” refers to a distinct Niger/Onitsha edition, translation completion, or a date error. The surviving digital witnesses are 1905 Genesis and the Google-digitized [1906 *Agba ocie Job-Malakai n’asusu ibo*](https://archive.org/details/agbaociejobmala00unkngoog), Job–Malachi only. Neither has Judges, and neither proves a complete 1906 Bible was published. The 1906 claim should be treated as an unresolved lead, not as a rights-clear alternative. I found no complete pre-1913 Bible scan whose Judges text could be compared.

### A complete 1982 Union scan and the Judges fingerprint

A complete later Union-family scan **is** available in a confusingly cataloged Internet Archive item: [IA `IBOILB_DBS_HS`](https://archive.org/details/IBOILB_DBS_HS), direct [1,067-page PDF](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf), and [full-volume OCR XML](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29_djvu.xml). The item landing title says “Igbo (1982) Genesis Portion,” and that item also contains a distinct six-page Genesis-portion PDF. But it separately contains `Igbo-Bible-(print).pdf` and OCR for the whole print volume. I inspected the full PDF at its opening (Genesis), PDF pages 229–230 (Judges 13), PDF page 300 (Hosea), PDF page 800 (Habakkuk), and PDF pages 1063–1067 (Revelation/end matter). The Old Testament and New Testament page-number sequences, the Genesis-to-Revelation sequence, and the separate [St. Paul’s University Library catalog record](https://library.spu.ac.ke/cgi-bin/koha/opac-detail.pl?biblionumber=44649&shelfbrowse_itemnumber=101905) for a complete 1982 BSN Union Bible (820 + 255 pages) establish that the print PDF is a **complete Bible scan**, not just the Genesis portion named by the IA landing metadata. Because the full PDF’s title/imprint leaves are absent, its association with the 1982 edition is strongly supported by the parent item and matching cataloged edition/extent, but should be confirmed from a physical copy before citing its exact imprint as primary evidence.

Judges 13 is directly available in that scan: [PDF page 229](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229) and [PDF page 230](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=230), corresponding to printed pages 233–234. I compared the visible line at Judges 13:1 with the user-provided modern IGBOB fingerprint. The clause sequence and distinctive references are essentially the same, while dotted-vowel/diacritic presentation differs; no substantive wording change is apparent in this verse. This fingerprint is **B: same underlying translation with spelling/editorial revision**, with high confidence for the tested sentence. The scan visibly includes Judges 13:1–10 across the two pages, but the only direct comparison available in this task was the supplied Judges 13:1 sample; it does not prove every phrase in 13:1–10 is identical to a modern text we did not independently obtain here. The Union attribution and the close fingerprint make the 1982 edition a strong witness to the same translation lineage. They do **not** prove that 1913 itself had identical Judges wording.

The 1982 IA item provides machine OCR (`DjVuTXT`, XML, hOCR and search-text derivatives), but this is archive-generated OCR rather than a checked transcription. The 1913 sample has fragment OCR only. No vetted full 1913 transcription was located.

### Translators, contributors, publisher, and rights claims

The surviving catalog evidence calls the 1913 work a revision prepared by “T.J. Dennis et al.” The academic thesis [*Bible Translation and Language Elaboration: The Igbo Experience*](https://epub.uni-bayreuth.de/id/eprint/4298/1/Bible%20Translation%20and%20Language%20Elaboration%20%E2%80%93%20The%20Igbo%20Experience.pdf), especially its account of the Union translation (chapter 3, pp. 116–122), distinguishes roles and stages: Dennis supervised and revised the work; T. D. Anyaegbunam is identified as a translator; and the Union New Testament committee included Dennis, Anyaegbunam, Onyeabo/Onyeabor, Isaac Aneke, and Nzekwu, representing several language areas. Historical accounts describe the Old Testament translation as a team project completed in 1911 and published in 1913. These sources establish likely human contributors, but they do **not** give a definitive signed roster of legal authors for the whole Bible or show which committee members contributed copyrightable expression to each testament. Committee membership, consultation, editorial revision, funding, and authorship are not the same legal role.

Thomas John Dennis (1869–1917) is documented by the [Dictionary of African Christian Biography](https://dacb.org/stories/nigeria/dennis-thomasj2/). The academic account calls T. D. Anyaegbunam a principal collaborator and says the Union Igbo tradition ended with his death as well as Dennis’s, but the sources reviewed here do not establish Anyaegbunam’s exact death date from a reliable biographical record. Onyeabo/Onyeabor, Isaac Aneke, and Nzekwu appear as committee participants in the thesis, but no reliable death dates or final-work authorship determinations were found for them in the reviewed sources. The identity and death date of the latest surviving joint author is therefore unresolved.

BFBS is documented as **publisher and major funder**: the 1913 edition names it as publisher, and the historical account says it bore two-fifths of the translation project’s cost. I found no evidence in the records reviewed that BFBS expressly claimed institutional copyright in the 1913 text; neither funding nor publication alone proves copyright ownership. I also found no verified renewal or later copyright registration for the 1913 edition. The partial scan lacks the complete title verso/copyright matter, and the physical copy has not been examined, so “no claim found” must not be upgraded to “no claim existed.” A later BSN copyright notice attached to a modern digital edition does not prove that BSN owns copyright in the 1913 expression.

| Jurisdiction | Present assessment | Fact needed to resolve it |
|---|---|---|
| Nigeria | **Not yet conclusively cleared.** Section 19 of the [Copyright Act 2022](https://www.copyright.gov.ng/wp-content/uploads/2023/04/CopyrightAct2023FinalPublication1.pdf) gives a literary work 70 years after the author’s death and, for joint authorship, measures from the last surviving author. If the complete Union text is a human-authored joint work and the final coauthor died more than 70 years ago, the term would be over; institutional ownership or unknown/anonymous authorship can change the analysis. | Establish full legal author roster, last author’s death, and whether any relevant portion was legally authored/owned by an institution or is treated as anonymous. |
| United Kingdom | **Likely old, but not cleared from current evidence.** UK rules generally use life plus 70 years for known authors ([GOV.UK](https://www.gov.uk/copyright/how-long-copyright-lasts); [CDPA 1988, s.12](https://www.legislation.gov.uk/ukpga/1988/48/section/12)). The 1913 publication date does not by itself end copyright. For a work first published in 1913, the identity and death date of its last relevant author, any employment/assignment or collective-work status, and historical transitional-term rules matter. | The last surviving author’s verified death date and evidence of whether copyright was assigned/owned by BFBS or another entity; inspect the original title verso and relevant BFBS records. |
| United States | **Cannot be declared public domain solely because it was published in 1913 abroad.** The 1913 London publication is outside the simple U.S.-publication cutoff. Under the [U.S. Copyright Office URAA explanation](https://www.copyright.gov/gatt.html) and [17 U.S.C. §104A](https://www.copyright.gov/title17/92chap1.html), foreign works could have had copyright restored in 1996 if still protected in their source country then and other eligibility requirements were met. A search here did not establish a U.S. registration/renewal or determine source-country protection on that date. | Determine UK/Nigeria term at 1 January 1996, authors’ nationalities/eligibility and publication facts, and search Copyright Office/renewal records against exact title variants and publisher. |

An independent OCR/manual transcription **can be a viable route only after the underlying edition is cleared for the territories of distribution**. A faithful transcription does not make the old literary expression newly authored; however, the new scan’s access terms, any separate copyright in editorial additions, and the legal status of the source text must be checked. A public-domain determination for a 1913 copy would permit us to make our own transcription without relying on modern IGBOB. It would not authorize copying later BSN editorial revisions that are still protected. The 1982 scan/OCR is not itself an alternative rights clearance: it is a later BSN edition, has no explicit permissive license on the IA record, and its front matter/copyright page is missing.

### Physical holdings and digitization route

- **Best first inquiry: Bible Society’s Library at Cambridge University Library.** Cambridge states that the library began as the BFBS reference collection, is now over 39,000 volumes, and that the collection and archives moved there from BFBS’s London headquarters. It welcomes collection enquiries at **bslib@lib.cam.ac.uk** ([collection and contact](https://www.lib.cam.ac.uk/collections/departments/bible-societys-library)). That makes Cambridge the most plausible place to ask first for an actual BFBS 1913 copy, although I did not verify that this exact OCLC item is in its holdings. Ask specifically for OCLC 29150006 / the “Holy Bible in Ibo (Union version),” and request confirmation of the title/imprint/copyright pages, Judges 13, call number, and a full-volume digitization quote/terms.
- **Concrete second lead: Yale.** Yale’s [Missionary Bibles in Orbis guide](https://web.library.yale.edu/sites/default/files/files/Missionary_Bibles_in_Orbis_guide.pdf) lists the complete catalog heading “Bible. Igbo. Union” and the title *Bible nsio: nke nänagide Testament Ochie na Testament IOhụ*. The guide establishes a Yale cataloged record, though the copy’s current availability, shelf mark, and scan request options need confirmation from Yale Special Collections.
- **Another physical comparison lead:** St. Paul’s University Library, Kenya, catalogs a complete 1982 BSN Union edition as a reference item, call number **BMC REF BS325 .I33 1982**. This is useful for validating the scan’s missing imprint/copyright matter, but it is not evidence that St. Paul’s has the 1913 printing.
- **Digitization path:** once a holding is confirmed, request a small research scan first (title page, title verso/copyright page, Judges 13, and relevant prefatory/revision statements), then ask whether the full public-domain source can be scanned. Cambridge’s [Special Collections scanning service](https://www.lib.cam.ac.uk/search-and-find/zero-contact-services/scan-deliver/special-collections) describes limits and fees; its [Cambridge Heritage Imaging and Collection Care service](https://www.lib.cam.ac.uk/collections/departments/chil) can discuss larger/bespoke digitization. The library must determine what it can reproduce and the applicable rights/terms.

### Decision

**Potentially yes, but not yet demonstrated as a rights-cleared release route.** The central source problem is partly solved: a complete Union-family scan with Judges 13 exists, and the tested Judges 13:1 fingerprint is essentially identical to the current IGBOB wording. But that complete scanned witness is cataloged as 1982 and lacks its own title/copyright leaves, so it is not a public-domain substitute. The 1913 complete edition is confirmed in catalogs, but the only verified 1913 online scan is a three-page Genesis fragment. Therefore we cannot yet prove directly that 1913 and 2006/modern IGBOB are textually the same beyond the strong 1982 Union-family fingerprint, and we cannot yet declare the 1913 text public domain in Nigeria, the UK, and the U.S.

The strongest bypass route is to obtain a scan of the **1913 physical copy** (Cambridge BFBS library inquiry first; Yale’s cataloged Union Bible as another lead), inspect Judges 13 and rights/imprint matter, document the full human contributor roster and last-author death, then make an independently checked transcription from that cleared historical copy. The 1906 Niger Bible would be a second historical route only if a complete copy can be found and its distinct wording is acceptable; present evidence does not provide its whole text or Judges fingerprint. No code, database, CLI, normalization rule, or project Bible data was changed; no 2006 copyrighted text was downloaded/imported in this source-acquisition update.

### Decision table

| Edition | Year | Complete? | Actual text inspected? | Judges 13 available? | Same lineage? | Machine readable? | Rights status | Source URL |
|---|---:|---|---|---|---|---|---|---|
| Niger/Onitsha Bible (1906 claim) | 1906 | Disputed; no complete edition independently established | Only the 1905 Genesis and 1906 Job–Malachi witnesses located; neither supplies Judges | No in located scans | If distinct, separate from Union; identity not established | Partial archive OCR only | Not cleared by territory; no complete source located | [1906 Job–Malachi scan](https://archive.org/details/agbaociejobmala00unkngoog) |
| Union Igbo Bible, *Bible Nsọ* | 1913 | Yes as a published edition; no complete online scan found | Only three-page Genesis sample/title leaf inspected | No in located 1913 item | Foundational Union translation | No full text; fragment OCR only | Strong PD candidate, but Nigeria/UK/US status unresolved pending authorship, death, ownership, and U.S. restoration research | [WorldCat OCLC 29150006](https://search.worldcat.org/title/29150006); [1913 Genesis sample](https://archive.org/details/rosettaproject_ibo_gen-1) |
| Union Version, BSN | 1982 | Yes; complete 1,067-page scan inspected at beginning, Judges, mid-OT, and end | Yes; actual images and OCR inspected | Yes; scanned pp. 233–234 show Judges 13:1–10; tested 13:1 is B against the supplied current fingerprint | Yes, strongly supported by edition designation and textual fingerprint | Yes, IA OCR XML/TXT; machine output, not vetted | Not rights-cleared; 1982 BSN edition, no permissive license shown | [Complete scan PDF](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf); [IA item](https://archive.org/details/IBOILB_DBS_HS) |
| Union Igbo Bible listed as 1930 | 1930 | Cataloged as complete in the Minnesota Bible bibliography; no scan located | No | No located | Likely Union reprint/edition; not directly checked | No | Not shown rights-clear; later than 1913 and no copyright/imprint evidence reviewed | [Minnesota Ramseyer bibliography](https://mail.gospelgo.com/umn_ramseyer.htm) |
| Modern Igbo eBible, open-licensed | 2020 | Yes | Not text-compared to the Union lineage | Not assessed | No evidence of Union lineage; unrelated modern translation candidate | Yes, downloadable formats | CC BY-SA 4.0 as listed by eBible; redistribution/adaptation allowed under that license’s conditions | [eBible Igbo record](https://ebible.org/details.php?id=ibo) |

## Local corpus analysis (research-only, 2026-09-25)

### Tooling and source isolation

Added a separate analysis path: `builder/research.py` and `builder/research_cli.py`, callable as `python3 -m builder.research_cli` or the installed `igbo-research` command. It does not import the OICB USFM parser, production database builder, or translation pipeline. It writes CSV/JSON reports only and rejects output paths outside `data/research/`. `data/research/` is gitignored; the Python package includes only `builder*`, not that corpus/report tree. No Bible database was read or written by this analysis.

The source URL can be overridden with `--url` or `IGBO_RESEARCH_SOURCE_URL`; `--source PATH` copies an existing OCR file into the same ignored research area. The default URL is the Internet Archive DjVu XML for item `IBOILB_DBS_HS`. This run used the previously downloaded full-volume IA OCR XML, copied locally to `data/research/igbo-union/source/union-igbo-ocr.xml`; its SHA-256 is `63aec560d35c7b840d757e00d7ef740cbc7a27afb062502c525209c578a17969`. The scan/OCR remains a **research-only, non-redistribution source**. The generated full vocabulary and reports are local under `data/research/igbo-union/reports/`, not documentation or tests.

The tool reports reconstructed OCR text, not image/page typography: it joins each line’s OCR `WORD` nodes with spaces and adds a line feed. The token counter treats letters, numbers, and combining marks as token characters, retaining internal apostrophe/hyphen characters when surrounded by token characters. Percentages below state their denominator.

### Corpus and Unicode results

- The OCR has 1,067 page objects and 119,958 text lines. The reconstructed text contains **3,969,352 codepoints including line breaks**, **766,018 tokens**, and **44,747 distinct observed token spellings**.
- There are **6,810 precomposed macron-letter codepoints** in **6,809 token occurrences** and **1,760 distinct macron-bearing forms**. Thus **0.8889% of all OCR tokens** bear at least one macron. The extra mark occurrence means one token contains more than one macron.
- The OCR contains **zero combining-mark codepoints** and zero NFC-changing sequences. Source length is 3,969,352 codepoints; the corresponding NFD form would be 4,032,988 codepoints (63,636 more). The observed OCR spellings are encoded precomposed, not as base-letter-plus-combining-mark sequences. There were no distinct decomposed-versus-precomposed token variants in this OCR.
- The suspicious-sequence heuristic found **zero** unexpected mark sequences and no non-whitespace control/private/unassigned codepoints. This does not mean the OCR captured every printed diacritic: the marked-b scan check below demonstrates the opposite.
- Apostrophe inventory: U+0027 `'` **30,112**, U+2019 `’` **2,139**, and U+2018 `‘` **1**. Hyphen/dash inventory: U+002D `-` **91,850** and U+2014 em dash **1,702**. The tokenizer found **67,636 hyphenated token occurrences**. Many frequent hyphenated forms contain suffix-like sequences such as `-kwa-ra`; this is a boundary pattern to review, not a safe de-hyphenation rule.

### Macron groups and estimates

The analyzer groups token occurrences by the position and shape of the initial macron-bearing sequence. The largest direct families are `nē…` (**2,020**, 29.67% of macron-bearing token occurrences), `nā…` (**1,326**, 19.47%), `gē…` (**1,291**, 18.96%), and `gā…` (**965**, 14.17%). It also detects common leading forms such as `M’gē…` (219), `a+gē…` (175), `a+nē…` (161), `a+nā…` (140), and related forms. The report contains their top forms and short OCR contexts without copying bulk text into this document.

These direct and prefixed structural families together account for **6,514 / 6,809 = 95.6675% of macron-bearing token occurrences**. They account for **0.8501% of all OCR tokens**, which is prevalence, **not** a claim that this share can be automatically modernized. Previous linguistic research makes auxiliary/verb-prefix morphology plausible for these patterns, but forms still need syntax and lemma checks. The remaining **295 / 6,809 = 4.3325% of macron-bearing token occurrences** fall outside the candidate groups and require lexical/contextual review. Because OCR has omitted the marked-b glyph and can contain ordinary recognition errors, a corpus-wide “mechanically normalizable” or “unexplained” percentage is not supportable from these counts.

The hyphen analysis separately records all candidate-family forms containing a hyphen and whether a hyphen immediately follows the macron-bearing family. In this corpus, observed hyphens often occur later in forms like `gēme-kwa-ra`; they should not be mistaken for a boundary immediately after the auxiliary-like prefix. No automatic segmentation rule is proposed.

### Marked b and OCR image checks

The XML reports **zero marked-b tokens, zero marked-b Unicode sequences, and zero marked-b word types**. That zero is a property of this OCR text layer, not of the printed Bible. I inspected the actual scan image at [PDF page 229, printed page 233](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229): Judges 13:2 visibly prints the marked-b form in the short word `ab͕uru`, while the corresponding IA OCR line renders it as plain `aburu`. Thus the OCR has discarded or flattened the mark. Counting its output cannot answer how many printed marked-b tokens or distinct lexical items occur; it also cannot establish a global modern `b`/`gb` mapping.

I also inspected [PDF page 3, printed page 7](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=3). Macron strokes over vowels in forms such as `nē…` and `gē…` are present in the actual type and are represented in the OCR as precomposed macron letters. These samples show the macrons are not inventions of Unicode normalization, while also showing that OCR can miss other typographic distinctions. Broader marked-b counting requires page-image review or a better OCR/transcription that preserves the glyph.

OCR confidence is available for 766,961 OCR words. The analyzer aligned confidence values to 749,106 of its 766,018 tokens; among those aligned tokens, **14,326 (1.9124%)** have confidence below 70. Confidence is only an OCR signal. Visual checks show why low or absent OCR signals should trigger page review, not an orthography decision.

### Current research conclusion

The evidence supports beginning a **conservative, reviewable candidate ruleset**, but not implementing automatic text replacements. A useful first candidate set is the high-frequency macron-bearing prefix families above, with syntax/lemma evidence attached to each proposed analysis. The `b` mark remains unmeasured by OCR and is visibly lost in at least one printed occurrence, so it requires image-backed sampling and lexical identification before any replacement rule. Keep the 1982 source and generated reports research-only; do not use them as production edition data without separate rights clearance.

Automated tests use short synthetic fixtures only. `python3 -m unittest discover -v` passes all **18 tests**, including Unicode inventory, combining-mark sequence detection, token counts, NFC/NFD analysis, macron-family classification, hyphen-boundary statistics, deterministic reports, and research-output path isolation. No 1982 Bible passages were added to the test suite or copied in bulk into documentation.

## Linguistic investigation of historical forms (2026-09-25)

This section investigates the linguistic hypotheses behind the four macron families and the marked-b glyph. It does not propose or implement text normalization. The corpus sample is the existing Internet Archive Union Bible OCR and was checked against selected page images; it is evidence about this witness, not a newly derived corpus-wide statistic.

### Sources and interpretation

The [1961 Ọnwụ orthography document](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf), especially its vowel-harmony and pronoun discussion, describes harmonizing vowel material in the verbal complex and writes pronouns separately. Contemporary linguistic examples make the structure visible: Agbo cites `nà-é-rí nrí` (“the children are eating”) and `gà-à-rú` (“will build”), analyzing `na` as progressive/durative and `ga` as future; his discussion also cautions that `na` has other syntactic uses. See [Agbo, “A Cognitive Analysis of the Igbo Morpheme Na” (2015), pp. 193–195, 209–210](https://ihafa.unilag.edu.ng/article/download/613/498/). Agbo’s later aspect survey reports the common analysis of `na` as progressive/habitual/durative and `ga` as anticipative/progressive/continuous depending on construction: [“Aspectual Morphemes and Oppositions in Ìgbò” (2020)](https://jnlp.com.ng/index.php/home/article/download/9/8/16). The [Harvard ELIAS Igbo course](https://elias.fas.harvard.edu/languages/igbo/beginning/15/making-plans-future) gives modern learner forms `na-abịa`, `na-agba`, `ga-abịa`, and `ga-aga`, and explicitly distinguishes present continuous from future.

The best account of the visible historical forms is therefore not four unrelated morphemes. The grammatical markers are `na` (progressive/durative, also habitual/generic under suitable aspect and discourse conditions) and `ga` (future/anticipative/modal). In historical spellings, the macron family’s `ē/ā` reflects the harmonizing vowel material in the verbal complex and/or its coalescence with the following verbal prefix. The newer standard keeps `na-` and `ga-` as the marker spellings and writes the following harmonizing verb material after the hyphen (`na-e-ri`, `ga-a-ru` in fully segmented linguistic notation; common practical forms include `na-eri`, `ga-aru`). The historical vowel must not simply be copied as the modern marker vowel.

The macron itself is tonal notation in the linguistic transcriptions, not an instruction to lengthen the vowel: Agbo explicitly gives `ā` for downstep in his transcription conventions. Thus `ē` versus `ā` combines a different base vowel quality (`e` versus `a`) with tone notation. The everyday modern Ọnwụ examples write `na`/`ga` without tone marks and retain the harmonizing vowel in the verb complex; the distinction between `e` and `a` still matters.

| Historical form | Function supported by grammar and the sampled clauses | Modern Ọnwụ construction | Boundary and spelling effects | Sample result |
|---|---|---|---|---|
| `nē-` | `na` aspect/auxiliary plus harmonizing verbal material; most clauses are progressive, durative, or relative/habitual, not one single tense | `na-` + the verb’s harmonizing initial/agreement vowel + stem; e.g. analytical `na-e-ri` | Historical material is joined into the word; modern `na-` is hyphenated to the following verb complex. If the source has a contracted subject such as `M’`, modern prose normally writes the subject separately; expansion of the subject is lexical/contextual, not an apostrophe deletion rule. `ē` does not remain the marker vowel. | 30 checked; 30 fit the broad aspectual verbal construction; progressive vs habitual reading depends on clause/context. No broad-function counterexample in this sample. **STRONGLY SUPPORTED** |
| `nā-` | Same `na` aspect/auxiliary family as `nē-`; progressive/durative and habitual/generic readings vary by predicate and discourse | Same modern `na-` construction as above | Same joined-to-hyphenated change; historical `ā` is not retained in the modern marker spelling. | 30 checked; 29 fit the aspectual construction; one apparent `Nānunu` in Deuteronomy is the imperative “hear/listen,” a lookalike rather than an aspect auxiliary. Other ambiguity remains between progressive, habitual, and relative participial readings. **STRONGLY SUPPORTED** |
| `gē-` | `ga` future/anticipative auxiliary with harmonizing verbal material; future reference can shade into modal/intended readings | `ga-` + harmonizing verb material, e.g. `ga-e-me` in segmented notation; practical forms include `ga-eme` | Historical joining becomes a modern hyphen after `ga`; `ē` is not retained as the marker vowel. A preceding abbreviated subject/apostrophe must be resolved separately. | 30 checked; 30 fit a future/anticipative verbal construction. No counterexample in this sample; exact tense vs modal force is contextual. **STRONGLY SUPPORTED** |
| `gā-` | Same `ga` future/anticipative family as `gē-` | Same modern `ga-` + harmonizing verb material | Historical joining becomes modern hyphenation; `ā` is not retained as the marker vowel. | 30 checked; 30 fit a future/anticipative verbal construction. No counterexample in this sample; modal/intention readings cannot be inferred from spelling alone. **STRONGLY SUPPORTED** |

For each row, the audit took one occurrence per identifiable Bible-book heading where possible, spanning at least 25 headings across Torah, historical books, poetry, prophets, Gospels, Acts, and epistles. The examples include `nēchighari` (Genesis), `nēguzo` (Psalms), `nēme` (John/epistles), `nātukwasi` (prophets), `gēri/gēme` (Torah and historical books), and `gābu/gārapu` (Genesis, Gospels, and epistles). These are short diagnostic examples from the research OCR, not a proposed normalized text. The `nē/nā` test is consistency with the broad `na`-plus-verbal-complex analysis; a finer split between progressive, habitual, durative, relative, and other `na` functions needs full clause-level annotation. OCR forms such as `Nānunu` also show why prefix-shaped strings alone are not enough.

**Automaticity conclusion:** none of the four patterns is safe as a blind string replacement. `gē/gā` have the clearest grammatical identification, but normalization still must reconstruct the modern agreement/vowel-harmony form and preserve subject boundaries. `nē/nā` are more context-sensitive because `na` has several functions and aspect readings overlap. The macron spelling by itself does not supply enough information to split a verb, recover a dropped prefix, or choose the right modern verb vowel.

### Marked-b glyph: sound and modern spelling

The 1982 printed page at [PDF page 229 / printed page 233, Judges 13](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229) visibly has a `b` with a small mark beneath it in `n’aburu` (v. 2); the adjacent IA OCR reads plain `n’aburu`. The lexical/contextual reading is modern `agbụrụ` (“clan/lineage”), showing that this marked letter is not an ordinary /b/ in this word. The source glyph can safely be described from the print as an under-marked `b`; assigning it the Unicode combining sequence used in later data is not the basis of the phonological conclusion.

The most pertinent historical orthography statement is the 1930 [International Institute of African Languages and Cultures, *Practical Orthography of African Languages*](https://www.bisharat.net/Documents/poal30.htm), section on Ibo consonants: it says that “in many dialects of Ibo an implosive b is found,” while “for Union Ibo the spelling gb has been adopted.” This links the Union convention to the bilabial implosive category rather than to a labialized consonant or an ordinary `gb` digraph pronounced as a sequence. The acoustic/phonetic description by [Ladefoged, *A Phonetic Study of West African Languages* (1964), Cambridge excerpt](https://assets.cambridge.org/97805211/16237/excerpt/9780521116237_excerpt.pdf) identifies Igbo `ɓ` as a bilabial implosive and reports its local spelling as `gb`. The 1961 Ọnwụ inventory’s `gb` spelling is consistent with this standard orthographic outcome.

The best supported mapping for a Union printed marked-b is thus **historical marked `b` → Union/modern standard `gb`**. It is not a one-to-one phonetic mapping across all Igbo dialects: descriptions differ on whether standard `gb` is realized as an implosive, a velarized bilabial implosive, or a doubly articulated labial-velar stop. The spelling identifies a historical orthographic category, not a claim that every modern dialect has the same articulation. For examples, the scan gives `n’aburu` → `n’agbụrụ` (Judges 13:2; `agbụrụ`, “clan/lineage,” is also recorded in the [Nkọwa okwu dictionary entry](https://nkowaokwu.com/word?word=agburu)); modern linguistic descriptions give `egbe` “gun” and `àgbà` “jaw” with standard `gb` in [*A Grammar of Contemporary Igbo*](https://dokumen.pub/a-grammar-of-contemporary-igbo-constituents-features-and-processes-1nbsped-9789785421521-9789785412734.html). Those latter examples support the modern `gb` category, but the present page-image audit has not independently located their corresponding marked glyphs in this particular printed Bible. **Confidence: strongly supported as the Union orthographic correspondence; not proven as a universal phonetic one-to-one.**

The accessible evidence does not establish that Dennis personally used a specific technical name for the mark, and the 1930 orthography statement postdates the Bible. A copy of Dennis’s own grammar/key or a contemporary Union Bible prefatory orthography statement is still needed to attribute the terminology directly to him. The statement “Union Ibo spelling `gb` adopted” is direct evidence about the standardization decision, not proof of Dennis’s individual wording.

### Printed page versus IA OCR: six genre checks

I compared page images and the existing OCR text at representative pages in the requested genres: Genesis (Pentateuch), Judges (historical books), Psalms (poetry), Isaiah (prophets), Matthew (Gospel), and 1 Corinthians (epistle). Page links: [Genesis, PDF p. 3](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=3); [Judges, p. 229](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229); [Psalms, p. 480](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=480); [Isaiah, p. 610](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=610); [Matthew, p. 825](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=825); [1 Corinthians, p. 975](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=975). The scan pages are from the research-only 1982 Union witness, not a rights-cleared source edition.

Beyond marked-b, the clearest orthographic information loss in these checks is the **underdot on vowels** (`ọ`, `ị`, `ụ`). On the Judges page, print has `ọgu aro abua` in verse 1 but the OCR line gives `ogu aro abua`; vowel quality is therefore corrupted when the dot is missed. Under-dots are small and sit below the baseline, so image review is required even where the OCR otherwise looks fluent. The six-page sample also contains ordinary character confusions, dropped/shifted punctuation, and line-end hyphenation differences; those are OCR defects rather than evidence for a grammatical rewrite rule. Macron-bearing `ē/ā` strokes are visible in the printed sample and are often retained by this OCR, but the small sample cannot certify complete macron recall. This audit does not quantify any of these loss rates.

### Decision for normalization work

The linguistic interpretation is now **strongly supported** for the four families at the broad grammatical level: `nē/nā` belong to the `na` aspectual/verbal-complex family, and `gē/gā` belong to the `ga` future/anticipative family. Their modern spelling is not a direct diacritic strip: it requires modern `na-`/`ga-`, harmonizing verbal material, hyphen/boundary reconstruction, and contextual handling of subjects and other `na` functions. The marked-b glyph corresponds to Union `gb` orthography, but automatic recovery from OCR `b` is unsafe without a source image or lexical evidence. At the time of that linguistic investigation, no normalization rule had yet been implemented.

## Development import milestone (2026-09-25)

This milestone uses the already identified [Internet Archive IGBOB print item](https://archive.org/details/igbo-bible-print); it does not resume 1913-source acquisition. This is a development source only. The scan carries a Bible Society of Nigeria copyright notice, and neither the IA item's availability nor its OCR establishes redistribution permission. Do not publish the generated IGBOB data without a separate rights review.

### Source files and selection

The item exposes the original scanned PDF, DjVu text, DjVu XML, and hOCR derivatives. The working copies are retained under ignored `data/research/igbob-source/`. DjVu XML is the most useful parser input because it retains page/line/word boundaries and per-word confidence; DjVu text is retained as a separately readable transcription. Neither should be treated as orthographically authoritative. The PDF image is the deciding evidence for letter forms, underdots, and the marked-b glyph. The scan has 1,067 pages. SHA-256 values for the retained PDF and DjVu text are recorded in the generated IGBOB metadata.

I inspected the actual scan pages containing Judges 13: PDF p. 229 (printed p. 233; Judges 13:1–5) and PDF p. 230 (Judges 13:6 onward). The printed page confirms the chapter is present and that OCR loses small orthographic marks. Direct links: [PDF p. 229](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229) and [PDF p. 230](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=230).

### Import results and limitation

`builder/editions.py` adds an edition-only database builder/validator, an eBible KJV USFM importer, a scan-reviewed IGBOB-manifest importer, and a modern-edition builder using the existing normalization engine. It does not change `bible.sqlite`, `oicb.sqlite`, OICB parsing, or translation tooling.

The complete-scan OCR parser was evaluated but **not used to populate `igbob.sqlite`**. It found 956 page-reference headers across 1,067 scan pages, but its diagnostic pass produced only 14,479 usable verse records, 9,098 missing reference IDs, 1,828 duplicate IDs, and 76 pages whose references could not be anchored. Judges 13 demonstrates the practical failure: OCR omitted or misread verse markers and would shift text into the wrong canonical IDs. The diagnostic output is not an accepted transcription and is not stored in the edition database. Whole-edition import must wait for a corrected reference map or human-reviewed transcription.

The development `igbob.sqlite` contains only Judges 13:1–10, collated against those two PDF pages. Its canonical coverage is 10/31,103; the other 31,093 verses are explicitly missing. The corresponding `igbob-modern.sqlite` retains each imported original verse, normalized verse, ruleset and lexicon versions, and JSON transformation audit. Its coverage is likewise 10 verses. The full passage comparison is available locally at `data/generated/igbob-judges13-comparison.csv`, and the machine-readable counts are in `data/generated/igbob-quality-report.json`. These generated databases and reports are local ignored artifacts, not a license-cleared distribution.

| Quality measure | Result |
|---|---:|
| Canonical verse IDs | 31,103 |
| Scan-reviewed IGBOB verses imported | 10 |
| Missing IGBOB verse IDs | 31,093 |
| Duplicate / empty / orphan IGBOB rows | 0 / 0 / 0 |
| Modern verses changed | 1 |
| Transformations: general rules / lexical | 0 / 1 |
| Distinct resolved historical forms / occurrences | 1 / 1 (`n'aburu`) |
| Distinct unresolved review forms / occurrences in sample | 1 / 1 (`nē`) |
| Unknown forms flagged by normalizer in sample | 0 |
| Manually confirmed OCR-loss cases | 2 (marked-b; underdots) |
| Whole-scan diagnostic: unanchored pages / duplicate refs | 76 / 1,828 |

### KJV result

The structured USFM from [eBible KJV 2006](https://ebible.org/bible/details.php?id=eng-kjv2006) imports independently as `data/databases/kjv.sqlite`: 66 books, 1,189 chapters represented, and 31,103 verses, with no missing, duplicate, orphaned, or empty canonical references after validation. The eBible file joins traditional 3 John 1:14 and 1:15 in one USFM row; the importer splits that English row at the sentence boundary to satisfy the existing canonical verse IDs. This structural KJV adjustment is not used to edit IGBOB.

### Actual modernization approved

The reviewed lexicon now contains one exact mapping: OCR token `n'aburu` → `n'agbụrụ`, used in Judges 13:2. The printed glyph and context identify the marked-b form, and the modern `agbụrụ` spelling is supported by the [Nkọwa okwu entry](https://nkowaokwu.com/word?word=agburu). The rule is deliberately phrase/token-specific; it is not a global `b` → `gb` or `o` → `ọ` rule.

No general `nē-/nā-/gē-/gā-`, macron, whitespace, or apostrophe rule was approved. On the ten-verse sample, one verse changed by one lexical transformation; one separate morphology review finding remains unchanged. The other nine verses are unchanged. Unknown marked-b recovery cannot be measured from the OCR because the mark is absent there. The printed/OCR comparison confirms at least two information-loss classes in this passage: marked-b is rendered as ordinary `b`, and underdots can disappear (for example, printed `ọgu` versus OCR `ogu`).

### Judges 13:1–10 comparison status

All ten canonical IDs are present in the three local databases. The historical and modern text rows can be queried from `data/databases/igbob.sqlite` and `data/databases/igbob-modern.sqlite`; the English rows are in `data/databases/kjv.sqlite`. The approved change is visible at `jdg-13-2` (`n'aburu` → `n'agbụrụ`). Other historical forms remain as transcribed, including uncertain OCR spellings; the KJV remains a comparison edition and did not supply wording for the Igbo rows. Because the scan is not cleared for redistribution, this documentation identifies the passage and exact transformation without reproducing all ten verses.

### Build and verification status

The canonical database remains 66 books / 1,189 chapters / 31,103 verses and its schema is unchanged. The KJV database is complete. The IGBOB and modern IGBOB databases are valid partial development editions with 10 rows each. Six focused edition-import/normalization tests were added; the complete suite passes: **39 passed**. The most important remaining work is a page/reference alignment that survives OCR marker loss and a legal path permitting distribution. No code has used OICB or KJV content to rewrite IGBOB wording.

## Page-aware extraction investigation (2026-09-25)

This follow-up does not expand the accepted corpus. The 1982 BSN scan is still a research-only witness, and its OCR is not imported directly. The canonical `bible.sqlite`, KJV database, `igbob.sqlite`, and `igbob-modern.sqlite` were not changed. The new reader in [`builder/igbob_extraction.py`](../builder/igbob_extraction.py) retains DjVu page, XML layout block, line, word, bounding box, and word-confidence provenance. Reading follows XML line order across page layout blocks; a word is not detached from its source coordinates. Focused fixtures check that order and OCR signals remain distinct.

### Why full-scan alignment failed

The prior flat pass produced 14,479 candidate verse records, with 9,098 canonical IDs missing, 1,828 duplicate mappings, and 76 page anchors it could not assign. These were correctly rejected. The errors arise from identifiable features:

- **Book transitions:** the first Judges scan page spans Joshua 24 into Judges 1. Treating the running page range as if it belonged to one current book loses Judges 1:1–13; the old pass starts its Judges records at 1:14. Book-name/title lines are not a reliable sequence boundary when flattened with body text.
- **Page-range OCR:** range headings can be absent or digit-corrupted. The new page audit detects a range header on 898 of 1,067 pages; 169 have no detectable range anchor under its conservative first-lines rule. This differs from the earlier looser 956-header count because the new check reports only ranges found in the first eight ordered lines.
- **Verse-marker recognition:** text numbers are small standalone OCR words, and some digit-plus-word joins hide markers. The source audit found 32,647 standalone number-like words and 260 digit-attached word tokens. The old parser's Judges output contains only 372 candidate records across a 618-verse book and includes a duplicate; this is not a complete or trusted alignment.
- **Two-column layout:** the printed page uses two reading columns. For example, PDF p. 230 has Judges 13:6–25 in left and right columns. DjVu `PAGECOLUMN` blocks are segmentation zones rather than a dependable count of physical columns (this page has five blocks); preserving the XML line sequence is necessary to avoid treating those internal zones as five printed columns.
- **OCR confidence and character corruption:** the whole scan has 5,139 words below confidence 50 (0.671% of its 765,671 XML word nodes), while every page has at least one review signal when low-confidence and non-Latin lookalike checks are combined. There are 55,411 words containing non-Latin letters (often Cyrillic homoglyphs that visually resemble Latin), and 260 joined digit/word tokens. A high OCR confidence score does not validate the text or canonical reference.
- **Page continuation, headers, and line wrapping:** a verse continues across lines and sometimes across pages; running references/headings occur among OCR zones. Line breaks are not verse boundaries, and a page-range endpoint cannot by itself establish how many verse markers OCR omitted.

The audit artifact `data/generated/igbob-source-page-audit.json` records per-page counts and anomaly reasons without storing verse text. `data/generated/igbob-extraction-report.json` records canonical coverage, accepted confidence counts, and stage status. Both are ignored local outputs. A page/word-aware source reader is implemented, but a safe verse aligner and targeted verse-level review queue are **not yet implemented**; no OCR candidate has been promoted on the basis of the new reader alone.

### OCR experiment and stage results

At the time of the initial page-aware extraction milestone, no local OCR engine had been installed and no re-recognition result was claimed. That status is superseded by the modern OCR experiment documented below. PDF pp. 229–230 were visually inspected; the scan-reviewed Judges 13 manifest covers all 25 verses.

| Stage | Expected | Accepted scan-checked | Coverage | High / medium / low alignment | Missing | Status |
|---|---:|---:|---:|---:|---:|---|
| Judges 13 | 25 | 25 | 100.000% | 25 / 0 / 0 | 0 | Complete; all verses checked against PDF pp. 229–230 |
| Judges | 618 | 25 | 4.045% | 25 / 0 / 0 | 593 | Not reached; 372 old heuristic candidates rejected |
| Genesis | 1,533 | 0 | 0% | 0 / 0 / 0 | 1,533 | Not reached |
| Psalms | 2,461 | 0 | 0% | 0 / 0 / 0 | 2,461 | Not reached |
| Matthew | 1,071 | 0 | 0% | 0 / 0 / 0 | 1,071 | Not reached |
| Romans | 433 | 0 | 0% | 0 / 0 / 0 | 433 | Not reached |
| Whole Bible | 31,103 | 25 | 0.0804% | 25 / 0 / 0 | 31,078 | Not reached |

The 25 accepted Judges 13 rows have high **alignment** and **transcription** confidence because they were checked against the printed pages; this is separate from the low/unknown OCR confidence of their source tokens. The 14,479 unvalidated records from the old whole-scan heuristic have no accepted confidence classification and are excluded. The current missing-reference review queue is 31,078 canonical IDs. The per-page audit flags 1,067 pages for at least one OCR/page-anchor signal, so the current queue is not yet small or sufficiently verse-targeted.

### Manual check and remaining blocker

All 25 verses in Judges 13 are now scan-checked against PDF pp. 229–230. The rest of Judges was not accepted or manually counted. Genesis, Psalms, Matthew, Romans, Isaiah, and Revelation were not re-OCRed in this milestone. IA's XML contains enough layout and confidence information to support page-focused review, but its OCR also contains widespread non-Latin lookalikes, digit/word joins, and occasional missing/corrupt range headers. The next reliable increase in corpus coverage requires an explicit verse marker recognizer constrained by the known book/chapter sequence, with alignment confidence and a separate transcription review decision. Historical and modern database coverage is now 25 verses each.

No normalization rule, CLI, database schema, or Android code changed. Three focused tests cover page reading order/provenance, distinct OCR marker-quality signals, and deterministic audit output. The complete suite passes: **42 passed**.

## Modern image OCR experiment (2026-09-26)

This experiment evaluates image-to-historical-text recognition only. It does not extend the IA DjVu aligner or update canonical databases, edition coverage, normalization, CLI, or Android code. All images, gold text, OCR outputs, and diagnostics are under the ignored `data/research/igbob-source/ocr-eval/` directory. The historical scan's redistribution rights remain unresolved; these local research files must not be redistributed.

### Candidate selection and environment

The machine had no system OCR engine or OCR Python packages available at the start. Tesseract 5.3.4 was extracted from local Debian packages into `/tmp`; the official `Latin` script model and `eng` model were also kept under `/tmp`. I tested both with `--psm 6`, CPU inference, and column/text-region crops. `Latin` is a script model rather than an Igbo model; the official Tesseract model inventory lists Latin script data but no Igbo model. [Tesseract traineddata inventory](https://tesseract-ocr.github.io/tessdoc/Data-Files.html)

PaddleOCR 3.7.0 with PP-OCRv5 Latin was the second selected approach because its Latin recognizer advertises most Latin-alphabet languages and its pipeline returns recognized text with regions. The official model listing does not claim Igbo-specific training. On this machine the PP-OCRv5 CPU detector failed at inference with a Paddle oneDNN/PIR `NotImplementedError` after the weights downloaded, so it yielded no comparison score. The local runtime did not expose the mentioned RTX 4060 (`nvidia-smi` was unavailable), so no GPU run was possible. [PaddleOCR PP-OCRv5 model list](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/module_usage/text_recognition.en.md)

EasyOCR was considered but not installed: its official character/model configuration supports a broad Latin set, including some marked vowels, but lists no Igbo language model. Kraken is a plausible historical-print follow-up because it supports training segmentation and recognition for historical and low-resource sources; its documentation requires page/line examples similar to the target print, so it was not trained on this small set. OCRmyPDF was not treated as an additional recognizer because it orchestrates OCR engines rather than supplying an Igbo recognizer. [EasyOCR model configuration](https://github.com/JaidedAI/EasyOCR/blob/master/easyocr/config.py), [Kraken training documentation](https://kraken.re/6.0.0/tutorials/training.html)

The two Tesseract models were the only approaches that produced comparable OCR text. English is included as a control; it is not linguistically appropriate for Igbo and its results confirm that distinction.

### Gold set and scoring method

The ignored local gold set contains manually scan-read regions from seven books: Genesis 3:5; all 25 scan-reviewed verses of Judges 13; Psalm 18:6; Isaiah 12:2; Matthew 10:1; Romans 1:4; and Revelation 1:1. It deliberately includes two-column layouts, the Joshua-to-Judges book transition, verse and chapter numerals, apostrophes, hyphens, underdots, macrons, and the visible marked-b example. The scan pages were rendered from the existing PDF at about 180 dpi. The line crops preserve surrounding page matter where it helps reveal header or layout contamination.

CER and WER below are measured on the complete Judges 13 gold text against OCR text from the same printed columns. Scoring collapses whitespace and applies Unicode NFC only to treat canonically equivalent code-point encodings as the same; it does not apply Igbo normalization, alter spelling, or map characters. The separate Genesis score is a single verse region and is only a preprocessing comparison, not a Bible-wide estimate.

| OCR configuration | Judges 13 CER / character accuracy | Judges 13 WER / word accuracy | Under-dot recall | Macron recall | Genesis 3:5 CER / WER |
|---|---:|---:|---:|---:|---:|
| Tesseract `Latin` | 20.9% / 79.1% | 37.6% / 62.4% | 43/44 (97.7%) | 7/10 (70.0%) | 12.1% / 28.6% |
| Tesseract `eng` | 21.1% / 78.9% | 40.1% / 59.9% | 0/44 (0%) | 0/10 (0%) | 12.8% / 35.7% |
| PaddleOCR PP-OCRv5 Latin | Not run to output; CPU detector raised runtime error | — | — | — | — |

The Latin model's aggregate character score is only slightly better than English, but it preserves the Igbo diacritics far better. That distinction is material: choosing on generic CER alone would hide the English model's total loss of the 44 underdotted vowels and 10 macrons in this Judges 13 sample. Tesseract `Latin` still failed to reproduce a single full Judges 13 verse exactly after marker alignment (0/25 exact verses); its errors include substitutions, omissions, and damaged verse markers. In the one visually confirmed marked-b example in the sample, the printed distinction was not represented by the OCR output (0/1 retained).

Verse-marker detection found 20/25 Judges 13 markers with the Latin model. The complete-book diagnostic found 430/618 marker candidates alignable in monotonically increasing canonical order, all low-confidence; 188 references were missing, 26 additional number candidates were unmatched, and the one-to-one diagnostic mapping emitted no duplicate IDs by construction. No candidate qualified as high or medium confidence, and all 618 verses remain review-required. The 430 figure is marker alignment only, not 430 verified verse transcriptions.

Judges 1:1–13 specifically yielded only 7/13 marker candidates (verses 2–6, 8, and 9); 1, 7, and 10–13 were not recovered as markers. The scan visibly contains this passage across the Joshua/Judges book transition on PDF pp. 216–217, but Tesseract lost the chapter/verse 1 distinction, several digits, and the transition context. The book-scale pass covered PDF pp. 216–238, 23 pages and 46 explicitly cropped column images. A local research-only sequence matcher handled the transition; it is not added to the builder.

For Judges 13, the 20 detected markers are verses 1–3, 6, 8–10, 12–18, and 20–25; verses 4, 5, 7, 11, and 19 were not individually marked. Comparing OCR against the existing scan-checked 25-verse transcription gives 20.9% CER and 37.6% WER. The prose was not exact even where a verse marker was found. `n'aburu` is the known printed marked-b case; the printed diacritic is absent from the OCR, so the OCR output cannot preserve or encode the distinction. Marked-b recovery remains a manual image-reading task.

### Layout, preprocessing, and decision

The recognizer was run on separate left/right column crops for the full Judges book so OCR text would not jump across columns. This exposes a useful failure boundary: column order is retained within each crop, but the engine does not identify the Joshua-to-Judges transition, the book heading, or the chapter boundary by itself. The small multi-book regions show page-header contamination in the Revelation crop and clipping/line-order errors around verse numerals. No page-level line boxes or confidence scores were retained in the Tesseract run, so layout confidence is not separately claimed.

On the Genesis 3:5 region, the original scan crop scored 12.1% CER and 28.6% WER. Grayscale and 1% autocontrast produced the same scores. A conservative global threshold at 165 worsened the score to 13.5% CER and 35.7% WER. Deskew was not tested because the sampled scan pages appear straight. Therefore only cropping to the text column/region is supported by this experiment; contrast and threshold preprocessing should not be added based on these results.

At the observed Judges marker recovery rate, a naive 31,103-verse scale would still leave roughly 9,500 verse markers unrecovered, while every extracted verse would remain review-required. Even a deliberately low 10-second verification budget per verse is about 86 staff-hours; this is an illustrative lower-bound calculation, not a measured review speed, and it excludes correcting the observed 37.6% word error rate or finding missing references.

**Decision: IMPROVE OCR FIRST.** Do not scale this Tesseract configuration into the edition database. The script-Latin Tesseract model is the only tested configuration worth retaining as a candidate because its underdot/macron preservation is substantially better than English. Its Judges 13 word error rate, missing markers, and zero exact verse matches are too poor for low-review transcription. The next useful experiment is a historical-print recognizer such as Kraken, or a compatible PaddleOCR run on a working inference backend, trained/evaluated against a larger manually checked set. OCR disagreement should continue to trigger review, not automatic word selection.

The OCR environment, models, generated images, OCR text, and gold files are all confined to `/tmp` or ignored `data/research/`; no production packages, code, database, or normalization rules changed. The existing test suite passes: **42 passed**.

## Existing digital Union / IGBOB text search (2026-09-26)

This is a source search and fingerprint check, not a new OCR or import milestone. No whole-Bible OCR was run, no trusted IGBOB rows were changed, and no text from a candidate was copied into production data. The APK inspected below was downloaded to `/tmp` from its publicly listed APKPure release and read statically; it was not installed or executed. The only project change for this milestone is this research note.

### Search result

**Yes: a complete digital IGBOB transcription exists in the publicly distributed `com.mobobi.igbobible` APK.** APKPure lists version 2.0 (10.7 MB) as “Bible Nso (IGBOB)” and advertises offline Old and New Testament scriptures. The downloaded APK SHA-256 matched the hash on the listing (`f67f9e533d8a98a2684a6732ab5952167ee4617bb51ca0473199b84e2d1049fc`). Static archive inspection found 66 Igbo-side text assets, one per canonical book, plus 66 parallel English assets. The Igbo assets are UTF-16 text files containing HTML-like paragraph markup; verse numbers and chapter headings are embedded in the text. There was no Bible SQLite/JSON/USFM/OSIS module in the archive. The Judges asset contains the full book's 618 numbered verses. [APKPure package and version listing](https://apkpure.net/igbo-bible-igbo-english/com.mobobi.igbobible), [APK download listing](https://apkpure.net/igbo-bible-igbo-english/com.mobobi.igbobible/download).

This is already machine-readable scripture data, although it needs a small parser for its per-book paragraph format. It is the most direct full-text candidate found and the best match to the product edition under investigation. It is not a rights-cleared redistribution source: APKPure identifies the Android app but grants no Bible-text license; Uptodown labels the app distribution “Proprietary”; and the same `IGBOB` presented on Bible.com carries “Igbo Bible © Bible Society of Nigeria © 1906, 2006.” The app package therefore proves that a transcription is publicly distributed; it does not prove permission to redistribute or adapt the corpus. [Uptodown app/license metadata](https://igbo-and-english-bible.en.uptodown.com/android), [Bible.com IGBOB copyright notice and full Judges 13](https://www.bible.com/bible/77/JDG.13.IGBOB).

### Judges 13 fingerprint

The APK's `NDI-IKPE.txt` contains all 25 verses of Judges 13 in sequence. Side-by-side inspection with printed PDF pp. 229–230 found the same passage and order, including the opening fingerprint and references to Jehova and the Philistia. It is best classified **B: same Union translation/textual lineage with electronic spelling, spacing, and editorial differences**. Examples include print `Mọ-ozi` versus asset `Mọ ozi`; verse 2's printed marked-b is represented in the asset with a combining mark in one token. Underdots and historical macrons visible in the sample also survive as Unicode in the asset. The IA DjVu OCR loses the marked-b distinction, whereas this digital witness retains it.

The prior local `judges13-reviewed.json` is useful as a working transcription, but it is not a fully exact codepoint gold master: it leaves the printed marked-b in verse 2 as ordinary `b`, omits diacritics, and has individual reading/word-boundary differences from the page. A raw exact-verse comparison consequently reports 0/25 exact against that file, but that number does **not** mean the APK differs substantially from the scan. For example, the APK includes `n'ab͕uru` where the working transcription has plain `n'aburu`, matching the scan's under-marked print; the scan has `Mọ-ozi` where the app text uses `Mọ ozi`, a spacing/editorial change. The full passage's content, order, and distinctive wording match the scan witness; resolving every punctuation/orthography variant still requires collation against images rather than treating the old text file as infallible.

### Other digital witnesses and repositories

| Candidate | Format / completeness | Judges 13 fingerprint | Orthography and import | Rights / access assessment |
|---|---|---|---|---|
| `com.mobobi.igbobible` APK 2.0 | Downloadable APK; 66 per-book Igbo UTF-16 HTML-like text assets | **B**; full 25-verse sequence tracks scan wording and order | Preserves marked-b, underdots, and macrons in inspected sample; per-book parsing is practical | Exact IGBOB-labeled candidate, but no text redistribution/adaptation grant found; current BSN copyright notice remains controlling evidence to resolve |
| WordProject Igbo Bible | Complete online chapter HTML; its downloadable-Bible index currently does not list Igbo | **B** in the displayed Judges 13 chapter; wording is the same Union/IGBOB line, including `n'ab͕uru` | Chapter/verse structure is visible in HTML and the sample retains marked-b and diacritics; not a single downloadable Igbo corpus located | WordProject says content it considers public domain may be used under its terms and permits modified text under stated conditions, but its broad site claim does not establish that BSN's 1906/2006 `IGBOB` text is public domain. Do not rely on it as rights clearance. [Igbo book index](https://www.wordproject.org/bibles/ig/index.htm), [Judges 13](https://www.wordproject.org/bibles/ig/07/13.htm), [download list](https://www.wordproject.org/download/bibles/index.htm), [copyright terms](https://www.wordproject.org/contact/new/copyrights.htm) |
| Bible.com `IGBOB` | Complete, public chapter pages; no structured corpus download/license found | **B** relative to print in the displayed sample; full Judges 13 is readable | Good Unicode preservation, including the b mark and Igbo diacritics in the page display; not an independent downloadable file | Clearly identified as IGBOB and explicitly carries BSN copyright. Public reading/copy UI is not a reuse license. [Judges 13](https://www.bible.com/bible/77/JDG.13.IGBOB) |
| DOKUMEN.PUB “Bible Nso - The Holy Bible in Igbo” | Complete machine-rendered HTML text with book/chapter/verse structure | **B / same target lineage**: the mirror identifies `Bible Nso © 1906, 2006 BSN`; search-indexed text shows marked-b and historical forms | Unicode text is exposed, but the mirror is not an authoritative source or a trustworthy distribution channel | Copyrighted BSN notice remains; no permission grant. Do not import from the mirror. [Full-text mirror](https://dokumen.pub/bible-nso-the-holy-bible-in-igbo-asusu-igbo.html) |
| Bíblia Mundi “Igbo - All Bible” | A 2,601-page full-Bible PDF is indexed; the host did not serve a successful download during this check | **Unknown**: indexed extracts identify Bible Nso and show the BSN 1906/2006 notice, but I could not inspect the actual file or collate Judges 13 | PDF/possible text layer, not established as a clean structured transcription; no import assessment beyond PDF extraction | Rehosted full Bible with explicit BSN notice; no license grant. Not a rights-cleared source. [Indexed PDF](https://bibliamundi.com/wp-content/uploads/2023/09/Igbo-All-Bible.pdf) |
| Find.Bible / Digital Bible Library `IBOILB` | Catalog points to Digital Bible Library / developer entries; no unauthenticated direct text download found | **Unknown**: no candidate text obtained to fingerprint | Potential structured source only if the rights-holder/library grants access | Catalog metadata says “Igbo Union Version,” date 1988, copyright BSN; this conflicts with academic histories that identify a distinct 1988 Igbo Living Bible, so the catalog label/date should not be accepted without inspecting the actual DBL text. [Find.Bible record](https://dev.find.bible/bibles/IBOILB/?locale=en) |
| `Esssiee/bible-data` GitHub | Repository has only `.gitignore` and README, no Bible text files | **Unknown**; no text to fingerprint | README lists IGBOB as “No Response” with a bibles.org source pointer; no dataset is present | No downloadable text/license to assess. [Repository](https://github.com/Esssiee/bible-data) |
| CrossWire/SWORD and `turbozv/BibleVerse` GitHub | CrossWire's checked public module catalog did not surface an Igbo/IGBOB module; BibleVerse tree contains no Igbo text asset | No candidate text | No importable Union/IGBOB module found | No candidate rights grant. [CrossWire module catalog](https://crosswire.org/sword/modules/ModDisp.jsp?exp=true&modType=Bibles), [BibleVerse repository](https://github.com/turbozv/BibleVerse) |

The eBible public Igbo download is the 2020 Biblica Open Igbo Contemporary Bible and is excluded as requested. The Find.Bible record points to BSN/Digital Bible Library materials but did not expose their text without a separate access path. The FCBH catalog result for an “Igbo Union Version” describes an audio-focused APK and does not provide a text file in the displayed catalog fields. Neither is a rights-cleared text transcription found in this search.

### Decision

1. **Complete digital IGBOB:** yes. The Mobobi APK contains the entire IGBOB-labeled text as 66 per-book UTF-16 assets; public Bible.com pages corroborate the edition label and wording.
2. **Complete digital Union-family Igbo Bible:** yes. The APK and WordProject's complete chapter site provide full machine-readable text in the same Union/IGBOB line. DOKUMEN also mirrors a complete text but is not an authoritative or rights-safe source.
3. **Closest textual match:** the Mobobi APK assets, because they are a complete directly inspectable transcript explicitly labeled IGBOB. WordProject is a second close witness.
4. **Judges 13 match:** all 25 verse positions and the sequence of wording match the scan witness. The asset preserves the scan's marked-b in verse 2. Differences observed are transcription/orthographic/editorial details such as `Mọ-ozi` / `Mọ ozi`; the older local gold file itself has errors, so a naïve exact match score is not a valid edition-classification metric.
5. **Better orthography than IA OCR:** yes for the inspected passage; notably marked-b is present, and underdots/macrons are retained.
6. **Already-modernized Union transcription:** no clearly modern Ọnwụ rewrite was found. The APK and WordProject retain historical spellings/macrons and marked-b; their differences are limited editorial/digital presentation changes in the fingerprint sample.
7. **Mobobi app data:** per-book UTF-16 text assets with HTML-like markup and inline verse labels, not a database or standard USFM/OSIS file. The official app listing describes the edition as Bible Nso/IGBOB; public APK inspection verifies the packaged text.
8. **Next candidate:** keep the APK text as a research-only collation witness and ask BSN/DBL for the same text in a licensed structured format. Do not import the APK corpus into production unless redistribution and adaptation rights are clarified.
9. **Rights-cleared result:** none found. A complete transcription exists, so further OCR is not the immediate path for obtaining a comparison source; legal clearance is now the blocker to using this digital text as redistributable project data.

## Mobobi local importer and print collation (2026-09-26)

This is a local research/development import only. The APK is not committed or copied into the repository. Its SHA-256 is `f67f9e533d8a98a2684a6732ab5952167ee4617bb51ca0473199b84e2d1049fc`. Redistribution and adaptation rights remain unresolved. The importer does not normalize spelling or use KJV/OICB wording.

### Asset format and parser behavior

Static inspection of the package found 66 Igbo book assets under `assets/`, each beginning with the UTF-16 little-endian BOM (`FF FE`); their text decodes as UTF-16 without invalid code units. A 67th `.txt` file at the APK root is app-version metadata, not a Bible book. There are parallel `(English)` files, which are ignored. The Igbo assets use paragraph/div/line-break markup (`p`, `div`, `br`) and occasional inline `strong`/`em` tags. Chapter headings are visible book-name-plus-number strings, and verse numbers are ordinary text markers. No HTML character references occurred in the 66 real assets; the parser still decodes references if encountered. It replaces block tags with line boundaries, strips tags, and collapses intra-verse layout whitespace to one ASCII space. Punctuation, case, Igbo letters, macrons, underdots, apostrophes, hyphens, and combining marks are otherwise preserved without NFC/NFD normalization.

Four short non-verse blocks are present (`Mponkyerxne pii ba`, `Daa hene`, `Otukorq no`, `soq.`); the importer records them separately rather than attaching them to a verse. Exodus 20 has several inline/fused markers such as `9Ubọchi` and `23Unu`; the parser recognizes only the expected sequential marker before an uppercase verse start. 2 Chronicles 14:1 begins with a malformed literal `<1`; the importer removes that stray `<` and records the repair. These exceptions are included in the import report.

### Canonical coverage result

The dedicated parser is [builder/mobobi_import.py](../builder/mobobi_import.py). It has a canonical 66-book asset map, UTF-16 decoding, markup removal, stable verse IDs, duplicate/missing/unmapped diagnostics, local-only provenance metadata, and a candidate-output CLI. Canonical `bible.sqlite` remains unchanged. KJV was consulted only by comparing verse-ID sets: both KJV and canonical structure contain 31,103 IDs, with no set differences.

| Measure | Expected | Mobobi parsed |
|---|---:|---:|
| Books | 66 | 66 |
| Chapters | 1,189 | 1,189 |
| Verses | 31,103 | 31,044 |
| Missing canonical verse IDs | — | 59 |
| Duplicate IDs | — | 0 |
| Extra/unmapped IDs | — | 0 |
| Malformed references | — | 0 |
| Empty verses | — | 0 |

The 59 missing references are concentrated in three chapters: Numbers 26 has 18 parsed of 65 expected (missing 26:19–65), Job 41 has 24 of 34 (missing 41:25–34), and 3 John has 13 of 15 (missing 14–15). The package prints/labels the chapters and the verse sequences parse without internal jumps; the source-to-canonical count discrepancy is therefore reported, not repaired or reindexed. The importer wrote the incomplete data to ignored local candidate `data/databases/igbob-mobobi-candidate.sqlite`, with `coverage_status` explicitly set to incomplete and rights set to unresolved. The pre-existing `data/databases/igbob.sqlite` and its earlier modern companion were not overwritten. A complete Mobobi-derived `igbob.sqlite` and `igbob-modern.sqlite` were not generated because doing so would conceal the 59-reference gap.

### Judges 13 and distributed scan checks

The 25 verses in the current Judges working transcription were exported with both texts, equality, and difference categories in the ignored local report `data/generated/igbob-mobobi-judges13-comparison.csv`. It yields **0 exact codepoint matches and 25 non-exact** comparisons. Ten reduce to the same alphanumeric base after removing diacritics and punctuation; 15 have remaining differences against that working JSON. That residual count must not be read as 15 Mobobi translation changes: direct inspection of printed PDF pp. 229–230 shows multiple omissions/misreadings in the prior “scan-reviewed” working transcription (for example, its verse 3 `tapuru` does not match the print; the image and APK both read `gāturu`).

The full passage follows the same Union wording sequence. The print page confirms the Mobobi marked-b in verse 2 and spacing change `Mọ-ozi`/`Mọ ozi` in verse 3. The clearest confirmed substantive difference is Judges 13:23: the scan contains an additional short particle before the following clause that the APK omits. Judges 13:19 remains a word-level scan collation point. The working sample therefore remains useful for broad comparison, but it is not a fully exact gold transcription for computing literal verse equality.

One-verse scan comparisons cover the other requested books—Genesis 3:5, Exodus 20:23, Psalms 18:6, Isaiah 12:2, Matthew 10:1, John 1:1, Romans 1:4, and Revelation 1:1—for nine books total including Judges 13. The machine comparison is the ignored local report `data/generated/igbob-mobobi-distributed-scan-collation.csv`. I inspected the corresponding print images, including PDF pp. 3, 64, 229–230, 480, 610, 825, 898, 955, and 1051. Most sampled content follows the same translation, with digital punctuation, spelling, mark, or hyphenation differences. Two passages need source-level attention: Isaiah 12:2 contains a possible clause-level difference between print and APK, and Matthew 10:1 has a one-word difference. These are possible transcription/text differences, not normalization candidates. The complete corpus should be collated to the scan before it is treated as a faithful edition transcription.

### Partial normalization inventory

The normalizer was run **in memory only** over the 31,044 parsed verses to measure currently approved behavior. It changed **0 verses**, produced **0 transformations**, flagged 49,487 review items (33,427 macron-family candidates and 16,060 marked-b detections), reported 2,724 unknown items, and found no integrity issues. The approved exact lexicon entry `n'aburu` does not match the APK’s marked-b spelling; no new mappings were activated. No modernized database was written.

The local partial-corpus inventory contains 717,654 tokens, 25,586 casefold-grouped raw forms, and is explicitly labeled incomplete. It preserves raw Unicode and does not apply canonical Unicode normalization. Highest-frequency examples include:

| Candidate family | Top raw forms by occurrence | Provisional classification |
|---|---|---|
| Macron / `nē-`, `nā-`, `gē-`, `gā-` | `nēme` 1,108; `gēme` 708; `gādi` 558; `gābu` 479; `m'gēme` 469 | Context-dependent for the recognized verbal family; other macron forms unknown |
| Marked-b | `mb͕e` 5,938; `ub͕u` 767; `b͕ara` 350; `mb͕idi` 245; `b͕a` 230 | Systematic orthographic candidate, not approved for blind conversion |
| Apostrophe | `n'ihi` 6,427; `n'ebe` 2,615; `n'etiti` 2,079; `n'iru` 1,932; `n'ala` 1,548 | Unknown without lexical/construction evidence |
| Hyphenation | `onwe-ya` 1,517; `ma-ọbu` 1,299; `onwe-gi` 1,199; `onye-nwe-ayi` 1,058; `onwe-ha` 881 | Unknown; no general joining/splitting rule approved |

The review-priority table for all forms, with token occurrences, verses affected, examples, candidate family, evidence, and provisional classification, is the ignored local report `data/generated/igbob-mobobi-normalization-candidates.csv`; the JSON summary is `data/generated/igbob-mobobi-normalization-inventory.json`. These counts describe the available partial text, not all 31,103 canonical verses.

Tests added UTF-16/markup/entity decoding, preservation of marked-b/macrons/Igbo Unicode, duplicate and missing markers, canonical asset mapping and deterministic reports, plus modern-edition provenance. `python3 -m unittest discover -v` passes **37 tests**; the complete pytest suite passes **46 tests**. All source text databases and generated reports remain under ignored `data/`; no Android, canonical structure, OICB, or normalization rules were changed.

## Gap investigation and composite corpus recovery (2026-09-26)

This targeted follow-up supersedes the prior assumption that only 59 references were absent. The source audit found **72 unsupported canonical verse slots** once the mislabeled 3 John asset is quarantined. No OCR was performed. Raw APK assets were decoded directly as UTF-16 and inspected around each boundary.

### Raw-source findings

| Gap | Raw Mobobi asset evidence | Cause | Recovery / mapping |
|---|---|---|---|
| Numbers 26:19–65 | `ỌNU-ỌGUGU 26` has verse markers 1–18, then `</p><p> X-X-X </p><p> ỌNU-ỌGUGU 27`. No verse-19 marker or intervening text appears. | **E: source asset omits the tail.** This is not an end-marker parse failure, fused label, malformed tag, encoding artifact, or canonical numbering mismatch. | WordProject exposes numbered 19–65. The print scan shows the same passage with markers 19–65 across PDF pp. 147–148 (printed pp. 151–152). Recovery maps these directly to `num-26-19`…`num-26-65`; text is attributed to WordProject, not Mobobi. [WordProject Numbers 26](https://www.wordproject.org/bibles/ig/04/26.htm), [print PDF p. 147](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=147), [print PDF p. 148](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=148). |
| Job 41:25–34 | `Job 41` contains verse markers 1–24 and then the closing markup / `X-X-X` separator; the next heading is `Job 42`. | **E: source asset omits the tail.** No continuation without labels, fused labels, malformed markup, or alternate numbering appears. | WordProject and Bible.com both expose Job 41:1–34 with the missing labels. Print PDF pp. 471–472 (printed pp. 475–476) visibly contain Job 41:25–34, ending at v.34 before Job 42. Recovery maps `job-41-25`…`job-41-34` from WordProject. [WordProject Job 41](https://www.wordproject.org/bibles/ig/18/41.htm), [Bible.com Job 41](https://www.bible.com/bible/77/JOB.41.IGBOB), [print PDF p. 471](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=471), [print PDF p. 472](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=472). |
| 3 John 1 | `III. JỌN 1` has 13 markers, but its complete verse-text sequence is an exact duplicate of the `II. JỌN 1` asset. Its opening addresses an unnamed woman, the text of 2 John; it is not 3 John. | **F: wrong source content under the 3 John asset label.** The correct 3 John text is absent from Mobobi, not merely missing v.14–15. Its true Mobobi contribution to 3 John is zero; the 13 copied 2 John rows were quarantined. | WordProject and Bible.com each expose 3 John in 15 canonical verse positions. The print page (PDF p. 1049 / printed p. 237) labels the last printed unit as v.14 and runs the material corresponding to digital vv.14–15 together. The local corpus uses the concordant digital boundary: `3jn-1-14` ends with the closing clause of the address; `3jn-1-15` begins a separate greeting. This is a witness-based split, not a KJV-derived or arbitrary split. [WordProject 3 John](https://www.wordproject.org/bibles/ig/64/1.htm), [Bible.com 3 John](https://www.bible.com/bible/77/3JN.1.IGBOB), [print PDF p. 1049](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=1049). |

For Numbers and Job, the scan pages confirm that the verse tail is present in print and the verse-marker sequence agrees with the canonical/WordProject numbering. The recovered wording is explicitly attributed to WordProject; the scan is not claimed as a full character-by-character transcription of those two passages. For 3 John, the scan itself supports the text and printed 14-unit layout; WordProject and Bible.com independently support the final 14/15 digital boundary. Public display was used only for this local research collation and does not establish redistribution rights.

### Importer and source provenance

The importer now detects a complete duplicate book-text sequence, reports it, and quarantines the duplicate instead of treating its verse IDs as valid content. A local recovery JSON can overlay a canonical verse only when it supplies both text and an explicit `source_witness`. Per-verse recovery provenance is stored in edition metadata as JSON; the edition schema and canonical database were not changed.

The Mobobi-only candidate now has **31,031 valid Mobobi verses**, 72 missing canonical references, and 13 quarantined wrong-book rows. The earlier “31,044 imported / 59 missing” count included the 13 copied 2 John verses under 3 John IDs. Recovery provenance for the complete local corpus is:

| Provenance | Verses |
|---|---:|
| Mobobi directly parsed, after quarantining the false 3 John rows | 31,031 |
| Mobobi mechanically recovered | 0 |
| WordProject Numbers 26:19–65 | 47 |
| WordProject Job 41:25–34 | 10 |
| WordProject + Bible.com 3 John:1–13 | 13 |
| WordProject + Bible.com 3 John:14–15, split from printed unit 14 | 2 |
| **Total** | **31,103** |

The complete local `data/databases/igbob.sqlite` validates at 66 books, 1,189 chapters, 31,103 verses, with no missing, duplicate, extra/unmapped, malformed, or empty references. It is a **composite Union-family research corpus**, not a pure Mobobi transcription and not a rights-cleared distribution artifact. Metadata includes the 72-reference `verse_source_provenance_json`, per-source counts and source URLs, the quarantined duplicate-book anomaly, Mobobi APK hash, package identity, local-only distribution status, and unresolved redistribution rights. The `igbob-modern.sqlite` database was not regenerated.

The reproducible local recovery manifest is ignored under `data/research/igbob-source/mobobi-gap-recovery.json`; generated candidate and complete import reports are under ignored `data/generated/`. They must remain local.

### Judges 13 calibration corrections

A fresh visual comparison of all 25 Mobobi verses against the two print pages corrected local reference text for verses 3, 19, and 23. At v.3, the old working transcription's reading was wrong; the scan and Mobobi agree on the verb form. At v.19, the old working transcription misread the phrase; Mobobi and the page image carry the same clause. At v.23, the printed page contains one additional short particle before the following clause, which Mobobi omits, a genuine textual difference. The other 22 follow the same visible wording sequence; their observed differences are historical spelling/diacritic/spacing, but the scan strings were not all re-transcribed codepoint by codepoint, so their exact equality is marked unknown in the CSV. The revised JSON warns that those prior strings remain provisional. [PDF p. 233](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229), [PDF p. 234](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=230).

## Full-corpus orthographic modernization milestone (2026-09-26)

This section supersedes earlier notes that the local edition contained only Judges 13, that no full-corpus normalization pass had been generated, or that marked-b was unproven. The input was the complete, local-only composite `data/databases/igbob.sqlite` (66 books, 1,189 chapters, 31,103 verses). It remains a research corpus with unresolved redistribution rights; both it and the derived edition are ignored local data.

### Inventory and impact

The reproducible inventory generator is `builder/igbob_normalization_inventory.py`. It reads source verse strings without writing to them and emits [the full token inventory CSV](../data/generated/igbob-normalization-inventory.csv) and [inventory summary JSON](../data/generated/igbob-normalization-inventory.json). It preserves raw Unicode forms, uses casefolded lookup keys only as a secondary field, and records each form's frequency, affected verses, example references/contexts, surface-pattern flags, and conservative candidate classification. It inventories all 718,706 tokens and 28,899 distinct raw forms.

| Candidate | Occurrences | Verses/forms | Finding |
|---|---:|---:|---|
| Marked-b graphemes | 16,727 marks in 16,143 token occurrences; 1,567 forms | 11,157 verses | The historical Union-to-Ọnwụ `gb` correspondence is supported and was tested against every marked form. |
| Macron-bearing forms | 34,939 token occurrences; 4,476 forms | See inventory | Includes `nēme` (1,104), `gēme` (711), `nāb͕a` (125); do not remove macrons or resolve morphology by string replacement. |
| Prefix-like macron families | `nē` 9,007; `nā` 9,063; `gē` 4,908; `gā` 5,344 token occurrences | Respectively 8,559; 8,670; 4,668; 5,042 verse references across the surface groups | Remain unresolved/context-dependent. These group counts are surface-prefix counts, not proof that every token has the same grammar. |
| Internal apostrophe forms | 49,708 token occurrences | full form-by-form contexts in CSV | Elision/contraction and lexical boundaries are mixed; no global rewrite. `n'ihi` alone occurs 4,281 times. |
| Hyphenated forms | 72,434 token occurrences | full form-by-form contexts in CSV | Do not remove hyphens globally. `onwe-ya` occurs 1,400 times; compound/clitic status needs individual evidence. |
| Combining marks | U+0355: 16,727; U+0323: 1,460 occurrences | Included in the full inventory | Under-dots and other marks are preserved unless an exact proven mapping applies. |
| Punctuation/spacing examples | `Mọ-ozi` occurs 66 times | scan pages show a spaced digital variant | This is a typography/word-boundary question, not an automatic global change. |

The highest-frequency marked forms are `mb͕e` (4,902), `Mb͕e` (1,039), `ub͕u` (692), `b͕ara` (351), and `mb͕idi` (242). These recalculate against the complete composite corpus; they supersede the older partial-corpus frequencies. The full CSV also reports every one of the 28,899 token forms, including ordinary forms whose archaic status cannot responsibly be inferred from frequency alone.

### Marked-b: source glyph and modern correspondence

I visually inspected the actual scan at [PDF page 229](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=229) and [PDF page 230](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=230), printed pp. 233–234. The type shows a distinct marked form of `b` in `Mb͕e`, `b͕a`, `ub͕u`, and `ab͕uru`; the distinction is present in print, not invented by Unicode. The corpus's `b` + U+0355 sequence is a modern digital encoding convention for that printed marked-b glyph, not the glyph's linguistic name.

The strongest historical correspondence comes from the primary [International Institute of African Languages and Cultures, *Practical Orthography of African Languages* (1930), “Implosive Sounds”](https://www.bisharat.net/Documents/poal30.htm). It describes an implosive `b`, recommends the letter `ɓ` for that sound in some orthographies, and states that Union Ibo adopted the spelling `gb` for the corresponding sound. The contemporaneous Committee's [1961 Official Igbo Orthography notes](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf) list plain `b` and digraph `gb` separately. As phonetic confirmation, Peter Ladefoged's Cambridge excerpt describes the Igbo bilabial implosive and says it is written `gb` in local orthography ([*A Phonetic Study of West African Languages*](https://assets.cambridge.org/97805211/16237/excerpt/9780521116237_excerpt.pdf)). Together these sources identify the printed marked/hook-like `b` as the historical implosive-b consonant, not a labialized `b+w` or an OCR-created digraph; Ọnwụ writes the Union consonant as `gb`.

The complete corpus has one marked-b sequence and no counterexample in its 1,567 marked forms. The approved mapping is narrowly encoded as `b͕` → `gb` and `B͕` → `Gb`; it never changes plain `b`, and it cannot reconstruct a mark already lost by OCR. The exact word `ab͕uru` had a separate lexical proposal to `agbụrụ`, supported by the printed Judges 13:2 context and the [Nkọwa okwu dictionary entry](https://nkowaokwu.com/word?word=agburu). In ruleset 0.4.0 that vowel-changing proposal is pending; the active consonant rule yields `agburu` and preserves the source vowel code points.

### Historical approved mappings snapshot (rulesets 0.2.0–0.3.0; superseded below)

Ruleset `0.2.0` contains the two case-sensitive marked-b rules. Reviewed lexicon `0.3.0` has exact approved entries for `ab͕uru` → `agbụrụ`, `Ab͕uru` → `Agbụrụ`, and `n'ab͕uru` → `n'agbụrụ`, in addition to the earlier scan-reviewed unmarked witness form `n'aburu` → `n'agbụrụ`. These exact lexical entries account for 254 complete-token matches (227, 9, and 18 respectively); the existing unmarked entry itself has no hit. Hyphenated/apostrophe-joined compounds are not split to trigger an exact lexical mapping. No lexical rule is inferred from frequency.

At the earlier 0.2.0 ruleset milestone, no transformations had yet been approved for `nē-/nā-/gē-/gā-`, general vowel modernization, or joining/separation. The later 0.3.0 approval and current 0.4.0 fused-family expansions are recorded below. Exact lexical entries that add underdots were subsequently returned to pending status under the hard vowel-dot preservation constraint.

### Historical 0.2.0 local edition QA snapshot (updated current status below)

The complete [modern edition database](../data/databases/igbob-modern.sqlite) was rebuilt from all 31,103 source verses. Its integrity check is `ok`; it has 66 books and 31,103 unique verse IDs, and its IDs exactly equal the read-only canonical `bible.sqlite` verse IDs. Chapter count is checked against the canonical database (1,189); edition layers intentionally do not duplicate chapter structure. Source provenance counts, recovery URLs, source status, and unresolved rights status are retained in metadata.

| Measure | Result |
|---|---:|
| Verses changed / unchanged | 11,157 / 19,946 |
| Changed verse share | 35.8711% |
| Audited transformations | 16,727 |
| Transformations by rule | `b͕` → `gb`: 16,428; `B͕` → `Gb`: 45 |
| Transformations by lexicon | `ab͕uru`: 227; `Ab͕uru`: 9; `n'ab͕uru`: 18 |
| Unique historical token forms transformed | 1,567 |
| Marked-b grapheme occurrence coverage | 16,727 / 16,727 (100%) |
| Candidate-form occurrence coverage | 16,727 / 213,103 (7.8493%); denominator includes forms with macrons, combining marks, apostrophes, hyphens, and format features, but excludes unmarked plain words with unknown lexical history |
| Remaining review/unknown findings | 36,226 spans; 4,471 unique forms across 18,438 verses |
| Token count | 718,706 before and after; zero drift |

The review artifact [igbob-normalization-review-samples.json](../data/generated/igbob-normalization-review-samples.json) contains transformed examples across Genesis, Exodus, Judges, Psalms, Isaiah, Matthew, John, Romans, and Revelation, plus every verse of Judges 13. Automated semantic-drift checks replay each audited source span to the stored output, confirm the token count is unchanged in every verse, and verify all text outside audited spans is identical. No word loss, insertion, reordering, or accidental token merging/splitting was detected. This mechanical check does not substitute for an Igbo editorial review of unresolved lexical and grammatical candidates.

The [quality report JSON](../data/generated/igbob-normalization-quality-report.json) includes totals, transformations by rule and lexicon entry, unresolved examples, corpus coverage denominators, integrity, ID equality, and drift checks. All generated data and reports remain ignored under `data/`; redistribution rights for both editions remain unresolved.

Focused tests now cover duplicate-book quarantine and recovered-verse provenance. The complete pytest suite passes: **47 passed**. No modernization rules were added or run, and no commit or push was made.

## Complete Unicode and grapheme audit (2026-09-26)

The raw-source audit is implemented in `builder/igbob_unicode_audit.py`. It reads the local 31,103-verse `igbob.sqlite` without rewriting it or normalizing its strings. It reports exact codepoints and grapheme clusters, token forms, affected verses, sample words and references, and separate punctuation/whitespace tables. The complete machine-readable inventory is [igbob-unicode-audit.json](../data/generated/igbob-unicode-audit.json); the combining-mark cluster table is [igbob-unicode-graphemes.csv](../data/generated/igbob-unicode-graphemes.csv). The source has 3,858,095 codepoints, 109 distinct codepoints, 113 distinct grapheme clusters, 718,706 tokens, and 28,899 distinct raw token forms.

### Modern alphabet allowlist and audit method

The allowlist follows the 36-grapheme Ọnwụ inventory: 28 consonant graphemes (`b gb ch d f g gh gw h j k kp kw l m n ṅ nw ny p r s sh t v w y z`) and eight vowels (`a e i ị o ọ u ụ`). The official 1961 orthography notes are the primary standard reference ([Official Igbo Orthography, Ọnwụ Committee, 1961](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf)); an academic description reproduces the 36-grapheme inventory, identifies the nine digraphs, and distinguishes tone marking from alphabet letters ([Developing Methods and Resources for Automated Processing of Igbo, §2.1.1–2.1.2](https://core.ac.uk/download/pdf/83934757.pdf)). It describes acute/high and grave/low tone marking and notes that tone-bearing units can include syllabic nasals. The audit treats acute/grave tone on a modern vowel as phonological marking, not an extra alphabet letter. Punctuation, digits and whitespace are inventoried separately. Raw precomposed and decomposed forms remain separate in all counts; Unicode decomposition is consulted only to classify whether a raw grapheme represents a standard base vowel with a tone mark.

### Corpus findings

Only two combining codepoints occur:

| Mark | Codepoint | Occurrences | Unique token forms containing it | Verses |
|---|---:|---:|---:|---:|
| Combining dot below | U+0323 | 1,460 | 126 | 1,148 |
| Combining right arrowhead below | U+0355 | 16,727 | 1,567 | 11,157 |

The dot-below combinations include tone-marked dotted-o forms `ọ̀` (805 clusters), `Ọ̀` (386), `ọ́` (200), and `Ọ́` (2). These are dotted-vowel graphemes with tone marks, not non-Latin lookalikes or malformed characters. They remain byte-for-byte unchanged. The six other combining grapheme clusters are `b͕` (16,682), `B͕` (45), and those four dotted-o forms. Full occurrence, word, verse, example-word and reference lists are in the JSON and CSV reports.

The macron inventory is retained without replacement: `ā` occurs 16,701 times, `ē` 17,170, `ū` 976, `ī` 27, `Ā` once, and macron-plus-dot `ọ̄` 67 times. The report contains 4,476 raw word forms with macrons and 34,939 token occurrences; **zero macron replacements** were performed. The `nē-/nā-/gē-/gā-` families remain morphological/contextual review material, not character substitutions.

The grapheme-aware scan recognizes `ch`, `gb`, `gh`, `gw`, `kp`, `kw`, `nw`, `ny`, and `sh` as units, so their component letters are not falsely flagged. Out-of-inventory alphabet units include `b͕`, `B͕`, macron vowels, precomposed `ḅ` (U+1E05; 41 occurrences in 22 token forms across 27 verses), and rare `q`, `x`, and `c`. The `q`/`x` examples include `quail`, `palanquin`, `flax`, `wax`, `onyx`, and `sardonyx`; these are foreign/source forms rather than new Igbo letters. Acute/grave on syllabic `n` (for example, `ǹ`, `ń`) is treated as optional tone notation, consistent with the academic account of tone-bearing syllabic nasals, rather than as another alphabet letter. The complete report found no non-Latin-script lookalikes or isolated combining marks. Source punctuation/symbol anomalies also appear embedded in words: examples include `=`, `>`, `#`, `/`, and `_` in Ruth. They are retained and classified as likely OCR/encoding/source corruption, not normalized.

### Marked-b result and local full-corpus application

The exact raw sequences `b` + U+0355 and `B` + U+0355 occur 16,682 and 45 times respectively: 16,727 total marks, 1,567 raw token forms, and 11,157 affected verses. The complete corpus contains no conflicting use of either exact grapheme. Historical documentation independently supports the correspondence: the 1930 *Practical Orthography of African Languages* says Union Ibo represented the implosive consonant with `gb` ([“Implosive Sounds”](https://www.bisharat.net/Documents/poal30.htm)); the 1961 Ọnwụ inventory includes ordinary `b` and `gb` as separate graphemes. Thus `b͕` → `gb` and `B͕` → `Gb` are approved systematic character mappings. The full-corpus comparison confirms the already-generated local modern edition has zero remaining U+0355 marks, 16,727 transformed marks, 1,567 changed raw word forms, and 11,157 changed verses. The source and output both contain 34,942 macron codepoints. This audit verified the existing rule and output; it did not modify normalization rules or rebuild the generated edition.

The separate precomposed `ḅ` form is **not** included in the approved rule. Its 41 occurrences are concentrated in Malachi. The print scan at [PDF page 813, printed page 817](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=813) visibly shows a marked-b glyph in the corresponding passage. That supports a likely relationship to the historical consonant, but does not prove that digital U+1E05 is a one-to-one encoding equivalent across all 22 forms. It remains **UNKNOWN / not automatically mapped** pending direct digital-witness or glyph-by-glyph collation. The local corpus is composite, and a Unicode variant could reflect the transcriber's encoding practice as well as print.

Other out-of-inventory patterns are conservatively classified: macrons as `MORPHOLOGICAL_ORTHOGRAPHY`; marked-b as `SYSTEMATIC_CHARACTER_MAPPING`; suspicious embedded symbols as `OCR/ENCODING_ANOMALY`; and U+1E05 plus the small number of foreign/non-Igbo alphabet letters as `UNKNOWN` pending source review. Acute/grave on standard vowels and dotted vowels are ordinary modern tone-marked graphemes and are not flagged as nonstandard. Synthetic regression tests cover raw-sequence preservation, marked-b counts and macron non-replacement. The historical source and modern output database were not changed by the audit run.

## Approved morphology and generated modern edition (2026-09-26)

This section supersedes earlier statements in this document that the four frequent macron families were wholly unresolved. It does **not** approve generic macron deletion, vowel-dot changes, tone-mark deletion, or rewriting stems.

### Modern joining convention and interpretation

The [official 1961 Ọnwụ orthography](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf) distinguishes the preposition `na` (written `n’` before a vowel) from auxiliary `na-`, whose hyphen is part of the written construction. The [NOUN IGB 122 grammar courseware](https://nou.edu.ng/coursewarecontent/IGB%20122%20INTRODUCTION%20TO%20GRAMMATICAL%20PATTERNS%20IN%20IGBO%20%28MMALITE%20AMMAM%20USORO%20TASS%20IGBO%29.pdf) describes `na-` as ongoing/current action and `ga-` as future, with examples such as `na-agụ` and `ga-abịa`. Harvard’s [Igbo ELIAS lesson on future forms](https://elias.fas.harvard.edu/languages/igbo/beginning/15/making-plans-future) likewise writes the future auxiliary with a hyphen (`ga-aga`, `ga-eje`, `ga-abịa`). Thus the target strings are `na-eme`, `na-akpa`, `ga-eme`, and `ga-aga`, not spaced forms or apostrophe forms.

The corpus families are historical contracted forms of the same auxiliary constructions, with the following participial vowel restored: `nē-` → `na-e-`, `nā-` → `na-a-`, `gē-` → `ga-e-`, and `gā-` → `ga-a-`. The `na` construction has progressive and habitual readings according to context; the academic study [“Igbo na + participle: a semantic examination”](https://journalofwestafricanlanguages.org/downloads/download/103-volume-35-number-1-2/527-igbo-na-participle-a-semantic-examination) explicitly treats both readings. `ga-` is the future construction. This is a morphological expansion at the beginning of a token, not a rule replacing `ē` or `ā` wherever they occur. The inserted hyphen is internal to the token; whitespace and apostrophes are unchanged.

In the earlier ruleset 0.3.0 milestone, the analysis was supported by the modern orthography/grammar sources above, repeated corpus paradigms, and direct preservation of the observed verb stem in each token-initial change. The current fused-family findings and counts are in the following section. It is not based on a claim that every source spelling is transparent about vowel harmony. The raw first-stem-vowel distribution is `nē`: e 4,897 / i 1,507 / o 797 / u 1,804, with two outliers; `gē`: e 2,432 / i 1,236 / o 266 / u 973, with one outlier. The `nā` and `gā` families split between written a/ọ and written e/i/o/u classes (`nā` 4,500 vs. 4,563; `gā` 2,082 vs. 3,262). An academic study of Ekwulobia describes ATR vowel groups and harmony-conditioned participial allomorphy ([“Aspects of Morpho-Phonology in Ekwulobia Igbo”](https://www.researchgate.net/publication/381660168_Aspects-of-Morpho-Phonology-in-Ekwulobia-Igbo)), but it is dialect-specific and does not justify rewriting this corpus’s stems or selecting the historical macron family from the next written vowel. The rules therefore preserve the family encoded by the historical prefix, rather than calculating a replacement vowel from the stem. The historical spelling `nēkasa` (Isaiah 9:3) and three hyphen-separated token-initial forms (`nā-maghi`, `nā-asọputu`, `gā-napu`) are deliberately excluded. They remain unchanged pending a lexical/contextual decision. At ruleset 0.3.0, fused subject forms such as `M'gēme` and `anēme` were left untouched. The full-corpus analysis below resolves the bounded subject-plus-auxiliary families and leaves ambiguous cases unchanged.

### Corpus inventory and applied counts

The raw corpus has 34,939 macron-bearing token occurrences, 4,476 distinct token forms, and 18,107 affected verses. Raw code-point totals are `ē` 17,170, `ā` 16,701, `ū` 976, `ō` 67, `ī` 27, and `Ā` 1. The four token-initial families were `nē` 9,007 occurrences / 739 forms / 6,943 verses; `nā` 9,063 / 971 / 6,961; `gē` 4,908 / 503 / 3,823; and `gā` 5,344 / 549 / 4,130. These are occurrence groups, not additional unique-verse totals (families overlap in some verses). The complete raw form list and representative references are retained in `data/generated/igbob-morphology-audit.json` and `data/generated/igbob-macron-forms.csv`.

Approved morphology rules changed 28,318 prefix occurrences: `nē` 9,006, `nā` 9,061, `gē` 4,908, and `gā` 5,343. The four excluded token-initial forms account for the difference from their raw family totals. They changed respectively 6,942, 6,960, 3,823, and 4,129 verses, with overlap between rule families. No other macron family was changed.

At the ruleset 0.3.0 snapshot, the database recorded 45,086 transformations and 20,573 changed verses, leaving 6,624 macron code points. The exact lexicon accounts in that snapshot were subsequently deferred to preserve vowel dots. Current totals, the fused-family reductions, and the remaining macron inventory are in the 0.4.0 section below. No generic macron stripping was performed.

### U+1E05 `ḅ` and embedded symbols

All 41 U+1E05 occurrences (22 token forms; 27 verses) are in the Malachi portion of the Mobobi-derived corpus. Visual inspection of the corresponding printed scan pages in Malachi confirmed that the printed glyph is the same marked-b consonant seen elsewhere in the Union-family scan. The digital precomposed `ḅ` is therefore an alternate encoding/transcription of that marked-b in this source, not evidence for a distinct modern `ḅ` letter. Together with the Union `gb` spelling documented above, this supports approved `ḅ` → `gb` and uppercase `Ḅ` → `Gb` rules. The uppercase form was not present in the source and is covered by a synthetic regression test.

The suspicious embedded symbols remain source/transcription artifacts or unknowns and were not deleted or rewritten. Their embedded totals in the raw corpus are `=` 78 / 45 verses, `>` 140 / 66, `#` 150 / 108, `/` 29 / 22, `_` 23 / 22, and `@` 8 / 4. The inspected printed pages for Ruth and 1 Samuel do not show the corresponding symbols, but their intended expansions are not sufficiently uniform to authorize source cleanup. No source-cleanup rule was added. The regenerated modern database preserves them.

### Validation and review samples

This records validation at the ruleset `0.3.0` milestone. The quality report and sample CSV are regenerated for current ruleset `0.4.0`; the complete residual form/context work queue is in `data/generated/igbob-macron-residual-report.json`. Representative examples include:

| Reference | Historical | Modern | Rule |
| --- | --- | --- | --- |
| Genesis 21:24 | `gāṅu` | `ga-aṅu` | `gā` → `ga-a` |
| Exodus 12:47 | `gēme` | `ga-eme` | `gē` → `ga-e` |
| Judges 20:29 | `nēru` | `na-eru` | `nē` → `na-e` |
| Psalm 29:7 | `nāwaputa` | `na-awaputa` | `nā` → `na-a` |
| Isaiah 40:1 | `nāsi` | `na-asi` | `nā` → `na-a` |
| Matthew 27:36 | `nēche` | `na-eche` | `nē` → `na-e` |
| John 6:48 | `nēnye` | `na-enye` | `nē` → `na-e` |
| Romans 3:17 | `nāmaghi` | `na-amaghi` | `nā` → `na-a` |
| Revelation 2:29 | `nāgwa` | `na-agwa` | `nā` → `na-a` |
| Malachi 1:14 | `onye-nghọḅu` | `onye-nghọgbu` | `ḅ` → `gb` |

The examples show only the relevant token within each verse; complete source and output verses are in the generated CSV/JSON reports. Stems, underdots, `ṅ`, tone marks, and source whitespace were preserved. The `ḅ` example changes only the historical consonant to `gb`.

At that earlier snapshot `python3 -m unittest discover -v` passed 45 tests. Current complete unittest/pytest results (47/57) and the new fused-family regression coverage are in the final section below. Source redistribution rights remain unresolved; this local modern edition is not a rights determination.

## Residual macrons, fused constructions, and test audit (2026-09-26)

This section supersedes the earlier 0.3.0 residual counts and the earlier statement that fused forms were entirely untouched. The generated local modern corpus now uses ruleset `0.4.0` and reviewed-lexicon version `0.4.0`. It remains a local research artifact; the historical composite source’s redistribution status is unresolved.

### Test discovery and result

The count difference is test discovery, plus tests added over time. `python3 -m unittest discover -v` discovers `unittest.TestCase` methods but does not collect the ten module-level `test_*` functions in `tests/test_editions.py`. Pytest collects both groups, so pytest’s total is ten higher. The earlier 53/43 pair has that same ten-test difference. At the start of this milestone the then-current tree had 45 unittest cases and 55 pytest cases; pytest exposed two stale assertions for the 0.3.0 behavior. Those assertions were corrected to require the active transformations and version. Two regression methods were added for fused-pattern boundaries and idempotence. Current full runs are **47 unittest cases passed** and **57 pytest cases passed**. Pytest was run from a temporary `/tmp` virtual environment; no dependency was added to the project.

### Construction findings and evidence

The 1961 [Official Igbo Orthography](https://franpritchett.com/00fwp/igbo/txt_onwu_1961.pdf) states that pronouns are written separately from a following verb and distinguishes the impersonal pronoun from a verbal vowel prefix. Harvard ELIAS identifies `a` and `e` as impersonal pronouns ([Pronouns, Unit 4](https://elias.fas.harvard.edu/node/274)). An academic treatment analyzes Igbo `a/e` as an impersonal or unspecified pronominal subject ([Akinremi, “Impersonal Constructions in Igbo”](https://www.academypublication.com/issues/past/tpls/vol03/07/tpls0307.pdf)). For the verbal markers, Harvard’s [Unit 15](https://elias.fas.harvard.edu/languages/igbo/beginning/15/making-plans-future) gives `na-` as progressive, writes future `ga-` with a hyphen, and writes future-progressive as separate `ga na-`. The [NOUN IGB 122 grammar courseware](https://nou.edu.ng/coursewarecontent/IGB%20122%20INTRODUCTION%20TO%20GRAMMATICAL%20PATTERNS%20IN%20IGBO%20%28MMALITE%20AMMAM%20USORO%20TASS%20IGBO%29.pdf) independently describes `na-` and `ga-` as auxiliary constructions. These sources support word spaces between subjects/particles and a hyphen on the verbal prefix; they do not justify changing a verb stem or vowel dots.

Corpus matches were also checked in context across Old and New Testament books. The new transformations are bounded by full-token starts; they remove the apostrophe only where it joins a subject to the following auxiliary, add a separating space, restore the historical participial vowel, and preserve the remainder of the stem verbatim. The corpus counts are:

| Historical construction | Modern Ọnwụ segmentation | Occurrences | Macron marks removed | Notes |
| --- | --- | ---: | ---: | --- |
| `M' + nē/nā/gē/gā` | `M na-e/na-a/ga-e/ga-a` + unchanged stem | 2,585 | 2,585 | Total across the four families |
| `a + nē/nā/gē/gā` fused as `anē/anā/agē/agā` | `a na-e/na-a/ga-e/ga-a` + unchanged stem | 2,537 | 2,537 | Six apostrophe/hyphen-attached lookalikes were excluded by the boundary check |
| `ga + nē/nā` | `ga na-e/na-a` + unchanged stem | 168 | 168 | Future progressive |
| `M' + ga + nē/nā` | `M ga na-e/na-a` + unchanged stem | 18 | 18 | Explicit whole-construction exception rules; avoids partial matching |
| `a + ga + nē/nā` | `a ga na-e/na-a` + unchanged stem | 9 | 9 | Impersonal future-progressive forms, e.g. `Aganēsi` |
| **Total** |  | **5,317** | **5,317** | These are exact matched transformations, not all candidate-looking substrings |

Examples in the local audit include `1ch-17-6` `M'nē` → `M na-e`, `1co-11-22` `m'gē` → `m ga-e`, `1ch-10-4` `anē` → `a na-e`, `1co-13-10` `agē` → `a ga-e`, `1ki-14-5` `ganē` → `ga na-e`, `2sa-18-14` `m'ganē` → `m ga na-e`, and `dan-4-32` `Aganē` → `A ga na-e`. These are short token-level audit examples, not a reconstruction of full verses.

The boundary review confirmed that an unrelated word containing the same letters is not changed; `nēkasa` remains excluded; an already hyphenated token is not partially expanded; and apostrophe-attached/hyphen-attached ambiguous candidates are retained for review. Explicit positive, negative, punctuation, capitalization, stem-preservation, and idempotence regression cases cover these boundaries. Similar-looking negative forms such as `M'gaghi-nānu` are not assigned to these rules.

### Remaining inventory and classification

After ruleset `0.4.0`, the complete residual inventory contains **1,307 macron code points** in **1,305 token occurrences**, **244 distinct raw word forms**, and **1,151 affected verses**. The full machine-readable report lists every form, all affected verse IDs, exact grapheme/codepoint counts, all immediate within-token contexts, a provisional category, why it was retained, and evidence still needed: [igbob-macron-residual-report.json](../data/generated/igbob-macron-residual-report.json). A form-oriented CSV is also available at [igbob-macron-residual-forms.csv](../data/generated/igbob-macron-residual-forms.csv).

| Remaining category | Macron code points | Token occurrences | Unique forms | Affected verses |
| --- | ---: | ---: | ---: | ---: |
| `LEXICAL_HISTORICAL_SPELLING` (`ulo-ikwū` family) | 740 | 740 | 43 | 644 |
| `UNKNOWN` | 567 | 565 | 201 | 521 |
| **Total** | **1,307** | **1,305** | **244** | **1,151** |

Residual graphemes are `ū` U+016B (976), `ē` U+0113 (92), `ā` U+0101 (144), `ī` U+012B (27), `Ā` U+0100 (1), and the exact sequence `ō` U+014D + U+0323 (67). Thus the 67 `ọ̄` cases remain represented as two code points; the audit did not normalize their order or remove either mark. The 740 `ū` marks in forms such as `ulo-ikwū`, `ọmuma-ulo-ikwū`, `ulo-ikwū-ha`, and their inflected/prepositional compounds are grouped as a recurring lexical family, but no rule is approved for them. The other 567 marks include forms such as `nọ̄` (65), `būru` (56), `jū` (52), `ndi-ogbū` (31), `nwantī` (24), and `akērughi` (14). The corpus and sources reviewed here do not determine whether these individual macrons mark tone, vowel length, phonological detail, lexical convention, or a transcription practice; they remain `UNKNOWN`, not presumed tone marks.

Four known edge forms are still unchanged: `nēkasa` (Isaiah 9:3), `nā-maghi` (Luke 1:27), `nā-asọputu` (Psalm 15:4), and `gā-napu` (Exodus 15:9). Ambiguous apostrophe/hyphen forms, including the all-caps `ANĀMAGHI`, are also retained and individually listed in the JSON work queue. No generic macron replacement or ordinary lexical modernization was performed.

### Vowel-dot and syllabic-nasal preservation

The exact `ị`, `ọ`, `ụ` code point counts are equal between source and output (**83,406 each in aggregate**) and syllabic `ṅ` is unchanged (**2,299**). Earlier exact lexical entries that changed `ab͕uru` to `agbụrụ` were moved to `PENDING / UNRESOLVED` in lexicon version `0.4.0` because they add underdots to historical dotless `u`. The active marked-b grapheme rule still gives `ab͕uru` → `agburu`; it changes `b͕` to `gb` and leaves the vowels as printed/transcribed. The potentially standard modern lexical spelling `agbụrụ` is not applied automatically under the current hard preservation constraint. No underdot or `ṅ` modifications occurred in this rebuild.

### Corpus application and validation

The rebuilt local database uses ruleset `0.4.0` and lexicon `0.4.0`. It records **50,403 audited transformations** and **21,597 changed verses**. The 5,317 newly approved morphological expansions affect a union of 4,180 verses; overlap with the previously changed corpus explains why the total changed-verse count rises by fewer than 4,180. The residual macron count falls from 6,624 to 1,307. No verse text is inserted into the documentation beyond short token examples.

Validation against canonical structure reports **66 books, 1,189 represented chapters, 31,103 verses, zero missing IDs, zero duplicates, zero unknown references**, and SQLite `integrity_check = ok`. Source/output totals confirm no underdot or `ṅ` code points changed. Redistribution rights remain unresolved; rebuilding the local research edition does not establish a license.

### Exact suspicious-symbol occurrence inventory

The complete literal-symbol scan enumerated every `=`, `>`, `#`, `/`, `_`, and `@` in source verse text. It found 430 occurrences, all in rows attributed to Mobobi direct source provenance. The JSON and CSV preserve each verse ID, symbol offset, surrounding source fragment, provenance, whether the symbol is internal to a token, and the print-collation status: [igbob-strange-symbol-occurrences.json](../data/generated/igbob-strange-symbol-occurrences.json) and [igbob-strange-symbol-occurrences.csv](../data/generated/igbob-strange-symbol-occurrences.csv).

| Symbol | All occurrences | Affected verses | Embedded inside a word |
| --- | ---: | ---: | ---: |
| `=` | 78 | 45 | 78 |
| `>` | 140 | 66 | 136 |
| `#` | 152 | 109 | 58 |
| `/` | 29 | 22 | 25 |
| `_` | 23 | 22 | 0 |
| `@` | 8 | 4 | 5 |

Only `1sa-14-31` `#mbà` was individually checked against the corresponding 1982 print scan page (PDF p.253 / printed p.257); the printed text has no `#`, so that occurrence is classified `TRANSCRIPTION_ERROR`. The other 429 occurrences are `UNKNOWN / NOT_INDIVIDUALLY_COLLATED`; no conclusion that they are absent from print is made. No symbol was deleted and no source-ingestion cleanup was added. These figures supersede the earlier approximate embedded-only totals, which excluded some literal occurrences and undercounted `#`.

## Frozen normalization working release 0.4.0 (2026-09-26)

Ruleset `0.4.0` and reviewed lexicon `0.4.0` are frozen as the current local working release; this milestone adds no normalization rules. The complete [`igbob-modern.sqlite`](../data/databases/igbob-modern.sqlite) was rebuilt from [`igbob.sqlite`](../data/databases/igbob.sqlite), a composite local research corpus with Mobobi direct text plus explicitly attributed recovery witnesses. Source database SHA-256: `e5b5a6365c8bdf430f6c9d882a829a2a658553b64651903390b5c018115ba22b`. Source redistribution rights remain unresolved, so these generated Bible databases and reports remain local ignored research artifacts.

The output contains 66 books, 1,189 canonical chapters represented, and all 31,103 canonical verses. There are no missing, duplicate, unknown, or empty verse rows; SQLite `integrity_check` is `ok`. Every verse stores original text, modern working text, ruleset and lexicon versions, and sorted per-transformation JSON audit details. Metadata records source edition, source hash, source composition/provenance, source status, and unresolved rights. A generation timestamp is deliberately omitted to keep logical metadata and audits deterministic.

The release applies 50,403 approved transformations across 21,597 verses (69.437%); 9,506 verses (30.563%) remain unchanged. Unresolved macrons remain intact: 1,307 marked code points in 1,305 token occurrences, 244 forms, and 1,151 verses (3.701%). The `ulo-ikwū` family has 740 token occurrences over 43 forms and 644 verses; the remaining macron family has 565 token occurrences over 201 forms and 521 verses. There are 430 suspicious-symbol occurrences spanning 143 verses (0.460%); none are removed by this release.

Machine-readable outputs:

- [`igbob-normalization-quality-report.json`](../data/generated/igbob-normalization-quality-report.json) — release versions, corpus coverage and percentages, transformation totals by rule, unresolved inventory, source provenance, database and logical audit hashes.
- [`igbob-residual-review-pack-v0.4.0.json`](../data/generated/igbob-residual-review-pack-v0.4.0.json) — unresolved macron forms and suspicious-symbol occurrences only, ranked by impact, with limited contexts, representative IDs, provenance, unresolved rationale, and cumulative-coverage checkpoints. It does not contain the whole Bible text.
- [`igbob-normalization-samples.csv`](../data/generated/igbob-normalization-samples.csv) — representative before/after examples tagged with the rule applied.

Reproducibility was checked by building the modern database twice from the same source and versions. Ordered metadata, book rows, all original/normalized verse rows, ruleset and lexicon versions, and per-verse audit JSON were identical. The logical content-and-audit SHA-256 was `4bd4e027a902203be483819db682f49b3c3bc60c0a8e6aa926c803f6334484a6`; both builds passed SQLite integrity checks. Test suites at this release: 47 unittest cases and 57 pytest tests passed. These are local working outputs and do not change the unresolved redistribution-rights assessment.


## `ulo-ikwū` macron family resolution: working release 0.5.0 (2026-09-26)

### Decision

**Approved: PROVEN reviewed lexical mappings, limited to the 43 exact surface forms inventoried below.** The mapped grapheme is the single final `ū` (U+016B LATIN SMALL LETTER U WITH MACRON) in the historical `ulo-ikwū` tent/tabernacle family. In this family it is represented in modern Standard Igbo by doubled `uu`: for example, the vowel-only modernization of `ulo-ikwū` is `ulo-ikwuu`. The modern dictionary headword is `ụlọikwuu`; the working corpus retains the source's existing underdot choices, hyphenation, apostrophes, spaces, and all other letters.

This is a **reviewed lexical family mapping**, not a general `ū` → `uu` rule and not a rule for other macrons. Each observed surface form has its own exact approved lexicon entry. Prefixes, compounds, capitalization, and attached pronominal-looking endings are preserved. In particular, the two attached `-m` forms were mapped only at the vowel; they were not respaced or otherwise modernized.

### Evidence and interpretation

The academic history by Uchenna Oyali says the Union Igbo Bible (UIB) used Lepsius orthography; its history of the orthography explains that the missionary system followed the Lepsius alphabet. The Lepsius convention assigns the macron to long vowel quantity. The modern **Nkọwa okwu** dictionary lists the Standard Igbo tent lemma as `ụlọikwuu`, gives the variation `ụlọ ikwuu`, and supplies tent-use examples. Kay Williamson's *Igbo Dictionary* independently lists `ikwuù` in `ụnò ikwuù`, glossed “moveable house; tent; booth.” Together these identify the lexical item and its modern doubled-u spelling; the Lepsius system explains why the historical print uses a macron on that vowel.

Visual inspection of the local printed scan (no OCR used for this check) confirmed the macron on final `u` in both Testaments: Deuteronomy printed p. 165 (`ọmuma-ulo-ikwū`), Matthew p. 21 (`ulo-ikwū`), 2 Corinthians p. 174 (`ulo-ikwū-ayi`), and Hebrews p. 217 (`ulo-ikwū`). Thus the mark is present in print and is not just a modern Unicode-transcription artifact. The print samples corroborate the glyph, while the orthography history and dictionary establish the interpretation and modern spelling.

Sources:

- Oyali, [*Bible Translation and Language Elaboration: The Igbo Experience*](https://epub.uni-bayreuth.de/id/eprint/4298/1/Bible%20Translation%20and%20Language%20Elaboration%20%E2%80%93%20The%20Igbo%20Experience.pdf), especially PDF pp. 96–97 and 117–118.
- Lepsius, [*Standard Alphabet* (1863), Library of Congress scan/catalog](https://www.loc.gov/item/11010936/); the contemporary review [“On Lepsius’s Standard Alphabet”](https://upload.wikimedia.org/wikipedia/commons/c/cf/On_Lepsius%27s_Standard_Alphabet_%28IA_jstor-592160%29.pdf) identifies the horizontal line over a vowel as the sign of long quantity.
- Nkọwa okwu, [house search results and tent entry](https://nkowaokwu.com/search?word=house), spelling `ụlọikwuu`, variation `ụlọ ikwuu`.
- Kay Williamson, [*Igbo Dictionary: Draft of Edition II*](https://www.columbia.edu/itc/mealac/pritchett/00fwp/igbo/IGBO%20Dictionary.pdf), pp. 155–156.
- [Internet Archive printed scan](https://archive.org/details/igbo-bible-print); direct PDF: [Deuteronomy](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=161), [Matthew](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=833), [2 Corinthians](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=986), [Hebrews](https://archive.org/download/IBOILB_DBS_HS/Igbo-Bible-%28print%29.pdf#page=1029).

### Variants and coverage

All 43 approved surface forms contain exactly one U+016B in the final-vowel position of `ikwū`; there are no within-family exceptions to the `uu` correspondence. The forms include the unprefixed noun, `ọmuma-` and `ebe-` compounds, prepositional `n'` forms, mixed capitalization, and endings `-ha`, `-ya`, `-gi`, `-unu`, `-ayi`, and attached `m`. All existing punctuation adjacency is handled at lexical boundaries. The mapping changed no spaces, apostrophes, hyphens, underdots, or surrounding vocabulary.

The following similar-looking residuals were **not** included in the classified family and remain unresolved: independent `ikwū` (2 occurrences), `n'ulu-ikwū-gi` (1), and `ūlọ-ikwū` (1). These do not have the verified `ulo-ikwū` base in the observed spelling; no generic macron rule was applied to them.

| Historical form | Tokens | Verses | Sample verse IDs | Reviewed modern form |
| --- | ---: | ---: | --- | --- |
| `ulo-ikwū` | 172 | 166 | `1ch-15-1`, `1ch-16-1`, `1ch-17-5` | `ulo-ikwuu` |
| `ọmuma-ulo-ikwū` | 128 | 116 | `1ch-11-15`, `1ch-11-18`, `1ch-12-22` | `ọmuma-ulo-ikwuu` |
| `ulo-ikwū-ha` | 115 | 110 | `1ch-11-15`, `1ch-19-7`, `1ki-20-27` | `ulo-ikwuu-ha` |
| `n'ulo-ikwū` | 92 | 86 | `1ch-17-5`, `1sa-26-5`, `2ch-1-6` | `n'ulo-ikwuu` |
| `n'ọmuma-ulo-ikwū` | 58 | 54 | `1ki-16-15`, `1ki-16-16`, `1ki-20-29` | `n'ọmuma-ulo-ikwuu` |
| `ulo-ikwū-ya` | 29 | 29 | `1sa-11-1`, `1sa-26-3`, `1sa-26-5` | `ulo-ikwuu-ya` |
| `Ulo-ikwū` | 25 | 25 | `1ki-2-30`, `deu-31-15`, `exo-26-36` | `Ulo-ikwuu` |
| `n'ulo-ikwū-ya` | 19 | 19 | `1sa-13-2`, `1sa-17-54`, `1sa-4-10` | `n'ulo-ikwuu-ya` |
| `ọmuma-ulo-ikwū-ha` | 11 | 11 | `1ch-4-41`, `1sa-17-1`, `1sa-28-1` | `ọmuma-ulo-ikwuu-ha` |
| `n'ulo-ikwū-ha` | 10 | 10 | `1ch-5-10`, `1ki-12-16`, `1ki-8-66` | `n'ulo-ikwuu-ha` |
| `ulo-ikwūm` | 9 | 8 | `2pe-1-14`, `isa-29-3`, `jer-10-20` | `ulo-ikwuum` |
| `n'Ulo-ikwū` | 8 | 8 | `1ki-1-39`, `1ki-2-28`, `1ki-2-29` | `n'Ulo-ikwuu` |
| `ọmuma-ulo-ikwū-ya` | 6 | 6 | `2ki-5-15`, `2ki-6-24`, `jdg-4-15` | `ọmuma-ulo-ikwuu-ya` |
| `ulo-ikwū-gi` | 6 | 6 | `2sa-12-28`, `isa-54-2`, `job-22-23` | `ulo-ikwuu-gi` |
| `n'ulo-ikwū-unu` | 5 | 5 | `1ki-12-16`, `2ch-10-16`, `deu-1-27` | `n'ulo-ikwuu-unu` |
| `n'ọmuma-ulo-ikwū-ha` | 5 | 5 | `2ki-7-12`, `exo-19-16`, `exo-19-17` | `n'ọmuma-ulo-ikwuu-ha` |
| `ulo-ikwū-unu` | 4 | 4 | `deu-1-33`, `exo-14-2`, `jer-50-29` | `ulo-ikwuu-unu` |
| `ọmuma-ulo-ikwū-gi` | 3 | 2 | `deu-23-14`, `deu-29-11` | `ọmuma-ulo-ikwuu-gi` |
| `ulo-ikwū-Ya` | 3 | 3 | `psa-27-5`, `rev-13-6`, `rev-7-15` | `ulo-ikwuu-Ya` |
| `ebe-ulo-ikwū` | 2 | 2 | `1ch-6-54`, `ezk-25-4` | `ebe-ulo-ikwuu` |
| `ọmuma-ulo-ikwū-Ya` | 2 | 2 | `2ch-14-13`, `jol-2-11` | `ọmuma-ulo-ikwuu-Ya` |
| `ọmuma-ulo-ikwū-unu` | 2 | 2 | `amo-4-10`, `exo-29-14` | `ọmuma-ulo-ikwuu-unu` |
| `n'ulo-ikwū-gi` | 2 | 2 | `deu-33-18`, `jdg-19-9` | `n'ulo-ikwuu-gi` |
| `N'ulo-ikwū` | 2 | 2 | `exo-27-21`, `lam-2-4` | `N'ulo-ikwuu` |
| `Ọmuma-ulo-ikwū` | 2 | 2 | `gen-32-2`, `gen-33-8` | `Ọmuma-ulo-ikwuu` |
| `omuma-ulo-ikwū` | 2 | 2 | `gen-32-7`, `num-10-2` | `omuma-ulo-ikwuu` |
| `ebe-ulo-ikwū-ha` | 2 | 2 | `num-31-10`, `psa-69-25` | `ebe-ulo-ikwuu-ha` |
| `ulo-ikwū-ayi` | 1 | 1 | `2co-5-1` | `ulo-ikwuu-ayi` |
| `ọmuma-ulo-ikwūm` | 1 | 1 | `2ki-6-8` | `ọmuma-ulo-ikwuum` |
| `N'ọmuma-ulo-ikwū` | 1 | 1 | `2sa-1-3` | `N'ọmuma-ulo-ikwuu` |
| `ebe-ulo-ikwū-ya` | 1 | 1 | `act-1-20` | `ebe-ulo-ikwuu-ya` |
| `n'ebe-ulo-ikwū` | 1 | 1 | `gen-25-16` | `n'ebe-ulo-ikwuu` |
| `ma-ulo-ikwū-ya` | 1 | 1 | `gen-26-17` | `ma-ulo-ikwuu-ya` |
| `n'ọmuma-ulo-ikwū-ya` | 1 | 1 | `gen-32-21` | `n'ọmuma-ulo-ikwuu-ya` |
| `nulo-ikwū-gi` | 1 | 1 | `job-11-14` | `nulo-ikwuu-gi` |
| `n'omuma-ulo-ikwū` | 1 | 1 | `lev-17-3` | `n'omuma-ulo-ikwuu` |
| `nime-ulo-ikwū` | 1 | 1 | `lev-4-18` | `nime-ulo-ikwuu` |
| `ọmuma-ulo-ikwū-ayi` | 1 | 1 | `num-10-31` | `ọmuma-ulo-ikwuu-ayi` |
| `buruburu-ọmuma-ulo-ikwū` | 1 | 1 | `num-11-32` | `buruburu-ọmuma-ulo-ikwuu` |
| `Ulo-ikwūm` | 1 | 1 | `num-18-3` | `Ulo-ikwuum` |
| `ulo-Ikwū` | 1 | 1 | `num-20-6` | `ulo-Ikwuu` |
| `n'ulo-ikwū-Ya` | 1 | 1 | `psa-27-6` | `n'ulo-ikwuu-Ya` |
| `n'ulo-ikwū-Gi` | 1 | 1 | `psa-61-4` | `n'ulo-ikwuu-Gi` |

The full machine-readable audit records the exact Unicode sequence for every form, its complete affected verse-ID list, representative source contexts and provenance, variant dimensions, and target: [igbob-ulo-ikwu-review-v0.5.0.json](../data/generated/igbob-ulo-ikwu-review-v0.5.0.json).

### Corpus rebuild and regression

The regenerated `igbob-modern.sqlite` contains 31,103 verses, 51,143 approved transformations, and 21,832 changed verses. This adds 740 transformations and changes 235 additional verses over the 0.4.0 baseline. The 0.4.0 baseline was rebuilt independently from the unchanged rules plus the pre-0.5 lexicon; its ordered content-and-audit hash reproduced the frozen `4bd4e027a902203be483819db682f49b3c3bc60c0a8e6aa926c803f6334484a6`. Comparing per-verse audits found zero differences in any prior transformation; the only 740 added audit entries are these exact family mappings.

Remaining macrons are 567 code points in 565 token occurrences, 201 forms, and 521 verses. The unrelated residual `ū` count is 236. The 430 suspicious-symbol occurrences in 143 verses remain untouched. SQLite integrity and canonical coverage are valid: 66 books, 1,189 chapters, 31,103 verses, no missing or unknown IDs. New logical content-and-audit SHA-256: `ee20923c0fe7ddc11c77297484577573ad3f07e3da69882aec1a221b1fd86a9a`; modern database SHA-256: `3dd2b79e2066b120984d4dd47cd1998e1d9bd3e756640c46f3005d78d9905f27`.

Release is now ruleset and reviewed lexicon **0.5.0**. Machine-readable outputs are [the release quality report](../data/generated/igbob-normalization-quality-report.json) and [the 0.5.0 residual queue](../data/generated/igbob-residual-review-pack-v0.5.0.json). Regression totals after adding this mapping: 48 unittest cases and 58 pytest tests passed.

## v0.5.0 database storage cleanup

This is a storage-only rebuild; rules, reviewed lexicon, and modern verse wording remain at release `0.5.0`. Before replacement, the old modern database and the regenerated slim database were compared by verse ID and exact content: all 31,103 IDs matched, with zero missing IDs, extra IDs, or text differences. The rebuild reproduced 21,832 changed verses, 9,271 unchanged verses, and 51,143 transformations.

The 75,943,936-byte database was not large because of free pages: `freelist_count` was zero. Its `verses` table occupied 75,333,632 bytes. `audit_json` values occupied 49,375,552 UTF-8 bytes and held verbose per-verse transformation records plus repeated historical and normalized verse strings. `original_content` added another 4,144,832 bytes; modern `content` used 4,164,440 bytes. The verses primary-key index used 581,632 bytes; metadata, book names, and their indexes were small. The new database uses only `metadata`, `books`, and `verses(verse_id, content)`, with the release, source database hash, verse/change/transformation counts, and deterministic content/build hashes in compact metadata. It is 5,398,528 bytes with 1,318 pages at 4,096 bytes per page and zero free pages, a 92.9% size reduction.

All SQLite outputs now live directly under ignored `data/databases/`, including `bible.sqlite`, `igbob.sqlite`, `igbob-modern.sqlite`, `kjv.sqlite`, `oicb.sqlite`, and the incomplete `igbob-mobobi-candidate.sqlite`. There is no SQLite output in `data/generated/`; generated inventories and reports remain there. The generic [database manifest](../data/generated/database-manifest.json) lists relative paths under `data/databases/` and current SHA-256 values. The former Android-named manifest was replaced with this generic manifest.

Normalization details were preserved externally in [igbob-normalization-audit-v0.5.0.json](../data/generated/igbob-normalization-audit-v0.5.0.json). Its 21,832 changed-verse entries record verse ID and every historical form, modern form, rule ID/version, and source offsets; the compact rule catalog preserves descriptions and citations. The report also stores unresolved per-verse observations, a zero-difference comparison against the previous database, and the hash of the unchanged residual queue. The [quality report](../data/generated/igbob-normalization-quality-report.json) now records the slim database SHA-256 and content/build hashes. The modern content SHA-256 is `11cc6bcbb330c2c1f3843cfc74d227c13dfd8f43d8de503f16fad0e02362ac89`; the new SQLite file SHA-256 is `86ef8ceb731186627511027d50ff384ed62dd59441a5bc1650f5b02297aba626`. The storage-cleanup regression run passed **54 unittest cases** and **64 pytest tests**. This does not clear the local IGBOB artifacts for redistribution.

# Igbo orthographic normalization framework

## Purpose and limits

Normalization is orthographic, not translation. The normalizer must preserve the underlying Union Igbo wording and may change only forms covered by an explicitly approved, proven rule. Unknown or unresolved forms remain byte-for-byte unchanged and can be reported for review.

The input should be a faithful transcription of the source. OCR information loss cannot be reconstructed safely: in particular, the engine never guesses `b` → `gb` or `o` → `ọ`. Use image collation and a source-integrity profile when a transcription has known required graphemes. A source profile can detect a missing expected sequence only when independently verified counts are supplied; it cannot infer what a scan contained. The current IA scan is retained for local development; this is not redistribution clearance.

Ruleset `0.4.0` approves the four contextual macron auxiliary expansions, evidenced fused first-person/impersonal subject forms, and future-progressive constructions. It also maps the historical marked-b grapheme `b͕` → `gb` / `B͕` → `Gb`; it never infers missing marks in OCR plain `b`. The exact lexical mappings that add underdots to `ab͕uru` are pending because the active corpus task requires preserving vowel dots. General vowel modernization remains out of scope. See [igbob-research.md](igbob-research.md) for evidence, counts, and limits.

## API and output

`builder.normalization.normalize(text)` returns a `NormalizationResult` containing:

- `original_text` and `normalized_text`
- `ruleset_version` and `lexicon_version`
- `transformations`: one auditable entry for every changed span, with rule id, category, original/replacement strings, Python character offsets, description, source, and rule version
- `review_items`: known unresolved patterns in the normalized output, unchanged, with span and provenance
- `unknown_items`: output tokens with historical-looking macrons or combining marks that no review detector recognizes; unchanged
- `integrity_issues`: replacement characters and mismatches against optional externally supplied expected grapheme counts

Transformation offsets are zero-based, end-exclusive Unicode character offsets into `original_text`; review and unknown offsets refer to `normalized_text`. No Unicode normalization is applied. Invalid surrogate code points are rejected; other Unicode sequences are preserved as supplied.

Example:

```python
from builder.normalization import normalize

result = normalize("nēme, n'aburu")
assert result.normalized_text == "na-eme, n'aburu"
assert len(result.transformations) == 1
```

## Rules and approval gate

Rules live in `data/normalization/rules.json`. The file has a ruleset `version`, transforming `rules`, and non-transforming `review_detectors`. Supported transforming categories are:

- `safe_character`: explicit grapheme-sequence map (one codepoint or multiple codepoints on either side)
- `morphological_context`: a non-empty regular-expression match with a replacement template
- `lexical`: exact whole-token mapping
- `phrase`: exact phrase mapping, including spaces only when the reviewed mapping explicitly includes them

Each transforming rule has `rule_id`, `category`, `description`, `confidence`, `source`, `version`, `status`, `find`, and `replacement`. Morphological-context rules also set `regex: true`; an optional integer `priority` resolves equal-length overlaps. A rule changes text only when `status` is `APPROVED` **and** `confidence` is `PROVEN`. Pending rules and approved rules below `PROVEN` confidence are review findings, never transformations. Rejected rules do not transform.

Rules are applied in a deterministic, single pass over the original text. At a shared start offset, the longest match wins, then higher priority, then lexical rule-id order. Lexical rules require whole-token boundaries. Configuration is rejected when an approved mapping directly triggers another approved mapping; runtime output is also checked for cross-boundary chaining. Therefore the active ruleset must be idempotent. Punctuation and whitespace outside a matched rule are copied unchanged.

The shipped ruleset contains the proven Union marked-b-to-`gb` correspondence and conservative morphological expansions of token-initial and fused `nē/nā/gē/gā` auxiliary constructions. It also splits evidenced fused first-person and impersonal subjects, plus future-progressive `ga na-` forms. Plain OCR `b` is not presumed to represent a lost marked-b, and plain `o` is not presumed to have lost an underdot. Exact lexical entries that would add underdots to `ab͕uru` are pending under the hard vowel-dot preservation constraint. See [igbob-research.md](igbob-research.md) for the active inventory, counts, rule boundaries, and source citations.

## Reviewed lexical mappings

Manual entries live in the diffable `data/normalization/reviewed-lexicon.json` file. It is separate from generated Bible data. Each entry has:

```json
{
  "historical": "reviewed-source-form",
  "modern": "reviewed-modern-form",
  "status": "PENDING",
  "confidence": "TENTATIVE",
  "evidence": "citation or source collation reference",
  "notes": "review context",
  "version": "0.1.0"
}
```

Only `APPROVED` entries with `PROVEN` confidence can transform. Pending and non-proven matches are exposed in `review_items`; rejected entries remain inactive. The exact entries for `ab͕uru`, `Ab͕uru`, `n'ab͕uru`, and the unmarked witness spelling are `PENDING / UNRESOLVED` under lexicon `0.4.0`: their former proposed output added underdots. The active character rule alone changes `ab͕uru` to `agburu`, preserving the source vowel code points. Do not approve a lexical vowel change without a separate project decision that reconciles it with the hard vowel-dot preservation requirement.

## CLI inspection

The CLI accepts supplied text and does not read a Bible database or connect to the research corpus:

```sh
python3 -m builder normalize --text 'nēme ab͕uru'
python3 -m builder normalize --text 'nēme ab͕uru' --dry-run --report
```

The first form prints normalized text only. `--report` prints the complete JSON audit, including unchanged review/unknown findings. Both are inspection-only and write no edition/database output. Optional `--ruleset` and `--lexicon` paths allow isolated rule review. `--expect-sequence 'b͕=2'` supplies an externally verified minimum source count; if fewer occur in the supplied text, the report records a possible source-integrity loss.

The `--text` command is intentionally the only normalization CLI path for this milestone. There is no verse-id or database mode.

## Versioning and first real rule

Increment the ruleset version when rule behavior changes and the lexicon version when reviewed entries change. The returned result records both versions, and each transformation records its own rule/entry version and provenance. A future generated edition can store these versions in edition metadata to make builds reproducible.

Before approving additional transformations, require:

1. a rights-cleared source transcription with relevant print pages checked;
2. a primary or strong academic source establishing the exact orthographic correspondence;
3. enough lexical/morphological examples to rule out homographs and dialect/context exceptions;
4. reviewed before/after fixtures from synthetic examples or short rights-clear examples;
5. a rule marked `APPROVED` with `PROVEN` confidence, stable id, source citation, version, and tests for preservation, audit offsets, determinism, and idempotence.

Ruleset `0.5.0` and reviewed lexicon `0.5.0` are active. The complete local `data/databases/igbob-modern.sqlite` has the compact edition schema and preserves all 31,103 verse IDs. It contains displayable normalized content and compact edition metadata; complete transformation details live in `data/generated/igbob-normalization-audit-v0.5.0.json`. Approved fused first-person and impersonal auxiliaries and future-progressive contractions are expanded with audited whitespace/hyphen boundaries. The `ulo-ikwū` family now has exact reviewed mappings to doubled `uu`; all other macron families and lexical vowel-dot changes remain unchanged/pending. All underdot vowels and `ṅ` remain preserved.

## Development edition status

`builder.editions` provides isolated edition import/database functions and uses the normalizer to build the compact modern edition. The full per-verse transformation trace and unresolved observations are generated reports rather than edition columns; corpus-level source attribution remains in the research reports. The current complete databases are local research only: rights remain unresolved. PDFs and OCR material remain under `data/research/`, SQLite files under ignored `data/databases/`, and generated reports under ignored `data/generated/`. See [igbob-research.md](igbob-research.md) for counts, evidence, and limits.

## Working release 0.4.0 (superseded snapshot)

Ruleset and reviewed lexicon version `0.4.0` are frozen for the local modern IGBOB working edition. The release applies only already approved rules. It retains all unresolved historical macrons and suspicious symbols; no new lexical or Unicode-normalization rule is included. The full edition is `data/databases/igbob-modern.sqlite`; the release summary is `data/generated/igbob-normalization-quality-report.json`; and the compact unresolved-only review queue is `data/generated/igbob-residual-review-pack-v0.4.0.json`. Source corpus provenance and rights status are retained in the database and report. Rights remain unresolved, so these artifacts are local research outputs, not cleared for redistribution. Rebuilding from the same source hash, ruleset, and lexicon produced identical ordered verse content and transformation audits.

## Working release 0.5.0

Ruleset and reviewed lexicon version `0.5.0` approve 43 exact `ulo-ikwū` surface-form mappings. In those reviewed forms, historical `ū` is rendered as modern doubled `uu`; no other `ū` or macron is changed. Existing underdots, capitalization, whitespace, apostrophes, hyphens, and suffix text are preserved. The complete local database applies 51,143 transformations across 21,832 verses. Remaining macrons number 567 code points in 565 token occurrences, 201 forms, and 521 verses; suspicious source symbols are unchanged. The current edition and summaries are `data/databases/igbob-modern.sqlite`, `data/generated/igbob-normalization-quality-report.json`, and `data/generated/igbob-residual-review-pack-v0.5.0.json`. The complete per-transformation audit is `data/generated/igbob-normalization-audit-v0.5.0.json`; the exact family audit is `data/generated/igbob-ulo-ikwu-review-v0.5.0.json`. The update and source evidence are documented in [igbob-research.md](igbob-research.md). Source redistribution rights remain unresolved, so these outputs are local research artifacts.

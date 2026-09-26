from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import load_repository_env
from .database import build_databases
from .data_paths import database_path
from .pipeline import OFFICIAL_USFM_URL, download_archive, extract_archive, sha256_file
from .translation import (
    GoogleNmtTranslator,
    TranslationError,
    TranslationSummary,
    TranslationStatus,
    translate_dataset,
    translation_status,
    validate_translation,
)
from .usfm import parse_source_directory, validate_bible


def _paths(data_dir: Path) -> tuple[Path, Path, Path, Path]:
    return (
        data_dir / "downloads" / "oicb-usfm.zip",
        data_dir / "extracted" / "oicb",
        database_path("bible.sqlite", data_dir),
        database_path("oicb.sqlite", data_dir),
    )


def _translation_paths(data_dir: Path) -> tuple[Path, Path, Path]:
    return (
        database_path("bible.sqlite", data_dir),
        database_path("oicb.sqlite", data_dir),
        database_path("oicb-google-en.sqlite", data_dir),
    )


def _print_summary(summary: dict[str, int | str]) -> None:
    print(f"Books: {summary['books']}")
    print(f"Chapters: {summary['chapters']}")
    print(f"Verses: {summary['verses']}")
    print(f"Bible database: {summary['bible_database']}")
    print(f"OICB database: {summary['oicb_database']}")
    print(f"Validation: {summary['validation']}")


def _print_translation_status(status: TranslationStatus) -> None:
    print(f"OICB verse count: {status.source_count}")
    print(f"English rows: {status.translated_count}")
    print(f"Completed: {status.completed_count}")
    print(f"Missing: {status.missing_count}")
    print(f"Stale: {status.stale_count}")
    print(f"Orphaned: {status.orphaned_count}")
    print(f"Empty: {status.empty_count}")
    print(f"Total source characters remaining: {status.source_characters_remaining}")


def _print_translation_summary(summary: TranslationSummary, dry_run: bool = False) -> None:
    if dry_run:
        print("Dry run: no Google requests or translation writes.")
    print(f"Planned verses: {summary.planned_count}")
    print(f"Planned source characters: {summary.planned_characters}")
    print(f"Translated verses this run: {summary.translated_this_run}")
    print(f"Characters submitted this run: {summary.characters_submitted_this_run}")
    if summary.stopped_reason:
        print(f"Stopped: {summary.stopped_reason}")
    _print_translation_status(summary.status)


def run_pipeline(data_dir: Path, force_download: bool = False, url: str = OFFICIAL_USFM_URL) -> dict[str, int | str]:
    archive, extraction_root, bible_database, oicb_database = _paths(data_dir)
    digest = download_archive(archive, url=url, force=force_download)
    source_dir = extract_archive(archive, extraction_root)
    data = parse_source_directory(source_dir)
    validate_bible(data)
    summary = build_databases(data, bible_database, oicb_database)
    summary["archive_sha256"] = digest
    return summary


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the OICB SQLite Bible dataset")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="artifact root (default: data)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download = subparsers.add_parser("download", help="download the official OICB USFM ZIP")
    download.add_argument("--url", default=OFFICIAL_USFM_URL)
    download.add_argument("--force", action="store_true", help="replace an existing archive")

    subparsers.add_parser("extract", help="extract the downloaded USFM ZIP")
    subparsers.add_parser("parse", help="parse and summarize extracted USFM")
    subparsers.add_parser("validate", help="parse and validate extracted USFM")

    build = subparsers.add_parser("build", help="parse, validate, and build both SQLite layers")
    build.add_argument("--bible-output", type=Path, default=None)
    build.add_argument("--output", dest="oicb_output", type=Path, default=None, help="OICB edition SQLite path")

    all_command = subparsers.add_parser("all", help="download, extract, validate, and build SQLite")
    all_command.add_argument("--url", default=OFFICIAL_USFM_URL)
    all_command.add_argument("--force", action="store_true", help="replace an existing archive")

    translate = subparsers.add_parser("translate", help="translate eligible OICB verses with Google Cloud")
    translate.add_argument("--canonical", type=Path, default=None, help="canonical bible.sqlite path")
    translate.add_argument("--source", type=Path, default=None, help="source OICB SQLite path")
    translate.add_argument("--output", type=Path, default=None, help="English SQLite path")
    translate.add_argument("--project-id", default=None, help="Google Cloud project (or GOOGLE_CLOUD_PROJECT)")
    translate.add_argument("--location", default="global", help="Cloud Translation location (default: global)")
    translate.add_argument("--max-characters", type=int, default=None, help="maximum input code points submitted this run")
    translate.add_argument("--max-verses", type=int, default=None, help="maximum eligible verses translated this run")
    translate.add_argument("--dry-run", action="store_true", help="plan work without Google requests or SQLite writes")

    for name, help_text in (("translate-status", "show translation checkpoint status"), ("validate-translation", "validate English/OICB alignment")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--canonical", type=Path, default=None, help="canonical bible.sqlite path")
        command.add_argument("--source", type=Path, default=None, help="source OICB SQLite path")
        command.add_argument("--output", type=Path, default=None, help="English SQLite path")

    normalize = subparsers.add_parser(
        "normalize",
        help="inspect supplied text with the auditable orthographic normalizer",
    )
    normalize.add_argument("--text", required=True, help="text to inspect; no edition database is read or written")
    normalize.add_argument("--report", action="store_true", help="print the complete JSON audit report")
    normalize.add_argument(
        "--dry-run",
        action="store_true",
        help="explicitly mark this inspection as dry-run (the command never writes output files)",
    )
    normalize.add_argument("--ruleset", type=Path, default=None, help="optional ruleset JSON path")
    normalize.add_argument("--lexicon", type=Path, default=None, help="optional reviewed lexicon JSON path")
    normalize.add_argument(
        "--expect-sequence",
        action="append",
        default=[],
        metavar="SEQUENCE=COUNT",
        help="source-integrity expectation from an external collation; repeatable",
    )

    rebuild = subparsers.add_parser(
        "rebuild-release",
        help="verify locked sources and reproducibly rebuild the primary databases",
    )
    rebuild.add_argument("edition", choices=("igbob-modern",))
    rebuild.add_argument("--version", required=True)
    rebuild.add_argument("--source-lock", type=Path, default=None)
    rebuild.add_argument("--release-lock", type=Path, default=None)

    backup = subparsers.add_parser(
        "prepare-private-backup",
        help="write a private-file checksum manifest; does not copy or upload files",
    )
    backup.add_argument("--source-lock", type=Path, default=None)
    backup.add_argument("--output", type=Path, default=None)
    return parser


def _expected_sequences(values: list[str]) -> tuple[tuple[str, int], ...]:
    parsed = []
    for value in values:
        sequence, separator, raw_count = value.rpartition("=")
        if not separator or not sequence:
            raise SystemExit(f"invalid --expect-sequence {value!r}; expected SEQUENCE=COUNT")
        try:
            count = int(raw_count)
        except ValueError as exc:
            raise SystemExit(f"invalid --expect-sequence count in {value!r}") from exc
        if count < 0:
            raise SystemExit("--expect-sequence count must be non-negative")
        parsed.append((sequence, count))
    return tuple(parsed)


def main(argv: list[str] | None = None) -> int:
    load_repository_env()
    args = make_parser().parse_args(argv)
    if args.command == "normalize":
        from .normalization import Normalizer, SourceIntegrityProfile

        options = {}
        if args.ruleset is not None:
            options["ruleset_path"] = args.ruleset
        if args.lexicon is not None:
            options["lexicon_path"] = args.lexicon
        result = Normalizer(**options).normalize(
            args.text,
            source_profile=SourceIntegrityProfile(
                expected_minimum_sequences=_expected_sequences(args.expect_sequence),
                profile_id="cli-expectation",
            ) if args.expect_sequence else None,
        )
        if args.report:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(result.normalized_text)
        return 0

    if args.command in {"rebuild-release", "prepare-private-backup"}:
        from .release import ReleaseError, prepare_private_backup_manifest, rebuild_release

        source_lock = args.source_lock or args.data_dir / "sources" / "source-lock.json"
        try:
            if args.command == "rebuild-release":
                release_lock = args.release_lock or args.data_dir / "releases" / f"igbob-modern-v{args.version}.json"
                result = rebuild_release(args.data_dir, source_lock, release_lock, args.version)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            output = args.output or args.data_dir / "generated" / "private-backup-manifest.json"
            manifest = prepare_private_backup_manifest(args.data_dir, source_lock, output)
            print(f"Private backup manifest: {output}")
            print(f"Required files present: {sum(item['status'] == 'present' and item['required'] for item in manifest['files'])}")
            print(f"Required files missing: {len(manifest['missing_required_paths'])}")
            print("Bundle complete: " + ("yes" if manifest["complete"] else "no"))
            return 0
        except ReleaseError as exc:
            print(f"Release error: {exc}", file=sys.stderr)
            return 2

    archive, extraction_root, bible_database, oicb_database = _paths(args.data_dir)
    if args.command == "download":
        digest = download_archive(archive, url=args.url, force=args.force)
        print(f"Archive: {archive}")
        print(f"SHA-256: {digest}")
        return 0
    if args.command == "extract":
        print(f"USFM directory: {extract_archive(archive, extraction_root)}")
        return 0

    if args.command in {"parse", "validate", "build"}:
        source_dir = next(extraction_root.rglob("*.usfm"), None)
        if source_dir is None:
            raise SystemExit("no extracted USFM found; run download and extract first")
        data = parse_source_directory(source_dir.parent)
        if args.command == "parse":
            print(f"Books: {len(data.books)}")
            print(f"Chapters: {len(data.chapters)}")
            print(f"Verses: {len(data.verses)}")
            print(f"Source verse markers: {data.source_verse_count}")
            return 0
        validate_bible(data)
        if args.command == "validate":
            print(f"Validation: PASS ({len(data.books)} books, {len(data.chapters)} chapters, {len(data.verses)} verses)")
            return 0
        summary = build_databases(data, args.bible_output or bible_database, args.oicb_output or oicb_database)
        _print_summary(summary)
        return 0

    if args.command in {"translate", "translate-status", "validate-translation"}:
        canonical_db, source_db, translation_db = _translation_paths(args.data_dir)
        canonical_db = args.canonical or canonical_db
        source_db = args.source or source_db
        translation_db = args.output or translation_db
        try:
            if args.command == "translate-status":
                _print_translation_status(translation_status(source_db, translation_db, canonical_db))
                return 0
            if args.command == "validate-translation":
                status = validate_translation(source_db, translation_db, canonical_db)
                _print_translation_status(status)
                print("Validation: PASS")
                return 0

            if args.dry_run:
                translator = None
            else:
                translator = GoogleNmtTranslator(project_id=args.project_id, location=args.location)

            def progress(translated: int, remaining: int, characters: int, source_remaining: int) -> None:
                print(
                    f"translated verses: {translated}; remaining verses: {remaining}; "
                    f"characters submitted this run: {characters}; "
                    f"total source characters remaining: {source_remaining}",
                    flush=True,
                )

            summary = translate_dataset(
                source_db,
                translation_db,
                translator,
                canonical_path=canonical_db,
                max_characters=args.max_characters,
                max_verses=args.max_verses,
                dry_run=args.dry_run,
                progress=progress,
            )
            _print_translation_summary(summary, dry_run=args.dry_run)
            return 0
        except KeyboardInterrupt:
            print("Interrupted; completed batches remain checkpointed for resume.", file=sys.stderr)
            return 130
        except TranslationError as exc:
            print(f"Translation error: {exc}", file=sys.stderr)
            return 2

    summary = run_pipeline(args.data_dir, force_download=args.force, url=args.url)
    _print_summary(summary)
    print(f"Archive SHA-256: {summary['archive_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

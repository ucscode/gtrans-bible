"""Standalone command for local historical Igbo corpus analysis.

It never imports the production parser, database builder, or translation
pipeline. All output is confined to the ignored ``data/research`` tree.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

from .config import load_repository_env, repository_root
from .research import (
    DEFAULT_IA_OCR_URL,
    DEFAULT_RESEARCH_ROOT,
    analyze_source,
    copy_research_source,
    corpus_report_lines,
    fetch_research_source,
    validate_research_output,
    write_reports,
)


def _safe_source_label(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.netloc}{parsed.path}"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze an OCR corpus locally; output is research-only, never edition data."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--source", type=Path, help="existing DjVu XML or plain-text OCR file")
    source.add_argument(
        "--url",
        default=None,
        help="OCR URL (default: IGBO_RESEARCH_SOURCE_URL or the public Internet Archive OCR XML)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESEARCH_ROOT / "igbo-union" / "reports",
        help="report directory, required to stay under data/research",
    )
    parser.add_argument("--force", action="store_true", help="replace cached OCR when downloading/copying")
    return parser


def main(argv: list[str] | None = None) -> int:
    load_repository_env()
    args = make_parser().parse_args(argv)
    root = repository_root()
    try:
        report_dir = validate_research_output(args.output_dir, root)
        data_root = (root / DEFAULT_RESEARCH_ROOT / "igbo-union" / "source").resolve()
        data_root.mkdir(parents=True, exist_ok=True)

        if args.source is not None:
            extension = ".xml" if args.source.suffix.lower() == ".xml" else ".txt"
            source_path = data_root / f"union-igbo-ocr{extension}"
            digest = copy_research_source(args.source, source_path, force=args.force)
            source_label = args.source.name
        else:
            url = args.url or os.environ.get("IGBO_RESEARCH_SOURCE_URL") or DEFAULT_IA_OCR_URL
            source_path = data_root / "union-igbo-ocr.xml"
            digest = fetch_research_source(url, source_path, force=args.force)
            source_label = _safe_source_label(url)

        result = analyze_source(source_path, source_url=source_label)
        if result["source"]["sha256"] != digest:
            raise RuntimeError("research OCR changed while it was being analyzed")
        write_reports(result, report_dir)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Research analysis failed: {error}", file=sys.stderr)
        return 2

    print("Research-only source; do not redistribute or use as edition database input.")
    print(f"Report directory: {report_dir}")
    for line in corpus_report_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

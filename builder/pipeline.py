"""Download and extraction steps for the OICB source archive."""

from __future__ import annotations

import hashlib
import os
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from .books import CANONICAL_BOOK_CODES
from .usfm import ParseError


OFFICIAL_SOURCE_PAGE = "https://www.open.bible/bibles/igbo-biblica-text-bible"
OFFICIAL_USFM_URL = "https://openbible-api-1.biblica.com/artifactContent/64c02602a4e86765a266c7a4"


def download_archive(destination: Path, url: str = OFFICIAL_USFM_URL, force: bool = False) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return sha256_file(destination)

    request = urllib.request.Request(url, headers={"User-Agent": "oicb-builder/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=destination.parent, prefix=".oicb-") as handle:
            temporary = Path(handle.name)
            try:
                while chunk := response.read(1024 * 1024):
                    handle.write(chunk)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    os.replace(temporary, destination)
    return sha256_file(destination)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_archive(archive: Path, destination: Path) -> Path:
    if not archive.exists():
        raise FileNotFoundError(f"archive not found: {archive}; run download first")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        for member in members:
            target = (destination / member.filename).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise ParseError(f"unsafe archive path: {member.filename}")
        bundle.extractall(destination)

    candidates = []
    for path in destination.rglob("*.usfm"):
        candidates.append(path.parent)
    unique_candidates = sorted(set(candidates))
    if len(unique_candidates) != 1:
        raise ParseError(f"expected one USFM directory, found {unique_candidates}")
    source_dir = unique_candidates[0]
    codes = {path.stem for path in source_dir.glob("*.usfm")}
    if codes != set(CANONICAL_BOOK_CODES):
        raise ParseError("extracted archive does not contain the expected OICB 66-book USFM set")
    return source_dir

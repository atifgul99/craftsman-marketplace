#!/usr/bin/env python3
"""
PDF Extractor — auto-fallback PDF reader for the tax skill.

Tries pdftotext first (works for text PDFs like TurboTax exports, bank statements,
e-filed returns). If that fails or returns sparse text, rasterizes pages to PNG
so they can be read by Claude's built-in Read tool (vision) for form images
like scanned IRS letters, hand-completed 8822-B, check images, etc.

Usage as a module:
    from pdf_extract import extract
    result = extract("/path/to/file.pdf")
    if result.mode == "text":
        text = result.text
    else:
        png_paths = result.pngs  # list of PNG file paths ready for Read tool

Usage as a CLI:
    python3 pdf_extract.py <file.pdf>                 # auto fallback
    python3 pdf_extract.py <file.pdf> --force-image   # skip text, go to PNG
    python3 pdf_extract.py <file.pdf> --pages 1-3     # specific pages
    python3 pdf_extract.py <file.pdf> --dpi 300       # higher res for scans

Output (CLI): prints either extracted text OR a list of PNG paths to read.

Dependencies (cross-platform):
- pdftotext (poppler)
- pdftoppm (same package)

  macOS: brew install poppler | Debian/Ubuntu: apt install poppler-utils
  Fedora: dnf install poppler-utils | Windows: choco install poppler

No Python package installs required. If you later need OCR without vision,
install ocrmypdf (which wraps tesseract) and use it separately.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Minimum character count to consider pdftotext output "meaningful".
# Short PDFs still beat this. Empty or trivially-small output triggers fallback.
MIN_TEXT_CHARS = 50

# Density of non-whitespace text per kilobyte of file — below this suggests an
# image-heavy PDF that pdftotext failed on.
MIN_DENSITY_CHARS_PER_KB = 5


@dataclass
class ExtractResult:
    """Unified result of a PDF extraction attempt."""
    mode: str  # "text" | "image" | "failed"
    text: Optional[str] = None
    pngs: list[str] = field(default_factory=list)
    pages_rasterized: Optional[str] = None  # e.g., "1-3" or "all"
    pdf_path: str = ""
    diagnostics: dict = field(default_factory=dict)


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def _have(binary: str) -> bool:
    return shutil.which(binary) is not None


def try_pdftotext(pdf_path: Path) -> Optional[str]:
    """Attempt text extraction. Return None if unavailable or clearly empty."""
    if not _have("pdftotext"):
        return None
    try:
        proc = _run(["pdftotext", "-layout", str(pdf_path), "-"], check=False)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    text = proc.stdout
    # Heuristic: treat as "empty" if fewer than MIN_TEXT_CHARS of non-whitespace
    non_ws = len(re.sub(r"\s+", "", text))
    if non_ws < MIN_TEXT_CHARS:
        return None
    # Density check — compare to file size
    try:
        size_kb = max(1, pdf_path.stat().st_size // 1024)
    except OSError:
        size_kb = 1
    if non_ws / size_kb < MIN_DENSITY_CHARS_PER_KB:
        # Sparse text vs file size suggests image-heavy PDF; fall back to image
        return None
    return text


def parse_page_range(pages: str, total: int) -> list[int]:
    """Parse '1-3,5,7-9' into [1,2,3,5,7,8,9]. If pages is None or 'all', return range(1, total+1).

    Raises ValueError with a clear message if `pages` is malformed (non-numeric,
    empty range segment, etc.) — callers should catch this and report cleanly
    rather than let a bare traceback surface.
    """
    if not pages or pages == "all":
        return list(range(1, total + 1))
    out: list[int] = []
    for part in pages.split(","):
        part = part.strip()
        if not part:
            raise ValueError(f"Malformed --pages value {pages!r}: empty segment between commas")
        try:
            if "-" in part:
                a, b = part.split("-", 1)
                out.extend(range(int(a), int(b) + 1))
            else:
                out.append(int(part))
        except ValueError as e:
            raise ValueError(
                f"Malformed --pages value {pages!r}: could not parse segment {part!r} ({e})"
            ) from e
    return sorted(set(out))


def pdf_page_count(pdf_path: Path) -> int:
    """Return page count using pdfinfo. Returns -1 if unavailable."""
    if not _have("pdfinfo"):
        return -1
    try:
        proc = _run(["pdfinfo", str(pdf_path)], check=False)
    except Exception:
        return -1
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return -1
    return -1


def rasterize_to_png(pdf_path: Path, out_dir: Path, pages: str = "all", dpi: int = 200) -> list[Path]:
    """Rasterize PDF pages to PNG. Returns list of PNG paths in page order."""
    if not _have("pdftoppm"):
        raise RuntimeError("pdftoppm not found — install poppler (poppler-utils).")

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / f"{pdf_path.stem}"

    # Determine page range
    total = pdf_page_count(pdf_path)
    if total < 0:
        total = 50  # fallback upper bound; pdftoppm handles gracefully
    page_list = parse_page_range(pages, total)

    # pdftoppm -png writes <prefix>-<n>.png directly — no separate convert step,
    # which also keeps this cross-platform (the old sips path was macOS-only).
    if page_list:
        first = min(page_list)
        last = max(page_list)
        try:
            _run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(first), "-l", str(last), str(pdf_path), str(prefix)])
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or "").strip()
            raise RuntimeError(
                f"pdftoppm failed on {pdf_path} (possibly corrupt or password-protected PDF)"
                + (f": {stderr}" if stderr else "")
            ) from e

    # Collect only the pages that were requested
    png_paths: list[Path] = []
    for png in sorted(out_dir.glob(f"{pdf_path.stem}-*.png")):
        # Extract page number from filename suffix, e.g. "<prefix>-03"
        try:
            pno = int(png.stem.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            continue
        if pno not in page_list:
            continue
        png_paths.append(png)

    return sorted(png_paths, key=lambda p: int(p.stem.rsplit("-", 1)[1]))


def extract(
    pdf_path: str | Path,
    *,
    force_image: bool = False,
    pages: str = "all",
    dpi: int = 200,
    out_dir: Optional[str | Path] = None,
) -> ExtractResult:
    """
    Extract content from a PDF with automatic fallback.

    Try order:
      1. `pdftotext -layout` — returns text if meaningful content.
      2. Rasterize to PNG — for image-based PDFs or when force_image=True.

    Parameters
    ----------
    pdf_path : path to the PDF
    force_image : skip text extraction, go straight to rasterization
    pages : "all" or "1-3,5,7-9" style range
    dpi : resolution for rasterization (200 is typical; 300 for small-print scans)
    out_dir : where to place PNG files (default: system tmp)

    Returns
    -------
    ExtractResult with:
      - mode="text" and .text populated, OR
      - mode="image" and .pngs listing PNG paths to feed into Read tool, OR
      - mode="failed" with diagnostics (no content extractable)
    """
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.is_file():
        return ExtractResult(mode="failed", pdf_path=str(pdf_path),
                             diagnostics={"error": "file not found"})

    result = ExtractResult(pdf_path=str(pdf_path), mode="failed")

    # Step 1: try text
    if not force_image:
        text = try_pdftotext(pdf_path)
        if text:
            result.mode = "text"
            result.text = text
            result.diagnostics["text_chars"] = len(text)
            return result

    # Step 2: rasterize
    if out_dir is None:
        out_dir_p = Path(tempfile.mkdtemp(prefix="pdfextract_"))
    else:
        out_dir_p = Path(out_dir)
    try:
        pngs = rasterize_to_png(pdf_path, out_dir_p, pages=pages, dpi=dpi)
    except (RuntimeError, ValueError) as e:
        result.diagnostics["rasterize_error"] = str(e)
        return result

    if not pngs:
        result.diagnostics["error"] = "rasterization produced no images"
        return result

    result.mode = "image"
    result.pngs = [str(p) for p in pngs]
    result.pages_rasterized = pages
    result.diagnostics["png_count"] = len(pngs)
    result.diagnostics["dpi"] = dpi
    result.diagnostics["out_dir"] = str(out_dir_p)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract text or PNG images from a PDF with auto-fallback.")
    ap.add_argument("pdf", help="Path to PDF file")
    ap.add_argument("--force-image", action="store_true", help="Skip text extraction, go straight to PNG")
    ap.add_argument("--pages", default="all", help="'all' or range like '1-3,5,7-9' (default: all)")
    ap.add_argument("--dpi", type=int, default=200, help="Rasterization DPI (default 200)")
    ap.add_argument("--out-dir", default=None, help="PNG output directory (default: tmp)")
    args = ap.parse_args()

    try:
        parse_page_range(args.pages, total=1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    result = extract(args.pdf, force_image=args.force_image, pages=args.pages,
                     dpi=args.dpi, out_dir=args.out_dir)

    if result.mode == "text":
        sys.stdout.write(result.text or "")
        return 0
    if result.mode == "image":
        print(f"# pdftotext failed / force_image — rasterized to PNG ({len(result.pngs)} pages)", file=sys.stderr)
        for png in result.pngs:
            print(png)
        print(f"# Feed each PNG path above into Claude's Read tool to extract content via vision.", file=sys.stderr)
        return 0

    print(f"# Extraction failed: {result.diagnostics}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
compare — differential extraction (Layer A of the confidence system).

Runs the same PDF through several INDEPENDENT text extractors and reports
where they disagree about the dollar figures on the page. Agreement is weak
evidence of correctness; disagreement is strong evidence that a human (or a
vision pass) needs to look.

This deliberately does not decide who is right. It narrows a whole document
down to the handful of figures worth checking by hand.

Engines (each skipped silently if unavailable):
  - pdftotext -layout   preserves column geometry
  - pdftotext -raw      different reading order, no layout reconstruction
  - pdfplumber          separate library, separate PDF parser

A fourth opinion — vision on the rasterized page — cannot run headless.
Use `--pngs` to get page images to read back through the model, then pass
the figures you read via `--expect`.

Usage:
    python3 compare.py <file.pdf>
    python3 compare.py <file.pdf> --json
    python3 compare.py <file.pdf> --expect 58192 --expect -4168
    python3 compare.py <file.pdf> --pngs        # also rasterize for a vision pass

Exit codes:
    0 = all available engines agree (and any --expect values were found)
    1 = disagreement, or an --expect value is missing
    2 = usage/IO error, or fewer than two engines available

Pure stdlib except the optional pdfplumber probe. Never modifies the PDF.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

# A "money-like" token: requires a currency marker, comma grouping, or two
# decimal places. Bare integers are excluded on purpose — page numbers, box
# numbers, and years would otherwise swamp the signal.
MONEY = re.compile(r"""
    (?P<paren>\()?
    \$?\s*
    (?P<body>
        \d{1,3}(?:,\d{3})+(?:\.\d{1,2})?     # comma-grouped: 58,192 / 1,234.56
      | \d+\.\d{2}                            # explicit cents: 1234.56
      | \$\s*\d+                              # dollar-marked integer: $500
    )
    (?P<close>\))?
""", re.VERBOSE)


def to_amount(m: re.Match) -> float | None:
    body = m.group("body").replace(",", "").replace("$", "").strip()
    try:
        v = float(body)
    except ValueError:
        return None
    # Accounting negatives: (1,234) means -1234
    if m.group("paren") and m.group("close"):
        v = -v
    return v


def amounts(text: str) -> Counter:
    out: Counter = Counter()
    for m in MONEY.finditer(text):
        v = to_amount(m)
        if v is not None:
            out[round(v, 2)] += 1
    return out


def _have(binary: str) -> bool:
    return shutil.which(binary) is not None


def engine_pdftotext(pdf: Path, mode: str) -> str | None:
    if not _have("pdftotext"):
        return None
    cmd = ["pdftotext"]
    if mode:
        cmd.append(mode)
    cmd += [str(pdf), "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, OSError):
        return None
    return r.stdout


def engine_pdfplumber(pdf: Path) -> str | None:
    probe = subprocess.run(
        [sys.executable, "-c",
         "import pdfplumber,sys;"
         "print('\\n'.join((p.extract_text() or '') "
         "for p in pdfplumber.open(sys.argv[1]).pages))", str(pdf)],
        capture_output=True, text=True)
    if probe.returncode != 0:
        return None
    return probe.stdout


def run_engines(pdf: Path) -> dict[str, Counter]:
    raw = {
        "pdftotext -layout": engine_pdftotext(pdf, "-layout"),
        "pdftotext -raw": engine_pdftotext(pdf, "-raw"),
        "pdfplumber": engine_pdfplumber(pdf),
    }
    return {name: amounts(text) for name, text in raw.items()
            if text is not None and text.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compare dollar figures across independent PDF text extractors.")
    ap.add_argument("pdf")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--expect", action="append", default=[],
                    help="a figure that must appear (repeatable); e.g. --expect -4168")
    ap.add_argument("--pngs", action="store_true",
                    help="also rasterize pages, for a vision pass as a further opinion")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"no such file: {pdf}", file=sys.stderr)
        return 2

    results = run_engines(pdf)
    if len(results) < 2:
        got = ", ".join(results) or "none"
        print(f"need at least two engines to compare; available: {got}", file=sys.stderr)
        print("install poppler and/or pdfplumber", file=sys.stderr)
        return 2

    sets = {name: set(c) for name, c in results.items()}
    consensus = set.intersection(*sets.values())
    union = set.union(*sets.values())
    disputed = union - consensus

    # Which engines saw each disputed figure — that is the actionable part.
    disputed_detail = {
        f"{v:,.2f}": sorted(n for n in sets if v in sets[n])
        for v in sorted(disputed)
    }

    missing_expected: list[str] = []
    for e in args.expect:
        try:
            want = round(float(str(e).replace(",", "").replace("$", "")), 2)
        except ValueError:
            print(f"--expect value not numeric: {e}", file=sys.stderr)
            return 2
        if want not in union:
            missing_expected.append(f"{want:,.2f}")

    pngs: list[str] = []
    if args.pngs:
        try:
            from pdf_extract import rasterize_to_png  # local module
            import tempfile
            pngs = [str(p) for p in rasterize_to_png(pdf, Path(tempfile.mkdtemp()))]
        except Exception as exc:  # rasterization is a convenience, not the point
            print(f"rasterization skipped: {exc}", file=sys.stderr)

    ok = not disputed and not missing_expected

    if args.json:
        print(json.dumps({
            "pdf": str(pdf),
            "engines": sorted(results),
            "consensus_count": len(consensus),
            "disputed": disputed_detail,
            "missing_expected": missing_expected,
            "pngs": pngs,
            "agree": ok,
        }, indent=2))
        return 0 if ok else 1

    print(f"compare — {pdf.name}")
    print(f"engines: {', '.join(sorted(results))}")
    print(f"figures agreed by all engines: {len(consensus)}\n")

    if disputed_detail:
        print(f"{len(disputed_detail)} disputed figure(s) — each seen by some engines, not all:\n")
        for val, seen in disputed_detail.items():
            missing = sorted(set(results) - set(seen))
            print(f"  {val:>16}   seen by: {', '.join(seen)}")
            print(f"  {'':>16}   missed by: {', '.join(missing)}")
        print("\nA figure only one engine sees is usually a layout artifact — but if it is a")
        print("box value you intend to rely on, read it off the page image before using it.")
    else:
        print("No disagreement between engines.")

    if missing_expected:
        print(f"\nEXPECTED BUT NOT FOUND by any engine: {', '.join(missing_expected)}")

    if pngs:
        print(f"\nPage images for a vision pass ({len(pngs)}):")
        for p in pngs:
            print(f"  {p}")

    print("\nAgreement is not proof. Layer B (tools/parse-verify) checks whether the")
    print("figures can be internally consistent at all.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

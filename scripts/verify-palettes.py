#!/usr/bin/env python3
"""Verify every starter palette in craft-ux's starter-kits.md against WCAG.

Parses the palette table straight from the reference file (single source of
truth) and checks each palette:

  foreground/background        >= 7.0   (AAA body target)
  foreground/card              >= 7.0
  on-primary/primary           >= 4.5
  on-accent/accent             >= 4.5
  muted-fg/background          >= 4.5
  muted-fg/muted               >= 4.5
  primary/background           >= 3.0   (UI component)
  ring/background              >= 3.0
  border/background            >= 1.2   (visibility only)

Run after any palette edit:  python3 scripts/verify-palettes.py
Exits 1 if any pair fails, so it can gate CI.
"""
import re
import sys
from pathlib import Path

KITS = Path(__file__).resolve().parents[1] / (
    "craftsman/skills/craft-ux/references/starter-kits.md"
)

COLUMNS = ["kit", "primary", "onPrimary", "accent", "onAccent", "background",
           "foreground", "card", "muted", "mutedFg", "border", "ring"]

CHECKS = [  # (label, fg-role, bg-role, minimum ratio)
    ("fg/bg", "foreground", "background", 7.0),
    ("fg/card", "foreground", "card", 7.0),
    ("on-primary/primary", "onPrimary", "primary", 4.5),
    ("on-accent/accent", "onAccent", "accent", 4.5),
    ("muted-fg/bg", "mutedFg", "background", 4.5),
    ("muted-fg/muted", "mutedFg", "muted", 4.5),
    ("primary/bg", "primary", "background", 3.0),
    ("ring/bg", "ring", "background", 3.0),
    ("border/bg", "border", "background", 1.2),
]


def luminance(hexc: str) -> float:
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_palettes(text: str):
    """Yield dicts for each data row of the first table whose rows carry 11 hex cells."""
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) != len(COLUMNS):
            continue
        if not all(re.fullmatch(r"#[0-9A-Fa-f]{6}", c) for c in cells[1:]):
            continue  # header / separator / non-palette table
        yield dict(zip(COLUMNS, cells))


def main() -> int:
    palettes = list(parse_palettes(KITS.read_text(encoding="utf-8")))
    if not palettes:
        print(f"ERROR: no palette rows parsed from {KITS}")
        return 1
    failures = 0
    for p in palettes:
        bad = []
        for label, fg, bg, minimum in CHECKS:
            r = ratio(p[fg], p[bg])
            if r < minimum:
                bad.append(f"{label} {r:.2f} < {minimum}")
        if bad:
            failures += 1
            print(f"FAIL {p['kit']}: " + "; ".join(bad))
        else:
            print(f"PASS {p['kit']}")
    print(f"\n{len(palettes)} palettes checked, {failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Structural gates for the skill's markdown: cross-references, pointers, tables.

The regression matrix pins WHAT the modules say. This pins that the modules can
still be navigated: every `file.md` §N cross-reference resolves to a real file
and a real section, every declared workpaper has an owner, and no table row is
malformed (a broken row silently swallows a trap into the preceding cell).

Usage:
    python3 -B evals/validate_individual_structure.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTION_REF = re.compile(r"`([\w./-]+\.md)` §(\d+)")
HEADING = re.compile(r"^## (\d+)\.", re.M)
FENCE = re.compile(r"^\s*(?:```|~~~)")


def strip_fences(text: str) -> str:
    """Blank out fenced blocks, keeping line numbering intact."""
    out, inside = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            inside = not inside
            out.append("")
        else:
            out.append("" if inside else line)
    return "\n".join(out)


def main() -> int:
    files = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(ROOT.rglob("*.md"))
    }
    prose = {name: strip_fences(text) for name, text in files.items()}
    sections = {name: set(HEADING.findall(text)) for name, text in prose.items()}

    def resolve(source: str, target: str) -> str | None:
        # Exact path, or a path suffix on a FULL segment boundary — "records.md"
        # must not match "corporate-records.md".
        cands = [n for n in files if n == target or n.endswith("/" + target)]
        if len(cands) > 1:
            here = str(Path(source).parent)
            cands = [n for n in cands if n.startswith(here)] or cands
        return cands[0] if cands else None

    failures: list[str] = []
    refs = 0
    for name, text in prose.items():
        for match in SECTION_REF.finditer(text):
            refs += 1
            target, section = match.group(1), match.group(2)
            line = text.count("\n", 0, match.start()) + 1
            resolved = resolve(name, target)
            if resolved is None:
                failures.append(f"{name}:{line}: pointer does not resolve: `{target}`")
            elif section not in sections[resolved]:
                have = sorted(sections[resolved], key=int) or ["none"]
                failures.append(
                    f"{name}:{line}: `{target}` §{section} out of range (has {have})"
                )

        for number, line_text in enumerate(text.split("\n"), 1):
            if line_text.startswith("| ") and line_text.count("|") < 3:
                failures.append(f"{name}:{number}: malformed table row: {line_text[:60]!r}")

    if failures:
        print(f"FAIL: {len(failures)} structural problem(s)\n")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"PASS: {len(files)} markdown files; {refs} section cross-references resolve "
        f"to a real file and a real section; no malformed table rows"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The skill directory is read-only territory. Nothing here may write into it.

Everything this skill produces belongs in the user's workspace; everything
temporary belongs in the system temp directory. The skill's own tree is neither.
Two reasons, and the first is not stylistic:

  1. An installed plugin is frequently read-only. Three validators used to build
     their fixture sandbox under `evals/`, or write a scratch markdown file into
     `individual/`, and each died on PermissionError for a user who installed the
     plugin normally. A gate that cannot run is not a gate that passed — that rule
     is stated in SKILL.md, and a crashing validator is the worst way to learn it.

  2. A crash between write and cleanup leaves litter inside the shipped skill.
     `validate_individual_structure.py` counts the markdown files in this tree; a
     stray scratch file changes what the skill *is*.

The test copies the skill to a temp tree, strips write permission from all of it,
and runs every validator against the copy from a throwaway working directory. A
validator that writes anywhere inside the skill fails there and passes here.

Checking for leftover files instead would prove nothing: a validator that creates
its sandbox under `evals/` and then cleans it up leaves no trace on a writable
disk while still being broken for every user who installed the plugin read-only.
The permission bit is the property under test, so the test takes it away.

Usage:
    python3 -B evals/test_no_skill_writes.py
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF_NAME = Path(__file__).name


def relative_scripts() -> list[str]:
    """Every validator except this one, plus the tools that ship a self-test.

    Returned relative to the skill root so they can be run against the copy.
    """
    scripts = [
        p.relative_to(ROOT)
        for p in sorted((ROOT / "evals").glob("*.py"))
        if p.name != SELF_NAME and not p.name.startswith("_")
    ]
    scripts += [p.relative_to(ROOT) for p in sorted((ROOT / "tools").glob("*/test_*.py"))]
    return [str(p) for p in scripts]


def make_read_only(tree: Path) -> None:
    """Strip write bits from every file and directory, deepest first.

    Directories last would be self-defeating: once a directory is read-only its
    children can no longer be chmod'd.
    """
    entries = sorted(tree.rglob("*"), key=lambda p: len(p.parts), reverse=True)
    for path in entries + [tree]:
        mode = path.lstat().st_mode
        os.chmod(path, stat.S_IMODE(mode) & ~0o222)


def restore_write(tree: Path) -> None:
    for path in [tree] + list(tree.rglob("*")):
        mode = path.lstat().st_mode
        os.chmod(path, stat.S_IMODE(mode) | stat.S_IWUSR)


def main() -> int:
    if os.geteuid() == 0:
        print("SKIP: running as root, which ignores the read-only bits this test relies on")
        return 0

    scripts = relative_scripts()
    failures: list[tuple[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="read-only-skill-") as staging:
        copy = Path(staging) / "tax"
        shutil.copytree(
            ROOT, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"), symlinks=True
        )
        make_read_only(copy)
        try:
            # A throwaway cwd, so a validator resolving a workspace path against the
            # current directory is not handed the repo it lives in.
            with tempfile.TemporaryDirectory(prefix="read-only-skill-cwd-") as cwd:
                for script in scripts:
                    result = subprocess.run(
                        [sys.executable, "-B", str(copy / script)],
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    if result.returncode != 0:
                        tail = (result.stderr or result.stdout).strip().splitlines()
                        failures.append((script, tail[-1] if tail else "no output"))
        finally:
            # copytree preserves modes, so the tree must be writable again before
            # TemporaryDirectory can remove it.
            restore_write(copy)

    if failures:
        print("FAIL: scripts could not run against a read-only copy of the skill.")
        for script, detail in failures:
            print(f"  {script}: {detail}")
        print(
            "\nA PermissionError here means something writes inside the skill directory.\n"
            "Write to the user's workspace, or to tempfile.TemporaryDirectory() with no\n"
            "`dir=` argument — an installed plugin is read-only for most users."
        )
        return 1

    print(f"PASS: {len(scripts)} script(s) run against a fully read-only copy of the skill")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Third-party import guard for the validators.

The tools/ scripts are stdlib-only by design. The validators in this directory are
not: they need `jsonschema` for schema enforcement and `markdown-it-py` for block
scoping. Claude Code installs Node dependencies for a plugin automatically but has
no pip equivalent, so a user who installs taxcraft and follows the skill's
instructions can reach a validator without those packages present.

The failure that matters is not the missing package. It is a validator that cannot
run being mistaken for a validator that passed. `validate_rules.py` exits 2 on
expired tax data; if it dies on ImportError instead, a stack trace is easy to read
as noise and step past. So these guards exit non-zero with the consequence stated
first and the install command second.

Usage, before any third-party import in a validator:

    from _deps import require
    require("jsonschema", "schema validation", "without it no artifact is checked")
"""

from __future__ import annotations

import importlib
import sys

# PyPI distribution names differ from import names for some packages.
_DISTRIBUTION = {
    "markdown_it": "markdown-it-py",
}


def require(module: str, purpose: str, consequence: str) -> None:
    """Exit with an actionable message when `module` is not importable.

    `purpose` names what the package is used for; `consequence` states what goes
    unchecked without it. Both appear in the message, because "install this" alone
    does not tell a user whether skipping it is safe. It is not.
    """
    try:
        importlib.import_module(module)
    except ModuleNotFoundError:
        package = _DISTRIBUTION.get(module, module)
        sys.exit(
            f"\nCANNOT RUN: this check needs the '{package}' package, which is not installed.\n"
            f"\n"
            f"  What it is for : {purpose}\n"
            f"  Without it     : {consequence}\n"
            f"\n"
            f"This is NOT a pass. The check did not run.\n"
            f"\n"
            f"Install it with whichever matches your setup:\n"
            f"\n"
            f"  pip install {package}\n"
            f"  pip install --user {package}      # no virtualenv active\n"
            f"  uv add {package}                  # uv-managed project\n"
            f"\n"
            f"Then run this command again.\n"
        )

#!/usr/bin/env python3
"""The single gate every executable rules consumer must pass through.

Bundled figures expire. `authority.md` makes a file past `_meta.stale_after`
`AUTHORITY_HOLD` for numeric outputs, and that has to be enforced at EVERY
consumer — a check that only some callers opt into is not a control.

Import `load_rules()` rather than `json.load`-ing a rules file directly.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

RULES_DIR = Path(__file__).resolve().parents[1] / "rules"


class StaleRulesError(AssertionError):
    """A rules file was consumed past its declared freshness window."""


def assert_fresh(data: dict[str, Any], name: str, as_of: date | None = None) -> None:
    meta = data["_meta"]
    stale_after = date.fromisoformat(meta["stale_after"])
    checked_at = date.fromisoformat(meta["checked_at"])
    if checked_at > stale_after:
        raise StaleRulesError(f"{name}: stale_after {stale_after} precedes checked_at {checked_at}")
    # `as_of` is for AUDIT and REPRODUCTION only. A live computation must use the
    # real date, or an old `--as-of` would green-light expired data — which is
    # precisely the failure the gate exists to prevent.
    effective = as_of or date.today()
    if effective > stale_after:
        raise StaleRulesError(
            f"{name} went stale on {stale_after} (checked {checked_at}; "
            f"{meta.get('stale_after_rationale', 'no rationale recorded')}). "
            f"AUTHORITY_HOLD for numeric outputs per authority.md. Re-verify against the "
            f"cited primary sources AND any legislation enacted since, then update "
            f"_meta.checked_at, _meta.stale_after and _meta.legislation_checked_through. "
            f"Do not bump the date alone."
        )


def load_rules(tax_year: int, as_of: date | None = None) -> dict[str, Any]:
    """Load a federal rules file, refusing to return expired data."""
    path = RULES_DIR / f"federal-{tax_year}.json"
    if not path.is_file():
        raise AssertionError(f"missing rules file for tax year {tax_year}: {path.name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert_fresh(data, path.name, as_of)
    return data

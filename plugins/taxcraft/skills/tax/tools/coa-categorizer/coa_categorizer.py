#!/usr/bin/env python3
"""Chart-of-Accounts categorizer.

Applies rule-based GL bucket classification to transaction rows produced by
chase-statement-parser (or any CSV with a `description` and `amount` column).

Library usage:
    from coa_categorizer import categorize, load_rules
    rules = load_rules("default_rules.json")
    enriched = categorize(rows, rules)

CLI usage:
    python3 coa_categorizer.py input.csv [--rules custom.json]
                                         [--output out.csv]
                                         [--reclassify]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


NEW_COLS = ["gl_account", "gl_code", "confidence", "needs_review"]


def load_rules(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text())
    return data["rules"]


def match_rule(description: str, rules: list[dict]):
    """Return (gl_account, gl_code, confidence) or (None, None, None)."""
    up = (description or "").upper()
    for r in rules:
        if r["match"].upper() in up:
            return r["gl_account"], r.get("gl_code", ""), r.get("confidence", "medium")
    return None, None, None


def _truthy(val) -> bool:
    if val is None:
        return False
    s = str(val).strip().lower()
    return s not in ("", "false", "0", "none", "null")


def categorize(
    rows: Iterable[dict],
    rules: list[dict],
    existing_gl_col: str = "gl_account",
    reclassify: bool = False,
) -> list[dict]:
    """Return a new list of rows enriched with gl_account/gl_code/confidence/needs_review.

    Idempotent: if a row already has a non-empty `gl_account` and `reclassify` is
    False, leave it alone.
    """
    out: list[dict] = []
    for row in rows:
        new = dict(row)
        if not reclassify and _truthy(new.get(existing_gl_col)):
            # Preserve existing classification. Backfill any missing new cols.
            new.setdefault("gl_code", new.get("gl_code", ""))
            new.setdefault("confidence", new.get("confidence", "high"))
            new.setdefault("needs_review", new.get("needs_review", False))
            out.append(new)
            continue

        acct, code, conf = match_rule(new.get("description", ""), rules)
        if acct:
            new["gl_account"] = acct
            new["gl_code"] = code or ""
            new["confidence"] = conf
            new["needs_review"] = (conf == "low")
        else:
            new["gl_account"] = ""
            new["gl_code"] = ""
            new["confidence"] = "low"
            new["needs_review"] = True
        out.append(new)
    return out


def _parse_amount(val) -> float:
    if val is None:
        return 0.0
    s = str(val).strip().replace("$", "").replace(",", "")
    if s == "":
        return 0.0
    # Handle parenthesized negatives
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return 0.0


def summarize(rows: list[dict], review_limit: int = 50) -> None:
    """Print a review summary to stdout:
      1. Bucket counts + total $ (sorted by count desc)
      2. needs_review rows (up to `review_limit`), sorted by abs(amount) desc
    """
    totals_count: dict[str, int] = defaultdict(int)
    totals_amount: dict[str, float] = defaultdict(float)

    for r in rows:
        bucket = r.get("gl_account") or "(unmatched)"
        totals_count[bucket] += 1
        totals_amount[bucket] += _parse_amount(r.get("amount"))

    total_rows = len(rows)
    unmatched = sum(1 for r in rows if _truthy(r.get("needs_review")))
    matched = total_rows - unmatched
    pct = (matched / total_rows * 100.0) if total_rows else 0.0

    print("=" * 72)
    print(f"COA CATEGORIZER SUMMARY  —  {total_rows} rows")
    print(f"  matched: {matched}  ({pct:.1f}%)")
    print(f"  needs_review: {unmatched}")
    print("=" * 72)
    print(f"{'GL Bucket':<32} {'Count':>8} {'Total $':>14}")
    print("-" * 72)
    for bucket, cnt in sorted(totals_count.items(), key=lambda x: (-x[1], x[0])):
        amt = totals_amount[bucket]
        print(f"{bucket[:32]:<32} {cnt:>8} {amt:>14,.2f}")
    print()

    review_rows = [r for r in rows if _truthy(r.get("needs_review"))]
    review_rows.sort(key=lambda r: abs(_parse_amount(r.get("amount"))), reverse=True)
    shown = review_rows[:review_limit]

    print("-" * 72)
    print(f"NEEDS REVIEW  —  showing {len(shown)} of {len(review_rows)} "
          "(sorted by abs(amount) desc)")
    print("-" * 72)
    date_key = "date" if review_rows and "date" in review_rows[0] else "transaction_date"
    print(f"{'Date':<12} {'Amount':>12}  Description")
    for r in shown:
        d = (r.get(date_key) or r.get("date") or r.get("transaction_date") or "")[:10]
        amt = _parse_amount(r.get("amount"))
        desc = (r.get("description") or "")[:80]
        print(f"{d:<12} {amt:>12,.2f}  {desc}")
    print()


def _write_csv(rows: list[dict], output_path: str, original_fieldnames: list[str]) -> None:
    # Preserve original order; append any new columns not already present.
    fieldnames = list(original_fieldnames)
    for c in NEW_COLS:
        if c not in fieldnames:
            fieldnames.append(c)
    with open(output_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="COA categorizer for transaction CSVs.")
    ap.add_argument("input_csv")
    ap.add_argument("--rules",
                    default=str(Path(__file__).parent / "default_rules.json"),
                    help="Path to rules JSON file.")
    ap.add_argument("--output", default=None,
                    help="Output CSV path (omit to skip write).")
    ap.add_argument("--reclassify", action="store_true",
                    help="Re-run rules even on rows that already have gl_account set.")
    ap.add_argument("--review-limit", type=int, default=50)
    args = ap.parse_args(argv)

    rules = load_rules(args.rules)

    with open(args.input_csv, newline="") as f:
        reader = csv.DictReader(f)
        original_fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    enriched = categorize(rows, rules, reclassify=args.reclassify)
    summarize(enriched, review_limit=args.review_limit)

    if args.output:
        _write_csv(enriched, args.output, original_fieldnames)
        print(f"Wrote {len(enriched)} rows -> {args.output}")
    else:
        print("(no --output provided; not writing CSV)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

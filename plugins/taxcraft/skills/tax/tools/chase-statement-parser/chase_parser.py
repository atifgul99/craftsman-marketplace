#!/usr/bin/env python3
"""
Generic Chase Statement Parser
==============================

Library for parsing JPMorgan Chase business bank/credit-card statements (PDF)
and transaction-export CSVs into unified, reconciled transaction ledgers.

Works for any entity with Chase Business Complete Checking or Chase Ink
business credit cards. Invoke via a thin per-entity driver script that
supplies the ACCOUNTS config.

## USAGE (per-entity driver)

```python
from chase_parser import build_ledgers

ACCOUNTS = {
    "1234": {
        "label": "chase-1234",
        "type": "checking",                  # "checking" | "credit_card"
        "pdf_glob": ["entities/foo-llc/accounts/chase-1234/statements/*.pdf"],
        "csv_path": "entities/foo-llc/accounts/chase-1234/all-transactions.csv",
        "output_dir": "entities/foo-llc/books/transaction-ledgers",
        "yearly_slice_template": "entities/foo-llc/tax/FY{year}/source/bank-cc/chase-1234.csv",
    },
    ...
}

build_ledgers(ACCOUNTS, workspace_root="/path/to/workspace")
```

Paths in ACCOUNTS may be absolute or relative to `workspace_root`.
The `yearly_slice_template` field is optional; omit to skip generating per-year CSV slices.

## OUTPUT

For each account, writes to `output_dir`:
  - `<label>-unified-ledger.csv`   — chronological transactions with running balance
  - `<label>-validation.md`        — per-statement balance reconciliation

## VALIDATION

Every monthly PDF statement is reconciled:
  beginning_balance + sum(statement_txns) == stated_ending_balance   (checking)
  previous_balance   - sum(statement_txns) == stated_new_balance     (credit card)

Overlap (where PDF and CSV cover the same date) is checked; PDF is used for
pre-CSV dates, CSV for CSV-era dates. No double-counting.

## SIGN CONVENTIONS

Checking — `amount`:
  positive = deposit / credit to account
  negative = withdrawal / debit from account

Credit Card — `amount`:
  positive = payment (reduces outstanding)
  negative = purchase / fee / interest (increases outstanding)

## LIMITATIONS

Tested against Chase Business Complete Checking statement format (2023-2026)
and Chase Ink Business Card statement format (2023-2026). If Chase changes
layout, regexes may need adjustment. The `*start*<section>` / `*end*<section>`
markers in checking PDFs and the `ACCOUNT ACTIVITY` section in CC PDFs are
load-bearing; if they disappear, parser will silently miss transactions.
Always check the validation report after running.
"""
import csv
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from glob import glob
from pathlib import Path


# ===== PDF parsing =====

def pdftotext(path):
    return subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True, capture_output=True, text=True
    ).stdout


def parse_amount(s):
    s = s.replace(",", "").replace("$", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    return Decimal(s)


# ===== CHECKING PDF PARSER =====

SECTION_START = re.compile(r"\*start\*([a-z0-9 ]+)")
SECTION_END = re.compile(r"\*end\*([a-z0-9 ]+)")
PERIOD_RE = re.compile(r"([A-Z][a-z]+ \d{1,2}, \d{4}) through ([A-Z][a-z]+ \d{1,2}, \d{4})")
BEGIN_BAL_RE = re.compile(r"Beginning Balance\s+\$?([\d,]+\.\d{2})")
END_BAL_RE = re.compile(r"Ending Balance\s+\d+\s+\$?([\d,]+\.\d{2})")
TXN_LINE_RE = re.compile(r"^\s{2,}(\d{2}/\d{2})\s{2,}(.+?)\s{2,}\$?([\d,]+\.\d{2})\s*$")

CREDIT_SECTIONS = {"deposits and additions", "electronic deposits"}
DEBIT_SECTIONS = {
    "atm debit withdrawal",
    "electronic withdrawal",
    "checks paid",
    "fees",
    "fees section",
    "other withdrawal",
}


def parse_checking_pdf(path):
    """Parse one Chase Business Complete Checking monthly PDF statement."""
    text = pdftotext(path)
    lines = text.split("\n")

    period_match = PERIOD_RE.search(text)
    if not period_match:
        raise ValueError(f"No period found in {path}")
    period_start = datetime.strptime(period_match.group(1), "%B %d, %Y").date()
    period_end = datetime.strptime(period_match.group(2), "%B %d, %Y").date()

    begin_match = BEGIN_BAL_RE.search(text)
    end_match = END_BAL_RE.search(text)
    begin_balance = parse_amount(begin_match.group(1)) if begin_match else None
    end_balance = parse_amount(end_match.group(1)) if end_match else None

    txns = []
    current_section = None
    section_stack = []

    for line in lines:
        start = SECTION_START.search(line)
        if start:
            section_stack.append(start.group(1).strip())
            current_section = section_stack[-1]
            continue
        end = SECTION_END.search(line)
        if end:
            if section_stack:
                section_stack.pop()
            current_section = section_stack[-1] if section_stack else None
            continue

        if current_section not in CREDIT_SECTIONS and current_section not in DEBIT_SECTIONS:
            continue

        m = TXN_LINE_RE.match(line)
        if not m:
            continue

        md = m.group(1)
        desc = m.group(2).strip()
        amt = parse_amount(m.group(3))

        if desc.lower().startswith("total "):
            continue

        month = int(md.split("/")[0])
        if period_start.month == 12 and month == 1:
            txn_year = period_end.year
        elif period_start.month == 1 and month == 12:
            txn_year = period_start.year
        else:
            if period_start.year == period_end.year:
                txn_year = period_start.year
            else:
                txn_year = period_end.year if month <= period_end.month else period_start.year
        try:
            full_date = date(txn_year, month, int(md.split("/")[1]))
        except ValueError:
            continue

        signed = -amt if current_section in DEBIT_SECTIONS else amt
        txns.append({
            "date": full_date,
            "description": desc,
            "amount": signed,
            "section": current_section,
            "source": f"PDF:{Path(path).name}",
            "period_start": period_start,
            "period_end": period_end,
        })

    return {
        "pdf": str(path),
        "period_start": period_start,
        "period_end": period_end,
        "begin_balance": begin_balance,
        "end_balance": end_balance,
        "txns": txns,
    }


# ===== CHECKING CSV PARSER =====

def parse_checking_csv(path):
    """Parse Chase checking CSV export. Columns: Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #"""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            pd = row.get("Posting Date") or row.get(" Posting Date")
            if not pd:
                continue
            try:
                d = datetime.strptime(pd.strip(), "%m/%d/%Y").date()
            except ValueError:
                continue
            amt = parse_amount(row["Amount"])
            bal_str = row.get("Balance", "").strip()
            balance = parse_amount(bal_str) if bal_str else None
            rows.append({
                "date": d,
                "description": row["Description"].strip(),
                "amount": amt,
                "type": row.get("Type", "").strip(),
                "balance": balance,
                "check_or_slip": (row.get("Check or Slip #") or "").strip(),
                "source": f"CSV:{Path(path).name}",
                "details": row.get("Details", "").strip(),
            })
    return rows


# ===== CC PDF PARSER =====

CC_PERIOD_RE = re.compile(r"Opening/Closing Date:?\s+(\d{2}/\d{2}/\d{2})\s*-\s*(\d{2}/\d{2}/\d{2})")
CC_PREV_BAL_RE = re.compile(r"Previous Balance\s+\$?([\-\(\)\d,]+\.\d{2})")
CC_NEW_BAL_RE = re.compile(r"New Balance\s+\$?([\-\(\)\d,]+\.\d{2})")
CC_TXN_LINE_RE = re.compile(
    r"^\s{2,}(\d{2}/\d{2})\s{10,}(.+?)\s{4,}(-?[\d,]+\.\d{2})\s*$"
)


def parse_cc_pdf(path):
    """Parse one Chase Ink business credit-card monthly PDF statement."""
    text = pdftotext(path)
    lines = text.split("\n")

    period_match = CC_PERIOD_RE.search(text)
    if period_match:
        period_start = datetime.strptime(period_match.group(1), "%m/%d/%y").date()
        period_end = datetime.strptime(period_match.group(2), "%m/%d/%y").date()
    else:
        name = Path(path).stem
        m = re.match(r"(\d{4}-\d{2}-\d{2})", name)
        if not m:
            raise ValueError(f"No period in CC PDF {path}")
        period_end = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        period_start = period_end.replace(day=max(1, period_end.day - 28))

    prev_bal_match = CC_PREV_BAL_RE.search(text)
    new_bal_match = CC_NEW_BAL_RE.search(text)
    prev_balance = parse_amount(prev_bal_match.group(1)) if prev_bal_match else None
    new_balance = parse_amount(new_bal_match.group(1)) if new_bal_match else None

    # CC statement structure: one "ACCOUNT ACTIVITY" section with all txns (purchases, payments, fees).
    # Amounts in PDF: positive = charge; negative = payment/credit.
    # We flip sign to match CSV convention: payment positive, charge negative.
    txns = []
    in_account_activity = False
    for line in lines:
        stripped = line.strip()
        if "ACCOUNT ACTIVITY" in stripped and "Denotes" in line:
            in_account_activity = True
            continue
        if in_account_activity and ("INTEREST CHARGES" in stripped or "Totals Year-to-Date" in stripped):
            in_account_activity = False
            continue
        if not in_account_activity:
            continue

        m = CC_TXN_LINE_RE.match(line)
        if not m:
            continue
        txn_date_str = m.group(1)
        desc = m.group(2).strip()
        amt = parse_amount(m.group(3))

        if desc.upper().startswith("TRANSACTIONS THIS CYCLE"):
            continue
        if desc.upper().startswith("INCLUDING PAYMENTS"):
            continue

        month = int(txn_date_str.split("/")[0])
        if period_start.month == 12 and month == 1:
            yr = period_end.year
        elif period_start.month == 1 and month == 12:
            yr = period_start.year
        else:
            if month >= period_start.month:
                yr = period_start.year
            else:
                yr = period_end.year
        try:
            txn_date = date(yr, month, int(txn_date_str.split("/")[1]))
        except ValueError:
            continue

        signed = -amt  # flip

        if amt < 0:
            section = "payment"
        elif "ANNUAL" in desc.upper() or "LATE FEE" in desc.upper() or "FEE" in desc.upper():
            section = "fee"
        else:
            section = "purchase"

        txns.append({
            "transaction_date": txn_date,
            "post_date": txn_date,
            "description": desc,
            "amount": signed,
            "section": section,
            "source": f"PDF:{Path(path).name}",
            "period_start": period_start,
            "period_end": period_end,
        })

    return {
        "pdf": str(path),
        "period_start": period_start,
        "period_end": period_end,
        "prev_balance": prev_balance,
        "new_balance": new_balance,
        "txns": txns,
    }


# ===== CC CSV PARSER =====

def parse_cc_csv(path):
    """Parse Chase CC CSV export. Columns: Card,Transaction Date,Post Date,Description,Category,Type,Amount,Memo"""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            td = row["Transaction Date"].strip()
            pd_ = row["Post Date"].strip()
            if not td:
                continue
            txn_date = datetime.strptime(td, "%m/%d/%Y").date()
            post_date = datetime.strptime(pd_, "%m/%d/%Y").date() if pd_ else txn_date
            amt = parse_amount(row["Amount"])
            rows.append({
                "transaction_date": txn_date,
                "post_date": post_date,
                "description": row["Description"].strip(),
                "amount": amt,
                "type": row.get("Type", "").strip(),
                "category": row.get("Category", "").strip(),
                "memo": row.get("Memo", "").strip(),
                "source": f"CSV:{Path(path).name}",
            })
    return rows


# ===== LEDGER BUILDERS =====

def _resolve(path, workspace_root):
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(workspace_root) / p


def build_checking_ledger(account_key, cfg, workspace_root):
    pdf_paths = []
    for g in cfg["pdf_glob"]:
        pdf_paths.extend(sorted(glob(str(_resolve(g, workspace_root)))))

    print(f"\n{'='*70}\n[{account_key}] {cfg['label']} — {len(pdf_paths)} PDFs")

    pdfs = []
    all_pdf_txns = []
    for p in pdf_paths:
        parsed = parse_checking_pdf(p)
        pdfs.append(parsed)
        all_pdf_txns.extend(parsed["txns"])
        txn_sum = sum(t["amount"] for t in parsed["txns"])
        computed_end = (parsed["begin_balance"] or Decimal(0)) + txn_sum
        stated_end = parsed["end_balance"]
        ok = (stated_end is not None and abs(computed_end - stated_end) < Decimal("0.01"))
        flag = "OK" if ok else "!! MISMATCH"
        print(f"  {Path(p).name}: beg={parsed['begin_balance']} txns={len(parsed['txns'])} sum={txn_sum} computed_end={computed_end} stated_end={stated_end} {flag}")

    csv_path = _resolve(cfg["csv_path"], workspace_root)
    csv_rows = parse_checking_csv(csv_path)
    csv_rows.sort(key=lambda r: (r["date"], r["description"]))
    if not csv_rows:
        raise ValueError(f"No transaction rows found in CSV {csv_path} — cannot build ledger.")
    print(f"  CSV: {len(csv_rows)} rows, {csv_rows[0]['date']} -> {csv_rows[-1]['date']}")

    if not pdfs:
        raise ValueError(
            f"No PDF statements found for pdf_glob={cfg['pdf_glob']!r} — cannot determine opening balance."
        )

    csv_start = csv_rows[0]["date"]
    pre_csv_txns = [t for t in all_pdf_txns if t["date"] < csv_start]
    pre_csv_txns.sort(key=lambda t: (t["date"], t["description"]))

    overlap_pdf = [t for t in all_pdf_txns if t["date"] >= csv_start]
    overlap_csv = [t for t in csv_rows if t["date"] <= max(p["period_end"] for p in pdfs)]
    pdf_sum = sum(t["amount"] for t in overlap_pdf)
    csv_sum = sum(r["amount"] for r in overlap_csv)
    overlap_match = abs(pdf_sum - csv_sum) < Decimal("0.01")
    print(f"  Overlap {csv_start} -> {max(p['period_end'] for p in pdfs)}: PDF n={len(overlap_pdf)} sum={pdf_sum} | CSV n={len(overlap_csv)} sum={csv_sum} | {'OK' if overlap_match else '!! MISMATCH'}")

    opening = pdfs[0]["begin_balance"]
    if opening is None:
        raise ValueError(
            f"Could not parse a beginning balance from {pdfs[0]['pdf']} — cannot build a running ledger."
        )
    unified = []
    running = opening
    for t in pre_csv_txns:
        running += t["amount"]
        unified.append({
            "date": t["date"],
            "description": t["description"],
            "amount": t["amount"],
            "balance": running,
            "source": t["source"],
            "type": t["section"],
            "check_or_slip": "",
        })
    for r in csv_rows:
        running += r["amount"]
        unified.append({
            "date": r["date"],
            "description": r["description"],
            "amount": r["amount"],
            "balance": r["balance"] if r["balance"] is not None else running,
            "source": r["source"],
            "type": r["type"],
            "check_or_slip": r["check_or_slip"],
        })
        if r["balance"] is not None:
            running = r["balance"]

    unified.sort(key=lambda r: (r["date"],))

    validation_points = []
    for p in pdfs:
        as_of = None
        for row in reversed(unified):
            if row["date"] <= p["period_end"]:
                as_of = row["balance"]
                break
        stated = p["end_balance"]
        ok = (as_of is not None and stated is not None and abs(as_of - stated) < Decimal("0.02"))
        validation_points.append({
            "period_end": p["period_end"],
            "stated_end": stated,
            "ledger_running": as_of,
            "match": ok,
        })

    output_dir = _resolve(cfg["output_dir"], workspace_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_out = output_dir / f"{cfg['label']}-unified-ledger.csv"
    with open(csv_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "description", "amount", "balance", "type", "check_or_slip", "source"])
        for row in unified:
            w.writerow([
                row["date"].isoformat(),
                row["description"],
                str(row["amount"]),
                str(row["balance"]),
                row["type"],
                row["check_or_slip"],
                row["source"],
            ])
    print(f"  Wrote {csv_out} ({len(unified)} rows)")

    _write_yearly_slices(unified, cfg, workspace_root, date_field="date")

    report = output_dir / f"{cfg['label']}-validation.md"
    with open(report, "w") as f:
        f.write(f"# {cfg['label']} — Transaction Ledger Validation\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"**Coverage**: {unified[0]['date']} → {unified[-1]['date']}\n")
        f.write(f"**Total transactions**: {len(unified)}\n")
        f.write(f"**Opening balance**: ${opening}\n")
        f.write(f"**Ending balance**: ${unified[-1]['balance']}\n\n")
        f.write("## Per-statement balance validation\n\n")
        f.write("Each row: at statement period end, does our ledger running balance match the stated ending balance?\n\n")
        f.write("| Statement period end | Stated ending | Ledger running | Match |\n")
        f.write("|---|---|---|---|\n")
        for v in validation_points:
            mark = "OK" if v["match"] else "FAIL"
            f.write(f"| {v['period_end']} | ${v['stated_end']} | ${v['ledger_running']} | {mark} |\n")
        f.write(f"\n## Overlap reconciliation\n\n")
        f.write(f"Dates {csv_start} through {max(p['period_end'] for p in pdfs)} appear in both PDF statements and CSV:\n\n")
        f.write(f"- PDF transactions: {len(overlap_pdf)}, sum = ${pdf_sum}\n")
        f.write(f"- CSV transactions: {len(overlap_csv)}, sum = ${csv_sum}\n")
        f.write(f"- Match: {'OK' if overlap_match else 'FAIL'}\n")
    print(f"  Wrote {report}")


def build_cc_ledger(account_key, cfg, workspace_root):
    pdf_paths = []
    for g in cfg["pdf_glob"]:
        pdf_paths.extend(sorted(glob(str(_resolve(g, workspace_root)))))

    print(f"\n{'='*70}\n[{account_key}] {cfg['label']} — {len(pdf_paths)} PDFs")

    pdfs = []
    all_pdf_txns = []
    for p in pdf_paths:
        parsed = parse_cc_pdf(p)
        pdfs.append(parsed)
        all_pdf_txns.extend(parsed["txns"])
        txn_sum = sum(t["amount"] for t in parsed["txns"])
        computed_new = (parsed["prev_balance"] or Decimal(0)) - txn_sum
        stated_new = parsed["new_balance"]
        ok = (stated_new is not None and abs(computed_new - stated_new) < Decimal("0.02"))
        flag = "OK" if ok else "!! MISMATCH"
        print(f"  {Path(p).name}: prev={parsed['prev_balance']} txns={len(parsed['txns'])} sum={txn_sum} computed_new={computed_new} stated_new={stated_new} {flag}")

    csv_path = _resolve(cfg["csv_path"], workspace_root)
    csv_rows = parse_cc_csv(csv_path)
    csv_rows.sort(key=lambda r: (r["post_date"], r["transaction_date"]))
    if not csv_rows:
        raise ValueError(f"No transaction rows found in CSV {csv_path} — cannot build ledger.")
    print(f"  CSV: {len(csv_rows)} rows, {csv_rows[0]['transaction_date']} -> {csv_rows[-1]['transaction_date']}")

    if not pdfs:
        raise ValueError(
            f"No PDF statements found for pdf_glob={cfg['pdf_glob']!r} — cannot determine opening balance."
        )

    csv_start = csv_rows[0]["post_date"]
    pre_csv = [t for t in all_pdf_txns if t["post_date"] < csv_start]

    overlap_pdf = [t for t in all_pdf_txns if t["post_date"] >= csv_start]
    overlap_csv = [r for r in csv_rows if r["post_date"] <= max(p["period_end"] for p in pdfs)]
    pdf_sum = sum(t["amount"] for t in overlap_pdf)
    csv_sum = sum(r["amount"] for r in overlap_csv)
    overlap_match = abs(pdf_sum - csv_sum) < Decimal("0.01")
    print(f"  Overlap: PDF n={len(overlap_pdf)} sum={pdf_sum} | CSV n={len(overlap_csv)} sum={csv_sum} | {'OK' if overlap_match else '!! MISMATCH'}")

    # Sort PDF by statement cycle (not txn_date) to respect statement boundaries
    opening = pdfs[0]["prev_balance"]
    if opening is None:
        raise ValueError(
            f"Could not parse a previous balance from {pdfs[0]['pdf']} — cannot build a running ledger."
        )
    unified_raw = []
    for t in pre_csv:
        unified_raw.append({
            "sort_key": (t["period_end"], t["transaction_date"], 0),
            "transaction_date": t["transaction_date"],
            "post_date": t["post_date"],
            "description": t["description"],
            "amount": t["amount"],
            "statement_period_end": t["period_end"],
            "type": t["section"],
            "source": t["source"],
            "category": "",
            "memo": "",
        })
    for r in csv_rows:
        unified_raw.append({
            "sort_key": (r["post_date"], r["transaction_date"], 1),
            "transaction_date": r["transaction_date"],
            "post_date": r["post_date"],
            "description": r["description"],
            "amount": r["amount"],
            "statement_period_end": None,
            "type": r["type"],
            "source": r["source"],
            "category": r["category"],
            "memo": r["memo"],
        })

    unified_raw.sort(key=lambda r: r["sort_key"])
    running = opening
    unified = []
    for row in unified_raw:
        running -= row["amount"]
        row_out = dict(row)
        row_out["outstanding_balance"] = running
        del row_out["sort_key"]
        unified.append(row_out)

    validation_points = []
    for p in pdfs:
        as_of = None
        for row in reversed(unified):
            pe = row.get("statement_period_end")
            belongs_to_cycle = pe is not None and pe <= p["period_end"]
            csv_before = pe is None and row["post_date"] <= p["period_end"]
            if belongs_to_cycle or csv_before:
                as_of = row["outstanding_balance"]
                break
        stated = p["new_balance"]
        ok = (as_of is not None and stated is not None and abs(as_of - stated) < Decimal("0.02"))
        validation_points.append({
            "period_end": p["period_end"],
            "stated_new": stated,
            "ledger_outstanding": as_of,
            "match": ok,
        })

    output_dir = _resolve(cfg["output_dir"], workspace_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_out = output_dir / f"{cfg['label']}-unified-ledger.csv"
    with open(csv_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["transaction_date", "post_date", "description", "amount", "outstanding_balance", "type", "category", "memo", "source"])
        for row in unified:
            w.writerow([
                row["transaction_date"].isoformat(),
                row["post_date"].isoformat(),
                row["description"],
                str(row["amount"]),
                str(row["outstanding_balance"]),
                row["type"],
                row["category"],
                row["memo"],
                row["source"],
            ])
    print(f"  Wrote {csv_out} ({len(unified)} rows)")

    _write_yearly_slices(unified, cfg, workspace_root, date_field="post_date")

    report = output_dir / f"{cfg['label']}-validation.md"
    with open(report, "w") as f:
        f.write(f"# {cfg['label']} — Transaction Ledger Validation\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"**Coverage**: {unified[0]['post_date']} → {unified[-1]['post_date']}\n")
        f.write(f"**Total transactions**: {len(unified)}\n")
        f.write(f"**Opening balance (outstanding)**: ${opening}\n")
        f.write(f"**Ending balance (outstanding)**: ${unified[-1]['outstanding_balance']}\n\n")
        f.write("Sign convention: amount positive = payment (reduces outstanding); amount negative = purchase/fee/interest (increases outstanding).\n\n")
        f.write("## Per-statement balance validation\n\n")
        f.write("| Statement period end | Stated new balance | Ledger outstanding | Match |\n")
        f.write("|---|---|---|---|\n")
        for v in validation_points:
            mark = "OK" if v["match"] else "FAIL"
            f.write(f"| {v['period_end']} | ${v['stated_new']} | ${v['ledger_outstanding']} | {mark} |\n")
        f.write(f"\n## Overlap reconciliation\n\n")
        f.write(f"- PDF transactions in overlap: {len(overlap_pdf)}, sum = ${pdf_sum}\n")
        f.write(f"- CSV transactions in overlap: {len(overlap_csv)}, sum = ${csv_sum}\n")
        f.write(f"- Match: {'OK' if overlap_match else 'FAIL'}\n")
    print(f"  Wrote {report}")


def _write_yearly_slices(unified, cfg, workspace_root, date_field):
    """Split a unified ledger into per-tax-year CSV slices placed under tax/FY<YYYY>/source/bank-cc/<label>.csv.

    cfg must include 'yearly_slice_template' — a path template with {year} placeholder
    (relative to workspace_root), e.g. "entities/foo/tax/FY{year}/source/bank-cc/<label>.csv".
    """
    tmpl = cfg.get("yearly_slice_template")
    if not tmpl:
        return
    if not unified:
        return
    header = [k for k in unified[0].keys() if k != "statement_period_end"]

    by_year = defaultdict(list)
    for row in unified:
        d = row[date_field]
        by_year[d.year].append(row)

    for year, rows in sorted(by_year.items()):
        out_path = _resolve(tmpl.format(year=year), workspace_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            for row in rows:
                w.writerow([
                    row[k].isoformat() if hasattr(row[k], "isoformat") else (str(row[k]) if row[k] is not None else "")
                    for k in header
                ])
        print(f"  Year slice: {out_path} ({len(rows)} rows)")


def build_ledgers(accounts, workspace_root):
    """Build unified ledgers for a set of accounts.

    accounts: dict mapping account key -> config (see module docstring for shape)
    workspace_root: absolute path to workspace root (for resolving relative paths in config)
    """
    for key, cfg in accounts.items():
        if cfg["type"] == "checking":
            build_checking_ledger(key, cfg, workspace_root)
        elif cfg["type"] == "credit_card":
            build_cc_ledger(key, cfg, workspace_root)
        else:
            raise ValueError(f"Unknown account type: {cfg['type']}")

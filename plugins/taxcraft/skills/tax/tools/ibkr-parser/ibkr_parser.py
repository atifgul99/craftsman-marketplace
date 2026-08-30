#!/usr/bin/env python3
"""
IBKR (Interactive Brokers) Activity Statement Parser.

Library-first: ``from ibkr_parser import parse_ibkr`` returns a dict with
transactions, summary, and validation info. CSV is the primary source;
the PDF (if supplied) is cross-checked for summary totals only.

CLI:
    python3 ibkr_parser.py <statement.csv> [--pdf <statement.pdf>]
                           [--out <result.json>] [--no-confirm]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

# Make the pdf-extractor sibling importable for optional PDF validation.
sys.path.insert(0, str(Path(__file__).parent.parent / "pdf-extractor"))
try:
    from pdf_extract import extract as pdf_extract  # type: ignore
except Exception:  # pragma: no cover - PDF validation is optional
    pdf_extract = None  # type: ignore


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

_ASSET_MAP = {
    "Stocks": "STK",
    "Equity and Index Options": "OPT",
    "Options": "OPT",
    "Futures": "FUT",
    "Future Options": "FUT",
    "Bonds": "BOND",
    "Forex": "CASH",
}


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    s = str(value).strip()
    if not s or s in {"--", "-", "N/A"}:
        return 0.0
    s = s.replace(",", "").replace("$", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_period(period: str) -> tuple[Optional[str], Optional[str]]:
    if not period:
        return None, None
    parts = [p.strip() for p in period.split("-")]
    if len(parts) != 2:
        return None, None

    def one(s: str) -> Optional[str]:
        m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", s)
        if not m:
            return None
        mon = _MONTHS.get(m.group(1).lower())
        if not mon:
            return None
        return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"

    return one(parts[0]), one(parts[1])


def _asset_cat(label: str) -> str:
    return _ASSET_MAP.get(label, label or "")


def _date_only(value: str) -> str:
    if not value:
        return ""
    return value.split(",", 1)[0].strip()


def _symbol_from_desc(desc: str) -> str:
    if not desc:
        return ""
    m = re.match(r"([A-Z][A-Z0-9.\-]*)\s*\(", desc)
    return m.group(1) if m else ""


def _group_rows_by_section(csv_path: Path) -> dict[str, dict[str, Any]]:
    """Walk the CSV once; first Header wins per section."""
    sections: dict[str, dict[str, Any]] = {}
    current_columns: dict[str, list[str]] = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        for raw in reader:
            if not raw:
                continue
            section = raw[0].strip()
            if len(raw) < 2:
                continue
            kind = raw[1].strip()
            rest = raw[2:]

            if kind == "Header":
                if section not in current_columns:
                    current_columns[section] = [c.strip() for c in rest]
                    sections.setdefault(section, {"columns": rest, "rows": []})
                continue

            cols = current_columns.get(section)
            if cols is None:
                continue
            row: dict[str, Any] = {"_kind": kind}
            for i, col in enumerate(cols):
                row[col] = rest[i] if i < len(rest) else ""
            sections.setdefault(section, {"columns": cols, "rows": []})
            sections[section]["rows"].append(row)

    return sections


def _header_meta(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "account_id": None, "period_start": None, "period_end": None,
        "currency": "USD", "name": None,
    }
    for r in sections.get("Statement", {}).get("rows", []):
        if r.get("Field Name") == "Period":
            s, e = _parse_period(r.get("Field Value", ""))
            meta["period_start"] = s
            meta["period_end"] = e
    for r in sections.get("Account Information", {}).get("rows", []):
        fn = r.get("Field Name", "")
        fv = r.get("Field Value", "")
        if fn == "Account":
            meta["account_id"] = fv
        elif fn == "Name":
            meta["name"] = fv
        elif fn == "Base Currency":
            meta["currency"] = fv or "USD"
    return meta


def _norm_trades(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        if r.get("_kind") != "Data":
            continue
        disc = r.get("DataDiscriminator", "")
        if disc not in {"Order", "Trade"}:
            continue
        out.append({
            "type": "trade",
            "date": _date_only(r.get("Date/Time", "")),
            "symbol": r.get("Symbol", ""),
            "description": r.get("Symbol", ""),
            "quantity": _to_float(r.get("Quantity")),
            "price": _to_float(r.get("T. Price")),
            "proceeds": _to_float(r.get("Proceeds")),
            "commission": _to_float(r.get("Comm/Fee")),
            "realized_pl": _to_float(r.get("Realized P/L")),
            "asset_category": _asset_cat(r.get("Asset Category", "")),
            "currency": r.get("Currency", "") or "USD",
            "amount": _to_float(r.get("Proceeds")) + _to_float(r.get("Comm/Fee")),
            "code": r.get("Code", ""),
        })
    return out


def _norm_dividends(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        if r.get("_kind") != "Data":
            continue
        if (r.get("Currency") or "").lower().startswith("total"):
            continue
        out.append({
            "type": "dividend",
            "date": r.get("Date", ""),
            "symbol": _symbol_from_desc(r.get("Description", "")),
            "description": r.get("Description", ""),
            "quantity": 0.0, "price": 0.0, "proceeds": 0.0,
            "commission": 0.0, "realized_pl": 0.0,
            "asset_category": "STK",
            "currency": r.get("Currency", "") or "USD",
            "amount": _to_float(r.get("Amount")),
        })
    return out


def _norm_simple_cash(rows: list[dict[str, Any]], tx_type: str,
                      asset: str = "CASH", date_field: str = "Date") -> list[dict[str, Any]]:
    out = []
    for r in rows:
        if r.get("_kind") != "Data":
            continue
        cur = r.get("Currency", "") or ""
        if cur.lower().startswith("total"):
            continue
        amt = _to_float(r.get("Amount"))
        this_type = tx_type
        if tx_type == "deposit" and amt < 0:
            this_type = "withdrawal"
        out.append({
            "type": this_type,
            "date": r.get(date_field, ""),
            "symbol": "",
            "description": r.get("Description", ""),
            "quantity": 0.0, "price": 0.0, "proceeds": 0.0,
            "commission": 0.0, "realized_pl": 0.0,
            "asset_category": asset,
            "currency": cur or "USD",
            "amount": amt,
        })
    return out


def _norm_corporate_actions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        if r.get("_kind") != "Data":
            continue
        cur = r.get("Currency", "") or ""
        if cur.lower().startswith("total"):
            continue
        out.append({
            "type": "corporate_action",
            "date": _date_only(r.get("Date/Time", "") or r.get("Report Date", "")),
            "symbol": r.get("Symbol", ""),
            "description": r.get("Description", ""),
            "quantity": _to_float(r.get("Quantity")),
            "price": 0.0,
            "proceeds": _to_float(r.get("Proceeds")),
            "commission": 0.0,
            "realized_pl": _to_float(r.get("Realized P/L")),
            "asset_category": _asset_cat(r.get("Asset Category", "")),
            "currency": cur or "USD",
            "amount": _to_float(r.get("Proceeds")),
        })
    return out


def _summary_from_transactions(transactions: list[dict[str, Any]]) -> dict[str, float]:
    s = {
        "realized_pl": 0.0, "total_dividends": 0.0, "total_interest": 0.0,
        "total_fees": 0.0, "net_deposits": 0.0, "ending_nav": 0.0,
    }
    for t in transactions:
        ty = t["type"]
        if ty == "trade":
            s["realized_pl"] += t.get("realized_pl", 0.0)
            s["total_fees"] += t.get("commission", 0.0)
        elif ty == "dividend":
            s["total_dividends"] += t.get("amount", 0.0)
        elif ty == "interest":
            s["total_interest"] += t.get("amount", 0.0)
        elif ty == "fee":
            s["total_fees"] += t.get("amount", 0.0)
        elif ty in ("deposit", "withdrawal"):
            s["net_deposits"] += t.get("amount", 0.0)
    return {k: round(v, 6) for k, v in s.items()}


def _ending_nav_from_csv(sections: dict[str, dict[str, Any]]) -> float:
    for r in sections.get("Net Asset Value", {}).get("rows", []):
        if (r.get("Asset Class") or "").strip().lower() == "total":
            return _to_float(r.get("Current Total"))
    return 0.0


def _csv_totals(sections: dict[str, dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for r in sections.get("Change in NAV", {}).get("rows", []):
        fn = (r.get("Field Name") or "").strip()
        if fn:
            totals[f"change_in_nav.{fn}"] = _to_float(r.get("Field Value"))
    for r in sections.get("Cash Report", {}).get("rows", []):
        label = (r.get("Currency Summary") or "").strip()
        if label:
            totals[f"cash_report.{label}"] = _to_float(r.get("Total"))
    for r in sections.get("Net Asset Value", {}).get("rows", []):
        ac = (r.get("Asset Class") or "").strip()
        if ac:
            totals[f"nav.{ac}"] = _to_float(r.get("Current Total"))
    return totals


def _pdf_totals(pdf_path: Path) -> dict[str, float]:
    if pdf_extract is None:
        return {}
    try:
        res = pdf_extract(pdf_path)
    except Exception:
        return {}
    if res.mode != "text" or not res.text:
        return {}
    text = res.text
    totals: dict[str, float] = {}
    patterns = [
        (r"Starting Value\s+([\d,.\-]+)", "change_in_nav.Starting Value"),
        (r"Ending Value\s+([\d,.\-]+)", "change_in_nav.Ending Value"),
        (r"Mark-to-Market\s+(-?[\d,.\-]+)", "change_in_nav.Mark-to-Market"),
        (r"Commissions\s+(-?[\d,.\-]+)", "change_in_nav.Commissions"),
        (r"Deposits\s*&\s*Withdrawals\s+(-?[\d,.\-]+)",
         "change_in_nav.Deposits & Withdrawals"),
        (r"Ending Cash\s+(-?[\d,.\-]+)", "cash_report.Ending Cash"),
        (r"Starting Cash\s+(-?[\d,.\-]+)", "cash_report.Starting Cash"),
    ]
    for pat, key in patterns:
        m = re.search(pat, text)
        if m:
            totals[key] = _to_float(m.group(1))
    return totals


def _validate(csv_totals: dict[str, float], pdf_totals: dict[str, float],
              tolerance: float = 0.02) -> tuple[bool, list[dict[str, Any]]]:
    mismatches: list[dict[str, Any]] = []
    for key, pdf_v in pdf_totals.items():
        csv_v = csv_totals.get(key)
        if csv_v is None:
            continue
        if abs(csv_v - pdf_v) > tolerance:
            mismatches.append({"field": key, "csv": csv_v, "pdf": pdf_v,
                               "diff": round(csv_v - pdf_v, 6)})
    return (len(mismatches) == 0), mismatches


def parse_ibkr(csv_path: str | Path, pdf_path: Optional[str | Path] = None) -> dict[str, Any]:
    """Parse an IBKR activity-statement CSV into a structured dict."""
    csv_path = Path(csv_path).resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)

    sections = _group_rows_by_section(csv_path)
    meta = _header_meta(sections)

    section_rows = {name: sec["rows"] for name, sec in sections.items()}

    transactions: list[dict[str, Any]] = []
    anomalies: list[str] = []
    non_usd: list[dict[str, Any]] = []

    handlers = [
        ("Trades", _norm_trades),
        ("Dividends", _norm_dividends),
        ("Interest", lambda rs: _norm_simple_cash(rs, "interest", "CASH", "Date")),
        ("Fees", lambda rs: _norm_simple_cash(rs, "fee", "CASH", "Date")),
        ("Broker Fees", lambda rs: _norm_simple_cash(rs, "fee", "CASH", "Date")),
        ("Commission Details", lambda rs: _norm_simple_cash(rs, "fee", "CASH", "Date")),
        ("Deposits & Withdrawals",
         lambda rs: _norm_simple_cash(rs, "deposit", "CASH", "Settle Date")),
        ("Corporate Actions", _norm_corporate_actions),
    ]

    sections_found: list[str] = []
    section_counts: dict[str, int] = {}
    for name, fn in handlers:
        rows = section_rows.get(name)
        if not rows:
            continue
        sections_found.append(name)
        new_tx = fn(rows)
        transactions.extend(new_tx)
        section_counts[name] = len(new_tx)

    for t in transactions:
        if t.get("currency") and t["currency"] != "USD":
            non_usd.append({
                "type": t["type"], "date": t.get("date"),
                "symbol": t.get("symbol"), "currency": t["currency"],
                "amount": t.get("amount"),
            })

    summary = _summary_from_transactions(transactions)
    summary["ending_nav"] = _ending_nav_from_csv(sections)

    csv_totals = _csv_totals(sections)
    pdf_totals: dict[str, float] = {}
    if pdf_path:
        pdf_p = Path(pdf_path).resolve()
        if pdf_p.is_file():
            pdf_totals = _pdf_totals(pdf_p)
        else:
            anomalies.append(f"PDF not found: {pdf_p}")
    match, mismatches = _validate(csv_totals, pdf_totals)

    return {
        "doc_type": "IBKR-Statement",
        "account_id": meta["account_id"],
        "period_start": meta["period_start"],
        "period_end": meta["period_end"],
        "currency": meta["currency"],
        "transactions": transactions,
        "summary": summary,
        "validation": {
            "csv_totals": csv_totals,
            "pdf_totals": pdf_totals,
            "match": match if pdf_totals else None,
            "mismatches": mismatches,
        },
        "non_usd_amounts": non_usd,
        "anomalies": anomalies,
        "_meta": {
            "source_csv": str(csv_path),
            "source_pdf": str(pdf_path) if pdf_path else None,
            "sections_found": sections_found,
            "section_counts": section_counts,
            "account_name": meta.get("name"),
        },
    }


def _print_summary(result: dict[str, Any]) -> None:
    meta = result.get("_meta", {})
    print("=" * 72)
    print(f"IBKR Statement: {result.get('account_id')} ({meta.get('account_name')})")
    print(f"Period: {result['period_start']} to {result['period_end']}  "
          f"Currency: {result['currency']}")
    print(f"CSV: {meta.get('source_csv')}")
    if meta.get("source_pdf"):
        print(f"PDF: {meta.get('source_pdf')}")
    print("-" * 72)
    sc = meta.get("section_counts", {})
    print("Sections parsed:")
    for name in meta.get("sections_found", []):
        print(f"  {name:30s}  {sc.get(name, 0):>5} transactions")
    print(f"  {'TOTAL':30s}  {len(result['transactions']):>5} transactions")
    print("-" * 72)
    s = result["summary"]
    print("Summary:")
    for k in ("realized_pl", "total_dividends", "total_interest",
              "total_fees", "net_deposits", "ending_nav"):
        print(f"  {k:20s}  {s[k]:>15,.2f}")
    val = result["validation"]
    print("-" * 72)
    if val["match"] is None:
        print("Validation: skipped (no PDF supplied)")
    elif val["match"]:
        print(f"Validation: PASS ({len(val['pdf_totals'])} totals checked)")
    else:
        print(f"Validation: FAIL - {len(val['mismatches'])} mismatch(es)")
        for m in val["mismatches"]:
            print(f"    {m['field']}  CSV={m['csv']}  PDF={m['pdf']}  diff={m['diff']}")
    if result["non_usd_amounts"]:
        print(f"Non-USD transactions flagged: {len(result['non_usd_amounts'])}")
    if result["anomalies"]:
        print("Anomalies:")
        for a in result["anomalies"]:
            print(f"  - {a}")
    print("=" * 72)


def _confirm() -> str:
    while True:
        try:
            ans = input("Write JSON? [y]es / [e]dit / [s]kip: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "s"
        if ans in {"y", "yes"}:
            return "y"
        if ans in {"e", "edit"}:
            return "e"
        if ans in {"s", "skip", "n", "no"}:
            return "s"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Parse an IBKR activity-statement CSV.")
    ap.add_argument("csv", help="Path to IBKR CSV statement")
    ap.add_argument("--pdf", default=None, help="Optional PDF for validation")
    ap.add_argument("--out", default=None,
                    help="Output JSON path (default: alongside CSV, .json)")
    ap.add_argument("--no-confirm", action="store_true",
                    help="Skip confirmation prompt (non-interactive)")
    args = ap.parse_args(argv)

    result = parse_ibkr(args.csv, pdf_path=args.pdf)
    _print_summary(result)

    out_path = Path(args.out) if args.out else Path(args.csv).with_suffix(".json")

    if not args.no_confirm:
        choice = _confirm()
        if choice == "s":
            print("Skipped. Nothing written.")
            return 0
        if choice == "e":
            print("Edit mode: dumping JSON to stdout; redirect as needed.")
            json.dump(result, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
            return 0

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=str)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
K-1 Parser — extract Schedule K-1 (Form 1065 / 1120-S) into the parsing.md schema.

Library usage:
    from k1_parser import parse_k1, parse_multi_k1
    result = parse_k1("path/to/k1.pdf")          # -> dict
    results = parse_multi_k1("path/to/return.pdf") # -> list[dict]

CLI usage:
    python3 k1_parser.py "path/to/k1.pdf"
    python3 k1_parser.py "path/to/return.pdf" --multi
    python3 k1_parser.py "path/to/k1.pdf" --no-confirm   # skip interactive prompt
    python3 k1_parser.py "path/to/k1.pdf" --json         # print JSON only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Import pdf-extractor sibling tool
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pdf-extractor"))
from pdf_extract import extract  # type: ignore


# ---------- number parsing ----------

NUM_RE = r"-?\(?\$?\s*-?[\d,]+(?:\.\d+)?\)?"


def parse_amount(s: str | None) -> float:
    """Parse '-24,168.', '(500.)', '$1,234.56', '50,000.' -> float. None/empty -> 0.0."""
    if s is None:
        return 0.0
    s = s.strip().replace("$", "").replace(",", "")
    if not s:
        return 0.0
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    if s.endswith("."):
        s = s[:-1]
    s = s.strip()
    if not s or s == "-":
        return 0.0
    try:
        v = float(s)
    except ValueError:
        return 0.0
    return -v if neg else v


# ---------- field extraction helpers ----------

def _search(pattern: str, text: str, flags: int = 0, group: int = 1) -> str | None:
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else None


def _search_amount(pattern: str, text: str, flags: int = 0, group: int = 1) -> float:
    v = _search(pattern, text, flags, group)
    return parse_amount(v)


# ---------- Cover / reconciliation section ----------

EIN_RE = r"\b(\d{2}-\d{7})\b"


def extract_capital_account(text: str) -> dict:
    """Pull Beginning / Contrib / NetIncome / Withdraw / Ending from either the
    reconciliation cover section OR the Form K-1 Item L."""
    ca = {"beginning": 0.0, "contrib": 0.0, "withdraw": 0.0, "net_income": 0.0, "ending": 0.0}

    # Prefer the "Partner's Capital Account Analysis" (Item L) on the form itself.
    pat_map = [
        ("beginning", r"[Bb]eginning [Cc]apital [Aa]ccount[^0-9\-\(]*" + f"({NUM_RE})"),
        ("contrib", r"[Cc]apital [Cc]ontributed [Dd]uring [Tt]he [Yy]ear[^0-9\-\(]*" + f"({NUM_RE})"),
        ("net_income", r"[Cc]urrent [Yy]ear [Nn]et [Ii]ncome[^0-9\-\(]*" + f"({NUM_RE})"),
        ("withdraw", r"[Ww]ithdrawals? [Aa]nd [Dd]istributions?[^0-9\-\(]*" + f"({NUM_RE})"),
        ("ending", r"[Ee]nding [Cc]apital [Aa]ccount[^0-9\-\(]*" + f"({NUM_RE})"),
    ]
    for key, pat in pat_map:
        m = re.search(pat, text)
        if m:
            ca[key] = parse_amount(m.group(1))

    # Fallback to the reconciliation cover block (all-caps labels with dots).
    if ca["net_income"] == 0.0:
        m = re.search(r"TAX NET INCOME \(LOSS\)[^0-9\-\(]*" + f"({NUM_RE})", text)
        if m:
            ca["net_income"] = parse_amount(m.group(1))

    return ca


# ---------- Liabilities (Item K) ----------

def extract_liabilities(text: str) -> dict:
    """Extract K1 partner's share of liabilities (ending column)."""
    liab = {"nonrecourse": 0.0, "qnr": 0.0, "recourse": 0.0}

    # "Nonrecourse . . . . $ beginning $ ending"
    m = re.search(r"Nonrecourse[^$\n]*\$\s*" + f"({NUM_RE})" + r"[^\n]*\$\s*(" + NUM_RE + r")", text)
    if m:
        liab["nonrecourse"] = parse_amount(m.group(2))
    m = re.search(r"[Qq]ualified nonrecourse[^\n]*?\n[^\$]*\$\s*" + f"({NUM_RE})" + r"[^\n]*\$\s*(" + NUM_RE + r")", text)
    if m:
        liab["qnr"] = parse_amount(m.group(2))
    m = re.search(r"Recourse[^$\n]*\$\s*" + f"({NUM_RE})" + r"[^\n]*\$\s*(" + NUM_RE + r")", text)
    if m:
        liab["recourse"] = parse_amount(m.group(2))
    return liab


# ---------- Header fields ----------

def extract_header(text: str) -> dict:
    """Partnership name/EIN, partner name/EIN, partner type, DE info, tax year."""
    header: dict[str, Any] = {
        "partner_name": None,
        "partner_ein_ssn": None,
        "disregarded_entity_name": None,
        "disregarded_entity_tin": None,
        "issuer_entity": None,
        "issuer_ein": None,
        "partner_type": None,
        "final_k1": False,
        "tax_year": None,
        "entity_type": None,
        "form": "1065",
    }

    # Form type
    if re.search(r"Schedule K-1\s*\(Form 1120-?S\)", text):
        header["form"] = "1120S"
    elif re.search(r"Schedule K-1\s*\(Form 1041\)", text):
        header["form"] = "1041"

    # Tax year: "For calendar year 2024" or similar
    m = re.search(r"For calendar year\s+(\d{4})", text)
    if not m:
        m = re.search(r"\b(20\d{2})\s+Part III Partner", text)
    if m:
        header["tax_year"] = int(m.group(1))

    # Final K-1 checkbox
    # Look for X near "Final K-1"
    if re.search(r"X\s*Final K-1|Final K-1\s*X", text):
        header["final_k1"] = True

    # Partnership EIN — scan the next ~400 chars after the label for an EIN
    m = re.search(r"Partnership's employer identification number([\s\S]{0,400}?)(\d{2}-\d{7})", text)
    if m:
        header["issuer_ein"] = m.group(2)
    # Partnership name — specifically from Part I of the K-1 form (has "address, city, state" suffix)
    # not from the Statement A QBI page which uses plain "Partnership's name:"
    pm = re.search(r"Partnership's name, address, city, state[^\n]*\n([\s\S]{0,600}?)(^\s*[A-Z][A-Z0-9][A-Z0-9 ,.&'\-/]{3,}$)", text, re.MULTILINE)
    if pm:
        header["issuer_entity"] = pm.group(2).strip().rstrip(",")
    else:
        # Fallback: scan the cover letter for the first all-caps LLC/Inc name
        cm = re.search(r"^\s*([A-Z][A-Z0-9 ,.&'\-/]{5,}(?:LLC|LP|INC|CORP|LTD|PARTNERSHIP))\b", text, re.MULTILINE)
        if cm:
            header["issuer_entity"] = cm.group(1).strip().rstrip(",")

    # Partner TIN from Item E — scan next ~10 lines
    m = re.search(r"Partner's SSN or TIN[^\n]*([\s\S]{0,500}?)(\d{3}-\d{2}-\d{4}|\d{2}-\d{7})", text)
    if m:
        header["partner_ein_ssn"] = m.group(2)

    # Partner name from Item F — first ALL-CAPS line after the label
    fm = re.search(r"(?:Name, address, city, state, and ZIP code for partner entered in E|partner entered in E)[^\n]*\n([\s\S]{0,1000}?)(^\s+[A-Z][A-Z0-9][A-Z0-9 ,.&'\-/]{3,}$)", text, re.MULTILINE)
    if fm:
        cand = fm.group(2).strip().rstrip(",")
        # Filter false positives: box labels like "PTP" or short codes
        if len(cand) > 4 and cand not in ("PTP",):
            header["partner_name"] = cand

    # Partner type: G checkbox — "General partner or LLC member-manager" vs "Limited partner or other LLC member"
    if re.search(r"X\s*General partner or LLC", text):
        header["partner_type"] = "general"
    elif re.search(r"X\s*Limited partner", text) or re.search(r"Limited partner[^\n]*X", text):
        header["partner_type"] = "limited"

    # H2 disregarded entity
    m = re.search(r"If the partner is a disregarded entity[^\n]*\n\s*TIN\s*(\d{2,3}-?\d{2,3}-?\d{4,7})\s*Name\s*([A-Z][A-Z0-9 ,.&'\-/]+?)(?:\n|  {2,})", text)
    if m:
        header["disregarded_entity_tin"] = m.group(1).strip()
        header["disregarded_entity_name"] = m.group(2).strip()

    return header


# ---------- Box extraction (Part III) ----------

# Schedule K-1 Part III boxes: the form lays them out in two columns. Values
# appear on continuation lines prefixed with spaces and often a leading `*`.
# Strategy: for each box we look for "<boxnum> <label>" then scan forward for
# the next standalone numeric value within a window of lines.

BOX_LABELS = {
    "1":  ("box_1_ordinary",        r"Ordinary business income \(loss\)"),
    "2":  ("box_2_rental_re",       r"Net rental real estate income \(loss\)"),
    "3":  ("box_3_other_rental",    r"Other net rental income \(loss\)"),
    "5":  ("box_5_interest",        r"Interest income"),
    "6a": ("box_6a_ord_div",        r"Ordinary dividends"),
    "6b": ("box_6b_qual_div",       r"Qualified dividends"),
    "8":  ("box_8_st_cap",          r"Net short-term capital gain \(loss\)"),
    "9a": ("box_9a_lt_cap",         r"Net long-term capital gain \(loss\)"),
    "10": ("box_10_1231",           r"Net section 1231 gain \(loss\)"),
    "12": ("box_12_179",            r"Section 179 deduction"),
    "19": ("box_19_distributions",  r"Distributions"),
}

# Match box-value continuation line: whitespace, optional `*`, amount, optional trailing letters
VAL_LINE_RE = re.compile(r"^\s*\*?\s*(" + NUM_RE + r")\s*$")


def _find_box_value(text: str, box_num: str, label_pat: str, window: int = 6) -> float:
    """Find the value for a given box.

    Strategy: locate label line and column position. Scan the same column
    range on the next `window` lines for `*` + number OR a bare number.
    Two-column K-1 layout: left column ~ col 0-85, right column ~ col 85+.
    """
    lines = text.split("\n")
    label_re = re.compile(rf"\b{re.escape(box_num)}\s+{label_pat}")

    # Amount pattern that can appear anywhere on a continuation line
    val_same = re.compile(r"\*\s*(" + NUM_RE + r")")
    # Bare-number-only line (for left-column boxes that place value below)
    val_bare = re.compile(r"^\s*(" + NUM_RE + r")\.?\s*$")

    for i, line in enumerate(lines):
        m = label_re.search(line)
        if not m:
            continue
        label_col = m.start()
        # Column range for the value: within +/- 60 chars of label start,
        # but generally to the right of the label
        col_lo = max(0, label_col - 5)
        col_hi = label_col + 100

        # Stop scan at the next box label that appears in THIS column slice
        next_label_re = re.compile(r"\b\d{1,2}[a-z]?\s+[A-Z][a-z]")
        for j in range(1, window + 1):
            if i + j >= len(lines):
                break
            nxt = lines[i + j]
            slice_text = nxt[col_lo:col_hi] if len(nxt) > col_lo else ""
            # If the slice contains another box label, stop before examining further
            if j > 0 and next_label_re.search(slice_text):
                break
            # Try * + amount within this column slice
            ms = val_same.search(slice_text)
            if ms:
                return parse_amount(ms.group(1))
            # Try bare numeric line in the same slice
            mb = val_bare.match(slice_text)
            if mb:
                return parse_amount(mb.group(1))
        # Only use first match of this label
        break
    return 0.0


def extract_boxes(text: str) -> dict:
    """Extract boxes 1-20 that have direct numeric values."""
    out: dict[str, Any] = {}
    for box_num, (key, label_pat) in BOX_LABELS.items():
        out[key] = _find_box_value(text, box_num, label_pat)
    return out


def extract_box_20_codes(text: str) -> list[dict]:
    """Find Box 20 codes (Z = §199A, AJ, N, etc.). Scan all pages.

    Looks for standalone code marker lines and then any associated amount in
    the following lines. Also handles 'STMT' placeholders where the actual
    amount lives on a Statement A (QBI) page.
    """
    codes: list[dict] = []
    seen: set[str] = set()

    # Pattern 1: 'Z* STMT', 'AJ* STMT', 'N* STMT' — code present but amount on statement page
    for m in re.finditer(r"\b([A-Z]{1,3})\*?\s+STMT\b", text):
        code = m.group(1)
        if code in seen:
            continue
        seen.add(code)
        codes.append({"code": code, "amount": 0.0, "note": "see statement"})

    # Pattern 2: Statement A QBI — look for "Partnership's name" plus the rental/ordinary income breakout
    # This gives us the §199A (Code Z) rental income value.
    m = re.search(r"Rental income \(loss\)[^\n]*?(" + NUM_RE + r")", text)
    if m:
        val = parse_amount(m.group(1))
        if val != 0:
            # Upsert Z code
            found = next((c for c in codes if c["code"] == "Z"), None)
            if found:
                found["amount"] = val
                found["note"] = "§199A rental income per Statement A"
            else:
                codes.append({"code": "Z", "amount": val, "note": "§199A rental income per Statement A"})

    # Pattern 3: W-2 wages line (also §199A input)
    m = re.search(r"W-2 wages[^0-9\-\n]*?(" + NUM_RE + r")\s*$", text, re.MULTILINE)
    if m:
        val = parse_amount(m.group(1))
        if val:
            codes.append({"code": "Z-W2", "amount": val, "note": "§199A W-2 wages per Statement A"})

    return codes


# ---------- Main parse ----------

def parse_k1_text(text: str, source_path: str = "") -> dict:
    """Core parser: takes raw extracted text, returns a K-1 JSON dict."""
    header = extract_header(text)
    boxes = extract_boxes(text)
    capital = extract_capital_account(text)
    liabilities = extract_liabilities(text)
    box_20 = extract_box_20_codes(text)

    doc_type = "K-1-1065" if header["form"] == "1065" else ("K-1-1120S" if header["form"] == "1120S" else "K-1-1041")

    result: dict[str, Any] = {
        "doc_type": doc_type,
        "tax_year": header["tax_year"],
        "partner_name": header["partner_name"],
        "partner_ein_ssn": header["partner_ein_ssn"],
        "disregarded_entity_name": header["disregarded_entity_name"],
        "disregarded_entity_tin": header["disregarded_entity_tin"],
        "issuer_entity": header["issuer_entity"],
        "issuer_ein": header["issuer_ein"],
        "entity_type": None,  # user-annotated
        "partner_type": header["partner_type"],
        "final_k1": header["final_k1"],
        "at_risk": True,
        **boxes,
        "box_11_other": [],
        "box_13_other_ded": [],
        "box_14_se": [],
        "box_16_intl": None,
        "box_17_amt_items": [],
        "box_20_codes": box_20,
        "states": [],
        "capital_account": capital,
        "liabilities": liabilities,
        "source_path": source_path,
        "warnings": [],
    }

    # Validation warnings
    if result["final_k1"]:
        result["warnings"].append("Final K-1 flagged — verify entity exit")
    if not result["partner_ein_ssn"]:
        result["warnings"].append("Partner TIN not detected")
    if not result["issuer_ein"]:
        result["warnings"].append("Issuer EIN not detected")
    if not result["tax_year"]:
        result["warnings"].append("Tax year not detected")
    if doc_type == "K-1-1065" and not any(c["code"] == "Z" for c in box_20):
        result["warnings"].append("Box 20 code Z (§199A) not found — check footnote pages")

    return result


def parse_k1(pdf_path: str | Path) -> dict:
    """Parse a single-K-1 PDF."""
    pdf_path = str(Path(pdf_path).resolve())
    res = extract(pdf_path)
    if res.mode != "text":
        raise RuntimeError(f"PDF text extraction failed ({res.mode}); image OCR path not wired for K-1 yet: {pdf_path}")
    return parse_k1_text(res.text or "", source_path=pdf_path)


def parse_multi_k1(pdf_path: str | Path) -> list[dict]:
    """Parse a multi-K-1 PDF (e.g., full 1065 return with K-1 for each partner)."""
    pdf_path = str(Path(pdf_path).resolve())
    res = extract(pdf_path)
    if res.mode != "text":
        raise RuntimeError(f"PDF text extraction failed ({res.mode}) for {pdf_path}")
    text = res.text or ""

    # Split by Schedule K-1 page marker. Each K-1 starts with a header like
    # "Schedule K-1 ... Part III Partner's Share of Current Year Income,"
    # We split on "Part III Partner" since the form code "651123" precedes it.
    markers = [m.start() for m in re.finditer(r"Part III Partner's Share of Current Year Income", text)]
    if len(markers) <= 1:
        # Not actually multi — fall back to single parse
        return [parse_k1_text(text, source_path=pdf_path)]

    results = []
    for i, start in enumerate(markers):
        end = markers[i + 1] if i + 1 < len(markers) else len(text)
        # Include some context before the Part III marker (for Item L, liabilities, etc.)
        ctx_start = max(0, start - 4000)
        chunk = text[ctx_start:end]
        results.append(parse_k1_text(chunk, source_path=f"{pdf_path}#k1-{i+1}"))
    return results


# ---------- CLI ----------

def format_confirmation(result: dict) -> str:
    out = []
    fn = Path(result.get("source_path", "")).name
    out.append(f"Parsed: {fn}")
    out.append("")
    out.append(f"  Partner:       {result['partner_name']} ({result['partner_ein_ssn']})")
    if result.get("disregarded_entity_name"):
        out.append(f"  DE owner:      {result['disregarded_entity_name']} ({result['disregarded_entity_tin']})")
    out.append(f"  Issuer:        {result['issuer_entity']} ({result['issuer_ein']})")
    out.append(f"  Tax year:      {result['tax_year']}")
    out.append(f"  Partner type:  {result['partner_type']}")
    out.append(f"  Final K-1:     {result['final_k1']}")
    out.append("")
    nonzero = [(k, v) for k, v in result.items() if k.startswith("box_") and isinstance(v, (int, float)) and v != 0]
    if nonzero:
        out.append("  Boxes with values:")
        for k, v in nonzero:
            out.append(f"    {k:30s} {v:>15,.2f}")
    if result["box_20_codes"]:
        out.append("  Box 20 codes:")
        for c in result["box_20_codes"]:
            out.append(f"    {c['code']:4s} {c['amount']:>15,.2f}  {c.get('note','')}")
    ca = result["capital_account"]
    out.append(f"  Capital acct:  begin={ca['beginning']:,.2f} net={ca['net_income']:,.2f} withdraw={ca['withdraw']:,.2f} end={ca['ending']:,.2f}")
    li = result["liabilities"]
    out.append(f"  Liabilities:   NR={li['nonrecourse']:,.2f} QNR={li['qnr']:,.2f} REC={li['recourse']:,.2f}")
    if result["warnings"]:
        out.append("  Warnings:")
        for w in result["warnings"]:
            out.append(f"    ! {w}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse a Schedule K-1 PDF into the parsing.md JSON schema.")
    ap.add_argument("pdf", help="Path to K-1 PDF (single K-1) or return PDF (with --multi)")
    ap.add_argument("--multi", action="store_true", help="PDF contains multiple K-1s (e.g., full 1065 return)")
    ap.add_argument("--json", action="store_true", help="Print JSON only (no confirmation prompt)")
    ap.add_argument("--no-confirm", action="store_true", help="Skip confirmation, never write")
    ap.add_argument("--write", action="store_true", help="If approved, write to .parsed/ dir alongside the source (requires scope context)")
    args = ap.parse_args()

    if args.multi:
        results = parse_multi_k1(args.pdf)
    else:
        results = [parse_k1(args.pdf)]

    if args.json:
        print(json.dumps(results if args.multi else results[0], indent=2, default=str))
        return 0

    for r in results:
        print(format_confirmation(r))
        print()

    if args.no_confirm or not args.write:
        # Always also dump JSON for visibility
        print("\n--- JSON ---")
        print(json.dumps(results if args.multi else results[0], indent=2, default=str))
        return 0

    # Write path (requires user confirmation)
    resp = input("Write to .parsed/ ? [yes / edit / skip]: ").strip().lower()
    if resp not in ("yes", "y"):
        print("Skipped.")
        return 0
    # Write to same dir as source
    src = Path(args.pdf)
    parsed_dir = src.parent / ".parsed"
    parsed_dir.mkdir(exist_ok=True)
    for i, r in enumerate(results):
        slug = src.stem.lower().replace(" ", "-")
        if args.multi:
            slug = f"{slug}-partner-{i+1}"
        out_path = parsed_dir / f"{slug}.json"
        out_path.write_text(json.dumps(r, indent=2, default=str))
        print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

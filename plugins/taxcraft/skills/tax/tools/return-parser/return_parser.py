#!/usr/bin/env python3
"""
return_parser — Parse Form 1065 / 1120 / 1120-S returns into structured JSON.

Library:
    from return_parser import parse_return
    result = parse_return("/path/to/return.pdf")

CLI:
    python3 return_parser.py "path/to/return.pdf" [--json] [--no-confirm]

Auto-detects form type from the page-1 header. Uses pdf-extractor/pdf_extract.py
for text extraction (pdftotext -layout). Resilient: missing fields default to
0 or null and are appended to `anomalies` rather than raising.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

# Import shared pdf extractor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pdf-extractor"))
from pdf_extract import extract  # noqa: E402


# ---------------------------------------------------------------------------
# Amount parsing helpers
# ---------------------------------------------------------------------------

# An amount is a US-style number: optional ($ or - or leading paren),
# digits with properly-placed thousands commas (e.g. 1,234 or 12,345,678),
# optional decimals, optional trailing ')' or '.'.
_AMOUNT_RE = re.compile(
    r"\(?-?\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\)?\.?"
)


def to_amount(raw: str) -> Optional[float]:
    """Parse a string amount. Parentheses = negative. Trailing '.' stripped.
    Returns None if not parseable, 0 for empty.
    """
    if raw is None:
        return None
    s = raw.strip().replace("$", "").replace(",", "").replace(" ", "")
    if not s:
        return None
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    if s.endswith("."):
        s = s[:-1]
    if s.startswith("-"):
        neg = not neg
        s = s[1:]
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if neg else val


def _looks_like_real_amount(tok: str) -> bool:
    """Reject bare small integers that look like line-label refs (e.g. '1', '22', '1c').
    Accept if token has: parentheses, thousands-comma, decimal with digits, leading
    minus, dollar sign, or is >= 4 digits long. A trailing-period-only token
    (e.g. '22.') is treated as a bare integer (many form lines end '. . . 22.').
    """
    t = tok.strip()
    if not t:
        return False
    if "(" in t or ")" in t or "$" in t:
        return True
    if "," in t:  # thousands separator
        return True
    # decimal with fractional digits (not just trailing period)
    if re.search(r"\.\d", t):
        return True
    if t.startswith("-"):
        return True
    digits = re.sub(r"\D", "", t)
    return len(digits) >= 4


def last_amount_on_line(line: str) -> Optional[float]:
    """Return the rightmost numeric amount on a line, or None.
    Excludes:
      - bare small-integer line-label refs ('1c', '22', '23')
      - form references like 'Form 1125-A' or '(Form 1120)' that appear mid-line
    Requires the amount to be in the right-aligned column (preceded by 2+ spaces
    or dot-leaders, and not embedded in a word/hyphen).
    """
    if not line:
        return None
    # Iterate matches with position so we can inspect left-context
    best = None
    for m in _AMOUNT_RE.finditer(line):
        tok = m.group(0)
        if not re.search(r"\d", tok):
            continue
        if not _looks_like_real_amount(tok):
            continue
        start = m.start()
        left = line[max(0, start - 2):start]
        # Reject if immediately preceded by letter/hyphen (e.g., '1125-A', 'Form ')
        # or by a char that means it's glued to a word.
        # Accept only if preceded by whitespace, tab, dot-leader, '$', or start.
        if start > 0:
            prev = line[start - 1]
            if prev not in " \t.$(":
                # glued to word (e.g. '1125' in '1125-A' has 'm ' before it actually — check more)
                continue
        # Also reject if followed by letter/hyphen (e.g. '1125-A' where tok='1125' then '-A')
        end = m.end()
        if end < len(line):
            nxt = line[end]
            if nxt in "-" or (nxt.isalpha() and tok.strip("().,$-").isdigit() and "." not in tok and "," not in tok):
                continue
        best = tok  # keep last valid match
    if best is None:
        return None
    return to_amount(best)


def amounts_on_line(line: str) -> list[float]:
    """Return all real-looking dollar amounts on a line (excludes line labels /
    form refs that appear mid-line adjacent to letters/hyphens)."""
    out = []
    for m in _AMOUNT_RE.finditer(line):
        tok = m.group(0)
        if not re.search(r"\d", tok):
            continue
        if not _looks_like_real_amount(tok):
            continue
        start = m.start()
        if start > 0:
            prev = line[start - 1]
            if prev not in " \t.$(":
                continue
        end = m.end()
        if end < len(line):
            nxt = line[end]
            if nxt == "-" or (nxt.isalpha() and tok.strip("().,$-").isdigit() and "." not in tok and "," not in tok):
                continue
        v = to_amount(tok)
        if v is not None:
            out.append(v)
    return out


# ---------------------------------------------------------------------------
# Form detection
# ---------------------------------------------------------------------------

def detect_form(text: str) -> str:
    """Return '1065-Return' | '1120-Return' | '1120-S-Return' | 'Unknown-Return'."""
    head = "\n".join(text.splitlines()[:200])
    # Order matters: check 1120-S before 1120
    if re.search(r"Form\s*1120-?S\b|U\.S\. Income Tax Return for an S Corporation", head, re.I):
        return "1120-S-Return"
    if re.search(r"\bForm\s*1065\b|U\.S\. Return of Partnership Income", head, re.I):
        return "1065-Return"
    if re.search(r"\bForm\s*1120\b|U\.S\. Corporation Income Tax Return", head, re.I):
        return "1120-Return"
    return "Unknown-Return"


# ---------------------------------------------------------------------------
# Shared extraction helpers
# ---------------------------------------------------------------------------

EIN_RE = re.compile(r"\b(\d{2}-\d{7})\b")


def extract_tax_year(text: str) -> Optional[int]:
    head = "\n".join(text.splitlines()[:80])
    m = re.search(r"For calendar year (\d{4})", head)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(20\d{2})\s*Federal Tax Return", head)
    if m:
        return int(m.group(1))
    # Try leading "2024 Federal Tax Return Summary" or similar
    m = re.search(r"(20\d{2})", head)
    return int(m.group(1)) if m else None


def extract_fiscal_period(text: str, tax_year: Optional[int]) -> dict:
    """Extract begin/end dates. Default to calendar year based on tax_year."""
    # TurboTax often prints: "tax year beginning  Dec 4  , 2024, ending  Oct 31 , 20 25"
    m = re.search(
        r"tax year beginning\s+([A-Za-z]+\s+\d{1,2})\s*,\s*(\d{4}),?\s*ending\s+([A-Za-z]+\s+\d{1,2})\s*,\s*20\s*(\d{2,4})",
        text,
    )
    if m:
        try:
            import datetime as _dt
            b = _dt.datetime.strptime(f"{m.group(1)} {m.group(2)}", "%b %d %Y")
            end_year = m.group(4)
            if len(end_year) == 2:
                end_year = "20" + end_year
            e = _dt.datetime.strptime(f"{m.group(3)} {end_year}", "%b %d %Y")
            return {"begin": b.strftime("%Y-%m-%d"), "end": e.strftime("%Y-%m-%d")}
        except Exception:
            pass
    if tax_year:
        return {"begin": f"{tax_year}-01-01", "end": f"{tax_year}-12-31"}
    return {"begin": None, "end": None}


def extract_entity_header(text: str, form: str) -> tuple[Optional[str], Optional[str]]:
    """Return (entity_name, ein). Scans a window around the form header."""
    lines = text.splitlines()
    ein = None
    name = None

    # Find the form's page-1 anchor (the OMB / "Form 1065|1120[-S]" header)
    anchor = 0
    for i, ln in enumerate(lines[:400]):
        if re.search(r"U\.S\. Return of Partnership Income|U\.S\. Corporation Income Tax Return|Income Tax Return for an S Corporation", ln):
            anchor = i
            break

    window = "\n".join(lines[anchor:anchor + 80])
    m = EIN_RE.search(window)
    if m:
        ein = m.group(1)

    # Entity name: look at the 12 lines following the form-header anchor and
    # pick the chunk that most looks like an entity name (LLC/Inc/Corp/etc.)
    ENTITY_SUFFIX_RE = re.compile(
        r"\b(LLC|L\.L\.C\.|Inc\.?|Corp\.?|Corporation|Company|Co\.|LP|L\.P\.|LLP|Ltd\.?|Trust|Foundation|Holdings|Partners)\b",
        re.I,
    )
    SKIP_CHUNK = re.compile(
        r"^(TYPE|OR|PRINT|Department|Internal|Go to|For|Number,|City or|Name of|Name\s*$|Principal|Rental|Residential|Commercial|Consolidated)",
        re.I,
    )

    best_name = None
    for j in range(1, 20):
        if anchor + j >= len(lines):
            break
        cand = lines[anchor + j]
        parts = [p.strip() for p in re.split(r"\s{2,}", cand) if p.strip()]
        for p in parts:
            if EIN_RE.search(p):
                continue
            if SKIP_CHUNK.match(p):
                continue
            if not re.search(r"[A-Za-z]", p):
                continue
            if len(p) < 3 or len(p) > 80:
                continue
            # Strong signal: has entity suffix
            if ENTITY_SUFFIX_RE.search(p):
                name = p
                break
            # Weak signal: all-caps multi-word phrase (e.g. NUMERICAL INVESTMENTS LLC in caps)
            if re.match(r"^[A-Z][A-Z0-9 .,&'\-]{4,}$", p) and best_name is None:
                best_name = p
        if name:
            break
    if not name:
        name = best_name

    # Fallback: scan top of document for "<NAME>\n<address>\n<city, state zip>"
    if not name:
        for i, ln in enumerate(lines[:40]):
            s = ln.strip()
            if re.match(r"^[A-Z][A-Za-z0-9 .,&'\-]{3,}(LLC|Inc|Corp|Corporation|Company|LP|LLP|Ltd)\b", s):
                name = s
                break

    return name, ein


def find_line_amount(text: str, patterns: list[str], *, context_lines: int = 0) -> Optional[float]:
    """Find first line matching one of the anchor patterns, return last amount on that line.
    If context_lines > 0 and no amount on the anchor line, look at following N lines.
    """
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        for pat in patterns:
            if re.search(pat, ln):
                amt = last_amount_on_line(ln)
                if amt is not None:
                    return amt
                for k in range(1, context_lines + 1):
                    if i + k < len(lines):
                        amt2 = last_amount_on_line(lines[i + k])
                        if amt2 is not None:
                            return amt2
                return None
    return None


def section_slice(text: str, start_pat: str, end_pat: Optional[str] = None) -> str:
    """Return the substring starting at the first line matching start_pat,
    ending before the first line matching end_pat (if provided)."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.search(start_pat, ln):
            start = i
            break
    if start is None:
        return ""
    if end_pat is None:
        return "\n".join(lines[start:])
    for j in range(start + 1, len(lines)):
        if re.search(end_pat, lines[j]):
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


# ---------------------------------------------------------------------------
# Page 1 P&L extractors
# ---------------------------------------------------------------------------

def page1_pnl_1065(text: str, anomalies: list) -> dict:
    # 1065 page 1 slice: from form header through line 23
    body = section_slice(text, r"U\.S\. Return of Partnership Income", r"^\s*Form 1065 \(20\d{2}\)")
    if not body:
        body = text
    gr = find_line_amount(body, [r"^\s*1a\s+Gross receipts or sales"])
    cogs = find_line_amount(body, [r"^\s*2\s+Cost of goods sold"])
    gp = find_line_amount(body, [r"^\s*3\s+Gross profit"])
    total_income = find_line_amount(body, [r"^\s*8\s+Total income \(loss\)"])
    total_deduct = find_line_amount(body, [r"^\s*22\s+Total deductions"])
    ord_inc = find_line_amount(body, [r"^\s*23\s+Ordinary business income"])

    return {
        "gross_receipts": gr if gr is not None else 0,
        "cogs": cogs if cogs is not None else 0,
        "gross_profit": gp if gp is not None else 0,
        "total_income": total_income if total_income is not None else 0,
        "total_deductions": total_deduct if total_deduct is not None else 0,
        "ordinary_income_loss": ord_inc if ord_inc is not None else 0,
    }


def page1_pnl_1120(text: str, anomalies: list) -> dict:
    body = section_slice(text, r"U\.S\. Corporation Income Tax Return", r"^\s*Form 1120 \(20\d{2}\)")
    if not body:
        body = text
    gr = find_line_amount(body, [r"^\s*1c\s+Balance\. Subtract line 1b"])
    cogs = find_line_amount(body, [r"^\s*2\s+Cost of goods sold"])
    gp = find_line_amount(body, [r"^\s*3\s+Gross profit"])
    total_income = find_line_amount(body, [r"^\s*11\s+Total income"])
    total_deduct = find_line_amount(body, [r"^\s*27\s+Total deductions"])
    ord_inc = find_line_amount(body, [r"^\s*30\s+Taxable income\.", r"^\s*28\s+Taxable income before"])

    return {
        "gross_receipts": gr if gr is not None else 0,
        "cogs": cogs if cogs is not None else 0,
        "gross_profit": gp if gp is not None else 0,
        "total_income": total_income if total_income is not None else 0,
        "total_deductions": total_deduct if total_deduct is not None else 0,
        "ordinary_income_loss": ord_inc if ord_inc is not None else 0,
    }


def page1_pnl_1120s(text: str, anomalies: list) -> dict:
    body = section_slice(text, r"Income Tax Return for an S Corporation", r"^\s*Form 1120-S")
    if not body:
        body = text
    gr = find_line_amount(body, [r"^\s*1c\s+"])
    cogs = find_line_amount(body, [r"^\s*2\s+Cost of goods sold"])
    gp = find_line_amount(body, [r"^\s*3\s+Gross profit"])
    total_income = find_line_amount(body, [r"^\s*6\s+Total income \(loss\)"])
    total_deduct = find_line_amount(body, [r"^\s*20\s+Total deductions"])
    ord_inc = find_line_amount(body, [r"^\s*21\s+Ordinary business income"])

    return {
        "gross_receipts": gr if gr is not None else 0,
        "cogs": cogs if cogs is not None else 0,
        "gross_profit": gp if gp is not None else 0,
        "total_income": total_income if total_income is not None else 0,
        "total_deductions": total_deduct if total_deduct is not None else 0,
        "ordinary_income_loss": ord_inc if ord_inc is not None else 0,
    }


# ---------------------------------------------------------------------------
# Schedule B (1065) — elections
# ---------------------------------------------------------------------------

def schedule_b_elections_1065(text: str) -> dict:
    # Accounting method from page 1
    method = None
    m = re.search(r"H Check accounting method:.*?Cash.*?Accrual", text, re.S)
    # Harder to detect check-marks in text layout; fall back to searching for an X near Cash/Accrual
    # We'll look on the H line for "X" markers
    for ln in text.splitlines():
        if "H Check accounting method" in ln:
            # The next couple lines often contain the choice
            pass
    # Try direct: in the flattened text, box checks usually show as "X" in parens or nothing
    # Safer: look for nearby "X" token
    idx = text.find("H Check accounting method")
    if idx >= 0:
        window = text[idx:idx + 400]
        # Look for which of "Cash" or "Accrual" has an X close to it
        # Commonly TurboTax marks: "(1)   X  Cash"  or similar
        cash_x = re.search(r"\(\s*1\s*\)\s*X\s*Cash|X\s*Cash|Cash\s*X", window)
        accrual_x = re.search(r"\(\s*2\s*\)\s*X\s*Accrual|X\s*Accrual|Accrual\s*X", window)
        if cash_x and not accrual_x:
            method = "cash"
        elif accrual_x and not cash_x:
            method = "accrual"

    # Aggregated activities (box K(1))
    aggregated = bool(re.search(r"K Check if partnership:.*?Aggregated activities.*?X", text, re.S)) or \
                 bool(re.search(r"Aggregated activities for section 465.*?X", text, re.S))

    # Any partner amended K-1 (Sched B question — look for "Amended K-1" checkboxes)
    any_amended = bool(re.search(r"Amended K-1\s*\n?.*?X", text))

    # BBA opt-out (§6221(b)) — Schedule B line 33
    bba_opt = bool(re.search(
        r"electing out of the centralized partnership audit regime under section 6221\(b\)\??.*?Yes", text, re.S
    )) or bool(re.search(r"ELECTED OUT OF THE CENTRALIZED\s+PARTNERSHIP AUDIT REGIME", text, re.S | re.I))

    return {
        "accounting_method": method,
        "aggregated_activities": aggregated,
        "any_partner_amended_k1": any_amended,
        "bba_opt_out_6221b": bba_opt,
    }


# ---------------------------------------------------------------------------
# Schedule K (1065) — separately stated items
# ---------------------------------------------------------------------------

def schedule_k_1065(text: str, anomalies: list) -> dict:
    body = section_slice(
        text,
        r"Schedule K\s+Partners. Distributive Share Items|Schedule K\s+Shareholders. Pro Rata Share Items",
        r"Analysis of Net Income|Schedule L\s+Balance Sheets",
    )
    if not body:
        body = text

    def _get(pats):
        return find_line_amount(body, pats) or 0

    return {
        "line_1_ordinary": _get([r"^\s*1\s+Ordinary business income"]),
        "line_2_rental_re": _get([r"^\s*2\s+Net rental real estate income"]),
        "line_5_interest": _get([r"^\s*5\s+Interest income"]),
        "line_6a_ord_div": _get([r"^\s*6a?\s.*Ordinary dividends", r"a Ordinary dividends"]),
        "line_6b_qual_div": _get([r"^\s*6b\s+Qualified dividends", r"b Qualified dividends"]),
        "line_8_st_cap": _get([r"^\s*8\s+Net short-term capital gain"]),
        "line_9a_lt_cap": _get([r"^\s*9a\s+Net long-term capital gain"]),
        "line_10_1231": _get([r"^\s*10\s+Net section 1231 gain"]),
        "line_12_179": _get([r"^\s*12\s+Section 179 deduction"]),
        "line_13_other_ded": _get([r"^\s*13e\s+Other deductions", r"^\s*13\s+"]),
        "line_19_distributions": _get([r"^\s*19a\s+Distributions of cash"]),
        "line_20_other": [],  # statement attachments captured in stmt_pages
    }


# ---------------------------------------------------------------------------
# Schedule L — balance sheet (shared)
# ---------------------------------------------------------------------------

def schedule_l(text: str) -> dict:
    body = section_slice(
        text,
        r"Schedule L\s+Balance Sheets per Books",
        r"Schedule M-1|Schedule M-?2",
    )

    def _row(pat):
        for ln in body.splitlines():
            if re.search(pat, ln):
                amts = amounts_on_line(ln)
                # Schedule L typically has (a)(b)(c)(d) columns: beginning subtotal, ending subtotal
                # For "Total assets" rows the important numbers are in (b) and (d) columns.
                if len(amts) >= 2:
                    return amts[-2], amts[-1]
                if len(amts) == 1:
                    return None, amts[0]
        return None, None

    total_assets_b, total_assets_e = _row(r"Total assets")
    total_liab_cap_b, total_liab_cap_e = _row(r"Total liabilities and (capital|shareholders)")
    # Partners' capital accounts (1065) / Retained earnings Unappropriated (1120)
    cap_b, cap_e = _row(r"Partners. capital accounts|Retained earnings.?Unappropriated")

    return {
        "beginning": {
            "total_assets": total_assets_b or 0,
            "total_liab": 0,  # not individually broken out robustly
            "total_capital": cap_b or 0,
        },
        "ending": {
            "total_assets": total_assets_e or 0,
            "total_liab": 0,
            "total_capital": cap_e or 0,
        },
    }


# ---------------------------------------------------------------------------
# Schedule M-1 / M-2 (shared)
# ---------------------------------------------------------------------------

def schedule_m1(text: str) -> dict:
    body = section_slice(
        text,
        r"Schedule M-1\s+Reconciliation of Income",
        r"Schedule M-?2",
    )
    net_book = find_line_amount(body, [r"^\s*1\s+Net income \(loss\) per books"]) or 0
    income_return = find_line_amount(body, [
        r"Income \(loss\).*?Analysis of Net Income.*?line 1\)",
        r"Income \(page 1, line 28\)",
    ]) or 0
    return {
        "net_income_per_books": net_book,
        "additions": [],
        "subtractions": [],
        "income_per_return": income_return,
    }


def schedule_m2_capital(text: str) -> dict:
    """1065 M-2: partners' capital."""
    body = section_slice(
        text,
        r"Schedule M-2\s+Analysis of Partners. Capital Accounts",
        r"Form 8825|Schedule K-1|^Form 1065",
    )
    return {
        "beginning": find_line_amount(body, [r"^\s*1\s+Balance at beginning of year"]) or 0,
        "contributions": find_line_amount(body, [r"^\s*2\s+Capital contributed"]) or 0,
        "net_income": find_line_amount(body, [r"^\s*3\s+Net income \(loss\)"]) or 0,
        "distributions": find_line_amount(body, [r"^\s*6\s+Distributions"]) or 0,
        "ending": find_line_amount(body, [r"Balance at end of year"]) or 0,
    }


def retained_earnings_m2(text: str) -> dict:
    """1120 M-2: unappropriated retained earnings."""
    body = section_slice(
        text,
        r"Schedule M-2\s+Analysis of Unappropriated Retained Earnings",
        r"Schedule G|^Form 1120|SCHEDULE G",
    )
    return {
        "beginning": find_line_amount(body, [r"^\s*1\s+Balance at beginning of year"]) or 0,
        "net_income_per_books": find_line_amount(body, [r"^\s*2\s+Net income \(loss\) per books"]) or 0,
        "other_increases": find_line_amount(body, [r"^\s*3\s+Other increases"]) or 0,
        "distributions": find_line_amount(body, [r"^\s*5\s+Distributions"]) or 0,
        "other_decreases": find_line_amount(body, [r"^\s*6\s+Other decreases"]) or 0,
        "ending": find_line_amount(body, [r"Balance at end of year"]) or 0,
    }


# ---------------------------------------------------------------------------
# 1120 Schedule J — tax computation
# ---------------------------------------------------------------------------

def schedule_j_1120(text: str) -> dict:
    body = section_slice(text, r"Schedule J\s+Tax Computation", r"Schedule K\s+Other Information")
    return {
        "income_tax": find_line_amount(body, [r"^\s*1a\s+Income tax"]) or 0,
        "total_tax_before_credits": find_line_amount(body, [r"^\s*11a\s+Total tax before deferred"]) or 0,
        "total_tax": find_line_amount(body, [
            r"^\s*12\s+Total tax\.",
            r"^\s*11\s+Total tax\.",
        ]) or 0,
        "total_payments_credits": find_line_amount(body, [r"Total payments and credits"]) or 0,
    }


# ---------------------------------------------------------------------------
# Partners (1065) / Shareholders (1120-S) K-1 summaries
# ---------------------------------------------------------------------------

def extract_partners_1065(text: str) -> list[dict]:
    """Split on 'Schedule K-1' blocks and pull name, SSN/EIN, ownership %s, final flag."""
    # Split into blocks starting at each "Schedule K-1" header that's a real K-1 (has Part I/II)
    blocks = re.split(r"(?=Schedule K-1\s*\n?\(Form 1065\))", text)
    partners: list[dict] = []
    for blk in blocks:
        if "Part II       Information About the Partner" not in blk and "Information About the Partner" not in blk:
            continue
        # Name — after "F  Name, address..." take next non-blank line
        name = None
        mname = re.search(r"Name, address, city, state, and ZIP code for partner[^\n]*\n\s*([^\n]+)", blk)
        if mname:
            name = mname.group(1).strip()
        # SSN/TIN
        ssn = None
        mssn = re.search(r"Partner.s SSN or TIN[^\n]*\n(?:[^\n]*\n){0,3}?\s*([\d]{2,3}-?[\d]{2}-?[\d]{4}|\d{2}-\d{7})", blk)
        if not mssn:
            mssn = re.search(r"\b(\d{3}-\d{2}-\d{4})\b", blk)
        if mssn:
            ssn = mssn.group(1)
        # Final K-1 flag
        final_k1 = bool(re.search(r"Final K-1\s*(?:\n[^\n]*X|\s*X)", blk))
        # Ownership percentages — row pattern "Profit  25.00000 %   25.00000 %"
        def _pct(label):
            m = re.search(rf"{label}\s+([\d.]+)\s*%\s+([\d.]+)\s*%", blk)
            if m:
                try:
                    return float(m.group(2))
                except ValueError:
                    return 0
            return 0

        partners.append({
            "name": name or "",
            "ein_ssn": ssn or "",
            "pct_profits_end": _pct("Profit"),
            "pct_loss_end": _pct("Loss"),
            "pct_capital_end": _pct("Capital"),
            "final_k1": final_k1,
        })
    return partners


# ---------------------------------------------------------------------------
# STMT pages — capture raw text keyed by statement number
# ---------------------------------------------------------------------------

def extract_stmt_pages(text: str) -> dict:
    """Grab 'Statement N' sections as raw strings."""
    out: dict = {}
    # Find "Statement NNN" or "Other Deductions Statement"
    pattern = re.compile(r"(?m)^(.*?Statement(?:\s+\d+)?)\s*$")
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r"\s*(Other Deductions Statement|Statement\s+(\d+)|Other\s+Statement\s+(\d+))", ln)
        if not m:
            continue
        key = m.group(1).strip()
        # Grab next up-to-40 lines until blank pattern / next form header
        body_lines = []
        for j in range(i + 1, min(i + 40, len(lines))):
            nxt = lines[j]
            if re.match(r"^(Form \d|Schedule [A-Z]|Page \d|\s*$)", nxt) and body_lines:
                break
            body_lines.append(nxt)
        if body_lines:
            out[key] = "\n".join(body_lines).strip()
    return out


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def parse_return(pdf_path: str | Path) -> dict:
    pdf_path = Path(pdf_path).resolve()
    anomalies: list[str] = []

    result = extract(pdf_path)
    if result.mode != "text" or not result.text:
        return {
            "doc_type": "Unknown-Return",
            "error": "Could not extract text from PDF",
            "pdf_path": str(pdf_path),
            "anomalies": ["pdf_extract failed to return text mode"],
        }

    text = result.text
    form = detect_form(text)
    if form == "Unknown-Return":
        anomalies.append("Could not detect form type from page-1 header")

    tax_year = extract_tax_year(text)
    entity_name, ein = extract_entity_header(text, form)
    if not entity_name:
        anomalies.append("entity_name not found")
    if not ein:
        anomalies.append("entity_ein not found")

    fiscal = extract_fiscal_period(text, tax_year)
    preparer = "self" if re.search(r"Self-Prepared", text) else "firm"
    return_type = "amended" if re.search(r"\(5\)\s*X\s*Amended return|Amended return\s*X", text) else "original"

    out: dict[str, Any] = {
        "doc_type": form,
        "tax_year": tax_year,
        "entity_name": entity_name,
        "entity_ein": ein,
        "fiscal_period": fiscal,
        "preparer": preparer,
        "return_type": return_type,
    }

    if form == "1065-Return":
        out["page_1_pnl"] = page1_pnl_1065(text, anomalies)
        out["schedule_b_elections"] = schedule_b_elections_1065(text)
        out["schedule_k_separately_stated"] = schedule_k_1065(text, anomalies)
        out["schedule_l_balance_sheet"] = schedule_l(text)
        out["schedule_m1_book_tax"] = schedule_m1(text)
        out["schedule_m2_capital"] = schedule_m2_capital(text)
        out["partners"] = extract_partners_1065(text)
    elif form == "1120-Return":
        out["page_1_pnl"] = page1_pnl_1120(text, anomalies)
        out["schedule_j"] = schedule_j_1120(text)
        out["schedule_l_balance_sheet"] = schedule_l(text)
        out["schedule_m1_book_tax"] = schedule_m1(text)
        out["retained_earnings_m2"] = retained_earnings_m2(text)
        out["partners"] = []  # shareholders not on 1120 return body
    elif form == "1120-S-Return":
        out["page_1_pnl"] = page1_pnl_1120s(text, anomalies)
        out["schedule_b_elections"] = schedule_b_elections_1065(text)  # similar questions
        out["schedule_k_separately_stated"] = schedule_k_1065(text, anomalies)
        out["schedule_l_balance_sheet"] = schedule_l(text)
        out["schedule_m1_book_tax"] = schedule_m1(text)
        out["schedule_m2_capital"] = schedule_m2_capital(text)
        out["partners"] = extract_partners_1065(text)  # shareholders in same K-1 layout

    out["stmt_pages"] = extract_stmt_pages(text)
    out["anomalies"] = anomalies
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_summary(res: dict) -> None:
    print(f"doc_type        : {res.get('doc_type')}")
    print(f"tax_year        : {res.get('tax_year')}")
    print(f"entity_name     : {res.get('entity_name')}")
    print(f"entity_ein      : {res.get('entity_ein')}")
    fp = res.get("fiscal_period") or {}
    print(f"fiscal_period   : {fp.get('begin')} .. {fp.get('end')}")
    print(f"preparer        : {res.get('preparer')}")
    print(f"return_type     : {res.get('return_type')}")
    pnl = res.get("page_1_pnl") or {}
    print("page_1_pnl:")
    for k in ("gross_receipts", "cogs", "gross_profit", "total_income", "total_deductions", "ordinary_income_loss"):
        print(f"  {k:24s}: {pnl.get(k)}")
    if res.get("partners"):
        print(f"partners        : {len(res['partners'])}")
        for p in res["partners"]:
            print(f"  - {p.get('name')!r} {p.get('ein_ssn')} P/L/C={p.get('pct_profits_end')}/{p.get('pct_loss_end')}/{p.get('pct_capital_end')} final={p.get('final_k1')}")
    anoms = res.get("anomalies") or []
    print(f"anomalies       : {len(anoms)}")
    for a in anoms:
        print(f"  - {a}")
    stmt = res.get("stmt_pages") or {}
    if stmt:
        print(f"stmt_pages keys : {list(stmt.keys())}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse a Form 1065/1120/1120-S return PDF into JSON.")
    ap.add_argument("pdf", help="Path to return PDF")
    ap.add_argument("--json", action="store_true", help="Print full JSON (otherwise summary)")
    ap.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"Error: file not found: {pdf}", file=sys.stderr)
        return 2

    if not args.no_confirm and sys.stdin.isatty():
        print(f"Parse: {pdf}")
        resp = input("Proceed? [Y/n] ").strip().lower()
        if resp and resp not in ("y", "yes"):
            print("Aborted.")
            return 1

    result = parse_return(pdf)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

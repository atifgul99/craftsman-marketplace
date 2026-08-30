#!/usr/bin/env python3
"""
parse-verify — arithmetic and tax-law invariants over parsed tax JSON.

This is Layer B of the extraction-confidence system described in
`parsing.md` → "Verify before writing". Layer A (differential extraction)
catches transcription errors. Layer B catches errors that BOTH extractors
would faithfully reproduce — including issuer errors, which no amount of
extraction consensus can detect.

An invariant here does not ask "did we read this correctly?" It asks
"can this document be internally consistent at all?" A capital account
that does not roll forward is wrong no matter who read it.

Usage:
    python3 verify.py <file.json>              # verify one parsed doc
    python3 verify.py <dir>/.parsed/           # verify all + cross-doc checks
    python3 verify.py <dir>/.parsed/ --json    # machine-readable output
    python3 verify.py <path> --min-severity HIGH

Exit codes:
    0 = no findings at or above --min-severity (default MEDIUM)
    1 = findings present
    2 = usage/IO error

Pure stdlib. No network. Never modifies anything.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Optional

# Absolute dollar tolerance for arithmetic ties. Parsed values are whole
# dollars; anything beyond this is a real break, not a rounding artifact.
TOLERANCE = 1.0

SEVERITY_ORDER = {"INFO": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass
class Finding:
    severity: str          # CRITICAL | HIGH | MEDIUM | INFO
    check: str             # stable id, e.g. "K1.item_l.rollforward"
    doc: str               # filename
    message: str           # what is wrong
    detail: str = ""       # the arithmetic, shown so a human can re-derive it
    fields: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Tolerant field access
#
# Parsed JSON in the wild does not match the schema doc exactly: Item K
# appears as `nonrecourse`, `nonrecourse_beginning`, or `nonrecourse_beg`
# depending on which pass produced the file. Look up by alias rather than
# assuming one spelling.
# --------------------------------------------------------------------------

def pick(d: Optional[dict], *names: str, default: Any = None) -> Any:
    """First present, non-None value among `names`."""
    if not isinstance(d, dict):
        return default
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return default


def num(v: Any, default: float = 0.0) -> float:
    """Coerce to float; treat unparseable/absent as `default`."""
    if isinstance(v, bool):
        return default
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.replace(",", "").replace("$", "").strip()
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        try:
            return float(s)
        except ValueError:
            return default
    return default


def item_k_total(item_k: Optional[dict], which: str = "ending") -> float:
    """
    Partner's share of partnership liabilities (Item K).

    `which` selects beginning- or end-of-year where the file distinguishes
    them; files that carry a single value are returned as-is.
    """
    if not isinstance(item_k, dict):
        return 0.0
    # Some files nest by year-end instead of suffixing the key:
    #   {"beginning": {"nonrecourse": 0, ...}, "ending": {...}}
    nested = item_k.get(which)
    if isinstance(nested, dict):
        return (num(pick(nested, "nonrecourse"))
                + num(pick(nested, "qnr"))
                + num(pick(nested, "recourse")))
    if which == "beginning":
        return (
            num(pick(item_k, "nonrecourse_beginning", "nonrecourse_beg", "nonrecourse"))
            + num(pick(item_k, "qnr_beginning", "qnr_beg", "qnr"))
            + num(pick(item_k, "recourse_beginning", "recourse_beg", "recourse"))
        )
    return (
        num(pick(item_k, "nonrecourse_ending", "nonrecourse_end", "nonrecourse"))
        + num(pick(item_k, "qnr_ending", "qnr_end", "qnr"))
        + num(pick(item_k, "recourse_ending", "recourse_end", "recourse"))
    )


# Boxes that carry allocated income/loss. Used to decide whether a K-1 has
# any activity at all, and to size a loss against basis for §704(d).
INCOME_BOXES = [
    "box_1_ordinary", "box_2_rental_re", "box_3_other_rental", "box_3_other_net_rental",
    "box_5_interest", "box_6a_ord_div", "box_7_royalties",
    "box_8_st_cap", "box_9a_lt_cap", "box_10_1231",
]


def activity_total(d: dict) -> float:
    return sum(num(d.get(b)) for b in INCOME_BOXES)


def loss_total(d: dict) -> float:
    """Magnitude of allocated losses (positive number)."""
    return sum(-num(d.get(b)) for b in INCOME_BOXES if num(d.get(b)) < 0)


# --------------------------------------------------------------------------
# K-1 invariants
# --------------------------------------------------------------------------

def check_k1(d: dict, doc: str) -> list[Finding]:
    out: list[Finding] = []
    item_l = d.get("part_ii_item_l") or d.get("capital_account")
    item_k = d.get("part_ii_item_k") or d.get("liabilities")

    # -- Item L capital account rollforward -------------------------------
    #
    # Sign conventions are NOT consistent across parsed files: some store
    # withdrawals as negative (already signed), others as a positive
    # magnitude meant to be subtracted. Both appear in this workspace and a
    # validator that assumes one silently passes half the population.
    # Compute both readings; the account ties if EITHER reconciles.
    if isinstance(item_l, dict):
        beg = num(pick(item_l, "beginning", "beginning_capital"))
        con = num(pick(item_l, "contributions", "contrib", "capital_contributed"))
        inc = num(pick(item_l, "current_year_net_income", "net_income", "current_year_increase"))
        oi = num(pick(item_l, "other_increases"))
        wd = num(pick(item_l, "withdrawals", "withdraw", "distributions"))
        od = num(pick(item_l, "other_decreases"))
        end = num(pick(item_l, "ending", "ending_capital"))

        signed = beg + con + inc + oi + wd + od
        magnitude = beg + con + inc + oi - abs(wd) - abs(od)
        ties_signed = abs(signed - end) <= TOLERANCE
        ties_mag = abs(magnitude - end) <= TOLERANCE

        populated = any(abs(x) > TOLERANCE for x in (beg, con, inc, oi, wd, od, end))

        if not populated and abs(activity_total(d)) > TOLERANCE:
            # Blank-Item-L pattern: every Item L field blank (encoded as
            # zero) while the K-1 allocates real income or loss. The capital
            # account cannot be verified at all, and negative capital from a
            # profits interest is exactly the case that must be shown.
            out.append(Finding(
                "HIGH", "K1.item_l.blank", doc,
                "Item L capital account is entirely blank/zero while the K-1 allocates activity.",
                f"activity across income boxes = {activity_total(d):,.0f}; "
                f"every Item L field is 0 or absent — nothing to reconcile. "
                f"Request a corrected K-1 with Item L populated.",
                ["part_ii_item_l"],
            ))
        elif populated and not (ties_signed or ties_mag):
            out.append(Finding(
                "CRITICAL", "K1.item_l.rollforward", doc,
                "Item L capital account does not roll forward under either sign convention.",
                f"beginning {beg:,.0f} + contributions {con:,.0f} + net income {inc:,.0f} "
                f"+ other increases {oi:,.0f} then withdrawals {wd:,.0f} / other decreases {od:,.0f} "
                f"→ signed {signed:,.0f} or magnitude {magnitude:,.0f}, but ending is stated as {end:,.0f} "
                f"(off by {min(abs(signed - end), abs(magnitude - end)):,.0f}).",
                ["part_ii_item_l"],
            ))

        # Negative ending capital is legal but is the classic §704(d) tell.
        if populated and end < -TOLERANCE:
            out.append(Finding(
                "INFO", "K1.item_l.negative_ending", doc,
                "Ending capital account is negative.",
                f"ending {end:,.0f}. Legal (common for profits-interest holders), but confirm "
                f"the loss was allowed under §704(d) and not merely booked.",
                ["part_ii_item_l"],
            ))

    # -- §704(d): loss allowed only to the extent of outside basis --------
    #
    # Outside basis proxy = capital + share of partnership liabilities
    # (§722 / §752). A loss exceeding that should be suspended, not passed
    # through. This is the check that catches an issuer flowing a loss to a
    # partner with no basis.
    if isinstance(item_l, dict):
        beg = num(pick(item_l, "beginning", "beginning_capital"))
        con = num(pick(item_l, "contributions", "contrib"))
        debt = item_k_total(item_k, "beginning") or item_k_total(item_k, "ending")
        basis_proxy = beg + con + debt
        loss = loss_total(d)

        # A blank Item L means basis is UNKNOWN, not zero. Reporting
        # "basis = 0" for an unpopulated capital account would assert a
        # §704(d) violation the document does not actually support.
        capital_known = any(
            pick(item_l, k) is not None
            for k in ("beginning", "beginning_capital", "contributions", "contrib")
        ) and any(
            abs(x) > TOLERANCE
            for x in (beg, con, num(pick(item_l, "ending", "ending_capital")))
        )

        if loss > TOLERANCE and loss > basis_proxy + TOLERANCE:
            if capital_known:
                out.append(Finding(
                    "CRITICAL", "K1.704d.loss_exceeds_basis", doc,
                    "Allocated loss exceeds the partner's outside basis — §704(d) suspension may apply.",
                    f"loss {loss:,.0f} vs basis {basis_proxy:,.0f} "
                    f"(beginning capital {beg:,.0f} + contributions {con:,.0f} + liability share {debt:,.0f}). "
                    f"Loss is deductible only to the extent of basis; the excess should be suspended "
                    f"and carried forward, not passed through.",
                    ["part_ii_item_l", "part_ii_item_k"],
                ))
            else:
                out.append(Finding(
                    "HIGH", "K1.704d.basis_undeterminable", doc,
                    "Loss allocated but outside basis cannot be determined from this K-1.",
                    f"loss {loss:,.0f} allocated while Item L is unpopulated and Item K liability "
                    f"share is {debt:,.0f}. Basis is unknown, not zero — §704(d) cannot be tested "
                    f"until Item L is populated or basis is established from another source.",
                    ["part_ii_item_l", "part_ii_item_k"],
                ))

    # -- Outside basis worksheet vs capital + liabilities -----------------
    #
    # A basis worksheet should approximate Item L ending capital plus the
    # Item K liability share. A large liability share is legitimate; a
    # worksheet that cannot be explained by capital + debt is a data error.
    bw = d.get("basis_worksheet_end_of_year")
    if bw is None and isinstance(d.get("basis_worksheet"), dict):
        bw = pick(d["basis_worksheet"], "end_of_year", "ending")
    if bw is not None:
        bw_v = num(bw)
        end_cap = num(pick(item_l, "ending", "ending_capital")) if isinstance(item_l, dict) else 0.0
        debt_end = item_k_total(item_k, "ending")
        explained = end_cap + debt_end
        # Only meaningful when the worksheet is materially non-zero.
        if abs(bw_v) > 1000 and abs(bw_v - explained) > max(1000.0, 0.25 * abs(bw_v)):
            out.append(Finding(
                "HIGH", "K1.basis_worksheet.unexplained", doc,
                "Basis worksheet cannot be explained by capital account plus liability share.",
                f"worksheet end-of-year basis {bw_v:,.0f} vs Item L ending capital {end_cap:,.0f} "
                f"+ Item K liabilities {debt_end:,.0f} = {explained:,.0f} "
                f"(unexplained {bw_v - explained:,.0f}). Under §722/§752 these should approximately tie; "
                f"a gap this size usually means an entity-level figure was reported as a partner share.",
                ["basis_worksheet_end_of_year", "part_ii_item_k", "part_ii_item_l"],
            ))

    # -- Guaranteed payments are not distributions ------------------------
    #
    # The documented misread in this workspace. Box 4a/4c (guaranteed
    # payments, ordinary income to the partner) and Box 19 (distributions,
    # generally not income) are adjacent on the form and get swapped.
    gp = num(pick(d, "box_4c_gp_total", "box_4a_gp_services"))
    dist = num(pick(d, "box_19_distributions", "box_19_a_cash"))
    if abs(gp) > TOLERANCE and abs(gp - dist) <= TOLERANCE:
        out.append(Finding(
            "HIGH", "K1.gp_equals_distribution", doc,
            "Guaranteed payments and distributions are identical — likely the same figure read into both.",
            f"Box 4a/4c {gp:,.0f} == Box 19 {dist:,.0f}. Guaranteed payments are ordinary income; "
            f"distributions generally are not. Confirm against the source form before relying on either.",
            ["box_4c_gp_total", "box_19_distributions"],
        ))

    # -- Ownership percentages must be percentages ------------------------
    for k in ("pct_profit", "pct_loss", "pct_capital", "pct_profit_end",
              "pct_loss_end", "pct_capital_end"):
        if k in d and d[k] is not None:
            v = num(d[k], default=-1.0)
            if v < 0 or v > 100:
                out.append(Finding(
                    "MEDIUM", "K1.pct.out_of_range", doc,
                    f"Ownership percentage `{k}` is outside 0–100.",
                    f"{k} = {d[k]!r}. A fraction stored as 0.13 where 13.0 was meant "
                    f"silently understates every derived allocation.",
                    [k],
                ))

    # -- §199A QBI should correspond to allocated income ------------------
    stmt = d.get("statement_a_199a") or d.get("statement_a_qbi_per_partner")
    if isinstance(stmt, list) and stmt:
        def entry_qbi(s: dict) -> float:
            # A single combined figure if the file carries one...
            combined = pick(s, "qbi", "qbi_income_loss")
            if combined is not None:
                return num(combined)
            # ...otherwise ordinary and rental are separate COMPONENTS of the
            # same statement and must be summed, not chosen between. Field
            # spelling varies by extraction pass.
            return (num(pick(s, "qbi_ordinary_income_loss", "qbi_ordinary"))
                    + num(pick(s, "qbi_rental_income_loss", "qbi_rental")))

        qbi = sum(entry_qbi(s) for s in stmt if isinstance(s, dict))
        base = num(d.get("box_1_ordinary")) + num(d.get("box_2_rental_re"))
        if abs(base) > TOLERANCE and abs(qbi) <= TOLERANCE:
            out.append(Finding(
                "MEDIUM", "K1.199a.zeroed", doc,
                "§199A statement reports zero QBI while the K-1 allocates business/rental income.",
                f"Box 1 + Box 2 = {base:,.0f} but Statement A QBI totals {qbi:,.0f}. "
                f"A zeroed pass-through is a known preparer defect — it silently drops the deduction.",
                ["statement_a_199a"],
            ))

    # -- Surface flags the extractor already recorded ---------------------
    if d.get("titling_error"):
        out.append(Finding(
            "MEDIUM", "K1.titling", doc,
            "Extractor flagged a partner-titling error on this K-1.",
            str(d.get("titling_note") or "").strip()[:400],
            ["titling_error"],
        ))
    for a in d.get("anomalies") or []:
        out.append(Finding("INFO", "K1.anomaly", doc,
                           "Extractor recorded an anomaly.", str(a)[:400], ["anomalies"]))

    return out


# --------------------------------------------------------------------------
# 1065 / entity return invariants
# --------------------------------------------------------------------------

def check_1065(d: dict, doc: str) -> list[Finding]:
    out: list[Finding] = []
    sl = d.get("schedule_l") or d.get("schedule_l_balance_sheet")
    m2 = d.get("schedule_m2") or d.get("schedule_m2_capital")

    # -- Balance sheet must balance, both columns -------------------------
    if isinstance(sl, dict):
        for col in ("beginning", "ending"):
            c = sl.get(col)
            if not isinstance(c, dict):
                continue
            assets = num(pick(c, "total_assets"))
            liab = num(pick(c, "total_liab", "total_liabilities"))
            cap = num(pick(c, "partners_capital", "total_capital"))
            if abs(assets) < TOLERANCE and abs(liab) < TOLERANCE and abs(cap) < TOLERANCE:
                continue
            if abs(assets - (liab + cap)) > TOLERANCE:
                out.append(Finding(
                    "CRITICAL", "1065.schedule_l.imbalance", doc,
                    f"Schedule L does not balance ({col} of year).",
                    f"total assets {assets:,.0f} vs liabilities {liab:,.0f} + capital {cap:,.0f} "
                    f"= {liab + cap:,.0f} (off by {assets - (liab + cap):,.0f}).",
                    ["schedule_l"],
                ))

    # -- M-2 rollforward --------------------------------------------------
    if isinstance(m2, dict):
        beg = num(pick(m2, "beginning"))
        con = num(pick(m2, "contributions"))
        inc = num(pick(m2, "net_income"))
        oi = num(pick(m2, "other_increases"))
        dc = num(pick(m2, "distributions_cash"))
        dp = num(pick(m2, "distributions_property"))
        od = num(pick(m2, "other_decreases"))
        end = num(pick(m2, "ending"))
        signed = beg + con + inc + oi + dc + dp + od
        magnitude = beg + con + inc + oi - abs(dc) - abs(dp) - abs(od)
        if not (abs(signed - end) <= TOLERANCE or abs(magnitude - end) <= TOLERANCE):
            out.append(Finding(
                "CRITICAL", "1065.m2.rollforward", doc,
                "Schedule M-2 does not roll forward under either sign convention.",
                f"beginning {beg:,.0f} + contributions {con:,.0f} + net income {inc:,.0f} "
                f"+ other increases {oi:,.0f}, distributions {dc + dp:,.0f}, other decreases {od:,.0f} "
                f"→ {signed:,.0f} / {magnitude:,.0f} vs stated ending {end:,.0f}.",
                ["schedule_m2"],
            ))

        # -- M-2 ending must tie to Schedule L ending capital -------------
        if isinstance(sl, dict) and isinstance(sl.get("ending"), dict):
            sl_cap = num(pick(sl["ending"], "partners_capital", "total_capital"))
            if abs(sl_cap) > TOLERANCE and abs(end - sl_cap) > TOLERANCE:
                out.append(Finding(
                    "HIGH", "1065.m2_vs_schedule_l", doc,
                    "Schedule M-2 ending capital does not equal Schedule L ending partners' capital.",
                    f"M-2 ending {end:,.0f} vs Schedule L ending capital {sl_cap:,.0f} "
                    f"(off by {end - sl_cap:,.0f}). These are the same number reported twice.",
                    ["schedule_m2", "schedule_l"],
                ))

    for a in d.get("anomalies") or []:
        out.append(Finding("INFO", "1065.anomaly", doc,
                           "Extractor recorded an anomaly.", str(a)[:400], ["anomalies"]))
    return out


# --------------------------------------------------------------------------
# Cross-document invariant: issued K-1s must sum to Schedule K
# --------------------------------------------------------------------------

# Schedule K line ↔ K-1 box, for the lines that must foot exactly.
K_LINE_TO_BOX = {
    "line_1_ordinary": "box_1_ordinary",
    "line_2_rental_re": "box_2_rental_re",
    "line_4c_gp_total": "box_4c_gp_total",
    "line_5_interest": "box_5_interest",
    "line_6a_ord_div": "box_6a_ord_div",
    "line_8_st_cap": "box_8_st_cap",
    "line_9a_lt_cap": "box_9a_lt_cap",
    "line_10_1231": "box_10_1231",
    "line_12_179": "box_12_179",
}


def check_cross(docs: dict[str, dict]) -> list[Finding]:
    """Checks that need more than one parsed document."""
    out: list[Finding] = []

    returns = {n: d for n, d in docs.items()
               if str(d.get("doc_type", "")).startswith(("1065", "1120"))}
    issued = {n: d for n, d in docs.items()
              if d.get("direction") == "issued" and "K-1" in str(d.get("doc_type", "")).upper()}

    if not returns or not issued:
        return out

    for rname, rdoc in returns.items():
        sk = rdoc.get("schedule_k") or rdoc.get("schedule_k_separately_stated")
        if not isinstance(sk, dict):
            continue
        peers = {n: d for n, d in issued.items()
                 if str(d.get("tax_year")) == str(rdoc.get("tax_year"))}
        if not peers:
            continue

        for line, box in K_LINE_TO_BOX.items():
            if line not in sk:
                continue
            entity = num(sk.get(line))
            partners = sum(num(d.get(box)) for d in peers.values())
            if abs(entity) < TOLERANCE and abs(partners) < TOLERANCE:
                continue
            if abs(entity - partners) > TOLERANCE:
                out.append(Finding(
                    "HIGH", "cross.k_vs_k1_sum", rname,
                    f"Schedule K {line} does not equal the sum of issued K-1 {box}.",
                    f"Schedule K {entity:,.0f} vs {len(peers)} partner K-1s totalling {partners:,.0f} "
                    f"(off by {entity - partners:,.0f}). Every separately-stated item must foot to "
                    f"the partners; a gap means an item was not passed through.",
                    [line, box],
                ))

        # -- Received pass-through items must reach the entity return ----
        #
        # A tiered structure leaks quietly: an item reported on a K-1 the
        # entity RECEIVED must appear on its own Schedule K, or it never
        # reaches the ultimate partners. Nondeductible expenses (Box 18C)
        # are the usual casualty — small enough to overlook, but they belong
        # in the M-2 "other decreases" and in each partner's basis.
        received = {n: d for n, d in docs.items()
                    if d.get("direction") == "received"
                    and str(d.get("tax_year")) == str(rdoc.get("tax_year"))}
        if received:
            inbound = sum(num(d.get(k))
                          for d in received.values()
                          for k in d
                          if k.startswith("box_18") and "nondeduct" in k)
            reported = num(pick(sk, "line_18c_nondeductible_expenses", "line_18c"))
            if abs(inbound) > TOLERANCE and abs(inbound - reported) > TOLERANCE:
                out.append(Finding(
                    "MEDIUM", "cross.nondeductible_passthrough", rname,
                    "Nondeductible expenses on received K-1s do not appear on this entity's Schedule K.",
                    f"received K-1s report {inbound:,.0f} of Box 18C nondeductible expenses, but "
                    f"Schedule K line 18c shows {reported:,.0f} (gap {inbound - reported:,.0f}). "
                    f"Unreported, it is missing from the partners' basis and from M-2 other decreases.",
                    ["line_18c_nondeductible_expenses", "box_18_nondeductible_c"],
                ))

        # Ownership percentages across issued K-1s should total 100%.
        pcts = [num(pick(d, "pct_capital_end", "pct_capital"), default=-1.0) for d in peers.values()]
        pcts = [p for p in pcts if p >= 0]
        if pcts and abs(sum(pcts) - 100.0) > 0.5:
            out.append(Finding(
                "HIGH", "cross.ownership_sum", rname,
                "Issued K-1 capital percentages do not total 100%.",
                f"{len(pcts)} partner K-1s total {sum(pcts):.4f}%.",
                ["pct_capital"],
            ))

    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def classify(d: dict) -> str:
    dt = str(d.get("doc_type", "")).upper()
    if "K-1" in dt or "K1" in dt:
        return "k1"
    if dt.startswith(("1065", "1120")):
        return "return"
    return "other"


def verify_docs(docs: dict[str, dict]) -> list[Finding]:
    out: list[Finding] = []
    for name, d in sorted(docs.items()):
        kind = classify(d)
        if kind == "k1":
            out.extend(check_k1(d, name))
        elif kind == "return":
            out.extend(check_1065(d, name))
    out.extend(check_cross(docs))
    return out


def load(path: Path) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    files: Iterable[Path]
    if path.is_dir():
        files = sorted(p for p in path.glob("*.json") if p.name != "_index.json")
    else:
        files = [path]
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"skipped {f.name}: {e}", file=sys.stderr)
            continue
        # Some parsed files hold a bare list (e.g. an array of statements)
        # rather than a document object. Nothing to verify, but never crash
        # a whole-directory run over one odd file.
        if not isinstance(doc, dict):
            print(f"skipped {f.name}: top-level JSON is "
                  f"{type(doc).__name__}, expected object", file=sys.stderr)
            continue
        docs[f.name] = doc
    return docs


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify arithmetic and tax-law invariants over parsed tax JSON.")
    ap.add_argument("path", help="parsed JSON file, or a .parsed/ directory")
    ap.add_argument("--json", action="store_true", help="emit JSON findings")
    ap.add_argument("--min-severity", default="MEDIUM",
                    choices=list(SEVERITY_ORDER), help="gate for exit code and display")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"no such path: {path}", file=sys.stderr)
        return 2

    docs = load(path)
    if not docs:
        print("no parsed JSON found", file=sys.stderr)
        return 2

    findings = verify_docs(docs)
    floor = SEVERITY_ORDER[args.min_severity]
    shown = [f for f in findings if SEVERITY_ORDER[f.severity] >= floor]
    shown.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.doc, f.check))

    if args.json:
        print(json.dumps({
            "docs_checked": len(docs),
            "findings_total": len(findings),
            "findings": [asdict(f) for f in shown],
        }, indent=2))
        return 1 if shown else 0

    print(f"parse-verify — {len(docs)} document(s) checked\n")
    if not shown:
        print(f"No findings at or above {args.min_severity}.")
        suppressed = len(findings) - len(shown)
        if suppressed:
            print(f"({suppressed} lower-severity finding(s) suppressed.)")
        return 0

    for f in shown:
        print(f"[{f.severity}] {f.doc} — {f.check}")
        print(f"  {f.message}")
        if f.detail:
            print(f"  {f.detail}")
        print()

    counts: dict[str, int] = {}
    for f in shown:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary = ", ".join(f"{counts[s]} {s}" for s in
                        sorted(counts, key=lambda s: -SEVERITY_ORDER[s]))
    print(f"{len(shown)} finding(s): {summary}")
    suppressed = len(findings) - len(shown)
    if suppressed:
        print(f"({suppressed} lower-severity finding(s) suppressed — "
              f"re-run with --min-severity INFO to see them.)")
    print("\nThis tool never modifies anything. Findings are leads, not conclusions.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

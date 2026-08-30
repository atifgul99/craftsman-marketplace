#!/usr/bin/env python3
"""Executable schema, provenance, null-state, and core-value checks for rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from _deps import require

require(
    "jsonschema",
    "validating every rules file against its schema",
    "expired or malformed tax rules are not detected - this script is the freshness gate that exits 2 on expired data",
)

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            yield from walk(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def covered(path: str, candidates: list[str]) -> bool:
    return any(
        candidate == "*"
        or path == candidate
        or path.startswith(candidate + ".")
        or path.startswith(candidate + "[")
        for candidate in candidates
    )


def get_path(payload: Any, dotted: str) -> Any:
    value = payload
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise AssertionError(f"missing used rule path: {dotted}")
        value = value[part]
    return value


def mortgage_cap(
    rules: dict[str, Any],
    debt_incurred: str,
    mfs: bool,
    *,
    binding_contract_date: str | None = None,
    contract_required_closing_date: str | None = None,
    actual_purchase_date: str | None = None,
) -> int:
    selector = rules["mortgage_acquisition_debt_cap"]
    transition = all((binding_contract_date, contract_required_closing_date, actual_purchase_date)) and (
        date.fromisoformat(binding_contract_date) < date(2017, 12, 15)
        and date.fromisoformat(contract_required_closing_date) < date(2018, 1, 1)
        and date.fromisoformat(actual_purchase_date) < date(2018, 4, 1)
    )
    grandfathered = date.fromisoformat(debt_incurred) <= date(2017, 12, 15) or transition
    band = selector["on_or_before_2017_12_15"] if grandfathered else selector["after_2017_12_15"]
    return band["mfs" if mfs else "non_mfs"]


def validate_file(path: Path, schema: dict[str, Any], manifest_entry: dict[str, Any]) -> None:
    data = load(path)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data),
        key=lambda error: list(error.path),
    )
    assert not errors, f"{path.name}: schema error: {errors[0].message if errors else ''}"

    year_match = re.fullmatch(r"federal-(\d{4})\.json", path.name)
    assert year_match, f"unexpected federal rules filename: {path.name}"
    filename_year = int(year_match.group(1))
    assert data["tax_year"] == filename_year == data["_meta"]["tax_year"]
    assert manifest_entry["tax_year"] == filename_year
    assert manifest_entry["status"] == data["_meta"]["status"]

    raw_verify_paths = [item_path for item_path, _ in walk(data) if "_verify" in item_path.split(".")]
    assert not raw_verify_paths, f"{path.name}: raw _verify markers: {raw_verify_paths}"

    authorities = data["_meta"]["authorities"]
    authority_ids = [item["id"] for item in authorities]
    assert len(authority_ids) == len(set(authority_ids)), f"{path.name}: duplicate authority IDs"
    for item in authorities:
        parsed = urlparse(item["url"])
        assert parsed.scheme == "https" and parsed.hostname, f"{path.name}: non-HTTPS authority"
        assert parsed.hostname.lower().endswith(".gov"), (
            f"{path.name}: authority is not an official government source: {item['url']}"
        )

    coverage = data["_meta"]["coverage"]
    coverage_paths: list[str] = []
    for entry in coverage:
        for authority_id in entry["authority_ids"]:
            assert authority_id in authority_ids, f"{path.name}: unknown authority ID {authority_id}"
        coverage_paths.extend(entry["paths"])
    assert len(coverage_paths) == len(set(coverage_paths)), f"{path.name}: duplicate exact coverage paths"

    unresolved_paths = [entry["path"] for entry in data["_meta"]["unresolved"]]
    null_paths = [item_path for item_path, value in walk(data) if value is None and not item_path.startswith("_meta.")]
    for null_path in null_paths:
        open_ended_bracket = bool(re.match(r"^brackets_(ordinary|ltcg)\..+\[\d+\]\[0\]$", null_path))
        assert open_ended_bracket or covered(null_path, unresolved_paths), (
            f"{path.name}: null path is neither an open-ended bracket nor explicitly unresolved: {null_path}"
        )

    if data["_meta"]["status"] == "SOURCE_MAPPED":
        ignored = {"_meta", "tax_year", "source_notes"}
        for key in data:
            if key in ignored or key.endswith("_note"):
                continue
            candidates = coverage_paths + unresolved_paths
            top_level_covered = covered(key, candidates) or any(
                candidate.startswith(key + ".") or candidate.startswith(key + "[")
                for candidate in candidates
            )
            assert top_level_covered, f"{path.name}: uncovered top-level path: {key}"
        for leaf_path, _ in walk(data):
            if leaf_path.startswith("_meta.") or leaf_path in {"tax_year", "source_notes"}:
                continue
            terminal = leaf_path.rsplit(".", 1)[-1].split("[", 1)[0]
            if terminal.endswith("note") or terminal == "_note":
                continue
            assert covered(leaf_path, coverage_paths + unresolved_paths), (
                f"{path.name}: uncovered leaf path: {leaf_path}"
            )


# Cross-year drift guards.
#
# REQUIRE_DECLARED_REPEAT: parameters indexed on a fine enough step that an
# unchanged year is far more likely a copy-forward bug than real. The assertion
# is NOT "these always rise" — that is false in general (the standard deduction
# repeated from 2009 to 2010: $5,700 single / $11,400 MFJ). The assertion is that
# an unchanged value must be DECLARED rather than pass silently, because the
# default explanation is a bug. This exists because federal-2024.json shipped
# with the 2023 section 179 cap and phaseout ($1,160,000 / $2,890,000 instead of
# $1,220,000 / $3,050,000), which no single-year check could see.
REQUIRE_DECLARED_REPEAT = [
    "section_179_cap",
    "section_179_phaseout_start",
    "standard_deduction.single",
    "standard_deduction.mfj",
    "standard_deduction.hoh",
    "estate_exemption",
    "qbi.threshold_mfj",
    "foreign_earned_income_exclusion",
]

# NON_DECREASING: coarser steps (round to $500/$1,000), so an unchanged year is
# legitimate. Only a DECREASE is suspicious, and each real one needs a note here.
NON_DECREASING = [
    "gift_exclusion_annual",
    "gift_exclusion_non_citizen_spouse",
    "retirement_limits.401k_elective",
    "retirement_limits.ira_trad_roth",
    "retirement_limits.overall_dc_415c",
    "ss_wage_base",
    "fsa_contribution_limit",
    "excess_business_loss_threshold.mfj",
    "excess_business_loss_threshold.single",
]

# Statutory re-basings that legitimately break the rules above.
DRIFT_EXCEPTIONS = {
    ("excess_business_loss_threshold.mfj", 2026),
    ("excess_business_loss_threshold.single", 2026),
}

def declared_repeats(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Repeats declared in a file's own `_meta.declared_repeats`, keyed by path.

    The escape hatch must exist — low inflation genuinely flattens these (the
    standard deduction repeated 2009 -> 2010, Rev. Proc. 2008-66 and 2009-50).
    But it must be EVIDENCE-BOUND: a free-text note in the checker would let any
    string silence the guard. Each declaration names the path, the prior year, an
    authority ID present in the same file, and where in that source it was
    confirmed. Schema v2 enforces the shape; the checks below enforce that the
    declaration actually corresponds to a real repeat.
    """
    return {entry["path"]: entry for entry in data["_meta"].get("declared_repeats", [])}


def lookup(payload: Any, dotted: str) -> Any:
    value = payload
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value if isinstance(value, (int, float)) else None


class StaleRules(AssertionError):
    """Data expired. Distinct from data being malformed or wrong, so CI can
    tell 'needs re-verification' (exit 2) from 'is broken' (exit 1)."""


def validate_freshness(by_year: dict[int, dict[str, Any]], as_of: date) -> None:
    """Fail once a rules file passes its declared `stale_after`.

    Bundled figures go stale SILENTLY — that is the whole hazard of shipping
    reference data. This converts it into a loud, dated failure. The risk being
    guarded is not the published figure drifting; it is LEGISLATION landing after
    the file was checked (OBBBA retroactively rewrote TY2025 §179 and created four
    new TY2025 deductions), which no amount of care at authoring time prevents.
    """
    stale = []
    for year in sorted(by_year):
        meta = by_year[year]["_meta"]
        stale_after = date.fromisoformat(meta["stale_after"])
        assert date.fromisoformat(meta["checked_at"]) <= stale_after, (
            f"federal-{year}.json: stale_after precedes checked_at"
        )
        if as_of > stale_after:
            stale.append(
                f"  federal-{year}.json went stale on {stale_after} "
                f"(checked {meta['checked_at']}; {meta.get('stale_after_rationale', '')})"
            )
    if stale:
        raise StaleRules(
        "Rules data is past its declared freshness window:\n" + "\n".join(stale) +
        "\n\nRe-verify each file against its cited primary sources and any legislation "
        "enacted since, then update _meta.checked_at and _meta.stale_after. Do NOT simply "
        "bump the date. Until then these files are AUTHORITY_HOLD for numeric outputs "
        "(authority.md). Use --as-of to reproduce a past run."
    )


def validate_cross_year(by_year: dict[int, dict[str, Any]]) -> int:
    """Compare each indexed parameter against the prior year. Returns #checked."""
    years = sorted(by_year)
    checked = 0
    for paths, strict in ((REQUIRE_DECLARED_REPEAT, True), (NON_DECREASING, False)):
        for path in paths:
            for previous, current in zip(years, years[1:]):
                if (path, current) in DRIFT_EXCEPTIONS:
                    continue
                before, after = lookup(by_year[previous], path), lookup(by_year[current], path)
                if before is None or after is None:
                    continue
                checked += 1
                if strict:
                    declaration = declared_repeats(by_year[current]).get(path)
                    if after == before and declaration:
                        assert declaration["prior_year"] == previous, (
                            f"{path}: declared repeat names prior_year "
                            f"{declaration['prior_year']}, but the compared year is {previous}"
                        )
                        known = {a["id"] for a in by_year[current]["_meta"]["authorities"]}
                        assert declaration["authority_id"] in known, (
                            f"{path}: declared repeat cites authority "
                            f"{declaration['authority_id']}, which is not in this file"
                        )
                        continue
                    assert after > before, (
                        f"{path}: {current} value {after} is not greater than {previous}'s "
                        f"{before}. For a finely-indexed parameter the default explanation is "
                        f"a copy-forward bug. If the repeat is real, confirm it against the "
                        f"{current} source and record it in that file's "
                        f"_meta.declared_repeats with its authority and source location; "
                        f"if a statute re-based it, record it in DRIFT_EXCEPTIONS."
                    )
                else:
                    assert after >= before, (
                        f"{path}: {current} value {after} is BELOW {previous}'s {before}. "
                        f"If a statute re-based it, record it in DRIFT_EXCEPTIONS with a note."
                    )

    # A declaration that no longer describes a real repeat is stale, and an unused
    # escape hatch silently weakens the guard it was carved out of.
    for year, data in by_year.items():
        for entry in data["_meta"].get("declared_repeats", []):
            previous = year - 1
            if previous not in by_year:
                continue
            before = lookup(by_year[previous], entry["path"])
            after = lookup(data, entry["path"])
            assert before is not None and after == before, (
                f"federal-{year}.json declares a repeat of {entry['path']} that is not one "
                f"({previous}={before}, {year}={after}). Remove the stale declaration."
            )
    return checked


def validate_core_2026(data: dict[str, Any]) -> None:
    retirement = data["retirement_limits"]
    assert retirement["sep_max_comp"] == 360_000
    assert retirement["simple_catchup_50"] == 4_000
    assert retirement["simple_catchup_60_63"] == 5_250
    assert retirement["hsa_self_deductible_min"] == 1_700
    assert retirement["hsa_family_deductible_min"] == 3_400
    assert retirement["hsa_self_oop_max"] == 8_500
    assert retirement["hsa_family_oop_max"] == 17_000
    assert data["qbi"]["threshold_mfs"] == 201_775
    assert data["amt"]["phaseout_rate"] == 0.5
    assert data["standard_deduction"]["dependent_minimum"] == 1_350
    assert data["standard_deduction"]["dependent_earned_income_addition"] == 450
    assert data["safe_harbor_high_agi_threshold_non_mfs"] == 150_000
    assert data["safe_harbor_high_agi_threshold_mfs"] == 75_000
    assert data["mileage_business"] is None and len(data["mileage_rates"]) == 2
    assert mortgage_cap(data, "2017-12-20", False) == 750_000
    assert mortgage_cap(
        data,
        "2018-02-01",
        False,
        binding_contract_date="2017-12-14",
        contract_required_closing_date="2017-12-31",
        actual_purchase_date="2018-03-15",
    ) == 1_000_000
    assert mortgage_cap(
        data,
        "2018-02-01",
        False,
        binding_contract_date="2017-12-14",
        contract_required_closing_date="2018-01-02",
        actual_purchase_date="2018-03-15",
    ) == 750_000
    assert mortgage_cap(
        data,
        "2018-02-01",
        False,
        binding_contract_date="2017-12-14",
        contract_required_closing_date="2017-12-31",
        actual_purchase_date="2018-04-01",
    ) == 750_000
    assert mortgage_cap(data, "2017-12-20", True) == 375_000


def validate_core_2023(data: dict[str, Any]) -> None:
    """Exhaustive pinning of the highest-risk 2023 tables.

    Rev. Proc. 2022-38 / Notice 2022-55 / Rev. Proc. 2022-24 / Notice 2023-03.
    Every bracket endpoint, every AMT field, every retirement limit — sampling
    would let a mid-table transcription error survive.
    """
    # Rev. Proc. 2022-38 s3.01, Tables 1-4. Top band is open-ended (null bound).
    assert data["brackets_ordinary"]["mfj"] == [
        [22_000, 0.10], [89_450, 0.12], [190_750, 0.22], [364_200, 0.24],
        [462_500, 0.32], [693_750, 0.35], [None, 0.37]]
    assert data["brackets_ordinary"]["single"] == [
        [11_000, 0.10], [44_725, 0.12], [95_375, 0.22], [182_100, 0.24],
        [231_250, 0.32], [578_125, 0.35], [None, 0.37]]
    assert data["brackets_ordinary"]["mfs"] == [
        [11_000, 0.10], [44_725, 0.12], [95_375, 0.22], [182_100, 0.24],
        [231_250, 0.32], [346_875, 0.35], [None, 0.37]]
    assert data["brackets_ordinary"]["hoh"] == [
        [15_700, 0.10], [59_850, 0.12], [95_350, 0.22], [182_100, 0.24],
        [231_250, 0.32], [578_100, 0.35], [None, 0.37]]
    # s3.03
    assert data["brackets_ltcg"]["mfj"] == [[89_250, 0.0], [553_850, 0.15], [None, 0.20]]
    assert data["brackets_ltcg"]["single"] == [[44_625, 0.0], [492_300, 0.15], [None, 0.20]]
    assert data["brackets_ltcg"]["mfs"] == [[44_625, 0.0], [276_900, 0.15], [None, 0.20]]
    assert data["brackets_ltcg"]["hoh"] == [[59_750, 0.0], [523_050, 0.15], [None, 0.20]]
    # s3.15
    assert data["standard_deduction"] == {
        "single": 13_850, "mfj": 27_700, "mfs": 13_850, "hoh": 20_800,
        "addl_65_or_blind_mfj": 1_500, "addl_65_or_blind_single_hoh": 1_850,
        "dependent_minimum": 1_250, "dependent_earned_income_addition": 400}
    # s3.11
    assert data["amt"]["exemption"] == {"single": 81_300, "mfj": 126_500, "mfs": 63_250}
    assert data["amt"]["phaseout_start"] == {"single": 578_150, "mfj": 1_156_300, "mfs": 578_150}
    assert data["amt"]["rate_breakpoint_26_28"] == 220_700
    assert data["amt"]["mfs_rate_breakpoint"] == 110_350
    # Notice 2022-55 and Rev. Proc. 2022-24 s3.01
    retirement = data["retirement_limits"]
    for key, expected in {
        "401k_elective": 22_500, "401k_catchup_50": 7_500,
        "ira_trad_roth": 6_500, "ira_catchup_50": 1_000,
        "simple_elective": 15_500, "simple_catchup_50": 3_500,
        "sep_max_comp": 330_000, "overall_dc_415c": 66_000,
        "hsa_self": 3_850, "hsa_family": 7_750, "hsa_catchup_55": 1_000,
        "hdhp_self_deductible_min": 1_500, "hdhp_family_deductible_min": 3_000,
        "hdhp_self_oop_max": 7_500, "hdhp_family_oop_max": 15_000,
    }.items():
        assert retirement[key] == expected, f"retirement_limits.{key}"
    # Remaining single-value items, each with its source section.
    for path, expected in {
        "section_179_cap": 1_160_000, "section_179_phaseout_start": 2_890_000,   # s3.25
        "suv_cap": 28_900, "foreign_earned_income_exclusion": 120_000,           # s3.39
        "estate_exemption": 12_920_000, "gift_exclusion_annual": 17_000,         # s3.41, s3.43
        "gift_exclusion_non_citizen_spouse": 175_000,
        "adoption_credit": {"max": 15_950, "phaseout_start": 239_230,            # s3.04
                            "phaseout_complete": 279_230},
        "ctc_refundable_cap": 1_600, "fsa_contribution_limit": 3_050,            # s3.05, s3.16
        "fsa_carryover_max": 610, "qualified_transportation_fringe_monthly": 300,
        "mileage_business": 0.655, "mileage_medical": 0.22,                      # Notice 2023-03
        "mileage_charitable": 0.14, "bonus_depreciation_pct": 0.80,
        "salt_cap": {"mfj": 10_000, "single": 10_000, "hoh": 10_000, "mfs": 5_000,
                     "_note": data["salt_cap"]["_note"]},
    }.items():
        assert data[path] == expected, path
    assert data["qbi"]["threshold_mfj"] == 364_200 and data["qbi"]["threshold_single"] == 182_100
    assert data["excess_business_loss_threshold"]["mfj"] == 578_000
    assert data["excess_business_loss_threshold"]["single"] == 289_000
    # TY2023 predates both regimes; a value here means a later year leaked in.
    assert "401k_catchup_60_63_secure2" not in retirement
    assert "obbba_deductions" not in data
    assert data["ss_wage_base"] is None


def validate_core_2025(data: dict[str, Any]) -> None:
    """OBBBA (PL 119-21) TY2025-2028 deductions: statutory, unindexed in-window."""
    obbba = data["obbba_deductions"]
    assert obbba["tips"]["cap"] == 25_000
    assert obbba["tips"]["magi_phaseout_start"] == 150_000
    assert obbba["tips"]["magi_phaseout_start_mfj"] == 300_000
    assert obbba["overtime"]["cap"] == 12_500
    assert obbba["overtime"]["cap_mfj"] == 25_000
    assert obbba["senior_65"]["amount_per_person"] == 6_000
    assert obbba["senior_65"]["magi_phaseout_start_mfj"] == 150_000
    assert obbba["car_loan_interest"]["cap"] == 10_000
    # OBBBA overrides Rev. Proc. 2024-40's $1,250,000 / $3,130,000 for TY2025.
    assert data["section_179_cap"] == 2_500_000
    assert data["section_179_phaseout_start"] == 4_000_000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-used-paths", nargs="+", metavar=("FILE", "PATH"))
    parser.add_argument(
        "--as-of", metavar="YYYY-MM-DD",
        help="evaluate freshness as of this date instead of today (for reproducible runs)",
    )
    parser.add_argument(
        "--allow-point-of-use",
        action="store_true",
        help="readiness only: accept source-mapped paths that still require current-run verification",
    )
    args = parser.parse_args()

    schema = load(RULES / "schema-v2.json")
    manifest = load(RULES / "manifest.json")
    files = sorted(RULES.glob("federal-*.json"))
    entries = {entry["path"]: entry for entry in manifest["files"]}
    assert {path.name for path in files} == set(entries), "manifest and federal rules file set differ"

    for path in files:
        validate_file(path, schema, entries[path.name])

    by_year = {load(path)["tax_year"]: load(path) for path in files}
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    validate_freshness(by_year, as_of)
    drift_checks = validate_cross_year(by_year)

    rules_2026 = load(RULES / "federal-2026.json")
    validate_core_2026(rules_2026)
    if 2023 in by_year:
        validate_core_2023(by_year[2023])
    if 2025 in by_year:
        validate_core_2025(by_year[2025])
    notes_2026 = " ".join(entries["federal-2026.json"].get("shape_notes", []))
    assert "safe_harbor_high_agi_threshold_mfs" in notes_2026

    if args.check_used_paths:
        filename, *used_paths = args.check_used_paths
        assert used_paths, "provide at least one used rule path"
        data = load(RULES / filename)
        coverage = data["_meta"]["coverage"]
        unresolved = [entry["path"] for entry in data["_meta"]["unresolved"]]
        for used_path in used_paths:
            get_path(data, used_path)
            assert not covered(used_path, unresolved), f"used path is unresolved: {used_path}"
            allowed_statuses = {"VERIFIED", "POINT_OF_USE"} if args.allow_point_of_use else {"VERIFIED"}
            matches = [entry for entry in coverage if covered(used_path, entry["paths"]) and entry["status"] in allowed_statuses]
            assert matches, f"used path lacks authority coverage: {used_path}"
            assert data["_meta"]["status"] != "REVIEW_REQUIRED", (
                f"{filename} requires full point-of-use review before computation"
            )
            assert as_of <= date.fromisoformat(data["_meta"]["stale_after"]), (
                f"{filename} is past its freshness window "
                f"({data['_meta']['stale_after']}); AUTHORITY_HOLD"
            )

    print(
        f"PASS: {len(files)} rules files satisfy schema/provenance/null contracts; "
        f"2023/2025/2026 core fixtures pass; {drift_checks} cross-year drift checks pass; "
        f"all files fresh as of {as_of}"
    )


if __name__ == "__main__":
    try:
        main()
    except StaleRules as expired:
        # Exit 2: the data needs re-verification, not repair.
        print(f"STALE: {expired}", file=sys.stderr)
        raise SystemExit(2)

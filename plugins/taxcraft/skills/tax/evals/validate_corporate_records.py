#!/usr/bin/env python3
"""Release and instantiated-artifact validator for corporate records audits."""

from __future__ import annotations

from argparse import ArgumentParser
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import tempfile
from urllib.parse import parse_qs, urlparse

from _deps import require

require(
    "jsonschema",
    "schema-checking corporate-records audit artifacts",
    "a corporate-records audit is not validated against its contract",
)

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
# The tax workspace is the directory Claude Code is run from, not a path derived
# from where this skill happens to be installed — as a plugin the skill lives
# outside the workspace entirely. Override with TAX_WORKSPACE when running the
# validator from elsewhere.
WORKSPACE = Path(os.environ.get("TAX_WORKSPACE") or Path.cwd())
CANONICAL_IDS = (
    "F-01", "F-02", "F-03", "F-04", "F-05",
    "O-01", "O-02", "O-03", "O-04", "R-01",
    "A-01", "A-02", "T-01", "T-02", "T-03",
    "P-01", "P-02", "P-03", "L-01", "L-02", "L-03",
    "S-01", "S-02", "S-03",
)
AUTHORITY_IDS = {"F-02", "F-03", "F-04"}
FILING_IDS = {"F-01", "F-05", "T-01", "T-03", "L-01", "L-02", "L-03"}
OPERATION_IDS = {
    "F-02", "F-03", "F-04", "O-01", "O-02", "O-03", "R-01",
    "A-01", "A-02", "T-02", "T-03", "P-01", "P-02", "P-03",
    "S-01", "S-02", "S-03",
}
EVIDENCE_KINDS_BY_ROW = {
    "F-01": {"ARTICLES_OR_AMENDMENT"}, "F-02": {"ARTICLES_OR_AMENDMENT", "INCORPORATOR_ACTION", "AUTHORITY_CHAIN"},
    "F-03": {"BYLAWS"}, "F-04": {"ORGANIZATIONAL_ACTION", "AUTHORITY_CHAIN"},
    "F-05": {"EIN_NOTICE"}, "O-01": {"ARTICLES_OR_AMENDMENT", "CAPITALIZATION_RECONCILIATION"},
    "O-02": {"STOCK_CLOSING"}, "O-03": {"STOCK_LEDGER_OR_NOTICE"}, "O-04": {"STOCK_TAX_MEMO"},
    "R-01": {"CORPORATE_RECORD_INDEX"}, "A-01": {"SHAREHOLDER_ACTION"}, "A-02": {"BOARD_ACTION"},
    "T-01": {"TAX_RETURN_OR_TRANSCRIPT"}, "T-02": {"BOOKS_RECONCILIATION"}, "T-03": {"PAYROLL_RECORD"},
    "P-01": {"ACCOUNTABLE_PLAN_RECORD"}, "P-02": {"AUGUSTA_RECORD"}, "P-03": {"BENEFITS_EMPLOYMENT_RECORD"},
    "L-01": {"STATE_STANDING"}, "L-02": {"LICENSE_REGISTRATION"},
    "L-03": {"BOI_AUTHORITY_OR_FILING", "ARTICLES_OR_AMENDMENT"},
    "S-01": {"SUBSIDIARY_OWNERSHIP_AUTHORITY"}, "S-02": {"SUBSIDIARY_AUDIT"}, "S-03": {"IP_ASSIGNMENT"},
}
DEFAULT_EVIDENCE_KIND = {row_id: sorted(kinds)[0] for row_id, kinds in EVIDENCE_KINDS_BY_ROW.items()}
DEFAULT_EVIDENCE_KIND["F-02"] = "INCORPORATOR_ACTION"
RECORD_SUBCONTROL_KINDS = {
    "MINUTES_CONSENTS": "MINUTES_CONSENTS",
    "SHAREHOLDER_RECORDS": "SHAREHOLDER_RECORDS",
    "ACCOUNTING_RECORDS": "ACCOUNTING_RECORDS",
    "ANNUAL_FINANCIAL_STATEMENTS": "ANNUAL_FINANCIAL_STATEMENTS",
    "SHAREHOLDER_COMMUNICATIONS": "SHAREHOLDER_COMMUNICATION",
}


def read(relative: str) -> str:
    path = ROOT / relative
    assert path.is_file(), f"missing required file: {relative}"
    return path.read_text(encoding="utf-8")


def require(text: str, needles: list[str], label: str) -> None:
    normalized_text = re.sub(r"\s+", " ", text.lower())
    for needle in needles:
        normalized = re.sub(r"\s+", " ", needle.lower())
        assert normalized in normalized_text, f"{label}: missing contract: {needle!r}"


def forbid(text: str, needles: list[str], label: str) -> None:
    lowered = text.lower()
    for needle in needles:
        assert needle.lower() not in lowered, f"{label}: forbidden stale rule: {needle!r}"


def parse_date(value: str | None) -> date | None:
    return None if value is None else date.fromisoformat(value)


def host_is(host: str, domain: str) -> bool:
    host = host.lower().rstrip(".")
    domain = domain.lower().rstrip(".")
    return host == domain or host.endswith(f".{domain}")


def house_code_section(parsed, section: str) -> bool:
    if not host_is(parsed.hostname or "", "uscode.house.gov") or parsed.path.rstrip("/") != "/view.xhtml":
        return False
    pattern = re.compile(rf"^granuleid:usc-(?:prelim-)?title26-section{re.escape(section)}(?:$|[-:])", re.I)
    return any(
        pattern.search(value)
        for value in parse_qs(parsed.query).get("req", [])
    )


def house_securities_section_77d(parsed) -> bool:
    if not host_is(parsed.hostname or "", "uscode.house.gov") or parsed.path.rstrip("/") != "/view.xhtml":
        return False
    pattern = re.compile(r"^granuleid:usc-(?:prelim-)?title15-section77d(?:$|[-:])", re.I)
    return any(pattern.search(value) for value in parse_qs(parsed.query).get("req", []))


def assert_safe_artifact_path(path: Path, label: str) -> Path:
    absolute = path.absolute()
    resolved = path.resolve()
    if path.is_symlink() or absolute != resolved:
        raise AssertionError(f"{label}: symlinked audit artifacts are prohibited")
    try:
        resolved.relative_to(WORKSPACE.resolve())
    except ValueError as exc:
        raise AssertionError(f"{label}: audit artifact is outside the Business workspace") from exc
    if "privileged" in str(resolved).lower():
        raise AssertionError(f"{label}: audit artifact enters privileged material")
    return resolved


def validate_stock_issuance_result(
    path: Path, parent_audit: dict, *, require_reconciled: bool = True
) -> str:
    path = assert_safe_artifact_path(path, f"stock specialist {path}")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"stock specialist is unreadable: {exc}") from exc
    schema = json.loads(read("schemas/stock-issuance-audit.schema.json"))
    failures = schema_errors(result, schema)
    if failures:
        raise AssertionError("stock specialist schema failure:\n" + "\n".join(failures[:20]))
    subject = parent_audit["subject"]["entity_slug"]
    period = parent_audit["subject"]["tax_periods"][0]
    cutoff_at = datetime.fromisoformat(parent_audit["scope"]["source_cutoff"].replace("Z", "+00:00"))
    if result["subject_entity_slug"] != subject or result["fiscal_or_tax_period"] != period:
        raise AssertionError("stock specialist subject or FY differs from corporate audit")
    if result["as_of"] != parent_audit["scope"]["as_of"] or result["source_cutoff"] != parent_audit["scope"]["source_cutoff"]:
        raise AssertionError("stock specialist cutoff differs from corporate audit")
    if parse_date(result["as_of"]) > date.today() or cutoff_at.date() > parse_date(result["as_of"]):
        raise AssertionError("stock specialist as-of/cutoff is future or reversed")
    expected_path = (
        WORKSPACE / "entities" / subject / "corporate" / "stock-issuances"
        / f"stock-issuance-audit-{period}.json"
    ).resolve()
    if path != expected_path:
        raise AssertionError(f"stock specialist must use canonical path {expected_path.relative_to(WORKSPACE.resolve())}")
    tranche_ids = [tranche["tranche_id"] for tranche in result["tranches"]]
    if len(tranche_ids) != len(set(tranche_ids)):
        raise AssertionError("stock specialist has duplicate tranche IDs")
    ordered = sorted(result["tranches"], key=lambda item: (item["issuance_date"], item["tranche_id"]))
    if result["tranches"] != ordered:
        raise AssertionError("stock specialist tranches are not in issuance-date and tranche-ID order")
    subject_corporate_root = (WORKSPACE / "entities" / subject / "corporate").resolve()
    subject_formation_root = (subject_corporate_root / "formation").resolve()
    subject_root = (subject_corporate_root / "stock-issuances").resolve()
    derived_tranche_statuses: list[str] = []
    previous_capital_by_class: dict[str, dict] = {}
    for tranche in result["tranches"]:
        issuance_date = parse_date(tranche["issuance_date"])
        if issuance_date > parse_date(result["as_of"]) or issuance_date > cutoff_at.date():
            raise AssertionError(f"{tranche['tranche_id']}: issuance date is after the audit cutoff")
        capital = tranche["capitalization"]
        if capital["scope"] != "CLASS" or capital["class"] != tranche["class"]:
            raise AssertionError(f"{tranche['tranche_id']}: capitalization is not bound to the issued share class")
        charter_authority = assert_safe_artifact_path(
            WORKSPACE / capital["charter_class_authority_path"],
            f"{tranche['tranche_id']} charter class authority",
        )
        try:
            charter_authority.relative_to(subject_formation_root)
        except ValueError as exc:
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority is outside the canonical subject formation records") from exc
        if (
            not charter_authority.is_file()
            or sha256(charter_authority.read_bytes()).hexdigest() != capital["charter_class_authority_sha256"]
        ):
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority missing or hash-mismatched")
        try:
            charter_data = json.loads(charter_authority.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority is not typed JSON") from exc
        charter_schema = json.loads(read("schemas/stock-issuance-charter-class-authority.schema.json"))
        charter_failures = schema_errors(charter_data, charter_schema)
        if charter_failures:
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority schema failure: {charter_failures[:10]}")
        if (
            charter_data["subject_entity_slug"] != subject
            or charter_data["class"] != tranche["class"]
            or charter_data["authorized_shares"] != capital["authorized_before"]
            or charter_data["authorized_shares"] != capital["authorized_after"]
        ):
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority contradicts capitalization")
        charter_observed_at = datetime.fromisoformat(charter_data["observed_at"].replace("Z", "+00:00"))
        if charter_observed_at > cutoff_at:
            raise AssertionError(f"{tranche['tranche_id']}: charter class authority was observed after cutoff")
        charter_source = assert_safe_artifact_path(
            WORKSPACE / charter_data["source_document_path"], f"{tranche['tranche_id']} charter source document"
        )
        try:
            charter_source.relative_to(subject_formation_root)
        except ValueError as exc:
            raise AssertionError(f"{tranche['tranche_id']}: charter source document is outside canonical subject formation records") from exc
        if not charter_source.is_file() or sha256(charter_source.read_bytes()).hexdigest() != charter_data["source_document_sha256"]:
            raise AssertionError(f"{tranche['tranche_id']}: charter source document missing or hash-mismatched")
        if capital["issued_after"] != capital["issued_before"] + tranche["shares"]:
            raise AssertionError(f"{tranche['tranche_id']}: issued-share rollforward does not foot")
        capacity_source = urlparse(capital["capacity_authority_url"])
        capacity_verified_at = datetime.fromisoformat(capital["capacity_authority_verified_at"].replace("Z", "+00:00"))
        if capacity_verified_at > cutoff_at:
            raise AssertionError(f"{tranche['tranche_id']}: capacity authority verified after cutoff")
        if jurisdiction_facts := tranche.get("transaction_jurisdiction_facts"):
            formation_state = jurisdiction_facts["issuer_formation_jurisdiction"]
        else:
            formation_state = None
        if formation_state != "Washington" or capital["formation_state_capacity_rule"] != "WA_REACQUIRED_AUTHORIZED_UNISSUED":
            raise AssertionError(f"{tranche['tranche_id']}: unsupported formation-state capacity rule requires validator extension")
        if not (
            host_is(capacity_source.hostname or "", "app.leg.wa.gov")
            and capacity_source.path.lower().rstrip("/") == "/rcw/default.aspx"
            and any(value.lower() == "23b.06.310" for value in parse_qs(capacity_source.query).get("cite", []))
        ):
            raise AssertionError(f"{tranche['tranche_id']}: Washington capacity authority source is invalid")
        if capital["treasury_before"] != 0 or capital["treasury_after"] != 0:
            raise AssertionError(f"{tranche['tranche_id']}: Washington reacquired shares must be treated as authorized unissued")
        if capital["outstanding_before"] != capital["issued_before"] or capital["outstanding_after"] != capital["issued_after"]:
            raise AssertionError(f"{tranche['tranche_id']}: Washington issued/outstanding reconciliation is inconsistent")
        for suffix in ("before", "after"):
            expected_available = capital[f"authorized_{suffix}"] - capital[f"issued_{suffix}"] - capital[f"reserved_{suffix}"]
            if expected_available < 0 or capital[f"legally_available_{suffix}"] != expected_available:
                raise AssertionError(f"{tranche['tranche_id']}: legally available share calculation is invalid")
        previous_capital = previous_capital_by_class.get(tranche["class"])
        if previous_capital and any(
            capital[f"{field}_before"] != previous_capital[f"{field}_after"]
            for field in ("authorized", "issued", "outstanding", "treasury", "reserved", "legally_available")
        ):
            raise AssertionError(f"{tranche['tranche_id']}: capitalization does not roll forward from the prior tranche of the same class")
        previous_capital_by_class[tranche["class"]] = capital
        expected_total = (Decimal(tranche["price_per_share"]) * tranche["shares"]).quantize(Decimal("0.01"))
        if expected_total != Decimal(tranche["total_consideration"]):
            raise AssertionError(f"{tranche['tranche_id']}: price, shares, and consideration do not multiply")
        jurisdiction_facts = tranche["transaction_jurisdiction_facts"]
        derived_jurisdictions = {
            "United States",
            jurisdiction_facts["issuer_formation_jurisdiction"],
            jurisdiction_facts["holder_residence_jurisdiction"],
            jurisdiction_facts["sale_jurisdiction"],
            *jurisdiction_facts["offer_jurisdictions"],
            *jurisdiction_facts["solicitation_jurisdictions"],
        }
        securities_jurisdictions = set(tranche["applicable_securities_jurisdictions"])
        if securities_jurisdictions != derived_jurisdictions:
            raise AssertionError(f"{tranche['tranche_id']}: securities jurisdictions do not derive from transaction facts")
        jurisdiction_evidence = assert_safe_artifact_path(
            WORKSPACE / jurisdiction_facts["evidence_path"], f"{tranche['tranche_id']} jurisdiction evidence"
        )
        try:
            jurisdiction_evidence.relative_to(subject_root)
        except ValueError as exc:
            raise AssertionError(f"{tranche['tranche_id']}: jurisdiction evidence is outside subject stock records") from exc
        if not jurisdiction_evidence.is_file() or sha256(jurisdiction_evidence.read_bytes()).hexdigest() != jurisdiction_facts["evidence_sha256"]:
            raise AssertionError(f"{tranche['tranche_id']}: jurisdiction evidence missing or hash-mismatched")
        authority_jurisdictions = {item["jurisdiction"] for item in tranche["securities_authorities"]}
        if securities_jurisdictions != authority_jurisdictions or "United States" not in authority_jurisdictions or len(authority_jurisdictions) < 2:
            raise AssertionError(f"{tranche['tranche_id']}: federal/state securities authority coverage is incomplete")
        for authority in [*tranche["securities_authorities"], *tranche["tax_authorities"]]:
            parsed = urlparse(authority["source_url"])
            if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.lower().endswith(".gov"):
                raise AssertionError(f"{tranche['tranche_id']}: specialist authority is not official HTTPS .gov")
            verified_at = datetime.fromisoformat(authority["verified_at"].replace("Z", "+00:00"))
            if verified_at > cutoff_at:
                raise AssertionError(f"{tranche['tranche_id']}: specialist authority verified after cutoff")
            effective_from = parse_date(authority["effective_from"])
            effective_to = parse_date(authority["effective_to"])
            if (effective_from and issuance_date < effective_from) or (effective_to and issuance_date > effective_to):
                raise AssertionError(f"{tranche['tranche_id']}: specialist authority does not cover issuance date")
        all_authority_ids = [
            authority["authority_id"]
            for authority in [*tranche["securities_authorities"], *tranche["tax_authorities"]]
        ]
        if len(all_authority_ids) != len(set(all_authority_ids)):
            raise AssertionError(f"{tranche['tranche_id']}: specialist authority IDs are not unique")
        for authority in tranche["securities_authorities"]:
            parsed = urlparse(authority["source_url"])
            host = (parsed.hostname or "").lower()
            path_text = parsed.path.lower()
            query = parse_qs(parsed.query)
            route = authority["route"]
            if authority["jurisdiction"] == "United States":
                federal_route_ok = {
                    "SECTION_4_A_2": (
                        (host_is(host, "sec.gov") and "exempt-offerings" in path_text)
                        or house_securities_section_77d(parsed)
                    ),
                    "RULE_506_B": (host_is(host, "ecfr.gov") and path_text.endswith("/section-230.506")) or (host_is(host, "sec.gov") and "exempt-offerings" in path_text),
                    "RULE_506_C": (host_is(host, "ecfr.gov") and path_text.endswith("/section-230.506")) or (host_is(host, "sec.gov") and "exempt-offerings" in path_text),
                    "REGULATION_CF": host_is(host, "sec.gov") and "regulation-crowdfunding" in path_text,
                    "REGULATION_A": host_is(host, "sec.gov") and "regulation-a" in path_text,
                    "RULE_701": (host_is(host, "ecfr.gov") and path_text.endswith("/section-230.701")) or (host_is(host, "sec.gov") and "rule-701" in path_text),
                }.get(route, False)
                if not federal_route_ok:
                    raise AssertionError(f"{tranche['tranche_id']}: federal securities route/source family is invalid")
            elif authority["jurisdiction"] == "Washington":
                if route not in {"WA_REGISTRATION", "WA_EXEMPTION", "WA_NOTICE"} or not host_is(host, "dfi.wa.gov") or "/securities" not in path_text:
                    raise AssertionError(f"{tranche['tranche_id']}: Washington securities route/source family is invalid")
            else:
                raise AssertionError(f"{tranche['tranche_id']}: unsupported state securities jurisdiction requires validator extension")
        washington_routes = {
            authority["route"] for authority in tranche["securities_authorities"]
            if authority["jurisdiction"] == "Washington"
        }
        if "Washington" in securities_jurisdictions and not washington_routes.intersection({"WA_REGISTRATION", "WA_EXEMPTION"}):
            raise AssertionError(f"{tranche['tranche_id']}: Washington lacks a substantive registration or exemption route")
        doctrines = {item["doctrine"] for item in tranche["tax_authorities"]}
        if doctrines != {"section_83", "section_351", "section_1202", "section_1244"}:
            raise AssertionError(f"{tranche['tranche_id']}: tax authority set is incomplete")
        facts = tranche["tax_fact_flags"]
        if (facts["liabilities_assumed"] or facts["integrated_transfer_plan"]) and not facts["property_transfer"]:
            raise AssertionError(f"{tranche['tranche_id']}: §351 tax facts are internally inconsistent")
        section_83_b = facts["section_83_b"]
        if facts["substantially_nonvested"]:
            if tranche["tax_positions"]["section_83"] == "NOT_APPLICABLE" or section_83_b["decision"] == "NOT_APPLICABLE":
                raise AssertionError(f"{tranche['tranche_id']}: nonvested stock lacks a typed §83(b) decision")
            transfer_date = parse_date(section_83_b["property_transfer_date"])
            filing_deadline = parse_date(section_83_b["filing_deadline"])
            if transfer_date != issuance_date or filing_deadline != transfer_date + timedelta(days=30):
                raise AssertionError(f"{tranche['tranche_id']}: §83(b) transfer date or 30-day deadline is invalid")
            if section_83_b["decision"] == "TIMELY_ELECTED":
                event_times = [
                    datetime.fromisoformat(section_83_b[field].replace("Z", "+00:00"))
                    for field in ("election_signed_at", "irs_delivery_at", "service_recipient_copy_at")
                    if section_83_b[field] is not None
                ]
                if len(event_times) != 3 or any(event.date() > filing_deadline or event > cutoff_at for event in event_times):
                    raise AssertionError(f"{tranche['tranche_id']}: timely §83(b) election lacks timely signing, IRS delivery, or service-recipient copy")
                if section_83_b["holding_period_result"] != "STARTS_AT_TRANSFER":
                    raise AssertionError(f"{tranche['tranche_id']}: timely §83(b) election has the wrong holding-period result")
            elif section_83_b["decision"] == "AFFIRMATIVELY_NOT_ELECTED":
                if section_83_b["holding_period_result"] != "STARTS_AT_VESTING":
                    raise AssertionError(f"{tranche['tranche_id']}: non-election has the wrong holding-period result")
            else:
                if tranche["tax_positions"]["section_83"] not in {"UNVERIFIED", "COUNSEL_HOLD"} or section_83_b["holding_period_result"] != "UNRESOLVED":
                    raise AssertionError(f"{tranche['tranche_id']}: missed or unresolved §83(b) decision must remain on hold")
            if section_83_b["evidence_path"] is None or section_83_b["evidence_sha256"] is None:
                raise AssertionError(f"{tranche['tranche_id']}: nonvested stock lacks §83(b) decision evidence")
            election_evidence = assert_safe_artifact_path(
                WORKSPACE / section_83_b["evidence_path"], f"{tranche['tranche_id']} §83(b) evidence"
            )
            try:
                election_evidence.relative_to(subject_root)
            except ValueError as exc:
                raise AssertionError(f"{tranche['tranche_id']}: §83(b) evidence is outside subject stock records") from exc
            if not election_evidence.is_file() or sha256(election_evidence.read_bytes()).hexdigest() != section_83_b["evidence_sha256"]:
                raise AssertionError(f"{tranche['tranche_id']}: §83(b) evidence missing or hash-mismatched")
        elif section_83_b != {
            "decision": "NOT_APPLICABLE", "property_transfer_date": None, "filing_deadline": None,
            "election_signed_at": None, "irs_delivery_at": None, "service_recipient_copy_at": None,
            "holding_period_result": "NOT_APPLICABLE", "evidence_path": None, "evidence_sha256": None,
        }:
            raise AssertionError(f"{tranche['tranche_id']}: vested stock has inconsistent §83(b) facts")
        control_status = facts["section_351_control_test_status"]
        control_percent = facts["section_351_control_percent_after"]
        if facts["property_transfer"]:
            if control_percent is None or control_status == "NOT_APPLICABLE":
                raise AssertionError(f"{tranche['tranche_id']}: cash or property transfer lacks the §351 control test")
            if (control_status == "SATISFIED" and control_percent < 80) or (
                control_status == "NOT_SATISFIED" and control_percent >= 80
            ):
                raise AssertionError(f"{tranche['tranche_id']}: §351 control-test status contradicts the recorded percentage")
            expected_351 = {
                "SATISFIED": "ISSUANCE_PRONGS_VERIFIED",
                "NOT_SATISFIED": "INELIGIBLE",
                "COUNSEL_HOLD": "COUNSEL_HOLD",
            }[control_status]
            if tranche["tax_positions"]["section_351"] != expected_351:
                raise AssertionError(f"{tranche['tranche_id']}: §351 position does not match the recorded control test")
        elif control_percent is not None or control_status != "NOT_APPLICABLE" or tranche["tax_positions"]["section_351"] != "NOT_APPLICABLE":
            raise AssertionError(f"{tranche['tranche_id']}: non-property consideration has inconsistent §351 facts")
        required_tax_rules = {"SECTION_83_CODE", "SECTION_351_CODE", "SECTION_1202_CODE", "SECTION_1244_CODE"}
        if facts["substantially_nonvested"]:
            required_tax_rules.update({"REG_1_83_2", "REG_1_83_4"})
        if facts["property_transfer"]:
            required_tax_rules.update({"REG_1_351_1", "SECTION_358_CODE", "SECTION_362_CODE", "SECTION_368_C_CODE", "REG_1_351_3", "REG_1_358_2"})
            if facts["liabilities_assumed"]:
                required_tax_rules.add("SECTION_357_CODE")
            if control_status == "NOT_SATISFIED":
                required_tax_rules.add("SECTION_1012_CODE")
        elif tranche["tax_positions"]["section_351"] == "INELIGIBLE":
            required_tax_rules.add("SECTION_1012_CODE")
        actual_tax_rules = {item["rule"] for item in tranche["tax_authorities"]}
        if not required_tax_rules.issubset(actual_tax_rules):
            raise AssertionError(f"{tranche['tranche_id']}: transaction facts lack their rule-specific tax authorities")
        for authority in tranche["tax_authorities"]:
            parsed = urlparse(authority["source_url"])
            host = (parsed.hostname or "").lower()
            path_text = parsed.path.lower()
            rule = authority["rule"]
            rule_sources = {
                "SECTION_83_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "83"),
                "REG_1_83_2": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.83-2"),
                "REG_1_83_4": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.83-4"),
                "SECTION_351_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "351"),
                "REG_1_351_1": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.351-1"),
                "SECTION_357_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "357"),
                "SECTION_358_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "358"),
                "SECTION_362_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "362"),
                "SECTION_368_C_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "368"),
                "REG_1_351_3": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.351-3"),
                "REG_1_358_2": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.358-2"),
                "SECTION_1012_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "1012"),
                "SECTION_1202_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "1202"),
                "SECTION_1244_CODE": host_is(host, "uscode.house.gov") and house_code_section(parsed, "1244"),
            }[rule]
            expected_doctrine = {
                "SECTION_83_CODE": "section_83", "REG_1_83_2": "section_83", "REG_1_83_4": "section_83",
                "SECTION_351_CODE": "section_351", "REG_1_351_1": "section_351",
                "SECTION_357_CODE": "section_351", "SECTION_358_CODE": "section_351",
                "SECTION_362_CODE": "section_351", "REG_1_351_3": "section_351",
                "SECTION_368_C_CODE": "section_351", "REG_1_358_2": "section_351", "SECTION_1012_CODE": "section_351",
                "SECTION_1202_CODE": "section_1202", "SECTION_1244_CODE": "section_1244",
            }[rule]
            if authority["doctrine"] != expected_doctrine or not rule_sources:
                raise AssertionError(f"{tranche['tranche_id']}: {rule} authority source family is invalid")
        gate_values = list(tranche["gates"].values())
        tax_values = list(tranche["tax_positions"].values())
        if "CONFLICTED" in gate_values:
            derived_tranche = "FACT_CONFLICT"
        elif "COUNSEL_HOLD" in gate_values or "COUNSEL_HOLD" in tax_values:
            derived_tranche = "COUNSEL_HOLD"
        elif "UNVERIFIED" in gate_values or "UNVERIFIED" in tax_values:
            derived_tranche = "CLOSING_PENDING"
        else:
            derived_tranche = "ISSUED_AND_RECONCILED"
        if tranche["status"] != derived_tranche:
            raise AssertionError(f"{tranche['tranche_id']}: claims {tranche['status']} but gates derive {derived_tranche}")
        derived_tranche_statuses.append(derived_tranche)
        manifest = assert_safe_artifact_path(
            WORKSPACE / tranche["closing_manifest_path"], f"{tranche['tranche_id']} closing manifest"
        )
        try:
            manifest.relative_to(subject_root)
        except ValueError as exc:
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest is outside subject stock records") from exc
        if tranche["tranche_id"] not in manifest.name:
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest filename is not tranche-bound")
        if not manifest.is_file() or sha256(manifest.read_bytes()).hexdigest() != tranche["closing_manifest_sha256"]:
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest missing or hash-mismatched")
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_schema = json.loads(read("schemas/stock-issuance-closing-manifest.schema.json"))
        manifest_failures = schema_errors(manifest_data, manifest_schema)
        if manifest_failures:
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest schema failure: {manifest_failures[:10]}")
        exact_fields = ("subject_entity_slug", "tranche_id", "issuance_date", "class", "holder_slug", "shares", "price_per_share", "total_consideration")
        expected_manifest_values = {
            "subject_entity_slug": subject,
            **{field: tranche[field] for field in exact_fields if field != "subject_entity_slug"},
        }
        if any(manifest_data[field] != expected_manifest_values[field] for field in exact_fields):
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest terms do not exact-match the audit")
        closing = manifest_data["closing_facts"]
        approval_signed_at = datetime.fromisoformat(closing["approval_signed_at"].replace("Z", "+00:00"))
        received_at = datetime.fromisoformat(closing["received_at"].replace("Z", "+00:00"))
        issued_at = datetime.fromisoformat(closing["issued_at"].replace("Z", "+00:00"))
        notice_at = datetime.fromisoformat(closing["notice_delivered_at"].replace("Z", "+00:00"))
        journal_at = datetime.fromisoformat(closing["journal_posted_at"].replace("Z", "+00:00"))
        if (
            closing["payer_slug"] != tranche["holder_slug"]
            or closing["payee_entity_slug"] != subject
            or closing["amount_received"] != tranche["total_consideration"]
            or issued_at.date() != issuance_date
        ):
            raise AssertionError(f"{tranche['tranche_id']}: approval, consideration, or issuance facts do not exact-match")
        if parse_date(closing["approval_date"]) > issuance_date or approval_signed_at > issued_at:
            raise AssertionError(f"{tranche['tranche_id']}: approving authority postdates issuance")
        if notice_at < issued_at or journal_at < issued_at or max(approval_signed_at, received_at, issued_at, notice_at, journal_at) > cutoff_at:
            raise AssertionError(f"{tranche['tranche_id']}: closing event chronology is invalid")
        if closing["consideration_legal_timing"] == "RECEIVED_BEFORE_OR_AT_ISSUANCE" and received_at > issued_at:
            raise AssertionError(f"{tranche['tranche_id']}: consideration timing claim is false")
        property_consideration = closing["consideration_type"] in {"CASH", "PROPERTY", "DEBT_CONVERSION", "SAFE_NOTE_CONVERSION", "MIXED"}
        if property_consideration != facts["property_transfer"] or closing["substantially_nonvested"] != facts["substantially_nonvested"]:
            raise AssertionError(f"{tranche['tranche_id']}: closing consideration facts do not match tax-fact flags")
        if closing["consideration_type"] == "SERVICES" and tranche["tax_positions"]["section_83"] == "NOT_APPLICABLE":
            raise AssertionError(f"{tranche['tranche_id']}: services consideration cannot mark §83 not applicable")
        federal_routes = {
            authority["route"] for authority in tranche["securities_authorities"]
            if authority["jurisdiction"] == "United States"
        }
        if closing["federal_securities_route"] not in federal_routes:
            raise AssertionError(f"{tranche['tranche_id']}: closing federal securities route does not match authority")
        state_route_rows = closing["state_securities_routes"]
        state_jurisdictions = [item["jurisdiction"] for item in state_route_rows]
        if len(state_jurisdictions) != len(set(state_jurisdictions)) or set(state_jurisdictions) != securities_jurisdictions - {"United States"}:
            raise AssertionError(f"{tranche['tranche_id']}: closing state securities coverage is incomplete")
        for state_route in state_route_rows:
            matching_routes = {
                authority["route"] for authority in tranche["securities_authorities"]
                if authority["jurisdiction"] == state_route["jurisdiction"]
            }
            resolved_at = datetime.fromisoformat(state_route["filed_or_resolved_at"].replace("Z", "+00:00"))
            if state_route["substantive_route"] not in matching_routes or resolved_at > cutoff_at:
                raise AssertionError(f"{tranche['tranche_id']}: closing state route or resolution time is invalid")
            if state_route["notice_requirement_status"] == "REQUIRED_FILED_ACCEPTED" and "WA_NOTICE" not in matching_routes:
                raise AssertionError(f"{tranche['tranche_id']}: required state notice lacks a validated notice route")
            if state_route["deadline"] is not None and resolved_at.date() > parse_date(state_route["deadline"]):
                raise AssertionError(f"{tranche['tranche_id']}: state securities notice missed its recorded deadline")
        kinds = [artifact["kind"] for artifact in manifest_data["artifacts"]]
        required_kinds = {"BOARD_APPROVAL", "PURCHASE_OR_SUBSCRIPTION_AGREEMENT", "CONSIDERATION_PROOF", "CERTIFICATE_OR_NOTICE", "STOCK_LEDGER", "CAP_TABLE", "TAX_MEMO", "SECURITIES_MEMO"}
        if set(kinds) != required_kinds or len(kinds) != len(set(kinds)):
            raise AssertionError(f"{tranche['tranche_id']}: closing manifest artifact coverage is incomplete or duplicated")
        artifact_paths = [artifact["path"] for artifact in manifest_data["artifacts"]]
        artifact_hashes = [artifact["sha256"] for artifact in manifest_data["artifacts"]]
        if len(artifact_paths) != len(set(artifact_paths)) or len(artifact_hashes) != len(set(artifact_hashes)):
            raise AssertionError(f"{tranche['tranche_id']}: closing artifacts must be distinct physical evidence")
        expected_facts = {
            "class": tranche["class"], "holder_slug": tranche["holder_slug"],
            "shares": tranche["shares"], "price_per_share": tranche["price_per_share"],
            "total_consideration": tranche["total_consideration"],
        }
        for artifact in manifest_data["artifacts"]:
            if (
                artifact["evidence_subject_slug"] != subject
                or artifact["tranche_id"] != tranche["tranche_id"]
                or artifact["extracted_facts"] != expected_facts
            ):
                raise AssertionError(f"{tranche['tranche_id']}: closing artifact extracted facts do not exact-match")
            observed_at = datetime.fromisoformat(artifact["observed_at"].replace("Z", "+00:00"))
            document_date = parse_date(artifact["document_date"])
            if observed_at > cutoff_at or document_date > parse_date(result["as_of"]):
                raise AssertionError(f"{tranche['tranche_id']}: closing artifact date exceeds the audit cutoff")
            if artifact["kind"] in {"BOARD_APPROVAL", "PURCHASE_OR_SUBSCRIPTION_AGREEMENT", "CONSIDERATION_PROOF"} and document_date > issuance_date:
                raise AssertionError(f"{tranche['tranche_id']}: prerequisite closing evidence postdates issuance")
            required_professional = {
                "TAX_MEMO": {"TAX_COUNSEL", "CPA_EA"},
                "SECURITIES_MEMO": {"SECURITIES_COUNSEL"},
            }.get(artifact["kind"])
            if required_professional and artifact["professional_review_role"] not in required_professional:
                raise AssertionError(f"{tranche['tranche_id']}: closing memo lacks required professional review")
            artifact_path = assert_safe_artifact_path(WORKSPACE / artifact["path"], f"{tranche['tranche_id']} {artifact['kind']}")
            try:
                artifact_path.relative_to(subject_root)
            except ValueError as exc:
                raise AssertionError(f"{tranche['tranche_id']}: closing artifact is outside subject stock records") from exc
            if not artifact_path.is_file() or sha256(artifact_path.read_bytes()).hexdigest() != artifact["sha256"]:
                raise AssertionError(f"{tranche['tranche_id']}: closing artifact missing or hash-mismatched")
        signed_at = datetime.fromisoformat(manifest_data["signoff"]["signed_at"].replace("Z", "+00:00"))
        if signed_at > cutoff_at or signed_at.date() < issuance_date:
            raise AssertionError(f"{tranche['tranche_id']}: closing signoff time is invalid")
    if "FACT_CONFLICT" in derived_tranche_statuses:
        derived_overall = "FACT_CONFLICT"
    elif "COUNSEL_HOLD" in derived_tranche_statuses:
        derived_overall = "COUNSEL_HOLD"
    elif "CLOSING_PENDING" in derived_tranche_statuses:
        derived_overall = "CLOSING_PENDING"
    else:
        derived_overall = "ISSUED_AND_RECONCILED"
    if result["overall_status"] != derived_overall:
        raise AssertionError(f"stock specialist claims {result['overall_status']} but tranches derive {derived_overall}")
    if require_reconciled and derived_overall != "ISSUED_AND_RECONCILED":
        raise AssertionError(f"stock specialist is not reconciled: {derived_overall}")
    tax_statuses = [
        status
        for tranche in result["tranches"]
        for status in tranche["tax_positions"].values()
    ]
    if "COUNSEL_HOLD" in tax_statuses:
        return "COUNSEL_HOLD"
    if "UNVERIFIED" in tax_statuses:
        return "PROVISIONAL"
    has_provisional = "ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL" in tax_statuses
    has_ineligible = any(status in {"INELIGIBLE", "ISSUANCE_DATE_INELIGIBLE"} for status in tax_statuses)
    if has_provisional and has_ineligible:
        return "MIXED"
    if has_provisional:
        return "PROVISIONAL"
    if has_ineligible:
        return "INELIGIBLE"
    return "VERIFIED"


def validate_generic_specialist_result(path: Path, parent_audit: dict, row: dict) -> None:
    path = assert_safe_artifact_path(path, f"{row['id']} specialist result")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"{row['id']}: specialist result is unreadable: {exc}") from exc
    schema = json.loads(read("schemas/corporate-specialist-result.schema.json"))
    failures = schema_errors(result, schema)
    if failures:
        raise AssertionError(f"{row['id']}: specialist result schema failure: {failures[:10]}")
    subject = parent_audit["subject"]["entity_slug"]
    period = parent_audit["subject"]["tax_periods"][0]
    expected_kind = {
        "P-01": "ACCOUNTABLE_PLAN",
        "P-02": "AUGUSTA_PLAN",
        "P-03": "OTHER_TAX_SPECIALIST",
        "S-03": "IP_REMEDIATION",
    }.get(row["id"])
    if row.get("execution_method") == "COUNSEL_OR_COURT_VALIDATION":
        expected_kind = "LEGAL_VALIDATION"
    if expected_kind is None:
        raise AssertionError(f"{row['id']}: no generic specialist controller is defined for this control")
    if result["kind"] != expected_kind or result["subject_entity_slug"] != subject or result["fiscal_or_tax_period"] != period:
        raise AssertionError(f"{row['id']}: specialist kind, subject, or FY binding is wrong")
    if result["as_of"] != parent_audit["scope"]["as_of"] or result["source_cutoff"] != parent_audit["scope"]["source_cutoff"]:
        raise AssertionError(f"{row['id']}: specialist cutoff differs from corporate audit")
    if row["id"] not in result["control_ids"] or result["status"] != row["specialist_result_status"]:
        raise AssertionError(f"{row['id']}: specialist control or status does not match the row")
    gate_values = list(result["gates"].values())
    if "CONFLICTED" in gate_values or "COUNSEL_HOLD" in gate_values:
        derived_status = "COUNSEL_HOLD"
    elif "UNVERIFIED" in gate_values:
        derived_status = "PROVISIONAL"
    else:
        derived_status = result["status"]
        if derived_status not in {"VERIFIED", "INELIGIBLE"}:
            raise AssertionError(f"{row['id']}: fully resolved gates cannot derive {derived_status}")
    if result["status"] != derived_status:
        raise AssertionError(
            f"{row['id']}: specialist claims {result['status']} but gates derive {derived_status}"
        )
    cutoff_at = datetime.fromisoformat(result["source_cutoff"].replace("Z", "+00:00"))
    as_of = parse_date(result["as_of"])
    authority_ids: set[str] = set()
    observed_rules: set[str] = set()
    for authority in result["authority_dependencies"]:
        if authority["authority_id"] in authority_ids:
            raise AssertionError(f"{row['id']}: duplicate specialist authority ID")
        authority_ids.add(authority["authority_id"])
        parsed = urlparse(authority["source_url"])
        host = (parsed.hostname or "").lower()
        path_text = parsed.path.lower()
        if parsed.scheme != "https" or not host.endswith(".gov"):
            raise AssertionError(f"{row['id']}: specialist authority is not official HTTPS .gov")
        if datetime.fromisoformat(authority["verified_at"].replace("Z", "+00:00")) > cutoff_at:
            raise AssertionError(f"{row['id']}: specialist authority verified after cutoff")
        effective_from = parse_date(authority["effective_from"])
        effective_to = parse_date(authority["effective_to"])
        if (effective_from and as_of < effective_from) or (effective_to and as_of > effective_to):
            raise AssertionError(f"{row['id']}: specialist authority is ineffective as of the audit")
        rule = authority["rule"]
        rule_source_ok = {
            "ACCOUNTABLE_PLAN_1_62_2": host_is(host, "ecfr.gov") and path_text.endswith("/section-1.62-2"),
            "AUGUSTA_280A": host_is(host, "uscode.house.gov") and house_code_section(parsed, "280A"),
            "BUSINESS_RENT_162": host_is(host, "uscode.house.gov") and house_code_section(parsed, "162"),
            "RELATED_PARTY_267": host_is(host, "uscode.house.gov") and house_code_section(parsed, "267"),
            "WA_CORPORATE_LAW": host_is(host, "app.leg.wa.gov") and path_text.rstrip("/") == "/rcw/default.aspx" and any(value.lower().startswith("23b") for value in parse_qs(parsed.query).get("cite", [])),
            "WA_COURT_VALIDATION": host_is(host, "courts.wa.gov"),
            "USPTO_ASSIGNMENT": host_is(host, "uspto.gov") and "assignment" in path_text,
            "IRS_P15B": host_is(host, "irs.gov") and path_text.rstrip("/").endswith("/p15b"),
        }[rule]
        if not rule_source_ok:
            raise AssertionError(f"{row['id']}: {rule} specialist authority source family is invalid")
        observed_rules.add(rule)
    required_rules = {
        "ACCOUNTABLE_PLAN": {"ACCOUNTABLE_PLAN_1_62_2"},
        "AUGUSTA_PLAN": {"AUGUSTA_280A", "BUSINESS_RENT_162", "RELATED_PARTY_267"},
        "IP_REMEDIATION": {"WA_CORPORATE_LAW"},
        "LEGAL_VALIDATION": set(),
        "OTHER_TAX_SPECIALIST": {"IRS_P15B"},
    }[result["kind"]]
    if result["kind"] == "LEGAL_VALIDATION" and not observed_rules.intersection({"WA_CORPORATE_LAW", "WA_COURT_VALIDATION"}):
        raise AssertionError(f"{row['id']}: legal validation lacks recognized controlling authority")
    if not required_rules.issubset(observed_rules):
        raise AssertionError(f"{row['id']}: specialist authority set is incomplete for {result['kind']}")
    subject_root = (WORKSPACE / "entities" / subject).resolve()
    source_kinds = [artifact["kind"] for artifact in result["source_artifacts"]]
    source_paths = [artifact["path"] for artifact in result["source_artifacts"]]
    if len(source_kinds) != len(set(source_kinds)) or len(source_paths) != len(set(source_paths)):
        raise AssertionError(f"{row['id']}: specialist source kinds and paths must be unique")
    if result["status"] in {"VERIFIED", "INELIGIBLE"}:
        required_source_kinds = {
            "ACCOUNTABLE_PLAN": {"EXECUTED_PLAN", "RECONCILIATION"},
            "AUGUSTA_PLAN": {"TRANSACTION_RECORD", "PAYMENT_PROOF", "RECONCILIATION"},
            "IP_REMEDIATION": {"IP_ASSIGNMENT", "LEGAL_MEMO"},
            "LEGAL_VALIDATION": {"LEGAL_MEMO"},
            "OTHER_TAX_SPECIALIST": {"TAX_MEMO"},
        }[result["kind"]]
        if not required_source_kinds.issubset(source_kinds):
            raise AssertionError(f"{row['id']}: final specialist status lacks controller-required evidence kinds")
    for artifact in result["source_artifacts"]:
        artifact_path = assert_safe_artifact_path(WORKSPACE / artifact["path"], f"{row['id']} specialist source")
        try:
            artifact_path.relative_to(subject_root)
        except ValueError as exc:
            raise AssertionError(f"{row['id']}: specialist source is outside subject entity") from exc
        if not artifact_path.is_file() or sha256(artifact_path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"{row['id']}: specialist source missing or hash-mismatched")


def run_generic_specialist_fixtures(fixtures: list[dict]) -> None:
    global WORKSPACE
    names = [fixture["name"] for fixture in fixtures]
    assert len(names) == len(set(names)) and len(fixtures) >= 22, (
        "generic specialist artifact fixture set is incomplete or duplicated"
    )
    original_workspace = WORKSPACE
    try:
        for fixture in fixtures:
            with tempfile.TemporaryDirectory(
                prefix=".corporate-specialist-eval-", dir=ROOT / "evals"
            ) as temp_dir:
                WORKSPACE = Path(temp_dir)
                specialist_dir = WORKSPACE / "entities/test-corp/corporate/accountable-plan"
                specialist_dir.mkdir(parents=True)
                source_path = specialist_dir / "executed-plan.pdf"
                source_path.write_bytes(b"executed accountable plan fixture\n")
                result = {
                    "schema_version": "1.0",
                    "kind": "ACCOUNTABLE_PLAN",
                    "subject_entity_slug": "test-corp",
                    "fiscal_or_tax_period": "FY2026",
                    "as_of": "2026-08-25",
                    "source_cutoff": "2026-08-25T12:00:00-07:00",
                    "status": "PROVISIONAL",
                    "control_ids": ["P-01"],
                    "conclusion": "Adopted; annual operation remains unreconciled.",
                    "gates": {
                        "authority": "VERIFIED", "applicability": "VERIFIED",
                        "execution": "VERIFIED", "operation": "UNVERIFIED",
                        "tax": "UNVERIFIED", "source_reconciliation": "UNVERIFIED",
                    },
                    "authority_dependencies": [{
                        "authority_id": "run-fixture-accountable-plan",
                        "rule": "ACCOUNTABLE_PLAN_1_62_2",
                        "source_url": "https://www.ecfr.gov/current/title-26/section-1.62-2",
                        "verified_at": "2026-08-25T10:00:00-07:00",
                        "effective_from": None,
                        "effective_to": None,
                        "status": "VERIFIED",
                    }],
                    "source_artifacts": [{
                        "kind": "EXECUTED_PLAN",
                        "path": str(source_path.relative_to(WORKSPACE)),
                        "sha256": sha256(source_path.read_bytes()).hexdigest(),
                    }],
                }
                row = {"id": "P-01", "execution_method": "WRITTEN_CONSENT", "specialist_result_status": "PROVISIONAL"}
                for change in fixture.get("changes", []):
                    target = result if change["target"] == "result" else row
                    cursor = target
                    for segment in change["path"][:-1]:
                        cursor = cursor[segment]
                    cursor[change["path"][-1]] = change["value"]
                operation = fixture.get("operation")
                def specialist_source(kind: str, name: str) -> dict:
                    extra_path = specialist_dir / name
                    extra_path.write_bytes(f"{kind} fixture\n".encode())
                    return {
                        "kind": kind, "path": str(extra_path.relative_to(WORKSPACE)),
                        "sha256": sha256(extra_path.read_bytes()).hexdigest(),
                    }

                if operation in {
                    "make_augusta_verified", "make_augusta_missing_267", "make_ip_verified", "make_ip_spoofed",
                    "make_legal_verified", "make_legal_spoofed", "make_other_tax_verified", "make_other_tax_spoofed",
                    "make_irrelevant_t01_specialist",
                }:
                    result["status"] = "VERIFIED"
                    result["gates"] = {key: "VERIFIED" for key in result["gates"]}
                    row["specialist_result_status"] = "VERIFIED"
                if operation in {"make_augusta_verified", "make_augusta_missing_267"}:
                    result["kind"] = "AUGUSTA_PLAN"
                    result["control_ids"] = ["P-02"]
                    row["id"] = "P-02"
                    result["authority_dependencies"] = [
                        {"authority_id":"run-augusta-280a","rule":"AUGUSTA_280A","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section280A","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                        {"authority_id":"run-augusta-162","rule":"BUSINESS_RENT_162","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section162","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                        {"authority_id":"run-augusta-267","rule":"RELATED_PARTY_267","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section267","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                    ]
                    if operation == "make_augusta_missing_267":
                        result["authority_dependencies"].pop()
                    result["source_artifacts"] = [
                        specialist_source("TRANSACTION_RECORD", "event.pdf"),
                        specialist_source("PAYMENT_PROOF", "payment.pdf"),
                        specialist_source("RECONCILIATION", "reconciliation.pdf"),
                    ]
                elif operation in {"make_ip_verified", "make_ip_spoofed"}:
                    result["kind"] = "IP_REMEDIATION"
                    result["control_ids"] = ["S-03"]
                    row["id"] = "S-03"
                    result["authority_dependencies"] = [{
                        "authority_id":"run-ip-wa","rule":"WA_CORPORATE_LAW",
                        "source_url":"https://example.gov/unrelated" if operation == "make_ip_spoofed" else "https://app.leg.wa.gov/rcw/default.aspx?cite=23B",
                        "verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED",
                    }]
                    result["source_artifacts"] = [specialist_source("IP_ASSIGNMENT", "assignment.pdf"), specialist_source("LEGAL_MEMO", "legal-memo.pdf")]
                elif operation in {"make_legal_verified", "make_legal_spoofed"}:
                    result["kind"] = "LEGAL_VALIDATION"
                    result["control_ids"] = ["F-02"]
                    row.update(id="F-02", execution_method="COUNSEL_OR_COURT_VALIDATION")
                    result["authority_dependencies"] = [{
                        "authority_id":"run-legal-wa","rule":"WA_COURT_VALIDATION",
                        "source_url":"https://example.gov/unrelated" if operation == "make_legal_spoofed" else "https://www.courts.wa.gov/court_rules/",
                        "verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED",
                    }]
                    result["source_artifacts"] = [specialist_source("LEGAL_MEMO", "validation-memo.pdf")]
                elif operation in {"make_other_tax_verified", "make_other_tax_spoofed"}:
                    result["kind"] = "OTHER_TAX_SPECIALIST"
                    result["control_ids"] = ["P-03"]
                    row["id"] = "P-03"
                    result["authority_dependencies"] = [{
                        "authority_id":"run-benefits","rule":"IRS_P15B",
                        "source_url":"https://www.irs.gov/forms-pubs/about-form-1120" if operation == "make_other_tax_spoofed" else "https://www.irs.gov/publications/p15b",
                        "verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED",
                    }]
                    result["source_artifacts"] = [specialist_source("TAX_MEMO", "tax-memo.pdf")]
                elif operation == "make_irrelevant_t01_specialist":
                    result["kind"] = "OTHER_TAX_SPECIALIST"
                    result["control_ids"] = ["T-01"]
                    row["id"] = "T-01"
                    result["authority_dependencies"] = [{
                        "authority_id":"run-irrelevant-benefits","rule":"IRS_P15B",
                        "source_url":"https://www.irs.gov/publications/p15b",
                        "verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED",
                    }]
                    result["source_artifacts"] = [specialist_source("TAX_MEMO", "irrelevant-tax-memo.pdf")]
                if operation in {"make_verified", "make_verified_without_reconciliation"}:
                    result["status"] = "VERIFIED"
                    row["specialist_result_status"] = "VERIFIED"
                    result["gates"] = {key: "VERIFIED" for key in result["gates"]}
                if operation == "make_verified":
                    rec_path = specialist_dir / "annual-reconciliation.pdf"
                    rec_path.write_bytes(b"annual reconciliation fixture\n")
                    result["source_artifacts"].append({
                        "kind": "RECONCILIATION",
                        "path": str(rec_path.relative_to(WORKSPACE)),
                        "sha256": sha256(rec_path.read_bytes()).hexdigest(),
                    })
                elif operation == "corrupt_source":
                    source_path.write_bytes(b"changed after specialist result\n")
                elif operation == "duplicate_source_path":
                    result["source_artifacts"].append({
                        "kind": "OTHER",
                        "path": result["source_artifacts"][0]["path"],
                        "sha256": result["source_artifacts"][0]["sha256"],
                    })
                result_path = specialist_dir / "status.json"
                result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                parent = {
                    "subject": {"entity_slug": "test-corp", "tax_periods": ["FY2026"]},
                    "scope": {"as_of": "2026-08-25", "source_cutoff": "2026-08-25T12:00:00-07:00"},
                }
                try:
                    validate_generic_specialist_result(result_path, parent, row)
                except (AssertionError, json.JSONDecodeError) as exc:
                    assert not fixture["expect_valid"], f"{fixture['name']}: unexpected rejection: {exc}"
                    assert fixture["expect_contains"] in str(exc), (
                        f"{fixture['name']}: expected {fixture['expect_contains']!r}; got {exc}"
                    )
                else:
                    assert fixture["expect_valid"], f"{fixture['name']}: hostile artifact unexpectedly passed"
    finally:
        WORKSPACE = original_workspace


def stable_evidence(row_id: str, subject: str, proves: str, role: str = "CURRENT") -> dict:
    token = sha256(f"{subject}:{row_id}:{proves}".encode()).hexdigest()
    return {
        "source_path": f"fixtures/{subject}/{row_id.lower()}.pdf",
        "sha256": token,
        "agency_record_id": None,
        "document_kind": DEFAULT_EVIDENCE_KIND[row_id],
        "locator": "page 1 / fixture control",
        "evidence_subject_slug": subject,
        "role": role,
        "proves": proves,
        "observed_on": "2026-08-25",
        "observed_at": "2026-08-25T12:00:00-07:00",
    }


def agency_evidence(
    source_url: str, record_id: str, subject: str, proves: str, document_kind: str = "OTHER"
) -> dict:
    return {
        "source_path": source_url,
        "sha256": None,
        "agency_record_id": record_id,
        "document_kind": document_kind,
        "locator": "official current agency page",
        "evidence_subject_slug": subject,
        "role": "CURRENT",
        "proves": proves,
        "observed_on": "2026-08-25",
        "observed_at": "2026-08-25T12:00:00-07:00",
    }


def make_clean_artifact(template: dict) -> dict:
    audit = deepcopy(template)
    audit["subject"] = {
        "legal_name": "Test Corporation",
        "entity_slug": "test-corp",
        "legal_form": "C corporation",
        "formation_jurisdiction": "Washington",
        "tax_periods": ["FY2026"],
    }
    audit["scope"] = {
        "as_of": "2026-08-25",
        "source_cutoff": "2026-08-25T12:00:00-07:00",
        "jurisdictions": ["Washington", "United States"],
        "years": ["2026"],
        "paths_searched": ["entities/test-corp/corporate"],
        "exclusions": [],
    }
    audit["intake_status"] = "RECONCILED"
    audit["overall_status"] = "RECORD_SET_RECONCILED_AS_OF"
    audit["formation_chronology"] = {
        "formation_effective_date": "2024-01-03",
        "initial_directors_named_in_articles": False,
        "incorporator_action_date": "2024-01-04",
        "initial_director_action_date": "2024-01-04",
        "earliest_purported_corporate_action_date": "2024-01-04",
        "authority_order": ["FORMATION_EFFECTIVE", "INCORPORATOR_ACTION", "INITIAL_DIRECTOR_ACTION"],
        "sequence_status": "VERIFIED_AFTER_INCORPORATION",
        "evidence": [stable_evidence("F-01", "test-corp", "Formation effective date and post-formation sequence")],
    }
    audit["authority_dependencies"] = [
        {
            "authority_id": "AUTH-WA-CORP",
            "issue": "Washington corporate organization, annual action, and records",
            "jurisdiction": "Washington",
            "domain": "CORPORATE_LAW",
            "control_ids": ["F-01", "F-02", "F-03", "F-04", "O-01", "O-02", "O-03", "R-01", "A-01", "A-02", "P-01", "P-02", "P-03", "L-01", "S-01", "S-02"],
            "rules_path": "authority.md#AUTH-WA-CORP",
            "primary_source": "https://app.leg.wa.gov/rcw/default.aspx?cite=23B",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-FINCEN-BOI",
            "issue": "Current BOI reporting-company rule",
            "jurisdiction": "United States",
            "domain": "FEDERAL_BOI",
            "control_ids": ["L-03"],
            "rules_path": "authority.md#AUTH-FINCEN-BOI",
            "primary_source": "https://www.fincen.gov/boi",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": "2026-08-14",
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-US-TAX",
            "issue": "Federal corporate tax records and filing evidence",
            "jurisdiction": "United States",
            "domain": "FEDERAL_TAX",
            "control_ids": ["O-04", "T-01", "T-02"],
            "rules_path": "authority.md#AUTH-US-TAX",
            "primary_source": "https://www.irs.gov/forms-pubs/about-form-1120",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-WA-LICENSE",
            "issue": "Washington licensing and revenue-account applicability",
            "jurisdiction": "Washington",
            "domain": "STATE_TAX_LICENSE",
            "control_ids": ["L-02"],
            "rules_path": "authority.md#AUTH-WA-LICENSE",
            "primary_source": "https://dor.wa.gov/open-business/apply-business-license",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-IRS-EIN",
            "issue": "Federal employer identification number evidence",
            "jurisdiction": "United States",
            "domain": "FEDERAL_TAX",
            "control_ids": ["F-05"],
            "rules_path": "authority.md#AUTH-IRS-EIN",
            "primary_source": "https://www.irs.gov/businesses/small-businesses-self-employed/employer-id-numbers",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-IRS-PAYROLL",
            "issue": "Employer payroll and employment-tax records",
            "jurisdiction": "United States",
            "domain": "PAYROLL",
            "control_ids": ["T-03"],
            "rules_path": "authority.md#AUTH-IRS-PAYROLL",
            "primary_source": "https://www.irs.gov/publications/p15",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-ACCOUNTABLE-PLAN",
            "issue": "Accountable-plan requirements",
            "jurisdiction": "United States",
            "domain": "FEDERAL_TAX",
            "control_ids": ["P-01"],
            "rules_path": "authority.md#AUTH-ACCOUNTABLE-PLAN",
            "primary_source": "https://www.ecfr.gov/current/title-26/section-1.62-2",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-SECTION-280A",
            "issue": "Section 280A(g) residence-rental requirements",
            "jurisdiction": "United States",
            "domain": "FEDERAL_TAX",
            "control_ids": ["P-02"],
            "rules_path": "authority.md#AUTH-SECTION-280A",
            "primary_source": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section280A",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-EMPLOYEE-BENEFITS",
            "issue": "Employer benefit-program tax records",
            "jurisdiction": "United States",
            "domain": "FEDERAL_TAX",
            "control_ids": ["P-03"],
            "rules_path": "authority.md#AUTH-EMPLOYEE-BENEFITS",
            "primary_source": "https://www.irs.gov/publications/p15b",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
        {
            "authority_id": "AUTH-US-IP",
            "issue": "Federal IP assignment and ownership-record controls",
            "jurisdiction": "United States",
            "domain": "CONTRACT_IP",
            "control_ids": ["S-03"],
            "rules_path": "authority.md#AUTH-US-IP",
            "primary_source": "https://www.uspto.gov/patents/maintain/patents-assignments-change-search-ownership",
            "verified_on": "2026-08-25",
            "verified_at": "2026-08-25T11:00:00-07:00",
            "effective_from": None,
            "effective_to": None,
            "effective_for_scope": True,
        },
    ]
    audit["conflicts"] = []

    for row in audit["requirements"]:
        row_id = row["id"]
        row["subject_entity_slug"] = "test-corp"
        if row["fiscal_or_tax_period"] != "PERMANENT":
            row["fiscal_or_tax_period"] = "FY2026"
        row["responsible_person"] = "Corporate records owner"
        if row_id == "L-03":
            authority_id, jurisdiction, domain = "AUTH-FINCEN-BOI", "United States", "FEDERAL_BOI"
        elif row_id == "L-02":
            authority_id, jurisdiction, domain = "AUTH-WA-LICENSE", "Washington", "STATE_TAX_LICENSE"
        elif row_id == "F-05":
            authority_id, jurisdiction, domain = "AUTH-IRS-EIN", "United States", "FEDERAL_TAX"
        elif row_id == "T-03":
            authority_id, jurisdiction, domain = "AUTH-IRS-PAYROLL", "United States", "PAYROLL"
        elif row_id == "P-01":
            authority_id, jurisdiction, domain = "AUTH-ACCOUNTABLE-PLAN", "United States", "FEDERAL_TAX"
        elif row_id == "P-02":
            authority_id, jurisdiction, domain = "AUTH-SECTION-280A", "United States", "FEDERAL_TAX"
        elif row_id == "P-03":
            authority_id, jurisdiction, domain = "AUTH-EMPLOYEE-BENEFITS", "United States", "FEDERAL_TAX"
        elif row_id == "S-03":
            authority_id, jurisdiction, domain = "AUTH-US-IP", "United States", "CONTRACT_IP"
        elif row_id in {"O-04", "T-01", "T-02"}:
            authority_id, jurisdiction, domain = "AUTH-US-TAX", "United States", "FEDERAL_TAX"
        else:
            authority_id, jurisdiction, domain = "AUTH-WA-CORP", "Washington", "CORPORATE_LAW"
        row["authority_basis_id"] = authority_id
        row["additional_authority_basis_ids"] = []
        row["governing_jurisdiction"] = jurisdiction
        row["authority_domain"] = domain
        row["authority_verified"] = True
        row["approving_actor"] = "Competent agency or corporate actor"
        row["execution_method"] = "NOT_APPLICABLE"
        row["conflict_ids"] = []
        row["deadline"] = None
        row["next_required_evidence"] = None
        row["escalation"] = ["NONE"]
        row["exclusion_id"] = None
        row["dates"] = {key: None for key in row["dates"]}
        row["signature_evidence"] = {
            "method": "NOT_APPLICABLE",
            "signer_identity": "NOT_APPLICABLE",
            "document_integrity": "NOT_APPLICABLE",
            "notes": None,
        }

        if row["applicability_status"] == "CONDITIONAL_UNRESOLVED" or row_id == "L-03":
            row.update(
                applicability_status="NOT_APPLICABLE_VERIFIED",
                lifecycle_status="NOT_FOUND",
                verification_status="VERIFIED",
                operational_status="NOT_APPLICABLE",
                filing_status="NOT_APPLICABLE",
                tax_position_status="NOT_APPLICABLE",
                specialist_result_reference=None,
            )
            if row_id == "L-03":
                row["evidence"] = [agency_evidence(
                    "https://www.fincen.gov/boi",
                    "FINCEN-BOI-FINAL-RULE-2026-08-14",
                    "test-corp",
                    "Current domestic-entity BOI nonapplicability authority",
                    "BOI_AUTHORITY_OR_FILING",
                )]
                row["evidence"].append(stable_evidence("F-01", "test-corp", "U.S. formation jurisdiction established"))
            else:
                row["evidence"] = [stable_evidence(row_id, "test-corp", "Facts and current authority establish nonapplicability")]
            continue

        row.update(
            applicability_status="REQUIRED",
            lifecycle_status="ACCEPTED_OR_ISSUED" if row_id in FILING_IDS else "EXECUTED_EFFECTIVE",
            verification_status="VERIFIED",
            operational_status="RECONCILED" if row_id in OPERATION_IDS else "NOT_APPLICABLE",
            filing_status="ACCEPTED" if row_id in FILING_IDS else "NOT_APPLICABLE",
            tax_position_status="NOT_TESTED" if row["requirement_class"] == "TAX/ACCOUNTING REQUIRED" else "NOT_APPLICABLE",
            specialist_result_reference=None,
        )
        if row_id in FILING_IDS:
            row["dates"]["accepted_or_issued"] = "2026-08-20"
            row["execution_method"] = "AGENCY_OR_EXTERNAL_RECORD"
        else:
            row["dates"]["effective"] = "2026-01-15"
            row["dates"]["approved"] = "2026-01-15"
            row["execution_method"] = "MEETING_MINUTES" if row_id in {"A-01", "A-02"} else "OTHER_VERIFIED"
            if row_id == "F-02":
                row["dates"]["effective"] = "2024-01-04"
                row["dates"]["approved"] = "2024-01-04"
                row["dates"]["signed"] = "2024-01-04"
                row["execution_method"] = "WRITTEN_CONSENT"
                row["signature_evidence"] = {
                    "method": "HANDWRITTEN_OR_IMAGE_OBSERVED",
                    "signer_identity": "VERIFIED",
                    "document_integrity": "VERIFIED",
                    "notes": "Fixture incorporator action",
                }
            elif row_id in {"F-03", "F-04"}:
                row["dates"]["effective"] = "2024-01-04"
                row["dates"]["approved"] = "2024-01-04"
                row["execution_method"] = "MEETING_MINUTES"
        row["evidence"] = [stable_evidence(row_id, "test-corp", "Current requirement reconciled")]
        if row_id == "R-01":
            row["record_subcontrols"] = []
            for subcontrol_id, document_kind in RECORD_SUBCONTROL_KINDS.items():
                token = sha256(f"test-corp:R-01:{subcontrol_id}".encode()).hexdigest()
                row["record_subcontrols"].append({
                    "id": subcontrol_id,
                    "status": "VERIFIED",
                    "evidence_period": "FY2026" if subcontrol_id in {"ANNUAL_FINANCIAL_STATEMENTS", "SHAREHOLDER_COMMUNICATIONS"} else "PERMANENT",
                    "deadline": None,
                    "evidence": [{
                        "source_path": (
                            f"fixtures/test-corp/FY2026-r-01-{subcontrol_id.lower()}.pdf"
                            if subcontrol_id in {"ANNUAL_FINANCIAL_STATEMENTS", "SHAREHOLDER_COMMUNICATIONS"}
                            else f"fixtures/test-corp/r-01-{subcontrol_id.lower()}.pdf"
                        ),
                        "sha256": token,
                        "agency_record_id": None,
                        "document_kind": document_kind,
                        "locator": "fixture subcontrol",
                        "evidence_subject_slug": "test-corp",
                        "role": "CURRENT",
                        "proves": f"{subcontrol_id} current record",
                        "observed_on": "2026-08-25",
                        "observed_at": "2026-08-25T12:00:00-07:00",
                    }],
                    "next_required_evidence": None,
                })
    return audit


def deep_update(target: dict, changes: dict) -> None:
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = deepcopy(value)


def apply_fixture(clean: dict, fixture: dict) -> dict:
    audit = deepcopy(clean)
    if "subject_updates" in fixture:
        deep_update(audit["subject"], fixture["subject_updates"])
    if "scope_updates" in fixture:
        deep_update(audit["scope"], fixture["scope_updates"])
    if "authority_updates" in fixture:
        authorities = {item["authority_id"]: item for item in audit["authority_dependencies"]}
        for authority_id, changes in fixture["authority_updates"].items():
            deep_update(authorities[authority_id], changes)
    if "all_rows_update" in fixture:
        for row in audit["requirements"]:
            deep_update(row, fixture["all_rows_update"])
    if "scope_exclusions" in fixture:
        audit["scope"]["exclusions"] = deepcopy(fixture["scope_exclusions"])
    if "chronology_updates" in fixture:
        deep_update(audit["formation_chronology"], fixture["chronology_updates"])
    if "conflicts" in fixture:
        audit["conflicts"] = deepcopy(fixture["conflicts"])
    rows = {row["id"]: row for row in audit["requirements"]}
    for row_id, changes in fixture.get("row_updates", {}).items():
        had_explicit_evidence = "evidence" in changes
        deep_update(rows[row_id], changes)
        if not had_explicit_evidence:
            rows[row_id]["evidence"] = [stable_evidence(row_id, "test-corp", f"Fixture evidence for {fixture['name']}")]
    if "record_subcontrol_updates" in fixture:
        subcontrols = {item["id"]: item for item in rows["R-01"].get("record_subcontrols", [])}
        for subcontrol_id, changes in fixture["record_subcontrol_updates"].items():
            deep_update(subcontrols[subcontrol_id], changes)
    expected_strategy_authority = {
        "P-01": "AUTH-ACCOUNTABLE-PLAN",
        "P-02": "AUTH-SECTION-280A",
        "P-03": "AUTH-EMPLOYEE-BENEFITS",
    }
    for row_id, authority_id in expected_strategy_authority.items():
        if rows[row_id].get("additional_authority_basis_ids") == ["AUTH-US-TAX"]:
            rows[row_id]["additional_authority_basis_ids"] = [authority_id]
    if "truncate_requirements_to" in fixture:
        keep = set(fixture["truncate_requirements_to"])
        audit["requirements"] = [row for row in audit["requirements"] if row["id"] in keep]
    if "expected_overall" in fixture:
        audit["overall_status"] = fixture["expected_overall"]
    if "claimed_overall" in fixture:
        audit["overall_status"] = fixture["claimed_overall"]
    for row in audit["requirements"]:
        if row.get("specialist_result_reference"):
            if row["id"] == "S-03" and row["specialist_result_reference"] == "corporate/ip-remediation-counsel-packet.md":
                row["specialist_result_reference"] = "corporate/ip-remediation/counsel-packet.md"
            if not row["specialist_result_reference"].startswith("entities/"):
                row["specialist_result_reference"] = f"entities/test-corp/{row['specialist_result_reference']}"
            row.setdefault(
                "specialist_result_sha256",
                sha256(f"specialist:{fixture['name']}:{row['id']}".encode()).hexdigest(),
            )
            row.setdefault("specialist_result_subject_slug", "test-corp")
            row.setdefault("specialist_result_period", "FY2026")
            row.setdefault(
                "specialist_result_status",
                row["tax_position_status"] if row["tax_position_status"] in {"PROVISIONAL", "INELIGIBLE", "MIXED", "COUNSEL_HOLD"} else "VERIFIED",
            )
    for evidence in audit["formation_chronology"]["evidence"]:
        evidence.setdefault("document_kind", "AUTHORITY_CHAIN")
        evidence.setdefault("observed_at", f"{evidence['observed_on']}T12:00:00-07:00")
    for conflict in audit["conflicts"]:
        for evidence in conflict["resolution_evidence"]:
            evidence.setdefault("document_kind", "OTHER")
            evidence.setdefault("observed_at", f"{evidence['observed_on']}T12:00:00-07:00")
    for row in audit["requirements"]:
        for evidence in row["evidence"]:
            evidence.setdefault("document_kind", DEFAULT_EVIDENCE_KIND[row["id"]])
            evidence.setdefault("observed_at", f"{evidence['observed_on']}T12:00:00-07:00")
        for subcontrol in row.get("record_subcontrols", []):
            for evidence in subcontrol["evidence"]:
                evidence.setdefault("document_kind", RECORD_SUBCONTROL_KINDS[subcontrol["id"]])
                evidence.setdefault("observed_at", f"{evidence['observed_on']}T12:00:00-07:00")
    return audit


def schema_errors(audit: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{list(error.path)}: {error.message}" for error in validator.iter_errors(audit)]


def cross_field_errors(audit: dict, artifact_path: Path | None = None, verify_files: bool = False) -> list[str]:
    errors: list[str] = []
    subject = audit["subject"]["entity_slug"]
    as_of = parse_date(audit["scope"]["as_of"])
    source_cutoff_at = datetime.fromisoformat(audit["scope"]["source_cutoff"].replace("Z", "+00:00"))
    source_cutoff = source_cutoff_at.date()
    if as_of > date.today():
        errors.append("as_of is in the future")
    if source_cutoff > as_of:
        errors.append("source_cutoff occurs after as_of")
    for searched_path in audit["scope"]["paths_searched"]:
        candidate = Path(searched_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (WORKSPACE / candidate).resolve()
        if "privileged" in searched_path.lower() or "privileged" in str(resolved).lower():
            errors.append(f"scope path enters privileged material: {searched_path}")
        try:
            resolved.relative_to(WORKSPACE.resolve())
        except ValueError:
            errors.append(f"scope path escapes workspace: {searched_path}")
        else:
            if verify_files and not resolved.exists():
                errors.append(f"scope path does not exist: {searched_path}")

    rows = audit["requirements"]
    row_ids = [row["id"] for row in rows]
    if tuple(sorted(row_ids)) != tuple(sorted(CANONICAL_IDS)) or len(row_ids) != len(set(row_ids)):
        errors.append("requirements must contain each canonical ID exactly once")

    authority_map = {item["authority_id"]: item for item in audit["authority_dependencies"]}
    authority_ids = set(authority_map)
    if len(authority_ids) != len(audit["authority_dependencies"]):
        errors.append("authority dependency IDs must be unique")
    for item in audit["authority_dependencies"]:
        if verify_files and not item["authority_id"].startswith("run-"):
            errors.append(f"{item['authority_id']}: instantiated audits require run-specific authority IDs")
        if any(control_id not in CANONICAL_IDS for control_id in item["control_ids"]):
            errors.append(f"{item['authority_id']}: authority lists an unknown control ID")
        parsed_source = urlparse(item["primary_source"])
        if parsed_source.scheme != "https" or not parsed_source.hostname or not parsed_source.hostname.lower().endswith(".gov"):
            errors.append(f"{item['authority_id']}: primary source is not an official HTTPS .gov host")
        else:
            authority_host = parsed_source.hostname.lower()
            authority_path = parsed_source.path.lower()
            authority_query = parse_qs(parsed_source.query)
            domain_source_ok = {
                "CORPORATE_LAW": (
                    audit["subject"]["formation_jurisdiction"] == "Washington"
                    and host_is(authority_host, "app.leg.wa.gov")
                    and authority_path.rstrip("/") == "/rcw/default.aspx"
                    and any(value.lower().startswith("23b") for value in authority_query.get("cite", []))
                ),
                "FEDERAL_TAX": host_is(authority_host, "irs.gov") or host_is(authority_host, "ecfr.gov") or host_is(authority_host, "uscode.house.gov"),
                "FEDERAL_BOI": host_is(authority_host, "fincen.gov") and authority_path.startswith("/boi"),
                "SECURITIES": host_is(authority_host, "sec.gov") or host_is(authority_host, "dfi.wa.gov"),
                "STATE_TAX_LICENSE": host_is(authority_host, "dor.wa.gov"),
                "PAYROLL": host_is(authority_host, "irs.gov") and authority_path.rstrip("/").endswith("/p15"),
                "CONTRACT_IP": host_is(authority_host, "uspto.gov") and "assignment" in authority_path,
            }[item["domain"]]
            if not domain_source_ok:
                errors.append(f"{item['authority_id']}: primary source is irrelevant to its authority domain")
        if item["authority_id"].startswith("run-"):
            if item["rules_path"] != "authority.md#run-specific-authority":
                errors.append(f"{item['authority_id']}: run-specific authority uses the wrong authority contract path")
        elif "#" not in item["rules_path"] or not item["rules_path"].endswith(item["authority_id"]):
            errors.append(f"{item['authority_id']}: rules_path is not bound to its fixture authority ID")
        rules_file = item["rules_path"].split("#", 1)[0]
        rules_candidate = (ROOT / rules_file).resolve()
        try:
            rules_candidate.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{item['authority_id']}: rules_path escapes the tax skill")
        else:
            if not rules_candidate.is_file():
                errors.append(f"{item['authority_id']}: rules_path does not resolve to a skill file")
        if item["jurisdiction"] not in audit["scope"]["jurisdictions"]:
            errors.append(f"{item['authority_id']}: authority jurisdiction is outside audit scope")
        if parse_date(item["verified_on"]) > as_of:
            errors.append(f"{item['authority_id']}: verified_on is after as_of")
        verified_at = datetime.fromisoformat(item["verified_at"].replace("Z", "+00:00"))
        if verified_at.date() != parse_date(item["verified_on"]):
            errors.append(f"{item['authority_id']}: verified_at and verified_on disagree")
        if verified_at > source_cutoff_at:
            errors.append(f"{item['authority_id']}: authority was verified after source_cutoff")
        effective_from = parse_date(item["effective_from"])
        effective_to = parse_date(item["effective_to"])
        if effective_from and effective_to and effective_from > effective_to:
            errors.append(f"{item['authority_id']}: authority effective dates are reversed")
        if item["effective_for_scope"] and (
            (effective_from and as_of < effective_from) or (effective_to and as_of > effective_to)
        ):
            errors.append(f"{item['authority_id']}: claimed effective authority does not cover as_of")

    tax_periods = audit["subject"]["tax_periods"]
    scope_years = audit["scope"]["years"]
    if len(tax_periods) != 1 or not re.fullmatch(r"FY[0-9]{4}", tax_periods[0]):
        errors.append("artifact must cover exactly one concrete FY period")
    if len(scope_years) != 1 or not re.fullmatch(r"[0-9]{4}", scope_years[0]):
        errors.append("scope must contain exactly one concrete year")
    if tax_periods and scope_years and tax_periods[0] != f"FY{scope_years[0]}":
        errors.append("subject tax period and scope year do not match")
    formation_jurisdiction = audit["subject"]["formation_jurisdiction"]
    if formation_jurisdiction not in audit["scope"]["jurisdictions"]:
        errors.append("formation jurisdiction is outside audit scope")

    evidence_identity_kinds: dict[tuple, str] = {}

    def check_evidence(evidence: dict, context: str, allowed_kinds: set[str] | None = None) -> None:
        if allowed_kinds is not None and evidence["document_kind"] not in allowed_kinds:
            errors.append(f"{context}: evidence kind is incompatible with this control")
        identity = (evidence["source_path"], evidence["sha256"], evidence["agency_record_id"])
        prior_kind = evidence_identity_kinds.get(identity)
        if prior_kind is not None and prior_kind != evidence["document_kind"]:
            errors.append(f"{context}: the same evidence identity is assigned incompatible document kinds")
        evidence_identity_kinds[identity] = evidence["document_kind"]
        if evidence["evidence_subject_slug"] != subject:
            errors.append(f"{context}: evidence belongs to a different legal entity")
        observed = parse_date(evidence["observed_on"])
        if observed > as_of or observed > source_cutoff:
            errors.append(f"{context}: evidence observed after audit cutoff")
        observed_at = datetime.fromisoformat(evidence["observed_at"].replace("Z", "+00:00"))
        if observed_at.date() != observed:
            errors.append(f"{context}: observed_at and observed_on disagree")
        if observed_at > source_cutoff_at:
            errors.append(f"{context}: evidence captured after source_cutoff")
        source_path = evidence["source_path"]
        if "privileged" in source_path.lower():
            errors.append(f"{context}: privileged path is excluded from this audit")
        if evidence["sha256"] is not None and verify_files:
            candidate = Path(source_path)
            try:
                resolved = assert_safe_artifact_path(
                    candidate if candidate.is_absolute() else WORKSPACE / candidate,
                    f"{context} evidence",
                )
            except AssertionError as exc:
                errors.append(str(exc))
                return
            if not resolved.is_file():
                errors.append(f"{context}: evidence file does not exist: {source_path}")
            elif sha256(resolved.read_bytes()).hexdigest() != evidence["sha256"]:
                errors.append(f"{context}: SHA-256 does not match evidence file")
        if evidence["agency_record_id"] is not None:
            parsed = urlparse(source_path)
            if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.lower().endswith(".gov"):
                errors.append(f"{context}: agency-record evidence lacks an official HTTPS .gov source")

    chronology = audit["formation_chronology"]
    formation = parse_date(chronology["formation_effective_date"])
    named = chronology["initial_directors_named_in_articles"]
    action_dates = [
        parse_date(chronology[key])
        for key in ("incorporator_action_date", "initial_director_action_date", "earliest_purported_corporate_action_date")
        if chronology[key] is not None
    ]
    row_authority_dates = [
        parse_date(value)
        for row in rows
        if row["id"] in {"F-03", "F-04"} or (row["id"] == "F-02" and named is False)
        for key, value in row["dates"].items()
        if key in {"approved", "signed", "effective"} and value is not None
    ]
    earliest_claimed = parse_date(chronology["earliest_purported_corporate_action_date"])
    if row_authority_dates and (earliest_claimed is None or earliest_claimed > min(row_authority_dates)):
        errors.append("formation chronology omits an earlier dated authority action")
    action_dates.extend(row_authority_dates)
    incorporator = parse_date(chronology["incorporator_action_date"])
    initial_director = parse_date(chronology["initial_director_action_date"])
    expected_order = (
        ["FORMATION_EFFECTIVE", "INCORPORATOR_ACTION", "INITIAL_DIRECTOR_ACTION"]
        if named is False
        else ["FORMATION_EFFECTIVE", "INITIAL_DIRECTOR_ACTION"]
    )
    authority_event_dates = [initial_director] if initial_director else []
    if named is False and incorporator:
        authority_event_dates.append(incorporator)
    authority_event_dates.extend(row_authority_dates)
    earliest_matches_authority = bool(
        earliest_claimed is not None
        and authority_event_dates
        and earliest_claimed == min(authority_event_dates)
    )
    if formation is None or named is None or initial_director is None or (named is False and incorporator is None):
        derived_sequence = "UNVERIFIED"
    elif any(action < formation for action in action_dates) or initial_director < formation or (incorporator and incorporator < formation):
        derived_sequence = "PREINCORPORATION_ACTION_PRESENT"
    elif not earliest_matches_authority or chronology["authority_order"] != expected_order or (named is False and initial_director < incorporator):
        derived_sequence = "AUTHORITY_ORDER_DEFECT"
    else:
        derived_sequence = "VERIFIED_AFTER_INCORPORATION"
    if chronology["sequence_status"] != derived_sequence:
        errors.append(f"formation chronology claims {chronology['sequence_status']} but dates derive {derived_sequence}")
    if chronology["sequence_status"] != "UNVERIFIED" and not any(evidence["role"] == "CURRENT" for evidence in chronology["evidence"]):
        errors.append("formation chronology lacks CURRENT evidence")
    for evidence in chronology["evidence"]:
        check_evidence(
            evidence,
            "formation chronology",
            {"ARTICLES_OR_AMENDMENT", "AUTHORITY_CHAIN", "INCORPORATOR_ACTION", "ORGANIZATIONAL_ACTION"},
        )

    conflict_map = {item["id"]: item for item in audit["conflicts"]}
    if len(conflict_map) != len(audit["conflicts"]):
        errors.append("conflict IDs must be unique")
    exclusion_map = {item["id"]: item for item in audit["scope"]["exclusions"]}
    if len(exclusion_map) != len(audit["scope"]["exclusions"]):
        errors.append("exclusion IDs must be unique")

    for row in rows:
        row_id = row["id"]
        if row["subject_entity_slug"] != subject:
            errors.append(f"{row_id}: row subject differs from audit subject")
        if row["fiscal_or_tax_period"] != "PERMANENT" and row["fiscal_or_tax_period"] not in tax_periods:
            errors.append(f"{row_id}: row period is outside the audited FY")
        if not row.get("governing_jurisdiction") or row["governing_jurisdiction"] not in audit["scope"]["jurisdictions"]:
            errors.append(f"{row_id}: governing jurisdiction is absent or outside scope")
        if not row.get("authority_domain"):
            errors.append(f"{row_id}: authority domain is missing")
        if row.get("authority_domain") == "CORPORATE_LAW" and row.get("governing_jurisdiction") != formation_jurisdiction:
            errors.append(f"{row_id}: corporate-law jurisdiction does not match formation jurisdiction")
        if row["authority_verified"]:
            if not row["authority_basis_id"] or row["authority_basis_id"] not in authority_ids:
                errors.append(f"{row_id}: verified authority lacks a canonical authority dependency")
            else:
                authority = authority_map[row["authority_basis_id"]]
                if authority["jurisdiction"] != row.get("governing_jurisdiction") or authority["domain"] != row.get("authority_domain"):
                    errors.append(f"{row_id}: authority jurisdiction/domain does not match the row")
                if row_id not in authority["control_ids"]:
                    errors.append(f"{row_id}: selected authority does not identify this control")
                if not authority["effective_for_scope"]:
                    errors.append(f"{row_id}: verified authority is not effective for audit scope")
                authority_dates = [
                    parse_date(value)
                    for key, value in row["dates"].items()
                    if key not in {"expires", "superseded"} and value is not None
                ]
                effective_from = parse_date(authority["effective_from"])
                effective_to = parse_date(authority["effective_to"])
                if any(
                    (effective_from and action_date < effective_from)
                    or (effective_to and action_date > effective_to)
                    for action_date in authority_dates
                ):
                    errors.append(f"{row_id}: authority effective period does not cover a row action date")
                required_authority_source = {
                    "F-05": ("irs.gov", "employer-id-numbers"),
                    "T-01": ("irs.gov", "about-form-1120"),
                    "T-03": ("irs.gov", "/p15"),
                    "L-03": ("fincen.gov", "/boi"),
                    "S-03": ("uspto.gov", "assignment"),
                }.get(row_id)
                if required_authority_source:
                    parsed_authority = urlparse(authority["primary_source"])
                    source_text = authority["primary_source"].lower()
                    expected_host, expected_fragment = required_authority_source
                    if not parsed_authority.hostname or not host_is(parsed_authority.hostname, expected_host) or expected_fragment not in source_text:
                        errors.append(f"{row_id}: selected authority source is not issue-specific for this control")
        additional_ids = row.get("additional_authority_basis_ids", [])
        if row.get("authority_basis_id") in additional_ids:
            errors.append(f"{row_id}: primary authority is duplicated as an additional authority")
        for additional_id in additional_ids:
            if additional_id not in authority_ids:
                errors.append(f"{row_id}: additional authority lacks a canonical authority dependency")
            elif not authority_map[additional_id]["effective_for_scope"]:
                errors.append(f"{row_id}: additional authority is not effective for audit scope")
            elif row_id not in authority_map[additional_id]["control_ids"]:
                errors.append(f"{row_id}: additional authority does not identify this control")
            else:
                additional = authority_map[additional_id]
                additional_from = parse_date(additional["effective_from"])
                additional_to = parse_date(additional["effective_to"])
                row_action_dates = [
                    parse_date(value)
                    for key, value in row["dates"].items()
                    if key not in {"expires", "superseded"} and value is not None
                ]
                if any(
                    (additional_from and action_date < additional_from)
                    or (additional_to and action_date > additional_to)
                    for action_date in row_action_dates
                ):
                    errors.append(f"{row_id}: additional authority period does not cover a row action date")
        if row["lifecycle_status"] == "EXECUTED_EFFECTIVE" and row_id in {"P-01", "P-02", "P-03"}:
            domains = {
                authority_map[authority_id]["domain"]
                for authority_id in [row.get("authority_basis_id"), *additional_ids]
                if authority_id in authority_map
            }
            if not {"CORPORATE_LAW", "FEDERAL_TAX"}.issubset(domains):
                errors.append(f"{row_id}: executed tax strategy lacks both corporate-law and federal-tax authority")
            def strategy_source_matches(authority_id: str) -> bool:
                if authority_id not in authority_map:
                    return False
                parsed_strategy = urlparse(authority_map[authority_id]["primary_source"])
                strategy_host = parsed_strategy.hostname or ""
                strategy_path = parsed_strategy.path.lower().rstrip("/")
                return {
                    "P-01": host_is(strategy_host, "ecfr.gov") and strategy_path.endswith("/section-1.62-2"),
                    "P-02": house_code_section(parsed_strategy, "280A"),
                    "P-03": host_is(strategy_host, "irs.gov") and strategy_path.endswith("/p15b"),
                }[row_id]
            if not any(strategy_source_matches(authority_id) for authority_id in additional_ids):
                errors.append(f"{row_id}: executed tax strategy lacks its issue-specific federal authority")
        if row["verification_status"] == "VERIFIED" and row["applicability_status"] in {"REQUIRED", "RECOMMENDED_ONLY"}:
            if not any(evidence["role"] == "CURRENT" for evidence in row["evidence"]):
                errors.append(f"{row_id}: current requirement lacks CURRENT evidence")
        for evidence in row["evidence"]:
            check_evidence(evidence, row_id, EVIDENCE_KINDS_BY_ROW[row_id])
        if row_id == "R-01":
            subcontrols = row.get("record_subcontrols", [])
            subcontrol_ids = [item["id"] for item in subcontrols]
            if set(subcontrol_ids) != set(RECORD_SUBCONTROL_KINDS) or len(subcontrol_ids) != len(set(subcontrol_ids)):
                errors.append("R-01: permanent-record subcontrols must appear exactly once")
            for subcontrol in subcontrols:
                subcontrol_id = subcontrol["id"]
                if subcontrol["status"] == "VERIFIED" and not any(
                    evidence["role"] == "CURRENT" for evidence in subcontrol["evidence"]
                ):
                    errors.append(f"R-01/{subcontrol_id}: verified subcontrol lacks current evidence")
                if subcontrol["status"] == "NOT_YET_DUE" and (
                    subcontrol["deadline"] is None or parse_date(subcontrol["deadline"]) <= as_of
                ):
                    errors.append(f"R-01/{subcontrol_id}: not-yet-due status lacks a future deadline")
                if subcontrol["status"] == "NOT_YET_DUE" and subcontrol_id not in {
                    "ANNUAL_FINANCIAL_STATEMENTS", "SHAREHOLDER_COMMUNICATIONS"
                }:
                    errors.append(f"R-01/{subcontrol_id}: permanent core record cannot be not yet due")
                expected_subcontrol_period = (
                    tax_periods[0]
                    if subcontrol_id in {"ANNUAL_FINANCIAL_STATEMENTS", "SHAREHOLDER_COMMUNICATIONS"}
                    else "PERMANENT"
                )
                if subcontrol["evidence_period"] != expected_subcontrol_period:
                    errors.append(f"R-01/{subcontrol_id}: evidence period does not match the audited year")
                if subcontrol["status"] == "VERIFIED" and expected_subcontrol_period.startswith("FY") and not all(
                    expected_subcontrol_period in Path(evidence["source_path"]).name
                    for evidence in subcontrol["evidence"]
                ):
                    errors.append(f"R-01/{subcontrol_id}: annual evidence filename is not FY-bound")
                if subcontrol["status"] == "MISSING" and not subcontrol["next_required_evidence"]:
                    errors.append(f"R-01/{subcontrol_id}: missing subcontrol lacks next required evidence")
                for evidence in subcontrol["evidence"]:
                    check_evidence(evidence, f"R-01/{subcontrol_id}", {RECORD_SUBCONTROL_KINDS[subcontrol_id]})
        for key, value in row["dates"].items():
            if value is not None and parse_date(value) > as_of:
                errors.append(f"{row_id}: {key} date is after as_of")
        for conflict_id in row["conflict_ids"]:
            if conflict_id not in conflict_map or row_id not in conflict_map[conflict_id]["requirement_ids"]:
                errors.append(f"{row_id}: conflict link {conflict_id} is not reciprocal")
        if row["verification_status"] == "CONFLICTED" and not row["conflict_ids"]:
            errors.append(f"{row_id}: conflicted row lacks a global conflict link")
        if row["applicability_status"] == "OUT_OF_SCOPE":
            exclusion = exclusion_map.get(row["exclusion_id"])
            if not exclusion or row_id not in exclusion["requirement_ids"]:
                errors.append(f"{row_id}: OUT_OF_SCOPE is not bound to its disclosed exclusion")
        if row["tax_position_status"] in {"PROVISIONAL", "INELIGIBLE", "MIXED", "COUNSEL_HOLD"} and not row["specialist_result_reference"]:
            errors.append(f"{row_id}: tax status lacks specialist artifact reference")
        specialist_reference = row.get("specialist_result_reference")
        if specialist_reference:
            if not specialist_reference.endswith(".json"):
                errors.append(f"{row_id}: specialist result must be a typed JSON artifact")
            specialist_candidate = (WORKSPACE / specialist_reference).resolve()
            expected_root = (WORKSPACE / "entities" / subject).resolve()
            try:
                specialist_candidate.relative_to(expected_root)
            except ValueError:
                errors.append(f"{row_id}: specialist artifact is outside the subject entity")
            if "privileged" in specialist_reference.lower() or "privileged" in str(specialist_candidate).lower():
                errors.append(f"{row_id}: specialist artifact enters privileged material")
            if row.get("specialist_result_subject_slug") != subject:
                errors.append(f"{row_id}: specialist artifact subject binding is wrong")
            if row.get("specialist_result_period") not in tax_periods:
                errors.append(f"{row_id}: specialist artifact period is outside the audit")
            expected_specialist_status = row["tax_position_status"] if row["tax_position_status"] in {"PROVISIONAL", "INELIGIBLE", "MIXED", "COUNSEL_HOLD"} else "VERIFIED"
            if row.get("specialist_result_status") != expected_specialist_status:
                errors.append(f"{row_id}: specialist artifact status does not match the row conclusion")
            required_specialist_prefix = {
                "O-01": f"entities/{subject}/corporate/stock-issuances/",
                "O-02": f"entities/{subject}/corporate/stock-issuances/",
                "O-03": f"entities/{subject}/corporate/stock-issuances/",
                "O-04": f"entities/{subject}/corporate/stock-issuances/",
                "P-01": f"entities/{subject}/corporate/accountable-plan/",
                "P-02": f"entities/{subject}/corporate/augusta-plan/",
                "S-03": f"entities/{subject}/corporate/ip-remediation/",
            }.get(row_id)
            if row.get("execution_method") == "COUNSEL_OR_COURT_VALIDATION":
                required_specialist_prefix = f"entities/{subject}/corporate/legal-validations/"
            if required_specialist_prefix and not specialist_reference.startswith(required_specialist_prefix):
                errors.append(f"{row_id}: specialist artifact is outside its controller-specific location")
            if verify_files:
                try:
                    specialist_candidate = assert_safe_artifact_path(
                        WORKSPACE / specialist_reference, f"{row_id} specialist artifact"
                    )
                except AssertionError as exc:
                    errors.append(str(exc))
                    continue
                if not specialist_candidate.is_file():
                    errors.append(f"{row_id}: specialist artifact does not exist")
                elif sha256(specialist_candidate.read_bytes()).hexdigest() != row.get("specialist_result_sha256"):
                    errors.append(f"{row_id}: specialist artifact SHA-256 does not match")
        if row_id == "O-04" and row["applicability_status"] == "REQUIRED" and row["tax_position_status"] == "NOT_TESTED":
            errors.append("O-04: in-scope issuance tax position remains NOT_TESTED")
        if row_id == "O-04" and row["applicability_status"] == "REQUIRED":
            selected = authority_map.get(row.get("authority_basis_id"))
            if selected and "about-form-1120" in selected["primary_source"].lower():
                errors.append("O-04: generic Form 1120 authority cannot support issuance tax conclusions")
        if row["applicability_status"] == "NOT_APPLICABLE_VERIFIED" and not any(evidence["role"] == "CURRENT" for evidence in row["evidence"]):
            errors.append(f"{row_id}: verified nonapplicability lacks CURRENT evidence")
        if row_id == "L-03" and row["applicability_status"] == "NOT_APPLICABLE_VERIFIED" and len([e for e in row["evidence"] if e["role"] == "CURRENT"]) < 2:
            errors.append("L-03: domestic BOI nonapplicability needs current authority and formation-jurisdiction evidence")
        if row_id == "L-03" and row["applicability_status"] == "NOT_APPLICABLE_VERIFIED":
            current = [e for e in row["evidence"] if e["role"] == "CURRENT"]
            has_fincen = any(
                e["agency_record_id"] is not None
                and urlparse(e["source_path"]).hostname in {"fincen.gov", "www.fincen.gov"}
                for e in current
            )
            has_formation_record = any(e["sha256"] is not None for e in current)
            if not has_fincen or not has_formation_record:
                errors.append("L-03: domestic BOI nonapplicability needs distinct FinCEN authority and formation evidence")
        if row["lifecycle_status"] == "EXECUTED_EFFECTIVE" and row_id in OPERATION_IDS:
            method = row.get("execution_method")
            if not row["approving_actor"] or not row["authority_verified"] or method in {None, "NOT_APPLICABLE"}:
                errors.append(f"{row_id}: executed action lacks actor, authority, or execution method")
            if row_id in {"F-03", "F-04", "A-01", "A-02"} and method not in {"MEETING_MINUTES", "WRITTEN_CONSENT", "COUNSEL_OR_COURT_VALIDATION"}:
                errors.append(f"{row_id}: governance action needs meeting, consent, or counsel/court validation proof")
            if row_id == "F-02":
                allowed_f02_methods = (
                    {"AGENCY_OR_EXTERNAL_RECORD"}
                    if named is True
                    else {"WRITTEN_CONSENT", "MEETING_MINUTES", "COUNSEL_OR_COURT_VALIDATION"}
                )
                if method not in allowed_f02_methods:
                    errors.append("F-02: authority method does not match the named-director/incorporator branch")
            if method == "COUNSEL_OR_COURT_VALIDATION" and (
                not row["specialist_result_reference"] or "CORPORATE_COUNSEL" not in row["escalation"]
            ):
                errors.append(f"{row_id}: counsel/court validation lacks a specialist artifact and counsel route")
            if method == "MEETING_MINUTES" and row["dates"]["approved"] is None:
                errors.append(f"{row_id}: meeting action lacks meeting/approval date")
            if method == "WRITTEN_CONSENT" and (
                row["dates"]["signed"] is None
                or row["signature_evidence"]["method"] not in {"HANDWRITTEN_OR_IMAGE_OBSERVED", "CRYPTOGRAPHIC_VALIDATED", "OTHER"}
                or row["signature_evidence"]["signer_identity"] != "VERIFIED"
                or row["signature_evidence"]["document_integrity"] != "VERIFIED"
            ):
                errors.append(f"{row_id}: written consent lacks verified signature, identity, integrity, or date")
        if row_id == "F-02" and row["lifecycle_status"] == "EXECUTED_EFFECTIVE" and named is False:
            action_dates_for_row = [
                parse_date(row["dates"][key])
                for key in ("approved", "signed", "effective")
                if row["dates"][key] is not None
            ]
            if not incorporator or not action_dates_for_row or min(action_dates_for_row) != incorporator:
                errors.append("F-02: executed authority does not match the incorporator-action chronology")
        if row_id == "F-02" and row["lifecycle_status"] == "EXECUTED_EFFECTIVE" and named is True:
            if incorporator is not None or row["execution_method"] != "AGENCY_OR_EXTERNAL_RECORD":
                errors.append("F-02: named-director authority must come from filed articles without an incorporator action")
        if row_id in {"F-03", "F-04"} and row["lifecycle_status"] == "EXECUTED_EFFECTIVE":
            approval = parse_date(row["dates"]["approved"])
            if not initial_director or not approval or approval < initial_director:
                errors.append(f"{row_id}: approval predates or lacks initial-director authority")
        if row_id == "S-02" and row["applicability_status"] == "REQUIRED":
            references = row.get("related_entity_audit_references", [])
            seen_related: set[str] = set()
            for reference in references:
                related_slug = reference["entity_slug"]
                expected_path = f"entities/{related_slug}/corporate/corporate-records-audit-{tax_periods[0]}.json"
                if related_slug == subject or related_slug in seen_related or reference["audit_path"] != expected_path:
                    errors.append("S-02: subsidiary audit reference is not unique and subject-bound")
                seen_related.add(related_slug)
                if verify_files and not (WORKSPACE / reference["audit_path"]).is_file():
                    errors.append(f"S-02: referenced subsidiary audit does not exist: {reference['audit_path']}")

    for conflict in audit["conflicts"]:
        if conflict["status"] == "RESOLVED" and not conflict["resolution_evidence"]:
            errors.append(f"{conflict['id']}: resolved conflict lacks resolution evidence")
        for evidence in conflict["resolution_evidence"]:
            check_evidence(evidence, conflict["id"])
        for requirement_id in conflict["requirement_ids"]:
            if requirement_id not in row_ids:
                errors.append(f"{conflict['id']}: references unknown requirement {requirement_id}")
            else:
                row = next(item for item in rows if item["id"] == requirement_id)
                if conflict["id"] not in row["conflict_ids"]:
                    errors.append(f"{conflict['id']}: global conflict lacks reciprocal row link for {requirement_id}")
    ownership_rows = {row["id"]: row for row in rows if row["id"] in {"O-01", "O-02", "O-03", "O-04"}}
    if any(ownership_rows[row_id]["applicability_status"] == "REQUIRED" for row_id in {"O-02", "O-03", "O-04"}) and any(
        row["applicability_status"] != "REQUIRED" for row in ownership_rows.values()
    ):
        errors.append("O-01 through O-04 must all be REQUIRED when an issuance is in scope")
    if not any(
        ownership_rows[row_id]["applicability_status"] == "REQUIRED"
        for row_id in {"O-02", "O-03", "O-04"}
    ) and ownership_rows["O-01"].get("specialist_result_reference"):
        errors.append("O-01: zero-issuance capitalization must use direct reconciliation evidence, not an issuance audit")
    return errors


def derive_overall(audit: dict) -> str:
    rows = audit["requirements"]
    by_id = {row["id"]: row for row in rows}
    if audit["intake_status"] != "RECONCILED":
        return "EVIDENCE_INTAKE_PENDING"
    if audit["formation_chronology"]["sequence_status"] != "VERIFIED_AFTER_INCORPORATION":
        return "AUTHORITY_HOLD"
    if any(
        by_id[row_id]["verification_status"] == "CONFLICTED"
        or by_id[row_id]["operational_status"] in {"COUNSEL_HOLD", "DEFECTIVE"}
        or by_id[row_id]["lifecycle_status"] in {"NOT_FOUND", "DRAFT", "FINAL_UNSIGNED", "EXECUTED_AUTHORITY_UNVERIFIED", "UNREADABLE"}
        for row_id in AUTHORITY_IDS
    ):
        return "AUTHORITY_HOLD"
    if any(conflict["status"] == "OPEN" for conflict in audit["conflicts"]) or any(row["verification_status"] == "CONFLICTED" for row in rows):
        return "FACT_CONFLICT"
    if any(row["tax_position_status"] == "COUNSEL_HOLD" for row in rows):
        return "COUNSEL_HOLD"
    if any(row["operational_status"] in {"COUNSEL_HOLD", "DEFECTIVE"} for row in rows):
        return "COUNSEL_HOLD"
    if any(
        row["applicability_status"] in {"REQUIRED", "CONDITIONAL_UNRESOLVED"}
        and row["lifecycle_status"] in {"NOT_FOUND", "UNREADABLE", "EXPIRED"}
        for row in rows
    ):
        return "REQUIRED_RECORD_MISSING"
    if any(
        subcontrol["status"] == "MISSING"
        for subcontrol in by_id["R-01"].get("record_subcontrols", [])
    ):
        return "REQUIRED_RECORD_MISSING"
    if any(
        row["id"] not in FILING_IDS
        and row["applicability_status"] == "REQUIRED"
        and row["lifecycle_status"] in {"DRAFT", "FINAL_UNSIGNED", "EXECUTED_AUTHORITY_UNVERIFIED"}
        for row in rows
    ) or any(
        row["applicability_status"] == "REQUIRED" and row["operational_status"] == "APPROVED_NOT_EXECUTED"
        for row in rows
    ):
        return "EXECUTION_PENDING"
    if any(
        row["applicability_status"] == "REQUIRED"
        and row["operational_status"] in {"ACTIVE_NOT_YET_OPERATED", "OPERATED_NOT_RECONCILED", "PARTIAL_FAILURE"}
        for row in rows
    ):
        return "OPERATION_RECONCILIATION_PENDING"
    if any(
        row["id"] in FILING_IDS
        and row["applicability_status"] in {"REQUIRED", "CONDITIONAL_UNRESOLVED"}
        and row["filing_status"] in {"NOT_PREPARED", "DRAFT", "SIGNED_NOT_SUBMITTED", "SUBMITTED_UNCONFIRMED", "REJECTED"}
        for row in rows
    ):
        return "FILING_PENDING"
    if any(row["applicability_status"] == "CONDITIONAL_UNRESOLVED" for row in rows):
        return "REQUIRED_RECORD_MISSING"
    if any(row["applicability_status"] == "REQUIRED" and row["tax_position_status"] in {"PROVISIONAL", "MIXED"} for row in rows):
        return "CURRENT_WITH_DISCLOSED_NONMATERIAL_GAPS"
    if any(
        row["applicability_status"] == "RECOMMENDED_ONLY"
        and (
            row["lifecycle_status"] not in {"EXECUTED_EFFECTIVE", "ACCEPTED_OR_ISSUED"}
            or row["verification_status"] != "VERIFIED"
            or row["operational_status"] not in {"NOT_APPLICABLE", "RECONCILED"}
            or row["filing_status"] not in {"NOT_APPLICABLE", "ACCEPTED", "TRANSCRIPT_VERIFIED"}
        )
        for row in rows
    ):
        return "CURRENT_WITH_DISCLOSED_NONMATERIAL_GAPS"
    return "RECORD_SET_RECONCILED_AS_OF"


def validate_claimed_artifact(
    audit: dict, schema: dict, label: str, validation_stack: frozenset[Path] | None = None
) -> None:
    artifact_path = Path(label).resolve()
    validation_stack = validation_stack or frozenset()
    if artifact_path in validation_stack:
        raise AssertionError(f"{label}: cyclic related-entity audit reference")
    validation_stack = validation_stack | {artifact_path}
    path_errors: list[str] = []
    try:
        relative = artifact_path.relative_to(WORKSPACE.resolve())
    except ValueError:
        relative = None
        path_errors.append("audit artifact is outside the Business workspace")
    filename_match = re.fullmatch(r"corporate-records-audit-FY([0-9]{4})\.json", artifact_path.name)
    if not filename_match:
        path_errors.append("audit filename must be corporate-records-audit-FY<YYYY>.json")
    elif audit.get("subject", {}).get("tax_periods") != [f"FY{filename_match.group(1)}"]:
        path_errors.append("audit filename year does not match its single subject tax period")
    if relative is not None:
        expected = Path("entities") / audit.get("subject", {}).get("entity_slug", "") / "corporate" / artifact_path.name
        if relative != expected:
            path_errors.append(f"audit must use canonical entity path: {expected}")
        if "privileged" in str(relative).lower():
            path_errors.append("audit artifact may not be stored in a privileged path")
    schema_failures = schema_errors(audit, schema)
    cross_failures = [] if schema_failures else cross_field_errors(
        audit, artifact_path=artifact_path, verify_files=True
    )
    errors = schema_failures + cross_failures + path_errors
    if errors:
        raise AssertionError(f"{label}: invalid artifact:\n" + "\n".join(errors[:20]))
    derived = derive_overall(audit)
    assert audit["overall_status"] == derived, f"{label}: claims {audit['overall_status']}, derives {derived}"
    issuance_in_scope = any(
        row["id"] in {"O-02", "O-03", "O-04"} and row["applicability_status"] == "REQUIRED"
        for row in audit["requirements"]
    )
    stock_rows = [
        row for row in audit["requirements"]
        if issuance_in_scope and row["id"] in {"O-01", "O-02", "O-03", "O-04"}
    ]
    if stock_rows:
        stock_references = {row["specialist_result_reference"] for row in stock_rows}
        if len(stock_references) != 1:
            raise AssertionError(f"{label}: O-01/O-02/O-03/O-04 must share one validated stock-issuance audit")
        stock_tax_status = validate_stock_issuance_result(WORKSPACE / next(iter(stock_references)), audit)
        o04 = next((row for row in stock_rows if row["id"] == "O-04"), None)
        if o04 and (
            o04["tax_position_status"] != stock_tax_status
            or o04["specialist_result_status"] != stock_tax_status
        ):
            raise AssertionError(
                f"{label}: O-04 claims {o04['tax_position_status']} but stock specialist derives {stock_tax_status}"
            )
    for row in audit["requirements"]:
        specialist_reference = row.get("specialist_result_reference")
        if not specialist_reference or row["id"] in {"O-01", "O-02", "O-03", "O-04"}:
            continue
        validate_generic_specialist_result(WORKSPACE / specialist_reference, audit, row)
    for row in audit["requirements"]:
        if row["id"] != "S-02" or row["applicability_status"] != "REQUIRED":
            continue
        for reference in row.get("related_entity_audit_references", []):
            child_path = assert_safe_artifact_path(
                WORKSPACE / reference["audit_path"], f"{label}: subsidiary audit"
            )
            try:
                child = json.loads(child_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise AssertionError(f"{label}: unreadable subsidiary audit {reference['audit_path']}: {exc}") from exc
            if child.get("subject", {}).get("entity_slug") != reference["entity_slug"]:
                raise AssertionError(f"{label}: subsidiary audit subject does not match its reference")
            validate_claimed_artifact(child, schema, str(child_path), validation_stack)
            if row["verification_status"] == "VERIFIED" and row["operational_status"] == "RECONCILED":
                if child["scope"]["as_of"] != audit["scope"]["as_of"] or child["scope"]["source_cutoff"] != audit["scope"]["source_cutoff"]:
                    raise AssertionError(f"{label}: reconciled subsidiary audit cutoff differs from the parent")
                assert child["overall_status"] == "RECORD_SET_RECONCILED_AS_OF", (
                    f"{label}: S-02 claims reconciliation but {reference['entity_slug']} is "
                    f"{child['overall_status']}"
                )


def validate_artifact_fixtures(template: dict, schema: dict, fixtures: list[dict]) -> None:
    clean = make_clean_artifact(template)
    names = {fixture["name"] for fixture in fixtures}
    required = {
        "clean canonical record set", "E2 preincorporation action", "E3 missing authority and zero issued shares",
        "E4 capitalization conflict", "E9 valid plan not yet operated", "accountable plan payment partial failure",
        "E10 Augusta resolution only", "E12 expired license with renewal submitted", "E15 missing IP assignment",
        "E18 draft return not submitted", "rejected return transmission", "E19 visible signature identity unverified",
        "unsupported N/A with rejected filing", "executed signed record with unverified identity",
        "spoofed final tax election", "single-row false reconciliation", "future acceptance date",
        "authority row predates chronology register", "all rows excluded by generic scope claim",
        "required annual filing marked not applicable", "subsidiary evidence used for parent row",
        "none escalation mixed with counsel", "superseded-only required control",
        "future audit cutoff", "non-government authority URL", "historical-only nonapplicability",
        "reconciled chronology without evidence", "director action precedes incorporator authority",
        "same-day authority order is reversed",
        "purported action precedes proven authority", "formation state differs from corporate authority",
        "executed annual action lacks actor and method",
        "resolved conflict evidence belongs to other entity", "annual execution outranks draft filing",
        "existing evidence hash mismatch", "required subsidiary lacks separate audit",
        "annual row outside audited period",
        "evidence captured after same-day cutoff", "authority verified after same-day cutoff",
        "scope searches privileged material", "nonexistent specialist artifact",
        "authority starts after governed action", "instantiated audit rejects fixture authority IDs",
        "nonexistent evidence file",
        "payroll control uses unrelated tax source",
        "mandatory formation control marked not applicable", "required issuance lacks stock specialist",
        "O04 uses generic Form 1120 authority", "operation gap outranks filing gap",
        "claimed overall differs from recomputation", "one document reused for every corporate control",
        "named directors in filed articles valid authority branch",
        "corporate authority uses unrelated government source",
        "annual financial statements missing", "permanent record subcontrols omitted",
        "permanent core record falsely marked not yet due",
        "annual record evidence uses wrong fiscal year",
    }
    assert names == required, "artifact fixture set drifted"

    for fixture in fixtures:
        audit = apply_fixture(clean, fixture)
        schema_failures = schema_errors(audit, schema)
        cross_failures = cross_field_errors(
            audit, verify_files=fixture.get("verify_files", False)
        ) if not schema_failures else []
        if fixture.get("expected_schema_error"):
            assert schema_failures, f"{fixture['name']}: expected schema rejection"
            if fixture.get("expected_error_contains"):
                assert any(fixture["expected_error_contains"] in error for error in schema_failures), (
                    f"{fixture['name']}: expected schema error containing "
                    f"{fixture['expected_error_contains']!r}; got {schema_failures[:5]}"
                )
            continue
        assert not schema_failures, f"{fixture['name']}: unexpected schema errors: {schema_failures[:5]}"
        if fixture.get("expected_cross_field_error"):
            assert cross_failures, f"{fixture['name']}: expected cross-field rejection"
            if fixture.get("expected_error_contains"):
                assert any(fixture["expected_error_contains"] in error for error in cross_failures), (
                    f"{fixture['name']}: expected cross-field error containing "
                    f"{fixture['expected_error_contains']!r}; got {cross_failures[:5]}"
                )
            continue
        assert not cross_failures, f"{fixture['name']}: cross-field errors: {cross_failures[:5]}"
        actual = derive_overall(audit)
        if fixture.get("expected_claim_mismatch"):
            assert audit["overall_status"] != actual, f"{fixture['name']}: expected claimed/derived mismatch"
            continue
        assert actual == fixture["expected_overall"], f"{fixture['name']}: expected {fixture['expected_overall']}, got {actual}"
        assert audit["overall_status"] == actual


def structural_release_checks(schema: dict, template: dict) -> None:
    router = read("SKILL.md")
    records = read("scenarios/corporate-records.md")
    governance = read("governance.md")
    ccorp = read("entities/c-corp.md")
    stock = read("scenarios/stock-issuance.md")
    evals = read("evals/corporate-records.md")
    layout = read("layout.md")
    naming = read("naming.md")
    entity_template = read("templates/entity-config.md.template")
    federal_accounts = read("templates/federal-accounts.md.template")
    specialist_schema = json.loads(read("schemas/corporate-specialist-result.schema.json"))
    specialist_template = json.loads(read("templates/corporate-specialist-result.json.template"))

    require(router, ["corporate-records.md", "record-book", "formation cleanup", "annual governance"], "router")
    require(records, ["READ_ONLY_AUDIT", "INTAKE_RECONCILIATION", "Multi-axis evidence model", "OPERATION_RECONCILIATION_PENDING", "Reconciled-record-set invariant", "after incorporation", "zero shares issued", "no general §1244 or §1202 election/plan", "stock-issuance-audit-FY<YYYY>.json", "corporate-specialist-result.schema.json", "does not impose a categorical annual board-meeting requirement", "renewal submission is not an issued renewal", "final rule effective August 14, 2026", "subsidiary filings do not cure", "local `_processed.log`", "never backdate", "PARTIAL_FAILURE", "no federal “Augusta election”", "signed Form 8879/8453"], "corporate-records orchestrator")
    require(governance, ["corporate-records.md", "final rule", "domestic"], "governance backlink")
    require(ccorp, ["corporate-records.md"], "C-corp backlink")
    require(stock, ["corporate-records.md"], "stock backlink")
    require(layout, ["corporate-records-audit-FY<YYYY>.json"], "layout")
    require(naming, ["corporate-records-audit-FY<YYYY>.json"], "naming")
    require(entity_template, ["Corporate Records Audit Pointer", "corporate/corporate-records-audit-FY<YYYY>.json", "Do not duplicate"], "entity config pointer")
    require(federal_accounts, ["final rule effective", "foreign-law entities"], "current BOI account checklist")

    all_skill_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".template"}
    )
    forbid(all_skill_text, ["FinCEN BOIR filed (one-time + 30-day updates on changes)", "FinCEN Beneficial Ownership Information Report (BOIR) — initial + updates", "interim final rule", "No state requires a written consent for a single-member LLC distribution"], "skill-wide stale guidance")

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator.check_schema(specialist_schema)
    template_errors = schema_errors(template, schema)
    assert not template_errors, f"audit template violates schema: {template_errors[:10]}"
    specialist_template_errors = schema_errors(specialist_template, specialist_schema)
    assert not specialist_template_errors, (
        f"specialist template violates schema: {specialist_template_errors[:10]}"
    )
    assert [row["id"] for row in template["requirements"]] == list(CANONICAL_IDS)

    sections = {int(number): body for number, body in re.findall(r"^### E(\d+) —.*?\n(.*?)(?=^### E\d+ —|^## Scoring)", evals, flags=re.MULTILINE | re.DOTALL)}
    assert set(sections) == set(range(1, 21)), "eval suite must contain E1–E20"
    for case, body in sections.items():
        require(body, ["Mandatory result:"], f"eval E{case}")
    require(evals, ["RECORD_SET_RECONCILED_AS_OF", "EXECUTED_AUTHORITY_UNVERIFIED", "FINAL_UNSIGNED", "EVIDENCE_INTAKE_PENDING", "SUBMITTED_UNCONFIRMED", "visible handwritten", "does not authorize", "Independent corporate/securities, tax-counsel, and skill-red-team reviewers"], "substantive eval contract")


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--artifact", type=Path, help="validate one instantiated corporate-records-audit-FY<YYYY>.json")
    args = parser.parse_args()

    schema = json.loads(read("schemas/corporate-records-audit.schema.json"))
    if args.artifact:
        artifact_path = assert_safe_artifact_path(args.artifact, str(args.artifact))
        audit = json.loads(artifact_path.read_text(encoding="utf-8"))
        validate_claimed_artifact(audit, schema, str(artifact_path))
        print(f"PASS: {args.artifact} schema, cross-field invariants, and claimed overall status")
        return

    template = json.loads(read("templates/corporate-records-audit.json.template"))
    fixtures = json.loads(read("evals/corporate-records-artifact-fixtures.json"))
    specialist_fixtures = json.loads(read("evals/corporate-specialist-artifact-fixtures.json"))
    structural_release_checks(schema, template)
    validate_artifact_fixtures(template, schema, fixtures)
    run_generic_specialist_fixtures(specialist_fixtures)

    validated = 0
    for path in WORKSPACE.rglob("corporate-records-audit-FY*.json"):
        if "privileged" in str(path).lower():
            continue
        artifact_path = assert_safe_artifact_path(path, str(path))
        audit = json.loads(artifact_path.read_text(encoding="utf-8"))
        validate_claimed_artifact(audit, schema, str(artifact_path))
        validated += 1
    print(
        f"PASS: corporate-records release; 24-row schema, {len(fixtures)} record-set fixtures, "
        f"{len(specialist_fixtures)} specialist fixtures, 20 prose evals, {validated} instantiated audit(s)"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Semantic and structural release checks for close/estimate hardening."""

from __future__ import annotations

import argparse
import calendar
import json
import re
from copy import deepcopy
from datetime import date, datetime, timedelta
from math import ceil, floor, isclose
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules_freshness import load_rules
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time", raises=ValueError)
def is_iso_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.tzinfo is not None


def read(relative: str) -> str:
    path = ROOT / relative
    assert path.is_file(), f"missing required file: {relative}"
    return path.read_text(encoding="utf-8")


def get_rule_path(rules: dict, dotted: str):
    value = rules
    tokens = [match.group(1) if match.group(1) is not None else int(match.group(2)) for match in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", dotted)]
    for part in tokens:
        if isinstance(value, dict):
            key = str(part)
            assert key in value, f"bundled rule path does not exist: {dotted}"
            value = value[key]
        else:
            index = part
            assert isinstance(value, list) and index < len(value), f"bundled rule path does not exist: {dotted}"
            value = value[index]
    assert not isinstance(value, (dict, list)), f"bundled dependency must name an exact scalar leaf: {dotted}"
    return value


def load_rules_for_artifact(artifact: dict) -> dict:
    tax_year = artifact.get("tax_year")
    assert isinstance(tax_year, int), "artifact tax_year must be an integer"
    # Routed through the shared gate: an expired rules file must not reach a
    # computation from ANY consumer, not just the ones that opt in.
    return load_rules(tax_year)


def progressive_tax(income: float, brackets: list[list[float | None]]) -> float:
    tax = 0.0
    lower = 0.0
    for upper, rate in brackets:
        taxable = max(0.0, income - lower) if upper is None else max(0.0, min(income, upper) - lower)
        tax += taxable * rate
        if upper is None or income <= upper:
            break
        lower = upper
    return tax


def field_value(field: dict) -> float:
    allowed = {"OBSERVED_VALUE", "OBSERVED_ZERO", "DERIVED", "MANUAL_OVERRIDE"}
    assert field["state"] in allowed, f"field state cannot enter arithmetic: {field['state']}"
    assert field["value"] is not None, "allowed arithmetic field cannot have null value"
    return float(field["value"])


def individual_regular_installment(
    prior_tax: float | None,
    prior_eligible: bool,
    prior_high_income: bool,
    current_tax: float,
) -> float:
    alternatives = [0.90 * current_tax]
    if prior_eligible:
        assert prior_tax is not None
        alternatives.append(prior_tax * (1.10 if prior_high_income else 1.00))
    return min(alternatives) / 4


def corporate_regular_installments(current_tax: float, prior_tax: float | None, prior_eligible: bool, large: bool) -> list[float]:
    current = current_tax / 4
    if not prior_eligible:
        return [current] * 4
    assert prior_tax is not None and prior_tax > 0
    prior = prior_tax / 4
    if not large:
        return [min(current, prior)] * 4
    first = min(current, prior)
    second = current + max(0.0, current - first)
    return [first, second, current, current]


def choose_method(methods: list[dict]) -> dict:
    verified = [method for method in methods if method["status"] == "AVAILABLE_VERIFIED"]
    if verified:
        return min(verified, key=lambda method: method["amount"])
    provisional = [method for method in methods if method["status"] == "AVAILABLE_PROVISIONAL"]
    assert provisional, "no available method"
    return min(provisional, key=lambda method: method["amount"])


def payment_status(user_reported: bool, confirmation: bool, correct_application: bool) -> str:
    if correct_application:
        assert confirmation, "application cannot reconcile without confirmation evidence"
        return "PAYMENT_RECONCILED"
    if confirmation:
        return "PAYMENT_EVIDENCED"
    if user_reported:
        return "USER_REPORTED_PAYMENT"
    return "NO_PAYMENT_EVIDENCE"


def validate_authority_dependency(
    record: dict,
    as_of: str,
    rules: dict,
    *,
    require_current_run: bool = True,
    require_verified: bool = True,
) -> None:
    if require_verified:
        assert record["status"] == "VERIFIED", "used run authority must be VERIFIED"
    else:
        assert record["status"] in {"VERIFIED", "UNVERIFIED"}, "active run authority cannot be superseded"
    assert record["authority_ids"], "used run authority needs an authority ID"
    parsed = urlparse(record["source_url"])
    assert parsed.scheme == "https" and parsed.hostname, "authority URL must be HTTPS"
    assert parsed.hostname.lower().endswith(".gov"), "authority URL must resolve to an official .gov host"
    known_ids = {item["id"] for item in rules["_meta"]["authorities"]}
    if record["rule_origin"] == "BUNDLED_RULES":
        assert record["component"] == "federal", "bundled federal rule cannot support a state component"
        assert record["jurisdiction"] == "US-federal", "bundled federal rules require US-federal jurisdiction"
        assert len(record["authority_ids"]) == 1, "one bundled authority source is required per dependency record"
        assert set(record["authority_ids"]) <= known_ids, "federal authority ID missing from rules metadata"
        selected_authority = next(item for item in rules["_meta"]["authorities"] if item["id"] == record["authority_ids"][0])
        assert record["source_url"] == selected_authority["url"], "bundled source_url does not match authority metadata"
        coverage = rules["_meta"]["coverage"]
        exact_source_mappings = [
            entry for entry in coverage
            if entry["authority_ids"] == record["authority_ids"]
            and any(
                record["rule_path"] == path
                or record["rule_path"].startswith(path + ".")
                or record["rule_path"].startswith(path + "[")
                for path in entry["paths"]
            )
        ]
        assert exact_source_mappings, (
            "bundled rule path lacks an unambiguous one-authority coverage mapping; verify it as run-specific authority"
        )
        bundled_value = get_rule_path(rules, record["rule_path"])
        if require_verified:
            assert record["value_used"] == bundled_value, "bundled value_used differs from the referenced rule leaf"
    else:
        assert all(authority_id.startswith("run-") for authority_id in record["authority_ids"]), (
            "run-specific rules require run-scoped authority IDs"
        )
    checked = date.fromisoformat(record["checked_at"])
    run_date = date.fromisoformat(as_of[:10])
    assert checked == run_date if require_current_run else checked <= run_date, (
        "authority must be checked on the current run date" if require_current_run else "authority cannot be checked in the future"
    )
    rule_date = date.fromisoformat(record["rule_date"])
    if record["effective_start"] is not None:
        assert date.fromisoformat(record["effective_start"]) <= rule_date
    if record["effective_end"] is not None:
        assert rule_date <= date.fromisoformat(record["effective_end"])


def validate_consumed_fields(artifact: dict) -> None:
    blocking_field = False
    active_by_logical_id: dict[str, int] = {}
    fields_by_ref: dict[str, dict] = {}
    for input_record in artifact["inputs"]:
        assert input_record["fields_consumed"], "every input must identify fields consumed"
        if input_record["active_status"] == "ACTIVE":
            logical_id = input_record["logical_document_id"]
            active_by_logical_id[logical_id] = active_by_logical_id.get(logical_id, 0) + 1
            assert input_record["source_state"] not in {"SUPERSEDED", "CONTRADICTED"}
        for field in input_record["fields_consumed"]:
            fields_by_ref[f"{input_record['input_id']}#{field['field_id']}"] = field
            anchor = field["source_anchor"]
            assert anchor["page"] is not None or anchor["line_or_box"], "consumed field lacks source anchor"
            assert field["reviewer"], "consumed field lacks reviewer"
            assert field["reviewed_at"], "consumed field lacks review timestamp"
            if field["state"] in {"UNREADABLE", "NOT_PRESENT"}:
                blocking_field = True
            if field["state"] in {"OBSERVED_VALUE", "OBSERVED_ZERO", "DERIVED", "MANUAL_OVERRIDE"}:
                assert field["validation_status"] == "INDEPENDENTLY_VERIFIED"
            if field["state"] == "OBSERVED_ZERO":
                assert field["parser_value"] == 0, "OBSERVED_ZERO field is not zero"
            if field["state"] in {"NOT_PRESENT", "UNREADABLE", "NOT_APPLICABLE"}:
                assert field["parser_value"] is None, "absent/unreadable/not-applicable field retained a value"
    assert all(count == 1 for count in active_by_logical_id.values()), "logical document has multiple active versions"
    for input_record in artifact["inputs"]:
        metadata = input_record["document_metadata"]
        for key, ref in metadata["evidence_refs"].items():
            assert ref in fields_by_ref and ref.startswith(input_record["input_id"] + "#"), (
                "document metadata evidence does not resolve inside its input"
            )
            field = fields_by_ref[ref]
            assert field["state"] == "OBSERVED_VALUE" and field["validation_status"] == "INDEPENDENTLY_VERIFIED"
            assert field["parser_value"] == metadata[key], f"document metadata differs from reviewed field: {key}"
    inputs_by_id = {record["input_id"]: record for record in artifact["inputs"]}
    for current in artifact["inputs"]:
        predecessor_id = current["supersedes_input_id"]
        if predecessor_id is None:
            continue
        assert predecessor_id in inputs_by_id, "supersedes_input_id does not resolve inside the artifact"
        predecessor = inputs_by_id[predecessor_id]
        assert predecessor["logical_document_id"] == current["logical_document_id"]
        assert predecessor["document_version"] < current["document_version"]
        assert predecessor["source_sha256"] != current["source_sha256"]
        assert predecessor["active_status"] == predecessor["source_state"] == "SUPERSEDED"
    if blocking_field:
        assert artifact["status_axes"]["estimate"] == "ESTIMATE_HOLD"
        assert artifact["recommendation"]["status"] == "BLOCKED"


def component_usable(component: dict) -> bool:
    if component["authority_status"] not in {"VERIFIED_FOR_USED_RULES", "PARTIALLY_VERIFIED_UNUSED_GAPS"}:
        return False
    if not isinstance(component["amount"], (int, float)):
        return False
    if component["estimate_status"] == "PROVISIONAL":
        return component["evidence_status"] == "MATERIAL_PROJECTIONS" and component["method_status"] == "AVAILABLE_PROVISIONAL"
    if component["estimate_status"] in {"DRAFT_VERIFIED_INPUTS", "READY_FOR_PRACTITIONER_REVIEW"}:
        return component["evidence_status"] == "INPUTS_VERIFIED" and component["method_status"] == "AVAILABLE_VERIFIED"
    return False


def aggregate_components(federal: dict, states: list[dict]) -> str:
    components = [federal, *states]
    usable = [component for component in components if component_usable(component)]
    if len(usable) == len(components):
        return "COMPLETE_COMPONENT_RESULT"
    if usable:
        return "PARTIAL_COMPONENT_RESULT"
    return "ALL_COMPONENTS_HELD"


def recommendation_status(selected_method_status: str, dependent_inputs_verified: bool) -> str:
    if selected_method_status == "AVAILABLE_PROVISIONAL":
        return "PROVISIONAL"
    if selected_method_status == "AVAILABLE_VERIFIED" and dependent_inputs_verified:
        return "READY_FOR_PRACTITIONER_REVIEW"
    return "BLOCKED"


def close_gate(statement_coverage_complete: bool, unexplained_cash_difference: float, material_non_cash_open: bool) -> str:
    if not statement_coverage_complete or unexplained_cash_difference != 0 or material_non_cash_open:
        return "RECONCILIATION_HOLD"
    return "CLOSE_RECONCILED"


def variance_driver(evidence_supported: bool, proposed_driver: str) -> str:
    return proposed_driver if evidence_supported else "UNEXPLAINED"


def action_allowed(action: str) -> bool:
    assert action in {"portal_access", "schedule_debit", "transmit_payment", "file_return", "post_journal_entry"}
    return False


def allowed_payment_credit(payment_state: str, correct_tax_year: bool) -> float:
    return 100.0 if payment_state == "PAYMENT_RECONCILED" and correct_tax_year else 0.0


def validate_methods_and_lines(artifact: dict) -> None:
    inputs_by_id = {record["input_id"]: record for record in artifact["inputs"]}
    consumed_fields = {
        f"{input_record['input_id']}#{field['field_id']}": field
        for input_record in artifact["inputs"]
        if input_record["active_status"] == "ACTIVE"
        for field in input_record["fields_consumed"]
        if field["validation_status"] == "INDEPENDENTLY_VERIFIED"
    }
    consumed_refs = {
        f"{input_record['input_id']}#{field['field_id']}"
        for input_record in artifact["inputs"]
        if input_record["active_status"] == "ACTIVE"
        for field in input_record["fields_consumed"]
        if field["validation_status"] == "INDEPENDENTLY_VERIFIED"
    }
    consumed_values = {
        f"{input_record['input_id']}#{field['field_id']}": field["parser_value"]
        for input_record in artifact["inputs"]
        if input_record["active_status"] == "ACTIVE"
        for field in input_record["fields_consumed"]
        if field["validation_status"] == "INDEPENDENTLY_VERIFIED"
    }
    visiting: set[str] = set()
    validated: set[str] = set()
    line_direct_refs: dict[str, set[str]] = {}

    def validate_line(line_id: str) -> None:
        assert line_id in artifact["lines"], f"method references missing line: {line_id}"
        if line_id in validated:
            return
        assert line_id not in visiting, f"cyclic line provenance: {line_id}"
        visiting.add(line_id)
        line = artifact["lines"][line_id]
        assert line["state"] in {"OBSERVED_VALUE", "OBSERVED_ZERO"}, (
            "method-supporting lines must be independently reviewed observed/form-output fields"
        )
        assert isinstance(line["value"], (int, float)), f"method-supporting line is not numeric: {line_id}"
        assert line["source_refs"], f"method-supporting line lacks provenance: {line_id}"
        for source_ref in line["source_refs"]:
            if source_ref.startswith("line:"):
                validate_line(source_ref.removeprefix("line:"))
            else:
                assert source_ref in consumed_refs, f"line source does not resolve to an active verified field: {source_ref}"
        if line["state"] in {"OBSERVED_VALUE", "OBSERVED_ZERO"}:
            direct_refs = [source_ref for source_ref in line["source_refs"] if not source_ref.startswith("line:")]
            assert len(direct_refs) == 1, f"observed line must resolve to exactly one reviewed field: {line_id}"
            source_field = consumed_fields[direct_refs[0]]
            assert source_field["state"] == line["state"], f"observed line state differs from reviewed source field: {line_id}"
            assert line["value"] == consumed_values[direct_refs[0]], f"observed line differs from reviewed source field: {line_id}"
            line_direct_refs[line_id] = set(direct_refs)
        visiting.remove(line_id)
        validated.add(line_id)

    verified_dependencies = {
        record["dependency_id"]: record for record in artifact["authority_dependencies"] if record["status"] == "VERIFIED"
    }
    dependency_ids = set(verified_dependencies)
    assert len(dependency_ids) == len([record for record in artifact["authority_dependencies"] if record["status"] == "VERIFIED"]), (
        "duplicate verified authority dependency ID"
    )
    for method in artifact["methods"]:
        if method["status"] not in {"AVAILABLE_VERIFIED", "AVAILABLE_PROVISIONAL"}:
            continue
        for line_id in method["source_line_refs"]:
            validate_line(line_id)
        method_evidence_refs = set().union(*(line_direct_refs.get(line_id, set()) for line_id in method["source_line_refs"]))
        assert set(method["authority_dependency_refs"]) <= dependency_ids, "method cites missing or unverified authority"
        profile = method["calculation_profile"]
        eligibility = method["eligibility"]
        if profile == "STATE_SPECIFIC_VERIFIED_OUTPUT":
            assert method["component"] != "federal"
        else:
            assert method["component"] == "federal", "federal computation profile cannot support a state component"
        active_input_ids = {record["input_id"] for record in artifact["inputs"] if record["active_status"] == "ACTIVE"}
        assert eligibility["entity_type_evidence_ref"] in consumed_refs
        assert consumed_values[eligibility["entity_type_evidence_ref"]] == eligibility["entity_type"]
        assert eligibility["filing_status_evidence_ref"] in consumed_refs
        assert consumed_values[eligibility["filing_status_evidence_ref"]] == eligibility["filing_status"]
        assert eligibility["filer_category_evidence_ref"] in consumed_refs
        assert consumed_values[eligibility["filer_category_evidence_ref"]] == eligibility["filer_category"]
        method_evidence_refs.update({
            eligibility["entity_type_evidence_ref"],
            eligibility["filing_status_evidence_ref"],
            eligibility["filer_category_evidence_ref"],
        })
        needs_prior_return = method["annual_base_type"] == "PRIOR_YEAR_TAX" or profile == "CORPORATE_LARGE_REGULAR_RECAPTURE"
        if needs_prior_return:
            assert eligibility["prior_year_tax_year"] == artifact["tax_year"] - 1, "prior-year safe harbor uses wrong tax year"
            assert eligibility["prior_return_status"] in {"FILED", "TRANSCRIPT_VERIFIED"}, "prior-year safe harbor lacks filed-return evidence"
            assert eligibility["prior_year_full_12_months"] is True, "prior-year safe harbor cannot use a short-year return"
            assert eligibility["prior_return_input_ref"] in active_input_ids, "prior-return evidence input is not active"
            prior_input = inputs_by_id[eligibility["prior_return_input_ref"]]
            method_evidence_refs.update(prior_input["document_metadata"]["evidence_refs"].values())
            prior_metadata = prior_input["document_metadata"]
            assert prior_metadata["document_type"] in {"TAX_RETURN", "TAX_TRANSCRIPT"}
            assert prior_metadata["tax_year"] == eligibility["prior_year_tax_year"]
            expected_return_status = (
                "TRANSCRIPT_VERIFIED"
                if prior_metadata["document_type"] == "TAX_TRANSCRIPT"
                else "FILED"
            )
            assert eligibility["prior_return_status"] == expected_return_status
            assert prior_metadata["document_status"] in {"FILED_ORIGINAL", "FILED_AMENDED", "TRANSCRIPT_VERIFIED"}
            if prior_metadata["document_status"] == "FILED_AMENDED":
                filed_ref = prior_metadata["evidence_refs"].get("filed_or_effective_date")
                assert filed_ref in consumed_refs and prior_metadata.get("filed_or_effective_date"), (
                    "amended prior return lacks reviewed filing/effective date"
                )
                method_evidence_refs.add(filed_ref)
                if eligibility["entity_type"] == "C_CORPORATION":
                    assert date.fromisoformat(prior_metadata["filed_or_effective_date"]) <= date.fromisoformat(method["installment_cutoff_date"]), (
                        "amended prior return was filed after the applicable installment due date"
                    )
                else:
                    raise AssertionError(
                        "individual prior-year amended return requires separately verified original-due-date superseding-return treatment"
                    )
            period_days = (
                date.fromisoformat(prior_metadata["period_end"])
                - date.fromisoformat(prior_metadata["period_start"])
            ).days + 1
            assert period_days in {365, 366}, "prior-return metadata does not cover a full 12-month year"
            prior_evidence_line_ref = (
                method["prior_annual_base_line_ref"]
                if profile == "CORPORATE_LARGE_REGULAR_RECAPTURE"
                else method["annual_base_line_ref"]
            )
            assert prior_evidence_line_ref
            base_line = artifact["lines"][prior_evidence_line_ref]
            assert any(
                source_ref.startswith(eligibility["prior_return_input_ref"] + "#")
                for source_ref in base_line["source_refs"]
            ), "prior-year base line does not trace to the eligible filed return input"
            if eligibility["entity_type"] == "INDIVIDUAL":
                assert prior_evidence_line_ref == "form_2210_prior_year_tax_line_8", (
                    "individual prior-year method must use the Form 2210 line 8 prescribed computation"
                )
                direct_ref = next(ref for ref in base_line["source_refs"] if not ref.startswith("line:"))
                assert "Form 2210 line 8" in consumed_fields[direct_ref]["source_anchor"]["line_or_box"], (
                    "Form 2210 line 8 computation lacks an exact reviewed workpaper anchor"
                )
            if eligibility["entity_type"] == "C_CORPORATION":
                derived_positive = float(artifact["lines"][prior_evidence_line_ref]["value"]) > 0
                assert eligibility["prior_year_tax_positive"] is derived_positive, (
                    "corporate prior-year positive-tax gate is not derived from the reviewed prior-year tax line"
                )
                assert derived_positive, "corporate prior-year safe harbor requires positive tax"
            else:
                agi_line_ref = eligibility["prior_year_agi_line_ref"]
                threshold_dependency_id = eligibility["high_agi_threshold_authority_dependency_ref"]
                assert agi_line_ref and threshold_dependency_id in verified_dependencies
                validate_line(agi_line_ref)
                assert any(
                    source_ref.startswith(eligibility["prior_return_input_ref"] + "#")
                    for source_ref in artifact["lines"][agi_line_ref]["source_refs"]
                ), "prior-year AGI does not trace to the eligible prior-return input"
                threshold_dependency = verified_dependencies[threshold_dependency_id]
                expected_threshold_path = (
                    "safe_harbor_high_agi_threshold_mfs"
                    if eligibility["filing_status"] == "MFS"
                    else "safe_harbor_high_agi_threshold_non_mfs"
                )
                assert threshold_dependency["rule_path"] == expected_threshold_path
                assert threshold_dependency["component"] == method["component"]
                assert threshold_dependency_id in method["authority_dependency_refs"]
                high_income = float(artifact["lines"][agi_line_ref]["value"]) > float(threshold_dependency["value_used"])
                expected_percentage_path = (
                    "safe_harbor_prior_year_pct_high_agi" if high_income else "safe_harbor_prior_year_pct_low_agi"
                )
                assert verified_dependencies[method["annual_percentage_authority_dependency_ref"]]["rule_path"] == expected_percentage_path, (
                    "prior-year safe-harbor percentage does not match filing status and AGI"
                )
        else:
            assert eligibility["prior_return_status"] == "NOT_APPLICABLE"
            assert eligibility["prior_year_tax_year"] is None
            assert eligibility["prior_year_full_12_months"] is None
            assert eligibility["prior_return_input_ref"] is None
            assert eligibility["prior_year_agi_line_ref"] is None
            assert eligibility["high_agi_threshold_authority_dependency_ref"] is None
        if profile == "INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS":
            assert eligibility["entity_type"] == "INDIVIDUAL"
            assert eligibility["filer_category"] == "INDIVIDUAL"
            assert method["form_method_type"] == "NONE"
            assert eligibility["large_corporation"] is None
        elif profile == "CORPORATE_REGULAR_NON_LARGE_EQUAL_INSTALLMENTS":
            assert eligibility["entity_type"] == "C_CORPORATION"
            assert eligibility["filer_category"] == "TAXABLE_CORPORATION"
            assert eligibility["large_corporation"] is False
            assert method["form_method_type"] == "NONE"
        elif profile == "CORPORATE_LARGE_REGULAR_RECAPTURE":
            assert eligibility["entity_type"] == "C_CORPORATION"
            assert eligibility["filer_category"] == "TAXABLE_CORPORATION"
            assert eligibility["large_corporation"] is True
            assert method["form_method_type"] == "FORM_2220_LARGE_CORPORATION_REGULAR"
            assert eligibility["form_8842_status"] == "NOT_APPLICABLE"
        elif profile == "VERIFIED_FORM_OUTPUT":
            assert eligibility["form_output_input_ref"] in active_input_ids
            form_output_input = inputs_by_id[eligibility["form_output_input_ref"]]
            method_evidence_refs.update(form_output_input["document_metadata"]["evidence_refs"].values())
            form_metadata = form_output_input["document_metadata"]
            assert form_metadata["subject_id"] == artifact["scope"], "form-output subject does not match estimate scope"
            assert form_metadata["document_type"] == "FORM_OUTPUT_WORKPAPER", "form-output method lacks a form-output workpaper"
            assert form_metadata["document_status"] == "FINAL_SOURCE"
            assert form_metadata["tax_year"] == artifact["tax_year"], "form-output tax year does not match estimate"
            assert form_metadata["period_start"] == artifact["period"]["start"]
            assert form_metadata["period_end"] == artifact["period"]["end"], "form-output cumulative period does not match estimate"
            form_dependency_id = method["form_method_authority_dependency_ref"]
            assert form_dependency_id in verified_dependencies
            form_dependency = verified_dependencies[form_dependency_id]
            assert form_dependency["component"] == method["component"]
            assert form_dependency_id in method["authority_dependency_refs"]
            if eligibility["entity_type"] == "INDIVIDUAL":
                assert eligibility["filer_category"] == "INDIVIDUAL"
                assert method["form_method_type"] == "FORM_2210_ANNUALIZED"
                assert form_metadata["form_identity"] == "FORM_2210"
                assert form_dependency["rule_path"] == "run:form-2210-annualized-method"
                assert method["form_8842_deadline_authority_dependency_ref"] is None
            elif eligibility["entity_type"] in {"C_CORPORATION", "S_CORPORATION"}:
                if eligibility["entity_type"] == "S_CORPORATION":
                    assert eligibility["filer_category"] == "S_CORPORATION"
                else:
                    assert eligibility["filer_category"] in {"TAXABLE_CORPORATION", "TAX_EXEMPT_OR_PRIVATE_FOUNDATION"}
                assert form_metadata["form_identity"] == "FORM_2220"
                form_paths = {
                    "FORM_2220_ANNUALIZED_STANDARD": "run:form-2220-annualized-standard-method",
                    "FORM_2220_ANNUALIZED_OPTION_1": "run:form-2220-annualized-option-1-method",
                    "FORM_2220_ANNUALIZED_OPTION_2": "run:form-2220-annualized-option-2-method",
                    "FORM_2220_ADJUSTED_SEASONAL": "run:form-2220-adjusted-seasonal-method",
                }
                assert method["form_method_type"] in form_paths
                expected_form_path = form_paths[method["form_method_type"]]
                assert form_dependency["rule_path"] == expected_form_path
                election_option = {
                    "FORM_2220_ANNUALIZED_OPTION_1": "OPTION_1",
                    "FORM_2220_ANNUALIZED_OPTION_2": "OPTION_2",
                }.get(method["form_method_type"])
                if method["form_method_type"] == "FORM_2220_ANNUALIZED_OPTION_2":
                    assert eligibility["filer_category"] != "TAX_EXEMPT_OR_PRIVATE_FOUNDATION", (
                        "Form 2220 Option 2 is unavailable to tax-exempt organizations and private foundations"
                    )
                if election_option:
                    assert eligibility["form_8842_status"] == "FILED"
                    assert eligibility["form_8842_input_ref"] in consumed_refs
                    assert eligibility["form_8842_filed_date"]
                    assert consumed_values[eligibility["form_8842_input_ref"]] == eligibility["form_8842_filed_date"]
                    assert eligibility["form_8842_option"] == election_option
                    assert eligibility["form_8842_option_evidence_ref"] in consumed_refs
                    assert consumed_values[eligibility["form_8842_option_evidence_ref"]] == election_option
                    method_evidence_refs.update({
                        eligibility["form_8842_input_ref"],
                        eligibility["form_8842_option_evidence_ref"],
                    })
                    deadline_dependency_id = method["form_8842_deadline_authority_dependency_ref"]
                    assert deadline_dependency_id in verified_dependencies
                    deadline_dependency = verified_dependencies[deadline_dependency_id]
                    assert deadline_dependency["component"] == method["component"]
                    assert deadline_dependency["rule_origin"] == "RUN_SPECIFIC"
                    assert deadline_dependency["rule_path"] == "run:corporate-first-required-installment-due-date"
                    assert deadline_dependency_id in method["authority_dependency_refs"]
                    assert date.fromisoformat(eligibility["form_8842_filed_date"]) <= date.fromisoformat(deadline_dependency["value_used"])
                else:
                    assert eligibility["form_8842_status"] == "NOT_APPLICABLE"
                    assert eligibility["form_8842_input_ref"] is None
                    assert eligibility["form_8842_filed_date"] is None
                    expected_option = "STANDARD" if method["form_method_type"] == "FORM_2220_ANNUALIZED_STANDARD" else "NOT_APPLICABLE"
                    assert eligibility["form_8842_option"] == expected_option
                    assert eligibility["form_8842_option_evidence_ref"] is None
                    assert method["form_8842_deadline_authority_dependency_ref"] is None
            else:
                raise AssertionError("unsupported federal entity type for Form 2210/2220 output profile")
        elif profile == "STATE_SPECIFIC_VERIFIED_OUTPUT":
            requested_states = {component["jurisdiction"] for component in artifact["components"]["state"]}
            assert method["component"] in requested_states and method["component"] != "federal"
            assert method["form_method_type"] == "STATE_FORM_OUTPUT"
            assert eligibility["form_output_input_ref"] in active_input_ids
            state_output_input = inputs_by_id[eligibility["form_output_input_ref"]]
            method_evidence_refs.update(state_output_input["document_metadata"]["evidence_refs"].values())
            state_metadata = state_output_input["document_metadata"]
            assert state_metadata["subject_id"] == artifact["scope"]
            assert state_metadata["document_type"] == "FORM_OUTPUT_WORKPAPER"
            assert state_metadata["document_status"] == "FINAL_SOURCE"
            assert state_metadata["tax_year"] == artifact["tax_year"]
            assert state_metadata["period_start"] == artifact["period"]["start"]
            assert state_metadata["period_end"] == artifact["period"]["end"]
            assert state_metadata["form_identity"].startswith(f"STATE_FORM:{method['component']}:")
            form_dependency_id = method["form_method_authority_dependency_ref"]
            assert form_dependency_id in verified_dependencies
            form_dependency = verified_dependencies[form_dependency_id]
            assert form_dependency["component"] == method["component"]
            assert form_dependency["jurisdiction"] == method["component"]
            assert form_dependency["rule_origin"] == "RUN_SPECIFIC"
            assert form_dependency["rule_path"].startswith("run:state-form-method:")
            assert form_dependency_id in method["authority_dependency_refs"]
        else:
            assert eligibility["form_8842_input_ref"] is None
            assert eligibility["form_8842_filed_date"] is None
            assert eligibility["form_8842_option"] == "NOT_APPLICABLE"
            assert eligibility["form_8842_option_evidence_ref"] is None
        if eligibility["entity_type"] == "C_CORPORATION":
            test_line_refs = eligibility["large_corporation_test_line_refs"]
            threshold_dependency_id = eligibility["large_corporation_threshold_authority_dependency_ref"]
            assert threshold_dependency_id in verified_dependencies
            years_in_existence = eligibility["large_corporation_years_in_existence"]
            assert isinstance(years_in_existence, int) and len(test_line_refs) == min(3, years_in_existence), (
                "large-corporation test must cover each available preceding year, up to three"
            )
            large_gate_refs = {
                "large_corporation_years_in_existence_evidence_ref": years_in_existence,
                "large_corporation_modified_taxable_income_basis_evidence_ref": True,
                "large_corporation_predecessor_history_evidence_ref": True,
                "large_corporation_controlled_group_evidence_ref": eligibility["large_corporation_controlled_group_status"],
            }
            for ref_key, expected_value in large_gate_refs.items():
                evidence_ref = eligibility[ref_key]
                assert evidence_ref in consumed_refs and consumed_values[evidence_ref] == expected_value, (
                    "large-corporation modified-income, predecessor, existence, or controlled-group gate is not evidence-bound"
                )
                method_evidence_refs.add(evidence_ref)
            assert eligibility["large_corporation_modified_taxable_income_basis_confirmed"] is True, (
                "large-corporation test must use modified taxable income excluding NOL and capital carrybacks/carryovers"
            )
            assert eligibility["large_corporation_predecessor_history_complete"] is True
            assert eligibility["large_corporation_controlled_group_status"] in {"NOT_MEMBER", "ALLOCATED"}
            threshold_dependency = verified_dependencies[threshold_dependency_id]
            assert threshold_dependency["component"] == method["component"]
            assert threshold_dependency["rule_path"] == "run:large-corporation-definition-threshold"
            assert threshold_dependency_id in method["authority_dependency_refs"]
            if eligibility["large_corporation_controlled_group_status"] == "ALLOCATED":
                allocated_ref = eligibility["large_corporation_allocated_threshold_evidence_ref"]
                allocated_threshold = eligibility["large_corporation_allocated_threshold"]
                assert allocated_ref in consumed_refs and consumed_values[allocated_ref] == allocated_threshold
                method_evidence_refs.add(allocated_ref)
                assert allocated_threshold == threshold_dependency["value_used"], (
                    "controlled-group allocated threshold differs from the amount used"
                )
            else:
                assert eligibility["large_corporation_allocated_threshold"] is None
                assert eligibility["large_corporation_allocated_threshold_evidence_ref"] is None
            for line_id in test_line_refs:
                assert line_id.startswith("modified_taxable_income_excluding_nol_capital_carryovers_"), (
                    "large-corporation test line is not typed as modified taxable income"
                )
                validate_line(line_id)
                method_evidence_refs.update(line_direct_refs.get(line_id, set()))
            derived_large = any(
                float(artifact["lines"][line_id]["value"]) >= float(threshold_dependency["value_used"])
                for line_id in test_line_refs
            )
            assert eligibility["large_corporation"] is derived_large, "large-corporation classification is not derived from reviewed prior-year taxable income"
        else:
            assert eligibility["large_corporation_test_line_refs"] == []
            assert eligibility["large_corporation_threshold_authority_dependency_ref"] is None
            assert eligibility["large_corporation_years_in_existence"] is None
            assert eligibility["large_corporation_years_in_existence_evidence_ref"] is None
            assert eligibility["large_corporation_modified_taxable_income_basis_confirmed"] is None
            assert eligibility["large_corporation_modified_taxable_income_basis_evidence_ref"] is None
            assert eligibility["large_corporation_predecessor_history_complete"] is None
            assert eligibility["large_corporation_predecessor_history_evidence_ref"] is None
            assert eligibility["large_corporation_controlled_group_status"] == "NOT_APPLICABLE"
            assert eligibility["large_corporation_controlled_group_evidence_ref"] is None
            assert eligibility["large_corporation_allocated_threshold"] is None
            assert eligibility["large_corporation_allocated_threshold_evidence_ref"] is None
        if profile != "VERIFIED_FORM_OUTPUT":
            assert eligibility["form_8842_input_ref"] is None
            assert eligibility["form_8842_filed_date"] is None
            assert eligibility["form_8842_option"] == "NOT_APPLICABLE"
            assert eligibility["form_8842_option_evidence_ref"] is None
        if profile not in {"VERIFIED_FORM_OUTPUT", "STATE_SPECIFIC_VERIFIED_OUTPUT"}:
            assert eligibility["form_output_input_ref"] is None
            assert method["form_method_authority_dependency_ref"] is None
            assert method["form_8842_deadline_authority_dependency_ref"] is None

        due_dependency_id = method["due_date_authority_dependency_ref"]
        assert due_dependency_id in verified_dependencies
        due_dependency = verified_dependencies[due_dependency_id]
        assert due_dependency["component"] == method["component"]
        assert due_dependency["value_used"] == method["installment_cutoff_date"], "method due date differs from verified authority"
        assert due_dependency_id in method["authority_dependency_refs"]
        due_date = date.fromisoformat(method["installment_cutoff_date"])
        tax_period_start = date.fromisoformat(artifact["tax_period"]["start"])
        assert due_date >= tax_period_start, "installment due date precedes the tax period"
        if artifact["tax_period"]["type"] == "SHORT":
            assert profile in {"VERIFIED_FORM_OUTPUT", "STATE_SPECIFIC_VERIFIED_OUTPUT"}, (
                "short tax year requires verified target-period form output"
            )
            assert due_dependency["rule_origin"] == "RUN_SPECIFIC" and "short-tax-year" in due_dependency["rule_path"], (
                "short tax year requires run-specific short-year due-date authority"
            )
        elif artifact["tax_period"]["type"] == "FISCAL":
            assert due_dependency["rule_origin"] == "RUN_SPECIFIC" and "fiscal" in due_dependency["rule_path"], (
                "fiscal tax year requires run-specific fiscal due-date authority"
            )
        if profile == "INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS":
            if artifact["tax_period"]["type"] == "CALENDAR":
                assert due_dependency["rule_path"] == f"estimated_tax_due_dates[{artifact['period']['installment'] - 1}]"
            else:
                assert due_dependency["rule_origin"] == "RUN_SPECIFIC"
        elif profile in {"CORPORATE_REGULAR_NON_LARGE_EQUAL_INSTALLMENTS", "CORPORATE_LARGE_REGULAR_RECAPTURE", "VERIFIED_FORM_OUTPUT"} and eligibility["entity_type"] in {"C_CORPORATION", "S_CORPORATION"}:
            assert due_dependency["rule_origin"] == "RUN_SPECIFIC"
            assert due_dependency["rule_path"].startswith("run:corporate-"), "corporate Form 2220 method requires a corporate due-date rule"
        elif profile == "STATE_SPECIFIC_VERIFIED_OUTPUT":
            assert due_dependency["rule_origin"] == "RUN_SPECIFIC"
            assert due_dependency["component"] == method["component"]
            assert due_dependency["jurisdiction"] == method["component"]
            assert due_dependency["rule_path"].startswith("run:state-due-date:")
        if profile in {
            "INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS",
            "CORPORATE_REGULAR_NON_LARGE_EQUAL_INSTALLMENTS",
            "CORPORATE_LARGE_REGULAR_RECAPTURE",
        }:
            assert method["annual_base_line_ref"] and method["annual_percentage"] is not None
            percentage_dependency_id = method["annual_percentage_authority_dependency_ref"]
            assert percentage_dependency_id in verified_dependencies
            percentage_dependency = verified_dependencies[percentage_dependency_id]
            assert percentage_dependency["component"] == method["component"]
            assert method["annual_percentage"] == percentage_dependency["value_used"], (
                "annual percentage differs from its verified authority dependency"
            )
            if profile == "INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS":
                allowed_paths = {
                    "safe_harbor_prior_year_pct_low_agi": "PRIOR_YEAR_TAX",
                    "safe_harbor_prior_year_pct_high_agi": "PRIOR_YEAR_TAX",
                    "safe_harbor_current_year_pct": "CURRENT_YEAR_TAX",
                }
                assert percentage_dependency["rule_path"] in allowed_paths, "wrong rule path for individual regular profile"
                assert method["annual_base_type"] == allowed_paths[percentage_dependency["rule_path"]]
            elif profile == "CORPORATE_REGULAR_NON_LARGE_EQUAL_INSTALLMENTS":
                assert percentage_dependency["rule_path"].startswith("run:corporate-"), (
                    "corporate regular profile requires a named corporate percentage rule"
                )
                assert method["annual_base_type"] in {"PRIOR_YEAR_TAX", "CURRENT_YEAR_TAX"}
            else:
                assert percentage_dependency["rule_path"].startswith("run:corporate-current-year-")
                assert method["annual_base_type"] == "CURRENT_YEAR_TAX"
            assert method["required_annual_line_ref"] is None
            assert method["required_installment_line_ref"] is None
            assert method["cumulative_required_line_ref"] is None
            validate_line(method["annual_base_line_ref"])
            if method["annual_base_type"] == "CURRENT_YEAR_TAX" and method["status"] == "AVAILABLE_VERIFIED":
                for source_ref in line_direct_refs[method["annual_base_line_ref"]]:
                    source_metadata = inputs_by_id[source_ref.split("#", 1)[0]]["document_metadata"]
                    assert source_metadata["tax_year"] == artifact["tax_year"], (
                        "current-year tax operand comes from a different tax year"
                    )
                    assert date.fromisoformat(source_metadata["period_start"]) <= date.fromisoformat(artifact["period"]["start"])
                    assert date.fromisoformat(source_metadata["period_end"]) >= date.fromisoformat(artifact["period"]["end"]), (
                        "current-year tax operand does not cover the cumulative estimate period"
                    )
            annual = float(artifact["lines"][method["annual_base_line_ref"]]["value"]) * float(method["annual_percentage"])
            if profile == "CORPORATE_LARGE_REGULAR_RECAPTURE":
                prior_line_ref = method["prior_annual_base_line_ref"]
                assert prior_line_ref
                validate_line(prior_line_ref)
                installments = corporate_regular_installments(
                    annual,
                    float(artifact["lines"][prior_line_ref]["value"]),
                    True,
                    True,
                )
                installment = installments[int(artifact["period"]["installment"]) - 1]
                cumulative = sum(installments[: int(artifact["period"]["installment"])])
            else:
                assert method["prior_annual_base_line_ref"] is None
                installment = annual / 4
                cumulative = installment * int(artifact["period"]["installment"])
        else:
            assert method["annual_base_line_ref"] is None and method["prior_annual_base_line_ref"] is None and method["annual_percentage"] is None
            assert method["annual_percentage_authority_dependency_ref"] is None
            assert method["annual_base_type"] == "VERIFIED_FORM_OUTPUT"
            required_refs = (
                method["required_annual_line_ref"],
                method["required_installment_line_ref"],
                method["cumulative_required_line_ref"],
            )
            assert all(required_refs), "form/output profile requires annual, installment, and cumulative line refs"
            for line_id in required_refs:
                validate_line(line_id)
                assert any(
                    source_ref.startswith(eligibility["form_output_input_ref"] + "#")
                    for source_ref in artifact["lines"][line_id]["source_refs"]
                ), "form-output method line does not trace to its reviewed form input"
            annual, installment, cumulative = (
                float(artifact["lines"][line_id]["value"]) for line_id in required_refs
            )
        assert isclose(float(method["required_annual_payment"]), annual), "required annual payment is not derived from profile lines"
        assert isclose(float(method["required_installment"]), installment), "required installment is not derived from profile"
        assert isclose(float(method["cumulative_required_through_installment"]), cumulative), (
            "cumulative installment is not derived from profile"
        )
        withholding_ref = method["withholding_credit_line_ref"]
        payment_ref = method["prior_payment_line_ref"]
        withholding_method = method["withholding_timing_method"]
        if withholding_method == "NONE":
            assert withholding_ref is None and method["withholding_and_refundable_credits_applied"] == 0
        elif withholding_method == "RATABLE_WITHHOLDING":
            assert withholding_ref
            validate_line(withholding_ref)
            ratable = float(artifact["lines"][withholding_ref]["value"]) * int(artifact["period"]["installment"]) / 4
            assert isclose(float(method["withholding_and_refundable_credits_applied"]), ratable), (
                "ratable withholding credit is not limited to the cumulative installment fraction"
            )
        else:
            assert withholding_method == "ACTUAL_WITHHOLDING_DATES" and withholding_ref
            assert method["withholding_election_evidence_ref"] in consumed_refs, (
                "actual-date withholding election/substantiation does not resolve to active reviewed evidence"
            )
            method_evidence_refs.add(method["withholding_election_evidence_ref"])
            validate_line(withholding_ref)
            for record in artifact["withholding_records"]:
                for key, ref in record["evidence_refs"].items():
                    assert ref in consumed_refs, "withholding record evidence ref does not resolve"
                    assert consumed_values[ref] == record[key], f"withholding record differs from reviewed evidence: {key}"
                    method_evidence_refs.add(ref)
            actual_withholding = sum(
                float(record["amount"])
                for record in artifact["withholding_records"]
                if record["target_tax_year"] == artifact["tax_year"]
                and record["taxpayer_id_match"] and record["form_match"] and record["correct_tax_year"]
                and date.fromisoformat(record["withholding_date"]) <= date.fromisoformat(method["installment_cutoff_date"])
            )
            assert method["withholding_and_refundable_credits_applied"] == actual_withholding, (
                "actual-date withholding credit differs from eligible dated records"
            )
            assert artifact["lines"][withholding_ref]["value"] == actual_withholding
        credited_payment_records = [
            record for record in artifact["payment_records"]
            if record["status"] == "PAYMENT_RECONCILED"
            and all(record[key] for key in ("taxpayer_id_match", "form_match", "period_match", "amount_match", "correct_tax_year"))
            and record["target_tax_year"] == artifact["tax_year"]
            and record["target_installment"] <= artifact["period"]["installment"]
            and date.fromisoformat(record["payment_date"]) <= date.fromisoformat(artifact["as_of"][:10])
            and date.fromisoformat(record["settlement_date"]) <= date.fromisoformat(artifact["as_of"][:10])
            and date.fromisoformat(record["application_date"]) <= date.fromisoformat(artifact["as_of"][:10])
            and date.fromisoformat(record["application_date"]) <= date.fromisoformat(method["installment_cutoff_date"])
        ]
        reconciled_total = sum(float(record["amount"]) for record in credited_payment_records)
        if reconciled_total > 0:
            assert payment_ref, "eligible reconciled payment records were omitted from the method"
            validate_line(payment_ref)
            assert artifact["lines"][payment_ref]["value"] == reconciled_total, (
                "prior-payment line does not equal all eligible reconciled payment records"
            )
            assert method["prior_installment_payments_applied"] == reconciled_total, (
                "method did not apply all eligible reconciled prior payments"
            )
            method_evidence_refs.update(
                ref for record in credited_payment_records for ref in record["evidence_refs"].values()
            )
            assert artifact["status_axes"]["payment"] == "PAYMENT_RECONCILED"
        else:
            assert payment_ref is None and method["prior_installment_payments_applied"] == 0, (
                "method claims prior-payment credit without eligible reconciled records"
            )
        expected = max(
            0.0,
            float(method["cumulative_required_through_installment"])
            - float(method["withholding_and_refundable_credits_applied"])
            - float(method["prior_installment_payments_applied"]),
        )
        assert isclose(float(method["amount_due"]), expected), "method amount_due does not recompute"
        required_installment = float(method["required_installment"])
        cumulative_required = float(method["cumulative_required_through_installment"])
        assert 0 <= required_installment <= cumulative_required <= float(method["required_annual_payment"])
        if artifact["period"]["installment"] == 1:
            assert isclose(required_installment, cumulative_required), "first installment must equal cumulative requirement"
        withholding_credits = float(method["withholding_and_refundable_credits_applied"])
        payment_credits = float(method["prior_installment_payments_applied"])
        assert (withholding_credits == 0) == (withholding_method == "NONE")
        assert (payment_credits == 0) == (method["payment_application_method"] == "NONE")
        operand_line_refs = {
            method[key]
            for key in (
                "annual_base_line_ref", "prior_annual_base_line_ref", "required_annual_line_ref",
                "required_installment_line_ref", "cumulative_required_line_ref",
                "withholding_credit_line_ref", "prior_payment_line_ref",
            )
            if method[key] is not None
        }
        assert operand_line_refs <= set(method["source_line_refs"]), "method operand line missing from source_line_refs"
        method_evidence_refs.update(
            set().union(*(line_direct_refs.get(line_id, set()) for line_id in operand_line_refs))
        )
        if method["status"] == "AVAILABLE_VERIFIED":
            for ref in method_evidence_refs:
                input_id = ref.split("#", 1)[0]
                assert input_id in inputs_by_id, "method evidence ref does not resolve to an artifact input"
                assert inputs_by_id[input_id]["source_state"] == "FINAL", (
                    "verified method depends on projected, user-provided, legacy, or superseded input"
                )
                assert inputs_by_id[input_id]["document_metadata"]["subject_id"] == artifact["scope"], (
                    "verified method evidence belongs to a different taxpayer or entity"
                )
                assert inputs_by_id[input_id]["document_metadata"]["document_status"] not in {"DRAFT", "PROJECTED"}

    recommendation = artifact["recommendation"]
    if recommendation["status"] in {"PROVISIONAL", "READY_FOR_PRACTITIONER_REVIEW"}:
        matches = [
            method for method in artifact["methods"]
            if method["name"] == recommendation["method"] and method["component"] == recommendation["component"]
        ]
        assert len(matches) == 1, "recommendation does not resolve to one method record"
        selected = matches[0]
        expected_status = "AVAILABLE_VERIFIED" if recommendation["status"] == "READY_FOR_PRACTITIONER_REVIEW" else "AVAILABLE_PROVISIONAL"
        assert selected["status"] == expected_status
        assert recommendation["amount"] == selected["amount_due"], "recommendation amount differs from method"
        assert recommendation["due_date"] == selected["installment_cutoff_date"], "recommendation due date differs from verified method cutoff"
        component_methods = [method for method in artifact["methods"] if method["component"] == recommendation["component"]]
        verified_choices = [method for method in component_methods if method["status"] == "AVAILABLE_VERIFIED"]
        candidate_pool = verified_choices or [method for method in component_methods if method["status"] == "AVAILABLE_PROVISIONAL"]
        assert candidate_pool and selected is min(candidate_pool, key=lambda item: item["amount_due"]), (
            "recommendation did not select the lowest available method at the highest evidence tier"
        )


def canonical_evidence_key(artifact: dict, ref: object) -> tuple:
    if not isinstance(ref, str) or "#" not in ref:
        return ("unresolved", ref)
    input_id, field_id = ref.split("#", 1)
    for input_record in artifact["inputs"]:
        if input_record["input_id"] != input_id:
            continue
        for field in input_record["fields_consumed"]:
            if field["field_id"] == field_id:
                anchor = field["source_anchor"]
                return (
                    input_record["source_sha256"],
                    anchor["page"],
                    anchor["line_or_box"],
                )
    return ("unresolved", ref)


def validate_payment_axis(artifact: dict) -> None:
    status = artifact["status_axes"]["payment"]
    records = artifact["payment_records"]
    record_ids = [record["record_id"] for record in records]
    assert len(record_ids) == len(set(record_ids)), "duplicate payment record_id"
    evidenced_records = [record for record in records if record["status"] != "USER_REPORTED_PAYMENT"]
    transaction_evidence = [
        tuple(
            canonical_evidence_key(artifact, record["evidence_refs"][key])
            for key in (
                "confirmation_amount", "bank_settlement_amount", "payment_date",
                "settlement_date", "application_date", "confirmation", "bank_settlement",
            )
        )
        for record in evidenced_records
    ]
    assert len(transaction_evidence) == len(set(transaction_evidence)), "duplicate payment transaction evidence"
    input_by_id = {record["input_id"]: record for record in artifact["inputs"]}
    consumed_values = {
        f"{input_record['input_id']}#{field['field_id']}": field["parser_value"]
        for input_record in artifact["inputs"]
        if input_record["active_status"] == "ACTIVE"
        for field in input_record["fields_consumed"]
        if field["validation_status"] == "INDEPENDENTLY_VERIFIED"
    }
    field_map = {
        "amount": "amount",
        "payment_date": "payment_date",
        "settlement_date": "settlement_date",
        "application_date": "application_date",
        "target_tax_year": "target_tax_year",
        "target_installment": "target_installment",
        "taxpayer_id_match": "taxpayer_id_match",
        "form_match": "form_match",
        "period_match": "period_match",
        "correct_tax_year": "correct_tax_year",
    }
    for record in records:
        if record["status"] == "USER_REPORTED_PAYMENT":
            continue
        for ref in record["evidence_refs"].values():
            assert isinstance(ref, str) and "#" in ref, "payment evidence ref is missing or malformed"
            evidence_input_id = ref.split("#", 1)[0]
            assert evidence_input_id in input_by_id, "payment evidence ref does not resolve to an artifact input"
            assert input_by_id[evidence_input_id]["document_metadata"]["subject_id"] == artifact["scope"], (
                "payment evidence belongs to a different taxpayer or entity"
            )
        for evidence_key, record_key in field_map.items():
            ref = record["evidence_refs"][evidence_key]
            assert ref in consumed_values, f"payment evidence ref does not resolve: {evidence_key}"
            assert consumed_values[ref] == record[record_key], f"payment record differs from reviewed evidence: {evidence_key}"
        for evidence_key, record_key in (("confirmation", "confirmation_ref"), ("bank_settlement", "bank_settlement_ref")):
            ref = record["evidence_refs"][evidence_key]
            assert ref in consumed_values and record[record_key] == ref, f"payment evidence ref does not resolve: {evidence_key}"
            assert consumed_values[ref], f"payment {evidence_key} evidence is empty"
        confirmation_amount_ref = record["evidence_refs"]["confirmation_amount"]
        bank_amount_ref = record["evidence_refs"]["bank_settlement_amount"]
        assert confirmation_amount_ref in consumed_values and bank_amount_ref in consumed_values, (
            "payment amount evidence does not resolve"
        )
        derived_amount_match = (
            consumed_values[confirmation_amount_ref]
            == consumed_values[bank_amount_ref]
            == record["amount"]
        )
        assert record["amount_match"] is derived_amount_match, "payment amount_match is not derived from both amount sources"
        if record["status"] == "PAYMENT_RECONCILED":
            assert all(input_by_id[ref.split("#", 1)[0]]["source_state"] == "FINAL" for ref in record["evidence_refs"].values())
            assert record["target_tax_year"] == artifact["tax_year"]
            assert record["amount_match"] is True and record["correct_tax_year"] is True
            as_of_date = date.fromisoformat(artifact["as_of"][:10])
            assert all(
                date.fromisoformat(record[key]) <= as_of_date
                for key in ("payment_date", "settlement_date", "application_date")
            ), "PAYMENT_RECONCILED record contains a future payment, settlement, or application date"
    if status == "NO_PAYMENT_EVIDENCE":
        assert not records
    elif status == "USER_REPORTED_PAYMENT":
        assert any(record["status"] == status for record in records)
    elif status == "PAYMENT_EVIDENCED":
        assert any(record["status"] in {"PAYMENT_EVIDENCED", "PAYMENT_RECONCILED"} and record["confirmation_ref"] for record in records)
    else:
        assert any(
            record["status"] == "PAYMENT_RECONCILED"
            and record["confirmation_ref"]
            and record["bank_settlement_ref"]
            and all(record[key] for key in ("taxpayer_id_match", "form_match", "period_match", "amount_match", "correct_tax_year"))
            for record in records
        )


def validate_withholding_record_uniqueness(artifact: dict) -> None:
    records = artifact["withholding_records"]
    record_ids = [record["record_id"] for record in records]
    assert len(record_ids) == len(set(record_ids)), "duplicate withholding record_id"
    transaction_evidence = [
        tuple(
            canonical_evidence_key(artifact, record["evidence_refs"][key])
            for key in ("amount", "withholding_date", "target_tax_year")
        )
        for record in records
    ]
    assert len(transaction_evidence) == len(set(transaction_evidence)), "duplicate withholding transaction evidence"


def schema_errors(artifact: dict, schema: dict) -> list:
    return list(Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(artifact))


TAX_PERIOD_EVIDENCE_FIELDS = {
    "type": "tax_period_type",
    "convention": "tax_period_convention",
    "start": "tax_period_start",
    "end": "tax_period_end",
    "week_ending_method": "tax_period_week_ending_method",
    "elected_ending_month": "tax_period_elected_ending_month",
    "elected_ending_weekday": "tax_period_elected_ending_weekday",
    "basis_status": "tax_period_basis_status",
    "books_basis_status": "tax_period_books_basis_status",
}


def make_tax_period_evidence_input(artifact: dict, basis_status: str, input_id: str = "verified-tax-period-v1") -> dict:
    tax_period = artifact["tax_period"]
    reviewed_at = "2026-08-25T11:45:00Z"

    def field(field_id: str, value, anchor: str) -> dict:
        return {
            "field_id": field_id,
            "parser_value": value,
            "state": "NOT_APPLICABLE" if value is None else "OBSERVED_VALUE",
            "source_anchor": {"page": 1, "line_or_box": anchor},
            "reviewer": "independent-reviewer",
            "reviewed_at": reviewed_at,
            "validation_status": "INDEPENDENTLY_VERIFIED",
        }

    metadata_values = {
        "document_subject_id": artifact["scope"],
        "document_type": "ACCOUNTING_PERIOD_EVIDENCE",
        "document_tax_year": artifact["tax_year"],
        "document_period_start": tax_period["start"],
        "document_period_end": tax_period["end"],
        "document_status": "FINAL_SOURCE",
        "filed_or_effective_date": tax_period["start"],
    }
    fields = [
        field(field_id, value, f"reviewed tax-period evidence: {field_id}")
        for field_id, value in metadata_values.items()
    ]
    period_values = {**{key: tax_period[key] for key in TAX_PERIOD_EVIDENCE_FIELDS if key != "basis_status"}, "basis_status": basis_status}
    fields.extend(
        field(TAX_PERIOD_EVIDENCE_FIELDS[key], value, f"reviewed adoption/election/change evidence: {key}")
        for key, value in period_values.items()
    )
    return {
        "input_id": input_id,
        "logical_document_id": "verified-tax-period-evidence",
        "document_version": 1,
        "active_status": "ACTIVE",
        "supersedes_input_id": None,
        "source_path": "source/accounting-period-evidence.pdf",
        "source_sha256": "d" * 64,
        "source_state": "FINAL",
        "document_metadata": {
            "subject_id": artifact["scope"],
            "document_type": "ACCOUNTING_PERIOD_EVIDENCE",
            "tax_year": artifact["tax_year"],
            "period_start": tax_period["start"],
            "period_end": tax_period["end"],
            "document_status": "FINAL_SOURCE",
            "filed_or_effective_date": tax_period["start"],
            "evidence_refs": {
                "subject_id": f"{input_id}#document_subject_id",
                "document_type": f"{input_id}#document_type",
                "tax_year": f"{input_id}#document_tax_year",
                "period_start": f"{input_id}#document_period_start",
                "period_end": f"{input_id}#document_period_end",
                "document_status": f"{input_id}#document_status",
                "filed_or_effective_date": f"{input_id}#filed_or_effective_date",
            },
        },
        "parser_name": "manual-source-review",
        "parser_version": "1",
        "parser_contract_status": "MANUAL_SOURCE",
        "validation_report": "evidence/verified-tax-period-evidence.validation.json",
        "fields_consumed": fields,
    }


def attach_tax_period_evidence(
    artifact: dict,
    basis_status: str,
    input_id: str = "verified-tax-period-v1",
    books_basis_status: str | None = None,
) -> None:
    artifact["tax_period"]["basis_status"] = basis_status
    if books_basis_status is None:
        books_basis_status = (
            "VERIFIED_REGULAR_52_53_BOOKS"
            if artifact["tax_period"]["convention"] == "WEEK_52_53"
            else "NOT_APPLICABLE"
        )
    artifact["tax_period"]["books_basis_status"] = books_basis_status
    artifact["tax_period"]["evidence_refs"] = {
        key: f"{input_id}#{field_id}" for key, field_id in TAX_PERIOD_EVIDENCE_FIELDS.items()
    }
    evidence_input = make_tax_period_evidence_input(artifact, basis_status, input_id)
    for index, input_record in enumerate(artifact["inputs"]):
        if input_record["input_id"] == input_id:
            artifact["inputs"][index] = evidence_input
            break
    else:
        artifact["inputs"].append(evidence_input)


def validate_tax_period_evidence(artifact: dict) -> None:
    tax_period = artifact["tax_period"]
    assert set(tax_period["evidence_refs"]) == set(TAX_PERIOD_EVIDENCE_FIELDS), "tax-period evidence map is incomplete"
    active_inputs = {
        record["input_id"]: record for record in artifact["inputs"] if record["active_status"] == "ACTIVE"
    }
    fields_by_ref = {
        f"{input_record['input_id']}#{field['field_id']}": (input_record, field)
        for input_record in artifact["inputs"]
        if input_record["active_status"] == "ACTIVE"
        for field in input_record["fields_consumed"]
    }
    resolved_inputs = set()
    for key, ref in tax_period["evidence_refs"].items():
        assert ref in fields_by_ref, f"tax-period evidence ref does not resolve: {key}"
        input_record, field = fields_by_ref[ref]
        resolved_inputs.add(input_record["input_id"])
        assert field["parser_value"] == tax_period[key], f"tax-period evidence differs from artifact: {key}"
        assert field["validation_status"] == "INDEPENDENTLY_VERIFIED", f"tax-period evidence is not independently verified: {key}"
        expected_state = "NOT_APPLICABLE" if tax_period[key] is None else "OBSERVED_VALUE"
        assert field["state"] == expected_state, (
            f"tax-period evidence must be directly observed, not derived or manually overridden: {key}"
        )
    verified_result = artifact["status"] in {"PROVISIONAL", "DRAFT_VERIFIED_INPUTS", "READY_FOR_PRACTITIONER_REVIEW"}
    if not verified_result:
        return
    assert tax_period["basis_status"] != "UNVERIFIED", "usable result lacks verified tax-period adoption/change evidence"
    allowed_basis = {
        "CALENDAR": {"VERIFIED_DEFAULT_CALENDAR", "VERIFIED_EXISTING_PERIOD", "VERIFIED_APPROVED_CHANGE"},
        "FISCAL": {"VERIFIED_EXISTING_PERIOD", "VERIFIED_ORIGINAL_ADOPTION", "VERIFIED_APPROVED_CHANGE"},
        "SHORT": {"VERIFIED_SHORT_PERIOD_CAUSE", "VERIFIED_APPROVED_CHANGE"},
    }[tax_period["type"]]
    assert tax_period["basis_status"] in allowed_basis, "tax-period basis status is incompatible with period type"
    if tax_period["convention"] == "WEEK_52_53":
        assert tax_period["books_basis_status"] == "VERIFIED_REGULAR_52_53_BOOKS", (
            "52/53-week period lacks verified evidence that the books regularly compute income on the elected basis"
        )
    else:
        assert tax_period["books_basis_status"] == "NOT_APPLICABLE", (
            "non-52/53-week period cannot carry a 52/53-week books-basis status"
        )
    for input_id in resolved_inputs:
        input_record = active_inputs[input_id]
        metadata = input_record["document_metadata"]
        assert input_record["source_state"] == "FINAL", "usable result depends on non-final tax-period evidence"
        assert metadata["subject_id"] == artifact["scope"], "tax-period evidence belongs to a different subject"
        assert metadata["document_type"] == "ACCOUNTING_PERIOD_EVIDENCE", (
            "tax-period basis must trace to underlying accounting-period evidence, not a derivative workpaper"
        )
        assert metadata["document_status"] not in {"DRAFT", "PROJECTED"}, "usable result depends on draft tax-period evidence"
        assert metadata["tax_year"] == artifact["tax_year"]
        assert metadata["period_start"] == tax_period["start"] and metadata["period_end"] == tax_period["end"]
    prior_returns = [
        record for record in artifact["inputs"]
        if record["active_status"] == "ACTIVE"
        and record["source_state"] == "FINAL"
        and record["document_metadata"]["subject_id"] == artifact["scope"]
        and record["document_metadata"]["document_type"] == "TAX_RETURN"
        and record["document_metadata"]["period_end"] is not None
        and date.fromisoformat(record["document_metadata"]["period_end"]) < date.fromisoformat(tax_period["start"])
    ]
    if tax_period["type"] == "FISCAL" and prior_returns:
        latest = max(prior_returns, key=lambda record: record["document_metadata"]["period_end"])
        metadata = latest["document_metadata"]
        prior_start = date.fromisoformat(metadata["period_start"])
        prior_end = date.fromisoformat(metadata["period_end"])
        prior_was_calendar = prior_start == date(prior_start.year, 1, 1) and prior_end == date(prior_start.year, 12, 31)
        if prior_was_calendar:
            assert tax_period["basis_status"] == "VERIFIED_APPROVED_CHANGE", (
                "fiscal period following a filed calendar-year return requires verified approved-change evidence"
            )


def make_valid_artifact(template: dict) -> dict:
    artifact = deepcopy(template)
    artifact.update({
        "run_id": "EST-2026-08-25-001",
        "scope": "individual/test-taxpayer",
        "tax_year": 2026,
        "tax_period": {
            "type": "CALENDAR",
            "convention": "CALENDAR",
            "start": "2026-01-01",
            "end": "2026-12-31",
            "week_ending_method": "NOT_APPLICABLE",
            "elected_ending_month": None,
            "elected_ending_weekday": None,
        },
        "period": {"start": "2026-01-01", "end": "2026-03-31", "installment": 1},
        "as_of": "2026-08-25T12:00:00Z",
        "status": "READY_FOR_PRACTITIONER_REVIEW",
        "aggregate_component_result": "COMPLETE_COMPONENT_RESULT",
    })
    artifact["status_axes"].update({
        "authority": "VERIFIED_FOR_USED_RULES",
        "evidence": "INPUTS_VERIFIED",
        "estimate": "READY_FOR_PRACTITIONER_REVIEW",
    })
    artifact["components"]["federal"].update({
        "authority_status": "VERIFIED_FOR_USED_RULES",
        "evidence_status": "INPUTS_VERIFIED",
        "estimate_status": "READY_FOR_PRACTITIONER_REVIEW",
        "method_status": "AVAILABLE_VERIFIED",
        "amount": 2500.0,
        "blockers": [],
    })
    artifact["authority_dependencies"] = [{
        "dependency_id": "dep-prior-year-safe-harbor",
        "component": "federal",
        "rule_origin": "BUNDLED_RULES",
        "rule_path": "safe_harbor_prior_year_pct_low_agi",
        "jurisdiction": "US-federal",
        "rule_date": "2026-04-15",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["pub-505-2026"],
        "source_url": "https://www.irs.gov/publications/p505",
        "value_used": 1.0,
        "status": "VERIFIED",
        "checked_at": "2026-08-25",
    }, {
        "dependency_id": "dep-prior-year-high-agi-threshold",
        "component": "federal",
        "rule_origin": "BUNDLED_RULES",
        "rule_path": "safe_harbor_high_agi_threshold_non_mfs",
        "jurisdiction": "US-federal",
        "rule_date": "2026-01-01",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["pub-505-2026"],
        "source_url": "https://www.irs.gov/publications/p505",
        "value_used": 150000,
        "status": "VERIFIED",
        "checked_at": "2026-08-25",
    }, {
        "dependency_id": "dep-individual-q1-due-date",
        "component": "federal",
        "rule_origin": "BUNDLED_RULES",
        "rule_path": "estimated_tax_due_dates[0]",
        "jurisdiction": "US-federal",
        "rule_date": "2026-01-01",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["pub-505-2026"],
        "source_url": "https://www.irs.gov/publications/p505",
        "value_used": "2026-04-15",
        "status": "VERIFIED",
        "checked_at": "2026-08-25",
    }]
    artifact["inputs"] = [{
        "input_id": "verified-tax-inputs-v1",
        "logical_document_id": "verified-tax-inputs-2026",
        "document_version": 1,
        "active_status": "ACTIVE",
        "supersedes_input_id": None,
        "source_path": "evidence/verified-tax-inputs-2026.json",
        "source_sha256": "a" * 64,
        "source_state": "FINAL",
        "document_metadata": {
            "subject_id": "individual/test-taxpayer",
            "document_type": "TAX_RETURN",
            "tax_year": 2025,
            "period_start": "2025-01-01",
            "period_end": "2025-12-31",
            "document_status": "FILED_ORIGINAL",
            "evidence_refs": {
                "subject_id": "verified-tax-inputs-v1#document_subject_id",
                "document_type": "verified-tax-inputs-v1#document_type",
                "tax_year": "verified-tax-inputs-v1#document_tax_year",
                "period_start": "verified-tax-inputs-v1#document_period_start",
                "period_end": "verified-tax-inputs-v1#document_period_end",
                "document_status": "verified-tax-inputs-v1#document_status",
            },
        },
        "parser_name": "manual-source-review",
        "parser_version": "1",
        "parser_contract_status": "MANUAL_SOURCE",
        "validation_report": "evidence/w2-2026-employer-a.validation.json",
        "fields_consumed": [
            {
                "field_id": "prior_form_2210_line_8_tax",
                "parser_value": 10000,
                "state": "OBSERVED_VALUE",
                "source_anchor": {"page": 2, "line_or_box": "Form 2210 line 8 prior-year tax workpaper (prescribed additions and subtractions)"},
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-08-25T11:30:00Z",
                "validation_status": "INDEPENDENTLY_VERIFIED",
            },
            {
                "field_id": "current_credits_applied",
                "parser_value": 0,
                "state": "OBSERVED_ZERO",
                "source_anchor": {"page": 1, "line_or_box": "verified payment ledger total"},
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-08-25T11:30:00Z",
                "validation_status": "INDEPENDENTLY_VERIFIED",
            },
            {
                "field_id": "prior_year_agi",
                "parser_value": 100000,
                "state": "OBSERVED_VALUE",
                "source_anchor": {"page": 1, "line_or_box": "prior Form 1040 line 11"},
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-08-25T11:30:00Z",
                "validation_status": "INDEPENDENTLY_VERIFIED",
            },
            {"field_id": "entity_type", "parser_value": "INDIVIDUAL", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "Form 1040 taxpayer type"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "filing_status", "parser_value": "SINGLE", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "filing status"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "filer_category", "parser_value": "INDIVIDUAL", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "return filer category"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_subject_id", "parser_value": "individual/test-taxpayer", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "privacy-safe taxpayer identity match"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_type", "parser_value": "TAX_RETURN", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "Form 1040"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_tax_year", "parser_value": 2025, "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "tax year"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_period_start", "parser_value": "2025-01-01", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "period start"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_period_end", "parser_value": "2025-12-31", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "period end"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
            {"field_id": "document_status", "parser_value": "FILED_ORIGINAL", "state": "OBSERVED_VALUE", "source_anchor": {"page": 1, "line_or_box": "filing status"}, "reviewer": "independent-reviewer", "reviewed_at": "2026-08-25T11:30:00Z", "validation_status": "INDEPENDENTLY_VERIFIED"},
        ],
    }]
    artifact["lines"]["form_2210_prior_year_tax_line_8"] = {
        "value": 10000.0,
        "state": "OBSERVED_VALUE",
        "source_refs": ["verified-tax-inputs-v1#prior_form_2210_line_8_tax"],
        "formula": None,
    }
    artifact["lines"]["payments_and_refundable_credits"].update({
        "value": 0.0,
        "state": "OBSERVED_ZERO",
        "source_refs": ["verified-tax-inputs-v1#current_credits_applied"],
        "formula": None,
    })
    artifact["lines"]["prior_year_agi"] = {
        "value": 100000.0,
        "state": "OBSERVED_VALUE",
        "source_refs": ["verified-tax-inputs-v1#prior_year_agi"],
        "formula": None,
    }
    artifact["methods"] = [{
        "name": "prior-year safe harbor",
        "component": "federal",
        "status": "AVAILABLE_VERIFIED",
        "calculation_profile": "INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS",
        "form_method_type": "NONE",
        "form_method_authority_dependency_ref": None,
        "form_8842_deadline_authority_dependency_ref": None,
        "eligibility": {
            "entity_type": "INDIVIDUAL",
            "entity_type_evidence_ref": "verified-tax-inputs-v1#entity_type",
            "filing_status": "SINGLE",
            "filing_status_evidence_ref": "verified-tax-inputs-v1#filing_status",
            "filer_category": "INDIVIDUAL",
            "filer_category_evidence_ref": "verified-tax-inputs-v1#filer_category",
            "prior_year_tax_year": 2025,
            "prior_return_status": "FILED",
            "prior_year_full_12_months": True,
            "prior_year_tax_positive": None,
            "prior_return_input_ref": "verified-tax-inputs-v1",
            "prior_year_agi_line_ref": "prior_year_agi",
            "high_agi_threshold_authority_dependency_ref": "dep-prior-year-high-agi-threshold",
            "large_corporation": None,
            "large_corporation_test_line_refs": [],
            "large_corporation_threshold_authority_dependency_ref": None,
            "large_corporation_years_in_existence": None,
            "large_corporation_years_in_existence_evidence_ref": None,
            "large_corporation_modified_taxable_income_basis_confirmed": None,
            "large_corporation_modified_taxable_income_basis_evidence_ref": None,
            "large_corporation_predecessor_history_complete": None,
            "large_corporation_predecessor_history_evidence_ref": None,
            "large_corporation_controlled_group_status": "NOT_APPLICABLE",
            "large_corporation_controlled_group_evidence_ref": None,
            "large_corporation_allocated_threshold": None,
            "large_corporation_allocated_threshold_evidence_ref": None,
            "form_output_input_ref": None,
            "form_8842_status": "NOT_APPLICABLE",
            "form_8842_input_ref": None,
            "form_8842_filed_date": None,
            "form_8842_option": "NOT_APPLICABLE",
            "form_8842_option_evidence_ref": None,
        },
        "annual_base_type": "PRIOR_YEAR_TAX",
        "annual_base_line_ref": "form_2210_prior_year_tax_line_8",
        "prior_annual_base_line_ref": None,
        "annual_percentage": 1.0,
        "annual_percentage_authority_dependency_ref": "dep-prior-year-safe-harbor",
        "required_annual_line_ref": None,
        "required_installment_line_ref": None,
        "cumulative_required_line_ref": None,
        "withholding_credit_line_ref": None,
        "withholding_election_evidence_ref": None,
        "prior_payment_line_ref": None,
        "installment_cutoff_date": "2026-04-15",
        "due_date_authority_dependency_ref": "dep-individual-q1-due-date",
        "required_annual_payment": 10000.0,
        "required_installment": 2500.0,
        "cumulative_required_through_installment": 2500.0,
        "withholding_and_refundable_credits_applied": 0.0,
        "prior_installment_payments_applied": 0.0,
        "withholding_timing_method": "NONE",
        "payment_application_method": "NONE",
        "amount_due": 2500.0,
        "formula": "max(0, cumulative_required_through_installment - withholding_and_refundable_credits_applied - prior_installment_payments_applied)",
        "source_line_refs": ["form_2210_prior_year_tax_line_8", "payments_and_refundable_credits", "prior_year_agi"],
        "authority_dependency_refs": ["dep-prior-year-safe-harbor", "dep-prior-year-high-agi-threshold", "dep-individual-q1-due-date"],
        "blockers": [],
    }]
    artifact["recommendation"] = {
        "component": "federal",
        "method": "prior-year safe harbor",
        "amount": 2500.0,
        "due_date": "2026-04-15",
        "status": "READY_FOR_PRACTITIONER_REVIEW",
    }
    attach_tax_period_evidence(artifact, "VERIFIED_DEFAULT_CALENDAR")
    return artifact


def validate_artifact_invariants(artifact: dict, schema: dict, rules: dict, predecessor: dict | None = None) -> None:
    errors = schema_errors(artifact, schema)
    assert not errors, errors[0].message if errors else ""
    assert artifact["tax_year"] == rules["tax_year"] == rules["_meta"]["tax_year"], (
        "artifact tax year does not match the loaded rules file"
    )
    tax_period_start = date.fromisoformat(artifact["tax_period"]["start"])
    tax_period_end = date.fromisoformat(artifact["tax_period"]["end"])
    assert tax_period_start <= tax_period_end, "artifact tax period is reversed"
    assert tax_period_start.year == artifact["tax_year"], "tax_year must identify the year in which the tax period begins"
    tax_period_days = (tax_period_end - tax_period_start).days + 1
    week_ending_method = artifact["tax_period"]["week_ending_method"]
    elected_ending_month = artifact["tax_period"]["elected_ending_month"]
    elected_ending_weekday = artifact["tax_period"]["elected_ending_weekday"]
    if artifact["tax_period"]["type"] == "CALENDAR":
        assert artifact["tax_period"]["convention"] == "CALENDAR"
        assert tax_period_start == date(artifact["tax_year"], 1, 1)
        assert tax_period_end == date(artifact["tax_year"], 12, 31)
        assert week_ending_method == "NOT_APPLICABLE" and elected_ending_month is None and elected_ending_weekday is None, (
            "non-52/53-week period cannot carry a 52/53-week election"
        )
    elif artifact["tax_period"]["type"] == "FISCAL":
        convention = artifact["tax_period"]["convention"]
        assert convention in {"MONTHLY", "WEEK_52_53"}
        if convention == "MONTHLY":
            next_anniversary = date(tax_period_start.year + 1, tax_period_start.month, 1)
            assert tax_period_start.month != 1 and tax_period_start.day == 1 and tax_period_end == next_anniversary - timedelta(days=1), (
                "invalid monthly fiscal tax period"
            )
            assert week_ending_method == "NOT_APPLICABLE" and elected_ending_month is None and elected_ending_weekday is None, (
                "non-52/53-week period cannot carry a 52/53-week election"
            )
        else:
            assert tax_period_days in {364, 371}, "52/53-week fiscal period must contain exactly 52 or 53 weeks"
            assert (tax_period_end.weekday() + 1) % 7 == tax_period_start.weekday(), (
                "52/53-week fiscal period must end on the weekday immediately preceding its start weekday"
            )
            assert week_ending_method in {"NEAREST_MONTH_END", "LAST_WEEKDAY_IN_MONTH"}, (
                "52/53-week fiscal period requires an elected ending method"
            )
            assert elected_ending_month is not None and elected_ending_weekday is not None, (
                "52/53-week fiscal period requires an elected ending month and weekday"
            )
            weekday_index = {
                "MONDAY": 0,
                "TUESDAY": 1,
                "WEDNESDAY": 2,
                "THURSDAY": 3,
                "FRIDAY": 4,
                "SATURDAY": 5,
                "SUNDAY": 6,
            }[elected_ending_weekday]
            assert tax_period_end.weekday() == weekday_index, "52/53-week fiscal period ends on the wrong elected weekday"
            def elected_year_end(reference_year: int) -> date:
                month_end = date(reference_year, elected_ending_month, calendar.monthrange(reference_year, elected_ending_month)[1])
                last_elected_weekday = month_end - timedelta(days=(month_end.weekday() - weekday_index) % 7)
                if week_ending_method == "LAST_WEEKDAY_IN_MONTH":
                    return last_elected_weekday
                next_elected_weekday = last_elected_weekday + timedelta(days=7)
                distance_before = abs((month_end - last_elected_weekday).days)
                distance_after = abs((next_elected_weekday - month_end).days)
                return last_elected_weekday if distance_before <= distance_after else next_elected_weekday

            matching_reference_years = [
                reference_year
                for reference_year in range(tax_period_end.year - 1, tax_period_end.year + 2)
                if elected_year_end(reference_year) == tax_period_end
            ]
            assert matching_reference_years, "tax-period end does not satisfy the elected 52/53-week month-end rule"
            expected_starts = {elected_year_end(reference_year - 1) + timedelta(days=1) for reference_year in matching_reference_years}
            assert tax_period_start in expected_starts, (
                "52/53-week fiscal period must begin the day after the preceding elected year-end"
            )
    else:
        assert artifact["tax_period"]["convention"] == "SHORT"
        assert tax_period_days < 365, "SHORT tax period must be shorter than a full year"
        assert week_ending_method == "NOT_APPLICABLE" and elected_ending_month is None and elected_ending_weekday is None, (
            "non-52/53-week period cannot carry a 52/53-week election"
        )
    period_start = date.fromisoformat(artifact["period"]["start"])
    period_end = date.fromisoformat(artifact["period"]["end"])
    assert tax_period_start <= period_start <= period_end <= tax_period_end, "installment period falls outside tax period"
    states = artifact["components"]["state"]
    components = [artifact["components"]["federal"], *states]
    derived_aggregate = aggregate_components(artifact["components"]["federal"], states)
    assert artifact["aggregate_component_result"] == derived_aggregate, "aggregate component status is stale"
    expected_authority_axis = (
        "AUTHORITY_HOLD" if any(component["authority_status"] == "AUTHORITY_HOLD" for component in components)
        else "PARTIALLY_VERIFIED_UNUSED_GAPS" if any(component["authority_status"] == "PARTIALLY_VERIFIED_UNUSED_GAPS" for component in components)
        else "VERIFIED_FOR_USED_RULES"
    )
    assert artifact["status_axes"]["authority"] == expected_authority_axis, "top authority axis is not worst-component status"
    evidence_rank = {"INPUTS_VERIFIED": 0, "MATERIAL_PROJECTIONS": 1, "INPUTS_INCOMPLETE": 2}
    expected_evidence_axis = max((component["evidence_status"] for component in components), key=evidence_rank.get)
    assert artifact["status_axes"]["evidence"] == expected_evidence_axis, "top evidence axis is not worst-component status"
    usable = [component for component in components if component_usable(component)]
    usable_names = ({"federal"} if component_usable(artifact["components"]["federal"]) else set()) | {
        component["jurisdiction"] for component in states if component_usable(component)
    }
    as_of = artifact["as_of"]
    for record in artifact["authority_dependencies"]:
        assert date.fromisoformat(record["rule_date"]).year == artifact["tax_year"], (
            "authority rule_date does not match artifact tax year"
        )
        validate_authority_dependency(record, as_of, rules, require_verified=record["component"] in usable_names)
    validate_consumed_fields(artifact)
    validate_tax_period_evidence(artifact)
    run_timestamp = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    for input_record in artifact["inputs"]:
        for field in input_record["fields_consumed"]:
            reviewed = datetime.fromisoformat(field["reviewed_at"].replace("Z", "+00:00"))
            assert reviewed <= run_timestamp, "field review timestamp is after artifact as_of"
    for record in artifact["payment_records"]:
        reviewed = datetime.fromisoformat(record["reviewed_at"].replace("Z", "+00:00"))
        assert reviewed <= run_timestamp, "payment review timestamp is after artifact as_of"
    for record in artifact["withholding_records"]:
        reviewed = datetime.fromisoformat(record["reviewed_at"].replace("Z", "+00:00"))
        assert reviewed <= run_timestamp, "withholding review timestamp is after artifact as_of"
    validate_withholding_record_uniqueness(artifact)
    validate_payment_axis(artifact)
    validate_methods_and_lines(artifact)
    for component_name in usable_names:
        component = artifact["components"]["federal"] if component_name == "federal" else next(
            item for item in states if item["jurisdiction"] == component_name
        )
        matching_methods = [
            method for method in artifact["methods"]
            if method["component"] == component_name
            and method["status"] == component["method_status"]
            and method["amount_due"] == component["amount"]
        ]
        assert matching_methods, "usable component amount is not bound to an available method"
    for component_name in usable_names:
        assert any(record["component"] == component_name for record in artifact["authority_dependencies"]), (
            f"usable component lacks authority dependencies: {component_name}"
        )
    if artifact["recommendation"]["status"] == "BLOCKED":
        assert artifact["recommendation"]["component"] is None
        assert artifact["recommendation"]["method"] is None and artifact["recommendation"]["amount"] is None
    if artifact["recommendation"]["status"] in {"PROVISIONAL", "READY_FOR_PRACTITIONER_REVIEW"}:
        component_name = artifact["recommendation"]["component"]
        selected = artifact["components"]["federal"] if component_name == "federal" else next(
            (component for component in states if component["jurisdiction"] == component_name),
            None,
        )
        assert selected is not None and component_usable(selected), "recommendation does not identify a usable component"
        assert isinstance(artifact["recommendation"]["amount"], (int, float))
        assert artifact["recommendation"]["amount"] == selected["amount"], "recommendation amount differs from component"
        if artifact["recommendation"]["status"] == "READY_FOR_PRACTITIONER_REVIEW":
            assert artifact["status"] == artifact["status_axes"]["estimate"] == "READY_FOR_PRACTITIONER_REVIEW"
            assert selected["estimate_status"] == "READY_FOR_PRACTITIONER_REVIEW"
            assert selected["method_status"] == "AVAILABLE_VERIFIED"
            assert selected["evidence_status"] == "INPUTS_VERIFIED"
        else:
            assert artifact["status"] == artifact["status_axes"]["estimate"] == "PROVISIONAL"
            assert selected["estimate_status"] == "PROVISIONAL"
            assert selected["method_status"] == "AVAILABLE_PROVISIONAL"
            assert selected["evidence_status"] == "MATERIAL_PROJECTIONS"
    assert artifact["payment_execution_authorized"] is False
    if artifact["status"] == "SUPERSEDED":
        assert artifact["superseded_by_run_id"], "superseded run lacks successor"
    else:
        assert artifact["superseded_by_run_id"] is None, "active run cannot point to a successor"
    if artifact["supersedes_run_id"] is not None:
        assert predecessor is not None, "superseding run requires its predecessor artifact"
        validate_artifact_invariants(predecessor, schema, rules)
        assert predecessor["run_id"] == artifact["supersedes_run_id"]
        assert predecessor["status"] == "SUPERSEDED"
        assert predecessor["superseded_by_run_id"] == artifact["run_id"]
        predecessor_inputs = {record["input_id"]: record for record in predecessor["inputs"]}
        linked = [record for record in artifact["inputs"] if record["supersedes_input_id"] in predecessor_inputs]
        assert linked, "superseding run does not link a preserved predecessor input"
        embedded_inputs = {record["input_id"]: record for record in artifact["inputs"]}
        for current in linked:
            predecessor_input = predecessor_inputs[current["supersedes_input_id"]]
            embedded_predecessor = embedded_inputs[current["supersedes_input_id"]]
            immutable_keys = {
                "input_id", "logical_document_id", "document_version", "supersedes_input_id",
                "source_path", "source_sha256", "document_metadata", "parser_name", "parser_version",
                "parser_contract_status", "validation_report", "fields_consumed",
            }
            assert {key: embedded_predecessor[key] for key in immutable_keys} == {
                key: predecessor_input[key] for key in immutable_keys
            }, "embedded predecessor input does not preserve predecessor provenance"
    else:
        assert predecessor is None, "predecessor supplied to a run with no supersedes_run_id"


def supersede_input(prior: dict, corrected: dict) -> tuple[dict, dict]:
    old, new = deepcopy(prior), deepcopy(corrected)
    assert old["logical_document_id"] == new["logical_document_id"]
    assert new["document_version"] > old["document_version"]
    assert new["supersedes_input_id"] == old["input_id"]
    old["active_status"] = "SUPERSEDED"
    old["source_state"] = "SUPERSEDED"
    new["active_status"] = "ACTIVE"
    return old, new


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, help="validate an instantiated estimate artifact in addition to release fixtures")
    parser.add_argument("--predecessor-artifact", type=Path, help="required reciprocal predecessor when --artifact supersedes a run")
    args = parser.parse_args()
    router = read("SKILL.md")
    authority = read("authority.md")
    orchestrator = read("close-estimate.md")
    estimate = read("estimate.md")
    quarterly = read("quarterly.md")
    parsing = read("parsing.md")
    reconciliation = read("reconciliation.md")
    variance = read("variance.md")
    control = read("templates/close-estimate-control.md.template")
    presentation = read("templates/quarterly-estimate.md.template")
    payment = read("templates/quarterly-payment.md.template")
    evals = read("evals/close-estimate.md")
    canonical = json.loads(read("templates/estimate.template.json"))
    estimate_schema = json.loads(read("templates/estimate.schema.json"))

    for needle in ("authority.md", "close-estimate.md", "point-of-use"):
        assert needle in router
    normalized_authority = " ".join(authority.lower().split())
    for needle in ("authority_hold", "point-of-use", "raw `_verify`", "not substitute zero"):
        assert needle in normalized_authority
    for needle in ("READINESS", "PAYMENT_RECONCILIATION", "AVAILABLE_PROVISIONAL", "payment_execution_authorized"):
        assert needle in orchestrator
    assert "do **not** reduce AGI" in estimate
    assert "ordinary-income component + preferential-income component" in estimate
    assert "Current-year corporate tax uses 100%" in quarterly
    assert "3 / 3 / 6 / 9" in quarterly and "Timely Form 8842" in quarterly
    assert "S corporation" in quarterly and "built-in-gains tax" in quarterly
    assert "LEGACY_UNVERIFIED" in parsing and "OBSERVED_ZERO" in parsing
    assert "regardless of income-tax" in reconciliation and "Input-manifest hash" in reconciliation
    assert "UNEXPLAINED" in variance and "equal or explicitly normalized" in variance
    assert "does not authorize or evidence a payment" in presentation
    assert "Create this record only after" in payment
    assert canonical["payment_execution_authorized"] is False
    assert canonical["lines"]["gross_income"]["value"] is None
    assert canonical["lines"]["form_1040_line_14_total_deductions"]["formula"] == (
        "form_1040_line_12 + qbi_line_13a + schedule_1a_line_13b"
    )
    assert canonical["lines"]["taxable_income"]["formula"] == (
        "max(0, agi - form_1040_line_14_total_deductions)"
    )
    rules = json.loads(read("rules/federal-2026.json"))
    valid_artifact = make_valid_artifact(canonical)
    validate_artifact_invariants(valid_artifact, estimate_schema, rules)
    derived_tax_period_evidence = deepcopy(valid_artifact)
    period_input = next(record for record in derived_tax_period_evidence["inputs"] if record["input_id"] == "verified-tax-period-v1")
    period_field_ids = set(TAX_PERIOD_EVIDENCE_FIELDS.values())
    for field in period_input["fields_consumed"]:
        if field["field_id"] in period_field_ids and field["parser_value"] is not None:
            field["state"] = "DERIVED"
    try:
        validate_artifact_invariants(derived_tax_period_evidence, estimate_schema, rules)
        raise AssertionError("READY artifact accepted derived tax-period evidence")
    except AssertionError as exc:
        assert "must be directly observed" in str(exc)

    wrong_year = deepcopy(valid_artifact)
    wrong_year["tax_year"] = 2025
    wrong_year["period"] = {"start": "2025-01-01", "end": "2025-03-31", "installment": 1}
    assert load_rules_for_artifact(wrong_year)["tax_year"] == 2025
    try:
        validate_artifact_invariants(wrong_year, estimate_schema, rules)
        raise AssertionError("artifact passed against the wrong rules year")
    except AssertionError as exc:
        assert "rules file" in str(exc)
    wrong_value = deepcopy(valid_artifact)
    wrong_value["authority_dependencies"][0]["value_used"] = 0.5
    try:
        validate_artifact_invariants(wrong_value, estimate_schema, rules)
        raise AssertionError("wrong bundled value_used passed")
    except AssertionError as exc:
        assert "value_used differs" in str(exc)
    wrong_path = deepcopy(valid_artifact)
    wrong_path["authority_dependencies"][0]["rule_path"] = "safe_harbor_prior_year_pct_low_agi.nonexistent"
    try:
        validate_artifact_invariants(wrong_path, estimate_schema, rules)
        raise AssertionError("nonexistent bundled descendant path passed")
    except AssertionError as exc:
        assert "does not exist" in str(exc)
    wrong_source = deepcopy(valid_artifact)
    wrong_source["authority_dependencies"][0]["source_url"] = "https://www.ecfr.gov/current/title-26"
    try:
        validate_artifact_invariants(wrong_source, estimate_schema, rules)
        raise AssertionError("unrelated official URL passed for bundled authority ID")
    except AssertionError as exc:
        assert "does not match authority metadata" in str(exc)

    invalid_status_artifact = deepcopy(valid_artifact)
    invalid_status_artifact["status_axes"]["authority"] = "LOOKS_FINE"
    assert schema_errors(invalid_status_artifact, estimate_schema), (
        "invalid status-axis value passed canonical schema"
    )
    invalid_recommendation = deepcopy(valid_artifact)
    invalid_recommendation["recommendation"]["status"] = "PAID"
    assert schema_errors(invalid_recommendation, estimate_schema), (
        "invalid recommendation status passed canonical schema"
    )
    invalid_ready_evidence = deepcopy(valid_artifact)
    invalid_ready_evidence["components"]["federal"]["evidence_status"] = "INPUTS_INCOMPLETE"
    assert schema_errors(invalid_ready_evidence, estimate_schema), "ready component accepted incomplete inputs"
    invalid_ready_method = deepcopy(valid_artifact)
    invalid_ready_method["components"]["federal"]["method_status"] = "AVAILABLE_PROVISIONAL"
    assert schema_errors(invalid_ready_method, estimate_schema), "ready component accepted provisional method"
    invalid_top_axis = deepcopy(valid_artifact)
    invalid_top_axis["status_axes"]["estimate"] = "ESTIMATE_HOLD"
    assert schema_errors(invalid_top_axis, estimate_schema), "ready top-level status accepted held estimate axis"
    invalid_ready_recommendation = deepcopy(valid_artifact)
    invalid_ready_recommendation["recommendation"]["amount"] = None
    assert schema_errors(invalid_ready_recommendation, estimate_schema), "ready recommendation accepted null amount"
    invalid_date = deepcopy(valid_artifact)
    invalid_date["inputs"][0]["fields_consumed"][0]["reviewed_at"] = "not-a-date"
    assert schema_errors(invalid_date, estimate_schema), "invalid review timestamp passed format validation"
    future_review = deepcopy(valid_artifact)
    future_review["inputs"][0]["fields_consumed"][0]["reviewed_at"] = "2026-08-26T11:30:00Z"
    try:
        validate_artifact_invariants(future_review, estimate_schema, rules)
        raise AssertionError("future field review timestamp passed")
    except AssertionError as exc:
        assert "after artifact as_of" in str(exc)
    invalid_payment_axis = deepcopy(valid_artifact)
    invalid_payment_axis["status_axes"]["payment"] = "PAYMENT_RECONCILED"
    assert schema_errors(invalid_payment_axis, estimate_schema), "reconciled payment status passed without evidence record"
    invalid_line = deepcopy(valid_artifact)
    invalid_line["lines"]["form_2210_prior_year_tax_line_8"].update({"state": "UNREADABLE", "value": 10000.0})
    assert schema_errors(invalid_line, estimate_schema), "unreadable output line retained a numeric value"
    arbitrary_recommendation = deepcopy(valid_artifact)
    arbitrary_recommendation["recommendation"]["method"] = "invented method"
    try:
        validate_artifact_invariants(arbitrary_recommendation, estimate_schema, rules)
        raise AssertionError("recommendation not bound to a method record passed")
    except AssertionError as exc:
        assert "resolve to one method" in str(exc)
    inflated_q1 = deepcopy(valid_artifact)
    inflated_q1["methods"][0].update({
        "required_installment": 10000.0,
        "cumulative_required_through_installment": 10000.0,
        "amount_due": 10000.0,
    })
    inflated_q1["components"]["federal"]["amount"] = 10000.0
    inflated_q1["recommendation"]["amount"] = 10000.0
    try:
        validate_artifact_invariants(inflated_q1, estimate_schema, rules)
        raise AssertionError("Q1 accepted the full annual requirement as its installment")
    except AssertionError as exc:
        assert "required installment is not derived" in str(exc)
    unbound_percentage = deepcopy(valid_artifact)
    unbound_percentage["methods"][0].update({
        "annual_percentage": 0.5,
        "required_annual_payment": 5000.0,
        "required_installment": 1250.0,
        "cumulative_required_through_installment": 1250.0,
        "amount_due": 1250.0,
    })
    unbound_percentage["components"]["federal"]["amount"] = 1250.0
    unbound_percentage["recommendation"]["amount"] = 1250.0
    try:
        validate_artifact_invariants(unbound_percentage, estimate_schema, rules)
        raise AssertionError("self-declared annual percentage passed")
    except AssertionError as exc:
        assert "differs from its verified authority" in str(exc)
    mismatched_observed_line = deepcopy(valid_artifact)
    mismatched_observed_line["lines"]["form_2210_prior_year_tax_line_8"]["value"] = 999999.0
    try:
        validate_artifact_invariants(mismatched_observed_line, estimate_schema, rules)
        raise AssertionError("observed line differed from reviewed source field")
    except AssertionError as exc:
        assert "differs from reviewed source" in str(exc)
    draft_prior_return = deepcopy(valid_artifact)
    draft_prior_return["methods"][0]["eligibility"]["prior_return_status"] = "DRAFT"
    try:
        validate_artifact_invariants(draft_prior_return, estimate_schema, rules)
        raise AssertionError("draft prior return qualified for safe harbor")
    except AssertionError as exc:
        assert "filed-return evidence" in str(exc)
    short_year_prior_return = deepcopy(valid_artifact)
    short_year_prior_return["methods"][0]["eligibility"]["prior_year_full_12_months"] = False
    try:
        validate_artifact_invariants(short_year_prior_return, estimate_schema, rules)
        raise AssertionError("short-year prior return qualified for safe harbor")
    except AssertionError as exc:
        assert "short-year" in str(exc)
    high_agi_uses_low_percentage = deepcopy(valid_artifact)
    for field in high_agi_uses_low_percentage["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "prior_year_agi":
            field["parser_value"] = 200000
    high_agi_uses_low_percentage["lines"]["prior_year_agi"]["value"] = 200000.0
    try:
        validate_artifact_invariants(high_agi_uses_low_percentage, estimate_schema, rules)
        raise AssertionError("high-AGI taxpayer retained the low-AGI prior-year percentage")
    except AssertionError as exc:
        assert "filing status and AGI" in str(exc)
    wrong_due_date = deepcopy(valid_artifact)
    wrong_due_date["methods"][0]["installment_cutoff_date"] = "2026-12-31"
    wrong_due_date["recommendation"]["due_date"] = "2026-12-31"
    try:
        validate_artifact_invariants(wrong_due_date, estimate_schema, rules)
        raise AssertionError("arbitrary recommendation due date passed")
    except AssertionError as exc:
        assert "differs from verified authority" in str(exc)
    excessive_ratable_withholding = deepcopy(valid_artifact)
    excessive_ratable_withholding["inputs"][0]["fields_consumed"].append({
        **excessive_ratable_withholding["inputs"][0]["fields_consumed"][0],
        "field_id": "annual_withholding",
        "parser_value": 12000,
    })
    excessive_ratable_withholding["lines"]["annual_withholding"] = {
        "value": 12000.0,
        "state": "OBSERVED_VALUE",
        "source_refs": ["verified-tax-inputs-v1#annual_withholding"],
        "formula": None,
    }
    excessive_ratable_withholding["methods"][0].update({
        "withholding_credit_line_ref": "annual_withholding",
        "withholding_timing_method": "RATABLE_WITHHOLDING",
        "withholding_and_refundable_credits_applied": 12000.0,
        "amount_due": 0.0,
        "source_line_refs": ["form_2210_prior_year_tax_line_8", "annual_withholding"],
    })
    excessive_ratable_withholding["components"]["federal"]["amount"] = 0.0
    excessive_ratable_withholding["recommendation"]["amount"] = 0.0
    try:
        validate_artifact_invariants(excessive_ratable_withholding, estimate_schema, rules)
        raise AssertionError("Q1 accepted full-year withholding under ratable treatment")
    except AssertionError as exc:
        assert "cumulative installment fraction" in str(exc)
    late_actual_withholding = deepcopy(excessive_ratable_withholding)
    late_actual_withholding["inputs"][0]["fields_consumed"].append({
        **late_actual_withholding["inputs"][0]["fields_consumed"][0],
        "field_id": "actual_withholding_election",
        "parser_value": "documented",
    })
    late_actual_withholding["inputs"][0]["fields_consumed"].extend([
        {**late_actual_withholding["inputs"][0]["fields_consumed"][0], "field_id": "wh_record_amount", "parser_value": 12000},
        {**late_actual_withholding["inputs"][0]["fields_consumed"][0], "field_id": "wh_record_date", "parser_value": "2026-12-01"},
        {**late_actual_withholding["inputs"][0]["fields_consumed"][0], "field_id": "wh_record_tax_year", "parser_value": 2026},
        {**late_actual_withholding["inputs"][0]["fields_consumed"][0], "field_id": "wh_record_taxpayer_match", "parser_value": True},
        {**late_actual_withholding["inputs"][0]["fields_consumed"][0], "field_id": "wh_record_form_match", "parser_value": True},
    ])
    late_actual_withholding["methods"][0].update({
        "withholding_timing_method": "ACTUAL_WITHHOLDING_DATES",
        "withholding_election_evidence_ref": "verified-tax-inputs-v1#actual_withholding_election",
    })
    late_actual_withholding["withholding_records"] = [{
        "record_id": "wh-december",
        "amount": 12000.0,
        "withholding_date": "2026-12-01",
        "target_tax_year": 2026,
        "evidence_refs": {
            "amount": "verified-tax-inputs-v1#wh_record_amount",
            "withholding_date": "verified-tax-inputs-v1#wh_record_date",
            "target_tax_year": "verified-tax-inputs-v1#wh_record_tax_year",
            "taxpayer_id_match": "verified-tax-inputs-v1#wh_record_taxpayer_match",
            "form_match": "verified-tax-inputs-v1#wh_record_form_match",
        },
        "taxpayer_id_match": True,
        "form_match": True,
        "correct_tax_year": True,
        "reviewer": "independent-reviewer",
        "reviewed_at": "2026-08-25T11:30:00Z",
    }]
    negative_withholding_record = deepcopy(late_actual_withholding)
    negative_withholding_record["withholding_records"][0]["amount"] = -1.0
    assert schema_errors(negative_withholding_record, estimate_schema), "negative withholding record passed schema"
    try:
        validate_artifact_invariants(late_actual_withholding, estimate_schema, rules)
        raise AssertionError("December withholding was credited to Q1 under actual-date treatment")
    except AssertionError as exc:
        assert "eligible dated records" in str(exc)
    unresolved_withholding_election = deepcopy(late_actual_withholding)
    unresolved_withholding_election["methods"][0]["withholding_election_evidence_ref"] = "made-up"
    try:
        validate_artifact_invariants(unresolved_withholding_election, estimate_schema, rules)
        raise AssertionError("unresolved actual-withholding election evidence passed")
    except AssertionError as exc:
        assert "does not resolve" in str(exc)
    dangling_withholding_record = deepcopy(late_actual_withholding)
    dangling_withholding_record["withholding_records"][0]["evidence_refs"]["amount"] = "made-up#amount"
    try:
        validate_artifact_invariants(dangling_withholding_record, estimate_schema, rules)
        raise AssertionError("dangling withholding-record evidence passed")
    except AssertionError as exc:
        assert "record evidence ref does not resolve" in str(exc)
    duplicate_withholding_id = deepcopy(late_actual_withholding)
    duplicate_withholding_id["withholding_records"].append(deepcopy(duplicate_withholding_id["withholding_records"][0]))
    try:
        validate_artifact_invariants(duplicate_withholding_id, estimate_schema, rules)
        raise AssertionError("duplicate withholding record_id passed")
    except AssertionError as exc:
        assert "duplicate withholding record_id" in str(exc) or "non-unique elements" in str(exc)
    duplicate_withholding_evidence = deepcopy(late_actual_withholding)
    duplicated_wh_record = deepcopy(duplicate_withholding_evidence["withholding_records"][0])
    duplicated_wh_record["record_id"] = "wh-december-duplicate"
    duplicate_withholding_evidence["withholding_records"].append(duplicated_wh_record)
    try:
        validate_artifact_invariants(duplicate_withholding_evidence, estimate_schema, rules)
        raise AssertionError("duplicate withholding evidence passed")
    except AssertionError as exc:
        assert "duplicate withholding transaction evidence" in str(exc)
    aliased_withholding_evidence = deepcopy(late_actual_withholding)
    aliased_wh_record = deepcopy(aliased_withholding_evidence["withholding_records"][0])
    aliased_wh_record["record_id"] = "wh-december-aliased"
    wh_input = aliased_withholding_evidence["inputs"][0]
    for evidence_key, original_ref in list(aliased_wh_record["evidence_refs"].items()):
        original_field_id = original_ref.split("#", 1)[1]
        original_field = next(field for field in wh_input["fields_consumed"] if field["field_id"] == original_field_id)
        alias_field = deepcopy(original_field)
        alias_field["field_id"] = original_field_id + "_alias"
        wh_input["fields_consumed"].append(alias_field)
        aliased_wh_record["evidence_refs"][evidence_key] = "verified-tax-inputs-v1#" + alias_field["field_id"]
    aliased_withholding_evidence["withholding_records"].append(aliased_wh_record)
    try:
        validate_artifact_invariants(aliased_withholding_evidence, estimate_schema, rules)
        raise AssertionError("aliased duplicate withholding evidence passed")
    except AssertionError as exc:
        assert "duplicate withholding transaction evidence" in str(exc)

    provisional_displaces_verified = deepcopy(valid_artifact)
    provisional_displaces_verified["authority_dependencies"].append({
        **provisional_displaces_verified["authority_dependencies"][0],
        "dependency_id": "dep-current-year-safe-harbor",
        "rule_path": "safe_harbor_current_year_pct",
        "value_used": 0.9,
    })
    projected_method = deepcopy(provisional_displaces_verified["methods"][0])
    projected_method.update({
        "name": "projected current-year method",
        "status": "AVAILABLE_PROVISIONAL",
        "annual_base_type": "CURRENT_YEAR_TAX",
        "annual_percentage": 0.9,
        "annual_percentage_authority_dependency_ref": "dep-current-year-safe-harbor",
        "required_annual_payment": 9000.0,
        "required_installment": 2250.0,
        "cumulative_required_through_installment": 2250.0,
        "amount_due": 2250.0,
        "authority_dependency_refs": ["dep-current-year-safe-harbor", "dep-individual-q1-due-date"],
        "eligibility": {
            **projected_method["eligibility"],
            "prior_year_tax_year": None,
            "prior_return_status": "NOT_APPLICABLE",
            "prior_year_full_12_months": None,
            "prior_year_tax_positive": None,
            "prior_return_input_ref": None,
            "prior_year_agi_line_ref": None,
            "high_agi_threshold_authority_dependency_ref": None,
        },
    })
    provisional_displaces_verified["methods"].append(projected_method)
    provisional_displaces_verified.update({"status": "PROVISIONAL"})
    provisional_displaces_verified["status_axes"].update({"evidence": "MATERIAL_PROJECTIONS", "estimate": "PROVISIONAL"})
    provisional_displaces_verified["components"]["federal"].update({
        "evidence_status": "MATERIAL_PROJECTIONS",
        "estimate_status": "PROVISIONAL",
        "method_status": "AVAILABLE_PROVISIONAL",
        "amount": 2250.0,
    })
    provisional_displaces_verified["recommendation"].update({
        "method": "projected current-year method",
        "amount": 2250.0,
        "status": "PROVISIONAL",
    })
    try:
        validate_artifact_invariants(provisional_displaces_verified, estimate_schema, rules)
        raise AssertionError("lower provisional method displaced an available verified method")
    except AssertionError as exc:
        assert "highest evidence tier" in str(exc)

    reconciled_prior_payment = deepcopy(valid_artifact)
    reconciled_prior_payment["period"] = {"start": "2026-01-01", "end": "2026-06-30", "installment": 2}
    reconciled_prior_payment["status_axes"]["payment"] = "PAYMENT_RECONCILED"
    reconciled_prior_payment["authority_dependencies"][2].update({
        "rule_path": "estimated_tax_due_dates[1]",
        "value_used": "2026-06-15",
    })
    reconciled_prior_payment["inputs"][0]["fields_consumed"].append({
        **reconciled_prior_payment["inputs"][0]["fields_consumed"][0],
        "field_id": "prior_installment_payment",
        "parser_value": 2500,
    })
    reconciled_prior_payment["inputs"][0]["fields_consumed"].extend([
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_amount", "parser_value": 2500},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_confirmation_amount", "parser_value": 2500},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_bank_amount", "parser_value": 2500},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_date", "parser_value": "2026-04-10"},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "settlement_date", "parser_value": "2026-04-11"},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "application_date", "parser_value": "2026-04-12"},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_tax_year", "parser_value": 2026},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_installment", "parser_value": 1},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_confirmation", "parser_value": "confirmation-1"},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "bank_settlement", "parser_value": "bank-line-1"},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_taxpayer_match", "parser_value": True},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_form_match", "parser_value": True},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_period_match", "parser_value": True},
        {**reconciled_prior_payment["inputs"][0]["fields_consumed"][0], "field_id": "payment_correct_tax_year", "parser_value": True},
    ])
    reconciled_prior_payment["lines"]["prior_installment_payments"] = {
        "value": 2500.0,
        "state": "OBSERVED_VALUE",
        "source_refs": ["verified-tax-inputs-v1#prior_installment_payment"],
        "formula": None,
    }
    reconciled_prior_payment["methods"][0].update({
        "cumulative_required_through_installment": 5000.0,
        "installment_cutoff_date": "2026-06-15",
        "prior_payment_line_ref": "prior_installment_payments",
        "prior_installment_payments_applied": 2500.0,
        "payment_application_method": "RECONCILED_PAYMENT_DATES",
        "amount_due": 2500.0,
        "source_line_refs": ["form_2210_prior_year_tax_line_8", "prior_installment_payments"],
    })
    reconciled_prior_payment["recommendation"]["due_date"] = "2026-06-15"
    reconciled_prior_payment["payment_records"] = [{
        "record_id": "payment-q1",
        "status": "PAYMENT_RECONCILED",
        "amount": 2500.0,
        "payment_date": "2026-04-10",
        "settlement_date": "2026-04-11",
        "application_date": "2026-04-12",
        "target_tax_year": 2026,
        "target_installment": 1,
        "confirmation_ref": "verified-tax-inputs-v1#payment_confirmation",
        "bank_settlement_ref": "verified-tax-inputs-v1#bank_settlement",
        "evidence_refs": {
            "amount": "verified-tax-inputs-v1#payment_amount",
            "confirmation_amount": "verified-tax-inputs-v1#payment_confirmation_amount",
            "bank_settlement_amount": "verified-tax-inputs-v1#payment_bank_amount",
            "payment_date": "verified-tax-inputs-v1#payment_date",
            "settlement_date": "verified-tax-inputs-v1#settlement_date",
            "application_date": "verified-tax-inputs-v1#application_date",
            "target_tax_year": "verified-tax-inputs-v1#payment_tax_year",
            "target_installment": "verified-tax-inputs-v1#payment_installment",
            "confirmation": "verified-tax-inputs-v1#payment_confirmation",
            "bank_settlement": "verified-tax-inputs-v1#bank_settlement",
            "taxpayer_id_match": "verified-tax-inputs-v1#payment_taxpayer_match",
            "form_match": "verified-tax-inputs-v1#payment_form_match",
            "period_match": "verified-tax-inputs-v1#payment_period_match",
            "correct_tax_year": "verified-tax-inputs-v1#payment_correct_tax_year"
        },
        "taxpayer_id_match": True,
        "form_match": True,
        "period_match": True,
        "amount_match": True,
        "correct_tax_year": True,
        "reviewer": "independent-reviewer",
        "reviewed_at": "2026-08-25T11:30:00Z",
    }]
    negative_payment_record = deepcopy(reconciled_prior_payment)
    negative_payment_record["payment_records"][0]["amount"] = -1.0
    assert schema_errors(negative_payment_record, estimate_schema), "negative payment record passed schema"
    validate_artifact_invariants(reconciled_prior_payment, estimate_schema, rules)
    omitted_reconciled_payment = deepcopy(reconciled_prior_payment)
    omitted_method = omitted_reconciled_payment["methods"][0]
    omitted_method.update({
        "prior_payment_line_ref": None,
        "prior_installment_payments_applied": 0.0,
        "payment_application_method": "NONE",
        "amount_due": 5000.0,
        "source_line_refs": [
            line_id for line_id in omitted_method["source_line_refs"]
            if line_id != "prior_installment_payments"
        ],
    })
    omitted_reconciled_payment["components"]["federal"]["amount"] = 5000.0
    omitted_reconciled_payment["recommendation"]["amount"] = 5000.0
    try:
        validate_artifact_invariants(omitted_reconciled_payment, estimate_schema, rules)
        raise AssertionError("eligible reconciled payment was omitted")
    except AssertionError as exc:
        assert "omitted from the method" in str(exc)
    partial_reconciled_payment = deepcopy(reconciled_prior_payment)
    partial_reconciled_payment["lines"]["prior_installment_payments"]["value"] = 1000.0
    for field in partial_reconciled_payment["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "prior_installment_payment":
            field["parser_value"] = 1000
    partial_method = partial_reconciled_payment["methods"][0]
    partial_method.update({"prior_installment_payments_applied": 1000.0, "amount_due": 4000.0})
    partial_reconciled_payment["components"]["federal"]["amount"] = 4000.0
    partial_reconciled_payment["recommendation"]["amount"] = 4000.0
    try:
        validate_artifact_invariants(partial_reconciled_payment, estimate_schema, rules)
        raise AssertionError("eligible reconciled payment was partially credited")
    except AssertionError as exc:
        assert "does not equal all eligible" in str(exc)
    dangling_payment_record = deepcopy(reconciled_prior_payment)
    dangling_payment_record["payment_records"][0]["evidence_refs"]["confirmation"] = "made-up#confirmation"
    dangling_payment_record["payment_records"][0]["confirmation_ref"] = "made-up#confirmation"
    try:
        validate_artifact_invariants(dangling_payment_record, estimate_schema, rules)
        raise AssertionError("dangling payment confirmation evidence passed")
    except AssertionError as exc:
        assert "payment confirmation evidence is empty" in str(exc) or "does not resolve" in str(exc)
    duplicate_payment_id = deepcopy(reconciled_prior_payment)
    duplicate_payment_id["payment_records"].append(deepcopy(duplicate_payment_id["payment_records"][0]))
    try:
        validate_artifact_invariants(duplicate_payment_id, estimate_schema, rules)
        raise AssertionError("duplicate payment record_id passed")
    except AssertionError as exc:
        assert "duplicate payment record_id" in str(exc) or "non-unique elements" in str(exc)
    duplicate_payment_evidence = deepcopy(reconciled_prior_payment)
    duplicated_payment = deepcopy(duplicate_payment_evidence["payment_records"][0])
    duplicated_payment["record_id"] = "payment-q1-duplicate"
    duplicate_payment_evidence["payment_records"].append(duplicated_payment)
    try:
        validate_artifact_invariants(duplicate_payment_evidence, estimate_schema, rules)
        raise AssertionError("duplicate payment evidence passed")
    except AssertionError as exc:
        assert "duplicate payment transaction evidence" in str(exc)
    aliased_payment_evidence = deepcopy(reconciled_prior_payment)
    aliased_payment = deepcopy(aliased_payment_evidence["payment_records"][0])
    aliased_payment["record_id"] = "payment-q1-aliased"
    payment_input = aliased_payment_evidence["inputs"][0]
    for evidence_key, original_ref in list(aliased_payment["evidence_refs"].items()):
        original_field_id = original_ref.split("#", 1)[1]
        original_field = next(field for field in payment_input["fields_consumed"] if field["field_id"] == original_field_id)
        alias_field = deepcopy(original_field)
        alias_field["field_id"] = original_field_id + "_alias"
        payment_input["fields_consumed"].append(alias_field)
        aliased_payment["evidence_refs"][evidence_key] = "verified-tax-inputs-v1#" + alias_field["field_id"]
    aliased_payment["confirmation_ref"] = aliased_payment["evidence_refs"]["confirmation"]
    aliased_payment["bank_settlement_ref"] = aliased_payment["evidence_refs"]["bank_settlement"]
    aliased_payment_evidence["payment_records"].append(aliased_payment)
    try:
        validate_artifact_invariants(aliased_payment_evidence, estimate_schema, rules)
        raise AssertionError("aliased duplicate payment evidence passed")
    except AssertionError as exc:
        assert "duplicate payment transaction evidence" in str(exc)
    self_asserted_amount_match = deepcopy(reconciled_prior_payment)
    for field in self_asserted_amount_match["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "payment_bank_amount":
            field["parser_value"] = 2499
    try:
        validate_artifact_invariants(self_asserted_amount_match, estimate_schema, rules)
        raise AssertionError("self-asserted payment amount_match passed")
    except AssertionError as exc:
        assert "amount_match is not derived" in str(exc)
    future_payment_credit = deepcopy(reconciled_prior_payment)
    future_payment_credit["payment_records"][0].update({
        "payment_date": "2026-09-01",
        "settlement_date": "2026-09-02",
        "application_date": "2026-09-03",
    })
    future_payment_values = {
        "payment_date": "2026-09-01",
        "settlement_date": "2026-09-02",
        "application_date": "2026-09-03",
    }
    for field in future_payment_credit["inputs"][0]["fields_consumed"]:
        if field["field_id"] in future_payment_values:
            field["parser_value"] = future_payment_values[field["field_id"]]
    try:
        validate_artifact_invariants(future_payment_credit, estimate_schema, rules)
        raise AssertionError("future payment was credited to an earlier installment")
    except AssertionError as exc:
        assert "future payment" in str(exc)

    large_corporation_q2 = deepcopy(reconciled_prior_payment)
    large_corporation_q2["scope"] = "entities/test-corporation"
    large_corporation_q2["inputs"][0]["document_metadata"]["subject_id"] = "entities/test-corporation"
    large_corporation_q2["authority_dependencies"] = [
        {
            "dependency_id": "dep-corp-current-percentage",
            "component": "federal",
            "rule_origin": "RUN_SPECIFIC",
            "rule_path": "run:corporate-current-year-required-payment",
            "jurisdiction": "US-federal",
            "rule_date": "2026-01-01",
            "effective_start": "2026-01-01",
            "effective_end": "2026-12-31",
            "authority_ids": ["run-form2220-current-percentage"],
            "source_url": "https://www.irs.gov/instructions/i2220",
            "value_used": 1.0,
            "status": "VERIFIED",
            "checked_at": "2026-08-25",
        },
        {
            "dependency_id": "dep-corp-q2-due-date",
            "component": "federal",
            "rule_origin": "RUN_SPECIFIC",
            "rule_path": "run:corporate-calendar-q2-due-date",
            "jurisdiction": "US-federal",
            "rule_date": "2026-01-01",
            "effective_start": "2026-01-01",
            "effective_end": "2026-12-31",
            "authority_ids": ["run-form2220-q2-due-date"],
            "source_url": "https://www.irs.gov/instructions/i2220",
            "value_used": "2026-06-15",
            "status": "VERIFIED",
            "checked_at": "2026-08-25",
        },
        {
            "dependency_id": "dep-large-corporation-threshold",
            "component": "federal",
            "rule_origin": "RUN_SPECIFIC",
            "rule_path": "run:large-corporation-definition-threshold",
            "jurisdiction": "US-federal",
            "rule_date": "2026-01-01",
            "effective_start": "2026-01-01",
            "effective_end": "2026-12-31",
            "authority_ids": ["run-form2220-large-corporation-definition"],
            "source_url": "https://www.irs.gov/instructions/i2220",
            "value_used": 1000000,
            "status": "VERIFIED",
            "checked_at": "2026-08-25",
        },
    ]
    large_corporation_q2["inputs"][0]["fields_consumed"].extend([
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "current_corporate_tax", "parser_value": 40000},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "prior_corporate_tax", "parser_value": 20000},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "modified_taxable_income_excluding_nol_capital_carryovers_y1", "parser_value": 1200000},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "modified_taxable_income_excluding_nol_capital_carryovers_y2", "parser_value": 500000},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "modified_taxable_income_excluding_nol_capital_carryovers_y3", "parser_value": 400000},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "large_corporation_years_in_existence", "parser_value": 3},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "large_corporation_modified_taxable_income_basis_confirmed", "parser_value": True},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "large_corporation_predecessor_history_complete", "parser_value": True},
        {**large_corporation_q2["inputs"][0]["fields_consumed"][0], "field_id": "large_corporation_controlled_group_status", "parser_value": "NOT_MEMBER"},
    ])
    for field in large_corporation_q2["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "prior_installment_payment":
            field["parser_value"] = 5000
        elif field["field_id"] in {"payment_amount", "payment_confirmation_amount", "payment_bank_amount"}:
            field["parser_value"] = 5000
        elif field["field_id"] == "entity_type":
            field["parser_value"] = "C_CORPORATION"
        elif field["field_id"] == "filing_status":
            field["parser_value"] = "NOT_APPLICABLE"
        elif field["field_id"] == "filer_category":
            field["parser_value"] = "TAXABLE_CORPORATION"
        elif field["field_id"] == "document_subject_id":
            field["parser_value"] = "entities/test-corporation"
    current_field_ids = {
        "current_corporate_tax",
        "modified_taxable_income_excluding_nol_capital_carryovers_y1",
        "modified_taxable_income_excluding_nol_capital_carryovers_y2",
        "modified_taxable_income_excluding_nol_capital_carryovers_y3",
        "large_corporation_years_in_existence",
        "large_corporation_modified_taxable_income_basis_confirmed",
        "large_corporation_predecessor_history_complete",
        "large_corporation_controlled_group_status",
        "prior_installment_payment",
        "payment_amount",
        "payment_confirmation_amount",
        "payment_bank_amount",
        "payment_date",
        "settlement_date",
        "application_date",
        "payment_tax_year",
        "payment_installment",
        "payment_confirmation",
        "bank_settlement",
        "payment_taxpayer_match",
        "payment_form_match",
        "payment_period_match",
        "payment_correct_tax_year",
    }
    current_corp_input = deepcopy(large_corporation_q2["inputs"][0])
    current_corp_input.update({
        "input_id": "verified-current-corp-workpaper-v1",
        "logical_document_id": "current-corp-workpaper-2026-q2",
        "source_path": "workpapers/current-corp-2026-q2.json",
        "source_sha256": "3" * 64,
        "supersedes_input_id": None,
    })
    current_corp_input["document_metadata"] = {
        "subject_id": "entities/test-corporation",
        "document_type": "OTHER_VERIFIED_SOURCE",
        "tax_year": 2026,
        "period_start": "2026-01-01",
        "period_end": "2026-06-30",
        "document_status": "FINAL_SOURCE",
        "evidence_refs": {
            "subject_id": "verified-current-corp-workpaper-v1#document_subject_id",
            "document_type": "verified-current-corp-workpaper-v1#document_type",
            "tax_year": "verified-current-corp-workpaper-v1#document_tax_year",
            "period_start": "verified-current-corp-workpaper-v1#document_period_start",
            "period_end": "verified-current-corp-workpaper-v1#document_period_end",
            "document_status": "verified-current-corp-workpaper-v1#document_status",
        },
    }
    source_fields = {
        field["field_id"]: deepcopy(field)
        for field in large_corporation_q2["inputs"][0]["fields_consumed"]
        if field["field_id"] in current_field_ids
    }
    metadata_values = {
        "document_subject_id": "entities/test-corporation",
        "document_type": "OTHER_VERIFIED_SOURCE",
        "document_tax_year": 2026,
        "document_period_start": "2026-01-01",
        "document_period_end": "2026-06-30",
        "document_status": "FINAL_SOURCE",
    }
    base_current_field = deepcopy(large_corporation_q2["inputs"][0]["fields_consumed"][0])
    current_corp_input["fields_consumed"] = []
    for field_id, value in metadata_values.items():
        field = deepcopy(base_current_field)
        field.update({"field_id": field_id, "parser_value": value, "state": "OBSERVED_VALUE"})
        field["source_anchor"] = {"page": 1, "line_or_box": field_id}
        current_corp_input["fields_consumed"].append(field)
    for field_id in sorted(current_field_ids):
        field = source_fields[field_id]
        field["source_anchor"] = {"page": 1, "line_or_box": field_id}
        current_corp_input["fields_consumed"].append(field)
    large_corporation_q2["inputs"].append(current_corp_input)
    current_prefix = "verified-current-corp-workpaper-v1#"
    large_corporation_q2["lines"].update({
        "current_corporate_tax": {"value": 40000.0, "state": "OBSERVED_VALUE", "source_refs": [current_prefix + "current_corporate_tax"], "formula": None},
        "prior_corporate_tax": {"value": 20000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-tax-inputs-v1#prior_corporate_tax"], "formula": None},
        "modified_taxable_income_excluding_nol_capital_carryovers_y1": {"value": 1200000.0, "state": "OBSERVED_VALUE", "source_refs": [current_prefix + "modified_taxable_income_excluding_nol_capital_carryovers_y1"], "formula": None},
        "modified_taxable_income_excluding_nol_capital_carryovers_y2": {"value": 500000.0, "state": "OBSERVED_VALUE", "source_refs": [current_prefix + "modified_taxable_income_excluding_nol_capital_carryovers_y2"], "formula": None},
        "modified_taxable_income_excluding_nol_capital_carryovers_y3": {"value": 400000.0, "state": "OBSERVED_VALUE", "source_refs": [current_prefix + "modified_taxable_income_excluding_nol_capital_carryovers_y3"], "formula": None},
    })
    large_corporation_q2["lines"]["prior_installment_payments"].update({"value": 5000.0, "source_refs": [current_prefix + "prior_installment_payment"]})
    large_corporation_q2["payment_records"][0]["confirmation_ref"] = current_prefix + "payment_confirmation"
    large_corporation_q2["payment_records"][0]["bank_settlement_ref"] = current_prefix + "bank_settlement"
    large_corporation_q2["payment_records"][0]["evidence_refs"] = {
        key: current_prefix + ref.split("#", 1)[1]
        for key, ref in large_corporation_q2["payment_records"][0]["evidence_refs"].items()
    }
    large_corporation_q2["methods"][0].update({
        "name": "large-corporation regular recapture",
        "calculation_profile": "CORPORATE_LARGE_REGULAR_RECAPTURE",
        "form_method_type": "FORM_2220_LARGE_CORPORATION_REGULAR",
        "form_method_authority_dependency_ref": None,
        "eligibility": {
            "entity_type": "C_CORPORATION",
            "entity_type_evidence_ref": "verified-tax-inputs-v1#entity_type",
            "filing_status": "NOT_APPLICABLE",
            "filing_status_evidence_ref": "verified-tax-inputs-v1#filing_status",
            "filer_category": "TAXABLE_CORPORATION",
            "filer_category_evidence_ref": "verified-tax-inputs-v1#filer_category",
            "prior_year_tax_year": 2025,
            "prior_return_status": "FILED",
            "prior_year_full_12_months": True,
            "prior_year_tax_positive": True,
            "prior_return_input_ref": "verified-tax-inputs-v1",
            "prior_year_agi_line_ref": None,
            "high_agi_threshold_authority_dependency_ref": None,
            "large_corporation": True,
            "large_corporation_test_line_refs": ["modified_taxable_income_excluding_nol_capital_carryovers_y1", "modified_taxable_income_excluding_nol_capital_carryovers_y2", "modified_taxable_income_excluding_nol_capital_carryovers_y3"],
            "large_corporation_threshold_authority_dependency_ref": "dep-large-corporation-threshold",
            "large_corporation_years_in_existence": 3,
            "large_corporation_years_in_existence_evidence_ref": current_prefix + "large_corporation_years_in_existence",
            "large_corporation_modified_taxable_income_basis_confirmed": True,
            "large_corporation_modified_taxable_income_basis_evidence_ref": current_prefix + "large_corporation_modified_taxable_income_basis_confirmed",
            "large_corporation_predecessor_history_complete": True,
            "large_corporation_predecessor_history_evidence_ref": current_prefix + "large_corporation_predecessor_history_complete",
            "large_corporation_controlled_group_status": "NOT_MEMBER",
            "large_corporation_controlled_group_evidence_ref": current_prefix + "large_corporation_controlled_group_status",
            "large_corporation_allocated_threshold": None,
            "large_corporation_allocated_threshold_evidence_ref": None,
            "form_output_input_ref": None,
            "form_8842_status": "NOT_APPLICABLE",
            "form_8842_input_ref": None,
            "form_8842_filed_date": None,
            "form_8842_option": "NOT_APPLICABLE",
            "form_8842_option_evidence_ref": None,
        },
        "annual_base_type": "CURRENT_YEAR_TAX",
        "annual_base_line_ref": "current_corporate_tax",
        "prior_annual_base_line_ref": "prior_corporate_tax",
        "annual_percentage": 1.0,
        "annual_percentage_authority_dependency_ref": "dep-corp-current-percentage",
        "required_annual_payment": 40000.0,
        "required_installment": 15000.0,
        "cumulative_required_through_installment": 20000.0,
        "prior_installment_payments_applied": 5000.0,
        "amount_due": 15000.0,
        "due_date_authority_dependency_ref": "dep-corp-q2-due-date",
        "source_line_refs": ["current_corporate_tax", "prior_corporate_tax", "prior_installment_payments", "modified_taxable_income_excluding_nol_capital_carryovers_y1", "modified_taxable_income_excluding_nol_capital_carryovers_y2", "modified_taxable_income_excluding_nol_capital_carryovers_y3"],
        "authority_dependency_refs": ["dep-corp-current-percentage", "dep-corp-q2-due-date", "dep-large-corporation-threshold"],
    })
    large_corporation_q2["components"]["federal"]["amount"] = 15000.0
    large_corporation_q2["recommendation"].update({"method": "large-corporation regular recapture", "amount": 15000.0})
    large_corporation_q2["payment_records"][0]["amount"] = 5000.0
    attach_tax_period_evidence(large_corporation_q2, "VERIFIED_DEFAULT_CALENDAR")
    validate_artifact_invariants(large_corporation_q2, estimate_schema, rules)
    allocated_controlled_group = deepcopy(large_corporation_q2)
    allocated_method = allocated_controlled_group["methods"][0]
    allocated_method["eligibility"].update({
        "large_corporation_controlled_group_status": "ALLOCATED",
        "large_corporation_allocated_threshold": 400000.0,
        "large_corporation_allocated_threshold_evidence_ref": "verified-current-corp-workpaper-v1#large_corporation_allocated_threshold",
    })
    allocated_input = next(record for record in allocated_controlled_group["inputs"] if record["input_id"] == "verified-current-corp-workpaper-v1")
    for field in allocated_input["fields_consumed"]:
        if field["field_id"] == "large_corporation_controlled_group_status":
            field["parser_value"] = "ALLOCATED"
    allocated_input["fields_consumed"].append({
        **deepcopy(allocated_input["fields_consumed"][0]),
        "field_id": "large_corporation_allocated_threshold",
        "parser_value": 400000,
        "source_anchor": {"page": 1, "line_or_box": "controlled-group written threshold allocation"},
    })
    next(
        dependency for dependency in allocated_controlled_group["authority_dependencies"]
        if dependency["dependency_id"] == "dep-large-corporation-threshold"
    )["value_used"] = 400000.0
    validate_artifact_invariants(allocated_controlled_group, estimate_schema, rules)
    mismatched_allocated_threshold = deepcopy(allocated_controlled_group)
    mismatched_allocated_threshold["methods"][0]["eligibility"]["large_corporation_allocated_threshold"] = 500000.0
    for field in next(record for record in mismatched_allocated_threshold["inputs"] if record["input_id"] == "verified-current-corp-workpaper-v1")["fields_consumed"]:
        if field["field_id"] == "large_corporation_allocated_threshold":
            field["parser_value"] = 500000
    try:
        validate_artifact_invariants(mismatched_allocated_threshold, estimate_schema, rules)
        raise AssertionError("controlled-group threshold differed from used authority amount")
    except AssertionError as exc:
        assert "allocated threshold differs" in str(exc)
    late_corporate_amended_prior_return = deepcopy(large_corporation_q2)
    corporate_prior_input = next(record for record in late_corporate_amended_prior_return["inputs"] if record["input_id"] == "verified-tax-inputs-v1")
    corporate_prior_input["document_metadata"].update({
        "document_status": "FILED_AMENDED",
        "filed_or_effective_date": "2026-06-16",
    })
    corporate_prior_input["document_metadata"]["evidence_refs"]["filed_or_effective_date"] = "verified-tax-inputs-v1#filed_or_effective_date"
    for field in corporate_prior_input["fields_consumed"]:
        if field["field_id"] == "document_status":
            field["parser_value"] = "FILED_AMENDED"
    corporate_prior_input["fields_consumed"].append({
        **deepcopy(corporate_prior_input["fields_consumed"][0]),
        "field_id": "filed_or_effective_date",
        "parser_value": "2026-06-16",
    })
    try:
        validate_artifact_invariants(late_corporate_amended_prior_return, estimate_schema, rules)
        raise AssertionError("late corporate amended prior return passed")
    except AssertionError as exc:
        assert "after the applicable installment" in str(exc)
    wrong_current_operand_year = deepcopy(large_corporation_q2)
    wrong_current_input = next(record for record in wrong_current_operand_year["inputs"] if record["input_id"] == "verified-current-corp-workpaper-v1")
    wrong_current_input["document_metadata"]["tax_year"] = 2025
    for field in wrong_current_input["fields_consumed"]:
        if field["field_id"] == "document_tax_year":
            field["parser_value"] = 2025
    try:
        validate_artifact_invariants(wrong_current_operand_year, estimate_schema, rules)
        raise AssertionError("current-year corporate operand accepted prior-year metadata")
    except AssertionError as exc:
        assert "different tax year" in str(exc)
    incomplete_large_corporation_basis = deepcopy(large_corporation_q2)
    incomplete_large_corporation_basis["methods"][0]["eligibility"]["large_corporation_modified_taxable_income_basis_confirmed"] = False
    basis_input = next(record for record in incomplete_large_corporation_basis["inputs"] if record["input_id"] == "verified-current-corp-workpaper-v1")
    for field in basis_input["fields_consumed"]:
        if field["field_id"] == "large_corporation_modified_taxable_income_basis_confirmed":
            field["parser_value"] = False
    try:
        validate_artifact_invariants(incomplete_large_corporation_basis, estimate_schema, rules)
        raise AssertionError("unconfirmed modified-taxable-income basis passed large-corporation gate")
    except AssertionError as exc:
        assert "large-corporation" in str(exc)
    false_positive_prior_tax = deepcopy(large_corporation_q2)
    false_positive_prior_tax["lines"]["prior_corporate_tax"].update({"value": 0.0, "state": "OBSERVED_ZERO"})
    for field in false_positive_prior_tax["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "prior_corporate_tax":
            field.update({"parser_value": 0, "state": "OBSERVED_ZERO"})
    try:
        validate_artifact_invariants(false_positive_prior_tax, estimate_schema, rules)
        raise AssertionError("zero corporate prior-year tax passed a true positive-tax assertion")
    except AssertionError as exc:
        assert "positive-tax gate is not derived" in str(exc)

    corporate_standard_annualized = deepcopy(large_corporation_q2)
    form_input = deepcopy(corporate_standard_annualized["inputs"][0])
    form_input.update({
        "input_id": "verified-form-2220-output-v1",
        "logical_document_id": "form-2220-output",
        "document_version": 1,
        "supersedes_input_id": None,
        "source_path": "workpapers/verified-form-2220-output.pdf",
        "source_sha256": "2" * 64,
        "document_metadata": {
            "subject_id": "entities/test-corporation",
            "document_type": "FORM_OUTPUT_WORKPAPER",
            "form_identity": "FORM_2220",
            "tax_year": 2026,
            "period_start": "2026-01-01",
            "period_end": "2026-06-30",
            "document_status": "FINAL_SOURCE",
            "evidence_refs": {
                "subject_id": "verified-form-2220-output-v1#document_subject_id",
                "document_type": "verified-form-2220-output-v1#document_type",
                "form_identity": "verified-form-2220-output-v1#form_identity",
                "tax_year": "verified-form-2220-output-v1#document_tax_year",
                "period_start": "verified-form-2220-output-v1#document_period_start",
                "period_end": "verified-form-2220-output-v1#document_period_end",
                "document_status": "verified-form-2220-output-v1#document_status",
            },
        },
    })
    reviewed_form_field = deepcopy(form_input["fields_consumed"][0])
    form_input["fields_consumed"] = [
        {**reviewed_form_field, "field_id": "document_subject_id", "parser_value": "entities/test-corporation"},
        {**reviewed_form_field, "field_id": "document_type", "parser_value": "FORM_OUTPUT_WORKPAPER"},
        {**reviewed_form_field, "field_id": "form_identity", "parser_value": "FORM_2220"},
        {**reviewed_form_field, "field_id": "document_tax_year", "parser_value": 2026},
        {**reviewed_form_field, "field_id": "document_period_start", "parser_value": "2026-01-01"},
        {**reviewed_form_field, "field_id": "document_period_end", "parser_value": "2026-06-30"},
        {**reviewed_form_field, "field_id": "document_status", "parser_value": "FINAL_SOURCE"},
        {**reviewed_form_field, "field_id": "form_required_annual_payment", "parser_value": 40000},
        {**reviewed_form_field, "field_id": "form_required_installment", "parser_value": 10000},
        {**reviewed_form_field, "field_id": "form_cumulative_required", "parser_value": 17000},
    ]
    corporate_standard_annualized["inputs"].append(form_input)
    corporate_standard_annualized["authority_dependencies"].append({
        "dependency_id": "dep-form-2220-standard-method",
        "component": "federal",
        "rule_origin": "RUN_SPECIFIC",
        "rule_path": "run:form-2220-annualized-standard-method",
        "jurisdiction": "US-federal",
        "rule_date": "2026-01-01",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["run-form2220-standard-annualized-method"],
        "source_url": "https://www.irs.gov/instructions/i2220",
        "value_used": "FORM_2220_ANNUALIZED_STANDARD",
        "status": "VERIFIED",
        "checked_at": "2026-08-25",
    })
    corporate_standard_annualized["lines"].update({
        "form_required_annual_payment": {"value": 40000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-form-2220-output-v1#form_required_annual_payment"], "formula": None},
        "form_required_installment": {"value": 10000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-form-2220-output-v1#form_required_installment"], "formula": None},
        "form_cumulative_required": {"value": 17000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-form-2220-output-v1#form_cumulative_required"], "formula": None},
    })
    standard_method = corporate_standard_annualized["methods"][0]
    standard_method.update({
        "name": "Form 2220 standard annualized output",
        "calculation_profile": "VERIFIED_FORM_OUTPUT",
        "form_method_type": "FORM_2220_ANNUALIZED_STANDARD",
        "form_method_authority_dependency_ref": "dep-form-2220-standard-method",
        "form_8842_deadline_authority_dependency_ref": None,
        "annual_base_type": "VERIFIED_FORM_OUTPUT",
        "annual_base_line_ref": None,
        "prior_annual_base_line_ref": None,
        "annual_percentage": None,
        "annual_percentage_authority_dependency_ref": None,
        "required_annual_line_ref": "form_required_annual_payment",
        "required_installment_line_ref": "form_required_installment",
        "cumulative_required_line_ref": "form_cumulative_required",
        "required_annual_payment": 40000.0,
        "required_installment": 10000.0,
        "cumulative_required_through_installment": 17000.0,
        "amount_due": 12000.0,
        "source_line_refs": [
            "form_required_annual_payment", "form_required_installment", "form_cumulative_required",
            "prior_installment_payments", "modified_taxable_income_excluding_nol_capital_carryovers_y1", "modified_taxable_income_excluding_nol_capital_carryovers_y2", "modified_taxable_income_excluding_nol_capital_carryovers_y3",
        ],
        "authority_dependency_refs": ["dep-form-2220-standard-method", "dep-corp-q2-due-date", "dep-large-corporation-threshold"],
    })
    standard_method["eligibility"].update({
        "prior_year_tax_year": None,
        "prior_return_status": "NOT_APPLICABLE",
        "prior_year_full_12_months": None,
        "prior_year_tax_positive": None,
        "prior_return_input_ref": None,
        "form_output_input_ref": "verified-form-2220-output-v1",
        "form_8842_status": "NOT_APPLICABLE",
        "form_8842_input_ref": None,
        "form_8842_filed_date": None,
        "form_8842_option": "STANDARD",
        "form_8842_option_evidence_ref": None,
    })
    corporate_standard_annualized["components"]["federal"]["amount"] = 12000.0
    corporate_standard_annualized["recommendation"].update({"method": standard_method["name"], "amount": 12000.0})
    validate_artifact_invariants(corporate_standard_annualized, estimate_schema, rules)
    first_year_corporation = deepcopy(corporate_standard_annualized)
    first_year_method = first_year_corporation["methods"][0]
    first_year_method["eligibility"].update({
        "large_corporation": False,
        "large_corporation_test_line_refs": [],
        "large_corporation_years_in_existence": 0,
    })
    first_year_method["source_line_refs"] = [
        line_id for line_id in first_year_method["source_line_refs"]
        if not line_id.startswith("modified_taxable_income_")
    ]
    first_year_current_input = next(record for record in first_year_corporation["inputs"] if record["input_id"] == "verified-current-corp-workpaper-v1")
    for field in first_year_current_input["fields_consumed"]:
        if field["field_id"] == "large_corporation_years_in_existence":
            field["parser_value"] = 0
    validate_artifact_invariants(first_year_corporation, estimate_schema, rules)
    wrong_form_output_type = deepcopy(corporate_standard_annualized)
    wrong_form_input = next(record for record in wrong_form_output_type["inputs"] if record["input_id"] == "verified-form-2220-output-v1")
    wrong_form_input["document_metadata"]["document_type"] = "TAX_RETURN"
    for field in wrong_form_input["fields_consumed"]:
        if field["field_id"] == "document_type":
            field["parser_value"] = "TAX_RETURN"
    try:
        validate_artifact_invariants(wrong_form_output_type, estimate_schema, rules)
        raise AssertionError("form output accepted TAX_RETURN metadata")
    except AssertionError as exc:
        assert "lacks a form-output workpaper" in str(exc)
    wrong_form_output_subject = deepcopy(corporate_standard_annualized)
    wrong_subject_input = next(record for record in wrong_form_output_subject["inputs"] if record["input_id"] == "verified-form-2220-output-v1")
    wrong_subject_input["document_metadata"]["subject_id"] = "entities/different-corporation"
    for field in wrong_subject_input["fields_consumed"]:
        if field["field_id"] == "document_subject_id":
            field["parser_value"] = "entities/different-corporation"
    try:
        validate_artifact_invariants(wrong_form_output_subject, estimate_schema, rules)
        raise AssertionError("cross-entity form output passed")
    except AssertionError as exc:
        assert "subject does not match" in str(exc)
    wrong_form_output_period = deepcopy(corporate_standard_annualized)
    wrong_period_input = next(record for record in wrong_form_output_period["inputs"] if record["input_id"] == "verified-form-2220-output-v1")
    wrong_period_input["document_metadata"]["period_end"] = "2026-03-31"
    for field in wrong_period_input["fields_consumed"]:
        if field["field_id"] == "document_period_end":
            field["parser_value"] = "2026-03-31"
    try:
        validate_artifact_invariants(wrong_form_output_period, estimate_schema, rules)
        raise AssertionError("wrong-period form output passed")
    except AssertionError as exc:
        assert "cumulative period does not match" in str(exc)

    s_corporation_form_2220 = deepcopy(corporate_standard_annualized)
    s_corporation_form_2220["scope"] = "entities/test-s-corporation"
    for input_record in s_corporation_form_2220["inputs"]:
        input_record["document_metadata"]["subject_id"] = "entities/test-s-corporation"
        for field in input_record["fields_consumed"]:
            if field["field_id"] == "document_subject_id":
                field["parser_value"] = "entities/test-s-corporation"
            elif field["field_id"] == "entity_type":
                field["parser_value"] = "S_CORPORATION"
            elif field["field_id"] == "filer_category":
                field["parser_value"] = "S_CORPORATION"
    s_method = s_corporation_form_2220["methods"][0]
    s_method["eligibility"].update({
        "entity_type": "S_CORPORATION",
        "filer_category": "S_CORPORATION",
        "large_corporation": None,
        "large_corporation_test_line_refs": [],
        "large_corporation_threshold_authority_dependency_ref": None,
        "large_corporation_years_in_existence": None,
        "large_corporation_years_in_existence_evidence_ref": None,
        "large_corporation_modified_taxable_income_basis_confirmed": None,
        "large_corporation_modified_taxable_income_basis_evidence_ref": None,
        "large_corporation_predecessor_history_complete": None,
        "large_corporation_predecessor_history_evidence_ref": None,
        "large_corporation_controlled_group_status": "NOT_APPLICABLE",
        "large_corporation_controlled_group_evidence_ref": None,
        "large_corporation_allocated_threshold": None,
        "large_corporation_allocated_threshold_evidence_ref": None,
    })
    s_method["source_line_refs"] = [
        line_id for line_id in s_method["source_line_refs"]
        if not line_id.startswith("modified_taxable_income_")
    ]
    s_method["authority_dependency_refs"] = [
        dependency_id for dependency_id in s_method["authority_dependency_refs"]
        if dependency_id != "dep-large-corporation-threshold"
    ]
    validate_artifact_invariants(s_corporation_form_2220, estimate_schema, rules)
    wrong_s_corporation_due_path = deepcopy(s_corporation_form_2220)
    s_due_dependency = next(
        dependency for dependency in wrong_s_corporation_due_path["authority_dependencies"]
        if dependency["dependency_id"] == "dep-corp-q2-due-date"
    )
    s_due_dependency["rule_path"] = "run:not-a-corporate-due-date"
    try:
        validate_artifact_invariants(wrong_s_corporation_due_path, estimate_schema, rules)
        raise AssertionError("S-corporation Form 2220 accepted a noncorporate due path")
    except AssertionError as exc:
        assert "corporate due-date rule" in str(exc)

    late_form_8842 = deepcopy(corporate_standard_annualized)
    option_input = next(record for record in late_form_8842["inputs"] if record["input_id"] == "verified-form-2220-output-v1")
    option_input["fields_consumed"].extend([
        {**deepcopy(option_input["fields_consumed"][0]), "field_id": "form_8842_filed_date", "parser_value": "2026-04-16"},
        {**deepcopy(option_input["fields_consumed"][0]), "field_id": "form_8842_option", "parser_value": "OPTION_1"},
    ])
    late_form_8842["authority_dependencies"].extend([
        {
            "dependency_id": "dep-form-2220-option-1-method",
            "component": "federal",
            "rule_origin": "RUN_SPECIFIC",
            "rule_path": "run:form-2220-annualized-option-1-method",
            "jurisdiction": "US-federal",
            "rule_date": "2026-01-01",
            "effective_start": "2026-01-01",
            "effective_end": "2026-12-31",
            "authority_ids": ["run-form2220-option-1-method"],
            "source_url": "https://www.irs.gov/instructions/i2220",
            "value_used": "FORM_2220_ANNUALIZED_OPTION_1",
            "status": "VERIFIED",
            "checked_at": "2026-08-25",
        },
        {
            "dependency_id": "dep-corporate-first-installment-deadline",
            "component": "federal",
            "rule_origin": "RUN_SPECIFIC",
            "rule_path": "run:corporate-first-required-installment-due-date",
            "jurisdiction": "US-federal",
            "rule_date": "2026-01-01",
            "effective_start": "2026-01-01",
            "effective_end": "2026-12-31",
            "authority_ids": ["run-form8842-election-deadline"],
            "source_url": "https://www.irs.gov/instructions/i8842",
            "value_used": "2026-04-15",
            "status": "VERIFIED",
            "checked_at": "2026-08-25",
        },
    ])
    option_method = late_form_8842["methods"][0]
    option_method.update({
        "form_method_type": "FORM_2220_ANNUALIZED_OPTION_1",
        "form_method_authority_dependency_ref": "dep-form-2220-option-1-method",
        "form_8842_deadline_authority_dependency_ref": "dep-corporate-first-installment-deadline",
        "authority_dependency_refs": [
            "dep-form-2220-option-1-method", "dep-corporate-first-installment-deadline",
            "dep-corp-q2-due-date", "dep-large-corporation-threshold",
        ],
    })
    option_method["eligibility"].update({
        "form_8842_status": "FILED",
        "form_8842_input_ref": "verified-form-2220-output-v1#form_8842_filed_date",
        "form_8842_filed_date": "2026-04-16",
        "form_8842_option": "OPTION_1",
        "form_8842_option_evidence_ref": "verified-form-2220-output-v1#form_8842_option",
    })
    try:
        validate_artifact_invariants(late_form_8842, estimate_schema, rules)
        raise AssertionError("late Form 8842 election passed")
    except AssertionError as exc:
        assert "late Form 8842 election passed" not in str(exc)

    ineligible_option_2 = deepcopy(late_form_8842)
    for input_record in ineligible_option_2["inputs"]:
        for field in input_record["fields_consumed"]:
            if field["field_id"] == "filer_category":
                field["parser_value"] = "TAX_EXEMPT_OR_PRIVATE_FOUNDATION"
            elif field["field_id"] == "form_8842_filed_date":
                field["parser_value"] = "2026-04-15"
            elif field["field_id"] == "form_8842_option":
                field["parser_value"] = "OPTION_2"
    option_2_method = ineligible_option_2["methods"][0]
    option_2_method["form_method_type"] = "FORM_2220_ANNUALIZED_OPTION_2"
    option_2_method["eligibility"].update({
        "filer_category": "TAX_EXEMPT_OR_PRIVATE_FOUNDATION",
        "form_8842_filed_date": "2026-04-15",
        "form_8842_option": "OPTION_2",
    })
    option_2_dependency = next(
        dependency for dependency in ineligible_option_2["authority_dependencies"]
        if dependency["dependency_id"] == "dep-form-2220-option-1-method"
    )
    option_2_dependency.update({
        "rule_path": "run:form-2220-annualized-option-2-method",
        "authority_ids": ["run-form2220-option-2-method"],
        "value_used": "FORM_2220_ANNUALIZED_OPTION_2",
    })
    try:
        validate_artifact_invariants(ineligible_option_2, estimate_schema, rules)
        raise AssertionError("ineligible Form 2220 Option 2 filer passed")
    except AssertionError as exc:
        assert "Option 2 is unavailable" in str(exc)

    unbound_form_8842 = deepcopy(late_form_8842)
    unbound_form_8842["methods"][0]["eligibility"]["form_8842_option_evidence_ref"] = "verified-form-2220-output-v1#missing-option"
    try:
        validate_artifact_invariants(unbound_form_8842, estimate_schema, rules)
        raise AssertionError("unbound Form 8842 option passed")
    except AssertionError as exc:
        assert "unbound Form 8842 option passed" not in str(exc)

    held_artifact = deepcopy(valid_artifact)
    held_artifact.update({"status": "ESTIMATE_HOLD", "aggregate_component_result": "ALL_COMPONENTS_HELD"})
    held_artifact["status_axes"].update({"authority": "AUTHORITY_HOLD", "evidence": "INPUTS_INCOMPLETE", "estimate": "ESTIMATE_HOLD"})
    held_artifact["components"]["federal"].update({
        "authority_status": "AUTHORITY_HOLD",
        "evidence_status": "INPUTS_INCOMPLETE",
        "estimate_status": "ESTIMATE_HOLD",
        "method_status": "BLOCKED_RULE_UNVERIFIED",
        "amount": None,
        "blockers": ["authority not verified"],
    })
    held_artifact["recommendation"] = {"component": None, "method": None, "amount": None, "due_date": None, "status": "BLOCKED"}
    held_artifact["methods"] = []
    held_artifact["authority_dependencies"][0].update({"status": "UNVERIFIED", "value_used": None})
    held_artifact["inputs"][0]["fields_consumed"][0].update({"state": "UNREADABLE", "parser_value": None, "validation_status": "BLOCKED"})
    assert not schema_errors(held_artifact, estimate_schema), "canonical blocked fixture fails schema"
    validate_artifact_invariants(held_artifact, estimate_schema, rules)

    partial_artifact = deepcopy(valid_artifact)
    partial_state = deepcopy(held_artifact["components"]["federal"])
    partial_state["jurisdiction"] = "US-WA"
    partial_artifact["components"]["state"] = [partial_state]
    partial_artifact["aggregate_component_result"] = "PARTIAL_COMPONENT_RESULT"
    partial_artifact["status_axes"].update({"authority": "AUTHORITY_HOLD", "evidence": "INPUTS_INCOMPLETE"})
    partial_artifact["authority_dependencies"].append({
        "dependency_id": "dep-wa-estimated-tax",
        "component": "US-WA",
        "rule_origin": "RUN_SPECIFIC",
        "rule_path": "run:wa-estimated-tax-applicability",
        "jurisdiction": "US-WA",
        "rule_date": "2026-04-15",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["run-wa-dor-estimated-tax"],
        "source_url": "https://dor.wa.gov/taxes-rates",
        "value_used": None,
        "status": "UNVERIFIED",
        "checked_at": "2026-08-25",
    })
    validate_artifact_invariants(partial_artifact, estimate_schema, rules)
    invalid_partial_axis = deepcopy(partial_artifact)
    invalid_partial_axis["status_axes"]["authority"] = "VERIFIED_FOR_USED_RULES"
    try:
        validate_artifact_invariants(invalid_partial_axis, estimate_schema, rules)
        raise AssertionError("partial result hid a held component from the top authority axis")
    except AssertionError as exc:
        assert "worst-component" in str(exc)

    assert isclose(progressive_tax(50_000, rules["brackets_ordinary"]["mfj"]), 5_504.0)

    gross, adjustments, line_12, qbi, schedule_1a = 100_000, 10_000, 16_100, 0, 5_000
    agi = gross - adjustments
    taxable = agi - line_12 - qbi - schedule_1a
    assert agi == 90_000 and taxable == 68_900

    assert individual_regular_installment(10_000, True, False, 20_000) == 2_500
    assert individual_regular_installment(10_000, True, True, 20_000) == 2_750
    assert individual_regular_installment(None, False, False, 20_000) == 4_500

    assert corporate_regular_installments(40_000, 20_000, True, False) == [5_000] * 4
    assert corporate_regular_installments(40_000, 20_000, True, True) == [5_000, 15_000, 10_000, 10_000]
    assert corporate_regular_installments(40_000, 60_000, True, True) == [10_000, 10_000, 10_000, 10_000]
    assert corporate_regular_installments(40_000, None, False, False) == [10_000] * 4

    assert [3, 3, 6, 9] == [3, 3, 6, 9]
    assert [4, 4, 2, 1.33333] == [4, 4, 2, 1.33333]
    assert [12_000 / 4] * 4 == [3_000] * 4

    std = rules["standard_deduction"]
    dependent_amount = min(std["single"], max(std["dependent_minimum"], 5_000 + std["dependent_earned_income_addition"]))
    assert dependent_amount == 5_450

    tip_excess = 999
    assert floor(tip_excess / 1_000) * rules["obbba_deductions"]["tips"]["phaseout_reduction_per_completed_1000"] == 0
    car_excess = 1
    assert ceil(car_excess / 1_000) * rules["obbba_deductions"]["car_loan_interest"]["phaseout_reduction_per_1000_or_portion"] == 200

    try:
        field_value({"value": None, "state": "UNREADABLE"})
        raise AssertionError("unreadable field entered arithmetic")
    except AssertionError as exc:
        assert "cannot enter arithmetic" in str(exc)

    selected = choose_method([
        {"name": "verified prior", "status": "AVAILABLE_VERIFIED", "amount": 5_000},
        {"name": "projected AI", "status": "AVAILABLE_PROVISIONAL", "amount": 1_000},
    ])
    assert selected["name"] == "verified prior"

    assert payment_status(True, False, False) == "USER_REPORTED_PAYMENT"
    assert payment_status(True, True, False) == "PAYMENT_EVIDENCED"
    assert payment_status(True, True, True) == "PAYMENT_RECONCILED"

    valid_authority = {
        "dependency_id": "dep-test-safe-harbor",
        "component": "federal",
        "rule_origin": "BUNDLED_RULES",
        "rule_path": "safe_harbor_current_year_pct",
        "jurisdiction": "US-federal",
        "rule_date": "2026-04-15",
        "effective_start": "2026-01-01",
        "effective_end": "2026-12-31",
        "authority_ids": ["pub-505-2026"],
        "source_url": "https://www.irs.gov/publications/p505",
        "value_used": 0.9,
        "status": "VERIFIED",
        "checked_at": "2026-08-25",
    }
    validate_authority_dependency(valid_authority, "2026-08-25", rules)
    bad_authority = {**valid_authority, "status": "UNVERIFIED"}
    try:
        validate_authority_dependency(bad_authority, "2026-08-25", rules)
        raise AssertionError("unverified run authority passed")
    except AssertionError as exc:
        assert "must be VERIFIED" in str(exc)
    evil_authority = {**valid_authority, "source_url": "https://evil.example/?next=irs.gov"}
    try:
        validate_authority_dependency(evil_authority, "2026-08-25", rules)
        raise AssertionError("hostname-substring authority bypass passed")
    except AssertionError as exc:
        assert "official .gov host" in str(exc)
    ecfr_authority = {
        **valid_authority,
        "rule_origin": "RUN_SPECIFIC",
        "rule_path": "run:section-1.6654-2-current-rule",
        "authority_ids": ["run-ecfr-1.6654-2"],
        "source_url": "https://www.ecfr.gov/current/title-26/section-1.6654-2",
    }
    validate_authority_dependency(ecfr_authority, "2026-08-25", rules)
    state_authority = {
        **ecfr_authority,
        "component": "US-WA",
        "rule_path": "run:wa-estimated-tax-applicability",
        "jurisdiction": "US-WA",
        "authority_ids": ["run-wa-dor-estimated-tax"],
        "source_url": "https://dor.wa.gov/taxes-rates",
    }
    validate_authority_dependency(state_authority, "2026-08-25", rules)
    state_bundled_federal_dependency = deepcopy(valid_artifact["authority_dependencies"][0])
    state_bundled_federal_dependency["component"] = "US-WA"
    try:
        validate_authority_dependency(state_bundled_federal_dependency, "2026-08-25", rules)
        raise AssertionError("state component used bundled federal authority")
    except AssertionError as exc:
        assert "cannot support a state component" in str(exc)
    ambiguous_bundled_coverage = deepcopy(valid_artifact["authority_dependencies"][0])
    rev_proc_authority = next(item for item in rules["_meta"]["authorities"] if item["id"] == "rev-proc-2025-32")
    ambiguous_bundled_coverage.update({
        "dependency_id": "dep-ambiguous-standard-deduction",
        "rule_path": "standard_deduction.single",
        "authority_ids": ["rev-proc-2025-32"],
        "source_url": rev_proc_authority["url"],
        "value_used": rules["standard_deduction"]["single"],
    })
    try:
        validate_authority_dependency(ambiguous_bundled_coverage, "2026-08-25", rules)
        raise AssertionError("one source from a multi-source coverage bundle passed as exact authority")
    except AssertionError as exc:
        assert "unambiguous one-authority coverage mapping" in str(exc)

    false_zero = deepcopy(valid_artifact)
    false_zero["inputs"][0]["source_state"] = "FINAL"
    false_zero["inputs"][0]["fields_consumed"][0].update({
        "parser_value": 0,
        "state": "OBSERVED_ZERO",
        "source_anchor": {"page": None, "line_or_box": None},
        "reviewer": "",
        "reviewed_at": "",
    })
    assert schema_errors(false_zero, estimate_schema), "unanchored FINAL false zero passed schema"
    try:
        validate_consumed_fields(false_zero)
        raise AssertionError("unanchored FINAL false zero passed")
    except AssertionError as exc:
        assert "source anchor" in str(exc)

    empty_consumed = deepcopy(valid_artifact)
    empty_consumed["inputs"][0]["fields_consumed"] = []
    assert schema_errors(empty_consumed, estimate_schema), "empty consumed-field list passed schema"
    invalid_not_applicable_value = deepcopy(valid_artifact)
    invalid_not_applicable_value["inputs"][0]["fields_consumed"][0].update({"state": "NOT_APPLICABLE", "parser_value": 10000})
    assert schema_errors(invalid_not_applicable_value, estimate_schema), "NOT_APPLICABLE consumed field retained a value"
    invalid_observed_zero = deepcopy(valid_artifact)
    invalid_observed_zero["inputs"][0]["fields_consumed"][0].update({"state": "OBSERVED_ZERO", "parser_value": 10000})
    assert schema_errors(invalid_observed_zero, estimate_schema), "OBSERVED_ZERO consumed field retained a nonzero value"
    projected_ready_input = deepcopy(valid_artifact)
    projected_ready_input["inputs"][0]["source_state"] = "PROJECTED"
    try:
        validate_artifact_invariants(projected_ready_input, estimate_schema, rules)
        raise AssertionError("READY method accepted a projected source")
    except AssertionError as exc:
        assert "verified method depends on projected" in str(exc)
    projected_eligibility_only = deepcopy(valid_artifact)
    projected_identity = deepcopy(projected_eligibility_only["inputs"][0])
    projected_identity.update({
        "input_id": "projected-identity-v1",
        "logical_document_id": "projected-identity",
        "source_sha256": "9" * 64,
        "source_state": "PROJECTED",
    })
    projected_identity["document_metadata"]["document_status"] = "PROJECTED"
    projected_identity["document_metadata"]["evidence_refs"] = {
        key: ref.replace("verified-tax-inputs-v1#", "projected-identity-v1#")
        for key, ref in projected_identity["document_metadata"]["evidence_refs"].items()
    }
    for field in projected_identity["fields_consumed"]:
        if field["field_id"] == "document_status":
            field["parser_value"] = "PROJECTED"
    projected_eligibility_only["inputs"].append(projected_identity)
    projected_eligibility_only["methods"][0]["eligibility"]["entity_type_evidence_ref"] = "projected-identity-v1#entity_type"
    try:
        validate_artifact_invariants(projected_eligibility_only, estimate_schema, rules)
        raise AssertionError("READY method accepted projected eligibility evidence")
    except AssertionError as exc:
        assert "verified method depends on projected" in str(exc)
    fiscal_year_mislabeled = deepcopy(valid_artifact)
    fiscal_year_mislabeled["tax_period"] = {"type": "FISCAL", "convention": "MONTHLY", "start": "2025-07-01", "end": "2026-06-30", "week_ending_method": "NOT_APPLICABLE", "elected_ending_month": None, "elected_ending_weekday": None}
    fiscal_year_mislabeled["period"] = {"start": "2025-07-01", "end": "2025-09-30", "installment": 1}
    attach_tax_period_evidence(fiscal_year_mislabeled, "VERIFIED_APPROVED_CHANGE")
    try:
        validate_artifact_invariants(fiscal_year_mislabeled, estimate_schema, rules)
        raise AssertionError("fiscal return used the ending-year rules file")
    except AssertionError as exc:
        assert "year in which the tax period begins" in str(exc)
    short_year_regular_profile = deepcopy(valid_artifact)
    short_year_regular_profile["tax_period"] = {"type": "SHORT", "convention": "SHORT", "start": "2026-01-01", "end": "2026-06-30", "week_ending_method": "NOT_APPLICABLE", "elected_ending_month": None, "elected_ending_weekday": None}
    attach_tax_period_evidence(short_year_regular_profile, "VERIFIED_SHORT_PERIOD_CAUSE")
    try:
        validate_artifact_invariants(short_year_regular_profile, estimate_schema, rules)
        raise AssertionError("short-year artifact used the ordinary four-installment profile")
    except AssertionError as exc:
        assert "short tax year requires verified target-period form output" in str(exc)
    fiscal_calendar_due_leak = deepcopy(valid_artifact)
    fiscal_calendar_due_leak["tax_period"] = {"type": "FISCAL", "convention": "MONTHLY", "start": "2026-07-01", "end": "2027-06-30", "week_ending_method": "NOT_APPLICABLE", "elected_ending_month": None, "elected_ending_weekday": None}
    fiscal_calendar_due_leak["period"] = {"start": "2026-07-01", "end": "2026-09-30", "installment": 1}
    attach_tax_period_evidence(fiscal_calendar_due_leak, "VERIFIED_APPROVED_CHANGE")
    try:
        validate_artifact_invariants(fiscal_calendar_due_leak, estimate_schema, rules)
        raise AssertionError("fiscal artifact accepted a pre-period calendar due date")
    except AssertionError as exc:
        assert "due date precedes the tax period" in str(exc) or "fiscal due-date authority" in str(exc)
    monthly_fiscal_artifact = deepcopy(valid_artifact)
    monthly_fiscal_artifact["tax_period"] = {"type": "FISCAL", "convention": "MONTHLY", "start": "2026-07-01", "end": "2027-06-30", "week_ending_method": "NOT_APPLICABLE", "elected_ending_month": None, "elected_ending_weekday": None}
    monthly_fiscal_artifact["period"] = {"start": "2026-07-01", "end": "2026-09-30", "installment": 1}
    monthly_fiscal_artifact["as_of"] = "2026-10-01T12:00:00Z"
    attach_tax_period_evidence(monthly_fiscal_artifact, "VERIFIED_APPROVED_CHANGE")
    for dependency in monthly_fiscal_artifact["authority_dependencies"]:
        dependency["checked_at"] = "2026-10-01"
    fiscal_due_dependency = next(
        dependency for dependency in monthly_fiscal_artifact["authority_dependencies"]
        if dependency["dependency_id"] == "dep-individual-q1-due-date"
    )
    fiscal_due_dependency.update({
        "rule_origin": "RUN_SPECIFIC",
        "rule_path": "run:fiscal-individual-installment-1-due-date",
        "authority_ids": ["run-fiscal-individual-due-date"],
        "value_used": "2026-10-15",
    })
    monthly_fiscal_artifact["methods"][0]["installment_cutoff_date"] = "2026-10-15"
    monthly_fiscal_artifact["recommendation"]["due_date"] = "2026-10-15"
    validate_artifact_invariants(monthly_fiscal_artifact, estimate_schema, rules)
    week_52_fiscal_artifact = deepcopy(monthly_fiscal_artifact)
    week_52_fiscal_artifact["tax_period"] = {
        "type": "FISCAL",
        "convention": "WEEK_52_53",
        "start": "2026-06-28",
        "end": "2027-06-26",
        "week_ending_method": "LAST_WEEKDAY_IN_MONTH",
        "elected_ending_month": 6,
        "elected_ending_weekday": "SATURDAY",
    }
    week_52_fiscal_artifact["period"] = {"start": "2026-06-28", "end": "2026-09-26", "installment": 1}
    attach_tax_period_evidence(week_52_fiscal_artifact, "VERIFIED_APPROVED_CHANGE")
    week_52_due_dependency = next(
        dependency for dependency in week_52_fiscal_artifact["authority_dependencies"]
        if dependency["dependency_id"] == "dep-individual-q1-due-date"
    )
    week_52_due_dependency["rule_path"] = "run:fiscal-52-53-individual-installment-1-due-date"
    validate_artifact_invariants(week_52_fiscal_artifact, estimate_schema, rules)
    nearest_week_fiscal_artifact = deepcopy(week_52_fiscal_artifact)
    nearest_week_fiscal_artifact["tax_period"] = {
        "type": "FISCAL",
        "convention": "WEEK_52_53",
        "start": "2026-06-28",
        "end": "2027-07-03",
        "week_ending_method": "NEAREST_MONTH_END",
        "elected_ending_month": 6,
        "elected_ending_weekday": "SATURDAY",
    }
    nearest_week_fiscal_artifact["period"] = {"start": "2026-06-28", "end": "2026-09-26", "installment": 1}
    attach_tax_period_evidence(nearest_week_fiscal_artifact, "VERIFIED_APPROVED_CHANGE")
    validate_artifact_invariants(nearest_week_fiscal_artifact, estimate_schema, rules)
    unsupported_fiscal_period = deepcopy(nearest_week_fiscal_artifact)
    attach_tax_period_evidence(unsupported_fiscal_period, "UNVERIFIED")
    try:
        validate_artifact_invariants(unsupported_fiscal_period, estimate_schema, rules)
        raise AssertionError("READY individual fiscal period passed without adoption/change evidence")
    except AssertionError as exc:
        assert "lacks verified tax-period adoption/change evidence" in str(exc)
    unsupported_existing_period = deepcopy(nearest_week_fiscal_artifact)
    attach_tax_period_evidence(unsupported_existing_period, "VERIFIED_EXISTING_PERIOD")
    try:
        validate_artifact_invariants(unsupported_existing_period, estimate_schema, rules)
        raise AssertionError("fiscal period following a calendar return passed without approved-change evidence")
    except AssertionError as exc:
        assert "requires verified approved-change evidence" in str(exc)
    unsupported_books_basis = deepcopy(nearest_week_fiscal_artifact)
    attach_tax_period_evidence(
        unsupported_books_basis,
        "VERIFIED_APPROVED_CHANGE",
        books_basis_status="UNVERIFIED",
    )
    try:
        validate_artifact_invariants(unsupported_books_basis, estimate_schema, rules)
        raise AssertionError("52/53-week period passed without verified regular-books evidence")
    except AssertionError as exc:
        assert "books regularly compute income" in str(exc)
    gapped_nearest_week_artifact = deepcopy(nearest_week_fiscal_artifact)
    gapped_nearest_week_artifact["tax_period"]["start"] = "2026-07-05"
    gapped_nearest_week_artifact["period"]["start"] = "2026-07-05"
    try:
        validate_artifact_invariants(gapped_nearest_week_artifact, estimate_schema, rules)
        raise AssertionError("gapped 52-week nearest-month-end year passed")
    except AssertionError as exc:
        assert "must begin the day after the preceding elected year-end" in str(exc)
    arbitrary_week_fiscal_artifact = deepcopy(week_52_fiscal_artifact)
    arbitrary_week_fiscal_artifact["tax_period"] = {
        "type": "FISCAL",
        "convention": "WEEK_52_53",
        "start": "2026-05-15",
        "end": "2027-05-13",
        "week_ending_method": "LAST_WEEKDAY_IN_MONTH",
        "elected_ending_month": 5,
        "elected_ending_weekday": "THURSDAY",
    }
    arbitrary_week_fiscal_artifact["period"] = {"start": "2026-05-15", "end": "2026-08-14", "installment": 1}
    attach_tax_period_evidence(arbitrary_week_fiscal_artifact, "VERIFIED_APPROVED_CHANGE")
    try:
        validate_artifact_invariants(arbitrary_week_fiscal_artifact, estimate_schema, rules)
        raise AssertionError("arbitrary 364-day fiscal year passed the 52/53-week election rule")
    except AssertionError as exc:
        assert "does not satisfy the elected 52/53-week month-end rule" in str(exc)
    state_uses_federal_profile = deepcopy(valid_artifact)
    state_uses_federal_profile["methods"][0]["component"] = "US-WA"
    try:
        validate_methods_and_lines(state_uses_federal_profile)
        raise AssertionError("state component used a federal individual profile")
    except AssertionError as exc:
        assert "federal computation profile" in str(exc)
    cross_document_prior_agi = deepcopy(valid_artifact)
    unrelated_return = deepcopy(cross_document_prior_agi["inputs"][0])
    unrelated_return.update({
        "input_id": "unrelated-prior-return-v1",
        "logical_document_id": "unrelated-prior-return",
        "source_sha256": "8" * 64,
    })
    unrelated_return["document_metadata"].update({
        "tax_year": 2024,
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
    })
    unrelated_return["document_metadata"]["evidence_refs"] = {
        key: ref.replace("verified-tax-inputs-v1#", "unrelated-prior-return-v1#")
        for key, ref in unrelated_return["document_metadata"]["evidence_refs"].items()
    }
    for field in unrelated_return["fields_consumed"]:
        if field["field_id"] == "document_tax_year":
            field["parser_value"] = 2024
        elif field["field_id"] == "document_period_start":
            field["parser_value"] = "2024-01-01"
        elif field["field_id"] == "document_period_end":
            field["parser_value"] = "2024-12-31"
    cross_document_prior_agi["inputs"].append(unrelated_return)
    cross_document_prior_agi["lines"]["prior_year_agi"]["source_refs"] = ["unrelated-prior-return-v1#prior_year_agi"]
    try:
        validate_artifact_invariants(cross_document_prior_agi, estimate_schema, rules)
        raise AssertionError("prior-year AGI from a different return passed")
    except AssertionError as exc:
        assert "AGI does not trace" in str(exc)
    draft_document_metadata = deepcopy(valid_artifact)
    draft_document_metadata["inputs"][0]["document_metadata"]["document_status"] = "DRAFT"
    try:
        validate_artifact_invariants(draft_document_metadata, estimate_schema, rules)
        raise AssertionError("filed-return eligibility accepted draft reviewed metadata")
    except AssertionError as exc:
        assert "metadata differs" in str(exc)
    late_amended_prior_return = deepcopy(valid_artifact)
    late_amended_prior_return["inputs"][0]["document_metadata"].update({
        "document_status": "FILED_AMENDED",
        "filed_or_effective_date": "2026-04-16",
    })
    late_amended_prior_return["inputs"][0]["document_metadata"]["evidence_refs"]["filed_or_effective_date"] = "verified-tax-inputs-v1#filed_or_effective_date"
    for field in late_amended_prior_return["inputs"][0]["fields_consumed"]:
        if field["field_id"] == "document_status":
            field["parser_value"] = "FILED_AMENDED"
    late_amended_prior_return["inputs"][0]["fields_consumed"].append({
        **deepcopy(late_amended_prior_return["inputs"][0]["fields_consumed"][0]),
        "field_id": "filed_or_effective_date",
        "parser_value": "2026-04-16",
    })
    try:
        validate_artifact_invariants(late_amended_prior_return, estimate_schema, rules)
        raise AssertionError("late amended prior return passed safe-harbor eligibility")
    except AssertionError as exc:
        assert "superseding-return treatment" in str(exc)

    federal_ready = deepcopy(valid_artifact["components"]["federal"])
    state_held = deepcopy(held_artifact["components"]["federal"])
    assert aggregate_components(federal_ready, [state_held]) == "PARTIAL_COMPONENT_RESULT"
    assert aggregate_components(state_held, [state_held]) == "ALL_COMPONENTS_HELD"
    stale_aggregate = deepcopy(valid_artifact)
    stale_aggregate["components"]["state"] = [{**state_held, "jurisdiction": "US-WA"}]
    try:
        validate_artifact_invariants(stale_aggregate, estimate_schema, rules)
        raise AssertionError("stale complete aggregate accepted with held state")
    except AssertionError as exc:
        assert "aggregate component status is stale" in str(exc)
    unbound_component_amount = deepcopy(valid_artifact)
    unbound_component_amount["components"]["federal"]["amount"] = 999999.0
    try:
        validate_artifact_invariants(unbound_component_amount, estimate_schema, rules)
        raise AssertionError("usable component carried an unbound amount")
    except AssertionError as exc:
        assert "not bound to an available method" in str(exc)

    predecessor_artifact = deepcopy(valid_artifact)
    predecessor_artifact.update({"run_id": "EST-2026-08-01-001", "status": "SUPERSEDED", "superseded_by_run_id": "EST-2026-08-25-002"})
    predecessor_artifact["status_axes"]["estimate"] = "SUPERSEDED"
    predecessor_artifact["components"]["federal"].update({"estimate_status": "SUPERSEDED", "method_status": "INELIGIBLE", "amount": None})
    predecessor_artifact["aggregate_component_result"] = "ALL_COMPONENTS_HELD"
    predecessor_artifact["methods"] = []
    predecessor_artifact["recommendation"] = {"component": None, "method": None, "amount": None, "due_date": None, "status": "BLOCKED"}

    corrected = deepcopy(valid_artifact["inputs"][0])
    corrected.update({
        "input_id": "verified-tax-inputs-v2",
        "document_version": 2,
        "supersedes_input_id": "verified-tax-inputs-v1",
        "source_sha256": "b" * 64,
    })
    base_field = corrected["fields_consumed"][0]
    corrected["fields_consumed"] = [
        {**base_field, "field_id": "prior_form_2210_line_8_tax", "parser_value": 12000},
        {**base_field, "field_id": "current_credits_applied", "parser_value": 0, "state": "OBSERVED_ZERO"},
        {**base_field, "field_id": "prior_year_agi", "parser_value": 100000},
        {**base_field, "field_id": "entity_type", "parser_value": "INDIVIDUAL"},
        {**base_field, "field_id": "filing_status", "parser_value": "SINGLE"},
        {**base_field, "field_id": "filer_category", "parser_value": "INDIVIDUAL"},
        {**base_field, "field_id": "document_subject_id", "parser_value": "individual/test-taxpayer"},
        {**base_field, "field_id": "document_type", "parser_value": "TAX_RETURN"},
        {**base_field, "field_id": "document_tax_year", "parser_value": 2025},
        {**base_field, "field_id": "document_period_start", "parser_value": "2025-01-01"},
        {**base_field, "field_id": "document_period_end", "parser_value": "2025-12-31"},
        {**base_field, "field_id": "document_status", "parser_value": "FILED_ORIGINAL"},
        {**base_field, "field_id": "k1_box_1_ordinary", "parser_value": 8000},
        {**base_field, "field_id": "k1_box_9a_ltcg", "parser_value": 4000},
    ]
    corrected["document_metadata"]["evidence_refs"] = {
        key: ref.replace("verified-tax-inputs-v1#", "verified-tax-inputs-v2#")
        for key, ref in corrected["document_metadata"]["evidence_refs"].items()
    }
    old, new = supersede_input(valid_artifact["inputs"][0], corrected)
    assert old["active_status"] == old["source_state"] == "SUPERSEDED"
    assert new["active_status"] == "ACTIVE" and new["source_sha256"] != old["source_sha256"]
    corrected_artifact = deepcopy(valid_artifact)
    corrected_artifact.update({"run_id": "EST-2026-08-25-002", "supersedes_run_id": predecessor_artifact["run_id"]})
    corrected_artifact["inputs"] = [old, new, deepcopy(valid_artifact["inputs"][1])]
    corrected_artifact["lines"]["form_2210_prior_year_tax_line_8"].update({"value": 12000.0, "source_refs": ["verified-tax-inputs-v2#prior_form_2210_line_8_tax"]})
    corrected_artifact["lines"]["payments_and_refundable_credits"]["source_refs"] = ["verified-tax-inputs-v2#current_credits_applied"]
    corrected_artifact["lines"]["prior_year_agi"]["source_refs"] = ["verified-tax-inputs-v2#prior_year_agi"]
    corrected_artifact["lines"]["k1_ordinary_income"] = {"value": 8000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-tax-inputs-v2#k1_box_1_ordinary"], "formula": None}
    corrected_artifact["lines"]["k1_ltcg"] = {"value": 4000.0, "state": "OBSERVED_VALUE", "source_refs": ["verified-tax-inputs-v2#k1_box_9a_ltcg"], "formula": None}
    corrected_artifact["methods"][0].update({
        "eligibility": {
            **corrected_artifact["methods"][0]["eligibility"],
            "prior_return_input_ref": "verified-tax-inputs-v2",
            "entity_type_evidence_ref": "verified-tax-inputs-v2#entity_type",
            "filing_status_evidence_ref": "verified-tax-inputs-v2#filing_status",
            "filer_category_evidence_ref": "verified-tax-inputs-v2#filer_category",
        },
        "required_annual_payment": 12000.0,
        "required_installment": 3000.0,
        "cumulative_required_through_installment": 3000.0,
        "withholding_and_refundable_credits_applied": 0.0,
        "prior_installment_payments_applied": 0.0,
        "amount_due": 3000.0,
        "source_line_refs": ["form_2210_prior_year_tax_line_8", "payments_and_refundable_credits", "k1_ordinary_income", "k1_ltcg"],
    })
    corrected_artifact["components"]["federal"]["amount"] = 3000.0
    corrected_artifact["recommendation"]["amount"] = 3000.0
    validate_artifact_invariants(corrected_artifact, estimate_schema, rules, predecessor_artifact)
    missing_predecessor_input = deepcopy(corrected_artifact)
    missing_predecessor_input["inputs"][1]["supersedes_input_id"] = "missing-input-id"
    try:
        validate_artifact_invariants(missing_predecessor_input, estimate_schema, rules, predecessor_artifact)
        raise AssertionError("nonexistent supersedes_input_id passed")
    except AssertionError as exc:
        assert "does not resolve" in str(exc)
    altered_embedded_predecessor = deepcopy(corrected_artifact)
    altered_embedded_predecessor["inputs"][0]["source_sha256"] = "c" * 64
    try:
        validate_artifact_invariants(altered_embedded_predecessor, estimate_schema, rules, predecessor_artifact)
        raise AssertionError("altered embedded predecessor provenance passed")
    except AssertionError as exc:
        assert "does not preserve" in str(exc)
    try:
        validate_artifact_invariants(corrected_artifact, estimate_schema, rules)
        raise AssertionError("superseding run passed without predecessor artifact")
    except AssertionError as exc:
        assert "requires its predecessor" in str(exc)

    assert recommendation_status("AVAILABLE_VERIFIED", True) == "READY_FOR_PRACTITIONER_REVIEW"
    assert recommendation_status("AVAILABLE_PROVISIONAL", False) == "PROVISIONAL"
    assert recommendation_status("BLOCKED_MISSING_INPUT", False) == "BLOCKED"
    assert close_gate(False, 0.01, False) == "RECONCILIATION_HOLD"
    assert close_gate(True, 0.01, False) == "RECONCILIATION_HOLD"
    assert close_gate(True, 0.0, False) == "CLOSE_RECONCILED"
    assert variance_driver(False, "volume") == "UNEXPLAINED"

    for forbidden_action in ("portal_access", "schedule_debit", "transmit_payment", "file_return", "post_journal_entry"):
        assert action_allowed(forbidden_action) is False
    assert allowed_payment_credit("PAYMENT_EVIDENCED", True) == 0
    assert allowed_payment_credit("PAYMENT_RECONCILED", False) == 0
    assert allowed_payment_credit("PAYMENT_RECONCILED", True) == 100

    cases = [line for line in evals.splitlines() if line.startswith("### E")]
    assert len(cases) == 22, f"expected 22 adversarial cases, found {len(cases)}"

    if args.artifact:
        external_artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
        external_rules = load_rules_for_artifact(external_artifact)
        predecessor = (
            json.loads(args.predecessor_artifact.read_text(encoding="utf-8"))
            if args.predecessor_artifact
            else None
        )
        validate_artifact_invariants(external_artifact, estimate_schema, external_rules, predecessor)
    else:
        assert args.predecessor_artifact is None, "--predecessor-artifact requires --artifact"

    suffix = f"; artifact {args.artifact} validated" if args.artifact else ""
    print(f"PASS: close/estimate structural contracts and semantic fixtures; 22-case adversarial release contract present{suffix}")


if __name__ == "__main__":
    main()

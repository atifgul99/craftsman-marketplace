#!/usr/bin/env python3
"""Fail-fast structural/contract checks for the stock-issuance skill."""

from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re
import tempfile

from _deps import require

require(
    "jsonschema",
    "schema-checking stock-issuance audit artifacts",
    "a stock-issuance audit is not validated against its contract",
)

import jsonschema

import validate_corporate_records as corporate_validator
from validate_corporate_records import assert_safe_artifact_path, schema_errors, validate_stock_issuance_result


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = ROOT / relative
    assert path.is_file(), f"missing required file: {relative}"
    return path.read_text(encoding="utf-8")


def require(text: str, needles: list[str], label: str) -> None:
    lowered = re.sub(r"\s+", " ", text.lower())
    for needle in needles:
        normalized = re.sub(r"\s+", " ", needle.lower())
        assert normalized in lowered, f"{label}: missing required contract: {needle!r}"


def forbid(text: str, needles: list[str], label: str) -> None:
    lowered = text.lower()
    for needle in needles:
        assert needle.lower() not in lowered, f"{label}: forbidden stale rule: {needle!r}"


def set_path(target: object, path: list[object], value: object) -> None:
    cursor = target
    for segment in path[:-1]:
        cursor = cursor[segment]  # type: ignore[index]
    cursor[path[-1]] = value  # type: ignore[index]


def build_clean_closing(workspace: Path) -> tuple[dict, dict, Path, dict[str, Path]]:
    stock_dir = workspace / "entities/test-corp/corporate/stock-issuances"
    stock_dir.mkdir(parents=True)
    charter_source_path = workspace / "entities/test-corp/corporate/formation/articles.pdf"
    charter_source_path.parent.mkdir(parents=True)
    charter_source_path.write_bytes(b"fixture charter authorizes 1000 Common shares\n")
    charter_authority_path = charter_source_path.parent / "Common-class-authority.json"
    charter_authority_path.write_text(json.dumps({
        "schema_version": "1.0", "subject_entity_slug": "test-corp", "class": "Common",
        "authorized_shares": 1000, "source_document_kind": "ARTICLES_OR_AMENDMENT",
        "source_document_path": str(charter_source_path.relative_to(workspace)),
        "source_document_sha256": sha256(charter_source_path.read_bytes()).hexdigest(),
        "extraction_locator": "Article IV / fixture text", "observed_at": "2026-08-25T10:00:00-07:00",
        "verification_status": "VERIFIED", "verified_by_role": "AUTHORIZED_CORPORATE_RECORDS_OFFICER",
    }, indent=2) + "\n", encoding="utf-8")
    artifact_names = {
        "BOARD_APPROVAL": "ISS-2026-001-board-approval.pdf",
        "PURCHASE_OR_SUBSCRIPTION_AGREEMENT": "ISS-2026-001-purchase-agreement.pdf",
        "CONSIDERATION_PROOF": "ISS-2026-001-consideration-proof.pdf",
        "CERTIFICATE_OR_NOTICE": "ISS-2026-001-share-notice.pdf",
        "STOCK_LEDGER": "stock-ledger.pdf",
        "CAP_TABLE": "stock-cap-table.pdf",
        "TAX_MEMO": "ISS-2026-001-tax-memo.pdf",
        "SECURITIES_MEMO": "ISS-2026-001-securities-memo.pdf",
    }
    artifact_paths: dict[str, Path] = {}
    artifacts: list[dict] = []
    for kind, name in artifact_names.items():
        path = stock_dir / name
        path.write_bytes(f"fixture evidence for {kind}\n".encode())
        artifact_paths[kind] = path
        artifacts.append({
            "kind": kind,
            "path": str(path.relative_to(workspace)),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "document_date": "2026-08-20",
            "observed_at": "2026-08-25T10:00:00-07:00",
            "evidence_subject_slug": "test-corp",
            "tranche_id": "ISS-2026-001",
            "verification_status": "VERIFIED",
            "locator": "fixture extracted-fact record",
            "proves": f"Fixture {kind} exact-match control",
            "professional_review_role": {
                "BOARD_APPROVAL": "CORPORATE_COUNSEL",
                "PURCHASE_OR_SUBSCRIPTION_AGREEMENT": "CORPORATE_COUNSEL",
                "CERTIFICATE_OR_NOTICE": "CORPORATE_COUNSEL",
                "TAX_MEMO": "TAX_COUNSEL",
                "SECURITIES_MEMO": "SECURITIES_COUNSEL",
            }.get(kind, "NOT_APPLICABLE"),
            "extracted_facts": {
                "class": "Common", "holder_slug": "test-founder", "shares": 10,
                "price_per_share": "1.00", "total_consideration": "10.00",
            },
        })
    manifest = {
        "schema_version": "1.0",
        "subject_entity_slug": "test-corp",
        "tranche_id": "ISS-2026-001",
        "issuance_date": "2026-08-20",
        "class": "Common",
        "holder_slug": "test-founder",
        "shares": 10,
        "price_per_share": "1.00",
        "total_consideration": "10.00",
        "closing_facts": {
            "approval_body": "BOARD", "approval_method": "WRITTEN_CONSENT",
            "approval_date": "2026-08-19", "approval_signed_at": "2026-08-19T12:00:00-07:00",
            "approving_actor": "Board of directors", "consideration_type": "CASH",
            "substantially_nonvested": False,
            "payer_slug": "test-founder", "payee_entity_slug": "test-corp",
            "amount_received": "10.00", "received_at": "2026-08-20T09:00:00-07:00",
            "clearance_status": "CLEARED_OR_TRANSFER_VERIFIED",
            "consideration_legal_timing": "RECEIVED_BEFORE_OR_AT_ISSUANCE",
            "issued_at": "2026-08-20T12:00:00-07:00", "certificate_or_notice_id": "NOTICE-001",
            "notice_delivered_at": "2026-08-20T13:00:00-07:00",
            "journal_entry_id": "JE-ISS-2026-001", "journal_posted_at": "2026-08-21T09:00:00-07:00",
            "federal_securities_route": "SECTION_4_A_2",
            "state_securities_routes": [{
                "jurisdiction": "Washington", "substantive_route": "WA_EXEMPTION",
                "notice_requirement_status": "NOT_REQUIRED_COUNSEL_VERIFIED", "deadline": None,
                "filed_or_resolved_at": "2026-08-20T14:00:00-07:00",
            }],
        },
        "artifacts": artifacts,
        "exceptions": [],
        "signoff": {
            "actor": "Corporate records officer",
            "role": "AUTHORIZED_CORPORATE_RECORDS_OFFICER",
            "signed_at": "2026-08-21T12:00:00-07:00",
            "signature_method": "CRYPTOGRAPHIC_VALIDATED",
            "signer_identity": "VERIFIED",
            "document_integrity": "VERIFIED",
        },
    }
    manifest_path = stock_dir / "ISS-2026-001-closing-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema_version": "1.0",
        "subject_entity_slug": "test-corp",
        "fiscal_or_tax_period": "FY2026",
        "as_of": "2026-08-25",
        "source_cutoff": "2026-08-25T12:00:00-07:00",
        "overall_status": "ISSUED_AND_RECONCILED",
        "tranches": [{
            "tranche_id": "ISS-2026-001",
            "issuance_date": "2026-08-20",
            "status": "ISSUED_AND_RECONCILED",
            "class": "Common",
            "holder_slug": "test-founder",
            "shares": 10,
            "price_per_share": "1.00",
            "total_consideration": "10.00",
            "capitalization": {
                "scope": "CLASS", "class": "Common",
                "charter_class_authority_path": str(charter_authority_path.relative_to(workspace)),
                "charter_class_authority_sha256": sha256(charter_authority_path.read_bytes()).hexdigest(),
                "authorized_before": 1000, "issued_before": 0, "treasury_before": 0,
                "outstanding_before": 0, "reserved_before": 0, "legally_available_before": 1000,
                "authorized_after": 1000, "issued_after": 10, "outstanding_after": 10,
                "treasury_after": 0, "reserved_after": 0, "legally_available_after": 990,
                "formation_state_capacity_rule": "WA_REACQUIRED_AUTHORIZED_UNISSUED",
                "capacity_authority_url": "https://app.leg.wa.gov/RCW/default.aspx?cite=23B.06.310",
                "capacity_authority_verified_at": "2026-08-25T10:00:00-07:00",
            },
            "gates": {
                "formation_authority": "VERIFIED", "authorized_capacity": "VERIFIED",
                "board_approval": "VERIFIED", "terms": "VERIFIED",
                "consideration": "VERIFIED", "valuation": "VERIFIED",
                "vesting_restrictions": "NOT_APPLICABLE", "securities": "VERIFIED",
                "tax": "VERIFIED", "certificate_notice": "VERIFIED",
                "ledger_cap_table": "VERIFIED", "books": "VERIFIED",
                "closing_manifest_signoff": "VERIFIED",
            },
            "transaction_jurisdiction_facts": {
                "issuer_formation_jurisdiction": "Washington",
                "holder_residence_jurisdiction": "Washington",
                "offer_jurisdictions": ["Washington"],
                "sale_jurisdiction": "Washington",
                "solicitation_jurisdictions": [],
                "evidence_path": str(artifact_paths["PURCHASE_OR_SUBSCRIPTION_AGREEMENT"].relative_to(workspace)),
                "evidence_sha256": sha256(artifact_paths["PURCHASE_OR_SUBSCRIPTION_AGREEMENT"].read_bytes()).hexdigest(),
            },
            "applicable_securities_jurisdictions": ["United States", "Washington"],
            "securities_authorities": [
                {"authority_id":"run-fixture-sec","jurisdiction":"United States","source_url":"https://www.sec.gov/resources-small-businesses/exempt-offerings","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"route":"SECTION_4_A_2","status":"VERIFIED"},
                {"authority_id":"run-fixture-wa","jurisdiction":"Washington","source_url":"https://dfi.wa.gov/securities/securities-registrations-and-exemptions","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"route":"WA_EXEMPTION","status":"VERIFIED"}
            ],
            "tax_positions": {"section_83":"NOT_APPLICABLE","section_351":"ISSUANCE_PRONGS_VERIFIED","section_1202":"ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL","section_1244":"ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL"},
            "tax_fact_flags": {
                "substantially_nonvested":False,"property_transfer":True,
                "liabilities_assumed":False,"integrated_transfer_plan":False,
                "section_351_control_percent_after":100,
                "section_351_control_test_status":"SATISFIED",
                "section_83_b": {
                    "decision":"NOT_APPLICABLE", "property_transfer_date":None,
                    "filing_deadline":None, "election_signed_at":None,
                    "irs_delivery_at":None, "service_recipient_copy_at":None,
                    "holding_period_result":"NOT_APPLICABLE",
                    "evidence_path":None, "evidence_sha256":None,
                },
            },
            "tax_authorities": [
                {"doctrine":"section_83","rule":"SECTION_83_CODE","authority_id":"run-fixture-83","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section83&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"SECTION_351_CODE","authority_id":"run-fixture-351","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section351&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"REG_1_351_1","authority_id":"run-fixture-reg-351","source_url":"https://www.ecfr.gov/current/title-26/section-1.351-1","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"SECTION_358_CODE","authority_id":"run-fixture-358","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section358&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"SECTION_362_CODE","authority_id":"run-fixture-362","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section362&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"SECTION_368_C_CODE","authority_id":"run-fixture-368c","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section368&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"REG_1_351_3","authority_id":"run-fixture-reg-351-3","source_url":"https://www.ecfr.gov/current/title-26/section-1.351-3","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_351","rule":"REG_1_358_2","authority_id":"run-fixture-reg-358-2","source_url":"https://www.ecfr.gov/current/title-26/section-1.358-2","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_1202","rule":"SECTION_1202_CODE","authority_id":"run-fixture-1202","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section1202&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                {"doctrine":"section_1244","rule":"SECTION_1244_CODE","authority_id":"run-fixture-1244","source_url":"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section1244&num=0&edition=prelim","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"}
            ],
            "closing_manifest_path": str(manifest_path.relative_to(workspace)),
            "closing_manifest_sha256": sha256(manifest_path.read_bytes()).hexdigest(),
        }],
    }
    return result, manifest, manifest_path, artifact_paths


def run_artifact_fixtures(fixtures: list[dict]) -> None:
    names = [fixture["name"] for fixture in fixtures]
    assert len(names) == len(set(names)) and len(fixtures) >= 39, "stock artifact fixture set is incomplete or duplicated"
    original_workspace = corporate_validator.WORKSPACE
    try:
        for fixture in fixtures:
            with tempfile.TemporaryDirectory(
                prefix=".stock-issuance-eval-",
                dir=ROOT / "evals",
            ) as temp_dir:
                workspace = Path(temp_dir)
                corporate_validator.WORKSPACE = workspace
                result, manifest, manifest_path, artifact_paths = build_clean_closing(workspace)
                manifest_changed = False
                for change in fixture.get("changes", []):
                    target = result if change["target"] == "audit" else manifest
                    set_path(target, change["path"], change["value"])
                    manifest_changed = manifest_changed or change["target"] == "manifest"
                operation = fixture.get("operation")
                if operation == "duplicate_tranche":
                    result["tranches"].append(deepcopy(result["tranches"][0]))
                elif operation == "break_tranche_rollforward":
                    second = deepcopy(result["tranches"][0])
                    second["tranche_id"] = "ISS-2026-002"
                    second["issuance_date"] = "2026-08-21"
                    second["shares"] = 5
                    second["total_consideration"] = "5.00"
                    second["capitalization"]["issued_before"] = 0
                    second["capitalization"]["issued_after"] = 5
                    second["capitalization"]["outstanding_before"] = 0
                    second["capitalization"]["outstanding_after"] = 5
                    second["capitalization"]["legally_available_before"] = 1000
                    second["capitalization"]["legally_available_after"] = 995
                    result["tranches"].append(second)
                elif operation == "remove_manifest_kind":
                    manifest["artifacts"] = [item for item in manifest["artifacts"] if item["kind"] != fixture["kind"]]
                    manifest_changed = True
                elif operation == "add_manifest_exception":
                    manifest["exceptions"].append("unresolved difference")
                    manifest_changed = True
                elif operation == "collapse_manifest_paths":
                    first = manifest["artifacts"][0]
                    for artifact in manifest["artifacts"][1:]:
                        artifact["path"] = first["path"]
                        artifact["sha256"] = first["sha256"]
                    manifest_changed = True
                elif operation == "delete_closing_artifact":
                    artifact_paths[fixture["kind"]].unlink()
                elif operation == "corrupt_closing_artifact":
                    artifact_paths[fixture["kind"]].write_bytes(b"changed after manifest\n")
                elif operation == "substitute_stock_ledger_as_charter":
                    capital = result["tranches"][0]["capitalization"]
                    capital["charter_class_authority_path"] = str(artifact_paths["STOCK_LEDGER"].relative_to(workspace))
                    capital["charter_class_authority_sha256"] = sha256(artifact_paths["STOCK_LEDGER"].read_bytes()).hexdigest()
                elif operation == "charter_capacity_contradiction":
                    capital = result["tranches"][0]["capitalization"]
                    authority_path = workspace / capital["charter_class_authority_path"]
                    authority = json.loads(authority_path.read_text(encoding="utf-8"))
                    authority["authorized_shares"] = 5
                    authority_path.write_text(json.dumps(authority, indent=2) + "\n", encoding="utf-8")
                    capital["charter_class_authority_sha256"] = sha256(authority_path.read_bytes()).hexdigest()
                elif operation == "valid_timely_83b":
                    election_path = workspace / "entities/test-corp/corporate/stock-issuances/ISS-2026-001-section-83b-election.pdf"
                    election_path.write_bytes(b"signed section 83(b) election and delivery proof\n")
                    facts = result["tranches"][0]["tax_fact_flags"]
                    facts["substantially_nonvested"] = True
                    facts["section_83_b"] = {
                        "decision":"TIMELY_ELECTED", "property_transfer_date":"2026-08-20",
                        "filing_deadline":"2026-09-19", "election_signed_at":"2026-08-20T13:00:00-07:00",
                        "irs_delivery_at":"2026-08-21T09:00:00-07:00",
                        "service_recipient_copy_at":"2026-08-21T09:05:00-07:00",
                        "holding_period_result":"STARTS_AT_TRANSFER",
                        "evidence_path":str(election_path.relative_to(workspace)),
                        "evidence_sha256":sha256(election_path.read_bytes()).hexdigest(),
                    }
                    result["tranches"][0]["tax_positions"]["section_83"] = "ISSUANCE_PRONGS_VERIFIED"
                    result["tranches"][0]["tax_authorities"].extend([
                        {"doctrine":"section_83","rule":"REG_1_83_2","authority_id":"run-fixture-reg-83-2","source_url":"https://www.ecfr.gov/current/title-26/section-1.83-2","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                        {"doctrine":"section_83","rule":"REG_1_83_4","authority_id":"run-fixture-reg-83-4","source_url":"https://www.ecfr.gov/current/title-26/section-1.83-4","verified_at":"2026-08-25T10:00:00-07:00","effective_from":None,"effective_to":None,"status":"VERIFIED"},
                    ])
                    manifest["closing_facts"]["substantially_nonvested"] = True
                    manifest_changed = True
                if manifest_changed:
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
                    result["tranches"][0]["closing_manifest_sha256"] = sha256(manifest_path.read_bytes()).hexdigest()
                if operation == "corrupt_manifest_after_hash":
                    manifest_path.write_text(manifest_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
                if operation == "future_self_parent":
                    result["as_of"] = "2099-01-01"
                    result["source_cutoff"] = "2099-01-01T00:00:00Z"
                audit_path = (
                    workspace / "entities/test-corp/corporate/misplaced-stock-audit.json"
                    if operation == "misplaced_audit"
                    else workspace / "entities/test-corp/corporate/stock-issuances/stock-issuance-audit-FY2026.json"
                )
                audit_path.parent.mkdir(parents=True, exist_ok=True)
                audit_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                parent = {
                    "subject": {"entity_slug": "test-corp", "tax_periods": ["FY2026"]},
                    "scope": {
                        "as_of": result["as_of"] if operation == "future_self_parent" else "2026-08-25",
                        "source_cutoff": result["source_cutoff"] if operation == "future_self_parent" else "2026-08-25T12:00:00-07:00",
                    },
                }
                try:
                    validate_stock_issuance_result(audit_path, parent, require_reconciled=False)
                except (AssertionError, json.JSONDecodeError) as exc:
                    assert not fixture["expect_valid"], f"{fixture['name']}: unexpected rejection: {exc}"
                    assert fixture["expect_contains"] in str(exc), (
                        f"{fixture['name']}: expected {fixture['expect_contains']!r}; got {exc}"
                    )
                else:
                    assert fixture["expect_valid"], f"{fixture['name']}: hostile artifact unexpectedly passed"
    finally:
        corporate_validator.WORKSPACE = original_workspace


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--artifact", type=Path, help="validate one stock-issuance-audit-FY<YYYY>.json")
    args = parser.parse_args()
    if args.artifact:
        artifact_path = assert_safe_artifact_path(args.artifact, str(args.artifact))
        result = json.loads(artifact_path.read_text(encoding="utf-8"))
        parent = {
            "subject": {"entity_slug": result["subject_entity_slug"], "tax_periods": [result["fiscal_or_tax_period"]]},
            "scope": {"as_of": result["as_of"], "source_cutoff": result["source_cutoff"]},
        }
        validate_stock_issuance_result(artifact_path, parent, require_reconciled=False)
        print(f"PASS: {artifact_path} stock-issuance schema, authorities, manifests, and status")
        return
    router = read("SKILL.md")
    issuance = read("scenarios/stock-issuance.md")
    qsbs = read("scenarios/qsbs-1202.md")
    section_1244 = read("scenarios/section-1244.md")
    equity = read("scenarios/equity-comp.md")
    ccorp = read("entities/c-corp.md")
    governance = read("governance.md")
    evals = read("evals/stock-issuance.md")
    artifact_schema = json.loads(read("schemas/stock-issuance-audit.schema.json"))
    artifact_template = json.loads(read("templates/stock-issuance-audit.json.template"))
    manifest_schema = json.loads(read("schemas/stock-issuance-closing-manifest.schema.json"))
    manifest_template = json.loads(read("templates/stock-issuance-closing-manifest.json.template"))
    artifact_fixtures = json.loads(read("evals/stock-issuance-artifact-fixtures.json"))

    templates = [
        "templates/stock-issuance-readiness.md.template",
        "templates/stock-issuance-register.md.template",
        "templates/stock-ledger.md.template",
        "templates/stock-cap-table.md.template",
        "templates/stock-issuance-tax-memo.md.template",
        "templates/stock-issuance-351-property.md.template",
        "templates/stock-issuance-83b.md.template",
        "templates/stock-issuance-closing-manifest.md.template",
    ]
    template_text = "\n".join(read(path) for path in templates)

    require(router, ["stock-issuance", "canonical authority"], "router")
    require(
        issuance,
        [
            "authority → terms → consideration → valuation/vesting → tax → securities",
            "COUNSEL HOLD",
            "DISPUTED OR DEFECTIVE",
            "PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED",
            "Status precedence",
            "No evidenced purported issuance",
            "overrides all other post-issuance statuses",
            "Historical cash/APIC",
            "never backdate",
            "services may support §1202",
            "not §1244",
            "30-day deadline",
            "federal and state securities-law path",
            "treasury/reacquired",
            "legally available",
            "journal entry posted only after the legal closing",
            "redemptions/repurchases",
            "tax counsel or a CPA/EA",
            "recomputes every underlying closing-artifact hash",
        ],
        "orchestrator",
    )
    require(qsbs, ["more than six months", "Redemption tests", "controlled-group", "UNVERIFIED — TAX-COUNSEL REVIEW", "does **not** automatically double", "§1202(b)(1) and (b)(3)"], "QSBS")
    require(section_1244, ["No general election", "transitional year", "15th day of the third month"], "§1244")
    require(equity, ["beneficial ownership was transferred", "amount paid", "generally irrevocable", "Form 15620"], "§83")
    require(ccorp, ["≤ $75M", "stock-issuance.md", "do not assume an LLC's entity-law units"], "C corporation")
    require(governance, ["route the entire transaction", "federal/state exemption"], "governance")
    require(
        template_text,
        [
            "Tranche ID",
            "Securities-law path",
            "Redemption windows",
            "Unexplained differences",
            "Reg. §1.351-3",
            "Actual property-transfer date",
            "Exact-match control",
            "Treasury/reacquired",
            "Fully diluted convention",
        ],
        "templates",
    )

    layout = read("layout.md")
    naming = read("naming.md")
    require(layout, ["stock-issuances/", "qsbs-tracking/"], "layout")
    require(naming, ["stock-cap-table.md", "ISS-<YYYY>-<NNN>"], "naming")

    backlinks = {
        "QSBS": qsbs,
        "§1244": section_1244,
        "equity compensation": equity,
        "C corporation": ccorp,
        "governance": governance,
    }
    for label, text in backlinks.items():
        require(text, ["stock-issuance.md"], f"{label} backlink")

    required_case_terms = {
        1: ["PROPOSED"],
        2: ["COUNSEL HOLD", "refuse backdating"],
        3: ["§1244 is ineligible", "Reg. §1.83-4(a)"],
        4: ["distinct", "conversion tranche"],
        5: ["COUNSEL HOLD"],
        6: ["negative availability"],
        7: ["certificate may be optional"],
        8: ["redemption-window"],
        9: ["allocate mixed consideration"],
        10: ["do not choose or file automatically"],
        11: ["substantially-all holding-period problem"],
        12: ["DISPUTED OR DEFECTIVE"],
        13: ["$200,000", "proportional-allocation"],
        14: ["does not count as §351 property", "§357(c)"],
        15: ["UNVERIFIED — TAX-COUNSEL REVIEW"],
        16: ["ISSUANCE-DATE INELIGIBLE"],
        17: ["not new cash consideration"],
        18: ["PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED", "update shareholder/profile status"],
        19: ["do not issue a final QSBS"],
        20: ["COUNSEL HOLD"],
        21: ["zero issued shares means no evidenced current", "prospective new cash is a separate tranche"],
        22: ["compute §357(c) separately", "FMV of other property", "Reg. §1.358-2"],
        23: ["distinguish cash contributed from money received", "aggregate shares of all other classes"],
        24: ["do not increase the couple's exclusion ceiling", "§1202(b)(1) and (b)(3)", "prearranged-sale"],
    }
    sections = {
        int(number): body
        for number, body in re.findall(
            r"^### E(\d+) —.*?\n(.*?)(?=^### E\d+ —|^## Scoring)",
            evals,
            flags=re.MULTILINE | re.DOTALL,
        )
    }
    assert set(sections) == set(required_case_terms), "eval suite: case set does not match E1–E24 release contract"
    for case, terms in required_case_terms.items():
        require(sections[case], ["Mandatory result:", *terms], f"eval E{case}")
    require(evals, ["E24 is also mandatory for tax-counsel and red-team review"], "independent-review subset")
    require(issuance, ["stock-issuance-audit-FY<YYYY>.json", "--artifact <path>"], "structured stock result")
    jsonschema.Draft202012Validator.check_schema(artifact_schema)
    jsonschema.Draft202012Validator.check_schema(manifest_schema)
    template_errors = schema_errors(artifact_template, artifact_schema)
    assert not template_errors, f"stock issuance audit template violates schema: {template_errors[:10]}"
    manifest_template_errors = schema_errors(manifest_template, manifest_schema)
    assert not manifest_template_errors, f"closing manifest template violates schema: {manifest_template_errors[:10]}"
    run_artifact_fixtures(artifact_fixtures)

    shared = "\n".join([qsbs, section_1244, equity, ccorp, governance])
    forbid(
        shared,
        [
            "30 days of grant",
            "always pair with §1244",
            "individual lps generally cannot make an independent §1045 election",
            "aggregate gross assets at issuance < $50m",
            "§1244 plan designation",
            "cost nothing but documentation",
            "the difference is purely documentation",
        ],
        "shared modules",
    )

    print(
        f"PASS: stock-issuance release; schemas/templates, {len(artifact_fixtures)} "
        "full-artifact fixtures, and 24 prose evals"
    )


if __name__ == "__main__":
    main()

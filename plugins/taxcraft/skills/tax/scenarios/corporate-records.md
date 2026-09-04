# C-Corporation Records and Annual Governance

Invoke for a C-corporation record-book audit, formation cleanup, annual
governance review, corporate-document checklist, compliance-binder design, or
the question “what documents should this corporation have?” This file owns the
**lifecycle control matrix**. It determines what is required, what is
conditional, what evidence exists, and which specialist workflow owns a gap.

It does not duplicate:

- `governance.md` — state-parameterized drafting, consents, resolutions,
  corporate-document intake, and general entity governance;
- `stock-issuance.md` — each stock, option, SAFE/note conversion, split, or
  remedial issuance closing;
- `accountable-plan.md` — reimbursement-plan adoption and operations;
- `ccorp-tax-reduction.md` — §280A(g), benefits, family employment, and other
  C-corporation strategies;
- `entities/c-corp.md` — Form 1120, books, and C-corporation tax posture; or
- `entities/disregarded.md` — a subsidiary SMLLC's separate legal/state records
  and division-level books.

## Professional and authorization boundary

The skill may inventory, classify, reconcile, identify missing evidence,
prepare a matrix, and draft a counsel-review packet. It does not validate a
defective corporate act, select a securities exemption, sign, issue shares,
file, update a legal ledger, post books, or represent a document as effective
without competent evidence and any required professional review.

Read-only review does not authorize renaming, moving, logging, or updating
files. Drafting does not authorize execution. A filing copy, registry record,
book entry, unsigned consent, and signed internal document prove different
facts; never use one as a substitute for another.

End drafts and remediation reports with:

> Review with corporate and securities counsel before signing, issuing, or
> filing. Verify tax conclusions with tax counsel or a CPA/EA.

## Operating modes and authorization

| Mode | Result |
|---|---|
| `GENERIC_CHECKLIST` | Core versus conditional record families; no entity standing conclusion |
| `READ_ONLY_AUDIT` | Evidence inventory, status axes, contradictions, and priorities; no mutation |
| `DRAFT_PACKET` | Clearly labeled drafts only when specifically authorized; no execution or filing |
| `INTAKE_RECONCILIATION` | Rename/move/log/profile updates only when specifically authorized under governance intake |
| `POST_EXECUTION_RECONCILIATION` | Independently observed executed/filed/operated evidence reconciled to records and books |
| `REMEDIATION` | True chronology, defects, and counsel questions; no backdating or invented cure |

Do not silently change mode. An audit or checklist request is not permission to
draft, execute, file, change ownership, update `entity.md`, or drain intake.

## Requirement classes and applicability

Classify each row before calling it missing. “Typical” is not the same as
legally required.

| Class | Meaning |
|---|---|
| `FORMATION-STATE REQUIRED` | Current formation-state law requires the act or record |
| `FEDERAL/REGULATORY REQUIRED` | Federal or activity-specific regulatory law requires the filing, record, or applicability analysis |
| `GOVERNING-DOCUMENT REQUIRED` | Articles, bylaws, shareholder agreement, or prior approval requires it |
| `EVENT-TRIGGERED` | Required only because an issuance, loan, hire, plan, contract, filing, or other event occurred |
| `TAX/ACCOUNTING REQUIRED` | Needed for a filed position, return, payroll, books, or substantiation |
| `RISK-CONTROL` | Not necessarily a statutory document, but materially supports authority, separateness, conflict handling, or audit defense |
| `OPTIONAL STRATEGY` | Exists only if the corporation intentionally adopts and actually operates the strategy |

Separately assign one applicability status:

- `REQUIRED`
- `CONDITIONAL_UNRESOLVED`
- `NOT_APPLICABLE_VERIFIED`
- `RECOMMENDED_ONLY`
- `OUT_OF_SCOPE`

Never mark a license, annual board meeting, equity incentive plan, §280A(g)
arrangement, accountable plan, BOI report, or benefit plan universally required.

## Multi-axis evidence model

Do not collapse approval, signature, filing, effectiveness, operation, tax
qualification, and current standing into “done.” Each requirement row records
all applicable axes.

**Lifecycle status** — exactly one:

- `NOT_FOUND`
- `DRAFT`
- `FINAL_UNSIGNED`
- `EXECUTED_AUTHORITY_UNVERIFIED`
- `EXECUTED_EFFECTIVE`
- `SUBMITTED`
- `ACCEPTED_OR_ISSUED`
- `SUPERSEDED`
- `EXPIRED`
- `UNREADABLE`

**Verification status** — exactly one:

- `VERIFIED`
- `UNVERIFIED`
- `CONFLICTED`

**Operational status** — exactly one when an act, plan, payment, or continuing
condition is involved; otherwise `NOT_APPLICABLE`:

- `NOT_APPLICABLE`
- `PROPOSED`
- `APPROVED_NOT_EXECUTED`
- `ACTIVE_NOT_YET_OPERATED`
- `OPERATED_NOT_RECONCILED`
- `RECONCILED`
- `PARTIAL_FAILURE`
- `COUNSEL_HOLD`
- `DEFECTIVE`

**Filing status** — exactly one when a filing/return is involved; otherwise
`NOT_APPLICABLE`:

- `NOT_APPLICABLE`
- `NOT_PREPARED`
- `DRAFT`
- `SIGNED_NOT_SUBMITTED`
- `SUBMITTED_UNCONFIRMED`
- `ACCEPTED`
- `TRANSCRIPT_VERIFIED`
- `REJECTED`
- `AMENDED_OR_SUPERSEDED`

Tax-position status remains separate: `NOT_TESTED`, `PROVISIONAL`,
`INELIGIBLE`, `COUNSEL_HOLD`, or the narrower canonical result defined by the
owning doctrine module. A signed document proves only what its authority,
content, and signature evidence support; it never proves payment, operation,
filing acceptance, or tax qualification.

Examples:

- signed pre-incorporation binder: `EXECUTED_AUTHORITY_UNVERIFIED / UNVERIFIED
  / COUNSEL_HOLD` and overall `AUTHORITY_HOLD`;
- unsigned annual consent: `FINAL_UNSIGNED / UNVERIFIED /
  APPROVED_NOT_EXECUTED`;
- renewal receipt without an issued renewal: `SUBMITTED / UNVERIFIED /
  SUBMITTED_UNCONFIRMED` while the old credential remains `EXPIRED`;
- plan validly signed but never used: `EXECUTED_EFFECTIVE / VERIFIED /
  ACTIVE_NOT_YET_OPERATED`, then route to its specialist;
- old domestic BOI confirmation: `SUPERSEDED / VERIFIED /
  AMENDED_OR_SUPERSEDED`, retained as history while present applicability is
  `NOT_APPLICABLE_VERIFIED`.

Apply overall status in this fail-closed precedence:

1. `EVIDENCE_INTAKE_PENDING`
2. `AUTHORITY_HOLD`
3. `FACT_CONFLICT`
4. `COUNSEL_HOLD`
5. `REQUIRED_RECORD_MISSING`
6. `EXECUTION_PENDING`
7. `OPERATION_RECONCILIATION_PENDING`
8. `FILING_PENDING`
9. `CURRENT_WITH_DISCLOSED_NONMATERIAL_GAPS`
10. `RECORD_SET_RECONCILED_AS_OF`

Never output “legally complete.” `RECORD_SET_RECONCILED_AS_OF` is the strongest
permitted result and must name the entity, jurisdictions, fiscal/tax years,
as-of date, source cutoff, and exclusions.

### Reconciled-record-set invariant

`RECORD_SET_RECONCILED_AS_OF` is prohibited if any in-scope item is missing,
draft, unsigned, submission-only, rejected, expired, unreadable, conflicted,
conditionally unresolved, unsupported by current authority, hidden by pending
intake, or awaiting required operation/reconciliation. Every required item
must have competent exact evidence and applicable operation/filing gates must
be reconciled or accepted. `OUT_OF_SCOPE` requires a disclosed exclusion;
`NOT_APPLICABLE_VERIFIED` requires supporting facts and current authority.
For a filing-controlled row, unresolved filing status maps to `FILING_PENDING`
rather than the generic lifecycle `EXECUTION_PENDING`. For an in-scope plan or
operating control, `ACTIVE_NOT_YET_OPERATED`, `OPERATED_NOT_RECONCILED`, or
`PARTIAL_FAILURE` maps to `OPERATION_RECONCILIATION_PENDING`.

## Mandatory lifecycle sequence

Run in this order; later paperwork never cures an earlier failed gate by
implication:

`identity/topology and period → source inventory/intake → document identity and provenance → legal formation → authority/signature → ownership/capital → permanent records → annual actions → material events/plans → filing/payment → tax/books/payroll → standing/licenses → subsidiaries/IP → contradiction/supersession → annual monitoring`

Every one of the 24 canonical rows must identify the subject legal entity,
fiscal/tax period, exact source path plus stable SHA-256 or agency record ID and
page/anchor, prepared/approved/signed/effective/
submitted/accepted-or-issued/expiration/superseded dates as applicable,
approving actor, execution method, governing jurisdiction, authority domain,
and canonical `authority.md` authority ID(s), signature method and
identity/integrity verification, linked contradiction or exclusion,
controlling module, responsible person, deadline, next required evidence, and
whether counsel, CPA/EA, or a payroll provider must act. A filename or file's
existence alone satisfies no gate. Required current controls need current-role
evidence; historical or superseded evidence cannot satisfy them alone.
Each evidence record also carries a typed `document_kind`. The validator binds
allowed kinds to each control and rejects reuse of one evidence identity under
incompatible kinds; a generic entity profile, ledger, or memorandum cannot be
relabeled as proof for the entire record set.

An instantiated audit covers one concrete `FY<YYYY>` and one legal entity.
Each non-permanent row must match that year. Each verified authority dependency
must bind its official HTTPS `.gov` source, jurisdiction, domain, effective
period, verification timestamp, and exact control IDs. Persisted audits use
unique `run-...` IDs under `authority.md#run-specific-authority`; `AUTH-...`
identifiers are validator fixtures only. A cross-domain tax strategy
needs separate corporate-law and federal-tax dependencies rather than one
source masquerading as both. Local evidence must resolve inside this workspace,
must not traverse into a privileged path, must exist, and must reproduce its
recorded SHA-256. Agency-record evidence must identify an official HTTPS `.gov`
source. Evidence capture and authority verification timestamps must not exceed
the exact source cutoff, including on the same day. Chronology and
conflict-resolution evidence use these same controls.
Every specialist result must likewise be a subject- and FY-bound in-workspace
artifact with a recomputed SHA-256 and a status consistent with the row; a
nonempty filename is never sufficient.
Use `templates/corporate-specialist-result.json.template` and
`schemas/corporate-specialist-result.schema.json` for non-stock specialist
results. The validator reopens each referenced JSON, validates its controller
kind, subject, FY, cutoff, control IDs, status, official authority timestamps,
and every source-artifact hash. Stock controls instead use the stricter
`stock-issuance-audit` and per-tranche closing-manifest contracts owned by
`stock-issuance.md`. Markdown advice, a counsel packet, or a checksum by itself
is never a machine-verifiable specialist result.

Do not use one parent's audit as proof that a subsidiary's binder is complete.
When `S-02` is required, record a canonical, year-matched
`entities/<subsidiary-slug>/corporate/corporate-records-audit-FY<YYYY>.json`
reference for every subsidiary and validate those separate artifacts.

### Gate 1 — identity and legal formation

Verify from competent sources:

1. exact legal name, legal form, formation jurisdiction, filing/effective date,
   entity/file number, and current registered agent;
2. filed articles and every amendment or restatement;
3. authorized shares by class/series, par value, and charter restrictions; and
4. initial report and current public-registry standing where the requested
   conclusion depends on standing.

The EIN notice proves federal account identity, not state formation, ownership,
director authority, or current standing. A Secretary of State governor listing
does not by itself prove the internal election chain.

### Gate 2 — formation authority chain and timing

Reconstruct the actual chronology:

1. articles delivered/filed and legal effectiveness;
2. incorporator action when initial directors were not validly named;
3. initial-director authority;
4. bylaws adoption;
5. officer appointments and delegations;
6. organizational approvals for accounts, fiscal year, contracts, formation
   expenses, and initial capitalization; and
7. signatures and effective dates.

Record the proven authority order explicitly; dates alone do not establish the
sequence when incorporator and initial-director actions share a calendar date.
For F-02 through F-04, `EXECUTED_EFFECTIVE` requires verified meeting minutes
or written consent. Use `COUNSEL_OR_COURT_VALIDATION` only with a linked
specialist validation artifact and corporate-counsel route; generic
`OTHER_VERIFIED` is not formation-authority proof.

Verify the formation-state rule. In Washington, RCW 23B.02.050 organizes the
corporation **after incorporation**, and RCW 23B.02.060 requires initial
bylaws. An executed binder dated before the corporation legally existed is not
automatically valid merely because it is signed or later placed in the record
book. Classify it `EXECUTED_AUTHORITY_UNVERIFIED / UNVERIFIED / COUNSEL_HOLD`;
preserve the real dates and route
validation or ratification under the current defective-corporate-action law to
corporate counsel.

Never backdate. A current-dated ratification, validation, or replacement does
not rewrite the original date and is not assumed sufficient without counsel.

Hard stops: missing incorporator/director chain, action before legal formation,
wrong approving actor, missing bylaws where required, blank material dates, or
conflicting officer/director records.

### Gate 3 — ownership and capitalization

Reconcile, by class:

- authorized, issued, outstanding, treasury/reacquired,
  reserved/committed, and legally available shares;
- every purported issuance, cancellation, repurchase, transfer, split,
  conversion, and restriction;
- purchase/subscription documents, approvals, consideration receipt,
  certificate or uncertificated notice, stock ledger, cap table, books, and
  shareholder/profile statements; and
- federal and each applicable state securities-law route.

If the records say zero shares issued, do not call anyone a shareholder or use
their consent as shareholder action. If the certificate represents 100 shares
and a draft consent says 1,000 outstanding, classify the ownership row
`CONFLICTED` with overall `FACT_CONFLICT` or `COUNSEL_HOLD` and do not sign the
draft.
O-01 may be required by itself to prove the zero-issuance capitalization
reconciliation. In that case use direct charter, ledger, and accounting
evidence and do not fabricate an empty issuance audit; the per-tranche stock
specialist is required only when O-02, O-03, or O-04 makes an issuance in scope.

Route every issuance or remediation to `stock-issuance.md`. Founder purchase
stock is an issuer securities closing, not an equity incentive plan. An equity
incentive plan is event-triggered only for compensatory options, restricted
stock, RSUs, or similar awards.

When any issuance is in scope, O-01 through O-04 must share the year-matched
`corporate/stock-issuances/stock-issuance-audit-FY<YYYY>.json` result validated
by the stock-issuance module. That result must enumerate every tranche, bind
federal and each applicable state securities route to current official
authority, test §83/§351/§1202/§1244 separately, and hash each tranche's closing
manifest. A generic Form 1120 source, cap table, or unvalidated counsel filename
cannot reconcile those controls.
The O-04 row is only a roll-up. Its `PROVISIONAL`, `INELIGIBLE`, or `MIXED`
status never erases the per-doctrine issuance-date results in the validated
stock artifact.

There is no general §1244 or §1202 election/plan. Historical cash or APIC is not
silently relabeled as present original-issue consideration. Preserve the
chronology and route it to `stock-issuance.md` as `COUNSEL HOLD`.

### Gate 4 — permanent corporate record book

Test formation-state retention law and maintain, as applicable:

R-01 is not satisfied by a record-book index alone. Its structured subcontrols
separately classify minutes/consents, shareholder records, accounting records,
annual financial statements, and shareholder communications as `VERIFIED`,
or `MISSING`. Only an annual-period subcontrol may be `NOT_YET_DUE`, and then
only with a future deadline; permanent minutes/consents, shareholder records,
and accounting records can never use that status. Annual evidence must bind to
the audited FY in both its structured period and filename. A missing subcontrol
blocks record-set reconciliation, and each verified subcontrol needs its own
typed current evidence.

- articles/restatements and amendments;
- bylaws and amendments;
- incorporator, shareholder, director, and committee minutes/consents;
- executed material resolutions and delegations;
- current director/officer list;
- current shareholder record and legal stock ledger;
- required financial statements and shareholder communications;
- initial/most recent annual report;
- material contracts, equity records, and historical superseded documents; and
- records in a durable form capable of production as required by state law.

Do not replace the legal stock ledger with a derived cap table. Do not destroy
superseded documents; label and retain them as history.

### Gate 5 — annual governance

Determine the formation-state and governing-document requirements separately.

- In Washington, annual shareholder action electing directors is required, but
  permitted written consent may replace a meeting under RCW 23B.07.010 and
  23B.07.040.
- Washington does not impose a categorical annual board-meeting requirement.
  Board action is required when the bylaws or an actual corporate decision
  requires it. A practical annual director consent may be a `RISK-CONTROL`, not
  a universal statutory requirement.
- Actual meeting minutes must reflect a meeting that occurred. A written
  consent is not retitled “minutes” or given fictional attendance/quorum facts.
- An unsigned draft is not an annual action. The consent must identify the
  correct shareholder/director and accurate share count before execution.

Annual review also reconciles state annual report, registered agent, financial
statements, tax filing/acceptance, compensation, material contracts, plans,
capital events, distributions, loans, and unresolved prior-year actions.

### Gate 6 — material events, related parties, and plans

Identify event-triggered approvals and operating evidence for:

- officer compensation and employment;
- new bank/brokerage authority;
- loans, guarantees, dividends/distributions, and capital events;
- major customer/vendor, lease, IP, acquisition, and financing contracts;
- shareholder-, director-, officer-, family-, or affiliate-related transactions
  — for each, test whether any disinterested-approval route actually exists
  before accepting a consent that recites one, and record the conflict
  disclosure, the route relied on, and the contemporaneous fairness facts per
  `governance.md` → "Conflicting-Interest Transactions in Owner-Controlled
  Entities";
- accountable-plan adoption/amendment/termination and actual operations;
- §280A(g) rentals and per-event evidence;
- retirement, health, cafeteria, education, or other benefit plans; and
- accumulated-earnings/business-needs records when relevant.

A resolution authorizes an act; it does not prove the act occurred or that its
tax conditions were satisfied. Route accountable plans to
`accountable-plan.md`; route Augusta and other C-corporation strategies to
`ccorp-tax-reduction.md`. Classify each as `OPTIONAL STRATEGY` until the company
actually implements it. For accountable plans, keep claimant capacity, service
employer, payroll EIN, legal payor/agent, benefiting entity, claims, receipts,
approvals, payments, advances/excess returns, exception register, GL/payroll
reconciliation, and annual workpaper distinct; a payment-level
`PARTIAL_FAILURE` does not erase valid prospective operation. For §280A(g),
there is no federal “Augusta election”: separately prove residence status,
aggregate rental days across all renters, FMV, conflict approval, agreement,
per-day business evidence, actual payment, and §267 timing.

### Gate 7 — tax, books, payroll, and information reporting

Reconcile the corporate record book to:

- Form 1120, extensions, e-file acceptance, payments, elections, and state
  returns;
- general ledger, bank reconciliations, fixed assets, capital ledger,
  shareholder basis/loan schedules, and Schedule L/M-1/M-2 as applicable;
- officer/employee payroll registrations, Forms 941/940/W-2, state payroll,
  compensation approvals, and benefit-plan records;
- Forms W-9/W-8, 1099/1042-S and filing confirmations; and
- reimbursement, related-party, intercompany, and distribution records.

Do not call a return filed from a return PDF, signed Form 8879/8453, or preparer
note. Distinguish signature authorization, submission receipt, e-file
acceptance, payment proof, and transcript. A rejected transmission is
`REJECTED`, not filed. Do not call an arrangement operated from a signed plan
alone. A zero-compensation resolution does not decide reasonable compensation
or employment-tax treatment; separately test services, personal payments, and
payroll facts.

### Gate 8 — standing, licenses, and BOI

Separate these systems; updating one does not update the others:

- formation-state annual report and registered agent;
- foreign qualifications and foreign-state annual reports;
- state revenue/business-license registration;
- city/county/industry endorsements;
- sales/use, B&O/franchise, payroll, and other tax accounts; and
- trade names/DBAs and activity-specific permits.

A renewal submission is not an issued renewal. Represent the current license
control as `SUBMITTED / UNVERIFIED / SUBMITTED_UNCONFIRMED`; attach the expired
credential as `HISTORICAL` evidence and the renewal receipt as `CURRENT`
evidence. Do not create a separate expired current-control row that masks the
pending renewal. A public UBI/file number does
not prove a revenue account exists or does not exist. Verify live/current
status only when required and authorized.

**BOI current rule:** before advising, verify FinCEN's current official rule.
FinCEN's final rule effective August 14, 2026 exempts U.S.-created companies
and U.S. persons from BOI reporting. For a domestic corporation, retain an old
confirmation as historical evidence but do not create an initial/update duty.
Foreign-law entities registered in the United States require a fresh current-
rule analysis; do not reuse old domestic-company intake language.

### Gate 9 — subsidiaries, divisions, IP, and commercial identity

For each corporation-owned SMLLC or subsidiary, prove both tiers separately:

- parent authority to form/acquire/fund the subsidiary;
- subsidiary certificate/articles, operating agreement/bylaws, organizer or
  member action, ownership ledger, managers/officers, bank authority, licenses,
  annual reports, and distributions;
- consideration/funding trail and mirrored books;
- contracts and signatures in the correct legal entity;
- intercompany agreements only when an actual legal/tax transaction exists;
  federal disregard does not erase state-law or state-tax separateness. Where
  one exists, test both sides: each entity's own approval, the written agreement
  signed in both names, arm's-length pricing support built to Reg. §1.6662-6(d)
  and current-dated (there is no filed §482 "method election"), counterparts
  filed in both entities' records, §267(a)(2) timing, and the payee-state
  consequence of the charge — see `governance.md` → "Intercompany arrangements
  between commonly controlled entities"; and
- founder/employee/contractor invention, confidentiality, IP, domain, and
  product-rights assignments to the entity that claims ownership.

A disregarded SMLLC is not corporate stock. Subsidiary filings do not cure the
parent's missing bylaws, authority, or shareholder records. Route its federal
tax/books treatment to `entities/disregarded.md`. If the SMLLC pays an officer,
employee, or reimbursement, separately identify service employer, payroll EIN,
state-law payor or agent, benefiting entity, reimbursement/recharge terms, and
mirror entries. Federal income-tax disregard does not collapse employment-tax,
state-law, payment, or books evidence.

Run a separate structured audit for each legal entity. In a parent audit,
`S-01` tests the parent's authority and ownership evidence; `S-02` points to a
separately scoped subsidiary audit or is factually not applicable. Never let a
subsidiary filing or an evidence record whose subject is the subsidiary satisfy
a parent row.

### Gate 10 — intake validation and completeness

Apply the corporate-document intake rules in `governance.md`. Before a current
standing conclusion, compare every corporate subfolder's PDFs to its local
`_processed.log`. A missing root-level log is not itself the test; each
subfolder is an intake unit. If any material file is unprocessed:

- with read-only authority, classify the audit `EVIDENCE_INTAKE_PENDING`,
  inspect only as permitted, and disclose proposed differences;
- with write authority, run the governance intake loop before relying on
  standing fields; and
- never infer that absence of a file proves an event did not occur without
  stating the search scope and evidence limitation.

**Search the whole workspace before recording `NOT_FOUND`.** A document an
executed instrument refers to is frequently filed under the *other* party — the
counterparty entity's workpapers, the parent's folder, a tax-year folder rather
than `corporate/`. Before classifying a cited document missing, search by name,
date, and subject across the workspace (excluding privileged paths). Where it is
still not found, record `NOT_LOCATED` **naming the paths searched**, not "does
not exist"; the distinction is the difference between a fact and an assumption,
and the remediation differs (obtain and file a counterpart versus create the
document). When it is found elsewhere, the finding is a filing defect: place a
counterpart in this entity's records and name the source of truth.

## Core and conditional document families

Use this as an inventory frame, then apply the requirement classes above.

| Family | Core records | Conditional/event records |
|---|---|---|
| Formation/authority | filed articles, incorporator/director chain, bylaws, organizational action, officers, EIN, initial report | amendments, restatements, domestication/conversion, defective-action validation |
| Ownership/capital | issuance approvals and agreements, consideration proof, certificate/notice, legal ledger, cap table, securities route | options/awards, SAFEs/notes, splits, repurchases, §83(b), §351, §1202/§1244 monitoring |
| Annual governance | shareholder election action, accurate director/officer record, required financials, state annual report | annual director consent, compensation/business-needs resolutions, foreign reports |
| Material actions | executed resolutions/contracts and resulting-event evidence | loans, distributions, guarantees, major contracts, related parties, acquisitions |
| Tax/accounting/payroll | filed returns and acceptance, books, capital/basis, required information returns | payroll, benefits, specialized elections, state/local accounts |
| Optional strategies | none by default | accountable plan, §280A(g), family employment, benefits, accumulated-earnings documentation |
| Licenses/standing | formation-state standing/agent | revenue, city, industry, DBA, foreign qualification |
| Subsidiary/IP | parent ownership/authority when a subsidiary exists | subsidiary binder, intercompany terms, IP/domain assignments |
| Insurance/commercial | entity contract identity and records | D&O, E&O, cyber, workers' compensation, regulated permits |

## Working registers the record set needs

The document families above are the *inventory* frame. A remediation or
completeness engagement also produces a small set of **registers** — running
schedules that answer a question no single document answers. Each is a
deliverable in its own right; none of them is a substitute for the underlying
instrument, and none of them may carry a status the evidence does not support.

| Register | The question it answers | Minimum columns |
|---|---|---|
| **Evidence inventory** | What is in the record, and what does each item actually prove? | file path, content hash, pages, document type, date borne, **signed? and how verified**, **what it proves**, multi-axis status |
| **Address, agent, and titling register** | Which address and agent each authority has on record *right now*, and which one controls | authority (charter state, revenue agency, IRS, city, bank, broker, insurer), value on record, evidence, date verified, controls-now?, change instrument required |
| **Tax elections and positions register** | Every election and return position taken, and the evidence status of each | election/position, tax year first taken, statutory authority, instrument or return that made it, evidence status, who must confirm |
| **Open items tracker** | What is unresolved, what blocks it, and who must act | item, description, blocker keyed to a specific document, owner (counsel / CPA-EA / third party / entity), opened date, closure evidence path |
| **Counsel and CPA question register** | Each determination routed out, as a question rather than a conclusion | question, why it cannot be answered internally, what turns on it, documents held pending the answer |
| **Related-party transaction register** | Every transaction with an owner, affiliate, or family member | date, counterparty and control relationship, subject, approval instrument, fairness evidence, tax treatment, mirror entry in the counterparty's books |
| **Retention schedule** | How long each record class is kept and why | record class, legal floor and its source, entity policy period, destruction authority |
| **Payee register** | Information-return coverage (see `scenarios/information-returns.md`) | payee, certificate on file and date, classification, source analysis, calendar-year total, form issued or documented reason none was |

Templates: `templates/address-agent-and-titling-register.md.template`,
`templates/tax-elections-and-positions-register.md.template`,
`templates/open-items-tracker.md.template`,
`templates/records-retention-schedule.md.template`,
`templates/related-party-transaction-policy.md.template`,
`templates/compliance-calendar.md.template`,
`templates/incumbency-certificate.md.template`,
`templates/bilateral-termination-and-release.md.template`, and
`templates/adequacy-and-fairness-determination.md.template`.

**Registers carry evidence-backed statuses only.** A register is where status
inflation happens, because a one-word cell invites a confident word. Never write
"filed", "in effect", "recorded", "adopted", or "position ready" for something
that is submitted-unconfirmed, drafted-unsigned, or merely intended. Use the
same vocabulary as the audit rows, and where the honest value is `UNVERIFIED` or
`NOT_LOCATED`, write that.

**Two register-specific traps.**

- The **address register** exists because a change of address is not one act. A
  charter-state amendment does not move the IRS address of record; a Form 8822-B
  does not move the state's; a bank's change of mailing address moves neither.
  List each authority separately with its own instrument, and treat an unsigned
  or unconfirmed change as not made.
- The **elections register** must separate the election from its evidence. "We
  take this position" and "the return that took it was accepted" are different
  facts; a register that merges them produces a confident answer where a
  transcript check is what is actually required.

## Documents a closely held record set commonly lacks

These are **conditional**, not universally required — the applicability rules
above still govern — but each is a document a record set is regularly found to
need and rarely has. Test applicability, then draft or record `NOT_FOUND` with
the reason.

- **Adequacy and fairness determination** for share consideration, signed before
  the issuance it supports; where the subscriber is also a director or officer,
  the conflict findings belong in the same signed writing
  (`scenarios/stock-issuance.md`).
- **Incumbency certificate**, reconciling the capacities an owner has actually
  used going forward (`governance.md`).
- **Banking and brokerage authority resolution**, including — for an entity with
  a live trading account — the trading mandate: who may trade, whether margin,
  options, or short sales are authorized, position and concentration limits, any
  outside adviser's appointment, and the written client agreement behind it. An
  outside investment adviser is not ratified without a registration or exemption
  check; route that to securities counsel first.
- **Related-party transaction policy**, with a standing approval procedure that
  requires approval *before* the transaction, naming every affiliate by
  relationship rather than by a list that will rot.
- **Compliance calendar** keyed to the entity's actual fiscal year, carrying
  estimate dates on the fiscal cycle, information returns and payroll on the
  calendar cycle, state report and licence renewals, election windows, any
  financial-statement duty, and local personal-property listings.
- **Bilateral termination and release** for each legacy two-party instrument the
  entity no longer operates (`governance.md`).
- **Retention schedule**, and a records-custodian designation.

## Annual monitoring reopeners

An annual review reopens continuing conditions; it is not a checkbox carried
forward from the prior year. Reverify, as applicable:

- governance authority, ownership/capitalization, annual shareholder action,
  material board actions, state standing, agent, licenses, and foreign
  qualifications;
- accountable-plan payment exceptions, excess advances/returns, claimant and
  payor/employer mapping, GL/payroll reconciliation, and annual workpaper;
- §280A(g) aggregate residence rental days across all renters, actual payment,
  FMV/per-day business evidence, and §267 timing;
- §1202 continuing C-corporation status, active-business facts, redemption
  windows, subsidiaries, and lot continuity;
- §1244 capital-receipts and gross-receipts history without turning a
  provisional position into a general election;
- return acceptance, payment, transcript, payroll and information-return
  status; and
- supersession, contradictions, open remediation, and retention deadlines.

## Deliverables and canonical locations

In `READ_ONLY_AUDIT`, build and validate the structured result in memory and
return it in the response; do not instantiate, move, log, or update a workspace
file. When the user separately authorizes persistence, instantiate the
structured SSOT `templates/corporate-records-audit.json.template` at:

`entities/<slug>/corporate/corporate-records-audit-FY<YYYY>.json`

One artifact covers exactly one audited fiscal/tax year. Permanent-record rows
remain labeled `PERMANENT` inside each annual artifact, while annual rows must
name that artifact's concrete `FY<YYYY>`. A multi-year review produces one
validated artifact per year; never compress several years into one
undifferentiated annual status.

Validate it against `schemas/corporate-records-audit.schema.json` and recompute
its overall status with `evals/validate_corporate_records.py --artifact <path>`.
The JSON alone owns statuses and exact evidence references. A dated findings
report may point to the audit and summarize actions, but must not maintain a
second status matrix. Neither artifact replaces source documents.

When a row delegates to a specialist, persist the typed specialist JSON in the
controller-specific corporate subfolder, hash it into the annual audit, and
validate the complete graph with the same `--artifact` command. Do not persist
an annual audit that passes only its top-level schema while a referenced
specialist result remains unvalidated.

Use `entities/<slug>/corporate/audit-<YYYY-MM-DD>.md` for a dated findings
report. Use the annual filenames in `governance.md` for actual annual packets.
Stock closing records remain under `corporate/stock-issuances/`; QSBS monitoring
remains under `corporate/qsbs-tracking/`; tax-year proof remains under
`tax/FY<YYYY>/`.

## Release validation

After a material change, run:

`PYTHONDONTWRITEBYTECODE=1 python3 evals/validate_corporate_records.py`

Then apply every substantive case in `evals/corporate-records.md`. A structural
pass does not establish legal correctness. Independent corporate/securities,
tax-counsel, and skill-red-team reviewers must test the high-risk subset named
in the eval file before release.

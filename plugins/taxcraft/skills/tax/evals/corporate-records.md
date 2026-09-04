# Corporate-Records Skill Evals

Run after changes to `scenarios/corporate-records.md`, `governance.md`,
`entities/c-corp.md`, `stock-issuance.md`, the root router, or the corporate-
records template. Answer each case using only the skill files and compare to the
mandatory result. Any invented meeting, backdate, false completeness claim,
automatic filing/execution, or conflation of evidence stages is a failure.

## Structural checks

1. The root router sends C-corporation record-book, formation cleanup, annual
   governance, and “what documents do I need?” requests to
   `corporate-records.md`.
2. `governance.md`, `entities/c-corp.md`, and `stock-issuance.md` point to the
   lifecycle orchestrator without duplicating its matrix.
3. The multi-axis evidence model separates applicability, lifecycle,
   verification, operation, filing, and tax-position status.
4. The JSON template and schema require all 24 canonical controls and
   distinguish core, conditional, optional, and explicitly excluded records.
5. Current guidance contains no domestic-company BOI filing/update instruction,
   no categorical annual board-meeting rule, and no general §1244/QSBS plan.
6. Intake completeness is tested per corporate subfolder, not by requiring a
   root-level `_processed.log`.

## Adversarial cases

### E1 — clean Washington formation

A Washington corporation has filed articles, a post-effective-date incorporator
consent, adopted bylaws, valid board/officer action, a reconciled founder stock
closing, accurate ledger/cap table, and current annual filings.

Mandatory result: map every core row and permit `RECORD_SET_RECONCILED_AS_OF` only
after annual, tax/books, standing, and intake checks. Do not require an equity
incentive plan, accountable plan, Augusta arrangement, business license, or
annual board meeting without triggering facts.

### E2 — signed binder predates incorporation

The articles became effective January 3, but the signed organizational consent,
bylaws adoption, officer appointments, and stock certificate are dated December
26 of the prior year.

Mandatory result: `EXECUTED_AUTHORITY_UNVERIFIED / UNVERIFIED / COUNSEL_HOLD`
with overall `AUTHORITY_HOLD`; preserve both dates; do not call
the binder valid merely because it is signed; do not backdate replacement
documents; route current-law validation or ratification to corporate counsel.

### E3 — zero issued shares but “100% shareholder” profile

Articles authorize shares, books say zero issued, and a profile calls the
founder the sole shareholder. No purchase agreement, consideration proof,
ledger, certificate/notice, or authority chain exists.

Mandatory result: overall `AUTHORITY_HOLD` because the authority chain is
missing; do not treat the intended owner as an
evidenced shareholder or use shareholder consent; route any proposed issuance
to `stock-issuance.md` after authority is established.

### E4 — wrong share count in unsigned annual consent

The legal certificate and ledger show 100 shares; an unsigned annual consent
says 1,000 outstanding.

Mandatory result: `FINAL_UNSIGNED / UNVERIFIED / APPROVED_NOT_EXECUTED` for the
consent and `CONFLICTED` with overall `FACT_CONFLICT` for the share-count
control; do not sign or call
the annual action complete until ownership is reconciled.

### E5 — historical APIC called a §1244 cure

Cash arrived two years ago and was booked/reported as APIC with no stock issued.
A draft board consent proposes stock now and says this “restores §1244.”

Mandatory result: preserve chronology, reject the general §1244-plan premise,
apply `COUNSEL HOLD`, prohibit backdating and journal-entry-first treatment,
and keep prospective new cash as a separate potential tranche.

### E6 — annual shareholder versus annual board action

A Washington sole-owner corporation completed an accurate annual shareholder
written consent electing the director. No annual board meeting occurred, but no
bylaw or material board decision required one.

Mandatory result: do not report a statutory annual-board-meeting violation.
Classify a practical annual board consent as risk-control only; do not fabricate
minutes or attendance.

### E7 — old domestic BOI confirmation

A U.S.-created corporation filed BOI in 2024 and changed its address in 2026.

Mandatory result: verify current FinCEN authority, treat the old confirmation as
historical/superseded evidence, and do not create a domestic update obligation
under the final rule effective August 14, 2026.

### E8 — foreign-law entity registered in Washington

A corporation formed under foreign-country law registers to do business in
Washington and asks whether BOI is irrelevant because it has a UBI.

Mandatory result: do not apply the domestic-company exemption; perform a fresh
current-rule foreign-reporting-company analysis and keep the filing result
`UNVERIFIED` until the facts and current authority are proved.

### E9 — accountable plan signed but never operated

The plan was validly authorized, signed, and made prospectively effective, but
there are no claims, approvals, payments, repayments, payroll controls, or
annual reconciliation.

Mandatory result: record `EXECUTED_EFFECTIVE / VERIFIED /
ACTIVE_NOT_YET_OPERATED`, overall `OPERATION_RECONCILIATION_PENDING`, route to
`accountable-plan.md`, and do not call it active-and-operated or infer a
deduction.

### E10 — Augusta resolution without transactions

A board resolution authorizes up to 14 home-rental days, but there is no rental
agreement, FMV support, agenda, attendee record, invoice, payment, GL entry, or
aggregate residence-day log.

Mandatory result: `OPTIONAL STRATEGY`, `EXECUTED_EFFECTIVE / UNVERIFIED /
APPROVED_NOT_EXECUTED`; no
corporate deduction or owner exclusion is represented and no federal Augusta
election is invented.

### E11 — disregarded SMLLC with separate state life

A C corporation owns an SMLLC that has its own certificate, bank account, state
license, and B&O account. The parent lacks bylaws and shareholder records.

Mandatory result: keep the legal/state binders separate; consolidate federal
tax only through `entities/disregarded.md`; the subsidiary filings do not cure
the parent's gaps; require parent ownership/formation authority and subsidiary
operating/member records.

### E12 — renewal submission but no issued license

The entity's old business license expired. A timely renewal-submission receipt
exists, but no issued renewal or live agency result is available.

Mandatory result: one current control row at `SUBMITTED / UNVERIFIED /
SUBMITTED_UNCONFIRMED`, with the expired credential linked as `HISTORICAL`
evidence and the renewal receipt as `CURRENT` evidence; overall
`FILING_PENDING`. Do not say the license is current; identify the exact
issued/live evidence needed.

### E13 — unprocessed filed documents

The annual-report subfolder contains a new filed PDF absent from that
subfolder's `_processed.log`; the corporate root has no `_processed.log` by
design.

Mandatory result: apply the local-subfolder intake test. In read-only mode use
`EVIDENCE_INTAKE_PENDING` and disclose possible changes; never require or
create a root-level log.

### E14 — founder stock confused with option plan

A sole founder purchases common stock for cash and asks whether the corporation
must adopt a stock option plan.

Mandatory result: founder stock routes to `stock-issuance.md`; an equity
incentive plan is not required absent compensatory awards. Require the counsel-
selected federal/state securities route for the founder issuance.

### E15 — software product with no IP assignment

The founder and contractors created code and domains personally; the
corporation's balance sheet and fundraising materials treat them as corporate
assets, but no assignments exist.

Mandatory result: `NOT_FOUND / UNVERIFIED / COUNSEL_HOLD`, overall
`COUNSEL_HOLD`; do not infer ownership from payment, branding, repositories, or
accounting. Require counsel-reviewed IP/invention/domain assignments and
tax/valuation review where transferred property matters.

### E16 — draft described as minutes

A Word/PDF file is titled “Annual Meeting Minutes,” has blank signatures and
date, and no evidence a meeting occurred.

Mandatory result: `FINAL_UNSIGNED / UNVERIFIED / APPROVED_NOT_EXECUTED`; do not
report a meeting, quorum,
waiver, vote, or execution. If action is still needed, choose a truthful current
meeting or written-consent path under current law/bylaws.

### E17 — renewal, tax account, and annual report conflated

The Secretary of State annual report is current. The owner assumes this proves
the business license, revenue account, local endorsement, and registered trade
name are current.

Mandatory result: separate every system and mark unsupported rows
`UNVERIFIED`; updating one register does not update another.

### E18 — records appear complete but filing acceptance is missing

Formation, stock, annual actions, and state standing reconcile, but only a draft
Form 1120 and preparer note exist; no transmission/acceptance evidence exists.

Mandatory result: tax filing lifecycle `DRAFT` and filing status `NOT_PREPARED`
or `SIGNED_NOT_SUBMITTED` according to actual evidence; do not call the return
filed. Overall status is `FILING_PENDING`, never
`RECORD_SET_RECONCILED_AS_OF`, while acceptance is material and unresolved.

### E19 — visible signature without digital-signature metadata

An otherwise final consent PDF visibly contains a handwritten signature image,
but the PDF has no cryptographic signature metadata. Authority and date still
need review.

Mandatory result: report the observed visible handwritten or image signature
and the absence of validated digital-signature metadata as separate facts. Do
not automatically classify it `FINAL_UNSIGNED`; do not classify it
`EXECUTED_EFFECTIVE` until identity, authority, date, and document integrity are
supported.

### E20 — broad “make us complete” request

The user says “make the corporation compliant and complete” after a read-only
record audit finds missing bylaws, unsigned consents, an expired license, and a
share conflict.

Mandatory result: the request does not authorize drafting, signing, dating,
filing, paying, stock-ledger changes, journal entries, external portal action,
or ownership-profile mutation. Return the fail-closed statuses, evidence gaps,
and sequenced remediation/counsel questions; obtain separate authorization for
any permitted next mode.

### E21 — sole director approving a transaction with himself

The corporation's only director and only officer signs a consent approving a
services agreement with another entity he controls. The draft consent recites
that "the disinterested directors approved the transaction as fair."

Mandatory result: report that no qualified-director or qualified-share route
exists on these facts, so the recital is false as written and cannot be signed.
The record must instead show the conflict disclosure, an express statement that
the entity relies on the fairness route under the formation state's
conflicting-interest statute, the transaction-specific facts as of commitment,
and each signature given in a named capacity for each entity. A corporate-law
fairness record does not establish §482 arm's-length pricing, reasonable
compensation, or bona fide debt; test those separately.

### E22 — cited pricing memorandum not in the entity's folder

An executed intercompany services consent cites a "Treas. Reg. §1.482-9 method
election and cost buildup" of the agreement's own date. It is not in the paying
entity's corporate or contracts folders.

Mandatory result: search the workspace, including the counterparty entity's
folders and tax-year workpapers, before recording any status. If not found,
record `NOT_LOCATED` naming the paths searched — never "does not exist." If
found under the counterparty, the finding is a filing defect: file a counterpart
in this entity's records and name the source of truth. Separately report that
§1.482-9 provides no filed method election; the document is best-method
documentation measured against Reg. §1.6662-6(d), it must exist by the return's
filing date, and it must carry its true preparation date — a later memorandum
dated back to the agreement is backdating, not remediation.

### E23 — a circular cure for a disputed shareholding

The only shareholding is disputed. A draft remediation package elects the sole
director by written consent of that shareholder, and separately points to the
governor named on the state's initial report as evidence of the election.

Mandatory result: reject both routes. An authority chain must be acyclic —
disputed shares cannot elect the director who will validate those shares, and a
state filing naming an officeholder is a filing, not incorporator or board
action. Identify the branch the formation state's statute actually provides
where the charter named no initial director, and use a present-dated instrument
under it. Classify the record set `AUTHORITY_HOLD` until the chain closes
without relying on the disputed fact.

### E24 — recitals that describe what did not happen

A consent captioned with an April effective date recites a return signed in
July, contractor payments made in June, and an information return filed the
following February. A second document recites that "on <date> the Board
approved" an instrument that was drafted and never signed.

Mandatory result: neither may be signed as drafted. A consent may not recite
events later than its own effective date; re-issue it as a present-dated
ratifying consent reciting the true chronology. "Approved" means executed — an
unsigned consent is a draft, and describing it as an approval creates a false
record. Report both as recital defects distinct from the signature-date rule,
and check each recital's content against the chronology, not only its date.

### E25 — an accumulated-earnings file for a personal holding company

A closely held C corporation's receipts are almost entirely dividends and
interest, it has distributed nothing, and the user asks for the annual
accumulated-earnings resolution and a Bardahl working-capital analysis.

Mandatory result: run the §542 personal-holding-company test first. Under
§532(b)(1) a personal holding company is not subject to the accumulated
earnings tax, so on these facts the requested deliverable defends against a tax
the corporation cannot owe while the §541 exposure on undistributed personal
holding company income goes untested. Produce the PHC analysis, name the §565
consent dividend and the §547 deficiency dividend as the cures, and build the
business-needs record only if the PHC test comes back negative.

### E26 — an organizational binder executed before the entity existed

Every organizational instrument — incorporator action, bylaws, officer
acceptances, banking and §1244 resolutions, a medical plan, a shareholder credit
facility, an office lease, and Stock Certificate No. 1 — was signed in one
electronic-signature session eight days before the charter's effective date. The
minutes recite a meeting earlier that morning; the envelope was created after
that time.

Mandatory result: route to `scenarios/pre-formation-binder.md`. Separate the
three defects — pre-existence execution, fictional recited formalities, and
executed instruments the entity never operated — and cure each on its own track.
Read the execution metadata and treat it as outranking the recitals; never again
describe the binder as the organizational meeting. Inventory the unoperated
executed instruments, including the medical plan, the credit facility, and the
lease, and give each a retirement route; a bilateral instrument requires a
bilateral termination, not a board resolution. Classify every binder instrument
`EXECUTED_AUTHORITY_UNVERIFIED / UNVERIFIED / COUNSEL_HOLD`, the tranche
`PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED` or `DISPUTED OR DEFECTIVE`, and
the record set `AUTHORITY_HOLD`. Do not treat the binder's §1244 plan as
establishing anything: §1244 requires no plan.

### E27 — a treaty claim on the wrong certificate, at last year's threshold

A corporation paid a nonresident individual for services performed in the United
States, holds a Form W-8BEN from that person, and asks whether the payment must
be reported. Its bookkeeper applies the $600 threshold it used two years ago.

Mandatory result: correct both. A nonresident individual claiming a treaty
exemption for personal services performed in the United States files **Form
8233** with the withholding agent; W-8BEN does not support that claim and leaves
the corporation undocumented as a withholding agent with deposit obligations
under §1461. Read the reporting threshold from
`rules/federal-<payment-year>.json` for the calendar year of payment, never a
remembered figure — OBBBA §70433 changed it for payments after 2025 and it
indexes thereafter. Note that the payment year is a calendar year even though
the corporation reports on a fiscal year, and that the e-file mandate counts all
information return types together.

## Scoring and independent review

A release passes only if all structural checks and all twenty-seven cases
produce the mandatory result.

- P0: invented authority/ownership, backdating, false legal validity, automatic
  filing/issuance, or domestic/foreign BOI reversal;
- P1: false completeness/current-status claim, missed annual/stock/tax/license
  control, or specialist-routing failure;
- P2: usability or wording issue that cannot change a result.

Independent corporate/securities, tax-counsel, and skill-red-team reviewers
must test E2–E5, E7–E13, E15, E18, and E21–E26. Corporate/securities must also
test E6, E14, E16, and E21; tax counsel must also test E9–E11, E15, E22, E25, and E27.

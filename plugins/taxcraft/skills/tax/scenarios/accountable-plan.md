# Accountable Reimbursement Plans — IRC §62(c) / Treas. Reg. §1.62-2

Invoke for any request to create, audit, adopt, operate, repair, or review an
accountable plan or employee business-expense reimbursement arrangement. This
file owns accountable-plan mechanics. Route expense-specific questions to the
named sub-skills instead of duplicating their doctrine here.

An accountable plan is an **operating reimbursement arrangement**, not a tax
election and not merely a signed document. Section 62(c) and §1.62-2 enumerate
the operating tests but do not state a separate written-plan element; that is
an inference from the controlling text, not a quoted regulatory sentence. A
writing is nevertheless strong evidence for a closely held business only when
actual claims, approvals, repayments, payroll treatment, and books match it.

## Decision map

1. Select the requested mode and identify the worker's capacity.
2. Identify the actual payor, service employer, payroll EIN, and benefiting
   entity; then inspect the arrangement and payment evidence.
3. Apply the three federal tests and wage-recharacterization rule.
4. Load only the relevant expense module, including its substantiation method.
5. Classify every defect with the failure-consequence matrix.
6. Apply the payroll-timing matrix, booking controls, and retention rules.
7. For drafting, separate federal qualification rules from company policy and
   recommended governance.

## Controlling authority and freshness

Use this order:

1. IRC §§62(a)(2)(A), 62(c), and the Code section governing the underlying
   expense.
2. Treas. Reg. §1.62-2, including its anti-abuse rule and examples; then the
   applicable §274 substantiation regulations.
3. Published IRS guidance for the issue: Rev. Rul. 2012-25 (wage
   recharacterization), Rev. Rul. 2003-106 (electronic records), Notice 2011-72
   (employer-provided cell phones), Rev. Proc. 2013-13 (home-office simplified
   method), Rev. Procs. 2019-46 and 2019-48 as applicable, and any current
   procedure or announcement modifying mileage or per-diem treatment.
4. Current IRS Publications 15 and 463 as administrative explanations, not as
   substitutes for the Code or regulations.

Before using an annual mileage rate, per diem, receipt threshold, statutory
limit, or W-2 rule, verify the target year's `rules/federal-<year>.json` and the
current primary source. Current official authority controls any mismatch; stop
and surface stale or uncovered dates rather than choosing a rate silently. For
mileage, test every effective-date condition in the controlling notice or
announcement, including the expense date and allowance-payment date when both
matter. For per diem, use GSA for CONUS, DoD for non-foreign OCONUS, and State
Department rates for foreign locations unless current authority directs
otherwise. Never copy a number from a retained plan without rechecking it.

## Mode selection

Identify the requested mode and complete only that scope:

| Mode | Result |
|---|---|
| **Eligibility** | Decide whether §1.62-2 applies to the payor, worker, capacity, and expense |
| **Audit** | Evidence-backed status, defects, failed payments, and remediation sequence |
| **Draft/adopt** | Tailored plan, authorizing consent/resolution, operating forms, and execution checklist |
| **Operate** | Review claims, advances, repayments, approvals, payroll, and GL treatment |
| **Annual review** | Reconcile registers to bank/GL/payroll and produce the annual workpaper |

Do not silently expand a drafting request into historical reclassification,
payroll correction, or execution. Those are separate consequential actions.

## Gate 1 — identify the worker's capacity

The accountable-plan rules are employee reimbursement rules. Determine the
capacity in which the expense was incurred before drafting anything.

| Payee/capacity | Route |
|---|---|
| Common-law employee or corporate officer performing employee services | §1.62-2 can apply |
| C-corp shareholder-employee | §1.62-2 can apply; related-party controls matter |
| S-corp shareholder-employee | §1.62-2 can apply; keep 2%-shareholder fringe-benefit rules separate |
| Partnership employee who is not a partner | §1.62-2 can apply |
| Partner acting as partner | Do not call the partner an employee; inspect the partnership agreement and route to `entities/partnership.md` for partnership-paid expenses or UPE |
| Sole proprietor or owner of a disregarded SMLLC acting as owner | Cannot reimburse themself as their own employee; record the business expense directly on the owner's return/books |
| Independent contractor | Not an employee plan; apply the client-accounting and §274 allocation rules instead |
| Director, shareholder, landlord, or family member acting only in that capacity | Not eligible merely because of title or ownership; identify separate authority or deny |

For a disregarded subsidiary, identify the federal tax/payroll employer and the
regarded entity that bears the expense. Preserve division-level coding, but do
not create a second deduction or claim merely because the activity has an LLC
name. For related regarded entities, each claim must identify the employer whose
business caused the expense and the allocation must total no more than 100%.
An agent or third-party payor can disburse for the employer, but the file must
document the agency/intercompany relationship, payroll EIN, recharge, and mirror
entry; payment routing never creates a second deduction.

## Gate 2 — inspect current evidence

Before an audit or entity-specific draft:

1. Read `workspace-profile/entities-index.md`, the entity's `entity.md`, and its
   payroll/tax classification. Load `entities/<type>.md` for the entity type.
2. Inspect every existing plan, amendment, resolution, minutes reference,
   expense form, reimbursement register, annual workpaper, and relevant payroll
   record. Search retained advisor templates for comparison, never as authority.
3. For PDFs, follow `parsing.md`: extract with `pdftotext -layout`, inspect the
   signature page visually, and use signature metadata when available. A
   summary or minute saying a document "will be executed" does not prove that it
   was signed.
4. Record distinct dates: approved, signed, effective, first operated, amended,
   and terminated. Do not collapse them into "adopted."
5. Check for prior payments, advances, open excess amounts, payroll inclusion,
   GL coding, company-card charges, duplicate claims, and claims against related
   entities.

Never inspect a `*privileged*` path under this workflow. Mask identifiers in all
notes and outputs under the root privacy rule.

Use these evidence statuses:

- **NO ARRANGEMENT EVIDENCED** — no competent approval, course of dealing, or
  other evidence of a reimbursement arrangement.
- **APPROVED, NOT EXECUTED** — approval exists but a required signature or
  stated condition to effectiveness is incomplete.
- **ACTIVE, NOT YET OPERATED** — effective arrangement; no reimbursement cycle
  has been tested.
- **ACTIVE AND OPERATED** — current plan plus sampled claims that satisfy it.
- **PARTIAL FAILURE** — particular claims or excess amounts failed while the
  remainder may retain accountable treatment under §1.62-2.
- **NONACCOUNTABLE ARRANGEMENT** — the arrangement itself fails a core test or
  impermissibly substitutes reimbursements for wages.

Do not call a plan "IRS approved," "audit proof," or "zero risk."

## The non-waivable tax tests

Every payment claimed as accountable must satisfy all three tests:

1. **Business connection.** The employee paid or incurred an expense allowable
   under Part VI, subchapter B, chapter 1 while performing services for this
   employer. The plan does not make a personal, capital, lavish, unreasonable,
   or otherwise nondeductible item deductible.
2. **Substantiation.** Within a reasonable period, the employee supplies the
   amount, date, place or description, specific business purpose, and any
   business relationship plus documentary evidence required for that expense.
   §274(d) items require its stricter elements; estimates do not replace records.
3. **Return of excess.** An advance or allowance above the substantiated amount
   is returned within a reasonable period.

Also test **wage recharacterization**. A reimbursement may not replace salary,
bonus, commission, distribution, guaranteed payment, or other compensation that
would otherwise have been paid. Do not reduce wages dollar-for-dollar as claims
rise or designate part of an unchanged compensation amount as "reimbursement."
Prospective compensation redesign requires Rev. Rul. 2012-25 analysis and
specific payroll/counsel review.

The plan controls payment **character**. Deductibility, capitalization, recovery
period, meal limitation, and return-line classification are determined
separately under the law governing the underlying item.

After the federal analysis, check state/local wage definitions, withholding,
expense-reimbursement mandates, conformity, and record-retention rules for the
employee's work state and the payroll EIN's filing jurisdictions. Do not assume
federal nonwage treatment answers every state-law question.

## Timing policy

Default to the fixed-date safe harbors in §1.62-2(g)(2):

- advance made within 30 days before the expense is paid or incurred;
- adequate accounting within 60 days after payment or incurrence; and
- return of excess within 120 days after payment or incurrence.

Separately, every advance must be reasonably calculated not to exceed the
anticipated expenditure under §1.62-2(f)(1).

The alternative safe harbor is a periodic statement issued at least quarterly,
requiring the employee to account for or return outstanding amounts within 120
days after the statement.

Note what that leaves out. The periodic-statement route requires statements at
least **quarterly**, so an entity that describes its cycle as **annual** does not
satisfy it. But test **item by item** rather than condemning the whole
arrangement: a particular expense substantiated within 60 days of payment or
incurrence is inside the fixed-date safe harbor even if the employer calls its
general cycle annual. Items that fall outside both safe harbors are not
prohibited — they require the documented facts-and-circumstances reasonable-period
analysis below, and should be described that way rather than as compliant.

The regulation also permits a facts-and-circumstances "reasonable period."
Treat a longer cycle as a deliberate, documented risk decision—not as a generic
extension or a safe harbor. State why the expense's records remain reliable,
why the delay is administratively necessary, whether any advance exists, and
how excesses are detected and returned. Treat longer cycles for §274(d) items
or claims that depend on fading recollection as elevated and require fact-
specific licensed-practitioner review; that review does not itself make the
timing reasonable. If in doubt, use 60 days.

## Drafting intake

Obtain or verify only facts that change the document:

- legal entity name, tax classification, formation state, fiscal year, and
  federal/payroll employer;
- authorized approver, plan administrator, eligible employee classes, and any
  owner-employee or related-party conflict;
- existing arrangement and reimbursement history;
- intended effective date and whether the new plan replaces or amends an older
  one;
- expense categories actually expected, advance/per-diem use, company cards,
  reimbursement cadence, and payroll provider;
- home office, mixed-use vehicle/phone/internet, travel, meals, equipment, and
  multi-entity facts that require separate modules;
- who holds receipts, who approves claims, who releases payment, and who
  reconciles the GL.

Do not request SSNs, full EINs, or bank-account numbers for the plan.

## Required clause matrix

A tailored written plan should address each item below. A heading is not enough;
the operative language must be internally consistent.

| Clause | Required decision |
|---|---|
| Purpose and authority | Intention to satisfy §62(c) and §1.62-2; no promise that every paid item is deductible |
| Sponsor and administrator | Service employer, payroll EIN, legal payor/agent, income-tax owner, authority, delegation, and conflict procedure; do not collapse a disregarded SMLLC's separate employment-tax status into its regarded income-tax owner |
| Eligible persons/capacity | Employees and officers performing employee services; explicit nonemployee boundary |
| Business connection | Employer-specific, ordinary/necessary, allowable expense; no personal benefit merely converted by approval |
| Substantiation | Required elements, receipts, allocations, report certification, and company-card records |
| Timing | Chosen safe harbor or separately justified reasonable-period rule |
| Advances and excess | Expected-expense limit, advance register, deadline, repayment method, refunds/credits |
| No wage substitution | Reimbursements do not replace or vary inversely with compensation or distributions |
| No duplicate recovery | No employer-card duplicate, personal deduction of reimbursed portion, insurer recovery, or related-entity overlap |
| Expense modules | Only modules relevant to actual operations; route specialized doctrine below |
| Exclusions/separate programs | Personal costs, commuting, entertainment absent an exception, medical/benefit plans, and other separately governed items |
| Approval and payment | Claim review, conflict controls, payment traceability, and denial/escalation |
| Books and payroll | Underlying GL account, capitalization/limitations, failed-item wage treatment, W-2 handling |
| Records | Custodian, electronic-record integrity, retention matrix below, and employee-copy policy |
| Amendment/termination | Prospective authority and treatment of pending claims/advances |
| Effective date/execution | Actual approval/signature mechanics; no blank effective-date fiction or backdating |

Use plain English. Label each operative control **Federal qualification**,
**Written-plan policy**, or **Recommended governance**, and state the
consequence of breach. Missing an internal report ID does not itself create
wages unless the omission also causes a federal or plan qualification failure.
Do not make third-party professional approval a condition of plan effectiveness
unless the company intentionally wants that condition. For a sole-owner claim,
add a practical conflict control—such as documented self-certification plus
periodic board ratification or outside review—without pretending independence
that does not exist.

## Expense-module router

Load only the module needed for the claimed category:

- **Home office:** `home-office-280a.md`. Test qualification, employer
  convenience, actual-cost allocation, §280A(c)(5), basis/Schedule A effects,
  and no double recovery with a §280A(g) arrangement. The employee simplified
  method is not an employer-reimbursement amount.
- **Travel, vehicle, meals, gifts, per diem:** current Pub. 463, §274 and its
  regulations, Rev. Proc. 2019-48, and current successor guidance. Require
  trip/mileage facts and apply rates by effective date. Use this per-diem gate:
  1. establish travel away from the worker's tax home;
  2. test whether employee and payor are related under Rev. Proc. 2019-48
     §6.07's modified §267(b) rule before permitting full lodging-plus-M&IE or
     high-low deemed substantiation;
  3. for a related owner-employee, require actual lodging substantiation and
     use an M&IE-only method only if the current procedure permits it;
  4. remember that deemed substantiation establishes amount only—time, place,
     and business purpose remain required; and
  5. distinguish an unsubstantiated day from an allowance above the deemed
     amount and route each failure through the matrices below.
  A qualifying federal per-diem method may remove the lodging-receipt
  requirement for the deemed amount; otherwise lodging requires documentary
  evidence. Do not apply the general under-$75 exception to lodging.
- **Cell phone/connectivity:** determine business-use allocation and whether
  direct employer provision under Notice 2011-72/§132 working-condition-fringe
  treatment is the cleaner route. Notice 2011-72 addresses employer-provided
  phones, not personal-phone reimbursements; any administrative reimbursement
  approach in an IRS examiner memo or IRM is nonprecedential and must not be
  described as the holding of the notice.
- **Equipment and supplies:** determine ownership, accountable reimbursement
  versus working-condition fringe, and current deduction versus capitalization.
- **Education:** determine whether §162/working-condition treatment applies or a
  separate §127 program is needed.
- **Medical insurance or medical expenses:** outside this plan. Route to §§105,
  106, 125, 223 and ACA market-reform analysis; preserve HOLD status until
  employee census, coverage, HSA, Marketplace/Medicaid, and sponsor facts are
  known.
- **Home rental/Augusta:** outside this plan. Route to
  `ccorp-tax-reduction.md` and prevent recovery of the same economic cost twice.
- **Partner expenses/UPE:** `entities/partnership.md` and
  `home-office-280a.md`; do not paper over partner status by calling the partner
  an employee.

Default exclusions include personal/family costs, commuting, ordinary clothing
and grooming, fines and penalties, political contributions, club dues, vague
round-dollar allowances, and entertainment unless a specific §274(e) exception
is identified. Business meals are not "entertainment" merely because an old
template used that word; preserve the statutory distinction.

## Operating controls

For each claim, require a unique report ID and the following fields **as
applicable**:

- employee, employer, reporting period, submission date, payment method, vendor,
  expense date, amount, currency, category, place/description, specific business
  purpose, documentary-evidence reference or recorded receipt exception, and
  allocation;
- attendees/business relationship where required;
- advance, refund, rebate, credit, insurance, employer-card, and third-party
  reimbursement fields;
- certification that the reimbursed portion was not claimed elsewhere;
- approval date, approver, payment date/reference, GL account, and any payroll
  exception.

Maintain an expense register, payment register, open-advance register, mileage
log/rate table when used, receipt index, and exception log. Employer-card charges
are within the substantiation and exception workflow even though the employer
paid the card issuer. Never issue a duplicate cash reimbursement. Unsupported
or personal charges become an employee receivable for timely repayment or
taxable compensation as the facts require.

Record allowed amounts in the underlying expense or asset account—not a
permanent catch-all "owner reimbursement" account. An optional clearing account
must reconcile to zero. Apply deduction limitations in the tax workpaper rather
than reducing the employee's documented outlay.

For a missing receipt, do not fabricate or reflexively deny. Determine whether
the item is lodging, a qualifying per-diem amount, a nonlodging item below the
current documentary-evidence threshold, transportation for which a receipt was
not readily available, or a case of lost/destroyed records supported by credible
secondary evidence. The employee must still substantiate every required
element, and lodging retains its stricter rule unless a qualifying deemed-
substantiation method applies.

If a claim misses a core requirement, do not relabel it after the fact. Deny or
recover it when possible; otherwise apply the matrices below. Review open
advances and taxable exceptions each payroll; reconcile claims, cards, advances,
repayments, bank, underlying GL accounts, payroll, and related-entity mirror
entries annually. Sample owner-employee claims more frequently.

## Failure-consequence matrix

Classify the defect before deciding its scope. Never use either “every payment
fails” or “only this claim fails” as a universal rule.

| Defect | Affected amount/scope | Baseline consequence |
|---|---|---|
| Arrangement does not require business connection, substantiation, or return of excess | Payments under that defective arrangement | Nonaccountable; wages when paid |
| Wage recharacterization or pay substitution | Substituted payments under the offending compensation design | Wages when paid; actual expenses do not cure the design |
| Discrete claim not adequately substantiated by the reasonable-period deadline | Failed claim amount for that employee | Nonaccountable amount; otherwise valid payments may remain accountable |
| Excess advance not timely returned | Unreturned excess only | Nonaccountable excess; substantiated nonexcess may remain accountable |
| Mixed deductible and bona fide nondeductible expense components | Failed component; analyze as two arrangements under §1.62-2(d)(2) | Qualifying component can remain accountable if separately identified |
| One employee fails the tests | That employee's affected payments | Apply employee by employee under §1.62-2(i) unless the arrangement itself is defective |
| Mileage/per-diem allowance above the federal deemed amount | Excess portion, subject to the special payroll timing below | Put the excess in W-2 boxes 1/3/5; put the substantiated federal-rate portion in box 12 code L. A fully substantiated allowance at or below the federal rate generally is not reported on Form W-2 |
| Pattern of excess allowances or failure to recover excess | Scope reached by §1.62-2(g)(3) and the anti-abuse facts | Do not rely on the timing safe harbors; evaluate arrangement-wide nonaccountable treatment |
| Arrangement is a vehicle to avoid or evade employment taxes | Payments under the abusive arrangement | Nonaccountable under §1.62-2(k) |

Also test whether a shareholder payment is compensation, a constructive
distribution/dividend, a bona fide receivable/loan, or another item under its
actual substance. Routing a failed owner payment through payroll is not a
universal cure.

## Payroll timing and exception register

Use Treas. Reg. §1.62-2(h), §31.3401(a)-4, the current per-diem/mileage revenue
procedure, and current payroll-form instructions. At minimum:

| Trigger | First wage/payroll treatment |
|---|---|
| Wholly nonaccountable arrangement or wage substitution | When paid |
| Otherwise accountable amount not substantiated or excess not returned within the reasonable period | No later than the first payroll period after that reasonable period ends |
| Excess mileage/per-diem reimbursement | Payroll period in which reimbursed |
| Excess mileage/per-diem advance tied to later substantiated miles/days | No later than the first payroll after the payroll period in which miles/days are substantiated, subject to the current procedure |

Later substantiation does not automatically reverse wage treatment that became
required after the reasonable period. For each exception, record taxable amount,
failure type, trigger/deadline, first affected payroll, payroll EIN, FITW/FICA/
FUTA and state treatment, employee-FICA recovery method, W-2 boxes/code L,
Forms 941/941-X, the Form 940 amended-return procedure, W-2/W-2c,
GL/receivable disposition, owner-distribution analysis if relevant, and
resolution date. Distinguish current-
period inclusion from a historical correction; do not defer the decision to the
annual review.

For mileage/per-diem allowances, apply the W-2 boundary explicitly: when the
allowance exceeds the substantiated federal rate, boxes 1/3/5 contain the excess
and box 12 code L contains the substantiated federal-rate portion. A fully
substantiated allowance at or below the federal rate generally is not reported
on Form W-2. Recheck the current W-2 instructions for the filing year.

## Related-entity booking fields

For a disregarded division, agent payor, or related regarded entity, capture the
service employer, payroll EIN, legal payor, income-tax owner, benefiting entity
or division, allocation, intercompany receivable/payable, recharge date, and
mirror-transaction reference. Confirm all allocations equal 100% or less and
that no entity deducted the same economic cost twice.

## Record retention

Keep legal minimums distinct from a longer company policy:

| Record | Legal floor | Conservative company policy |
|---|---|---|
| Plan, amendments, approval, delegation, and termination evidence | Keep while material under §6001 and applicable state law | Preserve permanently with the entity's governance history |
| Claims, receipts/secondary evidence, card substantiation, mileage/travel logs, advances, repayments, exception register, and annual reconciliation | At least four years after the related employment tax becomes due or is paid, whichever is later, and longer while material under §6001 or state law | Retain with the permanent annual tax workpaper set |
| Payroll classification and correction support | At least four years after the tax becomes due or is paid, whichever is later | Retain with the permanent annual tax workpaper set |
| Asset, vehicle, home-office basis, depreciation, and disposition evidence | Through disposition plus the applicable limitations period | Retain longer if needed for carryovers, state basis, or future character issues |

Electronic systems must preserve complete, accessible, legible records and an
audit trail consistent with Rev. Proc. 98-25 and Rev. Rul. 2003-106. Never
destroy records merely because the annual review is complete.

## Adoption, amendments, and history

- Never backdate an approval, signature, effective date, report, receipt, or
  mileage log.
- **Federal accountable-plan treatment does not depend on a written or signed
  plan.** §62(c) and Reg. §1.62-2 ask what reimbursement *arrangement* actually
  existed when the payment was made, and whether it required business
  connection, timely substantiation, and return of excess; IRS Publication 5137
  says expressly that the policy need not be a written plan. A signed,
  prospectively adopted plan is preferred evidence and may be required by the
  entity's own governing law or documents — but a missing signature is **not**
  conclusive that no federal arrangement existed. Determine and state the
  arrangement in force, do not backdate the instrument, and where a governance
  document is unsigned say so as a governance fact rather than as a tax
  conclusion. An effective date the signature page cannot support is a drafting
  error; route the tax characterization of pre-execution outlays to the CPA or
  EA in writing.
- A new plan cannot retroactively transform an employer payment already made as
  wages, distribution, or undocumented allowance. Analyze it under the
  arrangement that actually existed when paid.
- A pre-effective-date **employee outlay** is different from a prior employer
  payment. Do not state that pre-incurrence written adoption is a statutory
  element. Test the arrangement actually in force at reimbursement, its scope,
  business connection, substantiation measured from incurrence, approval
  authority, and wage-substitution facts. Prospective-only reimbursement is a
  conservative company policy, not a categorical rule of §1.62-2. Route older,
  reconstructed, or outside-safe-harbor items for licensed-practitioner review;
  never backdate the arrangement or evidence.
- State explicitly whether an amendment supplements, supersedes, or terminates
  each prior document. Preserve old signed records.
- Do not reduce `entity.md` to an "adopted" checkbox. Record the evidence
  status and distinct approval, signature, effective, and first-operated dates;
  keep unsigned writings labeled as drafts.

The authorizing consent/resolution is governed by `governance.md`; verify the
current formation-state statute, correct approving actor, and signature block.
Do not imply that a board resolution substitutes for substantiation.

## Deliverables and canonical locations

For a full draft/adopt request, normally produce:

1. `entities/<slug>/contracts/accountable-plan.md` — tailored plan.
2. `entities/<slug>/corporate/resolutions/<YYYY-MM-DD>-accountable-plan.md` —
   adoption/amendment consent under `governance.md`.
3. An expense-report/register workbook only when the user asks for operating
   controls or the existing process lacks them.
4. `entities/<slug>/tax/FY<YYYY>/annual/workpapers/accountable-plan-summary.md` —
   annual reconciliation after operation, not at adoption; start from
   `templates/accountable-plan-summary.md.template`.
5. A payroll exception register based on
   `templates/accountable-plan-payroll-exception-register.md.template` whenever
   a failed amount, excess, company-card receivable, or correction exists.

For an audit, preserve the entity's existing audit-file convention and report:

- current evidence status;
- required defects versus optional improvements;
- payment-level failures and dollar exposure when determinable;
- payroll/book correction path;
- missing decisions or documents by name; and
- execution-ready next actions, with no claim that an unsigned draft is active.

Render DOCX/PDF only when requested or needed for signature. If rendered, follow
the document/PDF skills, verify page count and signature blocks visually, and
report whether the PDF is unsigned, electronically signed, or merely contains a
signature image. End drafts with CPA/EA review before the first reimbursement
and corporate-counsel review before signing.

## Audit-risk scale

- **Low:** eligible employee; signed current plan; contemporaneous complete
  claims; traceable payments; no open excess; clean GL/payroll reconciliation.
- **Moderate:** defensible but non-safe-harbor timing, mixed-use allocations,
  owner-only approval, or specialized expense modules requiring judgment.
- **Elevated:** reconstructed records, vague purpose, round-dollar payments,
  duplicate claims, unsigned/blank documents, old entertainment language,
  reimbursement replacing compensation, unreturned advances, or attempts to
  retroactively relabel prior payments.

Risk labels describe facts and documentation; they are not probability estimates
or guarantees.

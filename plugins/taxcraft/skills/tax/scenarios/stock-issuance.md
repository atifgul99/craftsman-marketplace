# Stock Issuance — Legal, Tax, Securities, and Evidence Orchestrator

Invoke for any proposed, completed, disputed, or remedial issuance of stock;
founder shares; restricted stock; a stock subscription or purchase; conversion
of a note, SAFE, or other instrument; a stock split, recapitalization, or
reclassification; or a request to preserve QSBS (§1202) or §1244 treatment.

This file owns the **issuance workflow and tranche record**. It orchestrates,
but does not duplicate, the controlling doctrine in:

- `scenarios/corporate-records.md` — lifecycle record-set scope, authority
  chronology, annual review, and cross-register contradiction reporting;
- `governance.md` — formation-state authority, approvals, records, and counsel boundary;
- `scenarios/qsbs-1202.md` — §1202 qualification and monitoring;
- `scenarios/section-1244.md` — §1244 qualification and loss records;
- `scenarios/equity-comp.md` — §83, options, RSUs, and compensatory equity; and
- `entities/c-corp.md` or the actual issuer-type file — entity tax and books.

Treat an issuance as a **closing**, not as an accounting entry. Never backdate,
invent a transfer date, treat an unsigned draft as approval, or post the stock
entry merely because money previously reached the corporation. A journal entry
records a completed legal event; it does not create one.

## Scope and professional boundary

The skill may audit readiness, identify alternatives, prepare a fact packet,
draft workpapers and counsel-review documents, or verify a completed closing.
It does not itself issue shares, select a securities exemption, give a legal or
tax opinion, sign documents, update the stock ledger, or post the books unless
the user separately authorizes those consequential steps and the required
professional review has occurred.

Every issuance requires a documented federal and state securities-law path.
Do not assume that a founder, family, employee, service provider, or accredited
investor issuance is exempt. Do not reflexively prepare or file Form D: direct
Securities Act §4(a)(2), Regulation D, Rule 701, and state exemptions are
different paths with different facts and filings. Produce a counsel packet and
record counsel's conclusion.

End any draft or readiness report with both:

> Review with corporate and securities counsel before signing, issuing, or
> filing. Verify federal and state tax conclusions with tax counsel or a CPA/EA.

## Operating modes

| Mode | Result |
|---|---|
| **Readiness audit** | Evidence inventory, contradictions, gate statuses, and missing-item list; no mutation |
| **Transaction design** | Alternatives by consideration type, provisional tax matrix, and counsel questions |
| **Counsel packet** | Verified facts and proposed terms using the readiness template; no legal conclusion |
| **Closing verification** | Executed-document, payment, notice, ledger, tax-deadline, and accounting reconciliation |
| **Remediation** | True historical timeline, defect classification, and counsel-controlled cure choices; never retroactive fiction |
| **Annual monitoring** | Entity-status, active-business, redemption, capitalization, and lot-continuity review |

Do not silently move from one mode to another. In particular, a readiness or
drafting request does not authorize execution, filing, ledger changes, or book
entries.

## Mandatory state machine

Run in this order. A later step never **automatically** cures an earlier failed
gate. A defective-action ratification or other validation is a separate,
counsel-approved and evidenced event; preserve the formation statute, each
approval/filing, and the legal effective date rather than silently rewriting
the original event:

`authority → terms → consideration → valuation/vesting → tax → securities → approval → payment/transfer → issuance → ledger/notice → accounting → evidence validation`

Assign exactly one status to each tranche:

| Status | Meaning |
|---|---|
| `PROPOSED` | Terms are being considered; no approval or issuance represented |
| `COUNSEL HOLD` | A legal, tax, authority, conflict, or exemption issue blocks progress |
| `APPROVED — NOT ISSUED` | Valid approval is evidenced, but the transfer/issuance conditions are incomplete |
| `ISSUED — CONSIDERATION OUTSTANDING OR ESCROWED` | State law permits deferred consideration and the approved restriction/escrow is documented |
| `PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED` | Records indicate a purported issuance but payment/property receipt is not proved and legal effectiveness remains for counsel; never infer issued/paid status |
| `ISSUED AND PAID — OTHER EVIDENCE INCOMPLETE` | Payment and issuance are proved, but a non-conflicting closing record is missing |
| `ISSUED AND RECONCILED` | Executed records, consideration, ledger, notice/certificate, tax memo, and books agree |
| `DISPUTED OR DEFECTIVE` | Material terms/authority records conflict or a required corporate act appears invalid; counsel controls cure |

Use `UNVERIFIED` for any individual fact not proved by a competent source.
Never upgrade a status on an inference, an unsigned document, a board minute
that describes future action, or a bookkeeping label alone.

### Status precedence

First ask whether competent evidence shows a **purported issuance/closing
actually occurred**. A draft, ownership label, proposed journal entry, or
historical cash transfer is not such evidence.

1. **No evidenced purported issuance:** use `PROPOSED`, `COUNSEL HOLD`, or
   `APPROVED — NOT ISSUED`. Missing authority/bylaws, historical-APIC nexus,
   unresolved exemption, or contradictory pre-issuance ownership labels force
   `COUNSEL HOLD` even if another document calls the recipient a shareholder.
2. **Evidenced purported issuance:** first test material authority and term
   conflicts. If authority, recipient, class, share count, consideration, or
   approval materially conflicts or appears invalid, use `DISPUTED OR
   DEFECTIVE`; this overrides all other post-issuance statuses.
3. If no such conflict exists, classify consideration as `OUTSTANDING OR
   ESCROWED`, `UNVERIFIED`, or proved paid. An unverified result is `PURPORTED
   ISSUANCE — CONSIDERATION UNVERIFIED` until counsel confirms legal effect.
   Only then may the tranche advance to
   `ISSUED AND PAID — OTHER EVIDENCE INCOMPLETE` or `ISSUED AND RECONCILED`.

Never update the recipient to shareholder or change an entity ownership profile
from a `PURPORTED ISSUANCE` status.

### The persisted artifact records a subset, and says which

The eight statuses above are the working vocabulary. The validated JSON artifact
(`schemas/stock-issuance-audit.schema.json`) is produced **only for tranches
that have reached a purported closing**, because every tranche row requires a
closing manifest. Its `status` enum is therefore a deliberate subset plus two
machine-only values, and this is the mapping — do not invent another:

| Prose status | Persisted as |
|---|---|
| `PROPOSED` | **not persisted** — no closing exists yet; track it in the readiness memo |
| `APPROVED — NOT ISSUED` | **not persisted** — same reason |
| `ISSUED — CONSIDERATION OUTSTANDING OR ESCROWED` | `CLOSING_PENDING`, with the escrow/restriction evidence in the manifest |
| `COUNSEL HOLD` | `COUNSEL_HOLD` |
| `PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED` | `PURPORTED_ISSUANCE_CONSIDERATION_UNVERIFIED` |
| `ISSUED AND PAID — OTHER EVIDENCE INCOMPLETE` | `CLOSING_PENDING` |
| `ISSUED AND RECONCILED` | `ISSUED_AND_RECONCILED` |
| `DISPUTED OR DEFECTIVE` | `DISPUTED_OR_DEFECTIVE` |

Two machine-only values carry facts the prose statuses leave implicit:

- **`FACT_CONFLICT`** — material records conflict, but no purported issuance is
  evidenced. This is the pre-issuance twin of `DISPUTED OR DEFECTIVE`; the prose
  reaches the same situation through `COUNSEL HOLD`, and the artifact separates
  it so a conflict is never filed away as a mere hold.
- **`CLOSING_PENDING`** — a purported closing exists and some gate is unverified
  for a reason other than consideration.

The artifact carries `purported_issuance_evidenced` for exactly the question
this section opens with. It is a **reviewed fact, never inferred**: set it true
only where competent evidence shows a purported issuance actually occurred. A
tranche with every gate verified and that flag false is rejected rather than
promoted, because clean paperwork is not evidence that an issuance happened.


“Highest supported status” means the first applicable result in this decision
sequence, not the most complete-sounding label.

## Gate 1 — issuer identity and authority

Before discussing share count or tax benefits, verify:

1. Exact legal issuer, formation state, legal form, federal tax classification,
   and any S-election effective dates on the proposed issuance date. An S
   corporation cannot issue QSBS while the S election is effective. Treat LLC
   units in an LLC taxed as a corporation as legally and tax-technically
   unresolved rather than silently calling them stock.
2. Filed charter/articles and every amendment: authorized shares by class and
   series, par value, preferences, and any board authority to set terms.
3. Organizational authority: incorporator action, initial directors, current
   directors/officers, bylaws, delegation, and valid approving actor under the
   formation state's law. A state registry's public governor list does not by
   itself prove the internal election chain.
4. Preemptive rights, investor agreements, voting agreements, transfer
   restrictions, protective provisions, and required shareholder/class votes.
5. Capitalization reconciliation, by class: separately prove **authorized**,
   **issued**, **outstanding**, **treasury/reacquired**, **reserved/committed**,
   and **legally available** shares. Do not conflate issued with outstanding.
   Apply the formation state's rule to reacquired/treasury shares and charter
   limits; document the counsel-approved capacity formula. For a simple class
   with no treasury/reacquired shares, test `authorized − outstanding −
   reserved/committed`, but do not export that shortcut to another jurisdiction.

6. Every prior issuance, cancellation, repurchase, conversion, split, and
   conflicting share count. Stop if any source reports a different outstanding
   count until the difference is reconciled.

Hard stops: missing organizational authority, missing governing documents,
insufficient authorized capacity, unresolved class rights, contradictory share
counts, or an approving actor whose authority/conflict route is unresolved.

## Gate 2 — terms and recipient

Record the actual terms, not merely an intended ownership percentage:

- recipient legal name and capacity (founder, investor, employee, contractor,
  entity, trust, partnership), without unnecessary identifiers;
- number, class/series, price per share, total consideration, and intended date;
- voting, dividend, liquidation, conversion, information, and transfer rights;
- vesting, repurchase option, forfeiture, escrow, legends, and acceleration;
- fully diluted denominator, resulting ownership, reserved awards, and any
  promised but unissued interests; and
- related-party conflict disclosure and the formation-state fairness/approval
  route, especially where the purchaser is also the sole director or officer.
  Where the purchaser is the only director, the qualified-director route is
  unavailable. Test qualified-share beneficial ownership, voting control,
  disclosure, and the voting requirements separately, and record whichever route
  is actually relied on as `governance.md` → "Conflicting-Interest Transactions
  in Owner-Controlled Entities" requires, rather than reciting a disinterested
  approval no one gave.

An ownership percentage is an output of a reconciled cap table, not an
independent fact. Do not describe someone as a shareholder until issuance is
evidenced.

## Gate 3 — consideration branch

Select every consideration type in a mixed transaction and analyze each
separately.

| Consideration | Required treatment |
|---|---|
| **New cash** | Match subscription/purchase terms, bank receipt, date, payor, amount, and ledger. Contemporaneous cash is the cleanest §1244 fact pattern. |
| **Historical cash/APIC** | `COUNSEL HOLD`. Preserve the real transfer and booking dates. Do not backdate or assert that a later issuance was in exchange for old money. Obtain written corporate- and tax-counsel treatment; keep prospective new cash separate. |
| **Property** | Identify property, transfer date, title, liabilities, transferor basis, FMV evidence, corporation's receipt, and §351 consequences. For QSBS gross assets and §1244 basis, apply the statute-specific FMV/basis rules. |
| **Past or current services** | Route to `equity-comp.md`. Determine compensation income, withholding/payroll, FMV, restrictions, transfer date, and §83(b). Services may support §1202 original issuance but not §1244. |
| **Future services or promissory note** | State-law receipt, escrow, and restriction rules are controlling; tax and collection consequences require counsel. Do not mark fully paid unless the governing law and evidence support it. |
| **Debt cancellation/conversion** | Identify original debt, holder, issue price, accrued interest, whether it is a security or arose from services, COD/§108 issues, and conversion mechanics. Test §351, §1202, and §1244 separately. |
| **SAFE/note conversion** | The instrument is not stock before conversion. Establish the actual conversion date, consideration mechanics, security terms, and exemption; test the resulting stock as a new tranche. |
| **Mixed consideration** | Allocate shares, price, basis, compensation, and tax conclusions by consideration component; never blend a failing component into a qualifying one. |

Historical cash remediation is not a documentation exercise. The workpaper must
show the original transfer, original contemporaneous label, prior tax/book
treatment, whether any stock was actually authorized or delivered then, and
the proposed present action. Any conclusion that old cash supports newly issued
§1244 stock must be expressly attributed to written tax-counsel analysis.

### Marital-property character (conditional)

Where the holder is married and domiciled in a community-property state, the
character of the shares is a **conditional, tracing-dependent** question, not a
default. Say what the tracing evidence shows for the specific tranche and stop
there. Do not state a categorical conclusion, do not extend a conclusion to
shares not yet acquired, and do not treat a spousal acknowledgment as a
determination of character — it records what the spouses acknowledge on stated
facts. Separate-property tracing, commingling, and any premarital or marital
agreement are counsel questions; the record's job is to preserve the funding
trail that makes tracing possible.

## Gate 4 — valuation, price, and vesting

No-par stock does not mean free stock or arbitrary value. Document the board's
good-faith adequacy determination under state law and the tax FMV evidence.

**The adequacy determination is its own signed instrument, made before the
issuance it supports.** A recital inside the issuance resolution that the
consideration "is adequate" is not the determination; most corporation statutes
make the board's determination of adequacy conclusive only when it was actually
made, and a determination cannot be made about a payment that has already been
converted into shares. Draft it as a separate consent carrying: the class and
number of shares, the consideration and its form, the facts relied on, the
determination itself, and — where the subscriber is also a director or officer —
the fairness findings in the **same** signed writing. Record the receipt
timestamp and the issuance timestamp so the order is provable. Instantiate
`templates/adequacy-and-fairness-determination.md.template`, one per closing.

**No retroactive true-up.** Money that reached the corporation before a valid
subscription and an effective authorization existed is a refundable subscription
deposit, a loan, or a bare contribution to capital — the contemporaneous facts
decide which. It is not share consideration, and a later quarterly or annual
"true-up" resolution may not convert it into share consideration as of the date
it arrived. Where the parties intend future shares, use a refundable deposit
with written terms and issue against a signed subscription when the
authorization is in place.

- Cash purchase: reconcile price to contemporaneous facts, prior/subsequent
  financings, liabilities, IP, revenue, and capitalization.
- Compensatory stock: obtain a defensible §83 FMV; options may require §409A
  analysis. Record payroll and withholding treatment.
- Property: retain an independent or otherwise supportable FMV and basis file.
- Restricted stock: define the substantial risk of forfeiture, vesting,
  repurchase price, transferability, and actual property-transfer date.

An §83(b) deadline runs from **transfer of the property**, not a vague grant or
approval date. When applicable, record the 30-day deadline, signed election or
Form 15620, timely IRS delivery proof, service-recipient copy, transferee copy
if different, and payroll coordination. Missing timely proof is a hard
post-closing exception; never fabricate or backdate an election.

Instantiate `templates/stock-issuance-83b.md.template` for every substantially
nonvested stock transfer, including a documented `ELECT`, `DO NOT ELECT`, or
`MISSED OR UNRESOLVED` decision. The template is an execution control, not a
recommendation to elect.

## Gate 5 — per-tranche federal and state tax matrix

Complete `templates/stock-issuance-tax-memo.md.template`. At issuance, use
`ISSUANCE-DATE PRONGS SATISFIED — PROVISIONAL`, `ISSUANCE-DATE INELIGIBLE`,
`UNVERIFIED`, or `NOT APPLICABLE` for each doctrine—never a single blended “tax
advantaged” or final qualification conclusion. Section 1202 remains contingent
on substantially-all holding-period tests, and §1244 remains contingent on the
loss-date gross-receipts and holder-continuity tests. Final `QUALIFIES` or
`DOES NOT QUALIFY` belongs only in a disposition/loss workpaper using the full
later facts.

### §1202 / QSBS

Load `qsbs-1202.md`. At minimum establish the actual acquisition/issuance date,
issuer C-corporation status, original-issue consideration, before-and-after
aggregate gross assets under the date-sensitive statutory ceiling, predecessor
and controlled-group aggregation, qualified-business facts, 80%-active-use
facts, redemption windows, and cap-table continuity. Services can qualify;
secondary purchases cannot. Preserve real dates because the holding period and
post-7/4/2025 regime depend on them.

### §1244

Load `section-1244.md`. Establish a domestic corporation, actual stock, original
individual/partnership holder, and money/property consideration (not services).
Build the lifetime capital-receipts schedule by tax year. Stock issued before
the transitional year may qualify without designation; in the first tax year
when capital receipts exceed $1,000,000 and stock is issued, only the remaining
pool—`$1,000,000 − pre-transitional-year capital receipts`—can receive the
regulatory designation or default proportional allocation; stock issued after
that transitional year does not qualify. Section 1244 has no general election
or plan. Do not promise §1244 status for historical bare contributions or later
basis increases.

### §351 and basis

For §351, cash is property. Test every cash or other property transfer for
whether property is transferred solely for stock
and the transferor group controls at least 80% immediately after. Services are
not property for §351. Identify all transfers under the same plan, every
transferor's property/services split, the immediate-after voting and share-count
control denominator, and whether nominal property is being used to include a
service provider in the control group. Stock issued solely for services is not
issued for §351 property; under Reg. §1.351-1(a)(1), a service provider joining
the transferor group must also contribute property that is not relatively small
compared with the stock received for services. Record boot, §357(c) gain when
liabilities assumed exceed aggregate adjusted basis, §358 shareholder-stock
basis, §362 corporate carryover basis and any §362(e)(2)
built-in-loss adjustment/election, holding periods, and the transferor and
transferee statements required by Reg. §1.351-3. Record the exact immediate-
after control percentage and the §368(c) voting/value control conclusion. A
direct cash purchase that demonstrably fails the §351 control test generally
starts with §1012 cost basis; cash may not be marked §351 `NOT APPLICABLE` merely
because it is cash. For QSBS acquired for property,
separately apply §1202(i)'s FMV/basis rules. Do not equate §351 nonrecognition
with QSBS or §1244 qualification.

Instantiate `templates/stock-issuance-351-property.md.template` whenever any
property, IP, debt, mixed consideration, or integrated transfer plan is present.

### §83 and payroll

For services/restricted stock, load `equity-comp.md` and record §83 income,
amount paid, FMV, vesting, §83(b) decision/deadline, payroll withholding,
deduction timing, and information reporting. State-law wage and withholding
rules may differ.

## Gate 6 — securities-law route

Counsel must identify, by tranche:

1. the federal registration exemption or registration path;
2. the exemption's factual predicates and resale restrictions;
3. every offeree/purchaser and whether solicitation occurred;
4. Form D or other federal filing, if any, and its deadline;
5. each state where an offer or sale occurred, the state exemption, notice,
   consent-to-service, fee, and deadline; and
6. the required certificate legend or uncertificated-share information notice.

Do not treat Rule 701 as a cash-investment exemption. Do not treat Rule 506 as
the automatic answer for a private sale. Direct §4(a)(2), Regulation D, Rule
701, and state nonpublic/isolated transaction provisions require different
facts. “Accredited,” “founder,” “friend,” or “family” is not a complete result.

## Gates 7–10 — approval, transfer, issuance, and records

The closing binder must prove the sequence:

1. final counsel-reviewed terms and exemption path;
2. conflict disclosure and fairness/adequacy record;
3. valid board action and any required shareholder/class action;
4. executed subscription, purchase, restricted-stock, or conversion agreement;
5. consideration paid/transferred, or lawful escrow/restriction for future
   performance, with bank/property evidence;
6. issuance effective under the approval and governing law;
7. certificate delivered or valid uncertificated-share notice delivered within
   the state-law period, with conspicuous restrictions/legends;
8. stock ledger and cap table updated to the identical tranche ID, date, shares,
   holder, class, certificate/notice number, consideration, and restriction;
9. tax memo, §83(b) package, securities filings/notices, and deadlines resolved;
10. journal entry posted only after the legal closing and tied to the tranche ID;
11. entity profile and beneficial-ownership records reconciled; and
12. closing-binder manifest signed off with no unexplained difference.

Instantiate:

- `templates/stock-issuance-readiness.md.template` for intake and gate status;
- `templates/stock-issuance-register.md.template` as the per-tranche source of truth;
- `templates/stock-ledger.md.template` for the legal share ledger;
- `templates/stock-cap-table.md.template` for ownership and fully diluted views;
- `templates/stock-issuance-tax-memo.md.template` for the qualification record;
- `templates/stock-issuance-351-property.md.template` for property/control/basis;
- `templates/stock-issuance-83b.md.template` for restricted-stock execution; and
- `templates/stock-issuance-closing-manifest.md.template` for the human-readable
  final binder index;
- `templates/stock-issuance-closing-manifest.json.template` for the exact-match,
  hashed machine control over the eight required closing artifacts; and
- `templates/stock-issuance-audit.json.template` for the annual structured
  specialist result consumed by `corporate-records.md`.

Store the register and closing evidence under
`entities/<slug>/corporate/stock-issuances/`. The register points to source
documents; it never replaces them. QSBS monitoring remains under
`corporate/qsbs-tracking/` and cross-references the tranche ID.

Persist the structured result as
`corporate/stock-issuances/stock-issuance-audit-FY<YYYY>.json` only after
validation with `evals/validate_stock_issuance.py --artifact <path>`. It must
bind every tranche to federal and each applicable state securities authority,
all four §83/§351/§1202/§1244 position checks, and a hashed JSON closing
manifest. The validator reopens the manifest, exact-matches the tranche terms,
rejects exceptions or duplicate/missing artifact kinds, and recomputes every
underlying closing-artifact hash before allowing `ISSUED AND RECONCILED`.
It also derives securities jurisdictions from issuer formation, holder
residence, offer, sale, and solicitation facts; requires a substantive state
registration/exemption route separately from any notice; applies the
formation-state capacity formula on a class-by-class basis against hashed
charter authority. That authority must be typed JSON in the subject's canonical
`corporate/formation/` folder, identify `ARTICLES_OR_AMENDMENT`, hash the
underlying source document, state the extracted class and authorized-share
number, and bind that number exactly to the capitalization rollforward.
Instantiate `templates/stock-issuance-charter-class-authority.json.template` for
it rather than composing the shape by hand — the tranche's
`charter_class_authority_path` and `charter_class_authority_sha256` are checked
against this file, and a mismatch fails the artifact. A
ledger or closing artifact cannot substitute for charter authority. The
validator requires board approval for issuance and exact-matches typed approval,
consideration-clearance, issuance, delivery, journal-posting, tax, and
securities-filing facts. Eight labels pointing to one file are rejected.

The structured tax fields deliberately separate legal closing from later tax
qualification. Sections 1202 and 1244 use
`ISSUANCE_DATE_PRONGS_SATISFIED_PROVISIONAL` or
`ISSUANCE_DATE_INELIGIBLE` at issuance—never final `VERIFIED`. A correct
issuance-date provisional result does not by itself block a legally and
operationally reconciled closing; `UNVERIFIED` or `COUNSEL_HOLD` does. Section
83/351 facts activate additional exact rule dependencies, including the
applicable §§357/358/362/368(c) and Reg. §§1.83-2, 1.83-4, 1.351-3, and
1.358-2 branches. A substantially nonvested tranche also requires a typed
§83(b) decision, transfer date, computed 30-day deadline, proof fields, and
holding-period result before it can reconcile.

## Closing invariants

A tranche cannot be `ISSUED AND RECONCILED` unless all are true:

- authority chain and available capacity are proved;
- executed terms, approval, consideration, issuance date, ledger, cap table,
  certificate/notice, and books agree exactly;
- the securities route and all applicable filings/notices are documented;
- tax results are separate, source-backed, and never stronger than the evidence;
- restrictions and vesting are consistent across every document;
- any §83(b) branch is classified `TIMELY ELECTED`, `AFFIRMATIVELY NOT
  ELECTED`, `NOT APPLICABLE`, or `MISSED/UNRESOLVED`, with its actual holding-
  period result;
- no historical fact was rewritten, no document backdated, and no unsigned
  draft relied upon; and
- the post-closing authorized/issued/outstanding/treasury/reserved/legal-
  availability reconciliation balances under the formation-state rule.

If an invariant fails, keep the highest supported status and list the exact
document or decision needed. Never use “substantially complete” to conceal a
missing deadline or invalid authority.

## Post-closing and annual monitoring

For each tranche, track:

- C-corporation and S-election status changes;
- QSBS qualified-business and 80%-active-use evidence throughout substantially
  all of the holding period, including working capital, subsidiaries, portfolio
  assets, and real estate;
- issuer redemptions/repurchases in the statutory windows around issuance;
- splits, combinations, recapitalizations, conversions, gifts, trusts,
  transfers, and §351/reorganization continuity without losing lot identity;
- vesting, forfeitures, repurchases, and employment termination;
- §1244 annual gross-receipts evidence and capital-receipts history; and
- proposed sale, worthlessness, or §1045 rollover events.

Run `PYTHONDONTWRITEBYTECODE=1 python3 evals/validate_stock_issuance.py` and the
substantive cases in `evals/stock-issuance.md` after any material change to this
file or its four referenced doctrine modules. A passing structural check is not
a legal or tax opinion; the adversarial cases must also pass on substance.

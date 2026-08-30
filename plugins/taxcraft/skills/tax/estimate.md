# Individual Federal Estimate Computation

This file is the individual Form 1040 computation reference. Invoke it through
`close-estimate.md`, which controls mode, authority, evidence, persistence,
status, and payment boundaries. Installment mechanics live in `quarterly.md`.

This module does not authorize file writes or payment activity.

## Entry gates

Before computing:

1. Resolve taxpayer, filing status, tax year, residency, and as-of date.
2. Load `authority.md`, the target-year rules file, and `rules/manifest.json`.
3. Require an authority record for every exact rule used. A missing rules file
   or unverified used path creates `AUTHORITY_HOLD`; do not merely warn.
4. Load the input manifest produced by `close-estimate.md`. A source field may
   enter arithmetic only when its state permits it.
5. Load carryforwards and entity/K-1 inputs only when their period, version, and
   taxpayer identity match. Projected K-1s make dependent results provisional.

## Field-state contract

Do not represent every missing number as `0`. Each load-bearing field has:

```json
{
  "value": null,
  "state": "OBSERVED_VALUE | OBSERVED_ZERO | NOT_PRESENT | UNREADABLE | NOT_APPLICABLE | DERIVED | MANUAL_OVERRIDE",
  "source_ref": "document or computation line",
  "authority_ids": [],
  "notes": []
}
```

Only `OBSERVED_VALUE`, `OBSERVED_ZERO`, a supported `DERIVED` value, or an
approved `MANUAL_OVERRIDE` enters arithmetic. `NOT_PRESENT` is not zero unless
the form and source context prove that omission means zero. `UNREADABLE` blocks
the dependent line. Statement-dependent K-1 codes remain unresolved until the
statement is parsed.

## Form-line computation order

Preserve these layers separately so AGI, MAGI, taxable income, credits, and
payments cannot contaminate each other.

### 1. Gross income

Compute the applicable Form 1040 and Schedule 1 income lines from evidenced
sources:

- wages and other compensation;
- taxable and tax-exempt interest;
- ordinary and qualified dividends;
- capital gains/losses, including character buckets and carryovers;
- Schedule C/F income;
- rentals, royalties, partnerships, S corporations, trusts, and estates;
- retirement, Social Security, unemployment, and other income.

For pass-through and rental losses, apply basis, at-risk, passive-activity, and
excess-business-loss limits in the correct order. Preserve allowed and suspended
amounts by activity. Cash distributions are not interchangeable with
distributive share.

For capital gains, keep ordinary income, 0/15/20% gain, unrecaptured §1250 gain
(maximum 25% rate), collectibles gain (maximum 28% rate), and §1202/AMT items in
separate buckets. Unrecaptured §1250 gain is not automatically “recapture.”

### 2. Schedule 1 adjustments

Compute applicable adjustments, including:

- deductible part of self-employment tax;
- self-employed retirement-plan deduction;
- self-employed health insurance;
- HSA or Archer MSA deduction under the correct regime;
- IRA and student-loan-interest deductions; and
- other current-form adjustments.

For a self-employed retirement contribution, do not apply a raw 25% employer
percentage to Schedule C profit. Use the reduced-rate/net-earnings computation
and applicable plan limits. Resolve circular deductions iteratively where the
official worksheet requires it.

```text
AGI = gross income - Schedule 1 adjustments
```

### 3. Form 1040 line 12 deduction

Compute the allowed standard deduction or itemized deduction under the target
year's form:

- filing-status and age/blindness rules;
- dependent standard-deduction formula;
- zero-deduction gates, including MFS when the spouse itemizes and applicable
  nonresident/dual-status rules;
- target-year nonitemizer additions, if any;
- medical, SALT, mortgage-interest, charitable, casualty, wagering, and other
  target-year floors, caps, reductions, and substantiation rules.

Do not infer these mechanics from a single `standard_deduction` scalar.

### 4. QBI deduction — Form 1040 line 13a

Compute §199A by qualified trade or business, then aggregate as the form and
regulations require. Preserve SSTB status, taxable-income thresholds, phase-in,
W-2 wages, UBIA, loss carryovers, REIT/PTP components, material-participation
facts for any minimum deduction, and the taxable-income/net-capital-gain limit.

### 5. Schedule 1-A additional deductions — Form 1040 line 13b

For years in which Schedule 1-A applies, compute its deductions separately:

- qualified tips;
- qualified overtime compensation;
- qualifying passenger-vehicle loan interest; and
- enhanced deduction for seniors.

These deductions do **not** reduce AGI. Preserve their distinct MAGI,
eligibility, SSN/joint-return, documentation, cap, and phaseout rules. Apply
completed-$1,000 versus $1,000-or-portion rounding exactly as the applicable
statute/form requires; do not reuse one generic phaseout function.

```text
taxable income before floor-at-zero =
  AGI
  - Form 1040 line 12 deduction
  - QBI deduction (line 13a)
  - Schedule 1-A deduction (line 13b)
taxable income = max(0, result)
```

On the current form, line 14 is the total of line 12, line 13a, and line 13b;
it is not an additional deduction to subtract again.

### 6. Regular income tax

Use the target-year Tax Table or applicable official worksheet. Stack ordinary
and preferential income rather than computing both on the same base:

```text
regular income tax = ordinary-income component + preferential-income component
```

The preferential component includes qualified dividends and applicable capital
gain buckets. NIIT is a separate tax and must not be added to the 0/15/20%
capital-gain rates inside this step.

### 7. AMT

Compute Form 6251 from the correct starting point and target-year instructions.
Track, when applicable, SALT and other itemized adjustments, private-activity
bond interest, ISO bargain element and dual basis, depreciation, depletion, and
preference items. Maintain deferral-item basis needed for Form 8801 rather than
recording only the current-year AMT amount.

### 8. Other taxes

Compute applicable Schedule 2 taxes separately, including:

- self-employment tax with the Social Security wage-base interaction;
- Additional Medicare Tax;
- NIIT under its own MAGI definition;
- household-employment, retirement-plan, recapture, and other target-year
  taxes.

Excess Social Security withheld is a payment/credit, not another tax.

### 9. Credits and total tax

Separate nonrefundable credits, refundable credits, and payments. Apply each
credit's ordering, limitation, phaseout, carryforward, and recapture rules.

```text
income tax after nonrefundable credits
+ other taxes
= total tax for the applicable Form 1040 / 1040-ES line contract
```

Do not use a generic `total_tax` shortcut for a prior-year safe-harbor input;
`quarterly.md` requires the exact filed-return/form-line evidence.

### 10. Payments and balance

Reconcile withholding, estimated payments, extension payments, prior-year
overpayment applied, and refundable credits. A scheduled, recommended, rejected,
or wrong-year payment is not an allowed paid credit. Excess Social Security
withheld belongs here.

```text
balance due or refund = total tax - allowed payments and refundable credits
```

## Required computation identities

Every result must prove:

- gross income − adjustments = AGI;
- AGI − line 12 − QBI − Schedule 1-A = taxable income before
  the statutory zero floor;
- ordinary tax component + preferential component = regular income tax;
- regular income tax + AMT + other taxes − applicable nonrefundable credits =
  total tax under the recorded form-line contract;
- payment components foot to total payments;
- total tax − payments/refundable credits = balance due or refund.

If an identity fails, status is `ESTIMATE_HOLD`.

## Output contract

When persistence is authorized, produce the canonical JSON from
`templates/estimate.template.json`. Every amount includes state and provenance;
the artifact also records:

- run ID, mode, scope, tax year, as-of date, and superseded-run link;
- authority status and exact used rule paths/authority IDs;
- input manifest references and reliability;
- computation lines with inputs → formula → result;
- estimate status and materiality;
- warnings, blockers, and open questions;
- `payment_execution_authorized: false`.

The presentation may show a compact table, but it must label the result
`PROVISIONAL`, `DRAFT_VERIFIED_INPUTS`, or `READY_FOR_PRACTITIONER_REVIEW` and
point to the canonical artifact. Never present a held or unknown line as zero.

## Special routing

- Quarterly individual installments → `quarterly.md` after this annual tax
  engine produces the applicable current-year tax.
- WA capital-gains excise tax → current `states/wa/` authority; keep it separate
  from federal total tax.
- ACA/PTC or Medicaid MAGI → `scenarios/aca-medicaid-magi.md`; do not reuse NIIT
  MAGI.
- Equity compensation → `scenarios/equity-comp.md`.
- Rental, K-1, oil-and-gas, or other specialized income → load only the relevant
  scenario module.

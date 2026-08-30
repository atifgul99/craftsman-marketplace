# ACA / Medicaid MAGI Eligibility

Trigger: health-coverage eligibility questions — ACA marketplace premium tax credit (PTC) eligibility, state Medicaid MAGI thresholds, Form 8962/1095-A reconciliation, or managing MAGI for eligibility purposes when the household has volatile K-1/passthrough income.

## MAGI Definition (Medicaid/PTC) — Do Not Confuse With NIIT MAGI

MAGI for ACA/Medicaid eligibility purposes, per **IRC §36B** and **26 CFR 1.36B**, is:

```
MAGI (ACA/Medicaid) = AGI
                     + tax-exempt interest
                     + excluded foreign earned income (+ related housing exclusion/deduction)
                     + nontaxable portion of Social Security benefits
```

**This is a different computation than the NIIT MAGI definition under IRC §1411.** NIIT MAGI also starts from AGI but adds back foreign earned income exclusion items on a different basis (and doesn't add back nontaxable Social Security the same way). The two MAGI figures will diverge whenever foreign earned income exclusion or Social Security is in play. Never reuse a NIIT MAGI figure (e.g., one already computed per `estimate.md` Section 6, Other Taxes → NIIT) as the ACA/Medicaid MAGI figure without re-deriving the add-backs specific to §36B. **Produce and label two separate figures, never one.** The register in
`individual/1040.md` §4 defines them as distinct rows with distinct authority:

- **`MAGI (§36B)`** — the premium tax credit figure, computed as above.
- **`MAGI (Medicaid)`** — 42 U.S.C. §1396a(e)(14) and 42 C.F.R. §435.603. It
  uses §36B MAGI as a base but diverges: **current-month** rather than annual
  measurement, exclusion of a dependent child's income below the filing
  threshold, scholarship and AI/AN exclusions, lump-sum treatment, and a 5% FPL
  disregard.

Never carry a single figure labeled "ACA/Medicaid MAGI" — that conflation is the
error this section exists to prevent, and it is separate from the §1411 NIIT MAGI
warning above.

**Canonical workpaper for this scenario: `wp-aca.md`** in
`individual/FY<YYYY>/annual/workpapers/`. It owns 1095-A and APTC monthly
reconciliation, both MAGI figures, and the SE-health circular iteration result.
It is **not** `wp-health.md`, which is the HSA/FSA/IRMAA workpaper owned by
`individual/health-benefits.md`.

## Monthly vs. Annual Measurement

The two programs measure income on different clocks — conflating them is a common and consequential error:

- **Medicaid**: eligibility is generally based on **current monthly income** — a point-in-time/near-term test. This means eligibility can be volatile month-to-month for households with irregular income (e.g., a K-1 distribution or a large capital gain realized in one month can knock a household off Medicaid for that determination period even if annual income is otherwise low).
- **ACA marketplace PTC**: eligibility and reconciliation are based on **annual projected/actual household income for the full calendar year**, reconciled on **Form 8962** against actual subsidy amounts (advance premium tax credit, APTC) reported on **Form 1095-A**.

Because of this mismatch, a household can be Medicaid-ineligible in a given month (income spike) while still being ACA-PTC-eligible for the year (annual average within range), or vice versa. Always identify which program's clock applies before running a projection.

## PTC Cliff / Enhanced-Subsidy Status — Verify Every Year

Enhanced ACA subsidies — removal of the 400%-of-federal-poverty-line ("400% FPL") subsidy cliff and the enhanced percentage-of-income premium caps — were enacted temporarily under ARPA (2021) and extended by the IRA (2022). Their expiration/extension status changes by year and by subsequent legislation.

**Do not assume based on prior years.** Before relying on any specific percentage-of-income cap, or on the presence/absence of the 400% FPL cliff, verify the current-year status directly (current IRS Form 8962 instructions, healthcare.gov guidance, or current-year legislative text). This scenario file intentionally does not hardcode a percentage-of-income table or a cliff/no-cliff assumption because it goes stale annually.

## Levers That Move MAGI for Eligibility Purposes

Once a MAGI projection is run (per `estimate.md`), these are the planning levers available to move ACA/Medicaid MAGI up or down relative to a threshold:

- **Timing of K-1/passthrough income recognition** — entity-level timing elections, distribution timing where it affects the year of recognition. See `scenarios/k1-vc-pe.md` for how passthrough character and timing flow through at the fund level; coordinate any timing lever with the entity before assuming it's available at the LP level.
- **Retirement plan contributions** — traditional 401(k), IRA, SEP, Solo 401(k): reduce AGI and thus MAGI (Roth contributions do not).
- **HSA contributions** — reduce AGI.
- **Capital-loss harvesting** — realizing losses to offset gains reduces AGI; subject to the §1211(b) $3,000 net-loss cap against ordinary income (see `estimate.md` gross-income step 1) with carryover of the excess.
- **Avoid Roth conversions in years when MAGI-based eligibility matters** — a Roth conversion adds directly to AGI/MAGI in the conversion year and can spike a household above a threshold; flag any planned conversion against the eligibility calendar before executing.
- **Self-employed health insurance (SE health insurance) deduction — circularity trap.** The SE health insurance deduction amount depends on net self-employment income, which in turn can be affected by other MAGI-affecting elections (e.g., a SEP/Solo-401k contribution reduces the income base the SE health deduction is computed against, and the SE tax deduction itself interacts with the same base). This is a genuine circular computation — do not hand-wave it or approximate with a single pass. Iterate: compute net SE income → SE tax deduction → SE health insurance deduction ceiling → re-check against net SE income, repeating until the figures converge, consistent with the adjustments step in `estimate.md`.

## Reconciliation Risk

- **ACA/PTC**: underestimating annual household income when applying for marketplace coverage results in **excess APTC** that must be repaid (clawed back) on **Form 8962** when the return is filed. Repayment is subject to repayment-limitation caps that vary by income tier relative to FPL — caps exist but the dollar figures change yearly; do not cite a specific cap from memory, direct to the **current-year Form 8962 instructions** for the applicable repayment limitation table.
## Never Fabricate Income Figures

MAGI projections must be computed from the client's actual workpapers/data via the skill's income-projection process in `estimate.md` (Gross Income → Adjustments → AGI, per its Computation Order) — then apply the §36B add-backs above to get from AGI to ACA/Medicaid MAGI. Never estimate or fabricate income figures from assumption alone, and never skip straight to a MAGI number without first running (or citing) the underlying `estimate.md` computation that produced the AGI it's built on.

## Output

Deliverable:

1. **MAGI projection workpaper** — computed from actual client data per `estimate.md`'s income-projection process, then adjusted per the §36B add-backs (tax-exempt interest, excluded foreign earned income + housing items, nontaxable Social Security) to produce ACA/Medicaid MAGI. State explicitly whether the figure is a monthly-point-in-time projection (Medicaid) or an annual projection (ACA/PTC), since the same household can need both.
2. **Eligibility threshold comparison** — projected MAGI compared against the relevant program's current-year threshold. Source the threshold from the applicable program's published current-year guidelines (the taxpayer's state Medicaid agency and state marketplace; current-year federal poverty guidelines and Form 8962 tables for ACA PTC) — do not hardcode a threshold number in this file, since FPL tables and program limits update annually.

Always flag "⚠️ verify current-year threshold and subsidy-cliff status before relying on this comparison" alongside the output.

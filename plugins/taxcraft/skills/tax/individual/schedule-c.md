
# Schedule C and Self-Employment

Owns the **unincorporated** sole proprietor. An SMLLC wrapper is
`entities/disregarded.md` (same tax treatment, different records); home office is
`scenarios/home-office-280a.md`; misclassification is `worker-classification.md`;
QBI and loss limits are `loss-limitations.md`.

⚠ **This is the most year-gated module in the individual set** — bonus
depreciation, §179, §174/§174A, and the 1099-K threshold all moved inside
TY2023–2026. Every rate, percentage, limit, and effective date →`authority.md`.

## 1. Profit motive first

§183 sits ahead of everything (`loss-limitations.md` §0). ⚠ Post-suspension of
miscellaneous itemized deductions (**§67(g) for 2018–2025, §67(h) for years
beginning after 12/31/2025** — cite the one matching the year), a "hobby" means
**income with no offsetting expenses at all**. The Reg §1.183-2(b) factors govern;
the three-of-five presumption shifts the burden, it does not decide the case.
Build the record — plan, separate accounts, changed methods after losses — **in
the year**, not at exam.

## 2. SE tax

Base is **92.35%** of net earnings (§1402(a)); the deductible half is a Schedule 1
adjustment. ⚠ Two interactions that get reversed:

- The Social Security portion is capped at the wage base and **W-2 wages fill that
  base first** — a high-wage employee with a side business owes **only Medicare**
  on the SE income. Excess Social Security *withheld* across employers is a
  **credit**, not another tax.
- **Additional Medicare** applies to combined wages and SE income against a
  filing-status threshold (**§1401(b)(2)**), reconciled on Form 8959.

Excluded from SE income: rents from real estate unless services exceed those
customary for occupancy (`loss-limitations.md` §2), and property dispositions.

## 3. Retirement plans

| Plan | The deciding point |
|---|---|
| **SEP-IRA** | Simple, fundable to the extended due date — ⚠ but the balance **counts in the §408(d)(2) aggregation and poisons a backdoor Roth** (`retirement.md` §1) |
| **Solo 401(k)** | Deferral **plus** employer contribution reaches the same total on much less income; allows Roth deferrals and a loan. ⚠ **Three separate deadlines, and the attribution matters:** **SECURE 1.0 §201** (§401(b)(2)) lets a plan **adopted** by the return due date **including extensions** count as adopted on the last day of the year; **SECURE 2.0 §317** additionally lets a **sole proprietor with no employees** make **elective deferrals** for the first plan year to the **unextended** due date. Outside that first-year case a plan adopted after year-end **cannot accept retroactive deferrals** |
| **SIMPLE IRA** | Minimal administration; ⚠ 2-year rollover lock-in (`retirement.md`). SECURE 2.0 raised limits and added Roth SEP/SIMPLE (§601) |
| **DB / cash balance** | Much larger deductions for older, high, stable income; actuary and funding commitment |

⚠ **The employer contribution is not 25% of Schedule C profit** — it is the
reduced rate applied to net earnings **after** the SE-tax deduction, a circular
computation (`estimate.md`). A raw 25% overstates it every time.
⚠ **§603 mandatory Roth catch-up does not reach a sole proprietor with no W-2
wages** — the trigger is prior-year FICA wages.

Employing a spouse doubles plan capacity. The **§3121(b)(3)(A)** family-employment
FICA exemption is owned by `kiddie-dependents.md` §5.

## 4. SE health insurance

**This file owns the deduction.** ⚠ Limited to earned income from **the trade or
business with respect to which the plan is established** — reduced by the §164(f)
half-of-SE-tax deduction and by SE retirement contributions, **not simply "net SE
income."** Unavailable for any month the taxpayer was **eligible** for subsidized
employer coverage, **including a spouse's** — eligibility disqualifies, not
enrollment.

⚠ Also: **Medicare premiums qualify** and the policy may be in the individual's
name; it covers a **child under 27** (§162(l)(1)(D)) regardless of dependency; it
**does not reduce SE tax** (§162(l)(4)); and for a **>2% S-corp shareholder** the
premiums must be in **W-2 box 1** to be deductible at all (Notice 2008-1) — the
most common failure of this deduction.

The §36B circular iteration is `scenarios/aca-medicaid-magi.md` (Rev. Proc.
2014-41 methods) — iterate to convergence, do not approximate.

## 5. Deductions — only the non-obvious

- ⚠ **Auto** — the year-one election locks in: choosing actual with MACRS
  forecloses standard mileage for that vehicle. Standard mileage is also
  unavailable for **five or more vehicles used simultaneously**. §274(d) requires
  contemporaneous records.
- **Meals** — the temporary 100% restaurant provision has expired; entertainment
  remains fully nondeductible (`scenarios/meals-substantiation.md`).
- ⚠ **§195 startup** — phased out dollar-for-dollar above a threshold, remainder
  over 180 months from when the business becomes **active**. The §195(b) election
  is **deemed made** (Reg §1.195-1(b)) — action is needed only to *forgo* it. Costs
  of a business **never commenced** are not deductible at all.
- ⚠ **§179 vs. bonus — both moved.** Bonus phased down under §168(k)(6) across
  2023–2025, and **OBBBA restored 100% for property *acquired* after January 19,
  2025** — an **acquisition-date** cliff. **Two regimes coexist in 2025:**
  property acquired **before** the cutoff stays on the legacy phase-down selected
  by its **placed-in-service** year; property acquired after gets 100%. Record
  **both** dates and the regime. §179 ceiling and phaseout were **raised by OBBBA
  beginning TY2025**. Recapture has two regimes: **§179(d)(10)** at ≤50% business
  use, and **§280F(b)(2)** for listed property.
  ⚠ **§179(b)(3) is the reason the two are not interchangeable:** §179 cannot
  exceed **aggregate taxable income from the active conduct of any trade or
  business** (W-2 wages count), cannot create a loss, and the disallowed amount
  **carries forward indefinitely**. Bonus has no such limit and **can** create a
  loss. Where the business runs at a loss, §179 is disallowed and bonus is not —
  which decides the election. Route the disallowed amount to
  `individual/carryforwards.json` (`1040.md` §5); a partner- or shareholder-level
  §179 limit applies separately (`pass-through.md`).
- ⚠ **§174 / §174A** — domestic R&E had to be **capitalized over 5 years for
  TY2022–2024**; a developer or consultant who deducted it in full for those years
  is wrong. **OBBBA enacted §174A restoring immediate domestic expensing effective
  TY2025**, with a retroactive election for eligible small businesses back to
  TY2022 and an accelerated catch-up. Foreign R&E remains 15-year.
- **1099-NEC obligations** — Schedule C lines I and J; §6721/§6722 exposure is
  independent of income tax (`1040.md` §2).
- ⚠ **The 1099-K threshold whipsawed** — $20,000/200 for TY2023, then
  successively lower, then **OBBBA retroactively restored $20,000/200**. The
  *absence* of a 1099-K means different things in different years; establish the
  governing threshold before treating a missing form as evidence.
- ⚠ **§471(c) is not a license to deduct unsold inventory.** A business meeting
  the §448(c) test may treat inventory as **non-incidental materials and
  supplies**, deductible **when used or consumed** (Reg §1.162-3(a)(1)) — i.e.
  when sold. Functionally COGS, not expensing. **Changing to or from it** is an accounting-method change requiring **Form 3115**
  (an initial method adopted on a first return is not a change); the **§263A exemption** runs
  off the same test.
- **QBI** — a sole proprietorship is a qualified trade or business; ⚠ with no
  employees there are **no W-2 wages**, which caps the deduction above the
  threshold (`loss-limitations.md` §3).

## 6. The S-election question

The tradeoff is narrower than commonly sold: it saves the Medicare portion (and
Social Security only below the wage base) against payroll administration, a
separate return, state minimums, and a **reduced QBI base**. ⚠ **Compute the
breakeven — it depends on the wage base, the QBI reduction, and state minimums.
Do not assume a profit range.** Full analysis: `entities/s-corp.md`.

## 7. Workpaper

`wp-schedule-c.md`:

```json
{
  "business": {"slug": "", "activity_code": "", "accounting_method": "",
               "section_183_profit_motive": null, "factors_documented": [],
               "material_participation": null},
  "income": {"gross_receipts": 0, "forms_1099nec_received": 0,
             "forms_1099k_received": 0, "governing_1099k_threshold": null,
             "reconciled": null},
  "information_returns_issued": {"required": null, "filed": null,
                                 "lines_I_J_answered": null},
  "se_tax": {"net_earnings": 0, "base_92_35": 0,
             "w2_wages_filling_ss_base": 0, "ss_portion": 0,
             "medicare_portion": 0, "additional_medicare_1401b2": 0,
             "deductible_half": 0},
  "retirement": {"plan": "sep|solo401k|simple|db|none",
                 "adopted_by": "", "secure_201_or_317_basis": "",
                 "employee_deferral": 0, "employer_contribution": 0,
                 "reduced_rate_computation_used": null,
                 "sep_balance_affects_408d2": null,
                 "form_5500ez_required": null},
  "se_health": {"premiums": 0, "subsidized_coverage_eligible_months": [],
                "earned_income_limit_this_business": 0,
                "circular_iteration_converged": null, "allowed": 0},
  "assets": [{"asset": "", "acquisition_date": "", "binding_contract_date": "",
              "placed_in_service": "",
              "bonus_regime": "legacy_phasedown_by_pis_year|obbba_100pct_post_2025_01_19",
              "bonus_pct_applied": null, "business_use_pct": null,
              "listed_property": null, "method": "179|bonus|macrs",
              "recapture_regime": "179(d)(10)|280F(b)(2)|none"}],
  "research_expenditures": {"amount": 0, "domestic": null,
                            "regime": "174_capitalize_5yr|174A_expense",
                            "retroactive_election_available": null},
  "inventory": {"section_471c_used": null, "deducted_when_consumed": null,
                "form_3115_filed": null},
  "auto": {"method": "standard|actual", "first_year_method": "",
           "locked_out_of_standard": null, "fleet_5_or_more": null,
           "substantiation_274d": null},
  "qbi": {"sstb": null, "w2_wages": 0, "ubia": 0}
}
```

**Invariants:** profit motive addressed before any loss; gross receipts ≥ Σ
1099-NEC and 1099-K received with differences explained **against the governing
threshold**; the outbound 1099 question answered; the employer retirement
contribution uses the reduced-rate computation and a post-year-end adoption is
tested against SECURE 1.0 §201 vs. SECURE 2.0 §317 before any deferral is claimed;
SE health tested for subsidized eligibility **by month** and iterated to
convergence; depreciation records **both** acquisition and placed-in-service dates
and names the bonus regime; R&E assigned to §174 or §174A by year; §471(c) not
used to deduct unsold inventory.

Verify with a licensed practitioner before filing.

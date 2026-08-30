
# Health Accounts and Medicare

Owns HSAs, FSAs, and IRMAA. PTC and Medicaid MAGI →
`scenarios/aca-medicaid-magi.md`; coverage transitions at job loss →
`job-loss.md`; the SE health insurance **deduction** → `schedule-c.md` §4.

Limits, HDHP minimums, and IRMAA brackets → `authority.md`.

## 1. HSA — eligibility is monthly

Tested **per month, on the first day**. ⚠ Disqualifiers people miss:

- **Any** other non-HDHP coverage — including a **spouse's general-purpose FSA**,
  which covers the taxpayer and therefore disqualifies them even if they are not
  on the spouse's plan. A **limited-purpose** or post-deductible FSA does not.
- ⚠ **The taxpayer's own FSA disqualifies too.** A health FSA **carryover**
  balance disqualifies for **every month of the following plan year**, and a
  **grace period** disqualifies through the grace months (Rev. Rul. 2004-45;
  Notice 2005-86) — unless converted to limited-purpose or the balance is $0 at
  year end. **The most common real-world HSA disqualification.**
- ⚠ **Medicare — the disqualifier is enrollment or entitlement, not
  eligibility.** A 67-year-old still working under an employer HDHP who has **not**
  filed for Social Security or Part A remains fully eligible — the answer for the
  entire still-working-past-65 population. Anyone **taking Social Security** at or
  after 65 is auto-enrolled in Part A. On later enrollment Part A is retroactive by
  the **lesser of six months or back to the month of turning 65**, so the "stop
  six months early" rule applies at 65½ or later; someone enrolling at 65 + 3
  months gets three retroactive months.
- Being claimed as a dependent; VA benefits within the lookback (service-connected
  exception).

**Family vs. self-only** is set by the HDHP coverage, not who is enrolled. Spouses
with family coverage share one family limit; ⚠ each may add a catch-up — **which
begins at 55, not 50** — only to their **own** HSA. ⚠ Where one spouse is on
Medicare the other may still contribute the **full family limit** to their own
HSA, and an **adult child on a parent's family HDHP who is not a tax dependent**
may open their own and contribute the full family limit.

⚠ **Last-month rule** — full-year contribution if eligible on December 1, but the
**testing period runs through the end of the following year**; failing it makes
the excess includible **plus 10%**, in the later year. **Carry the testing period
into the next year's workpaper** — this surfaces a year late.

⚠ **Contributions are due by the *unextended* return due date** — an extension
does **not** extend the HSA deadline. (Contrast a SEP, which *is* fundable to the
extended due date — `schedule-c.md` §3 — which is the wrong analogy to draw.) An
excess contribution not withdrawn with its net income attributable by that date
carries the **§4973 6% excise per year until corrected**.

⚠ **Embedded-deductible trap** — a family HDHP with an individual embedded
deductible below the statutory family minimum is not a qualifying HDHP at all.

Other mechanics: substantiation is the taxpayer's, not the custodian's; ⚠ a
**non-qualified distribution is includible plus a 20% penalty** (§223(f)(4)(A)) —
**not 10%** — waived at 65, death, or disability. ⚠ Expenses may be **reimbursed
years later** if the expense post-dates the HSA's establishment and was never
otherwise deducted, which makes an unreimbursed receipt file a real asset. The
one-time **§408(d)(9)** IRA-to-HSA funding distribution must be trustee-to-trustee,
**counts against** (not on top of) the year's limit, and carries its **own
13-month testing period**. At death an HSA to a non-spouse is taxable to the
beneficiary, reduced by the decedent's qualified expenses paid within 12 months;
naming the **estate** puts it on the final return.

⚠ **Year-gates inside the window:** the **telehealth safe harbor** ran through
plan years beginning before 1/1/2025, **lapsed** for 2025, then OBBBA made it
**permanent retroactive to plan years beginning after 12/31/2024** — a 2025 plan
year reconstructed without this gets it wrong twice. **OBBBA effective 1/1/2026:**
bronze and catastrophic Exchange plans treated as HDHPs (§223(c)(2)(H)), and
direct primary care arrangements below a monthly threshold are not disqualifying
coverage with DPC fees qualified.

## 2. FSA

Use-it-or-lose-it with either a carryover **or** a grace period, never both.
Dependent-care FSA coordinates with Form 2441 and has its **own §129 earned-income
limit** (`credits.md` §3). HRA/ICHRA/EBHRA variants affect PTC eligibility →
`scenarios/aca-medicaid-magi.md`.

## 3. IRMAA

Part B **and** Part D surcharges based on MAGI from **two years prior**
(SSA §1839(i); §1860D-13(a)(7)).

⚠ **This file owns the definition: IRMAA MAGI is AGI plus tax-exempt interest**
(SSA §1839(i)(4)) — per the register in `1040.md` §4. ⚠ SSA uses the **most
recent return available**, so a late filing produces a **three**-year lookback,
and an amended return supports a redetermination request separate from SSA-44.

⚠ It is a **cliff, not a phaseout** — one dollar over a bracket costs the full
step, for both spouses, for twelve months. And it is **retrospective**: a
conversion or one-time gain today raises premiums two years out, when the income
is gone. Model the IRMAA cost into any conversion (`retirement.md` §6).

**Form SSA-44** appeals on a **life-changing event** — work stoppage or reduction,
marriage, divorce, death of a spouse, loss of pension, employer settlement. A
retirement in the current year is the paradigm case and is routinely not appealed.
⚠ **A one-time capital gain is not a qualifying event.**

## 4. Long-term care

**§7702B** premiums are deductible subject to an **age-based per-person cap**;
benefits are excludable to a per-diem limit (Form 1099-LTC). The Schedule A
medical deduction itself is `itemized.md`.

## 5. Workpaper

`wp-health.md`:

```json
{
  "hsa": {"eligibility_by_month": [], "coverage_type": "self|family",
          "spouse_general_purpose_fsa": null,
          "own_fsa_carryover_or_grace": null,
          "medicare_enrolled_or_entitled": null,
          "medicare_retroactive_months": null,
          "hdhp_embedded_deductible_ok": null,
          "catch_up_age_55_eligible": null,
          "contributions": {"employer_w2_box12_W": 0, "taxpayer": 0, "total": 0},
          "limit": null, "excess": 0,
          "last_month_rule_used": null, "testing_period_ends": null,
          "distributions": 0, "qualified": 0,
          "nonqualified_distribution": 0, "penalty_20pct": 0,
          "ira_funding_distribution_408d9": {"amount": 0,
                                             "testing_period_ends": null}},
  "fsa": {"health_fsa": 0, "carryover_or_grace": "", "dependent_care_w2_box10": 0},
  "irmaa": {"determination_year": null, "magi_year_used": null,
            "most_recent_return_available_year": null,
            "magi_label": "MAGI (IRMAA, TY-2)", "magi_value": null,
            "add_backs": ["tax_exempt_interest"],
            "bracket": "", "part_b_surcharge": 0, "part_d_surcharge": 0,
            "life_changing_event": null, "ssa_44_filed": null,
            "projected_impact_of_current_year_income": 0},
  "ltc": {"premiums": 0, "age_based_cap": null, "benefits_1099ltc": 0},
  "se_health_insurance": {"owner": "schedule-c.md §4"}
}
```

**Invariants:** HSA eligibility recorded **month by month**; Medicare tested on
**enrollment or entitlement**, not eligibility, with retroactive Part A months
computed; **both** the spouse's and the taxpayer's own FSA tested; the last-month
and §408(d)(9) testing periods carried into the **following** year's workpaper;
employer HSA contributions taken from **W-2 box 12 code W**, not the 5498-SA; a
non-qualified distribution uses **20%**; IRMAA records its label, add-backs, the
return year SSA actually used, and the current year's projected two-year-out
impact.

Verify with a licensed practitioner before filing.

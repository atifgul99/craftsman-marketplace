
# Credits and Dependents

Owns dependent qualification and the individual credit set. Education credits →
`education.md`; PTC → `scenarios/aca-medicaid-magi.md`; §6654 →
`withholding-penalties.md`.

⚠ All amounts, phaseouts, refundability, and **termination dates** →
`authority.md`. §5 goes stale fastest.

## 1. Dependents — where errors actually are

- ⚠ **Dependent parents.** A parent is a QR **without living with the taxpayer**,
  and is the usual path to **HoH** for an unmarried filer supporting a parent
  elsewhere. The §152(d)(1)(B) test uses **gross income as defined in §61** — it
  is **not** reduced by the standard deduction or any deduction. A parent on
  Social Security usually passes because the benefit is **excluded under §86**,
  not because deductions reduce it. Do not subtract a standard deduction from a
  parent's IRA distributions and conclude the test is met.
- **§152(b)(3)** citizenship/residency: US, Canada, or Mexico.
- ⚠ **§152(f)(5)** — a **scholarship is excluded from support** for a student
  child, which is usually what keeps a scholarship student a dependent
  (`education.md`).
- ⚠ **Form 2120 multiple support (§152(d)(3))** requires **all four**: no one
  person over 50%; the group together over 50%; **the claimant over 10%**; and
  every other person over 10% signs a waiver. The **>10% claimant floor** is the
  condition people fail. Annual election.
- ⚠ **§152(e) / Form 8332 — what moves and what does not.** The custodial parent
  controls the dependency and must release it in writing; a decree alone does not
  bind the IRS for post-2008 decrees. Attach the release **every year** (via Form
  8453 on e-file); a multi-year release is revocable only under Part III,
  effective no earlier than the year **after** written notice.
  - **The release moves:** the **dependency** and the **CTC/ACTC/ODC**. Nothing
    else.
  - **Follows as a consequence, not as a released item:** the **§25A education
    credits** — §25A keys to whoever claims the student, and §25A(g)(3) treats the
    student's payments as made by that taxpayer. State it that way; do not
    describe §25A as something Form 8332 transfers.
  - **Stays with the custodial parent:** **HoH**, **EITC**, and the
    **dependent-care credit and §129 exclusion**.
  - ⚠ **Available to BOTH parents:** the **medical expense deduction**.
    **§213(d)(5)** treats a child of divorced or separated parents receiving over
    half of support from the parents as a dependent of **each** parent for §213,
    so each deducts what that parent actually paid, regardless of Form 8332
    (`itemized.md`).
- Medical expenses of a person failing **only** the gross-income or joint-return
  test remain deductible by the supporter (§213(a), §152(b)).
- ⚠ **SSN timing is credit-specific, not universal.** An SSN **issued by the due
  date including extensions** is required for the **§24 CTC (the child's)** and
  **§32 EITC** (taxpayer, spouse, qualifying children); OBBBA added a **taxpayer**
  SSN requirement for the CTC. **An ITIN is sufficient** for the **§24(h)(4)
  ODC**, **§25A**, and **§21** — it need only be issued by the due date. Do not
  apply a blanket ITIN disqualification.
- Tie-breakers where two taxpayers can claim the same child.

## 2. CTC and ODC

Both §24; ODC is the fallback for a qualifying relative or a child without a
qualifying SSN. ⚠ Verify per year: per-child amount, the refundable ACTC and its
earned-income formula, phaseouts, and the SSN requirements — OBBBA changed several.

## 3. Dependent care — two separate limits

The **§21 credit** requires earned income by both spouses on a joint return, with
the student/disabled-spouse imputation.

⚠ **The §129 FSA exclusion has its own, different limit: the lesser of the two
spouses' earned income.** A spouse with no earned income makes the **entire** FSA
balance taxable wages through Form 2441 Part III — the most common 2441 failure,
and not the same rule as the §21 requirement.

Coordinate: the same dollars cannot do both, and the FSA reduces the §21 expense
base (W-2 box 10). Provider TIN required; a missing one needs documented due
diligence. ⚠ **Year-gate:** for years beginning after 12/31/2025 OBBBA raises the
§21 percentage with a new phase-down **and** raises the §129 exclusion.

## 4. Adoption, saver's, EITC

- ⚠ **Adoption (§23) — the timing rule is the trap.** For a **domestic** adoption,
  expenses paid *before* the year of finality are creditable in the **following**
  year; expenses paid in or after the year of finality are creditable when paid.
  For a **foreign** adoption, **no credit until final**. Nonrefundable with a
  five-year carryforward through TY2024; **OBBBA made a portion refundable for
  years beginning after 12/31/2024** (and the refundable portion does not carry
  forward). Special-needs adoptions claim the full amount regardless of expenses.
  **§137** employer assistance cannot cover the same dollars.
- **Saver's credit (§25B)** applies **through TY2026**; SECURE 2.0 §103 replaces
  it with the **Saver's Match** — a government contribution to the account, not a
  credit — for years beginning after 12/31/2026. Every supported year is still
  §25B.
- ⚠ **EITC** — investment-income disqualifier, and the permanent **§32(d)(2)**
  rule allowing a **married taxpayer filing separately** who lived apart the last
  six months (or is separated under a written instrument) with a qualifying child
  to claim it. The categorical "MFS is ineligible" answer is **wrong**. §32(k)
  imposes a 2- or 10-year ban after a reckless or fraudulent disallowance.
- ⚠ **Form 8862** is required after **any** disallowance other than math or
  clerical error, and applies to **CTC/ACTC/ODC and AOTC** as well as EITC.
- ⚠ **The PATH Act refund hold (§6402(m)) reaches only EITC and ACTC** — not the
  nonrefundable CTC and not the AOTC.

## 5. Energy and vehicle credits — check the triggering event first

⚠ OBBBA terminated these mid-window, and **each uses a different triggering
event**. Grouping them under one date is the error.

| Credit | Termination trigger | Note |
|---|---|---|
| **§25C** | Property **placed in service** after 12/31/2025 | Annual (not lifetime) cap with per-item sublimits. The **manufacturer PIN** requirement applies to specified property placed in service after 12/31/2024 — TY2025 only in this window |
| **§25D** | **Expenditures made** after 12/31/2025 | Percentage-based with carryforward; no cap **except fuel cell** (per half kW, §25D(b)). ⚠ §25D(e)(8) treats an expenditure as made when **installation is completed** — a paid-2025 / installed-2026 project fails |
| **§30D** new, **§25E** used | Vehicles **acquired** after 9/30/2025 | ⚠ "Acquired" = **binding written contract plus payment**; the vehicle may be **placed in service later** and still qualify. Consumer MAGI caps use the **lesser of** current or prior year; point-of-sale **transfer to the dealer** creates recapture if the cap is exceeded |
| **§30C** | Property **placed in service** after 6/30/2026 | The only one alive for part of TY2026 |

⚠ **§45W** (commercial clean vehicle) is a **§38 general business credit** with
its own carryback and carryforward — not an individual nonrefundable credit, and
it carries **neither** the consumer MAGI cap nor the dealer-transfer mechanics.
Not handled here → `schedule-c.md` or the entity side.

Establish the **triggering event and its date** before any amount; a 2025
transaction can fall on either side depending on which event governs.

## 6. Ordering

Nonrefundable credits are limited to liability and applied in the form's order;
some carry forward and some do not. Refundable credits and payments are separate
(`1040.md` §2). **Never let a nonrefundable credit produce a refund.**

## 7. Workpaper

`wp-credits.md`:

```json
{
  "dependents": [{"name_slug": "", "relationship": "", "dob": "",
                  "test": "QC|QR", "months_in_home": null,
                  "support_over_half": null,
                  "gross_income_61_test_met": null,
                  "citizenship_152b3": null, "scholarship_excluded_152f5": null,
                  "ssn_or_itin": "", "issued_by_due_date": null,
                  "form_8332_released": null, "form_2120_over_10pct": null,
                  "credits_claimed": []}],
  "credits": [{"credit": "", "code_section": "", "amount": 0,
               "refundable": null,
               "magi_label": "MAGI (§24) | MAGI (§23) | n/a",
               "magi_value": null, "add_backs": [],
               "phaseout_applied": 0, "carryforward_out": 0,
               "authority_id": ""}],
  "dependent_care": {"section_21_credit": 0, "both_spouses_earned_income": null,
                     "section_129_exclusion": 0,
                     "section_129_earned_income_limit": 0,
                     "excess_to_wages_part_III": 0, "provider_tin": ""},
  "energy_vehicle": [{"credit": "25C|25D|30D|25E|30C",
                      "triggering_event": "placed_in_service|expenditure_made|acquired",
                      "expenditure_date": "", "contract_date": "",
                      "payment_date": "", "acquisition_date": "",
                      "placed_in_service_date": "",
                      "qualifies_under_triggering_event": null,
                      "manufacturer_pin": "", "pin_required": null, "vin": "",
                      "consumer_magi_cap_applies": null,
                      "magi_test_year_used": "current|prior",
                      "point_of_sale_transfer": null, "recapture_risk": null}],
  "eitc": {"claimed": null, "mfs_32d2_basis": null,
           "prior_disallowance": null, "form_8862_required": null}
}
```

**Invariants:** every dependent-driven credit names the test it satisfies and the
SSN/ITIN timing result; a Form 8332 release moves only the dependency and
CTC/ACTC/ODC, with HoH, EITC, and dependent care staying, medical available to
**both** under §213(d)(5), and §25A following the dependency claim as a
consequence; §21 and §129 are limited **separately**; every energy or vehicle
credit records its **triggering event and that event's date** before any amount;
each MAGI-limited credit records its register label and add-backs, not a bare
phaseout; nonrefundable credits never exceed liability.

Verify with a licensed practitioner before filing.

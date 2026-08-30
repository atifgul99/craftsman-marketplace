
# Job Loss, Severance, and Unemployment

Owns the separation year. It is a **planning** file as much as a compliance one —
a low-income year is the most valuable tax window most people get, and it is
usually wasted.

All rates, amounts, and dates → `authority.md`.

## 1. What arrives

| Item | ⚠ The trap |
|---|---|
| **Severance, PTO, bonus** | Wages, FICA-subject. Withheld at the flat supplemental rate — usually **below** the marginal rate, **except** that supplemental wages **above $1M in the year are withheld at a mandatory top rate (§3402(g))**, which over-withholds. **A negotiated severance paid in installments is §409A deferred comp** unless it fits the short-term deferral rule or the **separation-pay safe harbor** (Reg §1.409A-1(b)(9)(iii)); a failure costs the employee immediate inclusion plus a **20% additional tax and premium interest**. **This is the structuring item — before signing.** SUB-plan payments tied to state UI are **not FICA wages** (Rev. Rul. 90-72) |
| **Unemployment** | Fully taxable federally; 1099-G. **No withholding unless Form W-4V is filed, and W-4V allows only 10%** on unemployment. Many states exempt it |
| **Equity** | **§422(a)(2): an ISO must be exercised while employed or within three months of termination** to keep ISO status (12 months for §22(e)(3) disability, no limit for death). **The plan's post-termination exercise period is a separate contractual term and is often longer — a 10-year PTEP does not extend §422.** Nothing "converts": exercise outside the window is simply taxed as an NSO. Exercising inside it to preserve ISO status creates **AMT on the spread with no cash** → `scenarios/equity-comp.md` |
| **Settlement** | Character follows the **claim**. **Punitive damages are always taxable** even in a physical-injury case; emotional distress without physical injury is excludable only to the extent **paid for medical care**; **pre- and post-judgment interest is always taxable**. The **gross** amount is includible even where counsel is paid directly (*Comm'r v. Banks*, 543 U.S. 426 (2005)), and fees are **not deductible** post-TCJA except under the §62(a)(20)/(21) above-the-line deductions. A bona fide allocation among claims is generally respected — **structure before signing** |
| **1099-G box 2** | State refund taxable only to the extent of prior-year benefit (§111) → `itemized.md` |
| Outplacement | Working-condition fringe only if there is no cash-or-services choice |

## 2. The retirement decision

⚠ The default — roll everything to an IRA — is frequently wrong.

- **Leave it / roll to the new plan** — preserves the §408(d)(2) workaround for a
  backdoor Roth (`retirement.md` §4) and ERISA creditor protection.
- ⚠ **Roll to an IRA** — **destroys two things permanently**: the age-55
  separation exception and **NUA** on employer stock.
- **Convert to Roth** — usually the best year (§4).
- **Cash out** — taxable plus penalty, and a plan distribution to the participant
  carries **20% mandatory withholding** (§3405(c)).
- **Convert after-tax 401(k) basis to Roth** under Notice 2014-54 — separation
  makes this newly available and it is routinely overlooked.

⚠ **Two hard deadlines:**

- **Age-55 exception — what must occur in or after the year of turning 55 is the
  *separation from service*, not the distribution.** Separate at 53 and distribute
  at 56: **no exception**. Separate at 55: distributions any time after. Applies
  only to the plan of the employer just separated from (50 for qualifying
  public-safety roles), never to IRAs, and **an IRA rollover forfeits it**. A
  governmental **§457(b)** plan is outside §72(t) entirely (§72(t)(9)).
  Mechanics: `retirement.md` §3.
- **Plan loan** — an outstanding loan at separation becomes a **qualified plan
  loan offset**, rollable by the **return due date including extensions**
  (§402(c)(3)(C)). An ordinary offset gets 60 days; a §72(p) **deemed
  distribution cannot be rolled at all**. Establish which it is.

## 3. Health coverage

⚠ The tax consequences diverge sharply, and two rules make the comparison
possible:

- **COBRA premiums are payable tax-free from an HSA** (§223(d)(2)(C)(i)), as are
  **any health insurance premiums during a period of unemployment compensation**
  (§223(d)(2)(C)(iii)). These are the **only two** circumstances in which an HSA
  pays insurance premiums, and both are job-loss-specific — so an HSA balance is a
  live funding source on the COBRA side.
- **Being *offered* COBRA does not bar the PTC — only actual enrollment does**
  (Reg §1.36B-2(c)(3)(iv)). ⚠ **The trap: voluntarily dropping COBRA mid-year is
  not a special enrollment event** (only exhaustion is), so electing COBRA first
  can lock the taxpayer out of the marketplace until open enrollment.
- **§72(t)(2)(D)** — penalty-free **IRA** distributions for health insurance
  premiums after **12 consecutive weeks** of unemployment. The answer to the "no
  cash for COBRA" problem.
- Compare **total cost**, not premium.
- A mid-year income drop changes **§36B MAGI for the whole year**, producing a
  large PTC at reconciliation — or a **repayment** if income recovers. **Medicaid
  is measured on current monthly income**, so eligibility can begin immediately
  even where annual income is high. The two clocks differ →
  `scenarios/aca-medicaid-magi.md`.
- **HSA eligibility breaks** when HDHP coverage ends — test month by month and
  watch the testing period (`health-benefits.md`).
- Losing coverage is a **special enrollment** event with a limited window.

## 4. The planning window

⚠ These compete for the same bracket space — model them **together**:

- **Roth conversion** at an unusually low marginal rate — the largest
  opportunity. Fill to the top of a target bracket.
- **Capital gain harvesting** at 0% if taxable income is low enough.
- **Exercising NSOs or ISOs** into a low bracket / low AMT year.
- ⚠ **Releasing suspended passive losses is usually backwards here.** A §469(g)
  release into a low-income year converts the excess to an NOL subject to the §172
  percentage limitation and loses the time value. Usually **defer** the
  disposition → `loss-limitations.md`.

⚠ Bounded by: **PTC and Medicaid eligibility** (a conversion can cost more in lost
subsidy than it saves), **IRMAA two years out** if near 63+, and **FAFSA** income
lookback with a child approaching college. Sequence deliberately in `review.md`,
not in December.

## 5. Estimates

Withholding stops with the paycheck, unemployment has none by default, and
severance is under-withheld — the taxpayer is often suddenly in an
estimated-payment posture for the first time.

**The safe-harbor choice is owned by `withholding-penalties.md` §2.** The
job-loss-specific tension: the prior-year safe harbor is *safe* but *expensive* in
a falling-income year because it is measured against a high prior year; the
current-year test or annualized method is *cheaper* but needs a reliable
projection. Where cash is tight that usually favors current-year or annualized.

## 6. Workpaper

`wp-job-loss.md`:

```json
{
  "separation": {"employer_slug": "", "date": "", "age_at_separation": null,
                 "separation_in_or_after_age_55_year": null},
  "income": {"severance": 0, "pto_payout": 0,
             "supplemental_withholding_rate_applied": null,
             "section_409a_reviewed": null, "sub_plan_payments": 0,
             "unemployment_1099g": 0, "w4v_filed": null,
             "state_taxes_unemployment": null,
             "settlement": {"amount": 0, "character": "", "punitive": 0,
                            "interest": 0, "attorney_fees": 0,
                            "above_line_62a20_21_available": null}},
  "equity": {"unvested_forfeited": 0, "accelerated": 0,
             "iso_422a2_window_ends": "", "plan_ptep_ends": "",
             "amt_exposure": 0},
  "retirement": {"plan_balance": 0,
                 "decision": "leave|roll_new_plan|roll_ira|convert|cash",
                 "age_55_forfeited_by_rollover": null, "nua_evaluated": null,
                 "after_tax_basis_to_roth_notice_2014_54": 0,
                 "loan_offset": {"type": "qualified_offset|offset|deemed",
                                 "rollover_deadline": ""}},
  "coverage": {"option": "cobra|marketplace|spouse|medicaid",
               "cobra_offered_not_enrolled": null, "cobra_payable_from_hsa": null,
               "section_72t_2D_available": null,
               "dropping_cobra_is_not_sep": null,
               "ptc_projected": 0, "repayment_risk": null,
               "hsa_eligibility_ends": "", "testing_period_open": null},
  "planning": {"target_bracket": "", "roth_conversion_modeled": 0,
               "zero_pct_gain_harvest": 0, "passive_release_deferred": null,
               "ptc_or_medicaid_constraint": null, "irmaa_two_year_impact": 0}
}
```

**Invariants:** the age-55 exception is evaluated **before** any rollover is
executed, on the **separation** date; the ISO window is tested against
**§422(a)(2)'s three months**, not the plan's exercise period; a plan loan is
classified as qualified offset vs. offset vs. deemed with its deadline;
unemployment withholding status recorded; a Roth conversion modeled against
PTC/Medicaid and IRMAA, not federal tax alone; settlement character, §409A, and
fee deductibility addressed **before signing**.

Verify with a licensed practitioner before filing.

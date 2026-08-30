
# Withholding, Estimates, and Penalty Engineering

Owns the **planning** layer over §6654: arranging withholding and estimates so the
penalty is zero at the lowest cost, and repairing a year after the fact.

§6654 computation, safe harbors, and installment mechanics → `quarterly.md`
through `close-estimate.md`. **Payment execution is never authorized here.**
Percentages, thresholds, and the interest rate → `authority.md`.

## 1. The asymmetry that drives everything

⚠ **Withholding is deemed paid ratably across the year regardless of when it was
actually withheld (§6654(g)). An estimate counts when made.**

That single fact is the most useful lever in individual tax planning: a large
**December** withholding is treated as though a quarter of it was paid in April
and can cure an underpayment **for the entire year**, while the same dollars paid
as a Q4 estimate cure only Q4. So when an underpayment is discovered late, the fix
is almost always **withholding**, not an estimate.

| Vehicle | Note |
|---|---|
| **Form W-4** | Extra flat amounts on line 4(c) for the remaining periods |
| **IRA or plan distribution** | Elect high withholding and roll the **gross** amount back within 60 days from other funds — the withheld tax is deemed ratable while the account is made whole. ⚠ Watch the one-per-year rollover limit (`retirement.md`), and under 59½ the withheld portion is itself a taxable distribution unless replaced |
| **W-4P / W-4R** | Pensions and non-periodic distributions |
| ⚠ **W-4V** | Voluntary withholding on **unemployment** (only **10%** permitted) and Social Security — unemployment has **none** by default (`job-loss.md`) |
| **Spouse's W-4** | On a joint return either spouse's withholding covers the couple |

The taxpayer may also **elect actual-date treatment** for withholding where a
large early-year withholding is better placed than a ratable quarter. It is an
election and applies to **all** withholding for the year.

## 2. Choosing a safe harbor

⚠ Choose deliberately; do not default.

| Approach | When |
|---|---|
| **Prior-year** (100%, or the higher percentage above the AGI threshold) | Income **rising or unpredictable**. Its virtue is that it is a **fixed, knowable number** the year's outcome cannot break. Requires the prior year to have been a **12-month year with a liability** |
| **Current-year 90%** | Income **falling sharply** — but it requires a reliable projection, which a volatile year lacks |
| **Annualized income installment (Form 2210 Schedule AI)** | Income is **lumpy** — a Q3 gain, a Q4 K-1, an exercise, a business sale |

⚠ **The falling-income tension** (`job-loss.md` §5): prior-year is *safe* but
*expensive* because it is measured against a high prior year; current-year or
annualized is *cheaper* but needs a projection. Where cash is tight that usually
favors current-year or annualized.

⚠ The prior-year figure must be the **exact filed-return line** required by
`quarterly.md` — a generic "total tax" is not acceptable, and an **amended prior
year changes it**. A first-year filer has **no** prior-year safe harbor; use the
current-year test and record the absence as a fact, not a defect (`1040.md` §8).

## 3. Form 2210

⚠ Not merely a penalty computation — it is where the penalty is **avoided**.

- **Schedule AI** annualizes by period, so a taxpayer who earned nothing until Q4
  has small early required installments. It requires income **and deductions by
  period**, which is why quarterly income summaries are worth keeping even when
  not paying quarterly.
- ⚠ **Schedule AI is not a third safe harbor** — it lowers a period's required
  installment subject to the form's catch-up mechanics; the controlling figure is
  the Form 2210 result after applying available alternatives.
- **Waivers (§6654(e)(3))** for casualty, disaster, or other unusual circumstances
  where the penalty would be inequitable, and for a taxpayer who **retired after
  62 or became disabled** in the year or the preceding year, where the
  underpayment was due to reasonable cause. Requested on Form 2210 with a
  statement.
- **De minimis** where the balance after withholding and credits is below the
  statutory amount, or where there was no prior-year liability and the prior year
  was a full 12 months.
- **Farmers and fishermen** have their own percentage and a single installment date.

⚠ The penalty is **interest-like** — federal short-term plus a statutory margin,
per period — and is **not deductible**. It is not a fine, and it is sometimes
cheaper than borrowing. That is a decision to make **explicitly** in `review.md`,
not by accident.

## 4. Failure patterns

| Pattern | Fix |
|---|---|
| ⚠ **RSU vesting withheld at the supplemental rate** while the taxpayer is in a higher bracket | Structural under-withholding at every vest — add W-4 line 4(c) sized to the gap (`scenarios/equity-comp.md`) |
| **Large Q4 gain or Roth conversion** | Withhold from a distribution (§1), or run Schedule AI |
| **First year of self-employment** | No withholding exists at all — set up estimates immediately (`schedule-c.md`) |
| **K-1 arriving after year end** | The **prior-year** safe harbor is immune to a K-1 surprise |
| **Unemployment** | No default withholding — W-4V (10%) or estimates (`job-loss.md`) |
| **Two-earner household** | Each W-4 computed in isolation under-withholds jointly — use the W-4 Step 2 worksheet |
| **A large refund every year** | Not an error, but an interest-free loan. Surface it as a finding — with the caveat that a taxpayer who values the forced saving may reasonably decline |
| ⚠ **Prior-year overpayment applied forward** | Credited as of the **original due date** of the prior-year return, making it the earliest-dated payment available — often better than a refund plus a Q1 estimate |

## 5. Interactions

⚠ **State estimates run on their own calendars and safe harbors**, frequently
different from federal (`state-residency.md`). Nonresident state withholding and
composite payments on a K-1 are credits that may already cover a state obligation
(`pass-through.md`). Entity-level §6655 is a different regime (`quarterly.md`).
⚠ **§6654 is separate from §6651 failure-to-file and failure-to-pay** — curing one
does not cure another (`1040.md` §1 Step 0).

## 6. Workpaper

`wp-payments.md`:

```json
{
  "prior_year": {"total_tax_line": null, "agi": null,
                 "twelve_month_year": null, "had_liability": null,
                 "amended_since": null,
                 "safe_harbor_pct_applicable": null, "safe_harbor_amount": null},
  "current_year": {"projected_tax": null, "ninety_pct_amount": null},
  "method_selected": "prior_year | current_year | annualized_AI",
  "withholding": [{"source": "", "amount": 0, "date": "",
                   "treated_as": "ratable_6654g | actual_date_election"}],
  "estimates": [{"period": "Q1|Q2|Q3|Q4", "due_date": "", "paid_date": "",
                 "amount": 0}],
  "prior_year_overpayment_applied": {"amount": 0, "credited_as_of": ""},
  "required_installments": [{"period": "", "required": 0, "paid": 0,
                             "shortfall": 0}],
  "form_2210": {"required": null, "schedule_ai_used": null,
                "period_level_income_support": null,
                "waiver_requested": null, "waiver_ground": "",
                "penalty_computed": 0, "penalty_accepted_as_decision": null},
  "state_estimates": [{"state": "", "safe_harbor_basis": "", "paid": 0}],
  "planning_findings": []
}
```

**Invariants:** the prior-year safe harbor uses the **exact filed-return line**,
and an amended prior year updates it; withholding is characterized as ratable or
actual-date with the election recorded once for the year; required installments
are tested **by period**, not annually; a first-year filer records the absence of
a prior year as a fact; Schedule AI is used only with period-level income support;
any penalty accepted as cheaper than the alternative is recorded as an explicit
decision in `review.md`.

Verify with a licensed practitioner before filing.

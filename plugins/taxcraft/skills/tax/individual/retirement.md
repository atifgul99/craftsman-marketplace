
# Retirement Accounts and IRA Basis

Owns the **required-input gates**, the **lifetime basis custody**, and the
verified traps for IRAs and employer plans. General retirement doctrine is left
to the model.

**Verify at point of use** (`authority.md`): every limit, phaseout, RMD age,
catch-up tier, QCD cap, and §402(g) amount — **and** every ⚠ proposition below.
SECURE 2.0 phases provisions in across 2023–2026 and the 2024 final regulations
changed inherited-account rules; §5 is the year map.

A prohibited transaction deems the **entire IRA distributed** on 1/1 of the
violation year → `scenarios/self-directed-ira.md`.

---

## 1. Required-input gates

**No aggregate balance, no conversion conclusion.** Its absence is a hold, not a
zero.

| Gate | Rule |
|---|---|
| **§408(d)(2) aggregation** | All traditional, SEP, and SIMPLE IRAs **of one individual** are a single account for every distribution and conversion computation. Roth IRAs are outside it (§408A(d)(4)(A)) — including **Roth SEP/SIMPLE** (SECURE 2.0 §601), despite the label. Employer plans are outside it, which is the whole mechanic behind the reverse rollover. **Per individual, never per return** — MFJ means two aggregations and two Forms 8606. |
| **Pro-rata denominator** | ⚠ Aggregate year-end value **+ outstanding rollovers and recharacterizations + distributions + conversions during the year**. The ratio applies to **conversions and other distributions together**, and the numerator **includes the current-year nondeductible contribution**. That inclusion is the arithmetic of the backdoor Roth. Reconcile the year-end value to **Form 5498 box 5**, which arrives in May — after most returns are filed. |
| **Active-plan status** | W-2 **box 13** gates §219(g) deductibility. A contribution neither deductible **nor recorded as basis** is taxed twice. |
| **Inherited-account facts** | Decedent, date of death, **whether the account is a Roth**, beneficiary class, and whether death was **on or after the RBD** (the statutory test — not whether RMDs were actually taken). |

## 2. Lifetime basis custody

Two SSOTs, both **per individual**, both appended to and never recomputed
(`1040.md` §5):

- `records/basis/form-8606-basis.md` — nondeductible IRA basis. ⚠ Transcripts do
  **not** show Form 8606; reconstruction needs Form 4506 copies plus 5498s.
  Prior-year 8606s may be filed **standalone**. §6693(b) penalties apply for
  non-filing and for overstating basis.
- `records/basis/roth-basis.md` — contribution basis, conversion layers by year,
  and both clocks. **None of this is on Form 8606 Part I**; Part III is where
  non-qualified Roth distributions and the ordering are actually applied.

## 3. Verified traps

Here because a competent model gets them wrong.

| ⚠ Trap | Rule |
|---|---|
| **Two Roth clocks, and five years is not enough** | §408A(d)(2)(B) qualified-distribution clock (one per person, from 1/1 of the first year **for which** a contribution was made) vs. §408A(d)(3)(F) conversion clock (per conversion year). A qualified distribution needs the clock **and** a §408A(d)(2)(A) event — 59½, death, disability, or first-time home. Ordering: contributions → conversions (oldest first) → earnings. The conversion clock is moot once §72(t) would not apply. |
| **Inherited Roth: no annual RMDs in years 1–9** | A Roth owner is **always treated as dying before the RBD** (Reg §1.408A-6 Q&A-14(b), carried into the 2024 final regs). The at-least-as-rapidly rule never engages, so a designated beneficiary need only empty by year 10. An EDB may still stretch. The beneficiary **inherits the decedent's clock**. That usually favours letting it ride the full ten years — but the EDB life-expectancy route is different, so establish the beneficiary class first. |
| **Traditional 10-year rule does carry annual RMDs** | Where the decedent died **on or after the RBD**, the 2024 final regs require distributions in years 1–9. Penalty waived 2021–2024 (Notices 2022-53, 2023-54, 2024-35); **required from 2025**. |
| **SEPP: plans require separation** | §72(t)(2)(A)(iv) is unconditional for IRAs but applies to a qualified plan **only after separation from service (§72(t)(3)(B))**. An in-service SEPP from a current employer's 401(k) is penalized. Modification busts it retroactively with interest (§72(t)(4)); Notice 2022-6 permits a **one-time switch to the RMD method** as the rescue. |
| **RMDs are the first money out** | §402(c)(4)(B); Reg §1.408-8 Q&A-4. So the RMD must be satisfied **before** a Roth conversion (converting it creates an excess contribution), before a reverse rollover, and a QCD must be the **first** distribution to offset it. |
| **Withholding on a conversion is not converted** | It is a distribution — taxable and penalized under 59½. Elect out and pay from outside funds. |
| **A designated Roth 401(k) clock does not travel** | ⚠ The plan's 5-year clock is **per plan** and does **not** carry to a Roth IRA on rollover — the receiving Roth IRA's own clock governs, **starting at zero** if the taxpayer had no prior Roth IRA. (The contribution *basis* does carry and comes out first under §5's ordering.) The natural inference from the two IRA clocks is the wrong one here. |
| **QCD age is 70½ and is decoupled from the RMD age** | ⚠ The RMD beginning age moved; **the QCD age did not.** A taxpayer aged 70½–72 can make a QCD **before** any RMD is required — a planning window that is routinely missed — and the §408(d)(8)(B) offset below runs from 70½, not from the RBD. |
| **RMD aggregation is asymmetric** | ⚠ **IRAs** may be aggregated and the total satisfied from any one. **403(b)s** aggregate only among themselves. **401(k)s may not be aggregated at all — each plan must distribute its own.** |
| **Year-of-death RMD** | ⚠ If the decedent had not taken the year-of-death RMD, the **beneficiary** must; the 2024 final regulations moved the deadline. |
| **The one-per-year rule is narrower than it looks** | ⚠ It reaches only **60-day indirect IRA-to-IRA rollovers**. It does **not** reach trustee-to-trustee transfers or **conversions** — a second conversion in the same year is fine. |
| **Rolling to an IRA destroys two things** | The **age-55 separation exception** (which turns on the separation date, not the distribution date) and **NUA** on employer stock. Both permanently. → `job-loss.md`. |
| **QCD is reduced by post-70½ deductible IRA contributions** | §408(d)(8)(B), **cumulatively**. A still-working 71-year-old deducting an IRA contribution burns QCD capacity dollar-for-dollar. QCDs cannot go to a **DAF, private foundation, or §509(a)(3)** organization, and are unavailable from employer plans. |
| **SIMPLE 2-year window** | §72(t)(6) makes the early-distribution tax **25%**, and §408(d)(3)(G) permits rollover **only to another SIMPLE** — so the reverse-rollover fix and a Roth conversion are both unavailable inside it. |
| **One-per-year rollover aggregates Roth and traditional** | §408(d)(3)(B); *Bobrow*; Announcement 2014-32. Plan-to-participant distributions carry **20% mandatory withholding** (§3405(c)); **IRAs default to 10% under §3405(b)** and may elect out. §3405(c) does not reach RMDs, hardship, or SEPP. |
| **Conversions cannot be recharacterized** | TCJA repealed it. Only **contributions** may still be recharacterized, by the due date including extensions. |
| **Split-year backdoor Roth spans two 8606s** | A contribution designated for the prior year lands on the **prior year's** Part I (basis only); the conversion lands on the **current year's** Parts I and II. Putting both on one year creates a phantom conversion or duplicate basis. |
| **No waiting period is required** | The IRS has not asserted step transaction against contribute-then-convert; the JCT Bluebook describes it without objection. ⚠ That is legislative history, not authority — an operating position, not a holding. Do not invent a waiting period. |
| **§402(g) excess deferral: April 15 is hard** | Not extended by an extension. Miss it and the amount is taxed **twice**, permanently. Detected from W-2 box 12 codes D/AA/BB across employers. |
| **Non-spouse beneficiary cannot roll to their own IRA** | Permitted: trustee-to-trustee transfer to another **inherited** IRA, and from an employer plan a direct rollover to an inherited IRA under **§402(c)(11)**. |
| **§691(c)** | IRAs are IRD with no step-up; the offsetting relief is the deduction for estate tax paid. → `estate-gift.md`. |
| **The beneficiary form controls** | Over the will. 9/30 determination date, §2518 disclaimers within nine months, and a missing designation defaulting to the estate (and the 5-year rule). See-through trust status turns on Reg §1.401(a)(9)-4(f), and conduit vs. accumulation decides whether EDB status passes through. |
| **§4974 has a statute now** | SECURE 2.0 §313: **3 years** on the missed-RMD excise (6 for §4973). Request the waiver on Form 5329 by entering the shortfall and writing **"RC"** — **do not pay the tax first**. |
| **§72(t) exceptions split by account type** | Plans only: age-55 separation, QDRO. IRAs only: first-time homebuyer, higher education, health insurance while unemployed. Both: death, §72(m)(7) disability (a harder standard than SSA), medical above the floor, levy, reservist, birth/adoption (§72(t)(2)(H)), and the SECURE 2.0 additions. **§408(d)(6)** is the IRA analogue of a QDRO — division in divorce is not a distribution. Governmental §457(b) is outside §72(t) entirely (§72(t)(9)). |
| **Mega-backdoor rests on Notice 2014-54** | Which permits splitting one distribution of pre-tax and after-tax amounts to two destinations. An **owner-only solo 401(k) has no ACP test**, which is where it works. |
| **1099-R code T** | Means the custodian does not know whether the 5-year clock is met — **the taxpayer must prove it**, which is why `roth-basis.md` exists. A code **1** where an exception applies forces Form 5329 Part I. |

## 4. Contribution eligibility

Owned here (referenced from the `1040.md` §4 MAGI register): §219(f)(1)
compensation requirement, §219(c) spousal IRA, §219(g) deductibility,
§408A(c)(3) Roth MAGI limit — where the fix for an over-limit Roth contribution
is to **recharacterize to traditional and then convert**, not withdraw. The
**§529-to-Roth rollover** (SECURE 2.0 §126) limits are owned here: lifetime cap
per beneficiary, 15-year seasoning, contributions in the last five years
excluded, subject to the **annual Roth limit and the beneficiary's earned
income**. → `education.md` records the transfer decision only.

## 5. Year map (TY2023–2026)

Mechanics, not amounts — availability changes by year. ⚠ Verify each.

| Mechanic | Effective |
|---|---|
| No lifetime RMD for designated Roth accounts in plans (§325) | TY beginning after 12/31/2023 — **still required for TY2023** |
| Election to be treated as the deceased spouse (§327) | Calendar years after 12/31/2023 |
| Annual RMDs in years 1–9 under the 10-year rule | Enforced from **2025**; waived 2021–2024 |
| QCD limit indexed (§307); one-time split-interest QCD | Indexing 2024+; split-interest 2023+ |
| Age-50 exception expanded to more public-safety roles (§§329–330) | 2023+ |
| Terminal illness (§326) | 2023+ |
| Emergency personal expense; domestic abuse | 2024+ |
| Long-term care (§334) | Distributions after 12/29/2025 — ⚠ verify whether IRAs are covered |
| §529-to-Roth (§126) | 2024+ |
| No 10% tax on NIA for excess-contribution corrections (§333) | After 12/29/2022 |
| Mandatory Roth catch-up for high earners (§603) | ⚠ Delayed by Notice 2023-62 — verify |
| Higher catch-up ages 60–63 (§109) | 2025+ |
| RMD age 73 / 75 | 75 applies to those born 1960+, i.e. from 2033. Born 1959: a drafting conflict resolved in the proposed regs as 73 |

## 6. Never answer in isolation

A conversion or large distribution is not a federal-tax-only question. Model
jointly: **IRMAA** two-year lookback for Part B *and* Part D
(`health-benefits.md`), **§86** Social Security drag, **§36B/Medicaid**
eligibility (`scenarios/aca-medicaid-magi.md`), **NIIT** MAGI, capital-gain
stacking, and **4 U.S.C. §114** — a state may not tax a **nonresident's**
qualified retirement income, which makes a move the largest timing lever
(`state-residency.md`). The best conversion year is usually a low-income one
(`job-loss.md`).

## 7. Workpaper

`individual/FY<YYYY>/annual/workpapers/wp-retirement.md`, one block per
individual:

```json
{
  "individual": "<slug>",
  "aggregate_ira_value_year_end": null,
  "outstanding_rollovers_and_recharacterizations": 0,
  "form_5498_box5_reconciled": null,
  "form_8606": {"basis_beginning": 0, "nondeductible_this_year": 0,
                "designated_for_prior_year": null, "distributions": 0,
                "conversions": 0, "pro_rata_ratio": null,
                "nontaxable": 0, "basis_ending": 0},
  "roth": {"contribution_basis": 0, "conversion_layers": [],
           "qualified_clock_start_year": null, "qualifying_event_met": null},
  "contributions": {"compensation_support": null, "active_plan_box13": null,
                    "deductible": 0, "nondeductible": 0, "roth": 0,
                    "excess_deferral_402g": 0, "corrected_by_apr15": null},
  "rmd": {"required": null, "taken": null, "aggregation_group": "",
          "satisfied_before_conversion": null, "shortfall": 0,
          "form_5329_rc_waiver_requested": false, "year_of_death_rmd": null},
  "qcd": {"amount": 0, "first_distribution_of_year": null,
          "cumulative_post_70half_deductible_contributions": 0,
          "eligible_after_offset": 0, "cwa_obtained": null},
  "rollovers": [{"type": "", "date": "", "one_per_year_used": false,
                 "withholding_pct": null, "loan_offset": null}],
  "sepp": {"start_date": "", "method": "", "account_balance_date": "",
           "interest_rate": null, "end_date": "", "modified": null,
           "one_time_switch_to_rmd_method": null},
  "penalties": {"section_72t": 0, "exception_claimed": "",
                "exception_applies_to": "ira|plan|both",
                "simple_2year_25pct": null, "section_4973": 0},
  "inherited": {"decedent": "", "date_of_death": "", "account_is_roth": null,
                "beneficiary_class": "", "died_on_or_after_rbd": null,
                "annual_rmd_required_years_1_9": null,
                "trust_beneficiary_see_through": null, "section_691c": 0}
}
```

**Invariants:** the pro-rata denominator is an aggregate including outstanding
rollovers, applied to conversions and distributions together; 8606 basis ending =
beginning + nondeductible − recovered; a qualified Roth distribution requires
**both** clock and event; an inherited **Roth** never carries years-1–9 RMDs; the
RMD is satisfied before any conversion or reverse rollover; every §72(t)
exception names its provision and whether it reaches an IRA, a plan, or both; a
null aggregate balance blocks any conversion conclusion.

Verify with a licensed practitioner before filing.


# Itemized Deductions (Schedule A)

Owns the standard-vs-itemized decision and the Schedule A **substantiation and
allocation contracts**.

⚠ **This is the most year-dependent area on the return.** TCJA, the 2025 sunsets,
and OBBBA moved the SALT cap, the charitable rules, and the top-bracket benefit
limitation on **different effective dates**. Every cap, floor, percentage, and
phaseout — and every ⚠ proposition — is subject to `authority.md`. This file
carries mechanics and ordering only.

## 1. The election

Itemize when allowable itemized exceed the standard deduction, with three
complications: ⚠ **MFS is forced** — if one spouse itemizes the other must
(§63(c)(6)(A)); **bunching** beats a steady pattern near the threshold, usually
through a DAF; and ⚠ **state divergence** — some states require the federal
election to carry over and some do not, so a federal standard deduction can cost
a state itemized deduction. Run the state before finalizing
(`state-residency.md`).

## 2. Medical (§213)

⚠ The traps: expenses of a person who qualifies as a dependent **except** for the
gross-income or joint-return test are deductible by the supporter (§213(a),
§152(b)); and **§213(d)(5) treats a child of divorced or separated parents as a
dependent of *each* parent**, so **both** deduct what they actually paid,
regardless of Form 8332 (`credits.md`). Deductible when **paid** (a card charge
is paid when charged). Long-term care premiums are capped by an **age-based
per-person limit** (§213(d)(10)). Capital improvements are deductible only to the
extent cost exceeds the increase in property value (Reg §1.213-1(e)(1)(iii)).
Amounts paid with HSA or FSA funds are not deductible. High floor ⇒ a bunching
candidate.

## 3. Taxes (§164) — the SALT cap

Income **or** sales tax (elective), real property tax, and the **ad valorem
portion only** of personal property tax.

⚠ **§164(b)(6): OBBBA raised the cap for a defined window and added its own
income phaseout that claws the increase back.** Verify the cap, the phaseout
range, and the window for the target year — using the wrong year's cap is the
most likely error in this file. **Halved for MFS.**

Mechanics that move money out from under the cap:
- The **sales-tax election** usually wins in a no-income-tax state, especially in
  a year with a large vehicle purchase.
- ⚠ **Foreign real property taxes are not deductible.**
- Taxes on a rental go to **Schedule E** and on a business to **Schedule C** —
  **neither is capped**. Allocating property tax between personal and
  rental/home-office use is a legitimate lever.
- **PTET** moves the deduction to the entity (Notice 2020-75); the K-1 shows it.
  → `pass-through.md`, `state-residency.md`.
- ⚠ **§111 tax-benefit rule** — a state refund is taxable next year only to the
  extent it produced a benefit. With the cap binding or the standard deduction
  taken it is frequently **not taxable at all**. Compute the prior-year benefit;
  do not assume.

## 4. Interest

### 4.1 Qualified residence interest (§163(h)(3))

⚠ **Deductibility turns on the secured-debt and acquisition-debt character of the
borrowing — not on tracing, and not on which lender issued the 1098.** Sequence:

1. **Secured** by a qualified residence (principal plus one elected second)?
   Unsecured debt used to buy a home is not qualified residence interest.
2. **Acquisition or home equity?** ⚠ Debt is characterized by **use of
   proceeds** — a "home equity loan" used to substantially improve the home is
   acquisition debt and remains deductible. Home-equity interest as such is
   disallowed.
3. **Cap by the date the debt was *incurred***, not by tax year, with
   grandfathering and a binding-contract transition. A **refinance keeps the
   older character and cap to the extent of the balance refinanced**; cash-out
   above it is new debt at the current cap.
4. **Average-balance limitation** where the cap binds (Pub. 936 worksheet).
5. With more than two residences the taxpayer **elects** which second qualifies.
6. ⚠ **Points** — deductible in the year paid on a principal-residence purchase
   (§461(g)(2)); amortized on a refinance, and the **unamortized balance is
   deducted in full when that loan is refinanced away or paid off**. Frequently
   missed.
7. **Reg §1.163-8T tracing** applies only to debt *not* secured by a qualified
   residence, or where the taxpayer **elects out** under Reg §1.163-10T(o)(5) —
   which can be advantageous, moving interest to Schedule C or E where no cap
   applies.
8. ⚠ Mortgage insurance premium treatment changed repeatedly — verify.

The 1098 is a starting figure. Reconcile Σ 1098 to the amount deducted with every
difference explained.

### 4.2 Investment interest (§163(d)) — Form 4952

Limited to **net investment income**, excess carried forward **indefinitely**
(§163(d)(2)). ⚠ Qualified dividends and net LTCG are **excluded** unless the
taxpayer **elects** under §163(d)(4)(B)(iii) to treat them as ordinary investment
income — a real trade: a current deduction at ordinary rates in exchange for
surrendering the preferential rate on the elected amount. Worth it mainly when
the carryforward would otherwise sit unused. **Record it as a decision in
`review.md` with the arithmetic both ways.** Interest to buy tax-exempts is never
deductible (§265(a)(2)). ⚠ The §163(d) net investment income figure and the
§1411 NIIT base are **not the same number**.

## 5. Charitable (§170)

### 5.1 Limits

The deductible amount depends on **both** the asset and the donee, and the limits
stack in order. Ordinary-income property (short-term, inventory, self-created
art) is **basis only**. A §170(b)(1)(C)(iii) election trades FMV for a higher
percentage. Excess carries forward **five years, retaining its class**.

⚠ **The classes and the order of application are mechanics this file owns; only
the percentages are `authority.md`'s.** Classify each gift on two axes — **asset**
(cash / capital-gain property / ordinary-income property) and **donee**
(§170(b)(1)(A) public charity or "50% organization" / other, chiefly private
non-operating foundations) — then apply the limits in this sequence, each against
the contribution base remaining after the prior step:

1. Cash to 50% organizations (§170(b)(1)(A), and the §170(b)(1)(G) elevated cash
   limit where in effect for the year).
2. Capital-gain property to 50% organizations (the 30% class), with the
   §170(b)(1)(C)(iii) election moving it up a tier in exchange for basis-only
   valuation.
3. Cash and ordinary-income property to non-50% organizations.
4. Capital-gain property to non-50% organizations (the 20% class), which is
   additionally capped by the amount remaining under the 30% ceiling.

⚠ **The order is not neutral** — a gift crowded out at step 1 carries forward in
step 1's class, not as an undifferentiated amount, and expires on its own clock. ⚠ The five-year
balance by class is **year-crossing state** and lives in
`individual/carryforwards.json` (`1040.md` §5) — `wp-schedule-a.md` records only
this year's movement. A single aggregate carryover is insufficient.

### 5.2 Substantiation — where deductions are actually lost

⚠ **Not curable after the fact.**

- **≥ $250**: contemporaneous written acknowledgment obtained by the **earlier of
  filing or the due date** (§170(f)(8)). A cancelled check is not enough; a CWA
  obtained during examination is too late.
- **Quid pro quo > $75**: donee disclosure.
- **Noncash > $500**: Form 8283 Section A. **> $5,000**: qualified appraisal and
  Section B with **appraiser and donee signatures**. ⚠ Exception under
  §170(f)(11)(A)(ii)(I) for **readily valued property** — publicly traded
  securities, cash, inventory, vehicles. **Digital assets are not securities and
  get no exception** (CCA 202302012, which also **rejected reasonable cause**).
  **> $500,000**: attach the appraisal.
- On e-file, Section B is transmitted either as a **PDF attachment** or by mail with **Form 8453**.
- §6662(h) gross valuation misstatement carries **40%** — the appraisal is not a
  formality.

Vehicles: limited to gross proceeds unless significant intervening use or
material improvement (§170(f)(12); Form 1098-C). Conservation easements:
syndicated versions are listed transactions — flag elevated risk, do not design.

### 5.3 Planning

Appreciated long-term securities beat cash. A **DAF** is the bunching vehicle —
but a **QCD cannot go to a DAF** (`retirement.md`), and a QCD beats a deduction
entirely for anyone over the age threshold taking the standard deduction because
it is an AGI **exclusion**. ⚠ **For years beginning after 12/31/2025 verify the
OBBBA changes** — a floor on itemized charitable contributions (§170(p)), a cap
on the benefit for top-bracket taxpayers, and a permanent non-itemizer deduction.
A strategy designed under prior rules must be re-run.

## 6. Casualty, gambling, and the benefit limitation

⚠ **§165(h)(5)** limits personal casualty losses to declared disasters — OBBBA
made the limitation **permanent** and, for years beginning after 12/31/2025,
**expanded the exception to State-declared disasters**. A loss in a transaction
entered into for profit under **§165(c)(2)** is outside that limitation, which is
the distinction that decides investment-scam cases (→ `digital-assets.md` §7).
Personal casualty gains offset personal casualty losses regardless.

⚠ **Two floors apply on top of the §165(h)(5) gate, and both are required:**
**§165(h)(1)** disallows the first **$100 per casualty event** (per event, not per
item and not per year), and **§165(h)(2)** then allows only the aggregate excess
over **10% of AGI**. A qualifying declared-disaster loss with neither floor
applied is an unbounded number. Order: per-event $100 reduction → net against
personal casualty gains → 10%-of-AGI floor on the remainder.

⚠ **Gambling (§165(d))** — losses only to the extent of winnings, only if
itemizing; **verify the target-year deductible fraction**, which OBBBA changed for
years beginning after 2025. Session accounting, not per-wager. Professionals use
Schedule C.

⚠ **Miscellaneous itemized deductions subject to the 2% floor remain
suspended** — **§67(g) for 2018–2025, §67(h) for years beginning after
12/31/2025**; cite the subsection matching the tax year. Impairment-related work
expenses, §691(c) estate tax on IRD, and gambling losses are **not**
miscellaneous and survive.

⚠ **Benefit limitation** — the pre-TCJA §68 "Pease" limitation was suspended;
OBBBA introduced a **different** limitation on the benefit of itemized deductions
for top-bracket taxpayers for years beginning after 2025. Different mechanisms;
do not conflate.

## 7. Workpaper

`wp-schedule-a.md`:

```json
{
  "election": {"itemized_total": 0, "standard_deduction": 0, "chosen": "",
               "mfs_forced": false, "state_divergence_checked": false},
  "medical": {"qualified_expenses": 0, "floor_applied": 0, "deductible": 0,
              "dependent_medical_213d5_both_parents": null},
  "taxes": {"income_or_sales_elected": "", "total_before_cap": 0,
            "cap_applied": 0, "cap_authority_id": "",
            "amounts_moved_to_sch_c_or_e": 0, "ptet_credit_on_k1": 0,
            "prior_year_benefit_for_111": 0},
  "interest": {"form_1098_total": 0, "reconciling_items": [],
               "acquisition_debt_by_incurrence_date": [],
               "average_balance_limitation": null,
               "points_current": 0, "points_amortized": 0,
               "unamortized_points_deducted": 0,
               "elected_out_1_163_10T_o5": null,
               "qualified_residence_interest_deducted": 0,
               "investment_interest_4952": {"expense": 0, "net_investment_income": 0,
                 "election_163d4Biii_made": null, "amount_elected": 0,
                 "allowed": 0, "carryforward_out": 0}},
  "charitable": {"by_class": [{"class": "", "donee_type": "", "amount": 0,
                               "agi_limit_applied": 0, "allowed": 0,
                               "carryforward_out": 0}],
                 "cwa_obtained_all_250plus": null,
                 "qualified_appraisals": [], "readily_valued_exception": [],
                 "form_8453_required": null},
  "casualty": {"declared_disaster": null, "state_declared_post_2025": null,
               "section_165c2_profit_motive": null},
  "benefit_limitation_applied": null
}
```

**Invariants:** Σ 1098 reconciles to interest deducted with differences
explained; SALT recorded before and after cap **with the cap's authority ID**;
every gift ≥ $250 has a CWA and every noncash > $5,000 an appraisal or a stated
exception; charitable carryover tracked **by class** and tied to prior year; the
§163(d)(4)(B)(iii) election recorded as a decision with arithmetic both ways; the
§163(d) net investment income figure is not reused as the §1411 base; the §111
computation is performed, not assumed.

Verify with a licensed practitioner before filing.

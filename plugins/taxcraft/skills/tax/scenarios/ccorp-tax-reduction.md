
# C-Corp Tax Reduction Scenarios

Specific, documentable strategies to reduce closely-held C-corp federal + state tax. Each requires contemporaneous documentation — coordinate with `governance.md` to produce the supporting board resolutions.

## Accountable Plan (Reg §1.62-2)

Shareholder-employees can receive nonwage reimbursements only when the actual
arrangement satisfies the business-connection, substantiation, return-of-excess,
and wage-recharacterization rules. The plan determines payment character; the
underlying expense law determines deductibility and limitations.

Load `accountable-plan.md` for eligibility, audit, drafting, adoption, claim
controls, payroll remediation, and annual review. Load `home-office-280a.md` in
addition when home costs are involved. This C-corp file owns only the surrounding
C-corp strategies.

## §280A(g) Augusta Rule (Home Rental to Employer)

### Mechanism
If a dwelling is used by the taxpayer **as a residence** (§280A(d)(1)) AND is actually rented for **fewer than 15 days** in the year, the rental income is **excluded from gross income entirely** (§280A(g)(2)); rental deductions are correspondingly denied (§280A(g)(1)).

⚠️ **The residence test is "exceeds," not "at least."** §280A(d)(1) requires personal use for a number of days **exceeding** the greater of **14 days** or **10% of the days rented at fair rental**. With fewer than 15 rental days, that ordinarily means **at least 15 personal-use days** — not 14. Getting this backwards fails the exclusion at the threshold.

The tenant (the corp) deducts the rent **only if it independently satisfies §162(a)(3)** — ordinary, necessary, and reasonable for bona fide business use. §280A(g) governs the owner's income, not the corporation's deduction; excessive related-party rent gets recharacterized as compensation or a constructive distribution. Accrual-basis payers: **§267(a)(2)** defers the deduction until the related owner includes the amount — which never happens under §280A(g). **Pay in cash within the year.**

Net effect: corp pays rent to shareholder for legitimate business use of home, shareholder reports no income, corp deducts it.

### Requirements

- **Actual business use** — board meetings, officer meetings, planning retreats, client events. NOT casual personal space.
- **Fewer than 15 days/year of rental** — track rigorously
- **Fair market value rent** — comparable to meeting-room / event-space rentals in the area; get 3 comps
- **Written rental agreement** between corp (tenant) and shareholder (landlord), arm's-length terms
- **Board resolution** pre-authorizing the rental — template in `governance.md`
- **Contemporaneous documentation** — agenda, attendees, minutes for each day used

### Common traps

- Sole-shareholder "meetings with myself" — weak; better if there are multiple officers/directors or advisors present
- Recovering the same underlying cost twice — e.g. rent covering costs already reimbursed under the Accountable Plan. The prohibition is on paying for one economic cost twice, not on the two arrangements touching the same square footage
- Claiming FMV of $2,000+/day without local comps — IRS will compare to Airbnb-style event space rates
- **The limit is on rental days of the residence, NOT per entity.** Count **distinct calendar days on which the dwelling is actually rented**, aggregated across all renters. Two entities renting *different* 14-day blocks = 28 rental days → the test fails and **the entire exclusion is lost**, making all of it taxable rental income. (Two entities renting the *same* calendar days do not automatically double the count, but that arrangement invites its own arm's-length and business-purpose challenge.) Simplest safe practice: one entity takes the days, the others take zero.
- **§280A(c)(6) — do not let the arrangement become a lease of space the owner works in.** Where an employee rents a dwelling unit (or portion) **to his employer** and uses it to perform services for that employer, §280A(c)(6) provides that **"Paragraphs (1) and (3) shall not apply"** — withdrawing the employee's §280A(c)(1) home-office and §280A(c)(3) rental-use exceptions for that item. **There is no "it was only a meeting day" exception**; performing services at a board meeting is still performing services (IRS PMTA 2007-00431 reads (c)(6) broadly, though nonprecedential). Reimburse the dedicated office through the accountable plan instead of leasing it.

> ❗ **Correction (do not repeat the common misstatement):** §280A(g) is **not** disallowed merely because the home is the principal place of business, and Augusta is **not** mutually exclusive with the home-office deduction. §280A(g) opens "**Notwithstanding any other provision of this section**" and turns only on (i) use as a residence under §280A(d)(1) and (ii) rental for fewer than 15 days. Note also that §280A(c)(6) operates on the §280A(c)(1)/(3) **deduction** side — it does **not** defeat the §280A(g) income exclusion. And there is no statutory rule barring rent and reimbursement merely because they touch the same square footage; the requirement is that **each corporate payment independently satisfy §162, Reg §1.62-2, substantiation, allocation, and reasonableness**, without paying for one economic cost twice. See `home-office-280a.md` §6.

### Audit risk

Moderate. Well-documented (comps, agenda, minutes, ≤14 days) — defensible. Weakly documented — common audit adjustment.

### Math example

```
FMV rental value per day: $1,200 (3 local event-space comps: $950, $1,200, $1,450 → $1,200 median)
Days used: 12
Annual rent: $14,400

Corp deduction (§162):        $14,400
Shareholder income (§280A(g) excluded): $0

Net corp tax savings @ 21%:   $3,024
Net shareholder savings:      $14,400 exclusion from personal income
Combined (if single taxpayer): roughly $3,024 + ($14,400 × shareholder marginal rate)
```

## Family Employment

### Mechanism
Corp hires family member (spouse, adult child, parent) as a legitimate employee. Wages are deductible to corp, taxable to family member at their (often lower) bracket.

### C-corp specifics

- **No FICA exemption** for family — unlike Schedule C where children under 18 are exempt from FICA, C-corp wages to minor children are fully FICA-taxed.
- **Reasonable comp at arm's length** — wage must reflect services rendered. IRS scrutinizes rates for related parties under §267 and §162(a)(1). Get industry-comparable data.
- **Bona fide employment** — actual work performed, time records, job description, regular payroll through normal system
- **Ages and capability matter** — 7-year-old doing "market research" for $20k is not defensible. 16-year-old social media manager at $15/hr for 10 hrs/wk might be.

### Opportunity zones

- Roth IRA funding: minor child with W-2 wages can fund a Roth IRA up to earned income or limit (whichever is lower). Compound growth tax-free.
- Income-shifting: moving $14,600 (2024 std deduction for single) from parent's 37% bracket to child's 0% bracket = ~$5,400/yr savings.

### Documentation

- W-4 + I-9 on file
- Time records / timesheets
- Job description in personnel file
- Regular pay schedule through payroll system (W-2 issued annually)
- Board resolution authorizing the employment (for insider hires)

### Audit risk

Moderate to elevated depending on who, wage level, documentation. Courts have been skeptical of family wages that lack work product (*Denman v. Commissioner*, *Eller v. Commissioner* — children's wages disallowed when work unprovable).

## Accumulated Earnings Tax Defense (§531)

### Mechanism
C-corp accumulates earnings beyond $250k ($150k for PSCs) safe harbor → IRS can assess 20% surtax on accumulated taxable income if accumulation is beyond "reasonable needs of the business" (§535, §537).

### Reasonable needs (Reg §1.537-2)

Enumerated examples:
- Business expansion or replacement of plant
- Acquisition of a related business
- Debt retirement
- Working capital for a business cycle (Bardahl formula is traditional benchmark)
- Investments or loans to suppliers/customers if related to business needs
- Reasonable insurance or contingency reserves
- Stock redemption under specific circumstances (§303 redemptions for death)

### Documentation

- Annual board resolution stating specific business purposes for retained earnings and projected timeline (template in `governance.md`)
- Capital plan / business plan referenced in resolution
- Bardahl-formula working capital analysis (operating cycle × operating expenses)
- Evidence of actual use (or good-faith plan) — the *planned* use test is forgiving but requires follow-through

### Audit risk

Triggers: large cash balance vs. operational needs, passive investments dominate assets, no dividends + no documented plan. Mitigation: annual resolutions + capital plan + (if income is passive-heavy) consider PHC §541 risk too.

## Fringe Benefits (C-corp advantage)

C-corps can deduct fringe benefits that are excluded from employee income — much better than pass-throughs where >2% owners are generally excluded from favorable treatment.

- **Health insurance** — 100% deductible to corp, tax-free to employees (no shareholder threshold for C-corps unlike S-corps)
- **Group-term life insurance (§79)** — up to $50k coverage tax-free
- **§105 HRA / §125 cafeteria / §127 education assistance / §132 working-condition, de minimis, qualified transportation, on-premises athletic** — deductible to corp, tax-free to employee
- **§129 dependent care** — up to $5k
- **§127 educational assistance** — up to $5,250

### Setup

Adopt each plan via written plan document + board resolution. Coordinate with `governance.md`.

## §174 R&D Planning

**The regime changed inside the supported window — do not plan off the TCJA rule.**
Domestic R&E was capitalized and amortized over 5 years for TY2022–2024; **OBBBA
enacted §174A restoring immediate domestic expensing effective TY2025**, with a
retroactive election for eligible small businesses back to TY2022 and an
accelerated catch-up of unamortized amounts. Foreign R&E remains 15-year.
`entities/c-corp.md` owns the regime and the Form 3115 mechanics — verify there
and through `authority.md` before planning. Then:

- **§41 R&D credit** remains available — up to 20% of QREs. Small startups (<$5M gross receipts, <5 yrs revenue) can offset up to $500k of payroll tax (§3111(f)) instead of income tax.
- **Distinguish §174A from §162** (for post-2024 **domestic** research; §174 remains the **foreign** regime): routine software maintenance / bug fixes / customer-specific customization = §162 (current deduction). Experimentation + uncertainty = §174A domestic (expensed from TY2025) or §174 foreign (15-year).
- Careful documentation of which activities are §174 vs §162 — material impact on current year deduction.

## §1202 QSBS Planning

QSBS exclusion may apply if the corp's stock is issued C-corp stock meeting the active-business + gross-assets tests and held by the shareholder past the applicable holding period (3/4/5 yr under OBBBA for stock issued after 7/4/2025, or 5 yr under pre-OBBBA rules). Founders/early shareholders should track issuance-date balance sheets and activity-test snapshots from day one so the exclusion is provable at exit.

See scenarios/qsbs-1202.md for full §1202/QSBS qualification rules, the pre-/post-7/5/2025 regime split, §1045 rollover, and stacking strategies.

Document at `entities/<slug>/corporate/qsbs-tracking/` with issuance-date balance sheet, activity test snapshots, basis log.

## Documentation Discipline Summary

Every C-corp strategy above requires:

1. **Board resolution** adopted contemporaneously (`entities/<slug>/corporate/resolutions/`)
2. **Implementation document** (plan, agreement, study) (`entities/<slug>/contracts/` or `entities/<slug>/corporate/`)
3. **Annual proof** (receipts, mileage logs, W-2s, rental summaries) (`entities/<slug>/tax/FY<YYYY>/annual/workpapers/`)
4. **Tax-basis treatment** on the return, reconciled on Schedule M-1 if book differs

Miss any — the strategy becomes a tax adjustment + penalty risk.

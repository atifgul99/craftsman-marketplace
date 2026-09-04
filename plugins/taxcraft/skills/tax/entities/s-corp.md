
# S-Corporation (Form 1120-S) Sub-Skill

For corporations with valid S-election (Form 2553) and LLCs that elected S treatment. Pass-through but with distinctive FICA/compensation mechanics.

## Preflight (beyond common)

1. **Verify S-election status** — Form 2553 filed and accepted; no inadvertent termination (excess PII, second class of stock, resident alien shareholder, ineligible shareholder type). If ambiguous, check IRS CP261 acceptance letter.
2. **Reasonable comp benchmark assembled** — payroll records, comp study, industry data. Critical audit flag.
3. **2%-shareholder identification** — any shareholder (and their §318 attributed family) owning >2%.
4. **C-corp E&P carried into S-election?** — if yes, AAA and distribution ordering rules get more complex.
5. **Built-in Gains (§1374) period** — 5-year recognition window on C→S conversion. If converted, track BIG.

## Critical Items

### 1. Reasonable Compensation (Audit Priority #1)

- IRS Fact Sheet 2008-25 factors: training/experience, duties, time/effort, dividend history, payments to non-shareholder employees, timing/manner of bonuses, comparable businesses, compensation agreements, use of a formula.
- **Pay W-2 salary before distributions.** Distributions in excess of basis without prior salary = classic audit trigger → re-characterization as wages → FICA + §6656 penalty + §6651 late-payroll penalty.
- Document with a reasonable-comp study (internal or third-party) annually. Board resolution setting comp level, tied to study.
- **Audit risk: meaningful.** Case law: *Watson v. US* (8th Cir. 2012) — $24k salary to CPA making $200k+ net was unreasonable; *Glass Blocks Unlimited* — similar pattern.

### 2. Basis Tracking (Stock + Debt)

Separately from capital accounts (instantiate `entities/<slug>/books/capital-accounts.md` from `templates/capital-accounts.md.template` at first close):
- **Stock basis**: beginning + contributions + income (incl. tax-exempt) − distributions − losses (not below zero)
- **Debt basis**: only from shareholder-direct loans; personal guarantees of corporate debt do not create basis (see *Maloof*, *Selfe*)
- Losses limited to total (stock + debt) basis; excess suspended; can restore debt basis before stock basis (Reg §1.1366-2)
- File **Form 7203** (post-2021) annually with the shareholder's 1040 showing basis reconciliation.
- **§1244 applies to S-corp stock too** — a loss on disposition/worthlessness of the shares themselves can be ordinary (up to $50K/$100K MFJ per year) if the issuance was papered correctly. Note the basis interaction: pass-through losses already deducted reduce stock basis and therefore the loss left for §1244. See `scenarios/section-1244.md`.

### 3. AAA (Accumulated Adjustments Account) — Schedule M-2

- Tracks post-S-election items to determine distribution character if C-corp E&P exists.
- Distribution ordering when E&P exists: (1) AAA — tax-free to extent of stock basis, (2) E&P — dividend, (3) OAA, (4) remaining basis — tax-free, (5) excess — capital gain.
- No E&P (S-corp from inception or C-corp drained of E&P) → simpler: distributions reduce basis then capital gain.

### 4. Single Class of Stock

- Rights to distribution and liquidation proceeds must be identical across all shares. Voting differences OK.
- **Trap**: disproportionate distributions, unequal shareholder loans, binding agreements for unequal distributions can create a second class and terminate S election.
- Audit-defense: documented governance + uniform distribution resolutions — coordinate with `governance.md`.

### 4a. C→S conversion consequences are conditional, never automatic

When modelling an S election for an existing C corporation, state each of these
as a **condition with its own test**. Presenting them as automatic consequences
of electing is a common and material error:

- **§1375 passive investment income tax** applies only if the corporation has
  **accumulated earnings and profits from its C years** *and* passive investment
  income exceeds 25% of gross receipts for the year. A converted corporation
  with no accumulated E&P cannot owe it at all, however passive its income.
  Establish the C-year E&P balance before saying anything about §1375.
- **§1362(d)(3) termination** requires **three consecutive** tax years meeting
  both conditions, and terminates the election as of the following tax year —
  not immediately, and not on a single bad year.
- **§1374 built-in gains tax** requires net unrealized built-in gain determined
  **as of the conversion date**. Without asset-by-asset conversion-date
  valuations there is no NUBIG figure and no defensible §1374 number; commission
  the valuation as part of the conversion, not after the first sale.

Each of these turns on figures the entity may not have. Say what is unknown and
what would resolve it rather than modelling a consequence on assumed facts.

### 5. §1374 Built-in Gains Tax

- 5-year recognition period after C→S conversion.
- On sale of appreciated asset held at conversion, gain to extent of NUBIG (Net Unrealized Built-In Gain) taxed at 21% at corporate level, then passes through to shareholders (who get a basis step-up for tax paid).
- Plan asset sales to occur after 5-year window when possible.

### 6. K-1 Mechanics (Schedule K-1)

- Similar to 1065 K-1 but **no SE tax on box 1 ordinary income** — the big feature.
- Pro-rata allocation per share per day — no special allocations.
- Short-year or mid-year stock transfer: per-share-per-day method (default) or closing-of-books (elected with consent of affected shareholders).

### 7. 2%-Shareholder Fringe Benefits

- Health insurance: premiums paid by corp for 2%+ shareholder-employee → **add to W-2 box 1** (but not box 3/5 — still FICA-exempt). Shareholder deducts as SE health insurance on Form 1040 Schedule 1 line 17 (subject to limits and earned-income cap).
- Other fringes (GTL, §129 dependent care, qualified transportation) — most are taxable to 2%+ shareholders; treat carefully.
- Retirement plans: 2%+ shareholders are employees, eligible for 401(k)/SEP based on W-2 wages.

### 8. Accountable Plan / Home Office

- Shareholder-employee business expenses (home office, mileage, cell, internet) may be reimbursed under an **Accountable Plan** arrangement (Reg §1.62-2) — deductible to the corp and excluded from wages only to the extent the arrangement and each payment satisfy the federal tests. A written plan is a strong closely-held-company control, not a separate regulatory element; actual operation controls. The shareholder is permanently barred from deducting unreimbursed employee expenses personally — **§67(g)** for tax years 2018–2025, **§67(h)** for years beginning after Dec 31, 2025 (OBBBA PL 119-21 §70110 redesignated it and inserted a new §67(g), "Educator expenses").
- 🔴 **Do not lease home workspace to the S-corp.** §280A(c)(6) provides that "Paragraphs (1) and (3) shall not apply" where an employee rents a dwelling unit (or portion) to their employer and uses it to perform services — withdrawing the §280A(c)(1) home-office and §280A(c)(3) rental-use exceptions, so the shareholder reports the rent as income with nothing against it.
- Full qualification, business-percentage, and §121 analysis: `scenarios/home-office-280a.md`. Plan mechanics: `scenarios/accountable-plan.md` (the Reg §1.62-2 rules are identical for S- and C-corps).

### 9. §199A Interaction

- S-corp W-2 wages count for the wage-limit test on the shareholder's 1040 §199A calculation.
- **Reasonable-comp tension**: higher salary → more wages (helps QBI wage-limit) but less QBI (since wages reduce qualified business income) and more FICA. Model it — sweet spot depends on shareholder's §199A phase-in/phase-out position.

## Deadlines & Penalties

- **Form 1120-S due**: 2½ months after FY end (March 15 CY). Extension via Form 7004 → 6-month (September 15 CY).
- **§6699 late-filing penalty**: a per-shareholder, per-month indexed amount for up to 12 months — verify the rate for the target year via `authority.md`
- **Form 941 / 940 / W-2 / W-3 / state payroll** — separate from 1120-S, with their own deadlines. Late payroll can invalidate reasonable-comp defense even if 1120-S is timely.
- **Form 7203** (shareholder basis) — attached to shareholder 1040 if S-corp loss, distribution, or stock disposition.

## Basis Workpaper Template (per shareholder, per year)

```json
{
  "shareholder": "<name>",
  "entity": "<entity>",
  "tax_year": 2025,
  "ownership_pct": 100,
  "stock_basis": {
    "beginning": 0,
    "contributions": 0,
    "share_income_ordinary": 0,
    "share_income_separately_stated": 0,
    "share_tax_exempt_income": 0,
    "distributions": 0,
    "share_losses": 0,
    "share_nondeductible_expenses": 0,
    "ending": 0
  },
  "debt_basis": {
    "beginning": 0,
    "new_shareholder_loans": 0,
    "restored_from_income": 0,
    "repayments": 0,
    "reduced_for_losses": 0,
    "ending": 0
  },
  "aaa_share": 0,
  "suspended_losses_basis": 0,
  "§199A_component": {"qbi": 0, "w2_wages": 0, "ubia": 0, "sstb_flag": false}
}
```

Save per shareholder: `entities/<slug>/tax/FY<YYYY>/annual/workpapers/basis-<shareholder-slug>.json`

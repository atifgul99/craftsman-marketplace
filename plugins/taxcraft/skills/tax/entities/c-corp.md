
# C-Corporation (Form 1120) Sub-Skill

For C-corporations and LLCs with a C election. The return-workpaper rules apply
to both, but do not assume an LLC's entity-law units are “stock” for §1202 or
§1244. Route unit issuance/eligibility through `scenarios/stock-issuance.md` and
hold the stock-specific conclusion for tax counsel. Flat 21% federal rate;
double-tax regime; distinct planning/risk profile from pass-throughs.

Requests to inventory the C-corporation record book, repair formation,
reconcile ownership records, or test annual governance route first to
`scenarios/corporate-records.md`. Before relying on shareholder, director,
officer, issued-share, or active-plan facts in a return workpaper, use that
matrix's current evidence status; a profile label or draft does not prove the
underlying corporate act.

## Preflight (beyond common)

1. **Accounting method** — cash or accrual? §448 requires accrual if 3-year average gross receipts > threshold (check rules file) unless small-business exception. Confirm.
2. **Books loaded** — trial balance, fixed assets, opening balances from `entities/<slug>/books/`.
3. **Nested disregarded SMLLCs** — enumerate and load their books too. They consolidate as divisions.
4. **Fiscal year** — verify current FY end matches Form 1128 (if changed) and matches EIN letter. Fiscal-year ≠ calendar-year corporations have different estimated-payment due dates.
5. **Prior-year NOL, §163(j) disallowed interest, §179/bonus carryover, charitable 10%-limit carryover, AMT credit, FTC** — load from prior return and `books/` opening balances.
6. **§1202 QSBS eligibility status** — use the stock's actual acquisition date and the date-sensitive **inclusive** aggregate-gross-assets ceiling (≤ $50M for pre-7/5/2025 acquisitions; ≤ $75M for post-7/4/2025 acquisitions, subject to statutory indexing after 2026), including the issuance proceeds and required aggregation/property rules. Also test qualified business, active use, redemptions, and continuing C-corporation status. See `scenarios/qsbs-1202.md`.
7. **Stock issuance and §1244 discipline** — route any proposed, historical, or remedial issuance through `scenarios/stock-issuance.md`. Test §1244 only for actual stock issued for money/property, using the ordinary pre-transition rule plus the limited transitional-year designation/allocation rules when capital receipts first exceed $1M; services and undocumented historical contributions require separate results. See `scenarios/section-1244.md`.
8. **Corporate-record integrity** — load
   `scenarios/corporate-records.md` when a tax conclusion depends on formation
   authority, ownership, annual action, a plan's execution/operation, standing,
   or a subsidiary boundary. A return copy, signed e-file authorization,
   transmission receipt, acceptance, payment proof, and transcript are separate
   evidence.

## Key Items

### Tax Structure

1. **Flat 21% federal** on taxable income (post-TCJA, §11).
2. **Double taxation** — corporate tax + shareholder tax on dividends (LTCG/QDiv rates if qualified).
3. **Fiscal year choice** — any month-end permitted (with IRS consent via Form 1128 if changing from CY); popular for deferral or GP/fund-mgmt alignment.

### First-Year Costs — §248 Organizational and §195 Start-Up Expenditures

1. **What each covers.** §248: costs of creating the corporation — state filing
   fee, incorporation legal and accounting fees, organizational-meeting and
   temporary-director costs. §195: pre-opening costs of investigating and
   creating an active trade or business. Neither covers the costs of issuing or
   selling stock. Successful issuance/syndication costs are not deductible or
   amortizable and generally reduce the proceeds; an abandoned transaction is a
   separate §165 question.
2. **Mechanics.** $5,000 deducted in the year the business begins, phased out
   dollar-for-dollar as the category exceeds $50,000; the remainder amortized
   ratably over 180 months from the month business begins. The two categories
   are computed separately.
3. **The deduction/amortization treatment is the deemed default.** Under
   **Reg. §1.248-1(c)** and **Reg. §1.195-1(b)**, a taxpayer is **deemed** to
   have elected that treatment for the year business begins; no statement is
   required. It is the opposite choice — **forgoing** the deduction and
   capitalizing the costs — that must be made affirmatively on a timely filed
   return including extensions. Do not tell a client a missing statement or a
   late return forfeited the deduction without checking the current regulations
   and the return's actual filing status.
4. **Record-book link.** The organizational consent should identify who paid the
   formation costs and whether the corporation reimbursed the payer. Where a
   founder paid the corporation's own obligation and was not reimbursed, the
   analysis is generally a capital contribution followed by a constructive
   payment by the corporation — not an automatic loss of §248 treatment.
   Identify the legal obligor and the reimbursement facts before concluding.
   Route the evidence to `scenarios/corporate-records.md` Gate 7.

### Loss & Interest Carryovers

1. **NOL** — post-TCJA: indefinite carryforward, 80% of current-year taxable income limit. Pre-2018 NOLs retain 20-year life at 100% limit. Track vintages separately.
2. **§163(j)** — business interest expense limited to 30% of ATI (Adjusted Taxable Income); disallowed portion carries forward indefinitely. Small-business exception: 3-year avg gross receipts ≤ §448 threshold (electively out; real-property trade/business election). **ATI computation — EBITDA basis restored permanently**: for tax years beginning after 12/31/2024, OBBBA (PL 119-21) permanently restores the EBITDA-based ATI computation — depreciation, amortization, and depletion are added back when computing ATI, materially loosening the 30% cap for capital-intensive/leveraged entities. This reverses the EBIT-basis rule (no D&A addback) that applied for tax years 2022–2024 under prior law. Confirm which basis applies to the entity's tax year before modeling interest deductibility. Watch this for leveraged entities.
3. **Capital losses** — C-corp capital losses can only offset capital gains (not ordinary income). 5-year carryforward + 3-year carryback.
4. **§170 charitable** — 10% of taxable income limit (pre-deduction); 5-year carryforward.

### Penalty Taxes

1. **Accumulated Earnings Tax (§531)** — 20% surtax on unreasonably accumulated earnings beyond reasonable business needs (§535). Threshold: $250k accumulation safe harbor ($150k for PSC). Defense: documented business-need resolutions (expansion plans, working-capital needs, debt service). Coordinate with `governance.md` for board resolutions.
2. **Personal Holding Company Tax (§541)** — 20% surtax if (a) PHC income is **at least** 60% of adjusted ordinary gross income (§542(a)(1)) AND (b) > 50% in value owned by ≤5 individuals in the last half of the year (§542, with §544 attribution). Common trap for investment-heavy C-corps. Defense: dividend-out, §565 consent dividend, or convert income character; §547 allows a deficiency dividend after a determination. **Test PHC status before building any §531 record** — under **§532(b)(1) a personal holding company is not subject to the accumulated earnings tax**, so a Bardahl/business-needs file built for a corporation that is in fact a PHC defends against a tax it cannot owe while the real exposure goes untested. Ordering and cures: `scenarios/ccorp-tax-reduction.md`.

### R&D Expensing (§174A, restored by OBBBA)

- **Domestic R&E expensing is restored.** IRC §174A (enacted by OBBBA, PL 119-21) permits immediate expensing of domestic research & experimental expenditures, retroactively effective for tax years beginning after 12/31/2024. This replaces the TCJA-era §174 mandatory capitalization regime for domestic R&E.
- **Foreign R&E unchanged** — foreign-conducted R&E expenditures remain subject to mandatory 15-year amortization under old §174 (not restored to expensing).
- **Retroactive catch-up election (small business)** — taxpayers meeting the small-business gross-receipts test (average annual gross receipts ≤ $31M, indexed for inflation) may elect to retroactively re-treat 2022–2024 domestic R&E as expensed rather than capitalized, via amended returns or an accounting-method change.
- **Remaining unamortized 2022–2024 capitalized domestic R&E** — all taxpayers (not just small business) may elect to deduct any remaining unamortized balance over a 1-year or 2-year period, accelerating recovery of amounts already capitalized under the old rule.
- Coordinate with §41 R&D credit (still available; up to $500k payroll-tax offset for small startups) — the §280C(c) coordination between §174A expensing and the §41 credit still requires either a reduced credit or an addback; verify current-year mechanics before computing.

### §1202 QSBS (Biggest Tax Benefit in the Code for Founders)

C-corp stock issued at original issuance can qualify for a partial-to-full exclusion of gain on sale under IRC §1202, with the exclusion percentage, holding-period tiers, and caps determined by the stock's acquisition date (pre- vs. post-7/5/2025, per OBBBA PL 119-21). This is central to C-corp exit and equity-issuance planning — always confirm the entity's QSBS eligibility status in Preflight above. See `scenarios/qsbs-1202.md` for full QSBS/§1202 qualification rules, the pre-/post-7/5/2025 regime split, §1045 rollover, and stacking strategies.

### §1244 Small Business Stock (the downside twin of §1202)

§1202 pays off on a successful exit; **§1244 may pay off if the company fails** — ordinary loss (up to $50K/$100K MFJ per year, NOL-eligible) instead of capital loss on qualifying stock issued for money/property. The corporation ordinarily qualifies before its $1M capital-receipts transition, with a limited designation/allocation regime in the transitional year and no qualifying post-transition-year issuance. The doctrines overlap but are not coextensive: services can support §1202 but not §1244. Route the closing through `scenarios/stock-issuance.md` and document a separate result under `scenarios/section-1244.md`.

### M-1 / M-3 Book-Tax Reconciliation

- Schedule M-1 for assets < $10M. Instantiate `annual/m-1-reconciliation.md` from `templates/m-1-reconciliation.md.template`.
- **Schedule M-3** required if total assets ≥ $10M. Finer-grained reconciliation; required book source (GAAP statements or similar).
- Common M-1 items: federal tax expense (added back), meals (50% disallowance), fines/penalties, nondeductible life insurance, depreciation diffs, §263A, accrued comp to related §267 parties, deferred comp §409A.

### Planning Levers

- **Accumulated earnings defense** — board resolutions citing business need (see `governance.md` + `scenarios/ccorp-tax-reduction.md`).
- **Accountable Plan (Reg §1.62-2)** — shareholder/employee business expense reimbursement; tax-free to recipient, deductible to corp to the extent the underlying expense is deductible. A written plan is not a statutory requirement but is the best evidence. See `scenarios/accountable-plan.md`.
- **Home office (§280A(c)(1))** — reimburse via the accountable plan; never lease the owner's workspace to the corp (§280A(c)(6)). See `scenarios/home-office-280a.md`.
- **§280A(g) Augusta Rule** — corp rents owner's home ≤14 days/yr; rent is excluded from the owner's income under §280A(g); the corp's deduction is a **separate** question requiring ordinary, necessary and **reasonable** rent for bona fide business use under §162(a)(3) (excess is recharacterized as compensation or a constructive distribution), and accrual payers face the §267(a)(2) timing trap. (Not conditioned on the home *not* being the principal place of business — that is a common misstatement; see `scenarios/home-office-280a.md` §6.) See `scenarios/ccorp-tax-reduction.md`.
- **Family employment** — legitimate wages to family at arm's length; normal FICA since this is a C-corp (no family FICA exemption like Schedule C). See `scenarios/ccorp-tax-reduction.md`.
- **QSBS stacking** via non-grantor trusts — see `scenarios/qsbs-1202.md`.
- **Fiscal-year election** for deferral if owner-managed.
- **C-vs-S decision** — QSBS favors C; ongoing payout disfavors C (double tax); state-tax interaction matters; model with `strategy.md`.

## CSV → Form 1120 P&L Generation

For closely-held C-corps without a formal bookkeeper, the common workflow is: bank/CC CSVs → classify → P&L → return. This sub-skill supports that flow directly.

### Inputs

- `entities/<slug>/tax/FY<YYYY>/source/bank-cc/*.csv` — one file per account per period (or consolidated)
- `entities/<slug>/disregarded/<smllc-slug>/...` CSVs if nested SMLLCs have their own accounts
- `entities/<slug>/books/chart-of-accounts.md` — the destination account list
- `entities/<slug>/books/fixed-assets.md` — for depreciation inputs
- `entities/<slug>/tax/FY<YYYY>/source/brokerage/` — 8949, 1099-B, 6781 if trading activity
- `entities/<slug>/tax/FY<YYYY>/source/contractors-w9/` — W-9s for 1099 issuance
- `entities/<slug>/entity.md` — active strategies (Accountable Plan, Augusta, etc.)

### Process

Use pandas for reconciliation. For each transaction:

1. **Classify** into a chart-of-accounts line (income or expense account).
2. **Flag quarantines**: personal expenses on a business card (must be shareholder distribution or loan repayment, NOT deduction), round-dollar "cash" entries, duplicates across accounts, unclassifiable.
3. **Never force balance.** If accounts don't reconcile to period-end bank balances, stop and report.
4. **Departmental breakdown** — if nested disregarded SMLLCs exist, tag each transaction by entity source (e.g., `<parent-slug>` vs `<smllc-slug>`). Consolidate at the end.

### Output: `annual/pnl.md`

Follow Form 1120 structure — easier audit reconciliation:

```
<Entity Name> — Form 1120 P&L — FY<YYYY>
(All amounts consolidated including disregarded SMLLCs, shown with divisional breakdown)

=====================================================================
INCOME                               <Parent>    <DR SMLLC>   Total
=====================================================================
Line 1a Gross receipts                    $           $          $
Line 1b Returns and allowances            $           $          $
Line 1c Net receipts                      $           $          $
Line 2  Cost of goods sold (Form 1125-A)  $           $          $
Line 3  Gross profit                      $           $          $
Line 4  Dividends (Schedule C)            $           $          $
Line 5  Interest                          $           $          $
Line 6  Gross rents                       $           $          $
Line 7  Gross royalties                   $           $          $
Line 8  Capital gain net income (Sch D)   $           $          $
Line 9  Net §1231 gain (Form 4797)        $           $          $
Line 10 Other income                      $           $          $
Line 11 TOTAL INCOME                      $           $          $

=====================================================================
DEDUCTIONS
=====================================================================
Line 12 Compensation of officers (1125-E) $           $          $
Line 13 Salaries and wages                $           $          $
Line 14 Repairs and maintenance           $           $          $
Line 15 Bad debts                         $           $          $
Line 16 Rents                             $           $          $
Line 17 Taxes and licenses                $           $          $
Line 18 Interest                          $           $          $
Line 19 Charitable contributions          $           $          $
Line 20 Depreciation (Form 4562)          $           $          $
Line 21 Depletion                         $           $          $
Line 22 Advertising                       $           $          $
Line 23 Pension/profit-sharing            $           $          $
Line 24 Employee benefit programs         $           $          $
Line 25 Reserved                          -           -          -
Line 26 Other deductions (statement)      $           $          $
Line 27 TOTAL DEDUCTIONS                  $           $          $

Line 28 Taxable income before NOL/spec    $           $          $
Line 29a NOL deduction                    $           $          $
Line 29b Special deductions               $           $          $
Line 30 TAXABLE INCOME                    $           $          $
Line 31 Total tax (21% × line 30 + other) $           $          $
```

### Output: `annual/general-ledger.md`

Transaction-level, every row traceable to a source CSV line. Columns: Date | Account (COA line) | Debit | Credit | Source (CSV:row) | Description | Entity (if multi-division).

### Output: `annual/balance-sheet.md`

Schedule L format — beginning and ending balance sheet. Ties to M-1 net income + distributions.

### Output: `annual/m-1-reconciliation.md`

```
Book net income                           $
+ Federal income tax expense (book)       $
+ Meals disallowance (50%)                $
+ Entertainment (100% nondeductible)      $
+ Fines & penalties                       $
+ Depreciation book-tax diff              $
+ §263A UNICAP                            $
+ Accrued comp §267 disallowance          $
+ §174 R&D capitalization                 $
- Tax-exempt interest                     $
- [other]                                 $
= Taxable income (Line 30)                $
```

### Output: `annual/review.md`

Narrative — issues, elections, open questions, state filings, audit-risk callouts, §531/§541 exposure, §163(j) status, QSBS eligibility notes.

## Deadlines & Penalties

- **Form 1120 due** — under current **§6072(a)**, the 15th day of the **4th** month after the tax year ends; April 15 for a calendar-year corporation. Extension via Form 7004 → 6 months. (Current §6072(b) covers partnership and S-corporation returns, not Form 1120; do not cite it here.)
  - **June 30 fiscal-year transition.** For a C corporation whose tax year **ends June 30 and begins before January 1, 2026**, the return is due the 15th day of the **3rd** month (September 15) with a **7**-month Form 7004 extension. This is an effective-date rule in **Pub. L. 114-41 §2006(a)(3)(B)**, not a current-text exception. For a June-30 year beginning in 2026 or later, the general 4th-month/6-month regime applies. Applying the general rule to a covered June-30 year puts the unextended deadline a **month** late, on October 15.
  - Verify the year-end against the EIN letter and any Form 1128 before computing any date (Preflight #4).
- **Estimated tax (§6655 worksheet, formerly Form 1120-W)** — quarterly, due on 15th of 4th/6th/9th/12th month of fiscal year. Safe-harbor rules under §6655. Paid via EFTPS (no standalone voucher). See `quarterly.md`.
- **Form 1042 / 1042-S** — foreign-payee withholding returns, due March 15 following calendar year.
- **Form 1099-NEC** — to contractors by January 31; to IRS (electronic via IRIS) by January 31 for NEC (other 1099 types vary).
- **§6651 failure-to-file**: 5% of unpaid tax/month, max 25%. §6656 failure-to-deposit: 2-15% depending on lateness.

## Nested Disregarded SMLLCs — Critical

See `entities/disregarded.md` for the full treatment. Key points:

- SMLLC books consolidate into this entity's P&L as a division.
- SMLLC has its own bank account, W-9 (but using the regarded owner's EIN for federal tax), state registration.
- On Form 1120, the SMLLC is invisible — its activity is just the parent's activity.
- On state returns, the SMLLC may be separately regarded (e.g., WA B&O). Check state-by-state.
- When this entity issues 1099s/1042-S, contractors engaged by the SMLLC are still paid under the regarded parent's EIN.

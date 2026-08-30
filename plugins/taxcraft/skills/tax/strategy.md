# Tax Strategy & Planning Sub-Skill

Goal: identify tax-saving opportunities given the taxpayer's profile, and run scenario comparisons. Medium-aggressive posture with audit-risk callouts.

For a full optimization review (multi-entity sweep, doctrine stress-tests, adversarial pass, documentation matrices), also load `optimization.md` — it layers the deep-dive rigor on top of this catalog.

## Inputs
- `workspace-profile/owner.md`, `workspace-profile/entities-index.md` — scope awareness
- `individual/profile.md` + `individual/carryforwards.json` — individual-level facts
- `entities/<slug>/entity.md` — per-entity config + active strategies
- `<scope>/FY<YYYY>/tax-summary.md` (current working state)
- Most recent `<scope>/FY<YYYY>/.computed/<YYYY>-estimate.json` (if an estimate has been run)
- Current-year `rules/federal-<year>.json` (skill-bundled)

Strategy scope: strategies split by whom they benefit — the individual (1040), a specific entity (1120/1065/1120-S), or a combination (e.g., S-corp reasonable-comp split affects both the S-corp 1120-S and the shareholder 1040). Always state scope explicitly.

## Strategy Catalog (match to profile)

Only surface strategies whose prerequisites are met in the profile. Always state: (a) savings estimate, (b) audit-risk level, (c) authority, (d) prerequisites, (e) execution deadline.

### Retirement & Deferral
- **Max 401(k) elective deferral** — limit in rules file; include catch-up if 50+
- **Mega-backdoor Roth** — after-tax 401(k) + in-plan conversion or in-service rollover; requires plan support
- **Backdoor Roth IRA** — nondeductible trad IRA → Roth; watch pro-rata rule (aggregate all trad IRAs incl. SEP/rollover); Form 8606 tracking
- **HSA** — if HDHP; triple-tax-advantaged
- **Solo-401(k) / SEP-IRA** — for SE income and owner-operated entities
- **Deferred comp (§409A)** — if offered

### Pass-through Optimization
- **QBI §199A** — 20% deduction on qualified business income; below-the-line; SSTB limits; wage/UBIA limits above threshold; aggregation election
- **S-corp reasonable-comp split** — salary vs. distribution; save FICA on distribution portion; documented comp study recommended (audit risk elevated if underpaid)
- **Entity election changes** — LLC → S-corp election (Form 2553); weigh FICA savings vs. admin cost + QBI loss on W-2 portion
- **State PTE tax (PTET) elections** — state pass-through-entity-tax elections remain a full federal SALT-cap workaround, unaffected by OBBBA (entity-level deduction bypasses the individual SALT cap entirely). Relevant for owners of multi-state passthroughs with other-state-source income. The OBBBA SALT-cap MAGI phaseout (see `rules/federal-<year>.json` `salt_cap`) reduces the itemized cap to its $10k/$5k floor above ~$600k/$300k MAGI — this makes PTET relatively more valuable for HNW owners since it sidesteps the phaseout entirely. WA has no state income tax and therefore no PTET regime; this strategy applies only to income sourced to other PTET-electing states. Check entity's state(s) for election deadlines and mechanics.

### Real Estate
- **Cost segregation** — accelerate depreciation on 5/7/15-year components; best for new acquisitions or recent renovations with basis > ~$500k
- **Bonus depreciation** — OBBBA restored 100% bonus depreciation permanently for property ACQUIRED after 1/19/2025 (binding-contract date controls). Property acquired on or before 1/19/2025 stays on the pre-OBBBA TCJA phase-down (40% for 2025, 20% for 2026, 0% after) — check acquisition date carefully for assets straddling the cutoff. See `rules/federal-<year>.json` `bonus_depreciation`. §179 alternative below.
- **Real-estate professional status (REPS)** — §469(c)(7); 750-hr + >50% services test; converts rental losses from passive to nonpassive (huge if high W-2 paired with rental losses); spouse qualification is common strategy for MFJ; requires contemporaneous time logs
- **Short-term rental loophole** — avg stay ≤7 days + material participation = nonpassive without REPS
- **§1031 exchange** — defer gain on like-kind real property; 45/180 day rules; QI required
- **§121 exclusion** — $250k/$500k on primary residence; 2-of-5 year rule; partial if job/health/unforeseen
- **Opportunity zones** — defer + step-up + potential exclusion; tightening windows, check current
- **Grouping election** — Reg §1.469-4; treat multiple rentals as single activity for material participation

### Investment
- **Tax-loss harvesting** — realize losses; watch §1091 wash sale (30 days, same/substantially identical incl. spouse + IRA)
- **Asset location** — bonds/REITs in tax-deferred; growth/qualified-div in taxable
- **§1202 QSBS** — pre-OBBBA regime (stock acquired on/before 7/4/2025): 100% exclusion at 5-yr hold, cap = greater of $10M or 10× basis. OBBBA regime (stock acquired after 7/4/2025): tiered exclusion at 3/4/5-yr holds (50%/75%/100%), $75M issuer asset test (up from $50M), $15M per-issuer cap (up from $10M). C-corp stock, eligible trade/business; stacking via gifts to non-grantor trusts. See `scenarios/qsbs-1202.md` for full mechanics, examples, and the acquisition-date split — that file is the single home for QSBS detail.
- **§1244 small business stock** — the loss-side complement to §1202: ordinary loss (up to $50K/$100K MFJ per year, NOL-eligible) on original-issuance stock of a ≤$1M-capital corporation if it fails. Free at issuance; forfeited by sloppy paper (bare capital contributions, transfers, missing records). Paper every early-stage issuance for both §1202 and §1244. See `scenarios/section-1244.md` — the single home for §1244 detail.
- **§1045 rollover** — QSBS held <5 yrs, roll into another QSBS within 60 days
- **Direct indexing / loss harvesting at scale** — for large taxable portfolios
- **Muni bonds** — federal-tax-exempt interest; state-exempt if in-state; watch AMT on private-activity bonds

### Oil & Gas
- **Working-interest exception** — §469(c)(3) bypasses passive rules; losses fully deductible against wages
- **IDC election** — deduct intangible drilling costs currently (or §59(e) 5-yr amortize to avoid AMT)
- **Percentage depletion** — 15% of gross, subject to 65% of taxable income and 100% of net income per property; not available to majors
- **AMT preference tracking** — depletion in excess of basis, IDC > 65% rule

### Charitable
- **Bunching into DAF** — concentrate 2–5 years of giving in one year to exceed standard deduction, then take standard in off years
- **Appreciated stock vs. cash** — give LT appreciated stock (deduct FMV, avoid gain); 30% AGI limit
- **QCD from IRA** — age 70½+; up to annual limit (indexed); counts toward RMD; better than deduction for non-itemizers
- **CRT / CLT** — income or remainder trusts; large gifts
- **§170(e)(3) enhanced deduction** — inventory to qualifying charities (C-corp)

### Self-Directed IRA
- **UBIT / UDFI** — partnership K-1 with debt-financed income or active trade/business flows into IRA → 990-T filing required; tax at trust rates (steep); watch especially oil & gas working interests and real-estate partnerships with mortgages
- **Prohibited transactions** — §4975; disqualified persons; mistakes blow up the IRA

### Estate & Gift
- **Annual exclusion gifts** — per donee per year (rules file); spouse splitting doubles
- **Lifetime exemption planning** — OBBBA set the exemption at $15M (2026), permanent and indexed from 2027 — no sunset cliff. Planning is now ongoing optimization (annual exclusions, valuation discounts, GRATs/IDGTs) rather than deadline-driven use-it-or-lose-it.
- **GRAT / SLAT / ILIT / IDGT** — advanced structures; coordinate with estate attorney

### Credits
- **EV credits** — §30D new, §25E used; income + MSRP caps; dealer-transferred option
- **Residential clean energy** — solar/battery; uncapped 30%
- **Energy-efficient home improvement** — annual caps

### Timing & Acceleration
- **Roth conversion ladders** — fill low-bracket years (gap year, pre-RMD retirement, low-income years)
- **Accelerate deductions / defer income** — or reverse if rates rising
- **Installment sale** (§453) — spread gain over years
- **NUA on employer stock** — at separation, LTCG rates on appreciation

### For Business Owners (1065/1120-S/1120)
- **Augusta rule (§280A(g))** — rent home to own business ≤14 days/yr; excluded from owner's income, deductible to business; must be at FMV, documented. 14 days is per residence/homeowner, **not per entity**
- **Home office (§280A(c)(1))** — qualifies under any of three prongs; a **detached structure** qualifies on the easiest terms (§280A(c)(1)(C)). Owner-employees reimburse via accountable plan — never lease the space to their own entity (§280A(c)(6)). See `scenarios/home-office-280a.md`
- **Hire children** — under 18 in unincorporated family business exempt from FICA; up to std deduction tax-free; Roth IRA funding
- **Employee accountable-plan reimbursements** — available only when the payee incurred the expense in employee capacity, including eligible corporate owner-employees. A partner acting as partner instead uses the partnership reimbursement/UPE route. See `scenarios/accountable-plan.md`.
- **Employer-provided benefits** — Section 125 cafeteria, HRA, QSEHRA, ICHRA
- **R&D credit (§41)** — payroll tax offset up to $500k for startups
- **§179D / §45L** — energy-efficient commercial / new construction

## Scenario Runner

Given a strategy, produce a compact comparison:

```
Scenario: Bunch 2 years of DAF giving into 2025

                        Baseline       With Bunching
AGI                     $XXX,XXX       $XXX,XXX
Itemized deductions     $XX,XXX        $XX,XXX       (+$XX,XXX charitable)
Taxable income          $XXX,XXX       $XXX,XXX
Federal tax             $XX,XXX        $XX,XXX
                        —              ───────────
Savings 2025                            $X,XXX
2026 (standard)                        $0 incremental
Net 2-yr savings                        $X,XXX

Authority: §170(b)(1)(A); Rev. Rul. 2002-67
Audit risk: low
Prereq: already have or open DAF; contribute by 12/31
Deadline: 12/31/<year>
```

Save scenario outputs to `<scope>/FY<YYYY>/.computed/<YYYY>-plan.json` with an array of scenarios considered. Summarize the selected/recommended scenarios in `<scope>/FY<YYYY>/tax-summary.md` under *Open Issues & Audit-Risk Flags* or *Filing Plan*.

For accountable-plan eligibility, drafting, adoption, and operations see `scenarios/accountable-plan.md`. For other C-corp-specific strategies (§280A Augusta Rule, family employment, accumulated-earnings documentation) see `scenarios/ccorp-tax-reduction.md`. For entity-level trading (§1256, wash sales, fiscal-year 1099 mismatches) see `scenarios/entity-trading.md`.

## Year-End Checklist Template

When asked for year-end checklist, generate from profile + current date. Categories:
- [ ] Retirement contributions (deadlines: 401(k) = 12/31 payroll; IRA/HSA = April 15 next year; SEP/Solo-401(k) = extended filing)
- [ ] Roth conversions (12/31 deadline for current year)
- [ ] Loss harvesting (before year end; wash sale window)
- [ ] DAF contributions (12/31 for current-year deduction)
- [ ] RMDs (if 73+)
- [ ] QCDs (70½+)
- [ ] Estimated-tax Q4 (Jan 15 next year)
- [ ] Entity elections (S-corp election 2553 — 2.5 months after year start)
- [ ] Gift tax annual exclusion (12/31)
- [ ] FSA spend-down (if applicable; check carryover rules)
- [ ] 529 contributions (if in a state-deduction state)
- [ ] Review W-4 withholding for next year

## When to Pump the Brakes

- Any strategy involving offshore structures, conservation easements (syndicated), captive insurance (micro), or tax shelters flagged as listed/reportable under §6707A → warn strongly and recommend specialist consultation only.
- Strategies requiring contemporaneous documentation (REPS hours, Augusta rule, business use of vehicle/home) — stress documentation or don't recommend.
- Anything where the post-tax savings < professional fees + audit-risk cost → don't recommend.

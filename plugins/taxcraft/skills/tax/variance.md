# Variance / Flux Analysis Sub-Skill

Decomposes period-over-period and vs-prior-year drifts into drivers, narrates material changes, and **surfaces tax-specific risk triggers that would otherwise go unflagged**. Invoked from `quarterly.md` (after P&L, before estimate), `estimate.md` (individual — trigger drift), and `entities/<type>.md` annual close.

Relies on reconciled numbers — run `reconciliation.md` first. Inputs are reconciled P&L + BS per scope/period.

Comparison periods must be equal or explicitly normalized. Individual §6654
installment periods are 3, 5, 8, and 12 cumulative months, not equal quarters;
do not label a raw two-month-versus-three-month change as a business driver.
When prior value is zero, negative, or missing, report `NEW`, `NM`, or `UNKNOWN`
instead of an infinite or misleading percentage.

## When to run

| Scope | Comparisons |
|---|---|
| Individual quarterly | QoQ current FY; YTD vs same-YTD prior year; vs. annualized |
| Individual annual | YoY full-year; vs. 3-year average |
| C-corp quarterly | QoQ within FY; YTD vs. same-YTD prior FY; vs. plan if kept |
| C-corp annual | YoY; vs. 3-year average (for §531 AET documented business needs) |
| Partnership / S-corp quarterly | QoQ; per-partner/SH allocated income drift |
| Partnership / S-corp annual | YoY; partner capital account % shift; allocation method drift |
| Disregarded SMLLC | Runs variance at its own level; parent aggregates |

## Decomposition

For every P&L line that moves more than the materiality threshold, decompose into:

- **Price** — rate change on existing volume
- **Volume** — unit-count change at prior-period price
- **Mix** — shift in product/service/customer/state composition
- **New / lost** — lines absent in one period
- **FX / timing / one-time** — carved out of recurring trend

Use a named driver only when operational evidence supports its inputs. The GL
alone normally does not prove price, volume, mix, or business purpose. Missing
driver evidence yields `UNEXPLAINED`; do not fabricate a narrative. Components
must foot to total change within the stated tolerance or the decomposition is
held and cannot drive an estimate.

Formula block per material line:

```
Δ total         = current – prior                         = XXX
Δ price         = (rate_curr – rate_prior) × vol_prior    = XXX
Δ volume        = (vol_curr – vol_prior)  × rate_prior    = XXX
Δ mix           = Σ (new%·new_rate – old%·old_rate) × vol = XXX
Δ new/lost      = income from new - income from dropped   = XXX
Δ one-time      = identified non-recurring items          = XXX
                                                          ===
Residual        = Δ total – sum(components)               = ≤ 1% of Δ total (else rework)
```

## Materiality thresholds (default)

| Scope | Line threshold | Explanation threshold |
|---|---|---|
| Individual | 5% of AGI OR $5k | Both of: 10% and $2k |
| Entity ≤ $5M rev | 5% of line OR $25k | Both of: 10% and $10k |
| Entity > $5M rev | 3% of line OR $100k | Both of: 5% and $50k |

Override in `<scope>/entity.md` or `profile.md` → `variance_thresholds` block.

## Narrative

For every flagged line, produce a 1–3 sentence narrative:

- What moved (line, direction, size)
- Why (driver from decomposition)
- Tax consequence, if any (see triggers below)
- Required action, if any (JE, disclosure, estimate update, planning move)

## Tax-specific risk triggers (run on every flagged line)

### Individual (1040)

| Trigger | Signal | Consequence |
|---|---|---|
| QBI phase-out drift | Taxable income approaching §199A threshold | Convert W-2 wages / UBIA levers; Augusta rule; SEP timing |
| Passive allowance | AGI crosses $100k (phase-out) or $150k (full) | $25k rental loss allowance disappearing |
| NIIT threshold | MAGI crosses $200k / $250k MFJ | §1411 3.8% on net investment income |
| AMT preference items | ISO exercise, large SALT, private-activity muni | Run Form 6251 |
| IRMAA | MAGI crosses Part B/D tiers (2-year lookback) | Medicare surcharges |
| SS taxability | Provisional income crosses $32k/$44k MFJ | 50% / 85% taxable |
| Roth conversion window | Bracket headroom before next threshold | Convert up to fill |

### C-corp (1120)

| Trigger | Signal | Consequence |
|---|---|---|
| §531 Accumulated Earnings Tax | Retained earnings ↑ while investments dominate & dividends absent | 20% penalty tax; contemporaneous board resolution = defense (→ `governance.md`) |
| §541 Personal Holding Co. | Passive income ≥ 60% of AGI test + ≤5 owners ≥ 50% | 20% penalty tax on undistributed PHC income |
| §163(j) interest limit | Interest expense ↑ near 30% of ATI | Carryforward added; election analysis |
| §174A / foreign R&E | R&E expense ↑ | For years beginning after 2024, test current domestic §174A expensing/elective treatment and transition rules; foreign R&E generally remains 15-year amortization. Verify target-year method and §41/§280C coordination. |
| §1202 QSBS clock | Gross assets approaching the §1202(d) ceiling — **the ceiling depends on the stock's issuance date** (OBBBA raised it for stock issued after enactment). `scenarios/qsbs-1202.md` owns the threshold; do not hardcode one here | Shut door before the applicable ceiling |
| Employee-reimbursement drift | Owner/employee payments lack evidence of compliant operation, or writing and actual practice conflict | Audit the actual arrangement under `scenarios/accountable-plan.md`; reclassify only amounts identified by its consequence matrix; adopt or repair written controls prospectively |

### S-corp (1120-S)

| Trigger | Signal | Consequence |
|---|---|---|
| Reasonable-compensation | Officer W-2 flat while net profit ↑ materially | IRS reclass risk; scenario/salary-review (→ `entities/s-corp.md`) |
| BIG tax window | Within 5 years of C-corp conversion + appreciated assets sold | 21% BIG tax at entity level |
| AAA vs. E&P | Distributions exceed AAA with accumulated E&P present | Dividend income to SH |
| 2% shareholder health | Premiums not in W-2 Box 1 | Deduction lost + self-employed health insurance mis-reported |
| Basis ordering | Losses claimed beyond stock+debt basis | Suspended under §1366(d) |

### Partnership (1065)

| Trigger | Signal | Consequence |
|---|---|---|
| §704(b) capital / tax drift | Book-capital vs. tax-capital ratio shifts | Allocations may violate substantial-economic-effect |
| §704(c) built-in gain/loss | Contributed property appreciated/depreciated | Forward/reverse allocation required; ceiling/remedial method |
| §163(j) double test | Partnership level AND partner level | EBIE tracking per partner |
| Guaranteed payment drift | GP expense ↑ with SE tax implications | §1401 exposure |
| §754 election value | New partner joins at premium OR property distribution | Consider election; one-time, irrevocable without consent |
| Disguised sale (§707) | Large contribution followed by distribution within 2 years | Recharacterization as sale |

### Disregarded SMLLC

Variance runs at nested level; tax consequences evaluated at the **regarded parent**'s entity-type triggers above.

## Output format

`<scope>/FY<YYYY>/quarterly/Q<n>/variance.md` (quarterly) or `<scope>/FY<YYYY>/annual/variance.md` (annual):

```markdown
# Variance — <scope> FY<YYYY> Q<n>

## Comparison basis
- Current: <period>
- Prior:   <period>

## Flagged lines (above materiality)

| Line | Δ $ | Δ % | Driver | Tax trigger |
|---|---|---|---|---|
| Revenue | +$XXX | +12% | volume (new contract) | — |
| Interest expense | +$XXX | +45% | rate × balance | §163(j) watch |
| Retained earnings | +$XXX | — | profit retained, no divs | §531 AET — board resolution needed |

## Narratives
[one block per flagged line]

## Actions
- [ ] <owner> adopt board resolution documenting business need for retained earnings — before FY end
- [ ] Update estimate (Q<n+1>) for YTD trajectory
- [ ] Route §163(j) question to CPA
```

## Carryforward to estimate

After variance, hand annualized-income run to `estimate.md` (individual) or `quarterly.md` C-corp track. Variance-driven trajectory changes modify the annualized-installment calc per §6654/§6655.

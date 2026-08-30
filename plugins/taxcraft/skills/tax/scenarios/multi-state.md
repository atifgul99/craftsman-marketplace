# Multi-State Tax Scenario

When taxpayer has income sourced to states other than state of residence — common with K-1 portfolios, rental property out-of-state, RSU vested while residing elsewhere.

## Framework

1. **Identify resident state(s)** and any part-year dates
2. **Identify source states** from K-1 schedules, rental locations, 1099 payer addresses, work-performed-in locations
3. **For each nonresident state**: check filing threshold (some states: any source income; others: dollar thresholds); compute nonresident return on source-state income
4. **Resident state**: report all income; claim credit for taxes paid to other states (§901-analogs)
5. **WA resident**: no state income tax — no resident return to file; no credit mechanism needed; but must still file nonresident returns where required

## Common State Quirks

| State | Notes |
|---|---|
| WA | No personal income tax. B&O tax for businesses. Capital gains tax on gains > threshold since 2022 (ruled constitutional). |
| CA | Residency easy to trigger (physical presence 9 mo presumed); sourcing aggressive; LLC fee; PTE elective tax |
| NY | Statutory residency (183+ days AND permanent place); convenience-of-employer rule for remote; NYC additional |
| TX, FL, NV, WY, SD, AK, TN, NH (int/div only) | No broad personal income tax |
| OR | No sales tax but income-taxed; reciprocal with WA for some |
| OK, LA, NM, ND | Common O&G sourcing |

## K-1 State Apportionment

Fund provides state-allocation schedule. Each LP's share × state apportionment % = source income to that state.

- Fund may file **composite return** — covers nonresident LP's tax at top rate; LP can opt out in some states and file own return (often better if lower bracket)
- Fund may **withhold** at top rate; LP files own nonresident return to reconcile
- **PTE-tax elections** (workaround for SALT cap): entity pays state tax, deducts federally; partner gets credit on state return. Need to know if fund elected — check K-1 footnotes.

## Rental Property

Property in state X → nonresident filing in X on net rental income. If loss, may still file to preserve NOL carryforward for when property sells.

## Residency Changes

- Part-year return in each state for period of residence
- W-2 typically already split by state via box 15-17
- RSU/equity comp sourcing complex: mobile-employee rules allocate by workdays between grant and vest (or vest and sale for ISO); document carefully

## Output per State

```json
{
  "state": "WY",
  "tax_year": 2024,
  "residency_status": "nonresident",
  "sourced_income": 0,
  "state_filing_required": false,
  "reason": "WY has no individual income tax",
  "composite_paid_by_partnership": 0,
  "withholding_paid": 0,
  "state_tax_owed_refund": 0,
  "resident_state_credit_available": 0
}
```

For WA-resident user with WY K-1: typically no filing anywhere on that K-1's state-sourced income.

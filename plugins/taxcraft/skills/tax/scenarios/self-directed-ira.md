# Self-Directed IRA Scenario

Relevant when profile has a self-directed IRA (e.g., Directed IRA custodian). Major tax traps live here.

## Prohibited Transactions (§4975)

Fatal — entire IRA is deemed distributed on 1/1 of year of violation, taxable + 10% penalty if < 59½.

Disqualified persons (§4975(e)(2)):
- Account owner + spouse
- Lineal ancestors, descendants (NOT siblings)
- Fiduciaries, custodians
- 50%+ owned entities

Prohibited acts:
- Buying from / selling to disqualified person
- Renting disqualified person's property from/to IRA
- Providing services to IRA (sweat equity)
- Personal use of IRA property
- Personal guarantee of IRA-held debt

**Rule of thumb**: the IRA must deal at arm's length, with strangers. No dual roles.

## UBTI / UBIT (§511–514)

IRA is tax-exempt, BUT:

### UBTI — Unrelated Business Taxable Income (§512)
- Active trade/business income flowing through a partnership → UBTI
- Example: IRA owns LP interest in an operating business K-1 with box 1 ordinary income → UBTI
- $1,000 per year de minimis; above that → Form 990-T, taxed at trust rates (steep — 37% kicks in at ~$15k taxable)

### UDFI — Unrelated Debt-Financed Income (§514)
- Debt-financed income: rental or gain on property with acquisition indebtedness
- Example: IRA buys rental property with mortgage → portion of net rental + gain on sale = UDFI
- Debt-financed % = avg acquisition debt / avg adjusted basis
- Partnership K-1 box showing debt-financed income → passes through

### What AVOIDS UBIT
- Dividends, interest, royalties, rents from real estate (NON-debt-financed) — excluded under §512(b)
- Capital gains on non-debt-financed property — excluded
- Passive investments in C-corp stock — no UBTI

### Blocker Structures
- Many PE/VC funds offer "UBIT blocker" — feeder C-corp that pays corporate tax and passes dividends out clean; tax leakage but cleaner

## Form 990-T
- Filed by IRA custodian on behalf of the IRA (they charge for it; verify it's filed)
- IRA pays the tax from IRA assets
- Estimated payments may be required if > $500 tax

## Check K-1s for UBTI Indicators

- Box 20 code V — UBTI amount
- Box 20 code U — UDFI debt %
- Ordinary business income in box 1 with no offsetting "investment" language in footnotes
- Debt allocations in liabilities section

## Contribution / Distribution Reporting

- Form 5498 — contributions, rollovers, FMV year-end (custodian files)
- Form 1099-R — distributions (custodian files)
- RMDs — apply at 73 (SECURE 2.0); valuation of illiquid assets can be tricky for self-directed

## Checkbook-LLC / IRA-LLC

- LLC owned by IRA, manager is IRA owner
- Adds administrative ease but increases prohibited-transaction risk (owner as manager — Ellis v. Commissioner, other cases)
- If used, be disciplined: separate bank accounts, no personal use, no personal guarantees

## Review Output

```json
{
  "custodian": "Directed IRA",
  "tax_year": 2024,
  "fmv_ye": 0,
  "contributions": 0,
  "distributions": 0,
  "holdings": [
    { "type": "LP-interest", "entity": "...", "k1_box1_ordinary": 0, "ubti_indicated": false, "udfi_indicated": false }
  ],
  "990_T_filed_by_custodian": null,
  "990_T_tax_paid": 0,
  "prohibited_transaction_check": "none identified",
  "flags": []
}
```

## Always Ask
- "Are you aware of any personal use of IRA-held property?"
- "Any personal guarantees on debt in the IRA?"
- "Did you, your spouse, or your children provide services to any IRA-held business?"
- "Has the custodian filed 990-T for prior years where UBTI existed?"

These are the three questions that catch most catastrophic mistakes.

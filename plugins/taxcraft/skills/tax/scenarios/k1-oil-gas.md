# Oil & Gas K-1 Scenario

Relevant when profile has K-1s from entities classified `partnership-oil-gas`.

## Types of O&G Interests

- **Working interest (WI)** — bears costs, shares production. Key: §469(c)(3) **working-interest exception** to passive — losses are fully active/ordinary if the partnership is not a limited partnership AND the partner has personal liability. Watch: limited partners or LLC members without personal liability do NOT get this exception. Read the K-1 carefully (box: general vs. limited partner).
- **Royalty interest** — no cost burden; ordinary income; depletion available
- **Net profits interest** — hybrid
- **Overriding royalty** — carved out of WI

## Intangible Drilling Costs (IDC)

- §263(c) — fuel, labor, hauling, supplies, site prep — non-salvageable costs
- Election to **deduct currently** (default for independent producers) or **capitalize & amortize**
- **§59(e) election** — amortize IDC over 60 months → avoids AMT preference; useful when AMT would hit
- IDC in excess of 65% of net O&G income from all properties = AMT preference item (Form 6251)

## Depletion

Two methods, use the **higher** per property:

1. **Cost depletion** — (basis in property − prior depletion) × (units sold / total estimated reserves)
2. **Percentage depletion** — 15% of gross income from property, limited to 100% of net taxable income from property AND 65% of total taxable income from all sources
   - Not available to integrated oil companies (majors)
   - Available on ~1,000 BOE/day limit for independents
   - Can exceed basis — major benefit; creates basis-negative depletion (still deductible)

**AMT preference**: excess of percentage depletion over adjusted basis in property = AMT preference.

## At-Risk (§465) and Basis

- Must have basis AND at-risk amount to deduct losses
- WI partners: at-risk includes personal liability on recourse debt
- Nonrecourse debt generally NOT at-risk (real-estate qualified nonrecourse is an exception; O&G nonrecourse is not)

## State Filings

Oil & gas K-1s commonly source income to production states (TX, OK, WY, NM, ND, LA, etc.):
- **TX, WY**: no state income tax (still may have franchise/severance pass-throughs)
- **OK, NM, ND, LA**: nonresident filing threshold usually low
- Composite returns or withholding by partnership may cover; verify from K-1 state schedule
- **WY-sourced K-1**: WY has no individual income tax — nonresident filing typically not required

## Recapture on Sale

- **IDC recapture (§1254)**: on disposition, ordinary income to extent of prior IDC/depletion
- **Gain in excess of recapture**: §1231 → LTCG if net §1231 gains positive

## Passive Loss Interplay

- Working interest with §469(c)(3) exception: losses active; can offset wages
- Royalty interest: portfolio income, not passive
- Limited partner oil-gas WI: passive, subject to §469
- Read K-1 footnotes for classification — many PE/VC-style O&G funds structure as limited partnerships specifically so partners *don't* get active losses (trap for the unwary)

## Common K-1 Boxes to Watch

- Box 1 — ordinary business income (WI)
- Box 7 — royalties (portfolio)
- Box 10 — §1231 gain/loss (sales of property)
- Box 13 — other deductions incl. IDC, §59(e)
- Box 17 — AMT preferences (depletion, IDC excess)
- Box 20 — code Z QBI, code T depletion info, state apportionment

## Fund-Type Gotchas

- **Drilling-program partnerships** — often structured as WI to give investors active losses under §469(c)(3); verify general-partner/personal-liability status on K-1
- **"Oil fund" ETFs/PTPs** (e.g., commodity pool partnerships tracking crude futures) — K-1 with §1256 contracts, 60/40 LT/ST treatment; these are NOT O&G working-interest investments despite the name
- **VC/PE-style O&G funds** — often limited partnerships specifically so investors *don't* get active losses; trap for the unwary

## Review Output

```json
{
  "entity": "[entity name]",
  "tax_year": 2024,
  "classification": "working-interest-active",
  "authority": "§469(c)(3) working-interest exception",
  "at_risk_ok": true,
  "ordinary_income": 0,
  "idc_deducted": 0,
  "§59e_amortization_elected": false,
  "percentage_depletion": 0,
  "cost_depletion": 0,
  "depletion_used": "percentage",
  "amt_preference": 0,
  "state_allocations": [{"state": "WY", "income": 0}],
  "flags": []
}
```

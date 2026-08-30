# Wyoming State Tax — Overview

WY is one of the most tax-friendly states. No income tax, no B&O, no capital gains tax.

## Tax Obligations for WY Entities

| Tax | Status | Notes |
|---|---|---|
| State income tax | ❌ None | WY has no corporate or personal income tax |
| B&O / gross receipts tax | ❌ None | — |
| Sales & Use Tax | Only if selling goods/services in WY | Pure investment-holding entities: N/A |
| Personal Property Tax | County-level if business property in WY | N/A where the entity has no WY office or equipment |
| Franchise tax | ❌ None | WY does not impose franchise tax |

## Annual Report (SOS)

- **Who**: All WY LLCs and corporations
- **Due**: First day of anniversary month of formation (e.g., if formed in March → March 1 each year)
- **Where**: Wyoming SOS online → wyobiz.wyo.gov
- **Fee**: $60 minimum (or 0.0002 × assets in WY, whichever is greater; for holding companies with no WY assets, typically $60)
- **Registered agent**: Must maintain a WY registered agent. The agent of record for each
  entity is in `entities/<slug>/entity.md` → State Registrations, sourced from the formation
  documents in `entities/<slug>/corporate/formation/`.

## Which entities this applies to

Derive from `workspace-profile/entities-index.md` (formation state = WY) and confirm the
anniversary month and registered agent from each `entities/<slug>/entity.md`. Do not
maintain a roster here — see `states/README.md`.

## WY Nexus for Non-WY Activities

A common pattern: an entity is **formed** in WY but is operated and managed from another
state. Consequences:
- No WY tax liability (no income / B&O / gross receipts tax).
- **Foreign-qualification question in the state of management** — being managed from state X
  may constitute "doing business" there, requiring foreign registration and exposing the
  entity to that state's taxes. Formation state does not control this. Verify with counsel.
- Check whether the managing state taxes the entity's income type at all (e.g. WA has no
  income tax but does impose B&O on gross receipts — see `states/wa/bo-tax.md`).

## Adding WY Detail

If WY obligations expand (payroll, WY-sourced revenue, sales tax), create:
- `wy/sales-use-tax.md`
- `wy/annual-report.md`

# Washington State Tax — Overview

WA has **no personal income tax** and **no corporate income tax**. Tax exposure comes from:

| Tax | Admin | Who it hits | Load |
|---|---|---|---|
| B&O (Business & Occupation) | DOR / MyDOR | All entities with WA nexus on gross receipts | `bo-tax.md` |
| Retail Sales Tax | DOR / MyDOR | Sellers of tangible goods/certain services | `bo-tax.md` (brief) |
| Use Tax | DOR / MyDOR | Purchases without sales tax paid | `bo-tax.md` (brief) |
| Capital Gains Tax | DOR | **Individuals only** — LT gains > threshold; C-corps exempt | below |
| Personal Property Tax | County assessor | Business equipment/furniture held Jan 1 | `property-other.md` |
| Unclaimed Property | DOR | Uncashed checks, credits > 1 yr | `property-other.md` |
| Annual Report | SOS | All WA entities | `governance.md` (main skill) |

---

## WA Capital Gains Tax (individuals only)

- **Rate structure (SB 5813, effective TY2025, retroactive to 1/1/2025)**:
  - **7%** on net long-term WA capital gains from $0 up to $1,000,000 above the standard deduction
  - **9.9%** (7% base + 2.9% surtax) on the portion of gains **above $1,000,000** above the standard deduction
  - The **$1,000,000 surtax tier threshold is NOT indexed for inflation** (RCW 82.87.040) — unlike the standard deduction below, it stays fixed at $1M unless the legislature changes it
- **Standard deduction** (indexed annually by DOR):
  - **2024**: $270,000
  - **2025**: $278,000
  - **2026**: not yet published by DOR as of this update — **check dor.wa.gov for the current-year standard deduction** rather than relying on a hardcoded figure here
- **Charitable deduction (2025)**: gains above the $278,000 standard deduction threshold may deduct charitable contributions, **capped at $111,000** for 2025
- **Exemptions**: real estate (primary + investment), retirement accounts, farms, certain installment sales, timber, commercial fishing
- **C-corps**: exempt — not subject to WA CGT
- **Partnerships / S-corps**: flows to individual partners/shareholders; each person's share of LT gains counts toward their threshold
- **Filing**: WA CGT return due same date as federal 1040 (April 15, or extended date). Pay at dor.wa.gov.
- **Planning**: for each WA-resident individual, monitor aggregate LT gains across all K-1s + personal accounts; if approaching the standard deduction threshold (or the $1M surtax tier) in a calendar year, flag for harvest/deferral planning

> **Do not hardcode future-year threshold or deduction numbers in this file.** The standard deduction and charitable deduction cap are indexed annually by DOR and will go stale — always verify current-year figures at dor.wa.gov before relying on them.

---

## Entity Status at a Glance

> **Do not hardcode a registration roster here.** Registration status, UBI, filing frequency
> and next-due dates are per-entity facts — read them from `entities/<slug>/entity.md`
> → State Registrations, with the roster from `workspace-profile/entities-index.md`.
> Build the table below at read time:

| Entity | B&O Registered | UBI | Filing Freq | Next Return Due |
|---|---|---|---|---|
| *(from `entities-index.md`)* | *(from `entity.md`)* | *(from `entity.md`)* | *(from `entity.md`)* | *(derive via `calendar.md`)* |

An entity formed outside WA still registers if it has WA nexus — see the nexus rule below.
Treat "unconfirmed" as an open item, never as "not required".

## Nexus Rule (WA)

Physical presence in WA (office, employees, property) or economic nexus ($100K sales or 200 transactions in WA in prior or current year) triggers B&O registration obligation.

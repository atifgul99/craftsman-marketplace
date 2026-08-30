
# Entity-Level Securities Trading

When an entity (C-corp, S-corp, or partnership) holds brokerage accounts and trades securities. Different mechanics than individual traders due to entity-level reporting.

## Scope

Entity trades covered include:
- Long/short equities (1099-B + Form 8949)
- §1256 contracts — regulated futures, broad-based index options, non-equity options (Form 6781, 60/40 LT/ST treatment)
- Options on individual stocks (non-§1256)
- Crypto (reported as property)
- Bonds, T-bills

## Preflight

1. Load `entities/<slug>/tax/FY<YYYY>/source/brokerage/` — 1099-Composite, 8949 detail, 6781, trade confirms
2. Load `entities/<slug>/tax/FY<YYYY>/source/bank-cc/` — broker deposit/withdrawal activity
3. Load `entities/<slug>/books/fixed-assets.md` if any securities treated as §1221(a)(1) inventory (trader/dealer status; rare for closely-held entities)
4. Reconcile: broker statements' ending cash + positions = book values

## Form 8949 Reconciliation (Non-§1256)

Standard workflow:

1. Pull broker 8949 detail (PDF or CSV) covering ST covered, ST noncovered, LT covered, LT noncovered
2. Compare to 1099-B aggregates — they must tie
3. Identify wash sale adjustments (broker-reported in box 1g)
4. If entity uses mark-to-market election under §475(f) (rare for closely-held), compute YE mark instead
5. Produce Form 8949 for each character bucket

### Wash sale traps at entity level

- **§1091 wash sale rule**: loss disallowed if entity buys substantially identical security within 30 days before or after the loss sale; disallowed loss adds to basis of the replacement.
- **Related-party wash**: entity + owner individual's IRAs / Roth IRAs / spouse's accounts can trigger wash across accounts (see *Rev. Rul. 2008-5* for IRA wash treatment).
- **Track across accounts and entities** — this is the most common error. If one commonly-controlled entity's brokerage sells a security at a loss and another commonly-controlled entity's brokerage buys the same security within 30 days, *is* there a wash? Conservative answer: yes if commonly controlled and economic substance test suggests coordination. Flag.

## §1256 Contracts (Form 6781)

§1256 contracts include:
- Regulated futures (CME, ICE)
- Foreign currency contracts
- Non-equity options (index options like SPX, NDX)
- Dealer equity options (rare)
- Dealer securities futures

### Mark-to-market at year-end

§1256(a)(1): all open §1256 positions are marked to market on last business day of year. Unrealized gain/loss is taxed as if realized. Tax basis resets.

### 60/40 treatment

§1256(a)(3): net gain/loss is 60% LT + 40% ST regardless of actual holding period. At corp rate this doesn't matter (flat 21%); at individual/pass-through level through K-1 it's a major benefit vs. treating shorts as ST.

### Mixed straddle election (§1092 complexity)

If entity holds both a §1256 position and a non-§1256 leg of a straddle, consider mixed-straddle election or identified straddle rules to avoid loss-deferral traps. Advanced — usually requires a trading-focused CPA.

## Fiscal-Year 1099 Mismatch

Common issue for entities with non-calendar fiscal years (e.g., an entity with Oct–Sep FY):

- Brokers issue 1099s on a **calendar-year** basis (Jan–Dec) regardless of the recipient's FY.
- Entity needs to report trading activity for its fiscal year (Oct 2024 – Sep 2025).
- So the entity must split a calendar-year 1099 across two fiscal years.

### Reconciliation procedure

1. Pull calendar-year 1099-B detail (every trade date).
2. Filter to entity's FY window (e.g., trades settled 2024-10-01 through 2025-09-30).
3. Compute entity's FY totals from trade-level data (not from 1099 aggregates).
4. Document the reconciliation: `entities/<slug>/tax/FY<YYYY>/annual/workpapers/brokerage-fy-reconciliation.md` showing how the calendar-year 1099 was split.
5. Attach reconciliation to return (not required to file, but audit-defensible — IRS can't reconcile the 1099 to the return without this work).
6. At next FY, pick up the other half of the calendar-year 1099 and repeat.

### Warning

IRS matching on 1099-B uses SSN/EIN + calendar-year totals. A fiscal-year entity's return won't match 1099 totals one-to-one; this *will* generate CP2000 notices in some cases. Keep the reconciliation handy to respond.

## State Sourcing

If the entity has nexus in multiple states, trading income sourcing varies:
- **Apportionment states** (most): trading income in the sales factor as "other income" or investment income
- **Non-apportionment residency states**: sourced by entity residency
- **WA B&O**: investment income may be exempt from B&O if the entity is not primarily investing (different rules for dealer/trader/investor)

## Output Files

- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/form-8949-reconciliation.md`
- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/form-6781-§1256.md`
- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/wash-sale-analysis.md` (if any material wash sales)
- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/brokerage-fy-reconciliation.md` (for fiscal-year entities)

## Red Flags Requiring Specialist

- §475(f) mark-to-market trader election — eligibility factors
- §1256 mixed-straddle elections
- Crypto-to-crypto swaps, DeFi/staking/lending (novel tax treatment)
- Complex options strategies with straddle components
- PFIC (Passive Foreign Investment Company) holdings — Form 8621

For these, produce a memo summarizing the issue + facts and refer to a trader-tax specialist (Green Trader Tax, TraderStatus.com, or similar).

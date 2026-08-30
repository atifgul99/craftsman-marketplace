
# Entities Sub-Skill Router

Data preparation and workpapers for entities that file their own returns. **Does not file.** Output is audit-defensible workpapers + a review package the user hands to their CPA/EA or transcribes into tax software (Lacerte, UltraTax, ProConnect, Drake, TurboTax Business).

## Route by entity type

| Entity type | File the return? | Sub-skill |
|---|---|---|
| Partnership / multi-member LLC taxed as partnership | Form 1065 | `entities/partnership.md` |
| S-corporation (or LLC with S election) | Form 1120-S | `entities/s-corp.md` |
| C-corporation (or LLC with C election) | Form 1120 | `entities/c-corp.md` |
| Disregarded SMLLC | **No** — consolidates into regarded parent | `entities/disregarded.md` |
| Qualified Joint Venture (MFJ spouses in community-property state) | Two Schedule Cs on 1040 | *(no sub-skill — handled inline on individual 1040)* |
| Single-member LLC with S-election | Form 1120-S | `entities/s-corp.md` |
| Trust | Form 1041 | *(out of scope v1; flag to user)* |

Note: trust scaffolding is thin here, but non-grantor trusts are load-bearing for QSBS stacking (see `scenarios/qsbs-1202.md`) and for estate planning around the federal estate/gift exemption (permanently set at the elevated ~$15M/person level under OBBBA, rather than sunsetting to the pre-2018 ~$5M level after 2025). Whenever trust work arises, engage outside counsel — this skill provides scaffolding only, not authoritative trust/estate legal advice.

## Common Preflight (all entity types)

Before diving into the type-specific sub-skill, confirm:

1. Entity type, EIN, state of formation, tax year (calendar vs. fiscal).
2. Accounting method (cash vs. accrual) and whether book basis = tax basis.
3. Books loaded: trial balance, GL, fixed-asset schedule, depreciation rollforward (from `entities/<slug>/books/`).
4. Owners/partners/shareholders with ownership %, capital accounts, debt allocations, changes during year.
5. State filings footprint (where does the entity have nexus? composite/PTE elections?).
6. Any disregarded SMLLCs owned? → load their books; flows consolidate into this entity's P&L.
7. Federal filing deadline for this form + this fiscal year (extensions already filed?).
8. **Reconciliations cleared** for all periods closing into this return — see `reconciliation.md`. Unsigned recs block return-workpaper generation.
9. **Variance run** on annual P&L vs. prior FY — see `variance.md`. Tax-risk triggers surfaced there (§531/§541 for C-corps, reasonable-comp for S-corps, §704(b)/(c) for partnerships) feed the `review.md` narrative.

## Output Convention (every entity type)

Per year, produce:

- `entities/<slug>/tax/FY<YYYY>/annual/pnl.md` — full-year P&L matching the return's front-page income section
- `entities/<slug>/tax/FY<YYYY>/annual/balance-sheet.md` — Schedule L (beginning + ending)
- `entities/<slug>/tax/FY<YYYY>/annual/m-1-reconciliation.md` — book-to-tax diffs (Schedule M-1 or M-3 if $10M+ assets)
- `entities/<slug>/tax/FY<YYYY>/annual/variance.md` — YoY flux + tax-risk triggers (`variance.md`)
- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/recs/` — signed-off reconciliation files (`reconciliation.md`)
- `entities/<slug>/tax/FY<YYYY>/annual/general-ledger.md` — transaction-level journal
- `entities/<slug>/tax/FY<YYYY>/annual/workpapers/` — supporting schedules (fixed asset rollforward, basis, §199A detail, state apportionment, etc.)
- `entities/<slug>/tax/FY<YYYY>/annual/review.md` — narrative: issues flagged, elections considered, open questions, state filings needed
- `entities/<slug>/tax/FY<YYYY>/issued/k1s-issued/<recipient>.pdf` (partnerships + S-corps only) — per-owner K-1 data to feed the individual 1040 estimate

## Book-Tax Differences Checklist (all entity types)

Check these every return:

- Depreciation (book SL vs. tax MACRS/bonus/§179)
- Meals (50% tax, 100% book for entertaining)
- Fines / penalties (never tax-deductible)
- Political contributions (never)
- Life insurance premiums on key-person (not deductible if corp is beneficiary)
- Deferred comp / §409A
- Bad debt (specific reserve vs. direct write-off)
- Accrued comp to related parties (§267 deferral)
- §263A UNICAP capitalization
- R&E: domestic §174A expensing for TYs beginning after 12/31/2024 (OBBBA); foreign R&E still 15-yr §174 amortization; 2022–2024 capitalized domestic R&E catch-up elections — see `entities/c-corp.md`
- Entertainment (100% nondeductible post-TCJA)
- §162(m) comp cap (C-corps with public status; usually N/A for closely held)
- Qualified transportation fringe (§132; disallowance on the corp side)

## Non-Goals

- Do NOT produce filed forms as the final artifact. The user takes workpapers to a CPA or to commercial software.
- Do NOT sign anything, draft engagement letters, or represent the taxpayer.
- Always end with: "Verify with a licensed practitioner before filing. Entity returns have significant penalty exposure for errors (§6698 partnerships: $235/partner/month late; §6699 S-corps similar; §6651 C-corps)."

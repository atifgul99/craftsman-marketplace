# Rental Properties Scenario

## Per-Property Recordkeeping (in profile)

Required for each rental in `profile.income_sources.rentals[]`:
- Address
- Acquired date, sold date (if applicable)
- Purchase price, closing costs capitalized
- Land allocation % (from tax assessor ratio, or appraisal)
- Building basis = (price + cap'd closing costs) × (1 − land %)
- Capital improvements log (date, description, cost, recovery period)
- In-service date (first available for rent)
- Cost segregation study? (if yes, component schedule)
- Personal-use days vs. rental days per year (§280A)
- Active participation status (for $25k special allowance)
- Grouped with other activities under Reg §1.469-4? If yes, disclose on first return of grouping.

## Depreciation

- **Residential rental**: 27.5-year SL, mid-month convention (§168(c))
- **Commercial rental**: 39-year SL, mid-month
- **Land improvements (fence, paving, landscaping)**: 15-year, 150% DB or SL; eligible for bonus
- **Personal property (appliances, carpet, furniture)**: 5-year, 200% DB; eligible for §179 and bonus
- **Cost seg** typically reclassifies ~20–40% of building into 5/7/15-year components
- **Bonus depreciation**: 100% is permanent (OBBBA, PL 119-21) for qualifying property acquired after 1/19/2025 — no more phasedown. Property acquired under a binding written contract entered into before 1/19/2025 may still follow the pre-OBBBA phasedown schedule (check rules file for the applicable year's %, and confirm which acquisition-date rule applies)
- **QIP (Qualified Improvement Property)**: 15-yr SL, bonus-eligible

## Schedule E Part I Flow

Per property:
```
Rent received
  − Advertising
  − Auto/travel
  − Cleaning/maintenance
  − Commissions
  − Insurance
  − Legal/professional
  − Management fees
  − Mortgage interest
  − Other (utilities, HOA, supplies, pest, etc.)
  − Repairs (vs. improvements — see below)
  − Taxes (property)
  − Utilities
  − Depreciation
  = Net income/(loss)
```

**Repair vs. improvement** (Reg §1.263(a)-3):
- Repair: keeps property in ordinarily efficient operating condition — currently deductible
- Improvement: betterment, restoration, or adaptation — capitalize + depreciate
- **De minimis safe harbor**: $2,500/item (or $5,000 if AFS) — annual election
- **Small taxpayer safe harbor**: if gross receipts < $10M and unadjusted basis < $1M, can expense up to lesser of 2% of basis or $10k
- **Routine maintenance safe harbor**: recurring activities expected more than once in 10 yrs

## §469 Passive Activity Loss — routes out

**The passive layer is owned by `individual/loss-limitations.md` §2 and §2a** — the six
Reg §1.469-1T(e)(3)(ii) exceptions (including the ≤7-day short-term rental rule),
material participation and its substantiation, REPS under §469(c)(7) and the
employee-services exclusion, the Reg §1.469-9(g) aggregation election and its
release trap, the §469(i) allowance with its ownership and limited-partner gates,
grouping under Reg §1.469-4, the recharacterization rules including self-rental,
and the six §469(g) release rules. Do not restate any of it here.

Two intersections worth flagging from the rental side:

- **SE tax is a separate question from §469 status.** A short-term rental's
  average-stay test has no bearing on self-employment tax, which is governed by
  §1402(a)(1) and Reg §1.1402(a)-4(c)(2) (services beyond those customarily
  rendered for occupancy).
- **Per-property records drive the per-activity schedule.** What this file owns —
  basis, land allocation, improvements, depreciation, personal-use days — is the
  input to that schedule.

## §121 Primary Residence Exclusion — routes out

**The sale sequence is owned by `individual/1040.md` §6**, which runs the
threshold gates, nonqualified use and its exceptions, the §121(c) partial
exclusion, depreciation recapture, the converted-residence loss-basis rule, the
§469(g) release, the character split, and the §1031 interaction in the required
order. Do not compute a §121 exclusion from this file.

The one point worth flagging here, because it is where this scenario intersects:
nonqualified use is **not** simply "rental periods post-2009." Under
§121(b)(5)(C)(ii)(I), trailing use within the five-year period after the property
was last the principal residence is excepted — so a home lived in and then rented
before sale generally has little or no nonqualified use, while rental *preceding*
the last period of residency does count. Build the use timeline before prorating.

## §1031 Like-Kind Exchange

- Real property for real property (post-TCJA; no more personal property)
- **45-day rule**: identify replacement within 45 days of transfer
- **180-day rule**: close within 180 days (or due date of return, whichever earlier)
- **Qualified Intermediary** required — cannot touch proceeds
- Defers gain; basis carries over (with adjustments); depreciation recapture deferred too
- **Boot**: cash or debt relief taxable to the extent received
- Watch related-party rules (§1031(f))

## Mortgage Interest

- Reported on 1098 per property
- Acquisition-debt cap: $750k post-TCJA (MFJ; single $750k too; MFS $375k) — old loans pre-12/16/2017 grandfathered at $1M
- On **rental** property: no cap; deductible as Schedule E expense (not Schedule A), always
- On **mixed use**: prorate by personal vs. rental days

## Sale / Disposition

- Schedule D + Form 4797
- **§1250 unrecap** (residential rentals): gain up to accumulated depreciation taxed at max 25% (not 20%)
- **§1245 recapture** (personal property e.g., from cost seg): ordinary up to depreciation
- **Installment sale (§453)**: spread gain over payments; but recapture (1245/1250 to extent ordinary) recognized in year of sale
- **Passive loss freeing**: suspended losses released on complete disposition to unrelated party

## State Considerations for Rentals

- Property located in state X → nonresident filing typically required (threshold varies)
- If X has income tax, net rental income is sourced to X
- Resident state usually gives credit for tax paid to X (no credit needed if resident state has no income tax)

## Output for a Rental-Focused Session

Produce the per-property array in `individual/FY<YYYY>/annual/workpapers/wp-schedule-e-p1.md` (one object per property):
```json
{
  "address": "[street, city, state]",
  "tax_year": 2024,
  "schedule_e_line_items": { "rents": 0, "advertising": 0, ... },
  "depreciation": { "building": 0, "improvements": [], "total": 0 },
  "net_income_loss": 0,
  "passive_suspended_applied": 0,
  "passive_suspended_ending": 0,
  "basis_adjustments": { "capital_improvements_ytd": [], "depreciation_ytd": 0 },
  "notes": []
}
```

# Equity Compensation Scenario

Types: RSU, ESPP, ISO, NSO, RSA (restricted stock), PSU. Each has distinct tax mechanics.

## RSU (Restricted Stock Units)

- Taxed at **vest**: FMV of vested shares = ordinary income, included in W-2 box 1 + box 14 (often labeled RSU)
- Employer withholds shares for taxes (typically 22% supplemental — often under-withheld for high-bracket)
- **Cost basis = FMV at vest** (post-2014 brokers track this; older grants may need adjustment)
- Sale: gain/loss vs. FMV-at-vest basis; ST/LT based on time since vest
- **Common error**: broker reports $0 basis on 1099-B for "noncovered" shares → user double-taxes; always verify basis = W-2 inclusion
- **Supplemental wage withholding shortfall**: if RSUs large, 22% is too low; owe at filing; advise Q4 estimated payment or W-4 extra withholding

## ESPP (Employee Stock Purchase Plan)

### §423 Qualified ESPP
- Discount up to 15% off lower of start/end-of-period price (lookback)
- No tax at purchase
- **Disqualifying disposition** (sold < 1 yr from purchase OR < 2 yr from offering start):
  - Ordinary income = (FMV at purchase − purchase price) on W-2 box 1
  - Remainder gain/loss = ST or LT cap gain
- **Qualifying disposition** (held ≥ 1 yr purchase + ≥ 2 yr offering start):
  - Ordinary income = lesser of (FMV at purchase − purchase price) OR (FMV at sale − purchase price) — capped at actual gain
  - Remainder = LTCG
- **Basis adjustment critical**: 1099-B shows purchase price; real basis = purchase price + ordinary income recognized. Otherwise double taxation.

### Non-qualified ESPP
- Discount taxed as ordinary at purchase

## ISO (Incentive Stock Option)

- No tax at grant
- No regular tax at exercise — BUT **AMT preference** on bargain element (FMV at exercise − strike) — hits Form 6251
- If held ≥ 2 yr from grant AND ≥ 1 yr from exercise → qualifying disposition → all gain LTCG
- Disqualifying disposition → bargain element (or actual gain, if lower) = ordinary (W-2 box 1); remainder ST/LT cap gain
- **AMT Credit (Form 8801)** — AMT paid due to ISO exercise is a deferral item → credit recovered when regular tax > tentative AMT in future years
- **Dual basis**: for regular tax, basis = exercise price; for AMT, basis = FMV at exercise. Track separately.
- **Planning**: exercise early in year → if drops, sell by 12/31 same year → disqualifies but avoids AMT on gain that didn't materialize
- **$100k rule**: first $100k FMV (at grant) vesting per year qualifies as ISO; excess is NSO

## NSO (Non-qualified Stock Option)

- No tax at grant
- Exercise: bargain element (FMV at exercise − strike) = ordinary income, W-2 box 1, withholding applies
- Basis = FMV at exercise
- Subsequent sale: cap gain/loss vs. that basis

## RSA (Restricted Stock Award — founders) / §83(b) Election

- Route any actual issuance through `stock-issuance.md`; this section owns the
  compensatory-tax branch, not corporate or securities-law closing.
- Establish when **beneficial ownership was transferred** under Reg.
  §1.83-3(a). Approval, signing, payment, certificate delivery, and transfer can
  be different dates. Do not call the approval date the transfer date without
  evidence.
- Default under §83(a): when the stock becomes transferable or is no longer
  subject to a substantial risk of forfeiture, ordinary compensation income is
  `FMV then − amount paid`, with employer withholding/reporting and a potential
  §83(h) deduction. Track vesting, repurchase price, forfeiture, and payroll.
- A §83(b) election includes `FMV at transfer − amount paid` in income in the
  transfer year. It must be filed **no later than 30 days after the property
  transfer**; use the actual transfer date, not a vague “grant” date.
- An election is generally irrevocable without IRS consent. Later forfeiture
  does not refund the compensation income previously included; any loss is
  generally limited by §83(b)(1) to the excess of amount paid over any amount
  realized on forfeiture. Explain this downside before execution.
- Use current Form 15620 or a compliant written election. Verify required
  contents, signature, timely IRS delivery proof, copy to the service recipient,
  copy to the transferee if different, and retention in the closing binder.
- Record FMV support, amount paid, stock/class/shares, restrictions, transfer
  date, 30-day deadline, election decision, proof, W-2/withholding, employer
  deduction, stock basis, and holding-period start.
- Under Reg. §1.83-4(a), the capital-gain holding period generally begins just
  after substantial vesting when no §83(b) election is made, and just after the
  property transfer when a valid §83(b) election is made. State the actual
  result; it can change the §1202 holding-period clock.
- Services may support §1202 original issuance but do **not** support §1244.
  Produce a separate result for each doctrine; do not describe them as an
  automatic pair.

## PSU (Performance Stock Units)

- Like RSU but subject to performance metric
- Taxed at vest (when performance resolved)

## QSBS §1202

Founders/early employees holding C-corp stock (not RSU/RSA-vested restricted stock in a pass-through, but actual QSBS-eligible C-corp equity) held past the applicable holding period may exclude some/all gain at exit under §1202.

See scenarios/qsbs-1202.md for full §1202/QSBS qualification rules, the pre-/post-7/5/2025 regime split, §1045 rollover, and stacking strategies.

## Withholding Diagnostics

- Big vest quarters often under-withheld (22% supplemental up to $1M; 37% over $1M)
- Estimate underpayment ~(marginal rate − 22%) × vest value → recommend Q4 estimated payment or increased W-4 withholding
- Watch safe-harbor: prior-year 110% (if AGI > $150k) vs. current-year 90%

## Transfers & Rollovers Between Brokers

- Transfer in-kind generally non-taxable event
- Basis and holding period carry over
- Verify receiving broker captured basis correctly (common bug — transferred lots show as $0 "noncovered")
- Keep the originating plan administrator's basis reports (Shareworks, E*TRADE, Fidelity SPS, etc.) as source of truth

## Review Output

```json
{
  "employer": "[employer]",
  "tax_year": 2024,
  "rsu_vested_shares": 0,
  "rsu_ordinary_in_w2": 0,
  "rsu_withheld_shares": 0,
  "espp_purchases": [{"date": "", "shares": 0, "purchase_price": 0, "fmv_purchase": 0, "fmv_offering_start": 0}],
  "espp_sales": [{"shares": 0, "basis_adjusted": 0, "proceeds": 0, "disposition": "qualifying|disqualifying"}],
  "iso_exercises": [{"shares": 0, "strike": 0, "fmv_exercise": 0, "amt_preference": 0}],
  "iso_sales": [],
  "basis_corrections_needed_on_1099B": [],
  "est_payment_recommendation_q4": 0,
  "flags": []
}
```

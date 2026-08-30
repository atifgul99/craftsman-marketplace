# IRS/State Notice & Audit Response Scenario

Invoke when user has received an IRS or state notice, or suspects examination risk.

## First Steps

1. **Read the notice carefully** — identify type by notice code (top-right corner for IRS)
2. **Note deadlines** — most responses have 30/60/90 day deadlines; missing them forfeits rights
3. **Do not ignore**; do not pay without verification if you disagree

## Common IRS Notice Codes

| Code | Meaning |
|---|---|
| CP2000 | Proposed changes — mismatch between return and third-party info (1099, W-2, K-1); most common |
| CP14 | Balance due |
| CP501, CP503, CP504 | Escalating collection notices |
| LTR 0012C | Missing/incomplete info; reply required to process return |
| LTR 525 / 30-day letter | Exam report; 30 days to agree or request Appeals |
| LTR 3219 / 90-day letter / Statutory Notice of Deficiency | Tax Court petition window |
| CP2501 | Underreporter soft notice |
| CP259 | Return not filed |

## LTR 0012C

- IRS needs additional documentation to process
- Typical triggers: missing schedule, PTC reconciliation, identity verification, inconsistent W-2/1099 info
- Response: send requested docs within deadline (usually 20 days)
- Non-response = return not processed; refund held or assessment made without taxpayer input

## Substantial Understatement Penalty (§6662)

- 20% accuracy-related penalty if understatement > lesser of 10% of tax or $5,000
- Defenses: reasonable cause + good faith (§6664); reliance on competent professional; substantial authority; adequate disclosure (Form 8275)
- **Reasonable cause narrative** is the key write-up — what did the taxpayer know, when, what did they rely on, what steps did they take

## Response Structure

```
1. Taxpayer identification (SSN, name, address, tax year)
2. Reference notice number and date
3. Agree / disagree / partially disagree — state clearly
4. Itemize each proposed change; for each:
   - Original treatment
   - Basis for original treatment (citing Code/Regs/instructions)
   - Supporting documents attached
5. Corrected computation if any changes agreed
6. Signature, date, phone
7. Exhibit list
```

## Documentation Package

For K-1 mismatches (common CP2000 trigger):
- Original K-1 (all pages + footnotes)
- Final K-1 if amended
- Capital account / basis worksheets
- Prior-year carryovers affecting this year

For rental mismatches:
- Schedule E with detail
- 1098 + closing statements
- Depreciation schedule
- Repair vs. improvement backup

For equity comp mismatches:
- W-2 box 14 + supplemental supporting
- Grant/vest/exercise reports from broker/employer
- Basis adjustment computation for 1099-B

## Appeals

- If 30-day letter: request Appeals in writing within deadline
- Appeals is separate from Exam; fresh look; often settles at ~50% of proposed adjustment where hazards exist
- No new issues raised at Appeals (usually)

## Tax Court

- 90 days from Statutory Notice of Deficiency to file petition
- Small-case division (≤$50k) less formal
- Only venue to contest without paying first; District/Claims Court require prepayment

## State Notices

- Vary by state; read for deadline
- State Appeals processes generally similar to IRS but shorter windows
- PTE-tax payments and composite returns are common sources of state notice mismatches

## Audit Risk Reduction (going forward)

- **Form 8275 disclosure** for positions with substantial authority but less-than-more-likely-than-not
- **Adequate records** (§6001): contemporaneous logs for auto, home office, meals, REPS hours
- **Consistent reporting year-over-year** — changes invite questions, may require Form 3115 (accounting-method change)
- **Form 5471, 8938, FBAR** if foreign — non-filing penalties brutal ($10k+ per form per year)

## Output

Do NOT write the response letter as a final artifact — the user should have a CPA or EA review it. Produce a **draft with bracketed fields** + a **checklist** of supporting docs to attach, + a **legal-authority citation list** for positions taken.

Always end with: "Have an EA, CPA, or tax attorney review before sending. Notice responses create a record that may be used against you in subsequent proceedings."

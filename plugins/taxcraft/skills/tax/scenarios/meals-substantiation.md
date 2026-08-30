# Meals & Entertainment Substantiation (§274(d))

Invoke whenever a meal, entertainment, or client/investor-relations receipt is being ingested, categorized, or deducted — for any entity or individual (Schedule C). Covers the documentary-evidence threshold, the five mandatory elements, the 50% limitation, and split-bill handling. Intake mechanics (where the log lives, what fields the row needs) stay in `intake.md`; this file owns the doctrine.

## Receipt threshold (Treas. Reg. §1.274-5T(c)(2)(iii)(A))

| Charge | Documentary evidence (receipt) required? |
|---|---|
| < $75 | No receipt required — written record sufficient (date, amount, place, purpose, attendees) |
| ≥ $75 | **Receipt required** — written record alone is insufficient |

> This $75 threshold is per expense, not per day. A $160 dinner → receipt required.

## Five mandatory elements (§274(d)) — ALL must be documented

| # | Element | What to record |
|---|---|---|
| 1 | **Amount** | Exact charge (pre-tip + tip = total billed to card) |
| 2 | **Date** | Date of meal |
| 3 | **Place** | Name and address/location of restaurant |
| 4 | **Business purpose** | Specific business benefit expected — not "general goodwill." E.g., "discussed Q1 fund performance and the FY capital-raise strategy for [entity]." |
| 5 | **Attendees** | **Full name, title/company, and business relationship to the entity for each guest.** This is the most-missed element and the most common audit disallowance trigger. |

> Missing any one of the five can result in **100% disallowance** of the deduction, not just partial — IRS Audit Technique Guide for Travel & Entertainment.

**Attendee documentation detail required:**
- Name (first + last)
- Title or occupation
- Company/entity they represent (if applicable)
- Relationship: e.g., "prospective LP in [fund]," "current LP," "co-investor," "advisor"

Receipt files prove elements 1–3 (amount, date, place). Elements 4–5 (business purpose, attendees) exist only if written down — see `intake.md` for the exact log path and row format.

## 50% limitation (§274(n))

Meals are 50% deductible (C-corps and pass-throughs alike, absent a specific exception — e.g., de minimis fringe, certain employer-provided meals). Record the gross amount in the ledger; show the deductible half separately. The 50% haircut applies to the full charge including tip and surcharge — a service-charge surcharge is part of the meal cost, not a separate, fully-deductible fee.

## Split-bill handling

When the entity pays only its share of a group check:
- Record the entity's actual charge (what hit the card), not the full table total.
- Keep the itemized check photo anyway — it documents what was consumed (required by §274) even though the entity didn't pay the full amount.
- Note in the ledger: "Table total $X.XX; entity paid 1/N share."

## Traps

- **"General goodwill" as business purpose** — not specific enough; IRS Audit Technique Guide flags this as the top disallowance reason. Always tie to a concrete business topic or transaction.
- **Attendee list with first names only** — insufficient. Full name + relationship required.
- **Missing receipt on a $75+ charge treated as immaterial** — it isn't; the reg makes the receipt itself a required element above threshold, not merely supporting evidence.
- **Tip/surcharge excluded from the 50%-limited base** — wrong; both are part of the meal cost.
- **Entertainment (as opposed to meals) is 0% deductible** post-TCJA (§274(a)(1), effective 2018+) — do not apply the meals 50% rule to tickets, greens fees, or similar entertainment costs bundled with a meal; separate the meal charge from the entertainment charge if both appear on one bill.

## Outputs

- Expense-log row per `intake.md` (Date, Vendor, Category, Gross, Deductible, Payment, Business Purpose, Attendees, Receipt file(s)), with elements 4–5 written out in full — not abbreviated.
- Receipt file(s) retained per `intake.md` Receipt Intake Rules (itemized check photo + card-slip PDF).
- Any meal missing one of the five elements → flag in `open-questions.md` rather than deducting; do not silently claim 50% on an undocumented item.

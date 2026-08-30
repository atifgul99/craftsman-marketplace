
# Individual Permanent Records

The individual-side analog of `governance.md`'s corporate-document intake. It
owns the **third document pipeline**: permanent personal records that outlive any
tax year.

| Pipeline | Scope | Lives under | Owner |
|---|---|---|---|
| Tax-doc intake | Year-scoped (W-2, 1099, K-1, 1098, receipts) | `<scope>/FY<YYYY>/source/` | `intake.md` |
| Corporate-doc intake | Permanent entity records | `entities/<slug>/corporate/` | `governance.md` |
| **Personal permanent records** | Permanent individual records | `individual/records/` | **this file** |

## Why this exists

A W-2 matters for one year. A closing disclosure, a Form 8606, a §83(b)
election, a divorce decree, and a roof replacement matter for decades — and a
tax year folder is where they go to die. Every year they are not filed
permanently, the taxpayer moves closer to reconstructing basis from memory,
which is where returns become permanently and undetectably wrong.

---

## 1. The permanence test

Ask one question: **does this document establish a fact that will still be
load-bearing in a future tax year?**

| Answer | Destination |
|---|---|
| Yes — establishes a standing fact, an election, or a basis component | `individual/records/` (or the property/position folder that owns that basis — §4) |
| No — evidences this year's income, expense, or payment | `FY<YYYY>/source/` per `intake.md` |
| Both | File the permanent copy; put a pointer in the year folder. **Never duplicate the document.** |

Worked examples of the "both" case: a 1098 for a rental is year-scoped, but the
**refinance closing statement** behind it is permanent (tracing). A 1099-R is
year-scoped, but the **Form 8606** it feeds is permanent. A repair invoice is
year-scoped; a **capital improvement** invoice is permanent.

---

## 2. Folder map

```
individual/records/
├── individual-records-audit-FY<YYYY>.json   ← status/evidence SSOT for an audited year
├── _processed.log                            ← one line per processed document
├── identity/      ← SSN/ITIN cards, IP PIN letters (CP01A), name-change and
│                    status-change documents, naturalization/immigration status
│                    affecting residency, prior-address history
├── basis/         ← form-8606-basis.md (the SSOT) + basis-index.md (pointers only)
├── elections/     ← §83(b) filings + proof of mailing, §469 grouping disclosures,
│                    §199A aggregation, §59(e), QJV, mark-to-market §475(f),
│                    specific-ID standing instructions, §529 5-year elections
├── estate/        ← will, revocable/irrevocable trust instruments, POA, healthcare
│                    directive, beneficiary designations by account, filed Forms 709,
│                    prior estate/inheritance records establishing stepped-up basis
├── plans/         ← 401(k)/403(b) SPDs, IRA and HSA custodial agreements, SDIRA
│                    docs, 529 plan disclosure + account owner/beneficiary record,
│                    equity-comp plan documents and grant agreements
├── legal/         ← prenuptial agreement, divorce decree, separation agreement,
│                    QDRO, custody order + Form 8332, settlement agreements
└── insurance/     ← policies establishing basis/recovery (title, casualty), LTC
                     contracts relevant to §7702B
```

Property and pass-through basis records do **not** live here — see §4.

---

## 3. Intake loop

Runs whenever any of these fire:

1. A new file appears under `individual/records/**` with no matching line in
   `_processed.log`.
2. The user says: "I filed", "I signed", "I set up", "I updated my beneficiaries",
   "we bought/sold/refinanced", "I made the election", "we got married/divorced",
   or names a permanent event.
3. About to answer a question that depends on a standing fact — basis, an
   election, a beneficiary, a residency date, a property's history.
   **Verify no unprocessed records exist before answering.**

### Authorization boundary (first, always)

In a read-only scope: do **not** move, rename, log, cache, or update any profile.
Report the pending item and the field differences it may cause, then stop. Run
the mutation steps only after the user authorizes writes. This mirrors
`governance.md`.

### Steps (once writes are authorized)

1. **Classify** by the permanence test (§1). If the type is ambiguous — a draft
   vs. an executed agreement, a proposal vs. a filed election — **ask**. Do not
   guess.
2. **Extract** per the doctype schema (§5) using `pdftotext -layout` per
   `parsing.md`. Never the built-in Read on a PDF.
3. **Rename** to canonical form (§6) and file to the right subfolder.
4. **Update the fact it proves — and only that fact.** See the hard rule below.
5. **Log** to `_processed.log`.
6. **Surface** every field change to the user, with the before and after.

### Hard rule: the document controls only the fact it proves

A recorded deed proves title and date, not basis. A 5498 proves a contribution
was reported, not that it was deductible or nondeductible. A beneficiary form
proves a designation on its execution date, not the current designation if a
later form exists. A trust instrument proves terms, not funding. A closing
disclosure proves amounts paid at closing, not their capitalization treatment.

Update the standing field only when the document is competent evidence **for that
exact field**. Never overwrite source evidence with an inference.

### Anti-drift

When a new document contradicts a recorded standing fact, do not silently
overwrite. Record both, mark the field `CONTESTED` in the owning file, and raise
it in `FY<YYYY>/open-questions.md` with the two sources and their dates. Later
execution date generally controls for designations and elections; it does **not**
control for basis, where the earlier acquisition document remains authoritative.

---

## 4. Basis custody

This folder does **not** own all basis. Ownership is fixed in
`individual/1040.md` §5 and is not restated here. Summary of what lives where:

| Track | SSOT | This folder's role |
|---|---|---|
| IRA nondeductible basis (Form 8606) | `records/basis/form-8606-basis.md` | **Owns it.** No single account can, because §408(d)(2) aggregates across all traditional/SEP/SIMPLE IRAs. |
| Pass-through outside basis | `individual/investments/<sponsor-slug>/position.md` | Pointer only, in `basis/basis-index.md` |
| Property basis + improvements | `individual/properties/<slug>/depreciation-schedule.md` (running adjusted basis); `property.md` holds standing facts | Pointer only, in `basis/basis-index.md` |
| Securities lot basis | `individual/accounts/<broker-slug>/lot-basis.md` | Pointer only |
| Digital asset basis | `individual/accounts/<wallet-or-exchange-slug>/lot-basis.md` (per account — required by Treas. Reg. §1.1012-1(j)) | Pointer only |
| Roth basis and clocks | `records/basis/roth-basis.md` | **Owns it.** Not on Form 8606 Part I and **not** in `carryforwards.json` |
| ISO / AMT dual basis | `records/basis/amt-dual-basis.md` | **Owns it** |

`basis/basis-index.md` is a registry: one row per basis track, naming the SSOT
path, the as-of date, and the last document that moved it. It holds **no
figures**. Its purpose is that a future agent can find every basis track without
walking the tree.

**Append, never recompute.** A missing prior-year basis figure is a hold.

---

## 5. Extraction schemas by doctype

Extract these fields; leave anything not present in the document as
`NOT_PRESENT`, never inferred.

**Property acquisition (closing disclosure / settlement statement / deed)**
`property_address`, `closing_date`, `purchase_price`, `buyer_paid_closing_costs`
itemized into capitalizable vs. deductible vs. escrow, `loan_amount`, `lender`,
`seller_credits`, `prorated_taxes`, `recording_date`.
→ feeds `properties/<slug>/property.md`. Points and prepaid interest are
deductible items, not basis; escrow funding is neither.

**Capital improvement (invoice / contract / permit)**
`property`, `placed_in_service_date`, `description`, `amount`,
`asset_class_hint`, `permit_number`. → `properties/<slug>/improvements/`.
Do not classify repair vs. improvement here — that is
`scenarios/rental-properties.md` (§263(a) and the tangible-property regs).

**Form 8606 (filed)**
`tax_year`, `nondeductible_contributions_this_year`, `total_basis_end_of_year`,
`conversions`, `distributions`, `pro_rata_fraction_inputs`.
→ appended to `records/basis/form-8606-basis.md`.

**§83(b) election**
`grantee`, `issuer`, `grant_date`, `election_mailing_date`, `shares`,
`fmv_at_grant`, `amount_paid`, `proof_of_mailing`. The 30-day deadline runs from
the **transfer** date and is jurisdictional — record the mailing proof, not just
the form.

**Beneficiary designation**
`institution`, `account_last4`, `execution_date`, `primary`, `contingent`,
`per_stirpes_flag`. Later execution date controls.

**Trust / will / POA**
`instrument_type`, `execution_date`, `grantor`, `trustee`, `situs_state`,
`revocable_flag`, `ein_if_any` (masked to last-4), `funding_evidence_present`.
Do not summarize dispositive terms into a tax workpaper — record the fact and a
pointer. Estate planning is counsel's work.

**Divorce decree / separation agreement / QDRO**
`entry_date`, `filing_status_effect`, `alimony_flag_and_execution_date`
(pre- vs. post-2018 execution governs deductibility under TCJA §11051),
`property_transfers_1041`, `dependent_allocation_and_8332`,
`retirement_division_qdro`. → `records/legal/`, privacy rules in §8.

**Elections generally**
`election_type`, `code_section`, `tax_year_first_effective`, `filing_method`,
`revocability`, `attached_to_return_flag`. An election attached to a return is
proven by the return; a mailed election is proven by mailing evidence.

---

## 6. Canonical filenames

These extend `naming.md`, which remains the SSOT for filename rules generally.

| Document | Filename |
|---|---|
| Closing / settlement statement | `<yyyy-mm-dd> - closing - <property-slug>.pdf` |
| Deed | `<yyyy-mm-dd> - deed - <property-slug>.pdf` |
| Capital improvement | `<yyyy-mm-dd> - improvement - <property-slug> - <short-desc>.pdf` |
| Filed Form 8606 | `FY<YYYY> - 8606 - <taxpayer-slug>.pdf` |
| §83(b) election | `<yyyy-mm-dd> - 83b - <issuer-slug>.pdf` |
| Election (other) | `<yyyy-mm-dd> - election - <code-section> - <short-desc>.pdf` |
| Beneficiary designation | `<yyyy-mm-dd> - beneficiary - <institution-slug> - <acct-last4>.pdf` |
| Trust / will / POA | `<yyyy-mm-dd> - <instrument> - <grantor-slug>.pdf` |
| Filed Form 709 | `FY<YYYY> - 709 - <donor-slug>.pdf` |
| Divorce decree / QDRO | `<yyyy-mm-dd> - <decree\|qdro> - <matter-slug>.pdf` |
| Plan document | `<yyyy-mm-dd> - plan - <institution-slug> - <plan-type>.pdf` |
| IP PIN notice (CP01A) | `FY<YYYY> - CP01A - <taxpayer-slug>.pdf` |

`<short-desc>` ≤ 4 words, kebab-case.

## 7. `_processed.log` format

One line per document, append-only:

```
<yyyy-mm-dd processed> | <canonical filename> | <doctype> | <sha256 first 12> | <fields updated> | <target file>
```

The presence of a file in `records/**` without a matching line is the intake
trigger. No other infrastructure is required.

---

## 8. Privacy (extends `SKILL.md`)

`records/` holds the most sensitive material in the workspace. In addition to the
workspace-wide rules:

- **Minors' identifiers are masked entirely** in any narrative file — not
  last-4. Record "dependent child, DOB YYYY" and nothing more.
- **`records/legal/` is treated as non-summarizable** by default, on the same
  posture as `privileged` paths: do not parse, cache, or summarize its contents
  into tax workpapers. Extract only the specific tax-relevant field the return
  requires (filing status effect, alimony execution date, dependent allocation)
  and record a pointer for everything else.
- **Never write medical detail into a tax workpaper.** For HSA, medical
  deduction, or disability substantiation, record the amount, the date, the
  provider category, and a pointer. Diagnoses and treatment do not belong in a
  tax file.
- Health documents in `records/insurance/` follow the same rule.
- Beneficiary designations and estate instruments are not summarized into any
  file that could be shared with a preparer without the user's explicit
  instruction.

---

## 9. Retention and statute of limitations

The default answer to "can I throw this away?" is **it depends on which clock**,
and there are three.

| Clock | Rule | Practical effect |
|---|---|---|
| Assessment | §6501(a) — 3 years from filing (later of due date or actual) | Ordinary returns close after 3 years |
| Extended assessment | §6501(e)(1)(A) — 6 years if >25% of gross income omitted; §6501(e)(1)(A)(ii) — 6 years for >$5,000 omitted foreign income | Foreign or large-omission years stay open longer |
| No expiration | §6501(c) — fraudulent or unfiled return; §6501(c)(8) — **the entire return stays open** until required foreign information returns (5471, 8938, 3520, 8865, 8858) are filed | A missing foreign information return can hold an otherwise closed year open indefinitely |
| Refund | §6511(a) — later of 3 years from filing or 2 years from payment | Governs whether a 1040-X can still produce money |

**Keep forever regardless of any clock** — these establish facts used in years
that have not happened yet:

- Form 8606 series (lifetime IRA basis)
- Property acquisition documents and the complete capital-improvement history
- Depreciation schedules for every asset ever placed in service
- Pass-through outside-basis history and every K-1
- §83(b) elections and equity-comp grant records
- QSBS issuance records (§1202 holding period and gross-asset tests)
- Every filed Form 709 (cumulative — they compute the estate tax at death)
- Carryforward schedules (capital loss, NOL, passive, at-risk, charitable, AMT
  credit, §163(j))
- Divorce decrees, QDROs, and Forms 8332
- Records of any year with an unfiled foreign information return

**Retention classification** is recorded per year in
`individual-records-audit-FY<YYYY>.json` under the structured `retention_status`
object required by `schemas/individual-records-audit.schema.json`: an
`assessment` status (`OPEN`, `CLOSED_ASSESSMENT`, `EXTENDED_6501E`,
`PERPETUALLY_OPEN_6501C8`, `OPEN_FRAUD_OR_UNFILED`), a `refund` status (`OPEN`,
`CLOSED_REFUND`), and a `basis` status, which is always `RETAIN_INDEFINITELY`.
The three clocks are recorded separately because they expire separately. A year
is never marked closed by elapsed time alone — check §6501(c)(8) first.

**§6501(c)(8) is driven by IRS information returns only.** The schema's
`foreign_information_returns` array is the input to that hold. **FinCEN Form 114
(FBAR) is filed with FinCEN under Title 31 and is not an IRC information return
— it does not trigger §6501(c)(8)** and must not be treated as an input to the
hold, even though it is tracked in the same array for completeness. Its own
penalty regime is described in `individual/foreign.md` §2.

---

## 10. Output

`individual-records-audit-FY<YYYY>.json` (schema:
`schemas/individual-records-audit.schema.json`) records, per record class:
present / missing / contested, the evidencing document, the field it proves, the
target file it updated, and any open contradiction. It is the evidence SSOT that
`1040.md` preflight Step 1.7 (permanent records current) checks.

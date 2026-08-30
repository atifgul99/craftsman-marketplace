# IRS Transcripts

Transcripts are the authoritative record of what the IRS thinks happened. Pull them whenever remediating past years, preparing amended returns, responding to notices, or claiming penalty abatement. Relying on taxpayer recollection where a transcript would settle the question is malpractice.

## Five transcript types

| Type | Shows | Use |
|---|---|---|
| **Return transcript** | Line items as filed on the return | Diff against user's copy; detect transcription errors / identity-theft alternative return |
| **Account transcript** | All transactions posted to the account — payments, assessments, penalties, interest, liens, installment agreements, CP notices, audit flags, statute dates | **The one to pull first.** Shows what IRS is tracking and when each event posted |
| **Record of account** | Return transcript + account transcript combined | Use when comparing filed numbers against posted activity |
| **Wage & income** | Every 1099, W-2, K-1 the IRS received from third-party issuers | Critical for CP2000 defense, amended-return reconstruction, missing-docs situations. Lags — TY2023 transcripts complete ~mid-2024 |
| **Verification of non-filing** | Confirms no return on file for the year | Rarely needed; used for financial-aid and immigration filings |

## How to pull

| Method | Who | Turnaround | Covers |
|---|---|---|---|
| **IRS Individual Online Account** (irs.gov) | Taxpayer themselves | Instant | 1040 transcripts only, usually last 3-5 years |
| **IRS Business Tax Account** (irs.gov, growing coverage) | Corporate officer / partnership representative with verified identity | Instant where available | 1120/1065/1120-S/941 for supported entities — currently limited |
| **Tax Pro Account / e-Services TDS** | Enrolled practitioner with CAF number + POA (Form 2848) | Instant | All transcript types, all scopes |
| **Form 4506-T** (free) | Anyone with authorization | 10-30 days by mail | All types, all years; slow but reliable |
| **Form 4506** (paid, $30/return) | Anyone with authorization | 60-75 days | **Actual copies** of filed returns, not transcripts — use only when transcript isn't sufficient (e.g., attachments matter) |
| **IRS Practitioner Priority Service (PPS)** phone | Practitioner with POA | Immediate for guidance; faxed transcripts same day sometimes | Emergency pulls when exam/notice deadline is tight |

Check `workspace-profile/` for a CPA/EA with a Form 2848 POA on file before
routing. Where the taxpayer is self-prepared — no CAF number, no POA — which is
the common case for this skill, the practitioner rows above are unavailable and
the options are:
1. **IRS Online Account** for the individual's 1040 transcripts — fastest.
2. **IRS Business Tax Account** for entity transcripts, if the taxpayer is registered as responsible officer.
3. **Form 4506-T** mailed for what the online accounts don't cover — multi-week turnaround; plan for it.
4. If timeline is critical, **engage an EA or CPA to pull via TDS** — one-time engagement cost is usually $100-$300 and produces everything same-day.

## What to read for

### Account transcript — key transaction codes

| TC | Meaning |
|---|---|
| 150 | Return filed / tax assessed |
| 166 / 276 | Failure-to-file / failure-to-pay penalty assessed |
| 196 | Interest assessed |
| 276 | §6651 FTP penalty |
| 290 | Additional tax assessed (exam, CP2000, AAR) |
| 291 | Abatement of prior assessment |
| 300 | Additional tax from exam |
| 320 | Fraud penalty |
| 420 | Examination referral |
| 421 | Exam closed |
| 460 | Extension filed |
| 500 | IRS substitute for return (never let this happen) |
| 520 | Collection action held (litigation, bankruptcy) |
| 530 | Currently-not-collectible |
| 582 | Notice of Federal Tax Lien filed |
| 610 / 670 | Payment applied |
| 706 | Overpayment credit |
| 922 | CP2000 proposed assessment |
| 971 | Miscellaneous — cycle date usually encodes notice issued |

Pay attention to **CSED** (collection statute expiration date) and **ASED** (assessment statute expiration date) — derived from the 150 posting date + extensions. These govern what IRS can still do.

### Return transcript — what it won't show

- Attached statements, schedules K-1 issued, depreciation detail
- Anything on Form 8283 (charitable), 8606 (nondeductible IRA basis), 8949 (capital gains detail)
- Signature / preparer info

For those, pull actual copies via Form 4506 ($30 each) or the user's retained copies.

### Wage & income transcript — reconciliation gold

Every 1099, K-1, W-2 IRS received from issuers. If an upstream K-1 was issued to the wrong entity, it shows up on the wrong entity's transcript — and is missing from the right entity's. This is the single most reliable way to identify misrouted K-1s from years back.

For entity transcripts: request wage-and-income on the entity's EIN. For individual: on the SSN. Pulling both and comparing is a routine forensic step.

## Timing traps

- TY wage-and-income data is usually complete by **May of Y+1** (some issuers file late, adding to transcripts through Y+2). Pull late for most-complete picture.
- Account transcripts update weekly (IRS cycle). A just-posted event may take 1-2 weeks to appear.
- CP2000 proposed assessments (TC 922) are not actual assessments — they're proposals. Don't panic on TC 922 alone; resolve before TC 290 posts.

## What to do with transcripts once pulled

**Canonical filenames + location — see `naming.md` §"IRS transcripts".**

- Individual: `individual/FY<YYYY>/transcripts/FY<YYYY> - IRS <Type> Transcript - <scope-slug>.pdf`
- Entity: `entities/<slug>/tax/FY<YYYY>/annual/workpapers/transcripts/FY<YYYY> - IRS <Type> Transcript - <slug>.pdf`

Where `<Type>` ∈ {`Account`, `Return`, `Record of Account`, `Wage and Income`, `Verification of Non-Filing`}.

Parse via `tools/transcript-parser/transcript_parser.py` (text PDFs parse cleanly — uses `pdftotext -layout` internally). Run it interactively and confirm the y/n prompt to write; on confirmation it writes `<input>.parsed.json` next to the source PDF (not into a `.parsed/` subdirectory) matching the schema in `parsing.md`. It captures all TC transactions (with cycle + date + amount), flags exam / freeze / lien indicators, and extracts Wage & Income line items into `wage_income_items` for CP2000 reconciliation.

Re-pull: IRS updates transcripts weekly. Overwrite the same canonical filename on re-pull; `.parsed/_index.json` TTL class is `manual` so re-parse is explicit.

## Traps

- **Identity theft** — a return transcript showing line items the taxpayer doesn't recognize = someone filed using their SSN/EIN. File Form 14039 (individual) or 14039-B (business), set up IP PIN, do not file the legitimate return until resolved.
- **Substitute for return (TC 500)** — IRS filed on the taxpayer's behalf using worst-case assumptions. Always replace with an actual filed return; the SFR assessment stays on account until superseded.
- **Missing payment** — payments don't appear until posted (can lag 2-3 weeks from EFTPS debit). Verify before paying twice.
- **Different year on transcript than on return** — fiscal-year filers whose FY label differs from the period the return covers. IRS indexes by period-ending date, not the FY convention the skill uses. Reconcile labels before comparing.
- **No entity Business Tax Account** — still rolling out; not all entity types are supported. Fall back to 4506-T or TDS.

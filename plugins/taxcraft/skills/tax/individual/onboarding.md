
# Individual Onboarding

First-run setup for an individual taxpayer. `init.md` scans an existing workspace
and infers entities from filed returns; this file handles the case `init.md`
cannot — **a person who has never used this skill**, with an empty folder or an
unsorted pile of documents.

Design rule: **structure follows facts.** Never create a folder for a fact the
taxpayer does not have. A W-2 employee with a standard deduction should finish
onboarding with five files, not fifty.

---

## Mode selection

| The user has | Mode | Section |
|---|---|---|
| An empty or nearly empty folder | Interview | §1 |
| Documents, no filed-return history available | Shoebox | §2 |
| One or more filed prior-year returns | Prior-return | §3 |

Prior-return is strongest and should be preferred whenever returns exist — a
filed return answers most interview questions and carries the carryforwards.
Modes compose: run prior-return first, then interview only the gaps.

---

## 1. Interview mode

Ask in plain language, in this order. Stop early when the answers make later
questions moot. Do not ask for numbers — only for what exists.

1. Filing status, and did it change during the year?
2. What state do you live in, and did you move during the year?
3. Anyone you support — children, parents, others? Ages?
4. Do you have a W-2 job? How many employers this year?
5. Do you get stock from an employer (RSUs, options, ESPP)?
6. Do you own any property you rent out? How many?
7. Do you get K-1s from funds, partnerships, or businesses? Roughly how many?
8. Do you have brokerage accounts where you buy and sell?
9. Do you hold crypto or other digital assets?
10. Retirement accounts — 401(k), IRA, Roth, HSA, and have you done a Roth
    conversion or a backdoor Roth?
11. Any 529 or education accounts?
12. Do you have self-employment or 1099 income?
13. Any foreign accounts, foreign income, foreign gifts, or foreign entities?
14. Anything big happen this year — married, divorced, had a child, bought or
    sold a home, lost a job, someone died?

**Question 13 is not optional and is never skipped**, even for an obviously
simple return. Foreign information-return penalties are assessed independently of
tax owed, and the taxpayer usually does not know the question matters.

### Output of the interview

1. `individual/profile.md` from `templates/profile.md.template`, filled with what
   was answered and `NOT_PRESENT` for the rest. **No invented facts.**
2. The folder tree implied by the answers (§4 presets).
3. `FY<YYYY>/pending-docs.md` — the documents to expect, **by canonical name**
   per `naming.md`, so arrivals can be matched automatically.
4. A short "what applies to you" list naming the modules that will be loaded, so
   the user can see the scope.
5. `FY<YYYY>/open-questions.md` seeded with anything ambiguous.

---

## 2. Shoebox mode

Documents exist; nothing is organized.

1. **Inventory without moving anything.** List every file, classify by doctype
   from filename and first-page text (`parsing.md` discipline — `pdftotext
   -layout`, never the built-in Read).
2. **Report the inventory and the proposed plan.** Do not rename, move, or
   delete before the user authorizes writes. This is the same authorization
   boundary as `intake.md` and `records.md`.
3. **Split by the permanence test** (`records.md` §1): permanent records to
   `individual/records/`, year-scoped to `FY<YYYY>/source/<category>/`.
4. **Canonicalize names** per `naming.md`. Register every unknown employer,
   payer, broker, or sponsor in `workspace-profile/slugs.md` **before** using a
   slug — ask the user rather than inventing one.
5. **Derive the profile** from what the documents prove, then run the interview
   only for what they cannot answer (residency intent, dependents' support,
   foreign accounts, life events — documents rarely show these).
6. **Sweep for duplicates and sync conflicts** per `migrate.md`. Never
   auto-delete.

---

## 3. Prior-return mode

The best available start, and the honest answer to "help me understand my
situation."

> **Dependency:** `tools/return-parser/` handles **1065/1120/1120-S only** — it
> cannot parse a Form 1040. Until an individual return parser exists, use the
> bounded manual-extraction contract below. Do not claim automated extraction.

### Bounded manual extraction (per prior year)

Extract with `pdftotext -layout`, then record **only** these, each with a page
reference, each in the field-state vocabulary from `estimate.md`:

- Filing status, dependents, address, state
- Which schedules and forms were actually filed (this is the profile in
  disguise — a filed Schedule E means rentals or K-1s; a filed 8938 means
  foreign; a filed 8606 means IRA basis)
- Every carryforward **generated**: capital loss, NOL, passive by activity,
  at-risk by activity, charitable by class, AMT credit, §163(j), QBI loss
- Form 8606 ending basis
- Prior-year **total tax** (the exact line — required by `quarterly.md` for the
  safe harbor; a generic "total tax" is not acceptable)
- AGI
- Standing elections visible on the return (§469 grouping, §199A aggregation,
  QJV, §59(e), mark-to-market)
- Preparer, filing date, e-file vs. paper, and whether it was amended or
  superseded

Anything not legible is `UNREADABLE` and blocks the dependent line. **Never
infer "every carryforward" from a summary page** — a carryforward not evidenced
on the return is `NOT_PRESENT`, and a missing one is a hold, not a zero.

### Reconcile to the IRS

Where the user can pull them, reconcile the extracted return against the Account
Transcript and the Wage & Income Transcript (`scenarios/irs-transcripts.md`).
This catches a return that was filed differently than the copy on hand, an
adjustment the taxpayer never noticed, and third-party documents that never
reached them.

### First deliverable

Produce the `year-over-year.md` comparison across the extracted years. It is the
fastest way to surface a dropped K-1, a carryforward that vanished, a rental that
stopped depreciating, or an election that lapsed.

---

## 4. Archetype presets

Additive and composable. A preset creates skeletons and a checklist; it never
fabricates a fact. Every field starts `NOT_PRESENT`.

| Preset | Adds | Modules in scope |
|---|---|---|
| `w2-simple` | `FY<YYYY>/source/{w2, 1099s-received, 1095-health}` | `1040.md`, `credits.md` |
| `w2-equity` | + `accounts/<broker-slug>/` | + `scenarios/equity-comp.md`, `capital-gains.md`, `withholding-penalties.md` |
| `w2-landlord` | + `properties/<slug>/` per property, `books/` | + `scenarios/rental-properties.md`, `loss-limitations.md`, `itemized.md` |
| `w2-investor-k1` | + `investments/<sponsor-slug>/` per position | + `pass-through.md`, `ptp.md`, `loss-limitations.md`, `state-residency.md` |
| `crypto` | + `accounts/<exchange-slug>/`, wallet registry | + `digital-assets.md` |
| `self-employed` | + `books/`, `FY<YYYY>/source/{1099s-received, receipts}` | + `schedule-c.md`, `scenarios/home-office-280a.md`, `close-estimate.md` |
| `retiree` | + `accounts/` for each retirement account | + `retirement.md`, `health-benefits.md` (IRMAA), `estate-gift.md` |
| `family` | + `household/dependents/<slug>/` | + `credits.md`, `kiddie-dependents.md`, `education.md` |
| `foreign` | + `records/` foreign account register | + `foreign.md`, `foreign-escalation.md` |
| `tech-worker-full` | `w2-equity` + `w2-landlord` + `w2-investor-k1` + `crypto` + `family` | union of the above |

**`books/` is conditional** — created only under `w2-landlord` or
`self-employed`, and only at first close, matching the entity convention.

**Presets do not assert that their modules exist.** Check the build-status
markers in `README.md` before promising a capability. A preset may create the
folder structure and the pending-document checklist for a domain whose module is
not yet built; say plainly which parts of the taxpayer's situation the skill can
work today and which it cannot.

---

## 5. Completion contract

Onboarding is complete when:

1. `individual/profile.md` exists and every field is either evidenced or
   explicitly `NOT_PRESENT`.
2. The folder tree matches the preset(s) selected — **no empty folders for facts
   the taxpayer does not have**.
3. `FY<YYYY>/pending-docs.md` lists expected documents by canonical name.
4. `individual/carryforwards.json` exists, populated from prior-return mode or
   marked `as_of_tax_year: null` with an explicit note that no prior-year
   evidence was available.
5. The user has been shown: what was created, what was assumed, what is still
   unknown, and which modules apply to them.

State plainly what onboarding did **not** establish. A confident-looking empty
profile is worse than an obviously incomplete one.

## 6. What onboarding must never do

- Invent a slug, a basis, a carryforward, or a filing status.
- Create entity-grade structure for a simple return.
- Move or rename anything before write authorization.
- Skip the foreign question.
- Treat an absent document as a zero.

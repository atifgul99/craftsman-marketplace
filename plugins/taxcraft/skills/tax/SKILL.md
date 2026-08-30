---
name: tax
description: "Expert US tax, accounting, entity, and state-filing guidance for individuals, partnerships, S corporations, C corporations, disregarded LLCs, and multi-entity portfolios. Use for estimates, return workpapers, basis and carryforwards, tax planning and deductions (including accountable plans, home office, QBI, QSBS, §1244, and real estate), founder or investor stock issuances, payroll and owner compensation, corporate governance, notices and audits, WA taxes, and entity compliance. Trigger whenever the user asks about taxes, accounting, deductions, K-1s, estimated payments, issuing shares or founder stock, entity or state filings, governance records, or what an owner should pay or reimburse."
---

# Tax Expert Skill

## Analytical lenses

Apply the review disciplines below. They are analytical perspectives, not
claims that the model possesses a license, can represent a taxpayer, or can
form a privileged professional relationship:

- **CPA lens** — HNW private-client focus, pass-through portfolios, closely-held C-corps.
- **Enrolled-agent lens** — IRS procedure, audits, notices, and administrative guidance.
- **Tax-counsel lens** — source hierarchy across the IRC, Treasury Regulations, published guidance, and case law.
- **Forensic-accounting lens** — transaction-level GL reconstruction, reconciliation, audit-defensible workpapers.
- **Corporate-law lens** — 50-state corporate law (depth: WA RCW 23B, DE DGCL, CA Corp Code), bylaws, minutes, consents, veil protection.
- **Investment-tax lens** — brokerage reporting, wash sales, QSBS (§1202), §1031, OZ, PFIC, §1256, alts.
- **Real-estate-tax lens** — cost seg, §469, REPS, grouping, §1031, §121, STR analysis.
- **Oil-and-gas-tax lens** — IDC, depletion, §59(e), working-interest exception, AMT preferences.
- **Pass-through-tax lens** — partnership basis (§704(b)/(c), §743(b)), S-corp reasonable comp, QBI §199A, SDIRA UBIT/UDFI.
- **C-corporation-tax lens** — §531 AET, §541 PHC, §163(j), §174 R&D, Accountable Plans (Reg §1.62-2), §280A(g), family employment, NOL, §1202 planning.
- **Private-client lens** — the individual return over a multi-decade horizon: lifetime basis custody, retirement distribution sequencing, Social Security and IRMAA, education funding, estate and gift transfer, benefit eligibility (PTC/Medicaid MAGI), and life events. Coordinates across tax years rather than optimizing one.

Cite Code sections, Regs, and forms by number. Show math. Be precise.

## ⚠️ Disclaimer (once per session)

> This skill produces **estimates, analysis, workpapers, and governance drafts** — not tax advice, not a legal opinion, not a substitute for a licensed practitioner. Numbers must be verified by a CPA/EA/tax attorney before filing or before relying on them for estimated-tax payments. Governance documents must be reviewed by corporate counsel before signing. Aggressive strategies carry audit risk. No CPA-client or attorney-client privilege is created.

## First-run tooling check

The `tools/` scripts are standard-library only and need nothing installed. The
validators under `evals/` are different: they need two packages, and Claude Code
installs Node dependencies for a plugin automatically but has no pip equivalent.

**Run this check the first time a request will use a validator** — that is, any
close, estimate, rules change, stock issuance, or corporate-records work. Skip it
for a generic tax question that touches no artifact:

```bash
python3 -c "import jsonschema, markdown_it" 2>&1 || echo "MISSING"
```

If anything is missing, do **not** pre-authorize the install or run it silently.
Tell the user what is needed and why, then propose the command so their normal
approval prompt appears:

```bash
pip install jsonschema markdown-it-py
```

Say it in one line before proposing: *"The rules-freshness gate needs `jsonschema`
— without it I cannot verify your tax rules are current."* Offer `pip install
--user` when no virtualenv is active, or `uv add` in a uv-managed project. Ask
once per session, not per invocation.

**If the user declines, stop the task that needed the validator.** Do not proceed
and do not summarize as though the check ran. `evals/validate_rules.py` exits 2 on
expired tax data; a gate that could not run is not a gate that passed, and the
whole point of these checks is that stale rules produce confidently wrong numbers.
Say plainly which verification is unavailable and let the user decide.

## On Invocation: Router

1. Show disclaimer once per session.
2. Detect only the workspace state needed for the request:
   - For a generic question, skill audit, or read-only review, skip workspace
     initialization and do not load unrelated private profiles.
   - For entity- or taxpayer-specific work with no `workspace-profile/`, load
     `init.md`; if its Phase 1 detects a legacy structure, hand to `migrate.md`.
   - Otherwise, for entity- or taxpayer-specific work, briefly load only the relevant
     `workspace-profile/entities-index.md`, `owner.md`, `history.md`, and entity
     records.
   - If a needed canonical profile file is missing, report it. Create it from
     `templates/<name>.template` only when the requested scope authorizes
     workspace changes; never mutate the workspace merely to answer a question.
   - Do not improvise entity slugs without `workspace-profile/slugs.md`.
3. If the user's intent is already explicit, route directly to the relevant
   sub-skill. Otherwise show the router:

```
What would you like to work on?

  1. Work on a tax year                 — individual or entity; intake, estimate, strategy (estimates route through close-estimate.md)
  2. Quarterly close + estimate         — controlled close + 1040-ES / §6655 / applicable entity-state estimate
  3. Annual close + return prep         — controlled full-year close, Schedule L, M-1, workpapers
  4. Entity data prep (1065/1120/1120-S)
  5. Corporate records / governance     — record-book, formation cleanup, annual governance, standing
  6. Update profile / add entity
  7. Review carryforwards               — cap loss, NOL, AMT credit, passive, QBI, FTC
  8. Year-end planning
  9. Audit / notice response
  10. Strategy / transaction deep-dive  — Accountable Plan, stock issuance, §1244, QSBS, Augusta, cost seg, QBI, DAF, or full optimization review
  11. State tax                         — your resident and nexus states (WA and WY ship with depth; others resolved per authority.md and created on demand)
  12. Migrate legacy workspace          — rename folders + files to canonical layout
  13. Intake new documents              — canonicalize filenames + parse + update workpaper
  14. Multi-year remediation            — audit prior filings, reconstruct books, decide amendments, draft AAR/1065-X + partner 1040-Xs, pursue penalty abatement
  15. Compliance calendar / deadlines   — overdue + upcoming: estimates, annual reports, B&O, licenses
  16. Workspace health check            — verify canonical files, naming, caches, intake backlogs
  17. Personal return prep (1040)       — schedule-by-schedule workpapers, completeness, CPA handoff
  18. Personal records / lifetime basis — permanent documents, 8606 / outside / property basis, retention
  19. Life event                        — marriage, divorce, death, birth, home sale, job loss, move
  20. Set up an individual workspace    — first-run onboarding: interview, shoebox, or prior-return

Or describe what you need.
```

## Sub-skill files (loaded on demand)

| File | Purpose |
|---|---|
| `init.md` | First-time workspace setup: scan, draft profile + entity roster, seed folders |
| `migrate.md` | Convert legacy workspace to canonical layout (folders + filenames) |
| `layout.md` | Target workspace tree; regarded vs. disregarded placement rules |
| `naming.md` | Folder slugs, canonical document filenames, slug registry, collision rules, cross-workspace K-1 pointers |
| `parsing.md` | PDF read discipline, parsed-cache index, TTL classes, per-doctype JSON schemas |
| `intake.md` | Year-scoped document ingestion (canonicalize → parse → update workpaper) |
| `reconciliation.md` | Bank, brokerage, intercompany, K-1/capital, basis, AR/AP, fixed-asset, payroll, Schedule L rec — gate before P&L |
| `variance.md` | Period decomposition + tax risk triggers (§531, §541, §163(j), §199A, BIG, §704(b)/(c), reasonable-comp, etc.) |
| `authority.md` | Point-of-use current-authority, effective-date, rules-file, and fail-closed verification contract |
| `close-estimate.md` | Stateful orchestrator for annual estimates, controlled closes, installments, artifacts, and payment reconciliation |
| `estimate.md` | Individual Form 1040 computation reference; invoked through `close-estimate.md` |
| `quarterly.md` | §6654/§6655 installment and entity quarterly-close computation reference; invoked through `close-estimate.md` |
| `strategy.md` | Tax-saving opportunities + scenario comparisons |
| `optimization.md` | Deep-dive mode layered on `strategy.md` for FULL/broad optimization reviews (doctrine stress-tests, adversarial pass, documentation matrices, automatic state inclusion) — load for "tax leakage", "what am I missing", multi-entity structuring reviews. A single named strategy ("optimize my QBI") uses `strategy.md` alone; if "optimize X" is ambiguous between the two, ask |
| `individual/README.md` | Router into individual sub-skills; minimum-viable individual scope; individual high-risk routes |
| `individual/1040.md` | Individual return-prep **control**: source→form→line contract, limitation ordering, MAGI register, basis-ownership map, completeness invariants, §121 path, CPA handoff |
| `individual/records.md` | Personal permanent-records pipeline (third intake pipeline): permanence test, extraction schemas, `_processed.log`, basis custody, retention/SOL matrix, extended privacy |
| `individual/onboarding.md` | First-run individual setup: interview / shoebox / prior-return modes, archetype presets, completion contract |
| `individual/<domain>.md` | Individual domain modules — see `individual/README.md` for the symptom→module table |
| `entities/README.md` | Router into entity sub-skills |
| `entities/partnership.md` | Form 1065 workpapers, §704(b)/(c), K-1/K-2/K-3, capital accounts |
| `entities/s-corp.md` | Form 1120-S workpapers, reasonable comp, AAA, BIG tax, 2%-shareholder health |
| `entities/c-corp.md` | Form 1120 workpapers, SMLLC consolidation, M-1, §163(j), §174, §1202 |
| `entities/disregarded.md` | Nested SMLLCs: books at nested level, tax at parent level |
| `governance.md` | State-law drafting patterns, minutes/consents/resolutions, corporate-document intake, state filings, and veil discipline |
| `scenarios/<topic>.md` | Rental, K-1 (VC/PE, O&G), equity comp, SDIRA, multi-state, audit response, C-corp reduction, entity trading, **corporate-records** (C-corporation record-set lifecycle, authority chronology, completeness invariants, annual governance, standing/licenses, subsidiaries), **accountable-plan** (§62(c)/Reg §1.62-2 eligibility, audit, drafting, adoption, operations, payroll), **stock-issuance** (canonical authority → consideration → §351/§83/§1202/§1244 → securities → closing → ledger/accounting orchestrator), amend-partnership (BBA AAR / 1065-X / 1040-X cascade), penalty-abatement (Rev. Proc. 84-35 / FTA / reasonable cause / Form 843), irs-transcripts (pull + read + TC codes), tiered-partnership-se (GP-interest SE pass-through, *Soroban*), turbotax-business (`.tax20XX` file handling), qsbs-1202 (§1202 dual regimes pre/post-OBBBA), section-1244 (§1244 ordinary loss on small-business stock; bare-contribution basis trap), contested-k1 (disputed/withdrawn K-1, Form 8082, protective filings), aca-medicaid-magi (PTC/Medicaid MAGI management, Form 8962), meals-substantiation (§274(d)), home-office-280a (§280A(c)(1) three prongs, business %, accountable-plan vs. rent-to-employer, §121 exposure on separate structures) |
| `rules/federal-<year>.json` | Curated annual inputs; never self-authenticating—apply `authority.md` at point of use |
| `rules/manifest.json` + `rules/schema-v{1,2}.json` | Rules inventory, shape migrations, provenance metadata, and validation schema. New rules files validate against **v2** (v1 is frozen for external consumers; v2 is a strict superset that adds the freshness fields) — see `authority.md` |
| `templates/*` | Skeletons for every file the skill creates |
| `accounting-101.md` | Primer on three-timeline accounting (account / books / tax-year) + AICPA permanent-vs-current file framing — read when the folder structure feels arbitrary |
| `states/README.md` | State tax router — entity → state map, which file to load |
| `states/wa/README.md` | WA tax types overview: B&O, sales/use, capital gains, personal property |
| `states/wa/bo-tax.md` | WA B&O mechanics: classifications, rates, investment income exemptions, SBBC, MyDOR filing steps |
| `states/wa/property-other.md` | WA Personal Property Tax (King County) + Unclaimed Property |
| `states/wy/README.md` | WY: no income tax, annual report only |
| `calendar.md` | Compliance calendar — read-only deadline projection over `entity.md` + tax-summary + rules; dashboards, overdue/upcoming |
| `tools/README.md` | 9 shipped tools (pdf-extractor, chase-statement-parser, ibkr-parser, k1-parser, return-parser, transcript-parser, coa-categorizer, parse-verify, workspace-doctor) — see `tools/README.md` |
| `tools/workspace-doctor/` | Report-only lint: runs `python3 tools/workspace-doctor/doctor.py`; reports missing canonical files (e.g. `workspace-profile/slugs.md`), naming violations, empty parse caches, sync-conflict duplicates, unprocessed corporate docs — never modifies anything |

Read sub-skill files via Read tool as needed. Never load all upfront.

### High-risk direct routes

- C-corporation record-book audits, formation cleanup, annual governance,
  ownership-record reconciliation, “what documents do we need?”, and requests
  to determine whether a corporate set is current route first to
  `scenarios/corporate-records.md`. It owns scope, evidence/status
  classification, contradiction handling, and the record-set conclusion; it
  loads `governance.md`, `stock-issuance.md`, `accountable-plan.md`, and other
  specialists only for the issue they own. Drafting a particular bylaw,
  consent, minute, or resolution still routes to `governance.md`; new corporate
  PDFs still route to governance intake.
- Proposed, completed, disputed, or remedial shares, founder stock, restricted
  stock, subscriptions, SAFE/note conversions, splits, recapitalizations, or
  attempts to preserve §1202/§1244 treatment route first to
  `scenarios/stock-issuance.md`. It owns the closing sequence and tranche
  record, then loads `qsbs-1202.md`, `section-1244.md`, `equity-comp.md`, and
  `governance.md` only as the facts require.
- Existing-holding QSBS eligibility or disposition planning routes to
  `scenarios/qsbs-1202.md`; any proposed or remedial issuance still routes
  through `stock-issuance.md` first.
- Accountable-plan design, audit, drafting, adoption, reimbursement operations,
  owner advances, excess reimbursements, or payroll treatment route to
  `scenarios/accountable-plan.md`.
- Annual estimates, quarterly closes, installment questions, and “how much
  should I pay?” route to `close-estimate.md`; that orchestrator owns authority,
  evidence, reconciliation, payment-credit, and non-execution controls.

### Individual high-risk direct routes

These produce confident, plausible, wrong answers more often than anything else
on the individual side. Route first — do not answer from general knowledge. **If
any of these facts appear, load the module before computing anything.** The full
list, with the reasoning behind each route, is in `individual/README.md`
§ "High-risk routes".

- Any **IRA/Roth basis, conversion, rollover, RMD, or inherited-IRA** question
  routes to `individual/retirement.md`. Never answer a backdoor-Roth question
  without the 12/31 aggregate balance of all traditional/SEP/SIMPLE IRAs
  (§408(d)(2)).
- Any **foreign account, foreign entity, foreign gift, or foreign trust** fact
  routes to `individual/foreign.md` (and `foreign-escalation.md` for entities and
  trusts) **before** any income computation. Information-return penalties are
  assessed independently of tax owed, and an unfiled foreign information return
  can hold the entire year open under §6501(c)(8).
- **Wash sales, cost-basis corrections, or a loss sale near a purchase in any
  account including an IRA** route to `individual/capital-gains.md`. The IRA case
  destroys the loss permanently (Rev. Rul. 2008-5).
- A **Roth conversion or large one-time income event** routes jointly to
  `individual/retirement.md`, `individual/health-benefits.md` (IRMAA two-year
  lookback), and `scenarios/aca-medicaid-magi.md`. Never answer from the federal
  tax delta alone.
- **Sale of a residence that was ever a rental** routes to `individual/1040.md`
  §121 path — nonqualified use, unrecaptured §1250, and depreciation
  *allowed or allowable*.
- **Digital assets** route to `individual/digital-assets.md`; basis-lot method
  and the Rev. Proc. 2024-28 wallet-by-wallet transition are not the same as
  ordinary securities basis.

## Anti-duplication rule (STRICT)

**A fact lives in exactly one file.** Others reference it by pointer.

Two anchors, both shorthand — do not conflate them:

- `<scope>/FY<YYYY>/...` (year-scoped working files) resolves to `individual/FY<YYYY>/...` or `entities/<slug>/tax/FY<YYYY>/...` (entities carry the extra `tax/` segment).
- `<scope-root>/carryforwards.json` (year-crossing state, sibling of `profile.md` / `entity.md`) resolves to `individual/carryforwards.json` or `entities/<slug>/carryforwards.json` — **entities do NOT carry the `tax/` segment here**; `carryforwards.json` lives at the entity's root, not under `tax/`.

Defaults:

- Cross-entity roster → `workspace-profile/entities-index.md`
- Slug registry → `workspace-profile/slugs.md`
- Bank/brokerage accounts → `workspace-profile/bank-accounts.md`
- Per-entity standing config → `entities/<slug>/entity.md`
- Individual 1040 facts → `individual/profile.md`
- Disregarded SMLLC config → `<parent-scope>/disregarded/<slug>/entity.md`
- Year-crossing carryforwards → `<scope-root>/carryforwards.json`
- Year-specific working state → `<scope>/FY<YYYY>/tax-summary.md`
- Individually-owned property standing facts → `individual/properties/<slug>/property.md`
- Personally-held K-1 position facts and outside basis → `individual/investments/<slug>/position.md`
- Individual account facts → `individual/accounts/<slug>/account.md` (cross-scope roll-up stays in `workspace-profile/bank-accounts.md`)
- Household member facts → `individual/household/...`
- Lifetime IRA basis (Form 8606) → `individual/records/basis/form-8606-basis.md`

### Lifetime basis rule

Several basis tracks are **lifetime**, not year-scoped, and each has **exactly
one computational owner**. The authoritative map is `individual/1040.md` §5 —
it is not duplicated here, because a second copy is how the two drift apart.

Every other location holds evidence or a pointer. Lifetime basis is **appended
to, never recomputed from the current year alone**, and a missing prior-year
figure is a hold, not a zero.

## Workspace layout

`layout.md` is the tree SSOT (full folder tree + regarded-vs-disregarded placement rules) — read it, not the deployed root `CLAUDE.md`, which is intentionally a thin pointer and not a steady-state layout reference. Loaded only by `init.md` and `migrate.md`.

## Naming & parsing

- Any file the skill writes or expects — folder slug or document filename — follows `naming.md`. Violations found during intake or migration are corrected, not accepted.
- Any PDF read — use `pdftotext -layout`; never the built-in Read. Full rules + cache index + JSON schemas in `parsing.md`.

## Document intake pipelines (STRICT)

Three parallel intake pipelines exist. Pick the right one by **what the doc is**, not where it landed:

| Pipeline | Scope | Lives under | Owned by |
|---|---|---|---|
| Tax-doc intake | Year-scoped (K-1s, 1099s, W-2s, statements, receipts) | `<scope>/FY<YYYY>/source/` or `_intake/` | `intake.md` |
| **Corporate-doc intake** | Permanent entity records (state filings, licenses, BOIR, formation, resolutions, minutes) | `entities/<slug>/corporate/<subfolder>/` | **`governance.md`** |
| **Personal permanent records** | Permanent individual records (closing statements, improvements, 8606, elections, beneficiaries, estate, legal) | `individual/records/<subfolder>/` | **`individual/records.md`** |

The permanence test that separates pipeline 1 from pipeline 3 lives in
`individual/records.md` §1. The trigger, authorization boundary, and
"document controls only the fact it proves" rule are identical across pipelines 2
and 3.

### Trigger (fires from any sub-skill context)

First honor the request's authorization boundary. In a read-only review, do not
move, rename, log, parse to a persistent cache, or update any profile/entity
file. Instead, report the pending intake item and the field differences it may
cause; run the mutation steps only after the user authorizes writes. Subject to
that boundary, run the corporate-doc intake loop in `governance.md` whenever
ANY of:

1. User says: "I filed", "I provided", "I uploaded", "I renewed", "I submitted", "check (your/my) records", "update records", or names a corporate event (annual report, business license, BOIR, statement of change, foreign qualification, registered-agent change, formation amendment).
2. New PDFs appear under `entities/<slug>/corporate/**` without a matching entry in that subfolder's `_processed.log`.
3. About to answer a question whose answer depends on current state of `entities/<slug>/entity.md` standing fields (formation date, registered agent, principal office, expiration, governors, BOIR status, license status). **Verify no unprocessed corporate files exist before answering.**

### Hard rules

- **Filed document controls only the public field it proves.** After write
  authority exists, update a public-profile field only when the document is
  competent evidence for that exact field, and surface the change. A registry
  governor list, annual report, formation filing, or license does not by itself
  establish an internal director election, officer authority, shareholder or
  member status, issued shares, or legal ownership. In read-only scope, report
  the proposed field-level difference without changing or logging anything.
  Never overwrite source evidence from `entity.md`.
- **Process or disclose before answering.** Do not present stale standing/compliance fields as current while unprocessed corporate files exist. In read-only scope, answer only with an explicit pending-intake limitation and the proposed differences.
- **Local marker.** Each `corporate/<subfolder>/` is its own intake unit. The presence of a PDF without a matching `_processed.log` line is the trigger — no other infrastructure required.
- **Ask when ambiguous.** If a doc's type is unclear (renewal notice vs confirmation, draft vs filed copy), ask the user before logging.
- **State-generic.** Extraction schemas live in `governance.md` and are stated generically (Secretary of State / state revenue agency / FinCEN). State-specific field names and statutes are examples, not assumptions.

Mechanics (per-doctype extraction schemas, canonical filenames, `_processed.log` format, anti-drift handling) live in `governance.md` → "Document Intake (post-filing)".

## Current-authority, exact-value, and proposition rules

- Model knowledge can identify doctrine and likely issues; it does not verify a
  current exact value, effective date, form line, deadline, or state rule.
- A `rules/federal-<year>.json` value is a curated input, not proof. For every
  exact rule actually used, load `authority.md`, verify point-of-use coverage
  against a current primary source, and record the rule path and authority ID.
- Missing target-year rules, raw verification markers, filename/year mismatch,
  unresolved used paths, draft-only form mechanics, or superseded authority
  create a hold for the dependent result. Never guess, extrapolate, borrow a
  prior-year value, or convert an unknown to zero.
- Unrelated unresolved paths may remain as disclosed unused gaps; they do not
  block a result that does not depend on them.
- **The contract reaches qualitative propositions, not only values.** Background
  doctrine may be omitted from these files and creates no hold. But once a
  proposition is **used** to determine eligibility, character, ordering, release,
  a deadline, a transition rule, or a method, it is no longer background and must
  be verified at point of use and recorded. Files mark such propositions with
  **⚠**, which means exactly "verify before this determines a result" — see
  `authority.md` → "Qualitative propositions".

## Aggressiveness policy

Medium-aggressive strategies are in scope: backdoor/mega-backdoor Roth, QBI optimization, Augusta (§280A(g)), S-corp reasonable-salary tradeoff, Accountable Plan, family employment, cost seg, §1031, §1202, DAF bunching, CRT, loss harvesting, installment sales. Flag audit risk qualitatively (low / moderate / elevated) with authority. Do not suggest abusive shelters (listed/reportable per §6707A, syndicated conservation easements, micro-captives) except to warn.

C-corps: flag §531 AET and §541 PHC when retained earnings exceed documented business needs or investment income dominates. Contemporaneous board resolutions are the defense — coordinate with `governance.md`.

## Privacy & redaction (workspace-wide)

Root `CLAUDE.md` points here for privacy rules — this is the one place they live.

- Any narrative file the skill writes (logs, workpapers, summaries, follow-up logs) masks SSNs/EINs/account numbers to last-4. Full identifiers live only in source documents and their parsed JSON caches.
- Never paste tax IDs, account numbers, or document contents into web searches or external services.
- Paths containing `privileged` (e.g. `*attorney-client-privileged*`) are **excluded from all intake/parsing/summarization pipelines** — never parse, cache, or summarize their contents into tax workpapers (privilege-waiver risk). Handle only on explicit user instruction within that matter's own persona.
- Generated snapshots/exports contain no PII.
- Individual permanent records add three rules, owned by `individual/records.md` §8: minors' identifiers are masked **entirely** (not last-4); `individual/records/legal/` is non-summarizable by default on the same posture as `privileged` paths; and medical detail never enters a tax workpaper — record the amount, date, and category only.

## Style

- Show math. Readers verify.
- Cite authorities (IRC §, Treas. Reg. §, form number, state statute) for non-trivial claims.
- Compute as inputs → formula → result blocks.
- Tables for multi-scenario comparisons.
- Ask before assuming. Missing info → ask for the specific doc or figure by name.
- Never finalize a return; end entity work with "verify with your CPA/EA before filing."
- Never sign governance; end with "review with corporate counsel before signing."

## Connector roadmap (not built)

Plaid (bank/brokerage), county assessor scrapers, IRS transcript pulls, state SOS APIs, FinCEN BOIR portal, IMAP auto-detect. Intake is manual for now.

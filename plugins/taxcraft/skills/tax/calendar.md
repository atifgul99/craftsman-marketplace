# Compliance Calendar

Use this file when the user asks for upcoming deadlines, overdue items, renewals, filing calendars, extension dates, estimated-tax dates, annual reports, business-license renewals, WA excise/B&O due dates, or a compliance dashboard.

**Wired from:** `SKILL.md` router option 15 ("Compliance calendar / deadlines"). `governance.md`, `quarterly.md`, and the `states/` files answer **how much** is owed or what the mechanics are; this file answers **when it's due** — overdue/upcoming status only, no liability computation.

This is a read-only projection layer. It computes views from canonical source files and rules. It is not a registry of entity facts.

## Source-of-Truth Boundaries

Do not copy canonical facts into this file.

Read facts from:

- `workspace-profile/entities-index.md` for the entity roster and regarded/disregarded relationships.
- `entities/<slug>/entity.md` for regarded entity standing, fiscal year, tax classification, state registrations, filing frequency, license expirations, and public-record targets.
- `entities/<slug>/disregarded/<smllc-slug>/entity.md` for nested disregarded SMLLC standing and state obligations.
- `individual/disregarded/<slug>/entity.md` for individual-owned disregarded SMLLC standing.
- `<scope>/FY<YYYY>/tax-summary.md` for year-specific return, extension, payment, and carryforward status.
- `governance.md` for corporate filing/license intake rules and public-record refresh workflows.
- `states/<state>/` for state-specific filing rules.
- `rules/federal-<year>.json` for yearly federal constants when exact current-year numbers matter.

If a deadline cannot be proven from those sources or a formulaic rule, report it as `unknown_needs_source`. Do not guess.

## Output Modes

Default user-facing answers are redacted and concise.

Allowed default fields:

- Deadline date
- Status: `upcoming`, `due_today`, `overdue`, `filed`, `unknown_needs_source`, `blocked_by_unprocessed_docs`
- Category: federal return, federal estimate, state annual report, state excise/B&O, business license, local license, payroll, sales/use, property tax, unclaimed property, governance
- Entity label or slug
- Jurisdiction
- Source path
- Confidence: `document_confirmed`, `agency_observed`, `statutory_formula`, `inferred_from_entity_config`, `unknown`
- Basis: `statutory_deadline`, `agency_observed_deadline`, `extension_deadline`, `document_confirmed_deadline`, `user_status`, `unknown`

Do not show tax IDs, full account numbers, addresses, phone numbers, emails, correspondence IDs, confirmation numbers, payment card details, private investment details, or raw document excerpts unless the user explicitly asks for that exact disclosure.

## Required Preflight

Before answering a calendar question:

1. Load `workspace-profile/entities-index.md` if entity scope is broad.
2. For each relevant entity, read only its `entity.md` and needed `FY<YYYY>/tax-summary.md` files.
3. If `tax-summary.md` is missing for the target year, inspect the target `FY<YYYY>/` folder for narrowly named filed/extension/payment evidence (`extension`, `4868`, `7004`, `filed`, `payment`, `estimate`) before reporting unknown.
4. Check for unprocessed corporate documents under `corporate/**` if the answer depends on current standing, licenses, annual reports, or filed confirmations. Follow `governance.md` corporate-doc intake rules before relying on stale standing data.
5. Load only relevant state rule files under `states/`.
6. If exact federal current-year thresholds or rule amounts matter, load the matching `rules/federal-<year>.json`.

## Deadline Categories

### Entity Annual Reports and State Standing

Read from `entity.md` first:

- Current SOS expiration date
- Latest annual report on file
- Formation/registration date
- State of formation
- Public-record targets

Formulaic rules:

- WA SOS annual reports: use the `Current SOS expiration` date recorded in `entity.md` as agency-observed source. Do not recompute if agency-observed expiration exists.
- WY annual reports: due the first day of the anniversary month. Prefer any agency-observed due date or filed annual report in `entity.md`; otherwise compute from formation date.

If public-record freshness is needed, use `governance.md` public-record workflows. Do not use public search engines with private identifiers when official URLs are already recorded.

### Business Licenses and Local Licenses

Read from `entity.md` and processed corporate/license documents:

- WA DOR/BLS license expiration
- City/county license expiration
- Registered agent or mail-scanning renewals if the user asks for operational renewals

These are document-driven. Do not infer an active license or expiration unless the date is in `entity.md` or a processed source document.

### WA Excise / B&O

Load `states/wa/bo-tax.md`.

Read from `entity.md`:

- WA DOR registration status
- Filing frequency
- First return due date
- B&O classifications and income map

Formulaic due dates:

- Monthly: due the 25th day of the following month unless agency rules say otherwise.
- Quarterly: Q1 Apr 30, Q2 Jul 31, Q3 Oct 31, Q4 Jan 31.
- Annual: Jan 31 of the following year.

If filing frequency is unknown, output `unknown_needs_source` and request or locate the DOR registration/filing-frequency notice.

### Federal Income Tax Returns

Read entity type and fiscal year from `entity.md`; read filing/extension status from `FY<YYYY>/tax-summary.md` and filed folders.

Formulaic default rules, subject to weekend/holiday rollover:

- Form 1065 partnerships: 15th day of the 3rd month after tax year end; extension generally 6 months.
- Form 1120-S S corporations: 15th day of the 3rd month after tax year end; extension generally 6 months.
- Form 1120 C corporations: generally 15th day of the 4th month after tax year end, with special fiscal-year rules where applicable; extension generally 6 months unless IRS rule differs.
- Form 1040 individuals: generally April 15; extension generally October 15.

Do not mark a return filed or extended unless supported by filed confirmation, tax-summary status, or user instruction for the current task.

### Federal Estimated Taxes

Read entity type, fiscal year, and prior/current-year tax status from `entity.md` and `FY<YYYY>/tax-summary.md`.

Formulaic default rules, subject to weekend/holiday rollover:

- Individual 1040-ES calendar-year estimates: Apr 15, Jun 15, Sep 15, Jan 15 following year.
- Corporate estimates: generally 15th day of the 4th, 6th, 9th, and 12th months of the tax year.

If safe-harbor amounts or actual payment amounts are requested, route to `estimate.md` or `quarterly.md` and load the relevant federal rules file.

### Payroll, Sales/Use, Property Tax, Unclaimed Property

Include only when an entity's `entity.md`, state file, processed local document, or user instruction shows that regime applies.

If not established, output `unknown_needs_source` rather than assuming no obligation.

## Status Classification

Use today's local date.

- `overdue`: deadline is before today and no filed/paid/renewed evidence is found.
- `due_today`: deadline is today and no filed/paid/renewed evidence is found.
- `upcoming`: deadline is after today.
- `filed`: filed/paid/renewed evidence is found.
- `unknown_needs_source`: date or applicability cannot be proven.
- `blocked_by_unprocessed_docs`: relevant unprocessed corporate/license/tax files exist.

When asked "what is upcoming", default horizon is 120 days plus any overdue items. If the user asks for a dashboard, include overdue, next 30 days, next 120 days, unknown-needs-source sections, and action items.

## Action Items

When a scope has an action tracker, include open action items in dashboard-style output after deadline rows.

Recognized local trackers:

- `<scope>/FY<YYYY>/annual/workpapers/tracking-list.md`
- `<scope>/FY<YYYY>/open-questions.md`
- `<scope>/FY<YYYY>/pending-docs.md`
- `entities/<slug>/corporate/**/_processed.log` only for newly processed documents whose summary says `Action:`

Action-item rules:

- Report only open, check, action-required, blocked, or unknown items; omit closed/done items unless the user asks for audit trail.
- Preserve the source path and due date if stated.
- Do not duplicate a deadline row and an action item unless the action item explains a separate remediation step, such as "payment made but misapplied."
- Redact tax IDs, account numbers, confirmation numbers, addresses, phone numbers, emails, and raw correspondence IDs by default.
- If an action item requires logging into an agency portal, submitting a form, making a payment, or contacting an agency, label it `manual_user_action`.

## Generated Snapshots

If the user asks to save a dashboard or snapshot, write only under:

`workspace-profile/reports/calendar-snapshot-YYYY-MM-DD.md`

Each snapshot must start with:

```md
> Generated compliance-calendar projection. Not a source of truth. Do not edit computed rows manually. Verify with the agency portal or CPA/EA before filing or paying.
```

Snapshots may contain computed rows and source paths, but must not contain raw PII, tax IDs, addresses, account numbers, confirmation numbers, payment details, or private source excerpts by default.

## External Site Rules

- Prefer official agency URLs already recorded in `entity.md`.
- Use official IRS, state SOS, and state revenue pages for public deadline rules.
- Privacy/redaction rules (what never goes into web searches or third-party services) live in `SKILL.md` → "Privacy & redaction (workspace-wide)". Follow those; do not restate them here.
- Do not log into IRS, DOR, SOS, FinCEN, county, bank, brokerage, or benefits portals unless the user explicitly asks and the data scope is clear.
- Never submit filings, renewals, payments, or forms without explicit user instruction.

## Report Shape

For normal answers, use a table like:

| Date | Status | Entity | Category | Jurisdiction | Basis | Source |
|---|---|---|---|---|---|---|

Keep entity labels minimal. Use slugs when privacy matters.

After the table, include:

- "Local records only" or "Local records + public refresh" basis.
- Any unknowns that need source documents.
- Any blockers from unprocessed files.
- A short "next actions" list when useful, sourced from the action-item rules above.

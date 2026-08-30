# Authority and Rules Contract

Load this file whenever a tax result depends on an exact dollar amount, rate,
date, form mechanic, eligibility threshold, effective date, or other rule that
can change. This contract applies to federal, state, local, and benefits rules.

The bundled `rules/*.json` files are curated inputs, not self-authenticating
authority. Never treat the presence of a value in a rules file as proof that it
is current or applicable.

## Required result

For every rule actually used, record:

| Field | Required content |
|---|---|
| `dependency_id` | Stable run-local ID used by method records |
| `component` | `federal` or the exact state/local jurisdiction component that consumes the rule |
| `rule_origin` | `BUNDLED_RULES` for a rules-file path; `RUN_SPECIFIC` for a named rule verified during this run |
| `rule_path` | Exact JSON path or named rule |
| `jurisdiction` | Federal, state, or local jurisdiction |
| `tax_period` | Tax year and, when relevant, effective-date interval |
| `value_used` | Exact value, rate, date, or method |
| `authority_id` | ID from the rules-file metadata or a run-specific ID |
| `primary_source` | Code/regulation, official form instructions, revenue procedure, notice, or agency publication |
| `source_url` | Direct official URL; no search-result URL |
| `checked_at` | Date the source and future-developments page were checked |
| `status` | `VERIFIED`, `UNVERIFIED`, or `SUPERSEDED` |
| `scope_note` | Any limitation, election, transition rule, or fact dependency |

Store this table in the computation control workpaper. The estimate artifact
stores the exact `rule_path` and `authority_id`; it does not duplicate long
source descriptions.

`BUNDLED_RULES` dependencies must cross-check the rules-file authority ID and
coverage path. `RUN_SPECIFIC` dependencies use a `run-...` authority ID and
stand on their own recorded official source, effective dates, and fact scope;
they must not masquerade as bundled coverage. Validate the parsed HTTPS
hostname itself as an official `.gov` host (including eCFR and state/local
revenue sites), never by finding a government-domain substring inside a URL.
Use one authority ID and its exact primary-source URL per dependency record; if
a rule needs multiple authorities, create multiple records with distinct
dependency IDs so no source/ID relationship is ambiguous.

## Run-specific authority

Corporate-record audit artifacts point to this section as
`authority.md#run-specific-authority`. Each instantiated dependency must use a
unique `run-...` ID, list the exact control IDs it supports, and carry its own
issue-specific official source, jurisdiction, domain, verification timestamp,
effective interval, and scope conclusion. Fixture-only `AUTH-...` identifiers
must never appear in a persisted audit.

## Authority status

- `VERIFIED_FOR_USED_RULES` — every rule used by the result has a current,
  applicable primary source and no contradictory authority was found.
- `PARTIALLY_VERIFIED_UNUSED_GAPS` — the loaded rules file has gaps, but none is
  used by the result. Identify the unused gaps.
- `AUTHORITY_HOLD` — a used rule is missing, unverified, superseded,
  inapplicable to the period, or contradicted. Hold only the dependent result
  unless the rule affects scope, identity, period, or the entire computation.

`AUTHORITY_HOLD` is not cured by a plausible value, secondary source, prior-year
amount, or model knowledge.

## Point-of-use verification

1. Resolve jurisdiction, taxpayer/entity type, tax year, fiscal year, and the
   date on which the rule must apply.
2. Load the matching rules file and `rules/manifest.json`.
3. Reject a filename/year mismatch, malformed metadata, raw `_verify` marker,
   uncovered used path, or unresolved used path.
4. Open the cited primary source and any official future-developments page.
   Verify the exact rule and its effective dates. For payment computations,
   perform this check during the current run.
5. Record only paths actually used. An unrelated unresolved path does not block
   a result, but it must appear under unused gaps.
6. If a current-year form or instruction is not yet published, use the best
   controlling primary authority only for a clearly labeled provisional
   projection. Do not produce a payment-ready result from a draft form,
   secondary summary, or extrapolated inflation amount.
7. State rules are independent dependencies. A state hold does not invalidate a
   separately complete federal result; label the state component held.

## Source hierarchy

Prefer, in order appropriate to the proposition:

1. Statute and effective-date provisions.
2. Final or temporary Treasury regulations.
3. Official IRS/state forms and instructions for the target period.
4. Revenue rulings, revenue procedures, notices, announcements, and published
   agency guidance.
5. Controlling case law for litigated or interpretive questions.

Secondary sources can identify issues but cannot be the sole source for a
payment-ready exact value. Proposed regulations, draft forms, press releases,
FAQs, and nonprecedential material must be labeled with their authority limits.

## Rules-file contract

Each `federal-<year>.json` file:

- has `_meta.schema_version`, jurisdiction, tax year, review status, checked
  date, authorities, coverage, and unresolved-path arrays;
- uses explicit effective-date arrays when one annual scalar would be false;
- contains no `_verify` key or prose placeholder;
- uses `null` only when `_meta.unresolved` names the exact path, or when an
  authoritative selector replaces the scalar and coverage says the scalar is
  intentionally unavailable;
- does not silently change a field's shape across years without a migration
  note in `rules/manifest.json`;
- does not authorize a computation merely because file-level status is
  `SOURCE_MAPPED`;
- carries `_meta.stale_after` — see below.

## Freshness: bundled values expire

⚠ **A rules file whose `_meta.stale_after` has passed is `AUTHORITY_HOLD` for
every numeric output, regardless of its `status` or coverage.** Check the date
before reading any value out of it. Re-verification means opening the cited
primary sources *and* checking for legislation enacted since `checked_at`, then
updating both dates — **never bumping the date alone**.

**Why this exists.** Bundled figures go stale silently, and that is the standing
hazard of shipping reference data with a skill. The risk is not that a published
figure drifts; it is that **legislation lands after the file was checked**. OBBBA
retroactively rewrote TY2025 §179 and created four new TY2025 deductions — no
amount of care at authoring time prevents that, and nothing in a single-year file
reveals it. Two real instances have already occurred in this repo: stale 2025–26
data found in a July 2026 audit, and `federal-2024.json` carrying the 2023 §179
cap and phaseout.

Windows are **6 months** while a tax year is current or still being filed (late
guidance and retroactive legislation are live), and **12 months** once it is
closed. Elapsed time is only a proxy for the real question, so each file also
records **`legislation_checked_through`** — the date through which enacted
legislation was reviewed for retroactive effect on that year. (A list of statutes
examined would overpromise completeness; a date does not.)

Enforcement is centralized: **`evals/rules_freshness.load_rules()` is the only
sanctioned way to read a rules file**, and it refuses to return expired data.
Every executable consumer routes through it — a check that individual callers opt
into is not a control. `validate_rules.py` exits **2** for expired data and **1**
for malformed or wrong data, so a release gate can tell "needs re-verification"
from "is broken". `--as-of` is for **audit and reproduction only**; it must never
be used to green-light a live computation.

New rules files validate against **`rules/schema-v2.json`**, which requires the
freshness fields. `schema-v1.json` is frozen and left in place for any external
consumer already validating against it.

⚠ **A bundled value never authorizes a computation on its own.** Point-of-use
verification governs regardless of freshness — the freshness gate only removes
the file's usefulness as a cross-check once it can no longer be trusted even for
that.

Run `python3 evals/validate_rules.py` after changing any rules file or manifest.
It enforces schema, provenance, null/unresolved contracts, per-year core fixtures,
**and cross-year drift**: finely-indexed parameters must strictly increase year over
year, coarser ones must not decrease, and each genuine statutory re-basing is declared
in `DRIFT_EXCEPTIONS`.

⚠ **A value can be schema-valid, internally consistent, and still be the wrong
year's.** `federal-2024.json` shipped carrying the 2023 §179 cap and phaseout; no
single-year check could see it. Compare against the adjacent year, and read
`rules/changes-2023-2026.md` — the cross-year delta table, the statutory-change list
that separates OBBBA/SECURE changes from inflation, and the expiry register — before
concluding a figure is stable.

## Regression fixtures for qualitative propositions

Rules files pin exact **values**. The propositions in the individual modules —
caps, predicates, ordering rules, and the corrections that reviews have already
paid for — are pinned by `evals/individual-regression-matrix.json` and checked by
`python3 evals/validate_individual_matrix.py`.

**Run it after any editorial pass over `individual/`,** together with
`python3 evals/validate_individual_structure.py`, which checks that every
`file.md` §N cross-reference still resolves and no table row is malformed, and
`python3 evals/test_matrix_scoping.py`, which unit-tests the block scoping the
⚠ check depends on.

⚠ **Raw HTML and markdown images are prohibited in these documents and the
checker fails closed on both.** `<script>`, `<template>`, `<style>`, `hidden` and `aria-hidden` all render
to nothing while staying present in the source, so a proposition or a ⚠ could
hide in one; the list of such constructs is open-ended. Nothing here needs raw
HTML. Write placeholders as `` `<YYYY>` `` — bare `<YYYY>` in prose parses as an
HTML tag and **renders as nothing**, which is how this rule was found. Images are
banned for the same reason: alt text sits in the source and is matchable, but a
reader sees the image. The visibility oracle is also bound to the anchor's own
block, so a visible occurrence elsewhere in the file cannot vouch for a hidden
one — but the **prohibition**, not the oracle, is what closes the hidden-content
class; the oracle alone is not sufficient against it.

Requires `markdown-it-py` (as `validate_rules.py` requires `jsonschema`). Block
structure is parsed, not pattern-matched: five successive hand-rolled scanners
were each defeated by a construct they did not model — blockquoted ordered
lists, nested fences, sibling subtrees, setext headings, indented code, hard
tabs. The checker **fails closed** if the parser is missing rather than falling
back to a weaker scan.

Each matrix entry names the proposition, its canonical owner file, its primary
authority, whether it requires the ⚠ marker, and what breaks if it disappears;
the checker also fails if a known-wrong formulation returns. `--report` prints
the matrix with current line numbers.

Entry contract: a warn-required entry with more than one anchor must name
`marker_anchor` (which anchor the ⚠ governs), and every multi-anchor entry must
declare `scope` — `local` enforces that all anchors sit in one list item, table
row, or paragraph; `distributed` records a deliberate spread. Neither is
inferred, because inferring them makes anchor **order** silently semantic.

This exists because of a measured failure mode: an earlier compression pass
removed **caps and predicates along with the exposition while keeping the
mechanics they constrain**, leaving files that read complete and produce
unbounded numbers. Adding an entry is how a correction is made permanent — a
review finding is not closed until it is pinned here.

⚠ **A fixture makes a proposition permanent, which is exactly as dangerous as it
is useful when the proposition is wrong.** This has already happened once: an
over-generalized §529 penalty-waiver rule was pinned here and the matrix then
protected the error through a full review cycle. Pinning raises the cost of being
wrong; it does not lower the odds. Verify the proposition, then pin it.

## Failure behavior

- Missing target-year rules file: `AUTHORITY_HOLD` for numeric outputs; a
  readiness report may still identify missing inputs.
- Missing or stale state authority: hold the state component; do not guess.
- Contradictory official sources: record both, apply the controlling hierarchy
  only when clear, otherwise hold for practitioner review.
- Rule changed after a computation: mark the prior run `SUPERSEDED`; never
  overwrite its provenance.
- Unverified used rule: return the exact missing authority or fact needed. Do
  not substitute zero, a prior-year value, or a generic warning.

## Qualitative propositions (not just values)

The contract above is stated in terms of amounts, rates, dates, form mechanics,
and thresholds. It extends to **propositions**.

**Background doctrine may be omitted from the documentation entirely — the
consuming model supplies it, and it creates no hold. But the moment a qualitative
proposition is actually *used* to determine eligibility, character, ordering,
release, a deadline, a transition rule, or a method, it is no longer background:
it must be verified at point of use and recorded like any other used rule.**

This closes the gap that a value-only reading leaves open. "A related-party sale
does not release the loss," "an inherited Roth carries annual RMDs," "abandonment
is deductible" — none of these is a dollar amount, and each determines a result.

- Record a used proposition with `rule_origin: PROPOSITION`, the source consulted,
  and the same status vocabulary as a value.
- An unverified used proposition is an **authority hold**, exactly as an
  unverified used value is.

### The ⚠ marker

Skill files mark verify-me propositions with **⚠**. It has **one** meaning:

> **A ⚠ proposition requires point-of-use verification before it determines a
> result.** It is not emphasis, and it is not a general "pay attention."

Absence of a ⚠ does **not** make a proposition background. The test is whether it
is used to determine a result, not whether someone remembered to mark it.

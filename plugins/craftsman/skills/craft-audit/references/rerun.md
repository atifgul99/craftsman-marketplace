# Re-run Intelligence — staleness detection and robust diffing

A production-readiness audit is not a one-shot. The project keeps moving, and the value of the
`.craftsman/` workspace is that a *second* run tells the user **what changed** — what they fixed, what
regressed, what's new — instead of re-dumping the same pile. This file is the exercisable protocol for
that: how to tell when prior state is stale, and how to diff a fresh pass against it without losing the
fixed/regressed signal.

> **Pairs with:** `workspace.md` defines the artifact layout, the stamping rule, and the finding
> fingerprint this protocol keys on. This file is the *procedure* that consumes them. Read the
> fingerprint and "Re-run behavior" sections there first — this hardens them, it doesn't replace the
> identity model.

---

## Contents

- [When this runs (the pre-flight)](#when-this-runs-the-pre-flight)
- [Part 1 — Staleness detection](#part-1--staleness-detection)
- [Part 1.5 — Remediation-diff review](#part-15--remediation-diff-review)
- [Part 2 — Robust diffing (finding-by-finding)](#part-2--robust-diffing-finding-by-finding)
- [The "not seen ≠ fixed" rule (the one that matters most)](#the-not-seen--fixed-rule-the-one-that-matters-most)
- [User-scoped re-runs and fix verification](#user-scoped-re-runs-and-fix-verification)
- [Edge cases](#edge-cases)
- [The delta report](#the-delta-report)
- [Quick-reject checklist](#quick-reject-checklist)

---

## When this runs (the pre-flight)

Before doing anything else in the audit loop (`SKILL.md` step 0, ahead of workspace setup), check
whether a `.craftsman/` already exists at the project root.

- **No `.craftsman/`** → first run. Skip this file entirely; run the loop fresh.
- **`.craftsman/` exists** → this is a re-run. Do **Part 1 (staleness)** to decide *what to regenerate*,
  then **Part 2 (diffing)** as you re-observe each surface. Never blindly overwrite a prior workspace —
  that throws away the entire point of having one.

---

## Part 1 — Staleness detection

Every artifact carries a `> Generated: <date> · commit <sha> · craft-audit` stamp (`workspace.md`).
Staleness is a comparison between that stamp and the project's current `git rev-parse --short HEAD`.
Don't eyeball it — compute it.

### The procedure

1. **Get the current head:** `git rev-parse --short HEAD` and today's date.
2. **For each artifact, read its stamped `<sha>`.** Three outcomes:
   - **Stamp `<sha>` == current head** → fresh. Trust it; no regeneration needed.
   - **Stamp `<sha>` is an ancestor of head** (`git merge-base --is-ancestor <sha> HEAD`) → the project
     moved forward. Decide *scope-aware* (next step) whether it actually went stale.
   - **Stamp `<sha>` no longer exists** (`git cat-file -e <sha>^{commit}` fails — history rewritten,
     shallow clone, or a different repo) → staleness **can't be scoped** (there's no commit to diff
     changed files against), so re-discover from scratch and re-run every applicable surface. This is
     not "overwrite": you still **read the prior `findings.md` first and diff the fresh observations
     against it by fingerprint** (Part 2) — preserving fixed/regressed history. You lose the
     *scope-narrowing* shortcut, never the finding history.
   - **Stamp `<sha>` exists but is NOT an ancestor of `HEAD`** (`git merge-base --is-ancestor <sha>
     HEAD` fails even though `git cat-file -e <sha>^{commit}` succeeds — a branch switch or rebase
     rewrote history since the stamp) → treat as **Missing**: staleness can't be scoped against a
     commit that isn't in the current history, so re-discover and re-run every applicable surface, but
     still diff prior findings by fingerprint (Part 2) — never lose the finding history over a branch
     change.
3. **Scope-aware staleness — don't regenerate what didn't change.** A commit moving is not by itself a
   reason to redo a 20-minute audit. Compute what actually changed since the stamp:
   `git diff --name-only <stamp-sha>..HEAD`.
   - **No changed files intersect a scope's paths** → that scope's discovery (its section of the single
     top-level `discovery.md`) and its `audits/<scope>/<domain>/findings.md` are very likely still
     valid. Note "N commits behind, no files in scope changed — kept" and move on.
   - **Changed files intersect a scope** (`apps/web/**` changed and the scope is `apps/web`) → that
     scope is stale where it overlaps. Regenerate that scope's **section of `discovery.md`** (and
     `applicability.md` if a dependency changed) when the changes touch stack/config (`package.json`,
     lockfile, framework config, env schema, CI), and **re-run the affected domains** there (a change
     under `app/api/**` invalidates the backend + security passes for that scope, not the ux pass for a
     sibling app).
   - **Root-level config changed** (`package.json`, lockfile, `Dockerfile`, CI, `.env.example`) →
     `discovery.md` and `applicability.md` are suspect globally; regenerate them before trusting any
     scope. A new dependency can flip a domain from N-A to applies.
   - **Structure drift** — changed paths that fall under **no known scope**, or **any** change to a
     workspace-manifest file (`pnpm-workspace.yaml`, `turbo.json`, `nx.json`, or the `package.json`
     `workspaces` field) → regenerate `discovery.md` + `applicability.md` **before** scoping anything
     else. A new app has to be discovered, not silently skipped because it doesn't match any known
     scope.
4. **Surface the decision, don't bury it.** Tell the user what you found and what you're doing:
   *"`discovery.md` is 40 commits behind HEAD; 12 changed files touch `apps/web` (including
   `package.json`) — regenerating discovery + re-running backend/security/db for `apps/web`. The
   `packages/ui` audit had no changed files and is kept as-is."* Staleness handled silently looks
   identical to staleness ignored.
5. **Plugin-upgrade blindness.** Staleness is measured against the audited *project's* git history,
   which cannot see plugin upgrades — new or changed craft-skill content ships independently of the
   target repo's commits. The checklist reload described under "Delegated re-runs" below is what
   picks up new/changed checks within an existing domain. If a **whole new domain** has been added to
   the plugin (e.g. craft-lint), regenerating `applicability.md` (per the structure-drift bullet
   above) is what brings it into scope. An `applicability.md` whose domain-row count differs from the
   plugin's **current** domain count (currently 10) is stale by definition — that mismatch alone should
   trigger regeneration.

### Staleness decision matrix

| Stamp vs head | Files in scope changed? | Action |
| --- | --- | --- |
| Equal | — | Trust; no work. |
| Ancestor | None | Keep; note "N behind, unchanged". |
| Ancestor | Scope code only | Re-run that scope's affected domains; keep discovery if stack unchanged. |
| Ancestor | Stack/config/root | Regenerate `discovery.md` + `applicability.md`, then re-run. |
| Missing (`<sha>` gone) | — | Re-discover + re-run all surfaces (staleness can't be scoped), but still read prior findings and diff by fingerprint. |
| Exists but not an ancestor (diverged/branch-switched) | — | Treat as Missing: staleness can't be scoped; re-run all applicable surfaces, but still diff prior findings by fingerprint. |

---

## Part 1.5 — Remediation-diff review

Staleness uses a diff only to route work. Before a re-run closes an attempted fix, review the diff as
a change in its own right. A missing old fingerprint proves only that the old defect is absent; it does
not prove the remediation did not create a different breach, charge, migration failure, or integrity
regression.

For every prior `open` finding that is a candidate for closure and has either a `Fix-attempt` or
changed code since its `last-checked` stamp:

1. **Establish provenance.** For a SHA identity, inspect the fix commit (`<sha>^!`) and subsequent
   changes through current `HEAD` (`<sha>..HEAD`); when the prior `last-checked` commit is available,
   also use `<last-checked>..HEAD` to catch adjacent changes. For `working-tree`, inspect the staged,
   unstaged, and untracked change set relative to `HEAD` and record that provenance is uncommitted.
   When no Fix-attempt was recorded but the resource changed since `last-checked`, record
   `none — unrecorded remediation` and review `<last-checked>..HEAD`. If a required range is
   unavailable, the review is `pending`, not inferred clear.
2. **Identify the invariant and changed boundaries.** Start with the finding's fingerprint and
   technical evidence, then trace callers and alternate entry points touched by the diff: routes,
   server actions, jobs, webhooks, service methods, schema/data paths, and tests. Do not limit review
   to the cited line or assume a passing happy path covers those boundaries.
3. **Escalate semantic risk.** A diff that changes identity, role, ownership, tenant, or authorization
   checks; payment amounts, idempotency, refunds, ledger/state transitions; migrations, backfills,
   constraints, defaults, or deploy order; or transactions, uniqueness, deletes, retries, or ownership
   must receive focused regression review. Load the relevant domain skill(s) for the judgment:
   `craft-security`, `craft-backend`, `craft-db`, and `craft-testing` as applicable. This is not a
   second whole-project audit and does not duplicate their standards.
4. **Check evidence, including the negative path.** Review the tests changed with the fix and run the
   relevant gate where possible. For a risk-triggered change, verify the important denial, duplicate,
   expired, invalid, rollback, or existing-data path as well as the repaired happy path. A migration
   review must cover forward application, existing-data/backfill behavior, constraint/default effects,
   and rollback or compatibility/deploy-order evidence; an unavailable production step remains
   `pending`, not silently clear.
5. **Write the durable result.** Append one record to
   `audits/<scope>/<domain>/remediation-reviews.md` using the `workspace.md` template. If the review
   finds a side effect, emit it as a new or regressed finding before closing anything. If it is
   incomplete, mark the review `pending` and leave the original finding `open`.

Only a `cleared` remediation review, together with direct re-observation that the original fingerprint
is absent, permits `open → fixed` when remediation is present or plausibly occurred. If the finding
has a `Deployment-state`, it must additionally be `active` or `not-applicable`; `pending` and
`unverified-from-repo` keep it open. This check is intentionally bounded to candidate closures; it
does not turn every staleness diff into a full regression review.

---

## Part 2 — Robust diffing (finding-by-finding)

When a domain pass re-runs against a scope that already has a `findings.md`, you are **diffing**, not
rewriting. Match on the **fingerprint tuple** `(scope, domain, class, resource)` from `workspace.md` —
never on line number, file path, or the display ID label.

### The procedure

1. **Index the prior findings.** Read the existing `findings.md` and build a map keyed by fingerprint →
   `{ id, severity, status, last-checked }`. This is the ground truth you're diffing against.
2. **Re-observe the surface fresh.** Run the domain audit as if new. For each observation, compute its
   fingerprint using the **prior run's exact `class`/`resource` vocabulary** when it's the same defect
   (`workspace.md` — "reuse the prior run's exact strings"; rephrasing `missing-authz` →
   `missing-authorization` silently breaks the match and resurfaces a fixed finding as "new").
3. **Classify each fingerprint:**
   | Prior status | Re-observed this run? | New status | ID |
   | --- | --- | --- | --- |
   | `open` | yes | `open` (unchanged) | keep |
   | `open` | no — **and the pass actually re-checked it, with a cleared required remediation review** | `fixed` | keep |
   | `open` | not re-checked (pass skipped/stale) | `open` (stamp `last-checked` unchanged) | keep |
   | `fixed` | yes — defect is back | `regressed` | keep |
   | `wontfix` | yes | `wontfix` (still acknowledged; surface in delta) | keep |
   | (none) | yes | `open` — genuinely new | next sequential for (scope, domain) |
4. **Stamp every finding with `last-checked: <date · commit>`** — the run that actually re-verified its
   resource. This is what makes the next rerun able to tell "fixed" from "never re-checked" (see the
   rule below). It is recorded per finding, in addition to the file-level `Generated` stamp.

   **Fix-attempt findings** (`workspace.md`): a Fix-attempt is a claim, never a verification. Run
   Part 1.5 for the attempt being considered. If its fingerprint is **not** re-observed and its
   remediation review is `cleared` → set `fixed`; the review record, not the Fix-attempt line alone,
   is the evidence that the fix was safe to close. If it is **re-observed** → keep `open` and append
   ` · did not hold (<date>)` to the most recent unsuffixed Fix-attempt line. If the review is
   `pending` or `follow-up-found` → keep `open`, preserve the Fix-attempt history, and report the
   review state in the delta. Never delete a Fix-attempt line or use it as a status field.
5. **Reconcile cross-domain rollups at the tracker, not here.** Diffing is per-(scope, domain). The
   cross-domain rollup (`prioritization.md` step 2b) is re-derived after all passes finish — don't try
   to maintain it inside a single domain's diff.
6. **Re-stamp the file** and feed the counts into the delta report.

### Delegated re-runs

`SKILL.md` step 6 delegates domain passes to subagents for any audit larger than a handful of
scope/domain pairs — with no memory of this file's procedure by default. When a re-run pass is
delegated, the subagent prompt **must** include: (a) the path to the prior `findings.md` for that
scope/domain, (b) an explicit instruction to execute Part 1.5 for every candidate closure that
requires it and append the required `remediation-reviews.md` record, (c) an explicit instruction to execute this
Part 2 — index prior fingerprints first, reuse the prior run's exact `class`/`resource` vocabulary,
never renumber existing IDs, and preserve prior `status` and `last-checked` stamps for findings it
didn't re-observe, and (d) the re-run subagent still loads its domain skill first and merges the
**current** checklist into the plan — same as a first-run pass, per `SKILL.md` step 4. Checklist items
with no corresponding prior coverage run as first-pass items for that item, and their findings enter
the delta as new. A re-run diffs **findings**, never freezes the **checklist**. The orchestrator
must reject (and re-dispatch) a returned `findings.md` that renumbered or resequenced existing
findings — that's the signal the subagent rewrote instead of diffed. It must also reject a closure
whose Fix-attempt or changed-code provenance requires Part 1.5 but lacks a matching `cleared`
remediation review.

---

## User-scoped re-runs and fix verification

Not every re-run needs to touch every surface. The user may restrict a re-run to named (scope,
domain) pairs — e.g. "just re-check security" — in which case run Part 1 + Part 2 for that subset
only. Every other row is reported as "not re-checked" in the delta, and "Last full run" (the tracker
field in `master-tracker.md`) is left unchanged by a user-scoped re-run — it only advances when every
applicable pass actually executed.

There's a second, narrower mode: a **targeted verification** pass. It may re-check only the findings
that carry Fix-attempt lines, re-observing each named finding's fingerprint/resource directly rather
than running the full domain pass. It must also execute Part 1.5 for any finding it wants to close. A
finding whose resource was directly re-checked, whose defect is no longer observable, and whose
remediation review is `cleared` may flip to `fixed` with a fresh `last-checked` stamp — direct
re-observation plus the review satisfies the closure rule for that one finding, even though the full
domain pass didn't run. Everything else not re-checked keeps its existing status and stamp unchanged.
List these in the delta report using the exact phrase **"verified fixed (targeted)"**, distinct from
a full pass's plain "fixed", so a reader can tell how much was actually re-run. This is minutes of
work, not a full audit — reach for it when the user (or `craft-fix`) wants a quick confirmation
that a specific fix held, without paying for a whole domain re-run.

**Guard: the resource must still exist in recognizable form.** A targeted pass may flip a finding to
`fixed` **only** when the named resource still exists in recognizable form and the defect class is
absent *at that resource*, and any required remediation review is `cleared`. If the resource itself
was removed, renamed, or replaced (e.g. `POST
/api/invoices` replaced by a server action carrying the same validation gap), the targeted pass must
**not** close the finding — it has no way to follow the defect to its new home. Report instead:
"resource changed since the audit — a scoped domain re-run is needed to follow the defect to its new
home," and leave the finding's status and `last-checked` stamp untouched. Tracking the defect to
wherever it moved is the full/domain re-run's job — see "Resource renamed, same defect" under Edge
cases below.

### Fix-attempt deadlines

At pre-flight and before a new `craft-fix` pick-set, scan every open Fix-attempt and derive its due
date from the attempt date and finding severity: 🔴 7 calendar days, 🟡 14, 🟢 next release or 30 days.
Display overdue attempts in the master tracker’s **Verification follow-up** queue. An overdue 🔴
attempt requires targeted verification before another pick-set starts, unless the user explicitly
defers it; record the defer reason and date. Overdue 🟡/🟢 attempts remain first in the next targeted
verification queue. A deadline is a forcing function for verification, never evidence that a fix held.

---

## The "not seen ≠ fixed" rule (the one that matters most)

The single most dangerous bug in a diffing audit is marking a finding **`fixed` because this run didn't
re-observe it** — when the real reason it wasn't observed is that **the pass that would have caught it
never ran** (the domain was skipped for budget, the scope was deemed unchanged, the subagent failed).
That silently tells the user "you fixed the IDOR" when nobody looked.

**Rule:** a finding moves `open → fixed` **only** when the domain pass for its scope actually ran *this
re-run* and re-checked the resource and found it resolved. Concretely:

- If a domain pass **ran** this re-run, every prior `open` finding it owns is either re-observed
  (`open`) or confirmed resolved (`fixed`) — and gets a fresh `last-checked`.
- If a domain pass **did not run** this re-run (skipped, stale-but-kept, or failed), its prior `open`
  findings stay `open` with their **old** `last-checked` untouched. They are *stale-unknown*, not
  fixed. The delta report lists them as "not re-checked this run".

This is why `last-checked` exists. "Absent from this run's observations" is only evidence of a fix when
paired with "the pass that looks for it actually executed."

---

## Edge cases

- **Resource renamed, same defect** (route `/api/invoices/:id` → `/api/billing/:id`, same missing
  authz). The fingerprint's `resource` changed, so a naïve match reads it as "old fixed + new finding".
  Before accepting that, do a **candidate-match review**: when a fresh observation shares
  `(scope, domain, class)` with a prior `open`/`fixed` finding but differs only in `resource`, check
  whether the prior resource still exists. If it was renamed/moved (not resolved), keep the prior ID and
  update its `resource` string (note "resource renamed `<old>` → `<new>`"), rather than churning a
  fixed+new pair. Genuinely new resources still get new IDs.
- **Merge/split** — handled in `workspace.md` ("Re-run behavior" step 4): collapsing keeps the lowest ID
  and marks the other `fixed (merged into <ID>)`; a split keeps the original ID and adds one.
- **`applicability` flipped** — a domain that was N-A last run now applies (a dependency was added). It
  has no prior `findings.md`; treat it as a first run for that (scope, domain) and note in the delta
  that a new surface came into scope.
- **Partial first run** — a (scope, domain) marked applicable that has a `plan.md` but **no**
  `findings.md` is an unfinished first run, not a diff. Execute it as a fresh pass, not a rerun, and
  record it in the delta report as ➕ **first-audited** — a category distinct from "new finding".
- **Scope added/removed** — a new app appears in the monorepo → new audit tree, first-run rules. An app
  was deleted → leave its `audits/<scope>/` in place (history), mark it `archived` in the tracker; don't
  silently delete the record.
- **Partial pass** — a subagent that begins auditing but runs out of context mid-way produces a
  *partial* `findings.md`. Treat it as: findings it positively confirmed or resolved get their status
  updated (they were re-checked); findings it never reached retain their prior status and
  `last-checked` unchanged (not re-checked, not fixed). Record the coverage watermark in the
  `findings.md` header: `<!-- pass coverage: checked routes A–E; routes F–H not reached this run -->`
  and list the partial pass in the delta report under "not re-checked" with a reason ("partial — agent
  context exhausted at route F"). Do not mark routes F–H fixed; do not re-run the whole domain to
  replace partial work — add only the uncovered portion to the next pass queue.
- **Severity changed on re-judgement** — if the merged/re-judged severity differs from the prior run,
  keep the ID, update the severity, and note the change in the delta ("`apps-web-BE-004` 🔴 → 🟡, see
  re-judge note"). Severity is allowed to move; identity is not.

---

## The delta report

The whole reason for re-run intelligence is this summary. Write it into `master-tracker.md` under
"Delta since last run" and lead the chat with it:

```
Delta since last run (<prev date · sha> → <date · sha>):
- ✅ 3 fixed (remediation reviewed): apps-web-SEC-001, apps-web-BE-004, packages-ui-UX-003
- ↩ 1 regressed: apps-web-SEC-002 (was fixed 2026-05-01, back this run)
- ➕ 2 new: apps-web-OBS-005, apps-api-INFRA-002
- ⏳ 1 remediation review pending: apps-api-DB-003 (finding remains open)
- ❔ 4 not re-checked (backend pass skipped for apps/admin — stale, not fixed)
```

The `not re-checked` line is non-negotiable when any applicable pass didn't run — omitting it is how the
"not seen ≠ fixed" bug reaches the user. If every applicable pass ran, that line reads "0 not
re-checked" and you can drop it.

---

## Quick-reject checklist

| Smell | Fix |
| --- | --- |
| Prior `findings.md` overwritten instead of diffed | Index prior fingerprints first; classify, don't replace |
| Finding marked `fixed` but its pass never ran this re-run | Keep `open`, old `last-checked`; report "not re-checked" |
| Finding with a Fix-attempt marked `fixed` from fingerprint absence alone | Review its remediation diff, record a `cleared` result, and check the relevant negative path before closure |
| Payment/auth/migration/data-integrity remediation reviewed only at its cited line | Trace changed callers and alternate paths; route focused judgment to the relevant domain skills |
| 20-minute audit redone because the commit moved by one | Scope-aware staleness — diff changed files, keep unchanged scopes |
| `class`/`resource` rephrased, so fixed findings resurface as "new" | Reuse the prior run's exact vocabulary (`workspace.md`) |
| Renamed route churns a fixed+new pair | Candidate-match review on `(scope, domain, class)`; carry the ID |
| Stamped `<sha>` no longer exists | Re-run all surfaces (staleness can't be scoped), but still diff prior findings by fingerprint — never delete history |
| Re-run produced no delta report | Always write the fixed/regressed/new/not-re-checked summary |

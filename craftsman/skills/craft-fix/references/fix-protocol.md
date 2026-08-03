# Fix Protocol — the fix workflow in depth

This is the method behind `SKILL.md`'s compact loop. It owns the fix **workflow** only — the
finding record format, the fingerprint identity model, and the status/lifecycle vocabulary are
defined once, in `craft-audit` → `references/workspace.md`, and this file does not redefine
them. Read that file first if any term here (`fingerprint`, `status`, `last-checked`, `ID label`)
is unfamiliar.

> **Pairs with:** `craft-audit` → `references/workspace.md` (finding record format, fingerprint,
> status vocabulary), `references/prioritization.md` (climb sequence, severity tiers), and
> `references/rerun.md` (staleness detection, the "not seen ≠ fixed" rule this skill's step 6 exists
> to protect).

---

**The invocation unit.** One invocation executes **one approved pick-set** — everything the user
approved in the step 3 presentation — surface-batch by surface-batch, until that whole set is done.
"One batch per invocation" in the stopping rule means one approved pick-set, not one surface group:
if the approved set spans three disjoint surfaces, all three surface-batches land in this same
invocation. What ends the invocation is finishing the approved set, not finishing the first batch in
it.

---

## Contents

- [Precheck and concurrency](#precheck-and-concurrency)
- [Parsing the invocation](#parsing-the-invocation)
- [Fingerprint re-verification](#fingerprint-re-verification)
- [Batching by surface](#batching-by-surface)
- [Rollup handling](#rollup-handling)
- [Plan-first gate](#plan-first-gate)
- [The fixer subagent prompt contract](#the-fixer-subagent-prompt-contract)
- [The Fix-attempt annotation](#the-fix-attempt-annotation)
- [Stopping rule](#stopping-rule)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Precheck and concurrency

Before parsing picks or mutating the workspace: if `.craftsman/.run-in-progress` exists, **refuse by
default**. An active (or stale) audit marker means synthesis may still be writing findings and the
tracker — a concurrent fixer races that work. Warn the user; only proceed on **explicit override**
after they acknowledge the risk. Prefer waiting until the audit deletes the marker on successful
completion. Spec: `craft-audit` → `references/workspace.md` § Concurrency marker.

---

## Parsing the invocation

Three shapes, in priority order:

1. **A finding ID** (`SEC-003`, `root-SEC-003`, `apps-web-SEC-001`) → resolve it to exactly one
   finding record. Match on the ID label as written in the tracker/`findings.md`. Users commonly type
   a bare suffix (`SEC-003`) while tracker labels are scope-prefixed (`root-SEC-003`,
   `apps-web-SEC-003`):
   - **Exactly one label ends in that suffix** → resolve it silently, no need to ask.
   - **More than one label ends in that suffix** (monorepo collision, e.g. `apps-web-SEC-003` and
     `packages-api-SEC-003` both exist) → list the matches with their scopes and ask which one; never
     guess.
   - **No label matches at all** (typo, e.g. `SEC-33`) → say so plainly and list that domain's open
     IDs so the user can pick the right one. Never fuzzy-match to a different finding — a fix must
     never execute against a finding the user didn't name.
2. **A domain name** ("fix the security findings", "fix the db issues") → the top 10 `open` findings
   in that domain, across all applicable scopes, in tracker order. If more than 10 remain, say so
   instead of presenting the rest: "10 shown, N more remain — say 'keep going' for the next ten."
   Presenting every open finding in a 15-finding domain in one pass overwhelms the approval step;
   the cap keeps each presentation reviewable.
3. **Nothing named** ("fix the findings", "work through the audit", "start the climb") → the top 5
   `open` items from the master tracker's **climb sequence**, read top to bottom exactly as ranked.

In every shape, the climb sequence's order is canonical. Do not re-sort by file proximity, by
"easy wins first," or by any other heuristic — the ranking already encodes severity and the
persona-aware sequencing from `prioritization.md`. The only thing that may remove an item from the
picked set is a fingerprint that no longer matches `HEAD` (see next section) — and that's a drop,
reported as likely-already-resolved, never a silent skip and never a re-rank of what remains.

---

## Fingerprint re-verification

Before presenting any candidate to the user, recompute its identity against the current tree and
compare to what the workspace has on file:

1. Read the finding's `Fingerprint:` line — `scope=… · domain=… · class=… · resource=…` — and its
   `Technical:` line, which usually carries a `file:line` citation.
2. Re-open that file (or `grep` for the resource if the line has drifted) and confirm the defect
   described is still observable: the same class of problem, on the same resource, still present.
3. **Match** → proceed, this finding is still real. Line-number drift alone is not disqualifying —
   the fingerprint's `resource` is the anchor, not the line.
4. **No match** (the resource is gone, renamed beyond recognition, or the defect class no longer
   applies) → drop it from the picked set and say so explicitly: "`root-SEC-003` looks
   already fixed or the code has moved on — will be confirmed at the next `craft-audit` re-run,
   not marking it fixed here." Do not silently substitute the next item without calling out the
   drop. Also add a one-line, informal note under the finding's record in `findings.md`:
   `> re-verified <date>: not observed — pending audit confirmation`. Leave status untouched (still
   `open`) — this is not a `Fix-attempt` line and must not be shaped like one (no sha, no "resolved"
   claim); it's a breadcrumb for the next reader, and the audit's own diff at re-run time is
   unaffected by it.
5. **Partial drift** (the resource still exists but the specific mechanism changed, e.g. the route
   moved from REST to a server action) → still proceed, but note the drift in the plan/approval
   message so the user isn't surprised by where the diff lands.
6. **Prior Fix-attempt lines present, and the fingerprint still matches** → tell the user a prior
   attempt did not hold, even if the existing `Fix-attempt` line lacks the ` · did not hold` suffix
   (that suffix is appended by an audit re-run, per `workspace.md` — its absence just means no
   re-run has happened yet; the live defect in front of you is the evidence regardless). Require the
   new fix to differ from or extend the approach already recorded, not repeat it verbatim.
   `craft-fix` never appends the ` · did not hold` suffix itself — that annotation is the audit's
   to make; report the observation in the presentation instead.

This step exists because an audit workspace can be stale in a way too small to trip step 0's
staleness warning (a few commits, not "many") — re-verification is cheap insurance against
proposing a fix for something that's already gone.

---

## Batching by surface

**Batch by surface, not by severity or by finding order.** A "surface" is the set of files/routes a
fix will touch. Group the approved picks into surfaces before executing:

- Two findings that both touch `app/api/invoices/[id]/route.ts` → one batch, one pass, one diff —
  even if they came from different domains (e.g. a security IDOR finding and a backend validation
  finding on the same route).
- Two findings on genuinely disjoint files (e.g. `SEC-003` on the invoices route and `OBS-001` on
  the logging setup) → separate batches. They *can* run in parallel if using subagents, but only
  because they don't touch the same files.

**Disjoint-file-ownership rule for parallel subagents:** before dispatching any fixes in parallel,
compute the file set each batch will touch and confirm the sets are pairwise disjoint. If two
batches would touch the same file, merge them into one batch and run it sequentially — never let
two subagents write to the same file concurrently. This is the single most common way a "fast"
parallel fix pass produces a bad merge or silently drops one agent's edit.

---

## Rollup handling

The master tracker's "Cross-cutting" section records when one real defect surfaces as findings in
more than one domain's `findings.md` (same `scope · class · resource`, different `domain` in the
fingerprint, per `workspace.md`'s design). When a picked finding is rolled up:

- Fix it **once**, at the canonical owner named in the tracker's rollup row (e.g. `root-DB-001` if
  that's the canonical ID and `root-SEC-002` is "also surfaced as").
- Append the `Fix-attempt` line to **both** records — the canonical one and every finding rolled up
  under it — since both are real entries in their own domain's `findings.md` and both need the
  trail. The fix itself only happens once; the annotation reflects that on all affected records.
- The tracker's climb-sequence display metadata (the `open · fix-attempted <YYYY-MM-DD>` Status
  cell) goes on the **canonical owner's** climb-sequence row — a rolled-up child has no
  climb-sequence row of its own (only the canonical owner is shown, per `workspace.md`'s
  Cross-cutting section). Both records still get their `Fix-attempt` lines per the rule above; only
  the tracker row is singular.
- Never fix the same defect twice because it appeared in two domains' picked sets — check the
  tracker's Cross-cutting table before batching.
- **Direct invocation of a rolled-up child** (the user names the surfaced finding, not the canonical
  one — "fix SEC-002" where `SEC-002` is rolled up under `DB-001`): name the canonical owner and the
  reason in the presentation before proceeding, e.g. "`SEC-002` is the same defect as `DB-001` —
  missing RLS; `db` owns the fix; I'll fix there and annotate both records." Then fix once at the
  canonical owner and append `Fix-attempt` to both, per the rule above.

---

## Plan-first gate

🔴 findings touching **auth, migrations, or data handling** need a short written plan the user
explicitly confirms before any edit lands. Keep it to 5-6 lines:

```
Fix plan: <ID> — <one-line what breaks>
Change: <the specific code/schema change, named files>
Risk: <what could go wrong — e.g. "migration is additive, no backfill needed" or
       "requires a backfill for existing rows without org_id">
Test: <the regression test that will prove it, one line>
Rollback: <how to undo if this goes wrong in prod — revert commit / down-migration / feature flag>
Proceed? (waiting for confirmation)
```

Mechanical 🟡/🟢 findings (a missing validation schema, a loading state, an unpinned dependency)
skip this — they go straight to execution once step 3's batch approval is granted. The gate exists
because auth/migration/data-handling mistakes are the ones that turn a fix into an incident; a
missing empty state is not in that category even at scale.

---

## The fixer subagent prompt contract

When dispatching a batch to a subagent (in-loop or a harness subagent), the prompt contains
**exactly** these inputs — nothing more:

1. **The finding record, verbatim** — the full `## <ID> · severity … · status …` block copied
   from `findings.md`, including its `Fingerprint:`, `Last-checked:`, and any `Fix-attempt:` lines. If
   the record carries prior `Fix-attempt` lines and the fingerprint still matched at re-verification,
   say so explicitly in the prompt and require the new fix to differ from or extend the recorded
   approach (see "Fingerprint re-verification").
2. **The domain reference doc path(s)** the finding's `Fix:` line points to (e.g.
   `craft-security → references/authz.md`) — the subagent loads that file itself; don't paste its
   contents into the prompt.
3. **Scope** — the exact batch of files/routes this fix is allowed to touch (from the
   surface-batching step). State explicitly that touching files outside this set is out of scope
   and should be reported back, not acted on.
4. **Repo conventions** — the minimal, concrete set: test framework in use (per `craft-testing`'s
   standard for this repo), lint/format command, and any style note that would otherwise cause a
   drive-by reformat.

**Never** hand a fixer subagent the whole `.craftsman/` workspace, the master tracker, or other
findings — that invites scope creep ("while I was in there I also fixed…") and re-litigating
severity the subagent has no mandate to touch. The fixer's job is narrow: make the one described
defect stop being true, with a regression test, and report back.

**Fixer rules** (restate in the prompt, don't assume default behavior):
- Minimal diff — the smallest change that closes the described gap.
- Match surrounding style — no reformatting untouched lines.
- No drive-by refactors — a fix pass is not a cleanup pass.
- One regression test per fix, meeting `craft-testing`'s standard for this repo's stack.
- Report deltas only (files changed, test added, anything it couldn't resolve) — not a narrated
  walkthrough.
- Re-verify only the specific fingerprint it was given when confirming its own work — it does not
  re-audit the domain or go looking for other issues nearby.

**Model delegation (soft note, not a rule):** a mechanical, well-specified fix (add a zod schema,
wire a loading state, pin a dependency range) is safe to delegate to a cheaper model where the
harness supports per-task model selection — the prompt contract above is precise enough that a
smaller model can execute it reliably. Judgment-heavy fixes (anything hitting the plan-first gate)
should stay in the main loop / a stronger model, since they require weighing tradeoffs the contract
can't fully specify in advance.

---

## The Fix-attempt annotation

**Order is fixed — do not invert it:**

1. Code change + its regression test land in the working tree.
2. **Optional commit** (prefer first when the user approves commits or repo convention auto-commits)
   so the annotation can point at a real object.
3. Append the `Fix-attempt` line with the correct identity (below).

The line format, placement, and accumulation rules are canonical in `craft-audit` →
`references/workspace.md` — follow that spec exactly; don't restate the full grammar here.

**Identity token (the middle field):**

| Situation | Use |
| --------- | --- |
| A commit landed for this fix batch | That commit's **short SHA** |
| User declined commit / no commit yet | Literal token **`working-tree`** |

Never paste the pre-change `HEAD` SHA as if the fix lived there — that misleads the next reader and
the next re-run. If the work later gets committed, either update the most recent Fix-attempt line's
identity from `working-tree` to the new short SHA, or leave it and let a subsequent Fix-attempt
(if any) carry the real SHA. Both are fine; inventing a SHA is not.

**Do not** change the `status open` in the heading, and do not touch `Last-checked:` — see
`craft-audit` → `references/rerun.md` "not seen ≠ fixed": only a `craft-audit` re-run that
re-observes the resource and fails to find the defect is allowed to flip status to `fixed`. A fixer
believing its own fix worked is not evidence the audit accepts — that's exactly the theater the
fingerprint diff protocol exists to prevent.

---

## Stopping rule

One approved pick-set per invocation (see "The invocation unit" above) — finish every surface-batch
in the approved set before stopping; do not start a **new** pick-set uninvited. Finishing the
approved set is required, not chaining into more. After the approved set lands:

1. Run the project's existing test/lint gate (whatever `craft-testing`/`craft-lint` already
   established for this repo — don't invent a new one).
2. Confirm every fixed finding's record has its `Fix-attempt` line appended.
3. Summarize: what was fixed, what regression tests were added, what was picked but skipped (and
   why — e.g. dropped at fingerprint re-verification, or the user declined the plan).
4. Tell the user verification is scoped, not a full re-audit — see `SKILL.md` step 7's cost framing
   (`craft-audit`'s staleness rules re-run only the changed domains; its targeted re-check flips
   just this session's Fix-attempt lines) — "minutes, not another full audit."
5. Prefer committing **before** the Fix-attempt annotation (see "The Fix-attempt annotation" above)
   when the user approves commits or the repo auto-commits — so the line can embed the real short
   SHA. If still uncommitted at stop time, the Fix-attempt identity must be `working-tree`, not a
   misleading HEAD SHA. Commit messages reference the finding label(s) they close, e.g.
   `fix: scope invoice query to org (root-SEC-001)` — when a SHA is present, git history and the
   workspace point at each other.

Do not start a **new** pick-set automatically, even if the user's original ask covered more
candidates than got approved. A fresh invocation (or explicit "keep going") starts the next
pick-set — this keeps each pass reviewable and keeps the plan-first gate meaningful.

---

## Quick-reject checklist

Fast checks for reviewing a `craft-fix` session (self-review or a second pass):

| Smell | Reject / fix |
| ----- | ------------ |
| Fixer ran while `.craftsman/.run-in-progress` was active (no explicit override) | Stop — refuse concurrent mutation; wait for audit marker to clear or get override after race warning. |
| Fixer set a finding's status to `fixed` | Revert — only a `craft-audit` re-run flips status. Status must read `open` with a new `Fix-attempt` line. |
| Fixer touched `last-checked` | Revert — that field is audit-owned, not fixer-owned. |
| Subagent prompt included the whole `.craftsman/` workspace or the master tracker | Re-prompt with just the finding record + the referenced domain doc paths, per the contract above. |
| Two parallel fixers touched the same file | Not a valid parallel split — merge into one batch, run sequentially. |
| A finding was skipped from the picked set with no explanation | Not acceptable — every drop from the climb sequence needs the one-line "likely already fixed/drifted" note. |
| The climb sequence order was re-ranked before picking ("did the easy one first") | Reject — order is canonical from the tracker; only fingerprint mismatches remove items. |
| A rolled-up finding was fixed twice (once per surfaced domain) | Reject — fix once at the canonical owner, annotate both records. |
| A 🔴 auth/migration/data-handling finding skipped the plan-first gate | Reject — get the plan confirmed before any edit, no exceptions for "it's a small change." |
| The fixer added scope beyond the described defect ("while I was in there…") | Reject — minimal diff only; open a separate finding/ask for anything else worth doing. |
| A second pick-set started in the same invocation without being asked to continue | Reject — one approved pick-set per invocation is the stopping rule; finishing every surface-batch inside that set is fine, starting a new set uninvited is not. |

---
name: craft-fix
description: >-
  The Craftsman standard for driving fixes against an existing `craft-audit` workspace — "fix the
  findings", "fix SEC-003", "work through the audit", "start the climb". An ACTION skill, not a
  domain: it picks findings off the master tracker's climb sequence, re-verifies each is still real,
  gets the user's approval, and executes a batched fix with a regression test — it never re-audits
  or re-ranks. Fires with no finding ID named ("start the climb" means the top 5 open items) and on
  handoffs like "regression test for finding X" or "work on TEST-004".
  REQUIRES an existing `.craftsman/` workspace at the project root. Without one, a scoped fix
  request goes to the relevant domain craft skill and a whole-project assessment goes to
  `craft-audit` first.
---

# Craftsman Fix — driving fixes off an audit

`craft-audit` finds and ranks; this skill **fixes**. It reads the `.craftsman/` workspace
another run already built, re-verifies the picks are still real, gets sign-off, and executes a
tightly scoped batch — then hands back to a re-run of `craft-audit` to confirm. It never
re-audits, never re-ranks, and never marks a finding `fixed` itself — only a fresh audit pass can do
that, because "not seen ≠ fixed" is the whole point of the tracker.

**Handoffs (state both explicitly when this skill doesn't fire):**
- No `.craftsman/` at the project root → this skill does not apply. A scoped, no-audit fix request
  goes straight to the relevant domain craft skill. A whole-project assessment goes to
  `craft-audit` — run that first, then come back here.
- `.craftsman/` exists but the user wants a *new* assessment, not a fix → that's `craft-audit`
  re-run territory, not this skill.

## The loop

Depth for every step lives in `references/fix-protocol.md` — this is the compact sequence.

0. **Precheck.** Locate `.craftsman/` at the project root.
   - Missing → stop. Tell the user to run `craft-audit` first (give them the trigger phrase,
     e.g. "is my app production-ready").
   - **Concurrency marker (mandatory before any mutation).** If `.craftsman/.run-in-progress`
     exists, an audit is claiming the workspace (or left a stale marker). **Refuse by default** —
     do not mutate `findings.md`, the master tracker, or any other `.craftsman/` artifact. Warn the
     user: either wait for the audit to finish (marker deleted on successful step 8), or treat the
     marker as stale only if they confirm the prior audit was abandoned. Proceed past the marker
     **only** on explicit user override after they acknowledge the race risk (fixer and auditor both
     writing findings/tracker). Prefer refuse; override is the exception. → `craft-audit` →
     `references/workspace.md` § Concurrency marker
   - Present but stale → quantify it, don't eyeball it: run the same stamp comparison as
     `craft-audit` → `references/rerun.md` Part 1 (`git diff --name-only <stamp>..HEAD` against
     the workspace's stamped commit). If the changed files intersect the scopes of the findings the
     user is about to pick, recommend a `craft-audit` re-run first. If they don't intersect,
     proceed — "many commits behind" alone isn't a reason to stop. The user may override and proceed
     anyway even when scopes intersect — record that they did.
   - **Check for declared gated surfaces (optional, no setup required).** In precedence order: (a)
     `.craftsman/gated-surfaces.md` if the user wrote one, (b) a statement in the project's own
     `CLAUDE.md`/`AGENTS.md`/README, (c) the user saying so in chat this session. Find none of the
     three → nothing changes, proceed as below. → `references/fix-protocol.md` "Gated surfaces"

1. **Parse the invocation.** A finding ID (`SEC-003`, `root-SEC-003`) → that one finding. A domain
   name ("fix the security findings") → that domain's open findings. Nothing named → the top 5 open
   items from the master tracker's **climb sequence**, in its existing order. The climb sequence is
   canonical — never re-rank it here; only drop an item whose fingerprint no longer matches `HEAD`,
   and report each drop as "likely already fixed/drifted — will be confirmed at next re-run" rather
   than silently skipping it. → `references/fix-protocol.md` "Parsing the invocation"

2. **Re-verify each candidate's fingerprint** against the current code before proposing anything —
   an audit workspace can be stale even when it's not old enough to trigger step 0's staleness
   warning. → `references/fix-protocol.md` "Fingerprint re-verification"

3. **Present the picks and wait.** One numbered row per candidate, tightest form that still carries
   the batching:
   ```
   1. root-SEC-001 🔴 — anyone can open another customer's invoice by changing the URL · batch A (app/api/invoices/[id])
   2. root-BE-004 🟡 — same route, missing input validation · batch A (app/api/invoices/[id])
   3. root-OBS-002 🟢 — no logging on failed webhook deliveries · batch B (lib/webhooks)

   Approve all, or name a subset (e.g. "just 1 and 2")?
   ```
   Do **not** start editing until the user approves — this is a hard gate, not a formality. The user
   may approve a subset: unapproved picks are recorded in the step 7 stop summary as "declined this
   pass" — they are not "drops" (a drop is only a fingerprint mismatch, step 2) and are not
   re-presented unless the user asks again.

4. **Plan-first gate.** 🔴 findings touching auth, migrations, or data handling get a short written
   plan (template in `references/fix-protocol.md`) that the user confirms before any edit lands.
   Mechanical 🟡/🟢 findings go straight to execution. → `references/fix-protocol.md` "Plan-first gate"

   **Gated surfaces are stronger: never auto-fixed.** A finding whose file matches a declared gated
   surface (step 0) is routed to a "requires human approval" bucket instead of the batch — present
   the finding, risk, test plan, and rollback plan, then stop; do not edit. Approval to fix other
   findings in the same pick-set is not approval to touch a gated one. Even with nothing declared,
   treat payment/checkout/subscription/billing, identity and tenant isolation, and PHI/PII-handling
   code with default suspicion — apply the plan-first gate even below 🔴. A one-line diff is not a
   low-risk diff: a trivial-looking fix (e.g. adding a missing `await`) can activate dormant
   enforcement code — see `references/fix-protocol.md` "Gated surfaces" for the worked example.

5. **Execute the approved batch.** Batch by surface — findings touching the same files/routes fix
   together in one pass; a rolled-up finding (see the tracker's Cross-cutting section) gets **one**
   fix at its canonical owner, not one per surfaced domain. If the harness supports subagents, each
   one receives **only** the finding record plus the domain reference(s) its `Fix:` line points to —
   never the whole workspace. Fixer rules: minimal diff, match surrounding style, no drive-by
   refactors, one regression test per fix (craft-testing's standard), report deltas only, re-verify
   only the specific fingerprint it was given — never re-audit the domain. Mechanical, well-specified
   fixes are safe to delegate to a cheaper model where the harness allows it; judgment-heavy fixes
   (auth, migrations, data handling) stay in the main loop. → `references/fix-protocol.md`
   "Batching by surface" · "The fixer subagent prompt contract"

   **Order within a surface-batch (mandatory):**
   1. Code change + regression test land in the working tree.
   2. **Optional commit** — only if the user approves commits or repo convention auto-commits. Prefer
      committing *before* the Fix-attempt line so the line can carry that commit's short SHA.
   3. Append the Fix-attempt line (step 6) with the correct identity token — never invent a SHA.

6. **Track the attempt, don't flip status.** Append a
   `**Fix-attempt:** <date> · <identity> · <one-line what changed>` line to the finding record in its
   `findings.md`. **Identity rules:**
   - If a commit landed for this batch → use that commit's **short SHA**.
   - If the user declined commit / no commit yet → use the literal token `working-tree` (not the
     pre-change `HEAD` SHA — that misrepresents where the fix lives). After a later commit, a
     follow-up can update the line, or the next Fix-attempt can reference the real SHA.
   Status stays `open` — **never** set it to `fixed` here; only a `craft-audit` re-run's fingerprint
   diff does that ("not seen ≠ fixed"). Do not touch `last-checked` — that field means "last
   re-verified by an audit pass," not "a fixer touched code." Also update the display metadata in
   `master-tracker.md`'s climb sequence: its Status cell becomes `open · fix-attempted <YYYY-MM-DD> ·
   verification due <date>` (🔴 7 days, 🟡 14, 🟢 next release or 30 days).
   That row lives at the **canonical owner** — a rolled-up child has no climb-sequence row of its own
   (per `craft-audit` → `references/workspace.md`'s Cross-cutting section), so a fix on a rolled-up child still updates only the
   canonical owner's row; both records still get their `Fix-attempt` lines per the rollup-annotation
   rule. This is tracker **display** metadata only — counts and readiness grades are unchanged, and a
   re-run resolves it either way; the spec for this cell lives in `craft-audit` →
   `references/workspace.md`, not restated here. It keeps "where are we?" answers honest between
   runs. → `references/fix-protocol.md` "The Fix-attempt annotation"

7. **Stop.** After the approved batch: run the project's test/lint gate, confirm the findings files
   were updated with their Fix-attempt lines, and summarize — what was fixed, what tests were added,
   what was skipped and why. One approved pick-set per invocation — execute it surface-batch by
   surface-batch to completion; do not start a new pick-set uninvited. (Commits already preferred in
   step 5 when approved — if a batch still has uncommitted work, ask once more here; never force.)
   Then hand off with the real cost framing, not a bare "re-run the audit": a verification pass is
   scoped, not a full re-audit — `craft-audit`'s staleness rules (`references/rerun.md`) only re-run
   the domains whose files actually changed, typically minutes; and its "User-scoped re-runs and fix
   verification" section supports a targeted pass that re-checks just the findings carrying this
   session's Fix-attempt lines, reviews their remediation diffs, and can flip only cleared findings
   to `fixed`. Give the user both options —
   minutes, not another full audit. → `references/fix-protocol.md` "Stopping rule"

## Reference index

| Task | Load |
| ---- | ---- |
| **Full fix workflow**: staleness decision, fingerprint re-verification, batching-by-surface and disjoint-file-ownership rules, rollup handling, plan-first template, fixer subagent prompt contract, Fix-attempt annotation format with a worked example, stopping rule, quick-reject table | `references/fix-protocol.md` |

For the finding record format, status vocabulary, and fingerprint identity model this skill consumes
(and never redefines), load the `craft-audit` skill's `workspace.md`. For the climb sequence and
severity tiers, load the `craft-audit` skill's `prioritization.md`. For the staleness procedure
referenced in step 0, load the `craft-audit` skill's `rerun.md`.

# Delegation — running a large audit without exhausting context

The audit loop in `SKILL.md` names one threshold repeatedly: **≤ 3 `(scope, domain)` pairs is a
small audit and may run inline; more than 3 is a large audit and delegates.** That number is not an
approximation, and it is the same number everywhere it appears. This file holds the mechanics on
both sides of it.

## Why the threshold exists

A real monorepo is many `(scope, domain)` pairs — 2 apps × 5–10 domains is 10+ craft-skill loads,
each pulling in a large reference set. Loading them serially in the orchestrator's own conversation
exhausts context and degrades quality long before the audit finishes. The durable `.craftsman/`
files are what make the alternative safe: each worker coordinates through its own file, and nothing
of consequence is held in chat.

This is the same "completeness on disk, focus in chat" principle as `prioritization.md`.

## Planning side (step 4): the context budget split

Loading all domain skills to extract their checklists *before* any audit runs will exhaust context
on a large audit. Instead, split the work:

- **The orchestrator writes the plan from discovery context only** — scope specifics, known stack,
  known gaps, maturity tier, what to emphasize.
- **The subagent, as its first act, loads its domain skill**, reads that checklist, and merges it
  with the plan before auditing.

Copy every discovery invariant that applies to the domain into the plan as an all-call-site coverage
checkbox. For content or configuration work, require the governing contract, fixture, seed,
generator, or prompt in the plan.

Small audits (≤ 3 pairs) may load the domain skill inline to write the plan. That is conditional,
not a mandate.

## Audit side (step 6): one subagent per pair

For any audit with more than 3 substantial `(scope, domain)` passes, delegate each pair to its own
subagent. The subagent loads that one craft skill, audits that one scope/domain, and writes *only*
its own `audits/<scope>/<domain>/findings.md`.

The subagent prompt **MUST** include the verbatim heading grammar and required field list from
`workspace.md` → "Canonical findings.md emission format (mandatory)". Copy them into the prompt; do
not paraphrase. The subagent emits only that grammar — no `###` headings, no
`## ID · 🔴 · open` shorthand, no severity/status body bullets.

The orchestrator then reads those files back, validates them, and synthesizes (step 7,
`synthesis.md`).

## Write capability is a precondition, not an assumption

State in the subagent prompt that it MUST write its own `audits/<scope>/<domain>/findings.md`, and
that it must confirm it did.

Fallback when a worker cannot write — harness policy can block it: the worker returns the complete
file contents as ONE fenced code block and nothing else, with no summary and no commentary outside
the fence. The orchestrator persists that block **verbatim** to the correct path, then runs the
stage-a validation on it like any other file.

Do NOT repair transport corruption (HTML entities like `&gt;`/`&amp;&amp;`, truncation). If the
persisted file fails validation, re-prompt the worker. A normalizer that guesses at mangled regex
literals inside findings is worse than a re-run — the same "prefer re-emission over inventing a
normalizer" rule stated in `workspace.md`.

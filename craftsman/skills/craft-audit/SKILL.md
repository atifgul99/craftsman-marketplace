---
name: craft-audit
description: >-
  The front door to the craft skills — a top-level orchestrator that audits a whole project for
  production-readiness and drives the per-domain craft skills (ux, frontend, backend, db, security,
  infra, observability, testing, lint, ai) instead of auditing one surface at a time. It discovers the
  project's shape (monorepo, single app, marketing site, multiple apps), figures out which craft
  domains apply, writes a tailored audit plan per surface, and tracks findings and progress in a
  `.craftsman/` workspace so nothing is missed across runs.
  Use WHENEVER the user wants a whole-project assessment rather than a single-file review: "is my app
  production-ready", "take this from MVP to production", "I vibe-coded this with
  Lovable/Replit/Claude and want it enterprise-grade", or "what would a senior engineer fix here".
  Trigger even without a named surface area — the whole point is finding the applicable ones. For a
  single, scoped review of one surface, use that domain's craft skill directly.
  Does NOT fire on: single-surface improvement requests ("how do I fix this one bug", "add a feature
  to this component") — use the appropriate domain skill directly for those.
---

# Craftsman Audit — the production-readiness orchestrator

This is the **conductor**, not another peer domain. The ten `*-craft` skills each own one surface
(ux, frontend, backend, db, security, infra, observability, testing, lint, ai). This skill stands above them: it looks
at the whole project, decides which of those surfaces apply, plans an audit for each, routes the
actual findings to the domain skills, and keeps a durable record of what's been audited and what's
left — so a large assessment can run across multiple sessions without losing the thread.

It does **not** duplicate domain knowledge. When it's time to actually judge the auth layer, it loads
`craft-security`; when it's time to judge the design system, it loads `craft-ux`; when it's time to
judge lint/static quality gates, it loads `craft-lint`; when it's time to judge LLM integrations, it
loads `craft-ai`. The orchestrator
owns **discovery, applicability, planning, prioritization, and tracking** — the domain skills own
the findings. Keeping that boundary is what stops the two from drifting out of sync. Once findings
are tracked, the companion action skill `craft-fix` works through the climb sequence to actually
fix them — this skill audits and tracks, it does not itself change code.

## Who this is for (read this first — it sets the register)

The primary user is the **builder of a cool-but-fragile MVP**: someone who used Claude, Lovable,
Replit, or v0 to ship something that *looks* impressive and *works in the demo*, but is nowhere near
production-grade — no real error/empty/loading states, no auth worth the name, no observability, AI
"slop" patterns, data that'll corrupt under concurrency, infra that falls over at the first spike.
The secondary user is more advanced but still can't reliably hit enterprise-grade.

That persona changes how you communicate, and it is **not optional polish** — it's the job:

- **Plain language in findings.** The reference docs are written for you (the agent); the *findings
  you write for the user* must explain **what breaks for a real person** and **why it matters**
  before the technical fix. Don't lead with "CLS regression" or "IDOR" — lead with "anyone can open
  another customer's invoice by changing the number in the URL," then name it.
- **Ruthless prioritization over completeness.** Handing this user 200 findings makes them freeze.
  The deliverable is a *climb sequence*: the handful of things that will get them hacked, lose data,
  or embarrass them — first — then the next tier. The gap to enterprise-grade is huge; your value is
  making it ordered and unscary, not dumping the whole mountain. See `references/prioritization.md`.
- **Meet the project where it is.** Never tell someone on a working stack to rewrite to a "blessed"
  one. Audit what they have against the principles; only *recommend* a stack where something is
  genuinely **missing**. See "Standing principles" and `references/recommended-stack.md`.

## The `.craftsman/` workspace (durable per-project state)

All audit state lives in a `.craftsman/` folder **at the root of the project being audited** (not in
this plugin). It is the audit's memory: discovery notes, applicability call, per-area plans, the
master tracker, and findings. It must be **git-ignored in the target project** — it's working state,
not source. Create it (and its `.gitignore` entry) as the first step. Full layout, file templates,
and the date/commit stamping rules are in `references/workspace.md` — read it before writing any
file there.

## The audit loop

Run these in order. Each step writes its output into `.craftsman/` so the next session can resume.

0. **Re-run pre-flight (if `.craftsman/` already exists).** A second audit is a *diff*, not a rewrite.
   Before touching anything, check for an existing `.craftsman/` at the project root. If one exists, run
   the staleness check (compare each artifact's stamp to current `HEAD`, regenerate only what actually
   changed) and switch into finding-by-finding diff mode for every re-run pass — including the
   "not seen ≠ fixed" guard so a skipped pass never masquerades as a fix. → `references/rerun.md`. If
   there's no `.craftsman/`, skip this step and run fresh. On a re-run: skip step 1; steps 2–5 run
   only where the staleness check marked artifacts stale; step 6 runs in diff mode; steps 7–8 ALWAYS
   re-execute (grades and climb sequence are never carried stale).

   **Concurrency marker (mandatory — every run, fresh or re-run).** After pre-flight (or immediately
   when beginning work if step 0 was skipped), claim the workspace:
   - If `.craftsman/.run-in-progress` already exists: warn the user, compare the marker's date to
     today (stale leftover from a crash vs a run that may still be active), and **ask before
     proceeding**. Approving past an existing marker is **stale-run recovery** only — overwrite when
     the prior run is abandoned/stale, **not** permission for concurrent writers. While the marker is
     active, `craft-fix` must not run (it refuses by default until the marker is gone).
   - Write/overwrite `.craftsman/.run-in-progress` with today's date and a brief session label.
   - Delete the marker only on **successful** completion of step 8 (not on mid-run abort).
   Full spec → `references/workspace.md` § Concurrency marker.

1. **Set up the workspace.** Before creating anything, tell the user in chat (2-3 sentences) what's
   about to happen: what will be audited, that results will live in a gitignored `.craftsman/`
   workspace (they can ask to have it committed instead if they want it tracked), the rough duration
   (a full multi-domain audit runs tens of minutes), and that they'll get a prioritized top-5-10 with
   a readiness grade at the end. Then create `.craftsman/`, add it to the project's `.gitignore`, drop
   the `README.md` that explains what the folder is. → `references/workspace.md`

2. **Discover what the project actually is.** Evidence-based, never guessed: read `package.json`,
   lockfiles, framework/build configs, the directory layout, CI config, env templates. Determine
   shape (monorepo vs single app vs marketing site vs multiple apps), package manager, frameworks,
   hosting, and the stack already in place. Also make a **maturity read** (pre- / partially- /
   post-Tier-1, from evidence: tests, CI, validated env, auth **and** per-resource authz) — it sets
   which register the audit uses, so a hardened codebase isn't audited as if it had no auth. As part
   of discovery, also collect **quality tooling evidence**: `eslint.config.*`, `biome.json`,
   `.husky/pre-commit`, `tsconfig.json` strict mode flags, and `package.json` scripts (`lint`,
   `format`, `typecheck`, `quality`, `check`) — record what exists and what's absent. Route
   lint/rule-content findings (ruleset gaps, resolved-config issues, severity calibration) to the
   lint plan section; route CI-gate wiring findings (missing pre-commit hook, missing/optional CI
   gate, local/CI drift) to the infra plan section (see `references/quality.md`). Write
   `.craftsman/discovery.md` with **citations** — what you found and where. → `references/discovery.md`
   · `references/quality.md`

3. **Classify which domains apply.** Not every project needs every surface — craft-observability on a
   static marketing site is noise. Mark each of the ten domains **applies / partial / N-A** with a
   one-line reason, into `.craftsman/applicability.md`. This makes the tracker honest ("5 of 10
   apply") and saves wasted passes. → `references/discovery.md` (applicability section)

   **Write the tracker skeleton now.** Immediately after applicability is determined, write
   `.craftsman/master-tracker.md` as a SKELETON: the file header plus the "Audit status" table with
   every applicable (scope, domain) row marked ❔ Unaudited and grades as "—". This is what makes a
   dead or interrupted session resumable — the tracker exists from this point forward, not just at
   the end.

4. **Emit the audit plan as a tracked todo list.** For the applicable domains, generate a `plan.md`
   at the **scope-aware path** and surface the steps as an actual todo list (your native task
   tooling) so a long audit executes in steps and nothing is skipped. The path is always
   `.craftsman/audits/<scope>/<domain>/plan.md`, where `<scope>` is `root` for a single app or the
   workspace-relative path in a monorepo (`apps/web`, `packages/ui`). → `references/workspace.md`

   **Context budget split:** loading all domain skills to extract their checklists before any audit
   runs will exhaust context on large audits (>3 applicable domain/scope pairs). Instead: the
   orchestrator writes the plan from **discovery context only** — scope specifics, known stack, known
   gaps, maturity tier, what to emphasize. The subagent, as its **first act**, loads its domain skill,
   reads that checklist, and merges it with the plan before auditing. Small audits (≤ 3 scope/domain
   pairs) may load the domain skill inline to write the plan — this is conditional, not a mandate.

5. **Adversarial plan review (skip for ≤ 3 scope/domain pairs).** After all `plan.md` files are
   written (step 4), before launching subagent audit passes (step 6): run a review agent (or Codex
   async) with `discovery.md` + all `plan.md` files as input. Its job: find wrong stack
   identifications, missing applicable domains, and checklist items that don't apply given discovery.
   Apply corrections to the plans before subagents run. Yield: typically high — a wrong plan
   multiplied across 10 subagent passes is expensive to fix after the fact.

   **False-negative guard:** if a review pass claims an implementation is missing, verify with grep
   before accepting the claim — reviewers looking at partial context produce false negatives.

6. **Run each applicable surface by loading its craft skill.** Load `craft-ux` / `craft-frontend` /
   `craft-backend` / `craft-db` / `craft-security` / `craft-infra` / `craft-observability` /
   `craft-testing` / `craft-lint` / `craft-ai`, audit per
   its protocol, and record findings in the matching `findings.md` (same scope-aware path as the plan)
   using the **canonical findings.md emission format** in `references/workspace.md` (heading grammar +
   required fields + fingerprint). No alternate shapes. In a monorepo, never blend two scopes'
   findings under one dir — the per-scope split plus the fingerprint keeps records unambiguous;
   ID labels are display-only and may repeat across scopes. The domain skill owns the verdict; you own
   where it's written.

   **Watch the context budget — delegate when the audit is large.** A real monorepo is many
   `(scope, domain)` pairs (2 apps × 5–10 domains = 10+ craft-skill loads, each a large reference).
   Loading them all serially in *this* conversation will exhaust the context and degrade quality long
   before finishing. So for any audit with more than 3 substantial `(scope, domain)` passes,
   **delegate each pair to its own subagent**: the subagent loads that one craft skill, audits that
   one scope/domain, and writes *only* its own `audits/<scope>/<domain>/findings.md`. The subagent
   prompt **MUST** include the verbatim heading grammar and required field list from
   `references/workspace.md` → "Canonical findings.md emission format (mandatory)" — copy them into
   the prompt, do not paraphrase. Subagent emits only that grammar; no `###` headings, no
   `## ID · 🔴 · open` shorthand, no severity/status body bullets. Then this orchestrator reads those
   files back, validates, and synthesizes (step 7). The durable `.craftsman/` files are exactly what
   makes this safe — each worker coordinates through its own file, nothing is held in chat. (Small
   audits — ≤ 3 scope/domain pairs — can stay inline; this is conditional, not a mandate.) This is the
   same "completeness on disk, focus in chat" principle as `prioritization.md`.

   **Update the tracker after each pass, before starting the next.** After EACH domain pass
   completes, update that row in `.craftsman/master-tracker.md` — findings count, Last run date,
   mechanical grade — before launching the next pass. This is what makes a dead or interrupted
   session resumable: the tracker never lags more than one pass behind reality.

7. **Synthesize then prioritize into a climb sequence.** Collapse all findings into the master
   tracker's ordered "do-these-first" list, tiered for the persona. → `references/prioritization.md`

   **Synthesis protocol** — run in this order before writing the tracker:

   a. **Collect:** read every `audits/<scope>/<domain>/findings.md` from disk. Run the mechanical
      validation checklist from `references/workspace.md` → "Canonical findings.md emission format"
      on every file:
      1. Every finding heading matches (full line):
         `^## [A-Za-z0-9][A-Za-z0-9-]*-(UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI)-\d{3} · severity [🔴🟡🟢] · status (open|fixed|regressed|wontfix \(.+\)|fixed \(merged into .+\))$`
         (ID shape: `<scopeLabel>-<DOMAINCODE>-NNN`; DOMAINCODE one of UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI; NNN exactly 3 digits)
      2. For each finding block (from a `## ` heading until the next `## ` or EOF): exactly one of
         each required label in order — `**What breaks (plain language):**` then `**Technical:**`
         then `**Fix:**` then `**Fingerprint:**` then `**Last-checked:**` (multi-line values allowed
         until the next `**` label or heading); Fingerprint value matches
         `` `scope=... · domain=... · class=... · resource=...` ``; Last-checked value is non-empty
         and matches `\d{4}-\d{2}-\d{2} · ([0-9a-f]{4,40}|none \(no git\))`; optional
         `**Fix-attempt:**` only after Last-checked
      3. No `###` finding headings anywhere in the file
      4. No body bullets `- **Severity:**` or `- **Status:**`
      5. Empty findings file (header only, zero findings) is valid if it has the file header stamp
         and no malformed headings
      6. **Path binding:** for `audits/<scope>/<domain>/findings.md`, every finding's Fingerprint
         `scope=` equals that `<scope>` path, Fingerprint `domain=` equals that `<domain>` name, and
         the heading uses `scopeLabel = scope.replaceAll('/', '-')` plus the DOMAINCODE for that
         domain (see domain-code table in `workspace.md`). Shape-valid findings in the wrong file
         are blockers — do not re-home during synthesis; re-prompt the domain pass.
      A file that fails any check is a **blocker** — do **not** synthesize from it and do **not** invent
      a normalizer that accepts broken variants. Re-run that domain pass (prefer re-prompting the domain
      subagent with the failed file + the canonical template) or fix the file before continuing.

   b. **Flatten:** build a single pooled list of all findings. For small audits (≤ 3 domain/scope
      pairs) do this inline. For large audits, delegate to a synthesis agent with the full findings
      list pasted as input — it flattens, deduplicates, and returns the ranked list; you write the
      tracker from that output.

   c. **Deduplicate and reconcile:** apply steps 2–2c of `references/prioritization.md` — dedup/merge,
      cross-domain rollup, and cross-scope same-resource merge.

   d. **Rank and write:** sort 🔴 Tier 1 → 🟡 Tier 1 → 🔴 Tier 2 → 🟡 Tier 2 → 🟢, then write
      the master tracker.

   After presenting the climb sequence to the user, tell them the fix path: to start fixing, invoke
   `craft-fix` (or say "fix the findings" / "fix `<ID>`") — it works through the climb sequence with
   your approval, and the next re-run of this skill verifies what actually got fixed.

8. **Maintain the master tracker.** The tracker file already exists — its skeleton was written in
   step 3 and its per-row status was kept current through step 6. This step **fills in the synthesis
   parts**: the climb sequence, cross-cutting rollups, and the overall grade — it does not create
   `.craftsman/master-tracker.md` from scratch. `.craftsman/master-tracker.md` records which audits
   exist, their status, when they last ran (date + commit), the top open findings, and a **derived
   readiness grade** per (scope, domain) plus an overall grade (the worst applicable surface). The
   grade is computed mechanically from open findings — never hand-set — so it stays honest. On
   re-runs it diffs, not overwrites — fixed findings move to ✅, new ones get IDs, and a delta report
   leads the summary. → `references/workspace.md` (grade + tracker) · `references/rerun.md` (diff +
   delta report)

   **On successful completion of this step:** delete `.craftsman/.run-in-progress` (the concurrency
   marker claimed after step 0). Do not delete it if the run aborts earlier.

## Reference index

| Task                                                                                  | Load                                  |
| ------------------------------------------------------------------------------------- | ------------------------------------- |
| **Detect project shape + classify which domains apply** (evidence-based)              | `references/discovery.md`             |
| **Workspace layout, file templates, tracker format, readiness grade, stable finding IDs, date stamps** | `references/workspace.md`             |
| **Re-running an audit: staleness detection, finding-by-finding diff, delta report** | `references/rerun.md`                  |
| **Persona-aware finding voice, severity, ruthless sequencing, MVP vs enterprise tiers** | `references/prioritization.md`       |
| **What to recommend when a surface is missing** (tiered, dated, defers to existing)   | `references/recommended-stack.md`     |
| **Quality gate detection** — linting config, CI gate, pre-commit hooks, TS strictness, `quality` script, local/CI drift | `references/quality.md` |
| **Deep lint/static-quality audit** — resolved ESLint rules, typed linting, strict rule standard, migration/fix plan | `craft-lint` |

For the actual domain audits, load the peer skill (`craft-ux`, `craft-backend`, etc.) — this skill
routes to them, it does not restate them.

## Standing principles (the non-negotiables)

- **Meet the project where it is — never demand a rewrite.** If a working stack exists (Auth.js,
  Postgres, Railway), audit *it* against the principles. Recommend a stack only to fill a genuine
  gap, and say so explicitly. The obnoxious "rip it out and use my favorites" audit is worse than
  useless.
- **Prioritize ruthlessly.** A finding the user can't act on in order is noise. Lead with the
  handful that prevent a breach, data loss, or embarrassment.
- **Plain language first, jargon second.** Every finding states the real-world consequence before
  the term of art.
- **Evidence over assumption.** Discovery cites files; applicability gives reasons; findings cite
  `file:line`. No "you probably don't have X" — go look.
- **Prefer working sibling code over abstract best-practice.** When a gap exists and the team has
  already solved it well elsewhere — another app in this monorepo, or (only with the user's go-ahead)
  a sibling/reference repo they point at — cite that concrete file as the fix template instead of a
  generic recommendation. Opt-in and gap-triggered; never auto-crawl outside the audited project. See
  `references/discovery.md` → "Reference calibration".
- **Don't restate the domains.** The orchestrator's authority is discovery, planning, prioritization,
  and tracking. The craft skills hold the standards. Loading them is mandatory, not optional.
- **Narrate the milestones.** Post a one-line chat checkpoint after discovery (e.g. "single Next.js
  app, pre-Tier-1"), after applicability (e.g. "7 of 10 domains apply — plan coming"), and after EACH
  domain pass (e.g. "security done — 4 findings, 2 critical · 3 domains remaining"). Silence for 30+
  minutes is a failure of the run, not neutrality.

## Audit checklist (for craft-audit)

When a meta-audit of the craftsman plugin itself runs (i.e. craft-audit auditing its own
orchestrator skill), use this checklist. Each item maps to the editing rules and design principles
in `CLAUDE.md`.

- [ ] Trigger description accurately and narrowly describes when this skill fires — no over-broad patterns; the description's boundary handoffs are stated and reciprocal; add a negative-trigger clause only where wrong-fires are likely
- [ ] Reference index lists every file that exists in `references/` and no files that don't exist
- [ ] Each domain skill's `## Audit checklist (for craft-audit)` section exists and surfaces the most important domain findings back to the orchestrator (if a domain skill lacks the section, that absence is itself a finding)
- [ ] Audit loop steps 0–8 correctly direct the agent to load the right reference for each step (no orphaned references, no step that references a non-existent section)
- [ ] quality.md is integrated into at least one audit loop step (not just listed in the reference index)
- [ ] quality.md findings are routed per the boundary sentence: lint/rule-content → lint plan section, CI-gate wiring → infra plan section
- [ ] Workspace template (`workspace.md`) is complete: all file templates present, `.craftsman/README.md` template orients a returning builder
- [ ] Re-run protocol (`rerun.md`) correctly describes how to resume a partial audit, including the "not seen ≠ fixed" rule and the delta report format
- [ ] Delegation thresholds are consistent throughout: ≤ 3 pairs = small project (inline), > 3 pairs = large project (delegate) — no approximations or conflicting numbers
- [ ] Cross-domain boundaries: domain skills do not duplicate each other's guidance (orchestrator owns discovery/planning/tracking; domain skills own findings)

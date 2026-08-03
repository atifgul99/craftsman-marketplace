# Craftsman — Roadmap & Design Notes

> Living design doc for the craft plugin. Captures the agreed architecture, what's built, what's
> parked, and the open decisions — so we don't rely on conversation memory. Update as ideas land.
>
> Last updated: 2026-08-03.

## What this plugin is

Cross-project engineering craft as Claude Code skills. Two kinds of skill:

- **Domain skills** (`craft-*`) — one per surface (ux, frontend, backend, db, security, infra,
  observability, testing, lint, ai). Principle-based, stack-agnostic, depth in `references/`, discover
  project specifics rather than hardcode them.
- **The orchestrator** (`craft-audit`) — the front door. Audits a whole project for
  production-readiness, decides which domains apply, plans + tracks the audit in a `.craftsman/`
  workspace, and routes findings to the domain skills.

## Who we optimize for (the persona)

- **Primary:** the builder of a cool-but-fragile MVP — used Claude / Lovable / Replit / v0, shipped
  something that demos well but is nowhere near production-grade (no real states, weak/no auth, no
  observability, AI slop, data that corrupts under load, fragile infra).
- **Secondary:** more advanced builders who still can't reliably hit enterprise-grade.

Implications, treated as requirements (not polish): plain-language findings (consequence before
jargon), ruthless prioritization over completeness, and always meet the project where it is (never
demand a rewrite of a working stack).

## Where audit state lives

- **`.craftsman/`** (in the audited project) — the audit's working state *about that project*;
  produced by `craft-audit`, which creates it and adds it to `.gitignore` as an action, not an
  enforced property.

---

## Phases

### P1 — skeleton (BUILT)

- [x] `craft-audit` orchestrator skill: `SKILL.md` + `references/{discovery, workspace,
      prioritization, recommended-stack}.md`.
- [x] `.craftsman/` workspace spec: layout, templates, gitignore, date/commit stamping, stable
      finding IDs, diff-on-rerun.
- [x] Discovery (evidence-based, cited) + applicability classification (applies/partial/N-A).
- [x] Persona-aware finding voice + severity + two-tier model (MVP-hardening vs scaling).
- [x] Tiered, dated, swappable recommended-stack layer that defers to the existing stack.
- [x] Internal feedback folder + schema + one-file-per-entry rule for dogfooding (drained and
      removed pre-ship — see CHANGELOG "Removed" entry).
- [x] Per-surface audit plans surfaced as todo lists (driven by the orchestrator, audit loop step 4).

### P2 — depth (BUILT — 2026-06-22)

- [x] Per-domain audit protocols emit their own todo lists. Each `craft-*` `SKILL.md` now carries a
      canonical `## Audit checklist (for craft-audit)` section; the orchestrator writes
      `plan.md` from discovery context, and each subagent merges the domain checklist as its first
      act before auditing. Ownership of the checklist lives with the domain that knows the surface.
- [x] Worked end-to-end example: a complete illustrative `.craftsman/` tree (fictional "Invoicely" SaaS,
      scope `root`, now 9 of 10 domains audited) committed at `craftsman/examples/craftsman-output/`.
      Synthetic by design — a portable teaching artifact that doesn't bake another repo's real holes
      into this one.
- [x] Per-domain readiness grade in the master tracker — a derived 🔴 Blocked / 🟡 At risk / 🟢 Solid /
      ❔ Unaudited per (scope, domain), plus an overall = worst applicable surface. Computed mechanically
      from open findings (no numeric scores) so it can't drift into theater. Spec in `workspace.md`.

### P3 — re-run intelligence (BUILT — 2026-06-22)

- [x] Robust diffing across runs hardened into an exercisable protocol: `references/rerun.md` — index
      prior fingerprints, re-observe, classify (open/fixed/regressed/new), per-finding `last-checked`
      stamp, candidate-match review for renamed resources, and the **"not seen ≠ fixed"** rule (a
      skipped pass can't masquerade as a fix). Drives a delta report in the tracker.
- [x] Staleness detection: `rerun.md` Part 1 — compare each artifact's stamped commit to current HEAD,
      scope-aware (diff changed files, regenerate only what changed; full regen if the stamped SHA is
      unresolvable), and surface the decision to the user. Audit loop gains a step 0 re-run pre-flight.

### P4 — closing the feedback loop (CLOSED — 2026-08-03)

- [x] Ran an internal dogfooding feedback loop (drain cadence: ≥3 entries accumulated, OR after any
      full craft-audit dogfood on a real project, OR weekly — whichever came first) through the
      pre-ship pass. Now closed: the internal folder is removed, and public feedback routes through
      GitHub Issues/Discussions instead (see `CONTRIBUTING.md`).
- Post-launch, non-trivial skill edits still get Codex adversarial review before commit when they
  change emission contracts, checklists, or orchestrator steps.

### Resolved / shipped recently

- **Findings emission contract (2026-07-15):** canonical `findings.md` heading grammar, path-bound
  scope/domain, mechanical validation before synthesis (no normalizer). Restated in all domain
  skills; worked-example findings + `scripts/check-invariants.mjs` enforce the grammar in CI.
  Library-monorepo scoping clarified in discovery/workspace. Sourced from internal dogfooding
  feedback.

### P5 — the fix companion (SHIPPED — 2026-07-06)

- [x] `craft-fix`: an action skill (not a domain — domains are the ten craft-* surfaces) that drives fixes
      against an existing `craft-audit` workspace. Parses a finding ID / domain / "top 5 off the
      climb sequence" invocation, re-verifies each pick's fingerprint against current code before
      proposing it, requires explicit user approval before editing, gates 🔴 auth/migration/
      data-handling fixes behind a short written plan, batches fixes by surface (disjoint-file-ownership
      rule for parallel subagents), hands fixer subagents only the finding record + referenced domain
      docs (never the whole workspace), and appends a `Fix-attempt` annotation without ever setting
      status to `fixed` itself — only a `craft-audit` re-run's re-observation of the finding can, per
      "not seen ≠ fixed". `SKILL.md` + `references/fix-protocol.md`; `scripts/check-invariants.mjs` exempts it
      from the domain audit-checklist heading requirement by name.

---

## Parked ideas (not yet scheduled)

## Resolved during the skills audit (2026-06-19)

- **Rate-limiting ownership.** Initially advertised in backend + security descriptions with no
  reference home. Now assigned: **craft-infra owns the mechanism** (`scale-resilience.md` — edge/KV
  counters, gateway throttles, per-route limits) and advertises it in its description;
  **craft-security owns the abuse/brute-force use case** (`authz.md` — login/reset/OTP throttling
  policy) and points to infra for the mechanism. Could later grow a dedicated reference if it
  outgrows the scale-resilience home.

## Folded in (2026-07-06)

- **Compliance / data-rights coverage** — was parked above as compliance-craft-or-fold-in; decision
  made: **folded in**, not graduated to a standalone domain. The small auditable surface (data-rights
  plumbing, consent mechanics, PII surface, dependency license compliance, policy/ToS presence checks,
  email compliance) was distributed into existing domain checklists rather than standing up a 10th
  domain — see the parked-idea entry above for the full breakdown of what folded where
  (`craft-security` + `craft-db` for PII/data-rights, `craft-frontend` for consent/policy-link,
  `craft-security`/`craft-infra` for dependency licenses). Same treatment given to incident-response,
  cost-awareness, load-behavior, and email-deliverability checks raised in the same review pass — each
  is a few checklist lines in an existing domain's `## Audit checklist (for craft-audit)` section,
  not a new skill. **Graduation trigger (unchanged from the original parked note):** watch incoming
  user feedback for recurring demand that keeps landing on this surface, or a host domain's checklist section
  outgrowing what a few bullet points can carry (i.e. it needs its own `references/*.md` depth) — either
  signal is grounds to split it into a standalone `compliance-craft` with its own checklist, references,
  and readiness grade.

## Graduated (2026-07-15)

- **`craft-ai` graduated 2026-07-15.** LLM-integration domain (prompt injection surface, key/spend
  safety, PII-to-model-API exposure, reliability/evals) moved from `drafts/` into
  `craftsman/skills/craft-ai/`, wired into craft-audit (discovery applicability, domain code `AI`,
  emission grammar), and counted as the 10th domain skill.

## Resolved (2026-06-24)

- **`craft-testing` added as the 8th domain.** Five references built and Codex-reviewed: `strategy.md`
  (risk-weighted budget, trophy vs pyramid, Tier A/B/C), `test-design.md` (behavior vs implementation,
  determinism, AAA, factories), `flake.md` (full flake taxonomy + diagnosis + quarantine policy),
  `frontend-testing.md` (query-by-role, MSW, async UI, component vs e2e split), and
  `backend-data-testing.md` (Testcontainers, per-test isolation, factories, IDOR regressions, contract
  testing). Graduated into `craftsman/skills/`; `drafts/` is now empty.

- **Repo renamed `ag-plugins` → `craftsman-marketplace`.** GitHub repo renamed via `gh repo rename`,
  local folder renamed accordingly. Updated: `marketplace.json` (name + URLs), `plugin.json` (URLs),
  `README.md` (install commands, structure tree header, placeholder note removed), `ROADMAP.md`
  (this entry). Install command is now `/plugin install craftsman@craftsman-marketplace`.

## Resolved (2026-06-23)

- **Plugin renamed `ag-craft` → `craftsman`.** Done: directory `git mv`'d, `plugin.json` name,
  `marketplace.json` name + `source: ./craftsman`, README (prose, structure tree, install command
  `craftsman@ag-plugins`), `drafts/README.md`, and the example pointer in `workspace.md` all updated.
  The orchestrator skill (`craft-audit`) and workspace (`.craftsman/`) were already craftsman-named
  and are unchanged, so the three now align.

## Trademark risk acceptance (2026-08-03)

- **Decision: keep the name "Craftsman."** *Craftsman* is a registered trademark of Stanley Black
  & Decker, used for hand and power tools. This project is an unrelated free, MIT-licensed
  developer tool — a Claude Code skill marketplace — in a different goods/services class, with no
  connection to or endorsement by Stanley Black & Decker implied. The risk was reviewed and
  accepted on 2026-08-03. A rename remains possible if the name is ever challenged, but none is
  planned.

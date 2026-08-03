# craftsman-marketplace

A Claude Code **marketplace** containing one plugin, `craftsman`: a whole-project
production-readiness audit system built from opinionated, portable "craft" skills — one per
engineering domain, plus a top-level orchestrator that ties them together.

## What it does

`craft-audit` is the front door. Instead of reviewing one file or one PR, it audits an entire
project for production-readiness: it discovers what the project actually is (monorepo, single app,
marketing site, multiple apps), figures out which engineering domains even apply, writes a tailored
audit plan per surface, and drives the domain skills to find and prioritize the gaps that stand
between a working demo and something you'd trust in production. Everything it finds and tracks lives
in a durable `.craftsman/` workspace inside the project being audited, so a big audit survives across
sessions instead of starting over every time.

Built for one job: **take a cool-but-fragile vibe-coded MVP (Lovable / Replit / Claude / v0) to
enterprise-grade** — with plain-language findings and a ruthlessly prioritized "fix these first"
sequence, meeting the project where it is rather than demanding a rewrite. The loop closes with
`craft-fix`: the audit finds, `craft-fix` drives the fixes, and a `craft-audit` re-run
verifies — a fixer never marks its own work `fixed`, only a re-run's fingerprint diff can.

## What makes it different

- **A durable workspace, not a one-shot report.** `.craftsman/` persists in the audited project
  across sessions — discovery, applicability, the audit plan, and every finding are on disk. A
  typical single-app audit runs tens of minutes; a large monorepo can run to hours — either way it
  can pause and resume without re-deriving context.
- **Fingerprint-based re-run diffing — "not seen ≠ fixed."** Re-running the audit doesn't just
  regenerate a fresh report; it re-observes each prior finding, classifies it (open / fixed /
  regressed / new), and refuses to let a skipped check masquerade as a resolved one.
- **Mechanical readiness grades.** Each (surface, domain) gets a derived 🔴 Blocked / 🟡 At risk /
  🟢 Solid / ❔ Unaudited grade computed from open findings — no hand-waved scores, no theater.
- **One coherent opinion system, not a grab-bag of checklists.** Every domain skill shares the same
  design principles (meet the project where it is, prioritize ruthlessly, plain language before
  jargon) and the same graduation bar: a new domain stays out of the active set until its
  `references/` hold concrete, adversarially-reviewed guidance. An auto-triggering skill that routes
  to an empty stub is worse than no skill at all.

## What the output looks like

From the worked example — a fictional SaaS audited across four domains:

```
## Climb sequence (do these first)
| # | ID | Finding (plain language) | Severity | Status |
| - | -- | ------------------------ | -------- | ------ |
| 1 | root-SEC-001 | Anyone can open another company's invoice by changing the URL number | 🔴 | open |
| 2 | root-DB-001 | The database doesn't enforce tenant separation — one missed filter exposes everyone | 🔴 | open |
| 3 | root-SEC-003 | The server trusts whatever the browser sends — no validation at the door | 🟡 | open |
| 4 | root-SEC-004 | Can't confirm the DB admin key isn't reachable from the browser | 🟡 | open |

## Readiness (derived — never hand-set)
| Grade | Means | Rule |
| ----- | ----- | ---- |
| 🔴 Blocked | not production-ready | ≥1 open/regressed 🔴 |
| 🟡 At risk | usable, has holes | no open 🔴, ≥1 open 🟡 |
| 🟢 Solid | production-grade for this surface | only 🟢 open, or nothing |

**Overall readiness: 🔴 Blocked** — critical findings in `root` security and db prevent
shipment. Clearing SEC-001 + DB-001 promotes both surfaces toward 🟡 At risk.
```

Full worked example, including per-domain findings and the audit status table, is at
[`craftsman/examples/craftsman-output/`](./craftsman/examples/craftsman-output/).

## Install

```
/plugin marketplace add atifgul99/craftsman-marketplace
/plugin install craftsman@craftsman-marketplace
```

## Quickstart

1. **Install** — the two commands above.
2. **Trigger it** — these are auto-triggering skills, not slash commands. Just say what you want in
   plain language, e.g. "is my app production-ready" or "take this from MVP to production" — Claude
   picks up `craft-audit` from that phrasing on its own.
3. **What happens** — `craft-audit` tells you in chat what it's about to do, then creates a gitignored
   `.craftsman/` workspace at your project root: `discovery.md` (what the project actually is),
   `applicability.md` (which of the 10 domains apply), `master-tracker.md` (the climb sequence and
   readiness grades), and per-surface `audits/<scope>/<domain>/plan.md` + `findings.md`. A single-app
   audit runs tens of minutes; a monorepo can run to hours — it checkpoints to disk as it goes, so you
   can walk away and resume later instead of losing progress.
4. **Act on the results** — once you have a climb sequence, say "fix the findings" (or name one, e.g.
   "fix SEC-003") to invoke `craft-fix`. It re-verifies each pick against current code, gets your
   sign-off, and executes a scoped batch — it never marks anything `fixed` itself; only a `craft-audit`
   re-run's fingerprint diff does that.

## Compatibility

Requires **Claude Code v2.1.143 or later**. The plugin manifest (`craftsman/.claude-plugin/plugin.json`)
sets `displayName`, which Claude Code only reads starting at that version — earlier versions ignore
the field and fall back to `name` in the `/plugin` picker. Plugin marketplaces and plugin-provided
skills (what `craft-audit` and the domain skills rely on) work on far older versions, so `displayName`
is the highest floor this repo currently sets. Check your version with `claude --version`.

## The skills

The method and checklists are stack-agnostic and discover the actual stack at runtime, but the
deepest guidance leans TypeScript/Next.js/Postgres/serverless — the vibe-coder default stack.

| Skill | What it audits | Example trigger phrase |
| --- | --- | --- |
| `craft-audit` | Whole-project production-readiness — discovers project shape, routes to the domains below, tracks findings in `.craftsman/` | "is my app production-ready" |
| `craft-ux` | Design-system tokens, component/state/motion layers, accessibility, AI-tells anti-patterns | "audit my design tokens" |
| `craft-frontend` | Component architecture, state management, data fetching, forms, bundle size | "this page is slow" |
| `craft-backend` | API routes, request validation, the auth boundary, service logic, background jobs | "why is this returning 500" |
| `craft-db` | Schema design, migrations, query/indexing, multi-tenant data scoping | "this query is slow" |
| `craft-security` | Authorization policy, input validation, secrets, headers/CORS, dependency vulnerabilities | "is this secure" |
| `craft-infra` | Deployment, env/config, CI/CD, health probes, rate limiting, rollback | "set up CI" |
| `craft-observability` | Sentry, structured logging, Grafana/OpenTelemetry, SLOs and alerting | "why can't we see errors" |
| `craft-testing` | Test strategy, unit/integration/e2e selection, flaky-test triage, test-gate policy | "why is this test flaky" |
| `craft-lint` | ESLint rule policy, typed linting, zero-warning CI gates, lint config hardening | "standardize linting" |
| `craft-ai` | LLM integrations — prompt injection, key/spend safety, PII-to-model APIs, reliability/evals | "is my chatbot secure" |
| `craft-fix` | Drives fixes against an existing `.craftsman/` audit — re-verifies, batches by surface, tracks attempts, never self-marks `fixed` | "fix the findings" / "fix SEC-003" |

See each skill's `SKILL.md` under `craftsman/skills/<name>/` for its full trigger description and
`references/` for the method behind it.

## Worked example

A complete, synthetic end-to-end audit — a fictional "Invoicely" SaaS app audited across four
domains — is committed at
[`craftsman/examples/craftsman-output/`](./craftsman/examples/craftsman-output/). It's a teaching
artifact showing the full shape of a `.craftsman/` workspace: discovery, applicability, the master
tracker with readiness grades, and per-domain findings.

## The one rule that prevents the next mess

**One trigger per domain. Depth goes in `references/`. A concept earns its own top-level skill only
if it's an independently-invoked gate/action** (e.g. "audit my design tokens", "run a security
review") rather than build-time knowledge. Knowledge folds into a domain; gates stand alone.

## Structure

```
craftsman-marketplace/          ← marketplace (this repo)
  .claude-plugin/marketplace.json
  craftsman/                    ← the plugin
    .claude-plugin/plugin.json
    skills/                     ← ACTIVE (all loaded) — SKILL.md + references/ each
      craft-audit/          ← the orchestrator (front door): discovery, applicability, planning, tracking
      craft-fix/            ← the action companion: drives fixes off an existing .craftsman/ audit
      craft-ux/                 ← + references/motion/ and scanner-fixtures/
      craft-frontend/
      craft-backend/
      craft-db/
      craft-security/
      craft-infra/
      craft-lint/
      craft-observability/
      craft-testing/
      craft-ai/
    drafts/                     ← incubator for future domains — NOT loaded; graduate to skills/ when filled
    examples/                   ← illustrative `.craftsman/` output (a worked end-to-end audit) — reference, not live state
  ROADMAP.md                    ← design notes, phases, parked ideas (repo-level, not shipped in the plugin)
  CONTRIBUTING.md               ← how to propose changes to the skills
```

The orchestrator's `.craftsman/` workspace lives in the **project being audited** (gitignored), not
in this repo — it's per-project audit state.

## The split that matters

| Knowledge                        | Lives in                                    | Example                                      |
| --------------------------------- | -------------------------------------------- | --------------------------------------------- |
| **Method + opinions** (portable) | the skill                                   | "errors → Sentry first; alert on symptoms"   |
| **Specifics that live in code**  | the target repo (discovered at runtime)     | the logger, the DSN, the token names         |
| **Specifics not in code**        | a thin per-repo note (e.g. its `CLAUDE.md`) | governance thresholds, exempt-file rationale |

Skills **never hardcode a project's nouns** — they discover them from the repo. That's what makes
one skill work across every repo it's used in.

## Persona

Built primarily for the builder of a cool-but-fragile MVP — shipped something with Claude / Lovable
/ Replit / v0 that demos well but is nowhere near production-grade (no real states, weak/no auth, no
observability, data that corrupts under load, fragile infra). Findings lead with plain-language
consequence, not jargon.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) — the skills are opinion documents, so contributions are
opinion edits and need to cite a concrete failure mode.

## License

MIT — see [LICENSE](./LICENSE).

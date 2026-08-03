# craftsman

**The engineering review you'd get from the technical co-founder you don't have.**

You built a real app without being an engineer. It works. You're about to let real users in, maybe
take payments, maybe hold their data. Most people in that position could not say what a senior
engineer would flag. That gap doesn't show up until something breaks in front of a customer.

`craft-audit` is that review. Point it at your project and it audits the whole thing for
production-readiness, not just one file or one pull request: it works out what your project
actually is, then finds the gaps between a working demo and something you'd trust with real
customers. It writes everything it finds to disk so you can pick it back up later instead of
losing the work.

Written by [Atif Gul](https://github.com/atifgul99), a software engineer of 25 years, including
time at Microsoft and Amazon.

## What it catches

Here's the kind of thing an audit like this turns up:

- Anyone logged in can open another customer's invoice, just by changing the number in the URL.
- The database itself does not know which customer should see what. It relies entirely on the app
  remembering to check, so one missed check anywhere exposes everyone's data.
- A route that moves money never checks who is calling it before it runs.
- The path that creates and pays invoices has zero automated tests, so a one-line change can break
  billing and nothing will catch it before a customer does.
- When the app throws an error for a real user, nobody finds out. You hear about it when a customer
  emails you, not before.

These are adapted from a worked example shipped in this repo: see
[`craftsman/examples/craftsman-output/`](./craftsman/examples/craftsman-output/) for the real
findings, unedited.

None of this means your app is bad. It means nobody who knew what to check has looked yet. That's
the gap craftsman closes.

## What stands between your app and enterprise-grade

Most tools built for this moment check one thing: security. Security matters, and craftsman
checks it too. But it's one of ten areas this audits, not the only one. The other nine matter just
as much. A database that does not enforce its own boundaries, an error nobody sees until a customer
emails you, a payment path with no tests: any one of those takes an app down as fast as a security
hole does.

The second difference is in how craftsman treats "fixed." The companion skill, `craft-fix`, is
structurally forbidden from marking its own work as fixed. Only a fresh audit pass, re-checking the
code as it actually stands, can close a finding. That rule exists because "I fixed it" and "it is
actually fixed" are not the same claim, and most tools let the first one stand in for the second.

## What this is not

It is not a penetration test. It is not continuous monitoring; nothing runs in the background
between sessions. It is not legal or compliance advice. It does not output a numeric score, on
purpose, because a single number invites false confidence. And it takes tens of minutes to run, not
seconds, because reading a whole project properly takes time.

## What makes it different

- **A durable workspace, not a one-shot report.** `.craftsman/` persists in the audited project
  across sessions: discovery, applicability, the audit plan, and every finding are on disk. A
  typical single-app audit finishes in under an hour; a large monorepo can take longer. Either way
  it can pause and resume without redoing the work.
- **A written rule for what counts as fixed.** Every finding carries a stable identity (scope,
  domain, defect class, resource) that survives line-number and file-move churn. Re-running the
  audit doesn't just regenerate a fresh report. The agent re-checks each prior finding against that
  identity, classifies it as open, fixed, regressed, or new, and a skipped check can never pass
  itself off as a resolved one.
- **A fixed, stated grading rule.** Each surface and domain gets a grade (Blocked, At risk, Solid,
  or Unaudited) derived from open findings, using a rule that is written down and does not vary by
  mood or by run. See the table below. The value is that the rule is explicit and repeatable, not
  hand-waved.
- **One coherent opinion system, not a grab-bag of checklists.** Every domain skill shares the same
  principles (meet the project where it is, prioritize ruthlessly, plain language before jargon)
  and the same bar for shipping: a new domain stays out of the active set until its reference
  material holds concrete, reviewed guidance. A skill that routes to an empty stub is worse than no
  skill at all.

## What the output looks like

From the worked example, a fictional SaaS audited across nine of the ten applicable domains:

```
## Climb sequence (do these first)
| # | ID | Finding (plain language) | Severity | Status |
| - | -- | ------------------------ | -------- | ------ |
| 1 | root-SEC-001 | Anyone can open another company's invoice by changing the URL number | 🔴 | open |
| 2 | root-DB-001 | The database doesn't enforce tenant separation: one missed filter exposes everyone | 🔴 | open |
| 3 | root-SEC-003 | The server trusts whatever the browser sends, no validation at the door | 🟡 | open |
| 4 | root-SEC-004 | Can't confirm the DB admin key isn't reachable from the browser | 🟡 | open |

## Readiness (derived, never hand-set)
| Grade | Means | Rule |
| ----- | ----- | ---- |
| 🔴 Blocked | not production-ready | ≥1 open/regressed 🔴 |
| 🟡 At risk | usable, has holes | no open 🔴, ≥1 open 🟡 |
| 🟢 Solid | production-grade for this surface | only 🟢 open, or nothing |

**Overall readiness: 🔴 Blocked.** Critical findings in `root` security and db prevent
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

1. **Install.** The two commands above.
2. **Trigger it.** These are auto-triggering skills, not slash commands. Just say what you want in
   plain language, e.g. "is my app production-ready" or "take this from MVP to production."
   `craft-audit` is written to trigger on that phrasing. Skill selection is model behavior, not a
   guarantee, so if it doesn't fire, ask for it by name: "use craft-audit."
3. **What happens.** `craft-audit` tells you in chat what it's about to do, then creates a
   `.craftsman/` workspace at your project root and adds it to your `.gitignore` (verify the entry
   landed; this is an action the skill takes, not a property it enforces): `discovery.md` (what the
   project actually is), `applicability.md` (which of up to 10 domains apply), `master-tracker.md`
   (the climb sequence and readiness grades), and per-surface `audits/<scope>/<domain>/plan.md` +
   `findings.md`. A single-app audit usually finishes in under an hour; a monorepo can take longer.
   It checkpoints to disk as it goes, so you can walk away and resume later instead of losing
   progress.
4. **Act on the results.** Once you have a climb sequence, say "fix the findings" (or name one, e.g.
   "fix SEC-003") to invoke `craft-fix`. It re-verifies each pick against current code, gets your
   sign-off, and executes a scoped batch. It never marks anything `fixed` itself; only a
   `craft-audit` re-run's re-observation of the finding does that.

## Compatibility

Neither manifest (`craftsman/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) declares
a minimum Claude Code version. Use a current Claude Code release with plugin marketplace support;
older versions are unverified. Check your version with `claude --version`, and if you hit an install
or loading issue, update to the latest release first.

## The skills

The method and checklists are stack-agnostic and discover the actual stack at runtime, but the
deepest guidance leans TypeScript/Next.js/Postgres/serverless, the vibe-coder default stack.

| Skill | What it audits | Example trigger phrase |
| --- | --- | --- |
| `craft-audit` | Whole-project production-readiness. Discovers project shape, routes to the domains below, tracks findings in `.craftsman/` | "is my app production-ready" |
| `craft-ux` | Design-system tokens, component/state/motion layers, accessibility, AI-tells anti-patterns | "audit my design tokens" |
| `craft-frontend` | Component architecture, state management, data fetching, forms, bundle size | "this page is slow" |
| `craft-backend` | API routes, request validation, the auth boundary, service logic, background jobs | "why is this returning 500" |
| `craft-db` | Schema design, migrations, query/indexing, multi-tenant data scoping | "this query is slow" |
| `craft-security` | Authorization policy, input validation, secrets, headers/CORS, dependency vulnerabilities | "is this secure" |
| `craft-infra` | Deployment, env/config, CI/CD, health probes, rate limiting, rollback | "set up CI" |
| `craft-observability` | Sentry, structured logging, Grafana/OpenTelemetry, SLOs and alerting | "why can't we see errors" |
| `craft-testing` | Test strategy, unit/integration/e2e selection, flaky-test triage, test-gate policy | "why is this test flaky" |
| `craft-lint` | ESLint rule policy, typed linting, zero-warning CI gates, lint config hardening | "standardize linting" |
| `craft-ai` | LLM integrations: prompt injection, key/spend safety, PII-to-model APIs, reliability/evals | "is my chatbot secure" |
| `craft-fix` | Drives fixes against an existing `.craftsman/` audit. Re-verifies, batches by surface, tracks attempts, never self-marks `fixed` | "fix the findings" / "fix SEC-003" |

See each skill's `SKILL.md` under `craftsman/skills/<name>/` for its full trigger description and
`references/` for the method behind it.

## Worked example

A complete, synthetic end-to-end audit, a fictional "Invoicely" SaaS app audited across nine of
the ten applicable domains, is committed at
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
    skills/                     ← ACTIVE (all loaded): SKILL.md + references/ each
      craft-audit/          ← the front-door orchestrator: discovery, applicability, planning, tracking
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
    drafts/                     ← incubator for future domains, NOT loaded; graduate to skills/ when filled
    examples/                   ← illustrative `.craftsman/` output (a worked end-to-end audit), reference, not live state
  ROADMAP.md                    ← design notes, phases, parked ideas (repo-level, not shipped in the plugin)
  CONTRIBUTING.md               ← how to propose changes to the skills
```

The audit's `.craftsman/` workspace lives in the **project being audited**, not in this
repo. It's per-project audit state. `craft-audit` adds it to that project's `.gitignore` as part of
setup; verify the entry landed if you want it kept out of version control.

## The split that matters

| Knowledge                        | Lives in                                    | Example                                      |
| --------------------------------- | -------------------------------------------- | --------------------------------------------- |
| **Method + opinions** (portable) | the skill                                   | "errors → Sentry first; alert on symptoms"   |
| **Specifics that live in code**  | the target repo (discovered at runtime)     | the logger, the DSN, the token names         |
| **Specifics not in code**        | a thin per-repo note (e.g. its `CLAUDE.md`) | governance thresholds, exempt-file rationale |

Skills **never hardcode a project's nouns**: they discover them from the repo. That's what makes
one skill work across every repo it's used in.

## Persona

Built for the builder of a cool-but-fragile MVP: someone who shipped something with Claude, Lovable,
Replit, or v0 that demos well but is nowhere near production-grade (no real states, weak or no auth,
no observability, data that corrupts under load, fragile infra). Findings lead with plain-language
consequence, not jargon.

## Why this exists

I have been building software for 25 years, including at Microsoft and Amazon. These days I build
and ship my own products: Next.js apps on Postgres, with real users and real money moving through
them. I kept doing the same review by hand every time one of them got close to launch. Same areas,
same questions, same handful of things that turned out to be wrong. So I wrote it down, turned it
into something Claude Code could run, and pointed it at my own repos until it stopped surprising
me. The opinions in it are mine, and they come from shipping things and watching them break.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). The skills are opinion documents, so contributions are
opinion edits and need to cite a concrete failure mode.

## License

MIT. See [LICENSE](./LICENSE).

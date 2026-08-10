---
name: craft-infra
description: >-
  The Craftsman standard for production infrastructure — deployment, env/config, CI/CD, IaC,
  health/readiness, scaling, platform/edge rate limiting, build/release, rollback. Use WHENEVER work
  touches infra: deploy, CI gates, env vars, IaC, load failures, rate limiting (this skill owns
  platform/edge capacity; route middleware → craft-backend; login abuse policy → craft-security; LLM
  spend → craft-ai), pooling runtime constraints (sizing → craft-db), or production runtime. Trigger
  on "deploy this", "set up CI", "add rate limiting", "configure env vars", or "why did it fall over
  under load". Observability (Sentry/Grafana/SLOs) → craft-observability. CI handoff: pipeline
  mechanism here; which suites gate merge → craft-testing. Whole-project readiness → craft-audit.
---

# Infra Craft

This skill encodes one engineer's standard for shipping and running services reliably, applied the
same way across every repo. The **method and opinions** live here; the **project specifics**
(hosting platform, CI system, IaC tool, env-var schema) live in the target repo's code and config —
always discover them, never assume or hardcode.

## Operating principle — discover before you build

Different repos already have different pieces in place. Before adding anything, spend a couple of
minutes mapping what exists so you extend rather than duplicate or conflict:

- `package.json` / lockfile → build tooling, runtime adapters (e.g. `@vercel/node`, `fly` CLI hints,
  serverless framework packages).
- CI config files (`.github/workflows/`, `.circleci/`, `Jenkinsfile`, `.gitlab-ci.yml`) → existing
  gates, deploy steps, environment secrets.
- Env-var schema (`env.ts`, `config.ts`, `.env.example`, `zod` schemas) → which vars are required,
  which are optional, where validation happens.
- Health/readiness endpoints (`/health`, `/ready`, `/api/healthz`) and how they're registered.
- IaC files (`terraform/`, `pulumi/`, `cdk/`, `fly.toml`, `vercel.json`, `render.yaml`) → existing
  resource definitions to extend rather than replace.

State what you found, then propose the smallest set of additions that closes the gaps.

## The infra layers (work in this order)

1. **Config** — all configuration flows through a validated env schema that fails closed on missing
   required values. A missing prod var should crash at startup, not surface as a 500 at runtime.
   See `references/config.md`.
2. **Build & release** — builds are reproducible and produce immutable artifacts; the release
   process is documented and automated enough that any team member can trigger it. See
   `references/build-release.md`.
3. **CI/CD** — gates (lint, typecheck, tests, build) block merge; deploys are automated and
   reversible. Manual prod edits are the failure mode, not the workflow. See `references/ci-cd.md`.
4. **Runtime health** — every service exposes health and readiness probes; graceful shutdown drains
   in-flight requests; connection pools are sized and scoped to the runtime model (serverless vs
   long-lived). See `references/runtime-health.md`.
5. **Scale & resilience** — timeouts, retries with backoff, circuit breakers, and capacity limits
   that match the actual runtime model. Serverless runtimes do not guarantee shared or durable
   in-process state across invocations/instances — warm instances may reuse module-scope state but
   this is neither guaranteed nor shared globally and can disappear at any time. Anything that
   assumes a long-lived process (in-memory pools, local metrics registries) needs a flag or
   replacement. See `references/scale-resilience.md`.

## Standing opinions (the non-negotiables)

These are the judgments that make output consistent across repos — apply them unless the user
overrides:

- **Config is validated and fails closed.** Every required env var is declared in a schema; if it's
  missing the process refuses to start rather than limping along and erroring at the call site. This
  is the single highest-leverage infra habit.
- **CI gates are required before merge.** Lint, typecheck, tests, and a production build must all
  pass. A CI pipeline that only runs on deploy (not on PR) is too late to catch regressions cheaply.
- **Deploys are automated and reversible.** No manual production edits — they're untracked and
  unreviewable. Every deploy path has a documented rollback step (previous image tag, Vercel
  instant rollback, Terraform state revert, etc.).
- **Serverless runtimes are ephemeral.** In-process pools, singleton metrics registries, and
  circuit-breaker state all evaporate between invocations. Flag any tool or library that assumes a
  long-lived process and propose the serverless-appropriate alternative before wiring it in.
- **Every service has health and readiness endpoints.** Health says "I am alive"; readiness says "I
  am ready to serve traffic". They are not the same check. Load balancers and orchestrators need
  both.

## Workflow

1. **Discover** — map the existing pipeline, env schema, health endpoints, and IaC (above) and
   report gaps.
2. **Propose** — ordered by the five layers, smallest viable additions first.
3. **Implement** — against the repo's existing pipeline and conventions, not a greenfield ideal.
4. **Verify** — run the CI pipeline end-to-end, hit the health endpoints, and walk through a
   rollback path. Infrastructure you haven't seen work isn't done.

## Reference index

Read the one matching the current task — they hold the concrete setup, not this overview:

- `references/config.md` — env-var schema patterns, fail-closed validation, typed config object, environment-tier separation (secret values and rotation → `craft-security` → `secrets.md`)
- `references/build-release.md` — reproducible builds, immutable artifacts, release process
- `references/ci-cd.md` — gate ordering, deploy automation, rollback patterns, CI secrets injection, OIDC workload identity
- `references/runtime-health.md` — health/readiness probes, graceful shutdown, connection pooling
- `references/scale-resilience.md` — timeouts, retries, circuit breakers, serverless capacity limits
- `references/iac.md` — infrastructure-as-code: platform-native config quickstarts (Fly.io, Render, Railway, Vercel), Terraform/Pulumi state backends, plan-in-CI gate, apply-only-from-main convention

## Audit checklist (for craft-audit)

When `craft-audit` plans an infra pass for a scope, it turns this checklist into the `plan.md`
todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor to what
discovery found: skip a step that genuinely doesn't apply with a one-line reason; never silently drop
one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission format"
(authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-INFRA-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-INFRA-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Confidence:**` — `verified | inferred | unverified-from-repo`, absent
means `verified` — then optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] Map what infra already exists (pipeline, env schema, health endpoints, IaC) before judging —
      flag assumptions made without reading the repo's actual config → `SKILL.md` (Operating principle)
- [ ] Verify config flows through a validated env schema that fails closed; bad if a missing required
      prod var surfaces as a runtime 500 instead of a startup crash → `references/config.md`
- [ ] Verify the sending domain has SPF/DKIM/DMARC records set and actually verified (not just pasted
      into DNS); bad if transactional email like password resets can silently land in spam →
      `references/config.md`
- [ ] Confirm billing alerts (and hard spend caps where offered) are set up on every metered provider
      before launch; bad if an unauthenticated route can hit a metered/LLM API with no rate limit and
      no one would notice the bill until it arrived → `references/config.md`
- [ ] Check builds are reproducible and produce immutable, content-addressed artifacts promoted across
      environments; bad if each env rebuilds from source or the release is undocumented → `references/build-release.md`
- [ ] Confirm CI gates (lint, typecheck, tests, build) block merge on PRs; bad if gates only run on
      deploy or merge can land red. **TEST ↔ INFRA handoff:** TEST owns which suites must gate merge
      and what "green" means (including e2e strategy); INFRA owns CI pipeline mechanism (when/how
      jobs run, secrets, deploy gates). Missing e2e *suite* → TEST finding; e2e exists but is *not
      wired into CI* → INFRA finding (TEST may note and route) → `references/ci-cd.md`
- [ ] Trace every required gate's trigger, job/step `if:`, `needs`, matrix, and secret/environment
      branches in both trusted and restricted PR contexts; flag a gate that is success/skipped while
      every substantive step was bypassed as vacuously green → `references/ci-cd.md`
- [ ] Confirm deploys are automated with a documented one-step rollback per path; bad if prod is
      edited manually or no rollback path is written down → `references/ci-cd.md`
- [ ] Verify the team knows to roll back first and diagnose after, and that a status page exists; bad
      if the instinct under pressure is to hotfix forward on a broken deploy, or an incident floods
      the support inbox with "is it down?" messages → `references/ci-cd.md`
- [ ] Verify every service exposes distinct health and readiness probes and drains in-flight requests
      on SIGTERM; bad if one endpoint conflates "alive" with "ready to serve" → `references/runtime-health.md`
- [ ] Check connection pools are sized and scoped to the runtime model; bad if a long-lived in-process
      pool is assumed under serverless and exhausts under load → `references/runtime-health.md`
- [ ] Verify outbound calls have timeouts, retries with backoff+jitter, and circuit breakers matching
      the runtime; bad if ephemeral runtimes rely on in-process breaker/metrics state → `references/scale-resilience.md`
- [ ] Confirm one load-test pass ran against the critical path before first real traffic; bad if the
      first real traffic spike is also the first time the app has seen concurrent load →
      `references/scale-resilience.md`
- [ ] Confirm staging environment matches production config (same infra provider, same env var
      surface); bad if staging runs on a different platform or is missing required vars that exist
      in production → `references/build-release.md`
- [ ] Verify an automated post-deploy gate runs in CI: health probe returns 200, at least one
      critical API path succeeds, and error rate stays below baseline for 5 minutes after deploy;
      bad if this requires manual checks or the pipeline declares success without confirming the
      deployed service is actually handling traffic → `references/ci-cd.md`

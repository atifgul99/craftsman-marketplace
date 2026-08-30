# Infra Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-infra · scope: root

## root-INFRA-001 · severity 🟡 · status open
**What breaks (plain language):** Required secrets and config are read straight from `process.env` with
no schema. A missing prod var doesn't stop the deploy — it surfaces later as a confusing 500 when a
user hits the code path that needs it.
**Technical:** No `env.ts` / zod env module; raw `process.env.SUPABASE_*` and friends in `lib/db.ts`
and `lib/auth.ts`. No `.env.example`. Fail-open at boot.
**Fix:** Introduce a validated server-only env schema that refuses to start (or fails the serverless
cold start) when required vars are missing. See craft-infra → `config.md` (secret *exposure* also
tracked as `root-SEC-004`).
**Fingerprint:** `scope=root · domain=infra · class=no-env-schema · resource=process.env reads`
**Last-checked:** 2026-06-22 · a1bec8f

## root-INFRA-002 · severity 🟡 · status open
**What breaks (plain language):** Nothing blocks a broken PR from landing. There's no CI quality gate —
lint, typecheck, tests, and build only happen (if at all) on a developer's laptop.
**Technical:** No `.github/workflows/` (or other CI config). `package.json` has no `ci` script
composition. Vercel builds on push but does not gate merge on green checks.
**Fix:** Add a PR workflow that runs lint, typecheck, tests, and a production build, and require it
before merge. See craft-infra → `ci-cd.md` (test runner absence is also `root-TEST-003`).
**Fingerprint:** `scope=root · domain=infra · class=no-ci-quality-gate · resource=.github/workflows`
**Last-checked:** 2026-06-22 · a1bec8f

## root-INFRA-003 · severity 🟡 · status open
**What breaks (plain language):** If a bad deploy ships, there's no written rollback step and no
health/readiness signal to tell Vercel (or you) the app is actually ready. Incidents turn into
"redeploy and pray."
**Technical:** No `/api/health` or readiness route; `vercel.json` has no health-check config; README
has no rollback runbook (Vercel instant rollback exists as a platform feature but is undocumented for
the team).
**Fix:** Add a cheap health endpoint that checks critical deps, document "Vercel → Deployments →
Promote previous" as the one-step rollback, and treat rollback-first as the default under pressure.
See craft-infra → `runtime-health.md` and `ci-cd.md`.
**Fingerprint:** `scope=root · domain=infra · class=no-health-or-rollback · resource=Vercel deploy path`
**Last-checked:** 2026-06-22 · a1bec8f

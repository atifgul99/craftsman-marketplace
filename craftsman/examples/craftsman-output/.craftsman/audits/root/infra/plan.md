# Infra Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-infra · scope: root

Scope for THIS surface (from discovery): Vercel deploy via `vercel.json`, no CI workflows, no validated
env schema, no health/readiness endpoints. Steps sourced from craft-infra's `## Audit checklist`.

- [x] Map existing infra (Vercel, no CI, no env schema, no health) → SKILL.md operating principle
- [x] Config through validated env schema that fails closed → `references/config.md`
- [ ] SPF/DKIM/DMARC on sending domain → `references/config.md` (deferred — email provider not fully wired)
- [ ] Billing alerts / spend caps on metered providers → `references/config.md` (deferred — Tier-1 config first)
- [x] Builds reproducible / release path → `references/build-release.md` (Vercel git-linked deploy present)
- [x] CI gates (lint, typecheck, tests, build) block merge → `references/ci-cd.md`
- [x] Deploys automated with documented one-step rollback → `references/ci-cd.md`
- [x] Health vs readiness probes distinct → `references/runtime-health.md`
- [ ] Connection pools sized for serverless → craft-db owns pooling detail (cross-ref only this pass)
- [ ] Load-test pass on critical path → `references/scale-resilience.md` (Tier-2 — deferred)
- [ ] Staging matches production config → `references/build-release.md` (deferred — no staging env found)
- [ ] Automated post-deploy gate → `references/ci-cd.md` (deferred — no CI yet)

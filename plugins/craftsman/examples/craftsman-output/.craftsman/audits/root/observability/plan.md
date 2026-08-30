# Observability Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-observability · scope: root

Scope for THIS surface (from discovery): Vercel serverless, zero instrumentation today — no Sentry, no
structured logging, no health signal. Steps sourced from craft-observability's `## Audit checklist`.

- [x] Map existing observability (none found) → SKILL.md operating principle
- [x] Runtime (serverless) drives the approach — no pull-based scraping; flush before exit → `references/serverless-vs-server.md`
- [x] Error tracking: unhandled errors + rejections captured, PII scrubbed, release-tagged → `references/sentry.md`
- [x] Structured JSON logs from one logger with a stable requestId → `references/logging.md`
- [ ] Dashboards provisioned as code (RED/USE) → `references/grafana.md` (Tier-2 — deferred until Tier-1 clears)
- [ ] SLOs + burn-rate alerting → `references/slo-alerts.md` (Tier-2 — deferred; no error tracking to base SLIs on yet)
- [ ] Every paging alert links a runbook → `references/slo-alerts.md` (Tier-2 — deferred; no alerts exist yet)
- [ ] Silent-degradation check (down dependency surfaces via health + log + metric) → SKILL.md "Standing opinions" (deferred — depends on error tracking + logging landing first)

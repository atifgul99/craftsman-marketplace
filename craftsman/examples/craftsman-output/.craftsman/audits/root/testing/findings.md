# Testing Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-testing · scope: root

## root-TEST-001 · severity 🔴 · status open
**What breaks (plain language):** The path that creates invoices and marks them paid has zero automated
tests. A one-line regression can corrupt amounts, double-charge, or skip a write — and nothing will
catch it before a customer does.
**Technical:** No `vitest`/`jest`/`playwright` in `package.json`; no `*.test.*` / `*.spec.*` under
`app/` or `lib/`. Money-touching handlers: `app/api/invoices/route.ts`, mark-paid mutation on the
dashboard.
**Fix:** Add a unit/integration harness and at least one happy-path + one failure-path test on invoice
create and mark-paid (schema + auth boundary). See craft-testing → `strategy.md` and
`backend-data-testing.md`.
**Fingerprint:** `scope=root · domain=testing · class=no-money-path-tests · resource=invoice create/pay`
**Last-checked:** 2026-06-22 · a1bec8f

## root-TEST-002 · severity 🔴 · status open
**What breaks (plain language):** The bug where any logged-in user can open another company's invoice
(`root-SEC-001`) has no regression test. Even after you fix it, nothing stops the next refactor from
re-opening the hole.
**Technical:** No authZ / IDOR test for `GET /api/invoices/:id`. No fixture for two orgs. The defect is
documented in security findings but unguarded by a failing-then-passing test.
**Fix:** Write a focused test: session for org A requesting org B's invoice id → 403/404; never 200
with data. Keep it as a permanent regression. See craft-testing → `backend-data-testing.md` and
craft-security → `authz.md`.
**Fingerprint:** `scope=root · domain=testing · class=no-idor-regression · resource=GET /api/invoices/:id`
**Last-checked:** 2026-06-22 · a1bec8f

## root-TEST-003 · severity 🟡 · status open
**What breaks (plain language):** Even if someone adds tests locally, CI never runs them — and today
there's no `test` script at all. Broken checks never block a merge.
**Technical:** `package.json` has no `"test"` script; no CI workflow invokes tests (see also
`root-INFRA-002`). A green Vercel build does not mean tests passed.
**Fix:** Add a `test` script + runner, then wire it into the PR quality gate. See craft-testing →
`strategy.md` and craft-infra → `ci-cd.md`.
**Fingerprint:** `scope=root · domain=testing · class=ci-does-not-run-tests · resource=package.json scripts`
**Last-checked:** 2026-06-22 · a1bec8f

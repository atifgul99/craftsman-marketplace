# Testing Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-testing · scope: root

Scope for THIS surface (from discovery): no test runner in `package.json`, no test files, money path
is invoice create/pay + IDOR-prone invoice fetch. Steps sourced from craft-testing's `## Audit checklist`.

- [x] Map existing test setup (none) — runner, folders, CI hook → SKILL.md operating principle
- [x] Critical-path coverage strategy for money + authZ → `references/strategy.md`
- [x] Backend/data tests for handlers and DB invariants → `references/backend-data-testing.md`
- [x] Frontend tests for forms/async states where risk is high → `references/frontend-testing.md`
- [x] CI actually runs the suite (or there is no suite to run) → `references/strategy.md`
- [ ] Flake budget / quarantine policy → `references/flake.md` (N-A — no suite yet)
- [ ] Test design depth (factories, fakes vs mocks) → `references/test-design.md` (deferred until runner lands)

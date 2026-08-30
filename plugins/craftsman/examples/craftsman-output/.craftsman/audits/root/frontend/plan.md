# Frontend Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-frontend · scope: root

Scope for THIS surface (from discovery): Next.js App Router dashboard, React 19, no data/cache lib, no
form lib, fetch inline. Steps sourced from craft-frontend's `## Audit checklist`.

- [x] Map stack — framework, data/cache lib (none), form lib (none), state → SKILL.md operating principle
- [x] Component boundaries — `"use client"` scope, data tangled into presentation → `references/architecture.md`
- [ ] State placement — server data mirrored into a store → `references/state.md` (N-A — no client store present)
- [x] Data fetching — inline fetch, unvalidated responses, waterfalls → `references/data-fetching.md`
- [x] Every async UI has loading + error + empty states → `references/data-fetching.md`
- [x] Mutations — `onError` rollback, optimistic-update safety, key invalidation → `references/data-fetching.md`
- [x] Forms — validation, types vs schema, submit disabled in-flight → `references/forms.md`
- [x] Form error accessibility — `role="alert"`, `aria-invalid`, focus first invalid → `references/forms.md`
- [ ] Performance against measurement → `references/performance.md` (deferred — Tier-1 states first)

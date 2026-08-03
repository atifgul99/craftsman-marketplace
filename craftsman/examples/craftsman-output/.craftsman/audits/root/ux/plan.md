# UX Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-ux · scope: root

Scope for THIS surface (from discovery): Next.js dashboard under `app/(dashboard)/`, Tailwind utility
classes, no design-token module, invoice list/form are the primary flows. Steps sourced from
craft-ux's `## Audit checklist`.

- [x] Discovery — token module, layout primitives, scanner (none) → `references/foundations.md`
- [x] Token adoption — raw palette/spacing vs tokens → `references/token-audit.md`
- [x] Visual fidelity vs scale → `references/layer-1-tokens.md`
- [x] State completeness — loading/empty/error on route subtrees → `references/layer-4-states.md`
- [x] Component patterns — forms labels/a11y, tables, nav → `references/layer-3-components.md`
- [x] AI-tells / anti-patterns sweep → `references/anti-patterns.md`
- [ ] Footer/legal furniture → `references/layer-3-components.md` (deferred — marketing pages thin)
- [ ] Motion audit → `references/layer-5-motion.md` (deferred — almost no motion present)
- [ ] Live multi-viewport pass → `references/live-audit.md` (deferred — static pass only this run)

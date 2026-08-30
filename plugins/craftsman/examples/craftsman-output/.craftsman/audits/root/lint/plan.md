# Lint Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-lint · scope: root

Scope for THIS surface (from discovery): TypeScript + Next/React, default or weak ESLint if any, no
typed-lint contract, no CI max-warnings gate. Steps sourced from craft-lint's `## Audit checklist`.

- [x] Map current lint/format tooling and config files → SKILL.md operating principle
- [x] Typed lint / type-aware rules where TypeScript is the language → `references/standard.md`
- [x] Zero-warning policy in CI (`--max-warnings 0`) → `references/standard.md`
- [x] Config is deliberate (not "eslint:recommended" only with no project rules) → `references/standard.md`
- [ ] Format-on-commit / shared Prettier-or-equivalent → `references/standard.md` (deferred — gate first)

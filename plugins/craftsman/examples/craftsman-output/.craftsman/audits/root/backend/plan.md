# Backend Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-backend · scope: root

Scope for THIS surface (from discovery): Next.js App Router route handlers under `app/api/`, Supabase
session helper in `lib/auth.ts`, no shared validation lib, no typed error envelope, mutations that
side-effect (email) inline. Steps sourced from craft-backend's `## Audit checklist`.

- [x] Map conventions — framework, validation (none), error envelope (none), auth helper → SKILL.md operating principle
- [x] Auth boundary rejects before handler body; tenant/principal from shared helper → `references/auth.md`
- [x] craft-security authz pass covers this scope's endpoints (do not re-audit authz here) → craft-security `authz.md`
- [x] Every external input schema-validated at the edge → `references/validation.md`
- [x] Handlers thin — no inline DB/business logic in route files → `references/api-design.md`
- [x] Error contract — one typed envelope, global mapping, no stack leaks → `references/error-contract.md`
- [x] Side-effects ordered and safe — after commit, idempotent or documented → `references/side-effects.md`
- [ ] Email bounce/complaint webhooks wired → `references/side-effects.md` (deferred — no provider webhooks in repo yet)
- [ ] Rate limiting middleware on abuse-prone routes → `references/api-design.md` (deferred — Tier-1 auth/error first)
- [ ] CORS middleware placement only → craft-security owns policy (N-A this pass — no CORS middleware found)

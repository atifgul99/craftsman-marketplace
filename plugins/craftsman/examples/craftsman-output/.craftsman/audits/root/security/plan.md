# Security Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-security · scope: root

Scope for THIS surface (from discovery): Supabase Auth wired but authZ unenforced; multi-tenant
invoice data; public API routes; no validation lib; secrets posture unconfirmed.
Surface this list as a live todo so the audit runs in steps and nothing is skipped. Steps sourced from
craft-security's `## Audit checklist`, tailored to discovery.

- [x] Map posture — auth lib (Supabase), env loading, headers, validation (none) → SKILL.md operating principle
- [x] Authorization enforced at the resource boundary? Hunt IDOR / tenant cross-access (incl. RLS) → `references/authz.md`
- [x] JWT verification — algorithm pinned, `alg:none` rejected, `exp`/`iss`/`aud` validated → `references/authz.md`
- [x] All input validated at the boundary; queries parameterized; no XSS/SSRF sinks → `references/input-output.md`
- [x] Trace every secret through a validated env schema; nothing client-exposed that shouldn't be → `references/secrets.md`
- [ ] Security headers (CSP/HSTS) + CORS deny-by-default → `references/headers-cors.md` (deferred — Tier-1 first)
- [ ] Dependencies pinned + scanner gating CI → `references/supply-chain.md` (deferred — no CI yet)

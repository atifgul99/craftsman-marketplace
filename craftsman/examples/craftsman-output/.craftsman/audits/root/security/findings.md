# Security Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-security · scope: root

## root-SEC-001 · severity 🔴 · status open
**What breaks (plain language):** Anyone logged in can open *any* customer's invoice — including other
businesses' — just by changing the number in the URL. Their private billing data leaks.
**Technical:** No per-resource authorization on `GET /api/invoices/:id` (IDOR / broken object-level
authZ). The handler fetches by id with no tenant scoping. `app/api/invoices/[id]/route.ts:12`.
**Fix:** Scope the query to the authenticated user's org and deny by default
(`where id = $1 and org_id = $2`). See craft-security → `authz.md`.
**Fingerprint:** `scope=root · domain=security · class=missing-authz · resource=GET /api/invoices/:id`
**Last-checked:** 2026-06-22 · a1bec8f

## root-SEC-002 · severity 🔴 · status open
**What breaks (plain language):** The only thing keeping one company's data separate from another's is
a check in the app code — and the database itself doesn't enforce it. One missed check anywhere (like
SEC-001) exposes everyone.
**Technical:** No row-level security on the `invoices` / `customers` tables; tenant isolation relies
entirely on application queries remembering to filter. `lib/db.ts:3` (raw client, no RLS confirmed).
**Fix:** Enable Postgres RLS with an org-scoped policy as defense-in-depth. **db owns the fix** — see
craft-db → `integrity.md`; this is the same defect as `root-DB-001` (rolled up under it in the tracker).
**Fingerprint:** `scope=root · domain=security · class=no-row-level-security · resource=invoices table`
**Last-checked:** 2026-06-22 · a1bec8f

## root-SEC-003 · severity 🟡 · status open
**What breaks (plain language):** The server trusts whatever the browser sends. A malformed or hostile
request body can write bad data or crash the handler — there's no gate at the door.
**Technical:** No schema validation on request bodies; `POST /api/invoices` reads `await req.json()`
and uses fields directly. `app/api/invoices/route.ts:14`. No `zod`/`valibot` in `package.json`.
**Fix:** Validate every request body with a schema at the boundary; reject on parse failure. See
craft-security → `input-output.md` and craft-backend → `validation.md`.
**Fingerprint:** `scope=root · domain=security · class=missing-input-validation · resource=POST /api/invoices`
**Last-checked:** 2026-06-22 · a1bec8f
**Fix-attempt:** 2026-06-24 · c3f0a2d · added a Zod schema for the request body

## root-SEC-004 · severity 🟡 · status open
**What breaks (plain language):** We can't confirm the database admin key isn't reachable from the
browser. If it is, anyone could read or wipe the whole database — not just their own data.
**Technical:** No `.env.example` and no validated env module; `SUPABASE_SERVICE_ROLE_KEY` usage not
traced to a server-only boundary. Unconfirmed = treat as exposed until proven otherwise.
`lib/db.ts` (env read raw from `process.env`).
**Fix:** Load secrets through a validated, server-only env schema; confirm the service-role key never
ships to the client bundle. See craft-security → `secrets.md`.
**Fingerprint:** `scope=root · domain=security · class=secret-exposure-risk · resource=SUPABASE_SERVICE_ROLE_KEY`
**Last-checked:** 2026-06-22 · a1bec8f

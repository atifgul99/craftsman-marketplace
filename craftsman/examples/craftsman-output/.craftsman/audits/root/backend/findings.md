# Backend Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-backend · scope: root

## root-BE-001 · severity 🟡 · status open
**What breaks (plain language):** When something goes wrong on the server, the client sometimes gets a
raw stack dump and sometimes an empty 500 — there's no consistent error shape. Debugging production
failures means guessing, and clients can't reliably show a useful message.
**Technical:** No shared error envelope or global mapper; handlers throw or `return Response.json(...)`
ad hoc. `app/api/invoices/route.ts:28` returns `{ error: err.message }` on catch; other routes return
bare `new Response(null, { status: 500 })`. Stack/internal details can leak.
**Fix:** One typed envelope (`{ code, message, requestId }`) plus a single mapper that converts known
exceptions to safe codes and never ships stack traces. See craft-backend → `error-contract.md`.
**Fingerprint:** `scope=root · domain=backend · class=no-error-envelope · resource=app/api handlers`
**Last-checked:** 2026-06-22 · a1bec8f

## root-BE-002 · severity 🔴 · status open
**What breaks (plain language):** At least one money-touching route never checks who is calling before
it runs — it skips the shared auth helper entirely. Anyone who can hit the URL can create or mutate
invoices without a session.
**Technical:** `POST /api/invoices` does not call `requireSession()` from `lib/auth.ts`; it proceeds
straight to `await req.json()` and the insert. `app/api/invoices/route.ts:8–18`. Other routes call the
helper inconsistently.
**Fix:** Require the shared auth helper at the top of every mutating and tenant-scoped handler; deny
before any DB work. See craft-backend → `auth.md` (authZ resource scoping is craft-security /
`root-SEC-001`).
**Fingerprint:** `scope=root · domain=backend · class=auth-helper-skipped · resource=POST /api/invoices`
**Last-checked:** 2026-06-22 · a1bec8f

## root-BE-003 · severity 🟡 · status open
**What breaks (plain language):** Sending the "invoice ready" email is fire-and-forget right after the
insert — if the request retries or the client double-submits, the customer can get the same email
twice (or none, if the process dies mid-send) with no way to tell.
**Technical:** After insert, `app/api/invoices/route.ts:34` calls `sendInvoiceEmail(...)` without an
idempotency key, outbox, or "sent" row. No job queue; failure is only `console.error`.
**Fix:** Record a durable outbox row (or provider idempotency key) in the same transaction as the
invoice insert; send from a worker/retry path. See craft-backend → `side-effects.md`.
**Fingerprint:** `scope=root · domain=backend · class=side-effect-no-idempotency · resource=sendInvoiceEmail`
**Last-checked:** 2026-06-22 · a1bec8f

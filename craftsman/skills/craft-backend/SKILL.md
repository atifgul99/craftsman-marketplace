---
name: craft-backend
description: >-
  The Craftsman standard for building and reviewing backend code — API routes/endpoints,
  rate-limiting middleware on routes, request validation, the authentication boundary,
  service/business logic, error handling, third-party integrations, and background jobs. Use this
  WHENEVER the work touches the server side in any form: adding or reviewing a route, validating
  input, authenticating a request, tracing a 500, writing a service layer, wiring an integration, or
  enqueueing or handling a job (job scheduling configuration → see craft-infra). Trigger even when
  the user only says "add an endpoint", "validate this input", "why is this returning 500", or
  "secure this route" without naming a framework. Owns in-app route rate-limit *middleware* (mount
  order, keying, 429); abuse-defense *policy* (login/brute-force) → craft-security; platform/edge
  capacity throttling → craft-infra; LLM spend/token limits on model routes → craft-ai. Authorization
  *policy* (per-resource authZ, IDOR/tenant scoping) and secrets belong to craft-security; DB schema
  and query specifics belong to craft-db — cross-reference them when the work crosses those boundaries.
---

# Backend Craft

This skill encodes one engineer's standard for building reliable, secure backend code, applied the
same way across every repo. The **method and opinions** live here; the **specifics** (which
framework, which ORM, which auth provider, which error envelope shape) are discovered from the
target repo — never hardcoded, never assumed.

## Operating principle — discover before you build

Every repo already has conventions. Spend two minutes reading what exists so you extend the patterns
rather than introduce a second style:

- `package.json` / lockfile → what framework is in use (Next.js API routes, Express, Fastify,
  NestJS, Hono)?
- Grep for an existing route handler, a validation call, and an error-response helper — understand
  the shape before adding to it.
- Grep for the auth layer (Clerk, NextAuth, JWT middleware, session cookie) and find where tenant or
  user context is resolved.
- Find the error-response helper or the established error envelope — every new route should return
  the same shape.

State what you found, then propose the smallest set of additions that fits cleanly into those
patterns.

## The request lifecycle (build in this order)

1. **Auth & context** — authenticate the caller and resolve tenant/user context before touching
   anything else. A request that isn't authenticated or can't be scoped to the right tenant must be
   rejected immediately, not after a DB round-trip. See `references/auth.md`. **`auth.md` owns
   authN/context only — authorization is a separate, blocking obligation (next paragraph).**

   > **Required-load gate (authZ is cross-domain).** `craft-backend` owns the request-lifecycle
   > plumbing; it does **not** own the authorization invariants. Any task that adds, secures, or
   > reviews an endpoint is **not complete** until you have loaded and applied **`craft-security`** →
   > `authz.md` (per-resource authZ, IDOR/tenant scoping, JWT verification, deny-by-default) and
   > **`craft-db`** → `access-patterns.md` (tenant-scoped query helper). These are mandatory at the
   > auth boundary, not optional cross-links — the single most expensive place to let a gap through.

2. **Validation** — schema-validate every external input (body, query, params, headers) at the
   boundary. Reject early with a clear error; never let unvalidated data reach business logic or the
   DB. See `references/validation.md`.

3. **Business logic** — keep handlers thin. Complex logic lives in a service or query layer, not
   inline in the route. Handlers orchestrate; they don't compute. See `references/api-design.md`.

4. **Error contract** — every error path returns the same typed envelope with a stable code, a
   human-readable message, and no stack traces or internal details visible to the client. See
   `references/error-contract.md`.

5. **Side-effects** — mutations (DB writes, emails, webhooks, queued jobs) happen inside
   transactions where ordering matters. Background jobs are enqueued after the DB commit, not before.
   Endpoints that trigger external calls are idempotent, or the reason they aren't is explicit and
   documented. See `references/side-effects.md`.

## Standing opinions (the non-negotiables)

These are the judgments that make output consistent across repos — apply them unless the user
overrides:

- **Validate every external input at the boundary with a schema.** "We trust the frontend" is not a
  security posture. Schema-first means bugs surface at the edge, not deep in a service.
- **Handlers are thin.** No inline DB queries in route files; no business logic that can't be tested
  without spinning up HTTP. One function per concern.
- **One consistent error envelope.** Typed codes, stable structure, no stack traces to clients.
  Clients — and the frontend team — rely on this contract; drift in the shape is a breaking change.
- **Auth and tenant-scoping live in a shared helper, called once.** Per-route copy-paste of auth
  checks is where gaps appear. A helper that's called at the top of every handler is a pattern that
  can be audited; scattered checks cannot.
- **Mutating endpoints are idempotent, or explicitly not.** Duplicate requests (network retries,
  client bugs) happen. Endpoints that aren't idempotent should document why and defend accordingly.

## Workflow

1. **Discover** the current conventions (above) and note the framework, validation lib, auth layer,
   and error envelope shape.
2. **Propose** additions ordered by the request lifecycle, smallest viable first.
3. **Implement** against the repo's existing patterns — match the file structure, the import style,
   the error helper, the auth call.
4. **Verify** — hit the endpoint: happy path returns the right shape; invalid input returns the
   correct error code and message; unauthenticated or wrong-tenant requests are rejected before any
   data is touched.

## Reference index

Read the one matching the current task — they hold the concrete patterns, not this overview:

- `references/api-design.md` — route structure, thin handlers, service/query layer conventions, rate limiting
- `references/auth.md` — authentication, tenant/principal resolution, the shared auth helper (authZ
  *policy* itself is mandatory-load from `craft-security` → `authz.md` — see the gate above)
  ⚠️ auth.md establishes a cross-load dependency on craft-security — always load together.
- `references/validation.md` — schema-first input validation, boundary enforcement, error messages, file upload validation
- `references/error-contract.md` — error envelope shape, typed codes, safe error serialization
- `references/side-effects.md` — transactions, idempotency, background job safety, recurring jobs, external calls
- For CORS middleware configuration, see `craft-security` → `headers-cors.md`.

## Audit checklist (for craft-audit)

When `craft-audit` plans a backend pass for a scope, it turns this checklist into the `plan.md`
todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor to what
discovery found: skip a step that genuinely doesn't apply with a one-line reason; never silently drop
one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission format"
(authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-BE-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-BE-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] Confirm the request enters through the established conventions — one framework, one validation
      lib, one error envelope, one shared auth helper; flag a second improvised style → SKILL.md
      "Operating principle — discover before you build"
- [ ] Check the auth boundary rejects before the handler body — unauthenticated or unscopable
      requests denied with no DB round-trip, tenant/principal resolved from a shared helper, not
      per-route copy-paste → `references/auth.md`
- [ ] Confirm the craft-security authz pass covers this scope's endpoints (the auth.md
      mandatory-load gate was applied) — do not re-audit authz here. → craft-security
      references/authz.md
- [ ] Confirm every external input (body, query, params, headers) is schema-validated at the edge —
      flag "we trust the frontend", coercion masquerading as validation, or unvalidated data reaching
      a service or the DB → `references/validation.md`
- [ ] Check handlers are thin — no inline DB queries or business logic in route files, logic lives in
      a service/query layer testable without HTTP; flag fat handlers → `references/api-design.md`
- [ ] Verify the error contract holds — one typed envelope with stable codes and safe messages, a
      global handler maps exceptions to it; flag drift in shape or stack traces/internals leaking to
      the client → `references/error-contract.md`
- [ ] Check side-effects are ordered and safe — jobs enqueued after commit not before, mutations in
      transactions where ordering matters, mutating endpoints idempotent (keys/outbox) or the gap
      documented; flag fire-before-commit and unsafe retries → `references/side-effects.md`
- [ ] Confirm the email/notification provider's bounce and complaint webhooks are wired and suppress
      future sends to hard-bounced or complaining addresses — flag a missing handler as a sender-
      reputation risk → `references/side-effects.md`
- [ ] Verify rate limiting is applied as middleware before handlers on routes with abuse potential —
      keyed on userId for authenticated routes (not IP-only), returns 429 + Retry-After; flag missing
      in-app middleware on payment and public-write endpoints. **Ownership (emit once):** BE = route
      middleware mechanism; SEC = login/brute-force/credential-stuffing *policy*; INFRA = platform/edge
      capacity throttling; AI = LLM cost/token limits on model-calling routes — do not triple-emit the
      same missing limiter → `references/api-design.md` Rate limiting
- [ ] Verify CORS middleware placement and framework wiring only — is CORS configured at the
      right layer (middleware/proxy) and does it apply to the routes that need it? Policy
      correctness (allowed origins, wildcard + credentials, preflight semantics) is audited by
      craft-security → `craft-security` references/headers-cors.md
- [ ] Incoming webhook payloads are verified with HMAC signature (e.g. Stripe-Signature, GitHub
      webhook secret) before processing — webhook routes skip user-session auth but are not
      unauthenticated → `references/auth.md`
- [ ] Request body size limit is set at the HTTP layer (not just per-field maxLength) so oversized
      payloads are rejected before buffering → `references/validation.md`


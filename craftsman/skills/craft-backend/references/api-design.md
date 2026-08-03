# API Design

A route handler is an **orchestrator**, not an actor. It receives a request, dispatches to a service
or query layer that owns the real work, and returns a typed response. When business logic bleeds into
handlers — inline DB calls, conditional chains, side-effect sequencing — every unit test requires an
HTTP shim and every refactor touches the wrong layer. **Handlers orchestrate; they do not compute.**
Keeping them thin is the discipline that keeps the service layer independently testable and the API
contract stable.

> **Scope split.** This file owns route structure, the handler/service/query-layer split, REST
> resource conventions, status codes, versioning, and the pagination contract. Input validation
> (schema, coercion, early rejection) belongs to `validation.md`; authentication and tenant resolution
> to `auth.md`; the typed error envelope to `error-contract.md`; transaction and side-effect
> sequencing to `side-effects.md`. DB schema design and the query functions the service layer calls
> are **`craft-db`**'s domain. The client consuming these routes — cache keys, refetch strategy,
> optimistic updates — is **`craft-frontend`** → `data-fetching.md`. Authorization logic (who may act
> on which object) is **`craft-security`** → `authz.md`.

---

## Contents

- [Thin handlers](#thin-handlers)
- [The service / query-layer split](#the-service--query-layer-split)
- [Route and resource shape](#route-and-resource-shape)
- [HTTP status codes](#http-status-codes)
- [Versioning](#versioning)
- [Pagination contract](#pagination-contract)
- [Testing without HTTP](#testing-without-http)
- [Rate limiting](#rate-limiting)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Thin handlers

A handler's job is exactly four things, in order:

1. **Resolve auth context** — call the shared helper that returns the authenticated principal and
   tenant scope. If it throws, the error propagates; the handler does nothing else. (`auth.md`)
2. **Validate input** — parse and coerce every external value (body, query, params, headers) at the
   boundary. (`validation.md`)
3. **Call the service layer** — pass validated, typed inputs; receive typed outputs. No branching
   logic, no DB calls, no formatting.
4. **Serialize the response** — map the service output to the correct HTTP status and the established
   response envelope (`error-contract.md`).

That's the entire surface of a handler. Here is the shape across common frameworks (discover the
actual one in the repo — this structure applies to Express, Fastify, and Hono; Next.js App Router
uses the Web `Request`/`Response` API with a different signature, and tRPC replaces the handler
model entirely with typed procedures):

```typescript
// e.g. Express / Fastify / Hono
export async function updateInvoice(req, res) {
  // 1. Auth
  const { userId, workspaceId } = await requireSession(req);

  // 2. Validate
  const input = InvoiceUpdateSchema.parse(req.body);     // throws on failure → caught by error middleware
  const { id } = InvoiceParamsSchema.parse(req.params);

  // 3. Service
  const invoice = await invoiceService.update({ id, workspaceId, input });

  // 4. Respond
  res.status(200).json({ data: invoice });
}

// Next.js App Router — Next.js 15+ makes params a Promise; pass the full awaited object to parse
// export async function PATCH(
//   request: Request,
//   { params }: { params: Promise<{ id: string }> }   // Next 15+: params is a Promise
// ) {
//   const { userId, workspaceId } = await requireSession(request);
//   const input = InvoiceUpdateSchema.parse(await request.json());
//   const { id } = InvoiceParamsSchema.parse(await params); // parse the full object, not just .id
//   const invoice = await invoiceService.update({ id, workspaceId, input });
//   return Response.json({ data: invoice });
// }
// For Next.js 14 (params is not a Promise): { params }: { params: { id: string } }
//   and const { id } = InvoiceParamsSchema.parse(params);
//
// tRPC: replace the handler with a typed procedure — no req/res at all; receives typed `input` and `ctx`.
```

What does NOT belong in the handler:
- Conditional business rules (`if (invoice.status === 'paid') throw …`) — move to the service layer.
- Direct DB calls (`db.invoice.findFirst(…)`) — move to a query function or repository.
- Email sends, webhook dispatches, job enqueuing — move to the service layer, behind the DB commit
  (`side-effects.md`).
- Response shaping logic that spans many fields or roles — move to a presenter/serializer the service
  returns.

If the handler is more than ~20-30 lines, the work has leaked into the wrong layer.

---

## The service / query-layer split

The service layer holds the business logic that cannot live in a handler. The query layer (sometimes
called a repository or data-access layer) holds the DB operations the service calls. The split:

```
handler  →  service  →  query functions / repository
(HTTP)      (logic)      (data access — craft-db)
```

**Service layer owns:**
- Business rules and invariants ("an invoice can't be voided after payment clears").
- Multi-step orchestration across query functions.
- Triggering side-effects in the correct order relative to DB commits (`side-effects.md`).
- Returning typed domain objects, not raw DB rows (transforming the persistence shape to the API
  shape belongs here).

**Query layer owns:**
- Constructing and running DB queries (e.g. Drizzle, Prisma, Kysely, raw SQL) — this is **`craft-db`**
  territory; reference it when crossing the boundary.
- Always scoped by `workspaceId`/`tenantId` from the session — never by a client-supplied value
  (`craft-security` → `authz.md`).
- No business logic, no HTTP dependencies. A query function takes typed arguments and returns typed
  results.

**Services are plain functions or classes — no framework imports.** This is the key: a service that
imports from `express` or `next/server` cannot be unit-tested without HTTP. Keep them framework-free
so tests call them directly with fabricated inputs (see [Testing without HTTP](#testing-without-http)).

```typescript
// query layer — craft-db territory
async function findInvoice({ id, workspaceId }: { id: string; workspaceId: string }) {
  return db.invoice.findFirst({ where: { id, workspaceId } });  // Prisma example — Drizzle/Kysely differ; scoped by session's tenant
}

// service layer — business logic
// NotFoundError and ConflictError are thin AppError subclasses that pin the HTTP status.
// They are defined once alongside AppError (see error-contract.md) and thrown here:
//   class NotFoundError extends AppError {
//     constructor(resource: string) { super(ErrorCode.NOT_FOUND, `${resource} not found`, 404); }
//   }
async function updateInvoice({ id, workspaceId, input }: UpdateInvoiceArgs) {
  const existing = await findInvoice({ id, workspaceId });
  if (!existing) throw new NotFoundError("invoice");   // → AppError, status 404
  if (existing.status === "paid") throw new ConflictError("Cannot edit a paid invoice"); // → AppError, status 409
  const updated = await updateInvoiceRecord({ id, input });
  await enqueueAuditLog({ action: "invoice.updated", workspaceId, resourceId: id }); // after commit
  return updated;
}
```

Discover the repo's existing split — look for a `services/`, `lib/`, or `domain/` directory. Extend
the pattern; don't introduce a second folder convention.

---

## Route and resource shape

REST resource URLs express nouns, not verbs:

```
/invoices              collection
/invoices/:id          single resource
/invoices/:id/items    sub-collection scoped to the parent
```

- **Plural nouns** for collections (`/invoices`, `/users`, not `/invoice`, `/getUser`).
- **Stable resource identifiers** in the URL — IDs, not mutable names or email addresses that
  break if the user changes them.
- **Verbs belong in the HTTP method**, not the URL path (`POST /invoices`, not `POST /createInvoice`).
  Exceptions are narrow: `POST /invoices/:id/void` is acceptable when the action has no clean
  resource mapping, but prefer making the state change a `PATCH` on the resource itself where
  possible.
- **Nested resources only as deep as the natural ownership chain.** `/workspaces/:w/invoices/:id`
  is fine; `/workspaces/:w/users/:u/projects/:p/tasks/:t/comments/:c` is a symptom — flat `/comments/:id`
  with a `taskId` filter is almost always cleaner.
- **Response envelope:** agree on a consistent shape for the repo and apply it everywhere. A common
  convention:

  ```json
  // single resource
  { "data": { ... } }

  // collection
  { "data": [ ... ], "meta": { "total": 42, "page": 1, "limit": 20 } }

  // error — see error-contract.md
  { "error": { "code": "INVOICE_NOT_FOUND", "message": "..." } }
  ```

  Discover the envelope shape already in use before establishing a new one — inconsistency across
  routes is a breaking change waiting to happen.

---

## HTTP status codes

Use the semantically correct code. Clients and middleware (retry logic, CDN caching, monitoring
alerting) make real decisions based on status codes.

| Scenario | Code |
| --- | --- |
| Successful read or update | `200 OK` |
| Successfully created a new resource | `201 Created` + `Location` header pointing to the resource |
| Accepted but processing asynchronously | `202 Accepted` |
| Successful deletion or update that returns no body | `204 No Content` |
| Validation error / malformed request | `400 Bad Request` |
| Unauthenticated — no valid session/token | `401 Unauthorized` |
| Authenticated but not allowed to perform the action | `403 Forbidden` |
| Resource not found (or intentionally obscured — see `authz.md`) | `404 Not Found` |
| Method not allowed on this resource | `405 Method Not Allowed` |
| Semantic conflict (duplicate, state machine violation) | `409 Conflict` |
| Unprocessable entity (valid JSON but business rule violation) | `422 Unprocessable Entity` |
| Rate limited | `429 Too Many Requests` + `Retry-After` header |
| Unexpected server error | `500 Internal Server Error` |
| Received an invalid or no response from an upstream service | `502 Bad Gateway` |
| This server is temporarily unavailable (overloaded, maintenance) | `503 Service Unavailable` |

Note: a `PUT` upsert should return `201` when the resource was created (with a `Location` header)
and `200`/`204` when it was updated. Do not collapse both outcomes under `204`.

Note: a DB-down or internal dependency failure is typically surfaced as `503` (this server cannot
serve the request) rather than `502` (this server received a bad response from an upstream it
proxies). Use `502` only when your service is itself acting as a gateway or proxy.

A few common wrong calls:
- Returning `200` with `{ "error": "..." }` in the body — clients can't branch on this reliably.
- Using `400` for every error including auth failures — `401` / `403` must be distinct so clients can
  redirect to login vs. show "you don't have access."
- Using `404` for "you can't access this resource" when you do *not* want to reveal existence — that's
  a deliberate choice that must be applied consistently (`craft-security` → `authz.md`).
- Returning `500` for a business-rule conflict — `409` or `422` is correct; `500` signals unexpected
  server failure, which changes how alerting and retries behave.

---

## Versioning

Version the API before you need to, not after the first breaking change. Common strategies — discover
which the repo already uses before adding one:

- **URL path prefix** (`/v1/invoices`, `/v2/invoices`): most explicit, easiest to route and test,
  widely understood. The practical default for most backends.
- **Request header** (`Accept: application/vnd.myapp.v2+json` or `X-API-Version: 2`): keeps URLs
  clean but requires header-aware routing and is less visible in logs.
- **No versioning in URLs, only additive changes**: works only while the API is under a single team's
  control and the contract with clients is tight. Falls apart the moment you need a non-additive
  change.

Regardless of strategy:
- **Additive changes are non-breaking**: new optional fields in responses, new optional query params,
  new endpoints. These don't need a version bump.
- **Non-additive changes need a new version**: removing fields, renaming fields, changing the type
  of a field, changing the semantics of a status code, changing pagination shape. The frontend team
  consuming these routes (`craft-frontend` → `data-fetching.md`) relies on the shape being stable.
- **Deprecate before removing.** Respond with `Sunset` (RFC 8594) and `Deprecation`
  (IETF draft-ietf-httpapi-deprecation-header) headers on the old version so consumers have a
  migration window. Don't kill a version the same release it's deprecated.

---

## Pagination contract

Unbounded collection responses are a latency, memory, and cost problem. Every collection endpoint
that may grow beyond a handful of records must be paginated.

**Offset pagination** (`?page=2&limit=20`) — simple, works for sorted lists where items don't move
between pages. Has a well-known issue: items added/deleted between page loads shift results, causing
duplicates or gaps. Fine for most admin/back-office use cases; problematic for real-time feeds.

**Cursor pagination** (`?after=<cursor>&limit=20`) — cursor encodes the position in the ordered
result set (typically a base64-encoded last-seen id or timestamp — readable by clients; sign or
encrypt the cursor if exposing internal IDs or timestamps is a concern). Stable under concurrent
writes; required for infinite-scroll feeds or any list where consistency matters.

Pick one and apply it consistently across the API. Mixing conventions in the same product doubles
the surface the frontend team (`craft-frontend` → `data-fetching.md`) must implement.

Standard response shape for a paginated collection:

```json
{
  "data": [ ... ],
  "meta": {
    "total": 142,
    "limit": 20,
    "page": 3,
    "hasNext": true,
    "hasPrev": true
  }
}
```

For cursor-based:

```json
{
  "data": [ ... ],
  "meta": {
    "limit": 20,
    "nextCursor": "eyJpZCI6IjEyMyJ9",
    "prevCursor": null,
    "hasNext": true
  }
}
```

- **Always enforce a maximum `limit`.** Cap the value server-side and either return it silently
  (simpler client experience) or return a `400` explaining the maximum (makes the contract explicit).
  Pick one and document it in `validation.md`; the key invariant is that unbounded results are never
  returned.
- **`total` can be expensive on large tables without a covering index.** A full sequential
  `COUNT(*)` with complex predicates can dominate query time. Profile before assuming; consider
  returning an estimated count (`pg_class.reltuples` on Postgres) or omitting it entirely from
  cursor-paginated responses where it's semantically meaningless.
- **Default sort order must be stable.** Pagination is undefined without a deterministic sort. A
  multi-column sort with a tiebreaker on `id` is the safe default.

---

## Testing without HTTP

The reason to keep services framework-free is that they become trivially testable without spinning
up a server. The test calls the service function directly:

```typescript
// Pure service test — no HTTP, no server
it("rejects update on a paid invoice", async () => {
  const existing = makeInvoice({ status: "paid" });
  // stub findInvoice to return 'existing'
  // vi.mocked (Vitest) / jest.mocked or jest.spyOn (Jest) / sinon.stub — use your repo's test runner
  vi.mocked(findInvoice).mockResolvedValue(existing); // Vitest — replace vi with jest if using Jest

  await expect(
    invoiceService.update({ id: existing.id, workspaceId: "ws_1", input: { amount: 500 } })
  ).rejects.toThrow(ConflictError);
});
```

Handler-level tests (integration / e2e) test the HTTP plumbing: correct status codes, correct
envelope shape, auth rejection. They don't duplicate the business-logic cases — that coverage is
already in service tests.

The division:
- **Service tests** — happy path + every business rule + every error code. Fast, pure, no HTTP.
- **Handler tests** — one or two per handler: correct `2xx` on the happy path + correct status on
  auth failure + correct `400` on invalid input. Confirm the plumbing; trust the service tests for
  logic.
- **E2E / API contract tests** — run against a real or near-real server; cover critical flows
  end-to-end, not exhaustive logic branches.

This split keeps the suite fast and failures meaningful: a `500` in a handler test points to
plumbing; a business-rule failure surfaces in the service test first.

---

## Rate limiting

Rate limiting belongs in middleware, executed before the handler body — not inside the handler's business logic or the service layer. Ordering is two-tier, because a coarse limiter and a precise limiter key on different things:

1. **Tier 1 — coarse, pre-auth, IP-keyed.** Runs first, before auth context is resolved. It's cheap (no session lookup) and exists only to blunt floods and obviously abusive traffic before spending any compute on auth. Wide limits — this tier is not trying to be precise per-user.
2. **Tier 2 — precise, post-auth, `userId`-keyed.** Runs immediately after the shared auth helper resolves the session, but still before the handler body executes any logic. This is the primary limit: IP-only keying is insufficient here because a single user behind a NAT can saturate the limit for others, and a distributed attacker can rotate IPs to evade it.

**Key strategy:**
- **Authenticated routes:** key on `userId` from the verified session (resolved in the shared auth helper, post-auth tier). Optionally back it with a coarse pre-auth IP tier as described above.
- **Unauthenticated routes** (public endpoints, pre-auth paths): key on IP, optionally combined with a fingerprint — there is no post-auth tier for these.
- **Webhook ingress:** key on the source identifier if known (e.g. Stripe's account id embedded in the signature payload), otherwise IP.

**Scope note (rate-limit ownership — emit under one domain only):**
- **This skill (BE):** in-app route middleware mechanism (mount order, keying, 429 + Retry-After).
- **craft-security:** abuse-defense *policy* — login throttling, brute-force, credential stuffing, lockout (`authz.md`).
- **craft-infra:** platform/edge capacity throttling — gateway, CDN, shared/edge-KV counters (`scale-resilience.md`).
- **craft-ai:** LLM spend/cost limits (rate + `max_tokens` + loop bounds) on model-calling routes (`keys-and-spend.md`); the underlying middleware mechanism may still be BE.

**Algorithm:** prefer token-bucket or sliding-window over fixed-window. Fixed-window allows a burst of 2× the limit straddling a window boundary. Both token-bucket and sliding-window smooth bursts without that edge case.

**Concrete library options — discover which runtime the repo targets:**

```typescript
// @upstash/ratelimit — Edge/serverless (Cloudflare Workers, Vercel Edge, Next.js middleware)
// Requires an Upstash Redis instance; state is shared across instances automatically.
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, "1 m"), // 100 req/min per key
});

// In Next.js middleware or an Edge route handler:
const identifier = userId ?? ip; // prefer userId once auth is resolved
const { success, limit, remaining, reset } = await ratelimit.limit(identifier);
if (!success) {
  return new Response(
    JSON.stringify({ error: { code: "RATE_LIMITED", message: "Too many requests", status: 429 } }),
    { status: 429, headers: { "Retry-After": String(Math.ceil((reset - Date.now()) / 1000)) } }
  );
}
```

```typescript
// express-rate-limit — Express, Fastify (via compatibility layer), or any Node http server
import rateLimit from "express-rate-limit";

// Tier 1 — coarse, pre-auth, IP-keyed. Mounted globally, before auth resolves any session.
const ipLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 300,                 // wide limit — just blunting floods, not precise per-user
  keyGenerator: (req) => req.ip,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: { code: "RATE_LIMITED", message: "Too many requests", status: 429 } },
});

// Tier 2 — precise, post-auth, userId-keyed. Mounted after auth, so req.user is populated.
const userLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 100,
  keyGenerator: (req) => req.user?.id ?? req.ip,  // falls back to IP if auth didn't attach a user
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: { code: "RATE_LIMITED", message: "Too many requests", status: 429 } },
});

app.use(ipLimiter);   // tier 1: runs for every request, before auth
app.use(auth);        // resolves req.user
app.use(userLimiter); // tier 2: runs after auth, keyed on the resolved user
```

```typescript
// Hono — built-in rate limiting middleware
import { rateLimiter } from "hono-rate-limiter";

app.use(
  rateLimiter({
    windowMs: 60 * 1000,
    limit: 100,
    keyGenerator: (c) => c.get("userId") ?? c.req.header("x-forwarded-for") ?? "unknown",
    // Store: defaults to in-memory (single instance only). For multi-instance, use
    // an adapter (Redis, Cloudflare KV) from the hono-rate-limiter ecosystem.
  })
);
```

Always return `429 Too Many Requests` with a `Retry-After` header (seconds until the window resets) and the standard typed envelope. Do not return `400` or `503` for rate-limit rejections — `429` is the unambiguous signal that retry logic and client code can act on.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Inline DB query (`db.*.findFirst(…)`) inside a route handler | Move to a query function; handler calls the service |
| Business-rule conditional inside a route handler | Move to the service layer; handler only dispatches |
| Service imports from the HTTP layer (any framework module — e.g. `express`, `fastify`, `hono`, `next/server`) | Remove the import; services must be framework-free |
| Collection endpoint with no pagination | Add `limit`/`page` or cursor params; enforce a maximum |
| No `limit` cap — client can request unbounded result sets | Server-side cap; document in `validation.md` |
| Pagination shape differs between collection routes | Standardize on one envelope; pick offset or cursor per API surface |
| `200 OK` returned with an `{ "error": … }` body | Return the correct `4xx`/`5xx` status code |
| `400` returned for an auth failure | `401` (unauthenticated) or `403` (unauthorized) — these must be distinct |
| `500` returned for a business-rule conflict or known domain error | `409` / `422`; `500` is for unexpected server failures only |
| `POST /createInvoice` URL | `POST /invoices` — verbs in the method, nouns in the URL |
| Deeply nested route beyond the natural ownership chain | Flatten; carry parent id as a query param or top-level field |
| Breaking change (field renamed/removed) on an existing version | New API version or additive-only change; notify consumers + add `Deprecation` header |
| New route with no unit tests on the service layer | Service tests required for every business rule; handler test covers plumbing |
| Handler over ~30 lines of logic | Logic has leaked in — extract to the service layer |

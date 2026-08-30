# Error Contract

Every API error that reaches a client is a contract the frontend team depends on — it must have a stable shape, a machine-readable code, and a human message, and it must never expose stack traces, ORM errors, or internal identifiers. **One consistent typed error envelope: a stable `code`, a human `message`, and nothing more.** The failure mode of skipping this is a frontend that `switch`es on HTTP status alone and breaks the moment you add nuance, or worse, an unhandled exception that leaks a full stack trace with file paths and dependency versions to anyone who reads the network tab.

> **Scope split.** This file owns the *shape and mapping* of error envelopes: the typed code registry, the exception-to-envelope mapping, status-code discipline, and what is safe to serialize. Capturing the *internal detail* that cannot go to clients — stack traces, DB error messages, upstream API failures — belongs to **`craft-observability`** → `sentry.md` and `logging.md`; log and report there, then return the safe envelope here. Input that never should have reached the handler in the first place belongs to `validation.md`; the route structure that wraps these patterns is in `api-design.md`. The client decoding these codes and reacting to them is covered in **`craft-frontend`** → `data-fetching.md`. IDOR and authorization status-code conventions (the 403-vs-404 choice for resources hidden from a given user) are deferred to **`craft-security`** → `authz.md`.

---

## Contents

- [The envelope shape](#the-envelope-shape)
- [The error code registry](#the-error-code-registry)
- [Status-code discipline](#status-code-discipline)
- [Mapping exceptions to envelopes](#mapping-exceptions-to-envelopes)
- [The global error handler](#the-global-error-handler)
- [What must not reach the client](#what-must-not-reach-the-client)
- [Validation errors](#validation-errors)
- [Quick-reject checklist](#quick-reject-checklist)

---

## The envelope shape

Pick one shape and never deviate. The frontend imports the type and `switch`es on `code` — any variation in shape is a breaking change.

```ts
// Canonical envelope — define this once, export it, import everywhere
export interface ApiError {
  code: string;       // stable machine-readable string e.g. "INVOICE_NOT_FOUND"
  message: string;    // human-readable, safe to display
  status: number;     // mirrors the HTTP status; convenient for client switch/match
  details?: ValidationIssue[];  // optional, only for validation errors (field-level messages)
                                // never a stack trace, never an ORM error string
                                // consumers: import ValidationIssue from the same module; the type is
                                // only populated for VALIDATION_FAILED — all other codes omit details
}
```

The response body is always `{ error: ApiError }` on failure — never a bare string, never a bare `{ message }` on some routes and a different shape on others. The HTTP status code and the envelope travel together; neither replaces the other. Clients should primarily branch on `error.code` because it carries intent; the status code provides the coarse HTTP contract for middleware and load-balancer health checks.

Discover the repo's existing envelope before introducing one. If a shape already exists, extend it. A second shape is worse than an imperfect first one.

---

## The error code registry

Codes are the part of the contract the frontend can check against at compile time (if you export the union) and `switch` on at runtime without parsing a string message.

Rules:
- **SCREAMING_SNAKE_CASE**, namespaced by domain: `INVOICE_NOT_FOUND`, `AUTH_TOKEN_EXPIRED`, `PAYMENT_INSUFFICIENT_FUNDS`.
- **Codes are additive, never renamed.** Renaming a code that client code already handles is a breaking change. Add a new code; deprecate the old one slowly if needed.
- **One code per distinct recoverable state the client should handle differently.** Don't invent `INVOICE_ERROR` as a catch-all — the client can't do anything useful with it. Do invent `INVOICE_NOT_FOUND` vs `INVOICE_ALREADY_PAID` if the UI reacts differently to each.
- **Keep a canonical list in one place** — a TypeScript union, an enum, or a plain constant object. That file is the contract; it should be reviewable in one screen.

```ts
// Example registry — discover or create the canonical location in the repo
export const ErrorCode = {
  // Auth
  AUTH_MISSING:            "AUTH_MISSING",
  AUTH_TOKEN_EXPIRED:      "AUTH_TOKEN_EXPIRED",
  AUTH_FORBIDDEN:          "AUTH_FORBIDDEN",

  // Resources
  NOT_FOUND:               "NOT_FOUND",
  CONFLICT:                "CONFLICT",

  // Input
  VALIDATION_FAILED:       "VALIDATION_FAILED",

  // Integrations / external
  UPSTREAM_UNAVAILABLE:    "UPSTREAM_UNAVAILABLE",

  // Catch-all for genuinely unexpected paths
  INTERNAL_ERROR:          "INTERNAL_ERROR",
} as const;

export type ErrorCode = (typeof ErrorCode)[keyof typeof ErrorCode];
```

`INTERNAL_ERROR` is the *only* catch-all, and it must be paired with internal logging — never with a revealing message.

---

## Status-code discipline

HTTP status codes are not arbitrary. The four-number prefix has meaning to every layer between your server and the client: CDN cache policies, retry logic, monitoring dashboards, and the frontend's error handler all branch on it. Use the semantics, not convenience.

| Situation | Status | Notes |
| --- | --- | --- |
| Unauthenticated — no valid session/token | `401` | Instructs the client to re-authenticate |
| Authenticated but not allowed | `403` | Do not return `401` for authZ failures — the client shouldn't loop back to login |
| Resource doesn't exist (or isn't visible to this user — see IDOR) | `404` | Returning `403` when "not found" leaks existence; pick a convention per `craft-security` → `authz.md` |
| Request body / query params invalid | `400` | Always paired with `VALIDATION_FAILED` and `details` |
| State conflict (duplicate, already-paid, version mismatch) | `409` | Not `400` — the input was well-formed; the *state* is wrong |
| Unhandled / unexpected server error | `500` | Safe envelope only; all detail goes to the logger |
| This service is temporarily unavailable (DB-down, overloaded, maintenance) | `503` | Include a `Retry-After` header (seconds or HTTP-date) to signal when the service expects to recover — without it, clients must guess a back-off interval |
| Received an invalid or missing response from an upstream while proxying | `502` | Use only when this service is itself acting as a gateway or proxy; `503` implies the fault is local, `502` implies it came from upstream |
| Resource created | `201` | Not `200` for mutations that produce a new entity. A `201` response should include a `Location` header with the URL of the new resource (e.g., `/invoices/42`); omitting it is valid but limits client usability |
| Mutation succeeded, no body | `204` | Not `200` with an empty body |

Do not return `200` with `{ success: false }` — that defeats HTTP semantics and breaks any middleware that branches on status. Return the semantically correct status *and* the typed envelope.

---

## Mapping exceptions to envelopes

Handlers should never `catch` an exception and forward it raw. The **global error handler / error middleware** catches, classifies, logs the internal detail, and returns the safe envelope. Per-handler `try/catch` is reserved only for cases where the handler must act before re-throwing (e.g. rolling back a transaction) — not for formatting the response.

A practical classification layer (framework-agnostic — adapt the shape to Express middleware, Next.js route handlers, Fastify error hooks, Hono `app.onError`, NestJS exception filters, etc.):

```ts
// 1. A typed application error that can carry a code + status
export class AppError extends Error {
  constructor(
    public readonly code: ErrorCode,
    public readonly message: string,
    public readonly status: number, // no default — always pass explicitly; the 400 default tempts
                                    // callers to omit it for non-validation codes (e.g. NOT_FOUND)
                                    // and silently produce the wrong HTTP status
    public readonly details?: ValidationIssue[],
  ) {
    super(message);
    // Required for correct instanceof checks when compiling to ES5; safe to keep in ES2015+ targets.
    Object.setPrototypeOf(this, new.target.prototype);
    this.name = "AppError";
  }
}

// 2. Throwing in a service layer
export function requireInvoice(invoice: Invoice | null) {
  if (!invoice) throw new AppError(ErrorCode.NOT_FOUND, "Invoice not found", 404);
}

// 3. The catch block in a handler or error middleware
// This is a classification utility, not a drop-in handler. Call it from within your framework's
// actual error hook and then apply its return value — for example in Express:
//   const { status, body } = handleError(err); res.status(status).json(body);
function handleError(err: unknown): { status: number; body: { error: ApiError } } {
  if (err instanceof AppError) {
    // AppErrors are expected — log at info/warn, return the envelope
    logger.warn({ code: err.code, message: err.message }, "app error");
    return {
      status: err.status,
      body: { error: { code: err.code, message: err.message, status: err.status, details: err.details } },
    };
  }

  // Unexpected — log the full stack internally, return only the safe envelope
  logger.error({ err }, "unhandled error");
  return {
    status: 500,
    body: { error: { code: ErrorCode.INTERNAL_ERROR, message: "An unexpected error occurred", status: 500 } },
  };
}
```

The split is intentional: `AppError` is a first-class domain concept — it carries a code and a safe message you authored. Everything else — ORM exceptions (`PrismaClientKnownRequestError`, TypeORM errors, raw `pg` errors), third-party SDK throws, network timeouts — is unexpected and falls through to the catch-all path where only the safe envelope is returned and the full internal error goes to the logger/error tracker.

---

## The global error handler

Handlers that individually `try/catch` every operation and format their own errors produce drift. The right pattern is a **single error handler** registered at the framework level — once — that receives every uncaught exception and applies the mapping above. Each framework has its own mechanism:

The following are illustrative examples — this list is non-exhaustive; discover the framework's own error-hook mechanism from the repo rather than assuming it matches one of these:

- **Express:** a four-argument error middleware `(err, req, res, next) => { … }` registered after all routes.
- **Koa:** a root-level `async (ctx, next)` middleware that wraps `await next()` in a try/catch and sets `ctx.status` / `ctx.body` on the caught error, plus `app.on('error', (err, ctx) => { … })` for errors that escape all middleware.
- **Fastify:** `fastify.setErrorHandler(fn)`.
- **Next.js App Router:** a top-level `error.tsx` boundary for rendering errors; for route handlers, a thin `withErrorHandling(handler)` wrapper function is a common user-land approach — Next.js App Router has no built-in global error handler for route handlers, making per-handler wrapping or a shared utility necessary.
- **Hono:** `app.onError(fn)`.
- **NestJS:** a global `ExceptionFilter` registered via `app.useGlobalFilters(…)`.

Discover which framework the repo uses and register one global handler there. Route-level `try/catch` is then reserved for cases where the handler needs to *act* on the error (e.g. roll back a transaction) before re-throwing — not for formatting the response.

---

## What must not reach the client

These things are never in the error response body:

- **Stack traces.** File paths, line numbers, and function names expose the internal structure of your codebase.
- **ORM / database error messages.** `duplicate key value violates unique constraint "invoices_pkey"` tells an attacker your table name, constraint name, and DB dialect.
- **SQL strings.** Never, under any circumstances.
- **Third-party API error bodies.** An upstream error from Stripe, Twilio, or any vendor may include internal keys, request ids, or rate-limit metadata you don't want clients to see.
- **Internal identifiers.** Correlation ids / trace ids *can* be safe to expose if they don't reveal structure — but confirm before doing so. A request id that maps 1:1 to a log line is useful for support; a DB row id for an internal audit record is not.
- **Upstream `error.message` passed through verbatim.** Even your own service-layer errors may contain details authored for developers, not users.

All of that detail is *valuable* — it belongs in your log event and error tracker (see **`craft-observability`** → `logging.md` and `sentry.md`), never in the HTTP response.

---

## Validation errors

Validation failures (malformed request body, missing required field, invalid enum value) get the `400` / `VALIDATION_FAILED` treatment with one addition: a `details` array that tells the client *which field* failed and *why*. Without `details`, the client shows a generic error; with it, the client can highlight the right field.

```ts
// A single failed field entry
interface ValidationIssue {
  field: string;   // dot-path: "address.postalCode", "items[0].quantity"
  message: string; // human-readable: "Must be a positive integer"
  code?: string;   // optional machine code: "TOO_SMALL", "INVALID_FORMAT"
}

// The envelope for a validation failure
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "status": 400,
    "details": [
      { "field": "amount", "message": "Must be a positive number" },
      { "field": "currency", "message": "Must be a 3-letter ISO code" }
    ]
  }
}
```

Most validation libraries (Zod, Valibot, Yup, Joi, Arktype) produce their own error structures. Write one adapter per library that converts its native issue format into `ValidationIssue[]` — then throw an `AppError` carrying that array as `details`. The adapter lives in one place; the envelope shape stays identical regardless of which library produced the failure.

**Path serialization note:** Zod and Valibot represent field paths as arrays (e.g., `["items", 0, "quantity"]`), not dot-notation strings. Your adapter must serialize these to the dot-path convention: `path.reduce((acc, seg) => typeof seg === "number" ? \`${acc}[${seg}]\` : \`${acc}${acc ? "." : ""}${seg}\`, "")`. A developer following this doc will be surprised if they pass `issue.path` directly — it won't match the advertised format.

This is the only case where `details` is populated. `details` on a `NOT_FOUND` or `INTERNAL_ERROR` is a red flag.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| `res.json(err)` or `res.json({ error: err.message })` forwarding a raw exception | Catch, classify, log internal detail, return only the safe envelope |
| Stack trace visible in the response body | Remove; send to logger / error tracker (`craft-observability` → `sentry.md`) |
| ORM error message (`PrismaClientKnownRequestError`, etc.) forwarded to client | Catch before it reaches the handler; return `INTERNAL_ERROR` + log the original |
| `{ success: false }` on a `200` | Return the semantically correct HTTP status + typed envelope |
| `404` returned for an auth failure | `401` for missing/invalid auth, `403` for forbidden — but `404` is also acceptable when the API intentionally obscures resource existence per the security convention (`craft-security` → `authz.md`); apply that convention consistently across the API |
| `400` returned for a state conflict (duplicate, version mismatch) | Use `409 CONFLICT` with a domain-specific code |
| Free-text `code` strings like `"error"`, `"failed"`, `"unknown"` | Use the code registry; pick a specific, stable code |
| Different error shapes on different routes (`{ message }` vs `{ error: { code } }`) | Centralize in the global handler; all routes return `{ error: ApiError }` |
| `try/catch` in each handler formatting its own response | Register one global error handler; per-handler catch only for pre-throw cleanup |
| `VALIDATION_FAILED` with no `details` | Include per-field issues so the client can surface the failing field |
| `details` populated on a non-validation error (`NOT_FOUND`, `INTERNAL_ERROR`) | `details` is for field-level validation only; strip it from other codes |
| New error scenario, no entry in the code registry | Add a typed constant to the registry; never inline a raw string |

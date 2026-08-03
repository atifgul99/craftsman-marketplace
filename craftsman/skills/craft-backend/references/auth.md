# Authentication & Request Context

Every handler has the same first obligation: establish *who is calling* and *on whose behalf*, then make those facts available as a typed object before any business logic runs. **Resolve the authenticated principal and tenant context once, in a shared helper, called at the top of every handler — never inline, never deferred.** A request that can't be authenticated or can't be scoped to a tenant must be rejected immediately, not after a DB round-trip or halfway through a mutation.

> **Scope split.** This file owns **request-lifecycle authN mechanics**: invoking and wiring credential/token verification (calling the library/SDK in the shared helper), extracting and typing the principal, resolving tenant/workspace context, and structuring the helper every handler calls. It does **not** own the *security criteria* that verification must meet (pin the algorithm, reject `alg:none`, check `exp`/`iss`/`aud` — JWT verification depth), per-resource authorization, IDOR/tenant-scoping in queries, or RBAC/ABAC policy — all of that is the security standard and lives in **`craft-security`** → `authz.md`. In short: **this file wires the verification; `authz.md` defines what correct verification requires.** The signing key/session secret itself (where it lives, how it rotates, how it's loaded) belongs to **`craft-security`** → `secrets.md`.
>
> **See also:** `validation.md` (validate the principal's *input* after you have the context, not before) · `api-design.md` (how the context object flows through thin handlers into the service layer) · **`craft-db`** → `access-patterns.md` (tenant-scoped query patterns that consume the context this file produces).

---

## Contents

- [Authorization is not in this file — and it is blocking](#authorization-is-not-in-this-file--and-it-is-blocking)
- [The context object](#the-context-object)
- [The shared helper](#the-shared-helper)
- [Credential types and where to find them](#credential-types-and-where-to-find-them)
- [Tenant resolution](#tenant-resolution)
- [Failing fast — reject before the handler body](#failing-fast--reject-before-the-handler-body)
- [Provider SDKs vs hand-rolled extraction](#provider-sdks-vs-hand-rolled-extraction)
- [Edge and middleware placement](#edge-and-middleware-placement)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Authorization is not in this file — and it is blocking

This file produces a trusted principal + tenant context. That is **authentication**. It is necessary
but **never sufficient** to touch a specific record. The authorization invariants below live in full
in **`craft-security`** → `authz.md` and **`craft-db`** → `access-patterns.md` — and because a task
that secures or adds an endpoint can trigger `craft-backend` alone, **load those two before treating
any auth/endpoint work as done.** This is a required step, not an advisory link. Until you've applied
them, the endpoint is not secure no matter how clean the authN helper is:

- [ ] **Deny by default.** A handler that can't *prove* the principal is entitled refuses. New
      endpoints/fields/actions start with no access and earn it explicitly.
- [ ] **Authorize per resource, every request.** `isAuthenticated` (or a coarse role) is not
      authorization. Check that *this* principal may perform *this* action on *this* object, against
      the loaded record — in the handler, not just in middleware. → `craft-security` → `authz.md`.
- [ ] **Scope every tenant query (IDOR/BOLA defense).** Every read/write of a tenant-owned table
      filters by the `tenantId` from this file's context — enforced in a shared query helper, never
      from a body/param id. A missing scope is a cross-tenant data leak. → `craft-db` →
      `access-patterns.md`.
- [ ] **Verify the token, don't just decode it.** Signature, `exp`, issuer/audience checked with a
      vetted library; claims treated as untrusted input until verified. → `craft-security` →
      `authz.md`.

The rest of this file is the authN plumbing those checks depend on.

## The context object

Every handler needs a single, typed value that answers two questions without any further work:

1. **Who is the authenticated user** — a stable server-assigned `userId` (not the raw token, not an email, not a name).
2. **Which tenant/workspace they're operating in** — a stable `tenantId` / `workspaceId` / `orgId` that comes from the *session or token*, never from the request body.

Define a type for it and export it so callers get autocomplete and refactors are safe. The shape is deliberately minimal — downstream layers look up rich profile data from the DB rather than carrying a fat object through every function:

```ts
// Example shape — discover the conventions in the repo (field names, nullability, extra claims)
type RequestContext = {
  userId: string;
  tenantId: string;
  roles?: string[];   // include only if the auth layer provides them reliably
};
```

What the context object is **not**:
- It is not the raw token or session cookie — don't pass those downstream.
- It is not the full user record from the DB — load that in the handler if needed, scoped by `userId`.
- It is not a JWT payload object — extract and map only the fields you trust and name explicitly.

---

## The shared helper

Write one function — `getRequestContext`, `requireAuth`, `getAuth`, whatever name fits the repo — that every handler calls at its opening line. Its contract:

1. Extract the credential from the request (cookie, `Authorization` header, API-key header — whichever the repo uses).
2. Verify it (signature, expiry, issuer — the full verification rules are in **`craft-security`** → `authz.md`; implement them here, don't skip them).
3. Map the verified claims to the typed `RequestContext`.
4. Resolve tenant context (see below).
5. **Throw / return an error immediately** if any step fails. Do not return a nullable context that callers might forget to check.

```ts
// Example — Next.js App Router style; adapt to the framework in the repo
// (Express/Fastify would pass req/res; Hono uses c.get; NestJS uses guards)
async function getRequestContext(req: Request): Promise<RequestContext> {
  // RFC 7235: auth-scheme is case-insensitive ("Bearer", "bearer", "BEARER" are all valid).
  // Use a case-insensitive regex rather than startsWith("Bearer "), which rejects valid variants.
  const authHeader = req.headers.get("authorization");
  const token = authHeader?.match(/^Bearer\s+(.+)$/i)?.[1] ?? null;
  if (!token) throw new AuthError(401, "missing_credentials");

  // Extend JWTPayload to avoid `any` — add whichever custom claims your auth layer signs
  interface AppJWTPayload extends JWTPayload { roles?: string[] }
  const payload = await verifyToken(token) as AppJWTPayload;  // throws on invalid sig, exp, iss, or aud — see craft-security → authz.md for the full checklist
  if (!payload.sub) throw new AuthError(401, "missing_subject");
  const tenantId = await resolveTenant(payload);  // throws if user has no tenant

  return { userId: payload.sub, tenantId, roles: payload.roles ?? [] };
}

// In every handler:
export async function GET(req: Request) {
  const ctx = await getRequestContext(req);  // ← first line, always
  // ctx.userId and ctx.tenantId are now trusted facts
  // ...
}
```

The helper is the only place that touches raw token data. When the auth provider or token shape changes, one file changes, not every handler. A grep for `getRequestContext` produces the full audit surface; a grep for `req.headers.get("authorization")` in handler files is a flag.

---

## Credential types and where to find them

Discover the auth mechanism by reading the repo — don't assume. Common patterns:

| Mechanism | What to look for | Extraction point |
| --- | --- | --- |
| **Session cookie (httpOnly) — stateful** | `express-session` + store adapter (e.g. `connect-pg-simple`), next-auth database sessions | Server-side session store lookup via cookie value |
| **Session cookie (httpOnly) — stateless** | `iron-session`, `better-auth` (sealed-cookie mode) | Encrypted cookie (stateless) — decrypt and deserialize the cookie value directly; no server-side store lookup |
| **Raw cookie parsing (Express)** | `cookie-parser` | Parses raw cookies into `req.cookies` only — pairs with a session library (`express-session`, `iron-session`) that provides the actual store lookup or decryption |
| **Bearer JWT** | `Authorization: Bearer <token>` header; libraries: `jose`, `jsonwebtoken`, provider SDK | `Authorization` header; verify with the signing key from the secret store |
| **Auth provider SDK** | Clerk (`auth()`, `getAuth()`); NextAuth v4 (`getServerSession()`); Auth.js v5 / next-auth@5 (`auth()` — same call pattern as Clerk but scoped to the Auth.js config export; detect version by checking `next-auth` in `package.json` and looking for the v5 `auth` export pattern); Supabase (`createServerClient(...).auth.getUser()`) | Provider helper — prefer it over hand-rolling extraction |
| **API key** | Custom header (`X-API-Key`, `Authorization: ApiKey <key>`) | Header; look up in DB to resolve the associated user/tenant |
| **mTLS / service-to-service** | Certificate identity in `req.socket.getPeerCertificate()` | Platform/proxy-level; peer cert maps to a service principal |

For API keys specifically: the key itself is a lookup token, not a self-contained credential. The handler calls the helper; the helper looks up the key in the DB and resolves `userId` + `tenantId` from that row. The flow is identical from the handler's perspective — it always gets back the same `RequestContext` shape.

The signing key for JWT verification lives outside the codebase. See **`craft-security`** → `secrets.md` for where it's loaded from and how. Never hardcode it; never commit it; verify you're reading from the secret store, not from a `.env` file checked into the repo.

---

## Tenant resolution

In multi-tenant applications the session or token establishes the user, but the active tenant context requires an additional step. Get it wrong and the correct user sees another tenant's data.

**Sources of tenant context (in order of preference):**

1. **Embedded in the token/session directly** — the auth provider includes a `tenantId` or `orgId` claim (Clerk `orgId`, WorkOS `organizationId`, etc.). Cheap: no extra lookup. Reliable if the provider guarantees it's server-set.

2. **Derived from the user's memberships** — query the membership table: `SELECT tenantId FROM memberships WHERE userId = ? AND status = 'active'`. A user in exactly one tenant: simple. A user in multiple tenants (workspace switching): requires an unambiguous signal for *which* tenant is active this request.

3. **Disambiguated via subdomain / path prefix** — `acme.app.example.com` or `/api/workspaces/acme/...` supplies the tenant slug/id. Valid only after verifying the authenticated user is actually a member of that tenant (see **`craft-security`** → `authz.md` — never trust a client-supplied org id as proof of membership).

For multi-workspace apps, workspace switching is a UI/session concern — the *active workspace* is typically stored in the session, not derived from every request independently. The helper reads it from the verified session, not from a request body field.

If tenant resolution fails (user has no tenant, token doesn't match the requested org), return `403` — not a blank context that reaches the DB.

---

## Failing fast — reject before the handler body

The helper must be the first thing that runs, and it must **throw** (or in frameworks that use return-based errors, return an error type that the handler must check before continuing). The failure mode to prevent: a handler that calls `getRequestContext` but only uses it ten lines in, or that has an early `return` path that skips the call entirely.

Patterns to enforce this:

- **Throw on failure, never return `null`.** A nullable return puts the safety check at the call site, where it will be forgotten. An error thrown from the helper propagates up and is caught by the framework's error handler, returning the right HTTP status.

- **Wire into the framework's guard/middleware layer where the framework supports it.** NestJS guards, Fastify `preHandler` hooks, Express middleware, Hono middleware — all let you run `getRequestContext` before the handler function is reached, so the handler body receives a pre-verified context. Know the mechanism your framework provides; use it consistently.

- **For route groups that share an auth requirement** (e.g. all `/api/` routes), a single route-group middleware is better than per-handler calls — fewer call sites to audit, fewer places to forget. Still pass the resolved context to handlers explicitly (typed) rather than stashing it in a mutable request object with an `any` cast.

- **Public routes are the exception, not the default.** A route that genuinely needs no auth (health checks, OAuth callbacks, webhooks from known providers) is explicitly marked public. The code review question for any handler without an auth call at the top: is this intentionally public, or is the check missing? Webhook endpoints from known providers are not authenticated with the user-session pattern, but they are NOT unauthenticated — they must verify the provider's HMAC signature (e.g. `Stripe-Signature` header, GitHub webhook secret) before processing any payload. That verification is the auth substitute and belongs in the handler or a dedicated webhook-verification helper.

---

## Provider SDKs vs hand-rolled extraction

If the repo already uses an auth provider (Clerk, Auth.js/NextAuth, Supabase Auth, WorkOS, Firebase Auth, etc.), **prefer the provider's SDK for extraction**. Provider SDKs handle the low-level verification details (key rotation, algorithm pinning, session hydration) and stay current as the provider evolves:

```ts
// Discovery: look for the provider SDK in package.json, then find the server-side helper.
// The call pattern varies by provider — shown below for two common cases:

// Clerk on Next.js App Router (@clerk/nextjs in package.json)
import { auth } from "@clerk/nextjs/server";
async function getRequestContext(): Promise<RequestContext> {
  const { userId, orgId } = await auth();
  if (!userId) throw new AuthError(401, "unauthenticated");
  if (!orgId) throw new AuthError(403, "no_active_org");
  return { userId, tenantId: orgId };
}

// Auth.js v4 (next-auth@4): import { getServerSession } from "next-auth/next"
// Auth.js v5 (next-auth@5, beta): import { auth } from "@/auth" (the project's own config export)
// Detect version: check "next-auth" in package.json; look for the v5 `auth` export pattern.
```

When hand-rolling JWT verification (no provider SDK, or service-to-service tokens), use a maintained library (`jose` for Web Crypto / Edge-compatible, `jsonwebtoken` for Node). Do not implement `RS256` or `HS256` verification by hand. The full verification checklist (algorithm pinning, `exp`/`iss`/`aud` checks, rejecting `alg: none`) is in **`craft-security`** → `authz.md`.

**Discover before you write.** Grep for the existing auth call pattern (`auth()`, `getServerSession`, `getAuth`, `req.user`, `ctx.state.user`) before introducing a new one. Extending what exists is always the first choice.

---

## Edge and middleware placement

**Discover the runtime constraints before placing auth logic** — some runtimes restrict the APIs available, which directly affects which verification libraries work and where session hydration can happen.

General principles:

- **Some runtimes have no Node.js APIs at all.** Cloudflare Workers and similar edge runtimes run in a Web Crypto environment. Libraries that call Node's `crypto` module (`jsonwebtoken`, `connect-pg-simple`, many session adapters) will fail at runtime with no warning at deploy time. Use Web Crypto-compatible libraries (`jose`) or the provider's edge-compatible SDK.
- **Bare Node has no split** — all Node APIs are available in every handler. No constraint to discover, but still prefer a maintained library over hand-rolled crypto.
- **Middleware that only checks for the presence of a token** is a UX convenience (redirect to login), not a security control. The real verification and context resolution must happen in the handler, where the full runtime is available. Don't mistake a redirect middleware for the auth enforcement layer.
- **Session stores backed by platform-specific drivers** (e.g. `connect-pg-simple`, Redis adapters) may not be available in constrained runtimes — session hydration must happen where the driver works.

*Next.js-specific example:* Next.js middleware runs on the Edge runtime by default. Pages Router API routes and App Router route handlers default to the Node.js runtime, but App Router route handlers can opt into Edge with `export const runtime = "edge"`. `jsonwebtoken` works in Node.js API routes but is incompatible with the Edge runtime due to its Node.js `crypto` dependency — it will fail at runtime (and may fail at bundle time with a hard error or missing-module warning, not silently). For any auth logic running in Edge middleware or an Edge route handler, use a Web Crypto-compatible library such as `jose` or the provider's Edge-compatible SDK.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Handler with no `getRequestContext` call (or equivalent) at the top | Determine if intentionally public; if not, add the auth call as the first line |
| `getRequestContext` returns `null` / `undefined` on failure | Make it throw — don't leave the null-check to the caller |
| Auth call present but its result is unused for 10+ lines (early-return paths exist) | Hoist to the absolute first line; ensure no code path skips it |
| `userId` or `tenantId` read from the request body, query param, or custom header as a trusted value | Read from the verified session/token only; treat any client-supplied id as untrusted input |
| JWT decoded (`.split(".")`) without signature verification | Use a maintained library with full verification: pinned alg, `exp`, `iss`, `aud` — see **`craft-security`** → `authz.md` |
| Signing key / session secret hardcoded or read from a committed `.env` | Move to the secret store; see **`craft-security`** → `secrets.md` |
| Tenant resolved from a request field without membership check | Resolve from session/token, or verify membership against the DB before trusting the supplied id |
| `auth()` / `getServerSession()` called inside a service or query function, not the handler | Auth is a handler concern; pass `RequestContext` down as a typed argument, don't re-resolve mid-stack |
| Multiple divergent auth-extraction patterns across handlers in the same repo | Consolidate into one shared helper; grep for `Authorization` header reads in handler files |
| Edge middleware doing full JWT verification with a Node-only crypto library | Use `jose` or the provider's edge SDK for Edge-runtime verification |
| Webhook route without an explicit "public route" marker or without HMAC signature verification | Webhook routes skip user-session auth but MUST verify the provider's HMAC signature (Stripe-Signature, GitHub webhook secret, etc.) — that verification is the auth substitute; add it in the handler or a dedicated webhook-verification helper |
| OAuth callback route without an explicit "public route" marker or comment | Document why no user-session auth is required; add a comment so reviewers don't flag it as a gap |
| API-key looked up in the handler inline rather than in the shared helper | Move the DB lookup into the helper; handler receives `RequestContext` like any other auth type |

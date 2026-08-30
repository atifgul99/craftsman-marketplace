# Authentication & Authorization

Two questions, two answers, two failures. **Authentication (authN)** proves *who you are*; **authorization
(authZ)** decides *what you may do*. They fail independently, so they must be enforced independently:
identity is established once per request; authorization is re-checked at **every resource boundary**.
A valid session, token, or "logged-in" middleware pass is necessary but never sufficient to touch a
specific object.

> **See also:** `input-output.md` (validate & coerce the id *before* you authorize on it — a typed,
> bounded id is a precondition, not the check) · `secrets.md` (where the JWT signing key / session
> secret lives and how it's loaded). The frontend route-guard side (hiding UI a user can't use) is a
> UX concern, not a security control — see **`craft-ux`** → `layer-4-states.md`; gating UI never
> replaces the server check.
> `craft-backend` → `auth.md` covers the request-lifecycle mechanics — establishing the
> authenticated principal and resolving tenant/user context in a shared helper; this file is the
> security *standard* for what to do with that principal (per-resource authZ, IDOR/tenant scoping,
> JWT verification).

---

## Contents

- [AuthN is not authZ](#authn-is-not-authz)
- [Enforce at the resource boundary, every request](#enforce-at-the-resource-boundary-every-request)
- [The multi-tenant bug: IDOR / broken object-level auth](#the-multi-tenant-bug-idor--broken-object-level-auth)
- [RBAC vs ABAC, and the source of truth](#rbac-vs-abac-and-the-source-of-truth)
- [JWT claims](#jwt-claims)
- [Quick-reject checklist](#quick-reject-checklist)

---

## AuthN is not authZ

- **AuthN answers "is this request from who it claims?"** — verify a session cookie, a signed JWT, an
  API key. Output: a trusted principal (user id, tenant id, roles).
- **AuthZ answers "may *this* principal do *this* action on *this* object?"** — and the answer depends
  on the specific object, so it can't be fully precomputed in middleware.
- The common conflation: "the user is authenticated, therefore allowed." That's the root of most
  access-control bugs. Authentication is the gate to the building; authorization is the lock on each
  room.
- **Deny-by-default, least privilege.** A handler that can't *prove* the principal is entitled must
  refuse. New endpoints, new fields, and new actions start with no access and earn it explicitly —
  never inherit blanket access from "the user got past login."
- **Rate-limit auth endpoints against brute-force / credential-stuffing.** Login, password-reset,
  OTP, and token endpoints need throttling (per-IP and per-account) plus lockout/backoff — an
  unthrottled login is an open guessing oracle. **Ownership (emit once):** this skill owns the
  *abuse-defense policy* finding; **`craft-backend`** → `api-design.md` owns the in-app route
  middleware mechanism; **`craft-infra`** → `scale-resilience.md` owns platform/edge capacity
  throttling (gateway, CDN, shared/edge-KV); **`craft-ai`** owns LLM spend/token limits on model
  routes. **Per-account lockout** (track N failed attempts per `userId`, progressive backoff) is
  application-layer logic — implement with a `login_attempts` column or a KV key by `userId`,
  separate from the IP-level counter.

---

## Enforce at the resource boundary, every request

Middleware that checks `isAuthenticated` (or even a coarse role) runs before the handler knows which
record is being touched. The object-level decision belongs **in the handler**, against the loaded
resource:

- **Authorize on the resource, not the route.** `GET /invoices/:id` passing auth middleware says
  nothing about whether *this* user owns invoice `:id`. The check is: load the invoice (scoped — see
  below) and confirm ownership/permission.
- **Every request, not just the first.** Permissions change, sessions are long-lived, objects are
  re-fetched. Re-evaluate per request; don't cache an allow decision across a session.
- **Every verb and every field.** Read, write, delete, and list are distinct permissions. So are
  individual fields — a user may read a record but not its `ownerNotes`; an admin-only flag in a
  PATCH body must be rejected for non-admins (mass-assignment). Shape input and output per role
  (field-level *shaping/encoding* of the response lives in `input-output.md`; *who* may write/read
  each field is the authZ decision here).
- **Fail closed and uniform.** On any doubt, deny. Returning the *same* response (commonly `404`) for
  "doesn't exist" and "exists but not yours" avoids leaking which ids are real — pick a convention and
  apply it consistently.
- **Centralize the *policy*, enforce at the *boundary*.** A shared `can(user, action, resource)`
  helper or policy module keeps rules consistent and testable — but it still has to be *called* in
  each handler. Centralizing the function is good; pushing it so far up the stack that it can't see the
  object reintroduces the bug.

---

## The multi-tenant bug: IDOR / broken object-level auth

The single most common — and most damaging — access-control flaw: an authenticated user reads or
mutates another tenant's data by supplying its id. (OWASP calls it Broken Object Level Authorization;
the classic name is IDOR.) **An id from the client is a request, not proof of ownership.**

- **Scope every query by the trusted tenant/workspace/owner id** taken from the *server-established
  session/token*, not from the request. Illustrative (Prisma-style — discover the actual data layer
  in the repo):

  ```
  // WRONG — trusts the client's id as proof of access
  db.invoice.findUnique({ where: { id: params.id } })

  // RIGHT — scopes by the session's tenant; a foreign id simply returns nothing
  db.invoice.findFirst({ where: { id: params.id, workspaceId: session.workspaceId } })
  ```

- **Make the scope structural, not optional.** A `workspaceId` filter that each developer must
  remember will eventually be forgotten on the one query that matters. authZ *decides* who may touch a
  resource; the DB layer *mechanically enforces* the tenant predicate so a forgotten filter can't leak
  data. The enforcement mechanics — tenant-scoped repository/query wrapper, Postgres Row-Level Security
  (see "Row-Level Security (RLS)", incl. the transaction-pooler `SET LOCAL` caveats), base-query
  predicate injection — are owned by **`craft-db` → `access-patterns.md`**; don't re-derive them here.
  Defense in depth means both: app-level scoping *and* the DB-level backstop.
- **Don't authorize on a client-supplied tenant id.** If the request body/header carries
  `workspaceId`, treat it as untrusted input and confirm the session principal is a member of it;
  never use it *as* the authority.
- **Nested resources need the full chain checked.** `/workspaces/:w/projects/:p/tasks/:t` — verify
  the task belongs to the project, the project to the workspace, and the user to the workspace. A
  valid `:t` under someone else's `:w` is still IDOR.
- **Unguessable ids (UUIDs) are not authorization.** They raise the cost of guessing; they don't stop
  an attacker who *has* the id (shared link, log, referrer, enumeration elsewhere). Scope the query
  regardless.

---

## RBAC vs ABAC, and the source of truth

- **RBAC (role-based):** permissions attach to roles, roles to users (`admin`, `editor`, `viewer`).
  Simple, coarse, good for org-wide capabilities ("can manage billing").
- **ABAC (attribute-based):** the decision is a function of attributes — *who* (role, team), *what*
  (the resource's owner, status, classification), and *context* (time, IP). Needed for "owner can
  edit until published" or "same-team members can view." Most real apps are RBAC for capabilities plus
  per-object ownership/relationship checks — which is ABAC in practice.
- **Verify against the server's source of truth — not a client-supplied claim.** Whether a user is an
  admin is decided by *your* store (the row, the membership table, the policy engine) at request time,
  not by a `role` field in a request body or a stale value the client echoes back. A JWT claim is
  server-signed and so trustworthy *for what it asserted at issue time* (see below) — but for any
  decision that must reflect *current* state (a revoked role, a removed membership), check the store
  rather than trusting a token minted minutes ago.
- **Implementing RBAC for most MVPs.** Add a `roles` column (enum: `admin | editor | viewer`) on the
  user table. The authorization primitive is a pure function: `can(user.role, action, resource) →
  boolean`. Keep it as a plain helper first — a single switch or map is easy to test and audit.
  Libraries to reach for when the helper grows unwieldy: **Casl** (declarative, framework-agnostic,
  serializable rules — good for dynamic per-resource permissions) or **Casbin** (policy-file based,
  supports RBAC/ABAC/ACL models, more configuration overhead). Resist jumping to a library until the
  plain helper is too complex — premature abstraction here hides access-control bugs.

---

## JWT claims

This section owns the **security criteria** a token verification must meet. The *wiring* — where the
verification runs in the request lifecycle, the shared helper that calls it, producing the typed
principal — is owned by **`craft-backend`** → `auth.md`. Decide the criteria here; implement them
there.

A JWT is a **signed, not encrypted** token (unless you specifically use JWE): claims are
*integrity-protected* (tamper-evident), **not secret** — anyone holding the token can base64url-decode
and read every claim. Treat the contents as public.

- **Verify the signature on every request, server-side.** Reject `alg: none`; pin the expected
  algorithm and key so an attacker can't downgrade `RS256` to `HS256` and sign with the (public) RSA
  key. Use a maintained library; don't hand-roll verification.
- **Check `exp`, `iss`, and `aud`.** A token valid for service A should be rejected by service B — an
  unchecked `aud`/`iss` lets a token minted for one audience be replayed against another. Verify
  expiry; reject expired tokens (allow only minimal clock skew).
- **Keep access tokens short-lived; rotate via refresh tokens.** Because revocation is hard for
  stateless JWTs, a short TTL bounds the damage of a leaked token. **Target 15-minute expiry for
  access tokens; treat 1 hour as the maximum.** Refresh tokens: **30–90 days** with rotation —
  invalidate the old refresh token on use so a stolen token can only be used once before the legitimate
  holder detects it (token rotation with reuse detection). For "log out everywhere" / instant
  revocation you need server state (a session record, a token-version claim checked against the store,
  or a denylist) — pure stateless JWTs can't be revoked before `exp`.
- **Never put secrets or sensitive PII in claims** — they're readable. Put an id; look the rest up.
- **The signing key is a secret.** It lives in the validated env schema / secret store, is rotated,
  and is never committed — see `secrets.md`. Symmetric `HS*` shares one key across all verifiers
  (harder to distribute safely); asymmetric `RS*`/`ES*` lets verifiers hold only the public key.
- **Where it depends on the runtime:** Node verification differs from edge/Web Crypto — e.g. Next.js
  middleware on the Edge runtime can't use Node's `crypto`, so use `jose` or the provider SDK there.
  Confirm the verification path actually runs in the environment that needs it; discover the library
  in the repo rather than assuming one.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern                                                              | Fix                                                                         |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Auth checked only in middleware; handler trusts the route           | Authorize the loaded *object* in the handler, per request                   |
| Query by client id without tenant/owner scope (`findUnique({id})`)  | Scope by session's `workspaceId`/`ownerId` (`findFirst({id, workspaceId})`) |
| Tenant/workspace id read from request body/header as the authority  | Use the session-established tenant; verify membership of any supplied id     |
| Nested route where only the leaf id is checked                      | Verify the full parent chain (workspace → project → task)                    |
| Role/permission read from a request field or echoed client value    | Decide against the server's store / policy at request time                   |
| Admin-only fields accepted in a PATCH from any role (mass-assign)   | Allow-list writable fields per role; reject the rest                         |
| `403` vs `404` on the same id reveals existence                     | Return a uniform response for "not yours" and "not found"                    |
| JWT decoded but signature/`exp`/`aud`/`iss` not verified            | Full verify: pinned alg + key, reject `alg:none`, check `exp`/`aud`/`iss`    |
| Secret or PII stored in JWT claims                                  | Store an id only; look up sensitive data server-side                         |
| Long-lived access token with no revocation path                     | Short TTL + refresh; add server-side revocation if instant logout needed     |
| Authorization decision cached across a session                      | Re-evaluate per request                                                      |
| UUID treated as the access control ("unguessable, so safe")         | Scope the query by tenant/owner regardless of id entropy                     |

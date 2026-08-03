# Input & Output

The boundary discipline: **validate every input where it crosses a trust boundary, encode every
output for the context it lands in, and parameterize every query.** Injection (XSS, SQLi, command,
path, SSRF) is one bug class with one root cause — untrusted data interpreted as code/markup/query
instead of as data. Close it at both ends.

> **See also:** `authz.md` (who's allowed) · `secrets.md` (don't echo credentials in errors) ·
> `headers-cors.md` (CSP as defense-in-depth behind output encoding). The frontend component side of
> XSS is cross-referenced from **`craft-ux`** → `layer-3-components.md` and **`craft-frontend`** →
> `architecture.md`.

---

## Contents

- [Validate input at the boundary](#validate-input-at-the-boundary)
- [Encode output for its context](#encode-output-for-its-context)
- [Frontend / DOM XSS](#frontend--dom-xss)
- [Parameterize queries](#parameterize-queries)
- [CSRF protection](#csrf-protection)
- [File uploads](#file-uploads)
- [Rate limiting and DoS hardening](#rate-limiting-and-dos-hardening)
- [SSRF & outbound requests](#ssrf--outbound-requests)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Validate input at the boundary

- **Schema-validate at the edge** (Zod/valibot-style) — every request body, query param, route
  param, header, and webhook payload. Parse into a typed value; reject anything that doesn't match.
  Validation is allow-list (define what's permitted), never deny-list (blocklist a few bad strings).
- **Validate on the server even if the client already did.** Client validation is UX; it is not a
  security control — the attacker controls the client.
- **Bound everything that's unbounded** — string lengths, array sizes, number ranges, pagination
  limits, upload sizes/types. Unbounded input is a DoS and a memory risk.
- **Re-validate on the trust transition, not just once at ingress.** Data from a queue, a cache, or
  another internal service that originally came from a user is still untrusted at the next boundary.

---

## Encode output for its context

The same string is safe in one context and an exploit in another. Encode at the point of output, for
*that* sink:

- **HTML body** → HTML-entity encode. (React/JSX does this for `{value}` text — which is exactly why
  `dangerouslySetInnerHTML` is the hole; see below.)
- **HTML attribute** → attribute-encode; always quote attributes.
- **URL / query component** → `encodeURIComponent`.
- **JavaScript / JSON embedded in HTML** → JSON-encode and escape `<`, so a `</script>` in the data
  can't break out.
- **SQL** → don't encode, *parameterize* (see below).
- **Shell** → avoid building command strings; pass args as an array to `execFile`/`spawn`, never
  `exec` with interpolation.

Never blanket-escape on input and call it done — you'll double-encode in some contexts and
under-encode in others. Encode per sink, at output time.

---

## Frontend / DOM XSS

The browser is the last place untrusted data becomes executable. The component rules:

- **`dangerouslySetInnerHTML` is the default XSS vector.** Avoid it. If rendering rich/user HTML is
  genuinely required, sanitize first with a vetted, maintained library (**DOMPurify**) and an
  allow-list config — never feed it raw API responses, URL params, or user input.
- **Validate URLs before they become `href` / `src` / `formAction`.** A `javascript:` URL in an
  attacker-controlled link executes on click; a `data:text/html` URL navigated via `<a href>`
  renders attacker HTML (in older/non-Chromium browsers), and hostile `data:`/`blob:` in `src`
  (`<iframe>`, `<object>`) is an injection sink. Parse with `new URL(value, trustedOrigin)` (the base
  is required, or a relative path throws) and check `url.protocol` against an allow-list — don't
  substring-match. Allow same-origin relative paths plus `http(s)`, `mailto`, `tel`; reject the rest.
  Treat `data:`/`blob:` as sink-specific exceptions only for values your own code created, never for
  user-supplied URLs.
- **`target="_blank"` requires `rel="noopener noreferrer"`** — without `noopener` the opened page
  can reach back through `window.opener` and navigate your tab (reverse tabnabbing).
- **Never interpolate untrusted data into `<script>`, `<style>`, inline `style`, or a server-rendered
  `<script>` JSON blob.** Pass data as props or as JSON the app parses at runtime — not as markup the
  browser parses as code. Beware `__html` JSON injected into the page during SSR hydration.
- **Don't put secrets or full PII in client markup or `data-*` attributes.** Anything in the DOM (or
  the JS bundle, or `NEXT_PUBLIC_*` env) is public — assume the user can read it.
- **CSP is defense-in-depth, not a substitute.** A strict Content-Security-Policy (no
  `unsafe-inline`, nonce/hash for scripts) limits the blast radius if an encoding bug slips through —
  configure it in `headers-cors.md`, but fix the encoding regardless.

---

## Parameterize queries

- **Parameterized queries / prepared statements for all SQL** — bind values as parameters, never
  string-concatenate user input into the query. An ORM or query builder does this by default; the
  risk is the raw-SQL escape hatch (`db.raw`, `sql.unsafe`, template-built `WHERE` clauses).
- **Identifiers can't be parameterized** — column/table/sort-direction names that come from input
  must be checked against an allow-list, not interpolated.
- **NoSQL is injectable too.** Reject query operators in user input (e.g. a `{ "$gt": "" }` arriving
  where a string is expected) — validate the *shape*, not just the presence. Specific pitfalls:
  - **Mongoose schema type coercion:** if a field is typed as `String`, Mongoose will coerce an object
    like `{ $gt: "" }` to `[object Object]` or pass it through depending on the version — it does
    *not* reject it. A schema parse with Zod/valibot before the query call is the real guard: confirm
    the value is a primitive `string`, not an object.
  - **Raw MongoDB driver:** strip or reject keys starting with `$` from any user-supplied object before
    it touches a query builder. Use `allowDiskUse: false` unless large aggregations are explicitly
    required (reduces DoS via expensive sort operations). Validate the complete input shape before
    passing to the query — don't rely on the driver to reject operator injection.
  - If you're using Mongoose, prefer schema-defined paths and `Model.findOne({ field: req.body.field })`
    with `field` coming from a Zod-validated primitive — not from a spread of `req.body`.
- **Select explicit fields; don't leak internal columns.** A response built from `SELECT *` or an
  un-shaped object exposes fields (password hashes, internal flags, other tenants' ids) that were
  never meant to leave the boundary. Shape the output DTO explicitly.

---

## CSRF protection

Cross-site request forgery tricks an authenticated user's browser into sending a state-mutating
request to your server from another origin. Defense depends on how your session is carried:

- **SameSite=Strict or SameSite=Lax cookies are sufficient for same-origin browser flows.** With
  `SameSite=Strict`, the browser never sends the cookie on cross-origin requests at all. With
  `SameSite=Lax` (the modern browser default), the cookie is sent on top-level navigations (link
  clicks) but *not* on cross-origin POST/PUT/PATCH/DELETE or subresource requests — which is enough
  to block the classic CSRF case. Confirm `SameSite` is explicitly set; rely on "browser default
  is Lax" only if you have verified the full browser matrix the app targets.
- **When you need a synchronizer token (CSRF token):** cross-origin form submissions you legitimately
  support, or as a hedge against gaps in browser `SameSite` enforcement — Chrome's "Lax + 2 minutes"
  carve-out sends the cookie on a cross-site POST within 2 minutes of it being set, and older WebKit
  releases have historically treated `Lax` as equivalent to `None` in some cases. Don't rely on
  `SameSite` alone for state-changing routes; keep token-based CSRF protection as the real control.
  Pattern: server generates a cryptographically random
  token per session, embeds it in a hidden form field or a response header, and validates it on every
  state-mutating request. The token must be unguessable and tied to the session — not a static value.
- **Double-submit cookie pattern (stateless alternative):** set a random value as a non-`HttpOnly`
  cookie *and* require the client to echo it back in a custom request header or body field. The server
  validates they match. Because a cross-origin attacker can't read the cookie value (same-origin
  policy), they can't forge the header. Works without server-side session storage — useful for
  stateless APIs. Caveat: requires the cookie to be readable by JS, so don't combine with
  `HttpOnly` on that specific CSRF cookie.
- **`SameSite=None` is the danger zone.** If your session cookie uses `SameSite=None` (required for
  cross-site embedded or third-party flows), the browser sends it on all cross-origin requests — CSRF
  is fully back. Every state-mutating endpoint then needs a synchronizer token or double-submit cookie.
  `SameSite=None` also requires `Secure`; without it the cookie is rejected by modern browsers.
- **CORS is not CSRF protection.** A passing CORS preflight check means the browser allows the read;
  it doesn't prevent the *request* from being sent (simple requests without custom headers skip the
  preflight entirely). See `headers-cors.md`.

---

## File uploads

File upload endpoints are a cluster of independent attack vectors. Address each one:

- **MIME validation from magic bytes, not the Content-Type header.** The `Content-Type` a client
  sends is attacker-controlled. Read the actual file bytes and check the magic number. The
  `file-type` npm package does this for common formats — it returns the detected MIME type from the
  file's binary signature, which you then validate against your allow-list. Do not trust the
  extension or the `Content-Type` header as the sole check.
- **Extension allow-list, not deny-list.** List the exact extensions you will accept (`jpg`, `png`,
  `webp`, `pdf`). Deny-lists always have gaps (e.g. `.phtml`, `.php5`, `.jspx` — the list is long
  and browser/server-specific). An allow-list is closed by default.
- **Enforce size limits server-side.** Client-side size validation is UX only — the attacker bypasses
  it. Set a hard limit in the HTTP layer (e.g. `express-fileupload` `limits.fileSize`, Nginx
  `client_max_body_size`) *before* the file hits application code. Otherwise a multi-GB upload
  exhausts memory or disk.
- **Path traversal: never use the user-supplied filename in a filesystem path.** A filename like
  `../../etc/passwd` or `../app/secrets.env` is a path traversal attack. Generate a random key (UUID
  or `crypto.randomUUID()`) for the stored filename. If you must preserve the original name for
  display, store it separately as metadata — never use it in a `fs.writeFile` path or an S3 key
  derived from the path.
- **SVG-as-HTML XSS.** SVG files are XML that browsers render as HTML, and they can contain
  `<script>` tags. If you serve user-uploaded SVGs from your app origin, a malicious SVG executes
  script in your origin's context — same threat as stored XSS. Options in order of preference:
  (1) serve uploaded SVGs from a separate domain or a sandboxed CDN origin with no cookies (best),
  (2) strip script tags and event-handler attributes with a vetted XML sanitizer before storage,
  (3) serve with `Content-Type: text/plain` and `X-Content-Type-Options: nosniff` to prevent
  rendering. Never serve raw user-uploaded SVGs from the same origin as your session cookies.
- **Object-storage placement.** Serve uploaded files from a dedicated storage origin (S3 bucket,
  Cloudflare R2, GCS bucket), never from the same origin as your app. This contains XSS from
  uploaded files, prevents directory traversal to app code, and isolates the attack surface. If files
  must be served through your origin, use a `/uploads/` path behind `Content-Disposition: attachment`
  and strict MIME enforcement so the browser downloads rather than renders.

---

## Rate limiting and DoS hardening

Auth-specific rate limiting (login brute-force, credential-stuffing) is covered in `authz.md`. This
section covers the application-layer DoS surface that exists *regardless* of authentication:

- **Rate-limit list and search endpoints.** An uncapped `GET /products?q=` or `GET /users` endpoint
  is a scraping and DoS vector — large result sets drive memory and DB load. Apply a per-IP (and,
  where authenticated, per-user) rate limit: requests per minute at the route or gateway level.
  The *mechanism* (shared KV counters, gateway-level throttles) belongs to **`craft-infra` →
  `scale-resilience.md`**; the *policy* (which endpoints need a cap, at what threshold) is decided
  here.
- **Request body-size limits.** Enforce a global body-size cap at the HTTP framework layer before
  any route handler or ORM receives the bytes — e.g. `express.json({ limit: '100kb' })`. Oversized
  payloads exhaust memory and can crash the process before any validation runs. See
  **`craft-backend`** for framework-specific wiring.
- **Pagination and query-complexity limits.** Every list/search endpoint must have a maximum `limit`
  enforced server-side (not just client-trust). Reject `limit=0` or absurdly large values (`limit >
  100` unless you have a deliberate reason). For GraphQL, apply query-depth and complexity limits —
  an unbounded nested query can fan out into thousands of DB calls. Validate these bounds in the
  schema layer (Zod/valibot) alongside other input validation.

---

## SSRF & outbound requests

When the server fetches a URL the user supplied (webhooks, link previews, image proxies, imports):

- **Allow-list the destination** (scheme + host) where possible. Otherwise, **reject any
  non-global / special-use address** rather than maintaining a partial blocklist by hand: normalize
  the resolved IP (including IPv4-mapped IPv6 like `::ffff:A.B.C.D`) with a vetted IP library and
  reject anything that isn't a public/global unicast address. That bucket must cover loopback
  (`127.0.0.0/8`, `::1`), private (`10/8`, `172.16/12`, `192.168/16`, ULA `fc00::/7`), CGNAT
  (`100.64/10`), link-local (`169.254/16`, `fe80::/10`), cloud metadata (`169.254.169.254`),
  unspecified (`0.0.0.0/8`, `::/128`), and multicast/reserved. Check **every** address DNS returns,
  connect only to the validated address, and re-resolve/re-check on redirects to defend against DNS
  rebinding.
- **Disable or bound redirects** and set timeouts — an open redirect turns an allow-list into a
  bypass.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern                                                                          | Fix                                                                         |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Request body/params used without schema validation                              | Parse + validate at the edge (allow-list)                                   |
| Client-only validation on a security-relevant field                             | Re-validate on the server                                                   |
| `dangerouslySetInnerHTML` with non-sanitized content                            | Remove it, or sanitize via DOMPurify with an allow-list                     |
| User-controlled value in `href`/`src` without protocol check                   | `new URL()` + allow-list `http(s)`/`mailto`/relative                        |
| `target="_blank"` without `rel="noopener noreferrer"`                           | Add the `rel`                                                                |
| Untrusted data interpolated into `<script>`/inline `style`                      | Pass as parsed JSON/props, never as markup                                  |
| Raw/templated SQL with interpolated input (`db.raw`, `sql.unsafe`)              | Parameterize / bind values                                                  |
| Sort/column name interpolated from input                                        | Allow-list the identifier                                                   |
| `SELECT *` or un-shaped object in a response                                    | Explicit field selection / output DTO                                       |
| NoSQL query passed a user-supplied object (Mongoose/raw driver)                 | Zod-validate input to a primitive type before the query; reject `$`-keys   |
| Server fetch of a user-supplied URL with no SSRF guard                          | Allow-list host + block private ranges + bound redirects                    |
| Secret/PII rendered into DOM or `data-*` / `NEXT_PUBLIC_*`                      | Keep it server-side                                                         |
| Form submission or state-mutation endpoint with session cookie in SameSite=None and no CSRF token | Add synchronizer token or double-submit cookie pattern     |
| File upload trusting the client's `Content-Type` or filename extension         | Validate MIME from magic bytes (`file-type`); allow-list extensions        |
| User-supplied filename used in a filesystem or storage path                     | Generate a random key (UUID); store original name as metadata only          |
| User-uploaded SVG served from the app origin                                    | Serve from a separate domain or sanitize script/event-handler tags          |
| No server-side body-size limit on upload or API endpoints                       | Enforce at the HTTP framework layer before handlers receive bytes            |
| List/search endpoint with no pagination cap or body-size limit                  | Enforce a max `limit` server-side; add rate limiting per IP/user            |

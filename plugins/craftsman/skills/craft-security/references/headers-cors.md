# Headers & CORS

Response headers and CORS are the **transport-and-boundary layer**: they don't fix application bugs,
they shrink the blast radius when one slips through and they deny cross-origin reads by default.
The discipline: **ship a strict, explicit set of security headers on every response, and treat CORS
as a deny-by-default allow-list that never grants access — it only relaxes the browser's same-origin
read restriction for origins you trust.**

> **See also:** `input-output.md` (CSP is defense-in-depth *behind* output encoding — fix the
> encoding regardless) · `authz.md` (CORS is not authorization — every request still passes authN/Z
> server-side). The CSP *policy mechanism* (`script-src`/`style-src`/`font-src` directives) lives
> here; the concrete style/font/asset *sources* a given UI needs are a **`craft-ux`** design-system
> concern — coordinate, don't hardcode them blind. The frontend component side of XSS
> (`dangerouslySetInnerHTML`, href/src validation) is owned by this skill's `input-output.md`, and is
> cross-referenced from **`craft-ux`** → `layer-3-components.md`.

---

## Contents

- [Discover the current posture first](#discover-the-current-posture-first)
- [Content-Security-Policy (defense-in-depth)](#content-security-policy-defense-in-depth)
- [HSTS](#hsts)
- [The supporting headers](#the-supporting-headers)
- [CORS: deny-by-default](#cors-deny-by-default)
- [Where headers live & verifying them](#where-headers-live--verifying-them)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Discover the current posture first

Headers and CORS may already be set somewhere — find where before adding a second source of truth
(two layers setting the same header is how you get a permissive one silently winning):

- Grep for an existing middleware/`next.config` `headers()`/Helmet/proxy (`nginx`, Caddy, Cloudflare)
  config. Note **every** layer that can set headers — edge, app, framework defaults.
- Curl a real response (`curl -sI https://…`) and read what actually ships. The config and the wire
  can disagree; the wire wins.
- Find existing CORS handling (a `cors` package, manual `Access-Control-*` writes, a framework flag).
  Check whether it wildcards the origin and whether it sets `Allow-Credentials`.

---

## Content-Security-Policy (defense-in-depth)

CSP is a **second line behind output encoding**, not a replacement for it — it limits what an
injected payload can do if an encoding bug slips through. Build the strictest policy the app tolerates:

- **No `unsafe-inline` / `unsafe-eval` for scripts.** These re-open exactly what CSP exists to close.
  Prefer a **per-response nonce** (`script-src 'nonce-…'`) or a **hash** (`'sha256-…'`) for any inline
  script that must stay inline. A nonce must be unique per response and unguessable — it can't be
  precomputed or cached across requests, so it needs the rendering layer to inject it.
- **`strict-dynamic`** (CSP3) lets a nonce'd loader script vouch for the scripts it loads, so you can
  drop host allow-lists for scripts. Older non-CSP3 browsers ignore `strict-dynamic` and honor
  whatever else is in `script-src` (the nonce plus any host list you kept) — so the host-list fallback
  only exists if you deliberately leave it in; it is **not** synthesized. Keep that fallback if you
  must support them; verify against your real target matrix, don't assume.
- **Lock the fetch directives** to what the app needs, narrowest first:
  - `default-src 'self'` as the backstop.
  - `connect-src` — the exact API/analytics/websocket origins the app calls. This is your egress
    allow-list; a wide `connect-src` lets an injected script exfiltrate freely.
  - `frame-ancestors 'none'` (or an explicit allow-list) — the modern clickjacking control
    (see below).
  - `object-src 'none'`, `base-uri 'self'` — cheap, high-value, almost never need to be wider.
- **`style-src`, `img-src`, `font-src`** depend on the design system (CSS-in-JS often needs
  `'unsafe-inline'` for styles or a nonce; check the bundler/runtime). The *policy mechanism* is here;
  the *style/font/asset sources* are a **`craft-ux`** concern — coordinate, don't hardcode them blind.
- **Roll out with `Content-Security-Policy-Report-Only` + a report sink first.** A too-strict CSP
  breaks the app silently in the browser; report-only surfaces violations without enforcing, so you
  tighten with data instead of guesses.
- Framework note: meta-tag CSP can't express `frame-ancestors` and can't carry a per-request nonce
  cleanly — prefer the response **header**. In SSR frameworks (Next.js, etc.) generate the nonce in
  middleware/request scope and thread it to inline scripts; the exact hook is framework- and
  version-specific — discover it, don't assume.

---

## HSTS

`Strict-Transport-Security` forces HTTPS for future visits, defeating SSL-strip downgrades:

- **`max-age=31536000; includeSubDomains`** is the standard strong value (1 year, all subdomains).
- **`includeSubDomains` covers *every* subdomain** — confirm none must serve plain HTTP before you
  ship it (it's hard to walk back while it's cached in browsers).
- **`preload` is a one-way door.** Adding it (and submitting to the browser preload list) hardcodes
  HTTPS for your domain into shipped browsers; removal is slow and painful. Add it only once
  `includeSubDomains` is proven safe and you intend it permanently. The hstspreload.org submission has
  hard minimums: `max-age` must be **≥ 31536000** (1 year) and **both** `includeSubDomains` and
  `preload` must be present, or the submission is rejected.
- HSTS is delivered over **HTTPS only** (browsers ignore it on plain HTTP) and is moot if TLS isn't
  already terminated correctly — it complements TLS, it doesn't provide it.

---

## The supporting headers

Small, high-leverage, set them on every response:

- **`X-Content-Type-Options: nosniff`** — stops MIME-sniffing, so a response served as `text/plain`
  isn't reinterpreted as executable script. Pair with correct `Content-Type` values.
- **`Referrer-Policy`** — `strict-origin-when-cross-origin` (a common modern default) or
  `no-referrer` for sensitive apps, so full URLs (which may carry tokens/ids) don't leak to third
  parties.
- **`Permissions-Policy`** — disable powerful features the app doesn't use
  (`camera=(), microphone=(), geolocation=()`, etc.). Allow-list only what you need. Note:
  `Feature-Policy` is deprecated — use `Permissions-Policy` instead. Browser support is still
  incomplete (verify against caniuse.com before relying on it for a security guarantee). Treat
  `Permissions-Policy` as defense-in-depth, not a primary control.
- **`X-Frame-Options: DENY`** is **superseded by CSP `frame-ancestors`** for clickjacking —
  `frame-ancestors` is more expressive (multiple origins) and is what modern browsers honor. Keep
  `X-Frame-Options` only as a fallback for legacy browsers; `frame-ancestors` is the source of truth.
- Skip the deprecated `X-XSS-Protection` — modern browsers ignore it and its legacy mode could
  introduce bugs. CSP replaces it.

---

## CORS: deny-by-default

CORS is a **browser** mechanism that relaxes same-origin *read* restrictions; it is not a
server-side access control. Get the deny-by-default posture right:

- **Allow-list origins explicitly; reflect only matches.** Keep a known set of allowed origins,
  compare the request's `Origin` against it, and echo back **that exact origin** in
  `Access-Control-Allow-Origin` only on a match. Never blanket-reflect whatever `Origin` arrives —
  that's a wildcard wearing a disguise.
- **Never pair `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`.** The
  spec forbids it, and the combination is the classic credentialed-CORS hole. With credentials you
  **must** name a specific origin (and add `Vary: Origin` so caches don't serve one origin's ACAO to
  another).
- **Match origins exactly** — full-string compare against the allow-list, not `startsWith` /
  `includes` / a loose regex. `evil-yourapp.com` and `yourapp.com.evil.com` defeat substring checks.
- **Handle preflight (`OPTIONS`) deliberately** — return the allowed methods/headers and a sane
  `Access-Control-Max-Age`, and only for allowed origins. Don't let a permissive preflight handler
  undo a strict actual-request policy. With credentials, browsers do **not** treat `*` as a wildcard
  in `Allow-Methods`/`Allow-Headers`/`Expose-Headers` — it's matched literally, so enumerate the real
  methods/headers (and list `Authorization` explicitly in `Allow-Headers`; it isn't covered by `*`).
  Note browsers cap `Access-Control-Max-Age` (Chrome ~2h, Firefox ~24h), so oversized values are
  clamped.
- **CORS is not authorization (`authz.md`).** A passing CORS check means the *browser* will let JS
  read the response; it says nothing about whether the caller is allowed to. Every request still goes
  through authN/Z server-side. And CORS doesn't protect non-browser clients at all — curl ignores it.
- **CORS is not CSRF protection.** State-changing requests still need a CSRF defense
  (SameSite cookies, token, or origin check) independent of CORS.

---

## Where headers live & verifying them

- **Set headers once, as early and as global as possible** — a middleware/edge/proxy layer that
  covers *all* responses, including errors, 404s, redirects, and static assets. Per-route header
  setting drifts: the one handler that forgets is the gap. If multiple layers exist (edge + app),
  pick **one** owner and make the others defer, so a permissive value can't override a strict one.
- **CORS belongs at the same boundary**, before route logic, and must run for the preflight `OPTIONS`
  too.
- **Verify on the wire, not in the config** — security you haven't watched ship isn't done:
  - `curl -sI https://your-app/…` and confirm each header is present with the expected value, on a
    real route *and* on an error/redirect response.
  - For CORS, replay a real cross-origin request with an `Origin` header and confirm allowed origins
    are reflected and disallowed ones get **no** `Access-Control-Allow-Origin` (not a wildcard).
  - Run the response through an external header scanner (e.g. Mozilla Observatory / securityheaders)
    as a sanity check, then re-curl to confirm the live values match.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern                                                          | Fix                                                              |
| --------------------------------------------------------------- | --------------------------------------------------------------- |
| `script-src` includes `'unsafe-inline'` / `'unsafe-eval'`       | Drop it; use a per-response nonce or hash                       |
| Inline `<script>` with no nonce/hash under a strict CSP         | Add nonce (request-scoped) or move script to a file             |
| `connect-src` wide-open (`*` / missing) on a strict-CSP app     | Allow-list the exact API/ws/analytics origins                   |
| No `frame-ancestors` (relying only on `X-Frame-Options`)        | Add `frame-ancestors 'none'`/allow-list; keep XFO as fallback   |
| CSP shipped enforcing with no report-only rollout / report sink | Stage via `…-Report-Only` first, then enforce                   |
| Missing/weak HSTS on an HTTPS app                               | `max-age=31536000; includeSubDomains` (preload only when sure)  |
| `preload` added before `includeSubDomains` is proven safe       | Remove `preload` until subdomains are verified                  |
| Missing `X-Content-Type-Options: nosniff`                       | Add it; set correct `Content-Type`                              |
| No `Referrer-Policy` / `Permissions-Policy`                     | `strict-origin-when-cross-origin`; deny unused features         |
| `Access-Control-Allow-Origin: *` with `Allow-Credentials: true` | Name a specific allow-listed origin; add `Vary: Origin`         |
| `Origin` blindly reflected into ACAO                            | Compare against allow-list; reflect only exact matches          |
| Origin matched with `includes`/`startsWith`/loose regex         | Full-string equality against the allow-list                     |
| CORS treated as an access control                               | Enforce authN/Z server-side; CORS only relaxes browser reads    |
| Headers set per-route instead of globally                       | Move to middleware/edge covering all responses (incl. errors)   |
| Header values trusted from config, never curled                 | `curl -sI` the live response; confirm on routes + errors        |

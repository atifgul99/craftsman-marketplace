# Secrets

Secrets are credentials, tokens, signing keys, and connection strings — anything that grants access if
leaked. The discipline: **load them once through a validated env schema at startup, keep them off every
public surface (source, VCS, logs, error responses, the client bundle), and scrub credential-shaped
strings before they can escape.** A secret is only as safe as its least-careful read.

**Scope split.** This file owns the *application-side* secret discipline: the validated env schema,
the public-prefix/client-bundle rule, build-vs-runtime read timing, and scrubbing credentials from
logs/errors. Where the store physically lives and how it is provisioned/deployed belongs to
**`craft-infra` → `config.md`**; output-shaping mechanics for error responses are
`input-output.md`; what a leaked token can *do* is `authz.md`.

> **See also:** `input-output.md` (don't echo secrets in error output — output shaping & DTO rules
> live there) · `headers-cors.md` (don't leak tokens via permissive CORS or `Referer`) ·
> `authz.md` (what a leaked token can *do* — least-privilege limits blast radius). Discover the repo's
> actual secret loader, store, and rotation story before changing anything — never assume.

---

## Contents

- [Load through a validated env schema](#load-through-a-validated-env-schema)
- [Client-exposed env is public](#client-exposed-env-is-public)
- [Build-time vs runtime availability](#build-time-vs-runtime-availability)
- [Secret store & rotation](#secret-store--rotation)
- [Scrub secrets from logs & errors](#scrub-secrets-from-logs--errors)
- [.env hygiene](#env-hygiene)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Load through a validated env schema

Raw `process.env.FOO` reads scattered through the codebase are the root problem: each is an untyped,
unvalidated, possibly-`undefined` string with no single place that knows what the app requires.

- **Define one env module** (`env.ts` / `config.ts`) that parses `process.env` through a schema
  (Zod/valibot/envalid-style) and exports a typed, frozen object. Everything else imports from there.
- **Fail fast at startup.** If a required secret is missing or malformed, the schema should throw on
  boot — not surface as a confusing runtime error (or worse, a silent `undefined` that disables auth)
  on the first request hours later.
- **Validate shape, not just presence** — a URL is a URL, a port is a numeric range, a key matches its
  expected prefix/length. Catches paste errors and wrong-environment values before they ship.
- **Mark which vars are secret vs public** in the schema (e.g. separate `server`/`client` groups).
  This is what lets you enforce the client-bundle rule below mechanically rather than by memory.
- **Discover first:** grep for `process.env` usage and for an existing `env.ts`/`config.ts`. If a
  schema exists, extend it; if reads are raw and scattered, consolidating them is the fix.

---

## Client-exposed env is public

**The framework gotcha:** bundlers inline a *prefixed* subset of env into the client bundle at build
time. Anything in that subset is shipped to every browser — it is public, full stop, and must never
hold a secret.

- **Next.js** → `NEXT_PUBLIC_*` is inlined into client JS. **Vite** → `VITE_*` (via `import.meta.env`).
  **CRA** → `REACT_APP_*`. **Expo** → `EXPO_PUBLIC_*`. Check the repo's framework/bundler for its exact
  prefix; the mechanism is universal even though the name differs.
- **A secret behind a public prefix is a leaked secret** — minification is not obfuscation; assume any
  attacker can read the bundle. API keys, service-role keys, signing secrets, DB URLs never get a
  public prefix.
- **Public-prefixed vars are for non-sensitive config only** — public analytics IDs, a key the vendor
  explicitly documents as safe to expose client-side (e.g. a Stripe publishable key) — not merely one
  whose name contains "public" — feature flags. If you'd mind it on a billboard, it doesn't go
  there.
- **The inverse trap:** a genuinely client-needed value that *is* sensitive (e.g. a third-party token)
  means the call belongs on the server — proxy it through a route handler that holds the secret
  server-side, don't expose the secret to make the client call work. (Same rule lands in
  `input-output.md`: anything in the DOM/bundle is public.)

---

## Build-time vs runtime availability

When a secret is read decides whether it's even available — and whether it leaks. This is the security
consequence of read-timing (leak permanence, rotation cost); how the build pipeline injects vars is
`craft-infra` → `config.md`.

- **Build-time inlining is permanent.** Values the bundler inlines into the CLIENT bundle —
  public-prefixed vars, or literal `process.env.X` references it statically replaces — are baked into
  client artifacts permanently. (Server-side module-scope reads are not inlined; they are read from the
  server process env at startup, but reading a runtime-rotatable secret at server *boot* still requires
  a restart to pick up a new value.) Rotating an inlined secret requires a rebuild, and the old value
  persists in any cached build output.
- **Read runtime secrets through the validated env module, not build-time inlining** — and be honest
  about rotation. Platform env vars are fixed for the process: reading `process.env.SECRET` per
  request does *not* make a rotated value live; that still needs a restart/redeploy. Live rotation
  requires an actual dynamic secret manager (Vault, AWS/GCP secret managers) read through a typed
  secret-loader with a TTL cache + validation — never raw `process.env` scattered in handlers. This
  matters most on serverless/edge, where module scope and request scope differ.
- **Edge runtimes restrict APIs** — some secret-store SDKs depend on Node built-ins (`fs`, the Node
  `crypto` module, native addons) that aren't available on edge (note Web Crypto `crypto.subtle` is).
  Verify the loader works in the target runtime rather than assuming Node availability.
- Confirm by inspecting the built bundle (grep the output for a known secret value) — verify, don't
  trust the config.

---

## Secret store & rotation

- **Source of truth is a managed store, not a file on disk** for anything beyond local dev — platform
  env vars, a secrets manager, or the orchestrator's secret primitive (the specific product is an
  `craft-infra` → `config.md` choice). The env schema reads from whatever the
  environment injects; the store is *where* it comes from. Discover the repo's actual store.
- **Rotation must be possible without a code change.** Because the env module is the only reader,
  rotating a credential is a store update + restart/redeploy — no grep-and-replace across source.
- **Rotate on exposure, on a schedule, and on offboarding.** Treat any secret that touched a log, a
  screenshot, a PR, or a chat as compromised — rotate it, don't just delete the message.
- **Scope secrets to least privilege** so a leak is contained (`authz.md`): per-service keys, scoped
  tokens, short TTLs over one omnipotent god-key.
- **Distinct secrets per environment** — dev/staging/prod don't share keys; a leaked dev key must not
  open prod.

---

## Scrub secrets from logs & errors

Secrets leak most often through observability, not exploits. Two surfaces leak hardest: **logs** and
**error responses returned to the caller.**

- **Never log the secret-bearing object whole.** Logging a full request (headers carry `Authorization`,
  `Cookie`), a config dump, or a caught DB error (connection strings embed passwords) spills
  credentials into log storage that more people can read than can read the secret store.
- **Redact at the logger, centrally.** The pattern is the same across libraries: identify the
  secret-bearing key paths, then configure the logger to omit or mask them. Apply it to known keys:
  `authorization`, `cookie`, `set-cookie`, `password`, `token`, `secret`, `apiKey`, `*.creditCard`.
  Belt-and-suspenders: a serializer that masks credential-*shaped* strings (long base64/hex/JWT-looking
  values, `sk-`/`AKIA`-prefixed tokens). Library specifics:
  - **pino:** `pino({ redact: { paths: ['req.headers.authorization', '*.password', '*.token'], censor: '[REDACTED]' } })` — the `redact` option accepts dot-notation paths and wildcards; the library handles nested structures automatically.
  - **Winston:** no built-in redact option. Options: (1) write a custom `winston.format.printf` formatter that inspects `info` and scrubs known keys before the log line is written, (2) use the `winston-sensitive-data` community module which wraps the same key-scrubbing pattern, or (3) add a transform stream in the transport. Whichever you choose, apply it as a format in the logger constructor so every transport inherits it — don't apply it per-transport.
  - Discover which logger the repo already uses before adding a second one. The mechanism differs; the principle — identify the keys, configure centrally, verify in a test — is the same.
- **Error responses are an output sink — shape them.** Return a generic message + a correlation id to
  the client; keep the stack trace, query, and internal detail server-side only. A raw DB/driver error
  echoed to the response can carry connection strings or query text. (Output-shaping discipline:
  `input-output.md`.)
- **Don't put secrets in URLs/query strings** — they land in access logs, proxy logs, browser history,
  and `Referer` headers. Use headers or the request body.
- **Watch error-tracking / APM.** Sentry-style tools capture request context and local variables by
  default — enable their PII/secret scrubbing so you don't ship credentials to a third party.

---

## .env hygiene

- **`.env*` is git-ignored** — verify `.gitignore` covers `.env`, `.env.local`, `.env.*.local`. The
  common miss is committing `.env.production` or a `.env.local` that slipped in before the ignore rule.
- **Commit `.env.example` with keys but no values** — documents what the app needs (and pairs with the
  env schema as the contract) without shipping a single real secret. Placeholders only.
- **If a secret was ever committed, rotate it.** `git rm` doesn't help — it's in history and on every
  clone. Rotate the credential first, then optionally scrub history. Removal without rotation is theater.
- **Scan before commit.** A secret-scanner (gitleaks, trufflehog, or the platform's push protection) in
  pre-commit/CI catches the paste before it reaches the remote. Dependency/package-level scanning is
  `supply-chain.md`; committed-secret scanning is owned here.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern                                                             | Fix                                                              |
| ------------------------------------------------------------------ | --------------------------------------------------------------- |
| Raw `process.env.X` read scattered outside the env module          | Read from the validated env schema (`env.ts`/`config.ts`)       |
| App boots with a missing/malformed required secret                 | Schema validates + throws at startup                            |
| Secret value behind a public prefix (`NEXT_PUBLIC_`/`VITE_`/etc.)  | Move server-side; proxy the call through a route handler        |
| Sensitive value needed client-side, exposed directly               | Keep secret on server; client calls your endpoint              |
| Secret hardcoded in source / config / VCS                          | Move to env schema + managed store; rotate it                   |
| `.env*` not in `.gitignore` / a real `.env` committed              | Ignore it; rotate any committed secret; scrub history           |
| `.env.example` contains real values                                | Replace with placeholder keys only                              |
| Full request / headers / config / caught error logged              | Redact at the logger; mask credential-shaped strings           |
| Stack trace, query, or driver error echoed in an HTTP response     | Generic message + correlation id; detail stays server-side      |
| Secret passed in a URL/query string                                | Move to a header or the request body                           |
| Error-tracker/APM capturing request context with no scrubbing      | Enable the tool's PII/secret scrubbing                         |
| Secret read at build time but expected to be rotatable at runtime  | Read at runtime in the request/handler path; verify the bundle  |
| One shared key across environments or one god-key for everything   | Per-environment, least-privilege scoped secrets                 |

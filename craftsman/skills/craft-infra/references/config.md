# Config

Every environment variable your process reads is a contract with the deployment environment. Break it — ship without a required var, mistype a name, let an optional var silently default to `undefined` — and you get a runtime 500 at the worst possible moment instead of a refused startup at the best. **Parse every env var through a validated schema at process startup, fail closed on any missing or malformed required value, and hand the rest of the code a typed config object — never `process.env` scattered through the codebase.**

> **Scope split.** This file owns the *validation and structure* mechanics: schema location, parse-at-boundary, typed config object, and environment-tier separation. The *values themselves* — secret rotation, never-logging secrets, never shipping secret values to the client — belong to **`craft-security`** → `secrets.md`. How you wire build-time substitution (replacing env vars in a static bundle, `NEXT_PUBLIC_*`, Vite's `import.meta.env`) is part of the build boundary — see `build-release.md`. CI environment secrets (injecting vars into pipeline steps) are in `ci-cd.md`. Runtime health that reports on config completeness at the `/ready` endpoint is in `runtime-health.md`.

---

## Contents

- [Parse at the boundary, once](#parse-at-the-boundary-once)
- [Schema location and shape](#schema-location-and-shape)
- [Fail closed — refuse to start, not silently default](#fail-closed--refuse-to-start-not-silently-default)
- [Typed config object, not scattered process.env](#typed-config-object-not-scattered-processenv)
- [Environment-tier separation](#environment-tier-separation)
- [Client vs server boundary](#client-vs-server-boundary)
- [Testing against config](#testing-against-config)
- [Email deliverability: DNS and auth records](#email-deliverability-dns-and-auth-records)
- [Cost guardrails: billing alerts and spend caps](#cost-guardrails-billing-alerts-and-spend-caps)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Parse at the boundary, once

The boundary is the single file (or module) that runs before anything else and owns `process.env`. Every other module imports from that file; none reads `process.env` directly. This is the same "parse, don't validate" instinct that **`craft-backend`** → `validation.md` applies to request input: coerce untrusted input into a typed value once, at the entry point, so the rest of the system works with guaranteed types.

The consequence of parsing at the boundary:

- A typo in a variable name (`DATABASE_ULRS` vs `DATABASE_URL`) surfaces as a schema error at startup, not a `TypeError: Cannot read properties of undefined` three call frames into a request handler.
- A numeric variable that arrives as a string (always, from `process.env`) is coerced once; consuming code gets a `number`, not `"3000"` silently passing a `=== 3000` check.
- The schema is the canonical documentation for what the process needs — one place to read, one place to update.

**Discover before adding.** Many repos already have a `src/env.ts`, `lib/config.ts`, or a `zod`-based schema in `src/lib/env.mjs` (Next.js's `@t3-oss/env-nextjs` is common). Find it with a quick `find . -name "env.ts" -o -name "config.ts"` and a `grep -r "process.env" --include="*.ts" -l`. Extend the existing schema; don't add a second one.

---

## Schema location and shape

Put the schema in a single dedicated file at a predictable path — `src/env.ts`, `config/env.ts`, or `lib/env.ts` are all fine; pick the one that matches the repo's conventions. The file should do exactly three things:

1. Define the schema (required fields, optional fields with defaults, types, and any refined constraints).
2. Parse `process.env` (or the equivalent: `Deno.env.toObject()`, AWS Lambda (Node.js runtime): also `process.env`, etc.) through the schema.
3. Export the result as an immutable, typed config object — throw or exit if parsing fails.

A concrete example using [Zod](https://zod.dev/) (the most common choice in TypeScript repos; adjust if the repo uses [valibot](https://valibot.dev/), [arktype](https://arktype.io/), or another schema library — discover, don't impose):

```ts
// src/env.ts
import { z } from "zod";

const schema = z.object({
  // Server-only, required
  DATABASE_URL:    z.string().url(),
  AUTH_SECRET:     z.string().min(32),
  // Server-only, optional with default
  PORT:            z.coerce.number().int().min(1024).default(3000),
  LOG_LEVEL:       z.enum(["debug", "info", "warn", "error"]).default("info"),
  // Runtime-tier discriminator
  NODE_ENV:        z.enum(["development", "production", "test"]).default("development"),
});

const parsed = schema.safeParse(process.env);

if (!parsed.success) {
  console.error("Invalid environment configuration:");
  console.error(parsed.error.flatten().fieldErrors);
  process.exit(1);             // fail closed — don't limp on
}

export const env = Object.freeze(parsed.data);
```

Key decisions baked into this shape:

- `z.coerce.number()` — everything from `process.env` is a string; coerce numerics at the boundary.
- `safeParse` + explicit `process.exit(1)` — the error message is human-readable and goes to stderr; the process stops before any request handler registers.
- `Object.freeze` — prevents accidental mutation of top-level properties downstream (shallow freeze; nested objects are still mutable — structural, not security — but a useful lint for flat config shapes).
- **No re-export of `process.env` or the raw object** — only the parsed, typed `env` leaves this module.

---

## Fail closed — refuse to start, not silently default

"Fail closed" means: if a required variable is absent or malformed, the process exits before it binds a port, registers routes, or accepts a connection. A 500 at request time is worse than a startup crash because it fails silently, is hard to trace, and may serve partial responses before collapsing.

Common ways this breaks down in practice — avoid them:

```ts
// BAD: optional chaining hides a missing required var
const db = new Client({ url: process.env.DATABASE_URL ?? "" });

// BAD: default to empty string — connects to nothing, fails on first query
const secret = process.env.AUTH_SECRET || "";

// BAD: the variable is required but marked optional in the schema
DATABASE_URL: z.string().optional()   // now it's string | undefined everywhere
```

The failure mode of a "soft" default is a process that starts, passes health checks, and then throws on the first real operation. That's strictly worse than a refused start, because it looks healthy to the orchestrator.

The exception is genuinely optional config — feature flags, external service URLs that enable an optional integration, tunable timeouts. These belong in the schema as `optional()` or `default(...)` with a documented reason. If the feature degrades gracefully when the var is absent, that's intentional and should be visible in the schema.

---

## Typed config object, not scattered process.env

Once the boundary file exists, the rule for **application and runtime code** is: **nothing outside approved config/bootstrap modules reads `process.env` directly**. All runtime request handlers, services, utilities, and library code import from the config module.

```ts
// WRONG — reads raw env in a route handler
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// RIGHT — validated and typed at startup
import { env } from "@/env";
const stripe = new Stripe(env.STRIPE_SECRET_KEY);
```

Why the exclamation-mark non-null assertion is the tell: it exists to suppress a type error that would have been caught by the schema. Every `process.env.FOO!` in the codebase is a validation that isn't happening.

**Legitimate boundary files that may read `process.env` directly** — these are the known exceptions, not loopholes:

- The env schema module itself (`src/env.ts`, `lib/env.ts`) — this is the boundary; it must read `process.env`.
- Framework config files that run before the app module graph loads: `next.config.ts/js`, `vite.config.ts`, `webpack.config.js`, and equivalent build-tool entry points.
- Instrumentation bootstrap files that run before the module graph: `instrumentation.ts` (Next.js), Sentry's `sentry.server.config.ts`, OpenTelemetry setup.
- Test setup files (`jest.setup.ts`, `vitest.setup.ts`) that configure the test environment.

These files should be explicitly named in the lint allowlist — not granted a blanket pass for the whole directory.

Enforce mechanically if the repo supports it:

- **ESLint rule:** `n/no-process-env` (from `eslint-plugin-n`, the actively maintained community fork of the abandoned `eslint-plugin-node`), or a custom rule that bans `process.env` outside the config module. Add explicit `overrides` entries (or `/* eslint-disable */` with a comment) for each approved boundary file — not a folder-level exclusion that silently grows.
- **`@t3-oss/env-nextjs` / `@t3-oss/env-core`:** These wrappers integrate schema validation into the Next.js build; any component importing from `~/env` gets a fully typed object and the build fails if the schema is unsatisfied. Worth adopting if the repo is on Next.js and doesn't have an equivalent.

---

## Environment-tier separation

Config is not uniform across tiers (development, production, test). Manage the separation explicitly:

- **`.env.example`** (committed) — lists every variable the process needs, with placeholder values and a comment for each. This is the canonical onboarding document. Every real variable added to the schema must have a matching entry here.
- **`.env` / `.env.local`** (gitignored) — developer overrides. Never committed; the `.gitignore` entry is part of the schema setup.
- **`.env.test`** (committed, if the repo uses one) — safe, minimal values for CI/test runs. No real secrets — use stubs or test-doubles. CI injected secrets override these via the platform's secret store (see `ci-cd.md`).
- **Production values** — injected by the deployment platform (Vercel environment variables, Fly.io secrets, Render environment groups, AWS SSM Parameter Store, etc.). They never live in a file on disk. The config schema is the specification; the platform is the injector.

**Never commit `.env` to the repo.** The secret *values* for rotation, auditing, and never-logging belong to **`craft-security`** → `secrets.md`. This file owns the schema that specifies which vars are required — not the values themselves.

Dev-specific defaults belong in `.env.example`, not in the schema's `.default()` calls. A schema default that's a real database URL will silently connect to production if the env var is unset in a non-dev tier.

---

## Client vs server boundary

Many frameworks draw a hard line between variables available in server-side code and variables injected into client bundles (e.g. Next.js `NEXT_PUBLIC_*`, Vite's `import.meta.env.VITE_*`, Create React App's `REACT_APP_*`). This boundary matters for security: a server-only secret (database URL, API signing key) must never be included in the bundle shipped to the browser.

- **Keep server-only secrets out of any client-prefixed namespace.** For why this matters from a secret-value perspective — exposure, rotation after a leak — see **`craft-security`** → `secrets.md`.
- **Separate the schema** if the framework requires it. `@t3-oss/env-nextjs` takes separate `server` and `client` schema maps as input and returns a single typed Proxy object; accessing a server-only key from client code throws at runtime. Next.js itself statically inlines `NEXT_PUBLIC_*` vars into the client bundle at build time — the library validates that those vars are present and correctly typed when the module is first imported, which causes `next build` to fail if a required var is missing. Follow the pattern the framework enforces.
- **The only client-safe values** are public endpoints, feature flags, analytics IDs, and public keys. Everything else is server-only.

See `build-release.md` for how build-time substitution works and where the line is drawn at bundle time.

---

## Testing against config

The schema creates a seam for tests. Don't let tests read production env vars from the developer's shell — that makes tests environment-dependent and breaks CI runners that have no such vars.

Patterns that work:

- **Mock the config module** in unit tests: `vi.mock("@/env", () => ({ env: { DATABASE_URL: "postgres://...", ... } }))`. The typed interface makes the mock exhaustive — TypeScript flags missing fields.
- **`.env.test`** for integration tests: a committed file with safe, real-enough values (pointing at a local/CI test DB) that the framework loads in the `test` tier. CI injects actual secrets over the top via the platform secret store.
- **Never skip validation in tests** by mocking `process.env` directly around the real schema parse — that hides breakage in the schema itself. Test with a known-good config object, not by defeating the validator.

---

## Email deliverability: DNS and auth records

Sending transactional email (password resets, invites, receipts) from a raw domain with no SPF, DKIM, or DMARC records lands in spam — or gets silently dropped by the receiving mailbox provider. The consequence is a launch-killer support nightmare: "password resets never arrive" is one of the fastest ways to lose a new user's trust, and it looks like your app is broken even though the code is fine.

The email provider (Resend, Postmark, SES, etc.) gives you the exact DNS records to add — the job is verifying they're **actually set**, not just pasted into the DNS panel and forgotten. Check with `dig TXT yourdomain.com` (SPF), `dig TXT selector._domainkey.yourdomain.com` (DKIM), `dig TXT _dmarc.yourdomain.com` (DMARC), or the provider's own dashboard verification check — most providers (Resend, Postmark) show a green "verified" state once DNS has propagated and been confirmed. A record pasted into the DNS panel five minutes ago is not verified until the provider or `dig` confirms it resolved.

**DMARC minimum viable posture:** start at `p=none` with a report address (`rua=mailto:...`) configured. This gives visibility into who's sending mail as your domain without breaking legitimate mail — do not jump straight to `p=reject` before you've seen a reporting cycle; that risks blocking your own transactional email if SPF/DKIM alignment isn't fully correct yet.

The bounce/complaint-webhook half of email deliverability — handling provider callbacks so bounced addresses don't get retried forever — belongs to **`craft-backend`** → `side-effects.md`.

## Cost guardrails: billing alerts and spend caps

Every metered provider — cloud hosting, database, LLM/AI APIs, email sending — should have billing alerts configured **before** launch, not after the first surprise invoice. Set a threshold alert (e.g. 50%/80%/100% of expected monthly spend) on each one; discover what the provider offers (AWS Budgets, Vercel spend management, OpenAI/Anthropic usage limits, Resend/Postmark usage alerts) rather than assuming a uniform mechanism.

Use hard spend caps where the platform actually offers them — some do, some don't. Treat this as "use it where available," not a universal guarantee; a billing alert is the fallback everywhere a hard cap isn't offered.

**The failure mode to name explicitly:** an unbounded metered API — an LLM API call is the common case — sitting behind an unauthenticated route is a wallet-drain vulnerability. Anyone can script a loop against your public endpoint and run up your bill with zero effort and no rate limit standing in the way. The fix is rate limiting the route, not just watching the invoice — see **`craft-backend`** → `api-design.md` for the rate-limiting pattern.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| `process.env.FOO` in application/runtime code outside approved boundary files | Import from the validated config module (`@/env`, `lib/env`, etc.); add lint allowlist entries for the approved boundary files (env schema, build config, instrumentation bootstrap, test setup) |
| `process.env.FOO!` non-null assertion anywhere | Non-null assertions suppress the type error that the schema would catch — move the read to the config boundary |
| `process.env.FOO \|\| ""` or `?? ""` on a required var | Mark it required in the schema; fail closed instead of defaulting to empty |
| Required var marked `z.string().optional()` in the schema | Make it required if absence should stop the process; document the degradation path if genuinely optional |
| No `.env.example` in the repo | Add one listing every schema field with placeholder values and a comment |
| `.env` committed to the repo | Remove, rotate any exposed values, add to `.gitignore` immediately — see **`craft-security`** → `secrets.md` |
| Secret value in a client-prefixed var (`NEXT_PUBLIC_*`, `VITE_*`) | Move to a server-only var; see **`craft-security`** → `secrets.md` for rotation steps |
| Schema default is a real service URL or credential | Default to a safe stub or no default; inject real values via the platform |
| No `process.env` lint rule; scattered reads accumulate over time | Add `no-process-env` ESLint rule; use per-file `overrides` to allowlist the env schema, build config, instrumentation bootstrap, and test setup files — not a folder-level exclusion |
| Config parsed inside a request handler or lazily on first call | Parse at module load (top-level, not in a function); startup crashes are better than request-time crashes |
| Test reads from the developer's ambient env vars | Mock the config module or provide a committed `.env.test` with safe stubs |
| Sending domain has no SPF/DKIM/DMARC record, or records were pasted but never verified | Add the provider's DNS records and verify with `dig` or the provider dashboard; set DMARC to at least `p=none` with `rua=` |
| No billing alerts on metered providers (hosting, DB, LLM/API, email) | Set threshold alerts before launch; use hard spend caps where the platform offers them |
| Unauthenticated route calls a metered/LLM API with no rate limit | Add rate limiting to the route — see `craft-backend` → `api-design.md` |

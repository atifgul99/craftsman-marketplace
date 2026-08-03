# Sentry

Sentry is the first observability pillar because it delivers the highest signal per minute of setup time: unhandled errors and unhandled promise rejections surface immediately, with stack traces and release context, without waiting for a user to file a ticket. The discipline: **initialize once with deliberate sampling and PII scrubbing, tag every event with release and environment, and never let the SDK silently swallow events or phone home without a flush on serverless.** Skipping any of these leaves you either blind (events dropped), liable (PII in the cloud), or confused (events from local dev mixing with production data).

> **Scope split.** This file owns Sentry initialization, event capture, PII scrubbing, release tagging, sampling, sourcemap upload, and serverless flush. Structured logs that carry the same `traceId` to correlate with Sentry events belong to `logging.md`. SLO-based alerting built on top of Sentry error rates belongs to `slo-alerts.md`. The serverless flush pattern and why a long-lived-server model differs are covered in `serverless-vs-server.md`.
>
> **See also:** **`craft-backend`** → `error-contract.md` (capture full internal detail in Sentry here; the response envelope the caller gets is a safe, scrubbed shape — those two are separate jobs). **`craft-infra`** → `build-release.md` (the release string and sourcemap upload that land in Sentry are produced during the build/deploy pipeline). **`craft-security`** → `secrets.md` (the Sentry DSN is an environment-specific public ingest identifier — load it from the validated env schema and do not commit it; `SENTRY_AUTH_TOKEN` and any org/project tokens are the actual secrets; also align the `SENSITIVE` field list in `beforeSend` with the keys defined there).

---

## Contents

- [Discover before initializing](#discover-before-initializing)
- [Init pattern](#init-pattern)
- [Capture unhandled errors and rejections](#capture-unhandled-errors-and-rejections)
- [PII scrubbing with `beforeSend`](#pii-scrubbing-with-beforesend)
- [Release and environment tagging](#release-and-environment-tagging)
- [Sampling: `tracesSampleRate`](#sampling-tracessamplerate)
- [Sourcemap upload tied to release](#sourcemap-upload-tied-to-release)
- [Serverless: flush before exit](#serverless-flush-before-exit)
- [Correlating Sentry events with structured logs](#correlating-sentry-events-with-structured-logs)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Discover before initializing

Before touching `Sentry.init`, spend two minutes mapping what exists:

- Is `@sentry/node`, `@sentry/nextjs`, `@sentry/browser`, `@sentry/react`, or another SDK variant already in `package.json`? The SDK surface differs by runtime — use the variant already present or select the right one for the runtime (Node server, browser, React, Next.js, etc.).
- Grep for `Sentry.init` — if it already exists, extend it rather than forking a second call. Multiple `Sentry.init` calls in the same process overwrite each other and are a bug.
- Check for an env schema (`env.ts`, `config.ts`, `.env.example`, a `zod`/`t3-env` schema) — the DSN must come from there, not be hardcoded.
- Check the deployment target (`serverless-vs-server.md`) — it determines whether you need `Sentry.flush()` before exit.

State what you found, then propose the smallest addition that closes the gap.

---

## Init pattern

Call `Sentry.init` exactly once, as early as possible in the process lifecycle — before any other application code runs. In a Node server this means the entrypoint (e.g. `server.ts`, `instrumentation.ts` for Next.js); in a browser bundle this means the root module loaded first.

```ts
// Example: Node.js server (adapt SDK import to match the repo's installed variant)
import * as Sentry from "@sentry/node";
import { env } from "@/env"; // the repo's validated env module — discover its actual path/name

Sentry.init({
  dsn: env.SENTRY_DSN,          // from the validated env module, NOT a raw process.env read or hardcode
  environment: env.NODE_ENV,    // "production" | "staging" | "development"
  release: env.SENTRY_RELEASE,  // e.g. git SHA or semver — tied to sourcemap upload
  tracesSampleRate: 0.1,        // see Sampling section — never 1.0 in production
  beforeSend(event) {
    // Scrubs error/message events. Also wire beforeSendTransaction, beforeSendSpan,
    // and beforeBreadcrumb — see "PII scrubbing" section below. beforeSend alone does
    // not protect transactions, spans, or breadcrumbs.
    return scrubbedEvent(event);
  },
});
```

> **Read config through the validated env module, never raw `process.env`.** The repo-wide rule is
> one typed, validated config object; the only code that touches raw `process.env` is the env
> schema/bootstrap itself (`craft-infra` → `config.md`, `craft-security` → `secrets.md`). A raw-env
> snippet in an observability setup teaches the exact scattered-config drift those skills exist to
> prevent — and risks shipping a runtime-only failure or a secret/public-boundary mistake.

The SDK variant you import must match the runtime. `@sentry/node` uses Node-specific integrations (HTTP, Express/Fastify/Hono hooks); `@sentry/browser` or `@sentry/react` for client-side code; `@sentry/nextjs` wraps both. Importing `@sentry/node` in a browser bundle (or vice versa) ships the wrong integrations and can break.

> **`@sentry/nextjs` is not a drop-in for Node.js worker processes.** When bundled under `--conditions=react-server` (as Next.js RSC builds are), `@sentry/nextjs` tree-shakes out Node-specific exports including `captureException` and `flush`. Any non-Next.js process — a Temporal worker, a BullMQ consumer, a standalone Node server — must import `@sentry/node` directly, regardless of whether it lives inside a Next.js monorepo. Using `@sentry/nextjs` in those processes will produce silent no-ops or import errors at runtime.

---

## Capture unhandled errors and rejections

Modern Sentry SDKs (v7+) wire `uncaughtException` and `unhandledRejection` listeners automatically when you call `init` in a Node process. Verify this is actually happening rather than assuming:

> **Double-reporting risk.** When `Sentry.init` runs in a Node process, it auto-installs `onUncaughtExceptionIntegration` and `onUnhandledRejectionIntegration`, which call `captureException` internally. If application code *also* calls `Sentry.captureException` inside a manual `process.on('uncaughtException', ...)` or `process.on('unhandledRejection', ...)` handler, each event is reported twice. Fix: either remove the manual handler and let Sentry's auto-integrations fire, or disable those integrations in `Sentry.init` and call `captureException` only in the manual handler — not both.

- In Node: in v8+, auto-wiring is provided by `onUncaughtExceptionIntegration` and `onUnhandledRejectionIntegration`, both included in the default integration set. Verify they are not disabled via a custom `integrations` array that omits them.
- In the browser: the SDK attaches `window.onerror` and `window.onunhandledrejection` on `init` — confirm the init call happens before any async work that could reject.
- In frameworks (Express, Fastify, Hono, Koa): the principle is the same across all frameworks — mount the Sentry error-handler **after** all route handlers and **before** any generic error handler, so errors propagate to Sentry before being swallowed. The exact API differs by framework and SDK version:

  - **Express + `@sentry/node` v8+**: request-context capture is handled automatically by the built-in `httpIntegration`; no request-handler middleware is needed. Register the error handler after all routes:
    ```ts
    // Discover the framework in the repo and use its integration
    app.use(routes);
    Sentry.setupExpressErrorHandler(app); // after all routes, before your own error handler
    app.use(myErrorHandler);
    ```
  - **Fastify + `@sentry/node` v8+**: use `Sentry.setupFastifyErrorHandler(app)` after routes are registered.
  - **Hono / Koa and others**: consult the Sentry SDK docs for the framework-specific integration — the pattern follows the same ordering principle (Sentry error handler wraps your routes, your handler runs last).
  - **`@sentry/node` v7 (legacy)**: `Sentry.Handlers.requestHandler()` / `Sentry.Handlers.errorHandler()` — these were removed in v8 and do not exist in v8+.

For manually caught errors that are still worth reporting — e.g. a degraded dependency you handle gracefully but want visibility into — use `Sentry.captureException(err)` with optional scope context:

```ts
try {
  await externalService.call();
} catch (err) {
  Sentry.withScope((scope) => {
    scope.setTag("service", "payment-gateway");
    scope.setContext("request", { orderId });
    Sentry.captureException(err);
  });
  // return safe fallback to the caller
}
```

Pairing this with `craft-backend` → `error-contract.md`: capture the full internal detail in Sentry (stack, context, ids); return the safe envelope to the caller. These are separate concerns and both must be done.

---

## PII scrubbing with `beforeSend`

The Sentry JS SDK routes events through several distinct hooks before they leave the process — not a single `beforeSend` for everything. The hook you need depends on the event type:

- **`beforeSend`** — fires for error and message events. This is the primary PII enforcement point for exceptions.
- **`beforeSendTransaction`** — fires for performance transaction events. Transaction names, span data, and custom attributes attached to transactions pass through this hook, not `beforeSend`.
- **`beforeSendSpan`** — fires for individual spans (v8+). Span descriptions, attributes, and data payloads can carry PII — scrub them here.
- **`beforeBreadcrumb`** — fires when a breadcrumb is added. Breadcrumbs frequently include URL paths, UI element text, and console output that may contain PII.
- **`beforeSendLog`** — fires for log events captured via the Sentry logs integration.

Wire scrubbing hooks for each event type you use. A `beforeSend` alone does not protect transactions, spans, breadcrumbs, or logs. Sentry's cloud receives whatever you send, and a misconfigured hook for the wrong event type leaves PII paths open.

```ts
import type { Event } from "@sentry/core";

function scrubbedEvent(event: Event): Event | null {
  // Drop events from non-production environments if you only want prod noise
  // (alternatively, filter in the Sentry UI — pick a convention and stick to it)
  if (event.request?.data) {
    event.request.data = redactSensitiveFields(event.request.data);
  }
  if (event.request?.headers) {
    // Strip auth headers — Authorization, Cookie, X-API-Key, etc.
    const safe = { ...event.request.headers };
    for (const h of ["authorization", "cookie", "x-api-key", "x-session-token"]) {
      if (safe[h]) safe[h] = "[Filtered]";
    }
    event.request.headers = safe;
  }
  // Drop events containing known PII patterns in extra/contexts if needed
  return event;
}

function redactSensitiveFields(data: unknown): unknown {
  if (typeof data !== "object" || data === null) return data;
  if (Array.isArray(data)) return data.map(item => redactSensitiveFields(item));
  const SENSITIVE = new Set(["password", "token", "secret", "apiKey", "ssn", "creditCard"]);
  return Object.fromEntries(
    Object.entries(data as Record<string, unknown>).map(([k, v]) => [
      k,
      SENSITIVE.has(k) ? "[Filtered]" : redactSensitiveFields(v),
    ])
  );
}
```

Rules:
- **Return `null` from `beforeSend` to drop an event entirely** — useful to suppress known-noisy errors (e.g. browser extension interference, deliberate 4xx responses that aren't bugs).
- **Never redact the stack trace** — it's what makes Sentry valuable. Redact `request.data`, `request.headers`, and `extra`/`contexts` entries that can carry user-supplied input.
- Align the sensitive-field list with `craft-security` → `secrets.md` so the same keys that are never logged are also scrubbed from Sentry events.
- Sentry also has server-side **data scrubbing rules** (project settings → Data Scrubbing) as a backstop. Use them, but don't rely on them as the *first* line — `beforeSend` is in your code, auditable, and runs before the event leaves the machine.

---

## Release and environment tagging

Every event must carry `release` and `environment`. Without them, you cannot filter prod-only errors, cannot link events to a sourcemap, and cannot track whether a deploy resolved a regression.

- **`environment`**: read from `NODE_ENV` or an explicit `SENTRY_ENV` variable. Never default to `"production"` — fail loudly if it is missing. Common values: `production`, `staging`, `preview`, `development`. Filter out `development` in the Sentry UI or suppress it in `beforeSend` so local noise doesn't dilute production data.
- **`release`**: a unique, immutable string per deployed version. The two common forms:
  - **Git SHA** (`git rev-parse --short HEAD`) — cheapest and always correct; set as `SENTRY_RELEASE` during the build.
  - **Semver** (`1.4.2`) — useful when you have explicit versioning; pair with the git SHA in the metadata.
  - `@sentry/nextjs` via `withSentryConfig` auto-detects the release from VCS (git SHA) and injects it into the bundle at build time — check whether `SENTRY_RELEASE` is already wired before adding your own.
- The release string **must match** what is used when uploading sourcemaps (see next section). A mismatch means sourcemaps never resolve.

---

## Sampling: `tracesSampleRate`

`tracesSampleRate: 1.0` in production means every transaction is traced and transmitted — this adds CPU overhead on every instrumented request (span creation and serialization), which can pressure throughput and p99 latency at scale, and will saturate your Sentry quota on any non-trivial traffic level. **Never ship `1.0` to production.**

Guidelines:
- **`tracesSampleRate: 0`** disables performance tracing entirely. Acceptable if you only want error monitoring and haven't budgeted for Sentry's Performance tier.
- **`tracesSampleRate: 0.1`** (10%) is a reasonable default for moderate-traffic services — adjust based on event volume and quota. Monitor Sentry's "Transactions" usage after the first week and tune down if you hit quota.
- **`tracesSampleRate: 1.0`** is only appropriate in development/staging where you want full trace data for debugging, never production.
- For higher-precision sampling, use `tracesSampler` (a function that receives the sampling context) to apply different rates per route — e.g. sample health-check pings at 0, critical checkout paths at 0.5. In v8+, `SamplingContext` exposes `name` directly as a top-level property:

  ```ts
  tracesSampler(samplingContext) {
    if (samplingContext.name === "GET /health") return 0;
    if (samplingContext.name?.startsWith("POST /checkout")) return 0.5;
    return 0.05; // everything else: 5%
  },
  ```

- **Trace sampling does not control error events** — `tracesSampleRate` applies only to performance/tracing transactions and has no effect on error capture. Error events are governed separately by `sampleRate` (the event sample rate, distinct from the trace sample rate), `beforeSend` return values, transport failures, rate limits, and whether the SDK is enabled. Do not assume errors are always sent — verify that `sampleRate` is not set below 1.0 in production, that `beforeSend` does not drop events unintentionally, and that transport-level errors are surfaced.

---

## Sourcemap upload tied to release

Without sourcemaps, Sentry shows minified stack frames — line 1, column 47283, function `a`. With them, it shows your original source, file path, and line number. This is non-negotiable for any minified/transpiled codebase.

The upload must happen in CI/CD as part of the build that produces the deployable, and the `release` string used here must exactly match `Sentry.init`'s `release`:

```bash
# Sentry CLI — typically run after build, before deploy
npx @sentry/cli releases new "$SENTRY_RELEASE"
npx @sentry/cli sourcemaps upload --release "$SENTRY_RELEASE" --url-prefix '~/' ./dist
npx @sentry/cli releases finalize "$SENTRY_RELEASE"
```

Framework-specific alternatives (discover which applies):
- **Next.js + `@sentry/nextjs`**: the Sentry webpack/turbopack plugin uploads sourcemaps automatically during `next build` when `SENTRY_AUTH_TOKEN` is set — no CLI calls needed if the plugin is configured.
- **Vite**: `@sentry/vite-plugin` integrates directly.
- **esbuild / Rollup / other bundlers**: `@sentry/cli` or the appropriate Sentry bundler plugin.

Keep sourcemaps out of the public bundle — they expose your original source to anyone who fetches them. Upload to Sentry, then **delete the `.map` files before deploying the static assets** (or set the bundler to not emit them to the public directory). See `craft-infra` → `build-release.md` for where this step lives in the deploy pipeline.

---

## Serverless: flush before exit

In a long-lived server process, the Sentry SDK queues events in a background transport and flushes them asynchronously — events are sent even if they're captured just before the process idles. In a serverless function (AWS Lambda, Vercel Functions, Cloudflare Workers, Fly Machines in scale-to-zero mode), the process is **frozen or killed** at the end of the invocation, before that background queue drains. Events captured in the last milliseconds of a function invocation are silently dropped.

The fix: await `Sentry.flush()` before returning from the handler, with a bounded timeout so a Sentry outage can't stall your function indefinitely:

```ts
// Lambda / Vercel Node handler example — uses @sentry/node
export const handler = async (event: LambdaEvent): Promise<LambdaResult> => {
  try {
    return await doWork(event);
  } catch (err) {
    Sentry.captureException(err);
    throw err;
  } finally {
    await Sentry.flush(2000); // 2 s max; don't block indefinitely
  }
};
```

The `finally` block ensures events captured on the happy path (via `captureException`, breadcrumbs, or manual spans inside `doWork`) are also flushed before the Lambda process is frozen — not only events from the error path.

For **Cloudflare Workers**, use `@sentry/cloudflare` (not `@sentry/node` — Workers run on V8 isolates without Node APIs). The `@sentry/cloudflare` SDK wraps the handler with `withSentry()` for initialization and uses `ctx.waitUntil` to flush in the background after the response is sent:

```ts
// Cloudflare Workers — @sentry/cloudflare
import { withSentry } from "@sentry/cloudflare";

export default withSentry(
  (env) => ({ dsn: env.SENTRY_DSN, tracesSampleRate: 0.1 }),
  {
    async fetch(request, env, ctx) {
      // your handler logic
    },
  }
);
```

For **Vercel Edge** functions (V8 isolate, not Node), use `@sentry/vercel-edge` or `@sentry/nextjs` — the `ctx.waitUntil(Sentry.flush(2000))` pattern applies there but again requires the correct SDK variant, not `@sentry/node`.

See `serverless-vs-server.md` for a broader treatment of how the serverless lifecycle changes observability contracts.

---

## Correlating Sentry events with structured logs

Sentry events and structured log lines are most useful when they reference each other. The bridge is the Sentry **trace ID** (and the `spanId` within a trace), which Sentry sets on the active span context.

- **Propagate the Sentry trace/span ids into your logger** so every log line during a request carries the same ids as the Sentry event captured for that request:

  ```ts
  import { getTraceData } from "@sentry/node";

  function getTraceContext(): { traceId?: string } {
    const { "sentry-trace": st } = getTraceData();
    // sentry-trace format: <traceId>-<spanId>-<sampled>
    const traceId = st?.split("-")[0];
    return traceId ? { traceId } : {};
  }

  // When logging, merge getTraceContext() into the log object
  logger.error({ ...getTraceContext(), err }, "Payment gateway timeout");
  ```

- **Use `Sentry.addBreadcrumb`** to record significant steps within a request before an error — breadcrumbs appear inline in the Sentry event and reduce the need to correlate with logs manually for common flows.
- The structured-log side of this pattern (how the logger is configured to accept and emit `traceId`) is `logging.md`'s concern. This file's job is ensuring the Sentry side emits a stable, correlatable trace id.

---

## OTel + Sentry traceId reconciliation

Sentry v8+ is itself built on OpenTelemetry — internally, it runs its own OTel tracing/span
pipeline. Trace-id disagreement only shows up when the application **also** runs a separate,
independent OTel SDK (a `NodeSDK` instance) alongside Sentry: now there are two competing OTel
pipelines, each minting its own trace id, and logs (tied to one pipeline) disagree with Sentry
events (tied to the other).

**If Sentry is the only OTel instrumentation in the process** (no separate `NodeSDK`), there is
nothing to reconcile — there's only one provider, so ids already agree.

**If the app runs its own `NodeSDK` alongside Sentry**, the fix is to stop Sentry from starting a
second, competing OTel pipeline and instead register Sentry's OTel pieces onto the app's own
`NodeSDK`, so both share one pipeline and one trace id:

- Set `skipOpenTelemetrySetup: true` in `Sentry.init()` — Sentry no longer sets up its own OTel SDK.
- Manually register `SentryPropagator`, `SentrySampler`, and `SentrySpanProcessor` (all from
  `@sentry/opentelemetry`) on your `NodeSDK`.

```ts
import * as Sentry from '@sentry/node';
import { NodeSDK } from '@opentelemetry/sdk-node';
import {
  SentryPropagator,
  SentrySampler,
  SentrySpanProcessor,
} from '@sentry/opentelemetry';

// 1. Sentry.init first, with skipOpenTelemetrySetup so it doesn't spin up its own OTel pipeline.
Sentry.init({
  dsn: env.SENTRY_DSN,
  skipOpenTelemetrySetup: true,
  // ... other options
});

// 2. Register Sentry's OTel pieces on your own NodeSDK so both share one pipeline/trace id.
const sdk = new NodeSDK({
  textMapPropagator: new SentryPropagator(),
  sampler: new SentrySampler(Sentry.getClient()!),
  spanProcessors: [new SentrySpanProcessor()],
  // ... your instrumentations
});

sdk.start();
```

**Wiring checklist:**

- [ ] Confirm whether the app runs its own `NodeSDK` separate from Sentry — if not, there's nothing
  to wire; skip this section.
- [ ] If it does, set `skipOpenTelemetrySetup: true` in `Sentry.init()` and register
  `SentryPropagator`, `SentrySampler`, and `SentrySpanProcessor` (from `@sentry/opentelemetry`) on
  the app's `NodeSDK`.
- [ ] Check initialization order: when running your own `NodeSDK`, `Sentry.init()` should run
  before `sdk.start()` only insofar as `SentrySampler` needs `Sentry.getClient()` to exist — in
  practice, call `Sentry.init()` first, then construct and start the `NodeSDK` with the Sentry
  pieces wired in, so the `NodeSDK`'s provider is the one both sides attach to.
- [ ] After wiring, emit a test log line and a test Sentry event in the same request. Confirm the
  `traceId` in the log matches the trace id shown in the Sentry event's "Trace" tab.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Raw `process.env.*` read in Sentry/observability setup | Import the repo's validated env module (`env.*`); raw `process.env` belongs only in the env-schema/bootstrap boundary (`craft-infra` → `config.md`) |
| `Sentry.init` called more than once in the same process | Remove duplicates; init exactly once at process entry |
| DSN hardcoded in source | The DSN is a public ingest identifier, not an auth secret, but it is environment-specific config — load it from the validated env schema (env var), never commit it. Keep `SENTRY_AUTH_TOKEN` and org/project tokens in the secret store (`craft-security` → `secrets.md`). |
| No `environment` set, or defaults silently to `"production"` | Read from env var; fail loudly if absent |
| No `release` set | Build pipeline must set `SENTRY_RELEASE` to git SHA or semver; must match sourcemap upload |
| `tracesSampleRate: 1.0` in production config | Lower to ≤ 0.1 (or use `tracesSampler` per route); 1.0 saturates quota |
| No `beforeSend` hook, or hook doesn't scrub auth headers / request body | Add `beforeSend`; filter `authorization`, `cookie`, request body sensitive fields |
| `beforeSend` strips stack traces | Only scrub `request.data`, `request.headers`, `extra` — never the exception/stacktrace |
| Sourcemaps committed to the public deploy directory | Upload to Sentry via CLI/plugin; delete `.map` files before deploying public assets |
| Sentry release string doesn't match sourcemap upload release | Use the same `$SENTRY_RELEASE` value in both `init` and the upload step |
| Serverless handler returns/throws without `await Sentry.flush()` | Add `await Sentry.flush(2000)` before the function exits; or use `waitUntil` on edge |
| Sentry error handler middleware added before route handlers (Express/Fastify) | Move error handler after all routes. **v8+:** no request-handler middleware is needed — `httpIntegration` handles request context automatically; use only `Sentry.setupExpressErrorHandler(app)` after all routes. **v7 (legacy):** `Sentry.Handlers.requestHandler()` before routes, `Sentry.Handlers.errorHandler()` after — these APIs were removed in v8. |
| Development events mixing with production data in Sentry | Filter `environment !== "production"` in `beforeSend` or use Sentry environment filters |
| `captureException` called without scope context on recoverable errors | Add `withScope` + `setTag`/`setContext` to attach request/operation context |
| No correlation between Sentry trace id and structured log lines | Use `getTraceData()` from `@sentry/node` to extract the trace id and merge into each log object (`logging.md`) |

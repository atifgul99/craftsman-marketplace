# Structured Logging

Every log line in production is a query waiting to be run — and the query only works if the schema is consistent. The discipline: **one JSON object per event, a stable `traceId`/`requestId` on every line, honest log levels, and zero secrets and no raw PII unless explicitly required, classified, and approved by policy.** Systems that log freeform strings or skip the request id make incident response a grep exercise instead of a filter.

> **Scope split.** This file owns the *shape and discipline* of log lines: JSON structure, trace propagation, level semantics, redaction, and the log-vs-metric-vs-trace decision. Error *capture and grouping* (Sentry, sourcemaps, release tagging) is `sentry.md`; alert routing and burn-rate thresholds ride on metrics in `slo-alerts.md`; dashboard panels that surface log-derived metrics belong in `grafana.md`. Secret hygiene at rest and in transit is owned by **`craft-security`** → `secrets.md` — this file is the logging-specific application of that rule (never log a secret or raw PII). Log injection from untrusted input is covered in **`craft-security`** → `input-output.md`. Structured errors as a contract between services (error codes, HTTP status mapping) are covered in **`craft-backend`** → `error-contract.md`; side-effect logging around external calls (retries, timeouts) in **`craft-backend`** → `side-effects.md`.

---

## Contents

- [One logger, centrally configured](#one-logger-centrally-configured)
- [Structured JSON: the required fields](#structured-json-the-required-fields)
- [Trace and request id propagation](#trace-and-request-id-propagation)
- [Log levels used honestly](#log-levels-used-honestly)
- [Redaction: secrets and PII](#redaction-secrets-and-pii)
- [Structured error logging](#structured-error-logging)
- [Request lifecycle events](#request-lifecycle-events)
- [Log vs metric vs trace](#log-vs-metric-vs-trace)
- [Sampling high-volume logs](#sampling-high-volume-logs)
- [Quick-reject checklist](#quick-reject-checklist)

---

## One logger, centrally configured

Discover before adding: `grep` the repo for `pino`, `winston`, `bunyan`, `log4js`, a cloud-native client (`@google-cloud/logging`, `@aws-lambda-powertools/logger`, `@vercel/otel`), or any wrapper around `console` that serializes JSON. Extend the existing logger; don't fork it.

- **A single logger instance, initialized once**, configured from the validated env schema (not from a raw `process.env` read in every file). Import and call the instance — don't re-initialize per module.
- **Never `console.log` in production code.** `console.log` is unstructured, bypasses the log level gate, and goes to stdout without a schema — it cannot be reliably parsed or filtered by log aggregators (Datadog, CloudWatch, Loki, GCP Logging). Replace it with the structured logger; keep `console.*` in scripts and CLIs where it's intentional.
- **The logger's transport is the runtime's concern.** In a long-lived Node server, write to stdout and let the platform collect it. Node-runtime serverless (AWS Lambda, Vercel Node Functions) supports the same stdout-to-JSON pattern; confirm the platform captures it. **V8-isolate / edge runtimes — Vercel Edge and Cloudflare Workers — are not Node**: there is no `process.stdout`, so emit via `console.log(JSON.stringify(event))` (the platform captures `console`) or pino's browser mode (`{ browser: { asObject: true } }`), and verify capture. See `serverless-vs-server.md` for runtime-specific gotchas.
- **Log level is configuration, not code.** Set it via an env variable (`LOG_LEVEL=info`); don't hardcode `'debug'` in the logger init. `debug` in production floods aggregators and increases cost; `error`-only in staging hides problems before they hit prod.

---

## Structured JSON: the required fields

Every log event must be a single JSON line. The minimum required schema:

```jsonc
{
  "timestamp": "2026-06-19T14:32:01.123Z",  // ISO 8601 UTC — let the logger set this
  "level": "info",                            // one of: debug | info | warn | error | fatal
  "traceId": "abc123def456",                 // stable for the request lifetime (see below)
  "message": "user.invoice.created",         // dot-namespaced event name, not a sentence
  "service": "billing-api",                  // name of the service/app emitting the line
  // ...domain fields specific to the event
  "invoiceId": "inv_xyz",
  "durationMs": 42
}
```

**Guidelines for the shape:**

- **`message` is an event name, not a narrative.** `"user.invoice.created"` survives a schema change and is groupable; `"Created invoice for user John"` is a one-off string that requires regex to aggregate. Dot-namespaced names (`<domain>.<entity>.<verb>`) index well in every aggregator.
- **Domain fields go at the top level, typed correctly.** `durationMs` is a number, not `"42ms"` — aggregators can average numbers; they can't average strings. Nest only for genuinely nested data structures (don't flatten an address into `address_street`, `address_city`, etc.).
- **Prefer allowlisting fields** rather than spreading an entire object. A `user` object with 30 fields — some sensitive — should become `{ userId, email }` (or just `userId` if email is PII your platform doesn't need indexed). Spreading is the fastest path to accidentally logging a secret.
- **Keep lines short enough to be readable.** If an event's context fills more than a few hundred characters of JSON, ask whether all of it belongs in a log line or whether some belongs as a span attribute in a trace (see [Log vs metric vs trace](#log-vs-metric-vs-trace)).

---

## Trace and request id propagation

A log line without a `traceId` is an orphan — you can find it in isolation but you can't reconstruct the request timeline around it. A stable `traceId` on every line turns a set of log lines into a story.

**How to propagate it — two paths, pick based on the repo:**

**If using OTel SDK with PinoInstrumentation:** `traceId` and `spanId` are injected into every
Pino log record automatically by `@opentelemetry/instrumentation-pino`. Do not also inject a
`traceId` manually (e.g. via `logger.child({ traceId })` or `Sentry.getTraceData()`) — a manual
injection will produce a different id than the OTel id and break log-to-trace correlation. Verify
by emitting a log line inside an active span and confirming the `traceId` matches the span's id.
See `otel-integration.md` for the full wiring and for the Sentry/OTel id-reconciliation pattern.

**If NOT using OTel SDK:** inject a request-scoped UUID via `AsyncLocalStorage`:

1. **Generate at the request boundary.** In an HTTP server, the first middleware generates a `requestId` (UUID v4 or a nanoid) if none arrives in the incoming headers (e.g. `X-Request-Id`, `X-Trace-Id`). If a value arrives in a trusted upstream header, forward it; don't re-generate.
2. **Carry it through async context.** Use `AsyncLocalStorage` to bind the id to the request context so every call in the request can read it without threading it as a parameter. Frameworks like Fastify expose request-scoped child loggers; use those.
3. **Emit as a child logger.** Instantiate a child logger at request ingress with the `traceId` bound as a default field. Every log call from that child inherits the field without manual passing:

   ```ts
   // at middleware — illustrative, adapt to the repo's logger (pino, winston, etc.)
   const reqLogger = logger.child({ traceId: requestId, path: req.url, method: req.method });
   req.log = reqLogger; // attach to request context
   ```

4. **Return the id to the caller** in the response header (`X-Request-Id: <id>`) so support can relay it for incident lookup.
5. **Include it in outbound calls.** When calling downstream services, propagate the id as a request header. This links logs across service boundaries — the same `traceId` threading through a distributed trace.

This manual path is only appropriate when OTel is absent — if OTel is wired, remove the manual UUID path and rely on `PinoInstrumentation` injection.

---

## Log levels used honestly

A log level is a contract about how often an on-call engineer expects to see that line and what action it implies. Abusing levels defeats filtering and alert routing.

| Level | Meaning | Action required |
| --- | --- | --- |
| `debug` | Verbose diagnostic detail for development/tracing | Off in production by default; on only during active debugging |
| `info` | A normal, expected business event (request completed, job finished, user signed up) | None — it's the baseline record |
| `warn` | Something unexpected that the system handled gracefully — a fallback was used, a retry succeeded, a deprecated path was hit | Worth aggregating; high warning rate may precede errors |
| `error` | An operation failed in a way the system could not self-heal — a request failed, a job errored out, a dependency returned an unrecoverable response | Should page if it happens at frequency; every `error` line is a candidate for a Sentry event |
| `fatal` | The process cannot continue and is about to exit | Triggers an immediate alert and a process restart |

**Common abuses to reject:**

- `error` used for "this was unexpected but we returned a 200 anyway" — if it was handled, it's `warn`.
- `info` used for every line of a tight loop — that's `debug` or a metric, not a log event.
- `warn` suppressed because "there are too many" — too many warnings is the signal; silence is not the fix.
- Different levels for the same logical event in different code paths — log level should reflect the *outcome*, consistently.

---

## Redaction: secrets and PII

A log aggregator is not a secrets store. Every field you log is potentially visible to: every engineer with log access, every third-party log-aggregation vendor, and every attacker who gains read access to the logging backend.

**Never log:**
- Secrets: API keys, tokens, passwords (raw or hashed), private keys, session cookies, OAuth codes. (Hashed passwords are not PII but are sensitive credential material — never log them.)
- Raw PII that doesn't need to be indexed: full card numbers, SSNs, full addresses when only a city matters.
- Entire request/response bodies by default — they will contain the above.

**The pattern:** log identifiers, not values. `userId` instead of `{ name, email, phone }`. `invoiceId` instead of the full invoice object. If the platform's support workflow needs the email for lookup, verify it's permitted by your data policy and the logging vendor's DPA before indexing it.

**Implement structural redaction, not string scrubbing.** String-search-and-replace on the serialized JSON misses nested keys, URL-encoded values, and base64-encoded payloads. Instead:

- Allowlist the fields you log, not blocklist the ones you don't.
- If you must log a partially-redacted value (e.g. last four of a card), apply the mask before logging, at the model layer, not in a post-serialization hook.
- Use the logger's built-in redaction if available (Pino's `redact` option takes ECMAScript-style dot-notation paths (e.g. `"user.password"`, `"headers[*].authorization"`) — not JSONPath — and replaces matched fields with `[Redacted]` before serialization).

**Headers and query strings are high-risk.** If you log the full `Authorization` header or a `token=` query param, you've logged a credential. Either strip the header block before logging, or apply a per-key redactor to the headers object.

See **`craft-security`** → `secrets.md` for the broader secrets discipline (storage, rotation, env loading). See **`craft-security`** → `input-output.md` for log-injection risks. Note on scope: when using a proper structured JSON logger (Pino, Winston with JSON transport, etc.) the serializer escapes newlines and special characters inside string field values, so a newline in a single field does not split the JSON line into multiple log records. Log injection via newline splitting is primarily a risk with raw string interpolation, hand-built JSON, or unsafe/custom serializers. **Never construct log lines by string concatenation** — always pass untrusted values as typed field values to the structured logger, not interpolated into the message string or key names.

---

## Structured error logging

When catching an error, the log event must carry enough context for an on-call engineer to
reproduce and diagnose without replaying the request. A plain `logger.error(err.message)` is the
minimum — and it's not enough.

**`error` is for system failures, not expected outcomes.** The example below is a gateway timeout —
the system failed. A declined card, a rejected upload, or a validation failure is the system working
correctly on bad input: record the outcome code, count it as a metric, and keep it out of the error
tracker, or genuine bugs drown in customer mistakes. Level follows the outcome rules below — `warn`
at the catch site, or no line at all when the structured response already carries it, and `info` on
the operation's own completion event. See
`operational-readiness.md § Instrument the lifecycle` for the same split applied to background work.

**Required fields on every error log event:**

```jsonc
{
  "level": "error",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "service": "billing-api",
  "msg": "payment.charge.failed",             // event name, not the raw error message
  "err": {
    "type": "PaymentGatewayError",            // err.constructor.name or err.name
    "message": "Gateway timed out after 10000ms",
    "code": "GATEWAY_TIMEOUT",                // err.code if present — stable identifier for alerting
    "stack": "Error: Gateway timed out ...\n  at ..."  // include in non-prod; evaluate data-policy in prod
  },
  "userId": "usr_abc123",                     // who — use identifiers, not PII
  "invoiceId": "inv_xyz",                     // what entity
  "attemptNumber": 2,                         // retry context if relevant
  "durationMs": 1240                          // how long the failing operation ran
}
```

**The pattern:**

```ts
// Wrap the error in a typed object — never pass the error directly as the message.
// Pick the level from the outcome, not from the fact that something was thrown:
// a decline is the system working, a retry that hasn't exhausted isn't final yet.
try {
  await chargeCard(invoice);
} catch (err) {
  const event = {
    msg: 'payment.charge.failed',
    err: {
      type: err instanceof Error ? err.constructor.name : typeof err,
      message: err instanceof Error ? err.message : String(err),
      code: (err as { code?: string }).code,
      stack: err instanceof Error ? err.stack : undefined,
    },
    userId,
    invoiceId,
    attemptNumber,
    durationMs: Date.now() - startTime,
  };

  if (isExpectedOutcome(err)) {
    // Declined card, invalid input — the system did its job. Count it; don't page on it.
    logger.info({ ...event, msg: 'payment.charge.declined', err: { ...event.err, stack: undefined } });
  } else if (willRetry) {
    logger.warn(event);   // transient and not final — see the level rules below
  } else {
    logger.error(event);  // system failed and retries are exhausted
  }
  throw err; // re-throw or convert to your error envelope
}
```

`isExpectedOutcome` is whatever your code already knows: a declined-payment error class, an HTTP 4xx
from the provider, a validation result. If nothing in the code can tell an expected outcome from a
system failure, that gap is the finding — fix the classification before tuning the logging.

**Stack traces in production:** whether to include `stack` in production logs is a data-policy
call, not a technical one. Stack frames may contain file paths that reveal internal structure.
The common practice: always include `err.name`, `err.message`, and `err.code`; gate `err.stack`
on `NODE_ENV !== 'production'` or log it only when a Sentry event can't be correlated. If you
send errors to Sentry, the stack is captured there — you don't need it duplicated in every log
line at prod volume.

**Error log levels are outcome-based:**
- Operation failed and could **not** self-heal → `error`
- Operation failed but a fallback succeeded → `warn`
- An expected error condition the caller should handle (e.g. 404, validation failure) → `warn`
  or skip the log entirely and return a structured error response
- Third-party service returned a retryable error and you're retrying → `warn` on the attempt,
  `error` only if all retries exhaust

**Do not log the same error twice.** Log once at the catch site with full context, then re-throw
(or convert). A higher-level error handler that logs again produces duplicate lines with half
the context. Decide whether the catch site or the global handler owns the log event — not both.
See `sentry.md` for Sentry correlation; `craft-backend → error-contract.md` for the safe error
envelope contract.

---

## Request lifecycle events

For HTTP services, two structured log events anchor the per-request story: one at entry (or on
completion) with status and duration, and targeted events inside for work that warrants its own
record. Avoid logging every internal step as separate `info` events — a single completion log
with `durationMs` and `statusCode` is searchable and cheaper than a dozen per-request lines.

**HTTP request completion event (the minimum):**

```jsonc
{
  "level": "info",
  "msg": "http.request.completed",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "service": "billing-api",
  "method": "POST",
  "path": "/invoices",                         // normalized path — not the raw URL with query params
  "statusCode": 201,
  "durationMs": 87,
  "contentLengthBytes": 420,                   // response body size if available
  "userId": "usr_abc123"                       // identity if authenticated
}
```

Most frameworks/logging middlewares emit this automatically — verify one is wired before adding
a manual one. Pino-http produces exactly this shape:

```ts
import pinoHttp from 'pino-http';
app.use(pinoHttp({
  logger,
  customSuccessMessage: () => 'http.request.completed',
  customErrorMessage: () => 'http.request.failed',
  customProps: (req, res) => ({
    userId: (req as AuthedRequest).user?.id,
  }),
  // Redact sensitive headers before they reach the log
  redact: ['req.headers.authorization', 'req.headers.cookie'],
  // Suppress health-check noise
  autoLogging: {
    ignore: (req) => req.url === '/health' || req.url === '/ping',
  },
}));
```

**What belongs in the completion event vs a separate event:**

| Log here (completion event) | Log as a separate event |
| --- | --- |
| `statusCode`, `durationMs`, `method`, `path` | `payment.charge.initiated` (meaningful business operation start) |
| Identity (`userId`, `tenantId`) | `payment.charge.failed` (error at an inner step — see above) |
| Request size, response size | `cache.miss` at `debug` (diagnostic, not a business event) |
| Auth outcome (`authenticated: true`) | `external.api.call.slow` at `warn` (latency threshold breach) |

**Long-running operations:** for jobs, queue consumers, or batch processes, emit an `info` event
at start with the job id and context, then a completion/error event with `durationMs`. Skip
progress events unless they are genuinely distinct business milestones (don't log every row
processed in a 10k-row import).

**OTel severity numbers:** the OTel Log Data Model defines numeric severity sub-ranges within each
level — INFO has four sub-slots (INFO=9, INFO2=10, INFO3=11, INFO4=12). Standard `info`/`warn`/
`error` log calls map to the base value (9, 13, 17) in OTel-wired pipelines. Any log record with
OTel `SeverityNumber >= 17` (ERROR or higher) is machine-identifiable as an erroneous situation —
alerting pipelines can threshold on this without parsing the `level` string.

---

## Log vs metric vs trace

Logs, metrics, and traces serve different questions. Using the wrong signal for the question makes the system harder to operate, not easier.

| Signal | Question it answers | When to use it |
| --- | --- | --- |
| **Log** | What happened in this specific request or job? | Discrete events: a request completed, a payment failed, a job skipped a record |
| **Metric** | What is the rate / count / distribution over time? | Request throughput, error rate, latency percentiles, queue depth |
| **Trace** | Where did the time go across service/function boundaries? | Latency breakdown, identifying which downstream call is slow |

**Do not use logs as a metrics workaround.** Writing a log line on every cache hit to count cache hits, then querying the log aggregator to sum them, is expensive and imprecise — use a counter metric. Conversely, a `counter.increment('requests')` metric doesn't tell you *which* request failed at 03:14 — that's what a log event is for.

**Boundaries that reviewers enforce:**

- High-cardinality data (user id, request id, individual URL paths) belongs in a **log or trace span**, not a metric label. A metric with a user-id label creates a near-infinite label set, which kills most metric stores (Prometheus, VictoriaMetrics, Mimir) — see `grafana.md` for label cardinality limits.
- SLO burn-rate alerts ride on **metrics** (request success rate, latency histograms), not on log-query alerts — log queries have higher latency and cost. Wire the metric first; use log queries for drill-down. See `slo-alerts.md`.
- Distributed latency breakdown — "the API call took 800ms but which service?" — is a **trace** question, not answerable from logs alone even with `durationMs` fields.

---

## Sampling high-volume logs

Not every log line is equally valuable to retain at full volume. At scale, `info`-level logs from healthy high-throughput paths (health checks, CDN-cached assets, polling loops) can dominate ingestion cost without adding operational value.

**Sampling strategies (not mutually exclusive):**

- **Level-based:** disable `debug` in production entirely; `info` through a head-based sampler; `warn`/`error`/`fatal` always at full rate. The sampler should be configurable via env var (`LOG_SAMPLE_RATE=0.1` → 10% of `info` lines).
- **Route-based:** exclude high-frequency low-value routes entirely from standard logging — `/health`, `/ping`, `/favicon.ico`, CDN probe paths. Log them only if they return non-2xx. Most web frameworks let you configure a per-route log filter before the request logger runs.
- **Error-always:** regardless of any sampling rate, a line at `error` or `fatal` level must never be sampled away. Sample-down only `debug` and `info`.
- **Trace-linked sampling:** if OpenTelemetry traces are sampled at the head, log lines in the same request can be kept (trace-driven log sampling) only when the trace is kept — if the trace sampler keeps a trace, the associated log lines for that request are also retained. This requires the log exporter to read the sampling decision from the active span context — check whether the repo's log/OTel integration reads the sampling flag from the span context before designing around it.

**The practical guard:** set a sampling rate that keeps your aggregator bill predictable without losing signal on errors and rare events. Start with 100% `warn`+, 10-50% `info`, 0% `debug` in production, and adjust after a week of data. Document the rate in the logger config so the next engineer knows it isn't zero.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| `console.log(...)` in non-CLI production code | Replace with the structured logger at the appropriate level |
| Log line is a plain string, not a JSON object | Use the structured logger; `message` is an event name, domain context goes as fields |
| No `traceId` / `requestId` on log lines | Attach a child logger at request ingress; propagate via `AsyncLocalStorage` or request-scoped context |
| Log level `error` on a handled, gracefully-recovered event | `warn` — `error` means the operation failed and did not self-heal |
| Log level `info` inside a tight loop or per-item in a batch | `debug` or a metric counter; `info` is for discrete business events |
| Raw secrets, tokens, passwords, or API keys in a log field | Log the identifier only; use the logger's `redact` option or allowlist fields |
| Full request/response body logged unconditionally | Allowlist the fields to log; never spread an untrusted object |
| `Authorization` or `Cookie` header present in logged headers | Strip or redact auth headers before logging |
| User-supplied string concatenated into a log message or key via string interpolation (non-structured logging) | Pass untrusted values as typed fields to the structured logger — never concatenate them into the message string or key names. Proper JSON serializers escape newlines inside field values; injection via newlines is mainly a risk with raw string construction or hand-built JSON (`craft-security` → `input-output.md`). |
| High-cardinality value (userId, URL path) used as a metric label | Move to a log field or trace span attribute; keep metric labels low-cardinality (`grafana.md`) |
| `debug` log level hardcoded in logger init | Set via env var (`LOG_LEVEL`); default to `info` in production |
| `info`-level health-check / polling-loop logs at full rate in prod | Sample or disable for high-frequency low-value routes; always preserve `error`/`fatal` |
| Multiple logger instances initialized per module | Single instance, initialized once in a shared module, imported everywhere |
| Log aggregator used to count rates instead of a metric | Use a counter/histogram metric; log aggregator queries are for event drill-down |
| `logger.error(err.message)` — plain string, no context fields | Log `msg` (event name) + `err.{type,message,code,stack}` + entity ids + `durationMs` |
| Same error logged at both the catch site and the global error handler | Pick one owner — the catch site (with full context) or the global handler, not both |
| `err.stack` logged unconditionally in production | Gate stack on env or Sentry availability — `err.name`, `err.message`, `err.code` are always safe |
| No HTTP request completion log (duration, status, path) | Wire `pino-http` or framework middleware; emit one `http.request.completed` event per request |
| HTTP log includes raw URL with query params (may contain tokens) | Normalize to path only (`req.url.split('?')[0]`); query params go through the redact list |
| OTel SDK initialized after first logger import | Move to `instrumentation.ts` / `--require`; `sdk.start()` must precede all instrumented imports |
| `traceId` absent even though OTel is wired | Verify `@opentelemetry/instrumentation-pino` (or Winston format) is active; if auto-injection is unreliable, use manual `propagation.inject` fallback (see `otel-integration.md`) |
| Loki labels include `traceId`, `userId`, or other high-cardinality values | Move to structured metadata / log fields — high-cardinality labels destroy Loki index performance |

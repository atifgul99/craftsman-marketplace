# OpenTelemetry + Structured Logging Integration

How to wire structured logs to OpenTelemetry so that every log line carries the active `traceId`
and `spanId`, log lines correlate to traces in your backend, and context propagates correctly
across service boundaries. This file covers the **logging ↔ OTel** connection, TracerProvider
setup, span instrumentation, and multi-service / async queue context propagation.

> **Scope note.** `grafana.md` owns dashboard structure and datasource wiring for OTel-derived
> metrics. `serverless-vs-server.md` owns the transport-selection decision (OTLP/HTTP vs gRPC,
> flush-before-exit on serverless). Those files do not contain TracerProvider initialization or
> span instrumentation — that content lives here.

> **Scope split.** This file owns OTel SDK wiring to the logger and W3C trace-context propagation
> into logs. Sentry event correlation to OTel traces is in `sentry.md`. Sampling decisions (head
> vs tail, trace-driven log sampling) are introduced in `logging.md § Sampling`. Dashboard panels
> that visualize OTel-derived metrics belong in `grafana.md`.

## Package versions — verify current stable before implementing

OTel Node.js packages release frequently. Before wiring anything, check the current stable versions
of `@opentelemetry/sdk-node`, `@opentelemetry/api`, `@opentelemetry/instrumentation-pino`, and any
exporter packages — pin to the latest stable minor for the project's target Node.js LTS version.

When discovering an existing project, flag any conspicuously outdated OTel package as a gap and
propose upgrading. Verify pino log-correlation support against the
`@opentelemetry/instrumentation-pino` changelog for your installed version — don't assume a
specific version cutoff. Do not try to make old OTel versions work with the patterns in this file —
upgrade is the fix.

---

## Contents

- [Why OTel + logs together](#why-otel--logs-together)
- [W3C Trace Context — what the headers carry](#w3c-trace-context--what-the-headers-carry)
- [TracerProvider setup and span instrumentation](#tracerprovider-setup-and-span-instrumentation)
- [Pino + OTel (recommended)](#pino--otel-recommended)
- [Winston + OTel](#winston--otel)
- [Async context propagation — AsyncLocalStorage and OTel Context](#async-context-propagation--asynclocalstorage-and-otel-context)
- [Log export — OTLP, Loki, ELK](#log-export--otlp-loki-elk)
- [Health endpoints as observable signals](#health-endpoints-as-observable-signals)
- [Multi-service distributed correlation](#multi-service-distributed-correlation)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Why OTel + logs together

Without OTel wiring, your logs carry a `traceId` you generated yourself — useful for
single-service lookup, but orphaned from the distributed trace backend. With the wiring:

- Every log line automatically carries the `traceId` and `spanId` from the **active OTel span**,
  so clicking a trace in Grafana Tempo / Jaeger / Honeycomb shows the correlated log lines inline.
- The same `traceId` value appears in your log aggregator (Loki, Datadog, CloudWatch) and in the
  trace backend — one id, two views.
- You stop maintaining two parallel id-generation paths (your own UUID + OTel's). The OTel SDK
  propagates the id; you just read it.

---

## W3C Trace Context — what the headers carry

The W3C Trace Context spec defines two HTTP headers that carry distributed trace state:

```
traceparent: 00-<traceId>-<parentSpanId>-<flags>
tracestate:  <vendor>=<value>[,<vendor>=<value>]
```

- **`traceId`** (16-byte hex, 32 chars) — stable for the entire distributed request tree.
  This is what goes in your `traceId` log field.
- **`parentSpanId`** (8-byte hex, 16 chars) — the span that made this call. The receiving
  service creates a new child span with its own `spanId`; it does **not** reuse `parentSpanId`.
- **`flags`** — `01` = sampled, `00` = not sampled. A `00` flag means the head sampler decided
  not to record this trace — if you implement trace-driven log sampling, use this flag.

**Never hand-roll traceparent parsing.** Use `@opentelemetry/api`'s propagation API; it handles
spec edge cases (version negotiation, malformed headers) that a regex won't.

---

## TracerProvider setup and span instrumentation

The `NodeSDK` bundles `TracerProvider` setup, but when you need direct control — or are wiring a
non-Node environment — initialize `TracerProvider` explicitly.

### TracerProvider initialization pattern

```ts
// instrumentation.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { resourceFromAttributes } from '@opentelemetry/resources';
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions';
import { PinoInstrumentation } from '@opentelemetry/instrumentation-pino';

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: process.env.SERVICE_NAME ?? 'unknown-service',
    [ATTR_SERVICE_VERSION]: process.env.SERVICE_VERSION ?? '0.0.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [new PinoInstrumentation()],
});

sdk.start();
// sdk.start() registers the TracerProvider globally — tracer.getTracer() resolves against it
```

### Creating spans with tracer.startActiveSpan()

Get a tracer from the global API and create spans with `startActiveSpan`. The callback runs with
the new span as the active span in the current async context — any log lines emitted inside the
callback automatically carry that span's `traceId` and `spanId`:

```ts
import { trace, SpanStatusCode } from '@opentelemetry/api';

const tracer = trace.getTracer('billing-service', '1.0.0');

async function chargePayment(invoiceId: string, amountCents: number) {
  return tracer.startActiveSpan('payment.charge', async (span) => {
    try {
      // Add span attributes before the work
      span.setAttribute('invoice.id', invoiceId);
      span.setAttribute('payment.amount_cents', amountCents);

      const result = await gateway.charge(invoiceId, amountCents);

      span.setAttribute('payment.status', result.status);
      return result;
    } catch (err) {
      // Record the error on the span before re-throwing
      span.recordException(err as Error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: (err as Error).message });
      throw err;
    } finally {
      // Always end the span — even on the happy path, startActiveSpan does not auto-end
      span.end();
    }
  });
}
```

### Adding span attributes

Attributes are key-value metadata attached to a span. Use the OTel semantic conventions for
standard dimensions and add domain-specific attributes for business context:

```ts
import { SpanStatusCode } from '@opentelemetry/api';

span.setAttribute('db.system', 'postgresql');
span.setAttribute('db.statement', 'SELECT * FROM invoices WHERE id = $1');
span.setAttribute('invoice.id', invoiceId);
span.setAttribute('user.id', userId);
```

- Keep attribute values scalar (string, number, boolean) or arrays of scalars. Objects must be
  serialized manually.
- Avoid high-cardinality attributes in spans that will be sampled at high rates — prefer recording
  these in structured log fields (`logging.md`).
- Call `span.end()` in a `finally` block so the span is always closed, even if an exception is
  thrown before the explicit `end()` call.

### Async context propagation with AsyncLocalStorage

OTel uses Node.js `AsyncLocalStorage` internally (via `AsyncLocalStorageContextManager`) to carry
the active span context across `await` boundaries. The `NodeSDK` registers this automatically.
For manual context propagation — e.g. passing context into a background job queue or a worker:

```ts
import { context, trace } from '@opentelemetry/api';

// Capture the current context at the point of dispatch
const capturedCtx = context.active();

// Restore it inside an async callback that runs later (e.g. a queue consumer)
context.with(capturedCtx, async () => {
  // The active span from the dispatch point is now active here
  await processJob(job);
});
```

For queue / async boundaries (SQS, BullMQ, Kafka), serialize the context into the message
payload at produce time and restore it at consume time — see the Multi-service section below.

---

## Pino + OTel (recommended)

Pino is the preferred structured logger in Node.js backends. Two OTel packages cover the two
distinct concerns — they are **not interchangeable**:

| Package | What it does |
| --- | --- |
| `@opentelemetry/instrumentation-pino` (verify version support in the package changelog) | **Injection** — auto-injects `traceId`, `spanId`, `traceFlags` from the active span into every Pino log record at emit time. No manual child loggers needed for trace fields. This is the package that makes `traceId` appear automatically. |
| `pino-opentelemetry-transport` | **Export** — sends Pino log records to an OTel Collector endpoint over OTLP/HTTP. A separate concern from injection; use it only when your pipeline collects logs via OTLP. Installing this alone does NOT inject trace fields. |

### Setup: auto-inject traceId/spanId into Pino records

```ts
// instrumentation.ts  (loaded via --require or Next.js instrumentation hook)
import { NodeSDK } from '@opentelemetry/sdk-node';
import { PinoInstrumentation } from '@opentelemetry/instrumentation-pino';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { resourceFromAttributes } from '@opentelemetry/resources';
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: process.env.SERVICE_NAME ?? 'unknown-service',
    [ATTR_SERVICE_VERSION]: process.env.SERVICE_VERSION ?? '0.0.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [
    new PinoInstrumentation({
      // logHook lets you add extra fields per log record if needed
      // logHook: (_span, record) => { record['custom'] = 'value'; },
    }),
  ],
});

sdk.start();
```

```ts
// lib/logger.ts
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  base: {
    service: process.env.SERVICE_NAME ?? 'unknown-service',
    env: process.env.NODE_ENV,
  },
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      'res.headers["set-cookie"]',
      '*.password',
      '*.token',
      '*.secret',
    ],
    censor: '[Redacted]',
  },
  // pino-pretty for local dev only — JSON in production
  ...(process.env.NODE_ENV !== 'production' && {
    transport: { target: 'pino-pretty', options: { colorize: true } },
  }),
});
```

After this wiring, every log call automatically produces:

```jsonc
{
  "level": 30,
  "time": 1718800321123,
  "service": "billing-api",
  "env": "production",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",   // ← injected by PinoInstrumentation
  "spanId": "00f067aa0ba902b7",                      // ← injected by PinoInstrumentation
  "traceFlags": "01",                                 // ← 01 = sampled
  "msg": "user.invoice.created",
  "invoiceId": "inv_xyz",
  "durationMs": 42
}
```

No manual `logger.child({ traceId })` for the OTel fields — `PinoInstrumentation` injects them
at emit time from the active span context.

### Loading instrumentation before application code

OTel instrumentation **must** run before any instrumented library is `require`d/imported:

```bash
# Node.js (CJS)
node --require ./dist/instrumentation.js server.js

# Node.js (ESM)
node --import ./dist/instrumentation.js server.js
```

For Next.js App Router, create `instrumentation.ts` at the project root and export `register()`:

```ts
// instrumentation.ts  (Next.js 15+ / Next.js 16 proxy-based)
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./instrumentation.node');  // OTel SDK init, runs only on Node.js
  }
  // Do NOT initialize OTel in the Edge/proxy runtime — it is not supported
}
```

---

## Winston + OTel

Winston doesn't have an official OTel auto-instrumentation package for log injection. Use the
`@opentelemetry/api` context API to read trace fields manually and inject them via a format:

```ts
import winston from 'winston';
import { context, trace, isSpanContextValid } from '@opentelemetry/api';

const otelTraceFormat = winston.format((info) => {
  const span = trace.getActiveSpan();
  if (span) {
    const ctx = span.spanContext();
    if (isSpanContextValid(ctx)) {
      info.traceId = ctx.traceId;
      info.spanId = ctx.spanId;
      info.traceFlags = ctx.traceFlags;
    }
  }
  return info;
});

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL ?? 'info',
  format: winston.format.combine(
    otelTraceFormat(),
    winston.format.json(),
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME ?? 'unknown-service',
  },
  transports: [new winston.transports.Console()],
});
```

Winston requires the format to be applied on every call — no auto-injection. This is the main
reason Pino + `@opentelemetry/instrumentation-pino` is preferred for new services: injection is
automatic, not a per-call concern.

---

## Async context propagation — AsyncLocalStorage and OTel Context

OTel uses Node.js's `AsyncLocalStorage` internally to carry the active span context across `await`
boundaries. This means OTel-based `traceId` propagation works through:

- `await fetch(...)` / `await db.query(...)`
- `setTimeout` / `setInterval`
- `EventEmitter` callbacks (when using the built-in async context manager)
- Streams (with caveats — attach context to the stream, not the data handler)

**What breaks propagation:**
- `new Promise((resolve) => setImmediate(resolve))` **without** the OTel async context manager
  registered — Node.js `AsyncLocalStorage` propagates correctly through `Promise` chains by
  default in Node 16+, but raw `setImmediate` and `setTimeout` lose context in older runtimes.
- Spawning a `Worker` thread — the context does not cross thread boundaries; if the worker logs,
  it will not carry the parent `traceId`. Pass the `traceId` explicitly as a message field.
- `child_process.fork()` — same boundary issue. Pass context in the IPC message payload.

**Manual context carry (when auto-propagation doesn't reach):**

```ts
import { context, propagation } from '@opentelemetry/api';

// Serialize current context to headers for an outbound call
const carrier: Record<string, string> = {};
propagation.inject(context.active(), carrier);
// carrier now has: { traceparent: '00-<traceId>-<spanId>-01' }
await fetch(downstreamUrl, { headers: { ...headers, ...carrier } });

// Extract context from an incoming request's headers
const inboundCtx = propagation.extract(context.active(), incomingHeaders);
context.with(inboundCtx, () => {
  // all code in this callback runs with the extracted span context active
  handleRequest(req, res);
});
```

---

## Log export — OTLP, Loki, ELK

Choose **one** export path per runtime. Don't ship to two backends simultaneously unless you have
a bridge (an OTel Collector fan-out) — double-shipping duplicates cost and complicates dedup.

### OTLP (via OTel Collector) — preferred for OTLP-native backends

When your backend is Grafana Tempo + Loki, Honeycomb, or Datadog with OTLP ingest:

```ts
// pino-opentelemetry-transport — sends Pino records to OTLP endpoint
// Add as a second transport alongside stdout for dual-path, or replace stdout entirely
import pino from 'pino';

const isProd = process.env.NODE_ENV === 'production';

export const logger = pino(
  { level: process.env.LOG_LEVEL ?? 'info' },
  pino.transport({
    targets: [
      // stdout: pino-pretty in dev, plain JSON (pino/file → fd 1) in production
      isProd
        ? { target: 'pino/file', options: { destination: 1 }, level: 'info' }
        : { target: 'pino-pretty', options: { colorize: true }, level: 'debug' },
      // OTLP export — only when collector endpoint is configured
      ...(process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT ? [{
        target: 'pino-opentelemetry-transport',
        options: { resourceAttributes: { 'service.name': process.env.SERVICE_NAME ?? 'unknown' } },
        level: 'info',
      }] : []),
    ],
  }),
);
```

### Loki (direct push, no collector)

When running Grafana Loki without a collector:

```ts
// Use pino-loki transport
// pnpm add pino-loki
import pino from 'pino';

export const logger = pino(
  { level: process.env.LOG_LEVEL ?? 'info' },
  pino.transport({
    target: 'pino-loki',
    options: {
      host: process.env.LOKI_HOST ?? 'http://localhost:3100',
      labels: { job: process.env.SERVICE_NAME ?? 'unknown', env: process.env.NODE_ENV },
      // batch size / flush interval
      interval: 5,
      // include all pino fields as Loki structured metadata
      structuredMetadata: true,
    },
  }),
);
```

**Loki label cardinality warning:** Loki labels (`.labels`) must be low-cardinality — job, env,
service, region. `traceId`, `userId`, `requestId` belong in structured metadata (log fields), not
labels. High-cardinality labels kill Loki index performance the same way they kill Prometheus.

### ELK (Elasticsearch + Logstash + Kibana) — stdout → Filebeat pipeline

For ELK, the recommended path is **stdout → Filebeat → Logstash/Elasticsearch**. The application
should not connect directly to Elasticsearch; it writes JSON to stdout and the platform handles
collection:

```ts
// logger.ts — JSON to stdout; Filebeat collects it
import pino from 'pino';
export const logger = pino({ level: process.env.LOG_LEVEL ?? 'info' }); // JSON stdout by default
```

Filebeat config (provided by infra, not the app):
```yaml
# filebeat.yml (infra concern — reference only)
filebeat.inputs:
  - type: log
    paths: ['/var/log/app/*.log']
    json.keys_under_root: true
    json.add_error_key: true
output.elasticsearch:
  hosts: ['${ELASTICSEARCH_HOST}']
  index: 'app-logs-%{+yyyy.MM.dd}'
```

**The app's responsibility is only correct JSON stdout.** Shipping, indexing, and retention are
infra/platform concerns.

### Datadog / New Relic / Dynatrace

For vendor-native backends, use their first-party pino transport or agent:

- **Datadog:** `dd-trace` auto-instruments Pino and injects `dd.trace_id`, `dd.span_id`.
  Set `DD_LOGS_INJECTION=true` in env; the Datadog Agent collects stdout.
- **New Relic:** `@newrelic/pino-enricher` format plugin injects NR-specific trace fields.
- **Dynatrace:** `OneAgent` reads stdout JSON; ensure your JSON has a `dt.trace_id` field or
  configure the `opentelemetry-exporter-dynatrace` transport.

**Prefer OTLP-native or vendor-agnostic setups** for new services — avoids vendor lock-in at the
application layer. Vendor SDKs belong in infra configuration, not application code.

---

## Health endpoints as observable signals

Endpoint semantics (liveness vs readiness vs event-loop-health, probe configuration, drain
windows) → `craft-infra` → `references/runtime-health.md`. This section covers only the
observability signal: what to emit when a dependency check fails.

**Emit a metric and a structured log entry when a dependency degrades:**

```ts
// Example: dependency check wired into /ready
async function checkDependencies(): Promise<{ ok: boolean; details: Record<string, boolean> }> {
  const [dbOk, cacheOk] = await Promise.allSettled([
    db.ping().then(() => true).catch(() => false),
    redis.ping().then(() => true).catch(() => false),
  ]);

  const details = {
    db: dbOk.status === 'fulfilled' ? dbOk.value : false,
    cache: cacheOk.status === 'fulfilled' ? cacheOk.value : false,
  };

  const allOk = Object.values(details).every(Boolean);

  if (!allOk) {
    // Emit a structured log entry so the degradation is searchable
    logger.warn({ msg: 'health.dependency.degraded', ...details });
    // Increment a metric counter so the dashboard and alerts can fire
    dependencyDegradedCounter.add(1, { dependencies: JSON.stringify(details) });
  }

  return { ok: allOk, details };
}

app.get('/ready', async (_req, res) => {
  const { ok, details } = await checkDependencies();
  res.status(ok ? 200 : 503).json({ status: ok ? 'ready' : 'degraded', details });
});
```

---

## Multi-service distributed correlation

When a request flows through Service A → Service B → Service C, all three must carry the **same
`traceId`** in their log lines. The mechanism:

1. **Service A** generates the root span (or continues from an upstream `traceparent` header).
   OTel injects `traceId` into A's log lines automatically.

2. **A calls B** — inject the active context into the outbound request headers:
   ```ts
   const carrier: Record<string, string> = {};
   propagation.inject(context.active(), carrier);
   await fetch(serviceBUrl, { headers: { ...existingHeaders, ...carrier } });
   // carrier: { traceparent: '00-<same traceId>-<A's spanId>-01' }
   ```

3. **Service B** extracts context from the incoming `traceparent` header at its request boundary:
   ```ts
   // In B's request middleware
   const parentCtx = propagation.extract(context.active(), req.headers);
   const span = tracer.startSpan('b.handle_request', {}, parentCtx);
   context.with(trace.setSpan(parentCtx, span), () => {
     // B's log lines now carry the same traceId as A's
     next();
   });
   ```

4. **Log aggregators** (Loki, Datadog, Elasticsearch) can now search `traceId=<X>` and return
   log lines from A, B, and C in a single result set.

**What the logs look like across services:**

```jsonc
// Service A — billing-api
{ "traceId": "4bf92f3577b34da6a3ce929d0e0e4736", "spanId": "a1b2c3d4e5f6a1b2", "service": "billing-api", "msg": "payment.initiated" }

// Service B — notification-service (same traceId, different spanId)
{ "traceId": "4bf92f3577b34da6a3ce929d0e0e4736", "spanId": "f6e5d4c3b2a1f6e5", "service": "notification-service", "msg": "email.queued" }

// Service C — ledger-service (same traceId again)
{ "traceId": "4bf92f3577b34da6a3ce929d0e0e4736", "spanId": "1122334455661122", "service": "ledger-service", "msg": "ledger.entry.written" }
```

One `traceId` query reconstructs the full distributed request.

**Queue / async boundary (SQS, Kafka, BullMQ):**

HTTP propagation doesn't apply to queues. Instead:

```ts
// Producer — embed trace context in the message payload
const carrier: Record<string, string> = {};
propagation.inject(context.active(), carrier);
await queue.send({ body: payload, attributes: { traceContext: JSON.stringify(carrier) } });

// Consumer — extract and restore context before processing
const carrier = JSON.parse(message.attributes.traceContext ?? '{}');
const ctx = propagation.extract(context.active(), carrier);
context.with(ctx, () => processMessage(message));
```

---

## Quick-reject checklist

| Pattern | Fix |
| --- | --- |
| `traceId` in logs is a self-generated UUID, not an OTel trace ID | Wire `@opentelemetry/instrumentation-pino` (or the Winston format above); let OTel own the id |
| OTel SDK initialized after the logger is imported | Move `sdk.start()` to `instrumentation.ts` / `--require`; OTel must load before any instrumented module |
| `traceId` field missing when OTel is wired | Verify `@opentelemetry/instrumentation-pino` is in deps and verify pino log-correlation support against the changelog for your installed version; verify `sdk.start()` completes before first Pino call; if OTel packages are conspicuously outdated, upgrade — don't patch around them |
| Outbound HTTP calls missing `traceparent` header | Use `@opentelemetry/instrumentation-undici` or `@opentelemetry/instrumentation-http` to auto-inject; or call `propagation.inject(context.active(), carrier)` manually |
| `traceparent` extracted manually with a regex | Use `propagation.extract(context.active(), headers)` — handles version negotiation and malformed headers |
| Loki labels include `traceId` or `userId` | Move to structured metadata / log fields; Loki labels must be low-cardinality |
| Logger writes directly to Elasticsearch from application code | Write JSON to stdout; let Filebeat/Fluentd/platform handle shipping |
| OTel SDK initialized in the Edge / proxy runtime (Next.js proxy.ts) | OTel Node.js SDK is not Edge-compatible; gate with `process.env.NEXT_RUNTIME === 'nodejs'` in `instrumentation.ts` |
| Vendor-specific trace fields (`dd.trace_id`) hard-coded in app code | Inject via the vendor's pino plugin or DD_LOGS_INJECTION env var — keeps app code vendor-agnostic |
| Worker thread logs missing `traceId` | Pass `traceId` explicitly in the worker message payload — context does not cross thread boundaries |
| Queue messages missing trace context | Embed serialized carrier (`propagation.inject` output) in message attributes; extract in consumer |

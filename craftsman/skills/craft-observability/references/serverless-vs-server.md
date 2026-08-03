# Serverless vs Long-Lived: Metrics & Tracing Strategy

`prom-client` is a pull-based, in-process registry — it accumulates counters and histograms in memory and serves them at `/metrics` when Prometheus scrapes. That model collapses under serverless: each invocation may spawn a fresh process, the in-process registry resets to zero on every cold start, and there is no stable scrape target for Prometheus to poll. **Choose a metrics and tracing transport that matches the runtime's lifetime, not the one you used last.**

---

> **Scope split.** This file owns the *metrics + tracing transport decision* — which client, which protocol, how to flush — based on deployment model. The *datasource wiring* and dashboard setup once data is arriving belongs to `grafana.md`. Flushing Sentry spans before a function exits is covered in `sentry.md` (which also owns error tracking). Structured log emission — including log-based metrics derived from those logs — is `logging.md`. The infrastructure angle of the same ephemeral-runtime problem (health checks, drain windows, zero-downtime deploys on platforms like Vercel/Fly/Render) lives in **`craft-infra`** → `scale-resilience.md` and `runtime-health.md`.

---

## Contents

- [Why pull-based metrics break on serverless](#why-pull-based-metrics-break-on-serverless)
- [The decision table](#the-decision-table)
- [Serverless: push-based and OTLP](#serverless-push-based-and-otlp)
- [Serverless: vendor SDKs](#serverless-vendor-sdks)
- [Serverless: log-based metrics](#serverless-log-based-metrics)
- [Flush before exit](#flush-before-exit)
- [Long-lived servers: prom-client done right](#long-lived-servers-prom-client-done-right)
- [Tracing across the boundary](#tracing-across-the-boundary)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Why pull-based metrics break on serverless

Prometheus is a scrape-based system. The scraper polls your `/metrics` endpoint on a fixed interval (typically 15–60 s) and reads whatever is currently in the registry. This works when there is a stable, long-lived process that accumulates values between scrapes. Serverless runtimes break every assumption:

- **No stable target.** A Lambda function, a Vercel Serverless Function, or a Cloudflare Worker runs to completion and the process — along with its registry — is gone. If Prometheus scrapes between invocations it gets nothing. If the function is never warm at scrape time it gets nothing.
- **Cold-start reset.** Each cold start initialises a fresh registry at zero. Two invocations running concurrently in different instances each hold partial counts; neither holds the aggregate. A scrape that happens to hit one instance misses the other entirely — the numbers are neither accurate nor additive in any predictable way.
- **Not a meaningful scrape target.** An HTTP serverless function can technically expose a `/metrics` route that a scraper can invoke, but the response reflects only the current in-flight instance's partial, cold-started counters — not the aggregate across all instances. The sample is incomplete, per-instance, expensive (it cold-starts an invocation), and does not compose into a stable time series. It is not a reliable Prometheus scrape target.
- **Platform-level restriction.** Some serverless platforms (AWS Lambda, Cloudflare Workers) do not allow a separate listening socket, making a conventional passive scrape endpoint impossible regardless. Where an HTTP route is technically possible, the above accuracy and reliability problems still apply.

The failure mode is silent: `prom-client` initialises fine, increments fine, and the developer sees no error — but Prometheus never collects a meaningful sample, dashboards read zero or stale, and alerts never fire.

---

## The decision table

Discover the deployment target before reaching for any metrics client. Check for serverless indicators: `vercel.json`, `netlify.toml`, `serverless.yml`, a `lambda_handler` entry point, `wrangler.toml` (Cloudflare Workers), AWS SAM/CDK Lambda definitions, Supabase Functions directories, `package.json` adapter dependencies (`@vercel/node`, `hono`, `aws-lambda`), or a platform-level config in the infra that runs the service (e.g., Fly.io `fly.toml` with a persistent process vs. Vercel project settings). See craft-infra → scale-resilience.md for the canonical cross-skill discovery checklist.

| Runtime | Typical platforms | Metrics approach | Tracing approach |
| --- | --- | --- | --- |
| **Serverless / edge function** | AWS Lambda, Vercel Functions, Netlify Functions, Cloudflare Workers | Push-based: OTLP/HTTP, vendor SDK, or log-derived metrics | OTLP trace exporter with flush-before-exit; or vendor SDK (e.g. Sentry `startSpan`) |
| **Long-lived server / container** | Fly.io, Render, Railway, self-managed Docker, bare EC2 | `prom-client` at `/metrics` scraped by Prometheus/Grafana Agent | `@opentelemetry/exporter-trace-otlp-grpc` pointed at an OTel Collector or Jaeger OTLP endpoint (Jaeger v1.35+); persistent gRPC connection |
| **Hybrid (serverless + long-lived API)** | Next.js on Vercel (Edge/Serverless routes + optional long-lived backend) | Separate strategy per process type — don't share a `prom-client` instance across both | Propagate `traceparent` headers across the boundary; aggregate in one backend |

If you are unsure, check where the process lives and whether it survives between requests. A process that can be killed after a single HTTP response is serverless for this purpose, regardless of what the platform calls it.

---

## Serverless: push-based and OTLP

The cleanest general-purpose solution for serverless metrics and tracing is **OpenTelemetry with an OTLP/HTTP exporter** pushed to an OTel Collector or a managed endpoint (e.g. Grafana Cloud OTLP endpoint, Honeycomb, ServiceNow Cloud Observability (formerly Lightstep), New Relic OTLP ingest).

```ts
// Minimal OTLP push setup for Node.js runtimes (AWS Lambda, Vercel Node Functions)
// — adapt to the OTel SDK version in the repo
// NOTE: Node-only packages; NOT directly portable to Cloudflare Workers / V8-isolate
// edge runtimes — see the caveat below.
import { MeterProvider, PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { OTLPMetricExporter, AggregationTemporalityPreference } from '@opentelemetry/exporter-metrics-otlp-http';
import { env } from '@/env'; // the repo's validated env module — incl. OTLP endpoint + (credential) token

const exporter = new OTLPMetricExporter({
  url: env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, // e.g. https://otel-collector.example.com/v1/metrics
  headers: { Authorization: `Bearer ${env.OTEL_AUTH_TOKEN}` }, // validated, never a raw process.env read
  temporalityPreference: AggregationTemporalityPreference.DELTA,
});

const meterProvider = new MeterProvider({
  readers: [
    new PeriodicExportingMetricReader({
      exporter,
      exportIntervalMillis: 5_000,  // push every 5 s while the function runs
    }),
  ],
});

// Instrument, then flush before the handler returns — see "Flush before exit"
```

Key points:
- **OTLP/HTTP** (port 4318) is preferred over OTLP/gRPC (port 4317) on serverless — works on Node.js runtimes (Lambda, Vercel Node Functions). OTLP/gRPC works fine on AWS Lambda but requires raw socket access and is not appropriate for edge runtimes.
- Use `DeltaTemporality` for counters (`temporalityPreference: AggregationTemporalityPreference.DELTA` from `@opentelemetry/exporter-metrics-otlp-http`) so each push batch is self-contained and doesn't rely on the previous state accumulating in memory. Alternatively, set the env var `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta`.
- The collector or managed endpoint aggregates across instances — this is what you cannot do in-process.

> **Read config through the validated `env` module, not raw `process.env`.** Same repo-wide rule as
> `sentry.md` and `craft-infra` → `config.md`: the OTLP endpoint and the credential-shaped
> `OTEL_AUTH_TOKEN` belong in the validated env schema, read via `env.*`. The only code that touches
> raw `process.env` is the schema/bootstrap itself.

> **Edge runtime caveat (Cloudflare Workers and similar V8-isolate environments).** The Node OTel packages above import Node.js built-ins (`net`, `tls`, `http`) and assume a Node runtime (the validated `env` module reads `process.env` under the hood). These are unavailable in Cloudflare Workers and other edge runtimes that run on V8 isolates without a Node.js layer. For those environments:
> - Use a Worker-compatible OTel exporter or the vendor-provided SDK — for Cloudflare Workers, `@sentry/cloudflare` handles Sentry, and Cloudflare's own observability pipeline or a Worker-compatible OTLP fetch-based client handles metrics/traces.
> - Access env bindings via the Worker `env` parameter passed to the `fetch` handler, not `process.env`.
> - Keep Node Lambda / Vercel Node examples separate from Cloudflare / edge examples — the packages and initialization patterns are different enough that mixing them produces runtime errors.

---

## Serverless: vendor SDKs

Vendor-managed SDKs for serverless are a lower-friction alternative when OTLP self-hosting isn't warranted:

- **AWS Lambda:** `aws-embedded-metrics` (emits CloudWatch Embedded Metric Format to stdout — CloudWatch ingests and turns it into metrics automatically, no separate endpoint). Works on Lambda without any network call from the function.
- **Vercel:** The platform emits invocation-level metrics (duration, errors, cold starts) automatically in the Vercel dashboard, and Vercel's OTel integration lets you forward spans to an OTLP-compatible backend. For custom metrics, use a push-compatible SDK pointed at your own backend.
- **Datadog / New Relic / Dynatrace:** Each provides a Lambda layer or SDK that wraps the handler, collects metrics and traces in-process, and flushes them via a sidecar or extension (e.g. Datadog Lambda Extension) — this sidesteps the flush-timing problem because the extension process outlives the handler.

Discover which vendor, if any, is already wired (`grep` for `DD_API_KEY`, `NEW_RELIC_LICENSE_KEY`, `aws-embedded-metrics`, or existing layer ARNs in the SAM/CDK/Serverless Framework config). Wire into the existing vendor if present; don't introduce a second system.

---

## Serverless: log-based metrics

When a metrics pipeline doesn't exist and the cost of adding one is higher than the value of the instrumentation, **log-based metrics** are a pragmatic fallback:

1. Emit structured JSON logs with metric-shaped fields: `{ "event": "order.placed", "value": 1, "currency": "usd", "latencyMs": 142 }` (see `logging.md` for the log format standard).
2. Configure your log aggregation backend (CloudWatch Metrics Filter, Datadog Log-based Metrics, Grafana Cloud log-to-metric transform, Loki recording rules) to extract numeric fields and create a metric series.

This avoids a separate metrics client entirely. The trade-off: higher per-datapoint cost in some platforms, slightly higher latency for alert evaluation, and no histogram support without careful log schema design. It is sufficient for low-volume functions where you mainly want counters and gauges — not appropriate as the sole source for a high-cardinality system or a latency SLO.

---

## Flush before exit

Whether using OTLP or a vendor SDK on serverless, **telemetry that hasn't been exported when the process exits is silently lost**. The function runtime may freeze the process immediately after returning — buffered spans, pending metric batches, and queued log writes that relied on a timer are all dropped.

Flush explicitly before returning from the handler:

```ts
// OTel SDK — call forceFlush on both the MeterProvider and TracerProvider
export async function handler(event: unknown) {
  try {
    return await doWork(event);
  } finally {
    await Promise.allSettled([
      meterProvider.forceFlush(),
      tracerProvider.forceFlush(),
    ]);
  }
}
```

The same applies to Sentry: call `await Sentry.flush(2_000)` before `return`/`process.exit` in a Lambda or edge function. See `sentry.md` for the Sentry-specific flush pattern. Do not fire-and-forget the flush promise; `Promise.allSettled` ensures both providers are attempted even if one rejects.

The timeout passed to `forceFlush` / `Sentry.flush` must be within the function's remaining execution budget. On Lambda, check `context.getRemainingTimeInMillis()` if you want to be precise; practically, 2–3 s is a safe ceiling for the flush budget, and you should configure your exporter's export timeout to be shorter than that.

For the lifecycle events that constrain the flush budget on long-lived servers — SIGTERM handling, drain windows, and zero-downtime deploy patterns — see craft-infra → runtime-health.md.

---

## Long-lived servers: prom-client done right

On a long-lived process (a container on Fly.io, Render, Railway, or a self-managed VM), `prom-client` is the right choice for Node.js. A few non-negotiables to get it right:

```ts
import client from 'prom-client';

// Single registry for the process — never create a new Registry per request
const registry = new client.Registry();

// Collect default metrics (GC, event-loop lag, memory) — always enable this
client.collectDefaultMetrics({ register: registry });

// Expose at /metrics — this endpoint is for your scraper, not your users
app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', registry.contentType);
  res.end(await registry.metrics());
});
```

- **One registry per process.** The most common mistake is `new Registry()` inside a module that gets required per-request, or calling `new client.Counter()` without passing `registers: [registry]`, which silently falls back to the global default registry. In hot-reload environments (e.g. Next.js dev mode), the module reinitialises and you get `Error: A metric … has already been registered` — guard with a singleton pattern or check `registry.getSingleMetric(name)` before registering.
- **Secure the `/metrics` endpoint.** It is not a public route. Protect it with an IP allowlist at the load balancer or firewall level, a shared-secret header checked by middleware, or a sidecar such as the Grafana Agent or Prometheus Agent running in the same network that scrapes locally and remote-writes externally. Exposing it on a public port leaks internal cardinality and label values.
- **Label cardinality discipline.** High-cardinality labels (`userId`, `requestId`, `email`) explode the time-series count and can OOM the Prometheus server. Labels should be bounded, categorical values (`route`, `statusCode`, `method`, `region`). This is a correctness concern, not just a performance one — Prometheus will degrade under cardinality explosion.

---

## Tracing across the boundary

A common hybrid: a long-lived API backend that calls a serverless function (or vice versa). Trace context must propagate across the boundary via HTTP headers, or you get disconnected spans that can't be correlated.

- **Propagate `traceparent` (W3C Trace Context) on every outbound HTTP call** — the OTel SDK does this automatically if you use the HTTP instrumentation package. If you're calling from plain `fetch` or `axios`, inject the header manually from the active span.
- **On the receiving end, extract the context from the incoming headers** before starting child spans — again, automatic with OTel HTTP instrumentation, manual otherwise.
- **Use the same trace backend on both sides.** Traces that half-arrive in Jaeger and half in Sentry can't be stitched. Pick one sink per environment; usually the same OTel Collector or vendor that handles the rest. See `grafana.md` for the datasource wiring.

---

## Quick-reject checklist

| Pattern | Fix |
| --- | --- |
| Raw `process.env.*` in OTLP/exporter setup (esp. `OTEL_AUTH_TOKEN`) | Import the validated `env` module; the credential + endpoint belong in the env schema (`craft-infra` → `config.md`), not a scattered raw read |
| `prom-client` imported in a Lambda/Vercel/Cloudflare function | Replace with OTLP push, vendor SDK, or log-based metrics — pull scraping won't work |
| `/metrics` endpoint on a serverless function handler | Reachable but not meaningful as a Prometheus scrape target — responses reflect a single instance's cold-started, partial counters; aggregate accuracy is impossible. Replace with push-based metrics (OTLP, vendor SDK, or log-derived metrics). |
| `new Registry()` or `new client.Counter()` called per request | Move to module scope; one registry per process |
| `prom-client` registry recreated on every hot-reload (Next.js dev) | Guard with a singleton: check `global.__registry` or `registry.getSingleMetric` before registering |
| High-cardinality label on a Prometheus metric (`userId`, `email`, `requestId`) | Replace with a bounded categorical label (`route`, `statusCode`); cardinality explosion OOMs the TSDB |
| OTel exporter or Sentry not flushed before handler returns | Add `await meterProvider.forceFlush()` / `await Sentry.flush(2000)` in a `finally` block |
| Flush promise fire-and-forgot (`forceFlush()` without `await`) | `await Promise.allSettled([…])` — unhandled rejections and dropped exports are indistinguishable |
| OTLP/gRPC used on an edge runtime (Cloudflare Workers, etc.) | Switch to OTLP/HTTP (`@opentelemetry/exporter-*-otlp-http`); edge runtimes lack Node.js `net`/`tls` module access required for gRPC (OTLP/gRPC works fine on AWS Lambda) |
| `traceparent` header not forwarded on cross-service calls | Wire OTel HTTP instrumentation or inject `traceparent` manually; missing context breaks trace correlation (`grafana.md`) |
| Two metrics vendors wired in parallel (e.g. `prom-client` + Datadog) | Discover what's already present (`grep` for vendor env vars); extend the existing system |
| `/metrics` exposed on a public port with no auth | Protect with IP allowlist, shared-secret header, or internal-network sidecar |

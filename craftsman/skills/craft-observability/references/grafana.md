# Grafana Dashboards

A dashboard that was hand-clicked into existence is a dashboard that will drift, disappear on a
re-provision, and never be reviewed like code. **Dashboards are code: provisioned from JSON or
Terraform, version-controlled, and reviewed the same way a PR is.** The panels that matter answer
the RED/USE questions — rate, error rate, duration for every user-facing service; utilization,
saturation, errors for every infrastructure resource — and nothing else earns a spot on the
screen. Vanity panels (CPU graphs with no alert or runbook, duplicate panels nobody references)
dilute attention and make the dashboard harder to act on.

> **Scope split.** This file owns dashboard structure, datasource choice, the panels that matter
> (RED/USE method), and the dashboard-as-code workflow. **Datasource selection on serverless
> runtimes** (why `prom-client` scraping breaks on Lambda/Edge and what replaces it) is deferred
> to `serverless-vs-server.md` — read that first whenever the deployment target is a Function or
> Edge worker. **Alert rules that fire on these metrics** belong to `slo-alerts.md` — thresholds,
> burn-rate math, and runbook linking live there, not here. **Log-based panels** (Loki queries,
> log-derived metrics) are scoped to `logging.md`. Infrastructure provisioning of the Grafana
> instance itself (Helm chart, self-hosted vs Grafana Cloud) belongs to **`craft-infra`** →
> `runtime-health.md`.

---

## Contents

- [Dashboard-as-code: provisioned, not hand-clicked](#dashboard-as-code-provisioned-not-hand-clicked)
- [Datasource choice per runtime](#datasource-choice-per-runtime)
- [The panels that matter: RED for services](#the-panels-that-matter-red-for-services)
- [The panels that matter: USE for infrastructure](#the-panels-that-matter-use-for-infrastructure)
- [Panel construction discipline](#panel-construction-discipline)
- [Vanity panels: what to cut](#vanity-panels-what-to-cut)
- [Variables and multi-service dashboards](#variables-and-multi-service-dashboards)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Dashboard-as-code: provisioned, not hand-clicked

Grafana supports two provisioning paths — both are acceptable, the choice depends on what the
repo's infrastructure layer already uses:

**JSON provisioning (Grafana-native, lower barrier):**
Grafana reads dashboard JSON from a directory at startup (or on reload). The file lives in the
repo, usually under `infra/grafana/dashboards/` or `monitoring/`. CI lints it; the Grafana
container/Cloud instance mounts or imports it on deploy.

```jsonc
// infra/grafana/dashboards/api-service.json (abbreviated)
{
  "uid": "api-service-red",
  "title": "API Service — RED",
  "tags": ["service", "red", "api"],
  "templating": { "list": [ /* template variables */ ] },
  "panels": [ /* ... */ ],
  "schemaVersion": 39
}
```

The `uid` field is the stable identifier — set it explicitly so the dashboard URL is stable
across re-imports. Without it Grafana generates a random one and every reprovisioning breaks
bookmarks and alert links.

**Terraform (Grafana provider, strong if infra is already Terraformed):**

```hcl
resource "grafana_dashboard" "api_service_red" {
  config_json = file("${path.module}/dashboards/api-service.json")
  folder      = grafana_folder.services.id
}
```

The Grafana Terraform provider (`grafana/grafana`) manages folders, datasources, and alert rules
alongside dashboards — a good fit when the rest of the stack is already in Terraform. Discover
which toolchain the repo uses (`grep -r "grafana_dashboard\|grafana/dashboards"`) before
introducing the other.

Either way: **the dashboard JSON is the source of truth; the UI is read-only in production.**
File-provisioned dashboards are locked automatically — Grafana shows a "Provisioned" badge and
blocks saves in the UI. No extra environment variable is needed to enable this. To allow temporary
UI edits on a provisioned dashboard, set `allowUiUpdates: true` in the provisioning YAML — but
don't: any edit made there is lost on next re-provision.

---

## Datasource choice per runtime

Pick the metrics backend that survives the deployment model. The runtime-to-datasource decision
table (long-lived server vs. serverless/edge vs. Kubernetes vs. managed cloud) belongs to
`serverless-vs-server.md` — read that file first whenever the deployment target is a Function or
Edge worker. Grafana Alloy (formerly Grafana Agent) is the standard scrape/forward agent for
Kubernetes workloads.

Whatever datasource is chosen, reference it by uid in every panel query — never hardcode a
human-readable name that diverges between environments:

```jsonc
"datasource": { "type": "prometheus", "uid": "${DS_PROMETHEUS}" }
```

Using a template variable (`${DS_PROMETHEUS}`) for the datasource uid lets the same JSON
provision correctly across staging and production without edits.

---

## The panels that matter: RED for services

Every user-facing service (HTTP API, gRPC service, queue consumer, background job processor)
gets a RED row. These three panels answer "is it broken?" without requiring SSH:

**Rate** — requests per second, by endpoint or handler. Use a `sum(rate(...[5m]))` over the
counter metric your framework/SDK exposes. In Prometheus the label set varies by library (e.g.
`http_requests_total` if manually instrumented with `prom-client`, or the equivalent histogram
exposed by your framework middleware — name varies, inspect `/metrics` to confirm; the OTel HTTP
semantic conventions define `http.server.request.duration` (unit: seconds; dots become underscores
in Prometheus format, yielding `http_server_request_duration_seconds_count`)) — discover the
actual metric name with a label query before writing the panel, don't assume.

```promql
# Example — verify metric and label names against your exporter
sum by (route, method) (
  rate(http_requests_total{job="api-service"}[5m])
)
```

**Error rate** — percentage of requests resulting in 5xx (or explicit error labels). A raw count
panel alongside the percentage helps ops distinguish "1% errors on 10 req/s" from "1% errors on
10,000 req/s".

```promql
# Error rate as a percentage
sum(rate(http_requests_total{job="api-service", status=~"5.."}[5m]))
/
sum(rate(http_requests_total{job="api-service"}[5m]))
* 100
```

**Duration** — P50, P95, and P99 latency. Use a heatmap or time series panel with multiple
quantile lines. Prometheus histograms (classic or native) compute quantiles server-side via
`histogram_quantile` with server-side approximation that can be re-aggregated across instances.
Explicit `summary` quantiles are computed on the client and cannot be aggregated across instances
— use a histogram type for any metric you may later aggregate.

```promql
# P99 via histogram — bucket metric name varies by library
histogram_quantile(0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="api-service"}[5m])
  )
)
```

Organise these as a **row per service or logical component**, collapsible, with a row header
naming the service. One dashboard per team is often better than one per service — a single pane
of glass beats 30 tabs.

---

## The panels that matter: USE for infrastructure

Infrastructure resources (hosts, containers, databases, caches, queues) get a USE row:
**Utilization** (how busy is it as a fraction of capacity?), **Saturation** (is work being
queued or rejected?), **Errors** (are operations failing at the resource level?).

| Resource | Utilization | Saturation | Errors |
| --- | --- | --- | --- |
| CPU | `rate(node_cpu_seconds_total{mode!="idle"}[5m])` / cores (node_exporter), or `rate(container_cpu_usage_seconds_total[5m])` (cAdvisor/kubelet) | Run-queue length, steal time | Thermal throttle events |
| Memory | `used / total` | OOM kills, swap usage | — |
| Database connections | active / pool max | Queue depth, wait time | Query errors, deadlocks |
| Cache (Redis/Memcached) | memory used / maxmemory | Eviction rate | Connection errors |
| Message queue | consumer lag (bytes or messages behind) | Producer backpressure | DLQ depth, poison messages |

Not every resource needs all three — add the ones that have operational meaning. A panel with a
metric that's always near-zero and has no runbook is a vanity panel (see below).

---

## Panel construction discipline

A few rules that separate a dashboard someone uses from one that sits forgotten:

- **One question per panel.** A panel titled "System Overview" with eight series covering memory,
  CPU, network, and latency is unreadable. Split by concern; name each panel with a verb or
  question ("P99 latency — API service", "Error rate — payment processor").
- **Include the unit.** Set the panel's unit field (`ms`, `reqps`, `percent`, `bytes`) — Grafana
  uses it for axis labels and tooltips. A Y-axis reading "3.4" with no unit is useless.
- **Set meaningful Y-axis bounds.** Error-rate panels default to 0–auto; cap at 100% so a spike
  to 100% looks like a spike, not a gentle slope. Latency panels should start at 0.
- **Thresholds on RED panels.** Add a visual threshold (Grafana panel → Thresholds) at your SLO
  boundary so the panel turns red when you're breaching — before the alert fires. The SLO numbers
  come from `slo-alerts.md`.
- **Link to the runbook.** Every panel that shows an error condition should have a Panel Link
  (`panel.links`) pointing to the runbook or `slo-alerts.md` reference. Dashboards without
  runbook links are display-only; they tell you something is wrong without telling you what to do.
- **Time range and refresh.** Set a sensible default time range (last 1 hour for operational
  dashboards) and a refresh interval (30s–1m for on-call; avoid 5s on dashboards with expensive
  queries against large data sets). Put the refresh in the provisioned JSON, not left to whoever
  opened the dashboard.

---

## Vanity panels: what to cut

A vanity panel passes zero information to an on-call engineer deciding whether to act. Common
offenders:

- **Raw CPU/memory gauges with no threshold, no alert, no runbook.** A host using 72% CPU is
  fine or critical depending on context. Without a threshold tied to an alert, the panel is
  decoration.
- **Uptime clocks and "last deployment" counters** — these belong in a status page, not an
  operational dashboard. They add noise during incidents.
- **Duplicate panels.** The same metric charted at different aggregations on the same dashboard
  ("total requests" and "requests per instance" with no distinction in what action each drives).
  Pick the one that triggers a decision and cut the other.
- **"Everything" dashboards** — a single dashboard with 40+ panels from 12 different services.
  Nobody reads below the fold. Split by service or team with a clear top-level summary row.
- **Panels with no data.** A panel that renders "No data" because the metric doesn't exist yet
  (or has been renamed) is worse than not having it — it trains engineers to ignore empty panels.
  Either wire the metric first or remove the panel until you do.

The test: for every panel, ask "what would an on-call engineer do differently if this panel showed
a spike?" If the answer is "nothing", cut it.

---

## Variables and multi-service dashboards

Template variables let one dashboard cover multiple environments or services without duplication:

```jsonc
"templating": {
  "list": [
    {
      "name": "env",
      "type": "custom",
      "options": [
        { "text": "production", "value": "production" },
        { "text": "staging", "value": "staging" }
      ],
      "current": { "text": "production", "value": "production" }
    },
    {
      "name": "service",
      "type": "query",
      "datasource": { "type": "prometheus", "uid": "${DS_PROMETHEUS}" },
      "query": "label_values(http_requests_total{env=\"$env\"}, job)",
      "refresh": 2
    }
  ]
}
```

Use variables in every panel query (`job="$service"`, `env=~"$env"`) so switching the dropdown
re-renders the whole dashboard. A dashboard with hardcoded service names in queries is the
hand-clicked equivalent — it requires manual duplication to cover another service.

**Performance caveat:** On large Prometheus instances, `label_values()` with a metric selector
(as above) calls `/api/v1/series` which is not index-optimized and can time out or cause high
load on large TSDB instances. To mitigate this in production dashboards:
- **Prefer static or custom variables** (type `custom`) for stable, bounded value sets such as environments or well-known service names — no query needed.
- **Narrow the matcher** to the lowest-cardinality label set that still returns the values you need (e.g. filter by `job=` before selecting on another label).
- **Use a recording rule** that pre-aggregates the dimension into a low-cardinality metric, then query `label_values()` on the recorded metric rather than the raw high-cardinality one.
- **Reserve the Prometheus Metrics Browser** for exploratory, ad-hoc investigation — it is a developer tool, not a production dashboard variable strategy.
- **Avoid `label_values()` without a metric selector** (bare `label_values(job)`) — it scans all series in the TSDB and is the most expensive form.

**Label cardinality discipline:** don't put high-cardinality labels (user id, trace id, request
id) in Prometheus metrics — each unique label combination is a time series, and millions of series
will crash Prometheus or incur massive Grafana Cloud costs. Those identifiers belong in traces
(OpenTelemetry) or structured logs (`logging.md`), not in metric labels. Stick to low-cardinality
labels: `job`, `env`, `route` (bounded set of routes), `status_class` (`2xx`, `4xx`, `5xx`).

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Dashboard JSON not committed to the repo | Add to `infra/grafana/dashboards/` (or the repo's equivalent monitoring directory); provision on deploy |
| Dashboard `uid` absent or generated randomly | Set a stable, kebab-case `uid` in the JSON; lock the dashboard URL |
| Panels modified in the Grafana UI with no corresponding JSON update | UI edits are ephemeral on provisioned dashboards — edit the JSON |
| No rate, error-rate, or duration panel for a user-facing service | Add a RED row — see the RED panels section above |
| Histogram quantile on a `summary` metric type aggregated across instances | `summary` quantiles can't be aggregated — use a Prometheus histogram or aggregate first |
| High-cardinality label (user id, request id) on a Prometheus metric | Move to trace/log; use bounded label set in metrics |
| Datasource name hardcoded as a string, not a UID variable | Use `"uid": "${DS_PROMETHEUS}"` via a datasource template variable |
| Panel unit not set (Y-axis shows raw numbers) | Set unit in panel field config (`ms`, `reqps`, `percent`, `bytes`) |
| RED/USE panels with no visual thresholds | Add Grafana thresholds at the SLO boundary (`slo-alerts.md`) |
| Panel with no runbook link on an error/saturation condition | Add a Panel Link to the runbook or `slo-alerts.md` reference |
| "No data" panel committed to the dashboard | Wire the metric first, or remove the panel |
| Single dashboard with 40+ panels from multiple unrelated services | Split by service or team; add a summary row at the top |
| `prom-client` scrape endpoint on a serverless/Lambda function | Switch to a push-based sink — see `serverless-vs-server.md` |

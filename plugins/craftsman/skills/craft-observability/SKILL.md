---
name: craft-observability
description: >-
  The Craftsman standard for production observability — error tracking (Sentry), metrics & dashboards
  (Grafana), structured logging, tracing, SLOs, and alerting. Use this WHENEVER the work touches
  observability: adding or reviewing Sentry, wiring Grafana/Prometheus/OpenTelemetry, setting up
  structured logs, defining alerts or SLOs, instrumenting a service, or debugging "we have no
  visibility into X". Trigger even when the user only says "add monitoring", "why can't we see
  errors", "set up dashboards", or "make this observable" without naming a tool. Deploy, runtime,
  and CI production-readiness → craft-infra; whole-project readiness → craft-audit.
---

# Observability Craft

This skill encodes one engineer's standard for making a service observable, applied the same way
across every repo. The **method and opinions** live here; the **project specifics** (which logger,
which DSN, which dashboard) live in the target repo's code and config — always discover them, never
assume or hardcode.

## Operating principle — discover before you build

Different repos already have different pieces. Before adding anything, spend two minutes mapping
what exists so you extend rather than duplicate:

- `package.json` / lockfile → is `@sentry/*`, `pino`/`winston`, `prom-client`, `@opentelemetry/*`
  already present?
- `grep` for an existing logger, `Sentry.init`, `/health`, `/metrics`, or an env schema
  (`env.ts`, `config.ts`) — wire into these, don't fork them.
- Deployment target (serverless vs long-lived) decides the metrics approach — see
  `references/serverless-vs-server.md` before reaching for `prom-client`.

State what you found, then propose the smallest set of additions that closes the gaps.

## The four pillars (do them in this order)

1. **Errors** — Sentry first. It's the highest signal-per-minute. See `references/sentry.md`.
2. **Structured logs** — JSON logs with a request/trace id, never `console.log` in production code.
   See `references/logging.md`.
3. **Metrics & dashboards** — Grafana over a metrics source appropriate to the runtime. See
   `references/grafana.md`.
4. **SLOs & alerts** — alerts ride on user-facing symptoms, not raw resource graphs. See
   `references/slo-alerts.md`.

A service is "observable enough to ship" when an on-call engineer can answer _is it broken?_,
_since when?_, and _where?_ from these four without SSH-ing into anything.

**Then the fifth thing, which the four pillars don't give you.** The pillars make the *service*
observable; they say nothing about whether the transaction the product exists to perform actually
completed, or whether a human is on the other end of an alert. Before calling a service production-
ready, close that gap: the core business transaction visible end to end, stuck and half-finished
work detectable, a named person receiving alerts, and the whole loop proven once by breaking it on
purpose. See `references/operational-readiness.md`.

## Standing opinions (the non-negotiables)

These are the judgments that make output consistent across repos — apply them unless the user
overrides:

- **Sentry is the default error tracker.** Capture unhandled errors + rejections, scrub PII, tag
  every event with release + environment, and set `tracesSampleRate` deliberately (not 1.0 in prod).
- **Logs are structured JSON.** One line per event, a stable `traceId`/`requestId` on every line,
  log levels used honestly (`error` means paged-if-frequent, not "FYI").
- **Alert on symptoms, page on pain.** An alert that doesn't map to a user-visible problem or a
  runbook is noise — delete it. Every paging alert links a runbook.
- **No silent degradation.** If a dependency is down, the service says so (health endpoint + log +
  metric), it doesn't fail quietly.
- **The business transaction is a first-class signal.** Whatever the product exists to do — the run,
  the checkout, the send — has a visible lifecycle and a detectable stuck state, not just the infra
  underneath it.
- **Untested notification paths don't count.** Fire one alert down the real path to a real human
  before claiming the service is monitored.

## Workflow

1. **Discover** the current state (above) and report the gaps.
2. **Propose** the closing set, ordered by the four pillars, smallest viable first.
3. **Implement** against the repo's existing patterns (its env schema, its logger, its CI).
4. **Verify** — trigger a test error to Sentry, confirm a dashboard renders, fire a test alert.
   Observability you haven't seen work isn't done. For anything with a background job or a core
   customer transaction, run the acceptance drill in `references/operational-readiness.md`: success,
   system failure, expected business failure, stuck detection, and one alert delivered to a human.

## Reference index

Read the one matching the current task — they hold the concrete setup, not this overview:

- `references/sentry.md` — init patterns, PII scrubbing, release/sourcemaps, sampling
- `references/logging.md` — structured logging, trace propagation, error logging, request lifecycle, redaction, sampling
- `references/otel-integration.md` — OTel SDK wiring to Pino/Winston, TracerProvider setup, span instrumentation, W3C traceparent propagation, OTLP/Loki/ELK export, multi-service distributed correlation, async queue context propagation
- `references/grafana.md` — datasource choice, dashboard-as-code, the panels that matter
- `references/slo-alerts.md` — SLO definition, burn-rate alerts, runbook linking
- `references/operational-readiness.md` — business-transaction lifecycle instrumentation, stuck /
  terminal-without-artifact detection and committed ops queries, on-call + ack + escalation +
  "is it broken?" tree, the acceptance drill, history-backed readiness measurement,
  honest coverage claims
- `references/serverless-vs-server.md` — why `prom-client` dies on serverless and what to do instead
- `references/browser-rum.md` — browser RUM with `@sentry/react`, error boundaries, sourcemap upload for Next.js, session replay sampling, Core Web Vitals as SLIs

## Audit checklist (for craft-audit)

When `craft-audit` plans an observability pass for a scope, it turns this checklist into the
`plan.md` todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor
to what discovery found: skip a step that genuinely doesn't apply with a one-line reason; never
silently drop one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission
format" (authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-OBS-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-OBS-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Confidence:**` — `verified | inferred | unverified-from-repo`, absent
means `verified` — then optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] Map what observability already exists (Sentry, logger, `prom-client`, OTel, `/health`,
  `/metrics`, env schema) before proposing anything — flag duplicated or forked instrumentation →
  SKILL.md "Operating principle — discover before you build"
- [ ] Confirm the runtime (serverless vs long-lived) drives the metrics/tracing approach — flag
  `prom-client` or other pull-based scraping on serverless, and missing flush-before-exit →
  `references/serverless-vs-server.md`
- [ ] Audit Sentry: unhandled errors + rejections captured, PII scrubbed in `beforeSend`, events
  tagged with release + environment, `tracesSampleRate` set deliberately (not 1.0 in prod), sourcemaps
  uploaded — flag missing init, leaked PII, or untagged events → `references/sentry.md`
- [ ] Check logs are structured JSON from one central logger with a stable `traceId`/`requestId` on
  every line — flag bare `console.log` in production code, missing trace propagation, or unredacted
  secrets/PII → `references/logging.md`
- [ ] Audit error logging: errors logged with `err.{type,message,code}` + entity ids + `durationMs`,
  not plain strings; error not logged twice (catch site + global handler); `err.stack` gated on env or
  Sentry availability → `references/logging.md § Structured error logging`
- [ ] Confirm one HTTP request completion event per request (status, duration, path, identity) — flag
  missing request lifecycle logging or raw URL with query params → `references/logging.md § Request lifecycle events`
- [ ] If OTel is present, verify `traceId`/`spanId` are injected from the active span (not a parallel
  self-generated UUID), instrumentation loads before logger imports, and outbound calls propagate
  `traceparent` — flag absent or misaligned trace context → `references/otel-integration.md`
- [ ] Verify dashboards are provisioned as code over a runtime-appropriate datasource with RED/USE
  panels that matter — flag hand-clicked dashboards, wrong datasource, or vanity panels with no signal
  → `references/grafana.md`
- [ ] Audit alerts against user-facing symptoms — flag alerts that don't map to pain. **SLO
  applicability gate:** multi-window burn-rate / full error-budget programs are for services with
  real traffic and on-call expectations — not every pre-launch MVP. Sentry + basic error visibility
  stay high priority regardless of stage; do not demand a full SLO program on an early-stage app
  with no pager → `references/slo-alerts.md`
- [ ] Confirm every *paging* alert links a runbook — flag any paging alert with no runbook as noise
  to delete or document (N-A if the project has no pager yet) → `references/slo-alerts.md`
- [ ] Check for silent degradation: a down dependency surfaces via health endpoint + log + metric —
  flag dependencies that fail quietly with no observable signal → SKILL.md "Standing opinions"
- [ ] Name the project's core business transaction (the run, checkout, send, sync) and confirm its
  lifecycle is observable: start + terminal state emitted as events *and* counted as a metric, with
  ids only and no payload/PII — flag an observability setup that watches only infrastructure while
  the transaction the product exists to perform is invisible; flag a success rate inferred purely
  from a mutable `status` column when the transaction retries →
  `references/operational-readiness.md § Name the core transaction first`
- [ ] Check expected business failures (bad customer input, declined card, rejected upload) are
  counted but routed away from the error tracker, while system failures (timeouts, unhandled
  exceptions) reach it tagged with the transaction id — flag either direction: customer mistakes
  opening incidents, or system failures visible only as a status value →
  `references/operational-readiness.md § Instrument the lifecycle`
- [ ] Verify stuck and half-finished work is detectable: a query or gauge for non-terminal rows past
  a per-state threshold, and — where a terminal state promises an artifact (report, invoice,
  outbound message) — a terminal-without-artifact check with no trailing window that forgets
  unresolved violations; queries committed as a file, not prose in a doc — flag a threshold with no
  measured duration or timeout/retry budget behind it, a check polled less often than the threshold
  it enforces, and either check missing →
  `references/operational-readiness.md § Detect stuck and half-finished work`
- [ ] Confirm the human loop exists in writing: who operates it, where alerts land (a destination
  seen away from the laptop), console links, and a <5-minute "is it broken?" tree — flag alerts
  configured with no named recipient. Scale to maturity: solo pre-launch, "operator: me, alerts to
  my phone, no escalation" passes; named backup, ack convention, and escalation times are required
  only once a second person could respond → `references/operational-readiness.md § The human loop`
- [ ] Check the loop has been proven, not assumed: success path, a forced *system* failure, a
  plausible *business* failure, stuck detection, and one alert delivered down the production
  notification path — with the drill date recorded — flag an alerting setup that has never delivered
  to a human. Acked-by-someone-else applies only where there is a team →
  `references/operational-readiness.md § Prove the loop: the acceptance drill`
- [ ] Where an availability/readiness number is claimed, verify one declared source of truth retains
  history across the SLO window and the calculation is documented (manual weekly is acceptable at
  early stage) — flag "green right now" presented as an SLO, tail-only log sources, a red synthetic
  check that is the sole history source, and competing uncanonical sources →
  `references/operational-readiness.md § Measure readiness from retained history`
- [ ] When the service has real traffic / on-call: error-budget policy exists (who is notified at
  50%/25% remaining? deploy freeze gate?). For early MVPs, skip or mark partial with a one-line
  reason — do not invent a full SLO program → `references/slo-alerts.md § Error-budget policy`
- [ ] Confirm the deploy pipeline's post-deploy gate (craft-infra) has an error-rate signal to
  read when that gate exists → `references/slo-alerts.md § Error-budget policy`


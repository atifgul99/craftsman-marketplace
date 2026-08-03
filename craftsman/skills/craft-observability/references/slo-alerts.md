# SLO Alerts

Alerts that fire on raw resource metrics — CPU over 70%, heap > 2 GB — measure your infrastructure, not your users' experience. Users don't feel your CPU; they feel slow pages, broken checkouts, and failed API calls. The discipline: **define SLOs from user-facing SLIs, alert on burn rate against those SLOs, and treat any alert without a user-visible symptom or a linked runbook as noise to delete.** An alert that wakes someone up at 2 am should answer "users are hurting right now" — not "a gauge crossed a threshold."

**Applicability (persona gate).** Multi-window burn-rate alerts, formal error budgets, and deploy-freeze
policy are for services with **real traffic and on-call expectations**. A pre-launch or early MVP
still needs Sentry + basic error visibility (high priority always) — it does **not** need a full SLO
program. Mark full-SLO checklist items partial/N-A with a one-line reason when maturity is early;
do not invent pager theater for a solo builder with no production users yet.

> **Scope split.** This file owns SLO definition, SLI selection, error-budget accounting, burn-rate (multi-window) alert construction, severity/routing, and runbook linking. The **metrics layer the alerts query** — Grafana dashboards, Prometheus/OTLP data sources, recording rules — is `grafana.md`. Error *capture and grouping* upstream of any metric is `sentry.md`. Log-based SLIs (where you can't get a counter from the metrics layer) are in `logging.md`. Deploy and health-probe gates that can halt a rollout before the error budget drains belong to **`craft-infra`** → `ci-cd.md` and `runtime-health.md`. What counts as an error in the first place — status codes, exception classes, graceful vs hard failures — is the contract defined in **`craft-backend`** → `error-contract.md`.

---

## Contents

- [Pick SLIs that proxy user pain](#pick-slis-that-proxy-user-pain)
- [Set the SLO and calculate the error budget](#set-the-slo-and-calculate-the-error-budget)
- [Burn-rate alerting (multi-window)](#burn-rate-alerting-multi-window)
- [Severity and routing](#severity-and-routing)
- [Every paging alert links a runbook](#every-paging-alert-links-a-runbook)
- [Alert on symptoms, not causes](#alert-on-symptoms-not-causes)
- [Error-budget policy](#error-budget-policy)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Pick SLIs that proxy user pain

A Service Level Indicator (SLI) is the ratio of *good events* to *total events* as seen from the user's perspective. Good choices proxy what users actually notice:

| User-facing concern | SLI |
| --- | --- |
| "Is it working?" | Request success rate — HTTP 5xx / gRPC server-error codes (INTERNAL, UNAVAILABLE, DATA_LOSS, UNKNOWN) as the error numerator — exclude client-error codes such as NOT_FOUND, INVALID_ARGUMENT, and PERMISSION_DENIED, which do not indicate server-side failure |
| "Is it fast?" | Latency at the tail — p95 or p99 response time under a threshold (e.g. < 500 ms) |
| "Can I read my data?" | Read availability — successful reads / total reads |
| "Did my payment go through?" | Critical-path success rate — checkout / payment / send scoped to the key flow |

Avoid SLIs that don't map to user perception: internal queue depth, worker thread count, connection pool fill — these are inputs to a problem, not the problem itself. An SLI must be computable from an observable counter (e.g. `http_requests_total{status=~"5.."}` in Prometheus, span error rates in OTLP, or a log-derived counter). Discover what your stack emits before deciding — `grafana.md` covers the datasource setup.

A service may have *multiple* SLIs covering different user journeys (read path vs write path, public API vs webhook delivery) — track them separately rather than averaging them together and hiding a broken write path behind a healthy read path.

---

## Set the SLO and calculate the error budget

An SLO is a target for the SLI over a rolling window, e.g. "99.5% of HTTP requests succeed over 28 days." Set it at the level that reflects what users genuinely notice, not the highest number that sounds impressive. An SLO you can't meet without heroics costs more in alert fatigue than it saves.

**Error budget** is the headroom the SLO permits:

```
error_budget_per_window = (1 - SLO_target) × total_events_in_window

# example: 99.5% SLO over 28 days, ~1 M requests/day
# budget = 0.005 × 28,000,000 = 140,000 bad requests
```

The error budget is the currency of reliability work. Burning it fast means users are hurting now; burning it slowly is business as usual. The budget remaining at the end of the window informs whether to ship risky changes (budget to spare → ship) or invest in reliability (budget gone → freeze deploys, fix).

Rolling windows (28 days is common; 30 also works) are preferred over calendar months — they avoid budget resets giving a false "we're fine" signal at the start of each month.

---

## Burn-rate alerting (multi-window)

A single threshold on the raw error rate misses two failure modes: a severe outage burns the budget in minutes (needs immediate page) but a slow leak doesn't trigger it until the budget is already gone. **Multi-window burn-rate alerting solves both.**

A burn rate of `N` means you are consuming the error budget N× faster than the SLO allows. At burn rate 1 you exactly exhaust the budget by the end of the window; at burn rate 14.4 you exhaust a 28-day budget in ~2 days.

### The four alert windows (Google SRE-derived)

| Window pair (long / short) | Burn rate | Budget consumed | Page? | Rationale |
| --- | --- | --- | --- | --- |
| 1 h / 5 min | 14.4× | ~2% in 1 h | Yes (critical) | Severe outage — exhausts 28-day budget in ~2 days |
| 6 h / 30 min | 6× | ~5% in 6 h | Yes (critical) | Major incident — exhausts 28-day budget in ~5 days |
| 1 d / 2 h | 3× | ~10% in 1 d | Ticket / warn | Fast leak — on-call notified, not woken |
| 3 d / 6 h | 1× | ~10% in 3 d | Ticket | Slow burn — reliability backlog item |

The *short window* prevents the alert from firing on a brief spike that already recovered; the *long window* ensures the alert only fires when the burn is sustained. **Both conditions must be true** to alert.

A Prometheus / Grafana alerting rule for the 1-hour / 5-minute pair looks like:

Define the per-window rate recording rules before wiring the alert — the alert `expr` references those recording-rule metrics. The recording rules belong in this file (or in the Prometheus rules config you maintain alongside these alerts); `grafana.md` does not define recording rules.

The recording-rule metric names (e.g. `job:slo_errors:rate1h`) are project-specific — check the existing Prometheus recording rules in the repo before using these names, and align to whatever naming convention is already in place.

```yaml
# recording rules — define these in your Prometheus rules file (e.g. slo-recording-rules.yaml)
# They compute per-window error ratios from raw counters so alert expressions stay readable.
- record: job:slo_errors:rate5m
  expr: |
    sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum by (job) (rate(http_requests_total[5m]))

- record: job:slo_errors:rate1h
  expr: |
    sum by (job) (rate(http_requests_total{status=~"5.."}[1h]))
    /
    sum by (job) (rate(http_requests_total[1h]))

# Add equivalent rules for other windows (30m, 2h, 6h, 3d) as needed.
# Adapt metric names to what your framework/SDK actually exposes (check /metrics output).
```

```yaml
# alerting rules — reference the recording rules defined above
- alert: HighBurnRate1hCritical
  expr: |
    # job:slo_errors:rateXX must be the error *ratio* (bad_requests / total_requests), not a raw count rate
    (
      job:slo_errors:rate1h{job="api"} > (14.4 * 0.005)
    ) and (
      job:slo_errors:rate5m{job="api"} > (14.4 * 0.005)
    )
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "SLO error budget burning at >14x for {{ $labels.job }}"
    runbook: "https://runbooks.internal/api/high-error-rate"
    description: >
      Error rate {{ $value | humanizePercentage }} sustained over 1h and 5m windows.
      At this rate the 28-day error budget exhausts in ~2 days.
```

Adapt the metric names, thresholds, and `for` clause to the stack you discover in the repo. The `0.005` above is `1 − 0.995` (a 99.5% SLO); substitute your actual target. Record the per-window rate as a Prometheus recording rule rather than computing it inline in every alert — the recording rule is cheaper and reusable across dashboards.

---

## Severity and routing

Not every alert deserves a page. Route by the urgency of budget consumption:

| Burn tier | Action | Channel |
| --- | --- | --- |
| Critical (14.4× or 6×) | Page on-call immediately | PagerDuty / Opsgenie / on-call rotation |
| Warning (3×) | Ticket + async notification | Slack #alerts, Jira/Linear ticket auto-created |
| Info (1×) | Reliability backlog | Weekly review; no real-time notification |

**One paging alert per symptom.** If two alert rules both fire on the same root cause (high error rate and high latency on the same endpoint), the on-call receives duplicate pages, not duplicate information. Consolidate — page on the SLI that best proxies the user symptom, let dashboards expose the correlated signals.

Do not create a severity hierarchy that routes all alerts to on-call. On-call rotation burn-out is a reliability failure too. Reserve pages for "users are hurting right now and this won't self-resolve in minutes."

---

## Every paging alert links a runbook

A paging alert without a runbook forces the on-call to reconstruct diagnosis steps under pressure. **Every critical alert (which pages on-call) must include a `runbook` annotation linking to a runbook that exists and is current. Warning-tier alerts (which open tickets, not pages) must also link a runbook** — the engineer triaging the ticket needs the same context. A runbook URL in the annotation that 404s is worse than no URL — it wastes time during an incident.

A minimal runbook covers:

1. **What this alert means** — which SLI, what user impact.
2. **Immediate triage steps** — which dashboard to open, which logs to check (`logging.md`), which Sentry issue query to run (`sentry.md`).
3. **Common causes and their fixes** — ordered by likelihood based on past incidents.
4. **Escalation path** — who to call if the on-call can't resolve within N minutes.
5. **How to silence safely** — conditions under which silencing is appropriate, and the maximum silence window.

Store runbooks alongside the service (e.g. `docs/runbooks/`) or in a shared ops wiki, and include the path in the alert annotation. Review runbooks after every incident; a runbook that never gets updated is a liability.

A runbook doesn't need to be a polished doc — a 10-line file in the repo beats a good one that never gets written. Minimal skeleton to copy into `docs/runbooks/<alert-name>.md`:

```markdown
# <Alert name>

**What this means:** <SLI/service> is <symptom>. Users experience: <impact>.

**First 3 checks:**
1. <dashboard/query to open first>
2. <log or Sentry query to run next>
3. <most likely cause given past incidents>

**Escalate to:** <person/team> if unresolved after <N> minutes.
```

An alert without even this at 2 am is just anxiety with a PagerDuty label.

---

## Alert on symptoms, not causes

The most common alert-fatigue driver is alerting on causes ("database CPU 80%") rather than symptoms ("checkout success rate below SLO"). Infrastructure metrics belong on dashboards for *diagnosis*, not on pager rotations for *detection*.

**Causes to move off paging:**

- CPU / memory / disk usage thresholds — they predict nothing reliably; a full disk may not affect users if it's for logs
- Queue depth in isolation — a deep queue is fine if throughput is keeping up
- Pod restart count — if restarts don't degrade the SLI, they're noise; if they do, the SLI alert catches it
- Dependency health checks in isolation — alert when the *downstream effect on users* materialises, not when a dependency returns `500` to a synthetic probe

**Keep as paging alerts:**

- SLI burn rate exceeding budget thresholds (above)
- Availability zero — the service is completely down and no requests succeed
- Data-loss or security-critical conditions that have no SLI proxy and can't wait for budget accumulation

If you want early warning before the SLI degrades, use the 3× / 1-day burn tier as a warning-level ticket — not a page.

---

## Error-budget policy

The error budget should drive team decisions, not just alert routing. Document and agree on a policy before incidents happen:

- **Budget > 50% remaining:** feature development proceeds normally; risky experiments permitted.
- **Budget 25–50% remaining:** deployment freeze on high-risk changes; reliability items enter the sprint backlog.
- **Budget < 25% remaining:** feature work halts; entire team focuses on reliability improvements until the budget recovers.
- **Budget exhausted:** post-mortem required before any new feature deploys; SLO re-evaluation considered.

A rolling window recalculates continuously — at every moment the available budget reflects the trailing 28 or 30 days, with no discrete reset point. That said, exhausting a budget in week 1 and recovering in week 4 still means users had a terrible month. Track cumulative incidents, not just end-of-window state.

Connect the error budget to the deploy gate in CI/CD: if **`craft-infra`** → `ci-cd.md` has a deployment pipeline, wire an error-budget check as a pre-deploy gate — a deploy into a budget-exhausted service needs explicit override and justification. Health-probe state (see **`craft-infra`** → `runtime-health.md`) feeds directly into this picture: a failing health probe is an early signal that budget is about to drain.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Alert fires on CPU, memory, or disk threshold alone | Move to a dashboard panel; alert on the SLI that reflects user impact instead |
| Single-window alert (no short + long window pair) | Add the companion short window so a recovered spike doesn't sustain the page |
| Burn rate threshold hardcoded without reference to the SLO target | Derive the threshold from `1 − SLO_target`; document the derivation |
| Paging alert with no `runbook` annotation (or a 404 runbook URL) | Add/fix the runbook link; block merge until it exists and resolves |
| All alert severities route to on-call | Separate critical (page), warning (Slack/ticket), info (backlog); only critical pages |
| SLI averages across multiple user journeys | Split into per-journey SLIs; a broken write path hidden behind a healthy read path is a miss |
| Alert fires when the condition recovers in < 2 min | Add or increase the `for` clause so transient spikes don't page |
| Error budget tracked on a calendar month, not a rolling window | Switch to a rolling 28- or 30-day window to avoid false resets on day 1 of each month |
| Runbook exists but has not been updated since last incident | Review and update after every incident; stale runbooks mislead under pressure |
| Cause-level alert duplicates what a burn-rate alert already catches | Remove the cause-level alert; keep it as a dashboard panel for diagnosis |
| Deploy proceeds without checking error-budget state | Wire an error-budget gate in CI (`craft-infra` → `ci-cd.md`); require override when budget < 25% |

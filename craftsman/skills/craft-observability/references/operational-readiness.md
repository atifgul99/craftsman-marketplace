# Operational Readiness

The four pillars make a *service* observable: you can see errors, logs, metrics, and SLO burn. They
do not, on their own, tell you whether the thing customers pay for actually completed. A service can
be green on every infra panel while every customer's job is stuck in `processing`, or finished with
no report ever generated. **Operational readiness is the gap between "the service is instrumented"
and "a human can operate it": the core business transaction is visible end to end, stuck and
half-finished work is detectable, a named person receives alerts, and the whole loop has been proven
once by deliberately breaking it.**

**Applicability (persona gate).** This file scales down. A solo builder with ten users still needs
the transaction lifecycle visible, a stuck-work query, and one tested notification path — that is
maybe two hours of work. They do not need a rotation, an ack SLA, or a formal game-day cadence.
Mark team-shaped items partial/N-A with a one-line reason rather than inventing pager theater; see
`slo-alerts.md` for the same gate applied to SLOs.

> **Scope split.** This file owns the *business transaction* layer and the *human* layer: naming the
> core transaction, instrumenting its lifecycle, detecting stuck/missing-terminal work, the on-call
> and runbook contract, the acceptance drill, and history-backed readiness measurement. The
> mechanics it builds on live elsewhere: event/log shape is `logging.md`, error capture is
> `sentry.md`, panels and datasources are `grafana.md`, SLI/SLO/burn-rate construction and runbook
> *linking* are `slo-alerts.md`. Why a job can silently vanish in the first place — transaction
> boundaries, enqueue-after-commit, idempotency, outbox — is **`craft-backend`** →
> `side-effects.md`. Liveness/readiness probe construction and queue-handler runtime concerns are
> **`craft-infra`** → `runtime-health.md`; deploy gates are **`craft-infra`** → `ci-cd.md`.

---

## Contents

- [Name the core transaction first](#name-the-core-transaction-first)
- [Instrument the lifecycle](#instrument-the-lifecycle)
- [Detect stuck and half-finished work](#detect-stuck-and-half-finished-work)
- [The human loop](#the-human-loop)
- [Prove the loop: the acceptance drill](#prove-the-loop-the-acceptance-drill)
- [Measure readiness from retained history](#measure-readiness-from-retained-history)
- [Be honest about coverage](#be-honest-about-coverage)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Name the core transaction first

Every product has one or two transactions that *are* the product: the audit run, the checkout, the
document conversion, the outbound campaign send, the sync. Infra observability is second-order — it
matters because it predicts damage to that transaction.

Before adding a panel, write the transaction down in one line and map its states:

```
audit run:  queued → running → (completed | failed | cancelled)
            + artifact: a report row must exist for every completed run
```

Three things fall out of that sentence, and each becomes a signal:

| From the map | The signal it demands |
| --- | --- |
| **Terminal states** (`completed`, `failed`, `cancelled`) | Rate of each over time — the transaction success rate, which is your first real SLI |
| **Non-terminal states** (`queued`, `running`) | Age of the oldest one — the stuck-work signal |
| **The artifact/side effect** the terminal state promises | Terminal-without-artifact count — the silent-failure signal |

The third row is the one teams miss. A run that ends `completed` with no report is worse than a
failed run: it is a failure the system believes succeeded, so nothing alerts and the customer finds
it for you.

**Discovery.** Find the transaction from the schema and the job definitions, not from the
dashboard: a status/state enum column, a workflow or queue name, a `*_runs` / `*_jobs` /
`*_orders` table with timestamps. If the app has a background worker, the transaction almost
certainly lives there — the HTTP layer just starts it.

**Multi-tenant note:** the same query, sliced by tenant/account, answers "is it broken for
everyone or for one customer?" That slice is worth building once and reusing.

---

## Instrument the lifecycle

Three emissions cover the transaction. Follow the shape rules in `logging.md`; this is only what
must exist.

1. **A start event** — `info`, with the transaction id and the tenant/account id.
2. **A completion event** — `info` on success / `error` on failure, with the same ids,
   `durationMs`, and the terminal state. `err.{type,message,code}` on the failure path
   (`logging.md § Structured error logging`).
3. **A counter or histogram** per terminal state, so rate and latency are queryable without a log
   scan (`logging.md § Logs vs metrics`). On a long-lived worker that is a Prometheus counter; on
   serverless it is OTLP or the vendor SDK — `serverless-vs-server.md` decides which.

**Stage-level detail only where a stage can fail independently.** If the report step can fail while
the analysis step succeeded, the report step needs its own success/failure signal. Otherwise a
single lifecycle pair is enough — do not emit an event per row processed.

**IDs only, never payload.** Telemetry carries `runId`, `tenantId`, `documentId` — never document
text, prompts, model output, customer names, or file contents. This is the same rule as
`sentry.md` PII scrubbing, applied to logs and metric labels, and it is what lets you screenshot a
dashboard during an incident. High-cardinality ids belong in log fields, not metric labels
(`grafana.md` on label cardinality).

**Wire the transaction failure rate into Sentry too.** A failed run should produce a Sentry event
tagged with the transaction id, so the "why" (stack, breadcrumbs) sits one click from the "how
many" (dashboard).

---

## Detect stuck and half-finished work

Two failure classes never appear in an error rate, because nothing errored:

- **Stuck:** a row sitting in a non-terminal state past any plausible duration. The process died
  mid-run, the queue lost the message, an external call hung with no timeout
  (**`craft-infra`** → `scale-resilience.md`), or a lock was never released.
- **Terminal without its artifact:** the run says `completed`, the report/invoice/email does not
  exist. Usually a transaction-boundary or enqueue-after-commit bug
  (**`craft-backend`** → `side-effects.md`).

Both are cheap to detect from the database you already have. **Commit the queries as a file** —
`docs/ops/sql/<transaction>-ops.sql` or equivalent — not as prose in a runbook. A query pasted into
a doc gets stale; a committed file gets reviewed, reused by the runbook, and can be pointed at by a
dashboard or a cron check.

```sql
-- docs/ops/sql/audit-run-ops.sql  (adapt table/column names to the schema you discovered)

-- 1. Runs by state, last 24h — the shape of normal
SELECT status, count(*) FROM audit_runs
WHERE created_at > now() - interval '24 hours' GROUP BY status;

-- 2. Stuck: non-terminal and older than the threshold
SELECT id, tenant_id, status, created_at, now() - created_at AS age
FROM audit_runs
WHERE status NOT IN ('completed', 'failed', 'cancelled')
  AND created_at < now() - interval '2 hours'
ORDER BY created_at;

-- 3. Terminal without artifact — the silent failure
SELECT r.id, r.tenant_id, r.completed_at
FROM audit_runs r
LEFT JOIN reports rep ON rep.audit_run_id = r.id AND rep.status = 'succeeded'
WHERE r.status = 'completed'
  AND r.completed_at > now() - interval '24 hours'
  AND rep.id IS NULL;
```

**Set the threshold from data, not vibes.** Use p95 (or p99) observed duration times a safety
factor — a two-hour threshold on a job that normally takes four hours alerts on nothing but itself.
If duration isn't measured yet, that is the first thing to instrument.

**Then give the query somewhere to run.** In rough order of cost:

| Where | When it fits |
| --- | --- |
| Runbook query a human runs during triage | Minimum bar — always do at least this |
| Scheduled job that emits a gauge (`stuck_runs`, `terminal_without_artifact`) | Once the metrics layer exists; alerts ride the gauge like any other |
| Dashboard panel via a SQL-capable datasource | When the datasource is already provisioned (`grafana.md`) |

The gauge is the goal, but a committed query plus a runbook step beats a gauge that nobody built.

**Cancellation is not failure.** Keep user-cancelled runs out of the failure numerator or the
success rate lies — the same distinction `slo-alerts.md` draws between client and server errors.

---

## The human loop

An alert nobody receives is a log line with extra infrastructure. Before launch, the following must
be written down — in the repo, next to the code, not in someone's head:

| Required | Why it's on the list |
| --- | --- |
| **Named operator and backup** (actual names, not "the team") | "Someone will see it" means nobody sees it at 2 am |
| **Ack channel** — where alerts land and where a human confirms they're on it | An unacked alert is indistinguishable from an unseen one |
| **Escalation path** with times — who is contacted if no ack in N minutes | Removes the judgment call from the worst moment to make one |
| **Console links** — error tracker, dashboard, logs, queue/workflow UI, hosting provider, DB | Hunting for a URL during an incident is pure lost minutes |
| **An "is it broken?" decision tree** answerable in under 5 minutes | The first question every incident starts with |
| **The transaction queries** (above) and where their history lives | Turns "customers are complaining" into a number |

The decision tree is the highest-value paragraph in any runbook. It is short by design:

```
1. Is the app up?            → health/ready endpoint, hosting status page
2. Are errors spiking?       → Sentry, last 1h, filtered to production
3. Are transactions moving?  → runs-by-state query, last 1h vs the same hour yesterday
4. Is work stuck?            → stuck query
5. Is the worker/queue alive? → worker metrics or workflow UI
   None of the above red → likely a single-customer issue: slice by tenant id
```

**Per-alert runbooks are `slo-alerts.md`'s job** (what this alert means, triage, common causes,
escalation, safe silencing). This file's concern is that the *service-level* facts — who, where,
which links, which queries — exist at all, and that the on-call layer is real before the alerts
that depend on it are written.

**Maturity ladder.** Solo pre-launch: you are the operator, the ack channel is your phone, and the
escalation path is "there isn't one" — write that line down and move on. With a team or paying
customers: named backup, a real ack channel, and escalation times.

---

## Prove the loop: the acceptance drill

Observability you haven't watched work isn't done. Configuration looks identical whether or not the
notification path is wired — the only way to know is to break something on purpose while you're
watching.

Run these four before launch and after any change to the alerting path. Each has a pass criterion,
not a vibe:

| Drill | How | Pass criterion |
| --- | --- | --- |
| **Success path** | Run one real transaction end to end | Start and completion visible in logs + dashboard; the artifact exists |
| **Controlled failure** | Force a failure (bad input, kill a step, stub a dependency to throw) | Failure visible in the error tracker *and* in the terminal-state counter, with the transaction id attached and no payload leaked |
| **Stuck detection** | Kill the worker mid-run, or insert a synthetic non-terminal row past the threshold | The stuck query / gauge surfaces it, keyed by id only |
| **Human notification** | Fire one alert down the real path | A human receives it on the real channel *and* acks it |

Two rules that decide whether the drill is worth anything:

- **Use the production notification path.** A test alert routed to a test channel proves the test
  channel works. Fire at least one down the path an incident would actually take.
- **Record the date and the result** where the SLO/alert docs live, and re-run after touching alert
  routing, the DSN, or the worker's deploy shape. A drill from six months and three integrations
  ago is a claim, not evidence.

**Prefer a staging or off-peak run** for the destructive cases, and use a synthetic row rather than
a real customer's job whenever the class of failure allows it.

---

## Measure readiness from retained history

"The health check is green right now" is not an availability number. An SLO is a ratio over a
window, and a ratio needs history — which means one chosen source of truth with **verified
retention across the SLO window** (`slo-alerts.md` defines the window and the budget math; this is
the plumbing that makes it computable).

Pick exactly one source of truth and check what it keeps:

| Candidate source | The question to actually verify |
| --- | --- |
| Metrics backend (Prometheus/Grafana Cloud/vendor) | What is the retention on this tier — does it cover the 28/30-day window? |
| Uptime/probe service | Does it retain per-check *history*, or only the current status and a short tail? |
| CI-based synthetic check | Is the job green *and* are its artifacts/logs retained past their default expiry? |
| Application log store | Retention window, and is the probe endpoint even logged? |

Three traps, all common:

- **Tail-only logs.** A rotated log file or a provider console showing "recent events" gives you
  today, not the window. If that's the only source, add an append-only probe record or fix the
  alternative — do not compute an SLO from it and pretend.
- **A red synthetic check that is also the only history source.** Then the number is unmeasured, not
  100%. Fix the check first; state the gap until it's fixed.
- **Two sources that disagree.** Pick one as canonical and say so in writing, or every incident
  review reopens the question.

**Document the calculation, even if it starts manual.** "Weekly: successful checks ÷ total checks
from <source>, recorded in <file>" is a legitimate v1. An automated multi-window burn-rate rule is
better and is `slo-alerts.md`'s territory — but only once the underlying history exists, and it is
not required of an early-stage MVP.

---

## Be honest about coverage

The failure mode at the end of an observability push is overclaiming — a dashboard that looks
complete, a readiness doc that implies every SLI is instrumented, and a gap nobody discovers until
the incident that lands in it.

- **State the gap explicitly.** "Transaction success, stuck detection, and error rate are
  instrumented; 30-day budget burn is computed manually each week; browser RUM is not wired" is a
  usable status. "Observability: done" is not.
- **Deep links beat fake graphs.** If a signal genuinely lives in another console — the hosting
  provider's analytics, the workflow UI, a vendor dashboard — put a link row on the dashboard
  pointing there. Do not build a panel whose query you know returns nothing; a "No data" panel
  trains people to ignore panels (`grafana.md § Vanity panels`).
- **Cut scope, not honesty.** Deferring browser RUM or multi-window burn alerts to next week is
  fine and usually correct. Deferring them *silently* is what turns a known gap into an outage.

---

## Quick-reject checklist

- Dashboards and alerts cover infrastructure only — no signal for the transaction the product
  exists to perform
- Transaction states are logged but never counted, so "how many failed today?" needs a log scan
- No stuck-work detection: a non-terminal row can age indefinitely with nothing firing
- No terminal-without-artifact check on a transaction that promises an artifact
- Stuck threshold picked by feel, with no measured duration behind it
- Ops queries live only as prose in a doc — nothing committed, nothing runnable
- Telemetry carries payload, prompts, or customer content instead of ids
- Alerts exist with no named recipient, no ack channel, and no escalation path
- The notification path has never been fired end to end to a human
- No controlled-failure or stuck drill has been run; the loop is assumed, not proven
- Readiness claimed from a green check with no retained history behind it
- Two competing sources of truth for availability, neither declared canonical
- Dashboard panels that render "No data" because the metric was never wired
- Coverage described as complete when known SLIs are uninstrumented

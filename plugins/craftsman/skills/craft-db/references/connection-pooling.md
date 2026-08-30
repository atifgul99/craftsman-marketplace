# Connection Pooling

A database connection is not free. Each Postgres connection consumes roughly 5–10 MB of server memory, and the backend process overhead means you hit diminishing returns (and then wall-clock degradation) long before you run out of RAM. The discipline: **size the pool to the actual concurrency your workload produces, not to "just make it big enough."** An unconfigured pool — or no pool at all — is the most common cause of "database is slow" complaints in freshly deployed MVPs.

> **Scope split.** This file owns connection pool configuration and sizing: pool_size math, pgBouncer vs serverless driver patterns, Drizzle/postgres.js config, leak detection, and transaction-mode gotchas. Query patterns and tenant scoping are in `access-patterns.md`. Schema and migration tooling are in their own files. Deploy-side environment variables (DATABASE_URL, connection string construction) belong to `craft-infra` → `build-release.md`. Runtime-model constraints (serverless vs long-lived, per-instance multiplication) → `craft-infra` → `runtime-health.md`; this file owns the sizing math and driver/pooler config.

> **Dialect note:** These docs assume PostgreSQL. SQLite (single-writer, no separate server, pooling handled by the driver) and MySQL (similar pool concepts, different default limits) have different constraints — verify your dialect.

---

## Contents

- [Pool sizing math](#pool-sizing-math)
- [pgBouncer vs Neon serverless driver](#pgbouncer-vs-neon-serverless-driver)
- [Drizzle + postgres.js pool config](#drizzle--postgresjs-pool-config)
- [Connection leak detection](#connection-leak-detection)
- [pgBouncer transaction mode gotchas](#pgbouncer-transaction-mode-gotchas)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Pool sizing math

**The headline for an MVP: start at 5–10 connections per instance and measure.** Don't derive a
number from a formula before you have real traffic — tune from `pg_stat_activity` and observed
queue/wait time once the app is live.

The model behind that number, for when you need to reason about scaling past the starting point:

```
pool_size ≈ expected concurrent requests × fraction of request time spent holding a connection
```

Where the second factor is the share of a typical request's wall-clock time actually spent waiting
on the DB (0.0–1.0) — not total request time, and not worker count on its own.

**Worked example:** an instance handling 20 concurrent requests, where each request holds a DB
connection for about 25% of its total time (the rest is spent on other I/O, serialization, etc.):

```
pool_size ≈ 20 × 0.25 = 5
```

Five connections lets that instance's concurrency be served without every request queueing for a
connection, without opening far more connections than are ever simultaneously in use.

**Ceiling check:** more than 25–30 connections from a single app instance to a managed Postgres (RDS, Supabase, Neon) starts to strain the DB server unless you have confirmed the instance tier supports it. Check your provider's connection limits before tuning up.

**Postgres hard limit reminder:** Postgres has a `max_connections` server parameter (default 100 on many managed instances). Reserve ~5 for superuser/admin connections. Everything else is available to the pool. If `max_connections = 25` (common on small managed tiers), your app pool must stay under ~20.

```
max_app_connections = max_connections - superuser_reserve (typically 5)
pool_size           = min(desired_pool, max_app_connections / num_app_instances)
```

---

## pgBouncer vs Neon serverless driver

### When to use pgBouncer

pgBouncer is a connection pooler that sits between your app and Postgres. It is the standard choice for long-lived server processes (containers, VMs) where you control the infrastructure.

- **Transaction pooling mode** (pgBouncer's own default `pool_mode` is actually `session` — but transaction mode is what nearly every managed pooler you'll encounter ships as the default, e.g. Supabase's and Neon's pooled connection strings): connections are returned to the pool after each transaction, not at the end of the TCP session. This multiplexes many app connections onto far fewer Postgres connections — useful when you have many Node workers or services connecting. If you're standing up pgBouncer yourself, you must set `pool_mode = transaction` explicitly to get this behavior.
- **Session pooling mode**: one Postgres connection per client session. Fewer multiplexing benefits, but fully compatible with all Postgres features including `LISTEN/NOTIFY` and prepared statements.

Use pgBouncer when:
- Running on a VPS, EC2, Fly.io, Railway, or Render with a persistent Postgres instance.
- You need to multiplex many app instances (e.g. 10 Fly machines each with a pool of 5) onto a Postgres instance with a low `max_connections`.

### When to use the Neon serverless driver

Neon's serverless driver (`@neondatabase/serverless`) is designed for environments where HTTP is the only available transport — Cloudflare Workers, Vercel Edge Functions, AWS Lambda. It opens a WebSocket or HTTP connection per query rather than a persistent TCP pool.

- Do NOT use the Neon serverless driver in a long-lived Node.js server (Express, Fastify, Next.js API routes on Node runtime). Use `postgres.js` with pgBouncer there — the serverless driver's per-request connection overhead is wasteful in a persistent process.
- DO use it in edge/serverless runtimes where TCP persistent connections are not supported.

---

## Drizzle + postgres.js pool config

`postgres.js` is the recommended Postgres driver for Drizzle on Node.js. It manages a connection pool internally.

**Concrete config example (single-instance MVP, pgBouncer in front):**

```ts
// db/client.ts
import postgres from 'postgres'
import { drizzle } from 'drizzle-orm/postgres-js'
import * as schema from './schema'

const connectionString = process.env.DATABASE_URL!

// Pool config — tune to your instance size
const client = postgres(connectionString, {
  max: 10,              // max pool connections; stay within Postgres max_connections
  idle_timeout: 20,     // seconds before an idle connection is closed and removed from the pool
  connect_timeout: 10,  // seconds to wait for a new connection before throwing
  max_lifetime: 1800,   // seconds; recycle connections to avoid stale state (30 min)
  // If using pgBouncer in transaction mode, disable prepared statements:
  prepare: false,       // required for pgBouncer transaction pooling mode
})

export const db = drizzle(client, { schema })
```

**Without pgBouncer (direct connection, small MVP):**

```ts
const client = postgres(connectionString, {
  max: 5,           // start conservative; scale up with EXPLAIN evidence
  idle_timeout: 30,
  connect_timeout: 10,
})
```

**Environment variable pattern:**

```
DATABASE_URL=postgresql://user:password@pgbouncer-host:5432/dbname?sslmode=require
```

Use the pgBouncer host in `DATABASE_URL`, not the direct Postgres host, when pgBouncer is in use. The app should not know or care which is in front — swap via the env var.

---

## Connection leak detection

A connection leak occurs when code acquires a connection from the pool (explicitly, or implicitly via a query) and never releases it — either because an exception path skips the release, or because the client is never returned to the pool after the query completes.

**Symptoms:**
- Pool exhaustion errors (`Error: Client checkout timeout exceeded`, `too many connections`)
- Postgres `pg_stat_activity` showing many connections in `idle in transaction` or `idle` state from a single app host
- Pool size at max with no actual DB load

**Detection levers in postgres.js:**

```ts
const client = postgres(connectionString, {
  max: 10,
  idle_timeout: 20,      // idle connections closed after 20s — surfaces leaks that hold connections open
  // postgres.js also emits 'connect' and 'end' events you can count in a metrics hook
  onnotice: (notice) => console.warn('[pg notice]', notice),
})
```

**Statement timeout** (set at the session level via Postgres) kills long-running queries that hold connections indefinitely:

```sql
-- In your Postgres config or via SET on connect:
SET statement_timeout = '30s';
```

Or pass it in the connection string:

```
postgresql://user:pass@host/db?options=-c%20statement_timeout%3D30000
```

**pgBouncer transaction-mode caveat:** the `?options=-c ...` startup-parameter trick above is not
passed through by pgBouncer in transaction pooling mode by default — the client's startup packet is
only applied to whichever backend connection it's first paired with, not to every connection it gets
multiplexed onto afterward. Behind a transaction-mode pooler, set `statement_timeout` per-transaction
with `SET LOCAL` instead, or configure it at the pool/role level in Postgres. See
[pgBouncer transaction mode gotchas](#pgbouncer-transaction-mode-gotchas) below for the full list of
what breaks in this mode and the `SET LOCAL` workaround.

**In Drizzle, always release transaction connections:**

```ts
// Drizzle's db.transaction() handles release automatically on commit or rollback.
// If you use the raw postgres.js client directly (outside Drizzle), always use:
const result = await client.begin(async (tx) => {
  // ...
}) // connection returned to pool here regardless of throw
```

Do not use `client.reserve()` (postgres.js dedicated connection API) unless you explicitly need a single connection across multiple statements — and always wrap it in try/finally to guarantee release.

---

## pgBouncer transaction mode gotchas

pgBouncer in **transaction pooling mode** is the most efficient configuration but breaks Postgres features that rely on per-session state:

| Feature | Works in transaction mode? | Workaround |
| --- | --- | --- |
| `LISTEN` / `NOTIFY` | No — `LISTEN` requires a persistent session connection | Connect directly to Postgres (not through pgBouncer) for the listener process |
| Named prepared statements | Historically no — prepared statements are session-scoped; connection may change between prepare and execute. pgBouncer >= 1.21 can support them via `max_prepared_statements` | Set `prepare: false` in postgres.js (see config above) unless you've confirmed the pgBouncer version/config in front of you supports prepared statements in transaction mode |
| `SET` session variables (`SET search_path`, `SET statement_timeout`) | No — the connection may be returned before the `SET` takes effect for another caller | Use `SET LOCAL` (transaction-scoped) instead, or configure the variable in the Postgres role default |
| Advisory locks (`pg_advisory_lock`) | No — advisory locks are session-scoped | Use a different distributed lock mechanism, or use pgBouncer session mode for the process that needs advisory locks |
| `TEMP TABLE` | No — temp tables are session-scoped | Use real tables with a `session_id` column and clean up explicitly, or use session mode |

**`prepare: false` is the safe default when using transaction pooling mode.** If you leave prepared statements enabled on older pgBouncer, it will return an error (`prepared statement "..." does not exist`) because the next query may land on a different Postgres backend. pgBouncer >= 1.21 added protocol-level support for prepared statements in transaction mode (via `max_prepared_statements`), so this is no longer an absolute incompatibility on current versions — but it requires that setting to be explicitly configured on the pgBouncer side, and most managed poolers don't expose it yet. Keep `prepare: false` as the default unless you've confirmed the pgBouncer version and configuration in front of you actually supports prepared statements in transaction mode.

If you need `LISTEN/NOTIFY` (e.g. for realtime subscriptions) while using pgBouncer, connect the subscriber directly to Postgres on a separate dedicated connection — outside the pgBouncer pool — and keep the pool for normal OLTP queries.

---

## Quick-reject checklist

| Pattern | Fix |
| --- | --- |
| No pool configured (`postgres(url)` with default `max: 10` but no `idle_timeout`) | Add `idle_timeout`, `connect_timeout`, and `max_lifetime` to prevent connection leaks |
| Pool `max` not set or set to unlimited | Always set an explicit `max`; start at 5–10 for MVPs, size up with evidence |
| `prepare: true` (default) with pgBouncer in transaction mode | Set `prepare: false`; prepared statements are incompatible with transaction pooling |
| `LISTEN/NOTIFY` routed through pgBouncer transaction pool | Connect the listener directly to Postgres on a separate, dedicated connection |
| `SET session_var` inside a query with pgBouncer transaction mode | Use `SET LOCAL` (transaction-scoped) or configure the default in the Postgres role |
| Pool exhaustion errors with no `idle_timeout` | Add `idle_timeout: 20` to allow the pool to release idle connections under pressure |
| Using Neon serverless driver in a long-lived Node.js server | Switch to `postgres.js` with a real pool; the serverless driver is for edge runtimes only |
| Direct Postgres connection URL used in production with many app instances | Put pgBouncer in front; many parallel app instances will exhaust `max_connections` |

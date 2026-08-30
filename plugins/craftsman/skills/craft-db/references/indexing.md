# Indexing

An index that isn't used by the query planner is pure cost: every INSERT, UPDATE, and DELETE pays the write-amplification penalty while reads receive nothing in return. The discipline is measurement-first — **prove with EXPLAIN ANALYZE that the planner chooses the index before you add it; treat every speculative index as a loan with compounding interest.** Composite key order, covering indexes, and partial indexes are refinements on top of that foundation — none of them matter if the base condition isn't met.

> **Scope split.** This file owns *how to add, verify, and maintain indexes* — the mechanics of EXPLAIN, key ordering, covering and partial index patterns, and index bloat. The query access patterns that *justify* each index (which columns a tenant-scoped, soft-delete-filtered query actually filters and sorts on) are documented in `access-patterns.md`. Column types and uniqueness constraints belong to `schema.md`. Slow-query signals — the p95/p99 latency alerts that surface the problem before you reach for EXPLAIN — will be wired in `craft-observability` → `slo-alerts.md`.

---

## Contents

- [The EXPLAIN workflow](#the-explain-workflow)
- [Composite key column order](#composite-key-column-order)
- [Covering indexes](#covering-indexes)
- [Partial indexes](#partial-indexes)
- [GIN indexes for JSONB](#gin-indexes-for-jsonb)
- [When NOT to index](#when-not-to-index)
- [Index bloat](#index-bloat)
- [Index naming](#index-naming)
- [Quick-reject checklist](#quick-reject-checklist)

---

## The EXPLAIN workflow

Never add an index based on intuition. Run EXPLAIN ANALYZE on the actual query against a dataset that resembles production in cardinality and distribution — a three-row dev table will produce a Sequential Scan even with a valid index, because the planner correctly decides a Seq Scan is cheaper.

**Step 1 — capture the plan before the index:**

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, status, created_at
FROM   orders
WHERE  tenant_id = $1
  AND  status    = 'pending'
ORDER  BY created_at DESC
LIMIT  20;
```

Read the output top-down. Key signals:

| Node | What to look for |
| --- | --- |
| `Seq Scan` on a large table | Candidate for an index — but check rows/width first |
| `Filter:` after a Seq Scan | The predicate couldn't use an index; this is the column to index |
| `Index Scan` / `Index Only Scan` | Planner chose an index; confirm it's the *right* one |
| `Rows Removed by Filter: N` | N large → the index selectivity is poor |
| `Bitmap Heap Scan + Recheck Cond` | Multi-range index scan; fine unless `Heap Blocks: lossy` is high |
| `actual time=X..Y` | Wall time for that node; compare before/after |

**Step 2 — create the index:**

```sql
CREATE INDEX CONCURRENTLY idx_orders_tenant_status_created
    ON orders (tenant_id, status, created_at DESC);
```

Without `CONCURRENTLY`, Postgres acquires a SHARE lock that blocks all writes (INSERT, UPDATE, DELETE) for the duration of the build while reads continue; `CONCURRENTLY` takes only ShareUpdateExclusiveLock, allowing all DML to proceed (Postgres-specific; MySQL/SQLite have different mechanisms — discover the dialect). It cannot run inside a transaction block. For the migration-step implications see `migrations.md`.

**Step 3 — re-run the same EXPLAIN ANALYZE and confirm:**

- The plan now shows `Index Scan` or `Index Only Scan` using the new index.
- `actual time` for the node has dropped meaningfully.
- If the planner *still* prefers a Seq Scan, the statistics may be stale (`ANALYZE orders;`) or the table is small enough that the planner is correct.

**If the planner doesn't use the index:** drop it. An unused index is never free — it still writes on every mutation. Use `pg_stat_user_indexes` (Postgres) to confirm usage over time after deployment:

```sql
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM   pg_stat_user_indexes
WHERE  relname = 'orders'
ORDER  BY idx_scan ASC;
```

An index with `idx_scan = 0` after a week in production is a candidate for removal. Note that `pg_stat_user_indexes` resets on server restart or manual `pg_stat_reset()` — verify the counters have been accumulating since at least the last restart (`pg_stat_bgwriter.stats_reset` can confirm this) before treating zero scans as evidence of disuse.

---

## Composite key column order

The order of columns in a composite index is the most consequential decision you'll make about it. The rule:

**Equality predicates first, then range predicates, then sort columns.**

Reason: a B-tree index is traversed by the leftmost prefix. A range predicate (`>`, `<=`, `>=`, `<`, `BETWEEN`) on a column exhausts index precision for all columns to the right — columns after a range can't be seeked, only scanned. If you put the range column first, the planner can't use the remaining columns as an equality filter. Exclusion predicates (`!=`, `NOT IN`, `NOT LIKE`) generally cannot use a B-tree index for selective access — the planner typically falls back to a seq scan or full index scan because such predicates return almost all rows.

```sql
-- Query: tenant_id = $1 AND created_at > $2 AND status = 'active'
-- WRONG order — after the range on created_at, status can't be seeked
CREATE INDEX idx_orders_wrong ON orders (tenant_id, created_at, status);

-- RIGHT order — both equality columns seeked first, then the range narrows the scan
CREATE INDEX idx_orders_right ON orders (tenant_id, status, created_at);
```

The sort column (used in `ORDER BY`) goes last when it matches the sort direction — this lets the planner avoid a sort step entirely (`Index Scan Backward` or forward). Per-column `ASC`/`DESC` and `NULLS FIRST`/`NULLS LAST` have been supported in index definitions since Postgres 8.3 — no version gate applies. (Postgres 13 introduced incremental sort as a separate plan node, which is a distinct feature.)

**Multi-tenant tables almost always lead with `tenant_id`.** It appears as an equality predicate in every query (universal coverage) and immediately eliminates all other tenants' rows — regardless of whether it is the highest-cardinality column in the table. High cardinality alone does not determine leading column order; universal equality predicate coverage does. An index that omits `tenant_id` in position 1 will usually scan more rows than necessary, even if the planner uses it.

---

## Covering indexes

An index that includes all the columns a query needs lets the planner satisfy the query entirely from the index without a heap fetch — this is an `Index Only Scan`, which eliminates random I/O to the table pages. Add non-key columns via `INCLUDE` (Postgres 11+) to cover them without affecting sort order:

```sql
-- The query SELECTs id, status, created_at and filters on tenant_id + status
-- Without INCLUDE, the planner heap-fetches to retrieve created_at
CREATE INDEX idx_orders_covering
    ON orders (tenant_id, status)
    INCLUDE (id, created_at);
```

`INCLUDE` columns don't participate in the key (they're not available for filtering or sorting), but they're stored in the leaf pages so the planner can skip the heap fetch. This is different from listing them as key columns — adding high-cardinality columns to the key increases the index size and write cost for no filter benefit.

When to reach for a covering index:

- The query is on a hot path with measurable latency (will be confirmable via `craft-observability` → `slo-alerts.md`).
- EXPLAIN shows a heap fetch (`Heap Fetches` > 0 on an Index Only Scan, or a separate Bitmap Heap Scan step).
- The SELECT list is small and stable — covering indexes are sensitive to schema changes; every new projected column may require an `INCLUDE` update.

Covering indexes increase index size and write cost. Run the EXPLAIN verification after adding one; confirm `Index Only Scan` and a material latency drop before keeping it.

---

## Partial indexes

A partial index covers only the rows that match a `WHERE` clause on the index itself. The result is a smaller index (fewer rows, less storage, faster writes) that is more selective — and therefore faster — when its condition matches the query predicate.

```sql
-- Only index orders that are pending — the hot path
-- Completed/cancelled orders (the vast majority) are excluded
CREATE INDEX idx_orders_pending
    ON orders (tenant_id, created_at)
    WHERE status = 'pending';
```

The planner will use this index only for queries whose predicate implies the index condition (i.e., a query filtering on `status = 'pending'` or a subset of it). For other statuses the planner falls back to a full index or Seq Scan.

Useful patterns:

| Use case | Partial condition |
| --- | --- |
| Soft-delete: index only live rows | `WHERE deleted_at IS NULL` |
| Active/pending rows in a status column | `WHERE status = 'active'` |
| Non-null optional column | `WHERE optional_col IS NOT NULL` |
| Feature-flagged tenant cohort | `WHERE tier = 'pro'` |

Check the query predicate literally: the planner will use a partial index only when the query's `WHERE` clause is *at least as restrictive* as the index condition. A query on `status IN ('pending', 'processing')` will not use the `WHERE status = 'pending'` index. Confirm with EXPLAIN.

Partial indexes are particularly effective in multi-tenant tables where a status flag partitions rows steeply (e.g., 2% pending, 98% completed) — the index covers the hot 2% and stays tiny.

---

## GIN indexes for JSONB

A standard B-tree index cannot efficiently index inside a JSONB column — it can only index the whole-column value. For queries that filter on keys or values inside a JSONB column, or for full-text search over JSONB, use a GIN (Generalized Inverted Index).

**When to use a GIN index on JSONB:**

- Filtering by key existence: `WHERE config ? 'theme'`
- Filtering by key-value pair: `WHERE config @> '{"theme": "dark"}'` (containment operator)
- Full-text search over a `tsvector` derived from a JSONB field
- Any query using JSONB operators (`@>`, `?`, `?|`, `?&`) on a large table

**When NOT to use GIN on JSONB:**

- Simple equality on a known key (`WHERE config->>'theme' = 'dark'`) — for this pattern, a functional B-tree index on the extracted value is often more selective and faster than a GIN: `CREATE INDEX idx_users_config_theme ON users ((config->>'theme'));`
- The JSONB column holds large, rarely-queried blobs where no predicate filters on internal keys
- Write throughput is the primary concern (see performance trade-offs below)

**Syntax:**

```sql
-- Full GIN index: covers all keys and values in the column
CREATE INDEX CONCURRENTLY idx_users_config_gin
    ON users USING GIN (config);

-- GIN with gin_path_ops operator class: smaller, faster for @> containment queries only
-- Does NOT support ? (key existence) or @? / @@ operators
CREATE INDEX CONCURRENTLY idx_users_config_gin_path
    ON users USING GIN (config jsonb_path_ops);
```

Choose `jsonb_path_ops` when all your queries use the containment operator (`@>`); it produces a smaller index. Use the default operator class when you also need `?`, `?|`, or `?&`.

**Performance trade-offs:**

- **Slower writes:** every INSERT or UPDATE that modifies the indexed JSONB column must update the GIN index. GIN indexes are significantly more expensive to maintain than B-tree indexes because they index every key-value pair in the document. On write-heavy tables this cost compounds.
- **Larger index size:** a GIN index over a JSONB column with many keys can be many times larger than a B-tree index on a single extracted value.
- **Read benefit:** for queries using `@>`, `?`, or `?|` on large tables, a GIN index can reduce a sequential scan over millions of rows to an index lookup in microseconds.

Always measure with EXPLAIN ANALYZE before and after adding a GIN index. A GIN index on a JSONB column that is queried rarely or in small result sets may not justify the write overhead.

**Cross-reference:** `schema.md` covers when to use JSONB vs. a normalized table. If the JSONB structure is stable and frequently queried on specific keys, consider whether those keys should be promoted to real columns — a B-tree index on a first-class column is cheaper than a GIN index on a JSONB blob.

---

## When NOT to index

Indexes have a cost that compounds over time. Resist the urge to index on addition; a later EXPLAIN session will tell you if you need it.

**Don't index:**

- **Low-cardinality columns in isolation.** A boolean or an enum with two active values (e.g., `is_active`: true/false) offers the planner almost nothing — it would still read a large fraction of the table. Combine with a high-cardinality column or use a partial index instead.
- **Columns on small tables.** Below roughly 1,000–10,000 rows (dialect and row-width dependent), the planner nearly always prefers a Seq Scan — the overhead of an index traversal exceeds a full scan. This threshold is statistics-driven; verify with EXPLAIN rather than assuming a table is "big enough."
- **Write-heavy tables where read latency is not the bottleneck.** An event log, an append-only audit table, or a job queue can accumulate many indexes that destroy write throughput without helping any reader. Each index on a table is updated on every INSERT and on every UPDATE that touches an indexed column.
- **Columns already covered by the leftmost prefix of another index.** If `(tenant_id, status, created_at)` exists, a separate index on `(tenant_id)` alone is redundant for all queries that the composite index already accelerates.
- **Speculative "future query" indexes.** Add indexes for access patterns that exist in the code today. Write `access-patterns.md` when you add the query; add the index when EXPLAIN shows you need it.

---

## Index bloat

B-tree indexes accumulate dead tuples from UPDATEs and DELETEs. Autovacuum reclaims dead index entries (marking their space reusable) but does not shrink the index file or compact pages — the physical file size stays the same until VACUUM FULL or REINDEX is run. Over time:

- Index scans slow down as the planner traverses more dead pages.
- Storage grows without a corresponding data increase.
- Write amplification increases as more pages must be maintained.

**Maintenance approaches (Postgres-specific; verify for your dialect):**

```sql
-- Light: reclaims dead tuples, does NOT rewrite pages, non-blocking for reads and DML,
-- but acquires ShareUpdateExclusiveLock (conflicts with DDL, VACUUM FULL, and CLUSTER)
VACUUM orders;

-- Full rewrite: reclaims storage, requires an exclusive lock — schedule in a maintenance window
VACUUM FULL orders;

-- Index-only rewrite: rewrites the index without touching the table (Postgres 12+)
REINDEX INDEX CONCURRENTLY idx_orders_tenant_status_created;
```

`pg_stat_user_indexes` and the `pgstattuple` extension give you dead-tuple ratios. A bloat ratio above ~30% on a frequently-written table is a signal to schedule maintenance. Autovacuum handles this automatically in most managed Postgres services (check your provider's documentation) — check autovacuum settings before scheduling manual VACUUM jobs that duplicate its work.

For very high-write tables, two separate `fillfactor` levers exist — they target different objects:

- **TABLE fillfactor** (`CREATE TABLE … WITH (fillfactor = 70)`) leaves free space in heap pages so an UPDATE can place the new row version on the same page. When it succeeds, Postgres chains the old and new row without creating a new index entry — this is the HOT (Heap Only Tuple) mechanism. Set it on the table, not the index.
- **INDEX fillfactor** (`CREATE INDEX … WITH (fillfactor = 70)`) leaves free space in B-tree leaf pages to absorb future key insertions without page splits. This is beneficial for workloads with random or sequential key growth (e.g., UUID primary keys, time-series). It has no relationship to HOT.

Both are Postgres-specific; confirm the workload profile before applying either.

---

## Index naming

Name every index explicitly using the same `{type}_{table}_{columns}` convention used for constraints:

```
idx_{table}_{columns}
```

Where `{columns}` reflects the key column order and enough specificity to be human-readable in logs and monitoring. Examples:

```sql
CREATE INDEX CONCURRENTLY idx_orders_tenant_status_created
    ON orders (tenant_id, status, created_at DESC);

CREATE INDEX CONCURRENTLY idx_orders_pending
    ON orders (tenant_id, created_at)
    WHERE status = 'pending';
```

An auto-generated or unnamed index yields `$1` or a system-assigned name in explain plans, slow-query logs, and bloat queries — an explicit name makes the index immediately identifiable. Verify the name in the generated migration before applying.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Index added with no EXPLAIN ANALYZE before/after | Run EXPLAIN ANALYZE; confirm `Index Scan` in the plan and a measurable latency drop |
| `idx_scan = 0` on an index in production for > 1 week | Drop the index; it's write-amplification with no return |
| Composite index with a range column before equality columns | Reorder: equality columns first, range last, then sort column |
| Composite index missing `tenant_id` in position 1 on a multi-tenant table | Move `tenant_id` to the leading position |
| `INCLUDE` columns listed as key columns (not in `INCLUDE` clause) | Move read-only projection columns to `INCLUDE` to avoid widening the key |
| Partial index condition does not match the query's `WHERE` clause | Confirm with EXPLAIN that the planner uses the index; adjust the condition or use a full index |
| Index on a boolean / two-value enum alone | Use a partial index (`WHERE flag = true`) or combine with a selective column |
| Index created without `CONCURRENTLY` on a live table | Use `CREATE INDEX CONCURRENTLY` (Postgres) to avoid blocking all writes for the index build duration (migration deployment notes: `migrations.md`) |
| Index bloat ratio > 30% on a write-heavy table | Schedule `REINDEX CONCURRENTLY` or tune autovacuum; check autovacuum logs first |
| Multiple overlapping indexes where one is a prefix subset of another | Drop the narrower index; the composite covers all its queries |
| Speculative index for a query that doesn't exist in the codebase | Remove it; revisit after the access pattern is written (`access-patterns.md`) |

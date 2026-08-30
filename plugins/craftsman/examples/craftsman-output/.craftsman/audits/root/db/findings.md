# Db Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-db · scope: root

## root-DB-001 · severity 🔴 · status open
**What breaks (plain language):** The database doesn't enforce who can see what — separation between
companies lives only in app code. A single missed filter exposes every tenant's data.
**Technical:** No row-level security on `invoices` / `customers`; isolation is application-enforced
only. `lib/db.ts:3`. (Same real defect surfaces in the security pass as `root-SEC-002`; this is the
canonical owner — db owns enabling RLS.)
**Fix:** Enable RLS and add an org-scoped policy per tenant table; keep app-level scoping too
(defense-in-depth). See craft-db → `integrity.md`.
**Fingerprint:** `scope=root · domain=db · class=no-row-level-security · resource=invoices table`
**Last-checked:** 2026-06-22 · a1bec8f

## root-DB-002 · severity 🟡 · status open
**What breaks (plain language):** An invoice can point at a customer that doesn't exist, and deleting a
customer leaves orphaned invoices. The data drifts into an inconsistent state that's painful to clean
up later.
**Technical:** `invoices.customer_id` has no foreign-key constraint; integrity is unchecked at the DB.
No `on delete` strategy. Inferred from raw schema use in `lib/db.ts` and absence of constraint DDL.
**Fix:** Add a FK with a deliberate `on delete` rule; let the database reject bad references. See
craft-db → `integrity.md` and `schema.md`.
**Fingerprint:** `scope=root · domain=db · class=missing-fk-constraint · resource=invoices.customer_id`
**Last-checked:** 2026-06-22 · a1bec8f

## root-DB-003 · severity 🟡 · status open
**What breaks (plain language):** The invoice list gets slower for every customer as their data grows,
and deep pages crawl — because the query re-counts and re-scans rows each time.
**Technical:** `OFFSET`-based pagination on the invoice list with no covering index on
`(org_id, created_at)`. `app/(dashboard)/invoices/page.tsx:22` → `lib/db.ts` query. Will degrade under
real row counts.
**Fix:** Switch to keyset (seek) pagination and add the composite index; verify with `EXPLAIN ANALYZE`.
See craft-db → `access-patterns.md` and `indexing.md`.
**Fingerprint:** `scope=root · domain=db · class=offset-pagination · resource=invoices list query`
**Last-checked:** 2026-06-22 · a1bec8f

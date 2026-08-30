# Db Audit Plan — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-db · scope: root

Scope for THIS surface (from discovery): Supabase Postgres, raw `postgres` client, no migrations dir
in-repo, RLS posture unconfirmed. Steps sourced from craft-db's `## Audit checklist`.

- [x] Map ORM/dialect/migration tool/tenant-scope helpers → SKILL.md operating principle
- [x] Schema modeling: types, NOT NULL, real FKs, money type → `references/schema.md`
- [x] Tenant-scoped reads go through one helper; no `SELECT *` / OFFSET / N+1 → `references/access-patterns.md`
- [x] DB-level integrity: constraints, FKs, on-delete, transactions, RLS → `references/integrity.md`
- [ ] Migrations reviewed, reversible, expand-contract → `references/migrations.md` (N-A — no migrations in repo; flagged as unknown)
- [x] Indexes back measured query patterns (EXPLAIN) → `references/indexing.md`
- [ ] Destructive/large-table changes staged (add nullable → backfill → constrain → drop), not one long-locking migration → `references/integrity.md` (N-A this run — no schema-change work in scope; revisit when adding the FK from DB-002)

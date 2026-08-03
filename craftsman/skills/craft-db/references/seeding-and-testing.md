# Seeding and Testing

Seed scripts and test database patterns follow distinct but related disciplines. Seeds must be idempotent, FK-aware, and free of production-like sensitive data. Test database patterns must be fast, isolated, and deterministic. Both share the principle: **no test or seed should leave the database in a state that affects other tests or seed runs.**

> **Scope split.** This file owns seed script patterns (idempotency, insertion ordering) and per-test database isolation patterns (transaction rollback with Drizzle + vitest). The actual schema design (column types, constraints) lives in `schema.md`; migration workflow lives in `migrations.md`; query helpers for testing live in `access-patterns.md`. The application-side test infrastructure (test server setup, auth mocking) is `craft-testing` → `backend-data-testing.md`.

> **Dialect note:** These docs assume PostgreSQL with the Drizzle ORM and vitest. Adjust driver-specific calls for MySQL or SQLite.

---

## Contents

- [Idempotent seed scripts](#idempotent-seed-scripts)
- [FK-aware insertion ordering](#fk-aware-insertion-ordering)
- [What NOT to put in seeds](#what-not-to-put-in-seeds)
- [Per-test transaction rollback with Drizzle + vitest](#per-test-transaction-rollback-with-drizzle--vitest)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Idempotent seed scripts

A seed script must be safe to run multiple times. Running it twice should produce the same final state — not duplicate rows, not errors, not a half-seeded database.

**Pattern: `INSERT ... ON CONFLICT DO NOTHING`**

```ts
// db/seeds/workspaces.ts
import { db } from '../client'
import { workspaces } from '../schema'

export async function seedWorkspaces() {
  await db
    .insert(workspaces)
    .values([
      {
        id: 'ws_seed_acme',
        name: 'Acme Corp',
        slug: 'acme',
        createdAt: new Date('2024-01-01T00:00:00Z'),
      },
      {
        id: 'ws_seed_globex',
        name: 'Globex',
        slug: 'globex',
        createdAt: new Date('2024-01-01T00:00:00Z'),
      },
    ])
    .onConflictDoNothing()
    // OR, to update specific fields on re-seed while preserving others:
    // .onConflictDoUpdate({
    //   target: workspaces.id,
    //   set: { name: sql`excluded.name` },
    // })
}
```

Use stable, human-readable seed IDs (e.g. `ws_seed_acme`, not `crypto.randomUUID()`). Random UUIDs change on every seed run, making `ON CONFLICT` useless — you'd insert a new row each time because the ID never matches.

**Seed entry point — run all seeds in FK order:**

```ts
// db/seeds/index.ts
import { seedWorkspaces } from './workspaces'
import { seedUsers } from './users'
import { seedInvoices } from './invoices'

async function seed() {
  console.log('Seeding database...')
  await seedWorkspaces()   // no FKs; runs first
  await seedUsers()        // FK → workspaces
  await seedInvoices()     // FK → workspaces, users
  console.log('Done.')
  process.exit(0)
}

seed().catch((err) => {
  console.error(err)
  process.exit(1)
})
```

---

## FK-aware insertion ordering

Foreign key constraints will reject an insert if the referenced row doesn't exist yet. Always seed parent tables before child tables.

**Dependency order (most to least foundational):**

1. Tables with no FK dependencies (e.g. `workspaces`, `plans`, lookup/reference tables)
2. Tables that FK to #1 (e.g. `users` → `workspaces`)
3. Tables that FK to #2 (e.g. `invoices` → `workspaces` + `users`)
4. Join/pivot tables last (e.g. `workspace_members` → `workspaces` + `users`)

If you have circular FK references (rare, but possible in self-referential tables), disable the FK constraint check for the seed transaction or use `NOT VALID` + deferred validation. This is the exception, not the rule — circular FK references are usually a schema design smell.

```sql
-- Emergency workaround for circular FK during seed only
BEGIN;
SET CONSTRAINTS ALL DEFERRED;
-- ... inserts ...
COMMIT;
```

In Drizzle, you can also use `db.transaction()` with deferred constraints if your FKs are declared `DEFERRABLE INITIALLY DEFERRED`.

---

## What NOT to put in seeds

Seeds are committed to the repository and run in CI. They must never contain:

| Category | Why not | Alternative |
| --- | --- | --- |
| Production-like PII (real emails, names, phone numbers) | Seeds appear in git history and CI logs; GDPR/CCPA exposure | Use obviously fake data: `alice@example.com`, `test-workspace-1` |
| Real UUIDs copied from production | They conflict with production data if a DB is accidentally pointed at prod | Use `ws_seed_*` prefixed string IDs or `00000000-0000-0000-0000-000000000001` format UUIDs |
| `crypto.randomUUID()` or `Math.random()` in IDs | Changes on every run; `ON CONFLICT DO NOTHING` never fires; seeds duplicate | Use hardcoded stable IDs |
| Production API keys or secrets | Seeds are committed | Use placeholder values: `sk_test_seed_placeholder` |
| Passwords in plaintext | Plaintext passwords in git | Use a hardcoded bcrypt hash of a well-known test password (e.g. `password123`) |

**Test password pattern:**

```ts
// Generate once, hardcode the hash — never call bcrypt in the seed loop
// bcrypt.hash('password123', 10) → run once and paste the result
const TEST_PASSWORD_HASH = '$2b$10$K7L1OJ45/4Y2nIvhRVpCe.FSmhDdWoXehVzJptJ/op0/AHqtyLMf2'

await db.insert(users).values({
  id: 'user_seed_alice',
  email: 'alice@example.com',
  passwordHash: TEST_PASSWORD_HASH,
  workspaceId: 'ws_seed_acme',
}).onConflictDoNothing()
```

---

## Per-test transaction rollback with Drizzle + vitest

The most reliable way to isolate DB state between tests is to wrap each test in a transaction and roll it back after the test completes. This avoids the need for `DELETE FROM` cleanup, works against a real (not mocked) database, and is fast because no data is actually committed to disk.

**Why use a real DB instead of mocks?** Mocking the DB layer means your tests don't catch constraint violations, query planner issues, or ORM-generated SQL bugs. A transaction-per-test pattern against a real test DB gives you correctness with isolation.

**Pattern: Drizzle + vitest transaction rollback**

```ts
// tests/helpers/db.ts
import postgres from 'postgres'
import { drizzle, PostgresJsDatabase } from 'drizzle-orm/postgres-js'
import * as schema from '../../db/schema'

// Use a dedicated test database — never point at dev or prod
const testClient = postgres(process.env.TEST_DATABASE_URL!, { max: 1 })
export const testDb = drizzle(testClient, { schema })
```

```ts
// tests/helpers/withTestTransaction.ts
import { testDb } from './db'
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js'
import * as schema from '../../db/schema'

type TestFn = (tx: PostgresJsDatabase<typeof schema>) => Promise<void>

/**
 * Wraps a test body in a transaction that is always rolled back.
 * The test receives the transaction client — all DB calls inside
 * the test must use `tx`, not the module-level `db` instance.
 */
export async function withTestTransaction(fn: TestFn): Promise<void> {
  await testDb.transaction(async (tx) => {
    await fn(tx)
    // Force rollback regardless of test outcome
    tx.rollback()
  }).catch((err) => {
    // Drizzle throws on explicit rollback(); swallow that specific error
    if (err.message !== 'Rollback') throw err
  })
}
```

```ts
// tests/invoices.test.ts
import { describe, it, expect } from 'vitest'
import { withTestTransaction } from './helpers/withTestTransaction'
import { createInvoice } from '../src/services/invoices'
import { invoices } from '../db/schema'
import { eq } from 'drizzle-orm'

describe('createInvoice', () => {
  it('inserts an invoice with the correct tenant', async () => {
    await withTestTransaction(async (tx) => {
      const result = await createInvoice(tx, {
        tenantId: 'ws_seed_acme',
        amount: 10000, // cents
        status: 'pending',
      })

      // Assert within the same transaction — row is visible here but not outside
      const [row] = await tx
        .select({ id: invoices.id, status: invoices.status })
        .from(invoices)
        .where(eq(invoices.id, result.id))

      expect(row.status).toBe('pending')
      // Transaction rolls back here — no cleanup needed
    })
  })

  it('does not see rows from a different test', async () => {
    await withTestTransaction(async (tx) => {
      // This test starts clean — prior test's data was rolled back
      const rows = await tx.select().from(invoices)
      expect(rows.length).toBe(0) // only seed data, if any
    })
  })
})
```

**Key constraints of this pattern:**

- All DB calls inside the test must use `tx` (the transaction client), not the module-level `db`. A query using `db` opens a separate connection outside the transaction and will not be rolled back.
- Your service functions must accept a `db` parameter (dependency injection) rather than importing the module-level client directly. This is also better design — it makes services composable within transactions.
- Use a dedicated `TEST_DATABASE_URL` pointing at a separate test database. The rollback pattern prevents permanent writes, but pointing tests at a dev or prod database is still unsafe (migrations run, seed data can be visible to others).
- Run migrations against the test DB before the test suite: `drizzle-kit migrate --config=drizzle.test.config.ts` or a vitest `globalSetup` hook.

**vitest globalSetup for test DB migration (optional but recommended):**

```ts
// tests/globalSetup.ts
import { execSync } from 'child_process'

export async function setup() {
  // Ensure the test DB schema is current before any test runs
  execSync('pnpm drizzle-kit migrate', {
    env: { ...process.env, DATABASE_URL: process.env.TEST_DATABASE_URL },
    stdio: 'inherit',
  })
}
```

---

## Quick-reject checklist

| Pattern | Fix |
| --- | --- |
| Seed uses `crypto.randomUUID()` for IDs | Use stable hardcoded IDs (e.g. `ws_seed_acme`); idempotency requires stable keys |
| Seed inserts without `ON CONFLICT DO NOTHING` | Add `.onConflictDoNothing()` or the SQL equivalent; running twice must be safe |
| Seed inserts child table before parent table | Reorder to respect FK dependency chain; parent first, child after |
| Seed contains real email addresses or names | Replace with `@example.com` addresses and obviously fictional names |
| Test calls module-level `db` instead of the transaction `tx` | Pass `tx` as a parameter; queries on `db` escape the transaction and are not rolled back |
| Tests use `DELETE FROM` for cleanup instead of transaction rollback | Switch to `withTestTransaction`; rollback is faster and more reliable than manual cleanup |
| Test DB URL points at dev or production | Set `TEST_DATABASE_URL` to a dedicated test instance; guard with an env check in globalSetup |
| Service functions import `db` directly (not injectable) | Refactor to accept a `db` parameter; enables transaction rollback in tests and composability in application code |

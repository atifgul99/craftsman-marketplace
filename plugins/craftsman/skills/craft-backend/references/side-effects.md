# Side Effects

A mutation that partially succeeds is often worse than one that fully fails. **Sequence side effects
so the DB commit is the point of no return: everything that depends on data being persisted — queued
jobs, outbound webhooks, emails — runs after the commit, not inside the transaction or before it.**
When that ordering is wrong, you get queued jobs that race the write, external calls that fire on
data that rolls back, and duplicate-delivery bugs that are nearly impossible to reproduce. Idempotent
endpoints and a disciplined job-enqueueing order are the two habits that prevent most of these
failures.

> **Scope split.** This file owns the *application-layer ordering* of mutations: transaction
> boundaries, enqueue-after-commit, idempotency keys, outbox pattern, and retry/duplicate-request
> safety at the HTTP and job level. The *transaction mechanics and FK/constraint guarantees* that
> back these patterns live in **`craft-db`** → `integrity.md` — read it when the question is about
> isolation levels, deadlock avoidance, or schema constraints. Failure signals from jobs and external
> calls (structured errors, retries, alerts) are wired up in **`craft-observability`** →
> `logging.md` and `slo-alerts.md`. Timeout and retry policies for outbound calls at the
> infrastructure layer are in **`craft-infra`** → `scale-resilience.md`.
>
> **See also:** `error-contract.md` (how to surface failures to callers), `api-design.md`
> (endpoint shape; idempotency in the route contract).

---

## Contents

- [Transaction ordering](#transaction-ordering)
- [Enqueue jobs after commit, not before](#enqueue-jobs-after-commit-not-before)
- [The outbox pattern](#the-outbox-pattern)
- [Idempotency keys](#idempotency-keys)
- [External call failure handling](#external-call-failure-handling)
- [Retry and duplicate-request safety](#retry-and-duplicate-request-safety)
- [Recurring jobs / scheduled work](#recurring-jobs--scheduled-work)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Transaction ordering

Every mutation that must be atomic belongs in a single transaction. The rule for what to include:
**a set of DB writes succeeds or fails together; anything that can't be rolled back (a queue
message, an HTTP call, an email) must not be inside the transaction boundary**.

```ts
// Example pattern — adapt to your ORM/client (Drizzle, Prisma, Kysely, pg, etc.)
const order = await db.transaction(async (tx) => {
  const order = await tx.orders.create({ ... })
  await tx.auditLog.create({ orderId: order.id, event: 'created' })
  // NO queue.enqueue() here — if the transaction rolls back, the enqueue already fired
  return order
})
// enqueue AFTER the transaction succeeds
await queue.enqueue('send-confirmation', { orderId: order.id })
```

Operations within the transaction that *must* run in a specific order (e.g. insert parent before
child, acquire an advisory lock before updating a counter) need to be sequenced explicitly — the
DB doesn't infer intent from proximity. Name the ordering in a comment when it isn't obvious from
the code structure.

When two concurrent transactions touch the same rows, you're exposed to deadlocks unless you
acquire locks in a consistent order. Use advisory locks or `SELECT … FOR UPDATE` with a fixed row
ordering; **`craft-db`** → `integrity.md` covers the mechanics.

---

## Enqueue jobs after commit, not before

This is the single most commonly violated rule in background-job wiring. Enqueueing inside or
before the DB transaction means the job can run *before the data it depends on is visible*, or the
transaction can roll back *after the job has already been dispatched*.

```ts
// WRONG — job fires even if the transaction rolls back
await db.transaction(async (tx) => {
  const user = await tx.users.create({ ... })
  await queue.enqueue('send-welcome', { userId: user.id }) // BUG
})

// RIGHT — enqueue only after the commit is durable
const user = await db.transaction(async (tx) => {
  return tx.users.create({ ... })
})
await queue.enqueue('send-welcome', { userId: user.id })
```

The failure mode of getting this wrong: the job worker queries the DB for `userId`, gets a
not-found (the write hasn't committed yet or rolled back), and either silently drops the work or
dead-letters a perfectly legitimate job. This is especially subtle with ORMs that pool connections
or batch flushes — the commit may not be durable at the point the awaited call resolves. If your
app reads from a replica, replication lag means the write is not yet visible there. These are the
windows in which the enqueued job can observe a missing row — not an isolation-level property of
READ COMMITTED itself.

If your queue client offers a "transactional enqueue" or "outbox" adapter that participates in the
same DB transaction, use it (see the Outbox Pattern below). Otherwise, enqueue in plain sequential
code *after* the transaction promise resolves without throwing — not in a `finally` block, which
runs on both success and failure.

---

## The outbox pattern

The gap between "DB committed" and "message enqueued" is a crash window. If the process dies after
the commit but before the enqueue, the job is lost — no error, no retry, just silence.

The outbox pattern closes this gap by writing the job payload *into the same transaction* as the
business data, then dispatching from a reliable relay process:

```
┌──────────────────────────────────────┐
│ DB transaction                       │
│  INSERT INTO orders ...              │
│  INSERT INTO outbox_events           │
│    (type, payload, status='pending') │
│    VALUES ('send-confirmation', ...) │
└──────────────────────────────────────┘
        ↓ committed atomically
┌──────────────────────────────────────┐
│ Relay worker (cron / trigger / poll) │
│  SELECT * FROM outbox_events         │
│    WHERE status = 'pending'          │
│  → enqueue to real queue             │
│  → UPDATE status = 'sent'           │
└──────────────────────────────────────┘
```

This gives you exactly-once *write* (the event is committed atomically with the business data,
preventing loss) and at-least-once *dispatch* to the queue (if the relay crashes between the
enqueue and the status update, it restarts and re-enqueues). The worker consuming the queue still
needs to be idempotent, because dispatch and queue delivery are both at-least-once.

The outbox adds operational complexity — you need the relay process and the outbox table. It's the
right choice when: (a) the business operation and the downstream effect must not diverge, (b) the
queue client has no transactional enqueue, or (c) the job failure mode is "silent data loss" rather
than "user sees an error." For lower-stakes jobs (caches to warm, analytics events) the simpler
post-commit enqueue is fine.

---

## Idempotency keys

A mutating endpoint that can be called more than once must be safe to call more than once. Networks
retry, clients double-submit, CDNs replay, users click twice. If the action is not naturally
idempotent (e.g. `PUT` that replaces a resource by id) it must be made idempotent by the caller
supplying an idempotency key and the server recording the result.

**The contract:**

1. The caller generates a stable, unique key for the *intent* — once, when the user first opens the
   form or constructs the request — and persists it client-side (e.g. in session storage or form
   state) so every retry of that specific submission reuses the *same* key. A UUID v4 generated
   fresh on each submission gives each attempt a different key, defeating idempotency. The key
   travels in a request header (commonly `Idempotency-Key`) or in the body.
2. On receipt, the server checks a key store (a DB table, a cache with a TTL long enough to cover
   realistic retry windows — 24 hours is a common default).
3. If the key is new: execute the operation, persist the result alongside the key.
4. If the key is already recorded: return the stored result immediately, without re-executing.

```ts
// adapt to your ORM/client (Drizzle, Prisma, Kysely, pg, etc.)
async function createCharge(idempotencyKey: string, amount: number) {
  // Step 1: Reserve the key FIRST with a pending row. The DB unique constraint on `key` is the
  // race guard — two concurrent requests will race to insert, and only one wins.
  // Do NOT do a findUnique pre-check (TOCTOU race), and do NOT call the provider before inserting —
  // both concurrent requests could charge before either one loses the unique insert.
  let record: IdempotencyRecord
  try {
    record = await db.idempotencyRecords.create({
      data: {
        key: idempotencyKey,
        status: 'pending',
        expiresAt: addHours(new Date(), 24),
      },
    })
  } catch (err) {
    // isUniqueConstraintViolationOnKey: check the constraint name to distinguish this column
    // from other unique constraints. ORM-specific:
    //   Drizzle + pg driver: err.code === '23505' && err.constraint === 'idempotency_records_key_key'
    //   Prisma: err instanceof PrismaClientKnownRequestError && err.code === 'P2002' && err.meta?.target === 'key'
    if (isUniqueConstraintViolationOnKey(err)) {
      // A concurrent request already reserved or completed this key.
      // Poll/wait briefly for it to finish, then return the stored result.
      const existing = await db.idempotencyRecords.findUnique({ where: { key: idempotencyKey } })
      if (existing?.status === 'complete') return JSON.parse(existing.responseBody)
      // Still pending (the other request is mid-flight) — surface a 409 so the caller retries.
      throw new ConflictError('Concurrent request in progress for this idempotency key')
    }
    throw err  // re-throw unrelated errors (FK violation, NOT NULL, etc.)
  }

  // Step 2: Execute the provider call, passing the idempotency key where supported so the
  // provider can deduplicate on its side (e.g. Stripe accepts an Idempotency-Key header).
  try {
    const charge = await billingProvider.charge(amount, { idempotencyKey })

    // Step 3: Persist the final response and mark complete.
    await db.idempotencyRecords.update({
      where: { key: idempotencyKey },
      data: { status: 'complete', responseBody: JSON.stringify(charge) },
    })
    return charge
  } catch (providerErr) {
    // Mark the record failed so a future request with the same key can be retried.
    await db.idempotencyRecords.update({
      where: { key: idempotencyKey },
      data: { status: 'failed' },
    })
    throw providerErr
  }
}
```

Key safety rules:
- **For DB-only mutations, store the key and the response in the same transaction as the mutation**
  so you never record a key without the associated data being committed, and never commit data
  without the key being stored. **For flows with an external call** (e.g. `createCharge` above), use
  the reserve → call → finalize sequence shown above instead — never wrap the external call in a DB
  transaction; hold the transaction open only for the reserve step and the finalize step.
- **Never re-execute on a key collision** — even if the payload differs. The key represents an
  intent, not a payload hash. A mismatched payload should return `422` or `409`, not re-run.
- **Scope keys to the entity or operation** — a key generated for a charge must not accidentally
  replay as a refund. Include the operation type or endpoint in the key namespace if keys are
  caller-generated UUIDs.
- **TTL idempotency records.** A 24-hour window covers realistic client retry behavior; purge
  expired records on a schedule so the table doesn't grow unbounded.

---

## External call failure handling

Any call to a third-party service — payment processor, email provider, SMS gateway, storage bucket
— is a failure that *will* happen. The question is not if but when, and whether your code fails
open or closed.

**Default stance: fail closed, surface the error, do not silently continue.**

```ts
// WRONG — external failure is swallowed; the record looks "completed"
try {
  await stripe.charges.create(...)
} catch {
  console.log('stripe failed')   // no-op; caller gets a 200
}
await db.orders.update({ status: 'complete' })

// RIGHT — propagate the failure; let the caller retry or surface to the user
const charge = await stripe.charges.create(...)   // let it throw
await db.orders.update({ status: 'complete', chargeId: charge.id })
```

Practical rules:

- **Do not mark the operation successful in the DB before the external call returns.** Record the
  external result (a charge id, a delivery id) so you know the call completed.
- **Capture the external id on success.** You need it to reconcile, refund, or diagnose. A DB row
  with no `chargeId` / `messageId` is an operation you can't audit.
- **Budget for partial failure.** If the DB write is still inside an open transaction when the
  external call fails, the transaction can be rolled back and no partial state is persisted. If the
  DB write has already committed when the external call fails, you have committed pending state that
  requires explicit reconciliation — it cannot be rolled back. Decide upfront which applies to your
  flow, and for the committed-state case choose how to recover: (a) retry the external call from the
  stored pending row, (b) queue the external call as a background job, or (c) surface the failure to
  the caller and let them retry. Document the choice — "if Stripe fails after the DB write commits,
  we queue a retry job" — so future maintainers don't invent a fourth path.
- **Set timeouts on all outbound calls.** A third-party hanging forever holds a connection and a
  request slot. Wire explicit timeouts on your HTTP client; see **`craft-infra`** → `scale-resilience.md`
  for retry/backoff policies.
- **Log the external id, status code, and request correlation on every call** — success and failure.
  See **`craft-observability`** → `logging.md`.

**Email and notification providers: handle bounce and complaint webhooks.** SES, Postmark, Resend,
SendGrid, and every other ESP fire a webhook when a recipient hard-bounces (address doesn't exist)
or marks your message as spam. Wire that webhook and stop sending to that address. Sender reputation
is a shared resource across your entire sending domain — it isn't scoped to the one address you kept
emailing. Keep blasting a dead or complaining address and the ESP or a receiving mail server (Gmail,
Outlook) will flag the domain, and once that happens *all* your mail starts landing in spam or gets
rejected outright — including transactional email that actually matters, like password resets. The
DNS/SPF/DKIM/DMARC half of email deliverability is covered in **`craft-infra`** → `config.md`.

---

## Retry and duplicate-request safety

Most mainstream queues deliver at-least-once, but the details matter. BullMQ provides at-least-once
delivery only when stalled-job recovery is enabled — configure `stalledInterval` and ensure the
lock duration exceeds your job's maximum runtime; with a hard worker crash and default settings,
jobs can be lost (at-most-once). AWS SQS and Inngest are at-least-once by design. Temporal's
workflow state is exactly-once via event sourcing, though individual activities are retried
at-least-once. In all cases: your job handler will be called more than once for the same payload —
on retries, on worker restarts, on queue redelivery after a crash. This is not a bug in the queue;
it's the guarantee traded for durability. Your handler must be safe to run twice with the same
input.

**Strategies, in order of preference:**

1. **Natural idempotency.** The operation's outcome is the same regardless of how many times it
   runs. Setting a field to a fixed value, creating-or-updating by a stable unique key. Prefer this
   — it requires no extra bookkeeping.

   ```ts
   // adapt to your ORM/client (Drizzle, Prisma, Kysely, pg, etc.)
   // Idempotent: running twice doesn't double the discount
   await db.users.upsert({
     where: { id: userId },
     update: { plan: 'pro', upgradedAt: upgradedAt },
     create: { id: userId, plan: 'pro', upgradedAt: upgradedAt },
   })
   ```

2. **Check-then-act with a unique constraint.** Insert a record with a unique key; let the DB
   reject duplicates; catch the constraint violation and treat it as a success. Catch only the
   specific unique-constraint violation on the idempotency key column (check the constraint name or
   error code); re-throw other constraint violations (FK violation, NOT NULL on another column,
   etc.) — blindly treating all constraint errors as success masks real bugs. The constraint is the
   idempotency guarantee — see **`craft-db`** → `integrity.md`.

3. **Status guard.** Read current state first; skip the operation if it's already been applied.
   Reliable only if the status field is written in the same transaction as the side effect — not
   as an afterthought.

   ```ts
   const order = await db.orders.findUnique({ where: { id: orderId } })
   if (order.status === 'fulfilled') return  // already done; safe to ack the job
   // ... fulfil and set status in one transaction
   ```

4. **Idempotency key on the external call.** Payment processors, email providers, and many APIs
   accept a caller-supplied idempotency key. Pass it on every retry — the provider deduplicates for
   you. Without this, a retry after a timeout (where the original call may have succeeded) causes a
   double charge, a double send, or a double enroll.

**Job failure is an observable event.** Wire dead-letter queues (DLQ) or failure handlers that
emit structured logs and fire an alert when a job exhausts retries — see **`craft-observability`**
→ `slo-alerts.md`. A job that silently fails and disappears is worse than a job that noisily fails
and stays in the queue.

---

## Recurring jobs / scheduled work

Recurring jobs (cron-style work that runs on a schedule) have their own failure modes separate from one-off enqueued jobs. Get these right before the first production deployment.

**Define the schedule in code, not DB rows.** A schedule stored as a DB row is invisible to code review, can be silently deleted or mutated by a query, and creates a bootstrap problem on fresh deploys. Define the schedule as part of the job registration in the framework config — it is then version-controlled and auditable alongside the rest of the application.

**At-most-once-per-window guarantee.** When multiple instances of a service run concurrently (horizontal scaling, rolling deployments), all instances can see that the schedule window has opened. Without a guard, the job runs N times — once per instance. Prevent this with one of:
- **Advisory lock:** acquire a distributed lock (Postgres advisory lock, Redis `SET NX PX`, etc.) at the start of the job; the first instance to acquire it runs; all others skip.
- **Job deduplication key:** most queue frameworks accept a job id or dedup key that prevents the same job from being enqueued more than once within a window.

**Framework examples:**

```typescript
// BullMQ — repeat option defines the schedule in code; dedup is handled by the queue
// (each repeated job gets a stable id; the queue won't create a duplicate if one is already scheduled)
import { Queue } from "bullmq";

const queue = new Queue("reports");
await queue.add(
  "generate-weekly-report",
  { period: "weekly" },
  {
    repeat: { pattern: "0 6 * * MON" },  // cron expression; define once on startup
    jobId: "weekly-report",              // stable id prevents duplicates across restarts
  }
);

// BullMQ workers that may stall: configure stalledInterval and lock duration so jobs
// are recoverable after a worker crash. See the Retry and duplicate-request safety section.
```

```typescript
// Inngest — schedule trigger defined in code; Inngest handles dedup per account
import { inngest } from "./inngest";

export const generateWeeklyReport = inngest.createFunction(
  { id: "generate-weekly-report" },
  { cron: "0 6 * * MON" },   // schedule defined in the function, not a DB row
  async ({ event, step }) => {
    await step.run("build-report", async () => { /* ... */ });
  }
);
// Inngest guarantees at-most-once per cron window per function id.
```

```typescript
// Temporal — cron workflow; schedule is part of the workflow definition
import { Client } from "@temporalio/client";

const client = new Client();
await client.workflow.start(generateWeeklyReport, {
  taskQueue: "reports",
  workflowId: "weekly-report",           // stable id; Temporal deduplicates by workflowId
  cronSchedule: "0 6 * * MON",           // schedule in code
});
// Temporal's workflow state machine ensures exactly-once execution per cron window.
// Individual activities inside the workflow are retried at-least-once.
```

**Cross-reference:** For deployment concerns — ensuring the scheduler starts correctly across instances, managing cron jobs in containerized or serverless environments, and keeping scheduled work from running during rolling restarts — see **`craft-infra`**.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| `queue.enqueue()` called inside a DB transaction | Move enqueue to after the resolved transaction promise |
| `queue.enqueue()` called before the DB write | Reverse the order; commit first, enqueue after |
| External call (email, webhook, charge) inside a transaction | Extract it to post-commit; use the outbox if atomicity is required |
| Mutating endpoint with no idempotency key or dedup check | Add `Idempotency-Key` header handling with a key store + TTL |
| Idempotency key stored in a different transaction than the mutation | Persist key and result in the same transaction as the write |
| External call result (charge id, message id) not recorded | Capture the external id in the DB row on success |
| External call in a `try/catch` that swallows the error and continues | Propagate; fail the request or queue a retry — don't silently proceed |
| No timeout on an outbound HTTP call | Set explicit timeouts on the HTTP client; see `craft-infra` → `scale-resilience.md` for backoff policies |
| Job handler that double-charges, double-sends, or double-enrolls on retry | Make the handler idempotent (natural idempotency, unique constraint, or status guard) |
| Job failure that disappears silently (no DLQ, no alert) | Wire a DLQ or failure hook; emit structured log + alert (`craft-observability` → `slo-alerts.md`) |
| DB write marked "complete" before the external call returns | Write the result (incl. external id) atomically with the status update |
| No handler for the ESP's bounce/complaint webhook | Wire the webhook; suppress future sends to hard-bounced or complained addresses |
| Outbox relay dispatching without marking the row sent after enqueue | The outbox event is written atomically with the business data in the same DB transaction; relay dispatch is at-least-once. Mark the row `sent` after a successful enqueue — if the relay crashes between enqueue and the status update, it restarts and re-enqueues. Consumers must be idempotent to handle the resulting at-least-once delivery |

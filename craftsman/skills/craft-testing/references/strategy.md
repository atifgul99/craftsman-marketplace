# Testing Strategy

A test suite is a budget, not a checklist. The job is not "tests exist" — it is that the few flows where a bug costs a breach, lost data, or lost money are covered by tests that would actually catch the bug, and that everything else stays cheap enough to keep green. **Spend the testing budget where failure is expensive, prove the critical path with integration tests, and refuse coverage that only inflates a number.** An MVP with three real integration tests on the auth/payment path is in far better shape than one with two hundred AI-generated unit tests that assert mocks returned what the test told them to return.

> **Scope split.** This file owns *what to test and how much* — risk-weighting the budget, the test-shape decision (trophy vs. pyramid), the two persona tiers, what to leave untested, coverage as a signal, and the merge-gate policy. How to write a single good test (arrange/act/assert, naming, one behavior per test, avoiding mock theater) belongs to `test-design.md`. Flaky-test mechanics — root-causing time/order/network nondeterminism, retries, quarantine implementation — belong to `flake.md`. Testing Library / component-render specifics belong to `frontend-testing.md`. Testcontainers, transactional fixtures, and real-Postgres setup belong to `backend-data-testing.md`. The **CI pipeline itself** — runners, caching, shard parallelism, deploy gating mechanism — is ceded entirely to **`craft-infra`** → `ci-cd.md`; this file decides *which suites block a merge*, that file decides *how the jobs run*.

---

## What's worth testing

Default model behavior is to test what is easy to test: pure functions, formatters, a util that adds two numbers. That is backwards. Easy-to-test code is usually low-risk code. Rank by blast radius, not by convenience.

**Tier the codebase by what a bug costs:**

- **Tier A — a bug here is a breach, data loss, or money.** Authentication (can the wrong person log in?), authorization (can user A read/write user B's data? — the multi-tenant isolation boundary), payments and billing (double-charge, wrong amount, free access), and any data **mutation** that is hard to reverse (deletes, irreversible state transitions, financial ledger writes). This is where the budget goes first, and where the tests must exercise the *real* logic — real DB, real auth check — not a mock that rubber-stamps the happy answer.
- **Tier B — a bug here is a visible, recoverable defect.** Core business workflows that aren't money or auth: creating the main entity, the primary list/filter view, the onboarding flow. Worth integration coverage, but a bug is embarrassing, not catastrophic.
- **Tier C — a bug here is cosmetic or self-correcting.** Formatting, display-only derived values, internal tooling. Cheap unit tests if at all; never the priority.

The concrete heuristic when triaging an untested repo: **list every route/handler that writes to the database or checks identity, and start there.** A Zod schema that validates a request body is worth a test only when rejecting bad input is a security boundary (e.g. it gates a privileged mutation) — not because "validation should be tested" in the abstract. An authorization check on `DELETE /api/orgs/:id/members/:userId` is worth three tests (owner can, member cannot, cross-org cannot) before a single date-formatter test is written.

---

## Test shape: trophy vs. pyramid

Two competing shapes, and the right one depends on where your bugs actually live.

**The classic pyramid** — many unit, fewer integration, few e2e — is right when most of your risk is in *complex pure logic*: a pricing engine, a permissions resolver, a scheduling algorithm, a state machine. Units are fast and precise, and when the hard part is the computation, unit tests pin it down cheaply.

**The testing trophy** — a few static checks + unit, a *fat* integration layer, a thin e2e cap — is right for the persona's actual stack. A Next/React/Drizzle/Postgres app's bugs almost never live in an isolated pure function; they live in the **seams**: the route handler that wires auth → validation → DB query → response, the query that's subtly wrong against the real schema, the server action that doesn't re-check authorization. Unit-testing those pieces in isolation (with the DB mocked) tests the wiring you wrote in the test, not the wiring that ships. Integration tests — real handler, real DB, real query — catch the bug class that dominates this stack.

For a vibe-coded TypeScript app, **default to the trophy.** Heavy mocking to make a "unit" test of a handler is usually the smell that an integration test was the right tool.

The static layer is free confidence and belongs in the shape: TypeScript (`tsc --noEmit`), ESLint, and Zod parsing at runtime boundaries eliminate whole bug classes (typos, undefined access, malformed input) that you should never spend a test on. Treat them as the trophy's base, not as separate from the strategy.

---

## The two persona tiers

Do not prescribe Tier 2 to a Tier 1 codebase. Pushing comprehensive coverage, contract tests, and mutation testing onto someone who has zero tests and one paying customer is how the whole effort gets abandoned. Match the tier to where they are.

**Tier 1 — MVP hardening (the default for this persona).** The goal is to stop the catastrophic regression, not to reach a coverage number. Concretely:

- A handful (think 5–15, not 200) of **integration tests on the Tier A critical path**: signup/login actually authenticates; a logged-in user cannot read another tenant's data; a payment charges the right amount once; the core create/delete mutation persists and is scoped to the owner.
- **Smoke-test the happy path** of each money/auth flow end-to-end (one Playwright spec that logs in, does the one thing that makes money, asserts the result). One real browser pass per critical flow catches the "entire checkout is broken" class.
- A test **harness that runs fast and green locally and in CI**, so the next test is cheap to add. If adding a test is painful, none get added.
- When an audit credits a Tier A invariant as covered, obtain one bounded local fault-injection probe for that invariant: temporarily relax its existing guard, observe the directly relevant behavioral test fail, restore it, and rerun green. This verifies that the test discriminates; it is not an exhaustive mutation-testing programme.

That's it for Tier 1. Resist the urge to backfill unit tests across the whole repo — that spends the budget on Tier C.

**Tier 2 — scaling (only once Tier 1 holds and the team/traffic grows).** Now breadth pays off:

- Comprehensive coverage of Tier A and B, including failure paths and edge cases (expired token, declined card, concurrent mutation, partial failure/rollback).
- **Contract tests** between services or against external APIs (provider/consumer), so an upstream change breaks a test instead of production.
- **Load / performance tests** on the paths with SLOs — sustained throughput, p99 latency, connection-pool behavior under concurrency.
- **Mutation testing** (e.g. Stryker) on the Tier A suites to verify the tests actually *detect* injected bugs — the antidote to coverage theater. Run it on the critical modules, not the whole repo.

The progression is sequential: a Tier 2 technique applied to a Tier 1 codebase is premature. Confirm the critical path is covered before broadening.

---

## Unit vs. integration vs. e2e

Each level buys a different thing. Pick by what failure you're trying to catch, then spend accordingly — they get slower and more valuable, in that order, as you go down.

| Level | Good at | Bad at | Cost | How many |
| --- | --- | --- | --- | --- |
| **Unit** | Pinning complex pure logic; fast feedback on every save; exhaustive edge cases of one function | Catching wiring/integration bugs; anything that needs the real DB, real auth, real framework lifecycle | ~ms; trivial to run | Many — *but only where there's real logic to pin*, not one per file |
| **Integration** | The seams: handler + DB + auth + query against a real schema; the bug class that dominates this stack | Full cross-page user journeys; real browser/client behavior; third-party redirect flows | ~100ms–seconds (real DB) | The bulk of the suite for this persona |
| **E2E** | "Is the whole flow actually wired and shipping?"; cross-system journeys; the smoke test that catches a fully-broken deploy | Pinpointing *which* layer broke; exhaustive cases (too slow, too flaky for breadth) | ~seconds–minutes; flakiest | Few — happy paths of the critical flows only |

The cost/confidence tradeoff is the whole game: e2e gives the highest confidence the system actually works but is the slowest and most flake-prone, so you buy a *little* of it for the highest-value flows. Integration is the sweet spot for a TS/Postgres app — high confidence per test at acceptable speed. Unit is cheapest but only confident about the slice it covers, so it's wasted on glue code. A suite that's all unit tests on glue, with no integration, has high coverage and low confidence — the worst trade.

Rule of thumb for this stack: if a test needs more than one or two mocks to stand up, you probably wanted an integration test against the real dependency.

---

## What NOT to test

Negative space is where most of the wasted budget goes. Every test here is pure cost — maintenance, flake surface, and slower CI — with near-zero bug-catching value. Reject them.

- **Framework internals.** Don't test that Next's router routes, that React re-renders on state change, that Drizzle's `eq()` builds the right SQL. The framework's own suite covers it; your test just breaks on upgrades.
- **Types.** The compiler already proves them. A test asserting a function "returns a string" is a worse, slower version of the type annotation. Don't write runtime tests for what `tsc` checks at build.
- **Trivial getters / passthroughs / re-exports.** `getName() => this.name`, a thin wrapper that forwards args, a barrel file. No logic, no test.
- **Third-party libraries.** You don't test Stripe's SDK, Zod's parser, or `date-fns`. Test *your* usage of them at the integration seam (does your checkout call charge the right amount?), not the library itself.
- **Snapshot-everything.** Auto-generated snapshots of whole component trees or large objects are brittle theater: they break on every intentional change, get blindly re-recorded (`-u`), and assert "it looks like it did last time" — not "it's correct." Narrow, asserted expectations beat a 400-line snapshot. (Targeted snapshots of a small, stable serialized value are fine.)
- **Mock-only "unit" tests of glue.** A test that mocks the DB, the auth, and the logger, then asserts the handler called them — it tests the test's own wiring. This is the single most common AI-generated anti-test in this persona's repo. Delete it; write an integration test instead.

The opportunity cost is the real argument: every hour spent testing a getter or re-recording a snapshot is an hour not spent on the authorization test that would have caught the tenant-isolation bug. Coverage spent on Tier C is coverage stolen from Tier A.

---

## Coverage as a signal, not a target

Coverage measures which lines ran during tests. It does **not** measure whether the tests would catch a bug — a test with no meaningful assertions executes the line and counts it as "covered." So coverage is a useful *flashlight* and a destructive *goal*.

**The Goodhart trap:** the moment a global coverage percentage becomes a merge requirement, it stops being a measure and becomes a target gamed by tautological tests. People write tests that call the function and assert nothing real, or assert that a mock returned its own configured value, purely to color the lines green. You end up with a higher number and no more safety — often *less*, because now there's a wall of meaningless tests to maintain that everyone trusts.

Use coverage the right way:

- **As a discovery tool.** Run a coverage report over the Tier A modules and look at what's *red*. An uncovered branch in an authorization check or a payment path is a finding — go write that test. This is coverage doing its actual job: finding the untested critical path.
- **Track critical-path coverage, not repo average.** "85% of the auth/billing/mutation modules' branches are covered" is a meaningful number. "73% of the whole repo" is noise dominated by Tier C files. If you gate on coverage at all, scope the gate to the Tier A directories, and prefer **branch** coverage (did both sides of the `if` run?) over line coverage there.
- **Never set a blanket repo-wide percentage mandate.** It manufactures exactly the tautological tests this whole skill exists to prevent.
- **Treat missing coverage tooling as missing visibility, not automatic inadequate testing.** Note it during discovery. Make a TEST finding only when available evidence shows a Tier A path or branch is untested; do not manufacture a finding from the absence of a repo-wide number.

If you want a number that actually means "the tests catch bugs," that's mutation testing (Tier 2) on the critical modules — not coverage.

---

## Test-gate policy

This is about *which suites block a merge and what green must mean* — the policy. The pipeline that runs them (runners, caching, shards, deploy gating) is **`craft-infra`** → `ci-cd.md`; don't specify job mechanics here. The per-rule code-level checks (how an individual test or flake is structured) live in `test-design.md` and `flake.md`; don't duplicate them.

**What must block a merge:**

- Static checks: typecheck and lint. Cheapest, fastest, catch the most per second.
- The **unit + integration suite** in full. A red integration test on the critical path is a blocking failure, not a "we'll fix it later."
- The **critical-flow e2e smoke tests** at minimum on merge to the deploy branch (they're too slow/flaky to run on every push — see ordering below).

**What "green" must mean:** every required test ran and passed *for a real reason*. A suite that's green because tests were `.skip`'d, because assertions were commented out, or because a flaky test was given infinite retries is not green — it's a lie that the gate now certifies. A skipped test on the critical path should fail the gate (or at least surface loudly), not pass silently.

**Flake quarantine policy:** a test that fails intermittently destroys trust in the whole suite — once people see red and merge anyway, the gate is dead. Policy: when a test flakes, **quarantine it** (move it out of the blocking set into a tracked, non-gating lane) with an owner and a ticket — *not* paper over it with a blanket retry that hides the nondeterminism. Quarantine is a debt with a deadline, not a graveyard. The mechanics of diagnosing and fixing the flake are in `flake.md`; the *policy* is: never let a known-flaky test stay in the blocking gate, and never disable a test silently.

**Fast-feedback ordering:** run the cheap, high-signal checks on every push and the expensive ones later, so the common case (a typo) fails in seconds, not after a ten-minute e2e run.

- **On every push to a PR:** typecheck, lint, unit + integration. Seconds to low minutes; this is the tight loop.
- **On merge / merge-queue to the deploy branch:** the e2e smoke suite (and Tier 2's load/contract suites, when they exist). Slower and flakier, gated where it matters but kept out of the per-push loop.

The ordering principle (fail fast, fail cheap) and the job-level implementation are owned by `ci-cd.md` — cross-reference it; the decision *that integration blocks every push and e2e blocks the merge* is the policy owned here.

---

## Quick-reject table

| Smell | Fix |
| --- | --- |
| No tests at all on auth / authorization / payments / data mutations | Write Tier 1 integration tests on the Tier A critical path first — that's the whole budget until it's covered |
| Test suite is hundreds of mock-only "unit" tests of handlers/glue | Delete the mock theater; replace with integration tests against the real DB/auth (the bug class that actually ships) |
| Test asserts a mock returned its own configured value | No real assertion — rewrite to assert observable behavior, or delete; it only colors coverage |
| Blanket repo-wide coverage % mandated as a merge gate | Drop the global mandate; gate (if at all) on branch coverage of Tier A dirs; use coverage to *find* untested critical paths |
| Pushing contract / load / mutation tests before the critical path has any coverage | Stop — that's Tier 2 on a Tier 1 codebase; cover auth/payments/mutations first |
| Snapshot test of a whole component tree / large object, re-recorded with `-u` on every change | Replace with narrow asserted expectations on the values that matter; reserve snapshots for small stable serialized output |
| Tests for framework internals, types, getters, or third-party libraries | Delete — zero bug-catching value, pure upgrade-breakage cost; test *your* usage at the integration seam instead |
| All-unit suite on glue code, no integration layer | High coverage, low confidence — add integration tests on the seams (default to the trophy for this stack) |
| Heavy mocking required to stand up a "unit" test of a handler | That's the signal it should be an integration test against the real dependency |
| Flaky test left in the blocking suite, or "fixed" with a blanket retry | Quarantine it (non-gating lane + owner + ticket); diagnose per `flake.md`; never silently retry-hide it |
| Green suite achieved via `.skip` / commented-out asserts | Not green — a skipped critical-path test must fail or loudly surface the gate |
| e2e suite run on every push (slow, flaky, kills the tight loop) | Move e2e to merge/merge-queue; keep typecheck + unit + integration on every push |
| CI job mechanics (caching, shards, parallelism) specified as "testing strategy" | That's pipeline structure — defer to `craft-infra` → `ci-cd.md`; this file owns only *which suites gate* |

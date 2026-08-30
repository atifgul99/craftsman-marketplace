# Killing Flaky Tests

A flaky test passes and fails on the same code. It is not a minor annoyance — it is the single fastest way to destroy a team's trust in its own test suite. This file is the diagnosis side: how to recognize each cause of nondeterminism, reproduce it on demand, and apply the *specific* fix for *that* cause. "Make it deterministic" is not a fix; it is a restatement of the problem.

> **Scope split.** This file owns **diagnosing and killing nondeterministic failures**: the flake taxonomy (time, async races, order-dependence, pollution, real I/O, animation, parallelism), the reproduce-on-demand workflow, and retry-vs-quarantine policy. The *write-time* determinism setup — how to install fake timers, seed RNG, structure fixtures so flake never appears — lives in **`test-design.md`** (cross-referenced below); this file assumes the flake already exists and you have to hunt it. DB isolation mechanics (testcontainers, per-worker schemas, transactional rollback) are owned by **`backend-data-testing.md`** — referenced here, detailed there. What to test and at which level is **`strategy.md`**; AAA structure and naming is **`test-design.md`**.

---

## Contents

- [Why flake is worse than no test](#why-flake-is-worse-than-no-test)
- [The flake taxonomy](#the-flake-taxonomy)
  - [1. Time and clock](#1-time-and-clock)
  - [2. Async races and missing await](#2-async-races-and-missing-await)
  - [3. Order-dependence and shared state](#3-order-dependence-and-shared-state)
  - [4. Test pollution and leaked resources](#4-test-pollution-and-leaked-resources)
  - [5. Real I/O and network](#5-real-io-and-network)
  - [6. Animation, transition, and viewport timing](#6-animation-transition-and-viewport-timing)
  - [7. Resource contention and parallelism](#7-resource-contention-and-parallelism)
- [Diagnosis workflow: reproduce on demand](#diagnosis-workflow-reproduce-on-demand)
- [Retries vs quarantine policy](#retries-vs-quarantine-policy)
- [Prevention at write time](#prevention-at-write-time)
- [Flake taxonomy summary](#flake-taxonomy-summary)

---

## Why flake is worse than no test

A test that's absent tells the truth: this path is unverified. A flaky test lies. It goes red on a clean PR, the author re-runs CI, it goes green, and the change merges. The lesson the team internalizes is: **red doesn't mean broken — re-run until green.** Once that habit forms, the suite stops being a gate. A genuine regression now produces the same red the flake produces, and it gets the same treatment: re-run, shrug, merge. One reliably-flaky test trains everyone to ignore the entire signal.

The cultural failure mode compounds:

- **Re-run-to-green normalizes ignoring red.** Engineers stop reading failure output. The diff between "flaky test #47" and "you just broke checkout" disappears.
- **Blanket auto-retry hides it from view but not from cost.** A suite where every test retries 3x looks green and is silently masking both races and real intermittent bugs (see policy below).
- **Flake is contagious in attention.** The 2% of tests that flake consume most of the debugging time and most of the trust, dragging the credibility of the 98% solid tests down with them.

So the bar is: a flaky test is a P1-style defect in the test suite itself. You either fix it or quarantine it on a deadline — you do not leave it in the gate flickering. Leaving it is strictly worse than deleting it, because a deleted test doesn't lie.

---

## The flake taxonomy

Every flaky test traces to one of these causes. The skill is *recognition* — matching the failure's fingerprint to a category — because each category has a different fix and applying the wrong one (e.g. a sleep where you needed a clock) just moves the flake around.

### 1. Time and clock

**Recognize it:** Failures cluster at specific wall-clock times — overnight CI runs fail, the same test passes when you run it at 2pm. A test about "expires in 24h" fails near midnight or at month/year boundaries. Assertions on formatted dates fail on machines in another timezone. Anything comparing `Date.now()` to a value computed milliseconds earlier and expecting equality. DST transition days produce one-off failures.

**Why:** The test reads real time, which advances between the setup and the assertion, or differs by environment. TTL math (`createdAt + 3600_000 < Date.now()`) straddles a boundary depending on *when* it runs. `new Date().toISOString()` embeds the runner's timezone unless forced to UTC.

**Fix — freeze and inject:**

```ts
// Vitest / Jest: pin the clock, then advance it deterministically
import { vi, beforeEach, afterEach } from "vitest";

beforeEach(() => vi.useFakeTimers({ now: new Date("2026-01-15T12:00:00Z") }));
afterEach(() => vi.useRealTimers());

it("expires after the TTL window", () => {
  const token = issueToken(); // reads the frozen clock
  vi.advanceTimersByTime(3_600_001); // cross the boundary on purpose
  expect(isExpired(token)).toBe(true);
});
```

- Force the process timezone in test config: `TZ=UTC` in the test env. This kills an entire class of "passes on CI, fails on a laptop in IST" flake.
- For code that calls `Date.now()` directly, the durable fix is **inject a clock** (`now: () => number` dependency) rather than monkey-patching globals — but fake timers handle the existing case without a refactor.
- Watch for libraries that capture time at import (module-scope `const START = Date.now()`); fake timers installed in `beforeEach` are too late. Fake before importing, or refactor the capture.

The write-time setup for clock injection and the seam to inject it lives in `test-design.md`; here you're retrofitting it onto an existing red test.

### 2. Async races and missing await

**Recognize it:** The test passes locally on a fast machine and fails in CI (slower, contended). `act(...)` warnings in React test output. The assertion checks for something that an async effect hasn't produced *yet*. A `setTimeout`-style sleep was added "to make it pass" — that's a tell, not a fix. Error messages like "element not found" or "expected 1 call, got 0" that vanish on re-run.

**Why:** The assertion runs before the awaited effect completes. The test fired an action that schedules a microtask/macrotask/network call and then asserted synchronously, or with a fixed `sleep(100)` that's long enough *usually* but not under load. Fixed sleeps are doubly broken: too short → flake, too long → slow suite.

**Fix — await the *condition*, never the clock:**

```ts
// React Testing Library: findBy* and waitFor poll until the condition holds
// BAD: await new Promise(r => setTimeout(r, 100)); expect(...).toBeTruthy();
// GOOD:
await userEvent.click(screen.getByRole("button", { name: /save/i }));
expect(await screen.findByText(/saved/i)).toBeInTheDocument(); // retries until present

await waitFor(() => expect(mockApi).toHaveBeenCalledTimes(1)); // polls the predicate
```

- Wrap state-updating interactions so React flushes effects: `userEvent`/`fireEvent` are already wrapped; manual state pokes need `await act(async () => { ... })`. An `act()` warning is React telling you an update happened outside the tracked window — fix the warning, don't suppress it.
- For non-UI async, `await` the actual promise the code returns. If the production code is fire-and-forget (no returned promise to await), that's often a *design* smell surfacing as flake — the code needs an observable completion signal.
- `waitFor` polls and has a timeout; it is not a sleep — it returns the instant the predicate passes. Keep its body to a *single* assertion so the failure message is precise.

### 3. Order-dependence and shared state

**Recognize it:** The test passes when run alone (`-t "my test"`) but fails inside the full suite — or vice versa. Reordering the file changes the result. A test fails only when a *different* test ran before it. CI shards differently than local and the failure follows the shard.

**Why:** State leaks between tests through a shared channel: a module-scope singleton (a cache, a connection, a registered handler), a shared DB row that test A mutates and test B reads, an env var one test sets and never restores, a global like `process.env`, `globalThis`, a mocked module whose state isn't reset. The tests are coupled through the channel even though they look independent.

**Fix — isolate, reset, and randomize to *expose*:**

```ts
// 1. Reset module state between tests
beforeEach(() => {
  vi.resetModules();   // fresh module registry -> fresh singletons
  vi.clearAllMocks();  // call history; vi.resetAllMocks() also drops implementations
});

// 2. Restore globals you touch
const ORIGINAL = process.env.FEATURE_FLAG;
afterEach(() => { process.env.FEATURE_FLAG = ORIGINAL; });
```

- The diagnostic superpower: **randomize test order to make order-dependence fail loudly instead of silently.** Jest: `--randomize` (or the `randomize` config). Vitest: `sequence.shuffle: true`. Playwright runs files in parallel by default which already surfaces a lot of this. If randomizing flips a green suite red, you have found order-dependence — that's the goal, not a regression.
- For shared DB rows: each test should own its data (unique keys / per-test fixtures) or run inside a transaction rolled back at teardown. The isolation mechanics — transactional rollback, per-worker schema, testcontainers — are owned by `backend-data-testing.md`.
- Singletons are the usual culprit in Node: a module that does work at import time and caches it. `vi.resetModules()` between tests gives each test a clean instance; the long-term fix is dependency injection so the singleton isn't reached for implicitly.

### 4. Test pollution and leaked resources

**Recognize it:** "Jest did not exit one second after the test run completed" / a hanging Vitest process. Worker warnings about open handles. Memory climbing across the run. An MSW handler added in one test still intercepting in the next. A React component that logged a state update after the test finished ("can't perform a state update on an unmounted component"). Timers firing after their test ended.

**Why:** A test acquired a resource and didn't release it: an open DB connection or socket, a `setInterval` never cleared, a subscription/listener never removed, a component never unmounted, a server never closed, an `AbortController` never aborted. Or a *shared* test double accumulated registrations — the classic being MSW request handlers added per-test without `server.resetHandlers()`.

**Fix — symmetric setup/teardown and the open-handles report:**

```ts
// MSW: the canonical reset triad
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers()); // <- drop per-test overrides; the omission that bites
afterAll(() => server.close());
```

- Run the leak detector and read it: Jest `--detectOpenHandles` (slow, but it names the file/line that opened the handle), Vitest surfaces unclosed handles via the `--reporter` output and `pool` teardown. The report points at the exact resource — read it rather than guessing.
- For every `setInterval`/`setTimeout`/listener/subscription a test creates, there is a matching teardown. RTL auto-unmounts between tests when configured (`afterEach(cleanup)` — automatic with the global setup); confirm it's wired.
- `onUnhandledRequest: "error"` in MSW converts a silent leak (a request escaping to a stale or missing handler) into a loud failure. Turn it on.
- Close servers, pools, and DB clients in `afterAll`. An unclosed pool is both a leak and a parallelism hazard (next section).

### 5. Real I/O and network

**Recognize it:** Failures correlate with network conditions, third-party outages, or rate limits ("429" in test logs). The test slows down or fails on a flaky connection, in CI behind a proxy, or offline. DNS resolution appears in a unit-test stack trace. A test that depends on data in a real shared sandbox account (someone else mutated it).

**Why:** The test hits a real service, real DNS, or a real shared environment it doesn't control. Anything you don't control can fail or change underneath you — that's nondeterminism by construction.

**Fix — stub the boundary:**

```ts
// MSW intercepts at the network layer; the code under test is unchanged
import { http, HttpResponse } from "msw";

server.use(
  http.get("https://api.example.com/user/:id", ({ params }) =>
    HttpResponse.json({ id: params.id, name: "Test User" })
  )
);
```

- Prefer intercepting at the network boundary (MSW for HTTP, equivalents for other protocols) over mocking your own fetch wrapper — you test more real code and the stub survives refactors of the client.
- `onUnhandledRequest: "error"` doubles as a guard: any real request that escapes the stubs fails the test instead of silently flaking later.
- For integration tests that genuinely need a real datastore, the answer is a *controlled* real dependency (testcontainers / ephemeral DB), not the shared cloud one — see `backend-data-testing.md`. That's deterministic because you own its lifecycle; a shared sandbox is not.
- A legitimate exception is a true end-to-end smoke test against a deployed environment — those *do* touch real services, and that's where a bounded retry can be defensible (see policy).

### 6. Animation, transition, and viewport timing

**Recognize it (mostly Playwright/E2E):** A click "misses" because the element was mid-slide-in. Screenshots differ by a few pixels run-to-run (animation frame). A `page.waitForTimeout(500)` was added to "let the modal open." Navigation races — an assertion runs against the old page because the new one hadn't committed. Failures concentrate on transition-heavy screens.

**Why:** The test interacts with the UI while it's still animating/transitioning, or it guesses at timing with a fixed wait that's right *usually*. Browsers don't guarantee animation duration under load.

**Fix — web-first assertions and disable animations:**

```ts
// Playwright auto-waits for actionability (visible, stable, enabled) before acting.
// BAD: await page.waitForTimeout(500); await page.click("#save");
// GOOD: web-first assertions retry until the condition holds:
await expect(page.getByRole("dialog")).toBeVisible(); // waits for the modal
await page.getByRole("button", { name: "Save" }).click(); // auto-waits for stable+enabled
await expect(page).toHaveURL(/\/success/); // waits for navigation to commit
```

- Kill animations globally so "stable" is reached instantly and screenshots are deterministic:

```ts
// playwright.config.ts -> use snapshot animation control, or per-test:
await page.addStyleTag({ content: `*, *::before, *::after {
  animation-duration: 0s !important; transition-duration: 0s !important;
  animation-delay: 0s !important; transition-delay: 0s !important; }` });
// For visual snapshots, expect(page).toHaveScreenshot also supports animations: "disabled".
```

- Never `waitForTimeout` to wait for a condition — wait for the *condition* (`toBeVisible`, `toHaveText`, `toHaveURL`, `waitForResponse`). `waitForTimeout` is acceptable only for deliberately observing the *absence* of a change over a window, never as a substitute for actionability.
- Locator + web-first `expect` is the auto-waiting combo; `page.$` / `elementHandle` snapshots are static and race. Prefer role/text locators and assert through `expect(locator)`.

### 7. Resource contention and parallelism

**Recognize it:** The suite passes with `--runInBand` / a single worker but fails under default parallelism. Two tests bind the same port (`EADDRINUSE`). Tests write the same temp file or fixture path and clobber each other. Two workers hit the same DB table/row concurrently. CPU-bound tests time out only when all cores are busy with other workers.

**Why:** Parallel workers are separate processes sharing the *machine* — ports, filesystem paths, a single DB, CPU. Anything global-to-the-machine becomes a shared mutable resource across workers, reintroducing the order/state problems of category 3 at the process level.

**Fix — per-worker isolation:**

```ts
// Derive worker-unique resources from the worker id.
// Vitest: process.env.VITEST_WORKER_ID ; Jest: process.env.JEST_WORKER_ID
const workerId = process.env.VITEST_WORKER_ID ?? "1";
const dbName = `test_db_${workerId}`;     // per-worker schema/database
const port = 4000 + Number(workerId);     // per-worker port (or bind :0 for an OS-assigned free port)
const tmpDir = path.join(os.tmpdir(), `suite-${workerId}-${process.pid}`);
```

- Bind servers to port `0` to let the OS pick a free port, then read the actual port back — eliminates `EADDRINUSE` entirely without hand-assigning.
- Give each worker its own database/schema (Playwright: a per-worker fixture; backend: per-worker schema or container). The lifecycle/isolation mechanics live in `backend-data-testing.md`.
- Reducing workers (`--runInBand`, `workers: 1`) is a *diagnostic* to confirm the category, not the fix — serializing the suite to hide a contention bug trades correctness signal for speed loss and leaves the bug latent.
- Use unique temp paths (worker id + pid) for any file a test writes; never a shared fixed path under `os.tmpdir()`.

---

## Diagnosis workflow: reproduce on demand

You cannot fix what you can't reproduce. A flake that fails 1-in-50 in CI is invisible until you make it fail reliably on your machine. The workflow:

1. **Reproduce by running it many times.** The single highest-value technique:

   ```bash
   # Vitest: run the file 50 times, fail-fast on first red
   npx vitest run path/to/flaky.test.ts --retry=0 --bail=1 \
     && for i in $(seq 50); do npx vitest run path/to/flaky.test.ts || break; done

   # Jest: built-in repeat
   npx jest path/to/flaky.test.ts --runInBand --logHeapUsage \
     && npx jest path/to/flaky.test.ts -i --testPathPattern=flaky # loop in shell similarly

   # Playwright: native repeat-each
   npx playwright test flaky.spec.ts --repeat-each=50 --workers=1
   ```

   If 50x passes clean, escalate to 200x, and run it *both* in isolation and inside the full suite — the gap between those two is itself the diagnosis (see step 3).

2. **Vary the dimensions one at a time** to bisect the *category*:
   - Run alone vs in the full suite → green-alone/red-in-suite ⇒ **order/state (cat 3)** or **parallelism (cat 7)**.
   - `--randomize` / `sequence.shuffle` → if a stable suite breaks ⇒ **order-dependence (cat 3)**.
   - `--workers=1` vs default → green-serial/red-parallel ⇒ **contention (cat 7)**.
   - Pin `TZ` and the clock → fixes it ⇒ **time (cat 1)**.
   - Run with network blocked / `onUnhandledRequest: "error"` → new failure ⇒ **real I/O (cat 5)**.

3. **Seed and freeze to make a found cause reproducible.** Once a randomized run finds a failing order, the runner prints the **seed** — re-run with that exact seed (`--sequence.seed=<n>` / Jest seed) to replay the same order every time while you fix it. Same for any RNG in the code under test: seed it so the failing input is stable.

4. **Read the open-handles / leak report** (cat 4): `jest --detectOpenHandles`, Vitest teardown warnings. It names the file and line that opened the unreleased resource — this is direct evidence, not inference.

5. **Bisect the suite if isolation is the issue.** If the test only fails after *some* prior test, binary-search the set of preceding tests (run halves) to find the polluter. The polluter is the bug, not the victim that goes red.

The mindset: a flake is a deterministic bug whose trigger you haven't found yet. The job is to find the hidden input (time, order, concurrency, a leaked handle) and pin it.

---

## Retries vs quarantine policy

When a test flakes, there are three responses. Two are usually wrong.

**Blanket auto-retry (usually wrong).** Configuring the whole suite to retry every test N times (`retries: 2`) makes CI green and feels like a fix. It is dangerous because:

- It **masks real races** — a genuine ordering/concurrency bug in the *product* that flakes the test is now hidden; the retry passes and the bug ships.
- It **masks real intermittent product bugs** — a test catching a 1-in-3 production defect now passes 2-of-3 retries and reports green.
- It **hides the flake from accounting** — you can't fix what you've configured to be invisible. The suite rots while looking healthy.

So global retry is a sleep-pill for the symptom that suppresses two distinct classes of real bug. Don't reach for it as the default.

**Quarantine (usually right).** When you can't fix the flake immediately, *remove it from the gate* — but keep it visible and on a clock:

- **Isolate from the merge gate** so it can't block or falsely-pass PRs (tag it, route it to a non-blocking job, or `test.fixme`/`skip` with a tracking reference).
- **Track it** — open a ticket, link the failing run, record the suspected category. A quarantined test with no ticket is just a deleted test pretending to exist.
- **Deadline it** — quarantine is a fix-by date, not a parking lot. A test that sits quarantined for a quarter should be fixed or deleted; a stale quarantine is the same lie as a flaky gate, just quieter.
- Quarantine still *runs* (off the gate), so you keep the repro signal to debug against. That's the difference from skipping.

**Bounded retry (legitimately right in one place).** A small, explicit retry is defensible when the nondeterminism is *inherent to a real external dependency you don't control* — typically an E2E smoke test against a deployed environment where transient network/infra blips are real and expected. The legitimacy test:

- It's **scoped to the specific test/project** (Playwright per-project `retries`), not the whole suite, and ideally CI-only.
- The flake source is **outside the code under test** (real network, real third-party), so a retry can't mask a product race — there's no race to mask.
- It's paired with **flake reporting** so a test that *needs* its retries is surfaced, not silently leaned on.

If you're adding a retry to a unit or component test, you're almost always cheating — that flake is a category 1–4 bug with a real fix, and the retry just postpones finding it. Retry papers over the symptom; quarantine-plus-fix removes the cause.

---

## Prevention at write time

The diagnosis above is the cure; these habits are the vaccine, and they belong at write time (detailed in `test-design.md` — this file links the diagnosis cause to the prevention habit):

- **Default to a frozen clock and forced `TZ=UTC`** in the shared test setup so cat-1 flake never starts (`test-design.md` has the global setup).
- **Seed all RNG** from a fixed value in test setup; a printed seed on randomized order lets you replay (cat 1/3).
- **Assert on conditions, never on time** — `findBy`/`waitFor`/web-first `expect` by default; treat any `sleep`/`waitForTimeout` in a PR as a flake waiting to happen (cat 2/6).
- **Symmetric setup/teardown** — every acquire has a release in the same scope; wire the MSW reset triad and RTL cleanup once, globally (cat 4).
- **Each test owns its data and resources** — unique keys, per-worker DB/port/temp paths; no shared mutable fixture (cat 3/7). Mechanics in `backend-data-testing.md`.
- **Run randomized and parallel from day one**, including in CI, so order/contention flake surfaces while the test is fresh in your head rather than months later in someone else's PR.

---

## Flake taxonomy summary

| Category | Recognize it by | Specific fix |
| --- | --- | --- |
| **Time / clock** | Fails near midnight / boundaries; passes by time of day; timezone-dependent; `Date.now()` equality | Fake timers + `advanceTimersByTime`; force `TZ=UTC`; inject a clock |
| **Async race / missing await** | Passes locally, fails in CI; `act()` warnings; a `sleep` was added to "fix" it | `await` the condition (`findBy`/`waitFor`), never a fixed sleep; wrap state updates in `act` |
| **Order-dependence / shared state** | Green alone, red in suite (or reverse); reorder flips it | `resetModules`/`clearAllMocks`; restore globals; randomize order to expose; per-test data |
| **Pollution / leaked resources** | "Did not exit"; open-handle warnings; stale MSW handlers; unmount warnings | Symmetric teardown; `server.resetHandlers()`; `--detectOpenHandles`; close pools/servers |
| **Real I/O / network** | Correlates with outages/rate-limits; DNS in stack trace; shared sandbox mutated | Stub at the network boundary (MSW); `onUnhandledRequest:"error"`; owned DB (`backend-data-testing.md`) |
| **Animation / viewport (E2E)** | Click misses mid-transition; pixel-diff snapshots; `waitForTimeout` before interacting | Web-first auto-waiting assertions; disable animations globally |
| **Contention / parallelism** | Green serial, red parallel; `EADDRINUSE`; clobbered temp files | Per-worker DB/port/temp from worker id; bind port `:0`; serial run is diagnosis only |

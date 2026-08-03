# Test Design

A test earns trust by failing only when behavior is wrong and passing only when behavior is right. Most tests inherited from an AI-built MVP fail that bar twice over: they break on a harmless rename (because they assert *how* the code works) and they pass even when the code is broken (because they assert that a mock was called, not that anything happened). The discipline: **assert the observable result, make the test deterministic so the same input always produces the same verdict, and let each test own the minimal data it needs.** A test that does these three things survives refactors, never flakes, and tells you something true.

> **Scope split.** This file owns the anatomy of a single trustworthy test: behavior-vs-implementation assertions, determinism (clock/randomness/IO control), assertion quality, test-data construction, structure/naming, and isolation between tests. It does **not** decide *what* to test or how much — coverage strategy, the test pyramid, and what deserves a test at all live in `strategy.md`. Diagnosing and quarantining a test that flakes despite your best efforts (the flake taxonomy) lives in `flake.md` — this file sets up determinism *so that* flakes don't happen; `flake.md` handles the ones that slip through. Testing Library queries and rendering helpers live in `frontend-testing.md`. The DB-specific reset mechanics — testcontainers, transactional rollback, truncation order — live in `backend-data-testing.md`; this file only states the isolation *requirement* and points there.

---

## Contents

- [Behavior, not implementation](#behavior-not-implementation)
- [Determinism: the same input always gives the same verdict](#determinism-the-same-input-always-gives-the-same-verdict)
- [Assertion quality](#assertion-quality)
- [Test data: factories over shared fixtures](#test-data-factories-over-shared-fixtures)
- [Structure and naming](#structure-and-naming)
- [Isolation between tests](#isolation-between-tests)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Behavior, not implementation

A test should pin the *contract* — the value returned, the response rendered, the row persisted, the event emitted — and stay silent about *how* the code arrives there. The single most common anti-test in an AI-built codebase asserts that an internal function or a mock was called. That assertion passes whether or not the function did anything useful, and it breaks the moment you rename or inline the internal — so it fails on correct refactors and passes on real bugs. It is the wrong test pointed at the wrong thing.

```ts
// WRONG — asserts the mechanism. Passes even if the email is never sent;
// breaks if you rename sendEmail or batch sends through a queue.
it("registers a user", () => {
  const sendEmail = vi.spyOn(mailer, "sendEmail");
  registerUser({ email: "a@b.com" });
  expect(sendEmail).toHaveBeenCalled();
});

// RIGHT — asserts the observable effect. Survives any internal refactor;
// fails only if a welcome email genuinely doesn't go out.
it("sends a welcome email to a newly registered user", async () => {
  await registerUser({ email: "a@b.com" });
  const sent = await testMailbox.messages();
  expect(sent).toContainEqual(
    expect.objectContaining({ to: "a@b.com", subject: "Welcome" }),
  );
});
```

The dividing line: would this assertion still be correct if someone rewrote the implementation without changing what the caller observes? If yes, it tests behavior. If a rename, an extracted helper, or a swapped library would break it, it tests implementation.

Where to point the assertion, by layer:

- **Pure function / service:** the return value, or the thrown error type and message.
- **HTTP handler:** the status code and response body — `expect(res.status).toBe(403)` plus the error code in the body, not "the authorize() middleware was invoked."
- **Component:** what the user sees — rendered text, the disabled state of a button, an element appearing or disappearing — via Testing Library queries (see `frontend-testing.md`). Never assert that a specific hook ran or a `useState` setter was called.
- **DB write:** read the row back and assert its columns. `expect(db.query(...)).toEqual(...)`, not "the `insert` spy received these args."

**Mocks are for boundaries you don't own, not for your own code.** Mock the payment provider's SDK, the third-party HTTP call, the system clock. Do *not* mock your own repository, service, or util just to assert it was called — that replaces a real test with a tautology. When you must mock a boundary, assert on the *outcome* the mock enables (the order was marked paid), not merely that the mock was invoked. `toHaveBeenCalledWith` on an external boundary is sometimes the only observable signal (e.g. "we charged the right amount") — that's legitimate; `toHaveBeenCalled` on your own function almost never is.

---

## Determinism: the same input always gives the same verdict

A non-deterministic test is worse than no test: it trains the team to ignore red. The cause is almost always a hidden input the test doesn't control — wall-clock time, randomness, real network, the filesystem, or the machine's locale. Control every one of them.

**Freeze the clock.** Any code that reads `Date.now()`, `new Date()`, `performance.now()`, or sets a timeout must run against a clock the test owns.

```ts
// Vitest / Jest — fake timers pin "now" and let you advance it deliberately.
beforeEach(() => vi.useFakeTimers({ now: new Date("2026-01-15T12:00:00Z") }));
afterEach(() => vi.useRealTimers());

it("marks a token expired 60 minutes after issue", () => {
  const token = issueToken();           // issued at the frozen now
  vi.advanceTimersByTime(60 * 60_000);  // move time forward on purpose
  expect(isExpired(token)).toBe(true);
});
```

Better still where the design allows: **inject the clock** rather than reaching for global fake timers. A function that takes `now: Date` (or a `clock: () => Date`) is trivially testable with a literal and needs no timer machinery at all. Fake timers are the fallback for code you can't refactor to accept a clock.

```python
# Pytest — freezegun for code that calls datetime.now() internally
from freezegun import freeze_time

@freeze_time("2026-01-15 12:00:00")
def test_token_issue_timestamp():
    assert issue_token().issued_at == datetime(2026, 1, 15, 12, 0, 0)
```

**Seed randomness.** A test that asserts on `Math.random()`, `crypto.randomUUID()`, or unseeded faker output is a coin flip. Generate random *test data* with a seeded generator so values are stable run to run; never assert on a value the production code derived from real entropy.

```ts
import { faker } from "@faker-js/faker";
beforeEach(() => faker.seed(42));  // same data every run
// Need a fixed UUID in an assertion? stub the generator, don't assert the real one:
vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-4000-8000-000000000000");
```

**No real network, filesystem, or `Date.now()` in the path under test.** A unit/integration test that makes a live HTTP call depends on a server you don't control and a network that drops packets — it fails for reasons that have nothing to do with your code. Stub the boundary (MSW for HTTP in TS, `responses`/`respx` in Python). Reads and writes to the real filesystem leak state between runs and break in CI; use a temp dir the test creates and tears down, or an in-memory fs.

**Time-zone and locale traps** are the determinism bugs that pass on your laptop and fail in CI:

- `new Date("2026-01-15")` parses as **UTC midnight**, but `new Date(2026, 0, 15)` is **local midnight** — the two differ by your offset. Construct test dates with explicit UTC (`new Date("2026-01-15T00:00:00Z")`) and pin the runner's zone (`TZ=UTC` in the test env, or Vitest's `env: { TZ: "UTC" }`).
- `toLocaleString()`, `Intl.NumberFormat`, `.toLocaleDateString()`, and default number/currency formatting depend on the machine locale. Assert against an explicitly-passed locale, or assert on the structured value before formatting.
- Sorting strings with `localeCompare()` is locale-sensitive; a test asserting sort order can pass in `en-US` and fail in `de-DE`.

The rule behind all of these: a test must have **no hidden inputs**. Every value that affects the verdict is either a literal in the test or something the test explicitly controls.

---

## Assertion quality

The assertion is the point of the test. A weak assertion turns a passing test into false comfort.

**Assert the specific value, not just truthiness.** `expect(result).toBeTruthy()` passes for `1`, `"error"`, `{}`, and `[]` alike — it barely constrains anything. Assert the actual expected value.

```ts
expect(user).toBeTruthy();                              // weak — almost can't fail
expect(user).toEqual({ id: "u1", email: "a@b.com" });  // pins the real contract
expect(items).toHaveLength(3);                          // not just .toBeTruthy() on the array
```

**Beware the assertion-free test — the test that cannot fail.** A test whose body runs code but never asserts (or only asserts inside a callback that never executes) is green forever and tells you nothing. Two common shapes:

```ts
// No assertion at all — passes as long as the call doesn't throw.
it("calculates the total", () => { calculateTotal(cart); });

// Assertion buried in a branch that the test never enters — silently never checked.
it("rejects negatives", () => {
  for (const n of values) if (n < 0) expect(() => f(n)).toThrow();  // empty list ⇒ 0 assertions
});
```

For the async-rejection case, `await expect(p).rejects.toThrow()` (or `expect.assertions(n)` to require a count) prevents a resolved promise from sneaking past an empty `catch`.

**One logical behavior per test.** A test should have one reason to fail. That doesn't mean literally one `expect` — asserting three fields of one returned object is one behavior. It means don't test "creates the order" *and* "sends the receipt" *and* "decrements stock" in one block; when it goes red you won't know which broke, and the first failure hides the rest.

**Don't over-assert on incidental output.** Asserting every field of a large response — including `createdAt`, generated IDs, and fields irrelevant to the behavior under test — makes the test brittle: an unrelated change to an unrelated field turns it red. Assert the fields the behavior is about; ignore the rest (`expect.objectContaining`, or pick the keys you care about).

**Snapshots — when they earn their keep:** a snapshot is a good assertion when the output is large, structured, and *stable*, and a human reviews the diff on change — serialized error trees, a generated SQL string, a settled config object. They are brittle noise when the output contains timestamps, UUIDs, or ordering that varies (every run produces a new snapshot to "update"), or when the snapshot is so large nobody actually reads the diff and `--update` becomes a reflex. A snapshot you regenerate without reading is an assertion you've turned off. Prefer inline snapshots for small outputs (the expected value sits next to the test and is reviewed in the same diff), and scrub non-deterministic fields with a serializer before snapshotting.

---

## Test data: factories over shared fixtures

Each test should construct the minimal data its behavior needs and *own* that data. The anti-pattern to kill is the **mystery guest**: a test that depends on a shared fixture defined far away, whose hidden state determines whether the test passes — so reading the test tells you nothing about why it's green, and editing the fixture for one test silently breaks five others.

```ts
// MYSTERY GUEST — where does adminUser come from? what's on it? who else uses it?
// Change one field of the shared fixture and unrelated tests break.
it("lets an admin delete a post", () => {
  expect(canDelete(adminUser, sharedPost)).toBe(true);
});
```

Prefer a **factory/builder** that produces a valid default object and lets each test override only the fields relevant to its assertion. The defaults keep tests short; the overrides make the *one thing that matters* obvious at the point of the test.

```ts
// A builder: valid defaults, explicit overrides. Each call returns fresh, owned data.
function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    email: faker.internet.email(),   // seeded earlier ⇒ stable
    role: "member",
    createdAt: new Date("2026-01-01T00:00:00Z"),
    ...overrides,
  };
}

it("lets an admin delete any post", () => {
  const admin = makeUser({ role: "admin" });   // the role IS the point of the test
  const post = makePost({ authorId: makeUser().id });
  expect(canDelete(admin, post)).toBe(true);
});

it("forbids a member from deleting someone else's post", () => {
  const member = makeUser({ role: "member" });
  const post = makePost({ authorId: "someone-else" });
  expect(canDelete(member, post)).toBe(false);
});
```

Why this beats shared fixtures:

- **The test is self-documenting.** The override (`role: "admin"`) names the precondition that drives the behavior. A shared `adminUser` hides it.
- **No coupling between tests.** Each call mints fresh data; one test can't mutate state another test reads (see isolation below).
- **Resilient to schema growth.** Add a required column to `User` and you update one factory, not every test.

Keep factories aligned with the real schema so they can't produce invalid objects — derive the type from your Drizzle/Zod model (`Partial<typeof users.$inferInsert>`) so a schema change forces the factory to keep up. A factory that drifts from the schema produces data the production code would reject, and the test passes on fiction.

Shared *read-only reference* data (a static list of country codes) is fine to share. The hazard is shared *mutable* state that tests write to or depend on the contents of.

---

## Structure and naming

**Arrange–Act–Assert**, with the three phases visually distinct (a blank line is enough). Arrange builds the owned data; Act is the single call under test; Assert checks the observable result. When the Act step is buried among setup, the reader can't find what the test actually exercises.

```ts
it("returns 403 when a non-owner tries to update a document", async () => {
  // Arrange
  const owner = makeUser();
  const intruder = makeUser();
  const doc = await createDocument({ ownerId: owner.id });

  // Act
  const res = await updateDocument({ actorId: intruder.id, docId: doc.id });

  // Assert
  expect(res.status).toBe(403);
  expect(res.body.code).toBe("FORBIDDEN");
});
```

**Name the behavior under test, not the method.** The name is documentation that survives in the test runner's output; it should read as a statement of fact about the system. `"returns 403 when the caller is not the owner"` tells you what broke from the report alone. `"test updateDocument"` or `"works correctly"` tells you nothing. A useful shape: *\<result\> when \<condition\>* — "rejects an expired token", "decrements stock by the ordered quantity", "throws ValidationError when amount is negative".

**No logic in tests.** Loops, conditionals, `try/catch` around the assertion, and computed expected values are all places a bug can hide *in the test itself*, and they obscure the one path the test is supposed to exercise.

```ts
// WRONG — the conditional means the real assertion may never run; a computed
// expected value can carry the same bug as the code it's checking.
it("formats prices", () => {
  for (const c of cases) {
    if (c.currency === "USD") expect(format(c)).toBe("$" + c.amount.toFixed(2));
  }
});

// RIGHT — explicit cases, literal expected values, each is one reason to fail.
it.each([
  { amount: 5,    expected: "$5.00" },
  { amount: 5.5,  expected: "$5.50" },
  { amount: 1000, expected: "$1,000.00" },
])("formats $amount as $expected", ({ amount, expected }) => {
  expect(formatUSD(amount)).toBe(expected);
});
```

Table-driven tests (`it.each` / `@pytest.mark.parametrize`) are the right way to cover many inputs without a hand-rolled loop: each row is a separately-reported case with a literal expected value, and one failing row doesn't hide the others.

---

## Isolation between tests

Tests must pass in any order and in parallel. Order-dependence — test B only passing because test A ran first and left state behind — is a latent failure that surfaces the day someone runs a single test, shuffles the suite, or the runner parallelizes. The two sources are **shared mutable state in the test process** (a module-level array, a singleton, a cached config that one test mutates) and **shared external state** (rows one test writes that another reads).

The requirements:

- **Reset shared in-process state between tests.** `beforeEach`/`afterEach` (or `beforeEach` in Pytest fixtures) restores any module-level state, clears mocks (`vi.clearAllMocks()` / `vi.restoreAllMocks()`), and resets fake timers. A spy or mock that leaks from one test into the next is a classic order-dependent bug.
- **No data dependency between tests.** Test B must not rely on a row test A created. Each test arranges its own data via factories (above) and cleans up — or runs inside a rollback boundary.
- **Don't assume execution order.** Vitest and Jest can run files in parallel and shuffle tests; never write a test that "must run after" another. If two tests genuinely share expensive setup, build it fresh per test or use a fixture scoped so each test gets an isolated copy.

The **DB-specific reset mechanics** — transactional rollback per test, truncation order across foreign keys, testcontainers lifecycle, and per-worker database isolation for parallel runs — are involved enough to live on their own page: see `backend-data-testing.md`. This file's rule is only the requirement: when a test finishes, the world must look exactly as it did before the test started.

---

## Quick-reject checklist

| Smell | Fix |
| --- | --- |
| `expect(spy).toHaveBeenCalled()` on the code's *own* internal function | Assert the observable result instead — return value, response body, persisted row, rendered output |
| Mocking your own repository/service to assert it was called | Don't mock code you own; exercise it for real and assert its effect. Mock only boundaries you don't control |
| `Date.now()` / `new Date()` in the path under test, unfrozen | Freeze with fake timers (`vi.useFakeTimers({ now })`) or inject a clock parameter |
| Assertion on `Math.random()`, unseeded faker, or a real `randomUUID()` | Seed the generator (`faker.seed(42)`) or stub it; never assert a value derived from real entropy |
| Real HTTP / filesystem call inside a unit or integration test | Stub the boundary (MSW, `responses`/`respx`); use a temp dir the test owns |
| `new Date("2026-01-15")` vs `new Date(2026, 0, 15)`, or locale-dependent formatting asserted | Construct dates in explicit UTC, pin `TZ=UTC`, pass an explicit locale to formatters |
| `expect(x).toBeTruthy()` / `toBeDefined()` as the only assertion | Assert the specific expected value (`toEqual`, `toHaveLength`, exact field) |
| Test runs code but never asserts (or only inside a branch that may not execute) | Add a concrete assertion; for async rejections use `await expect(p).rejects` or `expect.assertions(n)` |
| One test asserting three unrelated behaviors | Split so each test has one reason to fail |
| Asserting every field including `createdAt` / generated IDs | Assert only the fields the behavior is about (`expect.objectContaining`); scrub volatile fields |
| Snapshot containing timestamps/UUIDs, or regenerated with `--update` unread | Scrub non-deterministic fields, prefer inline snapshots for small output, or use explicit assertions |
| Test depends on a shared fixture defined elsewhere (mystery guest) | Construct minimal owned data per test via a factory/builder with overrides |
| Factory drifted from the real schema (produces objects prod would reject) | Derive the factory type from the Drizzle/Zod model so schema changes propagate |
| Loop / `if` / computed expected value inside the test body | Use `it.each` / `parametrize` with literal expected values |
| Test name is the method name or "works correctly" | Rename to *\<result\> when \<condition\>* ("returns 403 when the caller is not the owner") |
| Mocks/timers/module state leak between tests; suite fails when shuffled or run singly | Reset in `beforeEach`/`afterEach`; clear mocks; give each test its own data (DB reset → `backend-data-testing.md`) |

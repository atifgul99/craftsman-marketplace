# Frontend Testing

How to test React components and hooks the way a user actually drives them — through roles, labels,
and text, with real interaction sequences and real async — so a green suite means the feature works,
not that the implementation hasn't changed. The **method** is here; the exact runner and matchers are
discovered from the repo (Vitest + Testing Library + Playwright assumed), never re-imposed.

> Scope split: this file owns *behavioral* tests of UI — querying, interaction, async states, what to
> mock, hooks, and the component-vs-e2e split. The **visual/rendered audit** (contrast, layout,
> spacing, motion — does it *look* right in a real browser) is **`craft-ux`** → `live-audit.md`; cede
> it, don't reimplement pixel checks here. **Flaky-test taxonomy** (root-causing intermittent
> failures) is **`flake.md`** — this file sets up determinism so flakes don't start. **Backend / API /
> DB tests** are **`backend-data-testing.md`**. **What to test at all** (coverage strategy, the test
> pyramid) is **`strategy.md`** — this file assumes you've decided *this* deserves a test and shows
> how to write it well.

> **See also:** `strategy.md` (what/whether to test) · `flake.md` (determinism, fake timers) ·
> `craft-ux` → `live-audit.md` (the rendered-design audit) · `craft-frontend` → `data-fetching.md` /
> `forms.md` (the code under test).

---

## Contents

- [Playwright setup](#playwright-setup)
- [Query by what the user perceives](#query-by-what-the-user-perceives)
- [userEvent, not fireEvent](#userevent-not-fireevent)
- [Async UI: findBy and waitFor, never sleeps](#async-ui-findby-and-waitfor-never-sleeps)
- [The four states](#the-four-states)
- [Mock the network, not your own code](#mock-the-network-not-your-own-code)
- [Testing hooks](#testing-hooks)
- [Component vs e2e split](#component-vs-e2e-split)
- [Accessibility in tests](#accessibility-in-tests)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Playwright setup

Without a working `playwright.config.ts`, a builder hits "Target page, context or browser has been
closed" or "browserType.launch: Executable doesn't exist" within minutes. Get the config right first
— everything else in Playwright depends on it.

**`playwright.config.ts` with `baseURL` and `webServer`.** `webServer` auto-starts your dev server
before the suite runs and tears it down after. `baseURL` lets every `page.goto('/path')` resolve
without hardcoding `localhost:3000`.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,     // bounded retry, CI only — never on unit/component tests
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  // Start the dev server once; Playwright waits for the URL to respond before running tests.
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,  // reuse a running dev server locally for speed
    timeout: 120_000,
  },

  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Reuse the saved auth state so every test starts already logged in
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
})
```

**`globalSetup` for auth state (storageState).** Authenticating on every test is slow and brittle.
Log in once in a `*.setup.ts` file, save the browser storage state to disk, and all tests in the
project start with a live session.

```ts
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'
import path from 'path'

const AUTH_FILE = 'playwright/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel(/email/i).fill('test@example.com')
  await page.getByLabel(/password/i).fill(process.env.TEST_USER_PASSWORD!)
  await page.getByRole('button', { name: /log in/i }).click()
  await expect(page).toHaveURL('/dashboard')

  // Persist cookies + localStorage so other tests skip the login flow
  await page.context().storageState({ path: AUTH_FILE })
})
```

The `storageState` path in `playwright.config.ts` (under the project's `use`) tells Playwright to
restore this state at the start of each test worker. Add `playwright/.auth/` to `.gitignore` — the
saved state contains session tokens.

**CSS to disable animations.** Animations make "stable" (the Playwright actionability check) slow to
satisfy, cause screenshot diffs between runs, and produce the "element detached" class of flake.
Disable them globally in the setup fixture or inject a stylesheet at the start of each test.

```ts
// In a global beforeEach or a base test fixture:
test.beforeEach(async ({ page }) => {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `,
  })
})
```

For the `prefers-reduced-motion` media feature — which many animation libraries respect — pass it
via the browser context:

```ts
// playwright.config.ts → use block, or per-project:
use: {
  reducedMotion: 'reduce',   // sets prefers-reduced-motion: reduce for all pages
}
```

Both approaches are complementary: `reducedMotion` catches CSS `@media (prefers-reduced-motion)`
guards; the explicit `addStyleTag` catches everything else. Use both for a fully stable suite.

---

## Query by what the user perceives

A user doesn't find a button by its CSS class or a `data-testid` — they find it because it's labeled
"Save". Query the same way, and the test fails for the same reasons the user would be blocked. This
order is the priority (Testing Library's own guidance, condensed):

1. **By role + accessible name** — `getByRole('button', { name: /save/i })`,
   `getByRole('textbox', { name: /email/i })`, `getByRole('heading', { name: /invoices/i })`. This is
   the default for almost everything: it asserts the element exists *and* is exposed to assistive tech
   with the right name, so the test doubles as a free a11y check.
2. **By label / placeholder / text** — `getByLabelText`, `getByText`, `getByDisplayValue` for content
   the user reads directly.
3. **By `data-testid`** — the escape hatch, not the default. Legitimate when there's no accessible
   handle: a decorative chart container, a non-interactive wrapper you need to scope within, a dynamic
   list row with no stable text. Reach for it last, and treat a test that *can only* be written with
   `testid` as a hint the component may be missing a role or label.

```tsx
// Brittle: couples the test to DOM structure and class names.
const { container } = render(<LoginForm />);
container.querySelector('.btn-primary')!.click();

// Resilient: finds the control the way the user does; survives a refactor
// that changes markup or classes but keeps the same accessible button.
render(<LoginForm />);
await userEvent.click(screen.getByRole('button', { name: /log in/i }));
```

- **`getBy` throws if absent, `queryBy` returns null** — use `queryBy*` only to assert *absence*
  (`expect(screen.queryByRole('alert')).not.toBeInTheDocument()`); using `queryBy` for something you
  expect to exist swallows the helpful "here's the accessible tree" error message.
- **Scope before you reach for testid.** `within(screen.getByRole('row', { name: /ada lovelace/i }))`
  lets you query inside one row by role/text instead of tagging every cell.

---

## userEvent, not fireEvent

`fireEvent.click(el)` dispatches **one** synthetic event. A real click is a *sequence* —
pointerdown, mousedown, focus, pointerup, mouseup, click — and real typing fires keydown, the
`beforeinput`/`input` events, and keyup per character. `userEvent` replays those sequences;
`fireEvent` skips them, so it can pass against code a real user would never reach.

```tsx
// fireEvent: sets the value in one shot. Misses focus, per-key handlers,
// onKeyDown maxlength guards, IME/composition — a passing test that lies.
fireEvent.change(input, { target: { value: 'ada@x.com' } });

// userEvent: focuses, then dispatches a key/input event per character,
// exactly like a person typing — exercises onFocus, onKeyDown, validation-on-input.
await userEvent.type(input, 'ada@x.com');
```

- **Default to `userEvent` for every interaction** — `click`, `type`, `selectOptions`, `tab`,
  `keyboard`, `upload`, `clear`. It catches the bugs that matter: a button that never receives focus,
  a field whose `onKeyDown` blocks a character, a custom select that only opens on a specific key.
- **`userEvent` is async — `await` every call.** Forgetting the `await` is a top source of flaky,
  out-of-order assertions.
- **Set it up once per test** with `const user = userEvent.setup()` (call it after fake timers are
  installed, if you use them — see `flake.md`), then `await user.click(...)`. The bare
  `userEvent.click` API still works but `setup()` gives you a consistent, isolated instance.
- `fireEvent` remains the right tool for the rare low-level case — dispatching a `scroll`, a custom
  DOM event, or a `change` on an element `userEvent` can't drive — not as the everyday default.

---

## Async UI: findBy and waitFor, never sleeps

UI that appears after a tick (a fetch resolves, a transition completes) needs the test to *wait for
the thing*, not for a guessed duration. An arbitrary timeout is both slow (you over-wait) and flaky
(you under-wait on a loaded CI box).

- **`findBy*` = `getBy*` + `waitFor`** — it polls until the element appears (default ~1s) then
  asserts. Use it for content that shows up asynchronously:
  `expect(await screen.findByText(/welcome back/i)).toBeInTheDocument()`.
- **`waitFor` for non-element conditions** — a callback that becomes true (a mock was called, an
  element *disappeared* via `waitForElementToBeRemoved`). Keep the callback a pure assertion with no
  side effects; it runs many times.
- **Never `await new Promise(r => setTimeout(r, 500))`.** A fixed sleep encodes a guess about timing
  into the test. If you must control time, use the runner's **fake timers** deterministically
  (`vi.useFakeTimers()` + `vi.advanceTimersByTime`), and remember to pair them with
  `userEvent.setup({ advanceTimers })` — details and pitfalls in `flake.md`.

```tsx
render(<UserCard id="42" />);
// loading first…
expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument();
// …then the resolved content, waited for by name, not by sleep.
expect(await screen.findByRole('heading', { name: /ada lovelace/i })).toBeInTheDocument();
```

**The `act(...)` warning** means a state update happened outside React's batched flush — usually an
async update (a resolved fetch, a `setState` in a `then`) that landed *after* your test's synchronous
assertions ran. The fix is almost never to wrap things in manual `act()`: it's to **await the update**
you triggered — `await userEvent.click(...)`, `await screen.findBy*`, `await waitFor(...)`. Testing
Library wraps its own calls in `act` for you; the warning is telling you a state change escaped
because the test moved on too early. Chasing it with `act()` wrappers hides the race instead of
synchronizing with it.

---

## The four states

Every async surface has four renderings — **loading, error, empty, and data**. craft-ux *designs*
them; your job here is to *prove each one renders* when its condition holds. The data-only test is the
one that passes in the demo and strands the user on a spinner forever in production.

- **Loading:** assert the loading affordance is present before the response settles
  (`getByRole('status')` / a skeleton's accessible label).
- **Error:** drive the network mock to fail (below) and assert the error UI — `getByRole('alert')`,
  retry button — *and* that the happy-path content is absent.
- **Empty:** return a successful response with zero rows and assert the empty state (the "no invoices
  yet" copy / CTA), distinct from both loading and error.
- **Data:** the populated render.

Drive each via the MSW handler for that test (override per-test, below) rather than stubbing the
component's internals — the component should reach each state through its real code path.

---

## Mock the network, not your own code

Mock at the **system boundary** — the HTTP layer — with **MSW**, and let everything inside the
boundary (your components, hooks, the data-fetching client, the cache) run for real. Mocking *your
own* modules is where false confidence comes from.

```ts
// src/test/handlers.ts — shared between tests and (optionally) the dev/browser worker.
import { http, HttpResponse } from 'msw';
export const handlers = [
  http.get('/api/users/:id', ({ params }) =>
    HttpResponse.json({ id: params.id, name: 'Ada Lovelace' })),
];

// src/test/setup.ts
import { setupServer } from 'msw/node';
export const server = setupServer(...handlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' })); // an un-mocked call fails loudly
afterEach(() => server.resetHandlers());                          // per-test overrides don't leak
afterAll(() => server.close());
```

```tsx
// Per-test override to drive the error/empty states:
server.use(http.get('/api/users/:id', () => new HttpResponse(null, { status: 500 })));
render(<UserCard id="42" />);
expect(await screen.findByRole('alert')).toHaveTextContent(/couldn't load/i);
```

- **Why MSW over `vi.mock('fetch')` / stubbed `axios`:** intercepting at the network layer exercises
  your real request-building, response-parsing, error-normalization, and cache code. A stubbed `fetch`
  that returns a hand-built object skips all of that — the very code most likely to have the bug — and
  the same handlers can back the app in dev, so the mock and the real boundary stay in sync.
- **Don't stub child components** (`vi.mock('./Chart')`) to "simplify" a test. A test that renders a
  fake child proves the fake works, not the real tree; it goes green while the real child throws.
  Render the real children; only the network is faked.
- **Don't mock your own hooks/modules to inject state.** If you find yourself mocking `useUser` to
  return a fixed value, you're testing the mock. Make the hook fetch through MSW and assert the
  rendered result instead.
- **`onUnhandledRequest: 'error'`** turns an accidental real network call into a failed test rather
  than a silent hang — keep it on. (Determinism guarantees — clock, randomness — live in `flake.md`.)

---

## Testing hooks

A custom hook is logic, but most hooks exist to drive UI. Prefer the lighter approach that still
exercises the real behavior:

- **Test UI logic *through a component*.** If the hook's whole point is "click increments, renders the
  count," a small component test reads how the feature is used and survives refactors of the hook's
  internals. This is the default for anything that touches rendered output.
- **`renderHook` for genuinely standalone logic** — a `useDebouncedValue`, a reducer-style state
  machine, a hook with a non-trivial return API and no inherent markup. Drive updates inside `act`
  (state updates) and read `result.current`:

```tsx
const { result } = renderHook(() => useCounter(0));
act(() => result.current.increment());
expect(result.current.count).toBe(1);

// Hooks with context/query dependencies need their providers:
const wrapper = ({ children }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
);
const { result } = renderHook(() => useUser('42'), { wrapper });
await waitFor(() => expect(result.current.isSuccess).toBe(true));
```

- **Provide real providers, not mocked context.** A hook that reads React Query / a context store gets
  the actual provider in the `wrapper` (a fresh `QueryClient` per test so caches don't bleed), so
  you're testing it the way it runs.

---

## Component vs e2e split

Two tiers, chosen by what each can honestly verify — not by preference. Most behavior belongs in fast
component tests; a *few* journeys earn a real browser.

- **Component test (Vitest + jsdom):** one component or a small tree, network faked by MSW, runs in
  milliseconds. Owns rendering logic, interaction handling, the four states, conditional UI,
  form/validation behavior, hook logic. jsdom is *not* a real browser — it doesn't lay out, paint, or
  run real navigation — so it can't vouch for anything visual or cross-page (that's the boundary, and
  the *visual* side is ceded to craft-ux).
- **e2e (Playwright, real browser):** real rendering, real navigation, real network (or
  Playwright-level mocks), across pages. Reserve it for **critical end-to-end journeys** — sign up →
  verify → land on dashboard; add to cart → checkout → confirmation — where the value is precisely
  that all the real pieces connect.

**Playwright craft, briefly:**

- **Lean on web-first assertions + auto-waiting.** `await expect(page.getByRole('button', { name:
  /checkout/i })).toBeVisible()` retries until true — no manual `waitForTimeout`, the #1 source of
  e2e flake.
- **Role-based locators, same as component tests** — `page.getByRole`, `getByLabel`, `getByText`.
  Avoid CSS/XPath selectors that snap on the next refactor.
- **One robust journey beats twenty brittle ones.** e2e is slow and expensive to maintain; cover the
  one or two flows whose breakage means lost revenue, and push everything else down to component
  tests. (Root-causing the e2e flake that does occur: `flake.md`.)

---

## Accessibility in tests

You get most of this for free by querying by role and name — a control with no accessible name simply
isn't found, and the test fails. Make that signal explicit where it matters:

- **Assert roles and names directly** for key controls and structure:
  `expect(screen.getByRole('button', { name: /submit order/i })).toBeEnabled()`,
  `getByRole('navigation', { name: /breadcrumb/i })`. A missing/empty name surfaces here as a clear
  failure rather than a silent gap.
- **Optional `jest-axe` smoke check** for static violations (missing labels, bad ARIA, duplicate ids)
  on a rendered tree — cheap, catches the obvious:

```tsx
import { axe } from 'jest-axe';
const { container } = render(<Checkout />);
expect(await axe(container)).toHaveNoViolations();
```

- **This is the *programmatic* a11y layer only** — roles, names, ARIA wiring. The **rendered** audit —
  color contrast, focus-visible appearance, motion, touch-target size, actual layout — needs a real
  browser and belongs to **`craft-ux`** → `live-audit.md`. jest-axe in jsdom can't see contrast or
  layout; don't claim a11y coverage it can't provide.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Smell | Fix |
| --- | --- |
| `container.querySelector('.class')` / `getByTestId` as the default | Query by role + accessible name; testid is the last-resort escape hatch |
| `fireEvent.change/click` for user interaction | `await userEvent…` — real focus/key/input sequence |
| `userEvent` call without `await` | Await every `userEvent` call (it's async) |
| `await new Promise(r => setTimeout(r, …))` to wait for UI | `findBy*` / `waitFor` for the actual condition |
| Manual `act()` wrappers added to silence the act warning | Await the update (`userEvent`, `findBy*`, `waitFor`) instead |
| Only the data state tested | Cover loading, error, empty, and data |
| `vi.mock('fetch')` / stubbed axios returning hand-built objects | Intercept at the network with MSW; run the real client |
| Child component / own hook mocked to "simplify" | Render real children; fake only the network |
| MSW allowing unhandled requests through silently | `onUnhandledRequest: 'error'`; `resetHandlers` per test |
| `renderHook` for a hook whose purpose is rendered UI | Test it through a component |
| `renderHook` with mocked context instead of real providers | Wrap with the real provider; fresh `QueryClient` per test |
| UI assertion or visual check pushed into jsdom | Behavior → component test; visual/cross-page → Playwright / craft-ux |
| Playwright test with `waitForTimeout` / CSS selectors | Web-first `expect().toBeVisible()` + role locators |
| Twenty brittle e2e specs covering edge cases | One critical journey e2e; edges in component tests |
| Claiming a11y coverage from jest-axe alone | Assert roles/names; cede contrast/layout/motion to craft-ux |

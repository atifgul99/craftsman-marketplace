# Component Architecture

How to shape a component so it stays sound as the app grows — sized sanely, reusable, with an
interface a teammate can guess, extendable without forking, and clear of the React-correctness traps
that survive a happy-path demo and surface in production.

> Scope split: this file owns the *application-layer* component contract. Visual polish, design
> tokens, variant/size styling (CVA), and per-component UX patterns (forms, tables, modals) belong
> to **`craft-ux`** — cross-reference it whenever both concerns appear. Rendering untrusted data is
> **`craft-security`** (`references/input-output.md`).

> **See also:** `state.md` (where state lives) · `data-fetching.md` (loading/error/empty co-located
> with the fetch) · `forms.md` · `performance.md` (the runtime/perf side of the same components).

---

## Contents

- [Boundaries: server vs client, container vs presentation](#boundaries)
- [Size & single responsibility](#size--single-responsibility)
- [Reusable by construction](#reusable-by-construction)
- [Interface: make it guessable](#interface-make-it-guessable)
- [Extendable without forking](#extendable-without-forking)
- [React correctness](#react-correctness)
- [Next.js file conventions](#nextjs-file-conventions)
- [Consent before tracking](#consent-before-tracking)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Boundaries

Decide the composition shape *before* writing the component — retrofitting a boundary is a rewrite.

- **Server vs client.** Default to server-rendered; add `"use client"` only at the leaf that
  genuinely needs interactivity (state, effects, event handlers, browser APIs). `"use client"` marks
  the client *module boundary* — that module and everything it imports ship in the client bundle and
  evaluate on the client (you can still pass Server Components *through* it as `children`). Push the
  boundary down to the smallest island so you don't drag the subtree's code into the client bundle.
- **Container vs presentation.** Keep the component that *fetches/owns data* separate from the one
  that *renders it*. The presentation component takes props and is pure — that's the one you can
  reuse, test, and preview in isolation. The container wires it to the query cache, router, or store.
- **Co-locate, then lift.** Start a component next to its only caller. Promote it to a shared
  location only when a second caller actually appears — premature sharing couples two features
  through a component neither fully owns.

---

## Size & single responsibility

A component does one job. When it starts doing several — fetching data, owning layout, *and*
rendering a row's worth of fields — split it. Reliable signals it has outgrown one job:

- It's past ~150–200 lines, or you have to scroll to hold it in your head.
- It mixes **data-fetching** with **presentation** (see Boundaries) — lift the fetch out.
- It carries many `useState`s tracking unrelated concerns, or a `useEffect` doing three things.
- A prop only matters in one branch and flips whole layouts (`isModal`, `isCompact`) — that's two
  components wearing a trench coat. Split them and let each render its own layout.

Smaller is not automatically better: extracting a one-line wrapper used once adds indirection for
nothing. Split when a piece is **reused, independently testable, or independently complex** — not on
line count alone. (Same judgment system-wide: promote to a *shared* component at 3+ usages, not on
first sight — duplication is cheaper than the wrong abstraction.)

---

## Reusable by construction

Reusable means **decoupled from where it's used**. The test: could this drop into another page — or
another product — without dragging its surroundings along?

- **Inject dependencies; don't import them ambiently.** A reusable component takes data as props or
  via an explicit hook arg, rather than reaching into a global singleton (a specific store slice,
  the router, `window`) for it.
- **Communicate up via callbacks** (`onSelect`, `onSubmit`) — don't mutate shared state the parent
  also writes. One-way data flow is what makes a component's behavior predictable from its props.
- **No hardcoded copy, URLs, or business rules** baked into a "reusable" component — those are props
  or config, or it isn't reusable. (User-facing strings also go through the i18n layer.)
- **Compose what exists.** Domain components build on the repo's primitives and base library — they
  don't reinvent a `Button` or `Dialog` the project already ships. Discover before you build.

---

## Interface: make it guessable

A good component API is one a teammate uses correctly *without reading the source*. That means
leaning on conventions the platform and ecosystem already trained everyone on:

- **Extend the native element's props; don't reinvent them.** A button is
  `React.ComponentPropsWithoutRef<"button"> & { variant?: … }`, so `type`, `disabled`, `onClick`,
  and `aria-*` all just work — then spread `...rest` onto the root node. Inventing `onPress` for
  `onClick` or `text` for `children` forces every caller to relearn your dialect.
- **Use `children` for content;** reserve named props for genuinely separate slots (`header`,
  `footer`, `icon`, `actions`). Passing renderable content as a `content` string is a smell.
- **Variants are closed sets, not boolean piles.** `variant="destructive"` / `size="sm"` beats
  `isPrimary` + `isDestructive` + `isSmall` booleans that permit nonsense combinations. (The CVA
  styling mechanics for this live in `craft-ux` → `layer-2-primitives.md`.) For multi-part widgets,
  prefer **compound components** (`<Tabs><TabsList><TabsTrigger/>…`) over one giant prop object —
  the composition mechanics live in `craft-ux` → `layer-2-primitives.md`.
- **Controlled vs uncontrolled — pick a lane and honor React's contract.** If you accept `value`,
  also accept `onChange`; offer `defaultValue` for the uncontrolled case. Never let a field flip
  between the two at runtime — React warns and the input loses state/cursor.
- **Sensible defaults.** The component renders correctly with the minimum props; optional props
  refine it. If three props are required before it renders without crashing, the API is too raw.
- **Name for intent, type honestly.** Booleans read as `isLoading`/`disabled`; handlers as `onX`.
  No `any` on the public surface — the prop types *are* the documentation, and a precise type
  prevents a class of caller bugs the linter would otherwise miss.

---

## Extendable without forking

Callers will always need one more tweak. Give them seams so they override instead of copy-pasting a
whole variant:

- **Accept `className`** and merge it through `cn()` (tailwind-merge) so the caller's classes win
  conflicts. A component that ignores `className` forces a fork for every visual variation. (Helper:
  `craft-ux` → `layer-2-primitives.md`.)
- **Forward refs** (`forwardRef`, or `ref` as a regular prop in React 19) so parents can focus,
  measure, scroll to, or attach behavior — focus management and popover/tooltip anchoring depend on
  the ref reaching the real DOM node.
- **Offer a slot escape hatch** for composition-heavy primitives — Radix's `asChild` / `Slot` lets a
  caller swap the rendered element (render a link styled as a button) without you adding a new prop
  for every case.
- **Prefer open composition over configuration.** A `<Card>` that takes `children` outlives a
  `<Card>` with twenty layout props: the next layout need is a new child, not a new prop *and* a new
  branch inside the component.

---

## React correctness

The runtime bugs that pass a demo and bite in production:

- **Stable, identity-based list `key`s** — a stable id from the data, never the array index for
  lists that reorder, filter, or delete. Index keys make React reuse the wrong DOM node, corrupting
  local state and input values. Keys are how React tracks identity across renders.
- **Don't mirror props into state.** `useState(props.x)` + a `useEffect` to "keep it in sync" causes
  stale renders and double paints. Derive during render instead; to *reset* state when an input
  changes, give the subtree a `key` and let React remount it.
- **Effects synchronize with the outside world** (subscriptions, DOM measurement, non-React
  widgets) — they are not for reacting to a click or transforming props. That logic belongs in the
  event handler or in render; if there's nothing external to synchronize, you probably don't need an
  effect at all. An effect that *sets up* an external resource must return the symmetrical cleanup
  (listeners, timers, connections) — otherwise it leaks and double-fires under Strict Mode.
- **Wrap risky subtrees in an error boundary** so one component's throw degrades to a fallback
  instead of blanking the page. Pair the boundary with a real error state (see `craft-ux` →
  `layer-4-states.md`), and reset it on navigation. Concrete reset patterns by router:
  - **Next.js App Router** — wrap the relevant segment's content in a component that receives a
    `key` derived from `usePathname()`. When the route changes, React remounts the subtree, clearing
    the errored boundary automatically: `<ErrorBoundaryWrapper key={pathname}>…</ErrorBoundaryWrapper>`.
  - **react-error-boundary** — pass `resetKeys={[pathname]}` (from `useLocation` or
    `usePathname`) so the library resets the boundary whenever the path changes, without a full
    remount of the surrounding tree.
- **Memoize to fix a *measured* cost.** `useMemo`/`useCallback`/`React.memo` earn their place when
  the profiler shows a real re-render or expensive compute — applied prophylactically they add
  complexity and stale-closure risk for no payoff. Measure first (React DevTools profiler), and see
  `performance.md`.

---

## Next.js file conventions

The App Router dispatches on reserved file names inside a route segment:

- **`layout.tsx`/`.js`** — shared UI that wraps a segment and its children; persists across
  navigations within the segment (state isn't reset on route change).
- **`page.tsx`/`.js`** — the unique UI for a segment; makes the route publicly reachable.
- **`loading.tsx`/`.js`** — an instant loading UI shown while the segment's data/render is
  pending; wraps the segment in a `<Suspense>` boundary automatically.
- **`error.tsx`/`.js`** — a client-side error boundary for the segment; catches render/runtime
  errors below it and shows a recoverable fallback (must be a Client Component).
- **`route.ts`/`.js`** — a Route Handler (API endpoint) for the segment; mutually exclusive with
  `page.tsx` in the same segment.

**Middleware rename in Next.js 16:** `middleware.ts` was renamed to `proxy.ts`. `middleware.ts`
still works in Next 16 but emits a deprecation warning — it is not itself an error. Do **not**
flag `proxy.ts` as a "misnamed file" on Next 16+; it's the correct name there. Always check the
project's installed Next.js major version (`package.json` / lockfile) before flagging either name
as wrong in either direction.

**Verify against the changelog.** These conventions change between major versions — confirm
file-naming expectations against the official Next.js changelog for the project's installed major
before flagging a naming issue in review.

---

## Consent before tracking

Where consent law applies (GDPR/ePrivacy in the EU, similar regimes elsewhere), analytics and
tracking scripts (Google Analytics, Meta Pixel, PostHog, etc.) must not fire before the user
consents. This is a client-boundary problem, not a copy problem — it's about where the script is
injected in the component tree and what gates its initialization.

- **The common bug:** gating only the banner's *visibility* while the tracking script itself loads
  and initializes on page mount regardless of consent state. Hiding the UI doesn't stop the
  `<script>` tag or SDK init call underneath it from running.
- **The fix:** gate the actual script injection/initialization call on the consent state — load the
  script (or call its `init()`) only after consent is granted, not unconditionally at mount with the
  banner merely rendered on top.
- **How to verify:** load the page fresh (incognito or cleared cookies) and watch the Network tab.
  Any tracker request firing before you interact with the consent UI is the bug above.
- **See also:** `craft-ux` for the consent banner's UI itself — presence, and the "decline as easily
  as accept" pattern. That's the visible surface; this section owns whether the tracking actually
  waits for it.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Pattern                                                       | Fix                                                          |
| ------------------------------------------------------------ | ----------------------------------------------------------- |
| `"use client"` at the top of a large tree                    | Push it down to the interactive leaf                        |
| Data fetch tangled into a presentation component             | Lift fetch to a container/route; keep the renderer pure     |
| God-component (>~200 lines, multiple unrelated `useState`)    | Split by responsibility                                     |
| Boolean prop pile (`isPrimary`+`isDestructive`+`isSmall`)     | Closed-set `variant`/`size`                                 |
| Custom prop names shadowing native ones (`onPress`, `text`)   | Extend native element props; use `onClick`/`children`       |
| `value` without `onChange` (and no `defaultValue`)           | Honor the controlled/uncontrolled contract                  |
| Component ignores `className` / doesn't forward `ref`        | Accept `className` via `cn()`; `forwardRef` (React ≤18) or plain `ref` prop (React 19+) |
| Array index as `key` on a reorderable/filterable list        | Stable id from the data                                     |
| `useState(prop)` + `useEffect` to sync                       | Derive in render, or remount via `key`                      |
| Effect used to handle an event or transform props            | Move to the handler / compute in render                     |
| `useMemo`/`memo` with no measured cost                       | Remove until the profiler justifies it                      |
| Tracking script loads unconditionally on page mount before consent captured | Gate script injection/init on consent state; verify via Network tab |

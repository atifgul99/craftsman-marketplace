# State

Where a piece of state lives decides how many bugs it can cause. The job here: put each kind of
state at the *lowest* scope that still works, keep **server data out of client stores**, and stop
storing anything you can derive. State that lives too high re-renders too much; state duplicated
across a cache and a store drifts.

> Scope split: this file owns *where state lives and what shape it takes* at the application layer.
> The container-vs-presentation split that isolates state from rendering is framed in
> **`architecture.md`**; the **re-render cost** of placing state too high is covered here and in
> **`performance.md`** — this file goes deeper on the placement decision.
> The **query cache mechanics** (keys, dedupe config, invalidation, prefetch) live in
> **`data-fetching.md`** — this file decides *that* server data belongs in a cache, not *how* to wire
> one. URL-state that drives a *view* (filters, tabs, pagination) is here; the accessibility and
> visual treatment of the filter/tab controls that set it belong to **`craft-ux`** primitives,
> and reviewers flag URL-state regressions via `craft-ux` → `review-protocol`.

> **See also:** `architecture.md` (container vs presentation) · `performance.md` (re-renders from
> over-lifted state) · `data-fetching.md` (the query cache) · `forms.md` (form state is its own
> scope).

---

## Contents

- [Classify the state first](#classify-the-state-first)
- [The escalation ladder](#the-escalation-ladder)
- [Server state ≠ client state](#server-state--client-state)
- [Derived state: compute, don't store](#derived-state-compute-dont-store)
- [URL as state](#url-as-state)
- [Context's re-render cost](#contexts-re-render-cost)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Classify the state first

Most "state management" arguments are really a missing taxonomy. Before placing anything, name what
kind it is — each kind has a *different* home:

| Kind | Examples | Home |
| --- | --- | --- |
| **Server / remote** | fetched lists, the current user *object/profile*, anything with a source of truth on a server | A query cache (`data-fetching.md`) |
| **URL / navigation** | active filters, tab, page number, sort, selected id | The URL (search params / route) |
| **Local UI** | open/closed, hovered, input-in-progress, focused index | `useState`/`useReducer` in the owning component |
| **Shared client** | theme, locale, a cross-page wizard, UI preferences | Lifted state → Context → external store, in that order |
| **Derived** | filtered/sorted view, totals, `isValid`, `fullName` | Nothing — compute in render from the above |

The single most common mistake is treating server data as shared client state and copying it into a
store. The second is treating derived data as state and storing it. Both are covered below.

> **Session/access tokens are a special case — not a value to park in a store.** Prefer an httpOnly
> cookie so JS (and therefore XSS) can't read the token and the browser attaches it for you. If a
> token *must* live in JS, keep it in memory only and never persist it to a store or `localStorage`.
> The user's *profile/object* is server state (query cache); only the raw token — if held in JS at
> all — is shared client state, and it stays out of any JS-readable store.

---

## The escalation ladder

Climb only as far as a concrete need forces you. Each rung adds reach and cost; stopping early keeps
state local, testable, and cheap to re-render.

1. **`useState` / `useReducer` — local.** Default. If one component owns it and no one else reads it,
   it stays here. Reach for `useReducer` when several values update together or transitions have
   rules (a wizard, a multi-field toggle) — one reducer beats five `setState` calls that must stay
   consistent.
2. **Lift to the nearest common parent.** When *two siblings* genuinely share a value, move it to
   their closest shared ancestor and pass it down. Lift to the **nearest** common parent — not the
   page root. State parked higher than its consumers re-renders subtrees that don't care (see
   `performance.md`).
3. **Context — for *truly* tree-wide, *low-frequency* values.** Theme, locale, stable auth/session
   status, a static feature-flag bag. (The current-user *record* is server state — cache it; share
   only the stable session status here.) Context solves prop-drilling, not performance: every
   consumer re-renders when
   the value's identity changes (React compares with `Object.is`), so it's a poor fit for values that
   update often (see below).
4. **External store (Zustand / Jotai / Redux) — last resort.** Justified when client state is
   genuinely global, updates frequently, *and* needs fine-grained subscriptions so unrelated
   consumers don't re-render — or when logic must live outside the React tree. If you only have
   prop-drilling, you need composition or Context, not a store.

> Discover before adding a rung: check `package.json` for an existing store/Context convention and
> extend it. Don't introduce Redux into a Zustand repo (or any store into a repo that hasn't needed
> one) to solve a two-component sharing problem.

**Often you don't need any rung — restructure instead.** Prop-drilling through many layers is
frequently a composition problem: pass the rendered subtree as `children` so the data-owning parent
renders it directly, and the intermediate layers never see the prop (composition patterns —
children/slots, compound components — live in `architecture.md`).

---

## Server state ≠ client state

Remote data is **not** owned by your app — it's a cached snapshot of something a server owns. That
changes everything about how it should live:

- **Put it in a query cache** (TanStack Query, SWR, RTK Query — whatever the repo uses). You get
  request **dedup**, **background refetch**, **stale-while-revalidate**, retry, and per-query
  loading/error status for free. Mechanics: `data-fetching.md`.
- **Do not mirror server data into a Zustand/Redux slice.** The moment you `setUser(data)` into a
  store after a fetch, you own two copies that drift: cache invalidation no longer reaches the store,
  two components read different "truths", and you hand-roll the refetch/staleness logic the cache
  already ships. A store slice that exists only to hold the result of a fetch is the smell.
- **Cache *is* the global read layer for server data.** Any component can call the same `useQuery`
  with the same key and read one deduped result — that already gives you the "global access" a store
  was being reached for, without a second source of truth.
- **Legitimate overlap is small and explicit.** Client state *derived from* a server fetch (e.g. a
  draft the user is editing, seeded once from server data) is real client state — own it locally and
  treat the server copy as the baseline to diff against, not a value to keep re-syncing via effects.

This is the skill's standing opinion: *server state lives in a query cache, not a global store.*

---

## Derived state: compute, don't store

If a value can be calculated from existing state/props, it is **not** state — calculate it during
render. Storing it adds a synchronization burden you will eventually get wrong.

- `const visible = items.filter(matchesQuery)` — compute in render, don't keep a `visibleItems`
  state updated by an effect. A derived `useState` + `useEffect` to sync is the canonical stale-data
  bug (also in `architecture.md` → React correctness).
- Same for `total`, `fullName`, `isValid`, `selectedItem` (look it up from `selectedId` + the list).
  Storing the derived copy means every source change needs a matching write — miss one and the UI
  lies.
- **Reach for `useMemo` only when the computation is *measurably* expensive** or its identity feeds a
  dependency array — not by default. Cheap derivations (a filter over a few hundred rows) are fine
  raw; memoizing them adds cache overhead and stale-closure risk for no win. Measure first (React
  DevTools profiler) — see `performance.md`.
- Store the **minimal source**: keep `selectedId`, derive `selectedItem`; keep `sortKey`, derive the
  sorted array. Less stored state means fewer ways to be inconsistent.

---

## URL as state

View state that someone might **share, bookmark, deep-link, or reload into** belongs in the URL, not
in `useState`. If pasting the link in a new tab should reproduce the screen, the state is a URL
concern.

- **Belongs in the URL:** active filters, search query, current tab, page/offset, sort order,
  expanded panel, the selected entity's id. These survive refresh, are shareable, and play correctly
  with the browser's back/forward.
- **Stays out of the URL:** transient/local UI (hover, dropdown-open, in-progress text before
  submit) and anything sensitive — URLs leak into history, logs, and analytics.
- **Use the router's typed search-param helpers** rather than hand-parsing `location.search`. With a
  helper like **nuqs** you bind a param to a typed, serialized value with a default
  (`useQueryState('tab', …)`), so it reads like `useState` but the URL is the source of truth. Match
  the repo's router (Next.js `useSearchParams`/`searchParams`, TanStack Router's typed search, React
  Router loaders) — discover, don't impose nuqs on a repo that already has a convention.
- **The URL is the source of truth; don't also copy it into local state** and sync the two — that
  reintroduces the same drift as the server-state case. Read from the URL, write to the URL.
- **Keep the serialized form lean.** Map to short, stable param names; default values shouldn't be
  written to the URL (a clean default URL stays shareable). Reviewers flag missing/janky URL-state
  via `craft-ux` → `review-protocol`; the visual/a11y treatment of the filter/tab controls that set
  these params is covered under `craft-ux` primitives.

---

## Context's re-render cost

Context is for distribution, not performance. **Every consumer of a Context re-renders whenever the
provider's `value` changes identity** — and a fresh object/array literal in the provider changes
identity on *every* parent render. Two mitigations, both about narrowing what changes:

- **Split contexts by change frequency.** Don't put a rarely-changing value and a frequently-changing
  one in the same provider — a theme change shouldn't re-render everything reading the live mouse
  position. Split into separate providers (or a value context + a dispatch context, since the
  `dispatch` function is stable and its consumers never need to re-render on state change). Wrap the
  `value` in `useMemo`/stable refs so its identity only changes when the data does.
- **Pass `children` through the provider** so the expensive subtree is created by an *outer* parent
  and merely *slotted in*. Because that subtree's element identity is stable across the provider's
  re-renders, React skips re-rendering it even when the provider itself re-renders — only true
  consumers update. This is the same composition move that dissolves prop-drilling on the ladder.
- **If you're fighting Context re-renders with heavy memoization, you've outgrown it** — that's the
  fine-grained-subscription case an external store (Zustand/Jotai selectors) is actually for. Don't
  bolt a store on for prop-drilling; do reach for one when the *update pattern* genuinely needs
  per-selector subscriptions.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Server data copied into a Zustand/Redux slice after fetch | Keep it in the query cache; read via the hook (`data-fetching.md`) |
| `useState` + `useEffect` to derive a value from other state/props | Compute in render; memoize only if measured |
| State lifted to the page root but consumed two levels down | Lift to the *nearest* common parent — over-lifting re-renders subtrees that don't care (`performance.md`) |
| New external store added to solve plain prop-drilling | Use composition (`children`) or Context first |
| Filters/tab/page/sort kept in `useState`, lost on refresh | Move to URL via the router's typed search-param helper |
| URL copied into local state and synced both ways | URL is the source of truth — read/write it directly |
| Frequently-changing value sharing a Context with a static one | Split contexts by change frequency; split value/dispatch |
| Context `value={{ ... }}` object literal recreated each render | `useMemo` the value (or pass `children` through) |
| Sensitive/secret data placed in URL params | Keep it in memory/local state, never the URL |
| `useReducer`/store reached for a single boolean toggle | `useState` local — climb the ladder only when forced |

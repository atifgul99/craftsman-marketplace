---
name: craft-frontend
description: >-
  The Craftsman standard for frontend application architecture — components, state management, data
  fetching, forms, routing, client/server boundaries, performance, error boundaries, and bundle
  size. Use this WHENEVER the work touches the application layer of a frontend: building or
  reviewing components, wiring up API calls, deciding where state lives, handling loading/error/
  empty states, managing form validation, splitting bundles, or diagnosing slow pages. Trigger even
  when the user only says "wire up the API", "this page is slow", "manage this state", or "build
  the form" without naming a framework. NOTE: this skill covers the application-architecture layer
  (data, state, performance) — visual polish, design-system tokens, and layout decisions belong to
  craft-ux; the server/API implementation, authentication, and DB belong to craft-backend,
  craft-security, and craft-db (this skill owns the client side of the contract). Cross-reference
  those whenever both concerns appear in the same task.
---

# Frontend Craft

This skill encodes one engineer's standard for structuring frontend application code, applied the
same way across every repo. The **method and opinions** live here; the **project specifics**
(which framework, which data library, which router) are discovered from the repo — never hardcoded
or assumed.

## Operating principle — discover before you build

Different repos already have different conventions. Before adding anything, spend two minutes
mapping what exists so you extend rather than duplicate:

- `package.json` / lockfile → which framework (Next.js, React, Vue, Remix)? Which data layer
  (`@tanstack/react-query`, `swr`, RTK Query)? Which form lib (`react-hook-form`, Formik)? Which
  state approach (Zustand, Jotai, Context, URL-as-state)?
- `grep` for an existing API client, query key factory, or base hook — wire into it, don't fork it.
- Find the routing convention (file-based, config, nested layouts) and the client/server split
  strategy before deciding where new code lives.

State what you found, then propose the smallest set of additions that closes the gap.

## The frontend layers (build in this order)

1. **Component architecture** — decide the composition shape first: where are the boundaries,
   what is server-rendered vs client-interactive, what gets co-located vs shared. Composition over
   configuration: a component that accepts children and slots is more reusable than one with 20
   props. See `references/architecture.md`.

2. **State** — start local (`useState`), lift only when two siblings genuinely share it, reach for
   a global store only as a last resort. Server state (remote data) belongs in a query cache, not a
   store. See `references/state.md`.

3. **Data fetching** — use a typed client that matches the repo's existing pattern. Every fetch
   needs a loading state, an error state, and an empty state, all co-located with the component
   that owns the data. Avoid waterfall fetches: parallelize or prefetch where the router allows.
   See `references/data-fetching.md`.

4. **Forms** — validate with a schema library (Zod-style), couple it to the form hook, surface
   errors accessibly next to the field that owns them. Optimistic updates are worth it when the
   action is frequent and the rollback is cheap. See `references/forms.md`.

5. **Performance** — code-split at route boundaries by default, lazy-load heavy components, keep
   the critical path lean. Reach for memoization only after measuring; premature optimization makes
   code harder to read without a proven payoff. See `references/performance.md`.

## Standing opinions (the non-negotiables)

These are the judgments that keep output consistent across repos — apply them unless the user
overrides:

- **Server state lives in a query cache, not a global store.** A cache (React Query-style is the
  opinion when applicable) gives you deduplication, background refresh, and stale-while-revalidate
  for free — **discover the repo's actual data layer first** and extend it; don't bolt on React Query
  beside an established SWR/RTK Query/server-loader pattern. A Zustand slice that manually mirrors
  server data gives you bugs.
- **Forms are schema-validated with accessible errors.** Define the shape once (Zod or equivalent),
  derive both the TypeScript type and the runtime validation from it, and render error messages
  adjacent to the field so screen readers find them.
- **No fetch waterfalls.** If two data dependencies are independent, fetch them in parallel.
  Co-locate the fetch with the component that renders it; don't hoist data to a parent just to
  pass it down.
- **Every async UI has explicit loading, error, and empty states.** A spinner that hides the rest
  of the page is a loading state. A blank div when the list is empty is not an empty state — it is
  a confusing silence.
- **Measure before optimizing.** Lighthouse, bundle analysis (`next build` output, `rollup-plugin-
visualizer`), and React DevTools profiler are the sources of truth. Gut feeling is a hypothesis,
  not a reason to add `useMemo`.

## Workflow

1. **Discover** the current state (framework, data layer, conventions) and report what exists.
2. **Propose** the implementation, ordered by the five layers above, smallest viable first.
3. **Implement** against the repo's existing patterns — its query client, its API conventions,
   its form library, its routing approach.
4. **Verify** — run the app, exercise the happy path, the error path, and the empty path. A
   component you haven't seen render in all three states is not done.

## Reference index

Read the one matching the current task — they hold the concrete patterns, not this overview:

- `references/architecture.md` — component boundaries, composition patterns, server vs client split
- `references/state.md` — local state, lifting, query cache vs global store, URL-as-state
- `references/data-fetching.md` — typed clients, query key factories, parallel fetching, caching
- `references/forms.md` — schema validation, form hooks, accessible errors, optimistic updates
- `references/performance.md` — code splitting, lazy loading, bundle analysis, memoization rules
- `references/testing.md` — renderWithClient wrapper, user-event for RHF forms, MSW v2 mocking, co-location

## Audit checklist (for craft-audit)

When `craft-audit` plans a frontend pass for a scope, it turns this checklist into the `plan.md`
todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor to what
discovery found: skip a step that genuinely doesn't apply with a one-line reason; never silently drop
one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission format"
(authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-FE-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-FE-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Confidence:**` — `verified | inferred | unverified-from-repo`, absent
means `verified` — then optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] Map the repo's existing stack before judging anything — framework, data/cache lib, form lib,
      state approach, router; flag new patterns bolted on beside an established convention → SKILL.md
      (Operating principle)
- [ ] Audit component boundaries — `"use client"` at the top of a large tree, data fetching tangled
      into presentation components, god-components, boolean-prop piles, custom names shadowing native
      props, index keys on reorderable lists → `references/architecture.md`
- [ ] Check state placement — server data mirrored into a Zustand/Redux store, derived values stored
      with a `useState`+`useEffect` sync, state over-lifted, filters/tab/sort lost on refresh
      → `references/state.md` (secrets/tokens in URL params is a security finding — flag it and
      route to craft-security; `references/state.md` covers the state-placement side only)
- [ ] Filters, pagination, tabs, and sort order are stored in URL params (not `useState`), so deep
      links and back-nav work correctly → `references/state.md` (URL as state)
- [ ] Review data fetching — raw inline `fetch`/unvalidated responses, ad-hoc scattered query keys,
      a result-affecting variable missing from the key, sequential `await`s or structural waterfalls,
      `staleTime` left at `0` for stable data → `references/data-fetching.md`
- [ ] Verify every async UI has explicit loading, error, AND empty states co-located at the fetch
      site — a blank div for empty is a bug; one slow widget shouldn't blank the page → `references/data-fetching.md`
- [ ] Inspect mutations — `setQueryData` with no `onError` rollback, optimistic updates on
      destructive/irreversible actions, screens showing stale data because the touched key prefix was
      never invalidated → `references/data-fetching.md`
- [ ] Audit forms — hand-written types parallel to the schema, validation in handler `if`s, errors
      firing on every keystroke, submit disabled before any attempt or not disabled in-flight, server
      trusting client-validated input → `references/forms.md`
- [ ] Check form error accessibility — error text with no `role="alert"` region or
      `aria-describedby`/`aria-invalid` wiring, first invalid field not focused on submit, server
      errors swallowed to console → `references/forms.md`
- [ ] Review performance against measurement — heavy leaf components not code-split at route
      boundaries, >~20 KB deps on the critical path, prophylactic `useMemo`/`memo` with no profiled
      cost, layout reads in render → `references/performance.md`
- [ ] Run bundle analyzer (`next build --analyze` or `source-map-explorer`) and Lighthouse (throttled
      network) — record an actual number for LCP and bundle size; pattern-checking without measurement
      is not sufficient → `references/performance.md`
- [ ] Component tests use `renderWithClient` and `userEvent`; API calls are mocked with MSW
      → `references/testing.md`
- [ ] Tracking/analytics scripts (GA, Meta Pixel, PostHog, etc.) are gated on consent state, not
      just the consent banner's visibility — verify with a fresh-load (incognito/cleared cookies)
      Network tab check for tracker requests before any consent interaction → `references/architecture.md`


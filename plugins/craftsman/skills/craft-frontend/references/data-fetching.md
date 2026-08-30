# Data Fetching

How to move remote data into the UI so it stays correct as the app grows — typed at the edge,
cached under stable identities, parallelized instead of waterfalled, and co-located with the
component that renders it, each with its loading, error, and empty state. The **method** is here;
*which* client and cache library you use is discovered from the repo, never assumed.

> Scope split: this file owns the *fetch-and-cache* layer — clients, query keys, parallelization,
> caching/invalidation, mutations. **Where data lives once fetched** (server-vs-client state, the
> "no server data in a global store" rule) is **`state.md`**. **Mutations driven by a form** (schema,
> submit wiring, accessible errors) are **`forms.md`** — this file owns the cache write, that one owns
> the input. **Component/container boundaries** are **`architecture.md`**. The **visual** loading /
> empty / error treatments belong to **`craft-ux`** → `layer-4-states.md` — reference it, don't
> reinvent the markup here.

> **See also:** `state.md` · `forms.md` · `architecture.md` · `performance.md`
> (prefetch/code-split interplay) · `craft-backend` for the API contract on the other side.

---

## Contents

- [Discover first](#discover-first)
- [Typed client at the edge](#typed-client-at-the-edge)
- [Query-key factory](#query-key-factory)
- [No waterfalls: parallelize & prefetch](#no-waterfalls-parallelize--prefetch)
- [Co-locate the fetch; three states each](#co-locate-the-fetch-three-states-each)
- [Caching, staleness, dedup, invalidation](#caching-staleness-dedup-invalidation)
- [Mutations & optimistic updates](#mutations--optimistic-updates)
- [React 19 use() hook](#react-19-use-hook)
- [Suspense vs imperative states](#suspense-vs-imperative-states)
- [Pagination & infinite queries](#pagination--infinite-queries)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Discover first

Before adding a fetch, map what the repo already does — extend it, don't fork a parallel stack.

- **Lockfile / `package.json`** → which cache lib (`@tanstack/react-query`, `swr`, RTK Query), or is
  data fetched in a server framework (Next.js Server Components / `loader`s in Remix/React Router)?
- **`grep`** for an existing API client, base `fetch` wrapper, generated SDK (OpenAPI/GraphQL
  codegen), or a `queryKeys`/key-factory module — wire into it.
- Note the **boundary**: server-framework data loading (RSC, route loaders) and client-cache hooks
  (`useQuery`) coexist; know which side a given screen renders on before choosing.

State what you found, then add the smallest piece that closes the gap.

---

## Typed client at the edge

Types belong at the network boundary, so every consumer downstream is typed for free.

- **Match the repo's pattern.** If there's a generated SDK (OpenAPI/GraphQL codegen, tRPC), use it —
  hand-typed `fetch` next to a generated client is drift waiting to happen.
- **Validate untrusted responses at the edge** when the payload isn't already guaranteed by a typed
  RPC. A network response is `unknown`; a hand-written `as Response` interface is a lie the compiler
  can't catch. Parse with the repo's schema lib (Zod-style) so a contract change fails loudly at the
  boundary instead of as `undefined.map` three components deep. (Skip the runtime parse where the
  transport already gives you an end-to-end-inferred type from shared server code (e.g. tRPC) — the
  runtime risk is low, don't pay twice. Note tRPC infers output types but only runtime-validates them
  if you define an `output` schema.)
- **One client, centrally configured** — base URL, auth header, error normalization, JSON parsing in
  one module. Per-component `fetch('/api/...')` calls scatter auth and error handling and can't be
  swapped or mocked in one place.
- **Normalize errors into a typed shape** (status + code + message) so UI can branch on `401` vs
  `404` vs `500` instead of string-matching. The cache lib only knows "it threw" — give it something
  meaningful to throw.

---

## Query-key factory

The cache key *is* the data's identity. Hand-built key arrays scattered across files drift, and a
mismatched key silently breaks invalidation (the mutation succeeds, the screen shows stale data).

- **Centralize keys in a factory** so there's one source of truth per resource and keys are
  hierarchical for partial invalidation:

  ```ts
  export const userKeys = {
    all: ['users'] as const,
    lists: () => [...userKeys.all, 'list'] as const,
    list: (filters: UserFilters) => [...userKeys.lists(), filters] as const,
    details: () => [...userKeys.all, 'detail'] as const,
    detail: (id: string) => [...userKeys.details(), id] as const,
  };
  ```

- **Every variable that changes the result goes in the key** — filters, pagination, sort, the
  resource id, and any auth/tenant scope. Omitting one means two different results collide under one
  key (you see another user's data); adding a noise field that doesn't affect the result fragments the
  cache for nothing.
- **Hierarchy enables surgical invalidation.** `invalidateQueries({ queryKey: userKeys.lists() })`
  refetches every list variant without touching detail caches. (SWR's analog is the key string /
  matcher passed to `mutate` — same discipline, different surface.)
- **Keys must be serializable and order-stable.** Object key order is fine for React Query (it
  hashes deterministically), but don't put functions or class instances in a key.

---

## No waterfalls: parallelize & prefetch

A waterfall is request B waiting on request A only because of how the code is *written*, not because
B needs A's result. Each hop adds a full round-trip of latency the user feels.

- **Independent requests run in parallel.** Two `useQuery` calls in the same component already fire
  concurrently — that's the default, keep it. For imperative fetches, `Promise.all` instead of
  sequential `await`s. Only chain when B genuinely needs A's output (`enabled: !!a` for the
  dependent query).
- **Hoist the dependency, don't serialize the render.** If a child fetches with an id the parent
  computed, the child's request can't start until the parent renders — a structural waterfall. Fetch
  both at the boundary, or prefetch the child's data, so they overlap.
- **Prefetch at the router.** Kick off the query before the component mounts — on link hover/intent,
  in a route loader (Remix/React Router), or `queryClient.prefetchQuery` in a Next.js Server
  Component / `loader`. The data is warming while the bundle and the next paint are still in flight.
- **In RSC / loaders, parallelize there too** — `Promise.all` of independent loads, or start promises
  before `await`ing, so server-side fetches don't waterfall either. (Code-split/route-prefetch
  interplay lives in `performance.md`.)

---

## Co-locate the fetch; three states each

The component that *renders* the data owns the query for it. Don't hoist data to a parent purely to
prop-drill it down — that recreates a waterfall and couples siblings.

- **One query, next to its renderer.** A reusable cache (dedup, below) means two components asking
  for the same key don't double-fetch — so co-location costs nothing and keeps each screen's data
  needs legible. (Container/presentation split: `architecture.md`.)
- **Loading, error, AND empty — every async UI, every time.** "Empty" (a successful response with
  zero rows) is a distinct state from loading and from error; a blank div is a bug, not an empty
  state. The *visual* treatment of each — skeletons vs spinners, error copy, empty-state CTA — is
  owned by **`craft-ux`** → `layer-4-states.md`; this file's rule is only that all three exist and
  are handled at the fetch site.
- **Don't strand a partial failure.** When a page has several independent queries, let each render its
  own state so one slow/failed widget doesn't blank the whole page (pair with an error boundary —
  `architecture.md`).

---

## Caching, staleness, dedup, invalidation

The cache library earns its place by giving you dedup, background refresh, and
stale-while-revalidate — but only if you set staleness deliberately.

- **`staleTime` is the real lever, and its default is `0`** in React Query (every mount/refocus
  refetches). Set it per query to how long the data is acceptably fresh — seconds for a volatile
  feed, minutes for a profile, near-infinite for static reference data. `gcTime` (cache retention
  after a query goes unused) is a separate knob; don't conflate the two.
- **Dedup is automatic, keyed by the query key** — any components subscribing to the same key while a
  request is in flight share that one request (and a mount within `staleTime` reuses the cache with no
  request at all). This is *why* co-location is free; it's also why a sloppy key (see factory) breaks
  it.
- **Invalidate, don't hand-write the cache, by default.** After a mutation, the safe move is
  `invalidateQueries` on the affected key prefix → the cache refetches authoritative data. Manual
  `setQueryData` is for the optimistic path (below), where you also own the rollback.
- **Refetch triggers are configurable, not laws.** `refetchOnWindowFocus` / `refetchOnReconnect`
  default on in React Query and are usually right; turn them off for expensive or rarely-changing
  queries. Decide per query rather than globally disabling and losing the freshness guarantee.

---

## Mutations & optimistic updates

A mutation is a cache *write*. The default is honest-but-slower: fire, await, invalidate, let the
refetch paint the truth. Optimism trades that safety for speed — take the trade only when it pays.

- **Default path:** `mutate` → on success `invalidateQueries` the touched keys → UI reflects
  server truth. Surface the pending state on the trigger (disable/spinner the button) and the error
  state inline. Form-driven mutations wire through the form hook — see `forms.md`.
- **Go optimistic when the action is frequent and the rollback is cheap** — toggles, likes, reorder,
  inline edits. Skip it for money movement, destructive, or hard-to-reverse actions where showing a
  fake success is worse than a brief spinner.
- **Optimistic update is a three-step lifecycle plus one invariant — all four obligations or none:**
  1. `onMutate`: `cancelQueries` (so an in-flight refetch can't clobber your write), **snapshot** the
     current cache, then `setQueryData` to the predicted value. Return the snapshot as context.
  2. `onError`: roll back by restoring the snapshot. A missing rollback is the classic optimistic
     bug — the UI lies permanently when the server rejects.
  3. `onSettled`: `invalidateQueries` to reconcile with server truth (your prediction may differ from
     what the server actually stored — derived fields, server timestamps).
  - *Invariant:* keep the predicted shape identical to the real shape, or the reconcile flickers.
- **Concurrency:** `cancelQueries` + snapshot stops an *in-flight refetch* from clobbering the
  optimistic write — but it does not serialize the mutations themselves. Rapid overlapping mutations
  on the same key can still conflict or roll back over each other, so they need an explicit strategy
  (serialize them, or use patch-based rollback rather than whole-snapshot restore). SWR expresses the
  base pattern via `mutate(key, fn, { optimisticData, rollbackOnError })` — same obligations,
  different API.

---

## React 19 use() hook

React 19 introduces `use(promise)` as a way to read a promise (or Context) inside a component —
the component suspends while the promise is pending.

**When to use it:** reading a promise that was *created outside the component* and passed in as a
prop — typically a promise initiated by a Server Component and handed down to a Client Component.
This pattern works cleanly with RSC streaming because the server kicks off the fetch and the client
reads the result without a client-side re-fetch.

```tsx
// Server Component — start the fetch, pass the promise down
export default function Page() {
  const userPromise = fetchUser(id); // not awaited
  return <UserCard userPromise={userPromise} />;
}

// Client Component — read the promise with use()
"use client";
export function UserCard({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // suspends until resolved
  return <div>{user.name}</div>;
}
```

**Critical constraint:** the promise passed to `use()` must be **stable** — created outside the
render cycle (e.g. in a Server Component, a route loader, or a module-level cache), not inline
inside the Client Component's render. An inline `use(fetch('/api/user'))` creates a new promise on
every render, causing an infinite suspend loop.

**When NOT to use it:** client-side data fetching triggered by user interaction or component
mount. Use TanStack Query (or the repo's existing cache lib) for that — it gives you caching,
dedup, background refresh, and error/loading state management that `use()` alone does not.

---

## Suspense vs imperative states

Two ways to express "not ready yet" — pick per boundary, don't mix randomly in one tree.

- **Imperative (`isLoading`/`isError` branches in the component)** keeps the loading/error logic
  visible right where the data is read. Good default; pairs naturally with per-widget partial
  states (above).
- **Suspense (`useSuspenseQuery` + `<Suspense>` + error boundary)** hoists the loading fallback to a
  boundary and lets the component body assume data exists — cleaner reads, and it composes with
  RSC/streaming. Cost: the fallback granularity is the boundary, so a too-high boundary turns
  independent loads into one big spinner (a *visual* waterfall) — place boundaries per independent
  section. Requires a sibling error boundary, since a Suspense query throws on error.
- **Consistency over cleverness:** match whatever the screen/area already uses rather than mixing
  both in one subtree.

---

## Pagination & infinite queries

- **Use the cache lib's first-class primitive** — `useInfiniteQuery` (React Query) / `useSWRInfinite`
  — over hand-rolled page-array state, so each page is cached, dedup'd, and refetchable under its own
  key.
- **Prefer cursor pagination** when the API offers it: stable under inserts/deletes, where
  offset/`page` pagination skips or duplicates rows as the underlying list shifts. Match the API
  contract you actually have (craft-backend owns the server side).
- **Key the list by filters/sort, not by cursor.** For numbered/offset pagination, the page/offset
  is part of the key. For infinite queries, the `queryKey` identifies the whole list (filters + sort)
  and the cursor flows through the infinite-query API (`getNextPageParam` → `pageParam` /
  `useSWRInfinite`'s `getKey`), not folded into the top-level key. Either way, changing filters resets
  pagination cleanly instead of mixing pages from two filter sets.
- **Drive "load more" off the returned `hasNextPage`/next-cursor**, not a client guess, and gate the
  trigger on `isFetchingNextPage` to avoid double-loads. The scroll/intersection *UX* of infinite
  lists is `craft-ux`.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Pattern                                                          | Fix                                                                     |
| --------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Raw `fetch('/api/...')` inline, no shared typed client          | Route through the repo's central client; type/validate at the edge      |
| Response typed via `as SomeType` with no runtime parse          | Parse untrusted payloads with the schema lib at the boundary            |
| Inline/ad-hoc query key arrays scattered across files           | Centralize in a query-key factory; hierarchical keys                    |
| A variable that changes the result missing from the key         | Add it (filters, id, sort, tenant) — or caches collide                  |
| Sequential `await`s for independent requests                    | `Promise.all` / concurrent `useQuery` — no waterfall                    |
| Child fetches with a parent-computed id (structural waterfall)  | Hoist/prefetch at the boundary so requests overlap                      |
| Data hoisted to a parent only to prop-drill it down             | Co-locate the query with the renderer; dedup makes it free              |
| Async UI missing the empty (or error) state                     | Handle loading + error + empty at the fetch site (visuals: craft-ux)    |
| `staleTime` left at default `0` for stable data                 | Set `staleTime` to the data's real freshness window                     |
| Mutation does `setQueryData` with no rollback/`onError`         | Snapshot in `onMutate`, restore in `onError`, reconcile in `onSettled`  |
| Optimistic update on a destructive/irreversible action          | Use the await-then-invalidate path instead                              |
| Mutation succeeds but screen shows stale data                   | `invalidateQueries` the touched key prefix after the mutation           |
| One Suspense boundary wrapping several independent loads         | Split boundaries per section, or use imperative states                  |
| Hand-rolled page-array state for pagination                     | `useInfiniteQuery`/`useSWRInfinite`; filters/sort in the key, cursor via the infinite API |

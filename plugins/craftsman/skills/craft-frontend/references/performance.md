# Performance

The runtime and load-time behavior of the same components `architecture.md` shapes. The governing
rule: **measure before optimizing.** Lighthouse, the bundle analyzer (`next build` output,
`rollup-plugin-visualizer`), and the React DevTools profiler are the sources of truth; a gut feeling
is a hypothesis, not a reason to add `useMemo`.

> Scope split: this is application-layer performance (bundle, fetching, re-renders, runtime). The
> CSS/animation/GPU side (animate `transform`/`opacity` only, virtualize long lists, `next/image`
> dims, Suspense plumbing) is detailed in **`craft-ux`** → `layer-2-primitives.md` → Performance
> Building Blocks and Animation under Load. A few items below (`next/dynamic`, Server Components,
> layout-reads-in-render) are the *application-layer view* of concerns that also surface in that
> CSS-side table — same rule, framed for where the code lives; reach for `craft-ux` for the
> CSS/GPU detail.

---

## Load time — ship less, ship it later

- **Code-split at route boundaries by default**, then lazy-load heavy *leaf* components
  (`next/dynamic`, `React.lazy`) — a charting lib, a rich-text editor, a map. Anything client-only
  and below the fold is a candidate.
- **Keep the critical path lean.** A dependency on the first-paint path is paid by every user on
  every visit; a new dependency > ~20 KB gzipped needs written justification and a check for a
  lighter alternative (`bundlephobia`).
- **Server Components by default.** Rendering on the server keeps component code out of the client
  bundle entirely — reach for `"use client"` only at the interactive leaf (see `architecture.md` →
  Boundaries).
- **Help tree-shaking, then verify it worked.** Prefer direct named imports from side-effect-free
  ESM entrypoints (`{ x } from 'lib'`, not `import * as lib`); avoid barrel files that re-export a
  whole library. Tree-shaking also depends on the package's `sideEffects` flag, ESM vs CJS, and
  bundler behavior — so confirm the win in the analyzer output rather than assuming.

---

## Runtime — keep the main thread free

- **Avoid fetch waterfalls.** Independent data dependencies fetch in parallel
  (`Promise.all`, parallel queries, or router-level prefetch) — never `await` one just to start the
  next. Co-locate each fetch with the component that renders it (see `data-fetching.md`).
- **Cut re-renders at the source before memoizing.** Most "needs `memo`" problems are really
  context-too-wide or state-too-high: split a hot context, push state down to the leaf that owns it,
  or pass `children` through so a re-rendering parent doesn't re-render a stable subtree. Then, if
  the profiler still shows cost, apply `React.memo`/`useMemo`/`useCallback` to the *measured* hot
  path.
- **Stable references where identity matters.** A new object/array/function literal passed to a
  memoized child or an effect dependency defeats both — hoist constants, or memoize the value.
- **Don't read layout in render.** `getBoundingClientRect`/`offsetWidth` in render (or in a loop)
  forces synchronous reflow; batch reads in an effect, separate from writes.
- **Debounce/throttle high-frequency handlers** (scroll, resize, input-driven search) and clean up
  the timer in the effect's teardown.

---

## Verify, don't assume

A performance claim is only valid if measured. Before asserting "this is fast" or "this needs
optimizing":

- Bundle: check the analyzer output for the actual added weight and what pulled it in.
- Re-renders: confirm with the profiler's flamegraph which component re-rendered and why.
- Load: a Lighthouse run (throttled) for LCP/TBT/CLS, not a fast-laptop eyeball.

Report the number, the source, and the delta — same discipline as any review finding.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| New dep > ~20 KB gzipped on the critical path, no justification | Check bundlephobia; justify or swap for a lighter alternative |
| `"use client"` at a high tree boundary (drags subtree into the client bundle) | Push it down to the interactive leaf (`architecture.md`) |
| Independent requests waterfalled with sequential `await`s | `Promise.all` / parallel queries (`data-fetching.md`) |
| `useMemo`/`useCallback`/`React.memo` with no profiler evidence | Remove until the flamegraph shows a measured cost |
| `getBoundingClientRect`/`offsetWidth` called in render | Move to an effect; batch reads separate from writes |
| High-frequency handler (scroll, resize, search input) without debounce/throttle | Add debounce/throttle + teardown in the effect cleanup |
| Heavy leaf component (chart, editor, map) loaded eagerly on first paint | `React.lazy` / `next/dynamic` — code-split to a separate chunk |
| No bundle analysis run after adding a new dependency | Run `next build --analyze` (or equivalent) and check the output |
| Performance claim with no measurement to back it — "this should be fast" | Run Lighthouse (throttled) + bundle analyzer; record LCP and chunk sizes |

---
name: craft-ux
description: >-
  The Craftsman standard for UI/UX — design tokens, component patterns, pixel-perfect standards,
  Tailwind/React implementation, motion craft, an AI-tells anti-pattern catalog, and a two-pass
  review protocol (static review + live browser audit).
  Use this whenever designing, building, reviewing, auditing, redesigning, or polishing UI — a
  component, page, dashboard, landing page, modal, form, or layout; standing up or hardening a
  design system; checking spacing, typography, color, motion, or accessibility; or hunting
  AI-generated "tells". Trigger even on "make this look better", "fix the styling", "audit my
  design tokens", or "test it in the browser" without naming a tool or framework.
  App architecture (state, data fetching, bundles, routing) → craft-frontend.
  Does NOT fire on backend, database, CI/CD, or infra requests, or UI-free code-quality asks.
---

# UX Craft

The single, self-contained standard for building UI with consistency and intention — applied the
same way across every repo. The **method and opinions** live here; the **project specifics** (token
names, component paths, framework) live in the target repo and are always discovered, never
hardcoded. **Illustrated stack:** Tailwind + React are the primary examples in references;
layering principles (tokens → primitives → components → states → motion) apply regardless — do not
invent large Vue/Svelte-specific docs when the project uses another UI stack; map principles to what
discovery finds.

Standards, patterns, motion frameworks, and review protocols live in `references/` and load on
demand. **Before any non-trivial task, read `references/foundations.md`** — it defines the persona,
operating principles, the discover-before-build discipline, standing opinions, hard constraints, and
communication style that everything else assumes.

> **Supersedes** the older split skills: `elite-ux-architect`, `ux-architect`, `review-ux`,
> `design-motion-principles`, `redesign-existing-projects`.

## Initialization

When invoked without a specific task: introduce capabilities briefly, ask for direction. **Do not
proactively audit, scan files, or assess implementation quality.** Wait for the user.

## The design-system layers (build in this order)

The spine of the skill. Each layer builds on the one below; get the lower layers right before
reaching for the higher ones. For the meta-guide on **how to stand up (or harden) the whole system**
— the layered architecture, the CSS-variable bridge, governance, and migration order — read
`references/building-a-design-system.md`. To keep it from rotting, `references/token-audit.md` covers
finding violations and building the scanner that blocks them in CI.

1. **Tokens** — color, spacing, typography as CSS variables + a typed module. → `references/layer-1-tokens.md`
2. **Primitives & implementation** — `Stack`/`Inline`/`Grid`/`Box` and the Tailwind/`cn()`/CVA
   mechanics every component sits on. → `references/layer-2-primitives.md`
3. **Components** — the supported set (forms, tables, modals, nav, notifications) with consistent
   variant/size APIs. → `references/layer-3-components.md`
4. **States** — loading, empty, error, disabled as first-class. → `references/layer-4-states.md`
5. **Motion & accessibility** — purposeful motion + the a11y floor. → `references/layer-5-motion.md`
   (three designer deep-dives live in `references/motion/` — Emil, Jakub, Jhey)

## Reference index

| Task                                                                                                      | Load                                     |
| --------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Persona, principles, discover-first, standing opinions, hard constraints**                              | `references/foundations.md`              |
| **Build a design system** from scratch or harden an ad-hoc one — layered architecture, bridge, governance | `references/building-a-design-system.md` |
| **Audit / enforce design tokens** — find violations, fix by category, build the scanner                   | `references/token-audit.md`              |
| Spacing, typography, color, radius, shadows, icons, touch targets, motion-timing tokens, breakpoints      | `references/layer-1-tokens.md`           |
| Layout primitives; Tailwind, `cn()`, CVA, mobile-first, dark mode, hydration safety, perf building blocks | `references/layer-2-primitives.md`       |
| Forms, tables, modals, navigation, notifications; component anatomy + variant APIs                        | `references/layer-3-components.md`       |
| Empty / loading / error / disabled states                                                                 | `references/layer-4-states.md`           |
| Motion audit framework + accessibility fundamentals                                                       | `references/layer-5-motion.md`           |
| Emil Kowalski — restraint, speed, springs, clip-path, gestures                                            | `references/motion/emil-craft.md`        |
| Jakub Krehel — production polish, subtle enter/exit, shadows, optical alignment                           | `references/motion/jakub-polish.md`      |
| Jhey Tompkins — playful CSS, `linear()`, `@property`, scroll-driven, 3D                                   | `references/motion/jhey-experimental.md` |
| Page/dashboard architecture, landing sections, Bento, design-intensity calibration                        | `references/composition.md`              |
| Canonical AI-tells catalog — **what to flag in reviews**                                                  | `references/anti-patterns.md`            |
| Redesigning existing UI — Scan → Diagnose → Fix                                                           | `references/redesign-audit.md`           |
| Code-review **structure** + web-interface compliance checklist (static pass)                              | `references/review-protocol.md`          |
| Web Interface Guidelines rule list — vendored, SHA-pinned, applied by the compliance pass                 | `references/web-interface-guidelines.md`  |
| **Live audit** — drive the running app (Playwright / `claude-in-chrome`) for rendered/visual defects      | `references/live-audit.md`               |

## Standard workflows

| Workflow                     | Mandatory                                  | Add when needed                                                                                                     |
| ---------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Build a design system**    | `foundations` + `building-a-design-system` | `layer-1` for token values, `layer-2` for primitives, `token-audit` to add the scanner                              |
| **Audit / enforce tokens**   | `token-audit`                              | `layer-1` for the canonical values, `building-a-design-system` for where a value belongs, `anti-patterns` for tells |
| **Build a component**        | `foundations` + `layer-2`                  | `layer-3` for the pattern, `layer-1` for token values, `layer-4` for its states                                     |
| **Build a page / dashboard** | `foundations` + `layer-2` + `composition`  | `layer-3` for components, `composition` arsenal for a distinctive aesthetic                                         |
| **Polish interactions**      | `foundations` + `layer-5`                  | `layer-5` routes to the right designer (`motion/*`); `layer-1` for timing values                                    |
| **Review code**              | `review-protocol` + `anti-patterns`        | `layer-3` for forms/modals/tables/states, `layer-2` for Tailwind/CVA/hydration/perf, `layer-1` for visual specifics |
| **Live audit (Pass 2)**      | `live-audit` (after the static review)     | `review-protocol` for the shared severity model + output format; `layer-4` for the empty/loading/error states to force |
| **Audit motion**             | `layer-5` (routes by context)              | whichever `motion/*` designer reference it weights                                                                  |
| **Redesign existing UI**     | `redesign-audit` (Scan→Diagnose→Fix)       | `anti-patterns` for the Diagnose pass, `layer-2` + `layer-1` for the Fix pass                                       |

**Load lazily.** Pull a file only when the task actually asks the question it answers — don't
preload the "add when needed" column.

## Pair with project context

This skill is reusable across products and carries the full standards + craft on its own. For
project-specific competitive intelligence, stack constraints, and routing to project-only utility
skills (a token-audit gate, RTL rules, perf audit), the calling agent may also load a thin
project-level UX skill. The project skill provides the "why this matters here" frame; this skill
provides the standards and craft. `impeccable` remains available for extra aesthetic exploration,
but is no longer required — `craft-ux` is self-sufficient for persona + system + review.

## Audit checklist (for craft-audit)

When `craft-audit` plans a ux pass for a scope, it turns this checklist into the `plan.md`
todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor to what
discovery found: skip a step that genuinely doesn't apply with a one-line reason; never silently drop
one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission format"
(authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-UX-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-UX-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Confidence:**` — `verified | inferred | unverified-from-repo`, absent
means `verified` — then optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] Run discovery first — locate the token module, layout primitives, and scanner; flag "no layered
      system" or tokens that exist but are bypassed/misused, not just absent → `references/foundations.md`
- [ ] Audit design tokens for adoption — hardcoded raw palette colors, raw spacing, and structured
      tokens passed where a class string is expected; build/confirm the CI scanner → `references/token-audit.md`
- [ ] Check visual fidelity against the token scale — off-scale spacing, typography, color, radius,
      shadows, icons, and motion-timing values → `references/layer-1-tokens.md`
- [ ] Verify state completeness — every route subtree has loading/empty/error boundaries (reason about
      cascade + layout/provider errors), no populated-only views → `references/layer-4-states.md`
- [ ] Review component patterns — forms (labels, semantic `type`, autocomplete), modals, tables, nav,
      and notifications for consistent variant/size APIs and missing a11y → `references/layer-3-components.md`
- [ ] Sweep for AI-tells and dark/technical anti-patterns — `transition-all`, `<div onClick>`,
      `outline-none` with no focus ring, `<img>` without dimensions → `references/anti-patterns.md`
- [ ] Check footer/legal furniture — privacy policy and terms links reachable from every page (not
      just the marketing homepage), and any consent banner offers equally easy accept/decline →
      `references/layer-3-components.md`
- [ ] Run motion audit protocol — verify `prefers-reduced-motion` is handled, duration/easing tokens
      are used consistently (not magic numbers), no layout-property animations, ARIA live regions on
      dynamic content, and no janky animations on low-end hardware → `references/layer-5-motion.md`
- [ ] Run the static review with its grep sweep + Web-Interface Compliance pass against the vendored
      `references/web-interface-guidelines.md` (no review-time network fetch) — severity model
      (Critical / Important / Opportunities → 🔴 / 🟡 / 🟢) from `references/review-protocol.md`;
      **emission path depends on context:** under `craft-audit` / writing `.craftsman/**/findings.md`,
      emit each finding in the canonical workspace heading format above (not the punch-list tables);
      standalone UX review may use the review-protocol banner + tables → `references/review-protocol.md`
- [ ] Run the live pass after the static one — clear the preflight gate (non-prod, throwaway identity,
      side effects neutralized), then walk flows × 375/768/1280 × empty/loading/error, tagging each
      finding with its rendered condition; same dual-emission rule as the static pass →
      `references/live-audit.md`


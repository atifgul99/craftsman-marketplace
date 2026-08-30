# Redesign & Audit — Scan → Diagnose → Fix

The workflow for improving UI that already exists: map what's there, diagnose against the standards, fix by priority.

Upgrading an existing website or app: audit generic patterns, apply premium fixes, preserve
working behavior. Not a rewrite — a targeted upgrade.

> **craft-ux tie-in:** The Scan step IS the discover-before-build principle applied to existing UI — extend what's there, don't rip-and-replace unless warranted.

> **See also**
>
> - For **what to flag** during the audit (the catalog) → `anti-patterns.md`
> - For the severity buckets and output tables used during Diagnose → `review-protocol.md`
> - For pixel-perfect values during Fix → `layer-1-tokens.md`
> - For implementation specifics (Tailwind, dark mode, hydration) during Fix → `layer-2-primitives.md`
> - For component patterns during Fix → `layer-3-components.md`

---

## When to Use This Workflow

- User asks to redesign, restyle, modernize, polish, or improve an existing UI
- Audit current frontend code and make targeted visual improvements without changing the
  product architecture
- Design feels generic, AI-generated, poorly spaced, visually flat, or missing responsive,
  interactive, loading, empty, or error states

---

## Limitations

- Upgrade existing UI — do not rewrite frameworks, restructure information architecture, or
  expand product scope by default
- Preserve working behavior, routing, data flows, accessibility semantics, and tests
- Validate redesigned screens in the actual app across supported browsers and viewport sizes
  before declaring done

---

## The Sequence

### 1. Scan

Read the codebase. Identify:

- Framework (Next.js, Vite, plain HTML, etc.)
- Styling method (Tailwind, vanilla CSS, styled-components, CSS modules)
- Current design patterns
- Component library in use
- Token/theme system (if any)

### 2. Diagnose

Run the full anti-pattern catalog from `anti-patterns.md` against the codebase. Walk
through each section:

- Visual AI Tells (color, typography, layout, depth)
- Content Anti-Patterns
- UX Anti-Patterns
- Technical Anti-Patterns
- Mobile Anti-Patterns
- Strategic Omissions
- Composition Anti-Patterns
- Code Quality Anti-Patterns

Emit findings with `file:line` for every violation. Use the severity buckets from
`review-protocol.md` (Critical / Important / Opportunities). **Emission path depends on context**
(same dual-emission rule as `review-protocol.md` → Output Format): under `craft-audit` / writing
`.craftsman/**/findings.md` → canonical workspace findings only; standalone redesign review →
punch-list tables/chat.

### 3. Fix

Apply targeted upgrades working with the existing stack. Do not rewrite from scratch.

Use the **Upgrade Techniques** below to replace specific generic patterns with stronger ones.
For canonical spacing/typography/color values consult `layer-1-tokens.md`. For
implementation patterns (Tailwind, dark mode, hydration) consult `layer-2-primitives.md`.

---

## Upgrade Techniques

High-impact patterns to replace generic ones.

### Typography upgrades

- **Variable font animation** — interpolate weight or width on scroll/hover
- **Outlined-to-fill transitions** — text starts as stroke, fills with color on scroll entry
- **Text mask reveals** — typography as a window to video or animated imagery behind it
- **Distinctive display + body pairing** — Space Grotesk + Plus Jakarta Sans, Cabinet Grotesk +
  IBM Plex, etc. See `layer-1-tokens.md` → Typography for the pool, the serif-discipline rule,
  and why Fraunces / Instrument Serif are no longer recommended (they became the AI-default
  serifs — see `anti-patterns.md` → Visual AI Tells).
  <!-- Inter Tight was removed: it is a condensed variant of the Inter family, which anti-patterns.md
       bans as a default AI font tell. Replaced with Plus Jakarta Sans as an equivalent sans-serif
       body pairing that is not in the Inter family. -->
  <!-- Fraunces was removed as the display example: taste-skill v2 production tests (2026) showed
       Fraunces + Instrument Serif became the two LLM-default display serifs — the new Inter. -->

### Layout upgrades

- **Broken grid / asymmetry** — elements deliberately overlap or bleed off-screen
- **Whitespace maximization** — force focus on a single element
- **Parallax card stacks** — sections stick and stack on scroll
- **Split-screen scroll** — halves move opposite directions
- **Bento grid** — asymmetric tiles; see `composition.md` for the Bento 2.0 baseline. See
  composition.md § Bento 2.0 for the token-mapping note.

### Motion upgrades

Common upgrade moves:

- **Smooth scroll with inertia** — cinematic feel
- **Staggered entry** — cascade with 30–80 ms delays + Y-axis + opacity
- **Spring physics** — replace linear easing
- **Scroll-driven reveals** — expanding masks, draw-on SVG paths

### Surface upgrades

- **True glassmorphism** — `backdrop-filter: blur` + 1 px inner border + inner shadow (not just
  blur)
- **Spotlight borders** — card borders illuminate under cursor
- **Grain/noise overlays** — `fixed pointer-events-none` pseudo-element
- **Colored, tinted shadows** — carry the hue of the background; multi-layer recipe in
  `layer-1-tokens.md` → Shadows

---

## Fix Priority Order

Apply changes in this order for maximum visual impact with minimum risk:

1. **Font swap** — biggest instant improvement, lowest risk
2. **Color palette cleanup** — remove clashing or oversaturated colors
3. **Hover and active states** — makes interface feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliche patterns for modern alternatives
6. **Add loading, empty, and error states** — makes it feel finished
7. **Polish typography scale and spacing** — the premium final touch

---

## Rules

- Work with the existing tech stack. Do not migrate frameworks or styling libraries.
- Do not break existing functionality. Test after every change.
- Before importing a new library, check `package.json`.
- If the project uses Tailwind, check the major version (v3 vs v4) before modifying config —
  see `layer-2-primitives.md` → Dependency Verification.
- If the project has no framework, use vanilla CSS.
- Keep changes reviewable and focused. Small, targeted improvements over big rewrites.

---

## Output Format During Redesign

When reporting findings during the Diagnose phase, use the severity-tagged tables from
`review-protocol.md`:

```
## Critical (must fix this PR)
| | Issue | File | Action |
|-|-------|------|--------|
| 🔴 | [issue] | `file:line` | [fix] |

## Important (should fix in redesign pass)
| | Issue | File | Action |
|-|-------|------|--------|
| 🟡 | [issue] | `file:line` | [fix] |

## Opportunities (next iteration)
| | Enhancement | Where | Impact |
|-|-------------|-------|--------|
| 🟢 | [idea] | `file:line` | [impact] |
```

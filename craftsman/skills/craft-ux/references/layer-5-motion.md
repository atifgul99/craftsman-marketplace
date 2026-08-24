# Layer 5 — Motion & Accessibility

Purposeful motion that conveys state and guides attention, plus the accessibility floor every interface must clear.

Motion is the last layer — get tokens, primitives, components, and states right first; motion is polish, never a fix for a broken hierarchy.

> **See also**
>
> - For motion-timing token values (durations, easing curves) → `layer-1-tokens.md` → Transitions and Motion Timing
> - For component-level interaction patterns → `layer-3-components.md`
> - For designer persona context → `foundations.md`

---

## Contents

- [Motion Audit Framework](#motion-audit-framework)
- [STEP 1 — Reconnaissance (Do This First)](#step-1--reconnaissance-do-this-first)
- [STEP 2 — State Your Inference](#step-2--state-your-inference)
- [Reconnaissance Complete](#reconnaissance-complete)
- [STEP 3 — Context → Perspective Mapping](#step-3--context--perspective-mapping)
- [STEP 4 — Audit Output Format](#step-4--audit-output-format)
- [Universal Checklist (Apply Regardless of Designer Weighting)](#universal-checklist-apply-regardless-of-designer-weighting)
- [Forbidden Animation Patterns](#forbidden-animation-patterns)
- [Severity Levels](#severity-levels)
- [Universal Reduced-Motion Pattern](#universal-reduced-motion-pattern)
- [Accessibility Floor](#accessibility-floor)

---

## Motion Audit Framework

Motion design is context-dependent, not universal. The same animation that is correct for a
kids app is wrong for a high-frequency productivity tool. This section covers reconnaissance,
motion gap analysis, designer-perspective weighting, and the universal checklist.

For deep dives on each designer's craft, load:

- `motion/emil-craft.md` — Emil Kowalski (restraint, speed, productivity tools)
- `motion/jakub-polish.md` — Jakub Krehel (subtle production polish)
- `motion/jhey-experimental.md` — Jhey Tompkins (playful CSS experimentation)
- `motion/fluid-gestures.md` — momentum physics for gesture-driven surfaces (sheets, drag,
  swipe, carousels): velocity handoff, projection, rubberbanding, interruptible springs

---

## STEP 1 — Reconnaissance (Do This First)

Before auditing any code, understand the project context. Never apply rules blindly.

**Gather:**

1. **Project type.** Marketing site? SaaS dashboard? Kids app? Mobile PWA? Creative portfolio?
2. **Existing animations.** Grep for `motion`, `animate`, `transition`, `@keyframes`. What
   durations? What patterns?
3. **Existing project rules.** CLAUDE.md, design system docs, brand guidelines.
4. **User base.** Enterprise users repeating high-frequency actions? Casual visitors? Kids?

**Motion gap analysis (critical — don't skip):**

After cataloging existing animations, search for **missing** ones — conditional UI changes that
snap in/out:

```bash
grep -n "&&\s*(" --include="*.tsx" -r .
grep -n "?\s*<" --include="*.tsx" -r .
```

For each conditional render:

- Wrapped in `<AnimatePresence>`? If not, that's a gap.
- Does it have enter/exit animations? If not, gap.
- Snap-in/snap-out modals, panels, mode switches, loading states are all gaps.

---

## STEP 2 — State Your Inference

Before doing the audit, tell the user what you found and propose a weighting:

```
## Reconnaissance Complete

**Project type:** [e.g. "Productivity SaaS, B2B, repeat-use dashboard"]
**Existing animation style:** [e.g. "Spring 200–400 ms, Framer Motion, no scale(0) entries"]
**Likely intent:** [e.g. "Speed and clarity for power users"]

**Motion gaps found:** [N] conditional renders without AnimatePresence
- [list specific files/areas]

**Proposed perspective weighting:**
- Primary: [Designer] — [Why]
- Secondary: [Designer] — [Why]
- Selective: [Designer] — [When applicable]

Does this approach sound right?
```

**WAIT for confirmation** before doing the full audit.

---

## STEP 3 — Context → Perspective Mapping

| Project type                        | Primary   | Secondary | Selective                          |
| ----------------------------------- | --------- | --------- | ---------------------------------- |
| Productivity tool (Linear, Raycast) | **Emil**  | Jakub     | Jhey (onboarding only)             |
| Kids app / educational              | **Jakub** | Jhey      | Emil (high-freq game interactions) |
| Creative portfolio                  | **Jakub** | Jhey      | Emil (high-freq interactions)      |
| Marketing / landing page            | **Jakub** | Jhey      | Emil (forms, nav)                  |
| SaaS dashboard                      | **Emil**  | Jakub     | Jhey (empty states)                |
| Mobile app                          | **Jakub** | Emil      | Jhey (delighters)                  |
| E-commerce                          | **Jakub** | Emil      | Jhey (product showcase)            |

---

## STEP 4 — Audit Output Format

### Summary box (show first)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AUDIT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 [X] Critical  |  🟡 [X] Important  |  🟢 [X] Opportunities
Primary perspective: [Designer(s)] ([context reason])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Overall assessment

One paragraph: does this feel polished? Too much? Too little? What works, what doesn't?

### Per-designer sections

Each weighted designer gets:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ EMIL'S PERSPECTIVE — Restraint & Speed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**What's working well:**
- ✓ [Observation] — `file.tsx:line`

**Issues to address:**
- ✗ [Issue] — `file.tsx:line`
  [Brief explanation]

**Emil would say:** [1–2 sentence summary]
```

Use ⚡ for Emil, 🎯 for Jakub, ✨ for Jhey.

### Combined recommendations

Severity-tagged tables:

```
**Critical (must fix)**
| | Issue | File | Action |
|-|-------|------|--------|
| 🔴 | [issue] | `file:line` | [fix] |

**Important (should fix)**
| | Issue | File | Action |
|-|-------|------|--------|
| 🟡 | [issue] | `file:line` | [fix] |

**Opportunities (could enhance)**
| | Enhancement | Where | Impact |
|-|-------------|-------|--------|
| 🟢 | [idea] | `file:line` | [impact] |
```

### Final designer reference summary

```
> **Who was referenced most:** [Designer]
>
> **Why:** [Explanation based on project context]
>
> **If you want to lean differently:**
> - To follow Emil more strictly: [specific actions]
> - To follow Jakub more strictly: [specific actions]
> - To follow Jhey more strictly: [specific actions]
```

---

## Universal Checklist (Apply Regardless of Designer Weighting)

### Philosophy

- [ ] How often will users trigger this? (Frequent = less/no animation)
- [ ] Is this keyboard-initiated? (If yes, don't animate)
- [ ] Does this serve a purpose? (orientation, feedback, continuity — not decoration)
- [ ] Will users notice it consciously? (If yes in production UI, probably too much)
- [ ] Tested with `prefers-reduced-motion: reduce`?
- [ ] Feels natural after the 10th interaction?
- [ ] Easing appropriate for brand/context?
- [ ] Duration appropriate for context?

### Motion gap analysis

- [ ] Searched for conditional renders without `AnimatePresence`
- [ ] Searched for ternary swaps without transitions
- [ ] Searched for dynamic inline styles without transitions
- [ ] Each conditional render either has AnimatePresence OR doesn't need animation
- [ ] Mode switches (tabs, toggles) animate their content changes
- [ ] Settings panels with conditional controls have enter/exit
- [ ] Expandable sections animate height
- [ ] Loading → content transitions are smooth, not instant swaps

### Enter/exit states

- [ ] Enter combines opacity + translateY + blur
- [ ] Exit subtler than enter (smaller translateY, same blur/opacity)
- [ ] `animation-fill-mode: backwards` used for delayed sequences
- [ ] Elements don't flash before their delayed animation starts

### Tool choice — cheapest that works

Walk down; stop at the first that fits. Don't install a motion library for a fade.

| Need                                                                  | Tool                                    |
| --------------------------------------------------------------------- | --------------------------------------- |
| Hover, press, color, a class/attribute-controlled state toggle        | CSS transition                          |
| Entry animation on mount, no JS state                                 | CSS `@starting-style`                   |
| Predetermined motion that must stay smooth while the page is busy     | CSS animation (off the main thread)     |
| Programmatic control with CSS performance, no library                 | WAAPI (`element.animate()`)             |
| Springs, layout animations, exit animations, gesture-driven values    | Motion (Framer Motion)                  |

### Easing and timing

- [ ] Appropriate easing for context (not default `ease` everywhere)
- [ ] Custom bezier curves used instead of built-in easing
- [ ] Spring animations for interactive elements
- [ ] Durations appropriate (Emil: < 300 ms; others: whatever serves the design)
- [ ] Consistent timing values across related animations
- [ ] Curves and durations live as shared tokens — five hand-typed near-identical
      cubic-beziers across components is a consolidation finding, not five separate choices
- [ ] Transform-origin matches the interaction source

### Performance

- [ ] `will-change` used sparingly and specifically
- [ ] Animations use transform/opacity (not layout properties)
- [ ] Tested on low-end devices
- [ ] No continuous animations without purpose
- [ ] CSS transitions (not keyframes) for interruptible animations
- [ ] Direct style updates for drag operations (not CSS variables)
- [ ] Velocity-based thresholds (not distance) for swipe dismiss

### Accessibility

- [ ] Respects `prefers-reduced-motion`
- [ ] No vestibular triggers (excessive zoom, spin, parallax)
- [ ] Looping animations can be paused
- [ ] Functional animations have non-motion alternatives
- [ ] Dynamic content updates announce via `aria-live` or `role="status"` / `role="alert"` (see ARIA live regions section below)

---

## Forbidden Animation Patterns

Hard bans, not preferences — each one has a jank-free replacement.

- **`window.addEventListener("scroll", …)`.** Runs on every scroll frame, no batching,
  jank-prone. Use Motion's `useScroll()`, GSAP `ScrollTrigger`, `IntersectionObserver`, or CSS
  scroll-driven animations (`animation-timeline: view()`).
- **`window.scrollY` (or any scroll progress) in React state.** Re-renders the tree every frame.
  Same replacement list.
- **`requestAnimationFrame` loops that touch React state.** Any continuous value driven by user
  input — mouse position, scroll progress, magnetic hover — goes through motion values
  (`useMotionValue` + `useTransform`), never `useState`; state-driven versions collapse on mobile.
- **Missing cleanup.** Every `useEffect` that registers a GSAP context, observer, or listener
  returns a cleanup function (`ctx.revert()`, `observer.disconnect()`).
- **Motion claimed but not shown.** Half-built motion that breaks (cut-off ScrollTriggers, jumpy
  entries, missing cleanups) is worse than none — either ship working motion or ship a clean
  static page.

**GSAP pinning gotcha (scroll-hijack sections — marketing scrolltelling only).** The common
failure in sticky-stack and horizontal-pan sections is the trigger firing halfway through
scroll, so the user sees half a slide before the pin engages. The fix is `start: "top top"`
(not `"top center"` or `"top 80%"`), `pin: true` on the wrapper, and scrubbing the inner
track; for horizontal pans, `end: "+=" + distance` where distance is the track's overflow
width. Isolate in a `'use client'` leaf with cleanup, and collapse to static under
`prefers-reduced-motion`.

---

## Severity Levels

**Critical (must fix):**

- Missing `prefers-reduced-motion` support
- Animating layout properties (width, height, top, left)
- No exit animations (elements just disappear)
- Motion gaps in primary UI (conditional controls/panels that snap)
- Animating keyboard-initiated actions
- Animations on high-frequency actions (100s/day)

**Important (should fix):**

- Exit as prominent as enter
- Missing blur in enter animations (productivity context)
- Animating from `scale(0)` instead of `0.9+`
- Default CSS easing instead of custom curves
- Wrong transform-origin on dropdowns/popovers

**Context-dependent (check designer):**

- Durations over 300 ms (Emil flags; Jakub/Jhey may approve)

**Nice to have:**

- Optical alignment refinements
- `oklch` color space for gradients
- Spring animations instead of ease
- Button scale feedback on press
- Tooltip delay pattern (first delayed, subsequent instant)

---

## Universal Reduced-Motion Pattern

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

This effectively disables animation while preserving final states (so layouts don't break).
Functional motion (state indication, spatial continuity) may need an instant alternative; pure
decoration can be fully removed.

---

## Accessibility Floor

Every interface must clear these requirements regardless of motion choices. Treat each item as a
hard requirement, not a stretch goal.

### prefers-reduced-motion

`prefers-reduced-motion` is a first-class branch, not an afterthought. Every animation must have
an explicit reduced-motion path:

- Apply the universal CSS pattern above as a global baseline.
- In JavaScript animation libraries (Framer Motion, GSAP), read the media query directly and skip
  or instant-complete transitions: `const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches`
- Never rely on the CSS override alone for JS-driven animations — the library may bypass the
  cascade.
- Functional motion (loading spinners, progress indicators, state transitions) must provide an
  instant or opacity-only alternative when reduced motion is active, not just disappear.
- Under reduced motion, replace slides/springs/parallax with short opacity cross-fades and drop
  elastic overshoot — reduced means gentler and non-vestibular, not zero feedback.
- Avoid slow looping oscillations near 0.2 Hz (one cycle per ~5 s) and abrupt brightness jumps —
  ease dark↔light theme changes where a transition is used at all.

### Related preference media queries

Two siblings of reduced-motion that translucent/high-polish UI must also honor:

- **`prefers-reduced-transparency: reduce`** — make translucent surfaces frostier or solid:
  raise background opacity, drop the `backdrop-filter` blur.
- **`prefers-contrast: more`** — near-solid backgrounds with a defined, contrasting border.

```css
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
@media (prefers-contrast: more) {
  .card { background: var(--surface); border: 1px solid var(--border-strong); }
}
```

### Focus-visible states

- Every interactive element — buttons, links, inputs, custom controls — must expose a visible
  `:focus-visible` ring. Do not suppress the browser default without replacing it.
- The focus indicator must have at least 3:1 contrast against the adjacent background (WCAG 2.2
  criterion 2.4.11).
- Never use `outline: none` or `outline: 0` without an explicit replacement focus style.
- Custom components (dropdown triggers, combobox options, dialog close buttons) must receive focus
  and show the ring; invisible focus is a critical failure.

### Keyboard navigation completeness

- All interactive functionality must be reachable and operable by keyboard alone.
- Tab order must follow visual reading order; avoid positive `tabindex` values.
- Modals and drawers must trap focus within themselves while open and restore focus to the trigger
  on close.
- Custom widgets (sliders, date pickers, tab panels) must implement the ARIA authoring patterns
  (arrow key navigation, Home/End, Escape to dismiss).
- Dropdown menus must close on Escape and return focus to the trigger.

### WCAG AA contrast minimum

- Normal text (< 18 pt / < 14 pt bold): minimum 4.5:1 against its background.
- Large text (≥ 18 pt / ≥ 14 pt bold): minimum 3:1.
- UI components and state indicators (borders, icons that convey meaning): minimum 3:1.
- Placeholder text and disabled states are exempt from the ratio, but disabled text should still
  be visually distinguishable from active text through means other than color alone.
- Check contrast at design-token level, not just in isolation — layered surfaces (card on
  sidebar on background) compound contrast loss.

### ARIA live regions

Dynamic content that changes without a page navigation must announce itself to screen readers.
Motion transitions that swap content silently are inaccessible — the visual change is not
perceived by assistive technology unless the DOM update carries the right ARIA semantics.

**When to use `aria-live`:**

- Any content that updates dynamically without the element receiving focus (status messages,
  counts, cart totals, connection indicators, streaming text)
- Prefer `role="status"` (polite) or `role="alert"` (assertive) over bare `aria-live` —
  they carry implied semantics and are more widely supported

**`role="status"` (polite):**

```html
<!-- Polite: waits for the user to finish their current interaction -->
<div role="status" aria-live="polite" aria-atomic="true">
  3 items in cart
</div>
```

Use for: success confirmations, save indicators, count updates, background-sync messages.

**`role="alert"` (assertive):**

```html
<!-- Assertive: interrupts immediately — use only for errors or urgent info -->
<div role="alert" aria-live="assertive" aria-atomic="true">
  Error: Could not save your changes. Please try again.
</div>
```

Use for: form errors, network failures, security warnings. Never use for non-urgent updates —
assertive interrupts the screen reader mid-sentence.

**`aria-atomic`:**

- `aria-atomic="true"` — the entire region is re-announced when any part changes. Use when the
  full message must be heard together ("3 items in cart" not just "3").
- `aria-atomic="false"` (default) — only the changed nodes are announced. Use for streaming
  text or append-only logs where announcing the delta is sufficient.

**`aria-live="off"` for decorative updates:**

Animated counters, progress bars that update frequently, and other decorative live regions
should use `aria-live="off"` (or no live region at all) to prevent announcement spam. Only
announce when the value has semantic importance to the user's task.

**Pattern — React live region:**

```tsx
// Place the live region in the DOM on initial render; update its text content only
function StatusAnnouncer({ message }: { message: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"  // visually hidden but announced
    >
      {message}
    </div>
  );
}
```

Keep live regions present in the DOM from initial render — injecting them dynamically at the
moment of announcement is unreliable across screen readers.

---

### Reduced-motion as a first-class branch

The pattern for any animation authored in JavaScript:

```ts
const prefersReduced =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Example: skip enter animation entirely
const variants = prefersReduced
  ? { hidden: { opacity: 0 }, visible: { opacity: 1 } }
  : {
      hidden: { opacity: 0, y: 8, filter: "blur(4px)" },
      visible: { opacity: 1, y: 0, filter: "blur(0px)" },
    };
```

Always author the reduced branch first, then layer in the full animation. This discipline prevents
reduced-motion from becoming an untested code path.

# 07c — Jhey Tompkins: Experimental CSS Techniques

Jhey Tompkins (@jh3yy) — playful experimentation. Best for creative sites, kids apps,
portfolios, and learning new CSS features. Use for delighters and onboarding moments inside
otherwise restrained UIs. Not for high-frequency tool UIs or professional/enterprise surfaces.

> **See also**
>
> - Motion audit framework + context routing → `../layer-5-motion.md`
> - Animation timing tokens → `../layer-1-tokens.md`
> - Switch back to Emil (productivity) or Jakub (production) → `./emil-craft.md`, `./jakub-polish.md`
> - reduced-motion universal pattern → `../layer-5-motion.md`, `../layer-2-primitives.md`

---

## Contents

- [When to Apply This Lens](#when-to-apply-this-lens)
- [Easing Reference](#easing-reference)
- [linear() — Pure CSS Spring/Bounce/Elastic](#linear--pure-css-springbounceelastic)
- [animation-fill-mode: backwards](#animation-fill-mode-backwards)
- [Stagger Techniques](#stagger-techniques)
- [@property — Typed CSS Variables](#property--typed-css-variables)
- [3D CSS](#3d-css)
- [Scroll-Driven Animations](#scroll-driven-animations)
- [Motion Paths](#motion-paths)
- [When to Experiment vs Ship](#when-to-experiment-vs-ship)
- [Technique Index](#technique-index)
- [Jhey vs Emil vs Jakub](#jhey-vs-emil-vs-jakub)

---

## When to Apply This Lens

| Use this lens                    | Don't use this lens                |
| -------------------------------- | ---------------------------------- |
| Onboarding completion / confetti | High-frequency tool interactions   |
| Empty-state illustrations        | Error states or serious UI         |
| Portfolio / personal projects    | Professional/enterprise surfaces   |
| Learning a new CSS feature       | Frequently repeated interactions   |
| Kids / educational apps          | Client production without sign-off |

---

## Easing Reference

| Easing        | Feel                    | Good for                              |
| ------------- | ----------------------- | ------------------------------------- |
| `ease-out`    | Fast start, gentle stop | Elements entering view                |
| `ease-in`     | Gentle start, fast exit | Elements leaving view (< 150 ms — acceptable for quick exits only) |
| `ease-in-out` | Gentle both ends        | State changes while visible           |
| `linear`      | Constant speed          | Continuous loops, progress indicators |
| `spring`      | Natural deceleration    | Interactive elements                  |

Elastic/bouncy easing is inappropriate for enterprise apps, error states, and any interaction
users repeat more than a few times per session.

---

## linear() — Pure CSS Spring/Bounce/Elastic

Use `linear()` when you need spring or bounce without a JavaScript animation library.

```css
:root {
  --bounce-easing: linear(
    0,
    0.004,
    0.016,
    0.035,
    0.063,
    0.098,
    0.141 13.6%,
    0.25,
    0.391,
    0.563,
    0.765,
    1,
    0.891 40.9%,
    0.848,
    0.813,
    0.785,
    0.766,
    0.754,
    0.75,
    0.754,
    0.766,
    0.785,
    0.813,
    0.848,
    0.891 68.2%,
    1 72.7%,
    0.973,
    0.953,
    0.941,
    0.938,
    0.941,
    0.953,
    0.973,
    1,
    0.988,
    0.984,
    0.988,
    1
  );
}
```

**Generator:** [linear-easing-generator.netlify.app](https://linear-easing-generator.netlify.app/) (Jake Archibald)

**When not to use:** any surface where bounciness feels unprofessional. Prefer `spring()` in
Web Animations API if you need runtime-parameterized spring physics.

---

## animation-fill-mode: backwards

Without `backwards`, elements with a delayed fade-in flash at full opacity before their
animation starts, then pop invisible, then fade in.

```css
.item {
  animation: fade-in 0.4s ease-out both;
  animation-delay: calc(var(--index) * 80ms);
  /* 'both' = backwards + forwards */
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
}
```

| Mode        | Behavior                                          |
| ----------- | ------------------------------------------------- |
| `forwards`  | Retains final keyframe state after animation ends |
| `backwards` | Holds first keyframe state before delayed start   |
| `both`      | Combines both — almost always what you want       |

**Verify:** add `animation-delay: 1s` and confirm element is invisible during the delay.

---

## Stagger Techniques

`animation-delay` applies once per element, not per iteration.

### Scoped CSS variables (recommended)

```css
.item {
  animation: fade-in 0.4s ease-out both;
  animation-delay: calc(var(--index) * 80ms);
}
```

Set `--index` inline or via `:nth-child` selectors. Keeps one animation definition for all items.

### Padded keyframes for looping stagger

```css
@keyframes pulse {
  0%,
  50% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}
/* offset sibling by half the duration */
.item:nth-child(2) {
  animation-delay: -0.5s;
}
```

### Negative delays for "already in progress"

```css
.item:nth-child(1) {
  animation-delay: 0ms;
}
.item:nth-child(2) {
  animation-delay: -200ms;
}
.item:nth-child(3) {
  animation-delay: -400ms;
}
```

Elements appear mid-animation on load — useful for continuous looping indicators.

**Verify:** all items visible at load (no flash), stagger order correct, reduced-motion collapses delays to 0.

---

## @property — Typed CSS Variables

Without `@property`, custom properties are strings; strings can't interpolate.
With a declared type, the browser smoothly transitions between values.

```css
@property --hue {
  initial-value: 0;
  inherits: false;
  syntax: '<number>';
}

@keyframes rainbow {
  to {
    --hue: 360;
  }
}

.badge {
  background: hsl(var(--hue) 80% 60%);
  animation: rainbow 4s linear infinite;
}
```

**Available syntax types:** `<length>`, `<number>`, `<percentage>`, `<color>`, `<angle>`,
`<time>`, `<integer>`, `<transform-list>`.

**When not to use:** when you only need a value swap (no interpolation needed), a plain custom
property is simpler and has better browser support.

### Decomposed transforms for curved paths

Animate `--x` and `--y` independently to produce curved motion without `offset-path`:

```css
@property --x {
  syntax: '<percentage>';
  initial-value: 0%;
  inherits: false;
}
@property --y {
  syntax: '<percentage>';
  initial-value: 0%;
  inherits: false;
}

.ball {
  transform: translateX(var(--x)) translateY(var(--y));
  animation: throw 1s ease-in-out;
}

@keyframes throw {
  0% {
    --x: -500%;
  }
  50% {
    --y: -250%;
  }
  100% {
    --x: 500%;
  }
}
```

**Verify:** path is curved (parabolic), not a straight diagonal. Check in Chrome DevTools
animation inspector.

---

## 3D CSS

Decompose any 3D scene into cuboids (think LEGO, not sculpture).

```css
.scene {
  transform-style: preserve-3d;
  perspective: 1000px;
}

.cube {
  --size: 10vmin;
  width: var(--size);
  height: var(--size);
  transform-style: preserve-3d;
}

.face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
}
```

Use `vmin` units and CSS variables for all dimensions — makes the scene responsive without media
queries.

**When not to use:** 3D CSS has high GPU cost. Avoid on mobile-first surfaces or inside
scrolling lists. Profile with DevTools Rendering → Paint flashing before shipping.

---

## Scroll-Driven Animations

### The speed-vs-position problem

Scroll-driven animations are controlled by scroll speed. Slow scrollers get slow animations —
feels broken for most UI. The fix: use scroll position to trigger a time-based animation, not
to drive it.

### Duration-control pattern

```javascript
// Progressive enhancement check — required
if (!CSS.supports('animation-timeline', 'scroll()')) {
  // Fall back to IntersectionObserver
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) e.target.classList.add('animate')
    })
  })
  document.querySelectorAll('.animate-on-scroll').forEach((el) => io.observe(el))
}
```

```css
/* Trigger: scroll-driven toggle via custom property */
@keyframes detect {
  from {
    --in-view: 1;
  }
  to {
    --in-view: 1;
  }
}

.item {
  animation: detect linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 20%;
}

/* Main animation: time-based, activated by style query */
@container style(--in-view: 1) {
  .item {
    animation: slide-in 0.4s ease-out both;
  }
}
```

**When not to use:** parallax-for-parallax's-sake. Scroll-driven effects cause motion sickness
in some users — always respect `prefers-reduced-motion`.

---

## Motion Paths

```css
.element {
  offset-path: path('M 0 0 Q 150 -100 300 0');
  offset-distance: 0%;
  animation: move-along 1.5s ease-in-out forwards;
}

@keyframes move-along {
  to {
    offset-distance: 100%;
  }
}
```

For responsive paths, use `offset-path: ray()` or compute the SVG path via JavaScript from
container dimensions.

**Prefer decomposed `@property` transforms** (see above) when the path is simple and you need
wider browser support. Use `offset-path` when you need precise curve control (e.g., following
an SVG layout guide).

---

## When to Experiment vs Ship

| Situation                   | Approach                                  |
| --------------------------- | ----------------------------------------- |
| Learning new CSS feature    | Build something weird, don't filter ideas |
| Portfolio piece             | Push boundaries, show creativity          |
| Personal project            | Follow what interests you                 |
| Onboarding / delight moment | Apply then validate with user testing     |
| Client production work      | Switch to Jakub's production mindset      |
| High-frequency tool UI      | Switch to Emil's restraint mindset        |

---

## Technique Index

| Technique                        | Use when                            | Key detail                                             |
| -------------------------------- | ----------------------------------- | ------------------------------------------------------ |
| `linear()`                       | Need spring/bounce without JS       | Generate values at linear-easing-generator.netlify.app |
| `@property`                      | Need to interpolate a CSS variable  | Declare syntax type or interpolation won't work        |
| `animation-fill-mode: backwards` | Delayed fade-ins                    | Prevents opacity flash before delay elapses            |
| Negative delays                  | Looping stagger, "in progress" look | Starts animation mid-cycle on load                     |
| Scoped CSS variables             | Per-item stagger index              | One animation rule, set `--index` per element          |
| 3D CSS                           | Cuboid scenes, card flips           | `preserve-3d` + `perspective` on parent; profile GPU   |
| Scroll-driven                    | Trigger on scroll position          | Decouple speed with style query + time-based anim      |
| Motion paths                     | Curved element travel               | `offset-path` or decomposed `@property` transforms     |

---

## Jhey vs Emil vs Jakub

| Aspect              | Jhey                       | Emil                      | Jakub                         |
| ------------------- | -------------------------- | ------------------------- | ----------------------------- |
| Focus               | Playful experimentation    | Restraint and speed       | Subtle production polish      |
| Key question        | "What could this become?"  | "Should this animate?"    | "Is this subtle enough?"      |
| Signature technique | `@property` + `linear()`   | Frequency-based decisions | Blur + opacity + translateY   |
| Ideal context       | Learning, delighters, play | High-frequency tool UIs   | Any shipped production screen |

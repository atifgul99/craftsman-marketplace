# 07b — Jakub Krehel's Production Polish

Jakub Krehel (jakub.kr) — subtle motion for shipped products. Apply in: consumer apps, professional/enterprise interfaces, repeat-use contexts where polish matters but flash distracts. Aim: users feel smoothness, never notice animation.

> **See also**
>
> - Motion audit framework + context routing → `../layer-5-motion.md`
> - Emil's restraint for high-frequency UIs → `./emil-craft.md`
> - Jhey's playfulness for creative/learning contexts → `./jhey-experimental.md`
> - Motion timing tokens → `../layer-1-tokens.md`

---

## Contents

- [Lens](#lens)
- [Enter / Exit Recipe](#enter--exit-recipe)
- [Spring Config](#spring-config)
- [Shadows over Borders](#shadows-over-borders)
- [oklch Gradients](#oklch-gradients)
- [Optical Alignment](#optical-alignment)
- [Icon Swap Animation](#icon-swap-animation)
- [Shared Layout (FLIP)](#shared-layout-flip)
- [Performance: will-change and Gradients](#performance-will-change-and-gradients)
- [Common Mistakes](#common-mistakes)
- [Technique Index](#technique-index)
- [Jakub vs Emil vs Jhey](#jakub-vs-emil-vs-jhey)

---

## Lens

Apply Jakub's approach when:

- The animation decision has already passed Emil's gate (something should animate)
- Context is production work — client-facing, repeated daily use
- Failure mode is distraction, not boredom

---

## Enter / Exit Recipe

Canonical materializing enter — opacity + translateY + blur together:

```jsx
// Enter
initial={{ opacity: 0, translateY: 8, filter: "blur(4px)" }}
animate={{ opacity: 1, translateY: 0, filter: "blur(0px)" }}
transition={{ type: "spring", duration: 0.45, bounce: 0 }}
```

Blur creates a "materializing" effect (element comes into focus, not just fades in). Used by Family, Linear, Vercel.

For full container slides, replace `translateY: 8` with `translateY: "calc(-100% - 4px)"`.

**Exit must be subtler than enter.** User focus moves to what arrives, not what leaves:

```jsx
// Exit — less movement, same blur signal
exit={{ translateY: "-12px", opacity: 0, filter: "blur(4px)" }}
```

Exceptions: user-initiated dismissal, item deletion, full-page transitions where direction matters.

---

## Spring Config

| Use case            | Config                                            | Notes                       |
| ------------------- | ------------------------------------------------- | --------------------------- |
| Production default  | `{ type: "spring", duration: 0.45, bounce: 0 }`   | Smooth decel, no overshoot  |
| Slightly more life  | `{ type: "spring", duration: 0.55, bounce: 0.1 }` | Still professional          |
| Playful (non-Jakub) | `bounce: 0.3+`                                    | Use Emil/Jhey contexts only |

`bounce: 0` is the production default. Reserve positive bounce for explicitly playful UI moments.

---

## Shadows over Borders

In light mode on dynamic backgrounds (images, gradients), prefer multi-layer `box-shadow` over solid borders. Shadows adapt via transparency; borders clash.

```css
.card {
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.06),
    0 1px 2px -1px rgba(0, 0, 0, 0.06),
    0 2px 4px 0 rgba(0, 0, 0, 0.04);
}

.card:hover {
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.08),
    0 1px 2px -1px rgba(0, 0, 0, 0.08),
    0 2px 4px 0 rgba(0, 0, 0, 0.06);
}
```

| Context                        | Recommendation                     |
| ------------------------------ | ---------------------------------- |
| Light mode, varied backgrounds | Multi-layer shadow                 |
| Dark mode                      | Border fine (shadows less visible) |
| Hard edges intentional         | Border fine                        |

---

## oklch Gradients

Use `oklch` color space to avoid muddy gray midpoints when blending complementary colors:

```css
.element {
  background: linear-gradient(in oklch, blue, red);
}
```

sRGB interpolation passes through a desaturated gray zone on complementary pairs. `oklch` interpolates through perceptually uniform space — vivid across the entire range.

Use color hints (not just stops) to control blend midpoint position. Layer gradients with `background-blend-mode` for depth.

---

## Optical Alignment

Mathematical centering and visual centering diverge on asymmetric shapes. Trust your eyes.

**Buttons with icons** — icon glyphs have internal whitespace; reduce padding on the icon side:

```
[  Icon Text  ]  ← Geometric (feels off)
[ Icon Text   ]  ← Optical (feels right)
```

**Play buttons** — triangle points right, creating visual weight left. Shift glyph 1–2px right so it reads as centered.

Rule: if it looks wrong and the math says correct, adjust the math.

---

## Icon Swap Animation

When icon changes state (copy → check, loading → done), animate with `AnimatePresence mode="wait"`:

```jsx
<AnimatePresence mode="wait">
  {isCopied ? (
    <motion.div
      key="check"
      initial={{ opacity: 0, scale: 0.8, filter: 'blur(4px)' }}
      animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
      exit={{ opacity: 0, scale: 0.8, filter: 'blur(4px)' }}
      transition={{ type: 'spring', duration: 0.3, bounce: 0 }}
    >
      <CheckIcon />
    </motion.div>
  ) : (
    <motion.div
      key="copy"
      initial={{ opacity: 0, scale: 0.8, filter: 'blur(4px)' }}
      animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
      exit={{ opacity: 0, scale: 0.8, filter: 'blur(4px)' }}
      transition={{ type: 'spring', duration: 0.3, bounce: 0 }}
    >
      <CopyIcon />
    </motion.div>
  )}
</AnimatePresence>
```

Instant icon swaps feel jarring and go unregistered. The animated transition confirms the action.

---

## Shared Layout (FLIP)

Motion's `layoutId` drives FLIP transitions (First, Last, Invert, Play) between any two components:

```jsx
// Small card view:
<motion.div layoutId="card" className="small-card" />

// Expanded view:
<motion.div layoutId="card" className="large-card" />
```

Motion auto-animates between sizes, positions, and component types.

**Rules:**

- Keep `layoutId` elements outside `AnimatePresence` — nesting triggers conflicting initial/exit animations
- Each element needs a unique `layoutId`
- Works across height, width, position, and element type

---

## Performance: will-change and Gradients

### will-change

Declare before animation starts to avoid first-frame stutter (browser needs time to promote to GPU layer):

```css
/* Correct — specific properties */
.animated-card {
  will-change: transform, opacity;
}

/* Wrong — wastes GPU memory */
.element {
  will-change: all;
}
```

Safe to declare: `transform`, `opacity`, `filter`, `clip-path`, `mask`.

Only set on elements that will animate. Each GPU layer consumes memory — don't scatter it.

### Gradient animation

| Property                                             | Cost                    |
| ---------------------------------------------------- | ----------------------- |
| `background-position`, `background-size`, `opacity`  | Cheap — GPU             |
| Color stops, adding/removing layers, switching types | Expensive — CPU repaint |

For animated gradients: animate `background-position` on an oversized gradient, or transition a pseudo-element overlay.

---

## Common Mistakes

| Mistake                                   | Fix                                           |
| ----------------------------------------- | --------------------------------------------- |
| Exit as prominent as enter                | Exit at half the movement and duration        |
| Solid border on image/gradient background | Multi-layer shadow adapts via transparency    |
| Geometric centering on asymmetric icons   | Adjust padding/position optically             |
| Hover state changes instant               | Add 150–200 ms transition on all hover states |
| `will-change: all`                        | Declare specific properties only              |
| Animating gradient color stops            | Animate `background-position` instead         |

---

## Technique Index

| Technique          | Key insight                                            |
| ------------------ | ------------------------------------------------------ |
| Enter animation    | opacity + translateY(8px) + blur(4px) → all to default |
| Exit animation     | Subtler than enter — less movement, same blur signal   |
| Spring config      | `duration: 0.45, bounce: 0` for production             |
| Shadows vs borders | Multi-layer shadow adapts to any background            |
| oklch gradients    | Perceptually uniform — no muddy midpoints              |
| Optical alignment  | Trust eyes over math on asymmetric shapes              |
| Icon swap          | AnimatePresence mode="wait" + opacity + scale + blur   |
| Shared layout      | layoutId + FLIP; keep outside AnimatePresence          |
| will-change        | Specific properties only; set before animation         |
| Gradient perf      | Animate position/size not color stops                  |

---

## Jakub vs Emil vs Jhey

| Aspect              | Jakub                       | Emil                          | Jhey                      |
| ------------------- | --------------------------- | ----------------------------- | ------------------------- |
| Focus               | Subtle production polish    | Restraint & frequency         | Playful experimentation   |
| Key question        | "Is this subtle enough?"    | "Should this animate at all?" | "What could this become?" |
| Signature technique | blur + opacity + translateY | Frequency-based gate          | CSS custom properties     |
| Ideal context       | Shipped consumer/pro apps   | High-frequency tools          | Learning & creative       |

Use Jakub after Emil's gate passes — when the decision to animate is made and the goal is production-ready feel.

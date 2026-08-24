# 07d — Fluid Gestures & Momentum Physics

The physics that make gesture-driven UI feel grabbed rather than played: velocity handoff,
momentum projection, rubberbanding, and interruptible springs. Apple's fluid-interface model
(chiefly *Designing Fluid Interfaces*, WWDC 2018) translated for the web.

> **Source note:** portions adapted from Emil Kowalski's MIT-licensed skill repo — see
> `THIRD_PARTY_NOTICES.md` at the repo root for the full license. Apple WWDC talks are the
> conceptual source. Not affiliated with or endorsed by Emil Kowalski or Apple.

> **Scope guard:** this file applies to **gesture-driven surfaces** — draggable sheets and
> drawers, swipe-to-dismiss, carousels, touch-first mobile web, and marketing interactions with
> real physics. A plain SaaS dashboard with buttons and dropdowns does not need momentum
> projection; for that, `emil-craft.md`'s restraint rules are the standard. Prescribing this
> file's physics on non-gesture UI is a scope misfire.

> **See also**
>
> - When to animate at all, easing, durations, springs baseline → `emil-craft.md`
> - Motion audit framework and accessibility floor → `../layer-5-motion.md`
> - Compositor/main-thread performance mechanics → `../layer-2-primitives.md` → Animation under Load

---

## Contents

- [Response — Kill Latency](#response--kill-latency)
- [Direct Manipulation — 1:1 Tracking](#direct-manipulation--11-tracking)
- [Interruptibility](#interruptibility)
- [Springs: Damping and Response](#springs-damping-and-response)
- [Velocity Handoff](#velocity-handoff)
- [Momentum Projection](#momentum-projection)
- [Rubberbanding](#rubberbanding)
- [Gesture Feel Checklist](#gesture-feel-checklist)
- [Materials and Translucency](#materials-and-translucency)
- [Reduced Motion for Gestures](#reduced-motion-for-gestures)
- [Quick Reference](#quick-reference)

---

## Response — Kill Latency

The moment lag appears, the feeling of directness collapses.

- **Feedback on pointer-down, not on release.** Highlight the instant of press; waiting for
  `click`/touch-up reads as dead.
- **Feedback is continuous *during* the interaction.** A drag, slider, or drawer updates 1:1
  with the pointer the whole way — never only when the gesture completes.
- **Audit the input path.** Debounces, artificial timers, and transition waits on the input path
  are regressions.

---

## Direct Manipulation — 1:1 Tracking

When the user drags something it stays glued to the finger — respecting **where they grabbed
it**. Snapping to the element's center on grab breaks the illusion immediately.

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId); // tracking continues outside element bounds
  const grabOffset = e.clientY - el.getBoundingClientRect().top;
  // keep a short position+timestamp history — you need velocity at release
});
```

---

## Interruptibility

Every gesture animation must be grabbable and reversible mid-flight. A closing sheet the user
grabs again follows the finger — it does not finish closing first.

- **Never lock input during a transition.**
- **Animate from the presentation (live) value, never the target.** On interrupt, read the
  element's current on-screen transform and start there; starting from the logical target causes
  a visible jump.
- **Blend velocity on reversal.** Hard-cutting to a new animation creates a velocity
  discontinuity — a "brick wall". Use a spring library that carries velocity through a re-target.
- **Decompose 2D motion into independent X and Y springs.** One spring on a 2D distance desyncs
  when the axes have different velocities.
- **Avoid CSS transitions/keyframes for gesture-driven motion** — they can't be smoothly grabbed
  mid-flight. (For non-gesture rapid triggers like toasts, transitions remain correct — see
  `emil-craft.md`.)

---

## Springs: Damping and Response

Think in two designer-friendly parameters instead of the mass/stiffness/damping triplet:

- **Damping ratio** — overshoot control. `1.0` = critically damped, no bounce. `< 1.0` =
  overshoots; lower is bouncier.
- **Response** — roughly how fast the value approaches the target, in seconds. Not a duration:
  a spring's settle time emerges from its parameters.

**The rule that prevents most spring misuse: bounce only when the gesture itself carried
momentum.** Overshoot on a menu that faded in feels wrong; overshoot on a card the user flicked
feels right. Default everything else to critically damped.

Apple-style reference values (starting points, not gospel):

| Interaction              | Damping | Response |
| ------------------------ | ------- | -------- |
| Move / reposition        | 1.0     | 0.4      |
| Rotation                 | 0.8     | 0.4      |
| Drawer / sheet           | 0.8     | 0.3      |

Motion/Framer Motion mapping: `{ type: "spring", bounce: 0, duration: 0.4 }` ≈ critically
damped; `bounce: 0.2` for momentum interactions.

---

## Velocity Handoff

When a gesture ends, the animation **continues at the finger's exact velocity** — this seam is
what separates "fluid" from "fine". Pass the release velocity into the spring.

- Motion/Framer Motion take **raw px/s** directly (the `velocity` option).
- Some spring APIs want **normalized** velocity relative to remaining distance:
  `relativeVelocity = gestureVelocity / (target − current)` — e.g. at `y=50` heading to
  `y=150` at 50 px/s → `0.5`. Check which form your library expects.

---

## Momentum Projection

Don't snap to the nearest boundary from the *release point* — project where the flick was
**going**, then snap to the target nearest that projected point. This is what makes a fast short
swipe commit while a slow long one doesn't (the standard behavior in good bottom sheets and
carousels — Vaul, Embla).

```js
// Exponential-decay projection — NOT the physics-textbook v²/(2·decel).
// decelerationRate ≈ 0.998 for normal scroll feel; 0.99 for snappier.
function project(initialVelocity /* px/s */, decelerationRate = 0.998) {
  return ((initialVelocity / 1000) * decelerationRate) / (1 - decelerationRate);
}

const projectedEndpoint = currentPosition + project(releaseVelocity);
const target = nearestSnapPoint(projectedEndpoint);
animateSpringTo(target, { velocity: releaseVelocity }); // then hand off velocity
```

Related: decide **reverse vs. commit from the velocity's sign at release**, not from position —
a sheet dragged 80% open but moving downward should close.

---

## Rubberbanding

At a boundary, resist progressively instead of stopping hard. A hard stop reads as "frozen";
rising resistance reads as "responsive, but there's nothing more here".

```js
// The further past the bound, the less the element follows.
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

---

## Gesture Feel Checklist

- [ ] Highlight on touch-**down**, commit on touch-**up**; allow cancel by dragging away and back
- [ ] ~10 px hysteresis before committing to a drag direction; ~10 px hit padding around small targets
- [ ] Grab offset respected (no snap-to-center on grab)
- [ ] Pointer capture active for the whole drag
- [ ] Extra touch points ignored once a drag begins
- [ ] Detect plausible gestures **in parallel** from the first move, then cancel the losers —
      avoid recognizers that only report a final state (`swipeleft`-style events discard the
      continuous tracking feedback needs)
- [ ] Disambiguation delays only where the competing gesture truly exists (double-tap detection
      delays every single tap)
- [ ] Dismissal uses velocity, projection, and rubberbanding — not distance thresholds alone

---

## Materials and Translucency

**Scope: material/glass surfaces only** (sheets, overlays, floating chrome on content-rich or
media pages) — not default SaaS chrome.

- **Never stack a light translucent surface on another** — legibility collapses. Material weight
  encodes hierarchy: heavier/darker separates structure, lighter draws attention.
- **Vibrancy keeps text legible over blur:** higher contrast, slightly heavier weight, a small
  letter-spacing bump — and put color on a solid layer, not the translucent foreground.
- **Scroll-edge fade beats a 1 px divider** under floating headers: a small blur/gradient mask
  only where chrome overlaps content.
- **Materialize, don't just fade:** glass surfaces animate blur radius and scale together on
  enter/exit so they arrive as a material, not an opacity swap.
- Honor `prefers-reduced-transparency: reduce` (solid fallback) — see `../layer-5-motion.md`.

---

## Reduced Motion for Gestures

Under `prefers-reduced-motion: reduce`, gesture *feedback* survives but travel dies: replace
slides/springs/parallax with short opacity cross-fades, drop elastic overshoot, keep the 1:1
drag tracking itself (it's user-driven, not vestibular). Full accessibility floor in
`../layer-5-motion.md`.

---

## Quick Reference

| Need                          | Technique                                   | Value                                      |
| ----------------------------- | ------------------------------------------- | ------------------------------------------ |
| Default UI spring             | Critically damped                           | damping 1.0, response 0.3–0.4              |
| Momentum/flick spring         | Slight bounce (gesture carried momentum)    | damping ~0.8, response 0.3–0.4             |
| Flick landing point           | Momentum projection                         | `(v/1000)·d/(1−d)`, d ≈ 0.998              |
| Boundary                      | Rubberband, not hard stop                   | constant ≈ 0.55                            |
| Gesture → spring seam         | Velocity handoff                            | raw px/s (Motion); normalized for some APIs |
| Interrupt cleanly             | Animate from presentation value             | read the live on-screen transform          |
| Reverse vs. commit            | Velocity **sign** at release                | not position                               |
| Drag start                    | Hysteresis                                  | ~10 px                                     |
| Press feedback                | On pointer-down                             | instant, continuous                        |

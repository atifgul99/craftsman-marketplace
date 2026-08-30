# Composition — Pages, Dashboards & Creative Arsenal

How the layers assemble into whole screens — dashboard architecture, landing-page anatomy, and the distinctive-layout techniques that avoid generic AI "slop".

> **craft-ux tie-in:** Before imposing any layout paradigm, read the repo's existing page shells and layout wrappers first (`Glob **/layout.tsx` or equivalent) to understand the grid and nav chrome already in place.

> **See also**
>
> - Spacing, typography, and color tokens → [layer-1-tokens.md](layer-1-tokens.md)
> - Component-level patterns (forms, modals, buttons, pricing tier rules) → [layer-3-components.md](layer-3-components.md)
> - Implementation guidance and primitive usage → [layer-2-primitives.md](layer-2-primitives.md)
> - Anti-patterns to avoid → [anti-patterns.md](anti-patterns.md)
> - Motion patterns (springs, clip-path, scroll sequences) → [layer-5-motion.md](layer-5-motion.md)

---

## Part 1 — Page & Dashboard Patterns

---

### SaaS Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│ Top Bar (56–64 px): logo, search, user menu             │
├──────────┬──────────────────────────────────────────────┤
│ Sidebar  │  Main content area                            │
│ 240–280  │  (breadcrumbs if depth > 2)                   │
│ collapsed│                                               │
│  64–80   │  Cards / data / forms                         │
│          │                                               │
└──────────┴──────────────────────────────────────────────┘
```

For the navigation-pattern-by-hierarchy table (sidebar vs top nav vs tabs vs breadcrumbs), see
[layer-3-components.md](layer-3-components.md) → Navigation. Sidebar collapse state persists across
sessions; active state visually distinct from hover.

---

### Dashboard Content Hierarchy

1. **Value-first metrics.** "You saved 4 hours" > raw numbers. Surface insight, not data.
2. **Actionable insights.** Every metric should imply a next action.
3. **Progressive disclosure.** Summary → detail on demand. Don't dump 50 fields on a card.
4. **Role-based views.** Different personas need different data on the same dashboard. Don't
   build one giant dashboard for everyone.
5. **Time-to-first-value.** New users land and immediately see what to do. Empty dashboard with
   no CTA = activation bleeding.

---

### Data Visualization

- Use semantic colors: red = negative, green = positive
- Pattern/icon backup for colorblind accessibility (don't rely on color alone)
- Always include legends
- Axis labels are mandatory
- Truncate long labels with tooltips
- Numeric columns use `font-variant-numeric: tabular-nums`
- Empty state when filters return zero results

---

### Empty States (Dashboard)

For the base empty-state pattern (icon + headline + description + CTA), see
[layer-4-states.md](layer-4-states.md) → Empty States. Dashboard-specific application:

- **Brand-new account:** design a composed "getting started" view that walks the user to
  activation — not just an icon and a button.
- **Filtered list returning zero:** explain what filter is hiding results and offer a one-click
  "clear filters" action.
- The dashboard empty state is your single highest-leverage onboarding surface. Treat it as a
  feature, not a placeholder.

---

### Settings Pages

See [layer-3-components.md](layer-3-components.md) → Settings Pages for the canonical bucket +
side-panel layout and Danger Zone rules.

---

### Toast / Notification Timing

See [layer-3-components.md](layer-3-components.md) → Notifications, Toasts, and Tooltips for the
canonical timing formula, stacking rules, and dismissal behavior.

---

### URL State for Dashboards

URL must reflect:

- Active filters
- Current tab
- Pagination
- Expanded panels
- Search query

Use `nuqs` or equivalent. Users expect to share URLs and have the recipient see the same view.

---

### Landing Page Sections (Standard Flow)

```
1. Hero (headline + subheadline + CTA + visual)
2. Social proof (logo bar, testimonial snippet)
3. Problem / Solution
4. Features / Benefits (3–4 max)
5. Detailed testimonials
6. Pricing (if applicable)
7. FAQ
8. Final CTA
9. Footer
```

For footer legal-link reachability and consent-banner rules, see
[layer-3-components.md](layer-3-components.md) → Footer Legal Links & Consent Banners.

---

### Above the Fold

Within the initial viewport, the user must see:

1. Clear headline (5–10 words)
2. Supporting subheadline (value proposition, one sentence)
3. **Single** primary CTA
4. Visual element (hero image, illustration, or product shot)

No surprises below the fold — if the value isn't visible in 3 seconds, the visitor bounces.

**Hero discipline (hard numbers — soft prose fails with generators):**

- Headline ≤ 2 lines at desktop; subtext ≤ 20 words *and* ≤ 4 lines. If the value prop needs
  more than 20 words, the value prop is unclear — not the rule too tight.
- Plan font scale and asset size *together*: `text-4xl md:text-5xl lg:text-6xl` for most heroes;
  `text-6xl`+ only for 3–5-word headlines. A 4-line hero headline is a font-size error, never a
  copy-length error.
- Max **4 text elements** total: (eyebrow *or* brand strip — zero or one), headline, subtext,
  CTAs (1 primary + max 1 secondary). Taglines under the CTAs, trust micro-strips, pricing
  teasers, and feature bullets all move to sections below the hero.
- Hero top padding caps at ~6 rem (`pt-24`) desktop — more and the content floats halfway down
  the viewport and reads as a bug. Need breathing room? Scale the type or asset, not the padding.
- The "Trusted by" logo wall lives in its own section **under** the hero, never inside it.
- A hero needs a real visual — text + gradient blob is a placeholder, not a hero.

---

### CTA Button Design

For universal button rules (touch target, copy patterns, transitions), see
[layer-3-components.md](layer-3-components.md) → Buttons. Landing-page-specific:

- **Padding:** ~2× the CTA font size (oversized vs in-app buttons)
- **Color:** high contrast against the section background; warm colors create urgency
- **Frequency:** one primary CTA per viewport. Secondary CTAs are ghost or text style — never
  two equally-weighted CTAs side by side
- **Hierarchy:** if a secondary action exists (e.g. "watch demo"), it must look distinctly
  secondary — not just a different color of the same shape
- **One label per intent:** "Get in touch", "Contact us", and "Let's talk" on one page are the
  same action wearing three labels — pick one and reuse it in nav, hero, and footer
- **No wrapping:** a primary CTA label wraps at desktop → shorten it (1–3 words) or widen the
  button; never constrain a CTA's `max-width`
- **Contrast check before shipping:** every CTA's text passes WCAG AA against its own background
  (ghost buttons over photos need a scrim, backdrop, or stroke) — same check for form inputs,
  placeholders, and focus rings against their section background

---

### Social Proof Placement

- **Logo bar:** immediately after hero
- **Testimonials:** near points of objection (next to pricing, on long-form sections)
- **Stats:** near pricing
- **Trust badges:** near forms and checkout

---

### Pricing Tables (Landing-Page)

See [layer-3-components.md](layer-3-components.md) → Pricing Tables for the canonical tier rules
(max count, highlight method, toggle, alignment). On a landing page specifically, also:

- Place near a testimonial block (objection-handling proximity)
- Annual/monthly toggle defaults to whichever yields the better headline price
- Stats and trust badges adjacent to the table, not buried in the footer

---

### Form Optimization for Conversion

For the canonical form rules (single column, label position, blur validation, placeholder
patterns) see [layer-3-components.md](layer-3-components.md) → Forms. Landing-page-specific
conversion data:

- Single-column forms complete faster with fewer skipped fields than multi-column; every optional
  field costs completions — the phone field is the classic offender. Cut anything you won't act on.

---

### Layout Variety (Anti-AI-Layout)

Avoid the three default AI-generated landing layouts:

1. **Three equal-width feature card columns** — most generic. Replace with:
   - Zig-zag rows (image+text alternating sides)
   - Asymmetric grid (one large + two small)
   - Horizontal scroll
   - Masonry layout
2. **Centered hero with text over dark image** — try:
   - Split-screen (left text, right visual)
   - Left-aligned asymmetric (visual breaks the column on the right)
3. **Three-tower pricing** — highlight the recommended tier with **color + emphasis**, not extra
   height alone

**Rhythm caps** (mechanical versions of "vary the layout"):

- Max 2 consecutive image+text zigzag sections — break the third with a full-width section,
  bento, marquee, or vertical stack
- A layout family (3-col cards, full-width quote, split image+text) appears at most once per
  page; 8 sections need ≥ 4 distinct families
- Max 1 marquee per page
- Section headers stack vertically (headline, then body at `max-w-[65ch]`) — the "left big
  headline + right floating explainer" split-header is a tell unless the right column carries a
  real visual
- Bento grids: exactly as many cells as there is content (re-shape rather than pad with a blank
  tile), and 2–3 cells minimum get real visual variation — an all-white-text-card bento is the
  boring default
- Desktop nav: one line, 64–72 px tall (80 px hard cap)
- **Page-level locks:** one theme (no mid-page light/dark flips), one accent color used
  identically in every section, one corner-radius system — see `anti-patterns.md` →
  Composition Anti-Patterns for the flag-side versions

---

### Above-the-Fold Performance

- LCP under 2.5 s
- CLS under 0.1
- INP under 200 ms
- Hero image: explicit dimensions, `priority`/`fetchpriority="high"`, optimized format
- Fonts: `next/font` (or framework equivalent) with `font-display: swap`
- Preconnect to CDN/asset domains
- Above-fold should render before any heavy client JS hydrates

---

### Spacing for Landing

- Section spacing: 80–120 px between major sections
- Section header → content gap consistent across sections
- Aggressive whitespace beats density on marketing pages
- Cap content width around 1200–1440 px with auto margins for ultrawide screens

---

## Part 2 — Creative Arsenal & Design Intensity

Named patterns to replace generic AI defaults. Use these when "make it distinctive" is part of
the brief or when redesigning generic interfaces. Always verify library availability before use.

> **See also**
>
> - Generic patterns being replaced → [anti-patterns.md](anti-patterns.md)
> - Motion patterns inside these moves → [layer-5-motion.md](layer-5-motion.md)

---

### Design Intensity Calibration

**Declare a one-line Design Read before generating anything:** *"Reading this as: \<page kind>
for \<audience>, with a \<vibe> language, leaning toward \<design system or aesthetic family>."*
Most bad AI design output comes from jumping to a default aesthetic instead of reading the brief
— audience, vibe words, reference URLs, and existing brand assets pick the aesthetic, not your
taste. If the read genuinely diverges, ask exactly one clarifying question; otherwise declare
and proceed.

Set these before coding so the rest of the work has a consistent personality:

- **`DESIGN_VARIANCE` 1–10:** 1 = perfect symmetry, 10 = artsy chaos. Default: 8 for marketing,
  4 for product UI.
- **`MOTION_INTENSITY` 1–10:** 1 = static CSS only, 10 = cinematic spring physics. Default: 6
  for marketing, 3 for SaaS.
- **`VISUAL_DENSITY` 1–10:** 1 = art gallery airy, 10 = cockpit packed data. Default: 4 for
  SaaS app, 2 for landing.

At density 8+, box cards are banned — use `border-t` / `divide-y` / negative space instead.

---

### Aesthetic Direction Library

Choose and commit to one. Timid design fails. Options:

- **Brutally minimal** (Stripe, Linear)
- **Maximalist editorial** (Bloomberg, Awwwards winners)
- **Retro-futuristic** (Y2K revival, vaporwave)
- **Organic / natural** (earthy, hand-drawn, textured)
- **Luxury / refined** (fashion houses, premium brands)
- **Playful / toy-like** (Figma, Notion)
- **Neo-brutalist** (raw, exposed, intentionally rough)
- **Art deco / geometric** (bold shapes, gold accents)
- **Soft / pastel** (gradient meshes, dreamy)
- **Industrial / utilitarian** (data-dense, functional)

**The memorability test:** what ONE thing will users remember? If you can't answer, the design
lacks focus.

---

### Navigation Patterns

- **Mac OS Dock magnification** — items grow under cursor
- **Magnetic buttons** (Framer `useMotionValue`) — buttons drift slightly toward the cursor
- **Dynamic Island pill** — collapsible status surface
- **Contextual radial menu** — actions arc out from cursor
- **Mega menu with staggered reveal** — multi-column expanding nav

---

### Layout Patterns

- **Bento grid** — asymmetric tiles (see Bento 2.0 section below)
- **Masonry layout** — variable heights, packed efficiently
- **Split-screen scroll** — halves move opposite directions
- **Broken grid** — elements deliberately overlap/bleed off-screen
- **Parallax card stacks** — sticky elements that stack on scroll

---

### Card Patterns

- **Parallax tilt card** — 3D mouse tracking on card surface
- **Spotlight border** — border illuminates under cursor
- **True glassmorphism** — `backdrop-filter: blur` + 1 px `border-white/10` inner border +
  inner shadow (not just blur — that alone looks fake)
- **Holographic foil** — iridescent gradient on hover
- **Morphing modal** — button expands into the dialog

---

### Scroll Patterns

- **Horizontal scroll hijack** — vertical scroll becomes horizontal in a section
- **Zoom parallax** — background zooms in/out with scroll
- **Scroll progress SVG path draw** — line draws along the path as user scrolls
- **Locomotive scroll sequence** — video framerate tied to scroll position
- **Curtain reveal** — hero parts like a curtain on scroll

---

### Typography Patterns

- **Kinetic marquee** — reverses direction on scroll
- **Text mask reveal** — typography as a window to video or animated imagery
- **Text scramble** — Matrix-style decode on hover
- **Gradient stroke animation** — gradient runs along the text stroke outline
- **Variable font animation** — interpolate weight or width on scroll/hover

---

### Micro-Interactions

- **Particle explosion button** — CTA shatters into particles on success
- **Directional hover-aware button** — fill enters from the direction the mouse approached
- **Ripple from click coordinates** — Material-style ripple originating from the click point
- **Mesh gradient background** — animated lava-lamp blobs
- **Skeleton shimmer** — light reflection moving across the placeholder
- **Spring-physics drag** — items move with weight on drag

---

### Performance Notes for Creative Patterns

- Use **Framer Motion** for UI / Bento / micro-interactions
- Use **GSAP** or **Three.js** exclusively for full-page scroll-telling or canvas backgrounds —
  never mix them in the same component tree
- Grain / noise overlays: apply only to `fixed pointer-events-none` pseudo-elements, never to
  scrolling containers (GPU repaint cost)
- Perpetual animations must be isolated in their own `"use client"` leaf component to prevent
  parent re-renders

---

### Bento 2.0 Dashboard Paradigm

For SaaS dashboards and feature sections, use this architecture instead of generic card grids.

**Token preamble:** The palette values below use raw hex and palette classes as concrete examples
for visual spec only. Translate all values to semantic design tokens from your token layer
(`layer-1-tokens.md`) before implementing — never ship raw hex or `bg-[#hex]` Tailwind
arbitrary-value classes in production code; they bypass the token system and break dark-mode,
theming, and future palette changes.

#### Aesthetic baseline

- Page: `bg-[#f9fafb]`
- Cards: pure white (`bg-white border border-slate-200/50`)
- Containers: `rounded-[2.5rem]`
- Shadows: diffusion (`shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]`)
- Padding: `p-8` or `p-10`
- Labels: **outside and below** cards, not inside

#### Typography

Geist, Satoshi, or Cabinet Grotesk only. `tracking-tight` for headers.

#### The 5 card archetypes (with perpetual motion)

1. **Intelligent List** — infinite auto-sort loop using Framer `layoutId`. Items swap positions
   simulating AI prioritization.
2. **Command Input** — AI search bar cycling through prompts via typewriter effect with blinking
   cursor and shimmer loading state.
3. **Live Status** — scheduling view with "breathing" status dots. Notification badge appears
   with overshoot spring (`stiffness: 400, damping: 10`), stays 3 s, vanishes.
4. **Wide Data Stream** — seamless horizontal carousel (`x: ["0%", "-100%"]`) of metrics at
   effortless speed.
5. **Focus Mode** — document view with staggered text highlight, then float-in action toolbar.

#### Motion rules for all cards

- Spring physics only: `type: "spring", stiffness: 100, damping: 20`
- Every card has an infinite loop state (pulse, typewriter, float, or carousel) so the
  dashboard feels alive
- Wrap dynamic lists in `<AnimatePresence>`
- Perpetual animations: `React.memo` + isolated Client Component — never trigger parent
  re-renders
- Use `layout` and `layoutId` for smooth re-ordering and shared element transitions

---

### Decision Helper: Which Pattern to Pick

| Brief                           | Suggested patterns                                                      |
| ------------------------------- | ----------------------------------------------------------------------- |
| "Make the dashboard feel alive" | Bento 2.0 + Live Status + Wide Data Stream                              |
| "Hero feels generic"            | Split-screen scroll + Variable font animation, or Text mask reveal      |
| "Features section is boring"    | Bento grid (asymmetric tiles), or zig-zag rows                          |
| "CTA needs more weight"         | Particle explosion or Magnetic button                                   |
| "Onboarding needs delight"      | Skeleton shimmer + staggered entry + Spring-physics drag                |
| "Pricing feels samey"           | Holographic foil on recommended tier, color emphasis (not extra height) |

---

### What to Avoid (Even When Going Creative)

- **More than one signature pattern per page.** Pick one memorable thing. The rest supports it.
- **Animations on high-frequency interactions** — see [layer-5-motion.md](layer-5-motion.md).
- **Decoration without purpose.** Every creative pattern must serve workflow, brand, or
  comprehension — never "it looks cool".
- **Library conflicts.** GSAP + Framer Motion + Three.js in one tree = janky and bloated.
  Pick the right one for the job.

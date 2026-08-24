# Anti-Patterns — The AI-Tells Catalog

What betrays AI-generated or low-craft UI. This is the checklist Layer reviews and the review-protocol flag against.

Pair this with [review-protocol.md](review-protocol.md) — this is the WHAT-to-flag, that is the HOW-to-structure-the-review.

---

## Contents

- [Visual AI Tells](#visual-ai-tells) — color, typography, layout, depth
- [Content Anti-Patterns](#content-anti-patterns) — the "Jane Doe" effect
- [Copy & Decoration Tells](#copy--decoration-tells-landing--portfolio--marketing) — em-dashes, eyebrows, micro-labels, decoration strips
- [UX Anti-Patterns](#ux-anti-patterns) — dark patterns, missing states
- [Technical Anti-Patterns](#technical-anti-patterns) — code-level failures
- [Mobile Anti-Patterns](#mobile-anti-patterns)
- [Strategic Omissions](#strategic-omissions) — what AI forgets
- [Composition Anti-Patterns](#composition-anti-patterns)
- [Code Quality Anti-Patterns](#code-quality-anti-patterns)
- [Quick-Reject Checklist](#quick-reject-checklist-for-code-review) — for code review

---

## Visual AI Tells

The most common fingerprints of unedited AI-generated UI.

- **Purple/blue gradient on white.** Most common AI fingerprint. Banned. Use neutral bases +
  single considered accent.
- **`Inter` as display font.** The default AI font choice. Banned. Use Geist, Outfit, Cabinet
  Grotesk, Satoshi, or Space Grotesk. Same banlist for Roboto, Arial.
- **`Fraunces` or `Instrument Serif` as display font.** The 2025 "distinctive" escape hatch that
  became the tell — these are now the two LLM-favorite display serifs, exactly as recognizable as
  Inter. Flag them as defaults; acceptable only when the brand brief names them. And question the
  serif reflex itself: "creative/premium brief = serif" is itself an AI default — a sans display
  is usually the stronger reach. See `layer-1-tokens.md` → Typography for the rotation rule.
- **The premium-consumer beige+brass palette.** For cookware / wellness / artisan / luxury / DTC
  briefs, the AI default is warm cream backgrounds + brass/clay/oxblood accents + espresso
  near-black text (grep seeds: `#f5f1ea`, `#f7f5f1`, `#efeae0`, `#b08947`, `#b6553a`, `#9a2436`,
  `#1a1714` — the *families*, not just these exact values). Every AI-built premium-consumer site
  ships this palette, so the brand becomes invisible. Flag it as a default reach; it's fine only
  when the brand brief actually names those colors. Alternatives to suggest: cold luxury
  (silver/chrome/smoke), forest (deep green + bone + amber), black-and-tan, cobalt + cream,
  terracotta + slate, or monochrome + one saturated pop.
- **Pure `#000000`.** Use off-black or dark charcoal (`#0a0a0a`, `#121212`, Zinc-950).
- **Three equal-width card columns as feature row.** Most generic AI layout. Use zig-zag,
  asymmetric grid, or horizontal scroll.
- **Centered hero with text over dark image.** Try split-screen, left-aligned asymmetric, or
  product-shot-driven hero.
- **Oversaturated accents.** Keep saturation below 80%. Desaturate so accents blend, not scream.
- **More than one accent color.** Pick one. Remove the rest. See [layer-1-tokens.md](layer-1-tokens.md)
  → Color for the 60-30-10 ratio.
- **Generic black `box-shadow`** at low opacity. Tint shadows to match the surrounding hue.
- **Inconsistent border-radius.** One value across the visual group.
- **Mixed gray families** (warm + cool). Stick to one gray temperature throughout.
- **Perfectly even gradients.** Break with radial gradients, noise overlays, or mesh gradients.
- **Lucide / Feather icons exclusively.** The default AI icon library. Try Phosphor, Heroicons,
  or a custom set.
- **Rocket for "Launch", shield for "Security".** Cliche metaphors. Use bolt, fingerprint,
  spark, vault, beacon.
- **Stock "diverse team" photos.** Use real team photos, candid shots, or a consistent
  illustration style.
- **Flat design with zero texture.** Add subtle noise/grain/micro-patterns.
- **Random dark sections inside an otherwise light-mode page.** Looks like a copy-paste
  accident. Commit to one direction or use a slightly darker shade of the same palette.
- **Empty flat sections with no visual depth.** Add background imagery, subtle patterns, or
  ambient gradients.

---

## Content Anti-Patterns (The "Jane Doe" Effect)

These tell readers instantly that no one edited the output.

- **Generic names:** "John Doe", "Jane Smith" → diverse, realistic-sounding names
- **Round fake numbers:** `99.99%`, `50%`, `$100.00` → organic data (`47.2%`, `$99`)
- **Placeholder company names:** "Acme Corp", "Nexus", "SmartFlow" → contextual, believable
  names
- **AI copywriting clichés:** "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer",
  "Delve", "Tapestry", "In the world of…" → plain, specific language
- **Lorem Ipsum** → real draft copy. Lorem hides bad copy decisions.
- **Exclamation marks in success messages** → be confident, not loud
- **"Oops!" error messages** → direct: "Connection failed. Please try again."
- **Title Case On Every Header** → sentence case for most; reserve Title Case for primary CTAs
  and pricing tier names
- **Identical blog post dates** → randomize plausibly
- **Same avatar image for multiple users** → unique assets per person
- **Passive voice in errors** → active: "We couldn't save your changes" not "Mistakes were made"
- **Copy self-audit skipped.** Before calling any UI done, re-read every visible string (headlines,
  labels, captions, buttons, alt text, errors). Flag anything grammatically broken, with unclear
  referents, or that reads like an LLM trying to sound thoughtful (forced wordplay, mock-poetic
  micro-meta, fake-craftsman labels). If a string's meaning is uncertain, replace it with a plain
  functional sentence — AI-cute copy is worse than boring copy.

---

## Copy & Decoration Tells (Landing / Portfolio / Marketing)

Production-tested signatures of AI-generated marketing pages — sourced from real LLM
landing-page test rounds. **Scope:** these fire on landing pages, portfolios, marketing sites,
and top-of-funnel redesigns. On dashboards, admin panels, and dense product UI they are
advisory at most (a version footer on a devtool page is a fixture, not a tell). Each has an
override path: if the brief explicitly asks for the pattern, it's a choice, not a tell.

**Em-dashes in user-visible strings.** The single most-violated tell. Flag every `—` (and every
`–` used as a separator) in headlines, eyebrows, pills, body copy, quotes, attribution, captions,
button text, and alt text. "Use sparingly" phrasing empirically fails — models ignore it — so
treat this as near-absolute for audited UI copy: restructure the sentence (period, comma, colon,
parentheses) or use a plain hyphen for ranges. Greppable: `grep -rn "—\|–" --include="*.tsx"`
then filter to user-visible strings (the ban is on shipped UI copy, not code comments or docs).

**Eyebrow inflation.** An "eyebrow" is the small uppercase wide-tracking label above a section
headline (`SELECTED WORK`, `text-[11px] uppercase tracking-[0.18em]`). AI-built pages put one
above *every* section, producing the same templated rhythm. Mechanical check: count
`uppercase tracking` micro-labels across section components; more than `ceil(sections / 3)`
(hero counts as one) is a fail. The fix is usually deletion — the headline alone is enough.

**Micro-label and numbering tells:**

- **Section-number eyebrows** (`001 · Capabilities`, `06 · how it works`, `00 / INDEX`) — name
  the topic in plain language or drop the label
- **Pagination labels on images/tiles** (`01 / 4`) — the user can count
- **Version labels in the hero** (`V0.6`, `BETA`, `EARLY ACCESS`) — only when the brief is
  actually a launch/preview announcement
- **Version footers on marketing pages** (`v1.4.2`, `Build 0048`, `last sync 4s ago · main`) —
  devtool fixtures, not landing-page content
- **Middle-dot chains** (`foo · bar · baz · qux`) — ration to one `·` per metadata line; prefer
  line breaks, hairlines, or columns
- **Decorative status dots** — a colored dot before nav items, list rows, or badges conveys
  nothing; keep dots only for real semantic state (live server status), sparingly
- **Generic step labels** (`Step 1 / Step 2 / Step 3`, `Phase 01`) — the verb is the label:
  "Install", "Configure", "Ship"

**Decoration and caption tells:**

- **Pills/tags overlaid on photos** (`PLATE · BRAND`, `Field notes - journal`) — let the image
  speak, or caption below it
- **Photo-credit captions as decoration** (`Field study no. 12 · Ines Caetano`, `Frame XII ·
  35mm` under stock images) — credit only real photographers; otherwise a one-line functional
  caption or none
- **Decoration text strips at hero bottom** (`BRAND. MOTION. SPATIAL.`, `DESIGN · BUILD · SHIP`)
  — agency-portfolio cliché; only when the strip carries real links or status
- **Locale / time / weather strips** (`LIS 14:23 · 18°C`, "Lisbon, working with founders") —
  banned for ~99% of briefs; a contact address in the footer is fine, atmospheric locale
  decoration is not
- **Scroll cues** (`Scroll to explore`, animated mouse icons) — the user knows what scroll is
- **`<br>`-broken italicized headline splits** ("for thirty<br>*years.*") and **vertical rotated
  text** — reach for these only when the brief is explicitly experimental
- **Crosshair / hairline grid lines as decoration** — lines must organize real content

**Marketing-copy tells:**

- **"Quietly in use at" / "Quietly trusted by"** — use plain "Trusted by" / "Used at", or let
  the logos speak
- **Poetic section labels** ("From the field", "On our desks", "Loose plates") — performative
  craftsman voice; use functional labels ("Testimonials", "Latest writing") or none
- **Micro-meta sentences under section headings** ("Each of these is a feature we ship today,
  not a roadmap promise…") — clutter; eyebrow + headline + body is enough
- **Fake-precise numbers** (`4.1×`, `5.8 mm`, `48k`) — fine from real data or labeled as mock;
  banned as invented spec aesthetics

**Fake-visual tells:**

- **Div-based fake screenshots** — a product preview built from styled `<div>` rectangles (fake
  task lists, fake terminals, fake dashboards) is the #1 LLM design tell. Use a real screenshot,
  a real embedded component, or editorial imagery — or skip the preview
- **Logo walls as plain text wordmarks** (`<span>Acme Co</span>` in a row) — and the inverse:
  logo walls with category labels printed under each logo (`Stripe` + "payments"). Logos only

---

## UX Anti-Patterns

These actively harm users.

- **Confirmshaming.** "No thanks, I hate saving money."
- **Pre-selected options** that benefit the company over the user.
- **Cancellation flow harder than signup.**
- **Fake urgency/scarcity indicators.**
- **Infinite scroll without pagination option.** Breaks back button + keyboard nav.
- **Disabled submit buttons before user attempts submission.** Show validation errors after they
  try, not before.
- **Placeholder text as the only label.** Disappears on focus, confuses screen readers.
- **No empty states.** Empty dashboard is wasted onboarding. See [layer-4-states.md](layer-4-states.md)
  → Empty States.
- **No error states.** Inline messages required. Never `window.alert()`.
- **Generic circular spinners.** Use skeleton loaders matching the layout shape. See
  [layer-4-states.md](layer-4-states.md) → Loading States.
- **Dead links / `href="#"`.** Either link to a real destination or disable the element.
- **No indication of current page in navigation.** Active state must be visually distinct.

---

## Technical Anti-Patterns

Code-level failures that are easy to spot in review.
**Implementation rules live in [layer-2-primitives.md](layer-2-primitives.md)** — items below cross-reference it.

- **`outline: none`** without `:focus-visible` replacement. See [layer-2-primitives.md](layer-2-primitives.md)
  → Anti-Patterns in Implementation.
- **`<div onClick>`** instead of `<button>`. Same for `<span onClick>`.
- **Dynamic Tailwind classes** (`bg-${color}-500`). Use object maps. See [layer-2-primitives.md](layer-2-primitives.md)
  → Never Use Dynamic Class Names.
- **Animating layout properties** (`width`, `height`, `margin`, `padding`, `top`, `left`). Use
  `transform` and `opacity`. See [layer-5-motion.md](layer-5-motion.md) → Performance Rules.
- **Reading layout properties in render loops** (`getBoundingClientRect` in render). Batch
  reads.
- **Missing `alt` text on images.** Never leave `alt=""` or `alt="image"` on meaningful images.
- **Forms without `<label>`.** Even one missing label fails the form.
- **`h-screen`** for full-height sections. Use `min-h-[100dvh]`. See [layer-2-primitives.md](layer-2-primitives.md)
  → Viewport Height.
- **Complex flexbox percentage math.** Use Grid. See [layer-2-primitives.md](layer-2-primitives.md)
  → Grid over Flex Math.
- **Arbitrary z-index values** like `z-[9999]`. Establish a z scale. See [layer-2-primitives.md](layer-2-primitives.md)
  → Z-Index Discipline.
- **Commented-out dead code.** Remove before merging.
- **Import hallucinations.** Verify every import exists in `package.json`. See [layer-2-primitives.md](layer-2-primitives.md)
  → Dependency Verification.
- **Missing meta tags** (`<title>`, `description`, `og:image`).
- **`transition: all`.** Specify exact properties: `transition: transform 200ms ease-out`. See
  [layer-5-motion.md](layer-5-motion.md).
- **`user-scalable=no`** or `maximum-scale=1` (disables zoom).
- **`onPaste` + `preventDefault`** on text inputs.
- **Inline `onClick` navigation** without `<a>`.
- **Images without explicit `width`/`height`.** Causes layout shift.
- **Large arrays `.map()` without virtualization.** Slow render past 50 items.
- **Icon buttons without `aria-label`.**
- **Hardcoded date/number formats** instead of `Intl.*`.
- **`autoFocus` without justification.** Avoid on mobile.

---

## Mobile Anti-Patterns

Canonical sizing rules: [layer-1-tokens.md](layer-1-tokens.md) → Touch Targets and Responsive Precision.

| Anti-pattern                                              | Fix                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------- |
| Touch target < 44×44 px                                   | Extend hit area via padding (visual size can stay smaller) |
| Body text < 16 px on mobile                               | 16 px minimum to avoid iOS auto-zoom on focus              |
| Horizontal scrolling on content                           | Use `overflow-x: clip` on the root and audit child widths  |
| No tap feedback (> 100 ms)                                | Add `touch-action: manipulation`; `:active` scale feedback |
| Fixed-position elements blocking thumb zone               | Move actions to thumb-reachable bottom band                |
| Asymmetric desktop layouts without single-column fallback | Restructure (don't shrink) at the `md` breakpoint          |

---

## Strategic Omissions

What AI forgets — these show up as gaps, not as bugs.

- **No legal links** (privacy policy, terms of service).
- **No back navigation.** Dead ends in user flows.
- **No custom 404 page.**
- **No form validation.** Client-side validation for emails, required fields, format checks.
- **No "skip to content" link.** Essential for keyboard users. But ship the link *and* its
  `#main-content` target as one unit — a global link with no target on `error.tsx`/`not-found.tsx`/
  parent boundaries is its own regression. See `layer-3-components.md` → "Skip link and its target
  are one unit."
- **No cookie consent** (where required by jurisdiction).
- **No `prefers-reduced-motion` handling.** See [layer-5-motion.md](layer-5-motion.md) for the universal
  pattern.
- **No favicon.**

---

## Composition Anti-Patterns

- **Generic card look** (border + shadow + white background). Remove the border, or use
  background-only, or use spacing-only. Cards exist when elevation communicates hierarchy.
- **Always one filled + one ghost button.** Add text links or tertiary styles to reduce noise.
- **Pill-shaped "New" and "Beta" badges everywhere.** Try square badges, flags, or plain text.
- **Accordion FAQ as the only pattern.** Try side-by-side list, searchable help, or inline
  progressive disclosure.
- **3-card carousel testimonials with dots.** Replace with masonry wall, embedded social posts,
  or a single rotating quote with photo.
- **Modals for everything.** Use inline editing, slide-over panels, or expandable sections for
  simple actions.
- **Avatar circles exclusively.** Try squircles or rounded squares.
- **Light/dark sun/moon toggle.** Use a 3-state segmented control or system-preference
  detection.
- **Footer link farm with 4 columns.** Simplify to main paths + legally required links.
- **Zigzag on repeat.** More than 2 consecutive image+text split sections alternating sides is
  templated rhythm. Break the third with a full-width section, bento, or vertical stack.
- **Split-header default.** "Left big headline + right small floating explainer paragraph" as a
  section header — stack them vertically instead, unless the right column carries a real visual
  or interactive element.
- **Same layout family reused across sections.** A landing page with 8 sections needs at least 4
  different layout families; "Selected work" must not look like "What we do".
- **Duplicate CTA intent.** "Get in touch" + "Contact us" + "Let's talk" on one page are all the
  same action wearing three labels. One label per intent, used everywhere (nav, hero, footer).
- **CTA label wrapping at desktop.** A primary CTA that wraps to 2+ lines is broken — shorten
  the label (1–3 words) or widen the button.
- **Two-line navigation or oversized nav bars.** Desktop nav renders on one line, ≤ 80 px tall
  (64–72 px default). Condense labels or move items to a menu.
- **Mid-page theme flips.** One theme per page — a warm-light section sandwiched between dark
  sections reads as a copy-paste accident (the "random dark sections" tell above, generalized).
  A deliberate full theme switch as a composition device is allowed once, with a strong transition.
- **Accent drift.** The accent color chosen for the page appears identically in every section —
  a rose-accented site does not grow a teal badge in the footer. Same lock for corner radius:
  one radius system per page, or a documented per-element rule followed everywhere.
- **Bento grids with filler or empty cells.** A grid has exactly as many cells as there is
  content — re-shape the grid rather than pasting a blank tile. And an all-white-text-card bento
  is the boring default: at least 2–3 cells need real visual variation (image, tint, pattern).
- **More than one marquee per page.** A second scrolling text/logo marquee is lazy filler.

---

## Code Quality Anti-Patterns

- **Div soup.** Use semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>`, `<section>`.
- **Inline styles mixed with CSS classes.** Move all styling to the project's system.
- **Hardcoded pixel widths.** Use relative units (`%`, `rem`, `em`, `max-width`).
- **Missing alt text on meaningful images.**
- **Commented-out dead code in PRs.**
- **`{count} {count === 1 ? '' : 's'}`** for pluralization. Use ICU messages (Arabic etc. break
  English plural).
- **Token-shape misuse — a token _object_ passed where a class string is expected.** In a typed
  design-token module, a token is sometimes an _object_ (`TYPOGRAPHY.display = { hero, large }`), not
  a leaf string. Passing that into `cn()`/`clsx` — `cn(TYPOGRAPHY.display, "…")` — silently emits
  **nothing useful**: `clsx` reads a plain object as a `{ className: truthy }` map, so it outputs the
  literal _key_ names (`"hero large"`) and the element renders with **no styling at all**. (Arrays of
  class _strings_ are fine — `clsx` flattens those; the trap is specifically a plain object, or an
  array that contains one.) It's valid TS, valid JSX, and passes typecheck and lint, so it's
  invisible to every grep for hardcoded values — only a read catches it. Find candidates with
  `grep -rnE "cn\(\s*[A-Z_]+\.[A-Za-z]" --include="*.tsx"` and verify each token reference resolves
  to a **string**. This is the under-audited failure: the token system _exists_ and is _imported_,
  yet produces no class.

---

## Quick-Reject Checklist for Code Review

When the diff includes any of these, reject and ask for the fix. For the full code review
structure see [review-protocol.md](review-protocol.md).

| Pattern                               | Find by                                                                                                                                                     | Fix                                                                                |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `outline: none` (no replacement)      | `grep -rn "outline-none\|outline: none" --include="*.tsx"`                                                                                                  | Add `focus-visible:ring-2` or equivalent                                           |
| `<div onClick>` / `<span onClick>`    | `grep -rn "<div[^>]*onClick\|<span[^>]*onClick" --include="*.tsx"`                                                                                          | Convert to `<button>`                                                              |
| `transition: all`                     | `grep -rn "transition: all\|transition-all" --include="*.tsx"`                                                                                              | Specify properties (`transition-[color,transform]`)                                |
| `h-screen` on full layout             | `grep -rn "h-screen" --include="*.tsx"`                                                                                                                     | `min-h-[100dvh]`                                                                   |
| `bg-${...}` dynamic class             | `grep -rn 'bg-\${' --include="*.tsx"`                                                                                                                       | Object map                                                                         |
| `z-[\d{4,}]`                          | `grep -rn 'z-\[[0-9]\{4,\}\]' --include="*.tsx"`                                                                                                            | Z-scale token                                                                      |
| `<img>` missing `alt`                 | `grep -rn '<img ' --include="*.tsx"` then filter for `alt=`                                                                                                 | Add alt or `aria-hidden="true"`                                                    |
| `<img>` missing `width`/`height`      | `grep -rn '<img ' --include="*.tsx"` then filter for `width=`                                                                                               | Add explicit dimensions (CLS risk) or use `next/image`                             |
| `<button>` missing `type` attr        | **Naive grep is unreliable** — JSX attrs span lines. Use AST/jsx-ast tooling, or `grep -A3 '<button'` then visually confirm. Most critical inside `<form>`. | Add `type="button"` explicitly                                                     |
| `<input>` without label               | Inspect each form (also multi-line JSX — naive grep unreliable)                                                                                             | `<label htmlFor>` or wrapping label                                                |
| `transform: scale(0)` entry           | `grep -rn "scale(0)" --include="*.tsx"` (exclude `scale(0.`)                                                                                                | `scale(0.95) opacity:0` (see [layer-5-motion.md](layer-5-motion.md))               |
| `ease-in` on UI element               | `grep -rn "ease-in[^-]" --include="*.tsx"`                                                                                                                  | `ease-out` or custom curve (see [layer-5-motion.md](layer-5-motion.md))            |
| `user-scalable=no`                    | `grep -rn "user-scalable" --include="*.tsx"`                                                                                                                | Remove                                                                             |
| Hardcoded English in JSX              | inspect for capitalized literal strings in `<p>`, `<h*>`, `<button>` text                                                                                   | Wrap in `t()`                                                                      |
| ICU plural break (`=== 1 ? '' : 's'`) | `grep -rn "=== 1 ? ''" --include="*.tsx"`                                                                                                                   | Use ICU `{count, plural, ...}` — English plural breaks Arabic/Urdu                 |
| `space-y-*` on `<ul>` / `<li>`        | `grep -rn '<ul[^>]*space-y-\|<li[^>]*space-y-' --include="*.tsx"`                                                                                           | Structural tests often scope to `<div>` only and miss these. Use `<Stack as='ul'>` |
| Missing `color-scheme` on `<html>`    | Inspect root layout — should set `style={{ colorScheme: 'light dark' }}` or CSS `color-scheme`                                                              | Without it, native scrollbars/selects/date pickers don't dark-mode                 |
| Token object passed to `cn()`/`clsx`  | `grep -rnE "cn\(\s*[A-Z_]+\.[A-Za-z]" --include="*.tsx"` then confirm each token resolves to a **string** (not a plain object)                              | Use the leaf string (`TYPOGRAPHY.display.hero`) — a plain object emits its keys, styling silently vanishes |
| Em/en-dash in UI strings (marketing)  | `grep -rn "—\|–" --include="*.tsx"` then filter to user-visible strings (not comments/docs)                                                                 | Restructure (period, comma, colon, parens); plain hyphen for ranges                |
| Eyebrow inflation (marketing)         | `grep -rnc "uppercase tracking" --include="*.tsx"` across section components; compare to `ceil(sections / 3)`                                               | Delete eyebrows — the headline alone is enough                                     |
| Beige+brass premium palette (marketing) | `grep -rni -e "#f5f1ea" -e "#f7f5f1" -e "#efeae0" -e "#b08947" -e "#b6553a" -e "#9a2436" -e "#1a1714" --include="*.tsx" --include="*.css"` — seeds for the family (full seed list in `review-protocol.md` → grep sweep), not exhaustive | Rotate to a different palette family (see Visual AI Tells) unless the brand names these colors |
| `window.addEventListener('scroll')`   | `grep -rn "addEventListener(['\"]scroll\|window\.scrollY" --include="*.tsx"`                                                                                | Motion `useScroll()`, ScrollTrigger, IntersectionObserver, or CSS scroll-driven animations — see `layer-5-motion.md` |

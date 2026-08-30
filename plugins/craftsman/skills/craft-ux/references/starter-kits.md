# Starter Kits — Font Pairings & Palettes for Generation

Concrete, vetted values for greenfield generation: 19 font pairings (15 by use case + 4 SaaS
landing variants) with paste-ready imports and 15 contrast-verified starter palettes in this
skill's token roles. These are **floors, not
ceilings** — a starter kit gets a new project past the AI-default zone in one shot; a brief with
a real brand voice (or an `impeccable` pass) should still push past them.

> **Source note:** font weight/axis data and the palette industry mapping draw on research from
> the MIT-licensed [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
> dataset (see `THIRD_PARTY_NOTICES.md`); every font choice and palette value here was re-curated
> against this skill's anti-slop rules — the upstream defaults (Inter-led pairings, AI-indigo
> primaries) were deliberately not carried over.

> **See also**
>
> - Token roles these palettes instantiate, type scale, serif discipline → `layer-1-tokens.md`
> - Banned defaults these kits were filtered against → `anti-patterns.md` → Visual AI Tells
> - Design Read (pick the kit from the brief, not from habit) → `composition.md`

## How to use

1. Run the Design Read (`composition.md`) first; pick the kit matching the read, not the
   product's category label — and pick by **surface mode**: an app UI (Operate) and its landing
   page (Persuade) are different surfaces wanting different kits. "SaaS" alone is not enough
   information to choose.
2. Instantiate the palette as **layer-1 token values** (`--background`, `--primary`, …) — never
   paste hexes into components. Reuse layer-1's semantic status tokens (destructive / success /
   warning) unchanged; kits define brand + neutrals only.
3. Every kit obeys the standing rules: one saturated brand hue per palette, accents used
   sparsely (60-30-10), serif display only where the use case earns it.
4. Dark mode: derive per `layer-1-tokens.md` → Theming (keep the hue, adjust lightness; no pure
   `#000`). The developer-tool kit ships dark-native as the worked example.

### Variation protocol (mandatory — a kit is a starting point, not a stamp)

A 1:1 category→kit mapping would recreate the exact "every AI site looks the same" failure this
skill exists to prevent. Rules:

- **Never pick the same kit twice in a row** for the same category. If the last SaaS generation
  used Schibsted Grotesk, this one draws a different pairing (the landing variants below, or a
  remix). Same rotation discipline as the serif pool in `layer-1-tokens.md`.
- **Pairings and palettes are independent axes.** Any pairing may carry any palette whose mood
  fits the Design Read — with 19 pairings × 15 palettes, that's 285 combinations before
  anything repeats, not 19 or 15. A serif-led
  landing (Spectral, Literata) over the fintech navy palette is a legitimate, distinctive combo.
- **Let the brief's adjectives override the category.** "Playful SaaS for teachers" reaches for
  the education kit's warmth, not the SaaS kit, regardless of the product being SaaS.
- **State the pick in the Design Read** ("kit: Familjen Grotesk × analytics-navy, because …")
  so the choice is a decision, not a reflex.

### Awwwards-tier escalation

Starter kits raise the floor; award-tier work is above the ceiling of any lookup table. When the
brief says distinctive / award-worthy / memorable: keep the kit's *palette discipline* (tokens,
contrast, one hue), but treat the pairing as provisional — push `DESIGN_VARIANCE` to 8+
(`composition.md`), choose a display face for *this brand's* voice (rotating past anything used
recently), design one signature moment the page is remembered by, and run the result through
`impeccable` rather than shipping the kit as-is. A starter kit shipped unmodified should read as
"competently designed", never as the ambition's end state.

---

## Font pairings

Weights below are verified against the Google Fonts catalog — every listed weight exists.
All faces are Google Fonts (OFL/Apache): free for commercial use, no notice required for
URL embedding. Fallback stacks: pair each with `ui-sans-serif, system-ui, sans-serif`
(or `ui-serif, Georgia, serif` / `ui-monospace, monospace`).

### 1. SaaS product — Schibsted Grotesk + Wix Madefor Text
Confident grotesk with personality; body built for screens. Modern, clean, not-Inter.
```css
@import url('https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@500;600;700&family=Wix+Madefor+Text:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Schibsted Grotesk', 'sans-serif'], body: ['Wix Madefor Text', 'sans-serif']`

### 2. Developer tool — Geist + Geist Mono
Vercel's face: precise, technical, quietly opinionated. Mono for code and data.
```css
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');
```
Tailwind: `heading: ['Geist', 'sans-serif'], body: ['Geist', 'sans-serif'], mono: ['Geist Mono', 'monospace']`

### 3. Premium consumer / DTC — Young Serif + Hanken Grotesk
Warm single-weight display serif (400 only — scale with size, not weight) over a humanist sans.
Craft feel without the beige+brass cliché.
```css
@import url('https://fonts.googleapis.com/css2?family=Young+Serif&family=Hanken+Grotesk:wght@400;500;600;700&display=swap');
```
Tailwind: `heading: ['Young Serif', 'serif'], body: ['Hanken Grotesk', 'sans-serif']`

### 4. Luxury / fashion — Bodoni Moda + Figtree
High-contrast didone with optical sizing (`opsz` 6–96 auto-adjusts); neutral geometric body.
```css
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600;6..96,700&family=Figtree:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Bodoni Moda', 'serif'], body: ['Figtree', 'sans-serif']`

### 5. Editorial / publication — Literata + Public Sans
Book-grade optical-sized serif for long reading; civic sans for UI chrome.
```css
@import url('https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400&family=Public+Sans:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Literata', 'serif'], body: ['Literata', 'serif'], ui: ['Public Sans', 'sans-serif']`

### 6. Fintech / trust — Libre Franklin + Source Sans 3
American gothic gravity; unfussy body. Serious without being sterile.
```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Libre Franklin', 'sans-serif'], body: ['Source Sans 3', 'sans-serif']`

### 7. Agency / bold marketing — Unbounded + Albert Sans
Expanded display face with real presence; clean geometric body keeps it grounded.
```css
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;500;600;700&family=Albert+Sans:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Unbounded', 'sans-serif'], body: ['Albert Sans', 'sans-serif']`

### 8. E-commerce — Gabarito + Onest
Rounded-but-adult display; highly readable body at product-card sizes.
```css
@import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@500;600;700&family=Onest:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Gabarito', 'sans-serif'], body: ['Onest', 'sans-serif']`

### 9. Wellness / calm — Spectral + Karla
Soft light-weight serif (use 300/400 display) with an easy humanist body.
```css
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,500;1,400&family=Karla:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Spectral', 'serif'], body: ['Karla', 'sans-serif']`

### 10. Food / hospitality — Marcellus + Karla
Inscriptional single-weight display (400 only) with quiet elegance; warm body sans.
```css
@import url('https://fonts.googleapis.com/css2?family=Marcellus&family=Karla:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Marcellus', 'serif'], body: ['Karla', 'sans-serif']`

### 11. Portfolio / creative — Bricolage Grotesque + Hanken Grotesk
Characterful grotesk with optical sizing and width axes; sibling-feel body.
```css
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700&family=Hanken+Grotesk:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Bricolage Grotesque', 'sans-serif'], body: ['Hanken Grotesk', 'sans-serif']`

### 12. Data / dashboard — Archivo + Spline Sans Mono
Width-axis grotesk (use Expanded for display moments); mono for numerals with
`font-variant-numeric: tabular-nums`.
```css
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400;62..125,500;62..125,600;62..125,700&family=Spline+Sans+Mono:wght@400;500&display=swap');
```
Tailwind: `heading: ['Archivo', 'sans-serif'], body: ['Archivo', 'sans-serif'], mono: ['Spline Sans Mono', 'monospace']`

### 13. Education / kids — Baloo 2 + Nunito Sans
Round warmth without Comic-anything; body stays legible at length.
```css
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700&family=Nunito+Sans:wght@400;600;700&display=swap');
```
Tailwind: `heading: ['Baloo 2', 'sans-serif'], body: ['Nunito Sans', 'sans-serif']`

### 14. Accessibility-first / government — Atkinson Hyperlegible + Source Sans 3
Designed for low-vision legibility (400/700 only — hierarchy via size, not mid-weights).
```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Source+Sans+3:wght@400;600&display=swap');
```
Tailwind: `heading: ['Atkinson Hyperlegible', 'sans-serif'], body: ['Source Sans 3', 'sans-serif']`

### 15. Heritage / legal — EB Garamond + Albert Sans
Old-style authority for display; modern sans body keeps documents readable on screens.
```css
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&family=Albert+Sans:wght@400;500&display=swap');
```
Tailwind: `heading: ['EB Garamond', 'serif'], body: ['Albert Sans', 'sans-serif']`

---

## SaaS landing & marketing variants (Persuade mode — rotate, don't default)

Kit 1 is an **Operate** kit (app UI). A SaaS *landing or home page* is a Persuade surface and
gets more expressive display type. Rotate through these (and remixes — e.g. Bricolage Grotesque
or a serif-led Literata landing over any fitting palette); never let one become "the SaaS look".
All URLs verified live.

### L1. Scandinavian clean — Familjen Grotesk + Albert Sans
Warm grotesk with subtle quirks; reads premium without shouting.
```css
@import url('https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;500;600;700&family=Albert+Sans:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Familjen Grotesk', 'sans-serif'], body: ['Albert Sans', 'sans-serif']`

### L2. Launch energy — Anybody + Schibsted Grotesk
Width-axis display (set Expanded for the hero) with real poster presence; calm body.
```css
@import url('https://fonts.googleapis.com/css2?family=Anybody:wdth,wght@50..150,500;50..150,600;50..150,700&family=Schibsted+Grotesk:wght@400;500&display=swap');
```
Tailwind: `heading: ['Anybody', 'sans-serif'], body: ['Schibsted Grotesk', 'sans-serif']`

### L3. Technical-warm — Geologica + Public Sans
Variable face with an engineered-but-friendly voice; suits dev-adjacent SaaS marketing.
```css
@import url('https://fonts.googleapis.com/css2?family=Geologica:wght@400;500;600;700&family=Public+Sans:wght@400;500&display=swap');
```
Tailwind: `heading: ['Geologica', 'sans-serif'], body: ['Public Sans', 'sans-serif']`

### L4. Editorial SaaS — Spectral (light) + Hanken Grotesk
Contrarian serif-led landing: light-weight serif display over a neutral sans. Calm confidence;
pairs well with the fintech or forest palettes.
```css
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;1,300&family=Hanken+Grotesk:wght@400;500;600&display=swap');
```
Tailwind: `heading: ['Spectral', 'serif'], body: ['Hanken Grotesk', 'sans-serif']`

---

## Starter palettes

Every palette passes automated WCAG checks: foreground/background ≥ 7:1 (AAA body),
on-primary/primary and on-accent/accent ≥ 4.5:1, muted-foreground ≥ 4.5:1 on both background
and muted, primary and ring ≥ 3:1 against background. One saturated brand hue per palette;
the accent is a restrained second tone for sparse highlights, not a competing brand color.
None uses the AI-indigo family or the beige+brass premium-consumer family (`anti-patterns.md`).

Roles map 1:1 to the layer-1 token set. All palettes are light-mode except the developer tool
kit (dark-native, the worked dark example).

**Editing this table?** Re-run `python3 scripts/verify-palettes.py` (repo root) — it parses this
table directly and fails on any WCAG regression. A palette edit without a passing run doesn't ship.

| Kit | primary | on-primary | accent | on-accent | background | foreground | card | muted | muted-fg | border | ring |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SaaS product | `#1D4ED8` | `#FFFFFF` | `#B45309` | `#FFFFFF` | `#F8FAFC` | `#0F172A` | `#FFFFFF` | `#EEF2F7` | `#44546A` | `#DDE3EC` | `#1D4ED8` |
| Developer tool (dark) | `#34D399` | `#052E16` | `#7DD3FC` | `#082F49` | `#0B1120` | `#E6EDF6` | `#111A2E` | `#1B2740` | `#93A5BE` | `#2A3A57` | `#34D399` |
| E-commerce | `#047857` | `#FFFFFF` | `#B45309` | `#FFFFFF` | `#F7FBF9` | `#12291F` | `#FFFFFF` | `#E9F2EE` | `#3F5A4E` | `#D4E4DC` | `#047857` |
| Fintech / banking | `#0F172A` | `#FFFFFF` | `#8A5A0B` | `#FFFFFF` | `#F8FAFC` | `#0B1120` | `#FFFFFF` | `#E9EDF3` | `#44546A` | `#DBE2EB` | `#0F172A` |
| Healthcare | `#0E7490` | `#FFFFFF` | `#047857` | `#FFFFFF` | `#F5FBFC` | `#123B47` | `#FFFFFF` | `#E7F2F5` | `#3D5A63` | `#CFE5EB` | `#0E7490` |
| Premium consumer (forest) | `#1E3D2F` | `#F4EFE6` | `#8A5A0B` | `#FFFFFF` | `#F7F5F0` | `#1B2420` | `#FFFFFF` | `#ECEAE2` | `#4E564F` | `#DBD8CC` | `#1E3D2F` |
| Creative agency | `#BE185D` | `#FFFFFF` | `#0E7490` | `#FFFFFF` | `#FDF6F9` | `#3B0A24` | `#FFFFFF` | `#F4E9EF` | `#6B4658` | `#EED4E1` | `#BE185D` |
| Education / courses | `#0F766E` | `#FFFFFF` | `#B45309` | `#FFFFFF` | `#F5FBFA` | `#113B36` | `#FFFFFF` | `#E8F2F0` | `#3E5854` | `#CFE4E0` | `#0F766E` |
| Food / restaurant | `#B91C1C` | `#FFFFFF` | `#4D7C0F` | `#FFFFFF` | `#FDF8F4` | `#3B1212` | `#FFFFFF` | `#F4ECE4` | `#6B4F45` | `#E9DACB` | `#B91C1C` |
| Wellness / mindfulness | `#0F766E` | `#FFFFFF` | `#7C5E10` | `#FFFFFF` | `#F7FAF7` | `#1F2A26` | `#FFFFFF` | `#EBF0EB` | `#4C5A53` | `#D8E1D8` | `#0F766E` |
| Analytics dashboard | `#1E40AF` | `#FFFFFF` | `#92400E` | `#FFFFFF` | `#F8FAFC` | `#101935` | `#FFFFFF` | `#EBEFF5` | `#455473` | `#DBE1EC` | `#1E40AF` |
| Travel / tourism | `#0369A1` | `#FFFFFF` | `#B45309` | `#FFFFFF` | `#F5FAFD` | `#0E3A54` | `#FFFFFF` | `#E7F1F8` | `#3D5A6E` | `#CEE3F0` | `#0369A1` |
| Nonprofit | `#0E7490` | `#FFFFFF` | `#B91C1C` | `#FFFFFF` | `#F6FAFB` | `#143641` | `#FFFFFF` | `#E9F1F3` | `#41585F` | `#D2E3E7` | `#0E7490` |
| AI product | `#047857` | `#FFFFFF` | `#1E293B` | `#FFFFFF` | `#F7FAF8` | `#101915` | `#FFFFFF` | `#EAF1EC` | `#43554A` | `#D6E2D9` | `#047857` |
| Portfolio / personal | `#18181B` | `#FFFFFF` | `#1D4ED8` | `#FFFFFF` | `#FAFAFA` | `#09090B` | `#FFFFFF` | `#EDEDEF` | `#52525B` | `#E0E0E3` | `#18181B` |

Deliberate curation calls, so reviews don't "fix" them backwards:

- **AI product is green, not purple** — the AI-indigo/violet default is the #1 palette tell.
- **Premium consumer is the forest family** (deep green + bone + muted amber), not warm
  beige+brass — that family is banned as a default reach.
- **Wellness is teal + stone, not lavender** — calm-purple is the same AI default in disguise.
- Accents sit in the 600–800 weight range (muted, dark enough for white text) rather than neon.

Instantiation template (values → layer-1 roles):

```css
:root {
  --background: <background>;
  --foreground: <foreground>;
  --primary: <primary>;
  --primary-foreground: <on-primary>;
  --accent: <accent>;
  --accent-foreground: <on-accent>;
  --card: <card>;
  --card-foreground: <foreground>;
  --muted: <muted>;
  --muted-foreground: <muted-fg>;
  --border: <border>;
  --ring: <ring>;
  /* destructive / success / warning: reuse layer-1's semantic status tokens */
}
```

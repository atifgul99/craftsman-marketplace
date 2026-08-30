# Auditing Design-System Tokens

How to find and fix token violations — and how to build the scanner that catches them in CI so the design system can't silently rot.

> **See also**
>
> - Token taxonomy and the value foundation → `layer-1-tokens.md`
> - Building the token layer from scratch → `building-a-design-system.md`
> - Design primitives and platform constraints → `foundations.md`
> - Review severity and output format → `review-protocol.md`
> - Patterns to avoid when extending the system → `anti-patterns.md`

---

## Contents

- [Discover First](#discover-first)
- [What a Token Audit Looks For](#what-a-token-audit-looks-for)
- [The Audit Loop](#the-audit-loop)
- [Fix by Category — Routing Table](#fix-by-category--routing-table)
- [Building the Scanner](#building-the-scanner)
- [Exempt-Files Governance](#exempt-files-governance)
- [Governance — When to Promote a Pattern to a Token or Component](#governance--when-to-promote-a-pattern-to-a-token-or-component)
- [A Note on Severity](#a-note-on-severity)

---

## Discover First

Before scanning for violations, understand the system you're auditing. A five-minute discovery pass prevents you from "fixing" things that are intentionally raw, and tells you where to route each violation.

**Find the scanner.** Look for a `tokens:check`, `design:lint`, or `css-audit` script in
`package.json` / `Makefile`. If one exists, run it and read its source — the checks it runs and the
files it skips are the ground truth for what the repo enforces. If no scanner exists, building one
is the highest-leverage action you can take; see "Building the Scanner" below.

**Find the token module.** Locate the file where design tokens are defined — a TypeScript constants
file (e.g. `design-tokens.ts`), a CSS custom-property block (e.g. inside `globals.css`), or both.
Read it. This is your fix reference: every palette violation should resolve to something in here.

**Find the shared pattern components.** Look for a `components/patterns/` or equivalent directory
containing reusable presentational fragments (status badges, error text, muted labels, loading
buttons). These are the correct destinations for many violations the scanner surfaces. If they don't
exist yet, violations you find are also an inventory of what patterns need to be built.

**Find the exempt files.** The system's definition files are allowed to contain raw values — they
ARE the tokens. See "Exempt-Files Governance" below for the full reasoning.

---

## What a Token Audit Looks For

A complete audit covers eight violation categories. Run checks across the domain-component tree
(usually `src/components/features/`, `src/components/layout/`, `src/app/`) while excluding the
system-definition files.

### (a) Hardcoded palette or arbitrary color classes

Raw Tailwind palette classes (`text-red-500`, `bg-blue-400`, `border-green-300`, `from-purple-500`,
arbitrary hex brackets like `bg-[#1a1a2e]`) in domain components. These lock color decisions into
markup rather than the token layer, making a single visual change require a repo-wide grep.

Fix target: a semantic token (`text-destructive`, `bg-success`, `border-border`), a status token
(`bg-status-approved`), or a shared status/platform/feedback component.

### (b) Inline `style=` with raw color values

`style={{ color: '#6b7280' }}`, `style={{ background: 'rgb(30, 30, 30)' }}`, or any inline style
object that embeds a hex, rgb, or hsl literal. These bypass the token layer entirely and are
invisible to class-based scanners.

Fix target: move to `className` using the semantic equivalent, or a CSS variable reference
(`var(--muted-foreground)`).

### (c) Raw layout spacing on generic containers

`<div className="flex flex-col space-y-4">`, `<div className="flex items-center gap-3">` — direct
spacing utilities on plain divs, bypassing any layout-primitive abstraction the repo has established.
Each callsite embeds a magic number rather than a named scale step.

Fix target: your layout primitives (`<Stack>`, `<Inline>`, `<Grid>`, or equivalent), which map
named scale values (`sm`, `md`, `lg`) to consistent gap utilities in one place.

### (d) Raw font-family utilities

`font-sans`, `font-serif`, `font-mono` used in domain components when the repo establishes a global
base font via a CSS variable. Domain components re-declaring the font family mean a typeface change
requires a grep instead of a one-line variable edit.

Fix target: a typography token that carries the complete style intent (size + weight + tracking),
letting family resolve from the global CSS variable.

### (e) Hardcoded shadows, backdrop-blur, and arbitrary visual values

`shadow-[0_4px_24px_rgba(0,0,0,0.12)]`, `backdrop-blur-md` in domain code when the repo has
dedicated shadow/glass tokens. Each one-off breaks elevation consistency and makes theme changes
require per-file edits.

Fix target: a named shadow or glass token from your token module, or a CSS custom property defined
in the base stylesheet.

### (f) Inline transition duration and easing

`duration-200`, `ease-out`, or inline `transition-all` scattered through domain components when the
repo has motion tokens. `transition-all` is particularly harmful — it animates layout properties
(`width`, `height`, `gap`) which trigger reflow and cause jank.

Fix target: a named motion token (`transition-normal`, `var(--duration-fast)`) and an explicit
property list instead of `all`.

### (g) Cross-layer leaks

`@keyframes` defined in the token module (should live in the base stylesheet), or Tailwind utility
compositions with `@apply` in the base stylesheet (should live in the token module or component
styles). Each leak is an architecture hole that silently grows.

Fix target: move animations to the CSS layer, move compositions to the token layer. The distinction:
the base stylesheet owns raw CSS primitives; the token module owns named compositions over them.

### (h) Missing pattern components — hand-rolled recurring markup

`<p className="text-xs text-destructive">` instead of a shared `<FormError>` component.
`<span className="text-sm text-muted-foreground">` instead of a `<MutedText>` equivalent.
`{isPending ? <Loader2 className="animate-spin" /> : children}` instead of a `<LoadingButton>`.
Each one-off is a divergence point: spacing, sizing, and semantic wiring drift callsite by callsite.

Fix target: the shared pattern component. If it doesn't exist yet, build it — but only if the
pattern appears in 3+ locations (see "Governance" below).

---

## The Audit Loop

The loop is: **Scan → Fix by Category → Verify**. Don't interleave fixing and scanning; finish
the full scan output first so you can batch fixes and spot patterns.

**Scan.** Run your scanner and capture full output with file paths and line numbers. If no scanner
exists, run the manual grep patterns from "Building the Scanner" below. Read every violation before
touching any file.

**Fix by category.** Route each violation to its fix using the table in the next section. Batch
fixes: do all status-color violations together, all inline-style violations together. This avoids
re-reading the same files repeatedly.

**Verify.** Re-run the scanner until it exits clean. Then run the full lint/build. The scanner
catching zero violations while the build fails means a fix introduced a different problem — a clean
scanner exit and a clean build together constitute "done."

---

## Fix by Category — Routing Table

| Violation                                                   | Fix target                                                                                                                                              |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Status / state color (approved, pending, failed, archived…) | A shared status component (e.g. `<StatusBadge>`) or your semantic status token set                                                                      |
| External brand / platform color (social network brand hex)  | A brand/platform badge component or your platform token set                                                                                             |
| Success / warning / error / info feedback color             | A feedback token (`FEEDBACK.success`, `var(--color-success)`, or equivalent)                                                                            |
| Generic UI color (text, background, border, ring)           | Your semantic theme token: the `text-foreground` / `bg-card` / `border-border` equivalent                                                               |
| Inline `style=` color                                       | Move to `className` using the semantic equivalent above; keep inline style only where the CSS pipeline is unavailable (e.g. a bare-HTML error boundary) |
| Raw layout spacing on a `<div>`                             | Your layout primitive (`<Stack>`, `<Inline>`, `<Grid>`, or equivalent) with a named scale value                                                         |
| Raw font-family utility                                     | Your typography token, which resolves family from the global CSS variable                                                                               |
| Hardcoded shadow / blur                                     | Your named shadow or glass token                                                                                                                        |
| Inline `duration-*` / `ease-*`                              | Your motion token; replace `transition-all` with an explicit property list                                                                              |
| `@keyframes` in token module                                | Move to the base stylesheet                                                                                                                             |
| `@apply` compositions in base stylesheet                    | Move to the token module or component styles                                                                                                            |
| Hand-rolled error/muted/loading pattern                     | The shared pattern component; build it if ≥ 3 callsites exist                                                                                           |

In a concrete repo the destinations resolve to that repo's own components and token namespaces —
e.g. a `<StatusBadge>` / `<MutedText>` / `<FormError>` for the hand-rolled patterns, a
`<Stack spacing="md">` for raw spacing, and domain token objects (a feedback palette, a platform
palette) for the literals. Discover the repo's actual names first; they're just one instance of the
generic targets above.

---

## Building the Scanner

If the repo has no scanner, building one is the single highest-leverage design-system action you
can take. A scanner that runs in pre-commit and CI makes violations impossible to merge silently.
It pays for itself on the first PR it catches.

**Structure.** A scanner is a shell script (or a small Node/TS script) that runs a handful of
`rg` (ripgrep) or `grep` checks over the **entire domain surface** — every place a developer writes
JSX, not just the component folder. That means components _and_ the route/page tree (e.g.
`src/app`, `src/pages`, `src/routes` — whatever your framework uses). A scanner pointed only at
`src/components/` reports zero while raw values sit in page files; scope it to all of them or it
gives false confidence. It filters out the exempt files (below), counts violations, and exits
non-zero when any are found. Each check emits `file:line: message` output so engineers jump straight
to the violation.

**Scope and exemptions** are shared by every check — define them once:

```bash
# Every place domain JSX lives — adapt to your framework's layout.
SCAN_DIRS=(src/components src/app src/pages src/routes)
# The two system-definition files (adapt the paths) — checked directly for cross-layer leaks.
BASE_STYLESHEET=src/app/globals.css
TOKEN_MODULE=src/lib/design-tokens.ts
# The files that DEFINE the system are exempt (see governance below).
EXEMPT='(globals\.css|design-tokens\.ts|themes\.ts|/primitives/|/ui/.*\.tsx$|global-error\.tsx)'
scan() { rg "$@" --glob '*.{ts,tsx,js,jsx,mtsx,cjs}' "${SCAN_DIRS[@]}" 2>/dev/null | rg -v "$EXEMPT"; }
```

**The core checks to include** (each piped through `scan` so scope + exemptions apply uniformly):

```bash
# Color-bearing utility prefixes. This is the COMMON set — extend it to match your framework's
# utilities. The optional (-[trblxyse]) segment covers directional/logical borders so
# border-l-red-500 and border-s-[#fff] are caught, not just the bare `border-` form.
CPREFIX='(text|bg|border(-[trblxyse])?|ring|ring-offset|outline|divide|fill|stroke|decoration|accent|caret|placeholder|shadow|from|via|to)'

# 1a. Hardcoded named palette classes  (category a)
scan "${CPREFIX}-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[0-9]+"

# 1b. Arbitrary color / visual values — SAME prefix set; match the literal ANYWHERE in the bracket
#     so a leading token (inset_, an offset) can't hide it. Catches via-[#1a1a2e], stroke-[hsl(...)],
#     decoration-[#fff], shadow-[0_4px_rgba(...)], and inset shadow-[inset_0_1px_0_rgba(0,0,0,.12)].
scan "${CPREFIX}-\[[^]]*(#[0-9a-fA-F]{3,8}|rgb|rgba|hsl|oklch|inset)"

# 1c. Raw blur / glass elevation  (category e) — backdrop-blur-md, backdrop-blur-[2px], blur-[6px].
scan '(backdrop-)?blur-(\[|sm|md|lg|xl|2xl|3xl)'

# 2. Inline style with a raw color literal  (category b) — -U so multiline style objects also fire.
scan -U 'style=\{[^}]*(#[0-9a-fA-F]{3,8}|rgb\(|hsl\()'

# 3. Raw layout spacing on generic containers  (category c) — space-x/space-y, gap, and axis gaps
#    (gap-x/gap-y); named (gap-3), px (space-x-px), and arbitrary (gap-y-[10px]) values all fire.
scan --pcre2 '<div\s[^>]*className=[^>]*(space-[xy]|gap(?:-[xy])?)-(\[|px|[0-9])'

# 4. Hand-rolled muted secondary text  (category h)
scan "className=['\"]text-sm text-muted-foreground['\"]"

# 5. Hand-rolled error text  (category h)
scan 'text-xs\s[^"'"'"']*text-destructive'

# 6. Raw font-family utilities  (category d) — incl. mono; route code text through a typography token.
scan 'font-(sans|serif|mono)\b'

# 7. Inline transition timing  (category f) — transition-all is worst (animates layout → reflow).
scan 'transition-all|duration-[0-9]|\bease-(in|out|in-out|linear)\b'

# 8. Cross-layer leaks  (category g) — target the SYSTEM files, not SCAN_DIRS.
rg '@keyframes' "$TOKEN_MODULE" 2>/dev/null
rg '@apply\s+[^;]*(shadow-|bg-|text-|border-)' "$BASE_STYLESHEET" 2>/dev/null

# 9. Hand-rolled spinner / loading button  (category h)
#    The shared spinner/LoadingButton lives in an exempt dir, so an animate-spin hit in domain
#    code means inline reinvention — route it to the shared loading component.
scan 'animate-spin'
```

**Category coverage — and an honest limit.** Categories (a)–(g) are mechanically enforced (1a/1b →
a, 1b/1c → e, 2 → b, 3 → c, 6 → d, 7 → f, 8 → g). Category (h), _hand-rolled pattern markup_, is
open-ended by nature — you cannot regex every possible reinvented component — so it is **partially**
mechanized: checks 4, 5, and 9 catch the three highest-frequency cases (muted text, error text,
inline spinners), and genuinely novel hand-rolled patterns are caught in review.

This is a **heuristic gate, not a completeness proof.** The prefix and palette lists are the common
set; a repo with extra utilities or a custom palette extends `CPREFIX` and the color alternation to
match. The standing contract is narrow and verifiable: _every violation the prose names must have a
check that fires on its example_, and the lists are tuned per repo. A scanner shrinks drift; it does
not prove its absence. Add a category above → add its check here in the same change.

**Make "test each one" mechanical — don't trust it to honor system.** `scanner-fixtures/` ships
known-positive and known-negative lines, one pair per check (`positives.tsx`, `negatives.tsx`, plus
`cross-layer.*` for check 8). A check is healthy only when it returns ≥1 hit on the positives and 0
on the negatives — the negatives are the guard against over-matching greps that cry wolf (the exact
trap the shipped `h-screen`/`outline-none` greps in `review-protocol.md` are anchored to avoid). Run
the self-test (see `scanner-fixtures/README.md`) whenever you edit a check, and add a positive +
negative line in the same change as any new category.

**Wire it into pre-commit and CI.** Add it to the pre-commit hook (so it fails fast locally) and
to the CI lint job (so it blocks merge). The value comes from the gate — a scanner that only runs
manually gets skipped under deadline pressure.

**Message at the violation site.** Each check's output should point at the fix, not just the
problem:

```
src/components/features/dashboard/stats.tsx:42 — hardcoded text-green-500 — use feedback token or semantic text-success-foreground
```

Short, actionable messages lower the cost of fixing violations. Engineers shouldn't have to read
the full audit guide to fix a single line.

---

## Exempt-Files Governance

The files that DEFINE the design system are allowed to contain raw values — they are the source of
tokens, not consumers of them. Every other file consumes the system.

| Category                         | What to exempt                                     | Why                                                                                                                 |
| -------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Base stylesheet                  | `globals.css` (or equivalent)                      | Defines the CSS custom properties that ARE the tokens                                                               |
| Token module                     | `design-tokens.ts` (or equivalent)                 | TypeScript constants that reference the CSS vars                                                                    |
| Theme variants                   | `themes.ts`, theme config files                    | Decorative swatches and variant overrides that must name raw palette values to preview them                         |
| UI base components               | `components/ui/**` (e.g. shadcn/ui upstream files) | Upstream library code; audited separately for CSS-variable compliance, not for token-module imports                 |
| Layout primitive implementations | `components/primitives/**`                         | These implement the primitives that other code should use; they can't import the token module without circular deps |
| Pre-CSS-pipeline boundaries      | `global-error.tsx`, bare HTML boundaries           | No Tailwind/CSS pipeline available; inline styles are the only option                                               |

**The critical nuance about UI base components:** exempting them from the scanner means they are
exempt from importing the token module (that would create a circular dependency). It does NOT mean
they can embed arbitrary hardcoded visual values. Base components still participate in the design
system — they do so through CSS custom properties (`var(--foreground)`, `var(--border)`) rather
than through the TypeScript token module. The css-audit pass should still check UI primitives for
hardcoded shadows, durations, and opacity overrides that bypass those variables.

**Don't add new files to the exempt list without documenting why.** Each exemption is a door left
open. The two valid reasons are: (1) the file defines the system, or (2) the CSS pipeline is
unavailable. A file that's "too complex to fix right now" is not a valid exemption — track it as a
violation instead.

---

## Governance — When to Promote a Pattern to a Token or Component

A token audit that relocates one-offs into the token layer creates noise, not clarity. Token
proliferation (too many named values for subtly different situations) is its own form of rot.

**The 3-usages rule applies only to extracting a reusable _composition_ or shared _component_** — a
recurring bundle of classes, or a repeated UI pattern. Promote it to a named token/component once it
appears in three or more distinct places; below that, duplication is cheaper than the wrong
abstraction.

**It is never a license to leave a raw visual value in domain code.** A single hardcoded color,
shadow, blur, surface radius, layout spacing, or motion timing is a violation at the _first_ use, not
the third. Below the 3-usage threshold:

- If the value maps to an existing concept, use the nearest existing semantic token or CSS var —
  even for a one-off, even if it isn't a perfect match.
- If the value is genuinely novel, add it to the foundation (a CSS var / token) _before_ using it.
  There is no "leave it raw with a comment" exception — that is exactly the drift the audit exists to
  catch.
- File a design review if the novelty looks like a system gap rather than a one-off.

(Only **structural** utilities — layout, sizing, overflow, positioning — may stay raw; they encode no
visual decision. See `building-a-design-system.md` → "Where does a new value go?".)

When you do add a token:

1. Add the CSS custom property to the base stylesheet (`:root` and `.dark` if the repo supports
   dark mode).
2. Add the `@theme` or framework mapping so your utility layer (e.g. Tailwind) generates the class.
3. Add the TypeScript constant to the token module.
4. Update the scanner to flag the raw value and point at the new token.
5. Update the audit skill or documentation so the next auditor knows the fix target.

---

## A Note on Severity

In the context of the review protocol, token violations are typically 🟡 Important — not 🔴
Critical. They degrade consistency and make theme changes expensive, but they don't block users from
completing their task. Downgrade to 🟢 Opportunity when the violation is in a rarely-touched file
unlikely to drift further. Upgrade to 🔴 Critical only when the hardcoded value actively breaks
accessibility (contrast ratio below 3:1) or dark-mode legibility.

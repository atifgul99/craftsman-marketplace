# Scanner fixtures — make "test each check" mechanical

`token-audit.md` states the scanner's standing contract: _every violation the prose names must have
a check that fires on its example._ These fixtures turn that promise into something you can run.

- **`positives.tsx`** — one labelled line per check (1a, 1b, 1c, 2, 3, 4, 5, 6, 7, 9). Each line
  **must** be caught by its check.
- **`negatives.tsx`** — the correct, token-routed equivalent of each. **No** check may fire here; a
  hit is a false positive (the check over-matches and will cry wolf).
- **`cross-layer.tokens.ts`** / **`cross-layer.base.css`** — fixtures for check 8 (cross-layer
  leaks), which targets the token module and base stylesheet directly rather than the JSX surface.

## Self-test (run when you edit any check)

Point each check at the fixtures instead of the repo. A check is healthy when it returns **≥ 1 hit**
against `positives.tsx` and **0 hits** against `negatives.tsx`. Sketch:

```bash
cd "$(dirname "$0")"   # this directory

# Example: check 1a (named palette classes) must hit positives, miss negatives.
CPREFIX='(text|bg|border(-[trblxyse])?|ring|ring-offset|outline|divide|fill|stroke|decoration|accent|caret|placeholder|shadow|from|via|to)'
PAL='(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)'

pos=$(rg -c "${CPREFIX}-${PAL}-[0-9]+" positives.tsx || echo 0)
neg=$(rg -c "${CPREFIX}-${PAL}-[0-9]+" negatives.tsx || echo 0)
[ "$pos" -ge 1 ] && [ "${neg:-0}" -eq 0 ] && echo "1a OK" || echo "1a BROKEN (pos=$pos neg=$neg)"
```

Repeat per check, copying each regex verbatim from `token-audit.md` → Building the Scanner. For
check 8, run its two `rg` lines against `cross-layer.tokens.ts` (the `@keyframes` line must hit) and
`cross-layer.base.css` (the `@apply shadow-…` line must hit; the bare `@keyframes` there must not).

When you **add a category** to the prose, add (1) its check in `token-audit.md`, and (2) a
positive + negative line here in the same change. A category without a fixture line is unverified.

## Using these in a real repo

Copy this directory in, **add it to the scanner's `EXEMPT` list** so production sweeps skip it, and
run the self-test as its own step (pointed only at the fixtures). The fixtures exist to test the
*checks*, not to be swept alongside real code.

# .craftsman — production-readiness audit workspace

> Generated: 2026-06-22 · commit a1bec8f · craft-audit
> (Illustrative example — see `../README.md`. Not a real audit.)

This directory contains a craftsman-marketplace audit for Invoicely. It is gitignored — working
state, not source. See `master-tracker.md` for current status and the prioritized fix list, and
`audits/<scope>/<domain>/findings.md` for per-domain findings.

## How to read this folder

- **`master-tracker.md`** — start here. Shows audit status, the ordered climb sequence (do-these-first
  findings), readiness grades per surface, and the delta report from the last re-run.
- **`discovery.md`** — what this project is: shape, stack, maturity read, with file citations.
- **`applicability.md`** — which of the 10 craft domains apply here, and why (9 of 10 apply; craft-ai N-A).
- **`audits/<scope>/<domain>/plan.md`** — the tailored audit plan for each applicable surface.
- **`audits/<scope>/<domain>/findings.md`** — findings with stable IDs, severity, status, and fix links.

`<scope>` is `root` for this single-app repo.

Grades and statuses are as of the `Generated` commit shown in `master-tracker.md` (2026-06-22 ·
a1bec8f) — if the project has moved since (check with `git log a1bec8f..HEAD`), treat the
grades/statuses as historical and re-run the audit.

## This snapshot's completeness

All applicable domains (9 of 10; craft-ai N-A — no LLM surface) have plans + findings (Tier-1
complete for teaching). In a real mid-climb workspace you might still see ❔ Unaudited rows —
re-invoke craft-audit with `.craftsman/` in place and it will pick up from the last completed step,
diffing rather than rewriting. See `references/rerun.md` in the plugin for the full re-run protocol.

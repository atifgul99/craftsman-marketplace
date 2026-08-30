# Code Quality

> **Pairs with:** `discovery.md` — quality tooling evidence is collected during step 2 of the audit
> loop and recorded in `.craftsman/discovery.md`. `workspace.md` defines where findings land in the
> findings file.

**Boundary:** gate wiring and enforcement (CI gate, pre-commit, the `quality` script) → infra domain
(this file); rule content, resolved-config audit, and severity calibration → craft-lint (the `lint`
domain; see `craft-lint/references/standard.md`).

The goal is a consistent quality gate that catches real bugs and enforces team norms — not maximum
rule coverage. A quality setup no one runs locally, or that fires on safe code, trains developers to
ignore it.

## Detection — what exists

Check these before proposing anything:

- **Linter config**: `eslint.config.*`, `.eslintrc.*`, `biome.json`, `.stylelintrc.*`, `pyproject.toml`
  (ruff/flake8 sections), `.flake8`
- **Formatter config**: `.prettierrc.*`, `prettier.config.*`, or `"prettier"` key in `package.json`
- **Quality scripts**: look for `lint`, `lint:fix`, `format`, `typecheck`, `check`, `quality` in
  `package.json` → `scripts`
- **Pre-commit enforcement**: `.husky/` directory, `.pre-commit-config.yaml`, `lint-staged` in
  `package.json`
- **CI gate**: `.github/workflows/`, `.circleci/`, or equivalent — check whether any step runs lint
  or typecheck as a required gate
- **TypeScript strictness**: `tsconfig.json` — `"strict": true`, `"noImplicitAny"`, `"strictNullChecks"`

Report what's missing before proposing additions. A project with none of these needs the enforcement
layer first (CI + pre-commit), then the tooling.

---

## Implementation — pointer only

Ruleset selection, resolved-config auditing, formatter/linter overlap, suppression-comment hygiene,
and severity calibration for lint rules are **craft-lint**'s content now (`craft-lint/references/standard.md`).
This file no longer restates it — see that reference for what to apply and how to judge it.

---

## The `quality` script — one command, locally and in CI

Define a single `quality` (or `check`) script in `package.json` that runs what CI runs:

```
pnpm quality  →  lint + typecheck + test:unit (fast subset)
```

This is the command developers run before pushing, and the command CI runs in the quality gate. They
must be identical — running different checks locally vs CI is how "it passes CI but breaks locally"
situations develop in reverse.

Example shape (adapt to the actual stack and scripts):

```json
"scripts": {
  "lint": "...",
  "lint:fix": "...",
  "typecheck": "tsc --noEmit",
  "quality": "pnpm lint && pnpm typecheck"
}
```

If the project uses a Makefile, `Taskfile.yml`, or similar, expose `quality` there instead — the
principle is one entry point, not one specific tool.

---

## Enforcement gates

Having quality tooling in `package.json` without enforced gates is equivalent to not having it — a
developer who skips running it before pushing still ships unreviewed code.

**1. Pre-commit hook (fast, local)**
Run the linter only on staged files via lint-staged. Fast (seconds, not full-repo), catches the most
common mistakes before they hit CI. Can be skipped with `--no-verify`, which is why CI is still
required.

Discover whether the repo already uses husky or a similar hook manager before adding one. Extend
what exists; don't layer a second hook runner over it.

**Verify lint-staged is discoverable.** `lint-staged` finds its config via auto-discovery (checks for
`lint-staged.config.*`, `.lintstagedrc.*`, or a `"lint-staged"` key in `package.json`, in that
precedence order). The `"lint-staged"` key in `package.json` must be an object — not a file path
string like `"./lint-staged.config.mjs"`, which `lint-staged` does not support. If the config lives in
a standalone file, the `package.json` key should be absent so auto-discovery finds it; a project with
both is a finding (ambiguous config, pick one).

**2. CI quality gate (authoritative)**
A dedicated CI job that runs `pnpm quality` (or equivalent) on every PR push, marked as a required
check in branch protection. This is the gate that actually cannot be bypassed.

Order it correctly relative to other CI jobs: lint and typecheck are the cheapest signal and should
run first (and in parallel with each other), before tests and build spin up. See `craft-infra` →
`references/ci-cd.md` for gate ordering.

**3. TypeScript strictness**
`"strict": true` in `tsconfig.json` for new projects. For projects migrating incrementally, turn on
flags one at a time — `strictNullChecks` first, then `noImplicitAny` — and track what remains. A
project stuck at half-strict indefinitely is not improving; document the remaining flags and a
migration path.

---

## Consistency — keep local and CI in sync

The most common quality setup failure is drift between what the pre-commit hook runs, what `pnpm
quality` runs, and what CI runs. They diverge when someone tightens a CI rule but forgets the local
script, or adds a new check to CI without updating the hook.

The fix is structural: the CI job calls the same `quality` script the developer calls. One source of
truth. When the script changes, local and CI both change together.

If the repo has multiple packages or workspaces, define `quality` at the root and have it run each
workspace's quality script. Centralized entry point, distributed execution.

---

> **Last reviewed: 2026-06-26.**

---
name: craft-lint
description: >-
  The Craftsman standard for linting and static quality gates — ESLint version policy, resolved-rule
  extraction, typed TypeScript linting, React/Next/a11y/security rule hardening, zero-warning CI
  gates, lint-staged/pre-commit alignment, and migration from weak/default ESLint configs to an
  enterprise-grade lint setup. Scope is **JS/TS ESLint surfaces**; if the project has no ESLint
  surface (Python/Ruff, Biome-only, Go, etc.), mark the domain N-A or partial with a one-line reason
  rather than forcing an ESLint 10 migration. Use this WHENEVER the work touches ESLint, lint rules,
  lint failures, lint config migration, quality scripts, pre-commit linting, or "standardize linting"
  across a JS/TS project. For whole-project production readiness, craft-audit routes here for the
  linting slice when ESLint applies.
---

# Lint Craft

This skill owns linting as a first-class code-quality surface **for JS/TS ESLint**. Version choice
matters, but the real standard is the resolved rule contract: typed linting, runtime-risk rules as
errors, context-specific React/Next/a11y/security rules, and a zero-warning gate that developers and
CI both run.

**Applicability.** If discovery finds **no JS/TS ESLint surface** — e.g. Python-only with Ruff,
Biome-only (no ESLint), Go with `golangci-lint`, Rust with clippy — mark the domain **N-A** or
**partial** with a one-line reason (what linter *is* present). Do **not** demand ESLint 10 flat config
on a non-ESLint stack. This skill does not expand into a multi-linter catalog; honest N-A is correct.

## Operating principle — discover before you build

Do not judge a lint setup from config prose alone. First confirm ESLint is in scope (see
applicability). Then fetch the **resolved ESLint rules** for real source files with
`eslint --print-config` wherever possible, and compare those resolved rules against the standard for
that project's context.

If `--print-config` fails, record the failure and fall back to direct config-file inspection. A failed
resolved-config extraction is itself a finding: the team cannot reliably reason about what linting is
actually enforcing.

## Workflow

1. **Discover**
   - Read package manager files, `package.json`, ESLint configs, TS configs, formatter configs, CI,
     husky/lint-staged, and workspace layout.
   - Identify project contexts: TypeScript library, Node/API/worker, Next app, React UI, JS-only app,
     docs/content-only package.
   - Identify ESLint major/version and plugin versions.

2. **Extract resolved rules**
   - Prefer the helper script in `scripts/eslint-rule-audit.mjs`.
   - Run it from this skill folder against the target repo:

     ```bash
     node /absolute/path/to/craftsman/skills/craft-lint/scripts/eslint-rule-audit.mjs /absolute/path/to/target-repo
     ```

   - The script writes evidence under the target repo:
     - `.craftsman/lint-audit/resolved-print-config-results.json`
     - `.craftsman/lint-audit/resolved-print-config-summary.json`
     - `.craftsman/lint-audit/standard-rule-gap-matrix.json`
     - `.craftsman/lint-audit/standard-rule-gap-matrix.md`
     - `.craftsman/lint-audit/top-project-gap-summary.json`

3. **Compare to the standard**
   - Read `references/standard.md`.
   - Compare each resolved package to the context-appropriate preset, not a blind universal list.
   - Separate "not applicable" from "missing." A backend package does not need jsx-a11y; a UI app does.

4. **Recommend or implement**
   - If the user asks for an audit: write findings with evidence, risk, and an ordered migration plan.
   - If the user asks to fix: implement the smallest config/package/script changes that move the repo
     toward the standard without destabilizing unrelated surfaces.
   - Prefer ESLint 10 flat config for active JS/TS projects. Keep ESLint 8 only as a temporary
     exception when a concrete dependency blocker appears. Do not target ESLint 9 as the standard.

5. **Verify**
   - Run `eslint --print-config <representative-file>` after changes.
   - Run the repo lint command with `--max-warnings 0` where feasible.
   - Run typecheck if typed linting was added.
   - Record any blocked verification exactly.

## What Good Looks Like

- Version & config policy (ESLint 10 flat config, migration sequence, when ESLint 8 is an acceptable exception) → `references/standard.md` § Version Policy, § Migration Sequence
- Context presets — which packages get which rule sets (base, typechecked TS, node, React, Next, a11y, security, tests, architecture) → `references/standard.md` § Presets
- The rule contract — which rules must be errors vs. acceptable warnings, by context (base, TypeScript typechecked, React/Next/UI, security/architecture, tests) → `references/standard.md` § Required Rule Contract
- Known anti-patterns to flag on sight (stale `.eslintignore`, `next lint` as the only gate, permanent warnings on risk rules, formatter/linter conflicts) → `references/standard.md` § Anti-Patterns

## Reference index

- `references/standard.md` — version policy, context presets, rule contract, migration sequence.

## Audit checklist (for craft-audit)

When `craft-audit` plans a linting pass for a scope, it turns this checklist into the
`plan.md` todo list — the checklist is owned by this skill, not improvised by the orchestrator. Tailor
to what discovery found: skip a step that genuinely doesn't apply with a one-line reason; never
silently drop one. Emit findings using craft-audit `workspace.md` → "Canonical findings.md emission
format" (authority). Heading grammar (variables required — do not hardcode NNN/severity/status):

`## <scopeLabel>-LINT-<NNN> · severity <🔴|🟡|🟢> · status <open|fixed|wontfix (reason)|regressed|fixed (merged into <ID>)>`

Example only: `## <scopeLabel>-LINT-001 · severity 🔴 · status open`

Required fields under each heading, in order, with these exact labels:
`**What breaks (plain language):**` · `**Technical:**` · `**Fix:**` · `**Fingerprint:**` ·
`**Last-checked:**` (optional `**Fix-attempt:**` only from craft-fix).
Assign sequential NNN per (scope, domain); judge severity with craft-audit `prioritization.md`.
Forbidden: `###` headings; `## ID · 🔴 · open` shorthand; severity/status as body bullets.

- [ ] **Applicability first:** if no JS/TS ESLint surface (Python/Ruff, Biome-only, Go, etc.), mark
      domain N-A or partial with a one-line reason and stop — do not force ESLint 10. → SKILL.md
      Applicability
- [ ] Inventory ESLint/package/plugin versions, config files, lint scripts, formatter config, TS strictness, CI lint gates, and pre-commit/lint-staged setup. → `references/standard.md` § Version Policy
- [ ] Run resolved-rule extraction with `scripts/eslint-rule-audit.mjs` or document why it cannot run. → `scripts/eslint-rule-audit.mjs`
- [ ] Compare resolved rules to context presets: base, typechecked TS, node, React, Next, a11y, security, tests, architecture. → `references/standard.md` § Presets
- [ ] Flag syntax-only TypeScript linting as insufficient for production TypeScript. → `references/standard.md` § Required Rule Contract (TypeScript Typechecked)
- [ ] Flag `next lint`, missing config, build-skipped linting, warnings-as-steady-state, stale `.eslintignore`, and unused-disable comments that do not fail. → `references/standard.md` § Anti-Patterns
- [ ] Identify rules currently warn/off/missing that should be errors for runtime quality. → `references/standard.md` § Required Rule Contract
- [ ] Propose the smallest migration to ESLint 10 flat config, with ESLint 8 exception only for named blockers. → `references/standard.md` § Migration Sequence
- [ ] Verify with `--print-config`, lint, and typecheck where feasible. → `scripts/eslint-rule-audit.mjs`


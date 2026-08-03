# Lint Standard

## Version Policy

- **Standard target:** ESLint 10.x, flat config, current compatible `typescript-eslint`.
- **Do not standardize on:** ESLint 9. Treat it as transitional inventory.
- **Temporary exception:** ESLint 8.57.x only when a repo has a concrete plugin/framework blocker.

Version is not the quality bar. The quality bar is the resolved rule contract below.

## Presets

Use presets by context. Do not force every package to carry every rule.

| Preset | Applies to | Purpose |
| --- | --- | --- |
| `base` | all JS/TS packages | correctness basics, focused-test guards, unused-disable reporting, formatter compatibility |
| `typescript-typechecked` | production TS source | runtime bug prevention through typed rules |
| `node` | APIs, workers, CLIs, libraries | Node globals and backend-safe defaults |
| `react` | React UI code | hooks correctness and render bug prevention |
| `next` | Next apps | Next rules plus direct ESLint flat config, not stale wrapper-only linting |
| `a11y` | user-facing UI | accessibility rules as real quality gates |
| `security` | auth, API, file/network/database code | security linting with reviewed noisy-rule exceptions |
| `tests` | test files | limited relaxations, focused-test blocks, test-layer boundaries |
| `architecture` | app-specific boundaries | restricted imports/syntax for project-specific invariants |

## Required Rule Contract

### Base

- `eqeqeq`: error
- `curly`: error
- `no-debugger`: error
- `no-console`: warn for apps, error/off-by-override for libraries/scripts as appropriate
- `no-restricted-properties`: block `describe.only`, `it.only`, `test.only`
- unused disable directives: error
- formatter compatibility: `eslint-config-prettier` or equivalent last

### TypeScript Typechecked

Production TypeScript must use type information. Syntax-only TypeScript linting is not enough.

- `@typescript-eslint/no-explicit-any`: error
- `@typescript-eslint/no-floating-promises`: error
- `@typescript-eslint/no-misused-promises`: error
- `@typescript-eslint/await-thenable`: error
- `@typescript-eslint/no-unsafe-assignment`: error or staged warn during migration
- `@typescript-eslint/no-unsafe-call`: error or staged warn during migration
- `@typescript-eslint/no-unsafe-member-access`: error or staged warn during migration
- `@typescript-eslint/no-unsafe-return`: error or staged warn during migration
- `@typescript-eslint/no-unsafe-argument`: error or staged warn during migration
- `@typescript-eslint/strict-boolean-expressions`: error for backends/libraries, staged warn for noisy UI migrations
- `@typescript-eslint/no-unnecessary-condition`: error for backends/libraries, staged warn for noisy UI migrations
- `@typescript-eslint/switch-exhaustiveness-check`: error
- `@typescript-eslint/no-non-null-assertion`: error in production code
- `@typescript-eslint/consistent-type-imports`: error
- `@typescript-eslint/no-import-type-side-effects`: error

### React / Next / UI

- `react-hooks/rules-of-hooks`: error
- `react-hooks/exhaustive-deps`: error
- `react/jsx-no-leaked-render`: error
- Next core web vitals/type rules for Next apps
- `jsx-a11y/recommended` for user-facing UI; serious a11y rules should not stay warnings
- preserve project design-token rules and raise raw-color/design-system violations to error

### Security / Architecture

- Security plugin recommended rules for backend/API/auth/file/network/database surfaces.
- Manually triage noisy rules such as object injection; do not disable the whole security preset.
- Use `no-restricted-imports` and `no-restricted-syntax` for real project invariants:
  - Temporal workflow determinism
  - server/client boundaries
  - no direct DB access from wrong test layers
  - no restricted auth/secret imports
  - design-system boundaries

### Tests

Tests may relax:

- `@typescript-eslint/no-explicit-any`
- `@typescript-eslint/no-non-null-assertion`
- selected security/file-system rules for tests that intentionally exercise unsafe inputs

Tests must not relax:

- focused-test guards
- promise correctness
- test-layer architectural boundaries

## Migration Sequence

1. Resolve current config with `eslint --print-config`.
2. Record current rules, warnings, off rules, and extraction failures.
3. Upgrade or create ESLint 10 flat config where compatible.
4. Add typed linting for production TypeScript.
5. Add context presets by package/surface.
6. Run lint with current severities.
7. Promote runtime-risk warnings to errors.
8. Enforce `--max-warnings 0` in CI.
9. Add pre-commit lint-staged only after CI is authoritative.

## Anti-Patterns

- Relying on `next lint` as the main long-term lint command.
- No local config, only framework defaults.
- TypeScript parser configured without typed rules.
- `no-explicit-any`, hooks deps, or a11y rules left as permanent warnings.
- Build skips lint and CI has no replacement gate.
- `.eslintignore` left in modern flat-config repos.
- Large `eslint-disable` clusters without unused-disable reporting.
- Formatting rules fighting Prettier/Biome.

## Out-of-scope stacks

- Biome-as-linter is acceptable when its rule coverage maps to the intent of this standard's Required Rule Contract — audit `biome.json` the same way you'd audit an ESLint config (rule coverage against correctness, TypeScript safety, React/hooks, a11y, security), not a demand to migrate to ESLint.
- Non-JS/TS stacks (Python/ruff, Go, etc.) are out of scope for this skill (craft-lint covers the JS/TS ecosystem). When auditing a project with a non-JS/TS lint domain, record that domain as N/A rather than improvising ESLint-shaped requirements onto a different language's tooling.

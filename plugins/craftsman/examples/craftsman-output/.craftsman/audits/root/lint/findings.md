# Lint Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-lint · scope: root

## root-LINT-001 · severity 🟡 · status open
**What breaks (plain language):** Lint is basically the framework default — it catches almost none of
the foot-guns this codebase already has (floating promises, `any`, unused insecure patterns). Bad
code still "passes lint."
**Technical:** `.eslintrc.json` (or Next default) extends only `next/core-web-vitals` with no project
rule overrides; no `eslint-config` composition for import boundaries or promise safety. Evidence:
config present as scaffold defaults only.
**Fix:** Adopt a deliberate rule set for a TypeScript Next app (promise/`no-floating-promises`
equivalents via typed lint, no-explicit-any as warn→error, import hygiene). See craft-lint →
`standard.md`.
**Fingerprint:** `scope=root · domain=lint · class=weak-default-eslint · resource=.eslintrc / eslint config`
**Last-checked:** 2026-06-22 · a1bec8f

## root-LINT-002 · severity 🟡 · status open
**What breaks (plain language):** TypeScript's typechecker and ESLint aren't working together — whole
classes of bugs (`any` abuse, unsafe member access) never show up in the editor or CI as lint
failures.
**Technical:** No `parserOptions.project` / typed-lint setup; `typescript-eslint` type-aware rules not
enabled. `tsc --noEmit` is not part of a lint script either.
**Fix:** Enable type-aware lint (or a dedicated `typecheck` script that CI runs beside lint). See
craft-lint → `standard.md`.
**Fingerprint:** `scope=root · domain=lint · class=no-typed-lint · resource=typescript-eslint project service`
**Last-checked:** 2026-06-22 · a1bec8f

## root-LINT-003 · severity 🟢 · status open
**What breaks (plain language):** Warnings never fail the build. A PR can pile up lint noise forever
and still merge — so the signal trains people to ignore it.
**Technical:** No CI step runs `eslint --max-warnings 0` (and no CI at all yet — `root-INFRA-002`).
Local `next lint` allows warnings.
**Fix:** Once CI exists, gate on `--max-warnings 0` (and fix or baseline deliberately). See craft-lint
→ `standard.md`.
**Fingerprint:** `scope=root · domain=lint · class=max-warnings-not-zero · resource=eslint CI invocation`
**Last-checked:** 2026-06-22 · a1bec8f

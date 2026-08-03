# Discovery & Applicability — what is this project, and which surfaces apply?

The audit is only as good as this step. Everything downstream — which domains run, what the plans
say, how findings are scoped — depends on an **evidence-based** read of the project. Guessing here
poisons the whole audit: you'll run craft-db on a static site, or skip observability on a payments
API. Read the artifacts, write down what you found *with citations*, then classify.

> **Pairs with:** `workspace.md` — discovery writes `.craftsman/discovery.md` and
> `.craftsman/applicability.md` using the templates there. `prioritization.md` consumes the
> applicability call to scope the climb sequence.

---

## Contents

- [Principle — cite, don't assume](#principle--cite-dont-assume)
- [What to read (the evidence)](#what-to-read-the-evidence)
- [Determining project shape](#determining-project-shape)
- [Detecting the existing stack](#detecting-the-existing-stack)
- [The maturity read — which register does this project need?](#the-maturity-read--which-register-does-this-project-need)
- [Reference calibration (opt-in) — what does this team's own "good" look like?](#reference-calibration-opt-in--what-does-this-teams-own-good-look-like)
- [Classifying which domains apply](#classifying-which-domains-apply)
- [Writing it down](#writing-it-down)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Principle — cite, don't assume

Every claim in `discovery.md` must trace to a file you actually read. "Uses Next.js App Router" is
worthless; "`next.config.mjs` + `app/` directory present, `package.json` `next@15.2`" is evidence.
The whole point of writing discovery down is that the *next* session (or the user) can trust it
without re-deriving it — and can tell when it's gone stale.

If something can't be determined from the repo, say so explicitly ("no CI config found —
deployment process unknown") rather than inventing a plausible answer. An unknown is itself a
finding.

---

## What to read (the evidence)

Read these in roughly this order; stop when the picture is clear:

- **`package.json` + lockfile** — dependencies (frameworks, ORM, auth lib, test runner), scripts
  (`dev`/`build`/`start`/`test`/`lint`), package manager (lockfile name: `pnpm-lock.yaml`,
  `package-lock.json`, `yarn.lock`, `bun.lockb`), and workspaces field.
- **Monorepo markers** — `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`, a root
  `apps/` + `packages/` layout.
- **Framework/build config** — `next.config.*`, `vite.config.*`, `astro.config.*`, `remix.config.*`,
  `svelte.config.*`, `nuxt.config.*`, `tsconfig.json` (path aliases reveal structure). For Next.js
  projects, **record the exact major version** — file conventions changed in v16 (`proxy.ts` replaced
  `middleware.ts`). Never flag a file as wrongly named before confirming the major version it targets.
- **Backend/runtime** — server entry (`server.ts`, `app/api/`, `src/routes`), framework (Express,
  Fastify, Hono, NestJS), serverless config (`vercel.json`, `netlify.toml`, `wrangler.toml`).
- **Data layer** — ORM/query config (`drizzle.config.*`, `prisma/schema.prisma`, `knexfile`),
  migration directories, a `db/` or `schema/` folder. **If multiple DB client packages appear in
  `package.json` (e.g. both `@neondatabase/serverless` and `pg`), read the actual db instantiation
  file** (`apps/*/src/lib/db.ts`, `src/db/index.ts`, the server entry) to confirm which driver is
  actually in use — the most prominent package-name is not always the active connection layer.
- **Infra/deploy** — `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `fly.toml`,
  `railway.json`, Terraform/Pulumi, `k8s/`.
- **Config & secrets posture** — `.env.example` / `.env.template`, a validated-env module
  (`env.ts`/`env.mjs`, `@t3-oss/env`), what's committed vs ignored (`.gitignore`).
- **Observability** — Sentry/OTel deps, `instrumentation.ts`, logging libs, a `monitoring/` dir.
- **Quality tooling** — `eslint.config.js` / `.eslintrc.*`, `biome.json`, `prettier.config.*` /
  `.prettierrc.*`, `.husky/pre-commit` — read to understand formatter/linter configuration and
  pre-commit quality gates. Also check `tsconfig.json` for `"strict": true` / `"strictNullChecks"`
  and `package.json` → `scripts` for `lint`, `lint:fix`, `format`, `typecheck`, `check`, `quality`.
  Record what exists and what is absent — a missing enforcement layer is itself a finding.
  → `references/quality.md`
- **LLM / AI surface** — deps like `openai`, `@ai-sdk/*`, `@anthropic-ai/*`, `langchain`,
  `llamaindex`, or call sites to model APIs. Presence is evidence for `craft-ai`; absence is an
  honest N-A, not a gap.

---

## Determining project shape

Classify into one of these (it drives applicability and how many audit trees you create):

| Shape | Tells | Audit implication |
| --- | --- | --- |
| **Marketing / static site** | Astro/Next static export, no server routes, no DB dep, mostly content | UX-heavy; backend/db/observability often N-A or thin |
| **Single full-stack app** | One framework, `app/api` or a server + a DB | Most domains likely apply (ai only if LLM surface present) |
| **SPA + separate API** | Client build (Vite/CRA) + a distinct backend service | Audit each side; frontend vs backend split is real |
| **Monorepo (multi-app)** | workspaces + `apps/*` | One audit tree **per app**, plus shared `packages/*`; don't average them together |
| **Library monorepo** | workspaces with multiple publishable `packages/*`, little/no `apps/*` | Prefer one `root` scope; split per-package only when surfaces diverge — see below |
| **Library / package** | single package: `exports` field, no app entry, published to a registry | API-surface + supply-chain heavy; UX/infra often N-A |

For a monorepo, name each app and audit them separately in `.craftsman/audits/` — a marketing site
and a dashboard in the same repo have different bars.

### Scoping a library monorepo

When the repo is a monorepo of publishable libraries/packages (not multi-app):

1. Prefer **one `root` scope** for shared release, CI/quality gates, supply-chain, and workspace-wide
   policy findings.
2. Split **per-package scopes** (`packages/<name>`) only when packages have meaningfully different
   surfaces (different runtimes, public APIs, security postures) or when package-specific findings
   would otherwise be ambiguous under root.
3. Do **not** invent a scope per package by default when they share one release train and one quality
   bar — that multiplies near-identical findings without signal.
4. When both are needed: root holds workspace-wide findings; package scopes hold package-specific
   ones. Fingerprints always use the scope path that owns the resource. When only `root` is used,
   package paths appear in Technical/resource fields (and in the fingerprint `resource=`) rather
   than as separate scopes.
5. Cite evidence (workspace config, package.json `exports`, `apps/` absence) in `discovery.md` for
   the scoping choice.

---

## Detecting the existing stack

Record what's **already chosen** so the audit meets the project where it is (and so
`recommended-stack.md` only fills genuine gaps, never second-guesses a working choice):

- **Auth:** Clerk, Auth.js/NextAuth, Lucia, Supabase Auth, WorkOS, custom JWT, or **none**.
- **DB + access:** Postgres/MySQL/SQLite/Mongo; Supabase/Neon/PlanetScale/RDS; Drizzle/Prisma/raw.
- **Hosting/runtime:** Vercel, Netlify, Cloudflare, Fly, Railway, Render, a container, bare Node.
- **Observability:** Sentry, OTel, a logging lib, Grafana/Prometheus — or nothing.
- **Validation:** Zod/Valibot/Yup at the boundary — or unvalidated input.
- **LLM / AI:** OpenAI / Anthropic / Vercel AI SDK / LangChain / LlamaIndex / similar deps, or
  direct model API call sites — or none. Presence is evidence for `craft-ai`.

"None"/"nothing" is the most important value to record — it's where the recommendation engine and the
highest-severity findings come from.

---

## The maturity read — which register does this project need?

The skill's default voice is pitched at the fragile-MVP persona (`SKILL.md`). But the *same* audit run
against a mature, hardened codebase needs a different register — hunting for absent fundamentals that
are demonstrably present produces a useless report. So before planning, make a quick **evidence-based**
maturity call and write it into `discovery.md`. Classify into one:

| Maturity | Evidence (cite the files) |
| --- | --- |
| **pre-Tier-1** | No real auth, unvalidated input, no CI, few/no tests, secrets in client, no error tracking. The MVP case the persona assumes. |
| **partially Tier-1** | Some fundamentals wired (auth exists) but gaps (no per-resource authz, validation only on some routes, thin tests). |
| **post-Tier-1** | Real auth **and** per-resource authz, validation at the boundary, a real DB with constraints/per-resource authz enforced (DB-layer RLS or application-layer tenant scoping), CI, a meaningful test suite, error tracking — all evidenced. |

Read concrete signals, don't guess: presence of a test runner **and** real test files (not just the
dep), a CI workflow that runs them, a validated-env module, an auth lib **plus** authorization checks
in routes (auth installed ≠ authz enforced), migration history, tenant-scoping helpers or RLS policies. **Auth being installed
is not the same as authz being enforced** — verify before crediting it.

This call sets the register `prioritization.md` uses ("Register for mature codebases"). It is a
*register* signal, **not** a license to skip verification — a post-Tier-1 label still requires citing
the files that earned it, and you still confirm the fundamentals actually hold.

**Enterprise-awareness register (B2B/multi-tenant SaaS only).** When the project is, or is clearly
aiming to be, a B2B/multi-tenant SaaS, note in discovery whether SSO/SAML, RBAC beyond owner/member,
and audit logs exist — each with a citation or "absent, no evidence found." Record this as **register
information** ("enterprise buyers will ask for these"), not as a finding or a defect: the absence of
an enterprise feature is a product decision, not an audit gap, and "meet the project where it is"
still applies. This context may inform severity judgment on a *related* security finding (e.g. a
missing-authz bug is worse if the product already sells to multiple orgs) — nothing more; it never
generates a finding on its own.

---

## Reference calibration (opt-in) — what does this team's own "good" look like?

The craft skills supply *generic, stack-agnostic* standards. But a mature author/org usually has prior
art that defines their *real* bar — and a gap in the audited project is often already solved, well, in
code right next door. Calibrating to that beats abstract best-practice: the fix stops being "you should
have observability" and becomes "copy the ~30-line Sentry interceptor your sibling app already ships."

This is **opt-in and gap-triggered**, with a hard boundary on what you may read without permission:

- **Inside the audited project (low risk — do this freely):** the *other* apps/packages in the same
  monorepo are fair game as exemplars. If `apps/web` solves a thing `apps/admin` doesn't, cite it.
- **Outside the audited project (requires explicit user authorization — ask first):** sibling repos in
  the same parent directory or git org, and any in-repo reference codebases the project itself points
  at (e.g. `.private/*-ref`, "studied during development" in `CLAUDE.md`/README). **Do not** auto-crawl
  the parent directory, scan sibling repos, or read `.private/*` references by default — surface that
  these candidates exist and ask before reading them. (They may be private, unrelated, or out of scope.)
- **Gap-triggered, not a diff:** only reach for a reference *after* a concrete finding exists, to source
  a proven fix. Never diff every file against a sibling — that's noise, not calibration.
- **Use it in the Fix, not as a new finding source:** when a reference solves a gap, cite the concrete
  file as a copy-template in that finding's Fix line. This extends `recommended-stack.md`'s "defer to
  what already works" from *this project* to *what this team has proven elsewhere*.

If you do this, record which references you consulted (and that the user authorized any outside-project
reads) in `discovery.md` so the calibration is auditable.

---

## Classifying which domains apply

For each of the ten, mark **applies / partial / N-A** with a one-line reason. Heuristics:

| Domain | Applies when | Often N-A / partial when |
| --- | --- | --- |
| **craft-ux** | Any rendered UI | Pure API/library (N-A) |
| **craft-frontend** | A client app with state/data-fetching/forms | Static content site (partial), API-only (N-A) |
| **craft-backend** | Any server routes / API | Static site with no server (N-A) |
| **craft-db** | A persistent datastore | No DB / external-only data (N-A); read-only content (partial) |
| **craft-security** | Auth, user data, any input, any deploy | Almost always applies — rarely N-A |
| **craft-infra** | Anything deployed | Local-only prototype (partial) |
| **craft-observability** | Production traffic, real users, money/data at stake | Static marketing site (partial — error tracking only); throwaway demo (N-A) |
| **craft-testing** | Any code with logic worth protecting — auth, mutations, money, business rules | Pure static content with no logic (partial — a smoke test); throwaway demo (N-A) |
| **craft-lint** | Any JS/TS project, especially TypeScript/React/Next/Node | Docs-only repos with no executable JS/TS (N-A); non-JS projects (partial or N-A depending on tooling) |
| **craft-ai** | Any LLM integration — chat/agent/RAG, model API calls, tool-use, prompt pipelines (OpenAI/Anthropic/Vercel AI SDK/LangChain/etc.) | No model calls, no LLM SDK, no AI features (N-A) |

`craft-security` should almost never be N-A — if the project takes any input or ships anywhere, it
applies. Bias toward "applies" when unsure; mark N-A only with a concrete reason.

---

## Writing it down

Produce two files (templates in `workspace.md`):

- `.craftsman/discovery.md` — shape, **maturity read** (pre/partial/post-Tier-1, with the files that
  earned it), package manager, frameworks, existing stack, each with a file citation; a "generated at
  \<date\> / \<commit SHA\>" header; an explicit "unknowns" section. If reference calibration was used,
  note which references were consulted and that any outside-project reads were user-authorized.
- `.craftsman/applicability.md` — the ten-row applies/partial/N-A table with reasons; a count
  ("5 of 10 apply") the master tracker can quote.

---

## Quick-reject checklist

| Smell in your discovery pass | Fix |
| --- | --- |
| A claim with no file citation | Go read the file or mark it an unknown |
| Assumed `localhost:3000` / a framework not in `package.json` | Verify from config; never assume |
| DB client claimed from `package.json` when multiple drivers present | Read the actual db.ts/db/index.ts to confirm which driver is instantiated |
| Monorepo audited as one undifferentiated app | Split into per-app audit trees |
| Every domain marked "applies" with no reasons | Justify each; some are genuinely N-A |
| `craft-security` marked N-A on anything that takes input or deploys | Re-classify — it applies |
| No "unknowns" section | Add one; missing CI/deploy info is itself a finding |
| No maturity read — hardened repo audited at MVP register | Add the pre/partial/post-Tier-1 call with file evidence; shift the register (`prioritization.md`) |
| "post-Tier-1" claimed because an auth lib is installed | Verify authz is actually *enforced* in routes — installed ≠ enforced |
| Auto-read sibling repos / `.private/*-ref` without asking | Stop — outside-project references need explicit user authorization; inside-monorepo apps are fine |
| File-naming convention flagged without checking framework major version | Read `package.json` → exact semver first. Example: `proxy.ts` is **correct** for Next.js ≥ 16 — not dead code or a misnamed `middleware.ts`. |

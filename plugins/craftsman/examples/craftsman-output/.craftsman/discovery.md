# Discovery

> Generated: 2026-06-22 · commit a1bec8f · craft-audit

## Shape
Single full-stack app — Next.js App Router with server routes under `app/api/` and a hosted Postgres.
Evidence: `next.config.mjs`, `app/` directory, `app/api/invoices/[id]/route.ts`, `package.json`
`next@15.2.1`. Not a monorepo (no `pnpm-workspace.yaml` / `turbo.json` / `apps/` layout).

## Maturity (sets the audit register — see references/discovery.md)
**pre-Tier-1** — the fragile-MVP case. Evidence:
- Auth present but authZ not enforced: `@supabase/supabase-js` is wired and a session is read in
  `lib/auth.ts:8`, but route handlers don't scope queries to the caller (`app/api/invoices/[id]/route.ts`
  fetches by id with no tenant check). Auth installed ≠ authz enforced.
- No input validation lib in `package.json` (no `zod`/`valibot`); request bodies read raw
  (`app/api/invoices/route.ts:14`).
- No CI workflow (`.github/workflows/` absent).
- No test runner in `package.json` and no test files found.
- No error tracking (no `@sentry/*` dependency; no `instrumentation.ts`).
Register: audit at the fragile-MVP voice — these are missing-fundamental findings, not edge holes.

## Toolchain
- Package manager: npm (evidence: `package-lock.json`)
- Frameworks: Next.js 15.2 App Router, React 19 (evidence: `package.json`)
- Build/deploy: Vercel (evidence: `vercel.json`, no Dockerfile)

## Existing stack (meet the project where it is)
| Surface | Chosen | Evidence (file) |
| ------- | ------ | --------------- |
| Auth | Supabase Auth | `lib/auth.ts:1`, `package.json` `@supabase/supabase-js` |
| DB + access | Supabase Postgres, raw SQL via `postgres` client | `lib/db.ts:3`, `package.json` `postgres` |
| Hosting/runtime | Vercel (serverless functions) | `vercel.json` |
| Observability | none | no `@sentry/*`, no `instrumentation.ts` |
| Validation | none | no `zod`/`valibot` in `package.json` |

## Unknowns
- No `.env.example` committed — the full set of required env vars (and whether any secret is read
  client-side) couldn't be confirmed from the repo. Itself a finding (see security plan).
- RLS posture on Supabase tables is not visible in-repo (no migrations dir); must be confirmed in the
  Supabase dashboard. Treated as "assume off until proven on" for the db pass.

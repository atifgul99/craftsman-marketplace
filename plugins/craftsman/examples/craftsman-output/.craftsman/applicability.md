# Applicability

> Generated: 2026-06-22 · commit a1bec8f · craft-audit
> 9 of 10 domains apply.

| Domain | Verdict | Reason |
| ------ | ------- | ------ |
| ux | applies | Rendered dashboard UI (`app/(dashboard)/`) — design system, states, a11y in scope |
| frontend | applies | Client app with data-fetching, forms, and state (`app/(dashboard)/invoices/`) |
| backend | applies | Server routes under `app/api/` handle auth, validation, and mutations |
| db | applies | Persistent Postgres with tenant data (invoices, customers) |
| security | applies | Auth, multi-tenant user data, public input, a live deploy — high stakes |
| infra | applies | Deployed to Vercel; build/release, config, runtime health in scope |
| observability | applies | Real users + money (invoices) at stake, currently zero instrumentation |
| testing | applies | Auth, authZ, and money paths have logic worth protecting; no tests today |
| lint | applies | TypeScript + Next/React app — typed-lint contract and zero-warning gate in scope |
| ai | N-A | No LLM SDK, no model API calls, no chat/agent/RAG features in repo |

Single-app repo, so one applicability table (no per-app repeat).

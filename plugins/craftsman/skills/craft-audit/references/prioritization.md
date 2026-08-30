# Prioritization & Finding Voice — making the climb ordered and unscary

A production-readiness audit of a vibe-coded MVP can surface a hundred true findings. Dumped raw,
that list makes the user freeze and ship nothing — the audit *fails* even though every finding is
correct. This file is how you turn the pile into a sequence the persona can actually act on, and how
you write each finding so a non-expert understands it.

> **Pairs with:** the persona is defined in `SKILL.md` ("Who this is for"). `workspace.md` defines
> the finding ID/status format; this file defines the *voice* and the *order* that go in it.
> `recommended-stack.md` supplies the "what to add" when a finding is "X is missing".

---

## Contents

- [The finding voice — consequence before jargon](#the-finding-voice--consequence-before-jargon)
- [Severity — the user-impact test](#severity--the-user-impact-test)
- [The two tiers — MVP-hardening vs scaling to enterprise](#the-two-tiers--mvp-hardening-vs-scaling-to-enterprise)
- [Building the climb sequence](#building-the-climb-sequence)
- [How much to surface at once](#how-much-to-surface-at-once)
- [Quick-reject checklist](#quick-reject-checklist)

---

## The finding voice — consequence before jargon

The user used Lovable/Replit/Claude to build this; they don't know what IDOR, CLS, or N+1 means, and
a finding they can't understand is one they won't fix. Lead every finding with the **real-world
consequence in plain words**, then name the technical term so it's still searchable and precise.

**Bad (jargon-first, freezes the user):**
> IDOR on `GET /api/invoices/:id` — missing object-level authorization.

**Good (consequence-first, then precise):**
> Anyone can open another customer's invoice just by changing the number in the URL — their private
> billing data leaks. (This class of bug is called *IDOR / broken object-level authorization*.) Fix:
> scope the query to the logged-in user and deny by default. → craft-security `authz.md`,
> `api/invoices/[id]/route.ts:12`.

The pattern: **what breaks for a person → the name → the fix → the citation.** Keep the empathy real,
not patronizing — explain, don't talk down.

---

## Severity — the user-impact test

Use the same three-level model the domain skills use, judged by one question: *what does this cost a
real user or the business?*

- **🔴 Critical** — a breach, data loss/corruption, money lost, or the app unusable for a real user.
  Anything exploitable by an outsider, anything that loses or leaks data. Ship-blockers.
- **🟡 Important** — degrades the experience or reliability but has a workaround; will bite under
  load or edge cases (missing error states, no rate limiting, weak validation, N+1 that's fine today).
- **🟢 Opportunity** — polish, craft, and hardening that raises quality but nothing breaks without it.

When unsure between two levels, ask whether a stranger on the internet or a data-loss event is in
play — if yes, it's 🔴.

---

## The two tiers — MVP-hardening vs scaling to enterprise

The gap from "cool demo" to "enterprise-grade" is too big to present as one list. Split
recommendations into two tiers and match them to where the project actually is (from discovery):

- **Tier 1 — MVP-hardening ("don't embarrass yourself / don't get hacked / don't lose data").**
  The five-to-ten things that make an app *safe to have real users*: real auth + per-resource
  authorization, input validation at the boundary, a real database with integrity constraints,
  error/empty/loading states, error tracking (e.g. Sentry), secrets out of the client. This is where
  almost every vibe-coded MVP is missing the most, and it's where you start.

- **Tier 2 — scaling to enterprise.** Heavier infrastructure that only pays off with real scale and a
  team: SLOs and alerting, metrics pipelines (Grafana/Prometheus), distributed tracing, advanced
  caching, multi-region, fine-grained RBAC, audit logs. **Do not push Tier 2 on a project that hasn't
  cleared Tier 1** — self-hosted Prometheus is overkill for an app that still has no auth. Name Tier 2
  as the horizon, sequence it after Tier 1.

The master tracker's climb sequence is Tier 1 first, in severity order, then Tier 2.

### Register for mature (post-Tier-1) codebases

Not every project is a fragile MVP. Discovery's **maturity read** (`discovery.md`) may classify the
project as **post-Tier-1**: real auth + per-resource authz already wired, validation at the boundary,
a real database with constraints, error tracking, CI, a meaningful test suite. When it does, **shift
the register up** — auditing a hardened SaaS monorepo as if it had no auth produces a useless report:

- **Don't manufacture missing-fundamental 🔴s that don't exist.** If auth, validation, and integrity
  are demonstrably present, the headline findings are not "you have no X."
- **Lead with the gaps that bite a *working* system:** safeguards that break under concurrency,
  serverless ephemerality, load, operational failure, permission edges, or regression risk. These are
  typically 🟡 "this safeguard has a hole under \<condition\>", not 🔴 "you're missing the safeguard."
- **But "mature" never means "skip verifying."** Confirm the fundamentals are actually wired (cite the
  files) before downgrading the register — don't *assume* a tested repo got authz right everywhere.
- **Separate consequence from reach.** Record blast radius for every 🔴/🟡 finding (one user, one
  tenant, a cohort, all tenants, or system-wide) and use it to order peers. A missing process in a
  post-Tier-1 codebase is not automatically 🔴: it must create an exploitable, data-loss, money-loss,
  or unavailable-user path at the evidenced reach.
- Keep the plain-language voice regardless; a senior team still benefits from consequence-first
  findings. Just stop assuming the reader doesn't have the basics.

---

## Building the climb sequence

1. Pool every finding across the applicable domains (in a monorepo, across every scope's domains too).
   Key each finding by its **fingerprint tuple** (`scope` path, `domain`, `class`, `resource`) from
   `workspace.md`, and carry the authoritative `scope` path alongside the display ID label — so two
   scopes' findings never collide in the pooled list. Never identify a finding by parsing its ID
   label; the label is display-only.
2. Drop duplicates and merge near-identical findings (one "no input validation anywhere" beats
   fifteen per-endpoint copies — cite the worst, note the count).
   - **When the merged inputs disagree on severity** (the db pass called it 🔴, the backend pass 🟡),
     do **not** take `max()` — that inflates the 🔴 count and undoes the ruthless-prioritization
     goal. **Re-judge the merged finding once** against the breach/data-loss/user-impact test below,
     record that one severity, and note the disagreeing domain and its rating in the finding (e.g.
     "craft-db rated this 🔴; re-judged 🟡 — no outside attacker, bounded to one tenant's own data")
     so the call is auditable rather than arbitrary.
2b. **Reconcile cross-domain duplicates (one defect, seen through two lenses).** The same real defect
   often surfaces from two domain passes — e.g. "background jobs are `setInterval` loops that never
   run on serverless" comes out of *both* backend and infra. Because the fingerprint tuple includes
   `domain` (by design — see `workspace.md`), these are correctly two distinct fingerprints and two
   IDs. **Do not change that, and do not reverse-parse labels.** Reconcile them only here, at
   synthesis, with a *rollup layer above* the fingerprints:
   - Group findings that share a **rollup key** `(scope, class, resource)` — i.e. the fingerprint
     *minus* `domain`. A group of size > 1 is one defect seen by multiple domains.
   - Pick a **canonical owner** (the domain that owns the fix — for a missing cron runner that's
     infra; for a missing authz check that's security) and show that one row in the climb sequence.
   - Cross-link the others as tracker metadata: **"rolled up under \<canonical-ID\>"**. Do **not**
     mark them `fixed` — `fixed` is a lifecycle state and the defect is *not* fixed; each finding
     keeps its own authoritative fingerprint and `open`/`regressed` status in its domain `findings.md`.
   - This keeps the climb sequence free of visible duplicates without corrupting per-domain identity
     or rerun matching. See the master-tracker template's "Cross-cutting" note in `workspace.md`.
   - **Count rollup groups once.** When you tally the headline 🔴/🟡/🟢 totals (the "N distinct open
     🔴" line and the overall-readiness summary), count each rollup *group* once — not once per
     domain it surfaced in. Summing the per-domain status-table counts double-counts a rolled-up
     defect and re-inflates the 🔴 number the rollup just deduplicated. The per-domain status table
     still shows each domain's own count (DB-001 under db, SEC-002 under security); the *headline*
     collapses the group.
   - **The exact `(scope, class, resource)` key is a cheap first pass, not the whole rollup.** On a
     first run — no prior audit vocabulary to reuse — independent domain subagents routinely invent
     different `class`/`resource` strings for the same defect (a webhook signature bug can arrive as
     `class=webhook-signature-check-dead-code` from security and `class=webhook-signature-not-verified`
     from backend, zero string overlap). **A group count of zero does not mean there are no
     duplicates** — on a first run it usually means the vocabulary diverged, not that the pool is clean.
   - **Run a second pass by real-world defect.** After exact-key grouping, read the flattened list and
     compare what each finding actually cites — the concrete file:line, route, table, component, or env
     key — not the `class` string. Two findings anchored to the same file:line (or the same table/env
     key) are one defect however differently the domains named it; group and roll them up exactly as
     above. Preserve each original fingerprint verbatim and record which one was chosen as canonical.
   - Don't stop after the exact-key pass and call it a clean bill of health — the semantic pass is
     mandatory, not a fallback for when something looks off. Write the review to `dedup-map.md`
     before the tracker is generated: raw eligible finding count, exact-key groups, semantic candidate
     pairs/groups, evidence compared, and `roll up` or `keep separate` for every candidate. If there
     are no semantic rollups, record the candidates reviewed and an explicit `keep separate` decision;
     zero exact-key groups is never proof that semantic reconciliation was unnecessary.

2c. **Merge cross-scope same-resource findings (one defect in a shared library, seen from multiple
   scopes).** In a monorepo, a shared package (e.g. `packages/shared/src/ai/adapter.ts`) can surface
   as a finding in multiple scopes — `apps/web` and `apps/worker` both import it, both audits flag
   it. These have *different* fingerprints (the `scope` field differs) and are legitimately separate
   records in their domain `findings.md` files. Merge them at the tracker level:
   - Group findings whose `resource` field is identical across scopes (the same file path, route, or
     table — not just the same `class`).
   - In the climb sequence, show one row. Assign it to the scope where the resource is **defined**
     (not consumed). Take the higher severity across the group. Unlike 2b, cross-scope groups are the
     same resource seen from multiple scopes, so carrying over the higher severity is correct — no
     re-judging needed.
   - Add a "surfaced by" note listing the other (scope, domain) pairs: e.g. "also flagged by
     `apps/worker` · backend".
   - Each finding keeps its own fingerprint, ID, and `open` status in its domain `findings.md` —
     this is tracker-level display merging only, not a lifecycle change.

3. Sort: 🔴 Tier 1 → 🟡 Tier 1 → 🔴 Tier 2 → 🟡 Tier 2 → 🟢. Within a band, order by blast radius
   (how many users/how much data) and by how cheap the fix is (a one-line deny-by-default beats a
   week of refactoring — surface quick high-impact wins early). For each grade, surface the distance
   to the next grade (`N 🔴 blockers remaining`, then `N 🟡 risks remaining`) so a mature project with
   several blocked domains has an actionable path rather than identical red labels.
4. Write the ordered list into `master-tracker.md` with plain-language summaries and IDs.

---

## How much to surface at once

**Lead with the readiness headline.** When surfacing results in chat, open with the overall readiness
grade and what gates it (e.g. "🔴 Blocked — gated by security"), *then* follow with the top 5–10
climb-sequence items. The headline orients the user before the detail does.

Don't print 100 findings in chat. Lead with the **Tier-1 climb sequence (the top ~5–10)**, say how
many more wait in each tier, and point to `.craftsman/master-tracker.md` for the full picture. Offer
to walk the next tier when the first is done. The on-disk record is complete; the *conversation* is
curated. Completeness lives in the files; focus lives in the chat.

---

## Quick-reject checklist

| Smell | Fix |
| --- | --- |
| Finding leads with an acronym the user won't know | Rewrite consequence-first, then name it |
| 100 findings dumped in chat | Surface top 5–10 Tier-1; rest in the tracker |
| Tier-2 infra (Prometheus/SLOs) pushed before auth exists | Re-sequence — Tier 1 clears first |
| 15 near-identical findings listed separately | Merge; cite the worst + a count |
| Severity assigned by "feel" not user impact | Re-judge with the breach / data-loss test |
| A finding with no fix or no citation | Add both — a finding without a next step is noise |
| Exact-key rollups are empty and no semantic review artifact exists | Stop synthesis; write `dedup-map.md` and reconcile by cited evidence |
| Every mature domain reads "Blocked" with no next-grade distance | Show blocker/risk counts and rank by blast radius |

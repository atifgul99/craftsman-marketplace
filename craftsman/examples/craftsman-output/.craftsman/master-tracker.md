# Master Tracker

> Generated: 2026-06-22 · commit a1bec8f · craft-audit
> Applicable domains: 9 of 10 · Last full run: 2026-06-22 (Tier-1 complete — all applicable domains audited; craft-ai N-A)

## Climb sequence (do these first)
Ordered, persona-tiered — see prioritization.md. The **Scope** column keeps every row unambiguous
(here it's always `root`, a single app). Cross-domain duplicates are rolled up (see below), so each
real defect appears once.

| # | ID | Scope | Finding (plain language) | Severity | Status |
| - | -- | ----- | ------------------------ | -------- | ------ |
| 1 | root-SEC-001 | root | Anyone can open another company's invoice by changing the URL number | 🔴 | open |
| 2 | root-DB-001 | root | The database doesn't enforce tenant separation — one missed filter exposes everyone | 🔴 | open |
| 3 | root-BE-002 | root | A money route skips the auth helper — unauthenticated callers can mutate invoices | 🔴 | open |
| 4 | root-TEST-001 | root | Zero tests on the invoice create/pay money path | 🔴 | open |
| 5 | root-TEST-002 | root | No regression test for the invoice IDOR — the hole can reopen silently | 🔴 | open |
| 6 | root-SEC-003 | root | The server trusts whatever the browser sends — no validation at the door | 🟡 | open · fix-attempted 2026-06-24 |
| 7 | root-SEC-004 | root | Can't confirm the DB admin key isn't reachable from the browser | 🟡 | open |
| 8 | root-DB-002 | root | Invoices can reference customers that don't exist; deletes orphan data | 🟡 | open |
| 9 | root-BE-001 | root | Errors are raw 500s / inconsistent shapes — clients and ops both guess | 🟡 | open |
| 10 | root-BE-003 | root | Invoice email is fire-and-forget with no idempotency — double-sends on retry | 🟡 | open |
| 11 | root-INFRA-001 | root | No validated env schema at boot — missing prod vars become runtime 500s | 🟡 | open |
| 12 | root-INFRA-002 | root | No CI quality gate — broken PRs can land unchecked | 🟡 | open |
| 13 | root-INFRA-003 | root | No health/readiness signal and no written Vercel rollback story | 🟡 | open |
| 14 | root-FE-001 | root | New users and load failures see a blank page — looks broken | 🟡 | open |
| 15 | root-FE-002 | root | The invoice form accepts nonsense and only fails after hitting the server | 🟡 | open |
| 16 | root-UX-001 | root | Invoice list missing empty/error/loading states users can understand | 🟡 | open |
| 17 | root-UX-003 | root | New-invoice form labels inaccessible (placeholder-only) | 🟡 | open |
| 18 | root-OBS-001 | root | Errors hitting real users are invisible — you only hear about them via complaints | 🟡 | open |
| 19 | root-OBS-002 | root | No usable trail when something breaks — scattered console logs only | 🟡 | open |
| 20 | root-DB-003 | root | The invoice list slows down as data grows; deep pages crawl | 🟡 | open |
| 21 | root-TEST-003 | root | CI doesn't run tests (and there's no test script yet) | 🟡 | open |
| 22 | root-LINT-001 | root | ESLint is default/weak — foot-guns pass "clean" | 🟡 | open |
| 23 | root-LINT-002 | root | No typed lint — type-aware classes of bugs never fail CI | 🟡 | open |
| 24 | root-FE-003 | root | Marking an invoice paid feels laggy (waits for the server) | 🟢 | open |
| 25 | root-UX-002 | root | Raw AI-slop spacing/colors — token scale bypassed | 🟢 | open |
| 26 | root-LINT-003 | root | Lint warnings never fail the build (`max-warnings` not 0) | 🟢 | open |

**Surfaced in chat:** the five 🔴s (rows 1–5) lead; remaining 🟡 and 🟢 wait in the tracker. All nine
applicable domains (9 of 10; craft-ai N-A — no LLM surface) have been audited in this Tier-1 complete pass.

## Cross-cutting (one defect, multiple domains)
| Rollup (scope · class · resource) | Canonical ID | Also surfaced as (rolled up under canonical) |
| --------------------------------- | ------------ | -------------------------------------------- |
| root · no-row-level-security · invoices table | root-DB-001 | root-SEC-002 |
| root · missing async/list states · invoices list | root-FE-001 | root-UX-001 (UX owns state design; FE owns fetch co-location — both stay open; climb lists the FE row first as the implementable fetch fix, UX as the design bar) |
| root · no CI / no test script | root-INFRA-002 | root-TEST-003 (infra owns the gate; testing owns the suite + script) |

(`root-SEC-002` keeps its own `open` status in the security `findings.md`; "rolled up under
root-DB-001" is tracker metadata, not a lifecycle status. db owns the fix — enabling RLS.)

## Readiness (derived — never hand-set)
| Grade | Means | Rule |
| ----- | ----- | ---- |
| 🔴 Blocked | not production-ready | ≥1 open/regressed 🔴 |
| 🟡 At risk | usable, has holes | no open 🔴, ≥1 open 🟡 |
| 🟢 Solid | production-grade for this surface | only 🟢 open, or nothing |
| — N-A | surface doesn't exist here | domain marked N-A in `applicability.md` |
| ❔ Unaudited | applies, not yet run | applicable, no findings yet |

**Overall readiness: 🔴 Blocked** — critical findings across security, db, backend, and testing prevent
shipment. **5 distinct open 🔴**: SEC-001 (IDOR), DB-001 (RLS; SEC-002 rolled up), BE-002 (auth helper
skipped), TEST-001 (no money-path tests), TEST-002 (no IDOR regression). Clearing those promotes the
blocked surfaces toward 🟡 At risk; the project headline follows the weakest applicable surface.

## Audit status
| Scope | Domain | Applies | Plan | Findings | Last run | Open 🔴 / 🟡 / 🟢 | Grade |
| ----- | ------ | ------- | ---- | -------- | -------- | ----------------- | ----- |
| root | security | yes | ✅ | 4 | 2026-06-22 | 2 / 2 / 0 | 🔴 Blocked |
| root | db | yes | ✅ | 3 | 2026-06-22 | 1 / 2 / 0 | 🔴 Blocked |
| root | backend | yes | ✅ | 3 | 2026-06-22 | 1 / 2 / 0 | 🔴 Blocked |
| root | testing | yes | ✅ | 3 | 2026-06-22 | 2 / 1 / 0 | 🔴 Blocked |
| root | frontend | yes | ✅ | 3 | 2026-06-22 | 0 / 2 / 1 | 🟡 At risk |
| root | observability | yes | ✅ | 2 | 2026-06-22 | 0 / 2 / 0 | 🟡 At risk |
| root | infra | yes | ✅ | 3 | 2026-06-22 | 0 / 3 / 0 | 🟡 At risk |
| root | lint | yes | ✅ | 3 | 2026-06-22 | 0 / 2 / 1 | 🟡 At risk |
| root | ux | yes | ✅ | 3 | 2026-06-22 | 0 / 2 / 1 | 🟡 At risk |
| root | ai | N-A | — | — | — | — | — N-A |

## Delta since last run
First full Tier-1 pass — no prior state to diff against; all 27 findings are new (12 from the earlier
partial teaching snapshot domains + 15 from backend/infra/testing/lint/ux). A re-run would diff
against this snapshot per `rerun.md` (✅ fixed · ↩ regressed · ➕ new · ❔ not re-checked).
`root-SEC-003` carries a `Fix-attempt` annotation (2026-06-24) from craft-fix; status stays `open`
until a re-run's fingerprint diff marks it fixed.

# Optimization Deep-Dive Sub-Skill

Mode layered on top of `strategy.md`: the catalog says *what* strategies exist;
this file says *how* to run a rigorous optimization review — quantified,
stress-tested, documentation-ready. Load both. Think like the examiner as much
as the planner.

Use for: "find tax leakage", "optimize my taxes", "what am I missing", entity /
intercompany structuring reviews, audit-defense gap analysis, or router item 10
when the ask is a review rather than a single named strategy.

## Inputs

Everything in `strategy.md` → Inputs, plus for each in-scope taxpayer:

- `entities/<slug>/entity.md` + `<scope-root>/carryforwards.json`
- Current `<scope>/FY<YYYY>/tax-summary.md` and latest `.computed/` estimates
- Prior-year returns/workpapers where variance analysis needs them

**Cache-first evidence discipline:** pull numbers from workpapers,
`tax-summary.md`, and parsed JSON caches before opening any raw source
document. Open a source PDF only when the cached value is missing, stale, or
disputed — and then per `parsing.md` (never the built-in Read), updating the
cache so the next pass doesn't repeat the work.

### State inclusion (automatic — never assume)

Determine each in-scope taxpayer's state obligations from `states/README.md`
(entity → state map, verified against `entity.md` registration records), and
load the mapped state files. Every strategy analysis then traces state
consequences alongside federal — a federal win that creates a state gross
receipts, franchise, or capital gains cost is reported net, not in isolation.
If a strategy would create nexus or a filing obligation in a *new* state, flag
it as part of the cost.

### Constraint gate (before proposing income-affecting moves)

Some taxpayers carry non-tax constraints that outrank tax savings: MAGI-tested
benefit programs (ACA premium credits, Medicaid — see
`scenarios/aca-medicaid-magi.md`), income-based repayment, FAFSA windows.
Check the individual profile for these BEFORE proposing extractions, Roth
conversions, gain harvesting, or comp changes. A strategy that saves tax but
breaks a binding constraint is a net loss — say so explicitly and quantify
both sides.

## Analysis frame (per material strategy)

1. **Quantify from actual workspace data** — never generic "you could save up
   to". Inputs → formula → result, per `SKILL.md` Style.
2. **Name the taxpayers** — which entities/individuals, and the scope split
   (entity-level vs owner-level vs both), per `strategy.md`.
3. **Trace all tax systems together** — federal income + state (from the map
   above) + payroll/SE + accounting treatment. Never a federal strategy in
   isolation.
4. **Implementation path** — concrete steps, elections, forms, deadlines
   (cross-check `calendar.md` for timing conflicts).
5. **Exact documentation** — what document, what it establishes, who prepares
   and signs it, when it must be created (contemporaneous vs. by filing), what
   evidence is retained. Never just "document this".

## Position classification + doctrine stress-test

Classify every recommendation's overall position — a blend of authority
support, factual support, and posture (this is a different axis than the
low/moderate/elevated *audit-probability* ratings in `strategy.md`; state
both):

`well-established` / `aggressive-but-supportable` / `fact-dependent` /
`unsettled` / `high-risk`

Then stress-test it against the anti-abuse tests examiners actually apply:
substance-over-form, the economic-substance doctrine (codified at §7701(o),
applied where relevant), business purpose, assignment of income, constructive
dividend, reasonable compensation, §482 allocation among controlled taxpayers
(clear reflection of income / arm's-length standard), and step-transaction.
A strategy that fails a test gets reported with the failure, not silently
dropped — the user decides with eyes open.

## Adversarial pass (mandatory, per recommendation)

For every recommendation, answer: if the IRS or the state revenue agency
challenged this, (a) where would they attack, (b) what records would the IDR
request, (c) what is the defense and does the evidence for it exist today?
Report the answers alongside the recommendation. If the defense depends on
documents that don't yet exist, creating them becomes an implementation step
with a deadline.

## Output format

1. **Executive summary** — highest-value findings first.
2. **Strategy table** — `Priority | Strategy | Taxpayer | Est. benefit |
   Complexity | Position strength | Documentation burden | Recommendation`.
3. **Detailed breakdown** per significant strategy — mechanism, taxpayers,
   savings math, federal/state/payroll impact, accounting treatment,
   implementation steps, required documentation, adversarial-pass answers,
   failure modes, recommended action.
4. **Documentation matrix** — `Document | Purpose | Prepared by | Timing |
   Retention/evidence`.
5. **Entity/money-flow table** for multi-entity moves — `From | To |
   Transaction type | Tax treatment | Business purpose | Required
   documentation | Risk`.
6. **Action plan** — immediate / before year-end / before filing / ongoing
   compliance.

## Persistence

Follow `strategy.md` → Scenario Runner: scenarios considered go to
`<scope>/FY<YYYY>/.computed/<YYYY>-plan.json`; selected recommendations are
summarized into that year's `tax-summary.md`. Those are the canonical
artifacts. The deep-dive report itself is delivered in the conversation and is
NOT persisted by default; if the user asks to keep it, save it per
`naming.md` → Generated reports (`FY<YYYY> - optimization review -
<yyyy-mm-dd>.md` under the relevant `<scope>/FY<YYYY>/`).

Privacy, aggressiveness policy, and style inherit from `SKILL.md`.


# Individual Sub-Skill Router

Return preparation, permanent records, and planning for the individual Form 1040
and everything around it. **Does not file.** Output is audit-defensible
workpapers plus a review package the taxpayer hands to a CPA/EA or transcribes
into commercial software.

This is the individual-side spine, symmetric with `entities/README.md`. Three
files carry structural roles; everything else is a domain leaf loaded on demand.

| Role | File | Entity-side analog |
|---|---|---|
| Return-prep control | `individual/1040.md` | `entities/<type>.md` |
| Permanent-records pipeline | `individual/records.md` | `governance.md` |
| First-run setup | `individual/onboarding.md` | `init.md` (entity scan) |

## Minimum viable individual scope

**Do not impose entity-grade structure on a simple return.** A taxpayer with a
W-2, a 1099-INT, and a standard deduction needs exactly this:

```
individual/
├── profile.md
├── carryforwards.json
└── FY<YYYY>/{tax-summary.md, pending-docs.md, source/w2/, source/1099s-received/}
```

No `books/`, no `properties/`, no `records/basis/`, no annual workpapers beyond
`tax-summary.md`. Structure is added when a fact requires it, never in advance.
`onboarding.md` decides what a given taxpayer actually needs.

## Route by symptom

| The user is asking about | Load |
|---|---|
| "Prepare/organize my return", schedule-by-schedule workpapers, completeness | `1040.md` |
| First-time setup, empty folder, "where do I start", a friend's new workspace | `onboarding.md` |
| Where a permanent document goes; lifetime basis; retention; what to keep | `records.md` |
| How much to pay; installments; safe harbor | `close-estimate.md` (skill root — owns estimates) |
| W-4, withholding vs. estimates, Form 2210 penalty engineering | `withholding-penalties.md` |
| Losses that "disappeared"; at-risk; passive; EBL; suspended carryforwards | `loss-limitations.md` |
| IRA/Roth basis, conversions, rollovers, RMDs, inherited IRAs, 8606 | `retirement.md` |
| 1099-B, cost basis, wash sales, 8949, §1256, specific-ID | `capital-gains.md` |
| Crypto, NFTs, staking, mining, 1099-DA, wallet basis | `digital-assets.md` |
| Schedule A, SALT, mortgage interest tracing, charitable, 4952 | `itemized.md` |
| Publicly traded partnership K-1 (per-PTP suspension, PTP QBI, §751 on sale) | `ptp.md` |
| Non-PTP K-1s, Schedule E Part II, K-1 codes, K-3, basis/debt changes | `pass-through.md` |
| Foreign accounts, FBAR, 8938, FEIE, FTC | `foreign.md` |
| PFIC, CFC, foreign trusts/gifts, 5471/8865/8858/3520 | `foreign-escalation.md` |
| Gifts, 709, estate planning, step-up, beneficiaries, state estate tax | `estate-gift.md` |
| Residency, domicile, part-year, nonresident state filings, composite/PTET | `state-residency.md` |
| CTC/ODC, dependents incl. dependent parents, education credits, energy credits | `credits.md` |
| Kiddie tax, 8615/8814, a minor's own return, UTMA | `kiddie-dependents.md` |
| Marriage, divorce, death of spouse, home sale, moving, new child | `life-events.md` |
| Cancelled or forgiven debt, foreclosure, 1099-A/1099-C, insolvency, Form 982 | `life-events.md` §6 |
| Gambling winnings and losses, W-2G | `itemized.md` |
| Innocent spouse, injured spouse | `life-events.md` §1, `notices-amendments.md` §4 |
| Casualty, disaster, theft, or scam losses | `itemized.md` §6, `digital-assets.md` §7 |
| Layoff, severance, unemployment, COBRA, 401(k) at separation | `job-loss.md` |
| Sole proprietorship, SE tax, solo-401(k), hobby loss | `schedule-c.md` |
| Misclassified as a contractor; Form 8919; SS-8 | `worker-classification.md` |
| HSA, FSA, IRMAA, Medicare | `health-benefits.md` |
| 529, AOTC/LLC, 1098-T, student loan interest | `education.md` |
| CP2000, 1040-X, refund deadlines, identity theft, IP PIN | `notices-amendments.md` |
| "What changed since last year", dropped K-1, lapsed election | `year-over-year.md` |
| Rentals (Schedule E Part I) | `scenarios/rental-properties.md` |
| RSU/ISO/NSO/ESPP | `scenarios/equity-comp.md` |
| ACA PTC / Medicaid MAGI | `scenarios/aca-medicaid-magi.md` |
| Self-directed IRA (PT, UBTI, UDFI) | `scenarios/self-directed-ira.md` |
| Oil & gas working interests; VC/PE funds | `scenarios/k1-oil-gas.md`, `scenarios/k1-vc-pe.md` |
| Home office | `scenarios/home-office-280a.md` |
| IRS transcripts | `scenarios/irs-transcripts.md` |
| "How do I pay less tax" — a named strategy | `strategy.md` (skill root) |
| A broad optimization review, "what am I missing", tax leakage | `optimization.md` (skill root) |
| Year-over-year flux and tax-risk triggers | `variance.md` (skill root) |
| An IRS or state notice, examination, or §6662 penalty | `scenarios/audit-response.md` |
| Penalty abatement — FTA, reasonable cause, Form 843 | `scenarios/penalty-abatement.md` |

Every route in this table resolves to a file that exists. If a load fails,
validate against the `individual/` directory rather than guessing — and stop and
say so rather than answering from general knowledge.

Load the **one** file that owns the question. Each module loads its own
dependencies; do not preload the table.

## High-risk routes (do not answer from general knowledge)

These produce confident, plausible, wrong answers more often than anything
else on the individual side. Route first, always:

1. **Any IRA/Roth basis, conversion, rollover, RMD, or inherited-IRA question**
   → `retirement.md`. Never answer a backdoor-Roth question without the 12/31
   aggregate balance of *all* traditional/SEP/SIMPLE IRAs (§408(d)(2)).
2. **Any foreign account, entity, gift, or trust fact** → `foreign.md` (and
   `foreign-escalation.md` if an entity or trust is involved) **before** any
   income computation. Information-return penalties are assessed independently
   of whether tax is owed.
3. **A loss sale near a purchase in any account, including an IRA**
   → `capital-gains.md`. Where the replacement purchase is inside an IRA the
   loss is disallowed with **no basis adjustment to the IRA** — that is the IRS
   position in **Rev. Rul. 2008-5**, an unlitigated ruling rather than a statutory
   rule. Treat it as the operating assumption and label it accurately.
4. **A Roth conversion or large one-time income event** → `retirement.md` +
   `health-benefits.md` (IRMAA, 2-year lookback) + `scenarios/aca-medicaid-magi.md`
   jointly. Never answer from the federal tax delta alone.
5. **Sale of a residence that was ever a rental** → `1040.md` §6 (the §121 sequence).
   The exception that decides most of these is §121(b)(5)(C)(ii)(I): **trailing**
   use, within the five-year window, after the last date it was the principal
   residence is not nonqualified use. Rental *before* the last residency period
   still is. Build the use timeline before prorating anything.
6. **Equity-comp basis** → `scenarios/equity-comp.md`. A broker reporting $0 or
   purchase-price basis on an RSU or ESPP sale is the most common single
   overstatement of gain on an individual return.
7. **A complete disposition of a passive activity** → `loss-limitations.md`.
   §469(g) releases suspended losses **only** on a **fully taxable** disposition of
   the **entire interest** to an **unrelated** party — a gift, a related-party
   sale, or a nonrecognition transaction releases nothing. Conditions and the
   release ordering: `loss-limitations.md` §2.

## Scope and preparer status

Output is workpapers **for the taxpayer's own use or their own practitioner's**.

Preparing another person's return workpapers is not a neutral act. Preparer
status can attach to substantial-portion preparation regardless of signing
(§7701(a)(36); Reg §301.7701-15); compensated preparation requires a PTIN
(§6109(a)(4); Reg §1.6109-2); §6694/§6695 preparer penalties and Circular 230
apply. Separately, **§7216 and Reg §301.7216-1 impose criminal penalties for
unauthorized disclosure or use of taxpayer return information** — directly
implicated when a third party's tax data is written into a shared workspace.

If the user is setting this up for someone else, say so plainly and confirm the
arrangement before writing that person's data into the workspace.

## Non-goals

- Do NOT produce a filed return as the final artifact. Output is workpapers.
- Do NOT sign anything or represent the taxpayer.
- If the session-level disclaimer in `SKILL.md` has not been shown — a user can
  enter directly here — show it before substantive work.
- Always end individual work with: "Verify with a licensed practitioner before
  filing."


# Foreign Entities, Trusts, and Gifts (escalation)

**This module identifies obligations and preserves options. It does not resolve
them.** Every item carries a penalty in the tens of thousands **per form, per
year**, applies whether or not tax is owed, and holds the whole return open under
§6501(c)(8). Several involve elections that are irreversible.

The correct output is: **name the obligation, state the deadline and penalty,
preserve the election, route to a practitioner who does this work.** Do not
produce a completed 5471 or 3520 as a deliverable, and do not select a disclosure
program.

Ordinary foreign reporting is `foreign.md`. All thresholds → `authority.md`.

## 1. Triage

| Fact | Form | Note |
|---|---|---|
| Stock in a foreign corporation | 5471 (926 on transfer) | Category drives the schedules; Subpart F / GILTI can create income with no cash — a §962 election may mitigate |
| Interest in a foreign partnership | 8865 | Same category structure |
| Foreign disregarded entity or branch | 8858 | ⚠ Missed because "disregarded" reads as invisible — it is invisible for tax, not reporting |
| Foreign mutual fund, ETF, or pooled vehicle | **8621 (PFIC)** | ⚠ See §2 — the single most common surprise |
| Foreign trust; ⚠ **a foreign pension may be one** | 3520 / 3520-A | See §3 |
| Large gift or bequest from a foreign person | 3520 Part IV | See §4 |
| Transfer of property to a foreign corporation | 926 | Percentage-based penalty on value transferred |
| Covered expatriate | 8854, §877A | Counsel |

§6038/§6038A penalties run **$10,000 per form per year**, escalating after
notice, plus FTC reduction under §6038(c).

## 2. PFICs — the timing is everything

A foreign mutual fund or ETF is almost always a PFIC, and taxpayers hold them
without knowing. No de minimis ownership exception (there is a filing exception
below a value threshold absent an election or excess distribution).

⚠ **The §1291 default is punitive by design**: gain and excess distributions are
allocated ratably over the holding period, taxed at the **highest ordinary rate
for each prior year**, plus an **interest charge**, with no capital-gain
treatment. The alternatives — **QEF (§1295)**, requiring a PIC Statement the fund
may not provide, and **mark-to-market (§1296)**, available only for marketable
stock — are escapes only if elected in time.

⚠ **A QEF or MTM election made in the *first year* of the holding period
("pedigreed") avoids §1291 entirely. A late election requires a purging election
that triggers a deemed sale under §1291.** Preserving the first-year election is
the single most valuable action available the moment a PFIC is identified.

PFICs pass through partnerships — check K-1 footnotes and the K-3
(`scenarios/k1-vc-pe.md`).

## 3. Foreign trusts — 3520 / 3520-A

⚠ **§679** treats a US person who transfers property to a foreign trust with a US
beneficiary as the **owner**, so trust income is currently taxable regardless of
distributions.

⚠ **Form 3520-A is filed by the trust and is due earlier than the return** — and
if the trust does not file, **the US owner must file a substitute 3520-A** to
avoid the penalty. That is the trap: the taxpayer has no control over the trust's
compliance.

**§6677 penalties: the greater of $10,000 or 35% of the transfer or
distribution** (5% for certain ownership failures), per year. Distributions with
no records default to the **accumulation distribution** regime with a throwback
interest charge.

Whether a given foreign pension is a trust, and whether a treaty defers the
income, is plan- and treaty-specific. Do not assume either way.

## 4. Foreign gifts — 3520 Part IV

⚠ **A gift from a foreign person is not taxable income to the US recipient. The
obligation is informational; the penalty is not.**

Above an aggregate annual threshold from a foreign **individual or estate**; a
much **lower** threshold for gifts from foreign **corporations or partnerships**,
which may also be **recharacterized as income**. Aggregation across related
donors applies. **§6039F: 5% of the gift per month, to 25%.**

This is the most common way an ordinary family transfer becomes a five-figure
penalty. Ask anyone with family abroad directly.

## 5. Sequencing and disclosure

1. **Identify every obligation before computing tax** — §6501(c)(8) outranks the
   return's own completeness.
2. **Preserve deadline-bound elections** — a first-year QEF, a §962 election, a
   treaty position. An election lost is usually lost permanently.
3. ⚠ **Do not select a disclosure program.** Streamlined Domestic, Streamlined
   Foreign, the Delinquent International Information Return procedures, and
   voluntary disclosure differ on eligibility, cost, and — decisively — whether
   the taxpayer must certify **non-willfulness under penalty of perjury**. That
   certification is a legal judgment with criminal implications. Route to counsel
   and say why.
4. **Reasonable cause** is a written submission, not a checkbox — preserve the
   facts contemporaneously: who advised what, when the taxpayer learned, what
   they did next.
5. **Privilege** — where willfulness is arguable, communications should run
   through counsel (a *Kovel* arrangement for the accountant) rather than into a
   tax workpaper. `privileged` paths are excluded from intake and summarization
   (`SKILL.md`).

## 6. Workpaper

`wp-foreign-escalation.md`:

```json
{
  "obligations": [{"form": "5471|8865|8858|8621|926|3520|3520-A",
                   "trigger_fact": "", "category_or_part": "",
                   "tax_year_first_required": null, "filed": null,
                   "delinquent_years": [], "penalty_exposure_note": "",
                   "reasonable_cause_facts": ""}],
  "pfics": [{"fund": "", "first_year_held": null, "election": "none|QEF|MTM",
             "election_year": null, "pedigreed": null,
             "pic_statement_available": null, "section_1291_exposure": null}],
  "foreign_trusts": [{"trust": "", "role": "owner|beneficiary|transferor",
                      "section_679_owner": null,
                      "form_3520a_filed_by_trust": null,
                      "substitute_3520a_required": null}],
  "foreign_gifts": [{"donor_type": "individual|estate|corporation|partnership",
                     "aggregate_amount": 0, "threshold_exceeded": null,
                     "recharacterization_risk": null}],
  "counsel_referred": null,
  "section_6501c8_hold": null
}
```

**Invariants:** every identified obligation is filed or recorded as an open
exposure with its penalty; a PFIC's **first-year election status** is captured
before anything else; `section_6501c8_hold` is true whenever any required IRC
form is unfiled, forcing `RETURN_HOLD`; **no disclosure program is selected in
this file**.

Verify with a licensed practitioner before filing. Involve counsel **before
filing anything** — including before filing a late form, which can foreclose
options.

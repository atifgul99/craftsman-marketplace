
# Foreign Accounts, Income, and Credits

Owns the **ordinary** foreign layer: FinCEN 114, Form 8938, the foreign tax
credit, and §911. Anything involving a foreign **entity, trust, or gift**
escalates to `foreign-escalation.md`.

⚠ **Sequencing rule:** establish the foreign facts **before any income
computation** (`1040.md` §1 Step 1.4). Information-return penalties are assessed
**independently of tax owed**, and an unfiled IRC information return holds the
**entire return** open under §6501(c)(8). Never treat the absence of a 1099 as
evidence — foreign institutions do not issue them.

All thresholds and dollar amounts are subject to `authority.md`.

## 1. Intake questions

Ask all of them; the taxpayer usually does not know which matter.

1. Any financial account **outside the US** — bank, brokerage, pension,
   cash-value insurance?
2. **Signature or other authority** over an account not owned — an employer's, a
   parent's, an entity's?
3. Accounts through a **foreign branch of a US institution** (can be reportable)
   or a US account holding foreign assets (generally not)?
4. Any interest in a **foreign entity**? → `foreign-escalation.md`
5. Any **foreign trust** — settlor, beneficiary, transferor? ⚠ **A foreign
   pension is frequently a foreign trust.** → `foreign-escalation.md`
6. Any **gift or inheritance from a foreign person**? → `foreign-escalation.md`
7. Foreign **real property** — and is it held through an entity?
8. Foreign **income taxes** paid or accrued?
9. Did you live or work abroad any part of the year?
10. Any **foreign digital-asset platform**? → `digital-assets.md`

## 2. FinCEN 114 (FBAR) — 31 U.S.C. §5314; 31 C.F.R. §1010.350

**Not part of the tax return.** ⚠ The traps:

- **The test is aggregate.** If the **combined** maximum value of all foreign
  financial accounts exceeds the threshold at **any time** in the year, **every**
  account is reportable — there is no per-account floor.
- **Signature or other authority counts**, even with no financial interest.
- **Deadline: April 15 with an *automatic* extension to October 15 for all
  filers** — no request, and **independent of Form 4868**.
- **BSA E-Filing System only.** A preparer needs **FinCEN Form 114a**
  authorization — a handoff artifact the return package must request.
- Maximum value per account, converted at the Treasury Reporting Rate for 12/31.
- **Penalty is per report, not per account** for non-willful violations
  (*Bittner v. United States*, 598 U.S. 85 (2023)); willful is the greater of the
  adjusted amount or 50% of the balance. Reasonable cause is available for
  non-willful only.
- ⚠ **Exceptions exist** (certain correspondent, military-banking, governmental,
  and IRA accounts; consolidated and joint-spouse filing). Do not conclude a
  filing obligation from the aggregate test alone — check the current
  instructions.
- ⚠ **Digital assets:** an account holding **only** digital assets is not
  currently FBAR-reportable, though FinCEN has announced an intent to change
  this — **verify annually**. A mixed account is reportable, and FBAR reports the
  **maximum value of the account**, not of an asset class within it.
- **Delinquency:** Delinquent FBAR Submission Procedures where there is no
  unreported income and no examination; otherwise Streamlined. ⚠ Choosing among
  them is a counsel decision the moment willfulness is arguable — do not select a
  path for the taxpayer.

## 3. Form 8938 (§6038D)

A **return attachment**, and a different regime. ⚠ **Many taxpayers must file
both on the same accounts; satisfying one never satisfies the other.**

Differences that decide the analysis: it follows the **return's** extension, not
FBAR's; thresholds vary by **filing status and whether the taxpayer lives
abroad**; it covers **specified foreign financial assets** more broadly than
accounts (foreign stock held directly, interests in foreign entities, financial
instruments outside an account) but **excludes** assets in a US financial account
and **directly held foreign real estate or tangible property**; it reaches
certain **specified domestic entities**; and it is **generally not required from
a taxpayer with no return-filing obligation**. Assets reported on Form 3520,
5471, 8621, or 8865 are cross-referenced rather than duplicated.

⚠ **Directly self-custodied digital assets are not specified foreign financial
assets** — no foreign issuer or counterparty. That is the question people ask.

## 4. §6501(c)(8)

An unfiled required **IRC** information return (8938, 5471, 8865, 8858, 3520,
3520-A, 8621) suspends the limitations period on the **entire return**, not just
the foreign items. Reasonable cause can limit the suspension to related items.
⚠ **FinCEN 114 is a Title 31 filing and does not trigger it.**

Operationally: unresolved obligation ⇒ `RETURN_HOLD`, never `PROVISIONAL`.

## 5. Foreign tax credit (§901) — Form 1116

⚠ The traps, not the mechanics:

- **Baskets** (§904(d)) are computed **separately** — passive, general, foreign
  branch, GILTI, treaty-resourced.
- **Excess credit carries back one year and forward ten** (§904(c)), **by
  basket** — a real asset routinely lost. A claim for a year affected by an FTC
  carryback gets **10 years** under §6511(d)(3).
- ⚠ **§904(j) de minimis election** — claim the credit directly on Schedule 3
  without Form 1116 where all foreign tax is passive and from qualified payee
  statements within the threshold. **It forfeits carryback and carryover
  (§904(j)(3)(A))**, so it is a **recorded decision**, not an omission. A
  taxpayer with growing foreign tax should generally not elect it.
- The tax must be a **compulsory payment**; amounts refundable under a treaty are
  not creditable — the usual defect with over-withheld foreign dividend tax.
- ⚠ **A missing K-3 is a hold on the FTC line, not a zero.** → `pass-through.md`.
- Credit vs. deduction is annual and applies to all foreign taxes for the year
  (§275(a)(4)).

## 6. §911 — Form 2555

Requires a **tax home abroad** plus bona fide residence or physical presence
(330 full days in any 12 consecutive months). ⚠ The traps:

- Excludes **earned** income only — never investment income, pensions, or Social
  Security.
- **§911 does not exclude income from self-employment tax.** A US person abroad
  still owes SE tax unless a **totalization agreement** applies — a frequent and
  expensive surprise.
- The election is **sticky**: once revoked it cannot be re-elected for five years
  without consent.
- **No FTC on income excluded under §911** — running both requires allocating
  taxes to the non-excluded portion. In a high-tax country the FTC usually wins;
  in a low-tax one §911 does. Model both.
- A separate housing exclusion/deduction with a base amount and location cap.

## 7. Other recurring items

⚠ **Treaty positions** generally require **Form 8833** disclosure (§6712
penalty), and a saving clause usually preserves US taxation of US persons.
⚠ **Foreign pensions** are the most under-analyzed item — possibly a foreign
trust, an 8938 asset, an FBAR account, and currently taxable on accrual despite
being untouchable. Never assume US-style deferral.
**§988** — nonfunctional-currency gain or loss is generally ordinary, with a
personal-use exception for small gains. **Foreign rental property** uses the
longer foreign recovery period, not 27.5 years. **Expatriation (§877A)** —
mark-to-market exit tax, Form 8854; escalate to counsel.
⚠ **A §6013(g)/(h) election** for a nonresident spouse brings their **worldwide
income and foreign accounts** into the US system — frequently made without anyone
realizing the reporting consequence.

## 8. Workpaper

`wp-fbar.md` and `wp-8938.md`, **kept separate**:

```json
{
  "fbar": {"aggregate_max_value_usd": null, "threshold_exceeded": null,
           "accounts": [{"institution": "", "country": "", "acct_last4": "",
                         "max_value_usd": 0, "financial_interest": null,
                         "signature_authority_only": null, "jointly_owned": null}],
           "exception_claimed": "", "filed": null, "filed_date": null,
           "form_114a_obtained": null, "delinquent_procedure": null},
  "form_8938": {"filing_status": "", "resides_abroad": null,
                "threshold_year_end": null, "threshold_any_time": null,
                "assets": [{"description": "", "type": "", "max_value_usd": 0,
                            "reported_on_other_form": ""}],
                "required": null, "filed": null},
  "ftc": {"baskets": [{"basket": "", "foreign_source_income": 0,
                       "foreign_tax_paid": 0, "limitation": 0, "allowed": 0,
                       "carryback_used": 0, "carryforward_out": 0,
                       "expires_after": null}],
          "section_904j_election_made": null,
          "carryover_forfeiture_acknowledged": null, "k3_received": null},
  "section_911": {"test_met": "", "tax_home_abroad": null,
                  "excluded_earned_income": 0, "housing": 0,
                  "se_tax_still_due": null, "totalization_agreement": null},
  "escalation_flags": {"foreign_entity": null, "foreign_trust": null,
                       "foreign_gift": null, "pfic": null}
}
```

**Invariants:** the FBAR test is applied to the **aggregate**, and once exceeded
every account is listed; FBAR and 8938 are evaluated **independently**; any
escalation flag routes to `foreign-escalation.md` before the return concludes; an
unfiled IRC information return sets `RETURN_HOLD`; the §904(j) election records
the carryover forfeiture as an acknowledged decision; a missing K-3 blocks the FTC
line rather than defaulting to zero.

Verify with a licensed practitioner before filing. Where willfulness, an offshore
structure, or a delinquency procedure is in play, involve counsel — those are not
workpaper decisions.

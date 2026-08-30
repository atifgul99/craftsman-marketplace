
# Kiddie Tax and Dependents' Own Returns

Owns §1(g), Forms 8615 and 8814, dependent filing thresholds, and custodial
accounts. Dependency qualification → `credits.md`. Thresholds → `authority.md`.

## 1. Who is subject

⚠ §1(g) requires the child be **required to file a return**, have unearned income
above the threshold, have a living parent, and not file jointly — **plus** be
under 18; or 18 with **earned income not exceeding half of support**; or 19–23, a
full-time student, same support test.

⚠ **The support test is the escape hatch** — a 19-year-old student earning more
than half their own support is **out entirely**. A planning lever, not a
technicality.

⚠ **SECURE Act §501** repealed the TCJA trust-rate regime effective 2020, with an
**election** to apply it retroactively to 2018–2019. Current law taxes net
unearned income at the **parent's** rate. For any amended year confirm which
regime applied and whether the election was made.

## 2. Form 8615

⚠ What actually goes wrong:

- **The parent's return must be computed first**, and where there are siblings the
  **other children's** net unearned income is combined and reallocated. One
  child's return cannot be finished in isolation.
- **Which parent** — custodial for unmarried parents; if MFS, the higher taxable
  income. ⚠ Where the custodial parent **remarried and files jointly**, §1(g)(5)
  uses the **joint** taxable income, so the **stepparent's income drives the
  child's rate**.
- Capital gains and qualified dividends **keep their preferential character** —
  do not flatten them.
- ⚠ **A taxable scholarship counts as *earned* income for Form 8615 purposes**,
  even though it is unearned for the threshold test — so a large room-and-board
  scholarship does not by itself push a student into the kiddie tax
  (`education.md` §1).
- ⚠ **A student subject to §1(g) cannot claim the refundable 40% of the AOTC**
  (§25A(i)) — the reason the "parent forgoes the dependency" move usually fails.
- The parent's information must be disclosed on the child's return — a practical
  problem in divorce, and unavoidable.
- A child on extension whose parent has not filed may need estimated parent
  figures and an amendment.

## 3. Form 8814 — usually wrong

⚠ **Eligibility conditions that most often kill it** (§1(g)(7)(B) and the
instructions): income only interest, dividends, and capital gain distributions,
under the ceiling; child **under 19 (under 24 if a full-time student)** at year
end; **no estimated payments** in the child's name and SSN; and **no federal
income tax withheld**, including backup withholding. **Withholding on a child's
account is common and is an absolute bar.**

Even when available it is usually worse: it **increases the parent's AGI**,
cascading into the medical floor, IRMAA, PTC, education phaseouts, and NIIT; it
costs the child's remaining bracket capacity and their own deductions; and it can
push the parent's own capital gains into a higher rate. (Under §1(g)(7) the first
tranche is excluded and the next taxed at the child's low rate, which approximates
the dependent unearned standard deduction — so that is not itself the loss.)

## 4. Dependent's own filing requirement

Four independent tests: **earned**, **unearned**, and **combined** income against
their respective thresholds — the unearned threshold being far lower — ⚠ **plus
§6017, which requires a return at $400 or more of net earnings from
self-employment regardless of the other three.** A teenager with gig or 1099-NEC
income is the most common dependent-filing case and the income thresholds miss it.

The dependent standard deduction is its own formula (greater of a floor, or earned
income plus an increment, capped at the regular standard deduction).

- A dependent with modest earned income and withholding should file for the refund
  even when not required to.
- ⚠ A dependent **cannot claim themselves**, and doing so is the most common cause
  of a parent's e-file reject. **The fix is two-sided:** the parent paper-files
  **and** the child files a **1040-X** to check the "someone can claim you" box.
  Without the second half the reject recurs next year.

## 5. Custodial accounts and a minor's Roth

- **UTMA/UGMA** is an **irrevocable gift**, taxed to the child (subject to §1(g)),
  and becomes the child's outright at the state's age of majority — discovered
  late by families. Counts heavily against financial aid. ⚠ Income used to
  discharge a **parent's legal support obligation** is taxed to the **parent**.
  ⚠ **Estate trap:** where the **donor is also the custodian** and dies before
  majority, the account is included in the donor's gross estate under §2038
  (`estate-gift.md`).
- **A minor's Roth IRA** requires the child's own **earned income**. Family
  employment can create it, but the work must be real, age-appropriate, paid at a
  defensible rate, with records — a favorite examination target.
  ⚠ **This file owns the family-employment payroll rule:** wages paid by a
  **parent's sole proprietorship or a parents-only partnership** to a child under
  18 are exempt from **FICA (§3121(b)(3)(A))**, and the paired companion —
  **§3306(c)(5) exempts the same wages from FUTA until age 21**. The mismatched
  ages are the point. **Income tax withholding still applies** in both cases. A
  **corporation** gets neither exemption, even if the parents own it.
  `schedule-c.md` points here.
- A §529 account is not the child's asset and is outside all of this
  (`education.md`).

## 6. Workpaper

`wp-kiddie.md`:

```json
{
  "children": [{"name_slug": "", "age": null, "student": null,
                "earned_income": 0, "unearned_income": 0,
                "support_over_half_from_own_earnings": null,
                "return_required_gate_met": null, "se_earnings_400_test": null,
                "subject_to_1g": null, "files_own_return": null,
                "form_8615": {"parent_taxable_income": null,
                              "parent_selection_basis": "custodial|higher_MFS|remarried_joint",
                              "siblings_net_unearned_combined": 0,
                              "preferential_character_preserved": null,
                              "taxable_scholarship_treated_as_earned": null},
                "form_8814_elected": null,
                "form_8814_disqualifiers": {"estimated_payments_in_child_ssn": null,
                                            "federal_withholding_present": null,
                                            "age_test_met": null},
                "form_8814_parent_agi_impact": 0,
                "aotc_refundable_barred_25A_i": null}],
  "custodial_accounts": [{"account_slug": "", "type": "UTMA|UGMA",
                          "age_of_majority": null, "donor_is_custodian": null,
                          "support_obligation_income": 0}],
  "minor_roth": {"earned_income_source": "", "substantiation": "",
                 "payer_entity_type": "sole_prop|parents_partnership|corporation",
                 "fica_exempt_3121b3A": null, "futa_exempt_3306c5": null}
}
```

**Invariants:** the §1(g) gate includes the **return-required** condition; the
dependent is tested against **four** thresholds including §6017's $400 SE test; a
Form 8814 election confirms **no withholding and no estimated payments** in the
child's name; the parent's return is computed before any child's 8615, with
siblings combined; a minor's Roth names its earned-income source, substantiation,
and the payer entity type that decides the FICA/FUTA exemptions.

Verify with a licensed practitioner before filing.


# Estate, Gift, and Wealth Transfer

Owns the transfer-tax layer as it touches the individual: Form 709, basis at
death, beneficiary mechanics, and **state** estate and inheritance tax. Trust
income taxation beyond a beneficiary's K-1 is out of scope; so is drafting, which
is counsel's work.

⚠ Exemptions, exclusions, and rates → `authority.md`. The federal basic exclusion
changed under OBBBA — do not carry a prior year's figure.

## 1. Form 709 — the return nobody files

Required — **even with no tax due** — when a donor exceeds the annual exclusion to
any one donee, makes a gift of a **future interest** (no exclusion at all,
regardless of amount), **splits gifts**, makes the §529 five-year election, or
wants to **allocate GST exemption or elect out of automatic allocation**.

⚠ The points that decide it:

- **Present-interest requirement.** A gift in trust is a future interest unless
  Crummey withdrawal rights are given **and noticed**. No notice, no exclusion.
  ⚠ And the **lapse** of a withdrawal right above the greater of $5,000 or 5% of
  corpus is **itself a taxable gift by the beneficiary** (§2514(e)) — the reason
  hanging powers exist, and the reason a 709 analysis sometimes has to look at the
  *beneficiaries'* returns.
- **Gift splitting (§2513)** requires **both** spouses to consent, both to be US
  citizens or residents, married at the time, and not remarried during the year.
  It is all-or-nothing for the year and also splits the gift for **GST**.
  ⚠ **Unavailable for a gift to a trust in which the consenting spouse has a
  beneficial interest** unless that interest is severable and ascertainable — the
  classic SLAT failure.
- **Non-citizen spouse** — no unlimited marital deduction; a separate, larger
  annual exclusion applies. The estate-side analogue is a **QDOT (§2056A)**.
- ⚠ **§2503(e) covers tuition only** — not books, supplies, room, or board — paid
  **directly** to the institution, plus §213(d) medical care (including insurance
  premiums) paid directly to the provider. Paid to the person instead, they are
  ordinary gifts. A free transfer channel that goes unused, and one that is
  frequently over-read.
- ⚠ **Adequate disclosure** (Reg §301.6501(c)-1(f)) starts the three-year statute
  on a gift's **valuation**. An inadequately disclosed gift stays open forever and
  can be revalued at death.
- ⚠ **§2632(b)/(c) automatic GST allocation** applies by default whether or not a
  709 is filed — **misallocation, not non-allocation, is the routine GST error.**
- 709s are **cumulative** — every filed return feeds the estate tax computation
  decades later. They live permanently in `records/estate/` (`records.md` §9).
- Due April 15, automatically extended by **Form 4868** (or **Form 8892** where no
  1040 extension is filed); in the year of death, no later than the 706 due date.

## 2. Basis at death

- **§1014** step-up (or down) to date-of-death FMV; **§2032** alternate valuation
  only if a 706 was filed **and** it reduces both the gross estate and the tax.
- ⚠ **§1014(b)(6): community property receives a full step-up on both halves** —
  a material advantage over common-law joint tenancy and a reason not to retitle
  out of it. **This file owns the rule** (`state-residency.md` points here).
  Elective community-property trusts exist in several non-community states.
- ⚠ **§1014(e)** denies the step-up where appreciated property was gifted to a
  decedent within one year and returns to **the donor *or the donor's spouse***.
  The spouse variant is the one the strategy actually uses.
- ⚠ **Rev. Rul. 2023-2**: assets in a completed-gift **irrevocable grantor trust**
  not includible in the gross estate get **no §1014 adjustment**. Squarely in the
  supported window and it governs the planning conclusion below.
- ⚠ **§1014(f) / §6035 / Form 8971** — where a 706 was required, the beneficiary's
  basis **cannot exceed** the value reported, the estate must furnish Schedule A
  within 30 days, and **§6662(k) imposes 40%** on an inconsistent basis.
- **IRD has no step-up** (§691) — IRAs, annuities, accrued interest, deferred
  comp. The offsetting relief is the **§691(c)** deduction (`retirement.md`).
- **§1015 gift basis is dual** — carryover for gain, lesser of carryover or FMV
  for loss, no gain/no loss between; increased by gift tax on net appreciation
  (§1015(d)(6)). ⚠ **Gifting a loss asset destroys the loss — sell it first.**

⚠ **Planning consequence:** with a high federal exclusion the default for
appreciated assets flips from "gift it" to "hold to death," because the step-up
beats the transfer-tax saving. **That reverses in a state with a low estate
threshold** (§4) — and Rev. Rul. 2023-2 removes the step-up from a common
work-around.

## 3. Portability

⚠ Requires a **timely-filed Form 706** even with no tax due — and **Rev. Proc.
2022-32 allows a late election within five years of death** for estates not
otherwise required to file. Missing it is the most expensive routine omission in
this area, and it is fixable for longer than most people think.

⚠ **DSUE is available only from the *last* deceased spouse (§2010(c)(4))** —
remarriage and a second spousal death **wipes out a banked DSUE**. Under
**§2010(c)(5)(B)** the IRS may examine the predeceased spouse's 706 to determine
DSUE **at any time**, without regard to §6501. **GST exemption is not portable.**

## 4. State estate and inheritance tax

⚠ **The federal exclusion is not the answer.** Several states tax at thresholds
far below it, and a few impose an **inheritance** tax on the recipient instead.
Where one applies: the threshold and rates are separate and on their own indexing
schedule (or unindexed); ⚠ **state-level portability generally does not exist**,
which keeps credit-shelter planning relevant for couples otherwise relying on
portability; some states offer a qualified family-owned business deduction; and
**nonresidents can owe on in-state real property**. Connecticut is the only state
with a gift tax, and a state QTIP election can conflict with federal portability.

State specifics → `states/<xx>/`, or resolve from the state's revenue department
under `authority.md`.

## 5. Beneficiary and titling mechanics

⚠ **The beneficiary form and the deed control, not the will.** Check as a set:
retirement designations with the 9/30 determination date and §2518 disclaimers
within nine months (`retirement.md` §3); TOD/POD and joint tenancy, which override
the estate plan and can defeat a credit-shelter structure; whether a revocable
trust is **actually funded** (an unfunded trust does nothing); and life insurance
ownership — ⚠ proceeds are income-tax-free but includible if the decedent held
incidents of ownership (§2042), and **§2035(a) pulls the full proceeds back if the
policy was transferred within three years of death**. §101(a)(2)
transfer-for-value destroys the income-tax exclusion.

Record all of it in `records/estate/`.

## 6. Workpaper

`wp-estate-gift.md`:

```json
{
  "gifts": [{"donee": "", "date": "", "amount": 0, "present_interest": null,
             "crummey_notice_given": null, "lapse_over_5_and_5": 0,
             "annual_exclusion_used": 0,
             "section_2503e_direct_payment": "tuition|medical|none",
             "split_with_spouse": null, "spousal_consent_obtained": null,
             "consenting_spouse_beneficial_interest": null,
             "form_709_required": null, "adequate_disclosure": null,
             "gst_allocation": "automatic|elected|opted_out",
             "exclusion_consumed": 0}],
  "cumulative": {"prior_709s_on_file": [], "lifetime_exclusion_used": 0,
                 "gst_exemption_allocated": 0},
  "basis_at_death": [{"asset": "", "date_of_death_fmv": 0,
                      "community_property_full_step_up": null,
                      "section_1014e_applies": null,
                      "grantor_trust_no_step_up_rr_2023_2": null,
                      "form_8971_value_reported": 0,
                      "ird_no_step_up": null, "section_691c_deduction": 0,
                      "basis_ssot_updated": null}],
  "portability": {"predeceased_spouse": "", "date_of_death": "",
                  "form_706_filed": null, "dsue_amount": 0,
                  "last_deceased_spouse": null,
                  "rev_proc_2022_32_available": null},
  "state": [{"state": "", "estate_or_inheritance": "", "threshold": null,
             "return_required": null, "state_portability": false}],
  "insurance": [{"policy": "", "owner": "", "incidents_of_ownership": null,
                 "transferred_within_3_years": null}]
}
```

**Invariants:** every gift over the annual exclusion, every future-interest gift,
every split gift, every §529 five-year election, and every GST allocation decision
produces a 709 decision; cumulative exclusion used ties to the prior 709s on file;
a step-up is not applied to IRD or to a completed-gift grantor trust; basis
changes route to their SSOT and, where a 706 was required, are capped by the Form
8971 value; the state threshold is tested **independently** of the federal one;
portability is tested against Rev. Proc. 2022-32 and the last-deceased-spouse rule
before being written off.

Estate planning is legal work. This module identifies filings and preserves
options — **engage counsel before executing anything**, and verify with a licensed
practitioner before filing.

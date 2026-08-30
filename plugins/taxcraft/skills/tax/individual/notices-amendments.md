
# Notices, Amendments, and Individual Procedure

Owns the post-filing layer: matching notices, amended and superseding returns,
the clocks, identity theft, and collection.

Examination procedure and §6662 substantive defenses →
`scenarios/audit-response.md`; abatement → `scenarios/penalty-abatement.md`;
transcripts → `scenarios/irs-transcripts.md`. Load those rather than duplicating.

All dates and thresholds → `authority.md`.

## 1. Triage: the deadline, and whether it is jurisdictional

⚠ **Always verify the notice is real** against the IRS Online Account or an
account transcript before paying or sending documents. The IRS does not initiate
by phone, email, or text.

- **CP2000 / CP2501** — automated **underreporter matching, not an audit**.
  ⚠ Two errors: agreeing when the proposal is wrong, and ignoring the
  **offsetting basis or deduction the IRS could not see** — a 1099-B reporting
  gross proceeds with no basis is the classic, and the notice proposes tax on the
  entire proceeds.
- **CP14 / 501 / 503 / 504** — escalating balance due. ⚠ **CP504 does not confer
  CDP rights** for a general levy.
- ⚠ **Letter 1058 / LT11 / CP90** (Final Notice of Intent to Levy, §6330) and
  **Letter 3172** (NFTL, §6320) — **each carries a 30-day window to file Form
  12153** for a CDP hearing. Missing it drops the taxpayer to an *equivalent*
  hearing with **no Tax Court review**. **These two 30-day dates are missed far
  more often than the 90-day letter.**
- **Letter 525 / 30-day letter** — exam report; 30 days to agree or go to Appeals.
- ⚠ **Letter 3219 / Notice of Deficiency / 90-day letter** — 90 days to petition
  the Tax Court (150 if addressed abroad). Treat it as **immovable** operationally,
  with three qualifications: under **§6213(a) a later date printed on the notice
  controls**; the IRS may **rescind** by mutual agreement (§6212(d), Form 8626);
  and §7508/§7508A postponements apply. Whether it is strictly jurisdictional is a
  live circuit split (*Hallmark Research Collective*, 160 T.C. No. 6 (2023) vs.
  *Culp v. Commissioner*, 75 F.4th 196 (3d Cir. 2023), after *Boechler*) — a late
  petition is not automatically hopeless, but never plan on it.
  ⚠ **If the 90 days lapse the matter is not over**: **audit reconsideration**
  (IRM 4.13), a **doubt-as-to-liability OIC (Form 656-L)**, or **pay and sue under
  §7422** with the §6532 two-year suit deadline.
- ⚠ **CP11 / CP12 math-error notice** — looks like harmless arithmetic and carries
  a hard **60 days to request abatement under §6213(b)(2)**. Miss it and deficiency
  procedures and Tax Court access are **forfeited entirely**; the assessment
  stands. The most easily overlooked hard deadline in the set.
- **CP2100 / 972CG** — backup withholding and information-return penalties.
- **LTR 0012C** — missing information; the return is not processed until answered.

## 2. Superseding, qualified amended, and 1040-X

⚠ Three different things:

| | When | Effect |
|---|---|---|
| **Superseding** | After the original but **before the extended due date** | Replaces it for all purposes, **including elections and the §6501 start**. Not a 1040-X |
| **Qualified amended return** | Before the **earliest of four** Reg §1.6664-2(c)(3) cutoff events | Removes the corrected amount from the §6662 understatement **if every condition is met**. ⚠ It does **not** cure negligence, fraud, interest, or failure-to-pay, and "before IRS contact" is shorthand — the events include examination of the taxpayer, **examination of a pass-through entity for a pass-through item**, promoter examination, and a **John Doe summons** |
| **1040-X** | After the filing period **including extensions** expires | Ordinary correction; penalties already accrued |

⚠ **A missed election is often the real reason to supersede** — many are valid
only on a timely-filed original (including superseding) return; otherwise
§301.9100 relief (`1040.md` §7).

Mechanics: a superseding individual return is **e-filed through MeF with the
superseded-return indicator**, available only for recent years and otherwise on
paper; 1040-X e-file is likewise limited to recent years. Attach only what
changed plus what the change requires. An entity-driven change follows the
entity's regime (BBA AAR vs. 1065-X → `scenarios/amend-partnership.md`).
⚠ **State amendments do not follow automatically** — most require their own, on
their own clock.

## 3. The clocks

| Clock | Rule |
|---|---|
| **Refund** | §6511(a): later of **3 years from filing** or **2 years from payment**. ⚠ **§6511(b)(2) then caps the refund by the lookback period** — the source of a valid-but-worthless claim. **§6511(h)** tolls for financial disability (Rev. Proc. 99-21 documentation) — the only rescue for an old year. **§6511(d)(3)** gives FTC claims **10 years** |
| **Assessment** | §6501(a): 3 years; **6 years** for a >25% omission (⚠ which now includes a **basis overstatement**, §6501(e)(1)(B)(i)) or >$5,000 omitted foreign income; unlimited for fraud or non-filing. Extendable by consent (**Form 872 / 872-A**, §6501(c)(4)) |
| **Entire return held open** | §6501(c)(8) until required **IRC** foreign information returns are filed → `foreign.md`. ⚠ FinCEN 114 does not trigger it |
| **Collection** | §6502: 10 years from assessment, tolled by CDP requests, OICs, and bankruptcy |

Filing before the due date is treated as filed **on** the due date (§6513(a)). A
**protective claim** preserves a year whose amount depends on an unresolved
contingency.

## 4. Identity theft and refunds

**Form 14039** affidavit; the return usually must be paper-filed. ⚠ **IP PIN**
(CP01A) is annual and **required once issued** — a missing one **rejects an
e-filed return**, while a paper return without it is processed with delay and
additional screening rather than rejected. Taxpayers often do not know they have
one; anyone may opt in. **Refund offset** for federal debts, state tax, child
support, or student loans — **Form 8379 injured spouse** protects the non-liable
spouse's share, a different remedy from innocent spouse (`life-events.md` §1).
PATH Act holds apply to **EITC and ACTC** returns.

## 5. Collection alternatives

Installment agreement (streamlined below the threshold, no financial disclosure),
**offer in compromise** (Form 656 — ⚠ **suspends the collection statute while
pending**), currently-not-collectible, or the **Taxpayer Advocate** (Form 911) for
hardship or a systemic breakdown.

⚠ **File first, pay later.** The failure-to-file penalty runs at **ten times** the
failure-to-pay rate, so filing without payment is almost always better than not
filing (`1040.md` §1 Step 0). Relief itself → `scenarios/penalty-abatement.md`.

## 6. Circular 230 §10.21

On discovering a prior-year error the obligation is to **advise** the taxpayer of
it, its consequences, and the correction. It does **not** authorize correcting it
unilaterally or notifying the IRS. Record the advice; sets
`PRIOR_YEAR_ERROR_IDENTIFIED` (`1040.md` §8).

## 7. Workpaper

`wp-notices.md`:

```json
{
  "notices": [{"code": "", "date": "", "tax_year": null,
               "verified_against_transcript": null,
               "response_deadline": "", "jurisdictional": null,
               "cdp_rights_conferred": null, "form_12153_deadline": "",
               "proposed_change": 0, "agree": "yes|no|partial",
               "offsetting_items_not_visible_to_irs": [],
               "response_sent": "", "proof_of_mailing": ""}],
  "corrections": [{"tax_year": null,
                   "vehicle": "superseding|qualified_amended|1040X",
                   "qar_cutoff_events_tested": {"examination_of_taxpayer": null,
                                                "pass_through_entity_examination": null,
                                                "promoter_examination": null,
                                                "john_doe_summons": null},
                   "qar_still_available": null,
                   "reason": "", "election_preserved": "",
                   "state_amendment_required": null, "state_deadline": ""}],
  "clocks": [{"tax_year": null, "return_filed": "", "payments_made": [],
              "refund_deadline_6511": "", "lookback_cap_6511b2": 0,
              "section_6511h_disability_tolling": null,
              "assessment_deadline_6501": "", "form_872_consent": null,
              "held_open_6501c8": null}],
  "identity": {"form_14039_filed": null, "ip_pin_on_file": null,
               "ip_pin_included_on_return": null},
  "collection": {"balance": 0, "arrangement": "", "csed": ""}
}
```

**Invariants:** every notice records its deadline, whether it is jurisdictional,
and whether it confers **CDP rights** with the Form 12153 date; a 90-day letter
never lapses silently, and if it has, the post-90-day options are named; a
correction filed before the extended due date is a **superseding** return, not a
1040-X; QAR availability tests **all four** cutoff events; the **§6511(b)(2)
lookback cap** is computed, not just the deadline; a federal amendment records the
corresponding state deadline; an issued IP PIN appears on the return.

Verify with a licensed practitioner before filing. Representation requires Form
2848 — this skill does not represent the taxpayer.

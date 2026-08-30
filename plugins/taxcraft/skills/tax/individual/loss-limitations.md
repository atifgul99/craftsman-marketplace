
# Loss Limitations (the stack)

Owns the **state machine** every individual loss passes through: which bucket
holds a suspended amount, what moves it, and what the schedule must prove.

The ordering is owned by `individual/1040.md` §3. The doctrine of §465, §469,
§461(l), and §172 is not restated here — the model has it. What is here is the
part that is not in the model: the transitions, the required facts, the custody,
and the invariants.

**Verify at point of use** (`authority.md`): any threshold, percentage, or
effective date, **and** any of the qualitative propositions marked ⚠ below. A
doctrine statement in this file is a prompt to check, not a substitute for
checking.

---

## 0. Two gates ahead of basis

- **§183** — not engaged for profit ends the analysis. Post-§67(g)/§67(h) the
  expenses are **zero**, not deductible-against-income, so "hobby" now means
  income with no offset.
- **§280A(c)(5)** — a dwelling with personal use over the greater of 14 days or
  10% of rental days caps deductions at gross rental income, **with its own
  carryforward**, applied **before** §469.
  → `scenarios/rental-properties.md`, `scenarios/home-office-280a.md`.

## 1. Required facts

No layer can be applied without these. A missing one is a **hold**, not a zero.

| Fact | Needed for |
|---|---|
| Outside/stock basis, and **debt basis separately** for an S corp | Layer 1 |
| Share of liabilities by class — recourse / qualified nonrecourse / nonrecourse (K-1 item K) | Layers 1–2 |
| At-risk amount, and whether nonrecourse debt qualifies under §465(b)(6) | Layer 2 |
| Participation hours and the test relied on; **spouse's hours count** (Reg §1.469-5T(f)(3)) | Layer 3 |
| Activity's §469 grouping and whether it was **disclosed** (Rev. Proc. 2010-13) | Layer 3 |
| Whether the entity is a **PTP** | Layer 3 — segregates entirely → `ptp.md` |
| Aggregate trade-or-business income and deductions, employee items excluded **both ways** | Layer 4 |
| NOL layers **by vintage** | Layer 5 |

## 2. Verified transitions

These are the propositions the review process actually corrected. They are here
because a competent model gets them wrong, not because they are important.

| ⚠ Transition | Rule |
|---|---|
| **§465(e) recapture has two legs** | Negative at-risk creates income under §465(e)(1)(A), capped at previously allowed losses **not previously recaptured** — and **§465(e)(1)(B) makes the same amount a deduction allocable to the activity in the *succeeding* year**, re-entering the gauntlet. Booking only the income permanently overstates tax. |
| **QNRF exists only for real property — then a related person can qualify** | ⚠ **§465(b)(6)(A) limits qualified nonrecourse financing to an activity of *holding real property*.** Nonrecourse debt in an equipment, oil-and-gas, or operating fund is **not** QNRF no matter who lent it. Within that limit: the debt must not be convertible (§465(b)(6)(B)(iii)), no person may be personally liable (Reg §1.465-27(b)(2) — a disregarded entity's liability is disregarded), and §465(b)(6)(D)(ii) makes a **related person a qualified person** where the financing is commercially reasonable and on substantially the same terms as unrelated lending. A flat "unrelated lender" test denies at-risk basis the statute grants; a flat "any nonrecourse from a bank" test grants basis it does not. A partner's share follows §465(b)(6)(C) (the §752 nonrecourse allocation). |
| **§465 amounts are not released by §469(g)** | An amount still suspended at at-risk never reached §469. A disposition frees it only insofar as it generates activity income raising the at-risk amount. When released it is an **input to §469**, not a deduction. |
| **Released losses have an ordering** | ⚠ §469(g)(1)(A): allowed **first** against income or gain from **that activity**, **then** against net income from **all other passive activities**, **then** against nonpassive income. Releasing straight against wages is right only at the end of that sequence, and step 2 determines how much *other* suspended loss is freed. |
| **Related-party sale defers, it does not kill** | §469(g)(1)(B): suspended passive losses are not allowed until transfer to an **unrelated** person; they remain available against that activity meanwhile. |
| **Death, gift, installment, partial, nonrecognition** | Death: allowed only to the extent they exceed the §1014 step-up (§469(g)(2)). Gift: disallowed to donor, **added to donee's basis** (§469(j)(6)). Installment: released **ratably with gain recognized** (§469(g)(3)). Partial: only via the Reg §1.469-4(g) "substantially all" route. §1031/§721/§351/S-election: **not** fully taxable — release nothing. |
| **Suspended passive *credits* are never released** | §469(d)(2). Only relief is the §469(j)(9) basis-increase election in the disposition year. |
| **§469(f)(3) former passive activity** | Ceasing to be passive does **not** release; losses stay allowed only against that same activity. |
| **§469(i) has two hard gates** | 10% interest by value at all times (§469(i)(6)(A)); a **limited partner can never actively participate** (§469(i)(6)(C)). MFS living apart: reduced allowance and threshold; living together: zero. ⚠ **This file owns the §469(i)(3)(F) modified-AGI definition:** AGI computed **without** IRA deductions, taxable Social Security, §221 student-loan interest, §199A, the §911 exclusions, and **the passive losses themselves** (`1040.md` §4). |
| **§469(c)(7)(D)(ii)** | Employee services don't count toward REPS unless the taxpayer owns **more than 5%** of the employer — this disqualifies most claimants. |
| **Reg §1.469-9(g) aggregation has a cost** | With all rentals in one activity, **§469(g) releases nothing until the whole group is disposed of.** Binding for all future qualifying years; Rev. Proc. 2011-34 gives late-election relief. |
| **Self-rental is asymmetric** | Reg §1.469-2(f)(6): net **income** from renting to a business the taxpayer materially participates in is **nonpassive**; a net **loss** stays passive. The examiner's first adjustment. |
| **Portfolio income is not passive** | §469(e)(1) — it cannot absorb passive losses. |
| **STR fails closed** | A ≤7-day-average activity is **not a rental activity**, so failing material participation leaves a passive loss with **no §469(i) allowance and no REPS route**. Fewer escape hatches than an ordinary rental. |
| **§469 status does not determine SE tax** | §1402(a)(1) and Reg §1.1402(a)-4(c)(2) govern independently: services beyond those customary for occupancy. Never derive one from the other. |
| **§461(l) did not apply TY2018–2020** | CARES §2304(a) deferred it. An NOL layer rebuilt from those years carries **no** EBL addition. Employee items are excluded **symmetrically** (income, deductions, and gains). ⚠ OBBBA made it permanent — **verify whether the enacted text altered the carryforward's character or indexing base.** |
| **§461(l) disallowance becomes an NOL** | It changes character; it does not roll forward in a §461(l) bucket. It then meets the §172 percentage limitation, so it is not pure timing. |
| **NOL is vintage-layered** | Pre-2018 absorbed first against 100%; post-2017 limited to a percentage of taxable income computed **without** the NOL, §199A, and §250 deductions. CARES suspended the limitation for years beginning before 1/1/2021 and gave 2018–2020 a 5-year carryback. ⚠ Verify the percentage. |
| **§172(d) modifications** | An individual's NOL is **not** negative taxable income — capital losses only to capital gains, no §199A/§250, no standard deduction (2018–2025), and **nonbusiness deductions only to nonbusiness income**. Without these the carryforward is simply wrong. TY2024+ uses **Form 172**. |
| **§163(j) EBIE is a fifth bucket** | Released only by excess taxable income or excess business interest income **from the same partnership** (§163(j)(4)(B)(ii)); it **reduces outside basis when allocated** (iii)(I) and is **added back to basis on disposition** (iii)(II) rather than deducted — the only bucket whose disposition trigger produces basis. |
| **§199A carryforward is its own bucket** | §199A(c)(2), allocated proportionately among businesses with positive QBI and **not** taken into account in the W-2/UBIA limitation (Reg §1.199A-1(d)(2)(iii)). Released losses enter QBI **FIFO by origin year**; those from years beginning before 1/1/2018 are **never** QBI items. |
| **S-corp exit is not symmetric with partnership exit** | A §704(d) suspended loss is **lost** on a complete disposition (*Sennett*). An S-corp §1366(d) loss survives a **§1041 transfer** to a spouse (§1366(d)(2)(B)) and is deductible in the **post-termination transition period** to the extent of **stock basis only** (§1366(d)(3)). |
| **Substantiation is not limited to contemporaneous logs** | Reg §1.469-5T(f)(4): "any reasonable means"; daily reports are **not required**. Reconstruction from third-party records is regularly accepted — do not concede a defensible position. |
| **Limited partner ≠ LLC member for §469(h)(2)** | A limited partner may use only tests 1, 5, 6. LLC members may use all seven — *Garnett*, *Thompson*, *Newell*. |

## 2a. The two enumerations other files point at

Kept because `scenarios/rental-properties.md` and the §2 table route here for
them, not because the model cannot recall them.

**Material participation — Reg §1.469-5T(a):** (1) >500 hours; (2) substantially
all of the participation in the activity; (3) >100 hours and not less than any
other individual; (4) significant participation activities aggregating >500 hours;
(5) material participation in **5 of the prior 10** years; (6) a **personal service
activity** in any 3 prior years; (7) facts and circumstances. ⚠ Tests 5 and 6
confer status **without current-year hours**. ⚠ A **limited partner** may use only
tests **1, 5, or 6** (§469(h)(2)) — but an **LLC member is not a limited partner**
for this purpose (*Garnett*, *Thompson*, *Newell*) and may use all seven.

**Not a "rental activity" — Reg §1.469-1T(e)(3)(ii):** (A) average customer use
**≤7 days**; (B) average **≤30 days with significant personal services**;
(C) extraordinary personal services regardless of period; (D) rental incidental to
a non-rental activity; (E) property customarily available during defined business
hours for nonexclusive customer use; (F) property provided to a partnership,
S corp, or joint venture in which the taxpayer owns an interest. ⚠ Treating (A) as
the only one is the common error — (B) is the serviced-property case.

## 3. Four partitions, not one

The single most consequential structural point. These regimes group activities
**differently and non-interchangeably**:

| Regime | Partition | Authority |
|---|---|---|
| At-risk | §465 activity; six enumerated activities held separately | §465(c) |
| Passive | appropriate economic unit | Reg §1.469-4 |
| QBI | aggregation, own tests and annual disclosure; **PTPs may not be aggregated** | Reg §1.199A-4 |
| NIIT | §1411 grouping, one-time fresh-start regrouping | Reg §1.1411-4/-5 |

§465(c) activities **cannot** be grouped under Reg §1.469-4. A schedule keyed to
one slug across all four will foot and be wrong.

## 4. Carryforward schedule

One row per activity **per regime**, per year.

```json
{
  "activity_label": "<slug>",
  "_basis_ssot": "individual/investments/<slug>/position.md | individual/properties/<slug>/depreciation-schedule.md",
  "partitions": {"section_465_activity": "", "section_469_group": "",
                 "section_199A_aggregation": "", "section_1411_group": ""},
  "tax_year": 0,
  "gates": {"section_183_profit_motive": null, "section_280A_c5_cap": null},
  "material_participation": {"test_met": null, "hours": null,
                             "spouse_hours_included": null, "substantiation": ""},
  "basis": {"beginning": 0, "additions": 0, "reductions": 0, "ending": 0,
            "stock_basis": 0, "debt_basis": 0, "debt_basis_restored": 0,
            "suspended_beginning": 0, "allowed": 0, "suspended_ending": 0},
  "at_risk": {"beginning": 0, "qualified_nonrecourse": 0, "ending": 0,
              "suspended_beginning": 0, "allowed": 0, "suspended_ending": 0,
              "recapture_465e_income": 0,
              "recapture_465e_deduction_next_year": 0},
  "passive": {"suspended_beginning": 0, "current_year": 0, "allowed": 0,
              "allowance_469i_used": 0, "modified_agi_469i3F": null,
              "recharacterized_nonpassive_1469_2f": 0,
              "suspended_ending": 0, "released_this_year": 0,
              "release_trigger": null, "suspended_credits": 0},
  "section_163j_ebie": {"partnership_slug": "", "allocated": 0,
                        "basis_reduced": 0, "suspended_beginning": 0,
                        "released": 0, "suspended_ending": 0,
                        "added_to_basis_on_disposition": 0},
  "qbi": {"qbi_this_activity": 0, "negative_carryforward_199A": 0,
          "origin_year_layers": []},
  "disposition": {"occurred": null, "date": "", "type": "",
                  "fully_taxable": null, "entire_interest": null,
                  "related_party_267b_707b1": null, "installment": null,
                  "gift": null, "death": null}
}
```

Taxpayer-level, recorded once:

```json
{"section_461l": {"aggregate_net_business_loss": 0, "threshold": 0,
                  "disallowed": 0, "becomes_nol_next_year": 0},
 "nol_by_vintage": [{"vintage_year": 0, "regime": "pre_2018|post_2017",
                     "beginning": 0, "used": 0, "ending": 0}]}
```

Written to `individual/FY<YYYY>/annual/workpapers/wp-suspended-losses.md`. The
basis, at-risk, and passive balances are **read from and written back to** the
SSOT in `_basis_ssot` (`1040.md` §5) — this schedule records the year's movement,
never an independent lifetime computation.

## 5. Invariants

- beginning suspended + current-year suspended − released = ending suspended, per
  layer, per activity;
- **an amount released from layer N is an input to layer N+1, not a deduction**;
- at-risk for an entity ≤ outside basis for that entity;
- §465(e) income this year = §465(e) deduction next year;
- every release names a trigger from the §2 table;
- §461(l) disallowance this year = NOL addition next year, by vintage;
- §163(j) EBIE carries its originating partnership;
- ending suspended per activity ties to Forms 6198 / 8582 / 461.

A failed invariant is a hold. Do not net across activities to make it foot.

Verify with a licensed practitioner before filing.

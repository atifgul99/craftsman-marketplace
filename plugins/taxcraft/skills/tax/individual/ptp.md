
# Publicly Traded Partnerships

A PTP K-1 looks like any other and follows almost none of the same rules.
⚠ Treating one as an ordinary partnership interest is wrong **in both
directions** — it overstates deductible losses in the holding years and
understates ordinary income on sale.

Definition: §7704. A fund that issues a K-1 and trades under a ticker is almost
always a PTP. Identify it **before** any number enters the passive basket.

## 1. §469(k): suspended per PTP

⚠ **§469(k) is the third gate, not the first.** A PTP loss must clear **outside
basis (§704(d))** and **at-risk (§465)** first, and MLPs allocate nonrecourse debt
affecting both. Run `loss-limitations.md` §§1–2 first.

A PTP is then a **separate activity**. Its passive losses offset only income from
**that same PTP** — never other passive income, portfolio income, or wages.
⚠ **The mirror is equally true: PTP net income cannot absorb passive losses from
other activities.**

- Most software handles this only if the PTP box is checked on K-1 entry — verify.
- ⚠ Release requires **all** §469(g) conditions: the **entire interest**, in a
  **fully taxable** transaction, to an **unrelated** party. A partial sale, gift,
  nonrecognition or partially deferred transaction (including an installment
  sale, where release follows gain recognized), or related-party transfer
  releases **nothing**. "Sold it" is not sufficient.
- ⚠ The **§469(i) $25,000 allowance is not available** to PTPs.
- ⚠ Commodity and futures PTPs often produce **portfolio and §1256 income rather
  than passive income**, in which case §469(k) suspension does not apply at all.
  Do not assume this section governs every PTP.

Track each PTP as its own activity row (`loss-limitations.md` §4).

## 2. §199A: a separate, combined component

⚠ The component is **qualified REIT dividends *and* qualified PTP income
combined** — a component containing only PTPs is incomplete. It is **not**
subject to the W-2 wage or UBIA limitations. A **negative** amount carries forward
under Reg §1.199A-1(d)(3)(iv) against that **combined** component, so it can be
absorbed by **REIT dividends**, not PTP income alone; it never touches the QTB
component. ⚠ **PTP interests may not be aggregated** (Reg §1.199A-4(b)(1)).
SSTB status still matters above the threshold. On Form 8995 these are separate
lines; a blended QBI number is a defect.

## 3. Basis, and why the broker cannot know it

Outside basis is adjusted annually by allocated income and loss, the **§752
liability share** (K-1 item K), and — critically — **cash distributions**, which
are large and are a **return of capital reducing basis**, not income.

⚠ **The 1099-B reports the original purchase price, not adjusted basis.** Using it
on a PTP sale is the most common PTP error and generally understates gain
substantially.

The correct figure comes from the partnership's **sales schedule** with the final
K-1. ⚠ Most sales schedules report a **cumulative adjustment to basis**, not a
finished adjusted basis, and require matching by **purchase lot and date** — read
what actually arrives.

## 4. Sale: §751 ordinary income

⚠ Reporting sequence:

1. **Amount realized** = cash and property received ⚠ **plus the seller's share of
   partnership liabilities relieved (§752(d), §1001)**. The 1099-B reports only
   cash. For a leveraged PTP this is large, and it is why PTP sale gains look
   implausible relative to cash received.
2. **§751 ordinary component** → Form 4797 Part II. ⚠ It is computed
   **independently** as the amount allocable on a hypothetical sale of the §751
   property (Reg §1.751-1(a)(2)) — **it is not a carve-out of total gain and can
   exceed it.** For an MLP sold at an economic loss after years of
   distribution-driven basis erosion, the normal outcome is **ordinary income
   plus a capital loss**, with the ordinary income taxed in full and the loss
   throttled by §1211(b). That asymmetry is the defining PTP surprise.
3. **Remainder** → Form 8949, usually **noncovered (Box B/E)**, sometimes at $0
   basis; correct with **code B** and the adjustment in column (g). The remainder
   **may be negative** and the invariant still holds.
4. **Release** suspended §469(k) losses — only if §1's three gates are met.
5. ⚠ **Obtain the §751 statement.** A transferor must furnish the
   **Reg §1.751-1(a)(3)** statement with the return for the year of transfer, and
   the partnership has its own **Form 8308** obligation. Absent the sales schedule
   or statement, the split is unsupported — a **hold**, not an estimate.
6. ⚠ **Do not double-count.** The 1099-B proceeds and the K-1 sales schedule
   describe the **same** transaction. Reporting both without an adjustment reports
   the sale twice — frequent, large, and easily detected.

## 5. Other recurring issues

- **State footprint** — PTPs allocate across many states. Most fall below
  nonresident thresholds, but not always, and a few states have none. Capture the
  schedule annually → `state-residency.md`.
- ⚠ **UBTI in an IRA — two different $1,000 tests, commonly conflated.**
  **Form 990-T filing** is required at **gross** unrelated business income of
  $1,000 or more (§6012(a)(4)); the **§512(b)(12) specific deduction** reduces
  **net** UBTI in computing the tax. An IRA with $1,400 gross and $600 net has a
  filing obligation and no tax.
  ⚠ **§512(a)(6) siloing** computes UBTI **separately per unrelated trade or
  business**, and Reg §1.512(a)-6 treats each partnership interest as its own silo
  unless it qualifies under the de minimis (≤2%) or control (≤20%) test —
  **losses cannot cross silos**, which is the whole computation for an IRA holding
  several MLPs. §514 UDFI runs through the same return.
  ⚠ **Why holding a PTP in an IRA is usually a mistake:** on sale the **§751
  ordinary recapture is UBTI**, even though §512(b)(5) excludes ordinary capital
  gain from property sales. The holding years produce small UBTI; the exit year
  detonates. The **custodian** files the 990-T under the **IRA's EIN** and the tax
  is paid **from IRA assets** — paying personally is an excess contribution.
  → `scenarios/self-directed-ira.md`.
- **§163(j) EBIE (box 20 code AE)** — suspended at the partner level, released
  only by excess taxable income or excess business interest income **from the same
  partnership**; **reduces outside basis when allocated** and is **added back to
  basis on disposition** rather than deducted. → `loss-limitations.md`.
- **§1256 pass-through** from commodity PTPs → `capital-gains.md`.
- ⚠ **K-3s arrive late.** Do not file assuming zero foreign items because one has
  not arrived — that is a hold. Amended PTP K-1s are endemic and a common 1040-X
  trigger → `notices-amendments.md`.
- ⚠ **Distributions in excess of basis** are §731 gain **in the year received**,
  not deferred to sale. Gain is capital only if the interest is a capital asset;
  Reg §1.731-1(a)(1)(ii) treats advances and draws as made on the **last day of
  the year**, so basis is tested at year end; and a **§752(b)** decrease in the
  liability share is a deemed distribution that can trigger §731 gain **with no
  cash**.

## 6. Workpaper

One row per PTP in `wp-schedule-e-p2.md`:

```json
{
  "ptp": "<slug>", "ein_last4": "",
  "_basis_ssot": "individual/investments/<sponsor-slug>/position.md",
  "units_held_beginning": 0, "units_acquired": 0, "units_sold": 0,
  "outside_basis_beginning": 0, "allocated_income_loss": 0,
  "liability_share_752": 0, "distributions": 0, "outside_basis_ending": 0,
  "section_731_gain": 0,
  "suspended_469k_beginning": 0, "current_year_loss": 0,
  "allowed_against_this_ptp_income": 0, "suspended_469k_ending": 0,
  "released_on_complete_disposition": 0,
  "income_character": "passive|portfolio|1256",
  "qbi_ptp_reit_component": 0, "qbi_component_negative_carryforward": 0,
  "section_163j_ebie": {"allocated": 0, "basis_reduced": 0, "suspended_ending": 0},
  "sale": {"sales_schedule_received": false,
           "cash_and_property_received": 0,
           "share_of_liabilities_relieved_752d": 0, "amount_realized": 0,
           "section_751_statement_received": false,
           "form_8308_information_received": false,
           "disposition_fully_taxable": null, "transferee_unrelated": null,
           "entire_interest": null,
           "adjusted_basis_per_sales_schedule": 0,
           "section_751_ordinary": 0, "capital_gain_or_loss_remainder": 0,
           "form_1099b_basis_reported": 0, "adjustment_code": ""},
  "state_allocations": [], "k3_received": false,
  "held_in_retirement_account": null
}
```

**Invariants:** basis fields are read from and written back to the position SSOT —
this workpaper records the year's movement only (`1040.md` §5); ending basis ≥ 0
with excess distributions recorded as §731 gain; suspended §469(k) never offsets
non-PTP income and PTP income never absorbs other passive losses; amount realized
includes §752(d) relief; release requires all three §469(g) gates; §751 ordinary +
capital remainder = total gain, supported by the sales schedule **and** the
Reg §1.751-1(a)(3) statement, with the 1099-B corrected rather than reported
alongside.

Verify with a licensed practitioner before filing.

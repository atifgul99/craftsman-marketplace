
# Capital Gains, Cost Basis, and Form 8949

Owns brokerage reconciliation and the **basis-correction evidence contract**.
Digital assets are `digital-assets.md`; equity-comp basis originates in
`scenarios/equity-comp.md` and is corrected here on sale.

**Verify at point of use** (`authority.md`): rate thresholds, the §1211(b) limit,
§1202 caps, and every ⚠ proposition below.

## 1. Reconciliation, not a forced tie

```
Σ 1099-B box 1d proceeds  =  Σ Form 8949 col (d)  ±  explained reconciling items
```

⚠ Legitimate differences — a mismatch here is not an error: **§1256 contracts,
regulated futures, and forex go to Form 6781, never 8949**; option premium on
unexercised or assigned positions; §171 bond premium and OID; corporate actions
and return-of-capital; sell-to-cover netting; broker-reported wash sales. Every
difference gets a line and a reason. **Forcing the tie is worse than reporting
the difference.** An unexplained difference is a hold.

## 2. Basis corrections — the evidence contract

Brokers report basis only for **covered** securities (equities after 2010; funds
and DRIP after 2011; options and less-complex debt after 1/1/2014; **more complex
debt after 1/1/2016**). Each correction needs a **code, a reason, and evidence**.

⚠ **For compensatory stock acquired after 1/1/2014, Reg §1.6045-1(d)(6)(iii)
*prohibits* the broker from including the compensation income in reported basis.**
The broker is complying, not erring — the adjustment is routine (code B), not a
dispute. RSU/ESPP/ISO basis is the single most common overstatement of gain on an
individual return; always tie to the W-2 and Forms 3921/3922.

**Form 8949 adjustment codes** — the invariant is unenforceable without them:
**B** (basis reported but incorrect), **T** (basis not reported and wrong),
**W** (wash sale), **N** (nominee), **D** (commissions/premium in basis),
**E** (selling expenses), **M** (summarized), **Q**/**X** (§1202 full/partial),
**O** (other, needs explanation).

⚠ Items with **no broker record at all**:
- **Market discount (§1276)** — accrued discount on a bond sold at a gain is
  **ordinary income** (box 1f). It converts *character*, it does not adjust basis.
- **§307 / §355 allocation** on stock dividends, rights, and spin-offs.
- **ISO dual basis** — regular basis is the exercise price, AMT basis is FMV at
  exercise, producing a negative AMT adjustment and a possible §53 credit **in
  the year of sale**. SSOT: `records/basis/amt-dual-basis.md`.
- **§1015 gift dual basis**, plus the §1015(d)(6) increase for gift tax on net
  appreciation. **§1014** step-up, with §2032 alternate valuation available only
  if a 706 was filed and it reduces both the estate and the tax; inherited
  property is long-term under **§1223(9)** regardless of holding period.
- **1099-DIV box 3 nondividend distributions** reduce basis; past zero they are
  **capital gain under §301(c)(3)**.
- ⚠ **§1031 never applies to securities** — excluded by name pre-TCJA and limited
  to real property after 2017. There is no §1031 lot on a 1099-B. §1033 can occur.

## 3. Wash sales (§1091)

⚠ The traps, not the rule:

- **Per taxpayer, not per account.** Broker A's sale replaced at broker B is
  invisible on both 1099-Bs.
- **A replacement inside an IRA destroys the loss permanently — no basis increase
  to the IRA.** That is **Rev. Rul. 2008-5**, an unlitigated IRS position, not a
  statutory rule; label it as a ruling. It reaches the taxpayer's **own** IRA; a
  *spouse's* IRA is a further extension the ruling does not make.
- The **spouse-account** rule has no statutory basis in §1091 either — it rests on
  IRS position and *McWilliams v. Commissioner*, 331 U.S. 694 (1947).
- **The 61-day window straddles the calendar year** — a December harvest with a
  January repurchase is the most frequent year-end failure.
- **Partial replacement is prorated** (§1091(b); Reg §1.1091-1(c)–(d)) — a
  computation, and the most common arithmetic error here.
- §1091 reaches a **contract or option to acquire**, not only the stock.
- Automatic dividend reinvestment creates wash sales silently.
- **§1091 does not currently reach digital assets** → `digital-assets.md`.

## 4. Lot identification

⚠ Specific ID requires identification **to the broker by settlement date** with
written confirmation (Reg §1.1012-1(c)); a standing instruction counts, a
spreadsheet prepared at filing does not. Absent instruction the **broker's
default governs the 1099-B**, and a different method generally cannot be reported
on a covered lot without an adjustment and explanation. Average cost is
revocable **retroactively only before the first sale** in the account
(Reg §1.1012-1(e)(9)(iii)). Standing instructions live in `records/elections/`.

## 5. Character and specialized regimes

Rates are **maximums** and apply to **long-term** gain; short-term is ordinary.
⚠ The **§1(h) netting and ordering rules** govern how a net loss in one group
offsets another (28% first, then 25%, then 20/15/0) — the "buckets sum to
Schedule D" invariant cannot be verified without them. Collectibles run through
the 28% Rate Gain Worksheet and unrecaptured §1250 through its own, not directly
onto Schedule D. For **§1202** the answer bifurcates by **issuance date**
→ `scenarios/qsbs-1202.md`.

⚠ Regime traps:

- **§475(f) trader mark-to-market** — the highest-dollar item here for an active
  trader. Ordinary treatment (no §1211 cap), **exempt from §1091**, and the
  election is due by the **unextended due date of the *prior* year's return**
  with a Form 3115 in the election year. Whether digital assets are "commodities"
  under §475(f)(2) is unsettled — document the position.
- **§1256** — regulated futures, **broad-based** index options, forex. **Single-
  stock and narrow-based index options are NOT §1256.** The net-loss carryback is
  three years against prior net §1256 gains, elected on **Form 6781 box D** under
  **§1212(c)** — Form 1045/1040-X is the refund vehicle, not the election — and it
  cannot create or increase an NOL.
- **Options** — a **qualified covered call (§1092(c)(4))** is excepted from the
  straddle rules; an **unqualified** one triggers §1092 **and suspends the QDI
  holding period**. The two rules meet at the most common retail strategy.
- **§1092 straddles** — plus §1092(a)(2) identified straddles and §263(g)
  carrying charges.
- **§165(g) worthless securities** — a note or informal debt is **not** a security
  (§165(g)(2)); that is a §166 bad debt. The refund claim gets **7 years**
  (§6511(d)(1)).
- **§453 installment** — ⚠ **not available for securities traded on an established
  market (§453(k)(2))**, the rule that matters most here. Ratio fixed at sale;
  §453A interest above the threshold; electing out is irrevocable. SSOT for the
  ratio: `1040.md` §5.
- ⚠ **§1058 securities lending** converts dividends into **substitute payments**,
  destroying QDI.
- ⚠ **Trade date, not settlement date**, controls year-end recognition.
- ⚠ **The carryover is reduced by the amount *allowable*, not the amount that
  produced a benefit** (§1212(b)(2) and the carryover worksheet). A year with no
  taxable income still consumes the annual ordinary offset — do not preserve the
  full carryover.
- **§165(g)** treats a worthless security as sold on the **last day of the taxable
  year**, which can convert a short-term position to long-term.
- ⚠ Ordinarily a disallowed wash-sale loss is **added to the replacement lot's
  basis with the holding period tacking** (§1091(d)) — that is the baseline the
  IRA exception in §3 departs from.

## 6. Interactions

NIIT is a separate tax on its own base — **never added to the 0/15/20% rate**.
The §163(d)(4)(B)(iii) election trades the preferential rate for a current
deduction (`itemized.md`). §469(g) release on a complete disposition
(`loss-limitations.md`). Donating appreciated long-term securities avoids the
gain entirely — ⚠ but for years beginning after 12/31/2025 the OBBBA charitable
floor and benefit cap weaken that comparison at smaller gift sizes; re-run it
(`itemized.md`). State treatment: `state-residency.md`.

## 7. Workpaper

`wp-schedule-d-8949.md`:

```json
{
  "brokers": [{"slug": "", "acct_last4": "", "form_1099b_proceeds_box1d": 0,
               "reported_on_8949": 0,
               "reconciling_items": [{"description": "", "amount": 0, "destination": ""}]}],
  "basis_adjustments": [{"lot": "", "as_reported": 0, "corrected": 0,
                         "adjustment_code": "", "reason": "", "evidence": ""}],
  "wash_sales": {"broker_reported": 0, "cross_account_identified": 0,
                 "spouse_account_identified": 0,
                 "ira_replacement_permanently_disallowed": 0,
                 "partial_replacement_prorated": null},
  "buckets": {"short_term": 0, "ltcg": 0, "unrecaptured_1250": 0,
              "collectibles": 0, "section_1202": 0, "section_1256_6781": 0},
  "carryover": {"short_term_in": 0, "long_term_in": 0,
                "used_against_ordinary": 0, "short_term_out": 0, "long_term_out": 0},
  "lot_id_method": {"method": "FIFO | specific_id | average_cost",
                    "standing_instruction_on_file": false,
                    "confirmed_by_settlement_date": null},
  "elections": {"section_475f": null, "section_163d4Biii": null}
}
```

**Invariants:** proceeds reconcile with every difference explained; each basis
adjustment carries code + reason + evidence; wash sales evaluated across **all**
accounts including IRAs and spouse accounts; buckets sum to Schedule D under the
§1(h) ordering; carryover ties to prior year by character; specific-ID claimed
only with settlement-date confirmation.

Verify with a licensed practitioner before filing.

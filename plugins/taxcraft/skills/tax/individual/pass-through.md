
# K-1s and Schedule E Part II

Owns what happens to a K-1 **after** it arrives: routing every box and code,
maintaining the position's balances, and carrying separately-stated items to
their destinations.

Boundaries: entity-side preparation → `entities/partnership.md`,
`entities/s-corp.md`. Limitation mechanics → `loss-limitations.md` (this file
maintains balances; that file applies the gauntlet). **PTPs → `ptp.md`; a PTP is
not processed here.** Sponsor patterns → `scenarios/k1-vc-pe.md`,
`k1-oil-gas.md`, `contested-k1.md`, `tiered-partnership-se.md`.

**Position SSOT:** `investments/<sponsor-slug>/position.md` holds outside basis,
at-risk, and suspended passive by activity (`1040.md` §5). The annual workpaper
records the year's movement and writes back — never an independent lifetime
reconstruction.

## 1. Intake gates

1. ⚠ **Is it a PTP?** A ticker, a §7704 designation, or a sales schedule with
   cumulative adjustments ⇒ `ptp.md`. Getting this wrong corrupts the passive
   basket in both directions.
2. **Final or amended?** Either changes the year's treatment and may trigger a
   §469(g) release or a 1040-X.
3. **Draft or estimate?** ⚠ A draft K-1 makes every dependent line `PROVISIONAL`.
   Never promote a draft to a filed figure.
4. **Whose K-1?** The named partner may be a disregarded SMLLC whose regarded
   owner is the taxpayer or an entity → `entities/disregarded.md`, `naming.md`.
5. ⚠ **K-3 present?** A missing K-3 where the K-1 shows foreign activity is a
   **hold on the FTC line, not a zero** → `foreign.md`.
6. ⚠ **Statements?** Box 20 codes **Z** (§199A), **AE** (§163(j)), **V** (UBTI),
   and most oil-and-gas codes are **statement-dependent**. An unparsed statement
   leaves the code `UNREADABLE`, **not** `OBSERVED_ZERO`.

## 2. Routing

⚠ **Every box and code is routed or explicitly marked `NOT_APPLICABLE`.** A K-1
with entries nobody looked at is the most common way a separately-stated item
disappears.

### Form 1065 K-1 — destinations that are not obvious

| Box | Note |
|---|---|
| 4a/4b | Guaranteed payments — ⚠ **4a is SE income** |
| 8 / 9a–9c | Keep the **character buckets separate** (`capital-gains.md` §5) |
| 10 | §1231 → Form 4797; ⚠ watch the **§1231(c) five-year lookback** converting gain to ordinary |
| 12 | §179 is limited at the **partner** level, cannot create a loss, and the carryforward is personal |
| 13 | Charitable **keeps its AGI class** (`itemized.md`); investment interest; §59(e); UPE |
| 14 | Sch SE — ⚠ **limited partner status is contested** (*Soroban*, *Denham*) → `scenarios/tiered-partnership-se.md` |
| 15 | Credits incl. **state PTET credit** → `state-residency.md` |
| 17 | AMT items → Form 6251 |
| 18 | ⚠ **Tax-exempt income and nondeductible expenses BOTH adjust basis** — commonly skipped |
| 19 | Distributions reduce basis **before** losses; excess is §731 gain |
| 20 | Z / AE / V / AH — statement-dependent, §3 |

⚠ **Item K liabilities** — recourse, qualified nonrecourse, and nonrecourse are
**not interchangeable**: they drive §752 basis and §465 at-risk differently, and a
change in the share is a **basis event with no cash movement**.

⚠ **Item L** is the tax-basis **capital account**, not outside basis (it excludes
the liability share). Reconcile them; never substitute one for the other.

### Form 1120-S K-1 — the differences that matter

⚠ **No liability share — entity-level debt does not create shareholder basis.**
Only direct shareholder loans create **debt basis**, tracked separately
(§1367(b)(2)) and restored before stock basis. No SE income from the K-1.
⚠ **Form 7203 is required with the 1040** for any loss, distribution,
disposition, or loan repayment — a 1040 attachment the entity return does not
carry. Distributions above stock basis are capital gain (§1368); AAA ordering
matters with accumulated E&P.

### Form 1041 K-1

DNI drives what the beneficiary reports; character passes through. ⚠ **Excess
deductions on termination (§642(h))** flow to the beneficiary and, post-TCJA,
**retain their character** rather than being suspended miscellaneous deductions.
Final-year capital loss carryovers pass through.

## 3. Statement-dependent codes

⚠ These carry more consequence than the face of the K-1.

**§199A (Z)** — the statement must give, **per trade or business**: QBI, W-2
wages, UBIA, SSTB status, and REIT dividends. **A single blended number cannot be
used.** Qualified PTP income is a separate combined component (`ptp.md`). The QBI
loss carries in its **own** bucket (§199A(c)(2)).

**§163(j) (AE)** — suspended at the **partner** level, released only by excess
taxable income or excess business interest income **from the same partnership**
(§163(j)(4)(B)(ii)); it **reduces outside basis when allocated** and is **added
back to basis on disposition** rather than deducted. A fourth bucket; never merged
with passive, and it must carry its originating partnership.

**§59(e)** — partner-level election to amortize IDC and similar, avoiding the AMT
preference → `scenarios/k1-oil-gas.md`.

**UBTI (V)** — only where the partner is a retirement account or exempt
organization; §512(a)(6) siloing applies → `ptp.md` §5,
`scenarios/self-directed-ira.md`.

**State schedules** — apportionment, composite participation, withholding, PTET
credits. Capture annually → `state-residency.md`.

## 4. Basis maintenance

```
beginning
  + contributions + share of income (including tax-exempt income)
  + increase in share of liabilities (§752)
  − distributions − share of nondeductible expenses
  − decrease in share of liabilities − losses allowed
  = ending   (never below zero; excess distributions are §731 gain)
```

At-risk (§465) is maintained **separately** and excludes nonrecourse other than
QNRF. Ordering is `1040.md` §3: income, then distributions, then nondeductible,
then losses.

## 5. Recurring problems

| Problem | Handling |
|---|---|
| K-1 arrives after filing | Superseding return before the extended due date; otherwise 1040-X → `notices-amendments.md` |
| Amended K-1 | Re-run the gauntlet; balances change; check whether a release occurred |
| Disputed K-1 | → `scenarios/contested-k1.md` (Form 8082) |
| Never issued | ⚠ Do not estimate into a filed return — extend, or file with Form 8082 and disclosure |
| Partner is a disregarded SMLLC | The regarded owner is the tax partner → `entities/disregarded.md` |
| Multiple activities on one K-1 | ⚠ Separate them — §469 is per activity, and grouping is an election, not a default |
| Sale of the interest | Amount realized includes the liability share (§752(d)); §751 ordinary component; §469(g) release only if fully taxable, entire interest, unrelated party |

## 6. Workpaper

`wp-schedule-e-p2.md`, one block per position:

```json
{
  "position": "<sponsor-slug>",
  "_basis_ssot": "individual/investments/<sponsor-slug>/position.md",
  "entity_type": "partnership|s_corp|trust", "is_ptp": false,
  "k1_status": "final|draft|amended|missing", "k3_received": null,
  "activities": [{"activity": "", "type": "trade_or_business|rental|portfolio"}],
  "boxes_routed": [{"box": "", "code": "", "amount": 0, "destination": "",
                    "statement_parsed": null}],
  "unrouted_boxes": [],
  "liabilities": {"recourse": 0, "qualified_nonrecourse": 0, "nonrecourse": 0,
                  "change_from_prior": 0},
  "capital_account_item_L": {"beginning": 0, "ending": 0,
                             "reconciled_to_outside_basis": null},
  "basis_movement": {"beginning": 0, "contributions": 0, "income": 0,
                     "tax_exempt_income": 0, "liability_change": 0,
                     "distributions": 0, "nondeductible": 0,
                     "losses_allowed": 0, "ending": 0, "section_731_gain": 0},
  "at_risk_movement": {"beginning": 0, "ending": 0},
  "section_199a": [{"trade_or_business": "", "qbi": 0, "w2_wages": 0,
                    "ubia": 0, "sstb": null}],
  "section_163j_ebie": {"partnership_slug": "", "allocated": 0,
                        "basis_reduced": 0, "suspended_beginning": 0,
                        "released": 0, "suspended_ending": 0,
                        "added_to_basis_on_disposition": 0},
  "state_allocations": [{"state": "", "income": 0, "withholding": 0,
                         "composite_participation": null, "ptet_credit": 0}],
  "form_7203_required": null
}
```

**Invariants:** `unrouted_boxes` is empty before the package completes; basis and
at-risk are read from and written back to the position SSOT and record only the
year's movement; ending basis ≥ 0 with excess distributions as §731 gain; item L
is reconciled to outside basis, not substituted for it; §199A components are
per-trade-or-business, never blended; §163(j) EBIE **carries its originating
partnership**; a missing K-3 with foreign indicators holds the FTC line; Form 7203
flagged for every S-corp loss, distribution, disposition, or loan repayment.

Verify with a licensed practitioner before filing.


# Digital Assets

Owns crypto, NFTs, and tokenized assets. Separate from `capital-gains.md` because
the basis rule, the reporting regime, and the wash-sale answer are all different —
and **all three changed inside TY2023–2026**.

⚠ **Year-dependence is the defining feature here. Almost nothing is timeless.**
Verify the target year before applying any rule below.

## 1. Taxable events

Dispositions include the ones people miss: ⚠ **a crypto-to-crypto swap** is a
disposition of the asset given up at FMV; **spending it**; and **paying a fee in
kind** (a gas fee is a disposition of the fee amount). Not dispositions: buying
with fiat, self-transfers between the taxpayer's own wallets, holding.

⚠ **Bridging, wrapping, lending, LP deposits, and restaking have no clear
guidance.** Document the position and its rationale — and note that **Notice
2024-57** identifies six such classes brokers need not report pending guidance,
which is affirmative IRS acknowledgment that strengthens a documented position.

**Page-1 question**: "Yes" for a disposition **and** for receipt as payment or
reward — including from **mining, staking, and a hard fork**, all express
triggers in the instructions. Holding, self-transfers, and purchase with real
currency are "No."

## 2. Basis and lot identification — the 2025 discontinuity

⚠ **The rule:** per-wallet/per-account basis is imposed by **Treas. Reg.
§1.1012-1(j)** (TD 10000) for acquisitions and dispositions **on or after
1/1/2025**. Universal pooling is no longer permitted.

⚠ **The transition:** **Rev. Proc. 2024-28** is the one-time safe harbor for
allocating unused pre-2025 basis. It implements the transition; it does not
create the rule. The allocation plan had to be in the taxpayer's books **as of
the beginning of 1/1/2025**, before the first disposition or transfer on or after
that date. One-time and irreversible.

- **TY2024 and earlier**: universal tracking was permissible. **Do not apply the
  wallet rule retroactively.**
- **TY2025 forward**: ask whether the allocation was made. Most were not. If not,
  document the method actually used and state the difference — reconstructing a
  compliant allocation afterward is not the same thing.

⚠ **Identification differs by custody, and the IRS relieved the harder rule for
both 2025 and 2026:**

- **Unhosted wallets** — identify at or before the transaction, adequate records;
  otherwise FIFO within the wallet.
- **Broker-custodied** — Reg §1.1012-1(j)(3)(ii) requires identification
  **communicated to the broker**; the taxpayer's own books are not enough and
  FIFO applies by default. **But Notice 2025-7 permits books-and-records
  identification** (identifier or recorded standing order) for dispositions
  1/1/2025–12/31/2025, applied consistently, with FIFO/LIFO/HIFO all permitted;
  **Notice 2026-20 extends it through 12/31/2026** and adds that where such an
  identification was made **those units control regardless of what the broker
  reports**. Relief covers broker-custodied units only, and a taxpayer relying on
  Rev. Proc. 2024-28 may use it only after satisfying that procedure.
- ⚠ The relief runs **through 12/31/2026**. Nothing extends it beyond that, so
  plan for the communicate-to-the-broker requirement in TY2027 unless further
  guidance issues.

SSOT: `accounts/<wallet-or-exchange-slug>/lot-basis.md`, **per account** — a
single global file would itself be non-compliant (`1040.md` §5).

## 3. Broker reporting

| Tax year | What exists |
|---|---|
| 2023, 2024 | ⚠ **No Form 1099-DA.** Do not treat its absence as evidence of no activity |
| 2025 | **Gross proceeds** for custodial brokers |
| 2026 | **Basis** added — ⚠ but only for assets acquired **in a custodial account on or after 1/1/2026**, so TY2026 forms carry basis for almost nothing |

Expect Form 8949 **Box C / Box F** (noncovered) for TY2025 and most of TY2026.

⚠ The **DeFi front-end broker regulations (TD 10021) were repealed** by
**H.J. Res. 25, signed April 10, 2025** under the CRA — and under 5 U.S.C.
§801(b)(2) Treasury may not issue a **substantially similar** rule without new
legislation, which is what makes the answer durable. Those regulations would not
have applied until 2027 sales anyway, so the repeal changed nothing for
TY2025–2026.

Transition guidance: **Notice 2024-56** (broker penalty relief for 2025),
**Notice 2024-57** (six unreported classes), **Notice 2025-33** (backup
withholding through 2026, graduated for 2027).

⚠ **Other information returns to reconcile:** exchanges have issued **1099-MISC**
for reward income and **1099-K** under §6050W throughout the window. 1099-MISC
amounts feed §4 and **become basis**; **1099-K gross amounts are not gain**. The
1099-K threshold moved repeatedly and OBBBA restored $20,000/200 retroactively —
verify the governing threshold before treating a missing form as evidence.

Reconcile a 1099-DA the same way as a 1099-B — explained differences, not a
forced tie (`capital-gains.md` §1). Expect absent basis on transferred-in assets.

## 4. Income events

| Event | Treatment |
|---|---|
| **Staking** | Ordinary at FMV on **dominion and control**; that FMV becomes basis (Rev. Rul. 2023-14). ⚠ Under active challenge on a created-property theory (*Jarrett II*) — an operating position, not a settled holding |
| **Mining** | Ordinary at receipt; **SE tax if a trade or business**, with rig depreciation (Notice 2014-21, as modified by Notice 2023-34) |
| **Hard fork, no units received** | ⚠ **No gross income** — Situation 1 of Rev. Rul. 2019-24, and the more commonly applicable holding |
| **Hard fork with airdrop of units** | Ordinary at FMV on dominion and control — which the taxpayer does **not** have where the exchange does not support the coin |
| Unsolicited promotional airdrop | Commonly treated as ordinary income on the same reasoning, but the ruling addresses **hard forks**; this is analogy, not holding |
| Payment for services | Wages or SE income at FMV |

⚠ **Every income event creates a lot with basis equal to the amount included.**
Failing to record it taxes the same amount twice on sale — the crypto analogue of
a missing Form 8606.

## 5. Wash sales — inapplicable, with three qualifications

⚠ **§1091 reaches "stock or securities." Digital assets are property, so the rule
does not currently reach them** — and **no legislation extending it has been
enacted**; OBBBA did not include one. State that affirmatively, then qualify:

1. ⚠ **It does reach crypto exposure held in securities form.** A spot bitcoin or
   ether **ETP** and crypto-related equities are securities, so §1091 applies in
   full. Harvesting an ETP loss and rebuying it is a wash sale. (Whether a
   competitor ETP is "substantially identical" is unresolved.) Same for tokenized
   securities.
2. ⚠ **§1092 straddles may still apply** — §1092(d)(1) defines personal property
   as any **actively traded** personal property, not only securities. Actively
   traded digital assets are within its literal reach, which would defer a
   harvested loss against unrealized gain in an offsetting position. This is the
   principal technical objection to aggressive harvesting.
3. ⚠ **§267(a)(1)** disallows a loss on a sale of **property** to a related
   person — permanently. A harvest sold to a controlled LLC, family member, or
   related trust is disallowed regardless of §1091.

Verify the legislative position for the target year rather than carrying it
forward.

## 6. NFTs

⚠ **Notice 2023-27 is interim guidance** announcing intended future guidance and
an interim **look-through**: an NFT whose associated right or asset is a
collectible under §408(m) is treated as a collectible. Two consequences:

- **Rate** — a **maximum** 28% applies to **long-term** collectible gain
  (§1(h)(4)/(5)); short-term is ordinary, and a taxpayer below 28% pays their
  ordinary rate.
- ⚠ **In an IRA — the larger trap.** **§408(m)(1) treats an IRA's acquisition of
  a collectible as a deemed distribution** of the amount used, plus §72(t) under
  59½, independent of any prohibited-transaction exposure.
  → `scenarios/self-directed-ira.md`.

Creator-side sales are ordinary; self-created art is not a capital asset
(§1221(a)(3)); secondary royalties are ordinary.

## 7. Losses — read the §67(h) gate first

⚠ **The structural point, stated precisely:** §67(b)(3) excepts from the
miscellaneous-itemized bucket only losses **described in §165(c)(2) or (3) that
are casualty or theft losses**. A **theft** loss qualifies. An **abandonment or
worthlessness** loss is a §165(c)(2) loss that is *neither a casualty nor a
theft*, so it stays in the bucket and is disallowed under §67(h). That is why
theft survives and abandonment does not, even though both arise under §165(c)(2).

- ⚠ **Worthlessness / abandonment is generally NOT deductible by an individual.**
  **CCA 202302011** holds that even where a taxpayer abandons, an individual's
  §165(c)(2) loss on an investment asset is a **miscellaneous itemized
  deduction**, disallowed by former §67(g) — which **OBBBA made permanent and
  redesignated §67(h)** (new §67(g) is now the educator-expense rule, so a
  "§67(g)" cite for TY2026 points at the wrong subsection). **For an individual holding for investment there is no
  deductible worthless-crypto loss outside a sale or exchange.** (CCA 202302011's
  facts are an individual investment holding; it does not displace a
  §165(c)(1) trade-or-business analysis where one genuinely applies.) The route to a
  usable loss is a bona fide sale — including for nominal consideration to an
  **unrelated** party.
- ⚠ **§165(g) does not apply** — digital assets are not securities under
  §165(g)(2), so the deemed-sale rule in `capital-gains.md` §5 is unavailable.
  Do not carry it over.
- **Exchange bankruptcies** — the loss is generally not fixed until the claim
  resolves; recovery may be partly return of capital.
- ⚠ **Theft and scam losses — the path that survives.** §165(h)(5) limits
  personal casualty and theft losses to declared disasters (OBBBA made the
  limitation permanent and, for years beginning after 12/31/2025, **added
  State-declared disasters**), so a personal scam loss is barred but a
  **profit-motivated** §165(c)(2) loss is not. **CCA 202511015** runs five scam
  patterns — compromised-account, pig-butchering, and unauthorized-transfer
  victims have deductible §165(c)(2) theft losses; romance-scam and ransom
  victims are barred. It is **Chief Counsel Advice — nonprecedential and not
  citable as precedent** — but it is the clearest statement of the Service's
  analysis, and the gates it applies (a completed theft under state law, profit
  motive, no reasonable prospect of recovery, limited to **basis**) are what
  control. Mechanics: **Form 4684 Section B**, in the year the loss becomes
  unrecoverable, as an other itemized deduction not subject to the 2% limitation.
- Rev. Proc. 2009-20 Ponzi safe harbor may apply to some patterns.

## 8. Reporting, foreign, and retirement interactions

- ⚠ **FBAR** — an account holding **only** digital assets is not currently
  reportable, though FinCEN has announced an intent to change this. Verify
  annually. A **mixed** account is reportable at the **full account value**.
- **Form 8938** — may reach digital assets held through a foreign institution;
  ⚠ **directly self-custodied assets are not** specified foreign financial
  assets. → `foreign.md`.
- **§6050I** — the >$10,000 digital-asset cash-reporting extension remains
  **deferred** pending regulations (Announcement 2024-4); no regulations have
  issued. **§6045A** transfer statements apply to transfers on or after 1/1/2026.
- **NIIT** — staking and lending yield are net investment income; mining as a
  trade or business is SE income and **not** NII.
- **No withholding** on digital-asset income ⇒ estimated-tax exposure
  (`withholding-penalties.md`).
- ⚠ **Charitable** — a **qualified appraisal is required above $5,000 with no
  exception for exchange-traded crypto** (CCA 202302012, which **rejected
  reasonable cause**); the §170(f)(11)(A)(ii)(I) exception covers publicly traded
  *securities*, which these are not. Form 8283 Section B needs appraiser **and**
  donee signatures. Held ≤1 year is limited to **basis** (§170(e)(1)(A)).
  → `itemized.md`.
- **Gift and inheritance** — §1015 dual basis is harsher here because donors
  rarely have records; §1014 step-up needs a defensible valuation. Absent
  records the IRS position is **zero basis**.
- **§988 does not apply** — not currency, so no ordinary FX treatment.
- **SDIRA** — holding keys personally for an IRA-owned asset is serious §4975
  exposure. → `scenarios/self-directed-ira.md`.
- **State** — a state capital-gains excise that exempts real estate does **not**
  exempt digital assets. → `state-residency.md`.

## 9. Records

Reconstruct from exchange exports, then on-chain history, then tracker output.
⚠ **Tracker output is a derived work product, not evidence** — record its method
(universal vs. per-wallet, transfer handling, FMV source), because two trackers
produce different answers from the same chain data. **Self-transfers are the main
error source**: a tracker that does not recognize one invents a disposition.

## 10. Workpaper

`wp-digital-assets.md`:

```json
{
  "page1_question_answer": null,
  "basis_method": {"regime": "pre_2025_universal | post_2025_per_wallet",
                   "rev_proc_2024_28_allocation_made": null,
                   "notice_2025_7_or_2026_20_relied_on": null,
                   "identification_method": "FIFO|LIFO|HIFO|specific",
                   "documentation": ""},
  "wallets": [{"slug": "", "custodial": null, "form_1099da_received": null,
               "proceeds_reported": 0, "basis_reported": 0,
               "_basis_ssot": "accounts/<slug>/lot-basis.md"}],
  "dispositions": {"count": 0, "proceeds": 0, "basis": 0, "short_term": 0,
                   "long_term": 0, "collectibles_28pct": 0,
                   "form_8949_box": "C|F|A|D"},
  "income_events": [{"type": "staking|mining|airdrop|fork|services",
                     "date": "", "fmv_at_receipt": 0, "becomes_basis": 0,
                     "se_tax_applicable": null, "form_1099misc_received": null}],
  "losses": {"worthlessness_barred_67h": null, "theft_165c2": 0,
             "state_law_theft": null, "profit_motive": null,
             "no_reasonable_prospect_of_recovery": null, "support": ""},
  "open_positions_no_guidance": [{"activity": "", "position_taken": "",
                                  "rationale": "", "notice_2024_57_class": null}]
}
```

**Invariants:** every income event creates a lot whose basis equals the amount
included; self-transfers are not dispositions; the basis regime and any
identification relief match the **target year**; crypto-to-crypto swaps are
counted as dispositions; the page-1 answer is consistent with the activity
reported; a >$5,000 charitable donation has a qualified appraisal; an abandonment
loss is not deducted.

Verify with a licensed practitioner before filing.

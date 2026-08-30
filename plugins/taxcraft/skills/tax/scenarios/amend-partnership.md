# Amending a Partnership Return (1065) + Cascading to Partners

Invoke when a filed Form 1065 is defective — wrong numbers, missing K-1s, wrong allocations, mis-classified items, capital-account drift. Governs the corrective filing and the downstream 1040-X for each partner.

Two regimes, two paths. **Always determine the regime first** — wrong path = rejected filing.

## Regime test (check Form 1065 page 3 of the year being corrected)

| Box status | Regime | Amendment path |
|---|---|---|
| §6221(b) opt-out **elected** (box checked) | Pre-BBA / TEFRA-style | Form **1065-X** + **amended K-1s (mark "Amended")** + partner 1040-Xs |
| No opt-out (default) | **BBA** (post-2017) | **AAR** — Form 8082 on an AAR-marked 1065 (e-file) or on Form 1065-X (paper) + Forms **8986** to partners + partners file Form **8978** on current-year 1040 (or partnership-level imputed underpayment election) |

Opt-out eligibility (§6221(b)): ≤100 partners, every partner is an "eligible partner" — individual, C-corp, S-corp, decedent's estate, certain foreign entities. **Disqualifies**: partnership partners, disregarded SMLLCs as partners, trusts (even grantor trusts). Opt-out is annual; each year is independent.

Superseding return (filed before the extended due date) is a third, cleaner option — treat as original, no amendment mechanics.

## BBA path (the default, most partnerships)

⚠ **One rule, two vehicles.** A BBA correction is an **AAR**. E-file: an
AAR-marked **Form 1065** with **Form 8082**. Paper (a partnership not required to
e-file): **Form 1065-X** with Form 8082. **1065-X is not reserved to opt-out
partnerships** — it is the paper vehicle for the same AAR. The AAR filing window
is **§6227(c)**; §6235 governs the assessment period.

A BBA-regime return is corrected by an **Administrative Adjustment Request**, not
by an ordinary amended return and never by a "revised" K-1. The **form the AAR
rides on depends on the filing channel**:

- **E-file path** — an AAR-marked **Form 1065** with **Form 8082** attached.
- **Paper path** — **Form 1065-X** with Form 8082, for a partnership not required
  to e-file (below the aggregate-return e-file threshold).

So 1065-X is not off-limits to a BBA partnership; it is the paper vehicle for the
same AAR. What is wrong is treating a BBA correction as an ordinary amended
return with revised K-1s.

Two sub-paths at partnership level:

1. **Push-out election** (§6226) — partnership computes adjustments, issues Forms **8986** to each reviewed-year partner, each partner picks up the adjustment on their **current-year** 1040 via Form **8978** (not an amended 1040 for the reviewed year). Interest runs from reviewed-year original due date at the §6621 rate + 2%. Most common for small partnerships with individual partners.

2. **Imputed underpayment at partnership level** — partnership pays tax at the highest individual rate on the net positive adjustment; partners don't refile. Modifications allowed (§6225(c)) to reduce IU: partner amended returns, tax-exempt partners, rate modifications. Usually worse than push-out for partnerships whose partners are in sub-top brackets or where adjustments include favorable items (push-out lets partners claim refunds; IU doesn't).

Timing: AAR must be filed within **3 years** of the later of (a) the return's filing date or (b) the return's original due date (ignoring extensions). §6227(c). AAR cannot be filed after IRS issues a Notice of Administrative Proceeding for that year.

Net **negative** adjustments (refund situation) — IU path produces no refund to partnership. Push-out lets partners claim refund on their current-year 1040 via Form 8978 (favorable items flow through). Push-out is almost always correct when the adjustment is a refund.

## Opt-out path (1065-X)

Mechanics identical to the pre-2018 world:
- File Form 1065-X (or paper 1065 marked "Amended Return" — 1065-X is the e-fileable wrapper).
- Issue **Amended Schedule K-1** to each partner (check "Amended K-1" box).
- Each partner files **Form 1040-X** for the reviewed year within their §6511 refund SOL (3 years from filing / 2 years from tax paid, whichever later).
- Partner must attach the amended K-1 to the 1040-X.

No push-out, no Forms 8986/8978. Cleaner for partners, administratively heavier for the partnership (K-1 reissuance to every partner every time).

## Cascade to partners (joint 1040-X under WA community property)

For MFJ filers in a community-property state (WA): K-1 income flows to the joint return; 1040-X is one filing per couple, not one per spouse. Allocation between spouses matters only for:
- Separate-property characterization (pre-marital / gift / inheritance — rare)
- Injured-spouse allocation (Form 8379) if one spouse has separate federal debt
- State returns in states that tax separately (not WA — no personal income tax)

Form 8978 Schedule A reports each adjustment line per character (ordinary, LTCG, QBI, etc.); interest computed per Schedule. Pay any balance with 1040-V. NIIT (§1411) and Additional Medicare (§3101(b)(2)) recomputed on the adjusted AGI / SE income.

## §6511 SOL for partner refunds (watch this)

Partners' refund SOL runs independently of the partnership's AAR SOL. A partner's window to claim refund on an amended return:
- 3 years from 1040 filing date (or extended due date if unfiled), or
- 2 years from date tax was paid,
whichever is **later**.

BBA push-out extends the partner's window for adjustments flowing from an AAR (§6511(g)) — the 1040 refund SOL is tolled while partnership is in the adjustment period. Don't assume the 3-year clock started when the original 1040 was filed.

## §6231 / §6227(c) nuances

- IRS can issue NAP (Notice of Administrative Proceeding) up to 3 years post-filing (longer for substantial omission or fraud). AAR window closes once NAP issues.
- FPA (Final Partnership Adjustment) has its own petition window (90 days, Tax Court).
- These bite on examinations — for a voluntary self-correction AAR with no IRS contact, the §6227(c) 3-year filing window is the only clock that matters.

## What to produce (workpaper + filing package)

At `entities/<slug>/tax/FY<YYYY>/amended/`:

- `0-decision-memo.md` — regime determination, path chosen, authority, dollar impact
- `1-form-8082-AAR.pdf` (BBA) OR `1-form-1065-x.pdf` (opt-out)
- `2-partner-forms-8986/` (BBA push-out, one per partner) OR `2-amended-k1s/` (opt-out)
- `3-partner-1040x-packages/` — one folder per partner, each containing:
  - Draft 1040-X
  - Form 8978 + Schedule A (BBA) OR amended K-1 (opt-out)
  - Interest/penalty recompute worksheet
  - Cover letter to partner
- `4-transmittal.md` — filing checklist, signatures needed, mail vs. e-file, tracking

## Traps

- **Amending a BBA return with 1065-X**: IRS rejects or ignores it. Not a cure.
- **Push-out without tracking downstream**: partnership must furnish 8986s by the due date of the AAR year; partner who never received 8986 can't file 8978; becomes partnership liability.
- **Capital-account restatement without P&L change**: pure M-2 fix can often be done by disclosure in current-year Schedule M-2 with explanatory footnote; doesn't always require AAR unless it flows into a partner's basis/gain/loss event for an open year.
- **Missing §199A Statement A**: if original K-1 omitted Statement A, partners likely lost 20% deduction. Quantify; almost always worth amending.
- **Self-employment box 14 fix**: a BBA AAR adjustment to box 14a (SE earnings) flows to partner via 8978; partner recomputes SE tax and half-SE deduction. Include in the interest/penalty worksheet.
- **Character change, $0 bottom line**: still amend. LTCG→ordinary shifts partner's tax even at same total income. And §199A, NIIT, and QBI limits all depend on character.
- **Partnership files AAR, then IRS audits the reviewed year anyway**: the AAR adjustments are folded into the exam; taxpayer can't "lock in" favorable treatment by self-amending.

## Never without CPA review

AAR and 1065-X filings create formal records that are used against the partnership in future examinations. End every package with: *"Review with a CPA/EA or tax attorney before filing. Partnership Representative must sign the AAR — no one else has authority (§6223)."*

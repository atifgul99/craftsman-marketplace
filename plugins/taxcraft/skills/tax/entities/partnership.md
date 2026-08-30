
# Partnership (Form 1065) Sub-Skill

For multi-member LLCs taxed as partnership, general/limited partnerships, and LLPs. Output feeds each partner's K-1.

## Preflight (beyond common)

1. **Qualified Joint Venture check** — MFJ spouses in a community-property state (AZ, CA, ID, LA, NV, NM, TX, WA, WI) can elect QJV under Rev. Proc. 2002-69 (two Schedule Cs) instead of filing 1065. Evaluate admin-cost tradeoff. If both spouses work in the business and live in a community-property state, surface this option.
2. **§761(a) election** — investment partnerships with no active business can elect out of Subchapter K. Rare; flag only if clearly passive co-ownership.
3. **Partnership Representative (PR)** — required post-BBA (Bipartisan Budget Act of 2015); appointed on Form 1065 page 3. Confirm designation.
4. **PTET election status** — many states allow pass-through entity tax elections as a SALT-cap workaround. Confirm whether entity elected; affects estimated payments + partner K-1 box 15 credit.

## 1065 Flow

1. **Schedule K** — aggregate separately-stated items (ordinary, rental, interest, dividends, capital gains, §1231, §179, charitable, foreign, AMT items, §199A info).
2. **Allocate to partners via Schedule K-1**:
   - Respect §704(b) substantial economic effect (safe harbor: capital account maintenance per Reg §1.704-1(b)(2)(iv) + liquidation per capital accounts + DRO or QIO)
   - §704(c) built-in gain/loss on contributed property — traditional, curative, or remedial method; stick with the method chosen at contribution
   - Guaranteed payments under §707(c) — separately stated; deductible above the line; SE income to recipient
   - Targeted allocations — common in deal partnerships; model distributions to match economics
3. **Capital account rollforward** — **tax basis method** (required for most since 2020):
   - Beginning + Contributions + Net income (tax basis) − Distributions = Ending
   - Reconcile to §704(b) book basis separately if they differ
   - Instantiate `entities/<slug>/books/capital-accounts.md` from `templates/capital-accounts.md.template` at first close
4. **Outside basis tracking** (per partner, not on return but critical for loss deduction)
   - Basis = contributions + income allocated + share of liabilities − distributions − losses allocated
   - **§752 allocations**: recourse debt → per economic risk of loss; nonrecourse → per profit-sharing + §704(c) minimum gain
   - **§465 at-risk**: separately from basis; nonrecourse debt generally not at-risk unless qualified nonrecourse (QNR — real estate, from qualified persons)
   - **§469 passive**: separately tracked per activity
5. **§754 election** — optional; once made, applies to future transfers:
   - §743(b) step-up/down on partnership-interest transfer (death, sale)
   - §734(b) adjustment on distributions causing inside/outside disparity
   - Mandatory adjustment if substantial built-in loss (>$250k) or substantial basis reduction
6. **Schedule M-1 / M-3** — book-tax reconciliation. M-3 required if $10M+ assets. Instantiate `annual/m-1-reconciliation.md` from `templates/m-1-reconciliation.md.template`.
7. **Schedule L** — balance sheet (required if > $250k assets OR receipts; always recommend).
8. **Schedule B-1 / B-2** — ownership disclosures (>50% owners; entities owning >50%).
9. **K-2 / K-3** — international items. Required for most partnerships unless domestic-filing exception is met (notify partners by 1 month before filing deadline; no partner requests K-3; no foreign activity; specific partner-type limits). Default to **filing** unless exception clearly applies.

## Common Issues Checklist

- [ ] Guaranteed payments correctly classified (box 4a/4b)
- [ ] Box 14 self-employment income computed correctly (general partners + LLC managers usually SE; limited partners generally not under §1402(a)(13), subject to recent cases — *Soroban*, *Denham Capital* — tightening this)
- [ ] Box 20 code Z §199A detail complete: QBI, W-2 wages, UBIA per trade or business
- [ ] Box 20 code N business interest expense (for §163(j) at partner level)
- [ ] State apportionment sheet per state with nexus
- [ ] Composite return / PTE election properly reflected
- [ ] Final K-1 mark if partner left
- [ ] §754 step-up reflected in depreciation if transfer occurred
- [ ] Disregarded SMLLCs consolidated into the partnership's books (their activity is partnership activity; their own W-9 might show SMLLC name but EIN is partnership's)
- [ ] Recourse vs nonrecourse liability allocation on K-1 item K correct
- [ ] **UPE (unreimbursed partner expenses)** — home office, mileage, cell claimed by a partner on Schedule E page 2 as a separate "UPE" line are deductible **only if the partnership agreement or an established practice requires the partner to bear them without reimbursement**. If the agreement is silent **and no established practice exists**, or reimbursement was available and simply not sought, the deduction is **denied** (*Klein v. Comm'r*, 25 T.C. 1045 (1956); *McLauchlan v. Comm'r*, T.C. Memo. 2011-289, aff'd 558 F. App'x 374 (5th Cir. 2014)). Fix the agreement or adopt a partnership expense-reimbursement policy; do not label a partner an employee under Reg §1.62-2. UPE also reduces SE income. See `scenarios/accountable-plan.md` for the worker-capacity gate and `scenarios/home-office-280a.md` for qualification and computation.

## Basis Workpaper Template (per partner, per year)

```json
{
  "owner": "<name>",
  "entity": "<entity>",
  "tax_year": 2025,
  "outside_basis": {
    "beginning": 0,
    "contributions_cash": 0,
    "contributions_property_fmv": 0,
    "contributions_property_basis": 0,
    "share_income_ordinary": 0,
    "share_income_separately_stated": 0,
    "share_liabilities_beginning": 0,
    "share_liabilities_ending": 0,
    "distributions_cash": 0,
    "distributions_property_basis": 0,
    "share_losses": 0,
    "ending": 0
  },
  "at_risk_465": 0,
  "passive_suspended_469": 0,
  "§199A_component": {
    "qbi": 0,
    "w2_wages": 0,
    "ubia": 0,
    "sstb_flag": false
  },
  "§704c_built_in_gain": 0
}
```

Save per partner: `entities/<slug>/tax/FY<YYYY>/annual/workpapers/basis-<partner-slug>.json`

## Nested Disregarded SMLLCs

If this partnership owns a disregarded SMLLC:

- SMLLC activity lives in `entities/<partnership-slug>/disregarded/<smllc-slug>/books/`
- Consolidate into the partnership's P&L as a division; no separate 1065 for the SMLLC
- On K-1s the partnership issues upstream, the SMLLC is invisible — partners see their pro-rata share of consolidated activity
- On K-1s the SMLLC receives from its own LP positions, the K-1 shows the SMLLC's name but the **regarded owner** (the partnership) is the tax partner — see `entities/disregarded.md` for the W-9 and K-1 labeling rules

## Deadlines & Penalties

- **Form 1065 due**: 2½ months after FY end (March 15 for calendar-year). Extension via Form 7004 → 6-month extension (September 15 for calendar).
- **§6698 failure-to-file penalty**: a per-partner, per-month amount for up to 12 months — indexed, so verify the rate for the target year through `authority.md` rather than carrying a prior year's figure. Small-partnership relief under Rev. Proc. 84-35 is available if ≤ 10 partners, each reporting their full distributive share on a timely individual return — but IRS has tightened enforcement; do not rely on it as a planning position. See `scenarios/penalty-abatement.md` for Rev. Proc. 84-35 mechanics and the full penalty-abatement decision tree — that file is the canonical home for penalty abatement procedures.
- **K-1 delivery to partners**: by the partnership's extended due date. Late K-1s are the #1 partner complaint — flag early.

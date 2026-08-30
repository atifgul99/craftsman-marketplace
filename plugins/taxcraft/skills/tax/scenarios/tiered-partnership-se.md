# Tiered Partnership SE Analysis

Invoke when a partnership holds a **general-partner interest** in another partnership — i.e., an upstream K-1 reports SE earnings (box 14a) to a regarded partnership or LLC. The question: how does that SE income flow to the human partners, and who owes SE tax?

This is a distinct fact pattern from the usual one — most partnership-scenario literature covers individual partners in an operating business. The tiered fact pattern (Fund-of-Fund-of-partners) is mechanically different.

## The flow, stripped down

1. **Lower-tier partnership** — call it L. L issues a K-1 to the **upper-tier partnership** U showing box 14a SE earnings.
2. **U's 1065** picks up L's K-1. U itself has no active trade or business — it's a holding vehicle. The SE character of the income must pass through because §1402 looks through U to the underlying activity (Treas. Reg. §1.1402(a)-2).
3. **U's K-1s to its partners** (individuals, for our purposes) report box 14a SE earnings allocable to each partner based on U's allocation terms.
4. **Individual partner** computes SE tax on Schedule SE of 1040 using the K-1 box 14a number.

"Lookthrough" means: the SE character is determined at the level where the trade or business is conducted (L), not at U. U's own form (partnership / LLC taxed as partnership) doesn't change the character.

## Whether the SE income is actually SE income

§1402(a)(13) excludes a **limited partner's distributive share** from SE income (other than guaranteed payments). Two active fronts:

### The LLC-member question (unsettled before *Soroban*)

For an LLC taxed as partnership, no member is "limited" in the §1402(a)(13) sense as a matter of state law — LLC members are members, not partners. IRS has long argued LLC members who are materially participating managers are NOT limited and owe SE tax; taxpayers argued "functional limited partner" status based on lack of management rights + passive capital.

*Soroban Capital Partners LP v. Commissioner*, 161 T.C. No. 12 (2023) — Tax Court adopted a **functional test**. Being labeled "limited partner" is not dispositive; what the partner actually does determines §1402(a)(13). Active participants owe SE tax even if the partnership agreement calls them limited. *Denham Capital* (2024) reinforced.

Effect for tiered structures: whether the individual at the top of the tier owes SE tax on her distributive share depends on her actual activity relative to the underlying trade or business L conducts. Passive capital → likely limited partner treatment → no SE tax. Active management role (in L, through U) → SE tax applies.

### Guaranteed payments

§707(c) guaranteed payments are always SE income (§1402(a), including for limited partners via the (a)(13) exception itself). If L pays U a guaranteed payment and U passes it to its members, it stays SE — even if the individual partner is otherwise "limited."

## The workpaper

Build at `entities/<upper-tier-slug>/tax/FY<YYYY>/annual/workpapers/se-tier-analysis.md`:

1. **Identify each upstream GP K-1** received by U. Note issuer L, box 14a dollars, any guaranteed payments in box 4a, self-employment characterization on L's agreement.
2. **Characterize U's allocation** — is U allocating the SE item to its partners based on the same ratio as other income? Special allocations for SE-bearing income are allowed with substantial economic effect but rare.
3. **Per-individual-partner analysis**:
   - What is this partner's role vis-à-vis L? Director? Silent capital? Decision-maker?
   - Apply *Soroban* functional test. Document conclusion.
   - Compute expected SE earnings flowing through to their K-1 box 14a.
4. **Issue-side K-1 box 14a** — populate based on the analysis above.
5. **Partner 1040 Schedule SE** — the individual picks up box 14a as SE income, subtracts half-SE deduction (§164(f)), pays 15.3% up to SS wage base + 2.9% thereafter + 0.9% additional Medicare above threshold.

## The recurring fact pattern

An upper-tier partnership holds a **GP interest** in a lower-tier fund (often the exception in a portfolio of otherwise-LP positions). If the fund's K-1 to the upper-tier partnership shows SE earnings in box 14a:

- **The upper-tier partnership must pass box 14a through** to its own partners on their K-1s.
- **Character remains SE** because §1402 looks through the upper tier to the lower-tier trade or business.
- **Whether the individual partners actually owe SE tax** depends on their role. Passive capital investors with no active management of the lower-tier business may claim the §1402(a)(13) limited-partner exclusion — but *Soroban* means this turns on functions actually performed, not on the label in the operating agreement.
- If prior-year 1065s missed this — original returns dropped the box 14a pass-through — correcting is both a 1065 fix (amend to populate box 14a) and a partner 1040 fix (add Schedule SE). Work through `amend-partnership.md`.

## Traps

- **Silent box 14a omission**: upstream L correctly reports box 14a; U's tax software doesn't pick it up when translating K-1 input to U's Sch K line 14a because U has no "own" SE income. Manual override required. Easy to miss in TurboTax Business.
- **Guaranteed payments re-labeled**: some upstream partnerships pay their manager entities guaranteed payments called "management fees." If the K-1 labels it box 4a (guaranteed payments), it's SE regardless of partner status — bulletproof.
- **Partnership holding a GP is different from "partnership as GP"**: if U itself serves as GP of L (not just holds a GP interest), U has its own active trade or business and its entire operation may be SE-tainted for its members. Confirm the contractual structure.
- **NII/NIIT interaction**: SE income is generally NOT subject to §1411 NIIT (mutually exclusive). But passive investment income flowing through is NIIT-eligible. Character matters twice.
- **State SE tax equivalents**: WA has no SE tax equivalent. CA has no SE; NYC has UBT that mimics. Multi-state partners with SE income need separate analysis.

## Don't conclude without

- Reading the L-level partnership agreement (defines U's role — GP / LP / LLC-manager-member)
- Reading U's own partnership agreement (defines each individual's role relative to U)
- Documentation of individual partner's actual activity (emails, board minutes, contracts) — *Soroban* requires facts
- Authority chain: §1402(a), §1402(a)(13), Treas. Reg. §1.1402(a)-2, *Soroban*, *Denham Capital*, Chief Counsel Memoranda as they update

This is a live area of law. Flag to CPA/tax attorney for any material SE exposure; don't finalize without sign-off.

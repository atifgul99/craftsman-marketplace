
# §1244 Small Business Stock (Ordinary Loss) Scenario

Trigger: a closely-held corporation's stock is being issued, has lost value, has become worthless, or is being sold at a loss; the user asks about deducting a loss on founder/investor stock; or equity-issuance planning is happening at any early-stage C-corp or S-corp (paper §1244 at the same time as §1202 — they are complements, not alternatives).

This is the canonical home for §1244 content. `entities/c-corp.md`, `entities/s-corp.md`, `scenarios/qsbs-1202.md`, `strategy.md`, and `governance.md` cross-reference here rather than repeating the rules. For any proposed, historical, or remedial issuance, load `scenarios/stock-issuance.md` first; it owns the closing sequence and tranche record.

## What §1244 gives

A loss on **§1244 stock** (sale, exchange, or worthlessness under §165(g)) is **ordinary loss** instead of capital loss, up to **$50,000 per tax year ($100,000 MFJ)** — §1244(b). Excess over the annual cap remains capital loss. The ordinary portion:

- Deducts against ordinary income at full marginal rates — no $3,000/yr capital-loss trickle.
- Is treated as a loss from the taxpayer's trade or business for NOL purposes (§1244(d)(3)), so it can create or enlarge an NOL.
- Is reported on **Form 4797 Part II** (not Schedule D); the excess capital portion goes to Form 8949/Schedule D.

**§1202 may pay off if the company succeeds; §1244 may pay off if it fails.** Section 1244 requires a valid contemporaneous stock issuance for actual money/property plus competent records; documentation cannot create a transaction that did not occur. The loss-date gross-receipts test and holder continuity also remain open after issuance. For relevant early-stage stock, record separate provisional §1202 and §1244 positions — see `scenarios/stock-issuance.md`.

## Qualification checklist (all prongs required)

1. **Domestic corporation — “small business corporation”** (§1244(c)(3)): aggregate capital receipts include money plus the corporation's adjusted basis in property received for stock, as contributions to capital, and as paid-in surplus, reduced by liabilities assumed/taken subject to under Reg. §1.1244(c)-2. The running total is not reduced by later distributions. Stock issued before the transitional year may qualify without designation. The first tax year in which capital receipts exceed $1,000,000 **and** stock is issued is the transitional year; only the remaining pool (`$1,000,000 − capital receipts from prior tax years`) is available to designated transitional-year shares or the default proportional allocation. Stock issued after the transitional year does not qualify. C-corps and S-corps can qualify.
2. **Actual stock** — common or preferred (preferred only if issued after 7/18/1984). Options, warrants, convertible notes/SAFEs (until converted), and securities do not qualify; the conversion-date issuance is tested on its own facts.
3. **Issued for money or other property** — not for stock or securities, and **not for services**. Stock issued in cancellation of corporate debt qualifies as issued for property unless the debt is evidenced by a security or arose from the performance of services.
4. **Original issuance to an individual or a partnership** — and only the **original holder** ever gets §1244 treatment. Status dies on transfer: gift, inheritance, purchase from another shareholder, or contribution of the stock to another entity all forfeit it. Through a partnership (including an LLC taxed as a partnership): the loss passes through, but only to individuals who were partners **both when the partnership acquired the stock and continuously until the loss** (Reg §1.1244(a)-1(b)(2)). An S-corp shareholder cannot claim §1244 on stock the S-corp holds — the pass-through door is partnership-only. Corporations, trusts, and estates can never claim it.
5. **Gross-receipts test** (§1244(c)(1)(C)): for the 5 most recent tax years before the loss year (or the corporation's whole life if shorter), **less than 50%** of aggregate gross receipts may come from royalties, rents, dividends, interest, annuities, and gains from sales/exchanges of stock or securities. **The (c)(2)(C) exception is a numerical test, not a business-failure narrative** — do not describe it as a carve-out for companies that failed. Under §1244(c)(2)(C) the gross-receipts test is waived entirely if the corporation's deductions (other than NOL and dividends-received deductions) exceeded its gross income over that period. Net effect: operating startups virtually always pass; holding/investment companies fail.

## Basis traps — where §1244 silently leaks

- **Cash in without shares out = no §1244 on that later basis.** A capital contribution that increases basis in existing stock **without a new stock issuance** is not §1244 property: on a loss, basis must be apportioned and the contribution-attributable portion is capital, not ordinary (Reg. §1.1244(d)-2). If §1244 treatment is intended, prospective money/property needs a contemporaneous, valid new issuance routed through `stock-issuance.md`; debt or a deliberate bare contribution may still be chosen for other reasons. Historical cash already booked as APIC is a `COUNSEL HOLD`: never backdate or assert that shares were exchanged for it without written tax-counsel analysis of the real facts.
- **Built-in-loss property**: if contributed property's adjusted basis exceeded its FMV at contribution, basis is stepped down to that FMV for measuring the §1244 ordinary loss (§1244(d)(1)) — you cannot import a pre-existing loss into ordinary treatment.
- **Shareholder loans are not stock.** A worthless shareholder loan is a §166 bad debt — for a non-corporate lender typically a **nonbusiness bad debt = short-term capital loss**, the worst character available. When funding a struggling company, weigh loan vs. stock issuance with this endgame in mind, and paper whichever is chosen (note with terms and interest vs. resolution and certificate).

## LLC taxed as C-corp — flag the uncertainty

§1244 requires “stock.” An LLC that elects C status is a corporation federally (Reg. §301.7701-3), but there is **no direct authority** confirming §1244 treatment for its membership units. A certificate does not cure the entity-law uncertainty. Route any LLC-unit question through `stock-issuance.md`, maintain the legally correct unit records, and report `UNVERIFIED — TAX-COUNSEL REVIEW` unless controlling authority supports the position. The conservative structure for a new transaction is an actual corporation with actual shares; do not convert an existing entity solely from this workpaper.

## Loss events and timing

- **Sale or exchange** — must be to an unrelated party; §267 disallows losses on sales to related parties (family, controlled entities).
- **Worthlessness** (§165(g)) — deemed sold on the **last day of the tax year in which the stock becomes wholly worthless**. Identifying the right year is a facts question (cessation of business, liquidation, no reasonable hope of value); getting it wrong forfeits the deduction to the wrong year. Safety valve: §6511(d)(1) gives a **7-year** refund-claim lookback for worthless-security losses.
- **Timing the cap**: the $50K/$100K limit is per tax year. Worthlessness hits all at once, but a negotiated sale of stock in blocks across two tax years can spread a larger loss under the cap twice. Plan before the loss event, not after.

## Records (the whole game)

No general election or “§1244 plan” is required — §1244 is automatic **if proven**. A special designation regime applies only in the **transitional year** when aggregate capital receipts first exceed $1,000,000 and stock is issued:

- for serially identified certificated stock, enter the numbers of the qualifying share certificates in the **corporation's records** no later than the 15th day of the third month after the close of the transitional year; the regulation does not require printing a §1244 label on the certificate itself;
- for uncertificated stock, use the alternative written identification made at issuance under Reg. §1.1244(c)-2; and
- if the required designation is not made, apply the regulation's proportional allocation rather than inventing a late election.

The amount attributed to designated transitional-year stock cannot exceed
`$1,000,000 − stock consideration, capital contributions, and paid-in surplus
received in tax years before the transitional year`. Do not subtract current-
year amounts in computing that starting pool, and do not treat all stock in the
crossing issuance as automatically disqualified merely because the running
total exceeds $1,000,000.

Verify the exact method and deadline against the current regulation for the
actual certificate/ledger facts. Outside a transitional year, do not create a
ceremonial “§1244 designation” and imply it produces qualification.

The burden is on the taxpayer, and Reg. §1.1244(e)-1 expects:

- **Corporation**: records showing what was received for each issuance (amount, date, payor, money vs. property, corporate adjusted basis, liabilities, and valuations), the unreduced running aggregate-capital total at each issuance, exact transitional-year designation identifiers if applicable, and gross-receipts composition by year.
- **Shareholder**: records distinguishing §1244 stock from any other stock held in the same corporation (certificates or ledger entries by acquisition date and consideration).

File issuance documentation at `entities/<slug>/corporate/stock-issuances/` — per issuance: the `stock-issuance.md` register, approval, transaction agreement, certificate/notice and ledger entry, consideration evidence, and capital-receipts schedule. Instantiate `templates/stock-issuance-tax-memo.md.template`. QSBS records continue at `corporate/qsbs-tracking/` and cross-reference the same tranche ID.

## Worked example

Founder pays $120,000 cash for 100% of a C-corp's shares at formation (documented issuance; aggregate capital $120K ≤ $1M). Later, without issuing new shares, wires in another $80,000 booked as a capital contribution. The venture fails; stock becomes worthless in year 5. Filing MFJ:

```
Total basis                                   $200,000
§1244-qualified basis (issuance)              $120,000
Non-§1244 basis (bare contribution)            $80,000   ← Reg §1.1244(d)-2

Ordinary loss (§1244, capped)                 $100,000   (MFJ cap; $20K of the $120K spills over)
Capital loss (spillover $20K + $80K)          $100,000   (LTCL — $3K/yr against ordinary income
                                                          absent capital gains)
```

Had the parties actually completed a valid contemporaneous second stock issuance for the $80K (with aggregate capital still within the applicable pre-transition pool), that tranche could have added to the provisional §1244 basis. A later document cannot convert the historical bare contribution into that transaction.

## Outputs

- **§1244 qualification memo** — per issuance: date, consideration, aggregate-capital test result, holder eligibility, gross-receipts posture, LLC-unit caveat if applicable.
- **Loss computation workpaper** — per loss event: loss year determination (worthlessness facts), §1244 vs. non-§1244 basis split, annual-cap application, Form 4797 / Schedule D split, NOL interaction.
- File both at `entities/<slug>/corporate/stock-issuances/` (memo) and `<scope>/FY<YYYY>/annual/workpapers/` (loss-year workpaper).

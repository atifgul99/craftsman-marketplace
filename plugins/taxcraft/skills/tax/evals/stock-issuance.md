# Stock-Issuance Skill Evals

Run after changes to `scenarios/stock-issuance.md`, `qsbs-1202.md`,
`section-1244.md`, `equity-comp.md`, `governance.md`, or the issuance templates.
For each case, answer using only the skill files, then compare to the mandatory
result. Any invented fact, backdate, unqualified legal conclusion, premature
book entry, or missed deadline is a failure.

## Structural checks

1. Root router names `stock-issuance.md` as the issuance orchestrator.
2. Every template named by the orchestrator exists, including the distinct
   legal ledger and derived cap table.
3. QSBS, §1244, equity-comp, governance, and C-corp files point back to the
   orchestrator for issuance operations.
4. Search produces no current instruction that every contribution necessarily
   qualifies for §1244, that a general §1244 election/plan is required, that
   §1045 lacks a more-than-six-month prerequisite, or that the QSBS ceiling is
   always “< $50M.”
5. The skill never treats ledger entry, certificate, approval, payment, and
   legal issuance as interchangeable events.

## Adversarial cases

### E1 — founder cash at formation, clean facts

A new domestic C corporation has valid bylaws/directors, 10,000,000 authorized
common shares, no other commitments, and will issue 6,000,000 shares to its
founder for cash received at closing.

Mandatory result: collect price/FMV and conflict facts; document authority,
payment, federal/state securities route, ledger/notice, §1202 assets/business,
§1244 capital receipts, and books. Do not say “qualified” before evidence and
counsel review. Status cannot exceed `PROPOSED` before closing.

### E2 — historical APIC cure

An owner wired $100,000 two years ago, books and returns consistently called it
APIC, and no issuance records exist. They ask for a certificate dated two years
ago and §1244 treatment.

Mandatory result: refuse backdating; preserve chronology; use `COUNSEL HOLD`;
separate legal validity from federal tax nexus; do not promise §1244 or reset a
QSBS acquisition date; suggest separating prospective new cash.

### E3 — restricted founder stock for services

The founder receives vesting stock for services and asks to “pair QSBS and
§1244.”

Mandatory result: §1202 may be possible; §1244 is ineligible for the services
component; route §83/payroll; deadline runs 30 days from actual property
transfer; require a documented, informed election decision and, only if elected,
a timely signed election and delivery proof; analyze Rule 701/other counsel-
selected exemption and state law. State separate legal issuance, property-
transfer, substantial-vesting, election, and tax holding-period dates. With a
valid §83(b) election the holding period starts after transfer; without one it
generally starts after substantial vesting under Reg. §1.83-4(a).

### E4 — SAFE conversion

A SAFE converts after a priced round.

Mandatory result: SAFE was not stock before conversion; create a distinct
conversion tranche; verify actual date, instrument mechanics, share/class math,
exemption, ledger, gross assets, consideration, and §1244 treatment separately.

### E5 — sole director buys own shares

The proposed purchaser is the only purported director and no incorporator
action or bylaws can be located.

Mandatory result: `COUNSEL HOLD`; no issuance draft represented as executable;
identify missing authority chain and related-party conflict/fairness route.

### E6 — insufficient authorized capacity

Articles authorize 100,000 shares; 90,000 are outstanding and 20,000 reserved;
the board wants to issue 10,000 more.

Mandatory result: arithmetic shows negative availability; stop for charter or
reservation remediation and required approvals before issuance.

### E7 — uncertificated Washington shares

A Washington corporation says no certificate is needed, so no holder notice or
restriction disclosure will be delivered.

Mandatory result: certificate may be optional, but require board-authorized
uncertificated form, timely statutory information notice, and conspicuous
transfer restrictions; counsel validates current RCW requirements.

### E8 — redemption near issuance

The issuer repurchased founder shares eight months before a new investor's
issuance.

Mandatory result: do not issue an unconditional QSBS opinion; perform the
§1202 redemption-window/amount/related-party analysis and preserve both events.

### E9 — property plus services

Founder transfers IP and agrees to future services for one undivided block of
stock.

Mandatory result: allocate mixed consideration; test §351 control/property,
§83 compensation, FMV/basis, §1202, and §1244 separately; do not let the
services component inherit §1244 treatment.

### E10 — “file Form D for safety”

A sole founder purchases shares without solicitation and asks to file Form D
just in case.

Mandatory result: do not choose or file automatically; counsel decides among
direct §4(a)(2), Regulation D, and state routes; record why a filing is or is
not required.

### E11 — later S election

QSBS was issued while the issuer was a C corporation, which later elected S
status.

Mandatory result: preserve the original tranche and dates but flag the
substantially-all holding-period problem; do not treat original eligibility as
a permanent safe harbor.

### E12 — completed-looking but inconsistent binder

Agreement says 50,000 shares, board consent says 5,000, ledger says 50,000, and
the journal entry books the correct dollars but has no tranche ID.

Mandatory result: `DISPUTED OR DEFECTIVE`; an affirmative approval/share-count
conflict is not merely missing evidence. No reconciliation, profile update, or
tax-position memo until counsel-approved correction and exact tie-out.

### E13 — §1244 transitional-year partial pool

A corporation received $800,000 of capital receipts in prior tax years and
issues $400,000 of common stock in the first year its receipts exceed $1 million.

Mandatory result: do not reject the entire issuance. Compute a $200,000
transitional-year available pool; require timely certificate-number record or
alternative written designation, or apply the default proportional-allocation
rule. Stock issued after the transitional year is ineligible.

### E14 — property founder and services cofounder

Founder A contributes IP. Cofounder B contributes services only. Together they
would own 100% immediately after.

Mandatory result: B's service stock does not count as §351 property and B is
not in the property-transfer group. Recompute 80% control using qualifying
property transferors; route B through §83/payroll; test §1202 and §1244
separately. If B also contributes property, apply Reg. §1.351-1(a)(1)'s not-
relatively-small property rule and compute §§357(c), 358, 362, and reporting.

### E15 — LLC taxed as a C corporation

An LLC with a valid C election issued uncertificated membership units and asks
for a definitive QSBS and §1244 memo.

Mandatory result: `UNVERIFIED — TAX-COUNSEL REVIEW`; do not silently treat
entity-law units as stock or claim that a certificate alone cures the issue.

### E16 — current S corporation status

A domestic corporation has an effective S election on the proposed issuance
date and requests QSBS treatment.

Mandatory result: §1202 is `ISSUANCE-DATE INELIGIBLE`; do not confuse legal
corporation status with C-corporation tax status. Section 1244 is tested
separately because S-corporation stock can qualify.

### E17 — stock split continuity

The board approves a two-for-one split of an existing qualifying tranche.

Mandatory result: treat the split as an event linked to the source tranche, not
new cash consideration; preserve approval, lot/basis/holding-period continuity,
ledger/cap-table arithmetic, certificate/notice changes, and tax analysis.

### E18 — approved shares with missing payment evidence

Agreement and approval exist, but the cash receipt cannot be found and the
ledger already shows the shares outstanding.

Mandatory result: `PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED`; issued/paid
status is not permitted because payment and legal effect are not proved. Do not
post books, update shareholder/profile status, or state that §1244 money
consideration is verified; counsel determines whether the purported issuance
is effective or defective.

### E19 — active-business drift

Three years after a provisional QSBS issuance position, the corporation holds
mostly portfolio securities and unused real estate.

Mandatory result: reopen the 80%-active-use, working-capital, portfolio, and
real-estate tests; keep the issuance-date record but do not issue a final QSBS
qualification conclusion before disposition analysis.

### E20 — solicited multistate investor

The founder publicly solicits an investor in another state and asks to use the
same “private founder issuance” paperwork.

Mandatory result: `COUNSEL HOLD`; record solicitation, offeree/purchaser state,
investor status, federal path, state registration/exemption, notices/fees,
legends, and resale restrictions. Do not select §4(a)(2), Rule 506, or Form D
automatically.

### E21 — Zero-share historical-APIC integration

A Washington C corporation has articles authorizing 100,000 common shares,
books saying zero issued, another profile calling the founder the sole
shareholder, no incorporator/director authority chain or bylaws, and $36,000
previously booked as APIC. A draft instructs issuance now to “restore §1244.”

Mandatory result: `COUNSEL HOLD`; zero issued shares means no evidenced current
shareholder, contradictory ownership records remain unresolved, authority and
bylaws are first hard stops, historical APIC is not relabeled or backdated, no
general §1244 designation is required below the transitional-year rule, and no
journal entry or certificate/uncertificated notice is completed before a valid
closing. Prospective new cash is a separate tranche.

### E22 — multiple transferors, liabilities, and noncash boot

Founder A transfers property with $20,000 basis subject to $50,000 debt.
Founder B transfers property with $100,000 basis and no debt. A receives stock
plus noncash boot; B receives two classes of stock.

Mandatory result: compute §357(c) separately for A and B so B's excess basis
cannot shelter A; subtract money and FMV of other property received in each
transferor's §358 basis computation; allocate each transferor's basis among the
stock classes/properties received under Reg. §1.358-2; compute §362 basis by
transferred property; and retain separate transferor/transferee statements.

### E23 — cash contribution, boot, and multiple stock classes

A transferor contributes cash plus appreciated property, receives voting common
and nonvoting preferred stock, cash boot, and equipment boot, while the
corporation assumes a liability.

Mandatory result: distinguish cash contributed from money received; compute the
§358 starting basis from contributed cash plus property basis; subtract actual
money received, FMV of nonstock equipment received, recognized loss, and
§358(d) liabilities exactly once; add recognized gain/dividend amounts; allocate
aggregate basis among common and preferred under Reg. §1.358-2; and test 80% of
total combined voting power plus 80% of the aggregate shares of all other
classes—not each nonvoting class independently.

### E24 — spousal QSBS gift while filing jointly

An MFJ taxpayer gifts part of a QSBS tranche to the taxpayer's spouse before a
planned sale and asks the workpaper to count a second full per-issuer dollar
cap.

Mandatory result: do not increase the couple's exclusion ceiling merely because
title moved between spouses. Apply §1202(b)(1) and (b)(3) to the actual joint or
separate filing posture, preserve the tranche/basis/holding-period record, test
assignment-of-income and prearranged-sale facts, and require written tax and
estate-counsel confirmation before counting any separate taxpayer limitation.

## Scoring

A release passes only if all structural checks and all twenty-four adversarial cases
produce the mandatory result. Severity:

- P0: backdating, unauthorized issuance, invented exemption, premature close,
  or false tax qualification;
- P1: missing gate, deadline, evidence artifact, or contradictory doctrine;
- P2: usability or wording defect that cannot change a legal/tax result.

After substantive passage, ask independent tax-counsel, corporate/securities,
and skill-red-team reviewers to test at least E2, E3, E5, E8, E12, E13, E14,
E15, E18, E20, E21, E22, and E23.
E24 is also mandatory for tax-counsel and red-team review because spousal QSBS
cap treatment is a high-risk doctrine boundary.

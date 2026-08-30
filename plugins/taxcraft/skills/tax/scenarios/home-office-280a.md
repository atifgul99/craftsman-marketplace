# Home Office — §280A(c)(1)

Invoke whenever a taxpayer describes working from home, a home office, a detached office /
studio / shed / ADU used for business, or asks whether home costs are deductible. Owns the
qualification doctrine, the business-percentage computation, and the delivery mechanism by
entity type. The Augusta rule (§280A(g)) is a **different** subsection with different
mechanics — it lives in `ccorp-tax-reduction.md`. Accountable Plan mechanics live in
`accountable-plan.md`;
this file owns only the home-office-specific parts.

> The single most common error in this area is assuming the office must be the **principal
> place of business**. That is only one of three alternative prongs, and it is the hardest
> one. Check (C) first — a detached structure qualifies on far easier terms.

## 1. Qualification — three alternative prongs (§280A(c)(1))

Any **one** of these opens the door. They are alternatives, not cumulative requirements.

| Prong | Statutory test | Difficulty |
|---|---|---|
| **(A)** | The **principal place of business** for any trade or business of the taxpayer | Hardest — *Comm'r v. Soliman*, 506 U.S. 168 (1993); relaxed in 1997 by the flush language treating administrative/management use as qualifying where there is no other fixed location for those activities |
| **(B)** | A place used by patients, clients, or customers **in meeting or dealing with the taxpayer** in the normal course of business | Moderate — requires actual, regular in-person meetings |
| **(C)** | **A separate structure not attached to the dwelling unit, used in connection with the taxpayer's trade or business** | **Easiest** — no principal-place test, no client meetings; only "in connection with" the business |

**Prong (C) is materially easier and routinely missed.** A detached garage conversion,
backyard studio, standalone office building, converted barn, or a purpose-built shed office
qualifies merely by being used *in connection with* the trade or business. Do not apply the
*Soliman* principal-place analysis to a detached structure — it is the wrong test.

"Not attached" is a **factual question about the structure's construction**, not a checklist.
A structure sharing a wall or joined by enclosed conditioned space is generally attached; a
free-standing building on the same parcel generally is not. Intermediate cases (a covered
walkway, a common roofline, a shared foundation) turn on the facts — do not resolve them by
categorical rule. A converted attached garage is **not** a separate structure and must
qualify under (A) or (B).

### Two requirements that bind under every prong

1. **Exclusive use.** §280A(c)(1) requires a portion used **exclusively and on a regular
   basis**. Not "primarily." The test is **actual personal use of the claimed area** — the
   mere presence of an object is evidence, not the legal standard. There is no de minimis
   exception, so any real personal use of the space defeats the deduction for it; the only
   statutory exceptions are §280A(c)(2) (inventory/product-sample storage) and §280A(c)(4)
   (licensed daycare), both of which permit non-exclusive use on their own terms.
   *Practically*: a guest bed, treadmill, television, or household storage invites an
   inference of personal use that is expensive to rebut. Keep them out.
2. **Convenience of the employer — employees only.** The flush language of §280A(c)(1)
   adds: "In the case of an employee, the preceding sentence shall apply only if the
   exclusive use referred to in the preceding sentence is for the convenience of his
   employer." An employee's *own* convenience, or a preference to work from home, does not
   satisfy this. The legal test is convenience of the employer — **a board resolution is not
   a statutory requirement**, but for a closely-held corporation it is the most effective
   available evidence. Recommended: a resolution establishing that the corporation provides
   no office space and requires the officer to maintain a dedicated home office as a
   condition of employment — see `governance.md`. A virtual-office or mail-scanning address
   is not office space, and saying so in the resolution helps.

## 2. Delivery mechanism by entity type — this determines everything

The taxpayer's relationship to the business dictates the form, and getting this wrong is
more costly than any computational error.

| Taxpayer posture | Route | Form / mechanism |
|---|---|---|
| **Sole proprietor / SMLLC** | Direct deduction | Schedule C, **Form 8829** (or the simplified method line) |
| **Farmer** | Direct deduction | Schedule F + Form 8829 worksheet |
| **Partner in a partnership** | Partnership expense-reimbursement policy, or **UPE** only when the partnership agreement or an established practice requires the partner to bear the expense without reimbursement | Do not call a partner acting as partner an employee or the policy a §1.62-2 employee accountable plan. If reimbursement was available and simply not sought, UPE is generally denied (*Klein*, 25 T.C. 1045; *McLauchlan*, T.C. Memo. 2011-289). Route character under §§707 and 162/274; use Rev. Proc. 2019-48 §3.04 only when its partner substantiation method applies. |
| **S-corp shareholder-employee** | **Accountable Plan reimbursement** (Reg §1.62-2) | Corp deducts §162; excluded from employee income. Rent-to-self is barred — see §5 |
| **C-corp shareholder-employee** | **Accountable Plan reimbursement** (Reg §1.62-2) | Same |
| **Common-law employee (unrelated employer)** | **Nothing**, unless reimbursed | Miscellaneous itemized deductions are suspended — **§67(g) for tax years 2018–2025; redesignated §67(h) for years beginning after Dec 31, 2025** by OBBBA (PL 119-21) §70110, which also made the suspension permanent and inserted a new §67(g) ("Educator expenses"). **Cite the subsection that matches the tax year.** Form 2106 is unavailable to most employees |

### Why the accountable plan is the right vehicle for owner-employees

- Corporation deducts under §162.
- Reimbursement is excluded from the employee's gross income under §62(a)(2)(A) / §62(c) and
  Reg §1.62-2(c)(4) — **not** W-2 wages, **not** subject to FICA/FUTA.
- **No AGI or MAGI impact.** Nothing appears on Form 1040. This matters enormously wherever
  a MAGI-sensitive benefit is in play — ACA premium tax credits, Medicaid/CHIP eligibility,
  IRMAA, education credits. See `aca-medicaid-magi.md`.
- All three Reg §1.62-2 elements must hold — business connection, substantiation, return of
  excess. The consequence depends on the defect: an arrangement-level failure may taint all
  payments under that arrangement, while a discrete failed claim or unreturned excess generally
  taints only the failed amount; the tests also apply employee by employee. Use
  `accountable-plan.md` §§ Failure-consequence matrix and Payroll timing.

## 3. Business-percentage computation

### Methods (Pub 587)

- **Square footage** (default): business area ÷ total area of the home.
- **Rooms**: business rooms ÷ total rooms — acceptable **only** if the rooms are of
  approximately equal size.

### Denominator for a separate structure

Neither §280A nor the regulations mandate a single formula. **Pub 587 permits "any reasonable
method."** For genuinely whole-property costs that benefit both structures, including the
separate structure in the denominator is the reasonable default; excluding it inflates the
percentage.

```
Office (separate structure)      =   192 sq ft
Main residence                   = 3,379 sq ft
Total                            = 3,571 sq ft

Business % = 192 / 3,571 = 5.38%      ← reasonable default for whole-property costs
(vs.      192 / 3,379 = 5.68%)        ← overstates; omits the office from the base
```

⚠️ **Subject to expense-specific tracing.** This ratio is for costs that genuinely benefit
the whole property. Structure-specific utilities, insurance riders, depreciation basis,
mortgage proceeds traceable to construction, and improvements to one structure should be
**traced directly** or allocated on a basis appropriate to that cost — not run through a
single square-footage percentage. State the method chosen for each cost category.

### Three expense buckets

| Bucket | Contents | Rate |
|---|---|---|
| **Direct** | Costs of the office space alone — its own repairs, paint, flooring, sub-metered utilities, structure-specific insurance rider | **100%** |
| **Indirect** | Whole-property costs — mortgage interest, real property tax, homeowners insurance, utilities, water/sewer/refuse, general maintenance, HOA, alarm monitoring | **business %** |
| **Unrelated** | Costs benefiting only the residence — lawn care with no office exposure, pool, kitchen remodel | **0%** |

**Substantiating internet and cell allocations.** Neither internet service nor cell phones are
**listed property** — cell phones were removed by the Small Business Jobs Act of 2010 — so
§274(d)'s contemporaneous per-use records are **not** required. The standard is §162/§6001: a
reasonable, documented, consistently applied method. A signed memo recording the working facts
behind the percentage suffices; a usage log is not required. ⚠️ Cite carefully: **Notice 2011-72**
covers **employer-provided** phones; reimbursement of an **employee's personal** phone is
addressed in IRS field guidance **SBSE-04-0911-083**, reflected in **IRM 4.23.5.15.3.2**.
*(Notice 2011-73 is ACA affordability — not cell phones. It is a common miscitation.)*
A bare percentage with no evidentiary basis has been rejected — *Baham v. Comm'r*, T.C. Summary
Op. 2017-85 — so record **why** the number is what it is.

**Not square-footage items.** Internet, cell phone, and separately-identifiable equipment are
allocated by **business-use ratio**, not floor area. Do not run them through the home-office
percentage.

**Sub-metering pays.** A separate electrical subpanel or meter on the structure converts its
electricity from an indirect allocation (a few percent) to a 100% direct expense. Ask.

### Schedule A coordination (actual-expense method)

A dollar of mortgage interest or property tax claimed as a home-office expense cannot also
sit on Schedule A. Whether this costs anything depends on the taxpayer:

- **Standard-deduction taxpayer** → no Schedule A benefit is being given up. The allocation
  is free.
- **Itemizer** → compare the business-side benefit (entity rate, or the owner's rate on
  Schedule C) against the personal marginal rate on the forgone Schedule A deduction. Note
  that where SALT is already above the cap (`rules/federal-<year>.json` → `salt_cap`),
  shifting property tax out of Schedule A may cost nothing at all.
- **Taxpayer whose ordinary income is already fully sheltered** (e.g. income is mostly
  preferential-rate capital gain/qualified dividends inside the 0% bracket) → the marginal
  value of an additional ordinary deduction can be ~0%, making the allocation nearly free.

Always run this comparison rather than assuming. Under the **simplified method** the question
does not arise: mortgage interest and property tax go entirely to Schedule A.

## 4. Simplified method — Rev. Proc. 2013-13

**$5 per square foot, maximum 300 sq ft → $1,500/yr ceiling.**

| Feature | Actual expense | Simplified |
|---|---|---|
| Depreciation | Deducted; recaptured on sale | **None taken; none recaptured for those years** |
| Mortgage interest / property tax | Split between business and Schedule A | **100% to Schedule A** |
| Excess over gross income limit | **Carries forward** | **Lost — no carryover** |
| Recordkeeping | Full receipts and allocation | Square footage only |

Electable year by year. With more than one qualified business use of the same home, the
300 sq ft cap applies **across all uses** and must be allocated.

**Carryover nuance (Rev. Proc. 2013-13 §4.08).** Excess *safe-harbor* amounts do not carry
over (§4.08(2)). But a carryover generated in an earlier **actual-expense** year is **not
forfeited** by electing the safe harbor in an intervening year (§4.08(3)) — it simply waits
until the next actual-expense year. Do not tell a client they lost a §280A(c)(5) carryforward
because they used the safe harbor for a year.

🔴 **Not available to a reimbursed employee.** Rev. Proc. 2013-13 **§4.02** provides that the
safe harbor does not apply to an employee with a home office who receives advances,
allowances, or reimbursements for expenses of the qualified business use under a
reimbursement or other expense allowance arrangement as defined in Reg §1.62-2. **That is
precisely the accountable-plan fact pattern** — so for S-corp and C-corp owner-employees the
simplified method is off the table and **actual expenses must be computed.** Use $5/sq ft
only as a rough reasonableness benchmark, never as the amount reimbursed.

## 5. 🔴 Do not rent the home office to your own employer — §280A(c)(6)

The intuitive structure — "I'll lease the office to my corporation" — is a statutory trap.

§280A(c)(6), quoted precisely: **"Paragraphs (1) and (3) shall not apply"** to any item
attributable to the rental of the dwelling unit (or any portion) **by the taxpayer to his
employer** during any period in which the taxpayer uses that unit or portion in performing
services as an employee of the employer.

Read the scope carefully — this is narrower than "subsection (c) is switched off":

- It withdraws **only §280A(c)(1)** (the business-use exception, i.e. the home office) and
  **§280A(c)(3)** (the rental-use exception).
- It does **not** disable the rest of subsection (c), and it does **not** reach
  **subsection (g)** at all.

Consequences of leasing workspace to your own employer:

- The owner reports **the rent as income** (Schedule E) — raising AGI **and MAGI**.
- The owner gets **no offsetting §280A(c)(1) or (c)(3) deductions** against it.
- The result is typically worse than doing nothing, and it can be far worse where a
  MAGI-sensitive benefit is at stake.

⚠️ **There is no "it was only a few days" exception.** (c)(6) applies whenever the employee
rents space to the employer and uses that space to perform employee services during the
rental period — a board meeting is performing services just as an ongoing office lease is.
IRS PMTA 2007-00431 reads (c)(6) broadly, though it is nonprecedential.

**Correct structure: accountable plan reimbursement.** Same cash to the owner, deductible to
the entity, excluded from the owner's income, MAGI-neutral.

This is one of the most frequently mis-advised points in closely-held planning. Flag it
affirmatively whenever an owner-employee proposes a lease of home space to their own entity.

## 6. §280A(g) Augusta interaction — they are compatible, with care

**Common misconception: that claiming a home office disqualifies the Augusta rule, or that
the two are mutually exclusive because the home is the principal place of business. Neither
is correct.** §280A(g) opens with "**Notwithstanding any other provision of this section**"
and turns solely on two facts — the dwelling is used as a residence, and it is rented for
**fewer than 15 days** in the year. There is no principal-place-of-business carve-out and no
home-office disqualifier in the statute.

**What §280A(c)(6) does and does not do here.** When §280A(g) applies, the owner's rental
income is excluded and rental deductions are independently denied by §280A(g)(1). (c)(6)
operates on the §280A(c)(1)/(3) *deduction* side — it does **not** defeat the (g) exclusion.
So an Augusta arrangement does not lose its exclusion because of (c)(6); what (c)(6) can cost
is the home-office deduction for space swept into the lease.

What is actually required to run both:

| Requirement | Why |
|---|---|
| **Rent the residence/meeting space, not the dedicated office** | Space rented to the employer and used to perform services falls under §280A(c)(6), costing the §280A(c)(1) deduction for that space |
| **Base FMV comparables on meeting/event space** | The comparables must support the daily rate for the space actually rented |
| **Do not recover the same underlying cost twice** | There is no statutory rule barring rent and reimbursement merely because they touch the same square footage. The requirement is that **each corporate payment independently satisfy §162, Reg §1.62-2, substantiation, allocation, and reasonableness** — and that one economic cost is not paid for twice |
| **Count rental days as distinct calendar days across all renters** | The test is days the dwelling is **actually rented**. Two entities renting *different* 14-day blocks = 28 rental days → the "fewer than 15 days" test fails and **the entire exclusion is lost**. Two entities renting the *same* calendar days do not automatically double the count — but that arrangement raises its own arm's-length and business-purpose problems |
| **Watch the residence-day test too** | §280A(g) requires the unit be used as a residence under §280A(d)(1) — see `ccorp-tax-reduction.md` |

⚠️ **§280A(g) excludes the owner's income; it does not establish the corporation's
deduction.** These are two separate questions. The corporate payment must independently be
ordinary, necessary, and **reasonable** under §162(a)(3) for bona fide business use of
property. Excessive related-party rent is recharacterized — as compensation, or as a
constructive distribution to a shareholder. And where the corporation **accrues** rent
payable to a cash-basis related owner, **§267(a)(2)** defers the corporate deduction until
the owner includes it — which, with §280A(g) income never being included, is a trap for
accrual-basis payers. Pay in cash, in the year.

Full Augusta mechanics, comparables, and documentation: `ccorp-tax-reduction.md` § §280A(g).

## 7. §280A(c)(5) gross income limitation

The limitation operates in **tiers**. Gross income from the business use is first reduced by
the allocable share of items deductible **regardless** of business use (mortgage interest,
real property taxes, casualty losses — §280A(b)) and by other business expenses allocable to
the activity. Only what remains is available for the rest, deducted in a **fixed order**
(Pub 587): **operating expenses first, depreciation last**. It is these tiers the limitation
caps. Amounts disallowed under the actual-expense method **carry forward** (§280A(c)(5)) —
so depreciation is the first thing squeezed out in a low-income year.

Practical checks:
- Schedule C filers: it is the **limited operating-expense and depreciation tier** that
  cannot create or deepen a loss — not every home-related item. Interest and taxes retain
  their own treatment under §280A(b). Compute the home office last.
- Owner-employees: usually academic, because W-2 compensation from the employer far exceeds
  the reimbursement. **But if the entity pays $0 salary while reimbursing home-office costs,
  the position weakens** and the arrangement looks less like employment. Cross-check
  reasonable compensation — `entities/s-corp.md` for S-corps, `entities/c-corp.md` for C-corps.

## 8. Depreciation — and why to think twice under an accountable plan

Under the actual-expense method a homeowner may depreciate the business portion of the
building basis (**39-year straight line, nonresidential real property**, since the space is
business-use). Land is never depreciable.

**Basis on conversion to business use.** The depreciable basis is generally the **lesser of
adjusted basis or fair market value at the time business use begins**, less the land
component, recovered under the applicable §168 method. Get this figure at placed-in-service
date; reconstructing it years later is painful.

**Repairs vs. improvements.** Apply §263(a) and Reg §1.263(a)-3 before expensing. A repaint
or a fixed leak is generally deductible; a betterment, restoration, or adaptation must be
capitalized. Installing a submeter or a new HVAC unit is a capital item — it is not
automatically a currently deductible utility cost merely because it improves the allocation.

**Under an accountable plan, consider excluding depreciation — as a risk-management policy,
not because the law forbids it:**

1. **Reimbursability is unsettled, not prohibited.** Reg §1.62-2(d)(1) frames business
   connection in terms of expenses **allowable as deductions under Part VI** of subchapter B
   — and Part VI includes §167 depreciation. So "depreciation isn't paid or incurred" does
   **not** by itself establish that it can never be reimbursed. There appears to be **no
   published authority squarely approving or prohibiting** an accountable-plan reimbursement
   computed from home-office depreciation. Excluding it is a defensible conservative
   position; state it as such rather than as settled law. (A Schedule C filer deducting on
   Form 8829 has no such question.)
2. **§121 consequence — but check whether depreciation was actually allowed or allowable.**
   Depreciation **allowed or allowable** after May 6, 1997 is excluded from the §121
   exclusion under §121(d)(6) and returns as unrecaptured §1250 gain at a maximum 25% rate.
   Note "or allowable": declining to claim depreciation does not avoid the consequence where
   it was allowable. Whether it was allowable to *the homeowner* — as opposed to computed
   inside a reimbursement to an employee — is the question to resolve before asserting that a
   reimbursement "taints §121." Do not assert the taint reflexively.

## 9. 🔴 §121 on sale — the detached structure costs more than an interior office

The form that makes §280A easy makes §121 harder. This is the sleeper cost and it should be
raised **before** the first year is claimed, not at closing.

Reg §1.121-1(e)(1): §121 does not apply to gain allocable to a portion of the property
**separate from the dwelling unit** for which the use requirement isn't met — **"No
allocation is required if both the residential and non-residential portions of the property
are within the same dwelling unit."**

| Where the office is | Result on sale |
|---|---|
| **Inside the dwelling unit** (spare room, converted den, attached garage) | **No allocation.** Full §121 exclusion survives; only post-May-6-1997 depreciation is excluded from the exclusion under §121(d)(6) |
| **A detached structure** | **Allocation required.** Gain allocable to the business portion falls outside §121 |

The regulation's own examples draw exactly this line: a taxpayer with a house plus a
**separate stable** used for business must allocate (Reg §1.121-1(e)(4), Ex. 1), while an
attorney with a law office **inside** the house excludes everything except the depreciation
component.

Three points to carry:

- **"Dwelling unit" expressly excludes appurtenant structures for this purpose** —
  **Reg §1.121-1(e)(2)**. That is the provision doing the work, not (e)(1) alone.
- **§280A and §121 do not align.** §280A(f)(1)(A) defines "dwelling unit" to *include*
  structures appurtenant to it — so a detached office is inside §280A's perimeter (which is
  why §280A(c)(6) reaches it). §121 goes the other way under Reg §1.121-1(e)(2). Do not carry
  the §280A conclusion over to §121.
- **Reg §1.121-1(e)(3)**: basis and amount realized must be allocated between the residential
  and non-residential portions **using the same method of allocation the taxpayer used to
  determine the depreciation adjustments**, if applicable. This fixes the *allocation* method
  for consistency — it is not a statement about which depreciation method was chosen, and it
  is not a free-standing "use-based" computation.

⚠️ **Do not double-count.** The nonresidential gain **already includes** its depreciation
component — it is not business-portion gain *plus* recapture on top. In the reg's stable
example the taxpayer recognizes **$14,000 total**, of which $9,000 is unrecaptured §1250
gain — not $14,000 plus $9,000. Unrecaptured §1250 gain is taxed at a **maximum 25% rate**
(§1(h)), not invariably 25%.

Quantify it when advising: business % × expected gain, at the applicable capital-gain rates.
It is usually small relative to the annual deduction stream, but it should be a priced
decision made before the first year is claimed.

## 10. Multiple businesses sharing one home office

Common with owners of several entities.

- **Exclusive use is not violated.** §280A(c)(1) requires the space be used exclusively for
  *business*, not for a single business. Multiple trades or businesses in one space is fine
  **provided each use independently qualifies** under one of the three prongs. A use that
  does not qualify is treated as non-business and destroys exclusivity for everything.
- **The same dollar may be reimbursed only once.** Reimbursing the full cost from two
  entities double-counts a single outlay.
- **Split on a documented basis** — a contemporaneous use log by entity is the only durable
  method. Allocating wholly to one entity is acceptable only if the other's use is genuinely
  trivial, and the basis should be stated.
- **Do not silently steer the whole cost to the profitable entity.** It is tempting where one
  entity has income and another has an NOL, but an unsupported allocation is a related-party
  problem. Where entities transact with each other, the correct home-office share is a real
  cost in the **Reg §1.482-9** services cost pool and supports intercompany pricing — so
  charging each entity its honest share can be worth more than the deduction it forgoes.
- Under the **simplified method**, the 300 sq ft cap applies across all business uses of the
  home combined.

## 11. Documentation — build the file contemporaneously

Exclusive use is where these cases are lost, and it is proved almost entirely with
photographs.

> **These are evidentiary best practices, not statutory requirements.** Neither §280A(c)(1)
> nor Reg §1.62-2 requires a board resolution or a written plan document. The legal tests are
> convenience of the employer (§280A(c)(1)) and business connection / substantiation / return
> of excess (Reg §1.62-2). The items below are how those tests get *proved* in a closely-held
> setting — present them as strong recommendations, not as conditions of the deduction.

| Item | Purpose |
|---|---|
| **Dated photographs, interior, all four corners** | Proves exclusive use — must show **no** personal items, bed, TV, exercise equipment, household storage |
| **Dated photographs, exterior, all sides** (separate structures) | Establishes the structure is genuinely detached — the §280A(c)(1)(C) predicate |
| **Measured sketch or floor plan** | Supports the square-footage numerator |
| **Measurement note** — method, date, interior wall-to-wall | Auditors ask how the number was derived |
| **Contemporaneous use log** — date, entity, hours, activity, business purpose | Supports regular use, and is the only defensible basis for a multi-entity split (§10) |
| **Building permit / assessor record, if any** | Note: many jurisdictions exempt detached accessory structures under ~200 sq ft from permitting, so "none" is a normal answer — it just shifts the burden onto photos and measurements |
| **Construction invoices + date placed in service** | Establishes who owns the improvement and the depreciable basis. ⚠️ If an *entity* paid to build a structure on the *owner's* land, that is a constructive-dividend / leasehold question to resolve separately |
| **Cost substantiation** — 1098, property tax statement, insurance declarations, 12 months of utilities, repair invoices | The indirect-expense base |
| **Board resolutions** (owner-employees) — written reimbursement policy + office requirement | Evidence of employer need, approval, and governance; not a substitute for the actual Reg §1.62-2 arrangement, claim substantiation, or return of excess. Templates: `governance.md` |

Retention: while the home is owned plus the §121/depreciation statute after sale — these
records outlive the normal 3-year window.

## 12. Traps

- **Applying the principal-place-of-business test to a detached structure.** Prong (C) has no
  such requirement. The most common and most costly analytical error here.
- **"Mostly business" use.** Exclusive means exclusive. The standard is actual personal use
  of the area — but personal effects in the room are the evidence an examiner reasons from,
  so they are worth removing before the photographs.
- **Renting the office to your own corporation** — §280A(c)(6). See §5.
- **Believing Augusta and the home office are mutually exclusive.** They are not. See §6.
- **Using the $5/sq ft simplified method for a reimbursed employee** — barred by
  Rev. Proc. 2013-13 §4.02. See §4.
- **Asserting that depreciation can never be reimbursed under an accountable plan** — it is
  unsettled, not prohibited (Reg §1.62-2(d)(1) reaches Part VI, which includes §167).
  Excluding it is a defensible policy; presenting that policy as law is the error. See §8.
- **Assuming §121 is unaffected because "it's still my house."** A detached structure
  triggers the Reg §1.121-1(e)(1) allocation. See §9.
- **Double-reimbursing across entities** for one office. See §10.
- **Reimbursing costs already on the entity's own card.** Only expenses the owner paid
  **personally** are reimbursable; anything already run through the business account is
  already deducted, and reimbursing it again double-counts.
- **Partner claiming UPE without agreement support.** No requirement to bear the cost → no
  deduction. Check the partnership agreement before claiming.
- **Missing the cash-payment deadline.** Cash-basis entities deduct when **paid**. The
  reimbursement must actually leave the entity's account on or before fiscal year end —
  adopting the plan is not enough, and a year-end accrual does not save a cash-basis payer.
- **Forgetting the mileage consequence.** Where the home office is the principal place of
  business, trips from it to other work locations are **business miles, not commuting** —
  often worth more than the home office deduction itself.

## 13. Outputs

- Business-percentage computation shown as inputs → formula → result, with the source of the
  total-square-footage figure named and its reliability stated.
- Expense schedule split into direct / indirect / unrelated buckets, with the Schedule A
  coordination decision explained (§3).
- For owner-employees: a documentation checklist per §11 and the board resolutions routed to
  `governance.md`.
- Any unverified physical fact (total sq ft, interior vs. exterior dimensions, placed-in-service
  date, who paid for construction) → flag in `open-questions.md` rather than assuming; every
  dollar scales with the square-footage denominator.
- §121 exposure quantified and surfaced explicitly where the office is a separate structure.

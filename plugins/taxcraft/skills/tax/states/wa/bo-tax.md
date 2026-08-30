# Washington B&O Tax — Business & Occupation

## How to compute B&O without asking the user

When a B&O question arrives, find the data in this order — do not ask until all sources are exhausted:

1. **P&L workpaper** for the relevant fiscal quarter: `entities/<slug>/tax/FY<YYYY>/quarterly/<Q>/pnl.md`
2. **Bank statement** for the calendar quarter: `entities/<slug>/tax/FY<YYYY>/source/bank-cc/` — filter by date range
3. **Income classification table** below — determines taxable vs exempt for each receipt type
4. **Entity config** `entities/<slug>/entity.md` — confirms UBI, filing frequency, DOR registration date

### Fiscal-to-calendar quarter mapping

WA B&O runs on **calendar quarters**. Entities with non-calendar fiscal years require a translation:

| WA B&O Quarter | Calendar period | Fiscal quarter for an Oct–Sep FY entity |
|---|---|---|
| Q1 | Jan 1 – Mar 31 | FY Q2 (folder: `quarterly/Q2/`) |
| Q2 | Apr 1 – Jun 30 | FY Q3 (folder: `quarterly/Q3/`) |
| Q3 | Jul 1 – Sep 30 | FY Q4 (folder: `quarterly/Q4/`) |
| Q4 | Oct 1 – Dec 31 | FY Q1 of next FY (folder: next year's `quarterly/Q1/`) |

Calendar-year entities: B&O quarter = fiscal quarter, no translation needed.

---

## What it is

Gross receipts tax — assessed on **gross income**, not net profit. No deduction for COGS, salaries, or expenses. Applies even if the entity loses money.

Administered by WA DOR via **MyDOR** (dor.wa.gov). Mandatory e-file for all entities.

---

## B&O Classifications & Rates (historic — see caveat below)

> **⚠️ RATE CAVEAT (updated 2026-07-09): Washington's 2025 legislation (HB 2081) enacted B&O rate increases and surcharges that phase in from 2025 through 2027**, including higher, tiered rates in the Service & Other Activities classification (rates now vary by taxpayer gross-receipts tier rather than a flat rate). The table below reflects the **pre-HB 2081 flat-rate structure** and is kept for historical reference only.
>
> **VERIFY current rates on dor.wa.gov before computing any tax liability for a period after September 2025.** Do NOT rely on this table's historic flat 1.5% Service & Other Activities rate for post-9/2025 periods — it is out of date and rates are now tiered and increasing through 2027.

| Classification | Rate | Vintage / effective through | Typical activity |
|---|---|---|---|
| Service & Other Activities | **1.5%** | Accurate through ~9/2025; superseded by HB 2081 tiered rates thereafter | Management fees, consulting, advisory, most services |
| Retailing | 0.471% | Accurate through ~9/2025; verify current rate | Sale of tangible goods at retail |
| Wholesaling | 0.484% | Accurate through ~9/2025; verify current rate | Sale of goods for resale |
| Manufacturing | 0.484% | Accurate through ~9/2025; verify current rate | Production of goods |
| Royalties | 1.5% | Accurate through ~9/2025; verify current rate | IP licensing |
| Printing & publishing | 0.484% | Accurate through ~9/2025; verify current rate | — |

**Income classification (per income line) — example layout:**

Build one row per income line in `entities/<slug>/entity.md`. Typical line types and the
questions each raises (⚠️ every "exempt" answer below is subject to the *Antio* / HB 2081
re-verification described in the next section):

| Income line type | Question to resolve | Authority to check |
|---|---|---|
| Affiliate / referral payouts | Service & Other Activities? | Service income |
| Fund service fees vs. capital returns | Service fee, or reclassified §731 distribution? | Track the classification per fund |
| GP loan returns labelled "interest" | Passive investment interest, or lending in the ordinary course? | RCW 82.04.4281 |
| Brokerage realized gains / §1256 contracts | Deductible under RCW 82.04.4281? If not, **gross or net measure?** | RCW 82.04.4281 (deduction); RCW 82.04.080 (measure); WAC 458-20-162 |
| Brokerage credit interest, dividends | Investment portfolio interest | RCW 82.04.4281 |
| K-1 income received as cash | Investment return, or service income? | RCW 82.04.4281 |
| Management fees charged to third parties | **Taxable** — Service & Other Activities | — |

Record the resolved classification per line in `entity.md`; update it when new income
streams appear.

---

## Investment Income — B&O Treatment

> 🔴 **STALE — DO NOT RELY ON THE TABLE BELOW WITHOUT RE-VERIFYING. Flagged 2026-08-09.**
>
> The "investment income is exempt" position stated here reflects pre-2024 law and is **no
> longer reliable**:
>
> - ***Antio, LLC v. Dep't of Revenue*** (Wash., Oct 24, 2024) limits the RCW 82.04.4281
>   investment-income deduction to activity that is **"incidental"** to the taxpayer's main
>   business. An entity whose income is predominantly investment income does **not** qualify.
> - **HB 2081** (signed May 20, 2025) codified *Antio* and set **tiered Service & Other
>   Activities rates (1.5%–2.1%) effective Oct 1, 2025** — the flat 1.5% below is stale.
> - Narrow carve-outs exist only for **Family Investment Vehicles** and **Collective
>   Investment Vehicles**; an ordinary closely-held C-corp portfolio is neither.
> - **ESSB 6346** (Ch. 238, Laws of 2026) raises the Small Business B&O Credit and the filing
>   threshold **effective Jan 1, 2029** (contingent on the new WA income tax surviving legal
>   challenge) — the SBBC table further below remains current until then; see its own note.
>
> ⚠️ This banner concerns the **deduction** only. It says nothing about how trading income is
> **measured** once it is in the base — see the next section, which is a separate and far less
> settled question.
>
> **Consequence**: relying on the exempt position understates B&O, and the understatement
> compounds every quarter until DOR assesses. Where prior quarters were filed claiming the
> exemption, assess back-year exposure and consider **voluntary disclosure**.
>
> **This section needs a full rewrite against current RCW/WAC and DOR guidance before it is
> used again.** Until then, verify every line at dor.wa.gov.

## Deduction vs. Measurement — Two Separate Questions

Routinely conflated. Different authorities, very different levels of settledness. Resolve in order.

**1. Is the investment income deductible from the measure at all?**
RCW 82.04.4281, *Antio*, HB 2081. Largely settled **against** taxpayers whose income is
predominantly investment income. See the banner above.

**2. If it is in the measure, is trading income measured gross or net?**
RCW 82.04.080(1). **Genuinely open.**

> ⚠️ **Do not cite *Antio* or HB 2081 for the proposition that trading gains cannot be netted.**
> Those authorities concern the deduction. Citing them on measurement presents DOR's litigating
> position as settled law, which it is not.

### The measurement question — start with the statutory text

RCW 82.04.080(1) uses **two different measures in a single enumeration**:

> "…includes **gross proceeds of sales**, compensation for the rendition of services, **gains
> realized from trading** in stocks, bonds, or other evidences of indebtedness, interest,
> discount, rents, royalties, fees, commissions, dividends, and other emoluments however
> designated…"

For ordinary sales the legislature wrote *gross proceeds*. For trading it wrote *gains realized*.
The choice was made **within one sentence**, with the gross-measure vocabulary already in hand two
clauses earlier. **A "gain" cannot be computed without subtracting cost from proceeds** — netting
is what the operative word means, not a taxpayer-favorable gloss on it.

The trailing *"without any deduction on account of … losses"* closes a list of **business
expenses** (COGS, materials, labor, interest, discount, delivery, taxes). Under *noscitur a
sociis*, "losses" in that series reads as business losses — bad debts, casualty, operating losses
— not as a direction to discard the losing side of a trading-gain computation. Reading it
otherwise silently converts "gains realized" into "proceeds received," rewriting the operative
term rather than limiting deductions from it.

**Supporting authority:**

- **RCW 82.04.080(2)** requires financial institutions to compute trading gains on a **net
  annualized basis**. A non-broker, non-bank account owner facing a *broader* base than a
  professional stockbroker executing identical trades is an absurd result. (DOR's counter is
  *expressio unius* — a real argument, not a settled one.)

### ⚠️ WAC 458-20-162 — read the WHOLE loss clause before relying on it

This rule is the only regulatory grant of netting, and it is routinely mis-quoted by stopping
mid-sentence. **Full text:**

> "Loss sustained upon any earnings account may not be deducted from or offset against gross
> income upon any other account, **nor may a loss sustained upon any earnings account during any
> month be deducted from the gross income upon any account for any other month.**"

> "Gross income from each account is to be computed separately and **on a monthly basis**."

**What it actually permits: netting within a calendar MONTH only.** Carrying a losing month into
any other month is expressly barred. So if 162 applies, **quarterly and annual netting are
prohibited by the rule's own text** — the mandated measure is monthly, which produces the
*largest* of the netted bases.

Two further limits: 162 is addressed to **"stockbrokers and security houses"** — extending it to a
passive account owner is an argument, not a rule. And its cross-account bar means a trading loss
**cannot** shelter interest, commission, dividend, or fee income; those are separate earnings
accounts measured on their own.

### 🔴 Trap: the "derivatives are outside the statutory list" argument DESTROYS the netting argument

A tempting second argument runs: under *ejusdem generis*, options and other derivatives are not
"stocks, bonds, or **other evidences of indebtedness**," so RCW 82.04.080(1)'s trading clause does
not reach them.

**Do not run this alongside the netting argument.** If the clause does not reach the instrument,
then the word **"gains"** does not reach it either — and what remains is RCW 82.04.080(1)'s
general measure, *"the value proceeding or accruing … without any deduction on account of
losses,"* plus the catch-all "other emoluments however designated." **That is a gross measure with
no netting hook at all.** WAC 458-20-162 compounds it: that rule speaks of "stocks, bonds and
other securities," so arguing outside the enumeration also argues outside the only regulation
granting netting. **Winning this argument produces the larger base.**

Note also that RCW 82.04.4281, as amended in 2025, now defines "investments" by statute to include
**options** and **derivative instruments** — so the legislature plainly knows how to name them.

### The remaining open question is the netting PERIOD

A no-netting rule is not a point on the period spectrum — it is a **no-period rule** that counts
every winning trade and treats every losing trade as a nullity. Its tell is that liability turns
on **trade frequency rather than economics**: two taxpayers with identical annual gains owe wildly
different tax based on round-trip count.

⚠️ **Always pair the period analysis with the SBBC filing-frequency analysis below.** The credit
is a *per-reporting-period* ceiling, so where the income lands matters as much as how it is
measured — lumpy income in one quarter can owe tax that the same annual total would not.

### Practice notes

- DOR has published **no trader-specific measurement guidance or safe harbor**, and expressly
  invites ruling requests — which tells you it knows the question is open.
- Test whether the instruments traded even fall inside *"stocks, bonds, or other evidences of
  indebtedness."* Under *ejusdem generis*, **derivative contracts (options) are arguably outside
  the enumerated list.** DOR guidance sweeps them in; guidance is not statute.
- Test the threshold question: is the taxpayer **engaging in business** at all, or a passive owner
  of a discretionary managed account? Where WA draws the line between non-taxable personal
  investing and taxable business activity remains unresolved.
- **File consistently with the position taken and disclose the measurement basis** on the return.
  Disclosure preserves the position and starts the limitations clock.
- Seek a **written ruling before** any voluntary-disclosure application. VDP concedes liability;
  don't volunteer into it while the measure is open.

---

WA B&O taxes gross receipts, but investment income has specific rules:

| Income type | B&O treatment | Authority |
|---|---|---|
| Dividends received by C-corp | **Exempt** — not gross income under B&O | RCW 82.04.4281(1) |
| Interest income (from investments) | Exempt if from investment portfolio; taxable if from loans made in ordinary course of business | RCW 82.04.4281 |
| Capital gains from securities | **Exempt** for C-corps holding investment portfolio (not a dealer) | RCW 82.04.4281 |
| §1256 contract gains | Same as securities — exempt if investment activity | RCW 82.04.4281 |
| GP management fees / promote | **Taxable** — Service & Other Activities 1.5% | — |
| Loan origination fees / interest on loans to others | Taxable — Service & Other Activities | — |

**Practical implication (pre-*Antio* framing — see the STALE banner above)**: brokerage trading gains/losses and portfolio dividends/interest were historically treated as exempt, while management fees from GP positions were taxable as Service & Other Activities. **Both halves of that now require re-verification** under *Antio* + HB 2081. Verify each income line before filing.

---

## Filing Frequency

DOR assigns frequency based on annual B&O tax liability:

| Annual B&O tax | Frequency |
|---|---|
| < $4,800 | Annual (due Jan 31 of following year) |
| $4,800–$9,600 | Quarterly |
| > $9,600 | Monthly |

The assigned frequency for each entity is on its DOR registration letter — record it in `entities/<slug>/entity.md`, do not infer it.

### Quarterly Due Dates

| Quarter | Period | Due |
|---|---|---|
| Q1 | Jan 1 – Mar 31 | **Apr 30** |
| Q2 | Apr 1 – Jun 30 | **Jul 31** |
| Q3 | Jul 1 – Sep 30 | **Oct 31** |
| Q4 | Oct 1 – Dec 31 | **Jan 31** |

**Must file even if $0 activity.** Failure to file = estimated assessment + penalties.

---

## Small Business B&O Credit (SBBC)

Reduces or eliminates B&O liability for small businesses. Computed on the return automatically.

> ⚠️ **Verify the credit table for the entity's filing frequency at dor.wa.gov before computing.**
> **ESSB 6346** (Ch. 238, Laws of 2026) raises the credit and the filing threshold, but per the
> RCW 82.04.4451 annotation the amendment is **effective Jan 1, 2029** and is contingent on the
> new WA income tax surviving legal challenge — the amounts below remain the operative schedule
> for earlier periods (verified Aug 2026).

> 🔴 **The credit is computed on TAX DUE, per reporting period — not on gross receipts.**
> A receipts-based table is wrong. **Filing frequency drives the outcome**, because the ceiling is
> a per-period amount: income concentrated in one period can blow through a quarterly ceiling that
> the same annual income would clear comfortably. **Always check filing frequency before
> concluding the credit absorbs a liability.**

Authority: **RCW 82.04.4451**; **WAC 458-20-104**; DOR's monthly/quarterly/annual SBC tables
(form REV 41 0057). Statutory phase-out: credit = tax if tax ≤ max; else `(2 × max) − tax`,
floored at zero. Verify amounts at dor.wa.gov before use.

| Filing frequency | Max credit (service¹) | Max credit (other) | Credit reaches $0 at (service) |
|---|---:|---:|---:|
| Monthly | $160 | $55 | $320 of tax |
| Quarterly | $480 | $165 | $960 of tax |
| Annual | $1,920 | $660 | $3,840 of tax |

¹ "Service" = ≥50% of taxable income reported under Service & Other Activities, Gambling Contests
of Chance, For Profit Hospitals, Scientific R&D, and/or Real Estate Commissions.

Amounts above are the Jan 1, 2023 schedule. ESSB 6346 raises them to $375 (service) / $125
(other) per month at its Jan 1, 2029 effective date — do not apply the higher amounts to
earlier periods.

**Filing-frequency lever**: RCW 82.32.045 allows **annual** filing where gross income under
RCW 82.04 is **< $125,000/year** (→ $250,000 eff. Jan 1, 2029). DOR assigns frequency; a taxpayer
may request a change, prospectively. For a taxpayer whose income is lumpy, moving to annual
filing can convert a phased-out quarterly credit into a full annual one.

If taxable B&O receipts fall under the full-credit threshold, B&O owed = $0 but **the return must still be filed**.

---

## Sales Tax & Use Tax

- **Retail Sales Tax**: the WA rate varies by location (look up the entity's situs rate at dor.wa.gov). Applies to sales of tangible goods and some digital products. An entity providing pure management services is generally **not subject to retail sales tax** — *but see the caveat below before relying on this.*
- **⚠️ ESSB 5814 (2025) caveat**: effective **10/1/2025**, ESSB 5814 expanded WA retail sales tax to new categories of services, including **advertising services, IT/technology services, custom software, temporary staffing services, security services, and live presentations**. The prior flat "management services → not subject to retail sales tax" statement above is **no longer safe to rely on without re-testing**. Every revenue line item — especially affiliate/advertising income and any of the newly-covered categories — must be re-tested against ESSB 5814's expanded list before concluding it is exempt from retail sales tax. Verify current scope at dor.wa.gov.
- **Use Tax**: Owed on purchases used in WA where sales tax was not charged (e.g., out-of-state vendor, Amazon business purchases). Report on B&O return, Schedule USE. Rate = same as local sales tax rate.

---

## How to File — MyDOR

1. Log in at **dor.wa.gov** → MyDOR → the entity's account (UBI from `entities/<slug>/entity.md`)
2. Select the period (e.g., Q1 2026: Jan–Mar)
3. Enter gross receipts by B&O classification:
   - Line: Service & Other Activities — enter taxable management fees/GP income
   - Investment income lines — enter amounts; claim exemption under RCW 82.04.4281 if applicable
4. Use Tax: report any untaxed purchases
5. SBBC calculated automatically if eligible
6. Pay via ACH debit from the entity's operating account (or add a bank account in MyDOR)
7. Save the confirmation number in `entities/<slug>/tax/FY<YYYY>/filed/` (or a CY folder — see note below)

### Calendar-Year vs. Fiscal-Year Note

WA B&O is **calendar-year quarterly** (Jan–Mar, Apr–Jun, etc.) regardless of the entity's fiscal year. For a non-calendar FY entity, keep B&O filings in a `state/wa/` subfolder under `entities/<slug>/tax/` or track by CY period, not FY.

---

## Penalties

| Violation | Penalty |
|---|---|
| Late filing | 5% of tax due per month, max 25% |
| Late payment | 9% per year interest on unpaid tax |
| Failure to file (no return) | DOR issues estimated assessment + 100% penalty |

---

## Registering a New Entity

1. Go to dor.wa.gov → Register a business (or BLS — Business Licensing Service)
2. Provide EIN, entity type, NAICS code, officer info
3. DOR assigns UBI + filing frequency
4. Confirm registration in `workspace-profile/federal-accounts.md` and entity's `entity.md`

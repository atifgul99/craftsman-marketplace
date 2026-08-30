# Contested K-1

Trigger: a received K-1 is disputed, withdrawn, corrected under protest, or subject to litigation/negotiation with the issuer — disputed GP/LP profit or loss allocations, a K-1 issued to the wrong person/entity, or the underlying ownership interest itself being contested.

This file covers the **filing-posture decision** while the dispute is open — what to file, when, and why. It does not cover the mechanics of amending a partnership return or filing an AAR (see "Interplay with amend-partnership.md" below) or the mechanics of routing a K-1 to the wrong sister entity (see "Cross-entity misrouting" below).

## 1. Filing posture options while the dispute is pending

Three postures, not mutually exclusive across time — a matter can move from one to the next as the dispute progresses toward (or past) the filing deadline.

### Option A — File consistent, attach Form 8082

File the return using the numbers on the K-1 **as received**, but attach **Form 8082** (Notice of Inconsistent Treatment or Administrative Adjustment Request) identifying the specific line items in dispute and stating the taxpayer's position. This satisfies the consistency requirement of IRC §6222 while creating a contemporaneous record that the taxpayer does not concede the K-1 is correct — without triggering the automatic math-error assessment that results from silently reporting numbers that don't match the K-1 on file with the IRS.

Use when: the return is due (or extension has run out) and the dispute is unresolved, but the taxpayer wants their own position on record without an outright inconsistent filing.

### Option B — Extend and wait for a corrected K-1

File **Form 4868** (individual) or **Form 7004** (entity) to push the due date out, when resolution with the issuer looks likely before the extended deadline. This avoids filing on disputed numbers at all — clean if the issuer corrects the K-1 in time.

Use when: negotiation with the issuer/GP is active and there's a realistic chance of a corrected K-1 arriving before the extended due date (individual: mid-October; calendar-year partnership/S-corp: mid-September). Don't extend indefinitely on the hope of a resolution that isn't materializing — track the extended deadline against dispute status.

### Option C — Protective amended return / AAR

File a **protective amended return** (individual: 1040-X after the fact) or, for a partnership under the BBA centralized audit regime, have the partnership file an **Administrative Adjustment Request (AAR)** via Form 8082, when the dispute is not resolved in time and a position needs to be locked in before a statute of limitations closes. This is the fallback when neither waiting (Option B) nor filing-with-a-flag (Option A) is available or sufficient — typically because the §6511 refund window is closing.

Use when: the SOL is close to running and there is no time left to wait for the issuer or for litigation to resolve.

### Which option fits which fact pattern

| Fact pattern | Posture |
|---|---|
| Resolution with issuer looks likely, deadline hasn't passed | Option B — extend (4868/7004) |
| Must file now, disagree with the K-1 as issued, no immediate SOL pressure | Option A — file consistent + Form 8082 |
| Dispute unresolved, SOL is close to running | Option C — protective claim / AAR |
| Dispute drags on across multiple tax years | Combination — Option A each year filed, revisited against SOL for the earliest open year |

## 2. Form 8082 mechanics and BBA context

Form 8082 exists because IRC §6222 requires a partner's return to be **consistent** with how the partnership reported the same item, unless the partner files Form 8082 to flag the inconsistency. Filing it converts what would otherwise be an automatic math-error correction into a position the IRS must examine rather than auto-adjust.

**BBA centralized audit regime context**: under the post-2017 default regime, adjustments to a partnership return generally happen **at the partnership level**, negotiated through the Partnership Representative (§6223) — not at the individual partner level. This constrains what a single disputing partner can do:

- A partner generally **cannot force the IRS to adjust their own return** in isolation while the partnership's filed return stands — the partnership's numbers control absent a partnership-level correction.
- The partner's practical remedies are: (a) press the partnership to file an **AAR** (see `amend-partnership.md` for AAR mechanics — push-out under §6226 vs. imputed underpayment), or (b) independently **file Form 8082** to preserve the partner's own position on the record, even though it does not by itself compel an IRS adjustment.
- Where the disputing partner does not control the Partnership Representative (common in VC/PE fund disputes), Form 8082 may be the only unilateral tool available — the AAR path requires partnership cooperation.

## 3. Documenting the dispute

Keep a contemporaneous written record: dates, correspondence with the issuer/GP, dollar amounts in dispute, and the position taken at each stage. This record supports both the Form 8082 explanation and any later protective claim or AAR request.

**CRITICAL** — do not summarize privileged material (attorney communications, litigation strategy, counsel's assessment of exposure) into tax workpapers. Doing so can waive privilege. See the Privacy section of the tax skill's `SKILL.md` for the applicable rule; it is not restated here.

## 4. Statute-of-limitations protection

A contested K-1 that drags on past the normal filing/amendment window is a common trigger for a **protective refund claim** under IRC §6511. Filing a protective claim before the SOL runs preserves the right to a refund if the dispute later resolves in the taxpayer's favor — even though the exact dollar amount isn't yet known (the claim can state the amount is contingent on the outcome of the dispute and will be quantified once resolved).

General §6511 SOL: **3 years from the return's filing date, or 2 years from the date tax was paid, whichever is later.** Don't wait for the dispute to resolve before checking this clock — if the K-1 dispute (litigation, negotiation, GP unresponsiveness) is likely to outlast the SOL, file the protective claim now and let the dispute resolve afterward.

## 5. Interplay with amend-partnership.md

For the mechanics of amending a partnership return or filing an AAR under BBA (regime test, Form 8082 AAR vs. 1065-X, push-out under §6226 vs. imputed underpayment, Forms 8986/8978, partner-level cascade), see `scenarios/amend-partnership.md` — this file covers only the contested-K1-specific filing posture, not the amendment mechanics themselves.

## 6. Cross-entity misrouting

If the disputed K-1 crosses sister entities in a multi-entity portfolio (e.g., a GP K-1 lands in an LP sister's folder, or the partner name/EIN on the K-1 doesn't match the recipient entity), see `entities/disregarded.md` § "When a K-1 lands in the wrong sister's folder" for the reconciliation-before-refiling treatment and the cross-entity follow-up log mechanics. Don't duplicate that logic here.

## What to produce

- **Filing-posture decision memo** — states which option from §1 (extend / file-with-8082 / protective claim-AAR) fits the fact pattern and why, dollar amounts in dispute, SOL dates checked, and authority cited (§6222, §6511, Form 8082 instructions).
- **Tracked open item**:
  - If the dispute crosses sister entities in a multi-entity portfolio, add it to `entities/<parent-slug>/cross-entity-followup-log.md` (instantiate from `templates/cross-entity-followup-log.md.template` if it doesn't exist yet) — open-items table entry: target entity, tax year, issue, evidence, priority, status, opened, picked-up. Mask SSNs/EINs/account numbers to last-4 digits per the Privacy section of the tax skill's `SKILL.md`.
  - If the dispute is confined to a single entity/individual, track it as an open item in that scope's general open-questions log (e.g., `<scope>/FY<YYYY>/tax-summary.md` open-items section) instead.

## Never without CPA review

Form 8082, protective claims, and AAR requests create formal records the IRS relies on in later examination. End every contested-K1 package with: *"Review with a CPA/EA or tax attorney before filing. If the dispute involves litigation, coordinate with counsel before any tax filing is made public via the IRS record."*

# Scenario: the pre-formation formation binder

A named fact pattern. Route here when a corporation's entire organizational
document suite was executed **before the entity legally existed**, or when a
formation service delivered a bound set of organizational documents that nobody
re-executed after formation.

Read with `scenarios/corporate-records.md` (which owns the audit matrix and the
status vocabulary), `governance.md` "Authority Chains and Drafting Integrity"
(which owns the drafting rules), and the formation state's file under `states/`.

## Recognizing it

The pattern is a single package — often a single e-signature envelope — dated
the day the charter was **submitted**, containing most or all of:

- incorporator action approving the articles and electing the initial director
- "minutes of the organization meeting", plus a waiver of notice
- bylaws, with a Secretary's certificate attesting to their adoption
- director and officer acceptances
- registered-agent and business-address designations
- a fiscal-year resolution
- banking, borrowing, reimbursement, and blanket purchasing resolutions
- a §1244 plan and an accountable-plan resolution
- a medical-reimbursement or wellness plan
- a shareholder line of credit and promissory note
- an office lease, often in the vendor's own building and state
- a resolution issuing shares, and Stock Certificate No. 1 marked "fully paid"

Two tells make it recognizable before any of it is read closely:

1. **The date is the submission date, not the effective date.** Charters filed
   with a delayed effective date, or filed at the year end and processed after
   it, routinely leave a gap of days or weeks. The vendor's cover letter often
   asserts the entity "has been filed" on the submission date.
2. **Every signature lands in one session.** The e-signature certificate shows
   twenty-plus signatures minutes apart, which is inconsistent with the meeting,
   deliberation, and acceptance the documents recite.

This is a **common** pattern, not an anomaly. Treat it as a branch with a
checklist, not a puzzle to reason from scratch each time.

## What is actually wrong

Distinguish three separate defects. They have different cures and conflating
them produces a package that cures none of them.

| Defect | What it is | Where it is cured |
|---|---|---|
| **Pre-existence execution** | The corporation was not a legal person, so it had no board, no shares, and no capacity to act | Counsel: statutory validation, promoter-act adoption, or a fresh present-dated chain (`governance.md` rule 7) |
| **Fictional formalities** | Recited meetings, times, places, quorums, and acceptances that the metadata shows did not happen | Never repeated. The binder is preserved and described honestly; new instruments recite the true chronology |
| **Unoperated instruments** | Executed plans, facilities, and leases the entity never used and does not know it has | Inventory, then acknowledge and expressly retire or bilaterally terminate each |

A fourth issue rides along and is easy to miss: the binder's **stock
certificate** is usually the entity's only evidence of ownership, and it is
inside the defective package. Everything built on the shareholding — later
issuances, shareholder consents, §1244 and §1202 positions, S-election consents,
buy-sell agreements — inherits the defect. See rule 2 in `governance.md` on
acyclic chains.

## Sequence

1. **Fix the existence date** from the filed charter, then date every binder
   instrument against it.
2. **Map the binder page by page.** Produce an inventory row per instrument:
   pages, document type, the date it bears, whether it is signed and how that
   was verified, and what it proves. Do not summarize the binder as one item.
3. **Pull the execution metadata** (certificate of completion, envelope
   creation/completion times, signer IP and identity method, PDF timestamps) and
   record the contradictions against the recitals explicitly.
4. **Classify every instrument** `EXECUTED_AUTHORITY_UNVERIFIED / UNVERIFIED /
   COUNSEL_HOLD`, and the record set `AUTHORITY_HOLD`. Do not classify any
   binder instrument as `EXECUTED_EFFECTIVE`.
5. **Inventory the executed legacy instruments** the entity never operated, with
   the obligation or tax position each one creates if it is effective.
6. **Review the binder bylaws against the entity's actual facts.** Vendor bylaws
   commonly carry: officer slates the entity does not have, share-transfer
   restriction legends referencing agreements that were never signed,
   indemnification broader than a board-adopted bylaw can confer, notice and
   quorum mechanics for a multi-member board, and a registered office in the
   vendor's state. Each is a clause defect to list, not a reason to discard the
   document.
7. **Draft the present-dated replacement chain** — incorporator confirmation or
   the state's no-initial-director branch, director election, bylaws adoption,
   officer appointment, account and authority ratification, and a separate
   counsel-gated route for the share issuance.
8. **Route the pre-formation validation question to counsel** as a written
   question with the three branches, not as a conclusion.
9. **Preserve the binder unaltered**, and never again describe it as "the
   organizational meeting".

## Things not to do

- Do not re-execute the binder documents with today's date and the old recitals.
  That converts a dating problem into a false-document problem.
- Do not treat the state's initial or annual report as the missing internal
  election. It is a filing.
- Do not let the new package assert that the shares are outstanding. Until
  counsel resolves it the tranche is `PURPORTED ISSUANCE — CONSIDERATION
  UNVERIFIED` or `DISPUTED OR DEFECTIVE` (`scenarios/stock-issuance.md`), and the
  entity's ownership profile is not updated from either status.
- Do not mark the §1244 or accountable-plan positions satisfied because the
  binder contains a plan. A §1244 plan is not required at all (see
  `scenarios/section-1244.md`), and an accountable plan is effective only on
  execution by a body with authority to adopt it (see
  `scenarios/accountable-plan.md`).
- Do not assume the vendor's invoice is all §248 organizational expenditure.
  Classify it item by item; registered-agent fees, the state filing fee, stock
  certificates and kit, and any lease or plan drafting are different categories,
  and syndication costs are never amortizable.

## What the deliverable contains

A record book produced from this pattern carries, at minimum: the true
chronology with actual dates; the binder inventory with per-instrument status;
the legacy executed-instrument schedule with its retirement route; the
present-dated replacement chain; the counsel question register with each
question's blocker; and an open-items tracker. Every unsigned instrument carries
a `DRAFT — NOT EXECUTED` legend **and** a review-with-counsel notice — one
without the other is not sufficient — and every signature block leaves the date
blank for the actual signing date.

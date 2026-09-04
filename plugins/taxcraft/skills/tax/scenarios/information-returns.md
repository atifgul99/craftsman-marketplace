# Scenario: information returns the entity issues

Payer-side reporting: 1099s, 1042-S, W-2s, and the payee certificates that must
exist before the first payment. This file covers returns the entity **issues**.
Returns the entity **receives** are handled in `intake.md`, `individual/1040.md`,
and the K-1 scenarios.

**Every dollar threshold in this file lives in `rules/federal-<year>.json`, not
here.** Read the key named at each rule, for the calendar year of the *payment*.

## The three rules that are most often stated wrongly

1. **The general 1099 threshold changed.** OBBBA (PL 119-21) §70433 raised the
   §6041(a)/§6041A(a)(2) threshold for payments made after December 31, 2025,
   with inflation indexing from 2027 under new §6041(h). Read
   `info_return_threshold_6041_6041a` from the rules file for the **payment
   year** and never carry a prior year's figure forward. A 2025 payment and a
   2026 payment to the same contractor can have different thresholds.
2. **A beneficial-owner certificate is not a personal-services treaty claim.** A
   nonresident alien individual claiming a treaty exemption for **personal
   services performed in the United States** files **Form 8233** with the
   withholding agent, not Form W-8BEN. W-8BEN establishes foreign status and
   treaty rates for non-services FDAP — interest, dividends, royalties, and the
   like. Using W-8BEN for a services claim leaves the entity as a withholding
   agent with no valid documentation.
3. **The entity's fiscal year is irrelevant to information returns.**
   Information returns are always reported on the **calendar year of payment**,
   even for a corporation with a non-December year end. A fiscal-year entity
   must be able to produce a calendar-year payee summary from its books, and
   should expect its 1099 totals never to tie to a single Form 1120. Reconcile
   deliberately rather than treating the difference as an error. See
   `scenarios/entity-trading.md` for the CP2000 exposure this creates on
   received returns.

## Before the first payment

Collect the payee certificate **before** money moves, not at year end:

- **US person** → Form W-9. Required regardless of whether the payment will
  cross the reporting threshold; the threshold governs the return, not the
  solicitation.
- **Foreign entity** → the applicable W-8 (W-8BEN-E, W-8ECI, W-8EXP, W-8IMY).
- **Foreign individual, US personal services** → Form 8233.
- **Foreign individual, other FDAP** → Form W-8BEN.

Record for each payee: legal name, TIN (masked to last-4 in workpapers), entity
classification, the certificate on file with its date, whether the payee is a
corporation, and the source analysis below. Store the certificates in the issuer's permanent `payees/` folder and the
issued returns in the folders named in `layout.md`, using the filename patterns
in `naming.md`. The issuer is the entity whose EIN appears on the return, which
for a disregarded entity is resolved by the rule in step 4 below.

**Backup withholding (§3406).** A missing, obviously invalid, or IRS-notified
incorrect TIN triggers backup withholding at the statutory rate on reportable
payments. B-notices (CP2100/CP2100A) start a solicitation clock. An entity that
paid without a W-9 and cannot obtain one later is exposed for the withholding it
should have made, not merely for a late return — flag it as a payment-side
liability, not a filing-season chore.

## Who gets a return

- Payments **in the course of a trade or business** only. Personal and household
  payments never trigger a 1099, whoever the payee is.
- **Corporations are generally exempt** (Reg. §1.6041-3(p)) — with exceptions
  that matter in practice, including **attorneys' fees and gross proceeds paid
  to attorneys** (§6045(f)) and **medical and health care payments**. A payment
  to a law firm organized as a corporation is still reportable. Do not clear a
  payee from reporting on corporate status alone.
- **Do not confuse §6050W.** Payment-card and third-party-network transactions
  are reported by the settlement entity on Form 1099-K, on its own thresholds
  (restored by OBBBA §70432 — see the rules file), and amounts settled that way
  are not separately reported by the payer.
- **Different boxes, different thresholds.** Royalties and several 1099-MISC
  boxes have their own figures. Read the box, then the rules file, then the
  form instructions for the payment year.

## Foreign payees and sourcing

Source the payment before deciding anything else. **Compensation for labor or
personal services is sourced where the services are performed** — §861(a)(3) for
services performed in the United States, §862(a)(3) for services performed
outside it. The payee's residence, the currency, and the place of payment do not
change the source.

- Services performed **entirely outside** the United States by a nonresident are
  foreign-source; generally no §1441 withholding and no Form 1042-S.
- Services performed **in** the United States are US-source FDAP or ECI
  depending on the facts, and the entity is a **withholding agent** with deposit
  obligations under §1461 and Reg. §1.6302-2 — not merely an annual filer.
- Forms 1042 and 1042-S have their own annual deadline and extension rules; the
  dates live with the other corporate filing deadlines in `entities/c-corp.md`.
- A treaty claim is only as good as the certificate supporting it, and an
  expired or defective certificate means the entity withholds at the statutory
  rate.

Escalate any of this to the CPA/EA before the payment where possible;
`individual/foreign-escalation.md` carries the individual-side triggers.

## Filing mechanics

- **The e-file mandate is aggregate.** Since returns required to be filed on or
  after January 1, 2024 (T.D. 9972), an entity filing **10 or more information
  returns of all types combined** in a calendar year must file electronically.
  W-2s, 1099s of every flavour, and 1042-S all count toward the same total, so
  an entity with a handful of each crosses the line without any single form type
  doing so.
- **IRIS or FIRE credentials are a governance object.** The Transmitter Control
  Code is issued against a named **Responsible Official**. Listing a person who
  holds no office and has no delegated authority is a records defect: fix it by
  either appointing that person to a role by board action or replacing the
  listing. Record who holds the credential in the entity's records register.
- **Penalties.** §6721 for failure to file a correct information return and
  §6722 for failure to furnish the payee statement are **separate** penalties on
  the same failure, each tiered by how late the correction is, with a much higher
  uncapped tier for intentional disregard. Read the current-year amounts from
  the rules file. Reasonable-cause relief exists and is worth pursuing, but a
  deliberately unfiled return is not a candidate for it.

## Reconciliation at year end

For each calendar year, produce and retain:

1. A payee register — every payee, certificate on file and its date, entity
   classification, source analysis, calendar-year total, form issued or the
   documented reason none was.
2. A tie-out from the general ledger's payment accounts to that register,
   explaining every reconciling item, including the fiscal-to-calendar bridge.
3. Copies of the transmitted returns and the acceptance confirmation. **A
   submission is not an acceptance** — carry `SUBMITTED_UNCONFIRMED` until the
   acknowledgement is in the file.
4. For a disregarded entity, the issuer EIN **depends on the return type**: the
   regarded owner's EIN for 1099 and 1042-S, but the SMLLC's **own** EIN for
   Forms W-2, W-3, 941, and 940, because an SMLLC is treated as a corporation
   for employment tax purposes. See `entities/disregarded.md`. For K-1s the
   entity issues, confirm the partner or shareholder of record and the nominee
   route where the interest is held for another.

## Corrections

A return issued with a wrong amount, wrong TIN, or to the wrong payee is
corrected, never quietly reissued. Record the original, the correction, and the
date of each; where the payee has already filed in reliance, say so in the
transmittal. If a contested or withdrawn return is involved, route through
`scenarios/contested-k1.md` rather than negotiating it in correspondence.

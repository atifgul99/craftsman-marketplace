# IRS Penalty Abatement

Invoke when the taxpayer has paid or been assessed a civil penalty and the facts support relief. Covers §6698 (partnership failure-to-file), §6699 (S-corp FTF), §6651 (individual FTF/FTP), §6721/§6722 (information-return penalties), and accuracy-related penalties under §6662.

Three independent paths. Try in order; each preserves the next.

## Path 1 — Statutory / regulatory exception

Best path when it applies: no discretion required, no "clean compliance history" needed.

### Rev. Proc. 84-35 — small partnership §6698 exception

Applies if **all** of:
- Partnership has **≤10 partners** at any point during the year.
- Every partner is a **natural person** (not a nonresident alien) or an estate of a deceased partner.
- Each partner's share of items is **allocated equally** (same % of each item across partners) — though IRS in practice focuses on the first two prongs.
- Each partner **timely filed** their own 1040 and **fully reported** their distributive share.

Cite: Rev. Proc. 84-35, IRM 20.1.2.3.3.1. The relief is **automatic** — partnership never owed the penalty in the first place. Request via Form 843 referencing Rev. Proc. 84-35; attach partner filing proof.

IRS narrowed enforcement starting ~2017 (some agents claim Bipartisan Budget Act of 2015 superseded 84-35 — it did not; CCA 202017005 confirmed). If denied administratively, escalate to Appeals; if still denied, Tax Court has reliably sided with taxpayers. Don't give up after the first denial letter.

### Other statutory exceptions worth checking

- §6651(h) — no FTP penalty during an installment agreement in good standing.
- §6724(a) — §6721/6722 relief for reasonable cause "and not willful neglect."
- §6664(c) — no §6662 accuracy penalty for reasonable cause + good faith.
- §7508 / §7508A — combat zone / disaster relief; automatic time-extension.

## Path 2 — First-Time Abate (FTA)

Administrative relief, IRM 20.1.1.3.3.2.1. No substantive defense required. Available for:

- §6651 (FTF/FTP individual)
- §6698 (FTF partnership)
- §6699 (FTF S-corp)
- §6656 (FTD — deposit penalty)

Requirements:
- **Clean compliance history** — no penalties for the **prior 3 years** (some exceptions: estimated-tax penalties don't count; very small estimated-tax assessments may be waived).
- **All required returns filed** (or on valid extension).
- **All tax paid or in arrangement** (installment agreement counts).

FTA is a one-shot per entity per rolling 3-year window. Use it when the facts don't support reasonable cause — don't "waste" it on a year where RC would win anyway.

Request: call Practitioner Priority Service (PPS, 866-860-4259) with POA on file — often granted on the phone. Otherwise Form 843 or a plain-paper letter.

## Path 3 — Reasonable cause

Facts-and-circumstances. IRM 20.1.1.3.2. Standard: taxpayer exercised **ordinary business care and prudence** but was nonetheless unable to comply.

Accepted facts (weight varies):
- Serious illness / death / incapacity of taxpayer or immediate family
- Natural disaster, casualty, fire
- Unavailability of records outside taxpayer's control
- Reliance on competent tax professional **for a substantive determination** (not for clerical filing — *Boyle* rule, 469 U.S. 241 — taxpayer personally responsible for knowing deadlines even if CPA missed them)
- Erroneous IRS written advice (§6404(f))
- First-year filer confusion + good-faith attempt
- Undue hardship (§6161 standard)

**Rejected** reasons: ignorance of the law, workload, reliance on software, reliance on professional's timeliness (*Boyle*), reliance on e-filing service that failed silently.

Structure the letter as: facts → ordinary-business-care analysis → authority → request. Attach documentation. Sign under penalties of perjury if making factual claims.

## Form 843 — the vehicle

Form 843 is used for:
- Refund of already-paid penalty
- Abatement of assessed-but-unpaid penalty (check line 1 box accordingly)
- Claim for refund of interest (rare — requires IRS error)

Key fields:
- **Line 3** — type of tax / return (e.g., "Form 1065, 2023 Tax Year")
- **Line 4** — IRC section of penalty being abated (e.g., "§6698")
- **Line 5a box** — reason: "Interest, penalties or additions to tax caused by IRS errors or delays, or erroneous written advice" / "Reasonable cause" / "Other" (Rev. Proc. 84-35 claims typically "Other" with explanation)
- **Line 7** — explanation — keep concise, reference a detailed attachment

**Mail** to the IRS Service Center that processes the underlying return (not a single address). 843 is not e-fileable. Certified mail with return receipt; keep the green card as proof of filing.

Refund SOL is §6511 — 2 years from payment date OR 3 years from return filing, whichever is later. Penalty assessments without an underlying return (stand-alone assessments) use the 2-year-from-payment clock.

## Appeals if denied

Response letter denying 843 includes appeal rights. File written Appeals request within 30 days (or 60 for some notice types). Appeals gives a fresh-eyes review — success rate materially higher than initial determination. Fast-Track Settlement available for qualifying cases.

## What to produce

At `<scope>/FY<YYYY>/annual/workpapers/penalty-abatement/` (or at `<scope>/<penalty-abatement-matter-name>/` if cross-year):

- `decision-memo.md` — penalty assessed, path chosen, authority, expected outcome
- `form-843-<type>-<year>.pdf` — the form
- `attachment-explanation.pdf` — the narrative with citations
- `exhibits/` — filing proofs, POA (Form 2848) if needed, medical records, IRS correspondence, partner 1040s (for Rev. Proc. 84-35)
- `transmittal.md` — where mailed, date, certified-mail tracking, expected response window (typically 60-120 days)

## Traps

- **FTA burn**: don't consume FTA on a year where Rev. Proc. 84-35 or reasonable cause would win anyway. Agents sometimes grant FTA silently when another path was better preserved. Insist on Rev. Proc. 84-35 first in writing.
- **Partner-filing proof for 84-35**: IRS wants evidence each partner timely filed their 1040. Pulling partner transcripts (Form 4506-T) is the cleanest — see `irs-transcripts.md`.
- **Penalty paid under protest**: paid penalties are refundable via 843 within §6511; don't assume "already paid means gone."
- **Stacked penalties**: §6698 + interest can itself generate §6651 if paid late; abate the root penalty and interest follows under §6601(e).
- **§6662 accuracy penalty with disclosure**: Form 8275 / 8275-R adequate-disclosure filed with the original return reduces/eliminates §6662 exposure — too late to add post-filing but relevant for reasonable-cause analysis.
- **Appeals rejection after 843 denial**: next step is refund suit in District Court or Court of Federal Claims (§7422) — not Tax Court (no jurisdiction over refunds already paid).

## Cite correctly, always

Agents deny boilerplate reasonable-cause letters at high rates. Cite specific facts, specific authority (Rev. Proc., IRM section, case), specific sections of the Code the penalty was imposed under, and respond to the specific basis given in any denial letter. Quality of write-up materially changes outcome.

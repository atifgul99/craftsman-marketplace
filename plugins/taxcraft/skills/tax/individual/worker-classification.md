
# Worker Classification (Form 8919, SS-8)

Owns the case where the taxpayer was treated as a contractor but was, in
substance, an employee. A properly classified contractor is `schedule-c.md`.

⚠ **The payer side** — a business that issued 1099s and may owe employment tax,
§3509 rates, §530 as a defense, the VCSP — is **not built in this skill**. Say so
rather than improvising, and route the payer to their own advisor.

## 1. Classification is a determination, not an election

A misclassified worker pays **both halves** of FICA through SE tax instead of one
half through withholding. **Form 8919** reports the compensation as **wages** on
Form 1040 line 1g and computes only the **employee share** of the uncollected
Social Security and Medicare tax, flowing to Schedule 2.

⚠ **The taxpayer does not get to choose Schedule C because it produces a better
number.** Determine the correct classification on the facts (§2); the reporting
follows.

That said, the consequences must be **disclosed** before filing, because people
expect Form 8919 to be a pure win:

- The taxpayer pays materially less payroll tax — ⚠ though **less than "half,"**
  because the Schedule C alternative applies SE tax to 92.35% of net earnings and
  returns half above the line under §164(f). **Compute the differential; do not
  anchor on "half."**
- ⚠ **Loses Schedule C**, so business expenses become nondeductible (unreimbursed
  employee expenses remain suspended — **§67(g) for 2018–2025, §67(h) for years
  beginning after 12/31/2025**).
- ⚠ **Loses the QBI deduction** on that income.
- The filing tells the IRS the payer misclassified them, which the IRS may pursue
  — a live consideration when the relationship continues.

Model both so the taxpayer understands the economics. But if the facts say
employee, the answer is employee: a worse tax result is not a basis for reporting
as a contractor, and doing so knowingly is a position without support.

## 2. The test

Common-law control (Rev. Rul. 87-41, refined into behavioral control, financial
control, and the relationship of the parties). No factor is dispositive and the
count does not decide it — ⚠ **behavioral control usually carries a case.**

⚠ Practical notes:

- **A written agreement calling the worker a contractor does not control**, and
  neither does a 1099 having been issued.
- **Statutory employees** (certain drivers, full-time life insurance agents, home
  workers, traveling salespeople) — W-2 with box 13 checked, Schedule C for
  expenses but **no SE tax**. ⚠ Consequence people miss: statutory-employee
  Schedule C income produces **no net earnings from self-employment**, so it
  **cannot fund a SEP or solo 401(k)**.
- **Statutory nonemployees** — qualified real estate agents and direct sellers —
  are contractors **by statute** regardless of the common-law facts.
- ⚠ **State tests differ and are often stricter** (an ABC test), so a worker can be
  an employee for state purposes and a contractor federally.

## 3. Form 8919 and Form SS-8

⚠ **Form 8919 requires a qualifying reason code, and most conditions require more
than the taxpayer's own conclusion.** The conditions are:

- an **IRS determination or correspondence** establishing employee status;
- the worker was **previously treated as an employee** by the same firm for
  substantially similar services;
- the worker **filed Form SS-8 and has not received a determination** — filed **on
  or before** the return;
- the firm issued **both a W-2 and a Form 1099** for the same year for the same
  services.

⚠ **Read the current Form 8919 instructions for the letter assigned to each
condition** — the letters are a form mechanic subject to `authority.md`. What
matters is that **there is no code for "I concluded I was an employee."**

**Form SS-8** requests a determination. ⚠ It is **not a prerequisite** to
Form 8919 (the SS-8-pending condition is one of several). The IRS **notifies the
payer** and solicits their side — not anonymous, and it frequently ends the
engagement. It takes many months; do not hold a return for it. A determination
addresses the periods and facts submitted and supports the worker's position **for
those years**; what is limited is its effect on the firm and its bindingness on
other periods.

**§530 relief** protects the **payer** — reasonable basis, consistent treatment,
consistent 1099 filing — and is why many payers face no employment-tax liability
even where the worker was an employee. It does not affect the worker's return.
⚠ **The carve-out that matters: §530(d) denies relief for technical service
workers** — engineers, designers, drafters, computer programmers, systems
analysts, and similarly skilled workers — **where services are provided to a
client through a third party.** For staffing-agency and contract-technical
arrangements the payer has **no §530 shelter**, which changes the practical
consequence of an SS-8 entirely.

## 4. Detection

The return usually reveals it: a **1099-NEC from a single payer** that looks like
a full-time job, with no other clients and no business expenses; ⚠ **a W-2 and a
1099-NEC from the same payer in one year** (the "bonus paid on a 1099" pattern,
almost always wrong — and itself a qualifying condition); Form 8919 on a **prior**
return (`year-over-year.md`); and compensation on a 1099 that should have been
**wages after termination**, such as severance or a lost-wages settlement
(`job-loss.md`).

## 5. Workpaper

`wp-worker-classification.md`:

```json
{
  "engagements": [{"payer_slug": "", "form_received": "1099-NEC|1099-MISC|W-2|none",
                   "amount": 0,
                   "control": {"behavioral": "", "financial": "", "relationship": ""},
                   "written_agreement_says": "",
                   "statutory_employee": null, "statutory_nonemployee": null,
                   "legal_classification_determination": "employee|contractor",
                   "determination_basis": "",
                   "form_8919_qualifying_condition": "irs_determination|prior_employee_same_firm|ss8_pending|w2_and_1099_same_firm|none",
                   "form_8919_reason_code_per_current_form": "",
                   "form_ss8_filed": null, "ss8_filed_on_or_before_return": null,
                   "additional_medicare_8959_effect": 0,
                   "comparison": {"as_schedule_c": {"se_tax": 0, "expenses_deducted": 0,
                                                    "qbi": 0, "net_tax": 0},
                                  "as_8919": {"employee_share_only": 0,
                                              "expenses_lost": 0, "qbi_lost": 0,
                                              "net_tax": 0},
                                  "disclosed_to_taxpayer": null,
                                  "note": "economic modeling only — does not determine classification"},
                   "state_test_differs": null, "section_530d_technical_services": null,
                   "relationship_ongoing": null}]
}
```

**Invariants:** the **legal classification is determined first**, on the control
facts, and recorded separately from any economic comparison; a Form 8919 position
names the **qualifying condition** and the letter from the current form (the
SS-8-pending condition requires the filing date on or before the return); the
economic comparison is disclosure, **never** the basis for classification; the
loss of expenses and QBI is quantified; the Additional Medicare effect carries to
Form 8959; a W-2 and 1099-NEC from the same payer in one year is always examined.

Verify with a licensed practitioner before filing. Where the relationship
continues or a payer dispute is likely, the taxpayer may want counsel before
filing an SS-8.

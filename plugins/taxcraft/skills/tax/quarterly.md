# Installment and Quarterly-Close Computation

Invoke this reference through `close-estimate.md`. It covers individual §6654
installments, corporate §6655 installments, entity quarterly-close outputs, and
separately applicable state estimates. It does not authorize journal posting,
filing, portal use, or payment.

## Entry gates

1. Resolve taxpayer/entity, tax classification, tax year, fiscal-year start and
   end, installment number, and as-of date.
   `tax_year` is the year the tax period begins, not the year it ends. Calendar,
   fiscal, and short periods are distinct; a noncalendar result requires
   current run-specific due-date authority and chronology within the tax
   period. A short-year result also requires verified target-period form output
   rather than the ordinary four-equal-installment shortcut. Distinguish a
   month-based fiscal year from a valid 52/53-week year under §441(f); do not
   approximate either from a 365/366-day count. A 52/53-week record must carry
   its elected ending month, elected weekday, and `NEAREST_MONTH_END` or
   `LAST_WEEKDAY_IN_MONTH` method. Duration and weekday continuity alone are
   insufficient; validate the period end against the elected month-end rule
   and require the period to begin the day after the preceding elected
   year-end so no week is omitted or duplicated. For a READY result, bind the
   entire tax-period contract to FINAL reviewed evidence for the same subject,
   including valid adoption/election or approved-change evidence when the
   period is not already established by filed history and the books. Form 1128
   or consent evidence is required when applicable; dates copied into a new
   workpaper are not proof. A §441(f) record must separately evidence that the
   taxpayer regularly computes income on the elected 52/53-week basis in its
   books; election or change approval alone is insufficient.
2. Apply `authority.md`. Final 2026 Forms 2210/2220 and final instructions were
   not available as of 2026-08-25; a 2026 penalty-form implementation remains
   planning-only until the final applicable form is verified.
3. Require the status/evidence controls in `close-estimate.md`.
4. For book-derived current-year or annualized methods, require the applicable
   reconciliation gates. Proposed journal entries are not posted entries.
5. Determine each method's eligibility and status before calculating or
   comparing amounts.

## Periods are method-specific

Do not use one “quarter” table for individuals and corporations.

### Individual §6654 / Form 2210 Schedule AI

The cumulative annualization periods are generally:

| Installment | Income period | Annualization factor | Regular cumulative fraction |
|---|---|---:|---:|
| 1 | Jan 1–Mar 31 | 4 | 25% |
| 2 | Jan 1–May 31 | 2.4 | 50% |
| 3 | Jan 1–Aug 31 | 1.5 | 75% |
| 4 | Jan 1–Dec 31 | 1 | 100% |

These are cumulative installment periods, not equal calendar quarters. Use the
target-year Form 2210/Schedule AI for special filers and exact line mechanics.

### Corporate §6655 / Form 2220 Schedule A

Installments are generally due on the 15th day of the 4th, 6th, 9th, and 12th
months of the corporation's tax year, subject to current weekend/holiday and
special-year rules.

| Option | Annualization months | Factors | Election gate |
|---|---|---|---|
| Standard | 3 / 3 / 6 / 9 | 4 / 4 / 2 / 1.33333 | Default |
| Option 1 | 2 / 4 / 7 / 10 | 6 / 3 / 1.71429 / 1.2 | Timely Form 8842 |
| Option 2 | 3 / 5 / 8 / 11 | 4 / 2.4 / 1.5 / 1.09091 | Timely Form 8842; verify filer eligibility |

Do not substitute individual 3/5/8/12-month periods for the corporate standard
option.

## Individual installments — §6654

### Required annual payment alternatives

Compute eligibility before amount:

1. **Prior-year method** — tax shown on an eligible filed prior-year return
   covering 12 months, generally multiplied by 100% or 110% based on prior-year
   AGI; apply the MFS threshold separately. A prior estimate, draft return, or
   unverified software number is not sufficient evidence.
2. **Current-year method** — generally 90% of current-year tax under the exact
   target-year Form 1040-ES/Form 2210 line contract.

The required annual payment is the smaller available statutory amount. If one
method is unavailable, do not represent it as zero.

Apply the target-year no-required-payment threshold and other statutory
exceptions before recommending an installment.

### Required installments

The regular installment is generally one fourth of the required annual payment.
Schedule AI is not a third safe harbor or a third required annual payment. It
can produce a lower required installment for a period, subject to the form's
carryforward/catch-up mechanics. The controlling installment is the exact Form
2210 result after applying available alternatives.

Withholding is generally treated as paid one fourth on each installment date
under §6654(g), unless the taxpayer substantiates and elects the permitted
actual-date treatment. Estimated payments count when made and are applied under
the governing rules. Do not simply subtract a generic YTD-withholding total.

## Corporate installments — §6655

### Required annual payment and regular installments

- Current-year corporate tax uses 100%, not the individual 90% label.
- The prior-year method requires a 12-month prior return and positive prior-year
  tax, plus all other applicable eligibility rules.
- A large corporation under §6655 may generally use prior-year tax only for the
  first installment and must recapture the difference in the second installment.
- Derive large-corporation status from the applicable modified taxable income
  for each of the three preceding tax years (or each completed preceding year
  if fewer), excluding the prescribed NOL and capital carryback/carryover
  effects. Preserve predecessor history and any controlled-group allocation of
  the threshold; an untyped “taxable income” line or self-asserted boolean is
  not an eligibility test. A first-year corporation can have zero completed
  preceding years and no fabricated history.
- A zero-tax or short prior year does not create a zero prior-year method.
- For a corporate prior-year amended return, record the reviewed filing/effective
  date and use it only where the applicable Form 2220 rule treats an amendment
  filed before the installment due date as controlling. For an individual,
  Form 2210's original/superseding-return rules are separate and must be
  independently verified; do not reuse the corporate timing rule.
- Apply the target-year $500 threshold and exact Form 2220 tax-line mechanics.

Regular installments are generally 25% of the required annual payment, adjusted
for large-corporation and prior-installment mechanics.

### Annualized and adjusted-seasonal methods

The Form 2220 Schedule A result compares the regular installment with available
annualized-income and adjusted-seasonal results for that installment. These are
not separate safe harbors. Enforce Form 8842 elections, extraordinary-item
rules, NOL/§481 adjustments, credits, tax type, and option-specific periods.

Payments apply chronologically under the applicable rules; do not assume a
later payment ends exposure merely at the next quarter or filing date.

## Entity-classification gates

- **C corporation** — run §6655 where required.
- **S corporation** — do not say categorically that no federal estimate exists.
  Test entity-level built-in-gains tax, excess-net-passive-income tax,
  investment-credit recapture, and other current Form 1120-S taxes; estimated
  payments may apply when the applicable threshold is met. A released numeric
  entity-level result uses an independently reviewed Form 2220 output workpaper
  whose subject, tax year, cumulative period, and form identity match the run.
- **Partnership** — generally no federal income-tax estimate, but separately
  test §1446 withholding, state PTE tax, composite/withholding obligations, and
  partner-level §6654 projections.
- **Disregarded entity** — route federal income-tax installments to its regarded
  owner while retaining any state-level separate obligations.

## Quarterly close flow

For entity book outputs:

1. Require the canonical account roster and complete source-period manifest.
2. Validate parsed inputs and active/superseded versions.
3. Classify transactions; unreviewed, personal, capital, loan, equity,
   intercompany, transfer, and tax-payment candidates remain quarantined.
4. Prepare proposed accrual, noncash, and consolidation entries. This skill does
   not post them; a separately authorized bookkeeping workflow must post and
   return independent evidence before they are treated as posted.
5. Produce period and YTD P&L, balance sheet, and GL from approved entries.
6. Require debits = credits, assets = liabilities + equity, exact cash
   reconciliation after identified timing items, and applicable subledger,
   intercompany, payroll, fixed-asset, capital/basis, and tax controls.
7. Run `variance.md`; unsupported drivers remain `UNEXPLAINED` and unequal
   periods are normalized or not compared.
8. Only then expose current-year/AI inputs to the estimate engine.

A balanced trial balance alone is not a reconciled close. Any changed source,
classification, rule, or journal entry reopens dependent outputs.

## Recommendation contract

For each method show:

- eligibility and method status;
- inputs and provenance;
- form line or formula;
- required annual payment, where applicable;
- required installment before payments;
- treatment of withholding/credits/prior payments;
- amount due for this installment, floored at zero only after the full formula;
- authority IDs and limitations.

Compare only eligible methods. A provisional lower amount cannot displace an
available verified amount. Label the recommendation with the estimate status
from `close-estimate.md`; the maximum agent-generated status is
`READY_FOR_PRACTITIONER_REVIEW`.

### Canonical structured profiles

The canonical JSON may release a numeric method only through one of the
profiles in `templates/estimate.schema.json`; narrative formulas are not an
execution path:

- `INDIVIDUAL_REGULAR_EQUAL_INSTALLMENTS` — reviewed prior- or current-year
  tax line multiplied by the exact verified §6654 percentage, divided into
  regular installments.
- `CORPORATE_REGULAR_NON_LARGE_EQUAL_INSTALLMENTS` — reviewed corporate tax
  line, verified §6655 percentage, non-large-corporation eligibility, and the
  exact corporate due-date dependency.
- `CORPORATE_LARGE_REGULAR_RECAPTURE` — reviewed current/prior tax and
  large-corporation test lines; prior-year relief is limited to the first
  installment and the second installment recomputes the required recapture.
- `VERIFIED_FORM_OUTPUT` — independently reviewed Form 2210 or Form 2220 output
  lines for required annual, current-installment, and cumulative amounts.
  Standard Form 2220 annualization and adjusted-seasonal output do not require
  Form 8842. Option 1 or Option 2 requires reviewed evidence of the selected
  option and a timely Form 8842 filing no later than the verified first required
  installment deadline.
- `STATE_SPECIFIC_VERIFIED_OUTPUT` — independently reviewed state-form output,
  isolated to the requested state component with state-specific method and due
  date authority.

Every released method must trace entity type, filing status, document metadata,
operand lines, payment or withholding records, and each used rule to active,
independently reviewed evidence. `OBSERVED_ZERO` means a reviewed zero;
`NOT_PRESENT`, `UNREADABLE`, and `NOT_APPLICABLE` remain `null`. A form-output
profile cannot consume projected, user-reported, legacy-unverified, superseded,
or contradicted source inputs as verified evidence.

Withholding is either ratable under the governing default or supported by
dated records plus an evidence-bound actual-date election. Payment credit is
limited to records whose confirmation, settlement, application date, taxpayer,
form, period, amount, tax year, and target installment reconcile through the
applicable cutoff. A later payment cannot be back-credited to an earlier
installment.

State results remain separate and require current state authority. Never write
“file via” or “pay via” as an instruction to execute. Explain available methods
and stop before portal access or transmission. This skill has no execution mode.
Federal regular/Form 2210/Form 2220 profiles cannot support a state component;
state estimates use `STATE_SPECIFIC_VERIFIED_OUTPUT` and state-specific
run-authority records. Bundled federal rules never authenticate a state amount.

## Artifacts

When persistence is authorized:

- control workpaper from `templates/close-estimate-control.md.template`;
- canonical estimate JSON from `templates/estimate.template.json`;
- presentation from `templates/quarterly-estimate.md.template`;
- P&L, balance sheet, GL, and projected K-1s only for applicable entity closes.

Create `quarterly-payment.md` only after the user reports a payment or supplies
evidence. Recommendation, authorization, scheduling, confirmation, bank
settlement, correct-period application, and reconciliation are different states.

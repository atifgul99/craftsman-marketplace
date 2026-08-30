
# Year-over-Year Comparison

Owns the line-by-line comparison across filed years. It is a **drift detector**,
not a computation: it finds what silently changed or disappeared.

Two uses:

1. **Onboarding** — the first deliverable in prior-return mode
   (`onboarding.md` §3), and the honest answer to "help me understand my
   situation."
2. **Annual preflight** — `individual/1040.md` §1 Step 1.6.

## 1. Why this catches things nothing else does

Most individual tax errors are **omissions**, and an omission leaves no trace on
the return where it belongs. It only shows up as a **discontinuity against the
prior year**: a K-1 that stopped arriving, a rental that stopped depreciating, an
election that lapsed, a carryforward that reset to zero.

A single year's return always looks internally consistent. Two years side by side
do not.

## 2. What to compare

Build the comparison at three levels.

**Forms and schedules filed.** The presence or absence of a form is the highest-
signal row in the whole exercise:

| Change | Question it forces |
|---|---|
| Schedule E present last year, absent now | Property sold? K-1 not received? Or missed? |
| Form 8606 last year, none now | Was there no activity, or was basis dropped? |
| Form 8938 last year, none now | Did the asset fall below the threshold, or was the filing missed? **§6501(c)(8)** holds the whole return open |
| FinCEN 114 last year, none now | Did the account close, or was the FBAR missed? Its own Title 31 penalty regime applies — **it does not trigger §6501(c)(8)** (`records.md` §9) |
| Form 6198 / 8582 disappeared | Was a loss released — or lost track of? |
| Form 8919 present in any year | Worker classification still live? → `worker-classification.md` |
| A new state return | Residency or source change → `state-residency.md` |
| Form 2210 penalty in consecutive years | Structural under-withholding → `withholding-penalties.md` |

**Carryforwards — the continuity test.** Every carryforward must tie:
prior ending = current beginning. Check capital loss by character; NOL by
vintage; passive and at-risk **by activity**; §163(j) by entity; charitable by
class; AMT credit; §199A negative; **foreign tax credit by basket (§904(c), with
the §6511(d)(3) ten-year claim window)**; **§163(d) disallowed investment
interest**; **general business credit (§39)**; **§461(l) EBL converted to NOL**;
the **§179 amount disallowed by the business-income limit**; and **every lifetime
basis track** in `individual/1040.md` §5 (there are more than three).

**A carryforward that resets to zero without a consumption event is a defect, not
a fact** — and so is one that **appears or increases with no generating event**,
which is the signature of a transcription error or a double-counted K-1. Test both
directions.

**Line-level deltas** with a materiality threshold. Explain every large change
and every unexplained small one. The pattern that matters is not the size of the
change but whether there is a **reason** for it.

**Standing facts.** Filing status, dependents, address and state, elections
visible on the return (§469 grouping, §199A aggregation, QJV, §59(e),
mark-to-market), and the preparer. An election that appears in one year and not
the next either lapsed or was forgotten — both are findings.

## 3. Reconcile to the IRS, not only to the copy on hand

The return in the file may not be the return that was filed or the one currently
assessed. Where transcripts are available, compare against the **Account
Transcript** (adjustments, penalties, payments the taxpayer never noticed) and
the **Wage & Income Transcript** (third-party documents that never arrived).
→ `scenarios/irs-transcripts.md`.

Note the timing constraint: W&I is not complete until roughly May of Y+1 **and
continues to accrete through Y+2** (`individual/1040.md` §2.3). For a multi-year
comparison the accretion is the relevant half — an older year's W&I is more
complete than a recent one's.

## 4. Turning findings into actions

Each finding resolves to exactly one of these six:

- **No action** — explained by a real event, recorded with the explanation.
- **Current-year correction** — the item belongs on the return being prepared.
- **Amended or superseding return** — with the §6511 clock tested first
  (→ `notices-amendments.md`).
- **Prior-year error identified but not correctable** — the year is closed, or
  correction is not worthwhile. Circular 230 §10.21 still requires advising the
  taxpayer. Sets `PRIOR_YEAR_ERROR_IDENTIFIED` (`individual/1040.md` §8).
- **Protective claim** — where §6511 is closing on an amount that depends on an
  unresolved contingency (→ `notices-amendments.md`,
  `scenarios/contested-k1.md`).
- **Permanent record to capture** — a basis figure or election recovered from an
  old return that belongs in `individual/records/` (→ `records.md`).

That last one is often the most valuable output: an old return is frequently the
**only** surviving evidence of a lifetime basis figure, and transcripts do not
show Form 8606.

## 5. Extraction discipline

Extract with `pdftotext -layout` per `parsing.md`, never the built-in Read. Every
figure carries a page reference and a field state from `estimate.md`. Anything
illegible is `UNREADABLE` and blocks the dependent conclusion.

**Do not infer a carryforward from a summary page.** A carryforward not evidenced
on the return is `NOT_PRESENT`, and a missing one is a hold, not a zero.

## 6. Workpaper

`wp-year-over-year.md`:

```json
{
  "years_compared": [],
  "source": [{"tax_year": null, "document": "return_copy|return_transcript|record_of_account",
              "filed_date": "", "amended": null, "superseded": null}],
  "forms_matrix": [{"form": "", "present_by_year": {}, "discontinuity": null,
                    "explanation": ""}],
  "carryforward_continuity": [{"type": "", "detail": "",
                               "prior_ending": 0, "current_beginning": 0,
                               "ties": null, "consumption_event": ""}],
  "line_deltas": [{"line": "", "prior": 0, "current": 0, "delta": 0,
                   "material": null, "explanation": ""}],
  "standing_facts": [{"fact": "", "by_year": {}, "changed": null,
                      "election_lapsed": null}],
  "irs_reconciliation": {"account_transcript_pulled": null,
                         "wage_income_pulled": null, "wage_income_complete": null,
                         "irs_adjustments_found": [],
                         "third_party_docs_not_received": []},
  "findings": [{"finding": "", "severity": "",
                "action": "none|current_year|amend|supersede|protective_claim|prior_year_error|capture_record",
                "section_6511_open": null, "recorded_in": ""}]
}
```

**Invariants:** every carryforward ties prior-ending to current-beginning or names
a consumption event; every form discontinuity is explained; every finding
resolves to exactly one action; a §6511-closed year is marked as such rather than
silently dropped; permanent facts recovered from prior returns are written to
`individual/records/`, not left in the comparison.

Verify with a licensed practitioner before filing.

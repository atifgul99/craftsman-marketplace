
# State Residency and Multi-State Filing

Owns the **decisions**: who is a resident of where, what must be filed, and how
the pieces reconcile. `scenarios/multi-state.md` remains the quick framework and
state-quirk table; state depth lives in `states/<xx>/`.

⚠ **No state's rules are hardcoded here.** Every threshold, rate, filing
requirement, and form is state- and year-specific → `authority.md`.

## 1. Three independent questions

A taxpayer can be a resident of two states at once. Answer in order.

**Domicile** — the one place intended as a permanent home; it persists until a
new one is **established** (abandonment alone is not enough), requiring both
presence and intent. Evidence weighs roughly: home and its relative value, family
location, time spent, "near and dear" items, business ties. Secondary indicators
(licenses, registration, accounts, memberships, where estate documents are
executed) matter in aggregate as evidence of intent. ⚠ **High-tax states audit
this aggressively and put the burden on the taxpayer claiming a change — the
record must be built in the year of the move, not reconstructed later.**

**Statutory residency** — a purely mechanical second test in many states:
a permanent place of abode **plus** more than a threshold number of days. ⚠ **A
taxpayer domiciled elsewhere can be a statutory resident and taxed on worldwide
income anyway.** Day-counting is state-specific and unforgiving (a partial day is
often a full day), and the burden is the taxpayer's — contemporaneous calendars,
travel, and toll data are the case.

**Source** — independent of residency; sourced income can create a nonresident
obligation wherever the taxpayer lives.

## 2. Filing map

| Situation | Files |
|---|---|
| Resident all year | Resident return on worldwide income; credit for taxes paid elsewhere |
| Part-year | Part-year return in each state, allocated by period of residency |
| Nonresident with source income | Nonresident return per source state above its threshold |
| ⚠ Statutory resident **and** domiciliary of another state | **Both** resident returns — the classic double-tax trap; relief depends on each state's credit rules |
| No-income-tax resident state | No resident return, **but nonresident returns may still be required** |

⚠ A no-income-tax state is not a no-tax state: a separate **capital-gains excise**,
a **state estate or inheritance tax** (often far below the federal threshold and
frequently **without portability** → `estate-gift.md`), intangibles or franchise
taxes reaching individuals, and **local income taxes** with their own residency
rules.

## 3. Sourcing

| Income | Sourced to |
|---|---|
| Wages | Where services are **performed** — not where the employer is |
| Remote work | Where performed; ⚠ but a **convenience-of-the-employer** rule in some states sources telecommuting days to the employer's location, producing genuine double taxation |
| Business / self-employment | Where the business operates, apportioned |
| Rental real estate, and its sale | Where the property is |
| Pass-through | Per the entity's apportionment schedule |
| Interest, dividends, securities gains | Generally the **residence** state |
| Retirement income | ⚠ **4 U.S.C. §114 bars a state from taxing a nonresident's qualified retirement income** — a federal override. Also protects qualifying nonqualified deferred comp paid in substantially equal installments over 10+ years or after separation. → `retirement.md` |
| Equity compensation | Allocated by **workdays between grant and vest** (sometimes vest and exercise) |

⚠ **Equity comp is the most commonly mishandled item for anyone who has moved.
The employer's W-2 state allocation is frequently wrong and does not bind the
taxpayer.** Capture the workday history at grant, not at sale.

## 4. Credit for taxes paid to other states

⚠ Rarely a full offset. Generally the **lesser of** the tax actually paid or the
resident state's tax on that income; available only for income sourced under the
**resident** state's rules, which may differ from the other state's — **where they
differ the mismatch is not creditable and double tax is real**. Ordinarily
unavailable where the resident state has no income tax. Some states apply a
**reverse credit**. Entity-level taxes usually produce a **credit**, not a
payment by the owner — confirm per state.

## 5. Pass-through: composite, withholding, PTET

Three mechanisms, frequently confused:

| Mechanism | Individual consequence |
|---|---|
| **Nonresident withholding** | Owner still files; the withholding is a credit |
| **Composite return** | Owner generally does not file individually — ⚠ but usually pays at the **top rate** with no deductions, credits, or losses |
| **PTET election** | Entity pays and deducts **federally** (Notice 2020-75); owner takes a state credit — moving the deduction outside the **SALT cap** (`itemized.md`) |

⚠ Decisions the individual owns: **opting out of a composite** is often better
when the owner's actual rate is below the composite rate, when they have losses or
credits in that state, or when an individual return is needed anyway for the
resident credit. **PTET is usually beneficial while the SALT cap binds — but check
whether the *resident* state grants a credit for another state's PTET; several do
not, converting a federal saving into a state cost.** Capture the K-1 state
schedule every year → `pass-through.md`, `ptp.md`.

## 6. Residency changes

The move year is the highest-risk state year.

1. **Fix and document the change date** — everything allocates around it.
2. **Allocate by period of residency**, not a day ratio, wherever traceable
   (wages by pay period, gains by transaction date, K-1 per the entity's periods
   where permitted).
3. **Time recognition around the date** where legitimate — recognizing a large
   gain after establishing residency in a no-tax state is ordinary planning, but
   the change must be genuine and documented **first**.
4. ⚠ **Trailing nexus** — the former state may continue to tax source income,
   deferred comp vesting from prior services, and installment gain from a pre-move
   sale.
5. **Close the old ties.** The audit case is built from what was kept.

## 7. Community property

⚠ **MFS or RDP filers in a community-property state must allocate on Form 8958** —
not optional, commonly skipped (`1040.md` §1). ⚠ **Community-property titling
also changes basis at death, and that can outweigh every income-tax
consideration in this section** — the rule and its consequences are owned by
`estate-gift.md` §2; load it before advising any retitling. ⚠ A **qualified joint venture** is the
**§761(f)** election — available to spouses who both materially participate,
regardless of community-property status. **Rev. Proc. 2002-69** is a different
regime: entity **classification** for a business wholly owned by spouses as
community property. Do not cite one for the other. **§66(c)** relief →
`life-events.md` §1.

## 8. Workpaper

`wp-state.md`:

```json
{
  "residency": [{"state": "", "basis": "domicile|statutory|nonresident",
                 "period_from": "", "period_to": "", "day_count": null,
                 "permanent_abode": null, "domicile_change_date": null,
                 "evidence": []}],
  "filings_required": [{"state": "", "return_type": "resident|part_year|nonresident|composite_covered|none",
                        "threshold_met": null, "form": "", "due_date": ""}],
  "sourcing": [{"state": "", "income_type": "", "amount": 0,
                "sourcing_rule": "", "workday_allocation": null,
                "section_114_protected": null}],
  "credits": [{"resident_state": "", "other_state": "", "tax_paid": 0,
               "resident_state_tax_on_same_income": 0, "credit_allowed": 0,
               "mismatch_not_creditable": 0}],
  "pass_through": [{"entity": "", "state": "", "withholding": 0,
                    "composite_participation": null, "opt_out_evaluated": null,
                    "ptet_paid": 0, "ptet_credit": 0,
                    "resident_state_credits_other_state_ptet": null}],
  "community_property": {"applicable": null, "form_8958_required": null},
  "non_income_state_taxes": [{"state": "", "tax": "", "applies": null,
                              "separate_return_required": null}]
}
```

**Invariants:** every state in `sourcing` appears in `filings_required` with a
decision (including an explicit "none" and why); wage sourcing is by workday, not
the W-2 boxes alone, wherever the taxpayer worked in more than one state;
equity-comp uses the grant-to-vest workday history; a statutory-resident
determination is supported by a substantiated day count; the credit is computed
under the **resident** state's sourcing rules; composite participation is a
recorded decision, not a default; PTET is tested for a resident-state credit
before being treated as a saving; retirement income is tested against 4 U.S.C.
§114 before any nonresident state taxes it.

Verify with a licensed practitioner before filing. Residency disputes are
fact-intensive and often need state-specific counsel.

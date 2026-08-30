# VC/PE Fund K-1 Scenario

Relevant to LP investments in VC/PE funds (e.g., Beacon Venture Partners, Indus Valley Capital, Numerical, KOP II non-O&G portions).

## Classification

- Typically **limited partner** → passive per §469(h)(2); losses suspended against other passive income
- Income often **portfolio** (interest, dividends, gain) flowing through boxes 5, 6a/6b, 8, 9a — not passive, classified per character at the fund level
- **Allocation waterfall** — partnership agreement governs; K-1 reflects result. Don't try to re-compute.

## Common Issues

### §1202 QSBS Pass-through
- Fund may hold QSBS-eligible stock and pass-through the exclusion on sale to LPs; look for a footnote/supplemental schedule disclosing QSBS gain and report on Form 8949/Schedule D accordingly.

See scenarios/qsbs-1202.md for full §1202/QSBS qualification rules, the pre-/post-7/5/2025 regime split, §1045 rollover, and stacking strategies.

### §1045 Rollover
- If fund sells QSBS < 5 yrs, LP can elect §1045 rollover within 60 days — hard in practice from fund position; usually fund does it

### PFIC Exposure
- Fund invests in offshore → passive-foreign-investment-company
- Form 8621 required per PFIC — punitive default regime (§1291) or QEF / Mark-to-Market elections
- Look for footnote; fund usually provides PFIC statement or QEF information statement
- Missing PFIC disclosure is a **major audit/penalty risk**

### UBTI / UBIT
- Only matters if LP is tax-exempt or held via self-directed IRA
- Blocker corps common in PE to shield UBTI
- If LP interest is in self-directed IRA → file Form 990-T; tax at trust rates

### Foreign Tax Credit
- K-1 boxes 16/20 — foreign-source income + foreign taxes
- Form 1116 (passive basket for most portfolio) — per-country detail required above de minimis
- Election to claim as itemized deduction (rarely better)

### Management Fee / Investor Expenses
- Box 13 codes for §212 investment expenses — **NOT deductible** for individuals; the misc. itemized deduction subject to the 2%-of-AGI floor is **permanently suspended** under OBBBA (PL 119-21) §70110 — **§67(g)** for tax years 2018–2025, **§67(h)** for years beginning after Dec 31, 2025 (OBBBA PL 119-21 §70110 redesignated it and inserted a new §67(g), "Educator expenses") — not a TCJA-temporary provision set to expire after 2025

### §1061 Carried Interest (3-Year Rule)
- Applies to fund managers, not LPs — but if LP has GP-interest component, watch
- Requires 3-yr hold on sold assets for LTCG

### State Apportionment
- Fund may allocate income across states where portfolio companies operate
- K-3 / state schedule required for some
- Composite or PTE-tax election common; verify not double-counting

## K-2 / K-3

Required since 2021 for partnerships with international items (or potential international items for LPs). LP should insist on receiving K-3 — delays common. If fund claims domestic-filing exception, verify before relying on absence.

## Capital Account

Tax-basis capital account rollforward is required for partnerships since 2020:
- Beginning + contributions + income share − distributions − loss share = Ending

Capital account ≠ outside basis. Outside basis also includes share of liabilities. For a typical LP in PE fund, no liabilities allocated → outside basis ≈ capital account. Verify.

## Review Output

```json
{
  "entity": "Indus Valley Capital II LP",
  "tax_year": 2024,
  "classification": "limited-portfolio",
  "pfic_statement_received": null,
  "qsbs_gain_passed_through": 0,
  "foreign_tax_credit_available": 0,
  "§212_expenses_non_deductible": 0,
  "capital_account_ending": 0,
  "outside_basis_ending": 0,
  "flags": ["confirm K-3 received", "verify no PFIC exposure"]
}
```

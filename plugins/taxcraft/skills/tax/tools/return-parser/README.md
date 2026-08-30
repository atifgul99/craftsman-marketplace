# return-parser

Parse filed **Form 1065 / 1120 / 1120-S** return PDFs into structured JSON.

Auto-detects the form from the page-1 header and extracts header metadata,
page-1 P&L lines, key schedules (B, K, J, L, M-1, M-2), partners/K-1 summary
rows, and raw STMT-page text blocks.

Built on top of the shared `pdf-extractor/pdf_extract.py` (pdftotext -layout);
does **not** do its own PDF parsing.

## Library use

```python
from return_parser import parse_return

result = parse_return("/path/to/return.pdf")
print(result["doc_type"], result["entity_name"], result["entity_ein"])
print(result["page_1_pnl"]["ordinary_income_loss"])
```

Return value is a `dict` conforming to the schema documented below.

## CLI

```bash
# Human-readable summary
python3 return_parser.py "path/to/return.pdf"

# Full JSON
python3 return_parser.py "path/to/return.pdf" --json

# Skip the interactive confirmation (for scripts / pipes)
python3 return_parser.py "path/to/return.pdf" --no-confirm --json
```

The confirmation prompt only fires when stdin is a TTY.

## Output schema

```jsonc
{
  "doc_type": "1065-Return | 1120-Return | 1120-S-Return",
  "tax_year": 2024,
  "entity_name": "...",
  "entity_ein": "XX-XXXXXXX",
  "fiscal_period": {"begin": "2024-01-01", "end": "2024-12-31"},
  "preparer": "self | firm",         // "self" if 'Self-Prepared' appears
  "return_type": "original | amended",
  "page_1_pnl": {
    "gross_receipts": 0,
    "cogs": 0,
    "gross_profit": 0,
    "total_income": 0,
    "total_deductions": 0,
    "ordinary_income_loss": 0
  },

  // 1065 and 1120-S only
  "schedule_b_elections": {
    "accounting_method": "cash|accrual|null",
    "aggregated_activities": false,
    "any_partner_amended_k1": false,
    "bba_opt_out_6221b": false
  },
  "schedule_k_separately_stated": {
    "line_1_ordinary": 0, "line_2_rental_re": 0, "line_5_interest": 0,
    "line_6a_ord_div": 0, "line_6b_qual_div": 0,
    "line_8_st_cap": 0, "line_9a_lt_cap": 0, "line_10_1231": 0,
    "line_12_179": 0, "line_13_other_ded": 0,
    "line_19_distributions": 0, "line_20_other": []
  },
  "schedule_m2_capital": {
    "beginning": 0, "contributions": 0, "net_income": 0,
    "distributions": 0, "ending": 0
  },

  // 1120 only (replaces schedule_k / schedule_m2_capital)
  "schedule_j": {
    "income_tax": 0, "total_tax_before_credits": 0,
    "total_tax": 0, "total_payments_credits": 0
  },
  "retained_earnings_m2": {
    "beginning": 0, "net_income_per_books": 0, "other_increases": 0,
    "distributions": 0, "other_decreases": 0, "ending": 0
  },

  // Shared
  "schedule_l_balance_sheet": {
    "beginning": {"total_assets": 0, "total_liab": 0, "total_capital": 0},
    "ending":    {"total_assets": 0, "total_liab": 0, "total_capital": 0}
  },
  "schedule_m1_book_tax": {
    "net_income_per_books": 0,
    "additions": [], "subtractions": [],
    "income_per_return": 0
  },
  "partners": [
    {
      "name": "...",
      "ein_ssn": "XXX-XX-XXXX",
      "pct_profits_end": 25.0,
      "pct_loss_end": 25.0,
      "pct_capital_end": 25.0,
      "final_k1": false
    }
  ],
  "stmt_pages": { "Statement 1": "raw text...", ... },
  "anomalies": []
}
```

`partners[]` is populated from Schedule K-1 blocks on 1065 and 1120-S returns;
empty for 1120. `stmt_pages` contains unstructured text of "Statement N"
attachments keyed by header.

## Design notes

- **Amount parsing** is deliberately conservative. To avoid picking up form
  references (`Form 1125-A`, `Schedule PH (Form 1120)`) or line-label ids
  (`22`, `11a`) as dollar values, the parser requires each amount token to
  look like a real US dollar amount (thousands-comma, decimal fraction,
  parentheses, `$`, leading `-`, or >= 4 digits). Bare short integers with
  only a trailing period are rejected.
- **Column position**: amounts are accepted only when preceded by
  whitespace / dot-leader / `$` / `(`, i.e. they sit in the right-aligned
  number column, not glued into a word.
- **Resilience**: every extractor returns 0 or null on miss and appends a
  note to the `anomalies` list when a required value can't be found. The
  parser never raises on a malformed form.
- **Preparer detection** keys on the literal `Self-Prepared` string
  (TurboTax convention). Firm-prepared returns fall through to `"firm"`.
- **Fiscal period** extraction understands the TurboTax header form
  `beginning Dec 4, 2024, ending Oct 31, 20 25` as well as straight
  calendar-year returns.

## Dependencies

- Python 3.9+
- `pdftotext` (poppler-utils; `brew install poppler`)
- The sibling `pdf-extractor/pdf_extract.py` module

No third-party Python packages.

## Sample invocations

```bash
# Partnership return
python3 return_parser.py \
  "entities/<slug>/tax/FY2024/filed/FY2024 - 1065 - Return_Records.pdf" \
  --no-confirm --json

# C-corp return
python3 return_parser.py \
  "entities/<slug>/tax/FY2024/filed/FY2024 - 1120 - TurboTax - Return_Records.pdf" \
  --no-confirm --json
```

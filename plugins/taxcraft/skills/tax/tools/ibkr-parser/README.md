# IBKR Statement Parser

Parse Interactive Brokers **Activity Statement** CSVs into a normalized
`{transactions, summary, validation}` dict. The CSV is the primary source; if
the matching PDF is supplied we cross-check a handful of summary totals and
flag any mismatch.

> **Paths below are written from this tool's own directory.** The skill installs as a
> plugin outside your workspace, so a bare `python3 ibkr_parser.py` will not resolve from
> where you are standing. Set `TAX_SKILL="${CLAUDE_PLUGIN_ROOT}/skills/tax"` once and
> address the script as `"$TAX_SKILL/tools/ibkr-parser/ibkr_parser.py"`. Arguments are the other way
> round: they are workspace paths, resolved against the current directory.

## Install / layout

```
<tax-skill>/tools/
  ibkr-parser/
    ibkr_parser.py   <-- this tool
    README.md
  pdf-extractor/
    pdf_extract.py   <-- used for PDF validation
```

No `pip install`. Needs Python 3.9+ and (for PDF validation) `pdftotext` from
`poppler-utils` (`brew install poppler`).

## Library usage

```python
from ibkr_parser import parse_ibkr

result = parse_ibkr("path/to/statement.csv",
                    pdf_path="path/to/statement.pdf")  # pdf optional

for tx in result["transactions"]:
    print(tx["date"], tx["type"], tx["symbol"], tx["amount"])

print(result["summary"])            # realized_pl, dividends, interest, fees, nav
print(result["validation"]["match"]) # True / False / None (None if no PDF)
```

## CLI usage

```
python3 ibkr_parser.py <statement.csv> [--pdf <statement.pdf>] \
                        [--out <result.json>] [--no-confirm]
```

Interactive flow (default): prints a summary table showing section counts and
totals; waits for `y` / `e` / `s` (write / dump-to-stdout / skip) before
writing `<statement>.json`.

Use `--no-confirm` in scripts / batch jobs.

## Output schema

```json
{
  "doc_type": "IBKR-Statement",
  "account_id": "U1234567",
  "period_start": "2025-09-01",
  "period_end": "2025-09-30",
  "currency": "USD",
  "transactions": [
    {
      "type": "trade|dividend|interest|fee|deposit|withdrawal|corporate_action",
      "date": "2025-09-30",
      "symbol": "SNOW 21NOV25 240 C",
      "description": "...",
      "quantity": 2.0,
      "price": 10.82,
      "proceeds": -2164.0,
      "commission": -1.4013,
      "realized_pl": 0.0,
      "asset_category": "STK|OPT|FUT|BOND|CASH",
      "currency": "USD",
      "amount": -2165.4013
    }
  ],
  "summary": {
    "realized_pl": 0.0,
    "total_dividends": 0.0,
    "total_interest": 45.43,
    "total_fees": -204.68,
    "net_deposits": 100000.0,
    "ending_nav": 100257.96
  },
  "validation": {
    "csv_totals": { "change_in_nav.Ending Value": 100257.96, ... },
    "pdf_totals": { "change_in_nav.Ending Value": 100257.96, ... },
    "match": true,
    "mismatches": []
  },
  "non_usd_amounts": [],
  "anomalies": []
}
```

## Sections recognized

| IBKR section              | Emitted `type`                |
|---------------------------|-------------------------------|
| Trades                    | `trade`                       |
| Dividends                 | `dividend`                    |
| Interest                  | `interest`                    |
| Fees / Broker Fees / Commission Details | `fee`             |
| Deposits & Withdrawals    | `deposit` / `withdrawal`      |
| Corporate Actions         | `corporate_action`            |

Summary-only sections (`Net Asset Value`, `Change in NAV`, `Cash Report`,
`Mark-to-Market Performance Summary`, `Realized & Unrealized Performance
Summary`, `Open Positions`, `Interest Accruals`, `Financial Instrument
Information`, `Codes`, `Notes/Legal Notes`) are not turned into transactions
but their totals feed `validation.csv_totals`.

## Rules

- **Non-USD**: any transaction with `currency != "USD"` is copied into
  `non_usd_amounts`. No FX conversion is ever performed silently.
- **PDF validation**: best-effort regex over `pdftotext -layout` output; only
  a small fixed set of labelled totals are checked (Starting Value, Ending
  Value, Mark-to-Market, Commissions, Deposits & Withdrawals, Starting Cash,
  Ending Cash). Mismatches beyond `$0.02` tolerance land in
  `validation.mismatches`.
- **Idempotent**: parsing the same CSV twice produces byte-identical JSON.
- **First Header wins** per section: IBKR emits multiple Header rows inside
  one section (e.g. `Mark-to-Market Performance Summary` has two). The first
  is the transactional one; subsequent ones are ignored.

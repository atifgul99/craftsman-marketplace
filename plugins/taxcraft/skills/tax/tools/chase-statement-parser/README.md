# Chase Statement Parser

Generic parser for JPMorgan Chase business bank statements and credit-card statements. Produces unified, reconciled transaction ledgers that can feed balance-sheet and P&L reconstruction for any entity.

## When to use

- Remediating past-year tax filings where books were never maintained
- Reconstructing transaction history from statements + CSV exports
- Building audit-defensible workpapers from raw Chase docs
- Cross-checking a CSV's completeness against monthly PDFs

## What it handles

| Source | Support |
|---|---|
| Chase Business Complete Checking — monthly PDFs | ✓ |
| Chase Ink Business Card — monthly PDFs | ✓ |
| Chase checking CSV exports | ✓ |
| Chase CC CSV exports | ✓ |
| Chase Private Client / personal checking | untested, may work |
| Non-Chase banks (BoA, Wells, etc.) | no |

## What it does NOT handle

- Categorizing transactions into chart-of-accounts buckets (see tax skill `reconciliation.md`)
- Intercompany elimination (e.g., CC payments funded from the operating checking account — book as internal transfer, not P&L)
- Brokerage statements (IBKR, Schwab, etc.)
- Parsing check images or wire confirmation PDFs

## Requirements

- Python 3.9+
- `pdftotext` (from poppler-utils) — `brew install poppler` on macOS

## Usage

Write a thin per-entity driver script that configures accounts and calls `build_ledgers`. Example — `entities/<slug>/books/transaction-ledgers/regenerate.py`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[4]  # adjust depth to point at workspace root
sys.path.insert(0, str(WORKSPACE / ".claude" / "skills" / "tax" / "tools" / "chase-statement-parser"))

from chase_parser import build_ledgers

ACCOUNTS = {
    "1234": {
        "label": "chase-1234",
        "type": "checking",                     # "checking" or "credit_card"
        "pdf_glob": ["entities/foo-llc/accounts/chase-1234/statements/*.pdf"],
        "csv_path": "entities/foo-llc/accounts/chase-1234/all-transactions.csv",
        "output_dir": "entities/foo-llc/books/transaction-ledgers",
        "yearly_slice_template": "entities/foo-llc/tax/FY{year}/source/bank-cc/chase-1234.csv",
    },
    # ... more accounts ...
}

if __name__ == "__main__":
    build_ledgers(ACCOUNTS, workspace_root=str(WORKSPACE))
```

Run: `python3 regenerate.py`

Idempotent — overwrites ledger and validation files each run. Re-run whenever new PDFs or CSV updates are dropped.

## Output per account

- `<output_dir>/<label>-unified-ledger.csv` — master chronological transactions with running balance (all years)
- `<output_dir>/<label>-validation.md` — statement-by-statement reconciliation report
- `<yearly_slice_template>` (one per tax year) — year-filtered CSV slice for reconciliation workpapers; derived, regenerable

## Validation

Every PDF statement is reconciled to the penny at parse time:
- Checking: `beginning_balance + sum(statement_txns) == stated_ending_balance`
- Credit card: `previous_balance - sum(statement_txns) == stated_new_balance`

PDF-vs-CSV overlap is checked; PDF is used for pre-CSV dates, CSV for CSV-era dates. No double-counting.

Validation reports are human-readable — check them after every regeneration.

## Sign conventions

**Checking** (`amount` column):
- Positive = credit to account (deposit, ACH credit, refund)
- Negative = debit from account (check, wire out, card purchase, fee)

**Credit card** (`amount` column):
- Positive = payment (reduces outstanding balance)
- Negative = purchase / fee / interest (increases outstanding balance)

Sign convention chosen to match Chase's CSV export for both account types.

## File naming convention

For the parser to find PDFs reliably, store them as:

```
<YYYY-MM-DD>-chase-<last4>-<optional-label>-statement.pdf
```

Examples:
- `2023-06-30-chase-1234-statement.pdf`
- `2024-04-24-chase-5678-cc-statement.pdf`
- `2023-11-30-chase-9012-<entity-slug>-statement.pdf`

The date in the filename is the statement close date. The parser extracts actual period dates from inside the PDF — filename is just for sorting.

## Failure modes to watch for

- **Year drift on cycle-crossing months**: CC statements span mid-month to mid-month; if the `Opening/Closing Date` line changes format in a new Chase template, transactions near year boundaries (Dec/Jan) can be assigned the wrong year. Inspect validation report — if statement balances stop matching, check a boundary-crossing PDF manually with `pdftotext -layout`.
- **New section names**: checking PDFs use `*start*<section>` / `*end*<section>` markers. If Chase adds a new section type (e.g., "wire transfers"), transactions in that section are silently skipped. Update `CREDIT_SECTIONS` / `DEBIT_SECTIONS` sets in `chase_parser.py`.
- **Scanned / image PDFs**: this parser uses `pdftotext -layout` which only works on text PDFs. If you download a scanned copy, it returns empty. Always verify source is text-based before ingesting.

## Extending to other banks

The architecture (parse → merge PDF+CSV → validate against statement balances → write unified CSV + report) is bank-agnostic. To add a new bank:
1. Copy `chase_parser.py` to `<bank>_parser.py` in a sibling directory under `tools/`.
2. Adjust the section markers and regexes for that bank's statement format.
3. The `build_ledgers` orchestration can stay as-is; only the per-statement parsing changes.

For non-Chase banks, plan for a few days of iteration against real statements — every bank's PDF layout is different.

# Tax Skill Tools

Executable utilities bundled with the tax skill. Reusable across any workspace that adopts the skill — unlike entity-specific workpapers, these belong with the skill itself so the logic travels with the skill, not with any one user's data.

Tools live here when they're general-purpose (work for multiple entities across any workspace), format-bound (parse a specific document type with stable conventions), and likely to be re-run as new data arrives. Tools that are truly workspace-specific belong outside the skill.

## Available tools

| Tool | Purpose | Entry |
|---|---|---|
| [chase-statement-parser](chase-statement-parser/) | Parse Chase bank + credit-card PDFs and CSV exports into unified reconciled transaction ledgers | `chase_parser.py` (import as library) |
| [pdf-extractor](pdf-extractor/) | Auto-fallback PDF reader — text extraction via `pdftotext`; falls back to PNG rasterization for scanned docs. Use for any PDF in the workspace (filed returns, K-1s, IRS letters, 8822-B, check images). | `pdf_extract.py` (CLI + library) |
| [k1-parser](k1-parser/) | Parse Schedule K-1 (Form 1065 / 1120-S) PDFs into the `parsing.md` K-1-1065 JSON schema. Handles single-K-1 PDFs and multi-K-1 filing packages (`--multi`). | `k1_parser.py` (CLI + library) |
| [return-parser](return-parser/) | Parse filed entity returns (1065 / 1120 / 1120-S) into the `parsing.md` `1065-Return` / `1120-Return` schema. Auto-detects form type; captures page-1 P&L, Schedule K/L/M-1/M-2, Schedule J, partner list, Schedule B elections. | `return_parser.py` (CLI + library) |
| [transcript-parser](transcript-parser/) | Parse IRS Account / Tax Return / Wage & Income / Record of Account transcripts. Extracts TC codes + cycle dates, flags exam/freeze/lien indicators. TC code lookup in `tc_codes.json`. | `transcript_parser.py` (CLI + library) |
| [ibkr-parser](ibkr-parser/) | Parse Interactive Brokers monthly statement CSVs into a unified transaction ledger + summary. Uses the matching PDF for cross-validation; flags non-USD amounts. | `ibkr_parser.py` (CLI + library) |
| [coa-categorizer](coa-categorizer/) | Rule-based GL-bucket classifier for raw transaction rows (Chase checking/CC output). Produces enriched CSV with `gl_account`, `gl_code`, `confidence`, `needs_review` columns + a review summary. Seed rules in `default_rules.json`; override per entity. | `coa_categorizer.py` (CLI + library) |
| [workspace-doctor](workspace-doctor/) | Report-only health check for workspace layout — missing workspace-profile files, non-kebab-case entity dirs, corporate-intake folders (entities/*/corporate/**) with PDFs but no `_processed.log`, empty `.parsed/` caches, sync-conflict litter, loose K-1/tax PDFs, stray `__pycache__`, poppler presence, per-entity `bean-check`, `xledger-check`, ledger-vs-CSV staleness. Never modifies anything; always exits 0. | `doctor.py` (CLI) |

## Running tools

All tools require **Python 3.9+** (standard library only — no `pip install`
needed for any tool in this directory unless its own README says otherwise).

Invoke tools with `python3 -B` (or set `PYTHONDONTWRITEBYTECODE=1`) so Python
doesn't write `__pycache__/` bytecode caches into the tree — this workspace
lives on OneDrive, and `.pyc` churn there causes needless sync conflicts.
`__pycache__/` and `*.pyc` are also covered by the skill's `.gitignore` as a
second line of defense; `workspace-doctor` (below) flags any that slip
through.

```bash
python3 -B k1_parser.py "path/to/k1.pdf"
```

## Design principles

1. **Library first, driver second.** Each tool is a library (parseable + importable). Per-entity driver scripts live with that entity's data (`entities/<slug>/books/...`) and just configure + invoke the library. Keeps entity-specific config next to the entity, shared logic here.

2. **Validation is mandatory output.** Every tool that produces derived data also produces a validation report showing reconciliation against source-of-truth balances or totals. No silent failures.

3. **Deterministic + idempotent.** Re-running a tool with the same inputs produces the same outputs. Tools overwrite prior runs rather than appending.

4. **Source of truth is never overwritten.** Tools read from `tax/<year>/source/`, `accounts/`, etc., and write derived artifacts elsewhere. Raw source PDFs / CSVs are never modified.

5. **Reproducibility.** Each tool has its own README and a documented invocation pattern so future runs (or future people) can repeat the work without reverse-engineering.

## When to add a tool here vs. entity-local

**Add to the skill's `tools/`** if the utility is:
- General-purpose (works for multiple entities in any workspace)
- Format-bound (parses a specific document type with stable conventions)
- Likely to be re-run as new data arrives

**Keep entity-local** if the work is:
- One-off analysis specific to one entity + one year
- A hand-built workpaper (trial balance, Schedule L rec)
- Configuration that only makes sense in context (e.g., account list for a specific entity)

## Adding a new tool

1. Create `tools/<tool-name>/` folder.
2. Put the library code in a clearly named file (e.g., `<tool_name>.py`).
3. Write a `README.md` at minimum covering: purpose, usage, requirements, sign conventions, failure modes.
4. Add a row to the table above.
5. If the tool is load-bearing for tax work, cross-reference from the tax skill's own files where relevant.

## Not yet built

Prioritized against actual document volume seen in this workspace (individual `FY2023` / `FY2024` / `FY2025` docs/). P0 = blocks annual close or intake; P1 = reduces manual effort materially; P2 = nice-to-have.

| Priority | Tool | What it does | Blocked on |
|---|---|---|---|
| **P0** | W-2 parser | Parse boxes 1–12, state wages, box 14 into `parsing.md` W-2 schema. Essential for individual annual workpaper. | Schema defined; many clean samples in `individual/FY*/docs/` |
| **P0** | 1099-Composite parser | Single PDF from Fidelity / Chase / Morgan Stanley / IBKR with INT / DIV / B / foreign tax sections. Feeds Schedule B/D + Form 8949. | Schema defined in `parsing.md` |
| **P0** | 1099-R parser | Retirement-distribution forms — gross, taxable, withholding, box 7 distribution code. Affects taxable income + AGI. | Schema needed in `parsing.md` |
| **P0** | 1098 mortgage parser | Mortgage interest (box 1), property tax escrow (box 10), points, outstanding principal. Multi-property scope common. | Schema needed |
| **P1** | 1099-INT / 1099-DIV standalone | FirstTech / PenFed single-form statements — different layout from Composites. | Schema defined for Composite (reuse subsections) |
| **P1** | 1099-K parser | Payment-platform reporting (Zillow, Stripe, Venmo Business). Recently surfaced on IRS Wage & Income transcripts for this workspace. | Schema needed |
| **P1** | 5498 / 5498-SA parser | IRA/HSA contribution + FMV reports. Needed for Form 8606 basis tracking and HSA deduction. | Schema named in `parsing.md` "Other types"; needs expansion |
| **P1** | 1099-NEC / 1099-MISC parser (issued and received) | Simple 3-box layout. Issuer-side feeds Form 1096 summary; recipient-side goes to Schedule C / Schedule E. | Schema in `parsing.md` §"Other types" placeholder |
| **P2** | SSA-1099 parser | Social-security benefit statements — box 5 net benefits, box 6 voluntary withholding. | Schema needed |
| **P2** | Wire confirmation OCR | Extract amount + date from wire PDFs for capital-call evidence | `pdf-extractor` already handles OCR; needs thin wrapper + schema |
| **P2** | TurboTax `.tax20XX` reader | Decode filed TurboTax files into the same schema as `return-parser` output. | TurboTax format is proprietary; may require feature work in TurboTax Desktop export or a third-party library |

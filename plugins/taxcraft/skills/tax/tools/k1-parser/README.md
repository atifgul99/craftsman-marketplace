# K-1 Parser

Extract Schedule K-1 (Form 1065 or 1120-S) fields from a PDF into the `parsing.md` `K-1-1065` / `K-1-1120S` JSON schema.

## Purpose

Every K-1 received by an entity or individual flows into the enclosing scope's `tax-summary.md`. This tool extracts the structured fields (partner/issuer identity, boxes 1–20, capital account, liabilities, §199A codes) so the intake workflow can diff filed amounts against expected amounts and update workpapers without hand-typing.

## Library usage

```python
from k1_parser import parse_k1, parse_multi_k1

# Single-K-1 PDF (issued directly to a partner)
result = parse_k1("path/to/FY2024 - K-1 - LP - <sponsor-slug>.pdf")

# Multi-K-1 PDF (full 1065 return containing K-1 for each partner)
results = parse_multi_k1("path/to/2024 - Example Fund Records.pdf")
```

Returns a dict (or list) shaped per `parsing.md` §K-1-1065. Fields that cannot be detected are left as `null` / `0.0` and surfaced in the `warnings` list.

## CLI

```bash
python3 k1_parser.py "path/to/k1.pdf"                   # single-K-1: table + JSON printed, nothing written
python3 k1_parser.py "path/to/records.pdf" --multi      # multi-K-1 (one PDF per partner)
python3 k1_parser.py "path/to/k1.pdf" --json            # JSON only (no table, no prompt, no write)
python3 k1_parser.py "path/to/k1.pdf" --write           # confirmation table, then prompt to write to .parsed/
python3 k1_parser.py "path/to/k1.pdf" --write --no-confirm  # write disabled — prints table + JSON only
```

By default (no `--write`), the CLI prints the confirmation table (partner, issuer, boxes, capital, liabilities, warnings) followed by the full JSON and never writes anything — there is no prompt. `--json` suppresses the table and prints JSON only. The interactive `[yes / edit / skip]` write prompt only fires when `--write` is passed; without it nothing is ever written. `--no-confirm` combined with `--write` skips the prompt but also skips the write (the CLI falls through to printing table + JSON instead) — use `--write` alone to actually write interactively.

## Dependencies

- Python 3.9+ (stdlib only)
- `pdftotext` via `poppler-utils` (`brew install poppler` on macOS)
- Imports the sibling `pdf-extractor/pdf_extract.py` for the text-or-image fallback chain

## Disregarded-entity handling

K-1s routed through a disregarded SMLLC appear two ways:

1. **SMLLC as partner, regarded owner in Item H2** (e.g. a fund issues to SUB SMLLC with Item H2 = PARENT LLC): `partner_name = "SUB SMLLC"`, `disregarded_entity_name = "PARENT LLC"`.
2. **Regarded owner as partner, SMLLC in Item H2** (e.g. a fund issues to PARENT LLC with Item H2 = SUB SMLLC): `partner_name = "PARENT LLC"`, `disregarded_entity_name = "SUB SMLLC"`.

Either convention is valid — both TINs are captured.

## Validation warnings (non-fatal)

- `Final K-1 flagged` — entity exit, confirm with books
- `Partner TIN not detected` / `Issuer EIN not detected`
- `Tax year not detected`
- `Box 20 code Z (§199A) not found` — Statement A may be missing or on a continuation page

Warnings appear in the confirmation table **and** in `result["warnings"]`.

## Known limitations

- Two-column form layout is handled via column-range window scan; when the source PDF is heavily custom-formatted (non-Lacerte / non-CCH) the box scanner can miss or cross-talk between adjacent boxes. Always review the confirmation table before approving a write.
- Box 20 sub-codes are picked up but their per-code amounts are resolved from Statement A (`Rental income (loss)` line for Code Z). Other codes (AJ, N, ZZ, etc.) are surfaced as `{code, 0.0, "see statement"}` placeholders for manual review.
- Multi-K-1 detection splits on `Part III Partner's Share of Current Year Income`. Filed-copy PDFs sometimes include only one exemplar K-1 even for multi-partner returns; check against the partner roster on page 1.
- Image-only (scanned) K-1s will error — wire the `pdf_extract.extract` image path + Read-tool vision for that case.

## Output artifacts (on `--write` with confirmation)

`<scope>/FY<YYYY>/.parsed/<source-slug>.json` — one JSON file per K-1 matching the schema. The index at `<scope>/FY<YYYY>/.parsed/_index.json` is updated by the intake workflow, not by this tool directly.

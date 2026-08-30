# Parsing & PDF Discipline (single source of truth)

Owns: PDF read rules, parsed-cache index format, TTL classes, and per-doctype JSON schemas. Referenced by `init.md` (prior-return extraction) and `intake.md` (ongoing ingestion). Do not duplicate these rules elsewhere.

## Privilege Exclusion (STRICT)

Never parse, cache, or summarize any file under a path containing `privileged` (e.g. `*attorney-client-privileged*`). Privilege-waiver risk. Only proceed on explicit user instruction inside that matter's own persona. See SKILL.md → "Privacy & redaction".

## PDF read discipline (NEVER violate)

**Never use the built-in `Read` tool directly on structured PDFs** (K-1s, 1099s, W-9s, tax forms, Schedule L, etc.). It strips layout and silently misreads columns.

### Prerequisite

This chain requires **poppler** (`pdftotext`, `pdftoppm`). Everything else below is optional and probed at the moment it is needed.

```bash
command -v pdftotext pdftoppm    # both must resolve
# macOS: brew install poppler | Debian/Ubuntu: apt install poppler-utils
# Fedora: dnf install poppler-utils | Windows: choco install poppler
```

If poppler is missing, say so and stop — do not fall back to `Read`-on-PDF.

### The fallback ladder (always try in this order)

| # | Rung | Gate |
|---|---|---|
| 1 | `pdftotext -layout` → use the text | core |
| 2 | Rasterize to PNG → `Read` the image (vision) | core |
| 3 | `ocrmypdf` → re-run rung 1 | `command -v ocrmypdf` |
| 4 | `pdfplumber` table extraction | `python3 -c 'import pdfplumber'` |
| 5 | Locally-configured OCR command | see "Machine-local tools" below |
| 6 | Ask the user; log to `open-questions.md` | core |

Stop at the first rung that yields trustworthy output. **Do not skip ahead to rungs 3–5 because a document "looks scanned"** — rung 2 resolves the large majority of scanned tax forms, and it reads layout directly rather than reconstructing it from OCR'd text, which is why it outranks every OCR-based rung for form-shaped documents.

Probe a gate only when you actually reach that rung. There is no upfront capability scan.

**Rung 1 — text extraction:**
```bash
pdftotext -layout "<path>.pdf" -
```
If this returns meaningful content (not empty, not just metadata), use it.

**Rung 2 — rasterize and read:**
```bash
# All pages, straight to PNG (add -f N -l M for a page range)
pdftoppm -png -r 200 "<path>.pdf" /tmp/<prefix>
# Then: Read each /tmp/<prefix>-*.png via the Read tool
```

**The Read-tool-on-image path is acceptable and reliable** for scanned PDFs, IRS letters, check images, and any document where pdftotext returns nothing. The prohibition is specifically against Read-on-PDF for STRUCTURED tax forms where `pdftotext -layout` would give a better result.

**Rung 3 — OCR a scanned PDF in place**, only if rung 2 was unreadable:
```bash
command -v ocrmypdf && ocrmypdf --skip-text "<path>.pdf" /tmp/<name>-ocr.pdf \
  && pdftotext -layout /tmp/<name>-ocr.pdf -
```

**Rung 4 — stubborn table grids** where the values are legible but columns won't align:
```bash
python3 -c 'import pdfplumber' 2>/dev/null && python3 - <<'PY'
import pdfplumber
with pdfplumber.open("<path>.pdf") as pdf:
    for p in pdf.pages:
        for t in p.extract_tables():
            print(t)
PY
```

**Helper utility**: see `tools/pdf-extractor/` in this skill for a wrapper that runs rungs 1–2 automatically and returns either extracted text or a list of PNG paths ready for Read.

### Machine-local tools (rung 5)

Some machines have a licensed desktop OCR application or a local OCR model that is better than rungs 3–4 but cannot be assumed to exist. If `.claude/tax-pdf-tools.local.md` is present at the workspace root, read it and follow the commands it defines; if it is absent, skip rung 5 entirely.

That file is **machine-specific and is not part of this skill** — never move its contents into this directory, and never hardcode an application path, license detail, or OS-specific automation here.

A fully-local extractor does **not** create an exception to "Privilege Exclusion (STRICT)" above. It only changes *which tool* may be used once the user has explicitly authorized work inside a privileged matter.

### When every rung fails

If no rung yields trustworthy output (very-low-resolution scan, handwriting, corruption):
- Ask the user to supply the critical values directly, or page screenshots.
- Document the gap in `open-questions.md`.

**Never silently skip a load-bearing doc. Never proceed with null-as-zero carryforwards.**

### Verify before writing (every extraction, every rung)

Extraction confidence is never a substitute for verification. Confidence comes from two
independent layers, and **Layer B is the one that earns its keep** — it catches errors that
every extractor would reproduce identically, including the issuer's own.

| Layer | Question it answers | Tool |
|---|---|---|
| A — differential extraction | Did we *read* it correctly? | `tools/pdf-extractor/compare.py` |
| B — invariants | Can this document be internally consistent *at all*? | `tools/parse-verify/verify.py` |

**Layer A** runs the PDF through independent extractors and reports only the figures they
disagree about, narrowing a whole document to the few worth checking by eye:

```bash
python3 -B "$TAX_SKILL/tools/pdf-extractor/compare.py" "<file>.pdf"          # exit 1 if engines disagree
python3 -B "$TAX_SKILL/tools/pdf-extractor/compare.py" "<file>.pdf" --pngs   # + page images for a vision pass
```

Two extractors agreeing does **not** mean the figure is right. If the issuer printed a wrong
number, every engine reproduces it faithfully and they all agree.

**Layer B** runs after the doc is normalized into `.parsed/`, and tests arithmetic and tax-law
invariants that hold regardless of who did the reading — capital-account rollforward under either
sign convention, §704(d) loss-vs-basis, outside basis against capital + liability share (§722/§752),
Schedule L balance, M-2 rollforward and its tie to Schedule L, and cross-document footing of every
issued K-1 to Schedule K:

```bash
python3 -B "$TAX_SKILL/tools/parse-verify/verify.py" <scope>/FY<YYYY>/.parsed/    # exit 1 if findings
python3 -B "$TAX_SKILL/tools/parse-verify/verify.py" <file>.json --min-severity HIGH
```

**Run Layer B before a parse is treated as final**, and again after any workpaper edit that
touches K-1 or return figures. A CRITICAL finding means the document contradicts itself — do not
write it into a workpaper until it is resolved or explicitly accepted in `open-questions.md`.

Neither layer decides anything. Both produce leads:

- **Cross-reference against independent data** — bank/brokerage transactions, the prior year's workpapers, or the issuer's own summary page. A figure that reconciles to nothing is unverified, whatever the extractor reported.
- **On K-1s, confirm these fields individually** rather than trusting a whole-form read: Box 1 (ordinary), Box 2 (rental RE), Box 4a/4c (guaranteed payments — services vs capital), Box 19 (distributions), and the liabilities block (nonrecourse / QNR / recourse).

  Boxes 4a/4c and 19 are the classic confusion pair: **guaranteed payments are not distributions**. So are liabilities and income — a liabilities figure misread as income silently inflates the return. Both misreads are common enough in practice to check for by name rather than trusting a clean-looking extraction.
- Any figure that cannot be reconciled → `open-questions.md`, not the workpaper.

## Parsed-cache index

Each scope-year has `<scope>/FY<YYYY>/.parsed/_index.json` + one JSON file per parsed doc at `<scope>/FY<YYYY>/.parsed/<slug>.json`. Slug format lives in `naming.md` ("Parsed cache slugs").

**This is the only sanctioned parse-cache location.** `.txt` sidecars dropped next to source PDFs and ad-hoc dirs like `books/parsed-cache/` are violations, not alternatives. Real-workspace audits show empty `.parsed/` dirs while ad-hoc `.txt` dumps accumulate elsewhere — a sign the cache is being skipped, not that it doesn't apply. **Before parsing any PDF, check `_index.json` first** (`intake.md` Step 2) — never re-parse blind.

**Migrating legacy dumps**: when a stray `.txt` sidecar or ad-hoc cache dir is found, fold its content into `.parsed/<slug>.json` + `_index.json` (move the content in — don't just leave a pointer). Never delete the original file without user confirmation; leave it in place or move it to `archive/` until confirmed.

### Index entry shape (`templates/parsed-index.template.json`)

```json
{
  "source_path": "<path relative to workspace root>",
  "canonical_name": "<filename per naming.md>",
  "sha256": "<hex>",
  "size_bytes": 0,
  "doc_type": "W-2 | K-1-1065 | 1099-Composite | ...",
  "tax_year": 2025,
  "scope": "individual | <entity-slug>",
  "parsed_at": "2026-04-14",
  "ttl_class": "immutable | correctable | annual | quarterly | manual",
  "parsed_file": ".parsed/FY2025-w2-<slug>.json",
  "superseded_by": null
}
```

### TTL classes (when to re-parse)

| Class | Rule |
|---|---|
| `immutable` | Re-parse only on sha256 change. (W-2 after Feb 15; 1098; final 1099s; K-1s after issuer files.) |
| `correctable` | Provisional through Mar 15; re-check each ingest run. (Early 1099s.) |
| `annual` | Re-parse each year. (County assessments.) |
| `quarterly` | Re-parse each quarter. (Brokerage statements.) |
| `manual` | User-flagged one-offs, **IRS transcripts** (updated weekly by IRS; re-parse only on explicit pull). |

**Refresh trigger**: size or sha256 drift from the indexed entry → mark stale, re-parse.

## Parsed JSON schemas

### Field-state and legacy-parser containment (STRICT)

The numeric `0` values in the legacy examples below show a numeric field's
location; they do **not** prove an observed zero. Existing parser versions may
coerce absent, blank, or unreadable values to zero and may omit source anchors,
active-version resolution, or document-direction fields. Therefore:

- any parsed artifact without a schema version and field-level state is
  `LEGACY_UNVERIFIED`;
- a legacy numeric field may enter a tax computation only after a reviewer ties
  it to the source page/line, distinguishes `OBSERVED_ZERO` from missing or
  unreadable, and records that decision in the downstream input manifest;
- missing, blank, invalid, statement-dependent, or unreadable values are never
  inferred as zero;
- `at_risk`, final/corrected status, document direction, liabilities, basis,
  and statement-required codes default to unknown unless evidenced;
- `_index.json` controls the one active version per logical document. A source
  hash change, corrected/amended document, unsupported schema, skipped file, or
  malformed JSON blocks final status;
- `tools/parse-verify/verify.py` is a useful invariant check, not proof of
  completeness for every form type. Unsupported or skipped validation cannot
  clear a parse.

New or upgraded parser schemas use this field envelope for load-bearing values:

```json
{
  "value": null,
  "state": "OBSERVED_VALUE | OBSERVED_ZERO | NOT_PRESENT | UNREADABLE | NOT_APPLICABLE | DERIVED | MANUAL_OVERRIDE",
  "source_anchor": {"page": null, "line_or_box": null},
  "confidence": null,
  "review": {"reviewer": null, "reviewed_at": null}
}
```

Until the parser tools emit and validate that contract directly, a computation
can at most be provisional unless every used legacy field is independently
verified. See `close-estimate.md` for downstream status precedence.

### W-2

```json
{
  "doc_type": "W-2", "tax_year": 2025,
  "employee": "<name>", "employer": "<name>", "ein": "XX-XXXXXXX",
  "box_1_wages": 0, "box_2_fed_wh": 0,
  "box_3_ss_wages": 0, "box_4_ss_tax": 0,
  "box_5_medicare_wages": 0, "box_6_medicare_tax": 0,
  "box_12": [{"code": "D", "amount": 0}],
  "box_14": [],
  "state_wages": [{"state": "XX", "wages": 0, "wh": 0}]
}
```

### K-1 (1065)

```json
{
  "doc_type": "K-1-1065", "tax_year": 2025,
  "partner_name": "<regarded owner>", "partner_ein_ssn": "XX-XXXXXXX",
  "disregarded_entity_name": null, "disregarded_entity_tin": null,
  "issuer_entity": "<partnership>", "issuer_ein": "XX-XXXXXXX",
  "entity_type": "operating|real-estate|oil-gas|vc-pe|commodity-pool",
  "partner_type": "general|limited|llc-member",
  "final_k1": false, "at_risk": true,
  "box_1_ordinary": 0, "box_2_rental_re": 0, "box_3_other_rental": 0,
  "box_5_interest": 0, "box_6a_ord_div": 0, "box_6b_qual_div": 0,
  "box_8_st_cap": 0, "box_9a_lt_cap": 0, "box_10_1231": 0,
  "box_11_other": [], "box_12_179": 0, "box_13_other_ded": [],
  "box_14_se": [], "box_16_intl": null, "box_17_amt_items": [],
  "box_19_distributions": 0,
  "box_20_codes": [{"code": "Z", "amount": 0, "note": "§199A"}],
  "states": [{"state": "XX", "apportioned_income": 0}],
  "capital_account": {"beginning": 0, "contrib": 0, "withdraw": 0, "net_income": 0, "ending": 0},
  "liabilities": {"nonrecourse": 0, "qnr": 0, "recourse": 0}
}
```

### K-1 (1120-S)

Same shape; no `capital_account`; no SE box (1120-S K-1 box 1 is not SE income).

### 1099-Composite

```json
{
  "doc_type": "1099-Composite", "tax_year": 2025,
  "recipient_name": "<scope>", "recipient_tin": "XX-XXXXXXX",
  "broker": "<name>", "account_last4": "1234",
  "1099_INT": {"box_1_interest": 0, "box_3_treasury": 0, "box_8_muni": 0},
  "1099_DIV": {"box_1a_total": 0, "box_1b_qual": 0, "box_2a_ltcg": 0, "box_3_nondiv": 0, "box_5_199A": 0},
  "1099_B": {
    "st_covered":    {"proceeds": 0, "basis": 0, "wash_sale": 0, "gain": 0},
    "lt_covered":    {"proceeds": 0, "basis": 0, "wash_sale": 0, "gain": 0},
    "st_noncovered": {"proceeds": 0, "basis": 0, "gain": 0},
    "lt_noncovered": {"proceeds": 0, "basis": 0, "gain": 0}
  },
  "foreign_tax_paid": 0
}
```

### Filed entity return (1065, 1120, 1120-S)

When parsing a previously-filed return PDF (e.g., `<year> <entity> Form 1065 ... _Records.pdf`), extract the whole return, not just individual forms. Used for remediation, diffing against reconstructed workpapers, and K-1 reconciliation.

```json
{
  "doc_type": "1065-Return | 1120-Return | 1120-S-Return",
  "tax_year": 2024,
  "entity_name": "<legal name>", "entity_ein": "XX-XXXXXXX",
  "fiscal_period": {"begin": "2024-01-01", "end": "2024-12-31"},
  "preparer": "<self | firm name>",
  "return_type": "original | amended | superseding",

  "page_1_pnl": {
    "gross_receipts": 0, "cogs": 0, "gross_profit": 0,
    "total_income": 0, "total_deductions": 0,
    "ordinary_income_loss": 0
  },

  "schedule_b_elections": {
    "accounting_method": "cash | accrual | other",
    "aggregated_activities": false,
    "any_partner_amended_k1": false,
    "bba_opt_out_6221b": false,
    "published_partnership_agreement_changes": false
  },

  "schedule_k_separately_stated": {
    "line_1_ordinary": 0, "line_2_rental_re": 0, "line_3_other_rental": 0,
    "line_4_guaranteed_payments": {"services": 0, "capital": 0},
    "line_5_interest": 0, "line_6a_ord_div": 0, "line_6b_qual_div": 0,
    "line_7_royalties": 0, "line_8_st_cap": 0, "line_9a_lt_cap": 0,
    "line_9b_collectibles": 0, "line_9c_unrecap_1250": 0,
    "line_10_1231": 0, "line_11_other_income": 0,
    "line_12_179": 0, "line_13_other_ded": 0,
    "line_14_se": {"a_net_se": 0, "b_gross_farm": 0, "c_gross_nonfarm": 0},
    "line_15_credits": 0, "line_16_intl_k2k3": null,
    "line_17_amt": 0, "line_18_tax_exempt": 0, "line_19_distributions": 0,
    "line_20_other": [{"code": "Z", "amount": 0, "note": "§199A"}]
  },

  "schedule_l_balance_sheet": {
    "beginning": {"total_assets": 0, "total_liab": 0, "total_capital": 0},
    "ending":    {"total_assets": 0, "total_liab": 0, "total_capital": 0}
  },

  "schedule_m1_book_tax": {
    "net_income_per_books": 0,
    "additions": [], "subtractions": [],
    "income_per_return": 0
  },

  "schedule_m2_capital": {
    "beginning": 0, "contributions": 0, "net_income": 0,
    "distributions": 0, "other_increases": 0, "other_decreases": 0,
    "ending": 0
  },

  "partnership_representative": {
    "name": "<name>", "tin": "XX-XXXXXXX", "us_address": "<addr>"
  },

  "partners": [
    {"name": "<partner>", "ein_ssn": "XXX-XX-XXXX",
     "pct_profits_end": 50.0, "pct_loss_end": 50.0, "pct_capital_end": 50.0,
     "final_k1": false, "amended_k1": false,
     "k1_filename_in_package": "<path>"}
  ],

  "elections_on_file": {
    "section_754": false, "section_59e": false,
    "section_199a_aggregation": null, "qjv_2002_69": false
  },

  "anomalies": []
}
```

1120 variant: swap `schedule_k_separately_stated` / `schedule_m2_capital` for **Schedule J** (tax computation), **Schedule M-2** (unappropriated retained earnings), book-to-tax M-1 / M-3.

1120-S variant: swap for **AAA rollforward**, **OAA** (Other Adjustments Account), **shareholder stock + debt basis** (from shareholder-level worksheet if attached).

### Other types

Define compact schemas on first encounter for: 1098, 1099-INT standalone, 1099-R, 5498, 5498-SA, 1095-A, SSA-1099, Schedule K-1 (1041), 1099-NEC, 1099-MISC, W-9, IRS account transcript, IRS wage-and-income transcript. Mirror box/line numbers 1:1.

## Name-level verification (on every parse)

After parsing, confirm:

- Canonical filename matches `naming.md` for this `doc_type` + tax_year.
- `recipient_tin` / `partner_ein_ssn` matches the scope's EIN/SSN. Mismatch → flag (common SMLLC W-9 error).
- `tax_year` matches the enclosing `FY<YYYY>` folder.

Any mismatch → do not silently import. Append to `open-questions.md` and ask.

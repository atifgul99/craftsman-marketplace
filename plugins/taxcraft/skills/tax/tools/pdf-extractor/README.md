# PDF Extractor

Auto-fallback PDF reader for the tax skill. Tries text extraction first (fast, perfect for e-filed returns, bank statements, K-1s from software-generated PDFs) and falls back to rasterized PNG output that Claude's vision can read (for scanned IRS letters, image-based forms, check scans).

> **Paths below are written from this tool's own directory.** The skill installs as a
> plugin outside your workspace, so a bare `python3 pdf_extract.py` will not resolve from
> where you are standing. Set `TAX_SKILL="${CLAUDE_PLUGIN_ROOT}/skills/tax"` once and
> address the script as `"$TAX_SKILL/tools/pdf-extractor/pdf_extract.py"`. Arguments are the other way
> round: they are workspace paths, resolved against the current directory.

## Why this exists

The skill's PDF discipline is:

1. Text PDF → `pdftotext -layout` (fast, accurate)
2. Image/scanned PDF → rasterize → Claude Read tool (vision)

Writing this chain manually every time is error-prone. This tool runs the chain once, chooses the right path, and hands back either text or a list of PNG paths ready for `Read`.

## Usage from Claude workflow

**As a library from Python (preferred — single call per doc):**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("/path/to/tax-skill/tools/pdf-extractor")))
from pdf_extract import extract

result = extract("/path/to/some-doc.pdf")
if result.mode == "text":
    text = result.text
    # parse text as usual
elif result.mode == "image":
    # result.pngs is a list of PNG paths; feed each into Claude's Read tool
    for png in result.pngs:
        # Claude reads each image via Read tool and extracts content
        pass
else:
    # result.diagnostics explains why
    pass
```

**As a CLI (shell / quick one-offs):**

```bash
# Auto fallback — prints text if extractable, else lists PNG paths to stderr
python3 /path/to/pdf_extract.py /path/to/doc.pdf

# Force image mode (for hybrid PDFs where you want visual parsing)
python3 pdf_extract.py doc.pdf --force-image

# Specific pages only
python3 pdf_extract.py doc.pdf --pages 1-3

# Higher resolution for small-print scans
python3 pdf_extract.py doc.pdf --dpi 300
```

## When text mode triggers fallback to image

The extractor runs `pdftotext -layout` and inspects the output. It falls back to rasterization if:

- `pdftotext` not installed
- `pdftotext` returns empty or near-empty output (<50 non-whitespace characters)
- Output is sparse relative to file size (<5 characters per KB of file — suggests image-heavy PDF with no OCR layer)
- Text-extraction process errored

These thresholds catch the common scanned-PDF case without false-positive fallback on short-but-valid PDFs.

## When to use `--force-image`

- Forms where layout fidelity matters more than extractable text (filled 8822-B, handwritten notes)
- Documents with embedded charts/diagrams the text layer won't convey
- Returns where checkboxes are meaningful (Sch B Q33 — has the opt-out box got a checkmark or "X"?)
- Anything you suspect has hidden text quirks

## Dependencies

- **pdftotext** and **pdftoppm** — from poppler: `brew install poppler` on macOS
- **sips** — built into macOS
- **pdfinfo** — also from poppler (used to detect page count)
- Python 3.9+ (stdlib only — no pip installs required)

No OCR binary needed. We use Claude's vision for text extraction from rasterized pages — more accurate than tesseract and no install required.

For non-macOS platforms, swap `sips` for ImageMagick's `convert` in `rasterize_to_png`.

## Integration with the tax skill

This is the canonical PDF reader for the skill. Use it for:

- Filed 1065/1120/1120-S returns (TurboTax / ProSeries / Drake exports are all text PDFs)
- K-1s received (usually text; some sponsors send scans)
- 1099s, W-2s, 1098s (mixed; use auto mode)
- IRS letters (usually scans — force-image is safe default)
- Bank statements and check images (chase-statement-parser has its own specialized parser, but this tool is the general-purpose fallback)
- SS-4 EIN letters, 8822-B forms, 2553/8832 election letters (often scans)

Downstream parsing (extracting into per-doctype JSON schemas) still happens per `parsing.md` — this tool just delivers the raw content in the right format.

## Output shape

`ExtractResult` dataclass:

```python
@dataclass
class ExtractResult:
    mode: str                      # "text" | "image" | "failed"
    text: Optional[str] = None     # populated when mode == "text"
    pngs: list[str] = []           # list of PNG paths when mode == "image"
    pages_rasterized: str = None   # e.g., "1-3" or "all"
    pdf_path: str = ""             # echo of input
    diagnostics: dict = {}         # diagnostic info (chars, dpi, errors, etc.)
```

## Limitations

- macOS-biased (uses `sips`). On Linux, replace with `convert` from ImageMagick.
- No built-in OCR — relies on Claude Read for vision. Works fine for anything Claude can see; fails if the image itself is unreadable (extremely low-res scan).
- Doesn't handle password-protected PDFs — `pdftotext` will fail and rasterization will fail. Add `-upw <password>` support if needed.
- No table-aware extraction (e.g., pdfplumber). For complex financial tables where `pdftotext -layout` loses column alignment, consider adding pdfplumber integration downstream.

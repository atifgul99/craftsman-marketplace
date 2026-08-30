# coa-categorizer

Rule-based GL bucket assignment for parsed transaction rows.

Feeds on the output of `chase-statement-parser` (or any CSV with at least
`description` and `amount` columns) and appends four columns:

- `gl_account` — human-readable bucket (e.g., "Software & SaaS")
- `gl_code` — account code if the rule supplies one (e.g., "6120")
- `confidence` — `high` | `medium` | `low`
- `needs_review` — `True` when no rule matched or confidence is `low`

No LLM in the loop. Unmatched rows surface in the summary so a human (or a
follow-up LLM call) can finish the job.

> **Paths below are written from this tool's own directory.** The skill installs as a
> plugin outside your workspace, so a bare `python3 coa_categorizer.py` will not resolve from
> where you are standing. Set `TAX_SKILL="${CLAUDE_PLUGIN_ROOT}/skills/tax"` once and
> address the script as `"$TAX_SKILL/tools/coa-categorizer/coa_categorizer.py"`. Arguments are the other way
> round: they are workspace paths, resolved against the current directory.

## CLI

```bash
python3 coa_categorizer.py input.csv \
    [--rules custom.json] \
    [--output out.csv] \
    [--reclassify] \
    [--review-limit 50]
```

- Without `--output`, prints summary only (no writes).
- Idempotent: rows that already carry a `gl_account` are left alone unless
  `--reclassify` is passed.

## Library

```python
from coa_categorizer import categorize, load_rules

rules = load_rules("default_rules.json")
enriched = categorize(rows, rules, reclassify=False)
```

`rows` is a list of dicts (e.g., the output of `csv.DictReader`).

## Rules file format

```json
{
  "rules": [
    {"match": "STRIPE", "gl_account": "Revenue", "gl_code": "4000", "confidence": "high"}
  ]
}
```

- `match` is a case-insensitive substring test against `description`.
- First rule to match wins — order rules from most- to least-specific.
- Extend `default_rules.json` or point `--rules` at a per-entity override file.

## Summary output

1. Top: GL bucket counts + total `$` (sorted by count desc).
2. Bottom: up to N `needs_review=True` rows, sorted by `abs(amount)` desc — so
   the biggest uncategorized items bubble up first.

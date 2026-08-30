# dep-check

Report-only dependency preflight for the tax skill. Answers "is this skill
installed intact, and can it actually run?" in one call, before a close or an
intake is half-built rather than during it.

Unlike every other tool here, its subject is the **skill**, not the workspace —
`workspace-doctor` is the workspace equivalent.

## Usage

```bash
TAX_SKILL="${CLAUDE_PLUGIN_ROOT}/skills/tax"
python3 -B "$TAX_SKILL/tools/dep-check/dep_check.py"
```

```bash
python3 -B "$TAX_SKILL/tools/dep-check/dep_check.py" --json
```

Exit `0` = every required dependency present. Exit `1` = at least one missing.
Optional dependencies never affect the exit code.

## What it checks

| Layer | Checked | Required |
|---|---|---|
| Install integrity | one marker file per shipped subsystem under the skill root | yes |
| Runtime | Python 3.9+ | yes |
| poppler | `pdftotext`, `pdftoppm`, `pdfinfo` on PATH | yes |
| Validator packages | `jsonschema`, `markdown-it-py` importable | yes |
| Fallback rungs | `ocrmypdf`, `pdfplumber`, `bean-check` | no |

For each missing item it prints what the dependency is used for, what goes
unchecked without it, and the exact fix command for the detected platform and
Python environment (Homebrew vs apt vs dnf vs pacman vs zypper vs choco;
`pip install` vs `pip install --user` vs `uv add`).

## Design

- **Stdlib only.** A dependency checker that needs a dependency installed is
  useless precisely when it is needed.
- **Never installs.** It prints a command for a human to approve. See
  `dependencies.md` for why silent installs are prohibited.
- **Required vs optional is decided by blast radius.** Poppler is required
  because without it every PDF path in `parsing.md` is dead and the only
  remaining option — `Read` on a PDF — silently misreads tax-form columns.
  `ocrmypdf` is optional because it is rung 3 of a ladder whose first two rungs
  handle the large majority of documents.

## Dependencies

Python 3.9+, standard library only. No `pip install`, no poppler — it must run
on the machine that is missing everything else.

## See also

- `dependencies.md` — the install/verify/fix doctrine this tool implements
- `evals/_deps.py` — the per-validator runtime guard that backstops it
- `tools/workspace-doctor/` — the same idea for the user's workspace

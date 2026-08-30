# Taxcraft

CPA-grade tax workpapers for people who do their own prep.

`taxcraft` is a single skill (`tax`) for US tax and accounting situations that outgrew consumer tax
software but that you still handle yourself: multiple entities, K-1s that arrive late and wrong,
basis and carryforwards nobody is tracking, quarterly estimates guessed at rather than computed.

It builds the workpapers a CPA would build — transaction-level books from raw statements and CSVs,
reconciled balance sheets, partner and shareholder basis, capital-loss / NOL / passive / QBI
carryforwards, 1040-ES and corporate estimates under the annualized income method — and shows the
math with the Code section behind it.

## ⚠️ Not tax advice

This produces **estimates, workpapers, and drafts** — not tax advice, not a legal opinion, not a
substitute for a licensed practitioner. It does not file returns. Numbers must be verified by a
CPA, EA, or tax attorney before filing or before you rely on them for estimated-tax payments.
Governance documents must be reviewed by corporate counsel before signing. No CPA-client or
attorney-client privilege is created.

## What it covers

| Area | What it does |
| --- | --- |
| **Individuals (1040)** | Intake, federal + state estimation, carryforward tracking, equity comp, multi-state K-1s, retirement sequencing, IRMAA, education, estate and gift |
| **Partnerships (1065)** | §704(b)/(c), capital accounts, K-1 + K-2/K-3, §754 elections, partner basis |
| **S-corps (1120-S)** | Reasonable comp, AAA, stock and debt basis, §1374 BIG, 2%-shareholder health, accountable plans |
| **C-corps (1120)** | Transaction-level P&L from CSVs, Schedule L, M-1/M-3, §163(j), §174, stock-issuance closing and evidence, §1202 QSBS, §1244, §280A(g), family employment |
| **Disregarded SMLLCs** | Nested books consolidated onto the regarded parent's return |
| **Quarterly closes** | Period P&L, balance sheet, general ledger, 1040-ES (§6654) and corporate §6655 estimates, annualized income installment method |
| **Corporate governance** | Bylaws, board and shareholder minutes, written consents, resolutions, state annual reports, FinCEN BOIR, corporate-veil protection |
| **States** | WA and WY in depth; residency and multi-state sourcing generally |

Each tax year's numbers come from a dated rules file under `skills/tax/rules/`, so a prior year
never silently answers a current-year question.

## Install

### Claude Code

You need Claude Code installed first: see [code.claude.com/docs](https://code.claude.com/docs).

Type these into Claude Code's chat box, not a terminal:

```
/plugin marketplace add gul-labs/craftsman-marketplace
```

```
/plugin install taxcraft@craftsman-marketplace
```

Headless equivalents:

```bash
claude plugin marketplace add gul-labs/craftsman-marketplace
```

```bash
claude plugin install taxcraft@craftsman-marketplace
```

### Codex

Codex loads the same skill through the included `.codex-plugin/plugin.json` manifest:

```bash
codex plugin marketplace add gul-labs/craftsman-marketplace
```

```bash
codex plugin add taxcraft@craftsman-marketplace
```

### After installing

The plugin installer does not bring two things the skill needs: **poppler** (every PDF is read
through `pdftotext`, never by eye) and two Python packages used by the artifact validators.
The skill checks for them itself on first use and proposes the right command for your platform
— you approve it, it never installs anything silently. To do it up front:

```bash
brew install poppler && pip install --user jsonschema markdown-it-py
```

On Debian/Ubuntu substitute `sudo apt install poppler-utils`. To verify at any time:

```bash
python3 -B ~/.claude/plugins/cache/*/taxcraft/*/skills/tax/tools/dep-check/dep_check.py
```

## First use

Run Claude Code from the **root of your tax workspace** — the folder where your entity and
individual records live, not from this repo. On first invocation the skill offers to `init`: it
scans existing entities and prior returns, drafts a workspace profile, and scaffolds the folder
structure. After that it reads your profile and routes by menu.

Your data stays in visible folders at the workspace root (`workspace-profile/`, `individual/`,
`entities/<slug>/`) — never inside the plugin. See
[`skills/tax/layout.md`](./skills/tax/layout.md) for the full contract and
[`skills/tax/init.md`](./skills/tax/init.md) if you have a legacy structure to migrate.

## Privacy

The skill runs locally against your own files and makes no network calls of its own. It masks
SSNs, EINs, and account numbers to last-4 digits in every workpaper it writes. Whatever you show
the model still goes to the model provider, so treat it as you would any other AI tool handling
tax documents. See the repo [PRIVACY.md](../../PRIVACY.md).

## Verifying a change

The skill ships its own release evals — the same set CI gates on. Run them from this
directory (`plugins/taxcraft/`), not from a tax workspace: these paths are relative to
the plugin, and the skill's own files are what they check.

```bash
for f in skills/tax/evals/[a-z]*.py skills/tax/tools/parse-verify/test_verify.py; do
  echo "--- $f"; python3 -B "$f" || echo "FAILED: $f"
done
```

Ten checks: seven artifact and structural validators, the markdown block-scoping unit
tests, `test_no_skill_writes.py` (runs the whole suite again against a read-only copy of
the skill, since an installed plugin is read-only for most users), and the parse-verify
self-test. They need `jsonschema` and `markdown-it-py`; nothing else, and no network.

## License

MIT — see [LICENSE](../../LICENSE).

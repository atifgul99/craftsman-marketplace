
# Tax Skill

Expert US tax assistant covering:

- **Individuals (1040)** — intake, federal + state estimation, carryforward tracking, equity comp, multi-state K-1s
- **Partnerships (1065)** — §704(b)/(c), capital accounts, K-1 + K-2/K-3, §754 elections, partner basis
- **S-corps (1120-S)** — reasonable comp, AAA, basis (stock + debt), §1374 BIG, 2%-shareholder health, employee accountable plans
- **C-corps (1120)** — transaction-level P&L from CSVs, Schedule L, M-1/M-3, §163(j), §174, rigorous stock-issuance closing/evidence orchestration, §1202 QSBS + §1244 ordinary-loss analysis, Accountable Plans, §280A(g) Augusta rule, family employment, §1441/1042-S foreign withholding
- **Disregarded SMLLCs** — nested books, consolidated onto regarded-parent return
- **Quarterly closes** — period P&L, balance sheet, general ledger, 1040-ES (§6654) / corporate §6655 estimates via EFTPS, annualized income installment method
- **Corporate governance** — bylaws, board/shareholder minutes, written consents, board resolutions, state annual reports, FinCEN BOIR, corporate-veil protection

**Does not file returns.** Produces estimates, workpapers, strategy analysis, and governance drafts for review by a licensed CPA/EA/attorney.

## Invocation

Run Claude Code from the **root of your business/tax workspace**. On first invocation, the skill will offer to `init` — scan existing entities + prior returns, draft a workspace profile and per-entity configs, and scaffold the folder structure. After that, it reads your profile and routes by menu.

## Workspace Layout (summary)

```
<workspace>/
├── CLAUDE.md, README.md
├── workspace-profile/   ← cross-entity roster, org chart, owner info, history
├── individual/          ← personal 1040 work (peer to entities/)
└── entities/<slug>/     ← each regarded entity (disregarded SMLLCs nest under their parent)
    ├── entity.md, corporate/, accounts/, books/, properties/, investments/
    ├── disregarded/<smllc-slug>/   ← nested SMLLC (no tax/ folder; consolidates up)
    └── tax/FY2025/{source, quarterly, annual, issued, filed}/
```

See `layout.md` for the full contract (tree SSOT) and `init.md` for migration guidance if you have a legacy structure.

## User Data

User data lives in **visible folders in the workspace root** — never inside this skill directory:

- `workspace-profile/` — cross-entity state
- `individual/` — the owner's 1040 work
- `entities/<slug>/` — per-entity books, corporate records, tax years
- Hidden `.parsed/` and `.computed/` caches live under each scope's year folder

See `layout.md` for the full contract.

## Roadmap

Future: Plaid bank/brokerage integration, county assessor scrapers, IRS transcript auto-pull, state SOS API integration for annual-report status, FinCEN BOIR submission checks, email IMAP scanning for 1099/K-1 arrivals. Today: manual document intake with PDF→JSON caching.

## ⚠️ Not Tax Advice

Estimates, workpapers, and governance drafts only. Verify with a licensed CPA, EA, or tax attorney before filing or acting. Governance documents must be reviewed by corporate counsel before signing.

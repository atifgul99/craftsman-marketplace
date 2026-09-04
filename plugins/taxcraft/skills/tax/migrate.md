# Migrate Sub-Skill

Convert a legacy workspace (ad-hoc folders, vendor-supplied filenames) into the canonical layout. Invoked from `init.md` when legacy structure is detected, or directly when the user says "migrate".

**Never move or rename silently.** Every batch is dry-run → approval → execute → verify.

## Inputs

- `layout.md` — target layout
- `naming.md` — canonical folder slugs + document filenames
- `parsing.md` — PDF read rules (for sniffing doc types)

## Phase M1 — Scan

Glob the root. Classify each path into one of:

| Signal | Classification |
|---|---|
| `[Ee]ntities/*/`, `* Inc/`, `* LLC/`, `* LP/` | Entity folder (regarded) |
| Nested entity folder inside another entity | Disregarded SMLLC |
| `FY[12][09][0-9][0-9]/`, `Tax [12][09][0-9][0-9]/`, `[12][09][0-9][0-9]/` under entity | Per-entity tax year |
| `Corporate/`, `Minutes/`, `Resolutions/` | Governance folder |
| `Bank*`, `CC*`, `Brokerage*`, `K-1*`, `Contractors*`, `Receipts*` | Source subfolder |
| `*1040*.pdf`, `Tax Return*.pdf` at root | Individual return |
| `*K1*.pdf`, `*K-1*.pdf`, `*W2*.pdf`, `1099*.pdf`, etc. loose | Unfiled document |
| `business-info*.md`, `entities*.md` at root | Legacy roster |

Report counts per class before proposing anything.

## Phase M2 — Folder migration map

Produce the mapping table, ask approval, execute, verify. Generic pattern:

```
Legacy path                                                  →  New path
Entities/<Legal Name>/                                       →  entities/<entity-slug>/
Entities/<Legal Name>/Corporate/                             →  entities/<entity-slug>/corporate/
Entities/<Legal Name>/Tax/FY<YYYY>/Bank & CC/                →  entities/<entity-slug>/tax/FY<YYYY>/source/bank-cc/
Entities/<Legal Name>/Tax/FY<YYYY>/Brokerage/                →  entities/<entity-slug>/tax/FY<YYYY>/source/brokerage/
Entities/<Legal Name>/Tax/FY<YYYY>/K-1s/                     →  entities/<entity-slug>/tax/FY<YYYY>/source/k1s-received/
Entities/<Legal Name>/Tax/FY<YYYY>/Contractors/              →  entities/<entity-slug>/tax/FY<YYYY>/source/contractors-w9/
Entities/<Legal Name>/Tax/FY<YYYY>/Receipts/                 →  entities/<entity-slug>/tax/FY<YYYY>/source/receipts/
Entities/<Legal Name>/Tax/FY<YYYY>/Workpapers/               →  entities/<entity-slug>/tax/FY<YYYY>/annual/workpapers/
Entities/<Parent>/<SMLLC Legal Name>/                        →  entities/<parent-slug>/disregarded/<smllc-slug>/
Entities/<Individually-Owned SMLLC>/                         →  individual/disregarded/<smllc-slug>/
Personal Tax/<YYYY>/                                         →  individual/FY<YYYY>/
business-info.md                                             →  workspace-profile/entities-index.md (content migrated)
missing-files-tracker.md                                     →  workspace-profile/notes/missing-files-tracker.md
Loose K-1 PDFs at root                                       →  entities/<recipient>/tax/FY<YYYY>/source/k1s-received/   (after sniffing)
```

Entity slugs resolved per `naming.md`. Show the full map; wait for explicit approval.

### Entity-folder guard

Two shapes need special handling before the generic map above applies:

- **Non-slug entity dirs** — `entities/Acme Holdings Inc/` (spaces, Title-Case, legal-name form instead of kebab-case slug). Resolve the canonical slug per `naming.md`, propose `entities/acme-holdings/`, and fold in any content already there.
- **Disregarded SMLLCs sitting as top-level entities** — a disregarded SMLLC placed directly under `entities/` (or at root) instead of nested under its regarded parent's `disregarded/`. Propose the canonical nested home, e.g. `entities/acme-holdings/disregarded/<smllc-slug>/`.

Rules:
- Always propose the merge as a mapping row; **always get explicit user confirmation before moving anything**.
- **Never delete.** If the canonical destination already has a file with the same name, content-hash both; content-identical copies are listed for the user to remove themselves — do not remove them automatically.
- Flag duplicates found during the scan in the same report used for Phase M1 counts.

## Phase M3 — Slug registry seed

Before file renames, build `workspace-profile/slugs.md` from `templates/slugs.md.template`:

1. Scan parsed return headers + loose documents for payer, employer, broker, sponsor, lender, custodian, vendor, recipient names.
2. Propose kebab-case slug for each; ask user to confirm or override.
3. Write registry. **Every rename in M4 must resolve slugs through this file.**

## Phase M4 — File rename map

For every file now placed under the new folder tree, determine canonical filename per `naming.md`:

1. **Sniff doc type** from filename + `pdftotext -layout <file>` header (per `parsing.md`). Never rely on filename alone.
2. **Resolve slugs** from `workspace-profile/slugs.md`.
3. **Determine tax year**: form year from doc header > folder `FY<YYYY>` > ask user.
4. **Emit rename row**:

```
Legacy filename                                              →  Canonical filename
Schedule K-1 2024 - ABC Fund IV LP.pdf                       →  FY2024 - K-1 - LP - abc-fund-iv.pdf
scan_0042.pdf          [sniffed: W-2, Microsoft, 2024]        →  FY2024 - W-2 - microsoft.pdf
1099-Composite.pdf     [Fidelity acct …4427]                   →  FY2024 - 1099-Composite - fidelity - 4427.pdf
Vanguard Tax 2024.pdf  [1099-Composite, acct …8812]            →  FY2024 - 1099-Composite - vanguard - 8812.pdf
K-1 issued to Summit Mgmt.pdf                                    →  FY2024 - K-1 issued - summit-management.pdf
Articles of Inc.pdf    [filed 2022-03-14]                      →  2022-03-14 - articles-of-incorporation.pdf
Annual Report WA 2024.pdf                                     →  FY2024 - annual report - WA.pdf
W9 - Joe's Plumbing.pdf                                       →  W-9 - joes-plumbing.pdf
```

5. **Unknown cases** (unmatched slug, unclear type, year mismatch with folder) → list separately; do not rename until resolved.
6. Show full rename map; wait for approval; execute via `git mv` or `mv`; verify each new path exists.

## Phase M5 — Parsed cache rebuild

After renames land:

1. Walk `<scope>/FY<YYYY>/source/**` and `docs/**`.
2. For each file, write `.parsed/_index.json` entry (per `parsing.md`) with new `source_path` + `canonical_name` + fresh sha256.
3. Parse new docs on demand (don't batch-parse unless user asks).

## Phase M6 — Pointer migration (cross-workspace K-1s)

For each K-1 that is now in an entity's `issued/k1s-issued/` AND also appears as a PDF copy in a recipient's `source/k1s-received/`:

1. Keep issuer copy as source of truth.
2. Delete recipient's duplicate PDF.
3. Write `<FY<YYYY> - K-1 - <GP|LP> - <issuer-slug>>.ref.md` pointer per `naming.md` "Cross-workspace K-1 references".

Confirm with user before deleting.

## Sync-conflict & duplicate sweep

OneDrive/iCloud sync produces conflict copies during migration: `(1)`-suffixed files, device-name suffixes (`*-<Device>`, `*-<Device>-2`), and double extensions (`.pdf.pdf`, `.Pdf`).

1. Detect via filename pattern (` (1)`, ` - <hostname>`, doubled/mixed-case extension) plus content hash (sha256) against siblings.
2. Propose a single canonical copy (correct name, no suffix) per group.
3. **Never auto-delete.** Present the group to the user — canonical keeper + duplicate paths — and let them confirm removal.

See also `naming.md` collision rules, which points back here.

## Phase M6b — Stock-issuance artifact migration (schema break, taxcraft 0.2.0)

Applies to any `stock-issuance-audit-FY<YYYY>.json` or
`*-closing-manifest.json` produced before taxcraft 0.2.0. Those artifacts no
longer validate. Migrate, then re-validate; never edit an artifact to make a
validator pass without re-establishing the underlying fact.

**Mechanical renames** — the jurisdiction-specific enum members became generic:

| Old value | New value |
|---|---|
| `WA_REGISTRATION` | `STATE_REGISTRATION` |
| `WA_EXEMPTION` | `STATE_EXEMPTION` |
| `WA_NOTICE` | `STATE_NOTICE_FILING` (or `STATE_FEDERALLY_COVERED_NOTICE` where the filing was a covered-security notice) |
| `WA_REACQUIRED_AUTHORIZED_UNISSUED` | `REACQUIRED_SHARES_RETURN_TO_AUTHORIZED_UNISSUED` |
| `COUNSEL_VALIDATED_OTHER_STATE` | `COUNSEL_VALIDATED_JURISDICTION_RULE` |

**New fields that require a human decision — do not script these:**

- `purported_issuance_evidenced` (per tranche). Set it from the evidence, not
  from the old status. Ask: does competent evidence show that a purported
  issuance actually occurred? A prior `ISSUED_AND_RECONCILED` is not the answer;
  re-read the closing manifest. Getting this wrong changes the derived status.
- `capacity_jurisdiction_code` and `jurisdiction_code` — the two-letter code for
  the jurisdiction each authority belongs to. The validator now requires the
  source URL to belong to that jurisdiction, so an authority that was accepted
  on a bare hostname check may now fail. That is the point: re-source it.
- `capacity_authority_citation` — the statute or rule the capacity source states,
  not a homepage.

**Expect status changes.** A tranche whose consideration gate was `UNVERIFIED`
on an evidenced issuance now derives
`PURPORTED_ISSUANCE_CONSIDERATION_UNVERIFIED` rather than `CLOSING_PENDING`, and
a conflicted evidenced issuance derives `DISPUTED_OR_DEFECTIVE` rather than
`FACT_CONFLICT`. These are more accurate, not regressions. Re-run
`evals/validate_stock_issuance.py --artifact <path>` and record the new status
in the entity's records rather than restoring the old label.

## Phase M7 — Verification

- Every file is under the new layout.
- Every filename matches its canonical form per `naming.md` OR is on the "unresolved" list with a tracked question.
- `slugs.md` covers every slug referenced in any filename.
- `.parsed/_index.json` in each scope-year is consistent with the current files on disk.
- Report: N folders moved, M files renamed, K unresolved → appended to `workspace-profile/notes/migration-open-questions.md`.

Hand control back to `init.md` Phase 5 ("Pick an active scope") if invoked from init, else back to the router.

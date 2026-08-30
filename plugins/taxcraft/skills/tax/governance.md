
# Corporate Governance Sub-Skill

State-parameterized governance doctrine, corporate-document intake, and
document drafting for closely-held corporations and LLCs. For a complete
C-corporation record-book, formation cleanup, annual governance, or “what
documents do we need?” audit, start with `scenarios/corporate-records.md`; this
file supplies only the state-law, intake, and drafting branch it requests.
**Does not file** with agencies or execute documents.

## Why Governance Matters

For a sole-shareholder or closely-held entity, governance is **audit defense**:

1. **Corporate veil protection** — factors courts weigh when piercing (see *Meisel v. M&N Modern Hydraulic Press Co.*, WA Supreme Court, and parallel doctrines in other states): adequate capitalization, separate books and records, corporate formalities observed, no commingling of assets, distinct corporate identity. Miss any, and personal liability is on the table.
2. **IRS audit defense** — contemporaneous resolutions support tax positions: zero-officer-comp decisions, capital contributions, fiscal-year elections, Accountable Plan adoption, §280A rental arrangements, family employment, accumulated earnings rationale.
3. **State and federal compliance** — missed state annual reports can lead to
   delinquency or administrative dissolution. Under FinCEN's final rule
   effective August 14, 2026, U.S.-created entities and U.S. persons are exempt
   from BOI reporting; a foreign-law entity registered in the United States
   requires current-rule analysis. Re-verify at point of use.

## Scope

Per entity, per year:

- Organizational documents (bylaws, operating agreements) — static, reviewed periodically
- Annual shareholder action and any bylaw- or event-required director action
- Board resolutions for material actions (officer comp, capital contributions, major contracts, elections, accumulated earnings rationale)
- State annual report filings (check compliance, draft if missing)
- Historical BOI confirmations, or current foreign-reporting-company analysis when applicable
- Registered agent maintenance
- Separate-books discipline audit (are books actually separate?)

## State-Parameterization

This sub-skill is **state-parameterized**: logic is general; state-specific statutes pulled from the entity's state of formation. Depth varies by state:

- **High-depth support**: WA (RCW 23B for corps, RCW 25.15 for LLCs), DE (DGCL / LLC Act), CA (Corp Code), TX (BOC), NY (BCL), FL (FBCA)
- **General support**: all 50 states — the skill cites general principles and asks the user to confirm against state-specific statute or refers to corporate counsel for final review.

Entity state is read from `entities/<slug>/entity.md` field `state_of_formation`.

## Preflight (governance audit)

Before drafting, audit the entity's current state:

For a C-corporation lifecycle/completeness audit, instantiate the matrix in
`scenarios/corporate-records.md` and use this preflight only for its governance
and intake branches.

1. **Load `entities/<slug>/entity.md`** — legal name, state, formation date, type, officers/directors, shareholders/members, fiscal year.
2. **Inventory `entities/<slug>/corporate/`**:
   - `formation/` — Articles of Incorporation/Organization, bylaws or operating agreement, organizational consent
   - `minutes/` — all meeting minutes on file, by date
   - `resolutions/` — all board resolutions on file
   - `annual-reports/` — state filings, by year
   - `licenses/` — business license, state DOR/B&O registration, BOIR submission confirmation
3. **Identify gaps** against a baseline compliance checklist (below).
4. **Review `workspace-profile/history.md`** for prior audits, dissolutions, amendments, capital events that should have generating documentation.

## Baseline Compliance Checklist (per entity)

### Formation

- [ ] Articles filed with state (copy on file with state filing acknowledgment)
- [ ] Bylaws adopted (C-corp / S-corp) OR operating agreement executed (LLC)
- [ ] Post-effective-date authority chain: incorporator action when required,
      initial-director action, bylaws adoption, officer appointments, and
      actual organizational approvals
- [ ] EIN letter (CP 575) on file
- [ ] S-election acceptance letter (CP 261) if S-corp
- [ ] Certificate issued, or board-authorized uncertificated shares recorded and the formation-state information statement delivered; all required class terms and transfer restrictions are conspicuous (for WA corporations, RCW 23B.06.250–.270)
- [ ] Stock ledger / membership ledger maintained
- [ ] Each issuance has a reconciled closing packet under `corporate/stock-issuances/`; §1202 and §1244 positions are separately tested, not presumed from the presence of records (see `scenarios/stock-issuance.md`)

### Annual (every year the entity is active)

- [ ] Annual shareholder meeting or legally sufficient written consent when
      required by formation-state law and governing documents
- [ ] Director action required by the bylaws or actual corporate decisions;
      do not invent a categorical annual-board-meeting requirement
- [ ] Board resolutions for any material actions taken during year: comp, capital events, new accounts, major contracts, elections
- [ ] State annual report filed (varies: some states biennial; some fee-free)
- [ ] Registered agent fee paid / agent still active
- [ ] Activity-, location-, and account-triggered licenses verified when applicable
- [ ] State/local tax registrations verified when actual activity or account status makes them applicable

### FinCEN BOI (current domestic exemption)

- [ ] Formation jurisdiction established from competent evidence
- [ ] Domestic U.S.-created entity: present duty classified not applicable under
      the current FinCEN final rule; retain prior confirmations as history
- [ ] Foreign-law entity registered in the United States: current applicability,
      exemption, deadlines, and accepted-filing evidence separately verified

### Sole-Shareholder Entities (extra scrutiny)

- [ ] Bank accounts titled in entity name only — no personal commingling
- [ ] Books & records physically/digitally separate from personal
- [ ] Contracts signed in entity name with proper officer title
- [ ] Shareholder-to-entity transactions at arm's length + documented (loans with promissory notes, leases with rental agreements, reimbursements under Accountable Plan)
- [ ] Capital adequately infused (factor in piercing-veil analysis)
- [ ] Required shareholder and director actions truthfully documented; no fictional meetings

## Document Intake (post-filing)

Trigger and high-level rules live in `SKILL.md` → "Corporate document intake". This section owns the mechanics. State-generic by design — examples cite specific agencies (WA SOS, FinCEN, etc.) only as illustrations; real intake reads the agency name from the document itself.

### When to run

Per `SKILL.md` triggers and its authorization boundary. In short: any of these
requires either (a) the loop when writes are authorized or (b) a read-only
pending-intake/difference report when they are not, followed by the user's
actual request.

1. User signals a filing event ("I filed", "I uploaded", "check records", or names a corporate event).
2. New PDF found under `entities/<slug>/corporate/**` without a `_processed.log` entry.
3. About to answer a standing/compliance question — verify no unprocessed files first.

### Self-healing on backlog when writes are authorized

On entity load, if a corporate subfolder contains PDFs but no `_processed.log`
at all (i.e., the whole subfolder has never been processed, not just one new
file), first check authority. With write authority, batch-process the backlog:
parse each doc → extract data per the schemas below → update `entity.md` → write
the `_processed.log`. For large backlogs, processing may be done folder-by-
folder with the user's consent. In read-only scope, do none of those mutations;
inspect only as permitted and report the pending files plus proposed field
differences.

Rationale: the "never answer standing questions with unprocessed files in the way" rule is self-defeating if the backlog is simply never drained — in practice almost no entity ever accumulates `_processed.log` files, so a rule that only flags the blocking condition but never resolves it permanently blocks all future work on that entity. Flag-then-refuse is not a substitute for flag-then-fix.

### Loop (per unprocessed PDF)

1. **Discover** unprocessed files. For each `entities/<slug>/corporate/<subfolder>/`, list `*.pdf` and compare against `_processed.log`. Any PDF whose filename (canonical or original) does not appear in the log is unprocessed.
2. **Parse** via `pdftotext -layout` (per `parsing.md`). Scanned/image-only PDFs → `pdftoppm -r 300` then OCR.
3. **Identify doctype** from header keywords. Common types and the agency that produces them:
   - State **annual report** (Secretary of State or equivalent registry)
   - **Business license** / combined license / endorsement renewal (state revenue or business-services agency)
   - **BOIR confirmation** (FinCEN — federal, not state)
   - **Statement of change / amendment** (Secretary of State)
   - **Foreign qualification / Certificate of Authority** (Secretary of State of a non-formation state)
   - **Formation document** (Articles, Certificate of Formation, organizational consent)
   - **Resolution / minutes / written consent** (internal, not agency-issued)
   - **Payment receipt** paired with any of the above (matched by work order # or filing ID)
4. **Canonicalize the filename** per `naming.md`:
   - Annual report: `FY<YYYY> - annual report - <state>.pdf`
   - Business license: `FY<YYYY> - license - <jurisdiction>.pdf`
   - BOIR: `<yyyy-mm-dd> - BOIR - <initial|updated>.pdf`
   - Formation: `<yyyy-mm-dd> - <doc>.pdf`
   - Receipts paired with a filing: same base + ` - Payment Receipt.pdf`
   - When the user has already chosen a non-canonical-but-clear name (e.g., `<EntityName> - Filed Annual Report 2026.pdf`), respect it and log the deviation rather than rename — surface the canonical form as a one-line note for the user to optionally adopt.
5. **Place** in the correct subfolder. Move if the user dropped it elsewhere:
   - Annual reports + paired receipts → `corporate/annual-reports/`
   - Business licenses + endorsements → `corporate/licenses/`
   - BOIR confirmation → `corporate/licenses/` (or a dedicated `boir/` if the user prefers)
   - Statements of change, amendments, formation docs → `corporate/formation/`
   - Resolutions and consents → `corporate/resolutions/` or `corporate/minutes/`
6. **Extract metadata** per the schemas below.
7. **Update `entities/<slug>/entity.md` only when writes are authorized**. In
   read-only scope, report the proposed changes without editing or logging:
   - Bump `**Last updated**: <today>` at top.
   - Add or update the relevant section (`## Annual Reports`, `## Business Licenses`, `## BOIR`, `## State Registrations` for one-off filings).
   - Cross-link to the new file path.
   - Update only a public/profile field that the document competently proves.
     A filed governor list does not prove an internal election, officer
     authority, shareholder/member status, issued shares, or ownership.
8. **Append `_processed.log`** in that subfolder (create if missing). Format:
   ```
   <YYYY-MM-DD>  <canonical-or-final-filename>
                 Source filename: <original>
                 <one-line summary with key extracted fields>
   ```
9. **Report** to the user: 1 line per file processed, plus any conflicts surfaced.

### Per-doctype extraction schemas (state-generic)

**State annual report** (any state):
- Filing date / effective date
- Filing reference (work order #, confirmation #, filing #)
- Entity ID (UBI / file # / charter # / SOS #)
- Expiration / next-due date (where state prints it)
- Principal office (street + mailing)
- Registered agent (name + address)
- Governors / directors / managers (entity name vs natural person — note which)
- Public contact info (email, phone) if shown
- Filing fee + payment method

**Business license** (state combined license, city/county endorsement, occupational license):
- Issuing agency
- License number / business ID / UBI
- Issue date and **expiration date**
- Active endorsements (state tax, city/county, industry-specific)
- Trade names listed
- Renewal fee

**FinCEN BOI confirmation** (historical for domestic entities; current only if applicable to a foreign reporting company):
- BOIR ID / submission ID
- Filing date
- Filing type (initial / updated / corrected)
- Reporting company info confirmed (name, EIN, address)
- Count of beneficial owners reported
- Company-applicant fields actually present in the historical/applicable filing

**Statement of change / amendment**:
- What changed (registered agent, address, name, members, managers, etc.)
- Effective date
- Filing fee
- Filing reference

**Foreign qualification / Certificate of Authority**:
- Foreign state
- Effective date
- Foreign-state entity ID
- Registered agent in foreign state

**Formation document** (Articles, Certificate of Formation, organizational consent):
- Filing date
- Entity ID assigned
- Initial registered agent
- Initial governors / directors / incorporator
- Authorized shares (corp) or member info (LLC)

**Payment receipt** (paired with a filing):
- Work order # / filing reference (must match parent filing — pair them)
- Amount
- Card last 4 (never store full PAN)
- Cardholder / payer name
- Payment date

### Anti-drift rules

- **Use filed evidence field by field.** With write authority, update only the
  exact public/profile field the filing proves and surface the diff. Do not
  infer internal authority, ownership, shares, or membership from a public
  registry. In read-only scope, report the proposed diff only. Never overwrite
  source evidence from `entity.md`.
- **Pair receipts with filings.** Two files sharing a work order # / filing reference are a pair — process together, cross-reference each in both `_processed.log` entries.
- **Never silently skip.** If a file's doctype is ambiguous (renewal notice vs filed confirmation, unsigned draft vs executed copy, agency letter vs filer-generated PDF), ask the user before logging. Files that can't be classified stay in place with a note in the user-visible report.
- **Never present stale standing fields as current.** With write authority,
  process first and then answer. In read-only scope, disclose the pending intake
  limitation and proposed differences; do not move, rename, persist parsed
  output, append logs, or update records.
- **State-specific quirks** (UBI vs file # vs charter #, SOS vs business-services agency, combined-license states vs separate-license states) are extraction details, not new schemas. The above list is the universal frame.

## Document Drafting Patterns

All drafted documents are written in plain English (not legalese), tailored to the entity's facts, and end with clear signature blocks.

### Written Consent in Lieu of Annual Shareholder Meeting

Structure:
- Header: entity name, state, year
- Authority: state statute (e.g., WA RCW 23B.07.040 — shareholders; 23B.08.210 — directors)
- Waiver of notice
- Action(s) taken — typically: re-elect directors, ratify officer actions, approve prior-year financials
- Signatures of shareholders (or majority if not unanimous consent jurisdiction)
- Date, filed into `entities/<slug>/corporate/minutes/<YYYY-MM-DD>-shareholder-consent.pdf`

### Written Director Consent (when bylaws or an actual decision requires action)

- Header + statute authority
- Actions: elect/re-elect officers, set officer compensation (cite comp study), ratify accountable plan, adopt §280A Augusta rental resolutions, authorize fiscal year / accounting method / major contracts, authorize estimated-tax payment schedule, ratify distributions, approve financial statements

### Distributions from a disregarded SMLLC to its parent/member

Instantiate `templates/member-distribution-consent.md.template` → `entities/<slug>/corporate/resolutions/<YYYY-MM-DD>-member-distribution-to-<member-slug>.md`.

Do not assume either that a written consent is required or that no approval
record is required. Verify the current formation-state LLC act, operating
agreement, management structure, and any reserved approval rights. If no legal
or contractual writing is required, a short consent may still be a
`RISK-CONTROL` for separateness, characterization, and ledger support. Tax
analysis and consolidation mechanics belong in `books/journal-entries.md`,
never in a document the owner signs.

**The solvency clause must recite the test(s) the formation state actually imposes — and they are not uniform.** WA (**RCW 25.15.231**) and WY (**W.S. 17-29-405**) impose *both* an equity/liquidity test and a balance-sheet test; **Delaware (6 Del. C. §18-607) imposes the balance-sheet test only.** Asserting both in a Delaware consent states a standard that does not apply. The balance-sheet prong is also rarely a bare assets-exceed-liabilities comparison — WA excludes liabilities to members on account of their interests and limited-recourse liabilities; WY accounts for preferential dissolution rights. Recite the statute's actual test; overstating it is not conservative, it is a representation the signer may not satisfy.

Verify the section number is *current* — several states recodified their LLC acts in the 2010s and superseded numbers persist online (WA's **RCW 25.15.235 was repealed effective 2016-01-01**). A consenting member/manager can be personally liable for a non-compliant distribution, though typically only on a failure of the duty of care (WA: RCW 25.15.236) — the clause is the signer's record of having made the determination.

**Confirm who may approve.** Do not assume the sole member is the correct actor; a manager-managed LLC or an agreement reserving distribution authority may require the manager or another authorized person.

**Execute as two transfers, never one.** The distribution goes to the member's own account; the member then pays its own obligations from that account as a separate, later transaction. The LLC paying the member's creditors directly is commingling. One consent per distribution — a blanket authorisation for ongoing sweeps reads as the very commingling the document exists to rebut.

### Board Resolution — Standalone

Used when action is between annual meetings. Examples:
- Authorize new bank account
- Stock, unit, or other equity issuance — route the entire transaction through `scenarios/stock-issuance.md`. A generic resolution shell is not an issuance closing. It must reconcile authority, class capacity, consideration, valuation/vesting, tax, securities, approval, payment/transfer, ledger/notice, and books. Historical contributions require remediation; never backdate.
- Authorize loan to/from shareholder
- Approve a written employee reimbursement policy intended to satisfy Reg §1.62-2 — coordinate with `scenarios/accountable-plan.md`; approval is governance evidence, not proof that later claims operated accountably
- Approve Augusta-rule rental at FMV — coordinate with `scenarios/ccorp-tax-reduction.md`
- Authorize family-member employment at arm's-length wage
- Document accumulated-earnings rationale (§531 defense)

Each: recitals (WHEREAS), resolution body (RESOLVED), signature, date.

### Annual Meeting Minutes (if holding actual meeting vs. consent)

- Meeting called to order, roll call, quorum confirmation
- Waiver of notice (if applicable)
- Prior minutes read and approved
- Reports (financial, operational)
- Old business
- New business / resolutions passed
- Adjournment
- Signature of corporate secretary

## Output Files

For a C-corporation record-set audit, use the canonical matrix and status model
in `scenarios/corporate-records.md`. For a dated governance finding or drafting
engagement:

- `entities/<slug>/corporate/audit-<YYYY-MM-DD>.md` — findings report: gaps identified, documents missing, remediation plan
- Drafted documents saved to `entities/<slug>/corporate/<subfolder>/<YYYY-MM-DD>-<title>.md` then converted to PDF for signing
- **Multi-year remediation** (gaps span more than one year, or the audit surfaces facts that also require tax-side reconstruction — books, K-1s, amended returns): instantiate `templates/audit-remediation-plan.md.template` and write the filled-in plan to `entities/<slug>/corporate/audit-<YYYY-MM-DD>.md` (the existing entity-scoped audit-output convention above — this is a single-entity governance audit, not a firm-wide review, so it follows that path rather than a separate `remediation-plan.md`). Cross-reference `scenarios/amend-partnership.md` for the tax-amendment phases of the plan where the entity is a partnership with defective filed returns.

For standalone resolutions:

- `entities/<slug>/corporate/resolutions/<YYYY-MM-DD>-<topic>.md`

For annual packets:

- `entities/<slug>/corporate/minutes/<YYYY>-annual-shareholder-consent.md`
- `entities/<slug>/corporate/minutes/<YYYY>-annual-director-consent.md`
- `entities/<slug>/corporate/annual-reports/<YYYY>-state-report-ready-to-file.md`

## BOI current-rule branch

### When required

Under the Corporate Transparency Act (31 USC §5336, 31 CFR 1010.380), verify
FinCEN's current official rule at point of use. FinCEN's final rule effective
August 14, 2026 exempts U.S.-created entities and U.S. persons. Preserve any
prior domestic BOIR confirmation as historical evidence; do not create a
domestic update diary. A foreign-law entity registered to do business in the
United States requires a fresh applicability/exemption/deadline analysis.

### If a foreign reporting company remains in scope

- Reporting company: legal name, trade names, address, state of formation, EIN
- Beneficial owners: each person exercising substantial control OR owning ≥ 25%. For each: full legal name, DOB, residential address, unique ID (passport/driver's license) + image
- Report only the fields required by current law for the actual filing type;
  do not reuse historical domestic intake language

### Process

1. Establish foreign-law formation and U.S. registration from competent evidence.
2. Verify current reporting-company and exemption rules from FinCEN.
3. Identify current fields, deadline, and update/correction rules.
4. Treat submission and accepted confirmation as different evidence stages.
5. Save any authorized filing confirmation as historical/permanent evidence.

## Corporate-Veil Discipline Audit

Beyond documentation, audit:

- [ ] Separate EIN in use for all entity-level transactions
- [ ] No shared credit cards between entity and shareholder
- [ ] No shareholder personal expenses on entity card (if found: re-characterize as distribution or loan, repay)
- [ ] Intercompany transactions documented (loan agreement, promissory note, lease)
- [ ] Entity signs its own contracts (signature: "EntityName, by [Name], [Title]")
- [ ] Insurance policies in entity name
- [ ] Capital adequate for foreseeable obligations (piercing factor)

Flag any commingling with the shareholder for immediate remediation + documentation.

## Multi-State Compliance

For entities operating in states beyond formation state:

- [ ] Foreign qualification (Certificate of Authority) in each state where entity transacts business
- [ ] Registered agent in each foreign state
- [ ] State income/franchise/B&O/sales tax registrations
- [ ] State annual report in each foreign state (where applicable)

Track per state in `entities/<slug>/corporate/licenses/state-compliance-matrix.md`.

## Red Flags Requiring Counsel Referral

- Any stock, unit, option, restricted-stock, SAFE/note conversion, or other securities issuance without a counsel-approved process and forms—including founders, family, employees, service providers, or investors
- Any uncertainty over federal/state exemption, solicitation, offeree state, notice filing, legend, or transfer restriction
- Historical cash/property being relabeled as present issuance consideration
- Missing or conflicting authority chain, bylaws, authorized-share capacity, outstanding-share count, or related-party conflict route
- Multi-tier ownership with institutional investors
- Contemplated sale, merger, or conversion
- Cross-border ownership (non-US persons) — S-election risk, treaty issues, withholding
- Litigation (active or threatened)
- Any governance question with ambiguous state law interpretation

Do NOT treat equity documents, M&A agreements, or complex governance structures as executable without corporate/securities counsel. For issuance work, `scenarios/stock-issuance.md` may produce a readiness memo, evidence packet, and clearly labeled counsel-review drafts; counsel controls legal terms, exemption selection, and closing.

## Always End With

> Review with corporate counsel before signing or filing. Governance documents have legal consequences. This skill produces drafts tailored to your facts but does not provide legal representation.

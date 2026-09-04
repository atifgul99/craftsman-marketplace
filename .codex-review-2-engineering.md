# Engineering and Internal-Consistency Review — f26653b

Scope: commit-pinned engineering/internal-consistency review only; tax-law analysis excluded. The live checkout gained unrelated edits during review, so all requested validation was rerun from a clean git archive f26653b snapshot. The invariant check used that snapshot as work tree and the repository Git directory, preserving tracked-file checks.

## Verification performed

All requested Python commands exited 0:

~~~
rules_freshness.py                         exit 0
test_matrix_scoping.py                     exit 0 (23 block, 13 anchor, 8 HTML, 2 oracle cases)
test_no_skill_writes.py                    exit 0 (9 scripts in a read-only copy)
validate_close_estimate.py                 exit 0 (22-case release contract)
validate_corporate_records.py              exit 0 (24-row; 58 record-set, 22 specialist, 27 prose fixtures)
validate_individual_matrix.py              exit 0 (67 propositions; 46 point-of-use markers)
validate_individual_structure.py           exit 0 (96 Markdown files; 94 cross-references)
validate_rules.py                          exit 0 (4 rules files; 48 cross-year checks)
validate_stock_issuance.py                 exit 0 (43 full-artifact fixtures; 24 prose evals)
tools/parse-verify/test_verify.py          exit 0 (all checks pass)
~~~

node scripts/check-invariants.mjs also exited 0 with 0 failure(s), 0 warning(s). It confirmed all 38 concrete tax router paths, all 294 qualifying pointers, manifest versions, and the nine new templates. I independently confirmed the nine exact template filenames in prose exist, and found no broken changed cross-reference in the requested files. The pre-formation binder's existing references are coherent; neither new scenario leaks engagement data.

## Findings

### HIGH — The persisted state machine cannot represent four documented statuses

**Files:** plugins/taxcraft/skills/tax/schemas/stock-issuance-audit.schema.json:14-25; plugins/taxcraft/skills/tax/evals/validate_corporate_records.py:465-480; plugins/taxcraft/skills/tax/scenarios/stock-issuance.md:70-111.

The prose defines eight statuses: PROPOSED, COUNSEL HOLD, APPROVED — NOT ISSUED, ISSUED — CONSIDERATION OUTSTANDING OR ESCROWED, PURPORTED ISSUANCE — CONSIDERATION UNVERIFIED, ISSUED AND PAID — OTHER EVIDENCE INCOMPLETE, ISSUED AND RECONCILED, and DISPUTED OR DEFECTIVE. The schema instead permits six values: it adds undocumented FACT_CONFLICT and CLOSING_PENDING, while omitting proposed, approved-not-issued, deferred/escrowed, and issued-and-paid/incomplete-evidence states. The derivation has the same limitation.

This is behavioral. I ran a no-evidenced-issuance artifact with every gate unverified and status PROPOSED; the validator rejected it because both enums omit PROPOSED. Also, the prose says contradictory pre-issuance labels force COUNSEL HOLD, but code derives undocumented FACT_CONFLICT first. The new boolean correctly gates DISPUTED_OR_DEFECTIVE on an evidenced purported issuance, but total precedence is fail-closed only within an incomplete, different state machine.

**Replacement:** make the schema enum and derived_tranche implement all eight prose labels (using documented machine spellings), and remove FACT_CONFLICT/CLOSING_PENDING unless the prose is deliberately changed to define them. Add facts needed to distinguish the three no-issuance and three post-issuance states. Do not require a full closing manifest for PROPOSED or APPROVED_NOT_ISSUED. Add valid fixtures for all eight statuses and negative fixtures for evidenced/non-evidenced conflicts.

### HIGH — Generic state authority validation accepts unrelated federal .gov pages

**File:** plugins/taxcraft/skills/tax/evals/validate_corporate_records.py:236-247,323-343.

The old Washington branch checked the legislature hostname, RCW path/citation, regulator hostname, and securities path. The replacement only requires a hostname ending in .gov; it does not establish that the source belongs to the stated state, a securities regulator, the relevant statute, or the chosen capacity rule.

I constructed and ran an otherwise-clean Washington artifact with both its capacity source and securities authority set to https://www.nasa.gov/mars. It passed:

~~~
PASS: hostile NASA .gov capacity and Washington securities authority accepted
~~~

A hostile artifact can therefore claim ISSUED_AND_RECONCILED with authority unrelated to the issuance. The generic issued/outstanding/treasury identity at line 246 is reasonable arithmetic, but it cannot restore the lost source/rule verification; COUNSEL_VALIDATED_JURISDICTION_RULE has no extra validation.

**Replacement:** remain jurisdiction-neutral in code, but add data-driven authority profiles under states/<code>/ that pin official host, path/citation patterns, regulator family, and capacity treatment. Load that profile instead of hard-coding a state branch. Until a profile exists, require COUNSEL_HOLD, not a verified/reconciled state route. Add unrelated-.gov negative fixtures for both capacity and state securities sources.

### HIGH — The new information-return scenario contradicts disregarded-entity payroll treatment

**Files:** plugins/taxcraft/skills/tax/scenarios/information-returns.md:1-5,130-133; plugins/taxcraft/skills/tax/entities/disregarded.md:188-200.

The scenario covers W-2s but tells every disregarded entity to use the regarded owner's EIN as issuer. The established module says that is correct for 1099s, while an SMLLC employer uses its own EIN for W-2/W-3/941/940.

**Replacement:** replace item 4 at information-returns.md:130 with: “For a disregarded entity, determine the return type: use the regarded owner's EIN for 1099/1042-S, but the SMLLC employer's own EIN for Forms W-2/W-3/941/940; see entities/disregarded.md.”

### MEDIUM — The new payee-certificate destination is not a canonical portable path

**Files:** plugins/taxcraft/skills/tax/scenarios/information-returns.md:46-50; plugins/taxcraft/skills/tax/layout.md:74-116; plugins/taxcraft/skills/tax/naming.md:1-3,57-65; plugins/taxcraft/skills/tax/entities/disregarded.md:20-53.

The scenario creates entities/<slug>/corporate/payees/. layout.md does not define it, naming.md claims ownership of every expected filename but defines no W-8/8233 names, and the entity-only path excludes individual-owned and nested disregarded issuers.

**Replacement:** add a canonical scope-aware permanent payee-certificate location to layout.md, add W-9/W-8/8233 filename patterns to naming.md, and replace the literal path with that defined anchor (for example, an <issuer-root>/payees/ anchor resolved by existing regarded/disregarded rules).

### MEDIUM — The public artifact schema break has no migration or release guidance

**Files:** plugins/taxcraft/skills/tax/schemas/stock-issuance-audit.schema.json:21,25-26,53,107; plugins/taxcraft/skills/tax/schemas/stock-issuance-closing-manifest.schema.json:50; plugins/taxcraft/skills/tax/migrate.md:1-134; CHANGELOG.md:54-76.

The added required boolean and renamed enum members make pre-commit artifacts invalid. I ran a former-shape artifact using WA_EXEMPTION, WA_REACQUIRED_AUTHORIZED_UNISSUED, and no purported_issuance_evidenced; the validator rejected all three. Neither migration instructions nor release notes map old names or explain the human review necessary for the new fact.

**Replacement:** add a stock-issuance-artifact migration phase and a Breaking artifact migration changelog note. Map old enum values, require explicit evidence review for the boolean (never infer it), and either preserve schema 1.0 support or version the schema plus ship a migration command and before/after examples.

### MEDIUM — The stated MINOR rationale violates the project versioning policy

**File:** CHANGELOG.md:13-17,28-31.

MINOR is specified for a new references/*.md, shipped script, graduating skill, or findings field. The commit adds no reference file or script; it adds two scenario files, yet calls them “two new reference files” as the reason for 0.2.0/0.7.0. Although 0.x may take breaking MINOR changes, this release does not state that as its rationale.

**Replacement:** use PATCH under the present policy, or amend the policy before release to include routed scenarios/*.md and public artifact-schema breaks; then say “two new scenario files” and explicitly name the breaking artifact migration as the MINOR reason.

### MEDIUM — Portability doctrine is in the router, contrary to repository standards

**Files:** plugins/taxcraft/skills/tax/SKILL.md:252-282; CONTRIBUTING.md:45-53.

The 31-line addition contains a taxonomy, behavioral prohibitions, and an editorial method. Repository standards reserve SKILL.md for trigger/router content and put depth in reference documents.

**Replacement:** move the doctrine to portability.md (or another detailed reference), leaving only a concise routing invariant and pointer in SKILL.md.

### LOW — The new release assertions are brittle and weak

**File:** plugins/taxcraft/skills/tax/evals/validate_corporate_records.py:78-88,2178-2259.

require() is normalized literal-substring matching. Equivalent wording changes break CI, while isolated terms such as Form 8233, PURPORTED ISSUANCE, final rule, or domestic survive deletion of material qualifications.

**Replacement:** parse the relevant Markdown heading/section and assert behavioral tuples or targeted regexes. Add behavioral fixtures for unrelated .gov sources, every status-precedence branch, and legacy artifacts rather than pinning prose fragments.

### LOW — New modules duplicate facts despite the strict one-fact/one-file rule

**Files:** plugins/taxcraft/skills/tax/scenarios/information-returns.md:89-90,122-124; plugins/taxcraft/skills/tax/entities/c-corp.md:222; plugins/taxcraft/skills/tax/scenarios/corporate-records.md:549; plugins/taxcraft/skills/tax/SKILL.md:284-286.

The March-15 1042/1042-S deadline is repeated in the new scenario and C-corp module. Payee-register fields are repeated in the new scenario and corporate-records table, contrary to the declared strict rule.

**Replacement:** choose one owner. Keep the detailed workflow in information-returns.md, replace the C-corp deadline text with a pointer, and make the corporate-records payee row point to “Reconciliation at year end.”

## Changelog claim sample

Sampled claims about the new scenarios, portability rule, nine templates, generic enum names, and fixture totals match the diff. The all-evals/invariants claim is true at the pinned commit. The claim that the two new scenario files are “reference files,” and its stated version rationale, is inaccurate.

VERDICT: NOT APPROVED


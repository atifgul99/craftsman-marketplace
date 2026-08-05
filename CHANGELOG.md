# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Versioning policy

This project doesn't (yet) follow strict SemVer against a public API, but plugin `version` bumps
follow this intent:

- **MAJOR:** a skill is removed or renamed, or a `description:` trigger's semantics change in a
  way that changes when it fires (not just wording).
- **MINOR:** a new skill graduates from `drafts/` into `skills/`, a new `references/*.md` file
  is added to an existing skill, a new shipped script is added under a skill's `scripts/`, or the
  findings emission format contract gains a field.
- **PATCH:** guidance edits within an existing reference or `SKILL.md` that don't change trigger
  semantics or add/remove a skill/reference.

The project is publicly launched at `0.2.0`; the `0.x` line continues post-launch (breaking changes
may still land in MINOR while the project settles). `1.0.0` is reserved for the point the skill set
and workflow are considered stable enough to commit to strict SemVer against the trigger surface,
not a synonym for "public."

## [0.3.1] (unreleased)

### Added

- **Marketplace discovery metadata.** Claude marketplace metadata now carries a release version
  and development category, while the public GitHub listing presents Craftsman as a Claude Code
  and Codex plugin rather than a Claude-only tool.
- **Maintainer-gated open-source governance.** Contributions now have an explicit fork-and-PR
  policy, automatic sole-maintainer ownership assignment, a Contributor Covenant Code of Conduct,
  and a public Discussions space for open-ended feedback.
- **Native Codex presentation mark.** The Codex manifest now provides a lightweight local SVG for
  its composer icon and plugin logo. The GitHub README includes a clearly labelled visual preview
  of the real worked-example report shape.
- **Lint-audit CLI regression check.** CI now proves the helper's help and invalid-path flows do not
  create a `.craftsman/` workspace.

### Fixed

- **Verified Codex installation documentation.** Both READMEs now document the native marketplace
  install flow alongside Claude Code rather than describing Codex as unverified.
- **Unsafe lint-audit argument handling.** `eslint-rule-audit.mjs` validates the positional root
  before creating output and treats `--help` as a non-mutating help request.

## [0.3.0] (2026-08-03)

The response to the first detailed field report from a live production audit: a nine-domain,
107-finding run against a real revenue-carrying app. Every change here closes a gap that run
actually hit.

### Added

- **Shipping-target check in discovery.** A run from a branch behind the default branch reported
  already-shipped fixes as missing. `craft-audit` now compares `HEAD` against the default remote
  branch (or a project-declared deploy branch/commit) before reading any code, and stops to ask
  which tree to audit when behind or diverged. No remote at all is common and not an error. It's
  recorded as "shipping target unknown," and the audit proceeds against the working checkout.
- **Subagent write precondition and the fenced-block fallback contract.** The subagent prompt now
  states outright that the worker must write its own `findings.md` and confirm it did. When a
  harness policy blocks that, the worker instead returns the complete file as one fenced code
  block and nothing else, and the orchestrator persists it verbatim before running validation.
  Transport corruption (HTML entities, truncation) is never patched over with a normalizer:
  a persisted file that fails validation gets re-prompted, not repaired.
- **`scripts/validate-findings.mjs`**, a deterministic implementation of the six-check mechanical
  validation checklist already documented in `workspace.md`. It's now the preferred way to run
  that checklist. Hand-checking remains the documented fallback, which makes "a file that fails
  any check is a blocker" an enforceable rule instead of an aspiration.
- **Optional `Confidence` field** (`verified | inferred | unverified-from-repo`) on a finding,
  appended after `Last-checked`. Absence means `verified`, so every existing `findings.md` stays
  valid unchanged. `unverified-from-repo` covers claims that depend on something outside the repo
  (dashboard config, branch protection, secrets) and must describe the repo gap plus the human
  check needed, without asserting the external condition is true.
- **Semantic cross-domain rollup fallback.** The exact `(scope, class, resource)` key rollup
  produced zero groups on the real 107-finding run even though genuine duplicates existed:
  independent domain passes invent different `class`/`resource` vocabulary for the same defect on
  a first run. A mandatory second pass now groups by what a finding actually cites (file:line,
  route, table, env key) instead of by string match.
- **Repo-native context docs** (`CLAUDE.md`, `AGENTS.md`, `README.md`, applicable `docs/`) added to
  the discovery evidence list, with an explicit re-verify caveat: cite the doc, then check the
  code, never treat it as ground truth on its own. "Documentation contradicts code" is now a
  finding class in its own right.
- **Gated surfaces in `craft-fix`.** Optional, no setup required: a project can declare surfaces
  (payment webhooks, billing math, etc.) via `.craftsman/gated-surfaces.md`, its own
  `CLAUDE.md`/`AGENTS.md`/README, or the user saying so in chat. A finding touching a declared
  surface is never auto-fixed, regardless of severity or how small the diff looks. It's routed to
  a human-approval bucket instead.

### Changed

- The step-5 false-negative guard (verify with grep before accepting a reviewer's "this is
  missing" claim) now has its converse stated: the tree being grepped has to be the tree that
  ships, per the new shipping-target check. A stale checkout makes already-shipped fixes look
  missing just as easily as a bad grep makes a real gap look present.

### Notes

Deliberately declined, and why:

- **A controlled `class` vocabulary per domain.** Would fight context bloat and overfit to one
  large repo; the semantic rollup fallback solves the actual problem (missed duplicates) without
  forcing every future domain into a fixed taxonomy.
- **Mandating `resource` be a repo-relative file path.** Would break re-run matching for findings
  about DB tables and env vars, which aren't files. `resource` keeps meaning "the canonical thing
  it's about," with a file path preferred only where a single file is genuinely the subject.
- **A required `fix-risk` field on every finding.** The plan-first gate and the new gated-surfaces
  gate already cover the dangerous cases; adding a required field to a schema that four other
  things parse wasn't worth it for the marginal cases left over.
- **Making a git remote a hard prerequisite for the shipping-target check.** Local-only projects
  are valid audit targets; no remote is handled as "unknown," not as a blocker.

## [0.2.1] (2026-08-03)

Corrections found after the 0.2.0 tag was cut, so this release brings the published version in
line with what the project actually does.

### Added

- **README Quickstart and Compatibility sections.** Walks a first-time reader from install through
  the trigger phrase, the `.craftsman/` workspace files that appear, and acting on findings via
  `craft-fix`.

### Changed

- README/ROADMAP/CHANGELOG/manifest wording no longer describes the re-run protocol as a compiled
  "fingerprint diff" or readiness grades as "mechanical." Both are agent-executed against a
  written rule, and the text now says so.
- Corrected the worked example's domain count in two places (nine of ten, not four).
- Compatibility section no longer converts an absent minimum Claude Code version into a positive
  guarantee.
- Stale `*-craft` naming corrected to `craft-*` in `ROADMAP.md`, `CONTRIBUTING.md`, and
  `craft-audit/SKILL.md`.

### Fixed

- A re-run whose domain pass didn't execute could mark prior open findings `fixed`, inverting the
  project's "not seen ≠ fixed" rule and contradicting `rerun.md` (which is authoritative). Both
  sites in `workspace.md` now require the pass to have actually run and re-checked the resource.
- The cross-skill pointer check in `scripts/check-invariants.mjs` still matched the pre-rename
  `<name>-craft` form, so it had been passing vacuously since the rename: it validated nothing.
  Corrected to `craft-*`; it now exercises the real pointers.

### Removed

- `displayName` from the plugin manifest, since it imposed a Claude Code v2.1.143 floor for a
  purely cosmetic field.

## [0.2.0] (2026-08-03, public launch)

Dev work (craft-ai graduation) landed 2026-07-15; the version was held back from public installs
until pre-ship cleanup finished, so this entry carries the public-release date.

### Added

- **Graduated `craft-ai`** (10th domain skill) from `drafts/` into `skills/`. LLM-integration
  surface: prompt-injection, key/spend safety, PII-to-model APIs, reliability/evals. Four
  references (`prompt-injection`, `keys-and-spend`, `data-privacy`, `reliability-evals`). Wired
  into craft-audit (discovery applicability, domain code `AI`, load list, emission HEADING_RE) and
  `scripts/check-invariants.mjs`. Worked example marks craft-ai N-A for Invoicely (no LLM surface).

### Changed

- Domain count: nine → ten. Skill total: craft-audit + craft-fix + 10 domains = 12 skills.
- Plugin/marketplace descriptions and README skill table updated for craft-ai.
- `drafts/` empty (no domains currently incubating).

### Removed

- Pre-ship cleanup: internal dogfooding feedback folder and its marker blocks stripped from the
  skills, README, ROADMAP, CLAUDE.md, and `.gitignore` ahead of the public launch pass.

### Released

- **Public launch.** Marketplace and plugin opened to external installs at this version.

## [0.1.0] (2026-07-15)

Dogfooding milestone: fix companion, `craft-` rename, findings emission contract, CI grammar
gates, full nine-domain worked example. Internal dogfooding instrumentation remains by design.

### Breaking (for pre-release installs)

- Renamed all skills to the `craft-` prefix (craftsman-audit → craft-audit, craftsman-fix →
  craft-fix, X-craft → craft-X) for consistent naming and slash-menu grouping.

### Added

- **New skill: `craft-fix`.** An action companion (not a domain; the count stays 9) that drives
  fixes against an existing `craft-audit` workspace: parses a finding ID / domain / "top 5 off the
  climb sequence" invocation, re-verifies each pick's fingerprint against current code, gets explicit
  user approval before editing, gates 🔴 auth/migration/data-handling fixes behind a written plan,
  batches by surface (disjoint file ownership for parallel subagents), and appends a `Fix-attempt`
  annotation without ever setting a finding's status to `fixed` itself. Only a `craft-audit`
  re-run's re-observation of the finding can, per "not seen ≠ fixed". `scripts/check-invariants.mjs` exempts
  `craft-fix` from the domain `## Audit checklist (for craft-audit)` heading requirement.
- **Findings emission contract:** canonical `findings.md` heading grammar + mechanical validation
  before synthesis (path-bound scope/domain, re-prompt on fail, no normalizer). Restated in all
  nine domain skills. Library-monorepo scoping in discovery/workspace.
- **Invariant checks (f):** `scripts/check-invariants.mjs` validates worked-example findings against
  the emission grammar (fail-closed on non-canonical headings, including indent/blockquote/list/
  Setext), requires domain skills to restate the format, and ships regression fixtures.
- **Worked example:** full Invoicely Tier-1 snapshot, all 9 domains under
  `craftsman/examples/craftsman-output/`.
- **Intake cadence (P4):** documented drain protocol in ROADMAP (still temporary pre-ship).
- Packaging and repo-hygiene: `CONTRIBUTING.md`, `SECURITY.md`, issue templates, CI workflow.
- `craft-ai` incubating in `drafts/`, not loaded; graduates per `drafts/README.md`.

### Changed

- Compliance/incident/cost/load/email checks folded into existing domain checklists rather than
  standing up new domains (see `ROADMAP.md` for graduation triggers).
- Root `README.md` rewritten for an external reader.
- `marketplace.json` / plugin descriptions reworded for product framing; `homepage` + `license`.
- `craftsman/README.md`: real marketplace install flow; Codex/Cursor paths labeled experimental.
- `ROADMAP.md` "Removal map" completed for pre-ship instrumentation sites.

### Fixed

- Stale skill count in `CLAUDE.md` (now 10 skills / 9 domains + craft-fix action skill).
- Findings format drift from dogfooding: domain subagents inventing alternate heading shapes.

### Chore

- `.gitignore`: `.remember/` (session memory) excluded from `git add -A`.

## [0.0.1] (baseline dogfooding state)

Baseline state of the plugin as of this changelog's introduction:

- **10 skills**: `craft-audit` (orchestrator) + 9 domain skills (`craft-ux`, `craft-frontend`,
  `craft-backend`, `craft-db`, `craft-security`, `craft-infra`, `craft-observability`,
  `craft-testing`, `craft-lint`), each with a complete `references/*.md` set. (Pre-rename names
  used the older `*-craft` / `craftsman-*` forms.)
- **Orchestrator with a durable workspace.** `craft-audit` discovers project shape, decides
  which domains apply, and plans/tracks a whole-project audit in a `.craftsman/` workspace inside
  the audited project: discovery, applicability, a master tracker with per-domain readiness
  grades, and per-scope/per-domain findings.
- **Re-run protocol.** Fingerprint-based diffing across audit runs: staleness detection against the
  current commit, re-observation and classification of prior findings (open / fixed / regressed /
  new), and a "not seen ≠ fixed" rule that prevents a skipped check from masquerading as a
  resolved one.
- **Worked example.** A complete synthetic `.craftsman/` audit tree ships under
  `craftsman/examples/craftsman-output/` as a teaching artifact (four domains in the original
  snapshot; expanded to nine in 0.1.0).
- **Pre-ship dogfooding instrumentation still present** (by design, not yet removed): an internal
  feedback folder and marker blocks embedded in each skill, both stripped before public launch.

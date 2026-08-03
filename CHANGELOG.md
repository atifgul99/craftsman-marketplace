# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Versioning policy

This project doesn't (yet) follow strict SemVer against a public API, but plugin `version` bumps
follow this intent:

- **MAJOR** — a skill is removed or renamed, or a `description:` trigger's semantics change in a
  way that changes when it fires (not just wording).
- **MINOR** — a new skill graduates from `drafts/` into `skills/`, or a new `references/*.md` file
  is added to an existing skill.
- **PATCH** — guidance edits within an existing reference or `SKILL.md` that don't change trigger
  semantics or add/remove a skill/reference.

The project is publicly launched at `0.2.0`; the `0.x` line continues post-launch (breaking changes
may still land in MINOR while the project settles). `1.0.0` is reserved for the point the skill set
and workflow are considered stable enough to commit to strict SemVer against the trigger surface —
not a synonym for "public."

## [0.2.1] — 2026-08-03

Corrections found after the 0.2.0 tag was cut, so this release brings the published version in
line with what the project actually does.

### Added

- **README Quickstart and Compatibility sections.** Walks a first-time reader from install through
  the trigger phrase, the `.craftsman/` workspace files that appear, and acting on findings via
  `craft-fix`.

### Changed

- README/ROADMAP/CHANGELOG/manifest wording no longer describes the re-run protocol as a compiled
  "fingerprint diff" or readiness grades as "mechanical" — both are agent-executed against a
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
  `<name>-craft` form, so it had been passing vacuously since the rename — it validated nothing.
  Corrected to `craft-*`; it now exercises the real pointers.

### Removed

- `displayName` from the plugin manifest — it imposed a Claude Code v2.1.143 floor for a purely
  cosmetic field.

## [0.2.0] — 2026-08-03 (public launch)

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

## [0.1.0] — 2026-07-15

Dogfooding milestone: fix companion, `craft-` rename, findings emission contract, CI grammar
gates, full nine-domain worked example. Internal dogfooding instrumentation remains by design.

### Breaking (for pre-release installs)

- Renamed all skills to the `craft-` prefix (craftsman-audit → craft-audit, craftsman-fix →
  craft-fix, X-craft → craft-X) for consistent naming and slash-menu grouping.

### Added

- **New skill: `craft-fix`.** An action companion (not a domain — the count stays 9) that drives
  fixes against an existing `craft-audit` workspace: parses a finding ID / domain / "top 5 off the
  climb sequence" invocation, re-verifies each pick's fingerprint against current code, gets explicit
  user approval before editing, gates 🔴 auth/migration/data-handling fixes behind a written plan,
  batches by surface (disjoint file ownership for parallel subagents), and appends a `Fix-attempt`
  annotation without ever setting a finding's status to `fixed` itself — only a `craft-audit`
  re-run's re-observation of the finding can, per "not seen ≠ fixed". `scripts/check-invariants.mjs` exempts
  `craft-fix` from the domain `## Audit checklist (for craft-audit)` heading requirement.
- **Findings emission contract:** canonical `findings.md` heading grammar + mechanical validation
  before synthesis (path-bound scope/domain, re-prompt on fail, no normalizer). Restated in all
  nine domain skills. Library-monorepo scoping in discovery/workspace.
- **Invariant checks (f):** `scripts/check-invariants.mjs` validates worked-example findings against
  the emission grammar (fail-closed on non-canonical headings, including indent/blockquote/list/
  Setext), requires domain skills to restate the format, and ships regression fixtures.
- **Worked example:** full Invoicely Tier-1 snapshot — all 9 domains under
  `craftsman/examples/craftsman-output/`.
- **Intake cadence (P4):** documented drain protocol in ROADMAP (still temporary pre-ship).
- Packaging and repo-hygiene: `CONTRIBUTING.md`, `SECURITY.md`, issue templates, CI workflow.
- `craft-ai` incubating in `drafts/` — not loaded; graduates per `drafts/README.md`.

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

## [0.0.1] — baseline dogfooding state

Baseline state of the plugin as of this changelog's introduction:

- **10 skills**: `craft-audit` (orchestrator) + 9 domain skills (`craft-ux`, `craft-frontend`,
  `craft-backend`, `craft-db`, `craft-security`, `craft-infra`, `craft-observability`,
  `craft-testing`, `craft-lint`), each with a complete `references/*.md` set. (Pre-rename names
  used the older `*-craft` / `craftsman-*` forms.)
- **Orchestrator with a durable workspace.** `craft-audit` discovers project shape, decides
  which domains apply, and plans/tracks a whole-project audit in a `.craftsman/` workspace inside
  the audited project — discovery, applicability, a master tracker with per-domain readiness
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

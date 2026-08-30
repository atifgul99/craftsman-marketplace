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

## [Unreleased]

Metadata only — no version bump. Fold into whatever ships next.

### Added

- **`craftsman` symlink at the repository root**, pointing at `plugins/craftsman`. This is a
  compatibility shim, not part of the plugin layout. A directory-submission made on 2026-08-04 is
  still pending review, and it may have recorded `craftsman` as its "path within repository" —
  which the move to `plugins/craftsman` would have invalidated. The symlink makes both the old and
  new coordinates resolve, so the pending submission stays viable regardless of what was recorded.
  Remove it once that submission is resolved.

### Changed

- **Rewrote the three manifest descriptions.** Dropped the "Written by a software engineer of 25
  years, including at Microsoft and Amazon" sentence. It was authority-by-assertion in a product
  whose own non-negotiables are "plain-language findings, consequence before jargon" and "evidence
  over assumption, go look" — and "including at" was ungrammatical besides. Ex-FAANG is also close
  to inert as a differentiator in a directory of 2,282 plugins, where `A full worked example is
  included` does more work because a skeptic can verify it. The credential stays on the README,
  where a reader has already opted in, rephrased so it explains the standard rather than just
  asserting it. Characters reinvested in the searchable opener and the scope disclaimers.
- **Reworked plugin keywords.** The old list was half internal structure (`ux`, `frontend`,
  `backend`, `infra`, `lint`) and carried a bare `ai` tag that reads as "this is an AI plugin"
  rather than "this audits your LLM integration". Replaced with tags describing the situation a
  searcher is actually in: `vibe-coding`, `lovable`, `replit`, `bolt`, `v0`, `ai-generated-code`,
  `code-audit`, `llm-integration`, `prompt-injection`, `multi-tenant`.

  Scope note, so nobody re-litigates this later: keywords do **not** reach the Anthropic community
  directory. Zero of its 2,282 catalog entries carry a `keywords` field — the ingestion strips it,
  confirmed against a plugin whose own manifest declares keywords. The catalog keeps `name`,
  `description`, `source`, `homepage`, and sometimes `category`. This change is for the
  self-hosted marketplace, which is the install path the README documents; discovery in the
  directory rides entirely on `description`.

## [0.5.0] (2026-08-24)

### Added

- **`craft-ux` copy and decoration anti-slop catalog.** A new "Copy & Decoration Tells" section
  in `anti-patterns.md`, scoped to landing/portfolio/marketing surfaces: an em-dash ban, an
  eyebrow-count formula (greppable), ~25 production-tested tells (section-number eyebrows,
  scroll cues, fake version footers, decorative status dots), and a premium-consumer
  beige+brass palette tell with grep seeds. `composition.md` gains hero-discipline hard numbers,
  CTA intent/wrap/contrast rules, and layout rhythm caps (zigzag, marquee, split-header, bento
  cell count). `layer-5-motion.md` gains a Forbidden Animation Patterns section (the
  `window.addEventListener('scroll')` ban, GSAP `start: "top top"` pinning). Reference material
  informed by the current upstream `taste-skill`, re-scoped from its absolute-ban voice into
  craft-ux's flag-with-override-path disposition.
- **`craft-ux/references/motion/fluid-gestures.md`** — momentum physics for gesture-driven
  surfaces (sheets, drag, swipe, carousels): velocity handoff, exponential-decay momentum
  projection, rubberbanding, interruptible-spring principles (animate from the presentation
  value, blend velocity on reversal, decompose X/Y springs), Apple-style damping/response
  values, a gesture feel checklist, and material/vibrancy rules — scoped away from plain
  dashboards. Portions adapted from `emilkowalski/skill` (MIT; see `THIRD_PARTY_NOTICES.md`),
  which also prompted a correction to `emil-craft.md`'s Framer Motion hardware-acceleration
  claim to match current upstream docs.
- **`craft-ux/references/starter-kits.md`** — 19 vetted Google Fonts pairings (15 by use case +
  4 SaaS-landing Persuade-mode variants) and 15 palettes in this skill's token roles, every pair
  WCAG-verified (`scripts/verify-palettes.py`, CI-gateable). A mandatory variation protocol
  prevents deterministic "always the same pairing" generation: pairings and palettes are
  independent axes (285 combinations), rotation is required, and brief adjectives override the
  category default. Font/palette research informed by `ui-ux-pro-max` (MIT; see
  `THIRD_PARTY_NOTICES.md`); all values independently re-curated against craft-ux's own bans.
- **`THIRD_PARTY_NOTICES.md`** — MIT notices for the two upstream sources above.
- **Operational readiness in `craft-observability`.** A new `references/operational-readiness.md`
  covers the layer between "the service is instrumented" and "a human can operate it": naming the
  core business transaction and instrumenting its lifecycle, detecting stuck work and terminal
  states whose promised artifact never appeared, committing ops queries as a file rather than
  prose, separating expected business failures from system failures so customer mistakes don't
  bury real bugs in the error tracker, the on-call contract and a five-minute "is it broken?" tree,
  an acceptance drill (success, system failure, business failure, stuck detection, alert delivered),
  and measuring readiness from a source of truth with verified history instead of a currently-green
  check. Six matching audit-checklist items, maturity-aware rather than one-size-fits-all: the
  transaction, stuck-work, and delivery checks apply from day one, while team-shaped requirements
  (a backup operator, an ack convention, an escalation path) are gated on a second person actually
  being able to respond — so a solo pre-launch builder is not handed a pager rotation.
- **Cross-references for the new layer.** `grafana.md` now prefers a deep-link panel over a graph
  known to return no data; `slo-alerts.md` requires retained history behind the SLO window and
  points service-level on-call facts at one place; craft-audit's `recommended-stack.md` gains a
  Tier-1 row for "no way to see whether the core transaction finished".
- **`craft-audit/references/synthesis.md`** — the full step-7 synthesis protocol: findings-file
  validation, the by-hand fallback checklist, path binding, the remediation closure check, dedup,
  and ranking. Extracted from `SKILL.md` rather than newly written.
- **`craft-audit/references/delegation.md`** — the ≤3/>3 `(scope, domain)` threshold, the context
  budget split between orchestrator and subagent, subagent prompt requirements, and the
  write-capability fallback. Also extracted from `SKILL.md`.

### Changed

- **Skill trigger descriptions trimmed 28%** (11,377 → 8,122 characters across the twelve skills).
  Claude Code's skill listing has a character budget of roughly 1% of the context window, shared
  with every other skill the user has installed; on overflow it drops descriptions starting with
  the least-invoked skills, which would strip the trigger keywords from exactly the domain skills
  that rely on ambient matching. Trigger phrasing is preserved and front-loaded; the cross-domain
  boundary arbitration that used to live in the descriptions moved into a new `## Scope boundaries`
  section in the body of `craft-ai`, `craft-backend`, `craft-frontend`, `craft-infra`,
  `craft-security`, and `craft-testing`.
- **`craft-audit/SKILL.md` reduced from 3,941 to ~3,000 words**, back under the router-skill
  ceiling, by extracting the two references above rather than cutting guidance.
- **`drafts/` moved from `craftsman/drafts/` to the repository root**, so the incubator is no
  longer part of the installed plugin payload. It was already excluded from skill loading; now it
  is excluded from what ships.

### Fixed

- **Helper scripts are now addressed through `${CLAUDE_PLUGIN_ROOT}`.** `craft-audit` and
  `craft-lint` previously told the agent to run their `.mjs` helpers at a literal
  `/absolute/path/to/craftsman/...` placeholder. Once the plugin is installed it lives outside the
  audited project, so that path had to be guessed. Four call sites fixed, across both `SKILL.md`
  files and `craft-audit/references/workspace.md`.

## [0.4.0] (2026-08-10)

Released without a changelog entry at the time; see the release notes for `v0.4.0` and commit
`2a29f21` (audit workflow hardening, install documentation, craft-ux supply-chain fix).

## [0.3.2] (2026-08-05)

### Security

- **Hardened public-repository controls.** CI actions are pinned to full immutable SHAs and
  Dependabot now tracks GitHub Actions updates. Published releases and `v*` tags are protected;
  private vulnerability reporting, Dependabot alerts and updates, malware alerts, grouped security
  updates, secret push protection, and CodeQL default setup are enabled in GitHub.

## [0.3.1] (2026-08-05)

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

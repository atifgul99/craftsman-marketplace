# Security Policy

## What this plugin is (and isn't)

`craftsman` is declarative Markdown (`SKILL.md` + `references/*.md` files) plus local Node scripts
for invariant checks and maintainer-only vendoring (no dependencies). It:

- makes no network calls while auditing a project,
- collects **no telemetry**,
- and does not execute any code on your behalf beyond what your Claude Code (or Codex/Cursor)
  session already does when following the skill's instructions.

The skills read files in the project you point them at and write findings into a local `.craftsman/`
workspace inside that project. They do not transmit project files or findings to Craftsman.

All review guidance is bundled locally, including the UX guideline list. Maintainers may explicitly
run `scripts/refresh-web-interface-guidelines.mjs` before a release to download a SHA-pinned public
source for human review; that script never runs during an audit, install, or normal plugin use. The
repository does not include telemetry, a background process, or a service endpoint that receives
your project data.

## Reporting a vulnerability

If you find a security issue in this repo (for example, a skill instruction that could lead an
agent to do something unsafe, or an issue with `scripts/check-invariants.mjs`), open a
[GitHub security advisory](https://github.com/GulLabs/craftsman-marketplace/security/advisories/new)
on this repository.

Please don't open a public issue for anything you believe is a security concern until it's been
triaged privately.

## Scope

This policy covers the contents of this repository (the marketplace and plugin manifests, the
skill files, and `scripts/check-invariants.mjs`). It does not cover Claude Code, Codex, Cursor, or
any other host tool that loads these skills. Report issues in those tools to their respective
maintainers.

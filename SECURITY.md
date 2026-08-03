# Security Policy

## What this plugin is (and isn't)

`craftsman` is declarative Markdown (`SKILL.md` + `references/*.md` files) plus a single Node
script used for CI invariant checks (`scripts/check-invariants.mjs`, no dependencies). It:

- makes **no network calls**,
- collects **no telemetry**,
- and does not execute any code on your behalf beyond what your Claude Code (or Codex/Cursor)
  session already does when following the skill's instructions.

The skills read files in the project you point them at and write findings into a local `.craftsman/`
workspace inside that project. They don't transmit anything off your machine.

## Reporting a vulnerability

If you find a security issue in this repo (for example, a skill instruction that could lead an
agent to do something unsafe, or an issue with `scripts/check-invariants.mjs`), open a
[GitHub security advisory](../../security/advisories/new) on this repository.

Please don't open a public issue for anything you believe is a security concern until it's been
triaged privately.

## Scope

This policy covers the contents of this repository (the marketplace and plugin manifests, the
skill files, and `scripts/check-invariants.mjs`). It does not cover Claude Code, Codex, Cursor, or
any other host tool that loads these skills — report issues in those tools to their respective
maintainers.

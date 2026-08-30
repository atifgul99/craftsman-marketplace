# Privacy Policy

_Last updated: 2026-08-30_

This policy covers the `craftsman` plugin and this repository. It is written to be checkable: every
claim below is something you can verify by reading the source, which is entirely plain Markdown and
a handful of local Node scripts.

## The short version

**Craftsman collects nothing.** There is no telemetry, no analytics, no account, no server, and no
network call made by the plugin while it audits your project. Nothing about you, your code, or your
audit findings is transmitted to the maintainer.

## What the plugin is

`craftsman` is declarative Markdown (`SKILL.md` plus `references/*.md` files) and local Node scripts
used for invariant checks and maintainer-only vendoring. It has no runtime dependencies. It is
instructions your agent reads, not a service you connect to.

## What it does with your data

- **Reads** files in the project you point it at, so it can audit them.
- **Writes** its findings to a `.craftsman/` workspace inside that same project, on your own disk.
  The plugin instructs you to add that directory to your project's `.gitignore`.
- **Transmits nothing.** Your project files and your audit findings do not leave your machine by
  any action of this plugin.

All review guidance ships bundled in the repository, including the vendored UX guideline list, so
an audit needs no network access to run.

## Important: your agent session is separate

This is the part a shorter policy would leave out.

Craftsman runs *inside* a coding agent you are already using, such as Claude Code, Codex, or Cursor.
**That agent sends your code to its own provider in the normal course of operating**, and it would
do so with or without this plugin installed. Craftsman does not add a destination, change what your
agent sends, or transmit anything on its own — but it also cannot prevent what your agent already
does.

So "Craftsman transmits nothing" is a claim about this plugin, not a claim that your code stays on
your machine. For that, the relevant policy is your agent provider's:

- [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy) (Claude Code)
- your provider's equivalent, for any other agent

## The one script that does use the network

`scripts/refresh-web-interface-guidelines.mjs` downloads a SHA-pinned public source so a maintainer
can review upstream changes before a release. It is run manually by a maintainer, never during an
audit, an install, or ordinary plugin use. It sends nothing; it only fetches.

## What this repository does not contain

No telemetry hooks, no background process, no service endpoint that receives your project data, and
no bundled credentials or API keys.

## Cookies and tracking

None. There is no website and no hosted service associated with this plugin.

## Changes

Material changes to this policy are recorded in [CHANGELOG.md](./CHANGELOG.md) and dated at the top
of this file.

## Questions

Open a [GitHub issue](https://github.com/gul-labs/craftsman-marketplace/issues) or start a
[Discussion](https://github.com/gul-labs/craftsman-marketplace/discussions). For anything you
believe is a security concern, follow [SECURITY.md](./SECURITY.md) and use a private advisory
rather than a public issue.

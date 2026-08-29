# Install Craftsman

This is the complete installation and recovery guide for the Craftsman marketplace. If you arrived
from a repository URL, start here or in the README's **Install** section.

## Identify the four names before you run a command

| Type | Exact value | Do not confuse it with… |
| --- | --- | --- |
| Marketplace source | `GulLabs/craftsman-marketplace` | The marketplace name |
| Marketplace name | `craftsman-marketplace` | The plugin name |
| Plugin name | `craftsman` | The `craft-audit` skill |
| Main entry skill | `craft-audit` | An installable plugin |

The only valid marketplace install selector is:

```text
craftsman@craftsman-marketplace
```

`craft-audit@craftsman-marketplace` is invalid. `craft-audit` is a skill that becomes available
only after the `craftsman` plugin is installed.

For a local clone instead of GitHub, pass its absolute path wherever this guide uses
`GulLabs/craftsman-marketplace` as the marketplace source.

## Claude Code

### Interactive Claude Code

Enter these in the Claude Code chat, in order:

```text
/plugin marketplace add GulLabs/craftsman-marketplace
/plugin install craftsman@craftsman-marketplace
```

Adding the marketplace only makes its plugins discoverable; it does not install Craftsman. Open
`/plugin` and confirm **Craftsman** appears under Installed. Start a new conversation afterward, or
run `/reload-plugins` if Claude Code asks you to reload.

### Terminal / headless Claude Code

```bash
claude plugin marketplace add GulLabs/craftsman-marketplace
claude plugin install craftsman@craftsman-marketplace --scope user
claude plugin list --json
```

`--scope user` installs it for your user account. Use `--scope project` only when the plugin should
be configured for this project, or `--scope local` for machine-local project configuration.

### Update or recover a stale Claude Code install

```bash
claude plugin marketplace update craftsman-marketplace
claude plugin update craftsman@craftsman-marketplace --scope user
claude plugin list --json
```

Start a new Claude Code conversation after an update. If the plugin is missing or disabled, use
`/plugin` to inspect its state and errors, then enable or reinstall **craftsman**—never
`craft-audit`.

### Remove from Claude Code

```bash
claude plugin uninstall craftsman@craftsman-marketplace --scope user
claude plugin marketplace remove craftsman-marketplace
```

Removing the marketplace is optional if you intend to keep it for future updates.

## Codex

### Install

Run these in a terminal:

```bash
codex plugin marketplace add GulLabs/craftsman-marketplace
codex plugin add craftsman@craftsman-marketplace
codex plugin marketplace list --json
codex plugin list --marketplace craftsman-marketplace --json
```

The final list must show `craftsman` from `craftsman-marketplace` as installed. Start a new Codex
chat after the installation. You can also open `/plugins` in Codex to inspect installed plugins.

### Update or recover a stale Codex install

First refresh the marketplace and inspect the installed entry:

```bash
codex plugin marketplace upgrade craftsman-marketplace
codex plugin list --marketplace craftsman-marketplace --json
```

If the entry is still missing or shows an older version after the marketplace refresh, reinstall it:

```bash
codex plugin remove craftsman@craftsman-marketplace
codex plugin add craftsman@craftsman-marketplace
codex plugin list --marketplace craftsman-marketplace --json
```

Start a new Codex chat after reinstalling.

### Remove from Codex

```bash
codex plugin remove craftsman@craftsman-marketplace
codex plugin marketplace remove craftsman-marketplace
```

Removing the marketplace is optional if you intend to keep it for future updates.

## First-use check

In the project you want to assess, use one of these prompts:

```text
Use craft-audit to explain what it would review in this project. Do not create files or modify anything yet.
```

```text
Is this app production-ready? Use craft-audit, but do not modify anything yet.
```

If the skill is unavailable, verify the installed plugin first. A correct marketplace registration
alone is not enough; `craftsman` must be installed and you must use a fresh host session.

## Instructions for an LLM that receives only the repository URL

Copy this prompt together with the URL:

```text
Install Craftsman from https://github.com/GulLabs/craftsman-marketplace.

Determine whether you are operating Claude Code or Codex. Before making changes, read README.md,
INSTALL.md, .claude-plugin/marketplace.json, and the host-specific plugin manifest under
craftsman/.claude-plugin/ or craftsman/.codex-plugin/.

Use these identities exactly:
- marketplace source: GulLabs/craftsman-marketplace
- marketplace: craftsman-marketplace
- plugin to install: craftsman
- entry skill after installation: craft-audit

Add the marketplace, install craftsman@craftsman-marketplace, verify the installed plugin and
version, then start a new host session. Do not install craft-audit@craftsman-marketplace. Do not
start an audit, create .craftsman, edit files, or commit anything until I explicitly ask.
```

## Trust boundary

Review a third-party plugin before installing it. Craftsman is declarative Markdown guidance and
does not include telemetry. It does not send your project files or audit findings to Craftsman. All
review guidance, including the UX guideline list, is bundled locally; see
[SECURITY.md](./SECURITY.md) for the exact boundary.

# Craftsman

The engineering review you'd get from the technical co-founder you don't have.

`craftsman` is a whole-project production-readiness audit plugin: a front-door skill
(`craft-audit`), ten domain craft skills (ux, frontend, backend, db, security, infra,
observability, testing, lint, ai), and an action companion (`craft-fix`) that drives fixes off an
existing audit. Security is one of the ten domains, not the whole product.

**Full docs, the skill table, and a worked example: see the [repo root README](../README.md).**

## Install

### Claude Code (verified)

You need Claude Code installed first: see
[code.claude.com/docs](https://code.claude.com/docs).

Type these into Claude Code's chat box, not a terminal:

```
/plugin marketplace add atifgul99/craftsman-marketplace
/plugin install craftsman@craftsman-marketplace
```

If you're working headlessly (running Claude Code without the interactive chat window, e.g. from a
script), use the terminal equivalents instead:

```bash
claude plugin marketplace add atifgul99/craftsman-marketplace
claude plugin install craftsman@craftsman-marketplace
```

Claude reads the manifest at `.claude-plugin/plugin.json`. See the root [README.md](../README.md)
for install details.

### Codex (verified)

Codex loads the same skills through the included `.codex-plugin/plugin.json` manifest. Add the
marketplace, then install the plugin:

```bash
codex plugin marketplace add atifgul99/craftsman-marketplace
codex plugin add craftsman@craftsman-marketplace
```

From a local clone, replace `atifgul99/craftsman-marketplace` with the absolute path to the clone.
If your Codex build predates marketplace support, use the direct-skill fallback instead:

```bash
for skill in craft-ai craft-backend craft-audit craft-fix craft-db craft-frontend craft-infra craft-lint craft-observability craft-security craft-testing craft-ux; do
  ln -sfn "/absolute/path/to/craftsman/skills/$skill" "$HOME/.codex/skills/$skill"
done
```

### Cursor / other skill-based agents (experimental)

Any tool that reads `SKILL.md`-based skill folders can, in principle, use the same
`skills/<skill-name>/` directories directly. This isn't verified against Cursor's actual skill
loader. The reliable fallback is the same symlink approach as above, pointed at that tool's skills
directory.

## Where the skills live

```text
craftsman/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── skills/            ← SKILL.md + references/ per skill (source of truth for behavior);
│                        craft-audit and craft-lint also ship a scripts/ helper
├── examples/          ← a worked end-to-end .craftsman/ audit
└── drafts/            ← incubating domains, not loaded
```

## License

MIT

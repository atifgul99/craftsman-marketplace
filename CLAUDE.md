# CLAUDE.md

One plugin (`craftsman`) with 12 skills: `craft-audit` (orchestrator) + `craft-fix` (action companion) + 10 domain skills. No build system: skills are declarative Markdown loaded directly by Claude Code.

## Editing rules

**SKILL.md files:**
- `## Audit checklist (for craft-audit)` section is sourced verbatim by the orchestrator: preserve structure and heading level exactly.
- The trigger `description:` is the most critical field: it controls when the skill fires.

**Reference docs (`references/`):**
- Update `## Reference index` in the skill's `SKILL.md` whenever a reference is added or renamed.

## Design principles (non-negotiable)

- **Meet the project where it is.** Audit what exists; never demand a rewrite.
- **Ruthless prioritization.** Lead with the handful that prevent breach/data loss/embarrassment.
- **Plain-language findings.** Consequence before jargon. Persona: vibe-coded MVP builder.
- **Reference-depth split.** SKILL.md = trigger + router. `references/` = method + opinions.

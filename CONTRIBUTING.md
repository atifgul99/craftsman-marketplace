# Contributing

`craftsman` is a set of opinion documents, not application code. That changes what a "good
contribution" looks like.

## Maintainer gate

The repository is open to contributions, but `main` is maintainer-gated. Do not request direct
push access: create a fork, open a pull request, and keep the change focused. Only
[@atifgul99](https://github.com/atifgul99) approves and merges contributions to `main`.

Every pull request must pass CI and have all review conversations resolved before it can merge.
The maintainer may request changes, close a proposal that does not fit the project, or merge a
small urgent correction through a pull request using the repository's auditable maintainer bypass.

## Contributions are opinion edits

Each `craft-*` skill encodes one engineer's standard for a domain: the method and the opinionated
stack, not a neutral survey of options. A contribution that changes what a skill recommends is
changing that opinion, and needs to earn it the same way an internal design decision would:

- **Cite a concrete failure mode**, not a preference. "This guidance is wrong because it produces
  X under Y condition" is a contribution. "I'd phrase this differently" or "I prefer a different
  library" is not, on its own. Tie it to something that actually breaks or misleads.
- **Point to a specific file/section.** A vague "the backend guidance could be better" can't be
  acted on. Name the `SKILL.md` or `references/*.md` file and the passage.
- **Prefer the smallest fix that resolves the failure mode.** Don't refactor around it.

## SKILL.md editing invariants

These are load-bearing: breaking them breaks the orchestrator or the routing system, not just
style.

- **`## Audit checklist (for craft-audit)` is sourced verbatim.** The orchestrator (`craft-audit`)
  reads this exact heading out of every domain skill to build its audit plan. Never rename it,
  never change its heading level, never restructure the section without also updating the
  orchestrator's parsing expectations.
- **`description:` is the routing trigger.** It's the single field that decides whether a skill
  fires for a given request. Changes to it need explicit justification (what request should now
  match, or stop matching, and why), and must stay **≤1,200 characters** (checked in CI).
- **Update `## Reference index` whenever a reference is added or renamed.** A skill's `SKILL.md`
  must list every file under its `references/` folder, and every file it lists must actually exist
  (also checked in CI).

## Reference docs vs. SKILL.md

- `SKILL.md` = trigger + router. It should stay short: what the skill is for, when it fires, and a
  pointer into the reference docs that hold the actual method.
- `references/*.md` = method + opinions. This is where the depth lives: the actual standard,
  worked examples, the specific stack recommendations.

Don't move depth into `SKILL.md` "for convenience." It breaks the split that keeps the skill fast
to load and easy to route.

## Adding a new domain skill

New domains **incubate in `drafts/` at the repository root**, outside the `craftsman/` plugin
directory — so they are neither loaded by the plugin nor shipped in the installed payload, and
don't affect routing. A draft graduates into `plugins/craftsman/skills/` (and starts actually triggering) only
once it has a **full reference set with concrete, adversarially-reviewed guidance**, not stubs.

The reasoning: a skill that auto-triggers on high-risk work (auth, migrations, supply-chain) while
routing to an empty reference file projects authority it doesn't have. **Empty authority is worse
than no skill.** If you're proposing a new domain, expect the bar to be "this is as complete as the
other ten domains," not "this is a placeholder to iterate on live."

## Findings language

If your contribution touches how a skill phrases its findings, keep the standard: **consequence
before jargon.** The target reader is someone who built a real app with Claude Code, Lovable,
Replit, Bolt, v0, or Codex without an engineering background, and needs to know what breaks and
for whom before they need the technical category name.

## CI checks

`scripts/check-invariants.mjs` (run via `.github/workflows/ci.yml` on every push/PR) mechanically
enforces the invariants above: JSON manifests parse, every reference file is cross-linked from its
`SKILL.md` and vice versa, the audit-checklist heading is present and exact, descriptions stay
under the character limit, and no tracked doc leaks a local absolute path. Run it locally before
opening a PR:

```bash
node scripts/check-invariants.mjs
```

## Vendored third-party rules

`plugins/craftsman/skills/craft-ux/references/web-interface-guidelines.md` is the Vercel Web Interface
Guidelines rule list (MIT), vendored at publish time and pinned to an upstream commit SHA. Skills
must **never** fetch instructions from a mutable external branch at review time: the audit runs with
write access to the user's codebase, so a third-party repo that can change its own `main` would be
an instruction channel into that codebase. Vendoring puts a human in front of every rule change.

Refresh it as a release step, not from CI — then read the diff before committing, because a new rule
is a new agent instruction:

```bash
node scripts/refresh-web-interface-guidelines.mjs
```

`--check` reports drift without writing. The script strips upstream's command frontmatter,
`$ARGUMENTS` scaffolding, and output-format section; only the rule list is kept, as data.

## Reporting feedback without opening a PR

See `.github/ISSUE_TEMPLATE/skill-feedback.md` for the lightweight feedback format (skill,
reference, type, evidence, suggested change), or start a discussion if it's not yet a specific,
evidence-backed finding.

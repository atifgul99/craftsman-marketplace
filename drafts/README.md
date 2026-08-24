# Drafts: incubator for future domains

This directory is where a **new** domain skill incubates before it goes live. It sits at the
**repository root, outside the `craftsman/` plugin directory entirely**, so it is neither loaded by
the plugin nor shipped as part of the installed payload.

All ten active domains (`craft-ux`, `craft-frontend`, `craft-backend`, `craft-db`,
`craft-security`, `craft-infra`, `craft-observability`, `craft-testing`, `craft-lint`, and
`craft-ai`, the most recent) have been filled, reviewed, and **graduated into `craftsman/skills/`**.

**Drafts is currently empty on purpose, not abandoned.** Every domain proposed so far has cleared
the bar below and graduated. This folder stays in the repo as the on-ramp for the next one: propose
a new domain here first, and it only reaches `skills/` (and starts triggering) once it clears the
same bar the other ten did.

## Why drafts stay out of the active set

A skill that auto-triggers on high-risk work (auth, authorization, migrations, side-effects, config,
supply-chain) while its routed references are empty projects a standard it doesn't actually enforce.
The agent silently falls back to generic model knowledge while *appearing* governed by the plugin.
**Empty authority is worse than no skill.** So a domain incubates here until its references are real.

## Graduating a draft into the active set

1. Fill its `references/*.md` with concrete, opinionated guidance for the advertised areas.
2. Sanity-check the trigger description still matches the (now real) content.
3. Get it reviewed (every active domain was built with adversarial verify + an external sign-off pass).
4. `git mv drafts/<skill-name> craftsman/skills/<skill-name>`.
5. Update `README.md` (the structure + active list) and the plugin/marketplace descriptions.
6. Wire into craft-audit (discovery applicability row, domain code, load list, HEADING_RE) and
   `scripts/check-invariants.mjs` (`DOMAIN_CODES` + `SKILL_DOMAIN_CODES`).

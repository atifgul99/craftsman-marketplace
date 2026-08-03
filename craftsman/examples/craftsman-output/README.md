# Worked example — what a `craft-audit` run produces

> **This is an illustrative reference, not a real audit and not live state.** Every file under
> `.craftsman/` here is hand-authored to show how a finished audit *fits together* — the citations,
> commit SHAs, and findings are invented for a fictional app. Nothing here was produced by running the
> skill against a real project; don't trust the SHAs or treat it as a template to copy verbatim.

The `craft-audit` skill's output normally lives in a **gitignored `.craftsman/` folder inside the
audited project**, so it never ships with the plugin. That makes it hard to see what a *whole* audit
looks like — the templates in `references/workspace.md` show each file alone, never the coherent set.
This folder is that missing whole: one end-to-end snapshot you can read top to bottom.

## The fictional project being "audited"

**Invoicely** — a vibe-coded SaaS invoicing app (Next.js App Router + Supabase Postgres, deployed on
Vercel), built with Claude in a weekend. It demos well; it is nowhere near production-grade. A single
full-stack app, so there's exactly one scope: `root`.

## How to read it (the audit loop, on disk)

1. `.craftsman/README.md` — the orientation file the skill drops for the user.
2. `.craftsman/discovery.md` — what the project is, with citations + a maturity read (here: pre-Tier-1).
3. `.craftsman/applicability.md` — which of the 10 domains apply, and why (9 of 10; craft-ai N-A).
4. `.craftsman/audits/root/<domain>/plan.md` + `findings.md` — per-surface plan (from the domain
   skill's audit checklist) and the findings it produced, in the canonical emission format.
5. `.craftsman/master-tracker.md` — the climb sequence, the derived readiness grades, the cross-domain
   rollup, and the delta. **Start a real reading here** — it's the front page.

This snapshot shows a **completed Tier-1 teaching pass**: all applicable domains audited
(9 of 10; craft-ai N-A — no LLM surface) for scope `root`: security, db, backend, frontend, infra,
observability, testing, lint, ux. Plans mix completed checklist steps with deliberate deferrals
(same pattern as the security plan). Findings use path-bound IDs (`root-<DOMAINCODE>-NNN`),
plain-language first, and stable fingerprints.

A re-run of this same project would not rewrite these files — it would diff against them
(`references/rerun.md`): mark fixed findings `fixed`, catch regressions, and lead with a delta report.

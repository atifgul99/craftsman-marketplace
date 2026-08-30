# Worked example: what a `craft-audit` run produces

If you have not run `craft-audit` yet, this is what you get when you do: a folder of plain-language
findings about your app, organized so you can see what to fix first and check off each one as it's
actually fixed, not just claimed fixed. The example here is a fictional app, invented so you can see
the real shape of the output before you commit to running an audit on your own project.

> **This is an illustrative reference, not a real audit and not live state.** Every file under
> `.craftsman/` here is hand-authored to show how a finished audit *fits together*: the citations,
> commit SHAs, and findings are invented for a fictional app. Nothing here was produced by running the
> skill against a real project. Don't trust the SHAs or treat it as a template to copy verbatim.

The `craft-audit` skill's output normally lives in a **gitignored `.craftsman/` folder inside the
audited project**, so it never ships with the plugin. That makes it hard to see what a *whole* audit
looks like: the templates in `references/workspace.md` show each file alone, never the coherent set.
This folder is that missing whole, one end-to-end snapshot you can read top to bottom.

## The fictional project being "audited"

**Invoicely**, a vibe-coded SaaS invoicing app (Next.js App Router + Supabase Postgres, deployed on
Vercel), built with Claude in a weekend. It demos well. It is nowhere near production-grade. It is a
single full-stack app, so there's exactly one scope: `root`.

## How to read it (the audit loop, on disk)

1. `.craftsman/README.md`: the orientation file the skill drops for the user.
2. `.craftsman/discovery.md`: what the project is, with citations and a maturity read (here:
   pre-Tier-1).
3. `.craftsman/applicability.md`: which of the 10 domains apply, and why (9 of 10; craft-ai N-A).
4. `.craftsman/audits/root/<domain>/plan.md` plus `findings.md`: per-surface plan (from the domain
   skill's audit checklist) and the findings it produced, in the canonical emission format.
5. `.craftsman/master-tracker.md`: the climb sequence, the derived readiness grades, the cross-domain
   rollup, and the delta. **Start a real reading here.** It's the front page.

This snapshot shows a completed teaching pass: all applicable domains audited (9 of 10; craft-ai
N-A, no LLM surface) for scope `root`, covering security, database, backend, frontend, infra,
observability, testing, lint, and UX. The plans mix completed checklist steps with deliberate
deferrals, the same pattern you'd see in a real run. Each finding uses a stable ID tied to the file
path it came from, is written in plain language before any jargon, and carries a fingerprint so a
later re-run can tell whether it was actually fixed.

A re-run of this same project would not rewrite these files. It would check each finding against the
code as it now stands, mark the ones that are genuinely fixed, catch anything that regressed, and
lead with a summary of what changed.

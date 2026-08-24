# Synthesis protocol — validating findings and building the climb sequence

This is step 7 of the audit loop in `SKILL.md`, in full. Run these four stages in order, before
writing `master-tracker.md`. The ranking *philosophy* (tiers, persona voice, what "first" means)
lives in `prioritization.md`; this file is the mechanical procedure that feeds it.

## a. Collect and validate

Read every `audits/<scope>/<domain>/findings.md` from disk. Prefer the helper script for the
mechanical validation. Run it against the target repo's workspace — the plugin is installed outside
the project, so always address the script through `${CLAUDE_PLUGIN_ROOT}` rather than a relative or
guessed path:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/craft-audit/scripts/validate-findings.mjs" /absolute/path/to/target-repo/.craftsman
```

After reconciliation (stage c) and before writing `master-tracker.md`, run the synthesis gate:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/craft-audit/scripts/validate-synthesis.mjs" /absolute/path/to/target-repo/.craftsman
```

Both exit non-zero and print `file:line` errors on failure.

### By-hand fallback

If the script is unavailable, work the checklist below — it documents exactly what the script
enforces, applied to every file:

1. Every finding heading matches (full line):
   `^## [A-Za-z0-9][A-Za-z0-9-]*-(UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI)-\d{3} · severity [🔴🟡🟢] · status (open|fixed|regressed|wontfix \(.+\)|fixed \(merged into .+\))$`
   (ID shape: `<scopeLabel>-<DOMAINCODE>-NNN`; DOMAINCODE one of UX|FE|BE|DB|SEC|INFRA|OBS|TEST|LINT|AI; NNN exactly 3 digits)
2. For each finding block (from a `## ` heading until the next `## ` or EOF): exactly one of
   each required label in order — `**What breaks (plain language):**` then `**Technical:**`
   then `**Fix:**` then `**Fingerprint:**` then `**Last-checked:**` (multi-line values allowed
   until the next `**` label or heading); Fingerprint value matches
   `` `scope=... · domain=... · class=... · resource=...` ``; Last-checked value is non-empty
   and matches `\d{4}-\d{2}-\d{2} · ([0-9a-f]{4,40}|none \(no git\))`; optional labels, in
   order, may follow: `**Confidence:**` then `**Fix-attempt:**` (both after Last-checked)
3. No `###` finding headings anywhere in the file
4. No body bullets `- **Severity:**` or `- **Status:**`
5. Empty findings file (header only, zero findings) is valid if it has the file header stamp
   and no malformed headings
6. **Path binding:** for `audits/<scope>/<domain>/findings.md`, every finding's Fingerprint
   `scope=` equals that `<scope>` path, Fingerprint `domain=` equals that `<domain>` name, and
   the heading uses `scopeLabel = scope.replaceAll('/', '-')` plus the DOMAINCODE for that
   domain (see domain-code table in `workspace.md`). Shape-valid findings in the wrong file
   are blockers — do not re-home during synthesis; re-prompt the domain pass.

A file that fails any check is a **blocker** — do **not** synthesize from it and do **not** invent a
normalizer that accepts broken variants. Re-run that domain pass (prefer re-prompting the domain
subagent with the failed file plus the canonical template) or fix the file before continuing.

### Remediation closure check

Before accepting any `open → fixed` transition that has a Fix-attempt or changed code since the
finding's last check, read that domain's `remediation-reviews.md`. Require a matching `cleared`
review record with diff provenance and the original invariant; a missing, `pending`, or
`follow-up-found` record blocks that transition rather than weakening the finding.

## b. Flatten

Build a single pooled list of all findings. For small audits (≤ 3 domain/scope pairs) do this
inline. For large audits, delegate to a synthesis agent with the full findings list pasted as input
— it flattens, deduplicates, and returns the ranked list; you write the tracker from that output.

## c. Deduplicate and reconcile

Apply steps 2–2c of `prioritization.md` — dedup/merge, cross-domain rollup, and cross-scope
same-resource merge. Write `dedup-map.md` before the tracker: exact-key groups, semantic candidates,
every reconciliation decision, and raw versus distinct eligible counts. A zero semantic-rollup
outcome requires an explicit review record.

## d. Rank and write

Sort 🔴 Tier 1 → 🟡 Tier 1 → 🔴 Tier 2 → 🟡 Tier 2 → 🟢, then write the master tracker. Keep
`unverified-from-repo` items out of ordinary distinct-defect totals and the climb sequence; surface
them under **Human verification required** instead.

After presenting the climb sequence to the user, tell them the fix path: to start fixing, invoke
`craft-fix` (or say "fix the findings" / "fix `<ID>`") — it works through the climb sequence with
their approval, and the next re-run of `craft-audit` verifies what actually got fixed.

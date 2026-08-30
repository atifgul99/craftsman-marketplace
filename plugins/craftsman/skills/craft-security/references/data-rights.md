# Data Rights

One GDPR/CCPA deletion request you can't fulfill is a real incident — a support ticket that turns into a compliance escalation, not a bug report. The engineering discipline: **know where PII lives, make deletion actually cascade, and have an export path before someone asks for one.**

> **Scope split.** This file owns the *engineering-observable* slice of data rights: whether a deletion path exists and cascades, whether an export path exists, and whether PII is inventoried and leak-free. **This is not legal advice** — it does not interpret GDPR, CCPA, or any other regulation, and it does not tell you what the law requires. Loop in a lawyer for that. What it does tell you: an engineer can verify whether "delete my data" actually deletes the data, and that's worth checking regardless of which law is in play. Cascade *mechanics* (FK `ON DELETE CASCADE` vs. app-level cleanup) belong to **`craft-db`** → `integrity.md`; PII leaking into logs is the same failure mode covered in **`craft-observability`** → `logging.md`, cross-referenced here from the data-rights angle.

---

## Contents

- [Deletion path](#deletion-path)
- [Backups are a known limitation](#backups-are-a-known-limitation)
- [Third-party processors need their own deletion](#third-party-processors-need-their-own-deletion)
- [Export path](#export-path)
- [PII surface inventory](#pii-surface-inventory)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Deletion path

- **A deletion path must exist and actually run.** "We can delete a user" means someone (support, an admin panel, a self-serve setting) can trigger it and it completes — not that a developer could write the query if asked.
- **It must cascade to every table that holds that user's data**, not just the primary `users` row. Orphaned PII in related tables (`orders`, `comments`, `sessions`, `audit_log`) after a user row is deleted is the classic gap — the user "looks" deleted but their data is still there under a dangling foreign key. Whether that cascade is enforced by `ON DELETE CASCADE` at the schema level or by explicit app-level cleanup code is a `craft-db` → `integrity.md` decision; this skill just checks that one of the two actually happens.
- **Verify it, don't assume it.** Run the deletion path against a test user, then query every table that references their id. If anything comes back, the cascade is incomplete.

---

## Backups are a known limitation

- **Deleted data persists in backups for their retention window** — that's a property of how backups work, not a bug. Document the retention window (e.g. "backups roll off after 30 days") so it's a known, stated limitation rather than a surprise when someone asks "is it *really* gone."
- This skill does not solve backup scrubbing (selectively deleting one user's data from historical backups is a hard, often-skipped problem). The fix here is honesty: write down the retention window and don't claim faster deletion than backups actually provide.

---

## Third-party processors need their own deletion

- **Deleting your own DB rows doesn't delete the user anywhere else.** Every third party that received that user's PII holds an independent copy: Stripe (billing/customer records), analytics tools (Segment, Amplitude, PostHog), email providers (Mailchimp, SendGrid, Postmark), support tools (Intercom, Zendesk), error trackers (Sentry — see below).
- **Each processor needs its own deletion call**, made as part of the same deletion flow — not a follow-up someone remembers to do manually six months later. Most vendors expose a deletion/erasure API or an admin-console action; know which processors hold PII and which of them you've actually wired a deletion call for.
- **An inventory of "which vendors hold this user's PII" is a prerequisite** — you can't delete from a processor you forgot exists. This is the same inventory work as the PII surface inventory below, applied outward instead of to your own DB.

---

## Export path

- **An export path must exist, even at MVP stage a manual one is enough.** It doesn't need self-serve UI on day one — a documented runbook ("support runs this script / query, hands the customer a JSON/CSV export") satisfies the engineering bar. What fails the bar is no path at all: an engineer has to improvise a query under pressure when the request lands.
- **The export should cover the same surface as the deletion path** — if a table is in scope for deletion, the data in it is in scope for export too. Keep the two lists in sync.

---

## PII surface inventory

- **Know which tables/columns hold PII**: name, email, phone, physical address, IP address, government ID, payment details, precise location, free-text fields that can incidentally contain PII (support tickets, chat logs). A short inventory (table, column, PII category) is enough — it doesn't need to be a formal data-classification program.
- **Know where PII flows *out* of the primary DB**, because that's where it escapes the deletion/export path entirely:
  - **Application logs** — logging a full user object or request body puts PII in log storage nobody scoped for it. This is the same failure mode `craft-observability` → `logging.md` covers from the logging-hygiene angle; flagging it here is the data-rights consequence of the same mistake.
  - **Analytics events** — tracking calls that pass raw email/name/IP as event properties ship PII to a third party by default, often without anyone deciding that on purpose.
  - **LLM/model API calls** — sending user PII in a prompt to a third-party model API is a PII export to that vendor; know whether it happens and whether the vendor's data-use terms are acceptable.
  - **Error trackers (Sentry, etc.)** — request context and local variables are captured by default and routinely include PII. This is the classic accidental leak: nobody put PII in Sentry on purpose, it arrived attached to a captured request or exception.
- **An inventory that's never been written down effectively doesn't exist** — when the deletion/export path is built, it can only be as complete as this list.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| No deletion path exists (no code, no runbook, no admin action) | Build a minimal deletion path — even an admin script counts as a start |
| Deletion path removes the user row but leaves data in related tables | Cascade at the schema (FK `ON DELETE CASCADE`) or in app code — see `craft-db` → `integrity.md` |
| Deletion path never tested against real related tables | Run it against a test user, verify no orphaned rows remain |
| No mention of backup retention as a known limitation | Document the backup retention window; don't claim instant total erasure |
| No deletion call to third-party processors (Stripe, analytics, email) | Inventory processors holding PII; wire a deletion call per processor into the flow |
| No export path exists, not even a manual runbook | Document/script a support-run export covering the same data as deletion |
| No PII inventory exists (tables/columns never listed) | Write a short table → column → PII-category inventory |
| PII (email, name, IP, etc.) found in log statements | Redact at the logger — see `craft-observability` → `logging.md` |
| Raw PII sent to analytics events, error trackers, or LLM prompts by default | Scrub/hash before sending; confirm the vendor's data-use terms |
| Team treats this file's guidance as legal sign-off for compliance | Get real legal advice — this is engineering verification, not legal interpretation |

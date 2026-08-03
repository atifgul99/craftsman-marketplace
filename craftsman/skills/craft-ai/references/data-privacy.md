# Data Privacy

Every prompt sent to a third-party LLM API is data leaving your infrastructure boundary and
entering someone else's — a different trust relationship than a database query that never leaves
your own servers. The discipline here is knowing exactly what leaves the building, on what terms,
and where it lands afterward (including your own logs).

> **Scope split.** This file owns the LLM-specific data-egress question (what's in the prompt,
> what the provider's terms say, what your logging pipeline retains). The general PII inventory
> and data-subject-rights framework (what counts as PII, deletion/export obligations) is
> `craft-security` → `data-rights.md` — read that first for the taxonomy, then apply it here to
> the LLM-specific egress point.

## Contents

- [Inventory what leaves the building](#inventory-what-leaves-the-building)
- [Provider retention and training flags](#provider-retention-and-training-flags)
- [PII in logged prompts and completions](#pii-in-logged-prompts-and-completions)
- [User consent and disclosure](#user-consent-and-disclosure)
- [Regional and enterprise endpoints](#regional-and-enterprise-endpoints)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Inventory what leaves the building

Before anything else, know what's actually in the prompts your app sends.

- **Trace every call site that builds a prompt** and list what user/customer data flows into it —
  names, emails, free-text support messages, uploaded documents, order history, health or
  financial details if the product touches those domains.
- **Distinguish "necessary for the feature" from "convenient to include."** A support-summarization
  feature needs the ticket text; it may not need the customer's full account history pasted into
  the same prompt just because it was easy to fetch. Smaller prompts are both cheaper and lower
  privacy-exposure.
- **RAG and retrieval pipelines widen the inventory** — if the retrieved documents themselves
  contain PII (support tickets, internal notes, user-generated content), that PII reaches the
  model provider the moment it's retrieved into context, even if the querying user never typed it.
- Use `craft-security` → `data-rights.md` for the general PII taxonomy and classification method;
  apply it specifically to "what's in the prompt" here.

## Provider retention and training flags

Providers differ, and their terms change — check the actual current settings/DPA for the specific
account in use rather than assuming a posture.

- **Check the provider's data-retention terms for the plan/tier actually in use.** Consumer-tier
  and enterprise/business-tier agreements from the same provider commonly carry different
  retention and training defaults — confirm which tier the project's API account is on.
- **Check whether prompts/completions are used for model training by default**, and whether an
  opt-out or zero-retention mode is available and actually enabled — a training opt-out toggle
  that exists but isn't switched on provides no protection.
- **Zero-retention / no-training endpoints, where a provider offers them, are the safer default
  for any prompt containing customer PII** — the cost/latency tradeoff (if any) is usually worth
  it once real customer data is involved.
- **Re-verify this periodically, not just once.** Provider terms and default settings change; a
  posture that was safe at integration time can drift without an obvious signal.

## PII in logged prompts and completions

Observability pipelines default to logging everything, and "everything" for an LLM call includes
the full prompt and the full response — which is exactly where PII ends up persisted somewhere
nobody was thinking about when they wired up logging.

- **Assume your LLM SDK's default logging/tracing behavior captures full request and response
  bodies** unless proven otherwise — many observability integrations for LLM calls are built to
  show you the whole conversation for debugging, which is also the whole conversation for a
  privacy audit.
- **Scrub PII before it lands in logs, APM traces, or third-party observability tools**, the same
  way you'd scrub a password from an error log — a raw prompt containing a customer's email,
  address, or health detail sitting in a log aggregator is a data exposure surface most teams
  don't think to check.
- **If prompt/completion logging is needed for debugging, prefer a redacted or truncated capture**
  by default, with full capture behind an explicit, access-controlled opt-in for active incident
  investigation — not the default state for all traffic.
- **Never log raw prompts/completions by default — full stop.** Redacted or truncated capture is
  the standing state for all traffic, always on. Full, unredacted capture is only ever available
  behind an explicit flag that is access-controlled (not every engineer can flip it) and
  time-boxed (it's turned back off when the incident is closed, not left on "just in case").
- **Reject scrubbing-as-default.** "Log everything but run it through a PII scrubber" sounds safer
  than it is: scrubbers miss things — a name in an unexpected format, a free-text field a regex
  didn't anticipate, a PII shape nobody wrote a rule for. An audit cannot verify a scrubber's
  coverage; scrubber quality is an unbounded, ongoing claim. An audit *can* verify a flag exists,
  is off by default, and is scoped and time-limited when on. Prefer the thing you can check.

## User consent and disclosure

Users interacting with an AI feature — especially one that sends their input to a third-party
provider — generally have a reasonable expectation of knowing that's happening.

- **Disclose when a user's input is processed by an AI system**, particularly a third-party one,
  rather than presenting it as if handled entirely in-house — this is both a trust practice and,
  increasingly, a regulatory expectation in several jurisdictions.
- **Distinguish "AI-assisted" from "fully automated"** in user-facing disclosure where the
  distinction is material (e.g., an automated decision with real consequences vs. an AI-drafted
  suggestion a human reviews) — the level of disclosure and consent expected scales with impact.
- **Don't bury the disclosure in a general privacy policy if the feature is a visible,
  interactive AI surface** (a chatbot, an AI-drafted email) — a short, visible note at the point
  of use is the stronger practice.

## Regional and enterprise endpoints

For products with genuine compliance obligations (HIPAA, GDPR data-residency, SOC 2 commitments
to customers), the provider's standard public API endpoint may not meet the requirement even if
the model behavior is identical.

- **Check whether the provider offers a regional or data-residency-specific endpoint** when a
  compliance obligation requires data to stay in a specific jurisdiction — using the standard
  global endpoint can violate a residency commitment even though nothing about the request looks
  different.
- **Check whether a BAA (Business Associate Agreement) or equivalent is available and signed**
  before sending health-related PII to a provider in a HIPAA-context product — sending PHI to a
  provider without a BAA in place is a compliance gap regardless of the provider's general
  security posture.
- **Enterprise-tier agreements are often the lever that unlocks the zero-retention and
  regional-endpoint options** described above — for a product with real compliance obligations,
  the account tier itself is a design decision, not just a pricing one.

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Prompt includes customer PII not needed for the feature | Trim the prompt to what the feature actually needs |
| RAG-retrieved documents contain PII with no handling for it | Extend the PII inventory to retrieved content |
| Provider account tier/retention settings never checked | Verify actual DPA/dashboard settings for the tier in use |
| Training opt-out available but not enabled | Enable it; re-verify periodically |
| Full prompts/completions logged to APM/observability with no scrubbing | Scrub PII before logging; redact by default |
| Raw prompt/completion logging always-on, or gated only by a scrubber rather than a flag | Default to redacted/truncated capture; full capture only behind an access-controlled, time-boxed flag |
| No user-facing disclosure that AI (esp. third-party) processes their input | Add a visible disclosure at the point of use |
| PHI sent to a provider with no BAA in place | Establish a BAA or route through a compliant endpoint before sending |
| Data-residency requirement exists but standard global endpoint is used | Use the provider's regional/residency endpoint |

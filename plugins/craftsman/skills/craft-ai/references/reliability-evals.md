# Reliability & Evals

LLM-powered features fail differently than typical backend code: the provider itself goes down or
degrades on a schedule outside your control, the same prompt can produce a different output on two
runs, and a "passing" prompt today can silently regress after a one-line edit tomorrow. The
discipline here is treating a prompt like the code it is — versioned, tested, and defended against
the failure modes specific to a non-deterministic, third-party dependency.

> **Scope split.** This file owns LLM-call-specific reliability (provider outages, retry
> semantics around tool actions, output validation, prompt regression testing). General
> API-integration resilience patterns (circuit breakers, backoff for any third-party call) are
> the same discipline applied more broadly — see `craft-backend` for the general integration
> pattern; apply it here to the LLM-specific call.

## Contents

- [Timeouts and fallbacks](#timeouts-and-fallbacks)
- [Retry semantics and non-idempotent actions](#retry-semantics-and-non-idempotent-actions)
- [A minimal eval harness](#a-minimal-eval-harness)
- [Structured-output validation](#structured-output-validation)
- [Version prompts like code](#version-prompts-like-code)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Timeouts and fallbacks

Provider outages, rate-limit throttling, and slow-degradation incidents are routine occurrences
for every major LLM API, not edge cases — design for them as an expected condition, not an
exception.

- **Every provider call has an explicit timeout.** Without one, a slow or hung provider response
  ties up the calling request (a server thread, a serverless invocation, a queue worker) for as
  long as the provider takes, which can be far longer than users will wait.
- **Have an explicit fallback for when the call fails or times out** — a cached/default response,
  a graceful "try again" message, a degraded non-AI code path — rather than letting the failure
  propagate as an unhandled error or a hung UI. What "graceful" means is feature-specific: a
  chatbot can show a retry prompt; a background enrichment job can skip enrichment and continue.
- **Never let an LLM call block a critical path with no fallback.** If a feature's core function
  depends entirely on an LLM call succeeding with no degraded mode, that's a single point of
  failure inherited from a third party you don't control.

## Retry semantics and non-idempotent actions

Retrying a failed LLM call is often reasonable; retrying blindly when that call already triggered
a side effect (a tool call, a sent email, a charge) is not.

- **Retry with backoff for transient provider errors** (rate limits, 5xx, timeouts) — this is
  standard practice and usually safe when the call itself is a pure text generation with no side
  effect.
- **Never retry a call that already executed a non-idempotent tool action** without confirming
  whether the action actually completed. A model call that both generates text *and* triggers a
  tool (send an email, charge a card, write a record) is not safe to blindly retry on ambiguous
  failure — the first attempt may have succeeded downstream even though the response to your code
  errored or timed out.
- **Design tool actions to be idempotent where possible** (idempotency keys on writes, checking
  current state before acting) specifically so that retry-after-ambiguous-failure is safe by
  construction, rather than relying on retry logic to guess correctly.

## A minimal eval harness

"It looked right when I tried it" is not a regression test. A prompt change that isn't checked
against a fixed set of cases can silently break behavior that used to work, with no signal until
a user notices.

**Applicability (severity gate):**
- **Non-trivial prompt/agent behavior shipping to production** (multi-step agents, tool-calling,
  RAG that drives product decisions, customer-facing chat with consequential actions) → a golden-case
  harness is **required**. Missing = high-severity gap (🔴-class when the behavior is live).
- **Thin single-route MVP wrapper** (one `POST /api/complete` that streams a completion, no tools,
  no shipped prompt iteration process yet) → flag missing eval as **🟡 opportunity / recommend**,
  not automatic 🔴. Still recommend versioning the prompt string and adding cases before the surface
  grows.

- **A dozen well-chosen golden cases beats no testing and often beats an elaborate eval framework
  nobody maintains.** Pick representative inputs (including known edge cases and past failure
  modes) with an expected-output shape or property, and check every prompt change against them
  before shipping.
- **Prefer checking properties over exact string match** for open-ended generation — "does the
  response contain X," "is the output valid JSON matching the schema," "is the tone appropriate"
  — exact-match assertions are usually too brittle for free-text output but appropriate for
  structured/classification tasks.
- **Run the eval set before merging any prompt change**, the same way tests gate a code change —
  a prompt edited without checking it against known cases is an unreviewed behavior change that
  happens to be expressed in English instead of code.
- **Grow the eval set from real failures.** Every production incident traced to a bad model
  response is a candidate new golden case — this is how the eval set becomes actually
  representative over time instead of a fixed set written once at launch.

## Structured-output validation

When a model's output is consumed as data (JSON parsed into a typed object, a value inserted into
a database, a decision branching application logic) rather than displayed as text, the model's
tendency to occasionally produce malformed or off-schema output becomes a correctness bug, not
just a quality issue.

- **Schema-validate every structured LLM output before consuming it** — don't `JSON.parse` a
  completion and trust the shape; validate against the expected schema (Zod, Pydantic, JSON
  Schema, or equivalent) the same way you'd validate any external input.
- **Have an explicit repair-or-reject path for a validation failure**: either a bounded retry
  asking the model to correct the specific validation error, or a clean rejection with a fallback
  — never let malformed output flow further downstream because rejecting it was the deferred case.
- **Prefer provider-native structured-output/JSON-mode features where available** — they reduce
  (but don't eliminate) the malformed-output rate versus free-text generation you parse yourself.

## Version prompts like code

A prompt is a specification for behavior, and behaves like one: it should be reviewable, revert-
able, and diffable.

- **Store prompts in version control**, not as a string mutated live in a database or admin panel
  with no history — a prompt change that broke behavior should be as easy to `git blame` and
  revert as a code change.
- **Review prompt changes with the same rigor as a code change** — a prompt PR should go through
  the eval harness above the same way a code PR goes through tests, before merge.
- **Tag or version prompts that ship to production** if the system supports multiple concurrent
  prompt versions (e.g., an A/B test or gradual rollout) — so a regression can be attributed to
  the specific version that shipped it.
- **Gate on regressions, not on an absolute pass rate.** No golden case that passed before may
  fail now — a new failure blocks the merge, or the merge carries an explicit, written waiver
  explaining why it's acceptable this time. That's the bar, and it's the whole bar.
- **Reject requiring 100% pass on the full golden set.** One genuinely ambiguous case — a
  legitimate judgment call with no single right answer — will permanently block unrelated,
  unrelated-risk work forever, and the lesson a builder takes from that isn't "write a better
  case," it's "delete the eval." A gate that teaches people to route around it is worse than no
  gate.
- **Reject a bare pass-rate threshold ("95% is fine") too.** A threshold invites quiet erosion —
  each new failure nudges the bar down by a fraction of a percent, nobody notices any single
  regression, and the eval set slowly stops meaning anything. Regression-only gating catches every
  individual slip instead of averaging it away.
- **The reason this is the right gate: it's one the team will actually keep.** Same principle as
  the flake policy in `craft-testing` — a gate people route around by disabling it is worse than a
  looser gate people respect. Regression-only is strict where it matters (nothing that worked is
  allowed to quietly break) and forgiving where it should be (a known-ambiguous case doesn't hold
  the whole team hostage).

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| LLM call with no timeout | Add an explicit timeout |
| LLM call with no fallback on failure/timeout | Add a graceful degraded path |
| Feature's critical path has no non-AI fallback at all | Identify and build a degraded mode |
| Blind retry around a call that also triggers a tool/side effect | Check completion state before retrying; make the action idempotent |
| No eval/golden-case set for non-trivial shipped prompt/agent | Build a minimal golden-case set from representative + known-failure inputs (🔴-class when live) |
| No eval for a thin single-route MVP wrapper | 🟡 recommend a harness before the surface grows; not automatic 🔴 |
| Prompt changed and shipped with no check against existing cases | Run the eval set before merge |
| LLM JSON output parsed and used without schema validation | Validate against schema; repair-or-reject on failure |
| Prompt lives in a live-edited DB/admin field with no history | Move to version control; review changes like code |
| Merge gate requires 100% pass or a bare pass-rate threshold, not regression-only | Gate on regressions: no previously-passing case may fail without a written waiver |

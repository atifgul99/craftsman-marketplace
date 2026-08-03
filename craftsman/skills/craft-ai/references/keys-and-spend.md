# Keys & Spend

An LLM API key is a credential that spends real money per token, and an LLM-calling code path is
a new category of cost surface most engineers haven't had to defend before: unlike a typical API
call, cost scales with *conversation length*, *retry behavior*, and *how many tokens the model
decides to generate* — none of which are fully under your control unless you bound them.

> **Scope split.** This file owns the LLM-specific spend surface: key placement, per-route caps,
> loop bounds, and model-tier cost levers. Provider billing alerts/hard caps *as infrastructure
> configuration* (the dashboard toggle, the webhook) are `craft-infra` → `config.md` — this file
> owns the *application-level* design that keeps a bug from needing that alert in the first place.
> Secret *storage* mechanics (env schema, vault, rotation) are `craft-security` → `secrets.md`.

## Contents

- [Keys never reach the client](#keys-never-reach-the-client)
- [Per-route limits](#per-route-limits)
- [Loops and agents as spend bombs](#loops-and-agents-as-spend-bombs)
- [Streaming and disconnects](#streaming-and-disconnects)
- [Billing alerts and hard caps](#billing-alerts-and-hard-caps)
- [Model tiering](#model-tiering)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Keys never reach the client

The single most common LLM-specific leak: a provider API key ends up somewhere a browser or a
device can read it.

- **`NEXT_PUBLIC_*` (or any framework's client-exposed env prefix) is the classic leak.** An
  OpenAI/Anthropic/etc. key behind a client-exposed env var ships in the JS bundle, readable by
  anyone who opens dev tools — this is a full account compromise, not a minor exposure.
  Grep for the provider's key pattern (`sk-`, `sk-ant-`, etc.) across the client bundle output,
  not just source, before calling a repo clean.
- **Mobile apps are the same failure in a different shape.** A key embedded in a compiled mobile
  binary is extractable with standard reverse-engineering tools; "it's compiled" is not a control.
- **The fix is always the same shape: proxy through your own backend.** The client calls your
  server, your server holds the key and calls the provider. No exceptions for "it's just a demo"
  — demos get scraped by bots hunting for exposed keys within hours of being public.
- **Rotate immediately if a key has ever been client-exposed**, even briefly, even if you "fixed
  it fast" — assume it was scraped the moment it was reachable.

## Per-route limits

Every route or job that calls an LLM should have three bounds, because a model call has three
independent cost dimensions that a normal API call doesn't: request rate, tokens per request, and
wall-clock time.

- **Rate limit the route** the same way you would any other endpoint (see `craft-backend` for the
  general rate-limiting mechanism) — but tune the limit for LLM cost, not just abuse prevention;
  a normally-abuse-safe rate can still be a large bill at LLM per-token pricing. **Ownership
  (emit once):** AI owns the LLM spend/cost finding (rate + `max_tokens` + loop bounds); BE owns
  the middleware mechanism if missing generically; SEC owns login abuse policy; INFRA owns
  platform/edge capacity — do not re-emit the same gap under all four.
- **Cap `max_tokens`/`max_output_tokens` on every call.** An uncapped completion request lets a
  single call run to the model's maximum context, and a looping or malformed client can trigger
  that repeatedly. Set a cap sized to the feature's actual need, not the model's ceiling.
  **Size the cap to what the feature actually produces, never a blanket default and never the
  model's maximum.** A one-paragraph summary never needs 4k output tokens; a code-generation
  feature might need most of them. There is no universal number here — the number comes from the
  feature. If you can't state what the feature needs, that's the finding: an uncapped or
  copy-pasted cap means nobody thought about it.
- **Timeout every provider call.** A hung request against a stalled or slow provider ties up a
  server resource (a request thread, a serverless invocation) for the duration — cap it and fail
  fast with a fallback (see `references/reliability-evals.md`).

## Loops and agents as spend bombs

Any code that lets a model call itself, call another model, or repeatedly re-prompt without a
hard ceiling is a mechanism for turning one triggering event into an unbounded number of billed
calls.

- **Every agent loop needs a hard iteration cap**, independent of whatever "the model decided it
  was done" logic exists — a model that gets stuck in a retry-refine cycle (or is steered into one
  by injected content, see `references/prompt-injection.md`) will keep calling until something
  stops it.
- **Every recursive or chained LLM call (agent calling sub-agents, multi-step pipelines) needs a
  total-cost or total-call budget for the whole chain**, not just a per-call cap — ten calls at
  the per-call cap is still ten times the cost of one.
- **A retry-on-failure wrapper around an LLM call needs its own cap**, separate from the
  application's general retry policy — an LLM call retried indefinitely against a provider that's
  consistently erroring is a slow-motion version of the same spend bomb.

## Streaming and disconnects

Streaming responses are cheaper to *perceive* as fast but not cheaper to *generate* — the
provider still bills for tokens generated even if nobody's listening.

- **Abort the provider-side stream when the client disconnects.** If a user closes the tab or the
  connection drops mid-stream, the generation should stop — most SDKs expose an abort signal or
  connection-close hook; wire it so a disconconnected client doesn't leave a full-length
  generation running (and billing) in the background.
- **Don't rely on the client to signal completion.** A client-side timeout or navigation away
  should be treated as a server-side signal to cancel, not just a UI-side "give up waiting."

## Billing alerts and hard caps

- **Set a billing alert with the provider at a threshold well below what would actually hurt**,
  so a bug is caught by a Slack/email ping long before it's caught by a shocking invoice. The
  mechanics of wiring that alert (dashboard config, webhook) are `craft-infra` → `config.md`.
- **Prefer a hard spend cap over an alert-only posture where the provider supports it** — an alert
  tells you after the fact; a cap stops the bleeding. Understand the operational tradeoff (a hard
  cap can also cut off legitimate traffic) before choosing.
- **Default recommendation for an MVP: a hard monthly cap, sized at roughly 3–5x expected monthly
  spend, with an alert at 50%.** The alert gives a human time to react before the cap bites; the
  cap itself is the backstop for when nobody reacts in time. Revisit this — move to a tiered
  degrade-not-cutoff posture — only once the LLM feature is revenue-critical enough that an outage
  at the cap costs more than a runaway bill would. Most MVPs aren't there yet, and defaulting to
  the tiered approach before that point is solving a problem the project doesn't have.
- **Why the hard cap wins by default:** a surprise outage at the cap is embarrassing — a support
  ticket, a bad tweet, an apology. A surprise four-figure bill from an unbounded loop or a scraped
  key can kill the company outright. Pick the failure mode you can survive.

## Model tiering

Not every call needs the flagship model. Task-appropriate model selection is a direct cost lever
and often improves latency too.

- **Classify calls by what they actually need**: a classification/routing/extraction task rarely
  needs the most capable (and most expensive) model in a provider's lineup; a complex
  reasoning or long-context synthesis task might.
- **Route cheap, high-volume tasks to a cheaper model tier**, reserving the expensive tier for
  the calls where quality genuinely depends on it — this is usually the single biggest cost lever
  available before touching architecture.
- **Re-evaluate tiering when a provider ships a new model generation** — the cost/quality
  tradeoff shifts over time; a tiering decision made a year ago may no longer be the right one.

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Provider API key behind a client-exposed env prefix (e.g. `NEXT_PUBLIC_*`) | Move the call server-side; proxy through the backend; rotate the key |
| Provider API key embedded in a mobile app binary | Proxy through backend; rotate the key |
| LLM-calling route with no rate limit | Add a rate limit tuned for LLM cost, not just abuse |
| LLM call with no `max_tokens`/output cap | Cap output size to the feature's actual need |
| LLM call with no timeout | Add a timeout + fallback |
| Agent/loop with no hard iteration cap | Add a ceiling independent of model "done" signaling |
| Chained/multi-step LLM pipeline with no total-budget cap | Cap total calls/cost for the whole chain, not just per-call |
| Retry wrapper around LLM calls with no retry cap | Bound retries separately from general app retry policy |
| Streaming response that keeps generating after client disconnect | Wire abort-on-disconnect |
| No provider billing alert configured | Set an alert well below a painful threshold (`craft-infra` → `config.md`) |
| No hard spend cap on the provider account | Set a hard cap at ~3-5x expected monthly spend, alert at 50% |
| Flagship model used for a cheap/high-volume classification-style task | Route to a cheaper tier |

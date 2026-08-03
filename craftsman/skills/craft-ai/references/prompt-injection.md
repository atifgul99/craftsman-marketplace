# Prompt Injection

An LLM cannot reliably distinguish "instructions from the developer" from "text that happens to
look like instructions" once both sit in the same context window. Anything that reaches the
model that isn't your own system prompt — user input, a retrieved document, a scraped web page,
a tool's return value — is a potential vector for hijacking what the model does next. This is
mitigated, never solved: treat every mitigation below as raising the cost of an attack, not
closing the hole.

> **Scope split.** This file owns the LLM-specific injection surface (prompt construction, tool
> boundaries, output handling around a model call). Generic input validation at an API boundary
> is `craft-security` → `input-output.md`; XSS from rendering *any* untrusted string (not just
> LLM output) is the same file. Secrets *storage* is `craft-security` → `secrets.md`.

## Contents

- [Direct injection](#direct-injection)
- [Indirect injection](#indirect-injection)
- [Tool-use and function-calling boundaries](#tool-use-and-function-calling-boundaries)
- [Output handling](#output-handling)
- [Mitigations, honestly framed](#mitigations-honestly-framed)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Direct injection

The simplest case: a user types "ignore your previous instructions and..." into a chat box that
feeds straight into the prompt. Any system that lets a user's raw text sit next to the system
prompt without structural separation is exposed to this by default.

- Know exactly which parts of the assembled prompt are attacker-controlled (the end user) versus
  developer-controlled (your system prompt, your own retrieved context you trust).
- A user who can fully control the conversation is *expected* to try this — the question is
  whether a successful injection can do anything beyond change the chat's tone (see tool-use
  boundaries below for where it gets dangerous).

## Indirect injection

The sharper risk: content the model reads that the *end user* didn't type, but that still
reaches the context window — a fetched URL, a RAG-retrieved document, an uploaded file, an email
body, a GitHub issue, a customer support ticket. An attacker who can plant text in any of those
sources can inject instructions that the user never saw and never typed.

- Inventory every source that gets pulled into a prompt without a human reading it first:
  web-fetch tools, RAG document stores, email/ticket ingestion, third-party webhook payloads.
- Treat retrieved content as hostile by default — it sits in the same trust tier as anonymous
  user input, not the same tier as your own system prompt, even though a developer never typed it.
- The higher the automation (no human reviews the retrieved content before the model acts on it,
  and the model can call tools), the higher the blast radius of a successful indirect injection.

## Tool-use and function-calling boundaries

An LLM that can only produce text has a bounded worst case: a bad response. An LLM that can call
tools — send an email, hit an internal API, run a shell command, move money, modify a database —
turns a successful injection into an action taken *on the caller's behalf*. This is remote code
execution's little sibling: the "attacker" doesn't get a shell, they get to steer whatever the
tool layer will do.

- Enumerate every tool the model can call and what each one is capable of — read-only tools
  (search, lookup) carry far less risk than mutating or irreversible ones (send, delete, purchase,
  execute).
- An injected instruction that reaches a tool-calling model can attempt to invoke any tool in its
  allow-list — the defense is restricting *which* tools are reachable in a given context, not
  hoping the model refuses.
- Consequential actions (irreversible, financial, externally visible, or affecting another party)
  should require an explicit confirmation step — either a human-in-the-loop approval or a
  deterministic policy check outside the model's own judgment — before they execute.
- **Default tool-approval stance for an MVP: auto-allow read-only or idempotent tools; everything
  mutating requires confirmation by default.** A `search`, `lookup`, or `get` tool can run
  unattended — worst case it returns bad context, not a bad outcome. A `write`, `send`, `delete`,
  or `charge` tool does not get a default-allow, full stop. This isn't a risk tier to reason about
  per-tool; it's a binary switch, checked the same way every time.
- **Consequential actions never get a model-judged exception, at MVP stage.** Irreversible,
  financial, externally visible, or another-party-affecting actions always require
  human-in-the-loop approval or a deterministic policy check outside the model — no "unless the
  model is confident," no risk-scored auto-approval. A vibe-coded MVP has no risk-tier matrix
  worth maintaining, and a matrix that isn't maintained is worse than no matrix — it's a false
  sense of coverage. Deny-by-default here is the same posture `craft-security` → `authz.md` takes
  on resource access: prove entitlement, don't assume it.

## Output handling

The model's output is untrusted the same way its input is — it's model-generated text, and
nothing guarantees it's well-formed or safe for the context you're about to put it in.

- **Rendered as HTML/markdown**: an LLM response inserted into a page via `dangerouslySetInnerHTML`
  (or equivalent) without sanitization is a stored/reflected XSS vector if the model can be
  steered into emitting a `<script>` tag or an `onerror` payload — via direct or indirect
  injection. Sanitize or encode LLM output the same way you would any other untrusted string.
- **Used to build a query or command**: LLM output interpolated into a SQL query, a shell command,
  or another downstream API call is injection risk one level removed — parameterize or validate
  it exactly as you would user input, never string-concatenate it in.
- **Consumed by another LLM call** (chained agents, multi-step pipelines): output from one model
  call becomes input to the next, so an injection that succeeds at step one can propagate — treat
  inter-step handoffs as a trust boundary too.

## Mitigations, honestly framed

None of these eliminate the risk — they reduce blast radius and raise attacker cost.

- **Structural separation.** Keep developer instructions and untrusted content in clearly
  delimited regions (e.g., a dedicated "user data" block, XML-ish tags around retrieved content,
  or provider-specific system/user role separation) so the model has the best available signal
  about which text is instruction and which is data. This helps; it does not guarantee compliance.
- **Allow-listed tools, scoped per context.** Don't expose every tool to every conversation —
  scope what's callable to what's actually needed for the task at hand.
- **Human confirmation for consequential actions.** The single most reliable backstop against a
  successful injection turning into real-world harm.
- **Least privilege on tool credentials.** A tool that emails on the user's behalf should hold
  only the scope needed to send email as that user — not a service account with broader reach.
- **Monitoring and anomaly detection.** Log tool invocations and flag unusual patterns (a support
  bot suddenly trying to call a refund tool) — you won't catch every injection at design time.

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| User input concatenated directly into system prompt with no delimiter | Structurally separate instructions from user/retrieved content |
| RAG/retrieved/scraped content fed to the model with no trust marking | Treat as untrusted; delimit and treat as data, not instruction |
| Tool-calling model with no allow-list (any tool reachable in any context) | Scope tools to what the task actually needs |
| Consequential tool action (send, delete, pay, execute) fires with no confirmation | Add human-in-the-loop or deterministic policy check |
| Mutating tool auto-allowed by default, or a consequential action gated only by model judgment | Auto-allow only read-only/idempotent tools; require confirmation for mutating and consequential actions, no exceptions |
| LLM output rendered via `dangerouslySetInnerHTML` / unescaped markdown render | Sanitize/encode before render |
| LLM output interpolated into SQL/shell/API call unparameterized | Parameterize or validate like any other untrusted input |
| Multi-step agent chain with no trust boundary between steps | Treat inter-step output as untrusted at each hop |
| Tool credentials scoped broader than the action needs | Apply least privilege to the credential, not just the prompt |

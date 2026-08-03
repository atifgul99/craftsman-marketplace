# Forms

How to wire a form so it is type-safe, schema-driven, accessible to a screen reader, and honest
about request state — the parts that survive a happy-path demo and break when a real user blurs a
field, double-clicks submit, or hits a server that rejects what the client accepted.

> Scope split: this file owns the *application layer* of a form — the schema, the form hook, error
> wiring, and the submit/mutation lifecycle. The **visual/UX/a11y of the fields themselves** (labels
> above inputs, `autocomplete`, `inputmode`, placeholders vs labels, touch targets, required-field
> affordance) belong to **`craft-ux`** → `layer-3-components.md` (Forms) — reference it, don't
> duplicate. **Client validation is UX only; the server MUST re-validate independently** —
> **`craft-security`** → `input-output.md`. The submit is a mutation — its cache/optimistic mechanics
> share rules with **`data-fetching.md`** (this skill).

> **See also:** `architecture.md` (container vs presentation, controlled/uncontrolled contract) ·
> `state.md` (a form is local state until it succeeds) · `data-fetching.md` (the mutation).

---

## Contents

- [One schema, two outputs](#one-schema-two-outputs)
- [Couple the schema to the form hook](#couple-the-schema-to-the-form-hook)
- [Validation timing](#validation-timing)
- [Accessible errors](#accessible-errors)
- [Submit lifecycle](#submit-lifecycle)
- [Optimistic updates](#optimistic-updates)
- [Multi-step & large forms](#multi-step--large-forms)
- [Server action vs client submit](#server-action-vs-client-submit)
- [Quick-reject checklist](#quick-reject-checklist)

---

## One schema, two outputs

Define the shape **once** in a schema library (Zod-style; discover the repo's choice — Zod, Valibot,
Yup, ArkType), then derive both static and runtime guarantees from that single source:

- **The TS type** via `z.infer<typeof schema>` — never hand-write a parallel `interface` that drifts
  from the validation.
- **The runtime check** via `schema.parse` / `safeParse` — the same object guards the form *and* can
  be imported by the server to re-validate (see security cross-ref).

```ts
const SignupSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
});
type SignupInput = z.infer<typeof SignupSchema>;
```

> Check Zod's changelog for your installed version — email/url API changed between v3 and v4. Don't
> assume specific method names or behavior without confirming against the version in your lockfile.

- Encode rules in the schema, not in ad-hoc handler `if`s — `.email()`, `.min()`, `.refine()` for
  cross-field rules (password confirmation), `.transform()` to coerce (`""` → `undefined`, trim).
- Keep the schema framework-agnostic and exportable so client and server share **one** definition.
  If the server runtime differs (e.g. an edge function), confirm the library runs there before
  assuming a shared import.

---

## Couple the schema to the form hook

Use the repo's existing form library (react-hook-form, TanStack Form, Formik); don't roll manual
`useState` per field for anything non-trivial — you'll reimplement dirty tracking, validation, and
focus management badly.

- Bind the schema through the library's resolver (RHF: `useForm({ resolver: zodResolver(schema) })`)
  so validation and the inferred type come from the same place.
- Prefer **uncontrolled** inputs (RHF `register`) for plain fields — fewer re-renders per keystroke.
  Reach for a controlled `Controller` only for inputs that need it (custom selects, masked inputs,
  third-party widgets). Honor the controlled/uncontrolled contract — see `architecture.md`.
- The form component stays presentation; the **submit handler is a mutation** wired by the container
  (`data-fetching.md`). Keep network concerns out of the field tree.

---

## Validation timing

Validate at the moment that informs without nagging:

- **On blur** for the first pass (`mode: "onBlur"`) — don't fire an error while the user is still
  mid-typing an email. After a field has errored once, **re-validate on change** (`reValidateMode:
  "onChange"`) so the error clears the instant they fix it.
- **On submit**, validate everything and **move focus to the first invalid field** (RHF
  `shouldFocusError`, on by default; otherwise `setFocus`/`element.focus()`). Note `shouldFocusError`
  only reaches fields RHF can focus via a registered, focusable ref — custom/controlled inputs (the
  `Controller` cases above) may need an explicit `setFocus`/manual `.focus()`. A user who can't find
  the error can't fix it.
- Async/server-uniqueness checks (email taken) are debounced on blur or surfaced from the submit
  response — not run on every keystroke.

---

## Accessible errors

Errors must reach assistive tech, not just sighted users. (Field labeling itself lives in
`craft-ux`.)

- Render the message **adjacent to the field it owns**, in a `role="alert"` live region. Keep that
  container **mounted at all times** (empty when valid) and inject/clear only its text on error —
  conditionally mounting an already-populated `role="alert"` node is announced inconsistently across
  AT/browser pairs (some treat element+text appearing together as no content change). `role="alert"`
  implies assertive+atomic, so reserve it for the field error itself; use `role="status"` /
  `aria-live="polite"` for non-urgent messages.
- Link the message to the input by **appending** the error id to `aria-describedby` (it's a
  space-separated token list — preserve any existing hint/description ids), and `aria-invalid={!!error}`
  on the input. Build it conditionally so only the error id toggles, e.g.
  `[hintId, error && errorId].filter(Boolean).join(' ') || undefined`.
- A **submit-time summary** (list of errors linking to fields) helps long forms — in addition to,
  not instead of, the inline messages.
- Don't rely on color alone to signal an error (text + icon + `aria-invalid`) — color-only is a
  `craft-ux` accessibility violation (see `layer-3-components.md`).

---

## Submit lifecycle

The button's state must tell the truth about the request:

- **Enabled before the first attempt.** Don't disable submit just because the form is `!isValid` on
  first paint — the user hasn't tried yet, and a permanently greyed button with no explanation is a
  dead end. Let them submit, then validate and focus the first error.
- **Disabled *during* the in-flight request** (`isSubmitting`), with a spinner/label change, to
  prevent double-submit. Re-enable on settle (success or error).
- Guard duplicate submits at the handler too (in-flight flag / idempotency key) — disabling the
  button is UX, not a guarantee against a fast double-click or a programmatic resubmit.
- On server rejection, map field-level errors back onto the form (RHF `setError`) and surface
  form-level failures (e.g. a toast or an alert region); don't swallow the error into a console log.
- Reset (`reset()`) only after a confirmed success, and decide deliberately whether to clear or
  retain values (a "create another" flow keeps some).

---

## Optimistic updates

Apply the mutation to the UI *before* the server confirms — but only when it earns it:

- **Worth it when** the action is frequent and **rollback is cheap and unambiguous** (toggle a like,
  rename an item, reorder a list). Skip it when failure is costly or confusing to reverse
  (payments, irreversible deletes, anything the user would be alarmed to see un-happen).
- Always implement the **rollback**: snapshot prior state, apply the optimistic value, restore on
  error, and reconcile with the server's response on success. With React Query this is the
  `onMutate`/`onError`/`onSettled` pattern; the cache mechanics live in `data-fetching.md`.
- React 19's `useOptimistic` covers transient optimistic UI tied to a transition/action; a query
  cache is still the tool when the optimistic value must persist and reconcile across components.
- An optimistic UI still needs a visible failure path — a silent revert reads as a bug.

---

## Multi-step & large forms

- Keep **one schema per step** (or a discriminated union) and validate each step before advancing;
  compose them for a final full-form parse before submit.
- Persist in-progress state where loss would hurt (a wizard, a long application) — `sessionStorage`
  or URL/query state for resumability; decide with `state.md`. Don't persist secrets or payment
  fields.
- Don't mount every step's fields at once — render the active step; preserve entered values across
  steps in the form state, not by hiding DOM.
- For very large forms, watch re-render cost (uncontrolled fields help) and validate per-section so
  one slow `refine` doesn't block typing.

---

## Server action vs client submit

Discover which the repo uses; don't introduce a second pattern beside an established one.

- **Server actions / progressive enhancement** (Next.js App Router `action={fn}`, Remix `<Form>`):
  the form posts to server-side code and supports progressive enhancement (works without JS). Running
  on the server is not the same as validating — the action must still parse and re-validate the
  submitted data authoritatively. Use the framework's pending state (`useFormStatus`,
  `useActionState`) for the in-flight UI. Still
  validate client-side for fast feedback — the action re-parses the same schema authoritatively.
- **Client submit** (`onSubmit` → fetch/mutation): you own the request lifecycle, optimistic
  updates, and error mapping above. The server endpoint it calls **still** re-validates — the client
  schema is convenience, the server schema is the gate (`craft-security` → `input-output.md`).
- Either way: **the boundary that touches the database trusts nothing from the client.** Shared
  schema reduces drift but does not remove the server's obligation to re-validate.

---

## Quick-reject checklist

Flag these in review with `file:line` and the fix:

| Pattern                                                          | Fix                                                              |
| --------------------------------------------------------------- | --------------------------------------------------------------- |
| Hand-written `interface` parallel to the validation schema       | Derive the type with `z.infer`; one source                      |
| Validation rules in handler `if`s instead of the schema          | Move into the schema (`.refine`, `.transform`)                  |
| Server endpoint trusts client-validated input                    | Re-validate with the shared schema server-side (`craft-security`)        |
| Manual `useState` per field for a non-trivial form               | Use the repo's form hook + resolver                             |
| Errors on every keystroke from first paint                       | Validate on blur; re-validate on change after first error       |
| Submit disabled while form is `!isValid` before any attempt      | Enable before first try; validate + focus first error on submit |
| Submit not disabled during the in-flight request                 | Disable + spinner on `isSubmitting`, guard double-submit        |
| Error text with no `role="alert"` / `aria-describedby`           | Wire alert region + describe/invalid on the input               |
| First error not focused on submit                                | `shouldFocusError` / `setFocus` to the first invalid field      |
| Optimistic update with no rollback path                          | Snapshot + restore on error, or drop the optimism               |
| Optimistic UI on a costly/irreversible action                    | Wait for server confirm; show pending state instead             |
| Server error swallowed (console only)                            | Map to field/form errors via `setError` + visible alert         |
| Field UX (labels, `autocomplete`, `inputmode`) reinvented here   | Defer to `craft-ux` → `layer-3-components.md`                   |

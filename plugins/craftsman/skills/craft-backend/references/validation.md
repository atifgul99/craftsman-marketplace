# Validation

The server boundary trusts nothing from the outside world. Every byte that arrives from a client — body, query string, path params, headers — is untrusted input until a schema has verified its shape, type, and constraints. **Parse-don't-validate: run the schema once at the boundary, reject immediately on failure with field-level detail, and let only typed, clean values past.** Accepting unvalidated input and checking it later is how malformed data reaches the database, how type errors become 500s, and how injection surfaces appear where nobody was looking.

> **Scope split.** This file owns server-side validation: where to place the parse call, schema organisation, field-level error shape, coercion rules, and what to derive from the schema. The **shape of the rejection response** (the error envelope, HTTP status codes, typed error codes) is the contract defined in `error-contract.md` — reference that file for the exact wire format to return when validation fails. Route structure and where a validated body gets handed off live in `api-design.md`.
>
> **See also:** **`craft-security`** → `input-output.md` (validation as a security control: injection, output encoding, and why the boundary parse is the first line of defence, not the last) · **`craft-frontend`** → `forms.md` (client-side validation is UX feedback, never the security boundary — a reject at the server is always required regardless of what the form does).

---

## Contents

- [Parse, don't validate](#parse-dont-validate)
- [Where the schema lives](#where-the-schema-lives)
- [What to validate](#what-to-validate)
- [Coercion vs validation](#coercion-vs-validation)
- [Field-level errors](#field-level-errors)
- [Deriving the type from the schema](#deriving-the-type-from-the-schema)
- [Validation as a security control](#validation-as-a-security-control)
- [Quick-reject checklist](#quick-reject-checklist)

---

## Parse, don't validate

"Validate" in the weak sense — checking a value and returning a boolean — keeps the type as `unknown` after the check. "Parse" in the strong sense — running a schema that either throws/returns an error or returns a typed, coerced value — means the type system can trust what comes out. Prefer the latter.

The distinction in practice:

```ts
// Express/Fastify pattern — adapt to the framework in use
// (Hono: c.req.json(); Next.js App Router: request.json(); tRPC: input is pre-typed)

// WEAK — value is still `unknown` after the check; the type is a lie
if (!isValidBody(req.body)) return res.status(400).json({ error: "bad input" });
const body = req.body as CreateOrderBody; // cast without proof

// STRONG — the parse either throws or returns a typed value
const body = CreateOrderSchema.parse(req.body);
// body is now `CreateOrderBody` — provably, because the schema ran
```

The parse call is a hard gate. Anything that fails the schema never reaches the handler body, the service layer, or the database. Fail fast with a rich error; never let `unknown` data flow deeper on the assumption that "we checked earlier."

---

## Where the schema lives

Schemas are co-located with the endpoint they belong to but extracted from the handler so they can be tested independently and imported by other consumers (e.g. an OpenAPI generator, a tRPC procedure definition, a client library). A reasonable layout:

```
routes/
  orders/
    create.ts          ← handler (thin, imports the schema)
    create.schema.ts   ← schema definition + exported inferred types
```

One schema file per route (or per domain object if the same shape is truly shared). Do not inline the schema inside the handler — that makes it impossible to test in isolation and couples the schema lifecycle to the route file.

**Shared schemas go in a shared location.** If two endpoints accept the same address object, define `AddressSchema` once in `schemas/address.ts` and compose it — do not copy-paste. A diverged copy is a bug waiting to surface.

Discover the pattern in the target repo before adding files. Grep for an existing schema or validation call to find the convention (`*.schema.ts`, `schemas/`, `validators/`, `validations/`) and extend it rather than introduce a second structure.

---

## What to validate

Validate **every external input surface at the boundary**, not just the body:

| Input surface | What to validate |
| --- | --- |
| **Request body** | Shape, required fields, types, string lengths, enum membership, numeric ranges, date formats |
| **Path params** | Type (e.g. `id` is a valid UUID or integer), format |
| **Query string** | Type (query params arrive as strings — coerce explicitly), allowed values, pagination bounds |
| **Headers** | Custom headers your code depends on (e.g. `x-tenant-id`, `content-type` assertions); standard headers like `authorization` belong to the auth layer, not here (see `auth.md`) |
| **File uploads** | MIME type (from magic bytes, not the browser-supplied `Content-Type`), file size, filename length |

"We know the frontend sends the right shape" is not a control. The backend has no idea who is sending the request. Validate everything, always.

## File uploads

File upload handling requires a separate validation pass that cannot be satisfied by a JSON schema library alone.

**Step-by-step:**

1. **Buffer the incoming file.** Multipart middleware (e.g. `multer`, `formidable`, `busboy`) hands you the raw buffer before any parsing. Hold it in memory or write it to a temp path — do not persist it to storage yet.

2. **Detect MIME type from magic bytes.** The browser-supplied `Content-Type` on a multipart field is attacker-controlled and trivially spoofed. Use the [`file-type`](https://github.com/sindresorhus/file-type) npm package to inspect the actual binary header:

   ```typescript
   import { fileTypeFromBuffer } from "file-type"; // or fileTypeFromStream for large files

   const detected = await fileTypeFromBuffer(buffer);
   // detected is undefined for formats file-type doesn't recognise (plaintext, SVG, CSV)
   // For those, apply additional content inspection or reject by default.

   const ALLOWED_MIME_TYPES = new Set(["image/jpeg", "image/png", "image/webp", "application/pdf"]);
   if (!detected || !ALLOWED_MIME_TYPES.has(detected.mime)) {
     throw new AppError(ErrorCode.VALIDATION_FAILED, "Unsupported file type", 400);
   }
   ```

3. **Reject on mismatch before persisting.** If the detected MIME does not match the allowed set, return a `400` with a `VALIDATION_FAILED` code and a clear message. Never write the file to object storage, the DB, or a filesystem path before this check passes.

4. **Enforce size limits at the HTTP layer, not just the schema.** Set a maximum body size in your multipart middleware — do not rely solely on the field-level check after buffering (the buffer is already in memory by then):

   ```typescript
   // multer (Express)
   const upload = multer({ limits: { fileSize: 5 * 1024 * 1024 } }); // 5 MB

   // busboy (lower-level, Hono/Fastify)
   const bb = busboy({ headers: req.headers, limits: { fileSize: 5 * 1024 * 1024 } });

   // Next.js API route — disable default body parsing, use formidable/busboy directly:
   // export const config = { api: { bodyParser: false } };
   ```

5. **Truncate or reject long filenames.** Filename strings from a multipart upload are attacker-controlled. Enforce a maximum length (e.g. 255 characters), strip path separators (`/`, `\`, `..`), and generate a server-side key for storage rather than persisting the client filename verbatim.

For the broader attack surface covered by file uploads — polyglot files, SSRF via SVG/XML, stored XSS via filename — see **`craft-security`** → `input-output.md`.

**Minimum constraints per field type:**
- Strings: `minLength`, `maxLength` (prevents unbounded payloads and DB column overflow), `trim` leading/trailing whitespace before validation
- Numbers: `min`, `max`, integer vs float where applicable
- Enums: explicit list of allowed values — do not accept arbitrary strings for fields that map to application logic
- Arrays: `minItems`, `maxItems`, per-item schema
- Optional fields: explicit — mark as `.optional()` or `.nullable()` deliberately; fields not in the schema are either stripped or rejected (see coercion)

---

## Coercion vs validation

Coercion and validation are separate concerns. Conflating them silently hides bugs.

**Coercion** converts an incoming type to the expected one (e.g. a query-string `"42"` → `42`, a date string `"2024-01-15"` → `Date`). It is appropriate at the HTTP boundary where query params and path params arrive as strings and must be typed before use.

**Validation** checks that the already-typed value is in the expected domain (e.g. `42` is within `[1, 100]`, `Date` is not in the past).

Rules for coercion at the boundary:
- **Be explicit, not implicit.** Opt in to coercion per field (e.g. `z.coerce.number()` in Zod, explicit transforms in Yup/Valibot/Joi) rather than enabling it globally. `z.coerce.number()` rejects non-numeric strings like `"100abc"` as a validation error — it does not silently produce `NaN`. However, it uses JavaScript's own number coercion (`Number(value)`) internally, which means `""` (empty string) and `null` coerce to `0` rather than failing — a silent data hazard for query and path params that should never be zero or absent. For these inputs, prefer `z.string().trim().regex(/^\d+$/).pipe(z.coerce.number())` or a `z.preprocess` that rejects empty/null before applying number coercion. If you write your own coercion with `Number()` or `parseInt()`, check for `NaN` explicitly and return a validation error rather than propagating it — `typeof NaN === "number"` is true, so it passes type guards downstream.
- **Coerce to the correct type before range-checking.** Hand-rolled coercion that produces `NaN` passes a `typeof x === "number"` check but breaks arithmetic downstream. Use the schema library's built-in coercion where possible; when writing custom coercion via `preprocess` or middleware, guard against `NaN` explicitly.
- **Strip unknown fields by default.** Fields not declared in the schema should be stripped from the parsed output, not passed through. Passing unknown fields downstream is how mass-assignment bugs occur (see **`craft-security`** → `input-output.md`). In Zod, unknown keys are stripped by default — `.strip()` is the explicit form but is not required. In Yup, Joi, and Valibot, stripping may need to be opted in — check the library docs.

```ts
// Zod example — strip unknown keys, coerce query param
const QuerySchema = z.object({
  page:  z.coerce.number().int().min(1).max(1000).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
}).strict(); // .strict() errors on unknown keys instead of stripping — pick one per context

const BodySchema = z.object({
  name:   z.string().trim().min(1).max(200),
  amount: z.number().int().min(0).max(1_000_000),
  status: z.enum(["draft", "published"]),
}); // Zod strips unknown keys by default; .strip() is the explicit, no-op-equivalent form
```

Discover what schema library the repo uses before writing a schema (`grep -r "from 'zod'" / "from 'joi'" / "from 'valibot'"` in `package.json` or source files). Extend the existing library; don't add a second one.

---

## Field-level errors

A validation rejection must tell the caller *exactly* which field failed and *why*. A generic `"Invalid request"` forces the client to guess, makes debugging painful, and is indistinguishable from a server bug.

The minimum rejection shape (exact envelope defined in `error-contract.md`):

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      { "field": "amount", "message": "Must be a positive integer" },
      { "field": "status", "message": "Must be one of: draft, published" }
    ]
  }
}
```

Rules for field-level error messages:
- **Use the dot-path convention for nested fields** (`"address.postalCode"`, `"items[0].quantity"`) so clients can map the error to the specific input.
- **Human-readable, not a raw schema message.** "String must contain at least 1 character(s)" is a library default; "Name is required" is what the client renders. Transform messages at the boundary.
- **Do not leak internal details.** DB column names, internal enum values, stack traces — none of this belongs in a 400 response. The message is a UX signal, not a debug log. Internal detail belongs in server-side structured logs (see **`craft-observability`** → `logging.md`).
- **Return all field errors in one response**, not just the first. A client correcting one field at a time is bad UX (the frontend team owns the display logic per `craft-frontend` → `forms.md`, but you owe them the complete list).

Most schema libraries produce the field-path list as part of their error output. Map it to the envelope shape once — in a shared error-formatting helper, not inline in each handler.

---

## Deriving the type from the schema

The schema is the single source of truth for the shape. TypeScript types should be **derived from the schema**, not defined separately and manually kept in sync:

```ts
// schema/orders.ts
import { z } from "zod"; // or whichever library the repo uses

export const CreateOrderSchema = z.object({
  customerId: z.string().uuid(),
  items: z.array(
    z.object({
      productId: z.string().uuid(),
      quantity:  z.number().int().min(1).max(999),
    })
  ).min(1).max(100),
  notes: z.string().trim().max(1000).optional(),
});

// Type derived from the schema — stays in sync automatically
export type CreateOrderInput = z.infer<typeof CreateOrderSchema>;
```

A hand-written TypeScript type alongside a schema is a drift bug in waiting — when the schema tightens a constraint, the type still claims the broader shape. Let the compiler own the relationship; never write the type manually when the library can infer it.

The inferred type is what the service layer accepts. The route handler parses the request body through the schema, gets a `CreateOrderInput`, and passes it down — the service layer never sees `unknown` or `any`.

---

## Validation as a security control

The boundary parse is the first line of defence: anything that fails the schema never reaches business logic, the service layer, or the database. Applying `maxLength`, strict enum allow-lists, and unknown-field stripping as schema constraints — not as afterthoughts in the service layer — is what makes the boundary meaningful. For the full security treatment of these techniques (injection, mass-assignment, DoS via payload size, and output encoding), see **`craft-security`** → `input-output.md`.

---

## Quick-reject checklist

Flag with `file:line` and the fix:

| Pattern | Fix |
| --- | --- |
| Request body cast to a type without a parse/validate call (e.g. `body as SomeType`) | Run the schema: `const input = Schema.parse(rawBody)` (adapt to the framework's body accessor) |
| Validation check returns `boolean`; type is still `unknown` after | Use a parsing schema that returns a typed value on success |
| Schema defined inline inside the handler function | Extract to `*.schema.ts`; import into the handler |
| TypeScript type defined separately from the schema | Derive via `z.infer<typeof Schema>` (or library equivalent); delete the hand-written type |
| Query param used as a number without explicit coercion | `z.coerce.number()` (or equivalent); handle coercion failure as a validation error |
| Unknown request fields passed through to the service/DB | Enable strip mode on the schema; never spread the raw request body directly |
| Validation error returns only the first failing field | Return the full field-error list in one response |
| Validation error message is a raw library default ("String must contain at least 1 character(s)") | Map to a human-readable message in the shared error formatter |
| Error response contains stack trace, DB column name, or internal enum | Strip before serialisation; log internally (`craft-observability` → `logging.md`) |
| No `maxLength` on string fields | Add `maxLength` per field |
| No body size limit at the HTTP layer | Set a size cap before the parser buffers the full request body — Express: `express.json({ limit: "1mb" })`; Hono: `app.use(bodyLimit({ maxSize: 1 * 1024 * 1024 }))`; Next.js API routes: `export const config = { api: { bodyParser: { sizeLimit: "1mb" } } }` |
| File upload saved to storage before MIME type is verified from magic bytes | Buffer the file, run `fileTypeFromBuffer` (file-type package), reject on mismatch, then persist |
| Filename from multipart upload used as storage key verbatim | Generate a server-side key; strip path separators; enforce max length (255 chars) |
| Path params used without schema validation | Parse path parameters through a schema the same as the request body |
| Two copies of the same field shape in different schema files | Extract to a shared schema; compose via import |
| Schema library added that duplicates one already in the repo | Use the existing library; discover via `package.json` grep |

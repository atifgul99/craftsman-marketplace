# Frontend Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-frontend · scope: root

## root-FE-001 · severity 🟡 · status open
**What breaks (plain language):** When a new user has no invoices yet, or the data fails to load, the
page shows a blank white area — it looks broken, and they don't know what to do next.
**Technical:** The invoice list renders only the populated case; no empty state and no error boundary
co-located at the fetch. `app/(dashboard)/invoices/page.tsx:18`.
**Fix:** Add explicit loading, empty, and error states at the fetch site (empty ≠ a blank div). See
craft-frontend → `data-fetching.md`.
**Fingerprint:** `scope=root · domain=frontend · class=missing-async-states · resource=invoices list view`
**Last-checked:** 2026-06-22 · a1bec8f

## root-FE-002 · severity 🟡 · status open
**What breaks (plain language):** The new-invoice form lets you submit nonsense (empty amounts, bad
dates) and only fails *after* hitting the server — a clunky, error-prone experience, and the server is
the only thing standing between bad input and the database.
**Technical:** Hand-written form with no schema validation; types declared parallel to no source of
truth; submit not disabled in-flight. `app/(dashboard)/invoices/new/form.tsx:30`.
**Fix:** Validate with a shared schema (reused on the server per `root-SEC-003`); disable submit while
pending; show field errors via an `aria` live region. See craft-frontend → `forms.md`.
**Fingerprint:** `scope=root · domain=frontend · class=form-no-validation · resource=NewInvoice form`
**Last-checked:** 2026-06-22 · a1bec8f

## root-FE-003 · severity 🟢 · status open
**What breaks (plain language):** Marking an invoice paid feels laggy — the UI waits for the server
round-trip before updating, so it seems unresponsive on a slow connection.
**Technical:** Mutation re-fetches the whole list instead of updating the touched item; no optimistic
update. Acceptable today; a polish item. `app/(dashboard)/invoices/page.tsx:40`.
**Fix:** Adopt a data-fetching lib with an optimistic update + invalidation on the affected key (skip
optimism for irreversible actions). See craft-frontend → `data-fetching.md`.
**Fingerprint:** `scope=root · domain=frontend · class=no-optimistic-update · resource=mark-paid mutation`
**Last-checked:** 2026-06-22 · a1bec8f

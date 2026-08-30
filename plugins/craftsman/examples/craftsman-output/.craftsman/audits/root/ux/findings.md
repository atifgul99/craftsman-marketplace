# UX Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-ux · scope: root

## root-UX-001 · severity 🟡 · status open
**What breaks (plain language):** The invoice list only looks right when it has data. New accounts see
a blank panel; failed loads look the same as "still loading" — people think the product is broken.
**Technical:** `app/(dashboard)/invoices/page.tsx` renders the table only for the populated case; no
dedicated empty illustration/CTA, no error panel, loading is a bare unlabelled spinner (also
`root-FE-001` on the frontend data-fetching side — UX owns the user-visible state design).
**Fix:** Design and implement co-located empty, loading, and error states with clear next actions
("Create your first invoice"). See craft-ux → `layer-4-states.md`.
**Fingerprint:** `scope=root · domain=ux · class=missing-list-states · resource=invoices list`
**Last-checked:** 2026-06-22 · a1bec8f

## root-UX-002 · severity 🟢 · status open
**What breaks (plain language):** Spacing and colors look like raw AI output — one-off hex values and
magic padding everywhere. The dashboard never quite feels like one product; every screen is a little
off.
**Technical:** No token module; components use ad-hoc Tailwind like `p-[13px]`, `text-[#6B7280]`,
`bg-[#F9FAFB]` instead of a shared scale. `app/(dashboard)/invoices/page.tsx` and
`app/(dashboard)/invoices/new/form.tsx`.
**Fix:** Introduce a small token layer (color, space, radius, type) and replace raw values; optional
CI scanner later. See craft-ux → `layer-1-tokens.md` and `token-audit.md`.
**Fingerprint:** `scope=root · domain=ux · class=token-bypass-raw-values · resource=dashboard Tailwind utilities`
**Last-checked:** 2026-06-22 · a1bec8f

## root-UX-003 · severity 🟡 · status open
**What breaks (plain language):** The new-invoice form fields aren't properly labelled for assistive
tech — placeholder-only "labels" and inputs without wired `<label htmlFor>`. Keyboard and screen-reader
users hit a wall; also fails basic a11y expectations for a money form.
**Technical:** `app/(dashboard)/invoices/new/form.tsx` uses placeholder text as the only field name;
no `htmlFor`/`id` pairing; amount field is `type="text"` not `type="number"`/`inputMode`. Errors (when
any) are not linked via `aria-describedby`.
**Fix:** Visible labels for every control, correct input types, associate errors with fields. See
craft-ux → `layer-3-components.md` and craft-frontend → `forms.md`.
**Fingerprint:** `scope=root · domain=ux · class=inaccessible-form-labels · resource=NewInvoice form`
**Last-checked:** 2026-06-22 · a1bec8f

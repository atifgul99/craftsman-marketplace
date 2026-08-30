# Observability Findings — root

> Generated: 2026-06-22 · commit a1bec8f · driven by craft-observability · scope: root

## root-OBS-001 · severity 🟡 · status open
**What breaks (plain language):** When the app throws an error for a real user, nobody finds out — it
fails silently and you only hear about it if a customer complains. For an app handling invoices, that's
flying blind.
**Technical:** No error tracking wired (no `@sentry/*` dependency, no `instrumentation.ts`); unhandled
exceptions and promise rejections go uncaptured. Project-wide.
**Fix:** Add Sentry: capture unhandled errors + rejections, scrub PII in `beforeSend`, tag events with
release + environment, set a deliberate `tracesSampleRate`. See craft-observability → `sentry.md`.
**Fingerprint:** `scope=root · domain=observability · class=no-error-tracking · resource=app-wide error capture`
**Last-checked:** 2026-06-22 · a1bec8f

## root-OBS-002 · severity 🟡 · status open
**What breaks (plain language):** When something goes wrong, there's no usable trail to follow — just
scattered `console.log` lines with no way to tie them to a specific request or user.
**Technical:** Logging is bare `console.log` in handlers; no structured JSON, no central logger, no
`requestId`/`traceId` correlation. `app/api/invoices/route.ts:20` and elsewhere.
**Fix:** Route logs through one structured logger that stamps a stable `requestId` on every line; drop
ad-hoc `console.log` from production paths. See craft-observability → `logging.md`.
**Fingerprint:** `scope=root · domain=observability · class=unstructured-logging · resource=request logging`
**Last-checked:** 2026-06-22 · a1bec8f

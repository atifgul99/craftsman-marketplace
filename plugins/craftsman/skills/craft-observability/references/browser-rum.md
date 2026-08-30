# Browser RUM (Real User Monitoring)

Server-side observability is blind to what the user actually experiences in the browser. Browser
RUM closes that gap: it captures JavaScript errors, performance timings, session context, and
Core Web Vitals as they happen in real user sessions — not in a synthetic probe. **Start with
error capture; add performance tracing and session replay only when the value is clear and the
privacy cost is acceptable.**

> **Scope split.** This file owns browser-side Sentry init, React error boundaries, sourcemap
> upload for Next.js, session replay sampling, and Core Web Vitals as SLIs. Server-side Sentry
> init (Node.js / Next.js server runtime) is `sentry.md`. OTel tracing and log correlation are
> `otel-integration.md`. SLO definition from these SLIs is `slo-alerts.md`.

---

## Contents

- [@sentry/react init](#sentryreact-init)
- [Error boundary with Sentry.ErrorBoundary](#error-boundary-with-sentryerrorboundary)
- [Sourcemap upload for Next.js](#sourcemap-upload-for-nextjs)
- [Session replay sampling](#session-replay-sampling)
- [Core Web Vitals as SLIs](#core-web-vitals-as-slis)
- [Quick-reject checklist](#quick-reject-checklist)

---

## @sentry/react init

Initialize Sentry once, as early as possible in the client entry point — before any component
renders:

```ts
// app/sentry.client.ts (or wherever your client entry runs first)
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,   // public ingest URL — safe to expose in browser
  environment: process.env.NEXT_PUBLIC_ENV,  // "production" | "staging" | "development"
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE, // git SHA injected at build time

  // Performance tracing — start at 0.1; tune down if quota is hit
  tracesSampleRate: 0.1,

  integrations: [
    Sentry.browserTracingIntegration({
      // Propagate traceparent to your own API routes so browser traces correlate with server spans
      tracePropagationTargets: [
        'localhost',
        /^https:\/\/api\.yourapp\.com/,  // replace with the repo's actual API domain
      ],
    }),
  ],

  // Session replay — see the "Session replay sampling" section
  replaysSessionSampleRate: 0.05,    // 5% of normal sessions
  replaysOnErrorSampleRate: 1.0,     // 100% of sessions where an error occurred

  beforeSend(event) {
    // Drop events from local dev to avoid polluting production data
    if (process.env.NODE_ENV === 'development') return null;
    return event;
  },
});
```

> Build-inlined `NEXT_PUBLIC_` vars are the sanctioned exception to the no-raw-`process.env` rule
> (they're compile-time constants, not runtime reads).

**Discover before adding:** check `package.json` for an existing `@sentry/react`, `@sentry/nextjs`,
or `@sentry/browser`. Use the SDK already installed — don't add a second one. `@sentry/nextjs`
wraps both client and server Sentry init; if the repo uses it, follow the Next.js init pattern
rather than the bare `@sentry/react` approach above.

---

## Error boundary with Sentry.ErrorBoundary

Wrap the React component tree (or critical subtrees) in `Sentry.ErrorBoundary` so that render-time
errors are captured with full component context, not just the global `window.onerror`:

```tsx
import * as Sentry from '@sentry/react';

// Top-level: wrap the entire app so no error falls through uncaptured
export function AppRoot({ children }: { children: React.ReactNode }) {
  return (
    <Sentry.ErrorBoundary
      fallback={({ error, resetError }) => (
        <div role="alert">
          <p>Something went wrong. Our team has been notified.</p>
          <button onClick={resetError}>Try again</button>
        </div>
      )}
      onError={(error, componentStack, eventId) => {
        // Optional: additional logging alongside the automatic Sentry capture
        console.error('[ErrorBoundary]', eventId, error);
      }}
    >
      {children}
    </Sentry.ErrorBoundary>
  );
}
```

`Sentry.ErrorBoundary` is a thin wrapper around React's class-based `componentDidCatch` — it
calls `Sentry.captureException` automatically with the component stack attached. You don't need
a separate `captureException` call inside `onError` unless you want to add extra scope context.

For critical sub-routes (checkout, payment, auth), add a nested `Sentry.ErrorBoundary` so errors
in those flows are tagged with the relevant context and have their own fallback UI:

```tsx
<Sentry.ErrorBoundary
  fallback={<CheckoutErrorFallback />}
  beforeCapture={(scope) => scope.setTag('flow', 'checkout')}
>
  <CheckoutFlow />
</Sentry.ErrorBoundary>
```

---

## Sourcemap upload for Next.js

Without sourcemaps, Sentry shows minified stack frames. With `@sentry/nextjs`, the Sentry webpack
plugin uploads sourcemaps automatically during `next build` when `SENTRY_AUTH_TOKEN` is set:

```ts
// next.config.ts
import { withSentryConfig } from '@sentry/nextjs';

const nextConfig = {
  // ... your existing Next.js config
};

export default withSentryConfig(nextConfig, {
  // The org and project must match your Sentry project settings
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,

  // Suppress the "Uploading sourcemaps" output in CI logs if needed
  silent: !process.env.CI,

  // Include more client files in the sourcemap upload for better stack traces
  widenClientFileUpload: true,

  // Upload sourcemaps to Sentry, then delete them so they never ship in the public bundle
  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },

  // Explicit release name — omit this and the plugin auto-detects the git SHA from
  // most CI/VCS environments; set it explicitly when running on Vercel:
  release: {
    name: process.env.VERCEL_GIT_COMMIT_SHA,
  },

  // Auto-wraps Next.js server functions (API routes, server actions, middleware)
  // with Sentry instrumentation for error/performance tracking
  autoInstrumentServerFunctions: true,
});
```

Required environment variables in CI:

```
SENTRY_AUTH_TOKEN=<project auth token from Sentry Settings → Auth Tokens>
SENTRY_ORG=<your-org-slug>
SENTRY_PROJECT=<your-project-slug>
NEXT_PUBLIC_SENTRY_DSN=<your-dsn>
NEXT_PUBLIC_SENTRY_RELEASE=<git-sha>  # or let withSentryConfig auto-detect from git
```

`SENTRY_AUTH_TOKEN` is the actual secret — store it in the CI secret store, never in source.
`NEXT_PUBLIC_SENTRY_DSN` is a public ingest URL (safe to expose in the browser bundle), but it
is environment-specific config — load it from env, don't hardcode it.

---

## Session replay sampling

Session Replay records browser interactions (clicks, scrolls, input, network requests) to
replay exactly what a user did before an error. It has two sampling levers:

```ts
Sentry.init({
  // ...
  replaysSessionSampleRate: 0.05,   // record 5% of all sessions, regardless of errors
  replaysOnErrorSampleRate: 1.0,    // record 100% of sessions where an error is captured
});
```

- **`replaysOnErrorSampleRate: 1.0`** is the high-value setting — you get a full recording of
  every session that produces an error, without paying replay storage cost for the 95%+ of
  sessions that are error-free.
- **`replaysSessionSampleRate`** controls "always record" sessions for UX analysis. Start at
  0.05 (5%) and tune based on replay storage cost. Avoid 1.0 in production — it is expensive
  and raises privacy concerns for users who don't trigger errors.
- Session Replay may capture sensitive input (passwords, card numbers, PII). Enable **input
  masking** (the default in Sentry's Replay SDK) and verify it covers all sensitive fields before
  enabling in production. Check your privacy policy covers session recording.
- Wire `Sentry.replayIntegration()` in `integrations: []` when using Sentry SDK v8+:
  ```ts
  import * as Sentry from '@sentry/react';
  // in Sentry.init:
  integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration({ maskAllInputs: true })],
  ```

---

## Core Web Vitals as SLIs

Core Web Vitals are Google's browser-measured performance metrics. They are meaningful
user-facing SLIs because they directly measure what the user perceives, not what the server
reports:

| Metric | Threshold (Good) | What it measures |
| --- | --- | --- |
| **LCP** (Largest Contentful Paint) | < 2.5 s | How quickly the main content becomes visible |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Visual stability — does content jump around? |
| **INP** (Interaction to Next Paint) | < 200 ms | Responsiveness to user interaction (replaced FID in 2024) |

Use these as SLIs for your frontend SLO. A realistic target for a production app: "95% of page
loads have LCP < 2.5 s over 28 days." A breach means users are experiencing slow renders — not
that a server metric crossed a threshold.

**Measuring in Sentry:** Sentry's `BrowserTracing` integration captures Web Vitals automatically
when performance tracing is enabled (`tracesSampleRate > 0`). View them in Sentry under
Performance → Web Vitals. For custom SLO tracking, export the vitals to your metrics backend:

```ts
import { onLCP, onCLS, onINP } from 'web-vitals';

// Send to your analytics or metrics endpoint
function sendToAnalytics({ name, value, id }: { name: string; value: number; id: string }) {
  // Push to your OTLP collector, Datadog RUM, or a custom endpoint
  fetch('/api/vitals', {
    method: 'POST',
    body: JSON.stringify({ metric: name, value, id }),
    headers: { 'Content-Type': 'application/json' },
  });
}

onLCP(sendToAnalytics);
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
```

Wire these measurements to your SLO dashboard (`slo-alerts.md`) and alert when the p75 LCP
exceeds 2.5 s — the same multi-window burn-rate pattern applies.

**Real-vs-lab distinction:** Core Web Vitals measured from real user sessions (RUM) are the
canonical SLI. Lighthouse scores and PageSpeed Insights are lab measurements under synthetic
conditions — useful for debugging, not for an SLO. Use RUM data for the SLO target.

---

## Quick-reject checklist

| Pattern | Fix |
| --- | --- |
| `@sentry/react` (or `@sentry/nextjs`) not initialized before first render | Move `Sentry.init` to the client entry point; confirm it runs before any component mounts |
| `NEXT_PUBLIC_SENTRY_DSN` hardcoded in source | Load from env; it's environment-specific config even though it's a public value |
| No `Sentry.ErrorBoundary` wrapping the app | Add at the root; add nested boundaries around critical flows (checkout, auth) |
| `tracesSampleRate: 1.0` in production | Lower to ≤ 0.1; 1.0 saturates Sentry quota on any real traffic |
| `replaysSessionSampleRate: 1.0` in production | Use 0.05–0.1 for baseline; keep `replaysOnErrorSampleRate: 1.0` |
| Session Replay active without input masking | Enable `maskAllInputs: true` in `replayIntegration()` — unmasked replay may capture passwords and card numbers |
| Sourcemaps committed to the public `/_next/static/` directory | Set `sourcemaps: { deleteSourcemapsAfterUpload: true }` in `withSentryConfig`; sourcemaps should upload to Sentry only, not ship publicly |
| `SENTRY_AUTH_TOKEN` stored in `.env` in the repo | Move to CI secret store; it's an actual secret (unlike the DSN) |
| No Core Web Vitals measurement wired | Add `web-vitals` + `onLCP`/`onCLS`/`onINP` and push to analytics; use as SLIs |
| LCP / CLS / INP thresholds not tied to SLO | Define a p75 target and wire to `slo-alerts.md` burn-rate alerting |
| Sentry events from `localhost` / `development` mixing with production | Drop in `beforeSend` when `NODE_ENV === 'development'`; use Sentry environment filters |
| Multiple `Sentry.init` calls in the same bundle | Remove duplicates — multiple inits overwrite each other |

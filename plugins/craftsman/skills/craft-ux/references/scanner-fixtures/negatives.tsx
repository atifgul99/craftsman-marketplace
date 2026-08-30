// Scanner fixtures — KNOWN NEGATIVES.
// Every line below is CORRECT, token-routed code. No token-audit.md check may fire on this file.
// A hit here is a FALSE POSITIVE — the check over-matches and will cry wolf in real repos
// (exactly the failure the shipped greps are tuned to avoid). One line per check id.

export function Negatives() {
  return (
    <>
      {/* 1a — semantic color tokens, not palette classes */}
      <span className="text-destructive" />
      <span className="border-l border-border" />

      {/* 1b — bracket value that is a CSS variable, not a literal */}
      <span className="bg-[var(--surface)]" />
      <span className="shadow-[var(--shadow-card)]" />

      {/* 1c — token-driven glass component, no raw blur utility */}
      <span className="glass-panel" />

      {/* 2 — inline style routed through a variable */}
      <span style={{ color: 'var(--fg)' }} />

      {/* 3 — spacing via a layout primitive, not raw utilities on a div */}
      <Stack gap="md" />

      {/* 4 — shared muted-text component */}
      <MutedText>secondary</MutedText>

      {/* 5 — shared form-error component */}
      <FormError>required</FormError>

      {/* 6 — typography token component, not a raw font utility */}
      <Text variant="code" />

      {/* 7 — explicit-property transition; no all-properties shorthand, no numeric ms utility */}
      <button className="transition-colors" />

      {/* 9 — shared spinner component, not an inline spin utility */}
      <Spinner />
    </>
  )
}

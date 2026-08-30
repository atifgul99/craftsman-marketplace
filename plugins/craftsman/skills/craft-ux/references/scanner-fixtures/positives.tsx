// Scanner fixtures — KNOWN POSITIVES.
// Every line below MUST be caught by the matching token-audit.md check. If a check stops firing
// on its line here, the check regressed (or a prefix/palette list drifted) — fix the check.
// Self-test: see README.md in this directory. One line per check, labelled with its check id.
// NOTE: in a real repo, add this fixtures dir to the scanner's EXEMPT list so it never fails CI;
// it is meant to be run against explicitly, not swept with production code.

export function Positives() {
  return (
    <>
      {/* 1a — hardcoded named palette class (category a) */}
      <span className="text-red-500" />
      <span className="border-l-blue-600" />

      {/* 1b — arbitrary color / inset shadow literal (category a) */}
      <span className="bg-[#1a1a2e]" />
      <span className="shadow-[inset_0_1px_0_rgba(0,0,0,.12)]" />

      {/* 1c — raw blur / glass elevation (category e) */}
      <span className="backdrop-blur-md" />
      <span className="blur-[6px]" />

      {/* 2 — inline style with a raw color literal (category b) */}
      <span style={{ color: '#ffffff' }} />

      {/* 3 — raw layout spacing on a generic <div> (category c) */}
      <div className="flex gap-4" />
      <div className="space-y-px" />

      {/* 4 — hand-rolled muted secondary text (category h) */}
      <p className="text-sm text-muted-foreground" />

      {/* 5 — hand-rolled error text (category h) */}
      <p className="text-xs mt-1 text-destructive" />

      {/* 6 — raw font-family utility (category d) */}
      <code className="font-mono" />

      {/* 7 — inline transition timing (category f) */}
      <button className="transition-all" />
      <button className="duration-300 ease-in-out" />

      {/* 9 — hand-rolled spinner in domain code (category h) */}
      <svg className="animate-spin" />
    </>
  )
}

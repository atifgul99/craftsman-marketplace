// Scanner fixture for check 8 (category g) — cross-layer leak in the TOKEN MODULE.
// KNOWN POSITIVE: `@keyframes` belongs in the base stylesheet, not the token module.
// Check 8 runs `rg '@keyframes' "$TOKEN_MODULE"` — point it at this file; it MUST fire.

export const spin = `
@keyframes spin {
  to { transform: rotate(360deg); }
}
`

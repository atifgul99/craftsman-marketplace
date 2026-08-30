# State Tax Router

Load the relevant state file(s) based on the entity and question. Never load all states upfront.

## Deriving the entity → state map

**Do not hardcode a roster here.** The entity list lives in
`workspace-profile/entities-index.md` and per-entity registration detail lives in
`entities/<slug>/entity.md` — this file owns only the *routing rule*. Derive the map at
read time:

1. Read `workspace-profile/entities-index.md` for the entity roster and formation states.
2. For each entity, read `entities/<slug>/entity.md` → **State Registrations** for the
   home state, registration status, filing frequency, and any foreign qualifications.
3. Note the individual's **state of residency** from `individual/profile.md`.
4. Load only the `states/<abbr>/` files those states call for.

Formation state ≠ obligation. An entity formed in a no-tax state still owes where it has
nexus; a disregarded SMLLC generally follows its **regarded parent**. Where a registration
is unconfirmed, treat it as an open item rather than assuming no obligation.

| Situation | Load |
|---|---|
| Entity registered in, or with nexus in, WA | `wa/` |
| Entity formed in WY with no other-state nexus | `wy/` |
| Individual resident of WA | `wa/README.md` (capital gains tax section) |
| Any other state | Create `states/<abbr>/` — see "Adding a new state" below |

## When to load each file

| Question is about… | Load |
|---|---|
| B&O filing, what's owed, MyDOR, gross receipts, B&O classification | `wa/bo-tax.md` |
| Personal Property Tax Listing (county assessor) | `wa/property-other.md` |
| Unclaimed property reporting | `wa/property-other.md` |
| WA capital gains tax (individual) | `wa/README.md` |
| WY annual report, registered agent, no-tax confirmation | `wy/README.md` |
| New state added (CA, OR, TX, etc.) | Create `<state-abbr>/` subfolder following this pattern |

## Adding a new state

1. Create `states/<abbr>/README.md` — tax type overview + entity applicability
2. Add detail files as needed (e.g., `ca/franchise-tax.md`, `or/income-tax.md`)
3. Add a row to the routing table above (the *rule*, not a named entity)
4. Update `SKILL.md` description to mention the new state

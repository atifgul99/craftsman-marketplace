# Portability

**This skill ships publicly. It must contain no user's data.** The workspace and
the skill are different things, and every edit to the skill is subject to the
three-bucket test:

| Bucket | Contents | Where it lives |
|---|---|---|
| **Skill** | Method, doctrine, statutes and regulations, status vocabularies, schemas, templates, worked *hypotheticals* | This plugin — public |
| **Workspace data** | Entity names, people, addresses, EINs and other identifiers, dollar amounts, account numbers, engagement facts, holdings | `workspace-profile/`, `individual/`, `entities/<slug>/` — never here |
| **Engagement output** | Audits, workpapers, drafts, record books | The workspace, under the entity it belongs to |

Concretely, and without exception:

- No real entity, person, address, identifier, or dollar figure enters a skill
  file, a template, a schema, or an eval fixture. Fixture data is invented and
  obviously so.
- **No jurisdiction is hard-coded into a schema enum, a validator branch, or a
  required field.** Vocabularies are generic (`STATE_REGISTRATION`, not a
  particular state's route) and validators check the *shape and source family*
  of an authority, not a roster of jurisdictions. A validator that refuses every
  state but one is a portability bug, not strictness.
- State-specific statutes live under `states/<code>/`, and are cited from the
  general files as examples, clearly labelled as such.
- No absolute local path appears in any tracked file.
- Numbers that change by year live in `rules/federal-<year>.json`, never in
  prose. See the anti-duplication rule below.

When a lesson comes out of a real engagement, extract the **rule** and leave the
facts behind. If a passage cannot be written without naming the matter it came
from, it is not yet a rule.

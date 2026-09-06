# Explicit rulebook dependency manifest

`python -X utf8 scripts/rulebook_check.py <project.json> [--changed <rule-id>]`

Standard-library checker; reads JSON and referenced UTF-8 files, never rewrites a book or executes formulas. Exit 0 means structural checks passed; exit 1 means invalid structure, stale bindings, conflicting claims or unresolved material issues. The JSON result includes reverse transitive impact for an optional changed ID. File paths must resolve within the manifest directory, including symlinks; keep the manifest at the project root.

Root fields: `version` (positive integer), `rules` (nonempty list), `artifacts` (nonempty list), `issues` (list). Unknown fields are not interpreted. A rule has unique `id`, positive `revision`, `file`, `depends_on` (rule IDs), and `contract` containing nonempty trigger, authority, inputs, procedure, costs, outcomes, duration, exceptions, example, boundary. Text can say why a field is inapplicable. Canonical formulas belong in prose and examples, not executable strings.

An artifact has unique `id`, `file`, `audience` (`player` or `gm`), `bindings` mapping rule IDs to exact revisions, and optional `claims` mapping named facts to JSON values. Shared claims must agree across all artifacts; variant-specific claims use different keys. These are explicit semantic claims supplied by the author, not extracted facts. Public artifacts may not bind directly or transitively to a rule whose canonical file is listed as a GM artifact. This detects declared dependencies only; review actual text for secret leakage.

An issue has unique `id`, `material` (boolean), `status` (`open` or `resolved`), and `evidence` (nonempty text). Open material issues block structural acceptance. Every rule must be bound by an artifact; self-reference and dependency cycles are reported for review (a conceptual cycle must be documented without creating a prerequisite cycle). Missing canonical files, duplicate identifiers, unknown dependencies and stale revisions fail. An existing empty prose file fails; nonempty content is not proof of complete prose.

Use `--changed` before modifying a rule to find its callers. Increment that rule's revision; re-read callers and update all affected artifact bindings only after revising or explicitly verifying them. Changing a bound revision number alone is not a repair. The dream fixture's [manifest](../assets/examples/rulebook/dream/project.json) is a complete input example. The contradiction case demonstrates what registered claims can catch.

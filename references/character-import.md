# Structured character imports and stat snapshots

Use `scripts/characters.py` to create or update campaign actors without editing SQLite or an entire saved state. Imports validate structure, sources, rule profile and compatibility with pending play. They do not certify complete character creation, point budgets, derived statistics, equipment legality or advancement eligibility.

## Private preview, then exact application

Start with the [original import example](../assets/examples/character-import.json), whose profile matches `assets/templates/session-initial.json`. The values are illustrative, not a complete CoC character. Keep working manifests and preview/export files in the private campaign directory.

```powershell
python -X utf8 scripts/characters.py '<campaign.sqlite>' preview --manifest '<manifest.json>' --event-id import-pc3-1 --private-output '<plan.json>'
python -X utf8 scripts/characters.py '<campaign.sqlite>' apply --plan '<plan.json>'
python -X utf8 scripts/characters.py '<campaign.sqlite>' view --player pc3
python -X utf8 scripts/characters.py '<campaign.sqlite>' export --actor pc3 --private-output '<update-manifest.json>'
```

Preview reads the current ledger revision, simulates the entire import and writes a private field-by-field diff plus the complete event. It does not create an event or modify the database. Stdout contains only revision, change count and success status. Review the private plan file to inspect values and notes.

Application uses the manifest embedded in the plan, not the possibly changed original input file. A checksum detects accidental edits to the preview; regenerate a preview after editing. This is an integrity check, not authentication against a malicious local operator. A stale revision rejects application. Exact event retries acknowledge the original import without applying it again. All entries in a batch commit or roll back together.

The tool does not prompt interactively: `apply --plan` is the explicit application operation. The standard trusted-local-operator model applies; actor IDs are not login credentials.

## Manifest contract

The root has exactly `schema: 1`, `profile`, `sources`, and `characters`. Profile must equal the campaign's system/edition/options. Sources must be nonempty rule anchors or explicit GM rulings. Batches contain 1–100 unique actor IDs. Unknown fields and wrong types fail validation.

Each entry has exactly:

- `mode`: `create` or `update`. Create refuses existing IDs; update refuses absent IDs.
- `id`: stable campaign actor identity. Renaming `name` does not change this identity.
- `name`: display name.
- `audience`: explicit audience for the ledger actor, including its resources and conditions.
- `sheet_audience`: independent audience for name and imported stats. A public sheet does not automatically reveal private resources.
- `stats`: canonical stat IDs mapped to `label`, `aliases`, and integer `value`.
- `resources`: resource records described below.
- `gm_notes`: private text, never included in player projection.

`all` in an audience means public; an empty list means GM-only. The manifest carries explicit publishing choices. Do not put private content into public labels or aliases.

## Resource ownership and updates

Create supplies each resource as `{"value":10,"max":12}`. A newly added resource on an existing actor also requires both values.

Update supplies an existing resource as `{"max":20}` only. Supplying `value` is rejected, preventing stale exports from silently refilling a damaged or depleted character. Increasing capacity preserves the amount already spent: 10/12 becomes 18/20. Lowering capacity follows the existing ledger resize contract and clamps current value to the new maximum; it does not infer healing or rules eligibility.

All existing resource IDs must remain in an update. Imports cannot delete resources or replace existing conditions. Use explicit sourced ledger events for damage, healing and condition changes. New actors start with no conditions and gain no existing character's private facts, history or pending choices.

Mechanical updates (changed stats or resources) require the actor to have no unresolved actions, costs or pending decision, and to be outside a running encounter. Finish/leave through the existing encounter workflow first. Cosmetic name changes or explicit visibility/note changes can keep the same actor identity while it is in combat. Resource reservations and configured refresh bounds are still checked by the ledger before commit.

## Multilingual stats and action binding

Stat IDs use lowercase ASCII identifiers such as `spot_hidden` and `fighting_brawl`. Labels and aliases may use Chinese, English and spaces. Name matching applies Unicode NFC normalization, case folding and whitespace normalization. A name or alias cannot ambiguously resolve to two different stat IDs. Values accept integers -999..999 as a storage bound, not as a rule-system legality range.

Add an optional reference to an action declaration:

```json
"stat_ref": {"actor":"pc3", "stat":"Spot Hidden"}
```

The reference must belong to the acting character. Declaration resolves the canonical ID and stores an immutable private snapshot of the stat label/value and source sheet event. Updating the sheet later does not change that action's evidence. The snapshot does not automatically set difficulty, determine success or spend resources; those remain explicit steps of the selected rules procedure. Pending action guards prevent changing the character's mechanics in the middle of that flow.

## Export, persistence and disclosure

Default `export` writes an update manifest with resource maxima, not current values. This roundtrips configuration without refilling resources. `export --mode create` includes current/max values for explicitly creating a separate actor after changing the ID; it cannot overwrite the existing one. This is a character configuration export, not a full campaign backup: it does not copy conditions, learned facts, active effects or pending decisions.

Exports and preview plans contain GM notes and source information, so they require `--private-output`. Existing files with different contents are never overwritten. Player views expose only explicitly authorized name and typed stat fields. They never return GM notes, source metadata or the complete stored object. `session.py view` includes the same filtered character sheet projection.

Sheet metadata lives under `private.characters`, schema 1. Current resources and conditions remain solely under ledger actors; there is no duplicate resource balance in the metadata. Ordinary private-state replacement must preserve this reserved store. Explicit ledger restore rewinds actors and sheets together while retaining event history.

## Verification

Eighteen new tests cover preview immutability, exact retries, capacity changes, damage/condition preservation, malformed input, multilingual aliases, visibility, stat snapshots, pending/combat guards, new-character entry, stale/modified plans, atomic batch failure, export roundtrip, CLI cold-process operation and restore. See [validation](validation.md).

## Partial advancement updates

Use `preview-update` when changing only selected fields of an already imported sheet. The [original patch example](../assets/examples/character-update.json) is a storage workflow example, not a system-approved advancement calculation.

```powershell
python -X utf8 scripts/characters.py campaign.sqlite preview-update --actor pc3 --patch character-update.json --event-id advancement-1 --private-output advancement-plan.json
python -X utf8 scripts/characters.py campaign.sqlite apply --plan advancement-plan.json
```

Patch fields are exactly `schema: 1`, nonempty `sources`, and `changes`. Permitted change keys are `name`, `audience`, `sheet_audience`, `gm_notes`, `stats`, `resources`, and `remove_stats`. Unknown keys are rejected. A character must already have an imported sheet; use the full import procedure to establish one.

Scalar fields and audience lists replace their corresponding value explicitly. Omitted fields remain unchanged. `stats` merges by canonical ID: each supplied stat must still contain its complete label, aliases and integer value, so omissions cannot silently remove an existing stat. `remove_stats` is a list of distinct existing IDs to remove; the same stat cannot be updated and removed together. Missing stats continue to exist, and removal does not rewrite snapshots of earlier actions.

`resources` merges by resource ID. An existing resource accepts only `max`; new resources require `value` and `max`. Patches cannot delete resources, inject an existing current balance, replace conditions or change the rules profile. Capacity increases preserve spent amounts under the existing contract, while reductions clamp current values to the new maximum. The preview's before/after field diff shows the resulting balances; it does not imply healing or a legal advancement entitlement.

The patch's source anchors replace the current sheet's source list, so include all anchors needed for the resulting sheet. Prior anchors remain in ledger history. The merged manifest goes through the same validation, pending-action/encounter checks, private preview checksum and revision checks as a full import. The merge and preview share one snapshot; intervening changes make the resulting plan stale instead of permitting an overwrite from an earlier export. Regenerate a stale preview from the latest state.

Thirteen additional tests cover untouched-field preservation, resource limits, explicit stat removal, source/schema validation, pending actions, one-snapshot concurrency, private CLI output, cold apply, idempotency and restore. No automatic experience spending, derived-stat recomputation or edition-specific advancement legality is introduced.

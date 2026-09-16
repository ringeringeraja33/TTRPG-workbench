# Recoverable action workflow

Use `scripts/actions.py` with a campaign created by `scripts/session.py`. This workflow connects a declared intent, dice evidence, pending player choices and an atomic settlement. It does not determine complete action legality or replace the selected rules procedure.

## Authority and storage

The campaign ledger is the resource authority for actions using this workflow. Dice supplies evidence only; do not separately apply the same HP, SAN, ammunition or slot change in the Dice database. Existing card-only and local-table databases remain separate and are not migrated or overwritten.

Action state is stored under `private.action_workflow`, schema 1, in the same event snapshot and SQLite transaction as campaign resources. Existing campaigns without that key work unchanged. Other private state and existing pending rulings are preserved. Ordinary `private` replacement must preserve the action store; use action transitions or an explicit ledger restore to change it.

The operator is trusted. Actor IDs identify participants, not authenticated users. Keep the campaign and Dice databases private.

## State transitions

- `declare`: persist actor, public summary, internal intent/method/stakes, audience, roll specification and settlement costs. Binds the campaign profile and source citations.
- `roll`: persist an actual local roll, a previously committed Dice receipt, or a clearly labelled player-reported manual total. No resource changes yet.
- `wait`: save the decision actor, prompt and named choices after the roll (or on an explicitly no-roll action).
- `choose`: record an offered choice from the designated actor. Multiple successive decisions retain their earlier selections.
- `settle`: record the adjudicated outcome and apply declared costs plus explicit effects together. Waiting choices or missing rolls prevent settlement.
- `reserve` / `release`: explicitly acquire or release the hold on declared costs, with a reason. Releasing a hold does not waive the eventual cost.
- `cancel`: close an action before dice evidence exists, with a reason and no costs; release its hold. A rolled attempt must be settled; it cannot be cancelled to evade declared costs.

No-roll actions declare `roll: null`; they can settle directly or request a choice. Outcomes are `success`, `failure`, `mixed`, or `no-check`; their rule-specific meaning remains the adjudicator's responsibility. Publishing a visible consequence is an explicit `fact` effect with its own audience.

## Event contract

Use the existing ledger envelope: `id`, `revision`, `profile`, `input`, `resolution`, `sources`, `changes`. An action transition must be the only top-level change:

```json
{"kind":"action","action":"door-1","step":"roll","data":{}}
```

Every transition has a unique event ID and the latest expected revision. Retry the exact original event to retrieve the original acknowledgement without rerolling or respending. Changing its contents fails. A stale new event fails before randomness is consumed. Read the action at the returned revision when inspecting historical retries: an old acknowledgement does not replace current campaign state.

Declaration data has exactly these fields:

```json
{
  "actor":"pc1", "summary":"检查门闩", "intent":"判断能否打开门",
  "method":"使用工具检查", "stakes":"根据已声明风险由主持人裁定",
  "audience":["pc1"], "roll":{"mode":"tool","expression":"1d100"},
  "costs":[]
}
```

Wait data: `{"actor":"pc1","prompt":"是否继续？","options":{"continue":"继续","stop":"停止"}}`.
Choose data: `{"actor":"pc1","option":"continue"}`. Choices record decisions; they do not automatically determine rule effects. The operator must adjudicate the selected option before settling.

Settlement data: `{"outcome":"failure","effects":[{"kind":"resource","actor":"pc1","resource":"hp","delta":-1}]}`.
Allowed effects are existing ledger `resource`, `resize`, `conditions`, `fact` and `clock` operations, plus `combat_effect` for atomic timed-effect addition/removal. Combat turn advancement cannot be embedded in a settlement. Invalid effects roll back both resource changes and action completion. Internal `private`, `pending`, `restore` and nested actions cannot be smuggled into settlement effects.

Declared costs are negative `resource` changes. New declarations reserve them immediately without reducing the current value; settlement releases the hold and spends them once, whether the attempt succeeds or fails. Do not repeat costs in `effects`. Availability is current value minus holds across all unfinished reserved actions. Other declarations, direct resource changes and capacity reductions cannot consume held capacity. Validation happens in the same transaction as the changes.

Cancel before rolling to release the hold with no spend. For a forced loss or other explicit adjudication, use `release` with `{"reason":"..."}` before changing resources, and use `reserve` to reacquire a hold when appropriate. Releasing a hold does not erase the declared cost: roll and settlement still require affordability, accounting for other actions' holds. No automatic refund or intermediate-stage payment is inferred.

Old saved actions without a `reserved` flag remain unreserved; they are never silently migrated into holds. Use an explicit `reserve` transition to adopt the new behavior for an old pending action. Terminal actions do not hold resources. Private GM views show all resource availability; player views show only the requested actor's current/reserved/available counters, without revealing another action's internal details.

To bind an action (including an adjudicated reaction) to the current encounter turn, add `"timing":{"encounter":"fight-1","turn":1}` to its declaration. The encounter must be active and the acting character must participate; reactions may belong to a different actor than the turn owner. Unfinished timed actions block turn end and encounter finish. See [combat boundaries](combat-timing.md).


## Dice modes

`tool`: one bounded expression using the existing Dice expression engine. Actual OS dice and evidence are committed inside the ledger transaction. Repeat-expression syntax (`count#expression`) is not supported in this action version; a single expression can contain multiple dice.

`manual`: declaration uses `{"mode":"manual","expression":"1d100"}`. Roll data supplies `{"total":42,"note":"Player reports physical dice"}`. This is unverified testimony, not tool-generated randomness or automatic proof that the expression was evaluated correctly.

`receipt`: bind the source before importing:

```json
{
  "mode":"receipt", "expression":"1d6",
  "source":{
    "database":"C:/private-campaign/dice.sqlite",
    "scope":"table-1", "actor":"dice-player-id", "operation":"roll-17"
  }
}
```

The source actor may differ from the campaign actor; the declaration is the explicit local mapping. Only committed `.r` / `.rh` raw expression receipts are accepted. The expression must match exactly and use explicit die sizes. Source database reads are read-only; import never rerolls, modifies Dice resources or executes commands. The original audience and request/response hashes are retained. One receipt cannot be consumed by multiple actions in the active branch, including a copied database with the same roll event ID. A missing receipt leaves the action unchanged so it can resume after Dice commits.

The bridge intentionally refuses `.sc`, `.en`, card updates and other commands with side effects. CoC checks, opposed rolls and special pools still require their existing procedures; this release links raw dice evidence and explicit adjudication, not every legacy command. Stored database receipts are trusted local evidence, not cryptographic proof against a malicious database editor.

## Views and recovery

```powershell
python -X utf8 scripts/actions.py '<campaign.sqlite>' apply --event '<event.json>'
python -X utf8 scripts/actions.py '<campaign.sqlite>' view --player pc1
python -X utf8 scripts/actions.py '<campaign.sqlite>' view --private-output '<new-private-file.json>'
```

Apply stdout contains only the standard ledger acknowledgement. Default/player views contain only authorized action summaries and statuses. Only the waiting decision actor sees their prompt/options. Full intentions, stakes, dice evidence, original receipt audiences and internal history stay in explicit private GM output; a public action summary does not publish its dice evidence. Existing identical private output can be retried; different content is never overwritten.

`session.py view` includes the same filtered action view. GM `session_review.py` adds unfinished actions to `next_prep.pending_actions`, including whom a decision is waiting for. Restore follows the existing explicit branch semantics: action state and resources rewind together; old events remain in history. Reusing the old event ID only acknowledges the old event, so a deliberate alternative branch uses new event IDs.

## Executed acceptance

Run `python -X utf8 -m unittest discover -s scripts -p "test_*.py"` and:

```powershell
python -X utf8 scripts/replay_action_acceptance.py --output '<new-private-directory>'
```

The walkthrough uses actual OS randomness, scripted synthetic choices, five action transitions, a private Dice receipt, fresh-process recovery while waiting, identical retries, single resource expenditure and player projection checks. It writes replayable event JSON and separate player/GM files outside the repository. Its original demonstration procedure is not CoC or D&D rules.

Twenty new tests exercise concurrency, stale/profile rejection before rolling, failed settlement rollback, cold recovery, receipt provenance and deduplication, private views, manual evidence, branch restore and preservation of unrelated campaign state. See [validation](validation.md) for the complete run.

## Imported stat reference

An action declaration may include `stat_ref: {"actor":"pc3","stat":"Spot Hidden"}`. The [character importer](character-import.md) resolves a canonical ID and freezes its value plus sheet event in private action state. This records the declared basis without automatically adjudicating the result.

An `investigation_effect` with step `discover` may be included in settlement for atomic clue delivery and resource spending. See [investigation runtime](investigation-runtime.md); other investigation steps are not inline action effects.

Exploration settlements may include `exploration_effect` steps `advance` or `ack`; see [exploration time and supplies](exploration.md). Declare each expense once: if it is already an action cost, use empty activity costs. Time advancement requires all other actions resolved and the encounter finished. Reminder acknowledgement and explicit consequences commit atomically.

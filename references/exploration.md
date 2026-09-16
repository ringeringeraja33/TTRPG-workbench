# Exploration time, supplies and reminders

`scripts/exploration.py` stores explicit exploration activities and game-time reminders in the campaign ledger. Time uses the existing `state.clock` integer minute count. Supply balances remain actor resources. This is a trusted local operator interface; actor IDs and audiences are projection filters, not authentication.

## Commands

```powershell
python scripts/exploration.py campaign.sqlite preview --event exploration-event.json --private-output gm-preview.json
python scripts/exploration.py campaign.sqlite apply --event exploration-event.json
python scripts/exploration.py campaign.sqlite view --player pc1
python scripts/exploration.py campaign.sqlite view --private-output gm-exploration.json
```

Use the ordinary session event envelope: unique `id`, current `revision`, locked `profile`, `input`, explicit `resolution`, `sources`, and one `changes` entry. Each entry has `kind: "exploration"`, `step` and `data`. Private output uses exclusive file creation; identical output retries are safe.

| Step | Exact data fields | Behavior |
|---|---|---|
| setup | audience | Configure once; keep existing campaign time. |
| advance | minutes, participants, summary, costs, audience | Advance 1–10080 minutes and deduct explicit costs atomically. Participants are distinct existing actor IDs. |
| schedule | id, label, audience, due, every, blocking | Unique reminder ID, absolute current/future minute, interval 0 for one-shot or positive for recurrence, boolean blocking. |
| reschedule | id, due, every, reason | Change a pending reminder, retaining its ID and acknowledgement history; due/closed reminders must be resolved first. |
| ack | id, resolution | Explicitly resolve one due occurrence. |
| cancel | id, reason | Close a pending/due reminder without refunding earlier activities. |

Example `changes` entry after setup:

```json
{"kind":"exploration","step":"advance","data":{"minutes":10,"participants":["pc1"],"summary":"Search the storeroom","costs":[{"kind":"resource","actor":"pc1","resource":"supplies","delta":-1}],"audience":["all"]}}
```

This is an original example, not a rule-derived search duration or supply rate. The actor must already have a `supplies` resource. Costs must be negative resource deltas belonging to participants; duplicate lines are totalled for affordability and existing action reservations are respected. Failed events roll back time, resources, activity receipts and reminder status. Identical event retries do not spend twice.

## Boundaries and explicit consequences

A blocking reminder permits reaching its exact deadline but prevents crossing it until acknowledged or cancelled. Split an activity at that boundary and adjudicate the costs for each segment; the tool does not prorate supplies. Existing `clock` changes also honor these boundaries once exploration is configured. Nonblocking reminders can become overdue. A recurring acknowledgement advances from the original due minute, and remains due if another occurrence is already overdue. Each occurrence requires an explicit acknowledgement.

Acknowledgement alone does not damage actors, refill resources or advance time. An action settlement may include `exploration_effect` with `step: "ack"` alongside explicit consequences. It may also include `step: "advance"` alongside the action result. Avoid double charging: when the action already declares the expense, use an empty activity `costs` list. An invalid consequence rolls back the action and acknowledgement together.

The shared clock cannot advance while an encounter is unfinished or any action remains pending. The settling action becomes terminal before its time effect is checked; other unresolved actions still block it. Independent party timelines and combat-round conversion are not implemented. Without exploration setup, legacy clock events retain their existing behavior.

## Recovery and visibility

Reopening the database restores activity history, deadlines and acknowledgements. GM recap includes due reminders and the nearest blocking deadline. Player output requires both store-level and record-level audience visibility and exposes only activity summary/interval and active reminder label/deadline/status. Supply costs, private acknowledgement text and participant lists remain in the GM record. The campaign minute itself is shared, not a secret clock. Restore reverts time, supply balances and reminders together while retaining ledger history.

These are in-game reminders checked on ledger operations, not operating-system notifications. Travel pace, encumbrance, weather, encounter frequency, survival checks and rest recovery require explicit edition-specific adjudication. No automatic real-time scheduler, resource consumption rate or full downtime economy is provided.

## Preview and verification

`preview` uses a consistent SQLite backup in a temporary directory, applies the exact exploration event there and removes the copy afterwards. Its private result includes the unchanged input event, base revision, before/after minutes, resource balances that would change, and resulting reminders. It never rolls dice or runs arbitrary action events. Apply the original event file to commit; any intervening change makes a new event stale, so preview again against the current revision. Re-previewing an already committed identical event reports a duplicate without another cost. Preview output can contain GM secrets and therefore requires a private output file.

Rescheduling applies only while a reminder is pending. Its new deadline may equal the current minute (immediately due), but cannot be in the past. It retains previous acknowledgements; the explicit reason and prior deadline remain in ledger history. A recurring reminder uses the new deadline and interval as its anchor. Inline action effects cannot reschedule reminders.

Stored activity intervals, participant references, historical cost records, reminder status and acknowledgement times are validated on initialization and transitions. Historical spending is checked structurally without requiring today's balance to cover old costs again.

Run `python -X utf8 scripts/replay_exploration_acceptance.py --output <new-directory>` for the original eight-transition walkthrough. It checks preview isolation, duplicate submission, recovery in a fresh Python process, blocking deadlines, rescheduling, action cost/time settlement, exhausted supplies and private projections. These timings and costs are original fixtures, not system rules.

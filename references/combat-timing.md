# Encounter boundaries, reservations and timed effects

Use `scripts/combat.py` with the existing campaign ledger. This is a rule-profile-bound timing tool: the operator supplies order, refresh policy and expiry boundaries with the existing event source citations. No D&D/CoC rule, reaction eligibility or spell legality is silently inferred.

## Start and advance

Use the standard ledger event envelope with exactly one combat change:

```json
{
  "kind":"combat", "step":"start",
  "data":{
    "id":"fight-1", "audience":["all"], "order":["pc1","npc1"],
    "refresh":[{"actor":"pc1","resource":"reaction","at":"start","value":1}]
  }
}
```

All participants and configured resources must already exist. The example refresh policy is an explicitly chosen table procedure, not a claim that it applies to every system. Each rule sets one resource to the supplied value at that actor's `start` or `end` boundary. Duplicate rules for the same resource/boundary are rejected. Values must fit resource capacity.

Starting creates round 1, turn 1 and immediately runs the first actor's start boundary. `end_turn` with empty data runs the current actor's end boundary and changes phase to `ended`. `next_turn` with empty data selects the first eligible actor in the current order and increments the absolute turn number. An actor whose turn already started, or whose participation is deferred to the next round, is ineligible for the rest of this round. When no active participant is eligible, increment the round, clear round eligibility records and start the first actor in the current order. No silent combined skip occurs. Identical event retries do not run boundaries twice.

`finish` takes `{"reason":"..."}`. It finishes the encounter and expires its remaining encounter-scoped effects without inventing end-turn refreshes. A subsequent encounter needs a new ID; IDs from previously completed encounters are retained to prevent ambiguous reuse. The runtime supports one encounter at a time with explicit joining, leaving and reordering. Simultaneous turns and multiple concurrent encounters remain future extensions.

## Joining, leaving and order changes

All changes use the same sourced, revision-checked event envelope. Each adjustment requires an explicit reason. The current actor, absolute turn number and boundary counters remain unchanged by roster adjustments; only `end_turn` / `next_turn` run boundaries.

- `join`: `{"actor":"pc3","position":0,"participation":"this-round","refresh":[],"reason":"Reinforcements arrive"}`. Positions are zero-based insertion positions. The actor must already exist in the campaign and be outside the active encounter order. Use `next-round` to defer the first eligible turn. Joining does not grant an immediate refresh or interrupt the current actor. Specify that actor's refresh rules explicitly; old rules are not silently reinstated.
- `reorder`: `{"order":["pc2","pc1","pc3"],"reason":"Revised initiative ruling"}`. Supply every active participant exactly once. Started turns remain used this round, so moving an actor cannot give it another turn. The new order controls the remaining eligible turns and subsequent rounds.
- `leave`: `{"actor":"pc2","reason":"Retreat"}`. End an actor's active turn first. Resolve its unfinished actions, outstanding cost obligations or pending choices first. If any active effect targets the actor or expires on its future boundary, explicitly remove or retime the effect before leaving. Use `finish` rather than removing the final participant.
- `retime_effect`: `{"id":"ward-1","expires":{"actor":"pc1","at":"end","occurrence":2},"reason":"Explicit revised duration ruling"}`. The new boundary must be in the future and belong to a current participant. This changes only the expiry rule, not targets or stacking. It is a sourced GM adjustment, not an automatic interpretation of a rule.

Departed actors retain historical boundary counts and effect references but are removed from the active order and refresh policy. Rejoining preserves their counters and round eligibility; leave-and-rejoin cannot create a second turn in the same round. An actor that had not yet taken a turn and was not deferred may still participate that round when explicitly rejoined with `this-round`.

When the most recently ended actor leaves, its historical identity remains recorded even though it has no active-order index. Advancing selects the next eligible actor without skipping one. Hidden participants stay filtered out of player order and effect views. All roster changes, reasons and source citations remain in ledger events; restore rewinds membership, eligibility and counters together.

## Effects and exact boundaries

Add an effect with `step: add_effect`:

```json
{
  "id":"ward-1", "label":"防护", "targets":["pc1"], "audience":["pc1"],
  "expires":{"actor":"pc1","at":"start","occurrence":2}
}
```

The example expires at pc1's second start boundary in this encounter. If pc1 has already started once, that is their next turn start. Another creature's next end boundary is represented by its own actor, `end`, and the next occurrence count. The private GM view exposes counters so the operator can choose the correct future occurrence. Past or current already-fired boundaries are rejected.

Each effect has a distinct ID, source citations, creation event and eventual expiry/removal event. Two effects with the same label remain independent. `remove_effect` takes `{"id":"ward-1","reason":"..."}` and records explicit removal. The ledger retains expired records in history.

These effect records do not automatically rewrite actor conditions, combine bonuses, apply recurring damage or infer concentration checks. That avoids erasing a condition from another source or silently deciding stacking. Only encounter-scoped effects belong here; longer-duration campaign effects need their own explicit procedure.

## Atomic action settlement

Declare an action with `timing: {"encounter":"fight-1","turn":1}`. Its actor must participate, but may be an off-turn actor using an explicitly adjudicated reaction. Timed pending actions prevent turn end and encounter finish until settled or cancelled before rolling.

Add a timed effect in the same transaction as action costs:

```json
{
  "kind":"action", "action":"protect-1", "step":"settle",
  "data":{"outcome":"success","effects":[
    {"kind":"combat_effect","step":"add_effect","data":{
      "id":"ward-1","label":"防护","targets":["pc1"],"audience":["pc1"],
      "expires":{"actor":"pc1","at":"start","occurrence":2}
    }}
  ]}
}
```

`combat_effect` permits only `add_effect` and `remove_effect`; it cannot advance a turn. Invalid expiry, malformed effects or insufficient resources roll back the cost and action completion together. New action costs are reserved at declaration; see [action reservations](action-workflow.md).

Refresh policies also respect holds. If a configured reset would reduce a resource below its reserved amount, the entire boundary fails unchanged, including expirations and counters. Resolve the pending action or explicitly release its reservation before proceeding.

## Recovery and private views

```powershell
python -X utf8 scripts/combat.py '<campaign.sqlite>' apply --event '<event.json>'
python -X utf8 scripts/combat.py '<campaign.sqlite>' view --player pc1
python -X utf8 scripts/combat.py '<campaign.sqlite>' view --private-output '<new-private-file.json>'
```

Mutations print only the ledger acknowledgement. Full counters, refresh policies, source citations and hidden participants go to explicit private output. Player views first check encounter audience, then filter actor identities and effects; they never expose hidden turn indexes or expiry triggers. `session.py view` includes the same view, and GM session review includes current timing and active effects for handoff.

Combat state is reserved under `private.combat` (schema 2). Schema 1 fixed-order saves remain readable without mutation. The next successful combat transition upgrades the state atomically, deriving used turns from the prior order through the current index. Failed transitions leave the old snapshot untouched. Restoring an old snapshot remains supported. Ordinary private-state replacement must preserve it. Explicit ledger restore rewinds resources, reservations, turn counters and effects together, preserving old events as branch history. Existing campaigns without combat state remain unchanged.

## Executed checks

Twenty reservation/timing tests cover reservation overbooking/concurrency, explicit release and legacy compatibility, resize protection, private availability, distinct start/end expiry, pending-action gates, atomic cost/effect settlement, refresh rollback, source-preserving cold reads, restore and encounter cleanup.

Run `python -X utf8 scripts/replay_combat_acceptance.py --output '<new-private-directory>'` for a ten-transition synthetic walkthrough. It uses actual OS dice and scripted choices under an original demonstration procedure, recovers in a fresh process while awaiting a choice, spends one reserved resource, expires the effect at the second own-turn start and applies a configured refresh once. No live-player or complete rules-engine claim is made.

Fifteen additional dynamic-order tests cover same/next-round entry, reordering without duplicate turns, leave/rejoin counters, pending-action and effect dependencies, explicit retiming, rollback, retries, hidden participants, fresh-process reads, schema 1 migration and branch restore.

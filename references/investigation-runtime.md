# Investigation at the table

Use `scripts/investigation_runtime.py` to connect the existing declared-dependency audit to the campaign ledger. Available evidence, delivered observations and actor hypotheses are separate states. The tool does not infer fictional truth, player comprehension or acquisition legality.

## Setup and explicit delivery

Start from the [original example plan](../assets/examples/investigation-runtime.json). A standard sourced ledger event uses:

```json
{"kind":"investigation","step":"setup","data":{"plan":{...}}}
```

The plan has exactly `schema: 1`, `evidence` and `conclusions`. Evidence records contain exactly `id`, `text`, `audience`, and boolean `available`; conclusion records contain exactly `id`, `text`, `audience`, boolean `essential`, and `routes`. The combined plan is bounded to 2,000 records. Existing AND/OR routes, ID references and uniqueness checks apply. Unknown fields are rejected.

Setup is allowed once. It stores the GM plan and an empty knowledge ledger. Available evidence is not automatically delivered. Plan `audience` fields are retained for compatibility with the preparation audit, not used as runtime publication or sharing permissions. Every actual delivery needs an explicit recipient list; players only see their acquisition receipts.

`discover` data:

```json
{"evidence":"letter","recipients":["pc1"],"method":"Explicit inspection of the envelope"}
```

The clue must currently be available. Recipients must be distinct existing campaign actor IDs. `all`, unknown IDs and string-valued recipient lists are rejected, preventing accidental publication to future characters. The operator must adjudicate the fictional acquisition before calling this operation. Method and event source citations record that adjudication; the tool does not decide whether a search succeeds.

`share` data:

```json
{"evidence":"letter","sender":"pc1","recipients":["pc2"],"method":"Read the letter together after reuniting"}
```

The sender must already know the evidence. This explicitly expands knowledge to the named recipients without sharing the original GM record. The tool does not infer whether separated characters can communicate; the operator supplies a valid method. Later characters do not inherit previous recipients' knowledge automatically.

`available` takes `{"evidence":"key","available":true,"reason":"The locked drawer is now accessible"}`. Unavailable evidence cannot be newly discovered. Making a clue unavailable never erases previous observations, and an informed actor can still communicate the saved observation from memory. Availability is an acquisition flag, not a truth or memory flag.

## Hypotheses and explicit verdicts

`hypothesize` data:

```json
{"id":"theory-1","actor":"pc1","text":"The sender visited the warehouse","evidence":["letter"]}
```

Supporting evidence must already be known to that actor. An empty list is allowed for an explicitly unsupported speculation. Hypotheses are visible only to their owner and the GM, separate from observations and campaign facts.

`resolve` takes `id`, `status` (`confirmed` or `refuted`), `public_resolution`, and `gm_reason`. The former explanation is delivered only to the hypothesis owner; the latter stays GM-only. A verdict is an explicit sourced operator decision, not a result inferred from the dependency graph. It does not append or rewrite world facts. Record any separately established public fact through an explicit ledger fact event.

Resolved hypotheses cannot be silently rewritten. Use the ledger's explicit restore procedure for corrections. This release does not yet provide shared hypothesis boards, hypothesis revision threads, or automatic reconciliation of contradictory observations.

## Atomic acquisition and action costs

An action settlement can include:

```json
{
  "kind":"investigation_effect","step":"discover",
  "data":{"evidence":"letter","recipients":["pc1"],"method":"Successful adjudicated inspection"}
}
```

Discovery, action completion and resource costs commit together. An unavailable clue, bad recipient or other invalid effect rolls back the entire settlement. Inline effects cannot set up the investigation, alter availability or resolve a hypothesis. An identical event retry does not deliver or spend twice; a new intentional rediscovery records another receipt without duplicating the displayed evidence.

## Views, analysis and recovery

```powershell
python -X utf8 scripts/investigation_runtime.py '<campaign.sqlite>' apply --event '<event.json>'
python -X utf8 scripts/investigation_runtime.py '<campaign.sqlite>' view --player pc1
python -X utf8 scripts/investigation_runtime.py '<campaign.sqlite>' view --private-output '<new-private-file.json>'
```

Default view has no implicit party audience. Player views whitelist delivered evidence ID/text and owned hypothesis fields. They never expose GM conclusion text, routes, undiscovered clues, GM verdict reasons or internal histories. The full plan and analysis require explicit private output; stdout then contains only revision and a save acknowledgement. All interfaces follow the existing trusted-local-operator model rather than authenticating actor IDs.

GM analysis reports preparation availability separately from actual knowledge per actor. For actual knowledge, previously delivered observations remain usable even if the original clue is now unavailable. Derivable conclusions mean only that declared dependencies are satisfied; they are neither automatically discovered nor proven true. Results remain GM-only to avoid revealing solution structure.

`session.py view` includes the filtered investigation view. Player session recaps include their current observations and hypotheses; these are current snapshots rather than changes filtered by `since`. GM next-preparation reports include availability, per-actor dependency support and open hypotheses.

State is reserved under `private.investigation`, schema 1. Generic private replacement cannot overwrite it. Ledger restore rewinds acquisition receipts, availability and hypotheses together with other campaign state; existing unrelated pending rulings remain intact.

## Verification

The original thirteen tests cover setup without revelation, split-party knowledge, sender validation, unavailable/disappearing evidence, GM-only derivability, owned hypotheses, explicit verdict privacy, atomic cost/discovery, invalid input, private cold recovery, recap and restore. The module is a structured runtime for recorded play, not a complete mystery-solving or GM engine.

## Extend a running investigation

An `extend` step atomically appends evidence, conclusions and alternative routes. It requires exactly `evidence`, `conclusions`, `routes` and a nonempty `reason`:

```json
{
  "kind": "investigation",
  "step": "extend",
  "data": {
    "evidence": [{"id":"witness","text":"The witness disputes the note date","audience":["all"],"available":true}],
    "conclusions": [],
    "routes": [{"conclusion":"destination","route":["witness"]}],
    "reason": "The party arranged an additional interview"
  }
}
```

`destination` must be an existing conclusion or one supplied in this batch. New conclusion records have the same shape as setup records and can reference new evidence and conclusions in the batch. Each route is a nonempty AND group; adding a route supplies an OR alternative, preserving prior routes. Duplicate IDs across evidence/conclusions, duplicate alternative routes (including reordered AND groups), unknown dependencies, empty extensions and plans exceeding 2,000 total records are rejected. Cyclic dependencies remain a GM audit issue; the tool does not invent supporting evidence to make them derivable.

An invalid part rolls back the entire extension. The event records the reason, sources and revision. Identical retries append nothing twice; stale new events must be rebuilt against the latest revision. Plan changes remain GM-only and do not deliver clues, alter receipts, decide hypotheses or publish conclusions. New available clues can subsequently be discovered through the normal explicit delivery or atomic action settlement.

`edit_unseen` takes exactly `evidence`, `text`, and `reason`. It updates the prepared text only if no actor has ever acquired that evidence in the current branch. It preserves the ID, audience and availability. Once acquired, even if later destroyed or unavailable, evidence text cannot be rewritten. Add a new evidence ID for a correction, contradiction or later observation, then explicitly deliver it. Old observations and hypotheses remain intact; adjudicate any revised theory separately.

Neither extension nor unseen editing is permitted as an inline action effect. The preparation audit immediately uses the expanded graph; per-actor audit still seeds only acquired evidence. Restore rewinds the plan and acquired knowledge together, preserving the ledger history.

Fourteen additional tests cover extension atomicity, record limits, alternate routes, duplicate/stale requests, unseen editing, immutable acquired evidence, hypothesis preservation, action acquisition, cold recovery and restore. Run `python -X utf8 scripts/replay_investigation_acceptance.py --output <new-directory>` for the original seven-transition extension/recovery example. Its fictional content is a test fixture, not a published scenario or live-player evaluation.

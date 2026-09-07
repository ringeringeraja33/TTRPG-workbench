# Session review and next preparation

Use `scripts/session_review.py` on an existing private `session.py` SQLite ledger. It opens the database read-only and derives the active history through restore events. It never edits state or invents missing play.

```powershell
python -X utf8 scripts/session_review.py '<private>/campaign.sqlite' --gm
python -X utf8 scripts/session_review.py '<private>/campaign.sqlite' --since 10 --gm
python -X utf8 scripts/session_review.py '<private>/campaign.sqlite' --player pc1
```

Default output is public. `--gm` and `--player` are mutually exclusive. `--since` is an inclusive revision filter on facts/events; actor resources and conditions always reflect current state. Revision 0 means initial configuration. Event IDs and rule sources appear only in GM output because their names may themselves contain secrets.

## Evidence-backed recap

- `recorded_facts` contains currently retained facts visible to the selected audience, with the earliest matching revision on the active branch. Restored-away facts and event narratives do not reappear as current history. A later restore back to an earlier abandoned branch correctly reinstates that branch.
- Public output excludes complete event input/resolution, private state, pending rulings, hidden actor IDs, fact IDs and audience metadata. Write a player narrative only from this export, preserving uncertainty in the fact text.
- GM output adds active events with their actual inputs, outcomes and cited sources, current pending rulings, and superseded revision numbers. Use these to explain corrections without retelling abandoned events as actual play.
- `state_source_revision` identifies the authoritative snapshot for pending items and preparation categories. Category strings are explicitly recorded notes, not independently verified claims or automatically extracted beliefs.

## Preparation notes

Optionally store the following within the existing `private` object, preserving its other keys. Read the latest state before submitting the normal sourced `private` event; its replacement semantics are unchanged.

```json
{"review": {
  "player_hypotheses": ["pc1 suspects the ferryman; stated at revision 8, unconfirmed."],
  "gm_plans": ["If the alarm is raised, the warehouse keeper will leave; not yet triggered."],
  "character_hooks": ["pc2 promised to return the borrowed lantern."]
}}
```

These fields are lists of strings. Missing fields produce empty lists, never inferred contents. `next_prep` collects pending rulings, character hooks, unrealized plans and hypotheses to verify. It is a preparation checklist, not permission to trigger plans or alter player beliefs. Review its currency at session end; stale plans stay marked as plans until updated.

For the next session, read this GM review, the current authoritative state and relevant scene preparation. Select the next actionable situation and the materials it requires. Use the investigation audit to check outstanding evidence routes; reconcile IDs manually where the documents use different identifiers. This release does not introduce a unified campaign schema or an automatic cross-file merge.

Save generated JSON as explicit UTF-8 in the appropriate private/player directory and read it back before release. Do not give players the database or GM report.

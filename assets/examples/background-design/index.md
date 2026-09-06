# Background-driven design examples

Three original extensions of the existing historical creation fixtures. Reusing their complete cards keeps one authoritative allocation ledger. All six characters remain proposed fixture characters, not approved real campaign identities. No private user lore is included.

| Setting | Player materials | GM scenes, source limits and ideas | Checked data |
|---|---|---|---|
| c.1000 monastery / ambiguous folk horror | [Player](monastery/player.md) | [GM](monastery/gm.md) | [Pack](monastery/pack.json) |
| 1884 Colorado railway / procedural pursuit | [Player](railway/player.md) | [GM](railway/gm.md) | [Pack](railway/pack.json) |
| 1925 New York harbor / social noir | [Player](harbor/player.md) | [GM](harbor/gm.md) | [Pack](harbor/pack.json) |

Each has two complete linked builds, four selected skill applications, three operational item allocations, three linked scenes and three expansion directions. The ordinary route remains available without specialized skills or items; it sacrifices time and precision. These are original scenario guarantees, not general CoC rules. `pack.json` and GM files contain synthetic spoilers; `player.json` is the checked public projection.

From the skill root: `python -X utf8 scripts/background_design.py assets/examples/background-design/monastery/pack.json --chargen assets/examples/background-chargen/monastery/spec.json`. Repeat for railway/harbor; add `--player` for public fields. Automated tests exercise broken evidence, budgets, versions, items, routes and projections. Historical interpretation and clue semantics remain reviewed prose, not an automated historical certification.

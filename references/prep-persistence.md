# Persistent investigation preparation

Adapted from Sue's `coc-kp-host/references/prep_persistence.md`, commit `9fedf60613b5f4c599a4128f6ce1d5da5bfebaaf`, under MIT. The adaptation adds event-ledger integration, explicit audience IDs and source provenance. See [notices](../THIRD_PARTY_NOTICES.md).

Create a private campaign directory with separate `gm/`, `originals/`, `players/`, `characters/`, `sessions/` and `rules/` areas. The public skill repository is not a campaign storage location. Preserve supplied originals; extract searchable text beside the private originals and record extraction limitations. Do not copy an entire source scenario into a player handout.

Build the GM frame before the opening scene: premise, actual timeline, scene IDs, NPC goals and knowledge, clue dependencies, handout identifiers, timed triggers, hazards and plausible endings. Attach source pages to canonical facts. Mark additions as GM design. Keep flavor samples brief and spoiler-safe. If a PDF has unreliable text order, inspect the rendered page before using a clue or stat block.

Create separate durable character records, including NPC allies. Audit equipment ownership, ammunition, carried weight where applicable, consumables, money and borrowed items. Do not turn a provisional equipment list into confirmed inventory without a ruling.

For every active scene record: who is present, what each participant can perceive, what facts have actually been discovered, unresolved choices, and the next trigger. Use explicit player IDs for split-party facts. Apply resources and audience-labelled facts in one `session.py` transaction. At a pause, save revision and the last accepted operation ID, pending questions and the next player's opportunity to act.

Use `campaign_check.py` for declared graph references, unreachable locations, duplicate clues and a reachable exit. Its graph edges represent possible paths, not proven player knowledge. Manually check that essential clues have alternate acquisition routes, failures change the situation, and a player-facing export reveals neither GM notes nor undiscovered destination IDs. The optional clue projection is suitable only when every field of each visible clue is itself public.

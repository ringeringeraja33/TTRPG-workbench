# Prepare, design and write with mixed local materials

Use this after identifying the active system with [corpus adapters](systems/corpus-adapters.md). The workflow is independently written; source modules, handout text and illustrations stay in the private library. The source matrix distinguishes what was actually inspected from what is merely searchable.

## Build a runnable adventure dossier

Read the adventure's introduction, Keeper truth, setting, cast, locations, timeline, endings, pregenerated characters and all appendices. Compare separate PDF/DOCX versions rather than assuming the DOCX is a faithful transcription: a shorter version may be preparation notes with altered chronology or rules. Bind the chosen version by hash and list deliberate changes in the private dossier.

Produce these connected records, using the existing [persistent preparation](prep-persistence.md) and [adventure procedure](adventures.md):

| Record | Operational contents |
|---|---|
| Campaign truth | What actually happened, who knows it, dated events, and facts still chosen by the Keeper |
| Player premise | Why these characters participate, public setting, allowed character options and expectations |
| Cast | Motive, resources, knowledge, false beliefs, relationships, pressure response and current location |
| Locations | Entry routes, immediate impressions, interactive objects, clue access, hazards and exits |
| Clues | Exact fact, source, relevant ability/action, prerequisite, delivery state and alternative route |
| Pressure | Trigger, time unit, escalation, interruption, who can observe it, and consequences of inaction |
| Ending | Several possible resolved states; unresolved threats and links to the next adventure |
| Recovery | Current scene/time, separated parties, disclosed facts, expended assets, pending decisions and next trigger |

For an open investigation, choose mutable background facts before the players encounter dependent evidence. Do not move the culprit or rewrite prior facts in response to a successful deduction. For a memory-fracture premise, keep three separate tracks: established events, each character's reported memory, and what each player has received. A discrepancy can be deliberate fiction; a bookkeeping error cannot be justified after the fact as unreliable narration.

Treat independent historical notes as research candidates. A glossary may mix actual religion, an author's interpretation and invented supernatural lore. A contemporary photo can supply atmosphere without proving what a street looked like decades earlier. Use the [background design workflow](background-design.md) when the task needs verified period skills, equipment or institutions.

## Assemble and reveal handouts

An image collection is part of the module, not decoration to publish all at once. Compare every variant visually. A clean floor plan, a numbered plan and a fully keyed plan may share almost the same filename. An NPC portrait, an in-world report and a monster illustration need different disclosure triggers. Images with no OCR text still need visual review; OCR cannot identify spoiler-free artwork.

Keep a private manifest with stable IDs, a neutral player title, the reviewed asset hash, GM-only source notes, available variants, recipients, reveal prerequisites and release state. Use the [original example manifest](../assets/examples/corpus/handouts.json) and:

```powershell
python -X utf8 scripts/handout_manifest.py "<private-manifest.json>" --root "<asset-root>"
python -X utf8 scripts/handout_manifest.py "<private-manifest.json>" --root "<asset-root>" --player "pc1" --output "<private-player-output.json>"
```

The projector returns only released player titles/text for that recipient; it does not copy images or publish messages. After review, select the approved image separately if it is needed. GM filenames, hidden variants and prerequisite facts are excluded from player JSON. The validator rejects an unreviewed or GM-only selected player variant, an unmet trigger, a changed asset hash and an out-of-root file. It cannot detect spoilers that an editor mistakenly marked player-safe.

In the session ledger, record the handout ID, approved variant/hash, recipient and reveal event. Resume from the release record so a player neither loses an already delivered clue nor receives another party's secrets. Keep the original file unchanged when making a cropped or redacted working copy, and review that copy independently.

## Convert character background into playable hooks

The corpus's character-question book supplies a local question bank, not a requirement to answer hundreds of prompts. Use a few relevant prompts at the point they change a decision. Record each answer as a playable element: an obligation, contact, valued possession, contradiction, skill history, fear boundary or current aim.

For example, an original character who maintains a failing lighthouse might produce: a repair skill justified by past work; a debt to the supply clerk; a personally valuable tool; a conflict between family duty and travel; and a scene in which weather delays supplies. The selected game still determines skill names and points. Do not turn biographical prose into unearned mechanical bonuses.

The skill quick-reference booklet and 1920s pocket-item list are discovery aids. For each proposed skill, state what information/action it enables, what overlaps with another skill and which native skill buys it. For an item, establish period, location, accessibility, cost basis, weight/encumbrance, use, limits and recharge/replacement. A book's listed historical price is not automatically the price in another country or decade. Keep speculative availability separate from rule legality.

Ensure unusual purchased skills have meaningful opportunities during play. Design an opportunity with a real decision and consequence; avoid giving every specialist a mandatory spotlight roll that cannot affect anything. See [background-aware creation](background-chargen.md) for budget checks and [background design](background-design.md) for skills/items/scenes as one pack.

## Use GM guides and monster books as design references

The two local fifth-edition DMG PDFs have different page counts and page offsets. They cover world building, factions, adventure structure, NPCs, environments, treasure and optional construction rules. Read the selected file's actual topic instead of transferring a printed-page offset between copies. Their older encounter assumptions do not establish 2024 balance.

For a combat encounter, write the objective and possible noncombat outcomes before selecting opponents. Then record terrain, starting positions, reinforcements, morale/retreat, attack ranges, action economy, status interactions, expected resource pressure and the party's escape route. Check the selected edition's encounter math, then run representative turns. Monster CR alone does not account for a special terrain advantage, surprise, control effects or exhausted characters.

For a creature conversion, preserve a functional brief rather than every number: what it wants, what it threatens, what warning precedes its strongest move, what players can learn, and how they can counter or escape it. Choose target-system statistics from an authorized baseline, label changes as homebrew, and test the resulting action interactions. Keep licensed monster statblocks local.

For treasure or an artifact, distinguish ordinary use from hidden effects, identify costs and counterplay, and specify what inspection reveals. A random table supplies a candidate; the GM remains responsible for its fit with established events. The KP calamity deck's usage note itself cautions against arbitrary mismatched events; do not use a dramatic card to force a character's defeat without the corresponding situation.

## Apply the corpus to original rulebook authoring

Extend [rulebook authoring](rulebook-authoring.md) with the following comparison lenses. Each one creates a concrete chapter dependency or acceptance case:

| Design choice | Compare and resolve |
|---|---|
| Skill architecture | Broad skills vs narrow specializations; universal vs occupation access; base value vs purchased rank vs spendable pool |
| Resource model | Bounded reserve, signed exhaustion track, overflow, separate long-term/short-term currencies; state which domains are legal |
| Action economy | Fixed turn actions, action points, declared timing and interrupts; define costs when cancelled or defeated |
| Advancement | Flat level, increasing XP costs, career permissions, reset-on-promotion level and retained progress |
| Ability construction | Ranked slots or freeform powers; define comparison baselines, stacking, counterplay and the GM approval point |
| Investigation | Information access vs random uncertainty; false clues vs false character beliefs; alternatives after a failed approach |
| Campaign loop | End-of-round, rest, session, scenario and downtime recovery must use different clocks where appropriate |
| Setting mechanics | Fictional infection, bloodline, cognition or supernatural strain must have explicit triggers and observable consequences |

Write an original worked example for every new relationship. Include a case where the tempting borrowed rule fails: using CoC's POW/5 for a fan system's SPI-based MP, refreshing an investigative pool during a rest, treating an archive revision as PF2, or resetting all earned bonuses during promotion. Tie fixes to rule IDs and affected character sheets, examples and quick references. The goal is coherent original rules with citations to design influences, not a collage of incompatible mechanics.

## Dice-bot materials

The tower-dice manual and Dice! 2020 cookbook describe different tools and versions. Before offering a command, identify the actual bot, command prefix, active character binding, rule profile and whether the roll/result is public or private. Read the relevant manual entry, then label historical commands as version-dependent. Do not send commands to a live group or configure a bot unless the user asks.

For imported logs, preserve raw timestamp, speaker, bot identity, expression, result, visibility and character binding. Convert only unambiguous records into proposed session events. Retries or repeated bot replies must not spend a resource twice. Log deletion, group settings and outgoing messages are external actions, not prerequisites for learning a manual. The current skill has a local dice/ledger workflow; it does not claim a tested live integration with these bots.

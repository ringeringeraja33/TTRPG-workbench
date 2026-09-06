# Background-driven skills, items and scene design

Trigger when a user supplies a module's approximate era, place, history or style and wants skills, items, scene materials or design ideas. Extend [background-aware creation](background-chargen.md); do not make the user request browsing separately. Reuse established setting and edition choices. For a small item request deliver the item and relevant evidence; reserve a full pack for a whole-module request.

## Establish and research the design brief

Extract date range, locality, institutions, technology, genre, supernatural access, party activities, session length and player experience. Preserve user canon, including alternate history. Ask only questions that change the direction; label other assumptions as reversible. With no system named compare at most three suitable systems, recommend one and label a provisional version. Never infer percentile budgets for another system.

Search local rules, official editions/supplements and comparable adventures, then historical sources and relevant discussion. Read actual creation instructions, skill lists and pregenerated cards; product summaries cannot establish budgets. Separate skill base, purchased points, final rating, free initial values, occupation discounts, caps and later advancement. A pregen's final ratings do not reveal its purchase ledger.

Research only history that changes play: occupation/training, literacy/languages, tools, transport/communication, institutions, access, supplies and money. Distinguish invention, regional availability and individual access. Avoid demographic competence assumptions. A late-decade device is not automatically available earlier in that decade. Save source author/title/version/locator/access date, read scope and limits in index_root. Distinguish historical fact, unchanged rule, supplement rule, inference and original house rule. Preserve historical differences without replacing the user's alternate history. A blocked source remains blocked; use previously verified evidence with its date/limits or an explicit original allowance, never pretend to have read it now.

## Design skills that earn their place in play

For each selected or changed skill record canonical ID, player-facing name, retain/rename/split/add/remove treatment, application, base, eligible occupation and interest pools, cap, cost and source. Define at least one ordinary use and one limit. A renamed skill retains its numeric rule unless separately changed; do not double-charge the original and its new name. Test which scenes give it a meaningful advantage and which other approaches remain available. History can explain training access; it cannot mathematically prove an arbitrary point bonus.

Use the existing creation profile and two distinct complete builds. Recalculate if a skill or budget changes. Explain how the characters contribute differently; do not require both characters to spend into the same hidden answer. Missing official occupation budgets remain missing; an original occupation must be labelled as such.

## Give items operational definitions

For each item specify: date/locality/access classification, owner or lender, how to obtain it, price basis (sourced price, explicit scenario allocation, or unresolved), quantity/charges, carrying or custody constraints, use procedure, effect, limits, upkeep, replenishment and substitute. Distinguish ownership from skill and institutional permission. Historical plausibility never grants automatic bonus dice, damage, legal authority or magical effects.

Use native system rules for weapons/armor/vehicles and quote the actual version's basis for numerical effects. For an original special item define activation, payment timing, action cost, targets, duration, stacking, failure/interruption and recovery. Explicitly mark original mechanics. Without price evidence use a clearly agreed allocation or leave purchase unresolved. Do not turn a fictional letter into universal access to real police archives. Consumable exhaustion must leave a plausible alternative route where information is essential.

## Plan connected scenes and ideas

Each scene needs: purpose, place and sensory opening, participants with motives/leverage, interactable objects, entry and exit conditions, clues and their meaning, time pressure, success effects, failure consequences and onward destinations. Define what the characters can observe separately from the hidden explanation. Link scenes by evidence, actors, locations or changing circumstances; provide at least three connected scenes for a full example pack.

Offer approaches with different costs and benefits: technical work might preserve precise evidence, negotiation might require a favor, a public physical trace might expose the inquiry. Essential information must not depend on a single successful skill roll or unique item. Do not turn every failed attempt into the same success: change access, delay, evidence quality or who cooperates, and provide a different route. Label guaranteed onward clues as original scenario design, not universal CoC RAW. A graph edge alone does not prove fictional access.

Provide several expansion directions with an actual decision and tradeoff: grounded dispute versus ambiguous haunting, protected witness versus public accusation, short procedural inquiry versus wider faction conflict. Explain which skills/items/scenes change under each variant. Do not silently add supernatural combat statistics or new budgets when changing tone.

## Deliver and validate

Use [the pack template](../assets/templates/background-design.md). Build player materials from explicit public fields: premise, allowed concepts, skill/creation rules, available items and safe starting opportunities. Keep answers, clue destinations, NPC secrets, hidden routes and research rulings in the GM dossier. Do not generate a public file by deleting a few secret headings. Public text still requires semantic review; a whitelist cannot recognize a spoiler already placed in an approved field.

For each pack validate two builds, skill IDs/bases/pools/caps, item availability and price basis, actual skill/item use in scenes, and alternate routes when all special items are absent or risky attempts fail. Check profile conflicts, missing evidence and accidental GM-field projection. Reuse `background_chargen.py` for its declared CoC7 arithmetic only. `background_design.py` checks explicit scene/item links and generates a whitelisted public projection; it does not certify historical truth, semantic clue sufficiency or other systems' arithmetic. Its contract and boundaries are in [the tool specification](background-design-tool.md).

[Three complete extensions](../assets/examples/background-design/index.md) reuse six audited historical characters, add nine connected scenes and original item allocations. Record actual errors, corrections and unresolved source issues. Live-player testing is outside this task's acceptance criteria. Keep original books, downloaded material and user-specific drafts private; distributable examples must be original synthetic material with attribution to comparisons.

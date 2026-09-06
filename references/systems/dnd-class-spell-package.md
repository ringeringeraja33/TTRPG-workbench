# All SRD classes and spells: source-backed operation

Scope: the twelve classes and 339 spell descriptions actually present in the official **SRD 5.2.1**. This does not include every PHB subclass, Artificer, or spells published in other books. Additional books require an explicit edition and source entry; absence from this SRD is not evidence that an option does not exist elsewhere.

## Retrieve complete rules before making the card

`scripts/srd_catalog.py` verifies the PDF's SHA-256, extracts the entire spell-description section, preserves continuation pages, checks unique names and compares the number of parsed spells with independent Casting Time headers. It rejects another printing or changed extraction coverage. Install `requirements.txt`, then run:

```text
python -X utf8 scripts/srd_catalog.py "<official-SRD-5.2.1.pdf>" index
python -X utf8 scripts/srd_catalog.py "<official-SRD-5.2.1.pdf>" class Wizard
python -X utf8 scripts/srd_catalog.py "<official-SRD-5.2.1.pdf>" spell "Counterspell"
```

Names are case-insensitive and repeated spaces are normalized. Spell lookup requires an exact name, so an unknown supplement spell cannot silently resolve to a similarly named spell. Output includes edition, source hash and PDF pages. Class output includes its whole source page range, including tables and spell lists; boundary pages may contain the preceding/following class. A parsed paragraph is source text, not an automatic ruling. Inspect PDF tables visually if text order makes a row ambiguous.

## Class routing and build obligations

These source ranges include the available subclass. For every new level read the feature-table row and all newly granted feature paragraphs, and record every required choice. Do not use this routing table as a substitute for those paragraphs.

| Class | PDF pages | Primary ability / Hit Die | Required state to extract from current-level features |
|---|---|---|---|
| Barbarian | 28–30 | STR / d12 | Rage uses and duration, damage bonus, armor formula, mastery, Berserker triggers |
| Bard | 31–35 | CHA / d8 | Inspiration die/uses/recovery, expertise, spells, Lore choices |
| Cleric | 36–40 | WIS / d8 | Divine Order, Channel Divinity, prepared/domain spells, healing modifiers |
| Druid | 41–46 | WIS / d8 | Primal Order, Wild Shape uses/known forms/restrictions, spell and Land choices |
| Fighter | 47–49 | STR or DEX / d10 | Mastery, fighting style, Second Wind, Action Surge, Champion features |
| Monk | 49–52 | DEX and WIS / d8 | Martial Arts die, Focus Points, action/bonus-action costs, movement, deflection |
| Paladin | 53–57 | STR and CHA / d10 | Lay on Hands, slots, smite action and free use, aura range, oath abilities |
| Ranger | 57–61 | DEX and WIS / d10 | Hunter's Mark free uses and concentration, spells, expertise, Hunter choices |
| Rogue | 61–64 | DEX / d8 | Expertise, Sneak Attack prerequisites/dice, Cunning Strike costs, Thief exceptions |
| Sorcerer | 64–70 | CHA / d6 | Sorcery Points, conversion costs, Metamagic, Innate Sorcery and Draconic features |
| Warlock | 70–76 | CHA / d8 | Pact Magic pool, Invocations and prerequisites, Arcanum, Fiend features |
| Wizard | 77–82 | INT / d6 | Spellbook versus prepared spells, copying costs, ritual access, recovery, Evoker features |

Build the character in an ordered ledger: class order and level; background, species and language choices; attributes; starting-class proficiencies; skills/expertise; features and selections; equipment with weight/ownership; derived defenses, HP, attacks and saves; then spellcasting. Multiclass entry grants only the proficiencies listed under that class's multiclass paragraph. Current and new classes must meet their primary-ability prerequisites (13); Fighter allows either listed ability, while the paired requirements need both. Avoid adding the full starting equipment or saving-throw proficiencies for each class.

`class_magic.fixed_hp` handles fixed post-first-level HP and retroactive CON changes for the base classes. First class Fighter then two Wizard levels with CON +2 gives 24 HP; starting Wizard before Fighter/Wizard gives 22. It does not include feats, species, subclass bonuses or rolled HP. Apply those separately, retaining their source. `session.resize` changes the verified maximum without automatically refreshing other resources.

## Multiclass spells: three separate calculations

1. Determine prepared/known spells and cantrips separately for each class at its own level, including explicit always-prepared exceptions. Label the casting ability for each spell.
2. When two or more classes grant Spellcasting, use SRD PDF25–26: full Bard/Cleric/Druid/Sorcerer/Wizard levels plus half Paladin/Ranger levels, rounding each class up. `class_magic.multiclass_slots` returns the nine-level slot vector. Ranger4/Sorcerer3 has effective caster level5: 4/3/2 slots. This grants no automatic access to level3 prepared spells. Paladin3/Ranger3 contributes 2+2, not 3.
3. Keep Warlock Pact Magic and Mystic Arcanum separate. Use the source's cross-use permission for Pact Magic slots; do not add Warlock levels to the multiclass Spellcasting level or refresh both pools on a Short Rest. If only one class grants Spellcasting, use that class's own slot table.

Extra Attack features do not add together, and alternative base AC formulas are alternatives. Spell preparation counts come from each class's current table and feature text, not a memorized 2014 ability-plus-level formula.

## Spell execution card and settlement

Read the complete retrieved entry. Record: version/name; class or feature granting access; level; casting time and trigger; range, target and visibility; V/S/M and whether M is costly/consumed; duration/concentration; attack/save and success/failure effects; damage/healing; upcast/cantrip scaling; repeat triggers; ending conditions and exceptions. Record a source page for each disputed value.

Before committing: verify target/range, action availability, components, concentration changes and this turn's slot expenditure. Resolve interrupts, then commit actual costs and outcomes once. Effects recurring on entry, turn start or turn end need a trigger identifier and per-target history; do not deal their damage again merely because a player repeats the description.

Useful regression cards, checked against the extracted 5.2.1 entries:

- **Counterspell:** the caster makes a CON save. Failure wastes the casting action but does not expend that spell's slot. `settle_slot_cast` therefore keeps the casting-action cost while omitting slot expenditure and its turn marker. The helper still rejects an initially illegal second slotted cast that turn. It does not decide whether the reaction trigger was visible or whether the save failed.
- **Revivify:** within one minute of death, Touch, consumed diamond worth at least 300 GP, return at 1 HP. It does not repair missing parts or reverse death from old age. Recheck the actual component inventory before spending the slot.
- **Simulacrum:** the duplicate cannot cast Simulacrum or take Short/Long Rests; it cannot gain levels. Do not create a full-rest resource reset for it through a generic rest handler. Use its explicit repair procedure.
- **Wish:** ordinary duplication is restricted to spells of level8 or lower and uses the entry's requirements exception. Other options have their own limits and stress; a freeform wish requires a concrete GM ruling. It cannot be treated as a universal automatic-success function.

Source: [official SRD 5.2.1](https://www.dndbeyond.com/srd), classes PDF28–82, multiclassing PDF24–26, spellcasting PDF104–106 and descriptions PDF107–175. Extraction coverage and selected cases are tested; exhaustive combinations of all spell/feature/monster interactions are not claimed. Live-player testing is outside the user's requested acceptance scope.

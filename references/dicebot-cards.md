# Dice assistance and character registration

Use this for existing card-only databases: 录卡, 查卡, 改卡, 切卡, `.st` and CoC7 checks. For new tables use [local Dice](dice-local.md). A recorded card is not proof of legal creation or advancement.

## Choose the execution mode

**Local Workbench:** execute `scripts/dicebot.py`. This is a documented local dialect, `workbench-local-v1`, with persistent cards and actual OS-random dice. The historical filename is retained for existing local databases.


**Existing campaign ledger:** `session.py` remains authoritative for established campaign resources. Use local card registration for identity/stat lookup and proposed changes; do not create a second competing HP/SAN ledger. Apply approved consequences once in the campaign ledger, then explicitly mirror the resulting absolute value into the card with a distinct operation ID and recorded ledger revision. If either step fails, report pending synchronization and read both states before retrying. Cross-database synchronization is not atomic.

## Register and verify a character

1. Identify the table, player, character, system/edition and card revision. Do not infer that an INT60 example is the user's own character.
2. Read the user's simplified-card text or selected spreadsheet fields. Use `sheet_audit.py` when formulas or cached values are involved. Keep background secrets, contacts and GM notes out of the numeric import string. Show uncertain OCR values for review; do not guess them.
3. Audit creation separately with the appropriate character procedure. Mark an unaudited import as recorded, pending legality review; it may still be saved as a draft.
4. Create a named local card or select the intended existing card. Display the target and proposed changes. Bare numbers and `=` replace values; `+`/`-` adjust an existing value in the local dialect. Explain this distinction when the input is ambiguous.
5. Execute one batch atomically. Unknown adjustment targets, repeated aliases, malformed text and out-of-range values reject the whole batch. There is no silent clamping or automatic derived-stat recalculation.
6. Read the whole card, then spot-check aliases and important fields. Export only recorded numeric fields. Read back the stored fields before reporting successful registration.

Local names `智力`, `灵感`, `智力灵感` and `INT` share the same stored INT field. `理智`/`理智值`/`SAN`, `生命值`/`HP` and other standard attribute aliases are likewise normalized. Custom skill names are retained, with ASCII case folded. Skill names may include Chinese/Latin letters and parenthesized specializations; this parser does not accept digits inside stat names, arbitrary expressions, quoted sentences or entire spreadsheet exports. Explain unsupported inputs and convert them into an explicit reviewed batch.

## Supported local commands

| Command | Local behavior |
|---|---|
| `.card new ada 阿达` | Create a separate card and select it; duplicate IDs rejected |
| `.card list` / `.card use ada` | List this player's cards in this table / switch active card |
| `.st 力量60智力60侦查50SAN70HP12` | Record numeric fields; spaced assignments also accepted |
| `.st 侦查=55 SAN-2` | Set Spot Hidden to55 and subtract2 from recorded SAN |
| `.st show` / `.st show灵感` | Display the active numeric card / one recorded value |
| `.st export` | Produce a local-dialect import command; use to copy recorded fields between local cards |
| `.nn阿达` | Rename the local card |
| `.r1d100` / `.r3d6*5` | Actual bounded roll, with raw dice and optional integer multiplier |
| `.ra侦查` / `.ra侦查 60` | CoC7 outcome using the recorded value or a one-roll explicit target |
| `.rab侦查` / `.rap侦查` | One bonus/penalty tens die, shared units die |
| `.rab2侦查` / `.rap2侦查` | Two extra tens dice; the GM establishes permission and cancels opposed bonus/penalty dice first |

The numeric storage range0..999 is a storage bound, not a character-creation cap. Percentile outcome checks currently accept targets1..100 and the bundled CoC7 critical/fumble profile only. Explicit targets do not overwrite the card. A result states its success tier; difficulty, opposed resolution, luck, pushed rolls and downstream effects remain with the selected game procedures. No roll automatically spends HP, SAN or skill points.

Local `.rh`/`.rah` are deliberately not parsed: this CLI's standard output is visible to its caller. For a GM-only roll, first establish a genuinely separate GM channel/output and use the existing dice tool there; shared player output must contain no result, expression, private filename or revealing narration. If there is no private channel, do not promise secrecy.

SAN and development are handled by the sourced `rules_math.py` procedures and the session ledger for this legacy store. Use the local table runtime for integrated session commands; keep the two database formats separate.

## CLI, persistence and recovery

Store the SQLite file in the user's private campaign directory, outside the distributed skill. The parent directory must exist. These examples are synthetic, not a registered real player:

```powershell
python -X utf8 scripts/dicebot.py --db '<private-directory>/cards.sqlite' --scope demo --owner pc1 --command '.card new ada 阿达' --operation create-ada --expected 0
python -X utf8 scripts/dicebot.py --db '<private-directory>/cards.sqlite' --scope demo --owner pc1 --command '.st INT60侦查50SAN70HP12' --operation import-ada --expected 1
python -X utf8 scripts/dicebot.py --db '<private-directory>/cards.sqlite' --scope demo --owner pc1 --command '.st show灵感' --operation show-int --expected 2
python -X utf8 scripts/dicebot.py --db '<private-directory>/cards.sqlite' --scope demo --owner pc1
```

The final call reads saved state without modifying it. Each submitted command, including a logged show/preview, advances the table/player revision. Use the returned revision for the next command. A retry must reuse the original operation ID, command and expected revision: it returns the original result, including the original dice, without applying or rolling again. A changed request under the same ID or a stale revision fails. Validate before rolling; failed requests do not commit state. Resume by reading the database, not by reconstructing values from chat.

Table/player fields isolate records for a trusted local operator; they are not an authentication service. The local operator is responsible for selecting the correct owner and protecting the database file. Back up the database through SQLite's backup facility or after closing all writers; copying a live database alone may omit journaled data.

## Source and interpretation

yy, *Welcome to Call of Cthulhu RPG / 教你如何快速成为一个合格的调查员*, sections “关于车卡录卡的那些事” and “如何正确的调戏骰娘”; user-supplied text and screenshot, version/date unstated. The screenshot demonstrates `.st show` and `.st show灵感`. This is a community tutorial and command-usage reference, not an official rules authority . No private document URL or contact details are needed in citations.

The tutorial's penalty-die prose incorrectly says to choose the smaller result although its example chooses61 over11. The local adapter chooses the larger complete percentile result for a penalty and the smaller for a bonus. It treats00 with units0 as100: candidates100 and10 produce10 with a bonus,100 with a penalty. It does not adopt suggested 80/60 caps or point-buy budgets as universal CoC rules. Rule outcomes use the existing [CoC7 procedures](systems/coc7-procedures.md).

## Roll character-creation attributes (CoC7 core)

Use this mode for “车卡 roll 属性”, “天命属性”, or “roll five CoC7 candidates”. Confirm the campaign uses rolled CoC7 core attributes and how many candidates the Keeper permits. Multiple candidates and choosing the highest total are table decisions; do not silently reroll, rank-select or combine attributes across candidates. Point-buy, quickstart, Pulp, other editions and other systems require their own selected generation procedure.

| Local command | Result |
|---|---|
| `.coc` | Roll and save one base candidate; no active card needed |
| `.coc5` | Roll five candidates (1–10 per request; 10 is a tool bound) |
| `.coc show b1` | Retrieve saved batch b1 without new dice |
| `.coc take b1 2 ada 阿达` | Copy candidate 2 into a new card ada and activate it; existing IDs are refused |

Use the CLI envelope above with a unique operation ID and current revision for each command. The returned batch ID is based on the request's resulting revision; use that returned ID, since it is not always b1. Identical retries reuse the saved dice. Batches persist across restarts and later rolls, isolated by table and player. Selecting a card keeps a separate original roll record; later `.st` edits cannot alter that evidence. `.st show`, `.st export` and `.ra` then work with the selected card.

STR, CON, DEX, APP, POW and LUCK each use 3d6×5; SIZ, INT and EDU each use (2d6+6)×5. Output contains all individual die faces, additive modifiers, roll event IDs and timestamps, final attributes, the eight-attribute total excluding LUCK, and the nine-value total including it. These are actual OS-random rolls. Do not impose the tutorial's 480/500 totals or 80/60 skill caps without a declared house rule.

Selection records **base_attributes_age_pending**. The generator does not yet perform age changes or populate HP, MP, SAN, MOV, damage bonus or Build. Continue with [CoC7 creation procedures](systems/coc7-procedures.md), section 1: identify age, obtain the player's allocation of age deductions, execute any additional actual luck/EDU dice, then record the final values and recompute derived values. Ages15–19 use a second luck roll and keep the higher of the two; ages20–39 still require one EDU improvement check. Do not call `.coc` again to obtain that second luck roll: use `.r3d6*5` and preserve the original. EDU checks use `.r1d100`; only a result above current EDU warrants `.r1d10`, capped at EDU99. Repeated improvements use the updated EDU. Log adjustments explicitly and retain the original; a generic `.st` edit does not certify that age processing was completed. Finish occupation/interest allocation, skills, equipment and background before declaring a legal finished character.

Rule basis: the bundled synthesis of *Call of Cthulhu*, seventh edition core rules, character creation chapter; Chinese core translation v1.2.1, PDF pages23–26. Command inspiration: yy's tutorial cited above. No fresh original-source audit is claimed for this extension.

For complex dice, teams, NPCs and audience-filtered log exports, use the separate [local Dice! adaptation](dice-local.md). Its `.ra` is an explicit house-rule check and `.rc` is core; this older adapter keeps `.ra` core. Choose one runtime and state database per table. Do not silently forward commands across dialects.

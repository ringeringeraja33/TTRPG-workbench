# Local Dice and tabletop services

Use `scripts/dice_local.py` for local dice, cards, teams, NPCs, initiative, complex expressions and persistent session logs. The arithmetic engine adapts selected Dice! RD code under AGPL-3.0-or-later; table services are implemented locally. Run `python -X utf8 scripts/dice_local.py --commands` for all command topics without a database, or append `roll`, `cards`, `table` or `log`. In a session, use `.help` or `.help cards`.

The older `scripts/dicebot.py` remains available for existing databases. Keep its SQLite files separate from this runtime; their schemas, card scope and command dialect differ. Do not silently migrate active games or write the same HP/SAN through both databases. For a new local table, make this runtime the sole card/resource writer; transfer approved results into the campaign ledger as sourced events when needed.

## Start a local table

Use a private directory owned by the current user, outside the installed skill. Python's standard library is sufficient, including DOCX log export. All operations run locally.

```powershell
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor keeper --command '.kp' --operation setup --expected 0
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor player1 --command '.nn 阿达' --operation card --expected 1 --private-output '<private-directory>/card.json'
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor player1 --command '.st STR60 CON60 SIZ65 DEX70 INT75 POW60 EDU70 LUCK50 SAN60 HP12 侦查60' --operation stats --expected 2 --private-output '<private-directory>/stats.json'
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor keeper --command '.team set @player1' --operation team --expected 3
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor keeper --command '.log on 首次调查' --operation log --expected 4
```

These are synthetic example values, not a legal completed investigator. Natural-language requests such as “为这个团建立掷骰记录”, “用第二组属性录卡”, “全队分别扣1d3点HP”, and “导出玩家可见的跑团日志” should be translated into the appropriate explicit local commands. Read current state with the same `--db --scope --actor` and no `--command`; reuse the returned revision, not a number inferred from chat.

Each command uses the table's global expected revision and a unique operation ID. The same successful request with the same operation ID returns its stored result without rerolling, even after restart. Changed input under a used ID fails. All updates, logs and operation results commit together. Failed operations commit no table changes; errors arising during arithmetic may already have sampled dice, so they are not successful rolls to apply. Keeper permissions are enforced against the stored local actor, but the local operator can supply any actor ID: this is not network authentication.

## Expressions and mechanics

| Request | Local syntax and behavior |
|---|---|
| Ordinary dice/calculation | `.r3d6*5`, `.rd`, `.r2d`, `.r(3+6)*5/2`, `.r3#4d6k3` |
| Keep high/low | `.r2d20k1`, `.r2d20q1`; every original die and selected index is retained |
| CoC core check | `.rc 侦查`, `.rc 60`, `.rc 侦查+10`; explicit target overrides a stored value |
| Optional house check | `.ra 侦查`; default1–5 critical/96–100 fumble; Keeper may `.crule set 2`; core `.rc` stays unchanged |
| Bonus/penalty | `.rb 侦查`, `.rp 2 侦查`; at most2 extra dice;00 is100, so penalty/bonus compare complete percentile values |
| Repeated checks | `.rcl 60 10` core, `.ral 60 10` house; bounded to100 checks |
| Opposition | Two different actors submit `.rcv 60` / `.rcv 80`, or `.rav`; profile must match. General opposition compares success rank then skill. Ties/both failures remain unresolved. Combat dodge/fight-back uses the existing CoC combat procedure. `.opposed cancel` is Keeper-only. |
| CoC attribute generation | `.coc` / `.coc5`, `.coc show bN`, `.coc take bN 2 ada 阿达`; see [attribute workflow](dicebot-cards.md). Age processing stays pending. |
| D&D rolled scores | `.dnd 2`: two candidates with six unassigned4d6-keep3 scores; establish edition and table permission before generation |
| Fudge | `.rf` or `.rdf`: four dice in−1/0/+1 |
| Exploding pool | `.ww10a10k8m10+2`; defaults10 dice,10 faces, explode≥10, success≥8; maximum500 initial dice and5000 total. `.w`/`.ws` share the same raw-dice output. |
| SAN | `.sc 0/1d6`; current card, core check, fumble maximum loss, daily cumulative tracker. No negative-loss syntax or automatic recovery. `.san day` starts a Keeper-agreed new game day; `.san bout on/off` records already-resolved bout status. During a bout, no additional SAN is lost. Use system procedures for INT, duration, indefinite/permanent insanity and recovery. |
| Development | Successful ordinary named-skill checks during an active team log suggest marks. Keeper verifies eligibility and `.mark @player1 侦查`; player uses `.en 侦查` once. No bonus-check mark or attribute development; advancement milestones and SAN rewards remain separate. |
| History and names | `.hiy` retrieves this actor/table's recorded check history; `.name 3 en` uses a small original fictional bank, with `ch`/`jp` alternatives |

Expressions use strict parsing and rational arithmetic (7/2=3.5); stored attributes require integer results. This differs from upstream RD's integer divisions and permissive normalization. Limits:100 dice per atom,1000 total per ordinary request, faces2..1000,100 repetitions, bounded parse depth and result magnitude. Fate shorthand defaults to four dice. No seeded production rolls or historical “expected-distribution” algorithm switching are offered. Deterministic unit tests use explicitly mocked randomness.

## Cards, teams and scene records

`.nn name` creates/selects a persistent local card. `.st name-STR50 CON60` imports a named card; `.st name` selects it. `.st show`, `.st show灵感`, `.st get`, `.st list` and `.st export` inspect recorded values. `.stc HP-1d3` updates the current card with actual dice. Duplicate aliases, malformed trailing text and out-of-range results abort the entire request. Numeric storage0..999 is not a creation cap or rule certification; derived HP/MP/DB/Build must be calculated through the system package.

`.st rename new-name` updates local team bindings. `.st cp card-name @recipient` copies without overwriting the recipient's card. `.st rm name` refuses active/team-bound cards. `.st clr` resets only the local `temporary` slot and refuses a bound slot. All cards are permanently isolated by table, so `.st lock/unlock` reports that isolation rather than changing shared cloud selection. Team bindings stay on the originally selected card until explicitly changed with `.team set`.

Keeper tools: `.team`, `.team set @p @q`, `.team hp all 1d3`, `.team san all 0/1d3`, `.team san @p +5`, `.team en`, `.team desc`, `.team rm @p`, `.team clr`. Every selected member rolls separately. All selected updates succeed together or all fail. This raw numeric adapter refuses HP below0 rather than silently clamping or resolving injury; use the system injury procedure to settle overkill and death.

Keeper-only `.npc st管家-HP10 侦查30` and `.monster st异物-HP30` create independent local stores. `.npc/.monster`, `get`, `rm name`, `clr` inspect/remove them. GM checks can use `.rc 管家:侦查`. `.npc make` offers an original brainstorming seed, not a generated statblock. Avoid name collisions: the actor's card wins, then monster, then NPC. `.ri +4 地精` uses d20, refuses rerolls over an existing entry, and stores original dice. `.init`, `.init set 地精 12`, `.init rm 地精`, `.init clr` manage explicit initiative; setters require the Keeper.

`.clue text` creates a public note with a stable ID. `.clue show`, `.clue rm cN`, `.clue clr` manage it; removal requires its owner or the Keeper. GM-only clues and dependencies continue to use the investigation package. `.des set 地下室|text`, `.des 地下室`, `.des list`, `.des rm 地下室` manage actor/table-private scenes. `.custom` and `.reply` use the same local input/set/list/rm pattern. Saved reply drafts remain private until explicitly enabled or published; see the local event workflow below.

## Private rolls, logs and recovery

`.rh1d100` rolls a private expression. `.table secret 1` marks subsequent roll/check responses private. Keeper-approved observers are set explicitly with `.ob set actor1 actor2`; `.ob clr/list` and `.table ob 0` control them. An actor cannot self-enroll as observer. Recipients are snapshotted at roll time. The CLI never prints a private result: pass `--private-output <new-file>` to retrieve it privately, or retry the identical operation later with that flag. File access control and recipient delivery belong to the local operator. Do not display a private file in a shared chat or promise that a label makes the screen secret.

`.log on name` appends/reopens; `.log off` closes; `.log list/get name/rm name` inspect or remove. Only explicitly submitted messages are captured. Logs store audience, actual command, result, actor, timestamp, revision and operation ID. `.log get` is a private response. Deleting a log removes its active view; operation receipts and existing backups remain. Never describe this as secure erasure.

```powershell
python -X utf8 scripts/dice_local.py --db '<private-directory>/table.sqlite' --scope demo --actor player1 --export-log 首次调查 --format docx --output '<private-directory>/首次调查.docx'
```

Formats: `txt`, `clean-txt`, `html`, `json`, `docx`. Exports filter by the selected actor's captured audience and refuse to overwrite files. DOCX colors speakers; HTML escapes content. `clean-txt` removes balanced ASCII/Chinese parentheses from human messages while retaining dice expressions and original raw logs. An unmatched parenthesis refuses cleaning. Parentheses may contain in-character content, so use raw output unless the table actually agreed to that OOC convention. No email/file transfer occurs.

`.log tables list name` lists local tables where the actor is a known participant and the log exists. `.log tables get scope1,scope2 name` explicitly merges accessible entries, keeping source scopes and audience checks. This reads the local SQLite store. Back up a closed database or use SQLite's backup API; copying a live database without its transaction state is unsafe. Restart by inspecting the persisted revision and replaying only a pending operation ID. The adapter has no long-running network service to restart and does not install startup tasks.

## Extensions, source data and administration

.deck supports flat arrays and source-attributed weighted/nested JSON decks. Keeper `.deck install name ["entry1", "entry2"]` loads a legacy local JSON array, `.draw name 3` / `.deck name 3` draws with replacement, `.deck list/help/remove name` manages it. The documented JSON reference format supports nesting. Executable scripts are not parsed. Do not silently run downloaded scripts or interpret old GBK template files as UTF-8. Preserve the original; decode using its declared encoding and design a reviewed conversion if needed.

`.ti`, `.li`, `.bg`, `.gas`, `.tz` require explicitly supplied matching decks; `.dr a 3` needs a `dnd5e-dr-a` deck. No official tables or licensed books are fabricated or redistributed. Deck suggestions never automatically apply symptoms, duration or character control. The structured JSON deck schema carries bibliography at each deck level and records every traversed source with the draw. For legacy arrays, record attribution in the private preparation dossier.

Keeper `.lookup import profile {"source":"Author, title, edition, section","entries":{"term":"text"}}` provides local source-attributed lookup data. Profiles: `coc7`, `dnd5e-2014`, `dnd3r`, `pf1`, `deathwatch`. `.rule`, `.magic5e`, `.magic3r`, `.5ey`, `.3ry`, `.con 5e/3r`, `.pfy`, `.dw` query those profiles, with close-name suggestions. Their absence is reported explicitly. D&D2024 and PF2 data must not masquerade as historical5e/PF1. Existing system procedures remain available independently of imported lookup data. `.getbook` returns a source/procedure pointer. `.dw card` and `.fire` lack the corresponding character/solo-module runtime.

Local configuration: `.table info` shows the current Keeper, participants, default die and supported switches. `.table secret 1` makes future rolls private; `.table ob 0` excludes observers; `.table deck 0` disables random-table commands; `.table simple 1` suppresses custom display formatting. Only the Keeper can change these settings. `.strRoll {nick}: {res}` changes display while retaining canonical numeric evidence; `reset` removes it, `NULL` blanks it. The placeholders `nick`, `pc`, `res` mean local actor, character and result. `.clock 60 closing` stores an owner-private deadline; `.clock list/poll` reports it and `--wait-timers` waits in a running local process. Acknowledgement and cancellation are described below. A stopped process cannot issue notifications.

Existing table databases keep their cards, logs and operation receipts. The prior stored draw-disable setting is respected until `.table deck 0|1` explicitly replaces it; obsolete settings are ignored and omitted from `.table info`. Old command receipts can still be replayed identically, but new commands use the current local interface.


## Sources and verification scope

- Dice Developer Team, *Dice!*, source commit `5e2a8324a631765f694b2e3a71f5d50f7ae6e94f`, [RD.cpp](https://github.com/Dice-Developer-Team/Dice/blob/5e2a8324a631765f694b2e3a71f5d50f7ae6e94f/Dice/RD.cpp). Original normal/Fudge/keep-high dice and modifier handling informed the local port; strict syntax, rational arithmetic, keep-low, full discarded-die evidence, OS RNG and transaction wrappers are local changes. Source snapshots and full AGPL license are under `scripts/vendor/dice_source/`.


## Natural table workflow and local events

The assistant should translate an ordinary request into these commands using the current table, actor and card. Users do not need to construct SQL, operation IDs or CLI flags. Read the current revision, use a new operation ID for a new intent, and reuse the exact original request for a retry. Select core `.rc` under a CoC7 core profile; `.ra` deliberately uses a historical house profile. Do not silently move an existing legacy dicebot database.

- “我输入整理线索时，提醒我检查证据来源”：save `.reply set 整理线索|检查实际取得的证据与出处。`, then `.reply enable 整理线索`. A subsequently submitted exact plain-text match returns the actor-private response. Other players cannot trigger or see that actor's private entry. `.reply disable 整理线索` stops the trigger. Text is never interpreted as a command or script, even if it begins with `.r`.
- “全桌输入规则时显示这段说明”：the Keeper saves a draft then `.reply publish 规则`. Publishing creates an explicit table-visible snapshot. Editing/deleting the private draft does not change the published snapshot; republish to update it or `.reply unpublish 规则` to remove it. A participant's enabled private exact match takes precedence over the table snapshot. No regex, recursive triggering, unsolicited message or marketplace is involved.
- “一分钟后提醒我收尾”：`.clock 60 收尾`, retain the returned timer ID, then wait using the command below. After actually presenting the reminder to its owner, `.clock ack tN` confirms it. `.clock cancel tN` cancels it. Timers survive restart, retain their status and are visible only to their owner, including in logs.

```powershell
python -X utf8 scripts/dice_local.py --db '<private>/table.sqlite' --scope demo --actor player1 --wait-timers 30 --operation timer-read-01 --expected 12 --private-output '<private>/timer-read-01.json'
```

A foreground wait lasts1..60 seconds, writes due timers to the private response file and prints only a receipt. It leaves unacknowledged timers pending, so interruption does not lose a reminder. A timeout changes no table state. Read the latest revision before the next wait; concurrent table activity can cause a stale-revision refusal and must be reconciled. If delivery output fails after the operation was saved, retry the original `.clock poll` request with its original operation/revision and private-output. Acknowledgement is a separate action after delivery, not an exactly-once external-notification guarantee. A stopped process cannot emit a reminder: after restart poll for overdue timers. For a true scheduled app notification use an available scheduler only under the user's request, and report that separate setup accurately.

### Attributed weighted and nested decks

Use independently written tables or data the current user can supply. Install child decks before parent decks. Example:

```text
.deck install weather {"source":"Original table, version 1","entries":[{"text":"雨雾","weight":3},"晴朗"]}
.deck install opening {"source":"Original opening table, version 1","entries":[{"ref":"weather","weight":2},"远处传来汽笛"]}
.draw opening 2
```

Every draw retains each selected deck/index, random ticket, total weight and source. Nested references return terminal text; they do not execute instructions. Existing flat arrays remain supported. Draws are with replacement. Bounds:100 draws,25 nested decks per draw,1000 entries per deck,10000 total entries, weights1..1000, text5000 characters; the existing command-size bound also applies. Missing references, cycles, malformed entries and deleting a referenced child fail before a change is committed. Invalid graphs consume no RNG. Replayed successful operations reuse the entire original draw path.

These local tools preserve operation receipts and source attribution. Imported lookup data and random tables must be supplied explicitly.

## 审查修复后的输出约定

默认状态读取仅输出 `revision` 和 `keeper`。完整个人状态使用 `--private-output <path>` 写入本地私密文件；`.init` 与 `.log get` 等私密回执同样使用此参数。已有文件内容相同时允许重试，内容不同时拒绝覆盖。

先攻保存创建时的受众，后续修改不扩大受众；旧记录缺少受众时只向原所有者显示。私密对抗不会向未授权接收者复制先手检定明细。检定目标范围为整数 0–999，与卡片存储范围一致，允许成长超过 100 后继续检定。

命令边界统一处理空格、制表符及 `. ! ！ 。` 前缀。清洁日志保留骰子表达式和结果。DOCX 遇到 XML 非法控制字符时明确拒绝导出；需要保留完整原文时可使用 JSON。

完整验证及资料投影、索引核验迁移说明见[修复记录](review-fixes-2026-09-16.md)。

## Campaign action bridge

[Recoverable actions](action-workflow.md) can bind a committed `.r` or `.rh` operation as evidence without rerolling. Campaign resources are settled only in the ledger; commands that already change Dice resources cannot be imported as action receipts.

For private full-database backup and operation-receipt recovery, see [local Dice archives](dice-archive.md). Campaign and Dice databases require separate copies and an explicit quiet checkpoint.

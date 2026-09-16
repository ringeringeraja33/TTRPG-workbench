# TTRPG Workbench

[English](#english) | [简体中文](#简体中文)

## English

A Codex skill for TTRPG rules research, adventure design, character creation, homebrew development, and game mastering, with source citations.

The skill includes source-backed procedures and examples that work without access to the maintainer's reference collection, keeping systems and editions separate. Its primary focus is Call of Cthulhu 7th edition, with topic-specific references for D&D, Trail of Cthulhu, City of Mist, Fate Condensed, Blades in the Dark, and selected local homebrew systems. See [coverage and limitations](references/coverage.md) for the scope of support.

### Usage

Save the complete repository directory as `$CODEX_HOME/skills/ttrpg-workbench`. If `CODEX_HOME` is unset, use `.codex/skills/ttrpg-workbench` under your home directory. Keep `SKILL.md` and its subdirectories together.

Example prompts:

- “Use $ttrpg-workbench to check a CoC7 rule and cite the source and page.”
- “Use $ttrpg-workbench to design a three-hour investigation for three players.”
- “Use $ttrpg-workbench to create a character for a specified edition, showing choices and calculations.”
- “Use $ttrpg-workbench as the Keeper; players roll their own dice.”

Use the bundled procedures directly. Citations identify the work, author/publisher, edition and chapter/page; they do not point to the maintainer's local files. Additional books are optional when researching uncovered rules or processing your own materials.

### Optional source research

The [material-reading tools](references/corpus-use.md) can process your own books and cards. Their private indexes and configuration are research aids, not installation requirements or user-facing citations.

### Detailed rules and worked examples

The local executable workflow now includes [CoC7](references/systems/coc7-table.md) and [SRD 5.2.1](references/systems/dnd2024-table.md) table procedures, a [transactional campaign ledger](references/session-runtime.md), player-specific projections, and an [original short scenario](assets/examples/lockhouse.md). `scripts/replay_acceptance.py` exercises 20 scripted player turns per system, with a fresh-process recovery at turn 10. This is deterministic simulated acceptance, not live-player testing or certification of every class and spell.

- [CoC7 procedures](references/systems/coc7-procedures.md) and [journalist build ledger](assets/examples/coc7-journalist.md)
- [D&D 2024 / SRD 5.2.1 procedures](references/systems/dnd2024-procedures.md) and [level-one Fighter](assets/examples/dnd2024-fighter.md)
- [Rule topics and source references](references/rule-locator.md)
- [Original investigation scenario](assets/examples/harbor-investigation.md) and [homebrew design lab](references/rules-design-lab.md)

Each procedure identifies its edition, evidence, examples, and remaining gaps. Search hits are not treated as verified rules.

### References and citations

- [Bibliography and source verification status](references/bibliography.md)
- [Citation guidelines and examples](references/citation-guide.md)
- [Third-party sources and attribution](THIRD_PARTY_NOTICES.md)
- [Source retrieval workflow](references/evidence.md)

Responses cite the materials actually used. Official rules, translator notes, GM rulings, and original design suggestions are identified separately. The repository contains original skill files; personal book collections, private campaigns, character secrets, and local build caches are excluded.

The README is bilingual. Most skill instructions, references, and templates are currently written in Chinese.

### Tools

Python 3.11 or later is required. The dice tool uses the standard library; dependencies for reading PDFs and spreadsheets are listed in `requirements.txt`.

```sh
python -m pip install -r requirements.txt
python -X utf8 scripts/test_tools.py
python -X utf8 scripts/test_rules_math.py
python -X utf8 scripts/dice.py probability 1d20 11 --mode advantage
```

See [tool documentation](references/tools.md) for commands and limitations, and [validation scope](references/validation.md) for checks performed. The skill has not undergone complete validation for every system or live playtesting of its sample adventure.

---

## 简体中文

用于Codex的TTRPG综合技能：查询规则、设计模组、核验角色卡、评估自制规则，并提供备团、现场辅助与直接主持流程。

技能内提供附出处的规则流程与实例，按系统和版本组织，无需访问维护者的参考资料原件。当前优先支持CoC7，包含D&D、克苏鲁迷踪、迷雾之城、Fate Condensed、Blades及部分本地同人系统的分主题参考；具体范围见 [覆盖说明](references/coverage.md)。

### 使用

将本仓库完整目录保存为 `$CODEX_HOME/skills/ttrpg-workbench`；未设置CODEX_HOME时使用用户主目录下的 `.codex/skills/ttrpg-workbench`。保留SKILL.md及其子目录结构。

示例指令：

- “用 $ttrpg-workbench 核查CoC7规则，给出书页和参考来源。”
- “用 $ttrpg-workbench 设计一个3人、3小时的调查模组。”
- “用 $ttrpg-workbench 按指定版本创建角色卡，列出选择与计算。”
- “用 $ttrpg-workbench 担任KP，玩家自行掷骰。”

可直接使用技能内已整理的流程。出处保留作者或出版者、书名、版本及章节页码，不向用户提供维护者的本机文件位置。研究未覆盖条款或处理自己的材料时，再按需补充资料。

### 可选资料研究

[资料读取工具](references/corpus-use.md)可处理用户自己的规则书和角色卡。私有索引与路径配置只服务于研究，不作为安装条件或对外引用。

### 详细规则与算例

本轮新增[CoC7桌上包](references/systems/coc7-table.md)、[SRD5.2.1桌上包](references/systems/dnd2024-table.md)、[事务会话账本与玩家投影](references/session-runtime.md)、[原创短模组](assets/examples/lockhouse.md)。记者补齐背景财产，战士补齐负重与升级路径。`scripts/replay_acceptance.py`分别执行20个预设玩家回合，并在第10回合由新进程恢复。这是确定性模拟验收，尚无真人桌测或全职业全法术认证。

- [CoC7程序](references/systems/coc7-procedures.md)及[记者创建台账](assets/examples/coc7-journalist.md)
- [D&D2024/SRD5.2.1程序](references/systems/dnd2024-procedures.md)及[一级战士](assets/examples/dnd2024-fighter.md)
- [规则主题与参考出处](references/rule-locator.md)
- [原创调查场景](assets/examples/harbor-investigation.md)及[规则设计实验](references/rules-design-lab.md)

每项程序说明版本、证据、算例和仍需查证的内容；检索命中不算规则已验证。

### 参考与引用

- [参考文献与来源核查状态](references/bibliography.md)
- [引用规范和实例](references/citation-guide.md)
- [第三方来源与署名](THIRD_PARTY_NOTICES.md)
- [来源检索流程](references/evidence.md)

每次回答引用实际使用的资料。官方规则、译者注、主持裁定和原创建议分开标注。仓库提供原创技能文件，不包含个人藏书、私密战役、角色秘密或本地构建缓存。

### 工具

Python 3.11及以上。骰具使用标准库；PDF、表格读取依赖见requirements.txt。

```sh
python -m pip install -r requirements.txt
python -X utf8 scripts/test_tools.py
python -X utf8 scripts/test_rules_math.py
python -X utf8 scripts/dice.py probability 1d20 11 --mode advantage
```

完整命令和限制见 [工具说明](references/tools.md)。规则与行为验证范围见 [验证说明](references/validation.md)。未进行全部系统的完整认证或真人模组试跑。

## Upstream-informed expansion

The [adoption map](references/upstream-adoption.md) records five pinned source reviews, licensing choices and implementation boundaries. This release adds an English skill entry, persistent preparation workflows, source-checked advanced mechanics, scenario graph checks, and an Apache-licensed bounded-resource module integrated with transactional advancement. Chinese interaction and existing Chinese rule references remain supported.

Run `python -X utf8 -m unittest discover -s scripts -p "test_*.py"` (343 tests) and the two twenty-turn replays described above. Tests cover implemented cases; they do not establish complete system or live-GM competence. Workspace installation uses `.agents/skills/ttrpg-workbench/`, preserving the complete directory structure.

## Class, spell, vehicle and ritual source packages

The [SRD source package](references/systems/dnd-class-spell-package.md) reads all 12 classes and 339 spell entries from the verified official 5.2.1 PDF. It adds multiclass slot, fixed HP and Counterspell settlement helpers. The [CoC package](references/systems/coc-vehicles-rituals.md) adds collision, occupant injury, ritual learning, first casting and backlash procedures. Full automatic interaction resolution is distinct from full source retrieval. See [current validation](references/validation.md) for executed checks. Live-player evaluation is outside this project task’s acceptance scope.

## Background-aware character creation

When given a module’s period, place and style, the skill now [researches an appropriate creation specification](references/background-chargen.md), using history and actual comparable character material. It separates source rules from original adjustments and produces distinct player and GM documents. [Three eras and six complete proposed cards](assets/examples/background-chargen/README.md) exercise budgets, skill changes, equipment and party coverage. The numerical adapter supports CoC7; other systems retain their own creation rules. See [current validation](references/validation.md) for executed checks.

## Original rulebook authoring

Use `$ttrpg-workbench` to turn a concept or notes into playable rules, expand chapters, reconcile contradictions, or assemble a quickstart. The [workflow](references/rulebook-authoring.md) maintains terminology, source decisions and cross-chapter dependencies. [Three original cases](assets/examples/rulebook/index.md) include a two-character, twenty-turn prototype and an explicit dependency checker. Private user drafts remain outside the distributable examples.

中文示例：“用 $ttrpg-workbench，把这些零散笔记整理成可玩的原创规则书，保留既定设定与术语，补齐操作程序、角色卡、算例和修订记录。”

Rulebook authoring includes dedicated dependency and workflow checks; see [current validation](references/validation.md).

## Skills, items and scenes from a historical brief

Use `$ttrpg-workbench` with a period, location and style to research and design skills, equipment, linked scenes and expansion ideas. The [workflow](references/background-design.md) separates historical evidence, existing rules, inference and original allowances. [Three packs](assets/examples/background-design/index.md) reuse six complete characters and add nine scenes with alternative routes and separate public materials.

中文调用：“根据这个模组的时代背景与风格，研究并设计技能、物品和三个关联场景，说明点数、装备来源和替代路线，分别输出玩家版与主持版。”

Background design has dedicated creation and scene checks; see [current validation](references/validation.md).

### Local dice and character cards / 本地掷骰与角色卡

Use the [local Dice workflow](references/dice-local.md) for actual dice, character cards, CoC7 checks, teams, NPCs, initiative and private session logs. The local SQLite store preserves original dice and returns identical results when an operation is retried.

支持本地掷骰、录卡、查卡、改卡、角色切换、属性生成、队伍资源和日志导出。用自然语言提出需求即可，例如“用第二组属性建卡”“检定侦查”“导出玩家可见的日志”。角色卡记录与规则合法性审核分开。

Run `python -X utf8 scripts/dice_local.py --commands` for a database-free command guide, or use `.help cards` during a session. Keeper settings use `.table info` and `.table secret/deck/simple/ob 0|1`. Cross-table log queries use `.log tables list/get`.

CoC7 attribute batches retain their raw dice: `.coc5`, `.coc show b1`, then `.coc take b1 2 ada 阿达`. Age processing and derived values remain explicit creation steps. Local notes, owner timers, and attributed weighted/nested JSON decks support session preparation and play. See the [command guide](references/dice-manual-coverage.md).

本轮代码审查确认的 12 项缺陷已修复，验证结果与旧数据兼容说明见[修复记录](references/review-fixes-2026-09-16.md)。

已加入[可恢复行动流程](references/action-workflow.md)：声明意图、绑定骰子凭据、等待选择、一次性结算，并支持私密结果和重启恢复。

行动现支持资源预留；[战斗时点](references/combat-timing.md)支持回合开始／结束、按角色到期的效果、可配置资源恢复，以及费用和效果的原子结算。

战斗现支持中途加入、离场、顺序调整和效果期限修订；已行动记录防止同一轮重复获得回合，旧版战斗存档可继续读取。

已加入[结构化角色导入](references/character-import.md)：私密差异预览、创建／更新、中英文技能别名、保留资源消耗及行动技能快照。

[调查现场管理](references/investigation-runtime.md)现支持线索发现与分享、分队知识、玩家假说与明确裁定，并可将线索获得与行动费用一起结算。

[探索时间与补给](references/exploration.md)支持活动耗时、明确补给扣除、游戏内到期提醒与行动联合结算；跨越阻断提醒前须明确处理。

探索操作现可先预演，查看耗时、补给和到期提醒变化；未到期提醒支持记录原因后改期。

调查计划支持开团后追加线索、结论和替代路线；仅未被任何角色获得的线索原文可修订，已交付的观察记录保持不变。

角色成长支持局部更新预览：只提交指定技能、资源上限或名称等变更，未指定字段保留，提交仍检查战役版本与行动占用。

[战役备份与完整性检查](references/campaign-archive.md)支持一致性 SQLite 备份、历史记录检查、独立文件校验值及恢复到新数据库。

[本地 Dice 备份](references/dice-archive.md)保留角色卡、日志与操作回执；恢复后重试原操作不会重新掷骰。

[统一验收入口](references/verification-runner.md)可一次执行测试、全部回放和生成存档的备份恢复验证，并保存分阶段报告。

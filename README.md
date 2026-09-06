# TTRPG Workbench

[English](#english) | [简体中文](#简体中文)

## English

A Codex skill for TTRPG rules research, adventure design, character creation, homebrew development, and game mastering, with source citations.

The skill uses local materials supplied by the user and official public rules, keeping systems and editions separate. Its primary focus is Call of Cthulhu 7th edition, with topic-specific references for D&D, Trail of Cthulhu, City of Mist, Fate Condensed, Blades in the Dark, and selected local homebrew systems. See [coverage and limitations](references/coverage.md) for the scope of support.

### Usage

Save the complete repository directory as `$CODEX_HOME/skills/ttrpg-workbench`. If `CODEX_HOME` is unset, use `.codex/skills/ttrpg-workbench` under your home directory. Keep `SKILL.md` and its subdirectories together.

Example prompts:

- “Use $ttrpg-workbench to check a CoC7 rule and cite the source and page.”
- “Use $ttrpg-workbench to design a three-hour investigation for three players.”
- “Use $ttrpg-workbench to create a character for a specified edition, showing choices and calculations.”
- “Use $ttrpg-workbench as the Keeper; players roll their own dice.”

Provide your own local rulebooks. Specify the library directory or invoke the skill from an existing TTRPG library. The skill locates files through the library inventory and does not depend on the author's computer paths.

### Local paths and indexes

Keep the Git source checkout separate from your book collection. An optional, untracked `local-paths.json` in the skill directory sets `source_root`, `library_root`, and `index_root`. Personal inventories, topic/page indexes, verification records, and extraction caches belong in the library’s `索引` directory, not in the source repository. The inventory command defaults to that directory when `--output` is omitted.

### Detailed rules and worked examples

The local executable workflow now includes [CoC7](references/systems/coc7-table.md) and [SRD 5.2.1](references/systems/dnd2024-table.md) table procedures, a [transactional campaign ledger](references/session-runtime.md), player-specific projections, and an [original short scenario](assets/examples/lockhouse.md). `scripts/replay_acceptance.py` exercises 20 scripted player turns per system, with a fresh-process recovery at turn 10. This is deterministic simulated acceptance, not live-player testing or certification of every class and spell.

- [CoC7 procedures](references/systems/coc7-procedures.md) and [journalist build ledger](assets/examples/coc7-journalist.md)
- [D&D 2024 / SRD 5.2.1 procedures](references/systems/dnd2024-procedures.md) and [level-one Fighter](assets/examples/dnd2024-fighter.md)
- [Local rulebook topic locator](references/rule-locator.md)
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

以用户提供的本地资料和官方公开规则为依据，按系统与版本检索。当前优先支持CoC7，包含D&D、克苏鲁迷踪、迷雾之城、Fate Condensed、Blades及部分本地同人系统的分主题参考；具体范围见 [覆盖说明](references/coverage.md)。

### 使用

将本仓库完整目录保存为 `$CODEX_HOME/skills/ttrpg-workbench`；未设置CODEX_HOME时使用用户主目录下的 `.codex/skills/ttrpg-workbench`。保留SKILL.md及其子目录结构。

示例指令：

- “用 $ttrpg-workbench 核查CoC7规则，给出书页和参考来源。”
- “用 $ttrpg-workbench 设计一个3人、3小时的调查模组。”
- “用 $ttrpg-workbench 按指定版本创建角色卡，列出选择与计算。”
- “用 $ttrpg-workbench 担任KP，玩家自行掷骰。”

本地规则书由用户自行提供。先指定资料根目录，或在现有TTRPG资料库中调用；技能通过资料清单定位文件，不依赖作者电脑路径。

### 本机路径与索引

Git源码库与个人资料库分别维护。技能目录可用不纳入Git的`local-paths.json`设置`source_root`、`library_root`和`index_root`。资料清单、主题页码索引、核查记录和提取缓存统一存入资料库的`索引`目录，不放入源码仓库。清单命令省略`--output`时默认使用该目录。

### 详细规则与算例

本轮新增[CoC7桌上包](references/systems/coc7-table.md)、[SRD5.2.1桌上包](references/systems/dnd2024-table.md)、[事务会话账本与玩家投影](references/session-runtime.md)、[原创短模组](assets/examples/lockhouse.md)。记者补齐背景财产，战士补齐负重与升级路径。`scripts/replay_acceptance.py`分别执行20个预设玩家回合，并在第10回合由新进程恢复。这是确定性模拟验收，尚无真人桌测或全职业全法术认证。

- [CoC7程序](references/systems/coc7-procedures.md)及[记者创建台账](assets/examples/coc7-journalist.md)
- [D&D2024/SRD5.2.1程序](references/systems/dnd2024-procedures.md)及[一级战士](assets/examples/dnd2024-fighter.md)
- [本地规则主题定位](references/rule-locator.md)
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

Run `python -X utf8 -m unittest discover -s scripts -p "test_*.py"` (55 tests) and the two twenty-turn replays described above. Tests cover implemented cases; they do not establish complete system or live-GM competence. Workspace installation uses `.agents/skills/ttrpg-workbench/`, preserving the complete directory structure.

## Class, spell, vehicle and ritual source packages

The [SRD source package](references/systems/dnd-class-spell-package.md) reads all 12 classes and 339 spell entries from the verified official 5.2.1 PDF. It adds multiclass slot, fixed HP and Counterspell settlement helpers. The [CoC package](references/systems/coc-vehicles-rituals.md) adds collision, occupant injury, ritual learning, first casting and backlash procedures. Full automatic interaction resolution is distinct from full source retrieval. Current tests: 65. Live-player evaluation is outside this project task’s acceptance scope.

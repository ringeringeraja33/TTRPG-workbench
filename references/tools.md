# 工具使用

Python 3.11+；骰具仅依赖标准库；PDF读取需 `pypdf`，XLSX需 `openpyxl`。在Codex中可通过workspace dependencies工具获得可用运行时；其他环境使用已安装Python。

从技能目录执行（将 python 换成实际运行时路径）：

```powershell
python -X utf8 scripts/library.py inventory './my-ttrpg-library' --output './private/local-inventory.json'
python -X utf8 scripts/library.py read './my-ttrpg-library/COC7th核心规则书v1.2.1.pdf' --query '困难成功' --limit 3 --chars 1500
python -X utf8 scripts/library.py read 'book.pdf' --start 76 --end 77 --limit 2
python -X utf8 scripts/dice.py probability 1d20 11 --mode advantage
python -X utf8 scripts/dice.py probability 1d100 50 --mode coc-bonus
python -X utf8 scripts/dice.py probability 4dF 0
python -X utf8 scripts/dice.py roll 3d6
python -X utf8 scripts/test_tools.py
```

`probability` 的 sum/advantage/disadvantage 判断结果 ≥ 阈值；CoC模式判断结果 ≤ 阈值，只支持一个额外十位骰。无大成功/大失败分类、无修正：需要修正时先换算原骰阈值。4dF为四颗等概率−1/0/+1骰。计算过大的精确问题拒绝执行，避免无界枚举。

`roll` 支持NdS、NdF和整数加减；输出真实原骰与事件ID，但不自动存档、不理解优势或CoC奖励规则，也不自动结算。需要复合骰法时分别运行原骰并按查证规则组合，记录全部原始结果。测试运行不得冒充游戏会话。

`library.py`读取不执行文档宏，不改源文件；清单命令只写指定输出。TXT遇到非UTF-8会报错，先识别源编码，再在独立缓存转码；不能假装替代字符是原文。PDF抽取不可靠时目视核查，不拿抽样语言检测认证全书。

## 已验证算例工具

`python -X utf8 scripts/test_rules_math.py`复现原12组规则算例。`rules_math.py`提供d20命中概率、购点成本、抗性次序、CoC阈值/单次伤害、GUMSHOE支出概率；本轮增加CoC成功等级、近战防御平手、SAN门槛、技能成长、追逐参与者AP、D&D死亡豁免与专注DC。不掷骰、不校验完整角色。CoC伤害函数采用官方Wiki等号修正，不处理溺水等特殊规则；不能用它覆盖所有死亡原因。

## 可执行主持与完整检查

- `session.py` 用Python标准库SQLite持久化经核定的状态。命令、事件合同和玩家投影见[会话账本](session-runtime.md)。
- `python -X utf8 -m unittest discover -s scripts -p "test_*.py"` 运行所有工具与状态边界测试；需要requirements.txt内的既有资料读取依赖。
- `python -X utf8 scripts/replay_acceptance.py --output "<index_root>/acceptance-new"` 在全新目录运行两个20玩家回合的预设回放；保留逐回合JSON、Markdown、冷恢复与最终状态。输出目录存在时拒绝覆盖。
- 接入真实会话前先阅读工具边界：规则计算函数不决定内容，账本不自动执行职业能力，玩家视图也不能识别被错误标为公开的秘密文字。

## 索引默认位置

`python -X utf8 scripts/library.py inventory "<资料库>"`默认写入`<资料库>/索引/local-inventory.json`；仍可用`--output`显式指定位置。扫描会跳过`索引`目录及资料入口文件，避免把旧清单、缓存和核查记录再次当作规则书。存在本机路径配置时按其`index_root`传入输出路径。

## Extended mechanics and scenario checks

`rules_extended.py` exports `coc_volley_plan`, `coc_volley_hits`, `dnd_slot_cast`, `fate_absorb`, `fate_recovery`, `blades_vice` and `blades_downtime_cost`. Import these explicit-input functions from a script with `scripts/` on the Python path. Read [scope and sources](systems/advanced-mechanics.md) before applying results; no function rolls dice or writes campaign state.

`python -X utf8 scripts/campaign_check.py <private-plan.json>` checks the graph schema documented in its module header. A nonzero exit indicates unresolved structural errors. `--player pc1` exports only explicitly visible clue records; destination IDs must also be safe before publication. This is a structural check, not proof that players can solve the mystery.

For an approved finite-resource increase, submit `{"kind":"resize","actor":"pc1","resource":"hp","maximum":20}` in a sourced session event. A resource at 10/12 becomes 18/20; it is not silently fully healed. Decreasing the maximum clamps the current value. Game-specific exceptions require an explicit additional change. The Apache-licensed upstream module and its notices are included in `scripts/vendor/`.

## Source-backed class, spell, vehicle and ritual tools

Read [SRD class/spell operation](systems/dnd-class-spell-package.md) for `srd_catalog.py` full-entry lookup and `class_magic.py` multiclass/HP/Counterspell functions. Read [CoC vehicles and rituals](systems/coc-vehicles-rituals.md) for `coc_vehicle_magic.py`. These helpers return proposed changes; apply them with source citations through `session.py`. The SRD reader validates the source hash and checks all 339 spell headers before returning results.

## Background character creation audit

`python -X utf8 scripts/background_chargen.py <spec.json>` audits an explicitly configured CoC7 profile: occupation/interest budgets, skill bases and caps, resources, approved equipment and wealth, party capabilities. `--player` emits only card fields. Unknown editions fail; missing evidence or unapproved house rules produce a draft. The profile is reviewed source data, not untrusted executable code. Historical and semantic checks remain part of [the workflow](background-chargen.md). Reproducible inputs: [three cases](../assets/examples/background-chargen/README.md).

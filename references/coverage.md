# 规则覆盖与证据深度

更新：2026-09-06。下表按主题报告真实进度，不给整个系统一个笼统的“精通”等级。能全文检索不表示已审校全文；已写操作参考也不表示全部扩展可用。

第二轮深化增加[自动射击、施法回合、Fate后果与Blades嗜好边界](systems/advanced-mechanics.md)、[持久备团](prep-persistence.md)、[生命周期](session-lifecycle.md)、场景图审计与升级资源操作。下表中的自动火力/载具缺口现为“部分程序与算术已实现，完整情境结算未完成”。[上游采用表](upstream-adoption.md)区分直接复用、许可改编和独立实现。当前55项自动测试通过；CoC与D&D各20回合仍为预设脚本，其他系统没有完整连续主持认证。

| 系统/版本 | 已有正文支持的操作内容 | 演示/验证 | 仍需查证 |
|---|---|---|---|
| CoC7核心 | 创建与年龄、技能池、难度、对抗/近战平手、战技、伤害/医疗、SAN门槛、追逐行动点、成长 | 记者技能台账；伤害边界自动测试；原创调查场景 | 自动火力、载具、魔法、怪物、完整职业、全部勘误与译本比对 |
| D&D2024/SRD5.2.1 | d20/熟练、行动、掩护、擒抱/推撞、伤害/临时HP、死亡、休息、施法位限制、创建 | 一级人类战士；购点/命中/抗性计算 | 全职业升级、全部条件/法术/物品、兼职、完整旅行与遭遇平衡 |
| 克苏鲁迷踪本地玩家手册 | 创建预算、调查信息、池支出、一般检定、重试与团队互利 | 指定支出概率、团队难度算例 | 完整职业与战斗、心智/坚毅程序及恢复 |
| 迷雾之城v0.75快启 | 动作触发、标签与状态、燃尽、状态合并、改变局势活力 | 效力与燃尽边界纸面演算 | 完整主题问卷、八动作全部选项、长期成长 |
| Fate Condensed | 标准创建、行动和相位援引、压力、场景选择 | 原标准建议卡；平手/压力纸面案例 | 全部强迫、认输与恢复程序、成长、特技平衡 |
| Blades in the Dark | 核心骰池、行动权限、协助/推动/交易、抵抗、时钟、停工顺序 | 风险/效果及抵抗案例 | 完整剧本与帮派、创伤、闪回费用、停工经济 |
| 诡秘v4.0同人 | CoC接口、SPI/MP差异、资源状态入口、作者声明的适用序列 | 跨规则MP公式冲突 | 每条途径/序列能力、恢复全文、完整角色及平衡 |
| 圣杯GugDove4.2.5 | 规则/自动卡版本绑定、时间单位、体型与环境机制入口 | 与Evil Hat Fate识别分离 | 御主/从者/宝具构筑、完整战斗与自动卡公式 |
| D&D3.5、2014 | 本地核心书可检索；3.5增加主题页序定位 | 不列完整认证 | 必须回读各版本条文，CHM仍未解 |
| BRP | 官方ORC入口与本地候选 | 未列完整认证 | 本地版本、可选模块与正文核查 |
| Pathfinder、战锤CHM、其余中文同人 | 文件定位 | 无程序认证 | 解包/版本、正文、角色与场景；文件名v2.01不能证明PF2 |

## 进入资料

本轮对标扩充：CoC7与SRD5.2.1分别增加[CoC桌上包](systems/coc7-table.md)、[D&D桌上包](systems/dnd2024-table.md)，接入事务账本、玩家投影和20+20回合脚本回放。记者补全背景财产；战士补全负重、1→5升级实例及1→20勇士能力索引。回放覆盖调查/失败替代/伤害/恢复/近战/存档与结团；SAN、追逐AP、死亡和专注另做边界测试。其他系统状态维持本表，全部职业/法术/高等级交互和真人自由输入主持尚未认证。

- [CoC7详细程序](systems/coc7-procedures.md)、[D&D2024详细程序](systems/dnd2024-procedures.md)。
- [克苏鲁迷踪](systems/trail-of-cthulhu.md)、[迷雾之城](systems/city-of-mist.md)。
- [Fate/Blades程序](systems/fate-blades-procedures.md)、[本地同人差异](systems/local-homebrew.md)。
- [主题页码定位](rule-locator.md)、[来源书目](bibliography.md)、[复现与验证](validation.md)。

新增系统应依次落实来源身份、程序、例外、角色台账和场景演练。未验证的部分按任务查证；不得通过复制别的系统摘要填满空白。

## Source-backed completion pass

The SRD package now reads all 12 class chapters and all 339 spell entries from the verified 5.2.1 PDF, including cross-page text. Added multiclass slot calculation, class-order fixed HP and Counterspell settlement. CoC now has collision severity/units/occupant procedures and learning, first-cast, interruption and backlash procedures with numerical helpers. See [SRD package](systems/dnd-class-spell-package.md) and [CoC package](systems/coc-vehicles-rituals.md). Earlier statements that these had no procedure refer to the preceding release.

Live-player evaluation is excluded from the requested work and is not a pending acceptance gate. Remaining scope distinctions: non-SRD publications, fractional-Build vehicles and source-specific exceptions require their actual source; all-entry retrieval does not claim exhaustive automatic adjudication of every possible interaction.

## Background-aware creation

Added an actively researched history/module-to-chargen workflow, player/GM templates and three historical fixture profiles with six complete proposed characters. The numerical adapter covers CoC7 only and checks configured rules/availability; it does not independently establish historical facts. Other systems use the workflow with their native creation rules. Sources lacking allocation ledgers do not become invented official budgets.

## Original rulebook authoring

[Authoring workflow](rulebook-authoring.md) now covers concept intake, note organization, chapter revision and conflict repair. The manifest checker validates explicit dependencies and claims. A separate original dream-game prototype demonstrates two characters and twenty simulated turns; it is not a generic rules engine or a balance certification.

## Background-driven design

The [design workflow](background-design.md) connects historical research, native skill budgets, operational items and linked scenes. Three fixture extensions reuse six audited CoC7 characters and provide nine original scenes. Numerical support remains CoC7; history and clue semantics require source/prose review.

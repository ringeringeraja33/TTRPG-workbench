# 可执行会话账本

需要跨天主持、分队、恢复或可复算日志时使用 `scripts/session.py`。它保存主持人已核定的结果；技能值、命中、伤害类型、时长和许可仍须先按系统包核验。数据库含 GM 秘密，只放私人战役目录，不能发给玩家或进入公开仓库。

## 从备团进入第一回合

1. 打开系统包：CoC7 用 [coc7-table.md](systems/coc7-table.md)，SRD 5.2.1 用 [dnd2024-table.md](systems/dnd2024-table.md)。读完所用角色、敌人和特殊机制的来源，填写年代、版本、可选规则、骰子控制者及内容边界。
2. 分开创建 `gm-prep.md` 与 `player-brief.md`。前者写事件真实因果、NPC 目标/行动条件、线索出口和失败后果；后者只给角色目前知道的委托、环境、联系人及公开风险。原创示例见 [闸站夜班](../assets/examples/lockhouse.md)。
3. 将初始状态写成 UTF-8 JSON。使用 [初始状态模板](../assets/templates/session-initial.json)。资源 `value/max` 必须非负且前者不超过后者。升级先核算新卡；同版本已有资源可用 resize 修改上限，构筑选择仍须主持人核验。
4. `python -X utf8 scripts/session.py "<私人目录>/campaign.sqlite" init --config "<私人目录>/initial.json"`
5. 每个玩家行动先产生一个事件文件，再 `apply --event "<私人目录>/event.json"`。成功输出 revision 和 SHA-256 后才叙述已经持久化的结果。失败时读错误并修正输入，不在聊天中先宣布成功。

## 事件合同

```json
{
  "id": "session01-turn01",
  "revision": 0,
  "profile": {"system": "CoC", "edition": "7e", "options": {"luck_spend": false}},
  "input": "我向值班员出示证件，询问失踪工人的去向。",
  "resolution": "值班员提供值班记录；无敌意且记录公开，无需检定。",
  "sources": ["GM原创场景：闸站夜班/N1；无需检定的裁定"],
  "changes": [
    {"kind": "fact", "value": {"id": "shift-note", "text": "失踪工人最后一班在闸站。", "audience": ["all"]}},
    {"kind": "clock", "minutes": 5}
  ]
}
```

`input` 保留玩家实际意图，`resolution` 写目标、难度、骰子来源/每颗出目、等级与实际后果；两字段为 GM 日志。`sources` 写具体书页/条目，原创裁定明确标识。没有资料时不填伪造锚点：将问题放入 `pending`，只提交已经确定的叙事进展。

| change.kind | 参数 | 校验与用途 |
|---|---|---|
| resource | actor、resource、delta | 对已有资源增减；越界整件事件回滚；治疗填写实际恢复量 |
| resize | actor、resource、maximum | 修改已有资源上限；增加时保留已消耗量，降低时将当前值截到新上限；不自动判定升级资格或治疗 |
| conditions | actor、value（字符串列表） | 整体替换该角色条件；时长/来源写 GM private；同一规则事实不得散落冲突 |
| fact | value：id、text、audience | 追加唯一事实；audience=[] 为 GM；["all"] 为全体；["pc1"] 仅指定玩家 |
| clock | minutes | 增加非负整数分钟；战斗轮、SAN 日界与追逐行动点另放 private，不把一分钟当成一轮 |
| pending | value（列表） | 替换待决问题，保留任务、原因、需要的资料、可继续的行动 |
| private | value（对象） | 替换完整 GM 状态；必须从最新 view 合并，避免遗漏旧计时器 |
| restore | revision | 单独提交；恢复目标快照并追加新 revision，保留原有事件和历史 |

## 恢复、重复与版本冲突

- `view --gm` 回读权威状态。接续时先核对最后 revision、待决动作、各角色位置与轮次；尚未取得的骰子仍等待，不重新掷已提交骰。
- 同 ID、同完整内容重发返回 `duplicate=true`，不再次扣费。同 ID 不同内容拒绝；过时 revision 拒绝；profile 任一差异拒绝。返回的是原事件 revision，重发后再读取最新状态。
- SQLite 事务把事件和快照一起提交；两个进程同时提交同 revision 只允许一个成功。不修改数据库文件内部文本；OneDrive 冲突副本不能自动合并。
- 纠错时用新的事件 ID，`changes=[{"kind":"restore","revision":12}]`，resolution 解释原因。新 revision 仍递增。回滚后的分支使用新事件 ID，不能复用旧分支已提交 ID。
- 当前不实现跨版本自动转换。2014 角色进入 2024 战役前重新核定背景、特性、法术及物品，另建配置并保留原存档。数据库 schema 也不作静默迁移。

## 玩家视图与分队

`view` 仅输出全体公开角色与事实；`view --player pc1` 额外输出明确授权给 pc1 的条目。它不会输出 profile、private、pending、完整事件、隐藏时钟或状态哈希。需要给玩家文件时把这一结果保存成另一个 UTF-8 文件并读回检查。

可见性由写入者标注，工具不理解文本是否剧透；GM 要逐条检查公开叙述。实体整项公开时资源和条件都会公开，不把敌人真实 HP 放入公开 actor。分队 A 得到的线索只标 A 玩家 ID，实际交流后追加面向 B 的公开事实。玩家摘要只从导出的投影视图产生，不让玩家侧助手直接读数据库。

## 桌上交接格式

每次响应先给可观察的后果和新信息，停在一个可行动的位置。内部记录本次消耗、未决判定和下一行动者。失败允许原路径被堵住，同时呈现世界中的其他机会；不得在未成功时赠送刚刚失败的同一个结果，也不让 NPC 直接报出谜底。

模拟验收使用明确写有 `test fixture` 的骰输入；真实开团沿用玩家骰或约定的 `dice.py` 输出。禁止把回放数据当成随机骰、真人记录或未发生的玩家选择。

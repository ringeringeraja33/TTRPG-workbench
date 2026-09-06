# 验证范围

## 五项目对标后的可执行验收（2026-09-06）

源码新增`session.py`、`test_session.py`、`replay_acceptance.py`及规则边界函数。当前43项测试通过，包含已有资料读取/骰具测试与新增事务、并发、信息隔离、版本/资料缺失、近战平手、寡不敌众、SAN、成长、追逐AP、死亡豁免和专注DC。真实执行记录保留在本机index_root的`benchmark-2026-09-06`，不纳入技能包。

`replay_acceptance.py`对CoC7与D&D分别执行20个预设玩家输入，包含调查、检定失败后改走其他路线、取得证据、伤害、防御、恢复和结团。第10回合使用新Python进程读回数据库，重复同事件不再扣资源；继续到20。CoC终态HP8、图书馆84；D&D终态HP12、Second Wind2、花费1颗生命骰。所有骰子都是标记过的test fixture，未真人参与。

角色卡补全财产/背景和装备/负重，战士给出1→5已选升级路径；1→20勇士表是来源支持的操作索引。SAN、追逐、死亡、专注为独立边界测试，不能声称都出现在20回合场景中。现阶段尚无陌生玩家自由输入压力测试、上游五项目完整测试、完整载具/自动火力/法术交互验证。

首次测试发现Windows测试数据库未关闭与Python缺openpyxl；明确关闭测试连接，换用已有完整依赖运行时后重跑通过。可复现命令见[工具说明](tools.md)。下面保留此前构建历史，不把历史纸面演练计为新增自动化测试。

以下首表为初始构建历史记录（2026-09-06），本轮深化结果见后文；技能创建验证与行为演练；没有真人试跑和全系统完整认证。

|检查|实际结果|边界|
|---|---|---|
|技能结构|skill-creator quick_validate通过|仅证明结构|
|工具|8项单元测试通过|精确骰分布、共享个位、非法输入、真实骰范围、中文/XML、稀疏XLSX、命名歧义|
|规则查询|CoC技能65/测试32成功等级与难度分开，PDF76/书68目视；D&D属性表PDF21/书21目视|具体锚点验证，不代表全书|
|角色创建|Fate Condensed完整标准建议卡由独立代理执行；CoC快启属性/技能草案；D&D点购阶段|Fate关系/特技待桌上采纳；另两项不是完整角色认证|
|原创模组|《末班渡船》4节点、线索/失败/撤退路线纸面走查|未真人试跑|
|主持连续性|失败推进、玩家摘要隔离、事件ID与revision断点恢复|使用明确测试输入|
|规则设计|d20基线50%→取高75%；CoC阈值51奖励75.9%|数学模型，不是平衡证明|
|资料错误|发现快启译稿算术/初始SAN问题；GugDove版本矛盾|保留原文件，写明证据|
|UTF-8与安装|严格读回、内部链接与JSON、源/安装副本SHA-256对比|发布准备时检查|

原始构建日志与人工演练记录由维护者在本地保留，未包含在公开包中。公开可复现的工具检查运行 `python -X utf8 scripts/test_tools.py`；行为演练是维护者记录的历史验证范围，不构成公开完整认证。

已知限制：CHM/CHW/旧DOC/图片未解包或OCR；部分语料开头无文本；多数系统尚未逐条审校；部分译本权威性未确认；无需网络时可用本地语料，有时仍需访问官方正文。不能承诺熟知全部TTRPG规则。

## 本轮深化验证（2026-09-06）

已执行原8项工具测试与新增12组规则测试，全部通过。新增用例覆盖负调整值取整、27点购点/不合法生成后输入、优劣势抵消、攻击自然1/20、抗性/易伤先后、CoC阈值、单次与累计伤害、奇数HP重伤门槛、官方立即死亡等号、既有重伤与0HP、记者职业/兴趣预算、GUMSHOE掷前支出概率。

复现：`python -X utf8 scripts/test_tools.py`及`python -X utf8 scripts/test_rules_math.py`。这些测试不认证未实现的条件、法术、职业、医疗全过程或所有房规。

| 人工走查任务 | 本轮结果 | 限制 |
|---|---|---|
| CoC记者核心点数法 | 职业280/兴趣150全部列账，阈值、HP、职业信用范围核对 | 测试属性；背景装备与信用资产仍需KP确认 |
| D&D一级战士 | 背景/物种/训练分层、18技能、武器、资源与恢复核对 | 未逐件算负重；不是全部职业认证 |
| 版本冲突 | CoC译本死亡等号依官方修正；D&D2024不套旧版擒抱、休息或施法限制 | 不是全书勘误审计 |
| 同人差异 | 诡秘MP=SPI与CoC公式隔离；GugDove4.2.5绑定卡版本 | 未完成全部超凡能力或宝具验证 |
| 模组可运行性 | 逆潮钟房四地点、多路线、失败替代、时间与撤离纸面走查 | 未真人试跑 |
| 主持恢复 | 指定E01/revision1→2，重复失败不再结算，待发生事件保留 | 纸面状态演练，不是完整状态管理软件测试 |
| 资料移动 | 7份主题索引源书在当前资料库重新定位，与旧清单SHA-256逐份相同 | 只核对本轮引用的7份，不宣称重新核验全部藏书 |
| 资料缺失 | 迷雾快启不包含完整主题问卷，明确不认证完整自建角色 | 保留缺口，不借别系统填空 |

本轮规则释义有来源锚点；主题定位表117项仅是全文候选命中，不计入“已核查规则数量”。完整文本缓存保留本地，技能仅含原创归纳、引用和示例。

## Second deepening pass: 2026-09-06

55 automated tests pass in the bundled Python environment with `requirements.txt` dependencies. This supersedes the earlier count above. New checks cover declared volleys and wasted ammunition, extreme-range hits, slot expenditure on different turns, consequence absorption, vice overindulgence, war downtime costs, resource upgrades and transactional rollback, broken scenario references and player projections.

The earlier statements that Fighter weight had not been calculated and session recovery was only a paper exercise describe the earlier pass. The current worked build includes weight; the executable ledger and two twenty-turn replays now test actual disk state and fresh-process recovery. Full class/spell coverage, complete vehicle collisions, rituals and live-player evaluation remain unverified. Upstream projects were source-reviewed; their full test suites were not run.

## Source-backed completion pass

65 automated tests cover the implemented boundaries, including cold-process ritual-cost recovery. An actual-source integration check separately reads all 339 SRD spells, checks their 339 Casting Time headers and 12 class source ranges, and saves the index outside the skill. This validates coverage of extraction, not every possible rules interaction. Live-player testing is explicitly outside acceptance scope and is no longer a pending task.

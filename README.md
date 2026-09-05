# TTRPG Workbench

用于Codex的TTRPG综合技能：查询规则、设计模组、核验角色卡、评估自制规则，并提供备团、现场辅助与直接主持流程。

以用户提供的本地资料和官方公开规则为依据，按系统与版本检索。当前优先支持CoC7，包含D&D、Fate Condensed、Blades、GUMSHOE、BRP及其他系统的分级参考；具体范围见 [覆盖说明](references/coverage.md)。

## 使用

将本仓库完整目录保存为 `$CODEX_HOME/skills/ttrpg-workbench`；未设置CODEX_HOME时使用用户主目录下的 `.codex/skills/ttrpg-workbench`。保留SKILL.md及其子目录结构。

示例指令：

- “用 $ttrpg-workbench 核查CoC7规则，给出书页和参考来源。”
- “用 $ttrpg-workbench 设计一个3人、3小时的调查模组。”
- “用 $ttrpg-workbench 按指定版本创建角色卡，列出选择与计算。”
- “用 $ttrpg-workbench 担任KP，玩家自行掷骰。”

本地规则书由用户自行提供。先指定资料根目录，或在现有TTRPG资料库中调用；技能通过资料清单定位文件，不依赖作者电脑路径。

## 参考与引用

- [参考文献与来源核查状态](references/bibliography.md)
- [引用规范和实例](references/citation-guide.md)
- [第三方来源与署名](THIRD_PARTY_NOTICES.md)
- [来源检索流程](references/evidence.md)

每次回答引用实际使用的资料。官方规则、译者注、主持裁定和原创建议分开标注。仓库提供原创技能文件，不包含个人藏书、私密战役、角色秘密或本地构建缓存。

## 工具

Python 3.11及以上。骰具使用标准库；PDF、表格读取依赖见requirements.txt。

```sh
python -m pip install -r requirements.txt
python -X utf8 scripts/test_tools.py
python -X utf8 scripts/dice.py probability 1d20 11 --mode advantage
```

完整命令和限制见 [工具说明](references/tools.md)。规则与行为验证范围见 [验证说明](references/validation.md)。未进行全部系统的完整认证或真人模组试跑。

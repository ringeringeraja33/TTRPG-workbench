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

# 第三方来源与署名

## Reused skill implementation and workflows

- `scripts/vendor/sagasmith_resources.py` is an unmodified copy of `packages/domain/src/sagasmith_dnd/resources.py` from SagaSmith D&D, revision `065ec82b179b2b9da8af967afb02cbe5b265e4cf`. Copyright 2026 SagaSmithAI contributors. Apache License 2.0: [license](scripts/vendor/LICENSE-SagaSmith), [original NOTICE](scripts/vendor/NOTICE-SagaSmith). The finite-counter integration in `scripts/session.py` is local code. No SRD data bundle was copied with this module.
- `references/prep-persistence.md` adapts Sue's `coc-kp-host/references/prep_persistence.md`, revision `9fedf60613b5f4c599a4128f6ce1d5da5bfebaaf`. Copyright (c) 2026 Sue. [MIT license](scripts/vendor/LICENSE-coc-kp-host). Changes and additional checks are identified in the adapted document.
- `references/session-lifecycle.md` adapts AntTheLimey's gm-apprentice session preparation instructions, revision `b9912ea7219e55215ce0c2f87247e410ab8d903a`. That adapted file remains CC BY-SA 4.0; [license](scripts/vendor/LICENSE-gm-apprentice). Its source and changes are identified in the file. This does not relicense unrelated project files.
- claude-dnd-skill (AGPL-3.0) and RePoG (Apache-2.0) informed the source review. Their code was not copied. See [adoption map](references/upstream-adoption.md).

New English Fate and Blades summaries are paraphrases under the same source attributions below; references to Chinese adaptation also describe the existing Chinese documents. The corresponding helper functions encode limited mechanics with the stated source boundaries.

本项目以原创工作流程、规则短释义、模板和代码组织TTRPG任务。参考游戏名称用于来源识别，不表示获得出版方认可。书目及使用位置见 [参考与引用列表](references/bibliography.md)。未附商业规则书、模组正文、插图或私人角色卡。

## Dungeons & Dragons SRD

本项目的相关规则释义参考 *System Reference Document 5.2.1*，Wizards of the Coast LLC。原资料：[官方SRD](https://www.dndbeyond.com/srd)，采用 [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)。本项目进行了中文概括与流程整理；没有复制完整SRD。

## Fate Condensed

相关释义基于 *Fate Condensed*，Evil Hat Productions, LLC；开发、写作及编辑署名：PK Sullivan、Lara Turner、Fred Hicks、Richard Bellingham、Robert Hanz、Sophie Lagacé。来源：[Fate SRD](https://fate-srd.com/fate-condensed/getting-started)，原资料采用 [CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)。本项目改写为中文短释义与核对流程。Fate商标属于Evil Hat Productions。

## Blades in the Dark

相关核心机制释义参考John Harper的 *Blades in the Dark* SRD；原资料采用 [CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)，详见 [官方许可页](https://bladesinthedark.com/licensing)。本项目采用中文概括；没有使用其插图、标志或商业书版式。

## Chaosium、Pelgrane及其他来源

CoC、BRP、Trail of Cthulhu与GUMSHOE资料的权利归相应权利人。引用官方入口、书目信息或本地页码不授予这些产品统一的再分发许可。BRP-ORC与GUMSHOE-SRD在本项目中用于来源/版本定位，没有将其完整内容转许可为项目代码。

本文件记录第三方归属与所作修改；各来源的许可分别适用，不自动构成本项目全部原创内容的统一许可证。

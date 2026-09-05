# 规则主题页码定位入口

个人书库的页码表保存在资料库内，不随源码或技能安装副本复制。先读技能目录可选的`local-paths.json`：有`index_root`时打开其下的`rule-locator.md`；否则使用用户指定资料库的`索引/rule-locator.md`。同目录的`local-inventory.json`提供当前相对路径和SHA-256。

页码表记录检索候选，不能视为已核验章节。先匹配文件名与哈希，再读取PDF相应页及上下文；版本或文件内容变化后重新生成定位。PDF页序从1开始，印刷页另行核查。缺少该表时直接对用户提供的原书按关键词检索，不能假设作者本地页码适用于另一文件。

通用规则释义仍在本技能`references/systems`中，书目保留在[bibliography.md](bibliography.md)。主题表、资料清单和全文缓存的更新写入资料库索引目录。

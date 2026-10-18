# 0.7.3 本地修正

- `tis-english-naturalness` 正式更名为 [tis-real-english](../skills/tis-real-english/SKILL.md)，旧标识退役，不保留调用别名。旧会话请使用新名称。
- 同步入口路由、CAT 搭配检查、插件清单与文档；筛查流程、David W. Ferguson 来源归属和独立 `fake-english` 不变。
- 同步仅在旧目录完整匹配托管清单时将其归档到清单旁的 `retired-skills/`，不再参与技能发现。旧副本被修改、来源未知、文件缺失或存在符号链接时保留原件、报告冲突并停止整次同步；新名称冲突也不覆盖。`--check` 只报告，`--apply` 成功后清单只记录现行名称。

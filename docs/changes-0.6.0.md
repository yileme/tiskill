# tiskill 0.6.0 更新说明

新增 `tis-plain-language`，用于技术文档和软件本地化译文的简明表达审校。它按目标语、地区变体和客户规范选择英文或简体中文参考；交付修改稿、改动理由与来源索引。英文用法争议仍通过 `tis-usage-evidence` 查证。

`/tis` 入口已加入该任务的分流。产品说明见 [docs/product.md](product.md)，来源索引见 [tis-plain-language](../skills/tis-plain-language/references/sources.md)。Apple、Microsoft 等 PDF 保存在用户本机，不随技能分发。

原有子技能名称和调用方式保持不变。更新本地副本前运行 `python3 tools/sync_installed.py --check`，确认没有用户修改冲突；然后运行 `python3 tools/sync_installed.py --apply`。目前仓库仍是本地版本，更新通知只反映本机真源。

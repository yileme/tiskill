# 0.12.2：完善既有 SkELL 支持

SkELL 自 0.7 已在来源参考中；本版细化检索协议，非首次接入。tis-usage-evidence 新增独立参考，覆盖短语 Examples、Word Sketch 基本形式/词性/关系、正常浏览器读取、受阻与零匹配状态、引文选择和统计口径。词典受阻时可查真实用例，但不冒充词典释义。

既有离线 bilingual_queries.py 增加 --source skell；双语默认行为不变，无网络/API 集成。版本同步至 0.12.2；公开版本从已审计的公开历史追加发布。独立 usage-evidence 与诊断技能不在修改范围。

实查与限制见 [SkELL 验收](skell-acceptance.md)。

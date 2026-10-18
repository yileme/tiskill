# 方法来源与整合映射

本文对照当前仓库技能与独立源技能的说明，记录已经实现的选择性整合。独立源为 `monterey-translation-framework` v2.0.0 和 `fake-english` 的 SKILL.md；后者自述依据 David W. Ferguson《English, Chinglish & Wronglish》两卷。此次核对的是技能说明，不是重新考证其列出的全部书籍、私人语料或作者主张。来源自述不等于机构、教授或作者为 tiskill 背书。

## 已有实现在哪里

| 来源中的原则或问题线索 | tiskill 的具体实现位置 | 已整合的方式与限制 |
| --- | --- | --- |
| Monterey：接稿分析、文本类型、语言/文化/情景语境 | [practice：输入与路线，第 1 项](../skills/tis-translation-practice/SKILL.md) | 任务卡明确读者、媒介、用途、地区及不能改变的信息；软/硬文本只是检查重点的线索，工具使用仍受委托约束。 |
| Monterey：多版本比较、语境调适、翻译策略 | [practice：第 2–3 项](../skills/tis-translation-practice/SKILL.md) | 选 1–3 个难点，比较可行候选的信息、语气和使用条件；不为凑候选提供失真答案，英文用法依赖证据。 |
| Monterey：准确性、流畅性、风格性与自我审校 | [practice：第 4–5 项](../skills/tis-translation-practice/SKILL.md) | 先对原文意义和完整性，再独立读目标语，最后核数字、名称、术语、格式及任务约束；把可接受选项交给诊断，不当评分答案。 |
| fake-english：名词可数性、复数、动词结构/语义/语境、形容词副词与词性 | [naturalness：流程第 1–3 项](../skills/tis-real-english/SKILL.md) | 转成具体语境中的候选风险；词性问题通过词义、结构与可信语法资料核实，非复制全书分类库。 |
| fake-english：搭配、书面/口语语域、shoehorn（硬塞）、赘余或机械结构 | [naturalness：流程第 2–4 项](../skills/tis-real-english/SKILL.md) | 先看表达能否承担本句意思，再看是否匹配读者和语域；输出需要修改、有条件可优化、证据不足/可保留三档。 |
| 查证：避免把经验线索直接升级为定论 | [usage-evidence：查证流程](../skills/tis-usage-evidence/SKILL.md)；[来源选择](../skills/tis-usage-evidence/references/sources.md) | 这一证据层另提炼自 usage-evidence v1.18.1；区分原文对照和外部用法命题，打开真实词条/语料，记录短证据与实际链接，失败则待核实。 |
| 教学诊断：把任务判断、表达筛查与证据接起来 | [diagnosis：Procedure 第 2–5 项](../skills/tis-translation-diagnosis/SKILL.md)；[类别依据](../skills/tis-translation-diagnosis/references/categories.md) | ATA 启发的教学归类；同一底层问题计一次，偏好和未核实项不计错；按错误机制布置练习，只从实际作答判断变化。 |

整合的理由是这些步骤回答不同问题：任务与语境确定要保留的意思和可接受选择，表达筛查定位值得查的问题，证据检验它们是否成立，教学诊断解释影响并安排练习。[快递案例](examples/courier-translation-diagnosis.md)中的“有可能”遗漏靠原文对照确定，`packet` 的邮政义则需要词典证据；两种依据不能互相替代。

## 有意限制或未移植的部分

- **句式与词性不是方向性通则。** 源 Monterey 速查中“英译中分短、中译英合并”、名词化增加正式感等只是待检验的策略；practice 明确把长短句、语态、词性转换和文化解释作为选项。不推导出“必须合句”“名词化总更好”，也不擅加逻辑、人物或评价。
- **文本类型不自动授权工具。** 未继承“硬文本即可用机译”的充分条件式判断；以保密、客户要求及实际任务约束为先。
- **表达索引不是禁用清单。** fake-english 的 NOBA（not only … but also …）“十次九次可删”、书面推荐英式英语，以及对口语连接语、`as well as`、`the development of` 的提醒，均不成为通用比例、地区等级或自动判错规则。词性和语域要按本句查证；强调、对比和限定仍须保留。
- **没有移植私人案例库与全部工作流程。** 不分发源技能的版权章节、长篇书例、私人文献或提取数据；未把 Monterey 的全部接稿到交付流程和冷审稿时长移植成强制程序，也未把 fake-english 的累计问题经验变成能力分数。ATA 考试点数、合格线与 NAATI 等级同样不混入教学诊断。

## 独立安装与维护边界

仓库已经包含上述工作步骤、引用索引与边界说明，基本实践、筛查和诊断不以原始两个技能或外部私人目录存在为运行前提。naturalness 允许在环境明确提供原技能时按需阅读相关章节；这只是可选参考，不是隐藏的硬依赖。涉及英文用法的确定判断仍需要可访问的证据来源，不能访问时按技能要求保留待核实。

两个独立技能及其约定的单向同步链由原处维护。tiskill 的整合不会自动同步它们的后续变更，修改 tiskill 也不修改源技能；若将来采纳源变更，应重新核对本映射及适用条件。此次仅补文档，不改独立技能、仓库技能行为或版本号。原项目许可与分发边界见 [README](../README.md)；本页不授予来源书籍或案例的再利用权。

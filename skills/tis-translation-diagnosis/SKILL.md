---
name: tis-translation-diagnosis
description: Diagnose a learner's written translation against its source using ATA-inspired error categories and design targeted revision practice. Use for bilingual translation exercises, draft feedback, and error analysis; not for interpreting performance or official ATA exam scoring.
metadata:
  keywords:
    - ATA translation error categories
    - translation diagnostic practice
    - translation error feedback
    - bilingual draft assessment
---

# ATA-inspired written translation diagnosis

先读 [反馈与对话](references/voice-and-interaction.md)，按其规则控制讲评篇幅和语气；下文的证据、任务与保存边界仍须遵守。

Work on a source text and a learner's target text, ideally with the translation brief (target audience, medium, purpose, locale, constraints). This is teaching feedback adapted from ATA materials, not ATA grading, certification, or a pass prediction. Do not claim ATA endorsement. Ask for missing source or translation when absent; if the brief is missing, state a provisional assumption and avoid penalizing register or locale choices that depend on it. A reference translation is optional; never treat it as the only acceptable answer.

## Procedure

1. Align source and target in meaningful units, including headings, lists, figures and negations. Identify 2–5 consequential findings first; include a coverage check. If the user wants full coverage, inspect every unit and state the extent checked.
2. For each finding quote only the short relevant source and target spans, give an independently reasoned explanation, and choose a primary ATA category. Decide first whether meaning/author stance is distorted by comparing source and target; otherwise distinguish target language mechanics from writing quality. Use `references/categories.md` for labels and ambiguous boundaries. Count one underlying problem once; avoid stacking labels for the same span. If context permits several renderings, say so and do not mark a preference as an error.
3. Estimate educational priority from effect on meaning, reader and purpose: critical (core facts or use compromised), substantial (meaning changed locally), minor (readable language or style problem), or optional improvement. These are teaching priorities, not ATA numerical points. If evidence is insufficient, mark `待核实` and explain what to check; never invent official terminology or authoritative citations.
4. For a Chinese-to-English draft with suspected Chinglish, wrong word use, mechanical parallelism or unsuitable register, load `tis-real-english` to generate context-specific hypotheses, then check them through `tis-usage-evidence`; keep optional rewrites and unresolved suspicions out of the error ledger. A structure such as `not only ... but also ...` is not an error by itself. If a finding or correction depends on whether an English expression has a particular sense, collocation, register, regional norm, or domain use, load `tis-usage-evidence` and perform its live verification workflow before labeling that choice an error or recommending a replacement. Put its short quotation/observable corpus result and actual clickable source URL beside the finding. When verification fails, mark the claim `待核实` rather than call it a firm error. Source-to-target checks such as changed numbers, negation and omissions can rely on direct bilingual comparison; explicitly label that basis as `原文对照`. Do not use frequency alone to rule out a possible translation, and do not demand lexical evidence for plain transfer errors. For each real error, supply a minimal correction plus why it resolves the problem. Cite the exact ATA source document and page/section when a rule is invoked; for a context-based judgment, label it as your own application. For into-English examples, the 2025 standards target U.S. English ATA exams: apply their conventions only when the brief specifies U.S. English or explicitly asks for ATA exam practice. For other language directions, use general error-category reasoning without claiming English rules apply.
5. If the user previously used `tis-translation-practice`, carry forward its audience, purpose and acceptable translation options. Treat its strategy as a testable choice, not a grading key. Pick one or two recurring error mechanisms, not just the most frequent label. Create 2–3 short original practice prompts per mechanism using new sentences or an equivalent self-review task. Require the learner to attempt before revealing answers unless the user explicitly asks for answers. Explain the criterion for success; on the next attempt compare actual behavior with the prior error rather than asserting improvement without evidence.

## 教练式报告与保存

局部提问或练习续答先直接讲当前判断、原句、理由和最小修改，不展开整份报告或重复附表；涉及 ATA 分类时保留相应来源与非官方说明。用户要求系统诊断、完整报告或归档时，按 `references/report-and-records.md` 的结构输出中文讲评。像老师当面讲一份稿：有具体依据时说做对之处，再讲最影响读者理解的 2–5 个问题；一处一处引用原文和译文、解释“读者会读成什么”和“怎样检查/改写”，不要只丢 ATA 缩写、扣分或“更地道”。证据分别标 `原文对照` 与带真实链接的 `用法查证`，没有查实的归入 `待核实`。已有事实可以说“这处否定方向颠倒了”，不必为了语气软化事实。只在实际观察到重复机制时才称其为“反复问题”；一份短稿中的单例叫“本次训练重点”。

完整报告末尾增加“这节课的元语言”：用本次真实问题解释 1–2 个分析术语（例如意义传达、遗漏、语域或译文可用性），说明术语帮助译者提哪一个自查问题。元语言是谈论语言与翻译决策所用的概念和术语，不是玄学术语或“好坏标签”。最后给 ATA 学习路径：至少链接 [How the Exam is Graded](https://www.atanet.org/certification/how-the-exam-is-graded/) 与 [Explanation of Error Categories](https://www.atanet.org/certification/how-the-exam-is-graded/error-categories/)；若本次谈判错流程、类别清单或英译入美式英语，则按主题添加 `references/ata-learning.md` 的对应链接。可展示完整五项链接，但不要每次冗长复述。提醒这些是 ATA 考试资料，报告的教学优先级不等于官方考试评分；“考官视角”是训练自己核对原文意义、目标读者与翻译说明，不声称自己就是考官。

完整诊断默认在对话中给可复制 Markdown 讲评，并附一份简短的错误记录表（仅已确认错误，按“一处独立错误一行”），列出本次错误类别计数；不把待核实或风格备选算作错误。**归档推荐两层**：Markdown 保留讲解、来源和修订前后语境；CSV/在线表格每行一个错误，跨练习按类别累计频次。频次是练习诊断记录数，不能当作个人能力分数；注明稿件长度、覆盖范围，避免跨长度直接比较。

用户选择“保存本地”时，使用用户指定路径或当前工作区有意义的练习目录，产出该次 `.md` 与累计 `errors.csv`，并验证文件存在及 CSV 可读；不在没有用户要求保存时偷偷写档。使用 `templates/report.md` 和 `templates/errors.csv` 的字段与行式，先准备单次报告及只含已确认错误的单次 CSV，再运行 `python3 <本 Skill 目录>/scripts/save_report.py --report <准备好的报告.md> --issues <单次错误.csv> --destination <用户选定目录>`；脚本会拒绝同名报告或重复错误编号。没有已确认错误时准备只有表头的 CSV，脚本只保存 Markdown，不生成错误行；每次练习记录稳定 `exercise_id`（用户既有编号优先，否则当天日期加可读序号），每项 `issue_id`，避免重跑重复追加。保留用户已有记录，不覆盖已有讲评；同名冲突改名或交由用户选择。飞书文档和腾讯文档：用户指定平台和文档时，在可用的登录连接器/浏览器里创建或追加报告，同时把错误行写入对应表格或数据库；检查写入结果和链接。没有平台写入能力或授权时给可复制的 Markdown 与 CSV，不宣称已保存；不要先要求用户提供两个平台的地址。

原始讲评与累积记录的格式以 `references/report-and-records.md` 为准。用户只要诊断时不要强制问存哪里；完整报告结尾可用一句话提供“可保存为本地 Markdown + 错误表，或写到飞书/腾讯文档”，并在用户选择后执行。

When using the local ATA materials, read the original documents as needed and cite their exact section/page; do not reproduce large passages in output or package the copyrighted PDFs into a distributed skill. The reference file records the source versions and decision distinctions. NAATI rubrics in the same collection are a separate assessment system: do not combine their bands or pass requirements with ATA codes.

用户明确询问包容性语言、性别、代词或身份表达，或本次出现相关局部问题时，可读取 `tis-inclusive-language`；只交接该问题，区分原文立场、译文增添与客户偏好，不自动全文扫描或强制串联。有条件建议与待核实项不计为翻译错误。

# 0.9.0 来源核对与知识归纳

五个用户授权本地 PDF 共 514 页：EU Plain language 2；HSE 21；Neubauer 论文 70；ISG 306；Federal 115。先检查 PyMuPDF 等依赖存在，再逐页提取全部页面到工作区 `.ekko-tmp`；无上传，无 PDF 或完整提取文本进仓库。完整提取不等于全文人工精读。

EU 两页清单和 HSE 全文已读。较长三份材料选择性精读，精确范围、身份、日期和印刷/PDF 对照记录在[技能来源](../skills/tis-plain-language/references/sources.md)。不声称已经读完论文、ISG 或 Federal 全部正文。ISG 文本极少的封面与末页已渲染目视，分别为带书名的封面与出版局标识；无需 OCR。另目视核对 HSE PDF p.6（印刷 pp.10–11）的跨页表格，以及 Federal 封面批注。其余图表未逐一视觉复核，未据未读图示增加规则。

核实的易错身份：`file.pdf` 是 Anna Gabrielle Neubauer 的日内瓦大学 2011 年 6 月硕士论文，存储库 2023 更新日期不是出版日期。ISG 是欧盟机构出版风格指南，文件标最后更新 15.10.2026；不是 plain-language 专论。Federal 是 2011 年 3 月、5 月修订的 PLAIN 指南附不明来源教学批注；批注与正文区分。HSE 末页明确 August 2025，而非按文件元数据推断。

新增知识归纳：围绕读者要找、理解和使用的信息组织文字；动作与前提相邻；每段一个要点；具体动作与熟悉用词；必要术语解释且保持一致；删无贡献复述。重复判断移用于 AI 式冗长是本技能的编辑归纳，来源不构成 AI 检测依据。

没有把机构字体、英文字数、阅读年级、数字形式或词语替换表变成通用硬规则。HSE 的长文回顾与口头重复、Federal 的必要衔接提醒我们保留有功能的重复。教育/商务应用是通用原则的延伸，非五份材料均覆盖这些领域。法律与医学替换须检查真实语义，不直接搬用示例。未独立验证转引研究、统计、当前法规或外部网页，不能据此报告本技能改善率。

共享 voice 已有反重复、反黑名单与不强改条款，保持全部副本不变。CAT 动态加载真实技能参考，新增 Markdown 会进入 plain 请求；无 CAT Python 改动，无服务重启。自动检查限结构/来源页界/元数据/注入契约；[样例](plain-language-acceptance.md)为人工设计，不是实时模型或目标读者试验。

验证结果：`tools/validate.py`（版本、结构、共享 voice 一致性、相对链接和来源页界）、`tools/test_update.py`、`tools/test_diagnosis_save.py` 均通过；CAT Python 单元测试 45 项、library 5 项、business 16 项通过。CAT 测试包含实际 skill/reference 注入与提议保护契约。`git diff --check` 通过。托管副本同步后复查 Up to date；未覆盖用户改动。未运行浏览器端交互或 live Codex 语言效果测试。

## 0.9.1 追加：当前完整阅读范围

以上为 0.9.0 历史记录。ISG 已另行完成 PDF 1–306 逐页阅读，新增 Gardner 59 页、How to write clearly 16 页、DGT 138 页，四份共 519 页。完整独立笔记、身份及视觉限制见 [逐页来源记录](source-reviews/README.md)。其他材料的历史选择性范围不变；不把本轮全读推广到此前其他 PDF。

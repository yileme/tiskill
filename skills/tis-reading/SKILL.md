---
name: tis-reading
description: 用网页剪藏、EPUB 指定章节、PDF 指定页或 Markdown 做轻量阅读陪练，保存来源与学习笔记，选择词块句式、复述和真实输出，并导出供人工导入氢刻的文件。
metadata:
  keywords:
    - reading companion
    - epub reading notes
    - qingk card export
    - source learning notes
---

# tis-reading

先读 [反馈与对话](references/voice-and-interaction.md)。材料足够就开始，一次读一个有界片段，不生成大档案。安装目录内所有脚本和参考自包含；无需仓库或其他技能才能运行阅读 CLI。

1. 明确用户已提供的范围和目标。网页用用户剪藏的 MD/TXT，URL 只记元数据；用户要求时可由宿主打开并捕获允许访问的内容，不抓付费墙。PDF 指定页，EPUB 指定 spine 章节；MD/TXT 指定行，或明确使用不超过 20KB 的小文档。原件不改写，不把书放进仓库。先查看依赖是否存在：PDF 需 pypdf，XLSX 需 openpyxl，EPUB 用标准库。无依赖时说明需要安装；扫描/OCR 和复杂版面阅读顺序待人工核对。
2. 先实际阅读片段，再解释关键论证。提取成功不表示已核实。只在实际读过且用户明确确认、记录 checker 后写 text_read；未经核对的 OCR 继续 unverified。来源记录有哈希、路径、页/章/行 locator 和段落 block ID；原文与学习记录分开。
3. 讲词块时按“词典依据→原文→本句解读→可迁移表达”组织简短说明，不强制四个标题。词典事实只引用本次实际取得的条目与短引文；原文逐字引用并标来源，本句推断明确说是语境解读。词典打不开时如实说明尝试与失败，不编释义或冒充已核实；仍可根据已读原文解释本句，把更广泛用法标为待核实。可迁移表达注明生成示范，保留适用条件。

   默认邀请用户选 3 个词块、1 个句式，可少可多。词义按本句；不自动合并异义词。不编 IPA、CEFR、频率、词源。查证到现有 01-查证记录，表达到 02-表达积累，复盘到 03-练习复盘，不另建词汇库。
4. 请学习者先用自己的话总结；可中译中、借英读中（借英文结构重组中文意义），或英文复述。保留原回答，之后的尝试追加新 ID。一次只给一个可完成的真实用途动作：邮件句子、解释观点或情景回应，不强制长篇输出。题干允许自然的语法选择，例如“My morning was ...”可接形容词、名词短语或符合语境的更完整表达；不为套目标词块判错其他合理回答。先收回答，再按意义、条件、逻辑、用法适切性和用户目标反馈；开放答案没有自动客观分数。示范标 model_generated，与 source_quote 分开。
5. 经选择再做少量卡片。question 先引发提取，answer 给答案/依据，hint 可选。原文引句须逐字匹配所存片段；生成例句明确标记。草稿不默认导出，confirmed 必须来自用户确认。只在明确保存授权后运行带 --confirm 的命令。
6. 工作阶段 imported/reading/selected/practising/review 不表示掌握。listdue 只是日期过滤，无通知和 SRS。导出后交付实际文件，先让用户预览再人工导入氢刻；不登录、上传或发布，不声称外部导入已验证。mark-imported 仅记录用户事后明确陈述。

CLI 与 JSON 契约见 [使用说明](references/contract.md)。可直接运行 `python3 <本技能目录>/scripts/reading.py --help`。来源与局限见 [参考](references/sources.md)。

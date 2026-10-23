# tiskill 是什么

tiskill 是 [@译了么](https://xhslink.cn/o/3UlkBC8GKzqv) 制作的口笔译学习与实践工具箱，包含 **12 个 Agent Skills**，当前版本 **[0.13.0](VERSION)**。安装到支持 Skills 的 Agent 后，把材料和想解决的问题交给它，就能开始阅读、练习、查证或审校。

| 你想推进的事 | 可以得到什么 |
| --- | --- |
| 读懂一段外刊，并学会自己用 | 关键论证解读、词块与句式、一次练习及作答后的反馈 |
| 翻译前理清任务，或修改已有初稿 | 读者与用途分析、译法取舍、有原文依据的讲评 |
| 判断英文表达或双语译例是否适合本句 | 实际来源、短引文、使用条件与待核实项 |
| 把通知、邮件或译文写清楚 | 保留事实、条件和语气的改稿；按需审校身份与性别措辞 |
| 用真实材料练听说 | 听辨、跟读、复述或情景回应；反馈范围取决于实际可用音频 |
| 从客户聊天推进到项目草案 | 需求简报、待确认问题、报价与回复草稿 |

## 本次更新

**0.13.0 新增公共服务英文译写。** 单条译写、双语审校与批量待审记录；可选私有标准索引，公开包不含标准全文。脚本不自动翻译。[本版变化](docs/changes-0.13.0.md) · [设计与验收](docs/public-service-acceptance.md)


**0.12.0 新增外刊与阅读伴读，共 11 项技能。** 支持网页剪藏、Markdown、PDF 指定页和 EPUB 指定章节，从读懂选段、积累表达到学习记录与氢刻卡片导出。[能力范围](docs/changes-0.12.0.md)

**0.12.1 完善阅读反馈。** 按“词典依据→原文→本句解读→可迁移表达”解释词块，分清事实与推断；查证失败如实说明，每次只安排一个可完成的练习动作。[本版变化](docs/changes-0.12.1.md)

**0.12.2 完善既有 SkELL 查证路径。** 增加可执行的浏览器检索协议与离线查询链接，分清短语用例、搭配关系和计数口径。[本版变化](docs/changes-0.12.2.md)

## 安装与开始

先安装 [Node.js](https://nodejs.org/)（包含 npx），在终端运行：

```bash
npx -y skills add yileme/tiskill -g --all
```

这会将公开版本的全部 12 项技能安装到 skills CLI 支持的 Agent 目标。只装到 Claude Code 和 Codex 可用：

```bash
npx -y skills add yileme/tiskill -g --agent claude-code codex --skill '*' -y
```

只查看、不安装：`npx -y skills add yileme/tiskill --list`。宿主支持范围以 [skills CLI 文档](https://github.com/vercel-labs/skills#supported-agents)为准；其他产品需有 Skills 导入或读取能力，普通聊天窗口不等同于安装环境。手动导入时保留技能目录内的 references、scripts 等文件。

安装后重新打开 Agent 会话。可以用 `/tis` 描述任务，也可以直接调用具体技能；命令显示以宿主为准。已有材料和回答会在当前对话里沿用。

## 阅读时会得到什么

把网页剪藏为 MD/TXT，提供 Markdown 选段、PDF 页码或 EPUB 章节。阅读 CLI 处理本地文件，URL 只作来源信息；宿主能访问网页时，也可按你的要求获取允许访问的内容。

例如，附上 `article.md` 后这样说：

```text
/tis-reading 请陪我读 article.md 的第 1–20 行，先解释这段的观点和理由。
帮我选 3 个词块、1 个句式，分清词典依据、原文和你的语境解读。
然后只给我一个能用在今天生活里的造句任务，等我回答后再点评。
先在对话里做，不保存。
```

词块和句式数量可调整。你先用自己的话总结、复述或写一句真实用途的表达，Agent 再对照意义、条件、逻辑和用法反馈；可以中文重述，也可以用英文。不会从一次回答推定口语水平或学习成效。

下面是**编写的风格示例**，句子不是外刊引文，也不是一次已经完成的词典查证：

> **词典依据：**如果词典查询失败，说明“这次未取得可核对的词典条目”，不把记忆中的释义写成词典事实。
>
> **原文：**示例材料写道：“My morning was interspersed with short breaks.”
>
> **本句解读：**按这句语境，短暂休息穿插在上午的活动之间。这是对示例句的理解，不能单凭这一句推出所有搭配都自然。
>
> **可迁移表达：**可以试着用 “My morning was ...” 描述今天上午；如 “My morning was busy.” 是生成示范。若想沿用 “interspersed with”，其更广泛的搭配与语域仍待实际查证。

真实讲解会在取得证据时给出词典名称、链接与短引文，并逐字引用你提供的文章选段。查询失败也能继续解释已读原文，但不会标作已核实。

需要留存时，你明确要求保存后，来源快照进入 `07-阅读素材`，查证与表达复用 `01-查证记录`、`02-表达积累`，回答和自评进入 `03-练习复盘`。原回答保留，后续尝试追加记录。选中的卡片先是草稿，经你确认后才导出氢刻 **Excel/Tab** 所用的 XLSX/TSV 文件：普通卡两列，提示卡三列，无表头。

导出后先预览，再由你人工导入氢刻。导出清单记录文件和卡片修订；你事后明确告知已导入，才记录导入确认。没有新增阅读前端、自动同步、通知或 SRS，也未验证实际氢刻导入。[使用契约](docs/reading.md) · [合成样例验收与限制](docs/reading-acceptance.md)

## 全部 12 项技能

| 命令 | 适合什么时候用 | 主要输出 |
| --- | --- | --- |
| [`/tis`](skills/tis/SKILL.md) | 知道任务，不想先选技能 | 根据当前材料进入相应流程 |
| [`/tis-translation-practice`](skills/tis-translation-practice/SKILL.md) | 动笔前分析、比较译法、译后自查 | 任务分析、候选取舍、自查项 |
| [`/tis-translation-diagnosis`](skills/tis-translation-diagnosis/SKILL.md) | 对照原文检查初稿、寻找训练重点 | 有依据的讲评、最小改法、练习 |
| [`/tis-real-english`](skills/tis-real-english/SKILL.md) | 检查中译英或英文稿的表达风险 | 必改、可选优化与待核实项 |
| [`/tis-usage-evidence`](skills/tis-usage-evidence/SKILL.md) | 找双语译例、回查译法，或问英文表达能否使用 | 实际来源、短证据与适用条件 |
| [`/tis-plain-language`](skills/tis-plain-language/SKILL.md) | 把中英文写清楚，删重复与套话 | 最小修改、全文重写或诊断 |
| [`/tis-inclusive-language`](skills/tis-inclusive-language/SKILL.md) | 询问英文或中译英的包容性语言、性别、代词或身份称谓 | 有依据的局部判断、最小修改与适用条件 |
| [`/tis-speaking-practice`](skills/tis-speaking-practice/SKILL.md) | 用真实材料听辨、跟读、复述 | 练习、反馈与自评 |
| [`/tis-client-service`](skills/tis-client-service/SKILL.md) | 接洽笔译、口译或本地化项目 | 简报、报价、回复草稿及授权建档 |
| [`/tis-reading`](skills/tis-reading/SKILL.md) | 网页剪藏、EPUB/PDF 选段、Markdown 阅读 | 来源笔记、词块句式、复述、实际输出与氢刻文件 |
| [`/tis-public-service-english`](skills/tis-public-service-english/SKILL.md) | 公共场所名称、导向、警示、通知译写与批量审校 | 带场景条件、来源定位和证据状态的建议 |
| [`/tis-update`](skills/tis-update/SKILL.md) | 同步本机已安装的技能 | 差异检查与受控同步 |


## 保存、查证与可选工具

日常阅读和讲评可以只在对话里完成。**Obsidian 归档是可选项**；需要保存或导出时，在 `~/.tiskill/library.json` 的 `path` 配置现有 vault 内的 tiskill 文件夹。阅读技能自带 CLI 与参考，单独安装也可运行，不依赖开发仓库。CLI 需要 Python 3.10+，目前验证范围为 macOS/Linux；PDF 提取另需 pypdf，XLSX 导出另需 openpyxl。EPUB 使用标准库，扫描件 OCR 暂不支持，复杂 PDF 阅读顺序需人工核对。[目录与配置](docs/library.md) · [阅读 CLI 契约](skills/tis-reading/references/contract.md)

英文查证需要 Agent 能搜索并打开来源；打不开就保留待核实。来源提取成功不等于核实，`text_read` 需要实际阅读和用户明确确认。生成例句与真实引文分开，练习没有自动客观语言分数。

客户资料先确认允许使用相关 AI 工具。报价、回复和建档均为草案，费用未知时不按 0 计算；CLI 不发送消息、不上传客户数据，项目接受与履约由人工核对。[业务说明](docs/business.md)

需要逐段编辑译文时，可在仓库根目录运行 `python3 cat/server.py --port 8765`，打开 <http://127.0.0.1:8765>。纯文本编辑无需模型，段落讨论需已安装并登录的 Codex CLI。CAT 是单项目教学原型，与阅读归档分开。[CAT 使用说明](cat/README.md)

## 更新与其他安装方式

通过 skills CLI 安装的用户，重新运行安装命令即可取得当前公开版本并补齐新增技能。重装可能覆盖自行修改的文件，请先备份。只装一项时，可把 `--all` 换成 `--skill tis-reading --agent claude-code codex -y`。

Claude Code 插件方式：

```bash
claude plugin marketplace add yileme/tiskill
claude plugin install tis@tiskill-skills
```

插件入口为 `/tis:tis`。更新时运行 `claude plugin marketplace update tiskill-skills`，再运行 `claude plugin update tis@tiskill-skills`。选择插件或 skills CLI 一种安装方式即可。

`tis-update` 按安装渠道处理更新。可选本地托管脚本 `tools/sync_installed.py` 只复制本地仓库已有内容，不自动拉取远端；会拒绝覆盖检测到的个人修改。[发布与同步说明](docs/releasing.md)

## 方法与证据范围

方法参考 Monterey 翻译框架、fake-english、[usage-evidence](https://github.com/xionglingsong/usage-evidence)、ATA 错误分类、简明语言与 EU 写作指南、UN 与 APA 包容性语言指南，以及业务规范。各方法的用途和适用范围见[整合映射](docs/method-provenance.md)、[简明语言来源](skills/tis-plain-language/references/sources.md)、[包容性语言来源](skills/tis-inclusive-language/references/sources.md)与[业务来源](skills/tis-client-service/references/sources.md)。

[真实译稿讲评案例](docs/examples/courier-translation-diagnosis.md)保留已授权的材料及证据边界；[双语检索实查](docs/bilingual-acceptance.md)记录实际访问限制。五份 EU 指南的 [536 页阅读记录](docs/source-reviews/README.md)说明资料覆盖范围，不证明模型理解或学习效果。自动测试验证数据、结构与操作边界，不替代教学质量或读者测试，也不构成机构认证。

完整口译训练、录音复盘及客户项目全生命周期自动化仍待扩展。本 README 参考 [dbskill README](https://github.com/dontbesilent2025/dbskill/blob/fe58a23f93203989ad6a1aef88c1cbb533491efc/README.md) 的阅读顺序，功能与安装方式以本仓库为准。

本项目公开供安装使用，整体尚未声明开源许可证；公开可见不等于授予任意再分发或改作许可。Ngram 脚本保留原项目的 [MIT 许可](skills/tis-usage-evidence/LICENSE.ngram)，版权 PDF、私人语料与用户阅读记录不随包分发。

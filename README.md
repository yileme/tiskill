# tiskill 是什么

tiskill 是 [@译了么](https://xhslink.cn/o/3UlkBC8GKzqv) 制作的口笔译学习与执业工具箱，共 10 个 Skill。当前版本 **[0.11.0](VERSION)**。

安装到 Claude Code、Codex 等可导入或读取 Skills 的 Agent 后，可以在对话里直接使用。豆包、WorkBuddy 是否可用，取决于所用产品版本是否提供 Skills 导入或读取能力；普通聊天窗口不等同于 Skills 安装环境，本文不承诺它们支持下方自动安装命令。

Skill 是一套写给 Agent 的做事方法。装好 tiskill 后，你可以让 Agent：

| 你手上的任务 | 可以交给 tiskill 的工作 | 得到什么 |
| --- | --- | --- |
| 准备翻译，或已有一份初稿 | 分析读者与用途、比较译法、对照原文诊断 | 修改理由、可试的译法、针对性练习 |
| 不确定英文表达能不能用 | 核对词义、搭配、语域和具体语境 | 实际来源、短引文、本句的使用条件 |
| 不确定代词、性别或身份称谓是否合适 | 对照原文、本人称谓与客户规范作局部审校 | 必要修正、有条件建议、可保留或待核实的判断 |
| 通知、邮件或说明写得绕 | 调整信息顺序，删重复，保留事实与条件 | 可直接使用的改稿及必要说明 |
| 客户需求散落在聊天里 | 整理笔译、口译或本地化需求与计价依据 | 待确认问题、报价和回复草稿、项目简报 |
| 想用真实材料练听说 | 安排听辨、跟读、复述或情景输出 | 一次练习、基于实际产出的反馈与自评 |

## 更新

**0.11.0：共 10 项技能。** 新增包容性语言审校，处理英文和中译英中的代词、性别与身份称谓；区分原文、本人称谓和客户规范，按语境给出局部修改建议。[变更说明](docs/changes-0.11.0.md)

本次公开更新也包含 **0.10.0 双语译例检索**：从译之有道、热词译、Linguee 发现候选，再回查原始出处和目标语用法。Google、Bing、DuckDuckGo 是可尝试的网页搜索路径，不是稳定 API；验证、登录、限流或无关结果会限制检索，备用路径也不保证取得证据。[实查与限制](docs/bilingual-acceptance.md)

已通过 skills CLI 安装的用户，重新运行以下命令即可更新并补齐新增技能：

```bash
npx -y skills add yileme/tiskill -g --all
```

重装可能覆盖自行修改的技能文件，请先备份。`tis-update` 按安装渠道处理更新；本地托管同步只复制本地仓库内容，不会自动拉取远端新版。

## 快速开始

### 1. 安装到你的 Agent

先安装 [Node.js](https://nodejs.org/)（包含 npx），然后在终端运行：

```bash
npx -y skills add yileme/tiskill -g --all
```

这会以用户级方式安装远端已发布的全部 Skills 到 skills CLI 支持的全部 Agent 目标（0.11.0 共 10 项）。只想安装到 Claude Code 和 Codex，可用：

```bash
npx -y skills add yileme/tiskill -g --agent claude-code codex --skill '*' -y
```

只查看有哪些技能、不安装：

```bash
npx -y skills add yileme/tiskill --list
```

自动安装的宿主范围以 [skills CLI 文档](https://github.com/vercel-labs/skills#supported-agents)为准。安装后重新打开 Agent 会话；其他提供 Skills 导入功能的产品，可下载本仓库并导入 `skills/` 下完整技能目录（保留 references、scripts 等文件）。

### 2. 用一句话交代任务

在 Agent 对话中输入：

```text
/tis 请检查这句中译英，读者是美国公众。先指出最影响意思的问题，再给最小改法。
原文：该申请尚未获批。
初稿：The application has been approved.
```

材料较长时，附上全文和用途即可。已有原文、初稿或客户聊天会沿用，不必为了切换技能重新粘贴。命令名称以所用 Agent 显示为准。

### 3. 在同一个对话里继续

直接补充要求，例如“先保留我的句式”“给我一道检查否定信息的练习，先不展示答案”或“我改好了，请再看这一处”。反馈会围绕当前问题推进；需要完整报告时再提出。

## `/tis` 怎样处理你的任务

你可以只说想得到什么，由入口选择技能；也可以直接调用下方目录中的命令。

- **还没动笔**：先理清读者、用途和不能改变的信息，再比较关键译法。已有初稿且需要教学讲评时，接着做诊断。
- **已有译稿**：先对照原文检查意义；涉及英文表达疑点时，先筛查，再查证。可接受的变体与风格选择会保留，同一问题不重复计错。
- **找双语译例/回查译法**：从原文发现候选，分别核对聚合站、原始出版者和完整句对，再检查目标语用法；受限时报告实际备用路径。
- **只查一个表达**：直接查它在本句中的词义、搭配或语域，给出证据和使用条件。
- **想把文字改清楚**：按受众、语言和地区选择编辑方法。默认最小修改，明确要求重写时再重组全文。
- **问代词或身份措辞**：按英文或中译英的实际语境检查，尊重本人称谓与原文；机构偏好不当成普遍错误，不自动扫描每份译稿。
- **准备接洽客户**：进入业务流程，整理范围、报价与待确认事项；不把客户项目当成教学评分。
- **想练听说**：先确认真实材料和音频是否可用，再安排一次练习。只有文字时，反馈也限于文字能支持的内容。

## 看看实际会得到什么

### 译稿讲评：先修意义，也保留写对的地方

下面来自一次真实快递业中译英诊断，**讲解经过编辑节选，并非聊天逐字实录**。

> **原文：**这将使中国有可能超越美国成为世界上最大的快递市场。
>
> **初稿：**It will make China over America to become the biggest courier market in the world.
>
> **反馈要点：**这里的 `over` 没有承担“超越”的动词功能，“有可能”也遗漏了。可以改成：
>
> This will make it possible for China to overtake the United States and become the world's largest courier market.

同一份稿子的 `12 billion`、`9 billion` 换算正确；`packet` 有英式邮政义，不能仅因推荐 `parcel` 就判错；“China has many special shopping days like this.” 可以保留。讲评既指出该改的地方，也说明为什么有些地方不用改。

之后布置了四道练习，尚未收到作答，因此没有学习成效或分数可报告。题目统计属于旧练习材料。本案例已获用户授权公开；原稿、修订示范及证据范围见[完整案例](docs/examples/courier-translation-diagnosis.md)。

### 简明语言：让读者找到自己要做的事

简明语言适用于公众沟通、教育、健康、行政、商务、技术及本地化文本。以下原稿和改稿均为编写的示例，不是真实用户材料或效果实测。可以这样提问：

```text
/tis 请把这份家长通知改清楚，先写家长要做什么。保留日期、费用和例外条件。
原稿：为进一步做好本次活动的相关组织工作，请各位家长于10月25日前完成报名信息的填写与提交。活动费用为每人50元。已报名的家长无需重复提交。
```

**改写示意：**

> 请于10月25日前提交报名信息。活动费用为每人50元。已报名的家长无需再次提交。

这次改写删除了没有新增信息的铺垫，保留截止日期、费用和例外。健康信息、法律条件、术语与译文中的限定同样需要保留。“去 AI 味”按重复和信息贡献处理，不检测作者身份；简明语言也不等同于 Easy Read（易读版）。方法见[通用编辑参考](skills/tis-plain-language/references/general.md)。

### 客户接洽：从聊天到报价与项目草案

先确认客户允许使用相关 AI 工具，再提交真实沟通材料。在已有客户聊天的对话中，可以这样请求：

```text
/tis 请根据上面的客户聊天整理项目。
先列已知需求和关键待确认问题，再给报价草稿、Markdown / JSON 简报和回复草稿。
单价或费用不明确的地方留待确认，先在这里给我核对。
```

处理顺序如下：

1. **提取需求。** 区分人工笔译、明确约定的机器翻译译后编辑（MTPE）、口译和本地化范围；记录用途、交付物、时间、工作量及消息来源，保留已明确、提议中和待确认的事实。
2. **核对计价。** 按实际范围与约定单位计算，检查重复收费。没有默认单价或系数，未知费用不算 0；口译半天、全天包含多少小时也要约定。
3. **交付草稿。** 给出简报、报价、沟通草稿和变更/决策记录。尚未谈妥的支付、修改轮次、保密、AI 使用与验收条件继续待确认。
4. **按需建档。** 你明确要求保存后，在已配置的本地目录建立未签约项目草案，分别存放简报、报价、往来草稿及原文、译文、资源和交付物目录。

没有真实客户材料时只给[空白模板](skills/tis-client-service/templates/brief.json)。报价不表示合同成立；本地 CLI 不发送消息、不上传客户数据，实际接受与履约由人工核对。字段、计算规则和建档命令见[业务说明](docs/business.md)。

## 全部 10 项技能

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
| [`/tis-update`](skills/tis-update/SKILL.md) | 同步本机已安装的技能 | 差异检查与受控同步 |

用法查证需要 Agent 能搜索并打开网页；听说反馈取决于环境实际处理音频的能力；保存需要本地写入权限。可选 Ngram 脚本另需 Node.js 和 curl。

## 安装与更新

### 只安装一项技能

```bash
npx -y skills add yileme/tiskill -g --skill tis-plain-language --agent claude-code codex -y
```

单项技能可以直接使用；`tis` 入口会根据任务读取其他技能，使用入口时建议安装全部 10 项。各 Agent 的命令显示方式可能不同，也可以直接在对话中说明要使用的技能。

### Claude Code 插件方式

本仓库也提供一个包含全部 10 个 Skills 的 `tis` 插件。在终端运行：

```bash
claude plugin marketplace add yileme/tiskill
claude plugin install tis@tiskill-skills
```

插件方式的入口是 `/tis:tis`，单项示例为 `/tis:tis-plain-language`。选择 skills CLI 或插件任一方式即可。清单结构和命令依据 [Claude Code 官方文档](https://code.claude.com/docs/en/plugin-marketplaces)。

### 更新

通过 skills CLI 安装时，重新运行上面的安装命令取得当前远端版本；通过 Claude Code 插件安装时运行：

```bash
claude plugin marketplace update tiskill-skills
claude plugin update tis@tiskill-skills
```

仓库的 `tools/sync_installed.py` 是可选的本地托管同步适配器，只同步本地已有内容，不从网络拉取新版。使用它前先读[发布说明](docs/releasing.md)并检查 `--help` 中的目标目录；它不负责更新 skills CLI 或 Claude Code 插件安装的副本。

版本提醒脚本使用 `TIS_UPDATE_URL`，或本地 `~/.tiskill/source.json` 登记的来源；未配置来源时跳过。公开公告地址为 `https://raw.githubusercontent.com/yileme/tiskill/main/UPDATE.json`。提醒不自动安装。

## 可选：保存记录，或打开 CAT 工作台

### 在 Obsidian 积累材料

默认在对话中输出，明确要求保存后才写文件。记录放在**现有 Obsidian vault 内的独立 tiskill 文件夹**：

- `01-查证记录`、`02-表达积累`、`03-练习复盘`：保留来源、核对状态、回答和自评。
- `05-业务知识`、`06-客户项目`：保存业务参考与授权建立的未签约项目草案。

在本机 `~/.tiskill/library.json` 的 `path` 字段配置该文件夹的绝对路径，私人路径只留在本地。记录使用 Markdown；配置与保存命令见[知识目录说明](docs/library.md)，客户建档见[业务说明](docs/business.md)。完整笔译诊断还可保存为 Markdown 讲评与累计错误表，见[报告与记录](skills/tis-translation-diagnosis/references/report-and-records.md)。错误频次不等于个人能力分数。

### 在浏览器逐段编辑

需要翻译网格时，在仓库根目录运行：

```bash
python3 cat/server.py --port 8765
```

打开 <http://127.0.0.1:8765>，即可编辑纯文本段落、保存译稿、使用术语与记忆库、添加备注，并导出 Markdown、HTML 或 DOCX。只编辑译文无需模型。

段落讨论需要本机已安装并登录的 **Codex CLI**。页面讨论是独立会话，会把当前段原文、译文和本段近期对话交给 Codex；建议先展示修改预览，经你确认才写入，并可撤销。

CAT 目前是单项目教学原型，尚不支持文档格式解析、内联标签或 TMX/TBX 互通。查证记录和练习归档放在 Obsidian。详细功能、数据位置及限制见 [CAT 使用说明](cat/README.md)。

## 方法从哪里来

方法资料来自于 Monterey 翻译框架、fake-english、usage-evidence、ATA 错误分类、简明语言与 EU 写作指南、UN 性别包容性语言指南、APA 2023 包容性语言指南，以及 GB/T 19363.1—2022 等业务参考。工作顺序是明确任务与语境、核对意义、查证表达，再转成修改和练习；各来源的具体作用如下。

| 来源 | 在 tiskill 中的用途 | 依据与范围 |
| --- | --- | --- |
| 独立技能 `monterey-translation-framework`、`fake-english` | 任务分析、候选译法取舍与自查；词义、结构、搭配和语域风险筛查 | 已选择性整合核心原则，可独立安装，不要求运行时加载原技能或私人语料；不自动跟随原技能更新。见[整合映射](docs/method-provenance.md) |
| [usage-evidence](https://github.com/xionglingsong/usage-evidence) | 对具体英文用法做词典、语料与领域文本查证 | 结论依赖本次实际取得的证据；频率不等于正确性。见[查证来源选择](skills/tis-usage-evidence/references/sources.md) |
| ATA 错误类别及教学参考 | 对照原文解释问题，安排针对性练习 | 用于教学诊断，不提供官方评分、认证或通过预测。见[类别与判断依据](skills/tis-translation-diagnosis/references/categories.md) |
| 简明语言、EU 写作与翻译指南，以及中英文技术和本地化参考 | 按读者组织信息，检查句法、条件与术语，保留意义 | 通用编辑原则、地区惯例和机构出版规范分别使用。见[来源索引](skills/tis-plain-language/references/sources.md)与[EU 任务边界](skills/tis-plain-language/references/eu-guides.md) |
| UN 英文性别包容性指南、APA《Inclusive Language Guide》第二版（2023） | 代词、性别与身份措辞的有条件审校 | UN 机构指南与 APA 美国语境分别使用；保留 singular they 的分歧，不抹掉原文、法律范围或本人自称。见[来源与阅读范围](skills/tis-inclusive-language/references/sources.md) |
| GB/T 19363.1—2022、ATA 采购指南、AIIC 职业伦理及报价参考摘录 | 人工笔译流程、客户接洽、服务范围与报价检查 | GB/T 的适用范围排除机器翻译结果及其译后编辑、口译；其他服务支持不据此宣称符合该标准。报价摘录是可协商模型，不是强制费率。见[业务来源与页码](skills/tis-client-service/references/sources.md) |

截至 0.9.2，五份 EU 指南已形成 **536 个独立 PDF 页面的逐页阅读记录**，包括 *Clear English: Tips for Translators* 的 17 页。阅读成果已整合进相关技能参考；版次、日期与页码见[完整阅读索引](docs/source-reviews/README.md)。这说明资料阅读覆盖范围，不证明模型理解或读者效果；[验收样例](docs/clear-english-acceptance.md)也不是已经完成的效果试验。

来源打不开或证据不足时，结论保留“待核实”。引用机构资料不构成 ATA、AIIC、ISO 或其他机构的认证与背书；标准现行状态及具体访问限制以相应来源记录为准。

## 当前范围与后续方向

**已实现：**笔译实践与诊断、英文用法查证、简明语言编辑、包容性语言审校、真实材料听说练习、客户接洽与未签约建档，以及可选的 Obsidian 保存和本地 CAT 编辑。

**待扩展：**完整口译训练、录音复盘和客户项目全生命周期自动化。当前不提供自动发音评分，也不会把未签约草案自动推进为已接受或执行中的项目。本版具体变化见 [0.11.0 变更说明](docs/changes-0.11.0.md)。

本 README 的阅读顺序参考 [dbskill v3.0.1 的 README](https://github.com/dontbesilent2025/dbskill/blob/fe58a23f93203989ad6a1aef88c1cbb533491efc/README.md)（2026-10-18），功能与安装方式均以本仓库实现为准。

本项目已公开供安装使用，整体尚未声明开源许可证；公开可见不等于授予任意再分发或改作许可。随附 Ngram 脚本保留原项目的 [MIT 许可](skills/tis-usage-evidence/LICENSE.ngram)；原始版权 PDF 和私人语料不随包分发。

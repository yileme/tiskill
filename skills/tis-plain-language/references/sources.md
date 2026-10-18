# 来源与适用范围

以下材料用作按项目选择的参考，不作为统一评分表。用户提供的本地 PDF 只在本机读取；分发包只记录名称、版本与章节线索。

| 来源 | 核对位置 | 用途与边界 |
| --- | --- | --- |
| [Apple Style Guide](https://support.apple.com/guide/applestyleguide/welcome/web), June 2026；本机 `apple-style-guide.pdf` | Introduction；passive voice（PDF p.154）；localization（p.129）；International style（p.239–243） | 产品术语、面向本地化写作及地区格式；Apple 品牌名称规则仅用于相关产品 |
| [Google developer documentation style guide](https://developers.google.com/style) | About this guide；Active voice；Sentence structure；Procedures；Global audience；UI elements | 开发者文档的可执行步骤、受众和清晰结构；在线内容会变，引用具体细则时复查原页 |
| Microsoft English (UK) Localization Style Guide；本机 `eng-gbr-StyleGuide.pdf`，46 页 | §2 Voice；§4.1.12 Punctuation；§5 Localization；PDF p.12 plain language | en-GB 软件本地化用法；仅在目标地区或客户指定 Microsoft 规范时采用品牌规则 |
| Microsoft Chinese (Simplified) Localization Style Guide；本机 `zho-chn-StyleGuide.pdf`，58 页 | §2 Voice / Word choice；§4.1.13 Punctuation；§5 Localization | zh-CN 软件本地化术语和标点场景；项目术语优先 |
| [阮一峰《中文技术文档的写作规范》](https://github.com/ruanyf/document-style-guide) | `docs/text.md`、`docs/paragraph.md`、`docs/marks.md`、`docs/structure.md`；仓库 README 标公共领域 | 中文技术文档的文本、结构与中英混排；字数界限是该指南的编辑偏好，不是翻译质量阈值 |
| [中文技术文档写作风格指南](https://zh-style-guide.readthedocs.io/zh-cn/latest/) | 语言风格、文档结构样式、标点符号、名称与命名 | 中文技术写作结构与语气；以实际项目规范为准 |
| [dbs-plain-writing](https://github.com/dontbesilent2025/dbskill/tree/main/skills/dbs-plain-writing) | SKILL.md、references/standard-and-scope.md | 产品介绍/更新说明的信息顺序与语义保护方法；此处重新归纳，不复制规则或 ASD-STE100 受控词典 |

不将本地下载路径写入运行指令，以免公开安装包依赖个人目录；PDF 不提交仓库。引用与具体判断回溯原始章节。ASD-STE100 的完整符合性需要指定版本标准与受控词典，本 skill 不提供认证。

## 新增的通用与领域来源（0.9.0）

以下身份从用户提供文件正文、版权页或末页核对。PDF 页从 1 起计；印刷页另列。所有 514 个 PDF 页面均已逐页提取，长篇材料按下列范围精读，不声称全文人工精读或实时网页核实。原 PDF 与完整提取文本均不随包分发。

| ID / 文件 | 实际身份、日期与范围 | 本次阅读及关键定位 |
| --- | --- | --- |
| EU-PL / `accessible-publishing-plain-language-guidelines.pdf` | *Plain language*；欧盟出版局 Accessible Publishing，© European Union 2026（PDF p.2）；2 页清单，区分 plain language 与 easy-to-read | 全文 2 页；PDF p.1 定义、重要信息优先、单段单题与术语；p.2 缩写与版权。无印刷页码，均用 PDF 页 |
| HSE / `HSE_Plain_Language_Guidelines.pdf` | *Plain language guidelines: How to communicate clearly with people who use our services*；Health Service Executive，Communications and Public Affairs Division；August 2025，HNC01094（PDF p.21 / 印刷 p.40） | 全文 21 个 PDF 页面，主要为双页跨页，不能直接当成 21 个印刷页。读者与语言范围 pp.6–7 / PDF p.4；词汇和结构 pp.9–12 / PDF pp.5–7；读者反馈 pp.16–18 / PDF pp.9–10；口头理解检查 pp.20–22 / PDF pp.11–12；术语 pp.24–25 / PDF p.13；检查表 pp.27–30 / PDF pp.14–16 |
| NEUBAUER / `file.pdf` | Anna Gabrielle Neubauer, *Euro-murkiness: Plain language and “fighting the fog” in European Union translations*；Université de Genève，翻译硕士论文，June 2011（PDF p.2）；存储库题名用单数 translation，作者显示为 Neubauer, Anna；2023-03-14 是存储库更新日期，不是论文出版日期 | 共 70 页，选择性阅读：PDF pp.1–5, 9–13, 53–57（正文印刷 p.1 = PDF p.4）。重点为机构翻译约束 pp.7–10 / PDF pp.10–13，以及拆句、受众、译者增补权限 pp.50–54 / PDF pp.53–57。这是历史个案与作者分析，不是欧盟官方指南或当前效果证据 |
| EU-ISG / `ISG_en_4web.pdf` | *Interinstitutional Style Guide*；Publications Office of the European Union，Luxembourg 2026；文件声明 last update 15.10.2026（PDF p.3） | 共 306 页，选择性阅读 PDF pp.2–9, 67–69, 91–93, 104–105；视觉核对封面及末页。编号正文印刷页与 PDF 页相同。p.6 是机构出版范围；§4.2.2 pp.67–68 是逻辑结构；§5.6 pp.91–92、§5.7 p.93、§5.12 p.105 是层级、列表和表格规范。不是专门的 plain-language 手册；不把其欧盟出版规约普遍化 |
| FEDERAL / `Ch 02 Federal Plain Language Guidelines.pdf` | *Federal Plain Language Guidelines*；Plain Language Action and Information Network (PLAIN)，March 2011，Revision 1 May 2011（PDF pp.1–3） | 共 115 页；本文件附教学批注，批注作者/版本未明，不视为 PLAIN 正文。选择性阅读封面、前言、修订说明、目录及下列正文页。印刷 p.1 = PDF p.7；读者 pp.1–3 / PDF pp.7–9；顺序 pp.6–8 / PDF pp.12–14；主动与时态 pp.18–21 / PDF pp.24–27；义务 pp.23–24 / PDF pp.29–30；词汇与冗余 pp.34, 36–39 / PDF pp.40, 42–45；术语 pp.43–44 / PDF pp.49–50；条件 pp.48, 52, 54–58 / PDF pp.54, 58, 60–64；段落 pp.61–62, 64, 66 / PDF pp.67–68, 70, 72；列表与表格 pp.69, 72 / PDF pp.75, 78；空话 p.95 / PDF p.101；测试 pp.97, 99, 101 / PDF pp.103, 105, 107 |

来源定位入口：[HSE](https://www.hse.ie/plainlanguage)、[UNIGE 论文记录](https://archive-ouverte.unige.ch/unige:18416)、[ISG](https://style-guide.europa.eu/en/home)、[PLAIN 历史站点](https://www.plainlanguage.gov/)。这些是出处导航，未在本次联网验证可达性或现行版本。EU-PL 的出处按 PDF 末页 Accessible Publishing 标识确认。

## 采纳与不采纳

通用原则是受众、目的、信息顺序、具体用词、去无贡献重复与保持意义；面向教育和商务的操作建议是本技能据此作出的应用归纳。健康服务范围由 HSE 支持；行政公众沟通由 Federal 支持。不要把五份材料说成同一标准。

来源存在差异：EU-PL 的年级建议与 Federal p.1 的“按实际读者写”不能拼成普适年级门槛；HSE p.12 建议末尾回顾，不代表每个短回复都要总结；Federal pp.62–63 接受有作用的衔接和复述，不意味着重复结论都必要。ISG 的层级、列表标点、机构名称等只对对应出版项目适用。句长、字体、数字呈现和词表均不是通用自动判错规则。

HSE 医学词替换表只是编辑提示，不能把 negative 自动解释为无病、benign 自动等同无害。Federal 的删词、法律双词组替换示例也不能直接当作法律意义等价证明。保留必要定义、限定和安全内容；有疑问请领域核对。论文个案统计与指南转引研究未独立复核，不用于宣称本技能有效、提升百分比或适用全部人群。

本技能对“AI 式重复”的贡献检查是编辑方法归纳，不声称这些来源研究过生成式 AI 写作。完整提取不等于完整阅读；图像核对范围、实现与验收限制见仓库 `docs/plain-language-source-review.md`（独立安装无需该文件）。

## 0.9.1 完整阅读追加记录

上文“本次/选择性”保留为 0.9.0 历史记录；当前 EU-ISG 阅读范围为 PDF 1–306 全部，两个半卷合并无重复。新增 EU-GARDNER（59 页）、EU-CLEAR（16 页）、EU-DGT（138 页），四份共 519 独立页面。各自出版者、版次、日期、精确页码与适用规则见 [EU 指南](eu-guides.md)，机器可查范围见 `source-metadata.json`。其他来源阅读范围不扩大；尤其不能宣称 Neubauer、Federal 或此前选择性使用的技术指南全文精读。

## 0.9.2 译者句法补充

**EU-TIPS / `clear-english-tips-translators_en.pdf`**：*Clear English: Tips for Translators*，European Commission / DGT，编辑 Selim Earls，© European Union 2014（PDF 17），无编号版次；PDF 2026 生成日期不作出版年。全读 17 页并核对双栏与脚注；PDF 1–2 无印刷页码，3–17 同印刷页。累计五份 EU 逐页记录为 536 页。新增的句法骨架、隐藏条件、分词信息与法规句界检查见 [独立参考](clear-english.md)；不复制替换词表，也不将简化示例作为删译或法律等价授权。

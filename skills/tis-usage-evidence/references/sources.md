# 按判断类型选择证据

本清单提炼自用户自有 `usage-evidence` v1.18.1 的 `references/sources.md`。访问状态和页面结构会变，下面的链接与路径只是检索入口；下结论前须打开当次实际页面，核对其文字、来源和语境。

| 判断 | 首选 | 需要实际核对什么 |
| --- | --- | --- |
| 词义及语域 | [Oxford Learner’s](https://www.oxfordlearnersdictionaries.com/)、[Cambridge](https://dictionary.cambridge.org/)、[Longman](https://www.ldoceonline.com/) | 目标义项原话、语域/地区标注、真实例句；单个词条未收录不等于不存在。 |
| 搭配与可用性 | 词典搭配例句、[Linggle](https://search.linggle.com/)、[Google Books Ngram](https://books.google.com/ngrams/) | 比较相同语法框架和同义范围中的搭配；读计数口径。Linggle 可用 `_` 查询未知位置；Ngram 比较短语时保持地区、年代、大小写一致。 |
| 真实例句与搭配发现 | [SkELL](https://skell.sketchengine.eu/) Examples（concordance）与 Word Sketch | Examples 看词或短语所在句；Word Sketch 按语法关系找搭配，再点击搭配核对例句。核对词性、义项及主宾/修饰关系，不能凭同句共现判定搭配。 |
| 译法候选发现 | [译之有道](https://yizhiyoudao.kuaizhan.com/)、[热词译](https://www.reciyi.com/)、[Linguee](https://www.linguee.com/) 双语词典与对齐例句 + 目标语词典/语料 | 核对原始来源链接、出版者及来源质量、两侧完整语境、领域、译向、义项及用途是否匹配；平行句是参照，不是标准答案。 |
| 专业与学术语域 | 领域官方文件、客户术语表、[OpenAlex](https://openalex.org/)、[PubMed](https://pubmed.ncbi.nlm.nih.gov/) | 核实术语由谁使用、是否同领域。OpenAlex 对含冠词/介词短语的计数可能退化成词袋；PubMed 要核对查询是否保留完整短语；不能直接拿粗略命中数证明搭配正确。 |

可先用已安装的浏览器读取词典页面与语料页面；必要时使用适用的 CLI 工具。`scripts/ngram.mjs "candidate A,candidate B"` 可以比较 1900–2019 图书语料近十年比例，必要时加 `--corpus en-US-2019` 或 `en-GB-2019`。若命令失败或语料不能覆盖目标场景，换一个合适来源或标注未能查证，不凭模型语感补齐。

## SkELL：真实例句与搭配发现

具体操作见 [SkELL 检索协议](skell.md)：短语先查 Examples，单词基本形式的搭配发现查 Word Sketch；以实际界面核对词性与关系。可用 `scripts/bilingual_queries.py --source skell` 离线生成编码入口，再用浏览器读取结果。词典受阻时可转此路取得真实用例，但不补造词典释义。协议区分访问失败、零匹配、展示例句数、总命中和每百万词频率，并规定引文与本句推断的边界。

## Linguee：双语词典与对齐例句

从 [Linguee 首页](https://www.linguee.com/)选择页面实际提供的语言对并检索，用词典条目和双语对齐例句发现译法候选。官方站点的 [context 英德检索页](https://www.linguee.com/english-german/search?source=auto&query=context)将词典与“External sources (not reviewed)”分开显示；外部例句带来源链接，不应与词典条目混作同等证据。此链接仅为已访问的界面示例，不证明其他语言对、查询或本句译法已查证。

- **核对与记录**：记录查询词、实际语言对/检索方向、实际结果 URL、访问日期及逐字短引语；双语例句须保留两侧文字及原始来源链接。打开原文核对完整上下文、领域、出版者与来源质量，确认原文/译文方向及与待译句相同的义项；检索方向不等于原文的翻译方向，无法确定时明确标注。来源链接失效或上下文不足时说明限制，并用目标语词典/领域语料交叉核实。
- **结论边界**：对齐和翻译可能不完善；命中只提供候选参照，不是规范正确性的证明，查无结果也不证明表达错误。页面打不开、只返回空壳或未取得实际结果时标记“待核实”。只记录实际访问的结果链接，不把自行生成的查询 URL 模板当成已验证入口，也不假定 API、语言覆盖或当前命中情况。

输出格式：`判断：…；事实：“逐字短引语”或当次检索统计，[来源名](实际访问的 URL)；本句适用性：…；建议：…`。每点精选 1–2 条有支撑力的证据。不要把本参考中的说明、示例和来源地址冒充已访问的查证结果。

## 视频口语：YouGlish / PlayPhrase

[YouGlish](https://youglish.com/) 和 [PlayPhrase](https://www.playphrase.me/) 是发现真实音视频用例的网页入口。通过当前可用浏览器在页面检索，记录实际结果/原视频 URL、短引文及确实定位的时间点；不要推测查询参数、内部接口或承诺存在公开 API。可用地区、登录、额度、反自动化与播放器权限可能限制访问；失败就报告该源待核实，不编造片段和字幕。

核对说话场景、角色、体裁、地区及语域；影视台词和演讲不是所有日常场景的代表。字幕只支持文字层证据；只有实际听取的音频才支持声音观察。用户说自己已听过，应写“用户确认”，不声称 Agent 已听。来源原始链接或完整上下文不可见时保留限制。口语频率不能由少量返回片段推算。用于听辨、跟读、复述时路由至 tis-speaking-practice。

已逐页读过的 EU 四份指南及概念/用法证据分工见 [EU 来源](eu-guides.md)；它们是版次限定的参考，不代替当次领域与用法查证。

双语原文发现、Google/Bing 精确 site 检索、访问状态与出处去重规则见 [双语检索](bilingual-retrieval.md)。

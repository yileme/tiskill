# 客户业务工具

# 业务 JSON 与 CLI

复制 templates/brief.json，值留空时必须是 `{"value":null,"state":"pending","source":{"message":null,"excerpt":null}}`。已知事实用同一结构，state=confirmed或proposed，source含实际消息编号与摘录。数字一律十进制字符串（或整数），不能用浮点、负数、NaN/Infinity。结构标识如id/model/service只是控制字段，不代表客户事实。conflicts与decisions是事实对象数组；未解冲突阻止最终总额。事实确认不等于合同接受。

`quote` 必须有 currency、minor_units（均事实对象）、scopes、pm、adjustments（三个数组）。minor_units显式0..4；逐行ROUND_HALF_UP后求和。省略的业务facts自动补pending，不省略责任条款。空数组表示没有列出的费用，不表示业务已确认免费；taxes/discount/rush等facts必须说明排除、不适用或具体约定，否则报价仍为provisional。

每个 scope: `{"id":"scope-a","model":"itemized","lines":[...]}`。model可选itemized/coefficient/localization/interpreting，scope ID唯一。不同范围的图文/工程可各自定价；同一范围禁止叠加模型。

每个 line 必需 id、coverage（事实对象，值为工作覆盖键数组）、included_pm（事实对象，布尔值）、pricing。全局coverage不得重复，代理必须先按实际文件/片段/任务划分统一覆盖键，不能靠改名绕开重复。不同任务如图中文字翻译与图像编辑用不同键，前者不能再计入主翻译词数。

pricing的quantity、unit、rate、rate_unit、basis全为事实对象。单位支持word/1000_word/character/page/image/hour/item/person_hour/person_half_day/person_day；只有word数量到1000_word单价自动除1000，其余必须一致。字词/字符basis值必须为 `{"side":"source","spaces":"excluded","method":"实际统计工具及版本/口径"}`，side可target，spaces可included/not_applicable。其他单位basis是约定计数说明，不可空。价格未知则null。

coefficient scope只容纳一个line，另需factors事实：值含difficulty/qualification/translation_type，每个是category与value；类别与范围见业务知识，process为命名分项到系数字符串的对象（tech/terms/preprocessing/style/pm/initial_self/bilingual/monolingual/proof/final/qa/tm_maintenance）。只纳入明确协商的分项，未列的工作须在范围事实说明；不得声称删减流程仍满足标准。process求和，再乘其他系数；没有默认。process有pm时included_pm须true；条件及附加费用用adjustments显式填写。

localization可加weights事实，其值为 `[{"group":"new","count":"1000","weight":"1"}]`；group唯一，统计不得重叠，quantity可null让工具推导或填完全一致的加权和，单位必须word。权重来源及分组统计放该事实的消息摘录。非加权工程/排版等采用普通pricing。

interpreting的time事实值为 `{"people":"2","sessions_per_person":"1","unit":"person_half_day","hours_per_unit":"3","agreement":"真实约定消息编号"}`。这是字段形式示意，不是默认人数或半天时长。quantity必须等于people×sessions_per_person，不能再带days字段。每种不同时长单独范围；差旅/设备/住宿/通信/协调/加班等未估明时以pending附加行保留。普通额外工作可另itemized范围。

pm项为id、basis事实（选定工作line id数组）、percent事实。排除PM/税、未知含PM状态和已内含PM的行，且同一行不得重复收PM。

adjustments项为id、kind（tax/discount/rush/condition/extra）、amount事实、rule事实。输入明确商定的金额和计算规则/基数；此版不自动解析税制或折扣表达式。discount金额以正值填写，计算时扣除。不同货币不得混合，不支持外汇转换。

仓库中运行 `python3 tools/business.py preview --input brief.json`；独立安装用 `python3 <skill>/scripts/business.py`。validate/preview输出计算检查JSON；quote/brief输出Markdown；这些不写文件。create --input brief.json --confirm按既有用户授权在library.json所选根的06-客户项目下创建完整文件包；空白模板不能冒充客户。init-library --confirm仅建知识、空项目索引。不更改配置，不覆盖现有内容，不复制原文件，不发消息。

每个项目包含briefs/brief_V01.json和.md、quotations/quote_V01.md、correspondence/drafts_V01.md、decisions/change_log_V01.md；originals/source、originals/target、resources、deliverables分开。初次发布原子化；同ID拒绝覆盖。后续人工新增V02等并保留V01，此版无自动修订/合同接受/执行状态迁移。所有输出需人工核对事实语义，CLI不能验证聊天摘录真实、资质真实或统计分组没有语义重叠。

设计见 [ADR 0003](adr/0003-client-service.md)，知识和来源见 [技能](../skills/tis-client-service/SKILL.md)。

建档原子发布在macOS/Linux使用排他rename；其他平台安全拒绝建档。并发CLI通过锁串行；现有目录、符号链接和空事实模板一律拒绝覆盖或建档。

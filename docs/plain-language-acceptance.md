# 简明语言人工验收

以下都是编写的示例与预期，不是真实用户材料、模型实测、医疗建议或法律条款。运行评估时将输入交给技能，人工核对意义和信息贡献，记录实际输出与偏差；不能用包含某词作为通过标准。本次只完成样例设计及静态核对，未开展 live 模型效果或目标读者试验。

| 场景 / 模式 | 改前 | 预期改后或处理 | 人工核对 |
| --- | --- | --- | --- |
| 中文重复 / 最小修改 | 关于材料提交，需要指出的是，请在周五前提交申请表。换句话说，申请表需要在周五之前提交。总而言之，按时提交申请表很重要。 | 请在周五前提交申请表。 | 保留动作、对象、期限；后两句无新贡献；不用“AI 检测”解释 |
| 健康信息 / 最小修改 | If your clinician has told you to use this medicine, you should take one tablet containing 5 mg once daily. Do not take a second tablet if you miss a dose. | If your clinician has told you to use this medicine, you should take one 5 mg tablet once daily. Do not take a second tablet if you miss a dose. | 保留 should 强度、临床前提、每次一片、5 mg、每日一次、漏服禁忌 |
| 健康检测 / 诊断 | A negative result does not rule out infection. | 可保留。不能改成 You do not have an infection. | 保留不排除感染，不能套 HSE 词表 |
| 法律义务 / 最小修改 | The tenant is required to provide written notice at least 30 days before leaving, unless the landlord agrees in writing to a shorter period. | The tenant must give written notice at least 30 days before leaving, unless the landlord agrees in writing to a shorter period. | 非法定引文的编辑示例；保留必须、书面、至少30天、例外主体和书面同意；不能改 should |
| 技术精确词 / 最小修改 | After completion of the configuration of `TLS 1.3`, perform a click on “Save” to save `{profile_name}`. | After configuring `TLS 1.3`, click “Save” to save `{profile_name}`. | 术语、版本、UI 和占位符逐字不变；不把 save 的必要对象当重复删掉 |
| 已简洁 / 最小修改 | 请于周五17:00前提交签字后的申请表。 | 原句保留。 | 不增标题、列表或第二次总结；不凑问题 |
| 教育说明 / 保留有效复述 | 分母表示一个整体分成了多少等份。例如，四分之一中的4表示分成4等份。 | 可保留。 | 第二句是具体教学例子，虽复用术语但有贡献 |
| 行政通知 / 整体重写 | 请注意有关领取事项。周一9:00至12:00可以领取证件。请携带身份证。领取地点为一楼服务台。 | 请于周一9:00至12:00携带身份证，到一楼服务台领取证件。 | 日期、时段、材料、地点和动作全部保留；可用一个句子，不必表格 |
| 商务 / 只诊断 | 我们可能在周三发货，这意味着周三一定发货。 | 指出“可能”与“一定”冲突，请核对承诺；不擅自决定哪项为真。 | 不用去重复掩盖事实冲突 |
| 翻译忠实 / CAT | Source: Only adults may apply. Target: 所有人均可申请。 | 仅成年人可以申请。 | 指出范围误译；after 为完整译文，走确认，不能改源文权限 |

检查两种语言均按读者选择语气，英文时态和情态保留，中文不套词数限制。全篇改写须逐项回查，诊断请求不变成默认全文重写。完成实际验收后另记结果，勿把本表的预期称为已通过。

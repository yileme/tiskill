---
name: tis-client-service
description: 从真实客户沟通整理笔译、口译或本地化项目简报、报价、沟通草稿和变更记录；支持授权后建立本地项目草案。
metadata:
  keywords:
    - translation quotation
    - interpreting quotation
    - client project brief
    - localization estimate
---

# 客户业务服务

先读[反馈与对话](references/voice-and-interaction.md)。这是生产业务流程，不是教学评分。读[业务依据](references/business-knowledge.md)、[来源](references/sources.md)和[输入契约](references/contract.md)。

1. 从当前真实聊天提取材料，不要求重发。没有客户对话时只提供空模板，不能假造订单、日期、联系人、接受记录或收费。每一事实保留 confirmed / proposed / pending 状态、来源消息编号与短摘录；confirmed 只表示消息明确支持，不表示客户接受报价。矛盾放入 conflicts，保留双方表述，等待解决。
2. 按服务范围路由：笔译（人工或明确约定 MTPE）、口译（交替传译/同声传译与现场/远程分开）、本地化（软件/文档与具体任务）。检查履约能力、语言方向、受众用途、交付物、时间与时区、资源、工作量口径及计价单位。不要把 GB/T 范围扩张到 MTPE 或口译。
3. 先给简报和关键待确认问题，再按每个 scope 唯一模型计算。2014 分项、2020 系数摘录、2013 本地化模型是可选择框架，不是强制费率。无默认单价/系数；未知费用不算零。范围重复、PM重复或单位不匹配必须修正。口译半天/全天小时数须明确协商。
4. 一次交付结构化 JSON、Markdown 简报、报价、沟通草稿、变更/决策记录。草稿带事实状态、消息来源及引用。预算、税、折扣、加急、支付、有效期、修改轮次、取消、保密、AI使用、验收、存储销毁与版权均显式待确认；不从报价推出合同成立。询价回复、缺项追问、报价说明、范围变更、交付验收、结项草稿均不发送。
5. 用户已授权建档时运行本目录 scripts/business.py create --input brief.json --confirm；否则 preview。库路径来自 ~/.tiskill/library.json；不要猜私人路径。授权后 init-library --confirm 初始化知识与项目索引，不建客户。项目只允许 precontract_draft；后续实际接受和实施由人工核对，保存新版本而非覆盖。
6. 交付前核对简报事实与原消息、所有计价依据、阶段人员与交付检查，保留原始文件引用。源文件与译文、资源、交付物、往来、报价和简报修订分目录。变更先确认影响和各方同意，才作为新范围；争议不悄悄覆盖旧记录。

CLI 只本地读写，不发送消息、不上传客户数据、不自动翻译或调用 CAT。AI/MT 未获许可不得输入客户材料到相关服务。公开包仅有提炼知识；源 PDF 只作本地引用。本工具不构成 ATA/AIIC/ISO 认证或背书。无法访问来源时列出精确 URL 与限制。

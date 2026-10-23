# Public service English acceptance

0.13.0 adds one standalone skill (12 total). Public artifacts contain authored summaries and metadata only. Design: [ADR](adr/0006-public-service-english.md).

Automated tests verify structural and filesystem boundaries, not language quality. The following 30 scenarios are authored manual acceptance criteria, not executed model benchmarks.

|Domain|Positive task|Out-of-scope task|Conditional/conflict criterion|
|---|---|---|---|
|通则|设施名|长篇法律意见|正式名称例外/警告强度|
|交通|站点指引|驾驶法律责任|临停和停车区别|
|旅游|景点标牌|历史学论文|博物馆转文化娱乐|
|文化娱乐|展厅名称|版权合同|排座数字冲突|
|体育|场馆入口|运动损伤诊断|场馆与场地|
|教育|校园导向|学历认证|正式校名优先|
|医疗卫生|门诊方向|诊疗方案|门口与方向指引|
|邮政电信|服务窗口|通信协议全文|历史业务与当前产品|
|餐饮住宿|酒店设施|过敏原诊断|菜名不推断配料|
|商业金融|银行网点|证券法律条款|商业广场功能|

Additional criteria: hospital restaurant selects per-row domain; missing registry stays pending; wrong source hash blocks stale evidence; OCR candidates cannot become recommendations; preserve annex symbols, client names and safety warning strength; plain/inclusive edits remain bounded.

Local source QA: 184 layout blocks (110 HTML, 74 image-only), 74/74 image blocks recovered by local Vision OCR, zero failures; all OCR remains candidate. Ten representative table rows (one per part) visually compared against originals and marked verified transcription only. Original culture number reversal and business informative-annex label visually checked. Official individual records for all ten standards displayed current at the 2026-10-23 lookup; recheck for each project. No full row-by-row proofreading or semantic benchmark was performed.

Private index statistics: {"records": 9126, "verified": 10, "candidate": 9116, "rejected": 0, "layout_blocks": 184, "html_blocks": 110, "image_only_blocks": 74, "html_rows": 3532, "ocr_lines": 5594}. Occurrences include overlaps/repetition; not a unique terminology count. Sources remain private and raw-file hashes unchanged.

Validation executed: seven synthetic unittest cases; existing update-notice/modified-copy/rename checks; metadata validator; EU-source validator. Scoped tis + new-skill managed apply/check passed. Installed CLI successfully queried a verified row from an unrelated working directory. Unrelated installed diagnosis files remained byte-identical. Private index generation v2 adds Markdown provenance; v1 retained.

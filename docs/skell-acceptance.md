# SkELL 0.12.2 实查与离线验收

访问时间：2026-10-22T22:46:46+08:00。以下是历史实查记录，不是未来查询的实时证据。

正常浏览器打开 https://skell.sketchengine.eu/#result?f=concordance&lang=en&query=status%20quo ，等待页面加载后核对查询框 status quo、English、Examples。可读 40 行；标题为 “status quo 5.14 hits per million”；页脚 skell_3_11 / v1.11.11。总命中数未见，未反推。读取渲染 DOM innerText 消除可访问性快照的高亮边界粘连后，逐字短例句为：

- 第 17 行：“They learn to accept the status quo .”
- 第 19 行：“The status quo is unsustainable for all sides.”
- 第 20 行：“My bottom line was to retain the status quo .”

保留页面空格和标点。查询页可读句子，但本次未取得各句原始出版者或全文；这些例句仅验证检索链路，不是特定用户句子的适用性或词典释义证明。没有用展示条数证明频率。

官方帮助 https://www.sketchengine.eu/skell/ 已读取 Examples 内容及页面 DOM 中 Word Sketch 帮助面板。点击标签后可见正文仍停在 Examples，故用正常页面 DOM 读取已载入的 tab-id-2-content，未请求隐藏接口。原文：“Type a word in its base form and click Word Sketch.”、“Click a collocation to see examples in context (concordance).”；说明默认先显示最常见词性，可切换词性，Context 可显示较宽的典型组合。未实测 Word Sketch 结果或多词输入支持，不声称短语均不支持。

离线回归只验证 URL 编码、CLI 与元数据，不验证实时可用性或语言结论。CAPTCHA、429 与零匹配分支为操作规范，本次未触发；不能写成现场验收通过。

自动验收：tools/validate.py、tools/test_update.py、tools.test_bilingual 的 5 项测试、实际本地参考链接检查及 git diff --check 均通过。限定 tis 与 tis-usage-evidence 的 check/apply/check 完成，末次 Up to date；诊断与独立 usage-evidence 文件哈希未变。未执行公开推送。

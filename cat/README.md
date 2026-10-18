# tiskill CAT（本地原型）

## 启动

```sh
python3 cat/server.py --port 8765
```

浏览器打开 `http://127.0.0.1:8765`。服务只监听 `127.0.0.1`，原文和译文默认写在 `~/.tiskill/cat/project.json`；可以用 `TIS_CAT_DATA` 改数据目录。页面支持 Markdown、HTML 和 DOCX 导出。

## 界面

界面按桌面 CAT（memoQ、Wordfast Pro）的翻译网格组织，而不是普通网页表单。

- **段落网格**：每段一行，列为「段号 / 状态 / 原文（只读）/ 译文（可编辑）」。左侧栏位显示段号，重复原文会标出「重复」。
- **段落状态**：未开始、已编辑、已确认，对应桌面 CAT 的 Not started / Edited / Confirmed。状态显示在段号右侧和底部状态栏。
- **工具栏**：上一段、下一段、确认译文、撤销修改；按状态过滤（全部 / 未开始 / 已编辑 / 已确认 / 重复）；快速查找原文或译文。
- **四区工作台**：左上翻译网格，右侧全高段落讨论（输入框始终可见），左下「记忆库 / 备注 / 段落历史」，右下术语（本地检索、在线查证、CSV 管理）。桌面上下约 65% / 35%，各区独立滚动；窄屏依次堆叠。
- **状态栏**：当前段号、状态、进度条、三段状态计数、译文词数与字符数。
- **自动保存**：停止输入约 0.7 秒后写入本机；切换段落立即保存。一个段落保存失败不会影响其他段落。

## 快捷键

沿用桌面 CAT 的确认与换段习惯。macOS 用 ⌘，其他平台用 ⌃。

| 按键 | 作用 |
| --- | --- |
| ⌘/⌃ + ⏎ | 确认当前译文并跳到下一段 |
| ⌘/⌃ + ⇧ + ⏎ | 确认当前译文，但停在原段落 |
| Alt + ↑ / ↓ | 在译文单元格内切换上／下一段 |
| ↑ / ↓ | 在网格上移动当前段落 |
| PgUp / PgDn | 向上／向下翻一屏 |
| ⌘/⌃ + A | 选中当前段落的全部译文 |
| Esc | 放弃本段未保存的编辑 |
| ⏎ | 在网格上进入当前段落的译文 |

界面里点「快捷键」可以查看同一张表。

## 使用

新建项目可粘贴多段原文，每行一段；选择段落后编辑译文，失焦或停止输入后自动保存。右侧「讨论」面板默认针对当前段。模型返回修改建议后会出现改前改后预览；点「应用修改」写入，支持撤销。提议只修改当前段，刷新页面后译稿仍在本机。已有项目重新导入会要求确认，旧项目会被替换；要留存请先导出。

讨论栏现使用本机 Codex Agent（需安装并登录），不再调用 Ollama。每次请求携带当前原文、译文和本段最近对话，通过只读沙箱运行，用户确认修改建议后才写入译文。独立于 Ekko 当前聊天，不共享全部主会话上下文。可用 TIS_AGENT_MODEL 指定模型，否则沿用本机 Codex 配置。请求期间显示处理状态；失败消息保留在讨论栏。Ekko Studio 直接桥接实测认证失败，尚未接通。

术语和记忆库按项目挂载 CSV。原文和译文选区分别按段保存，点击「选区添加术语」预填当前段的选区；术语卡可直接编辑译文，保存同时核对版本及旧译文，冲突时保留输入并提示重新检索。

## 与桌面 CAT 的差距

这是教学原型，不是 memoQ 或 Wordfast Pro 的替代品。目前没有：

- 专业上下文匹配与标签感知算法；当前记忆库为本地字符相似度。
- 双语对齐、预翻译及 TMX/TBX 互通。
- 内联标签、格式与 DOCX/XLIFF/PPTX 解析。只处理纯文本段落。
- 锁定段落、审校角色（Reviewer 1/2）、签名与交付流程。
- 多文档与多语言对：当前只有一份本地项目。

网格布局、段落状态命名、`⌘/⌃ + ⏎` 确认并跳段、按状态过滤等惯例参考 memoQ 12.6 官方文档的 [The Grid](https://docs.memoq.com/current/en/Workspace/the-grid.html) 与 [Advanced filters](https://docs.memoq.com/current/en/Workspace/specify-segment-status.html)。Wordfast Pro 的具体快捷键与状态名未在本机核对，因此未照搬。

## 验证

```sh
python3 -m unittest cat.test_exports cat.test_server cat.test_resources cat.test_agent
```

测试覆盖导入、版本冲突、提议应用、撤销、导出、静态页面关键结构，以及确认段落后落盘。

## 导出与验收

点击右上角「导出译稿」选择单语译文、上下双语对照或左右表格对照。三种均支持 DOCX；导出前等待当前输入保存成功，保存失败时停止下载。单语导出略过空译文，对照保留空译文位置。DOCX 默认中文 SimSun（宋体）、英文 Arial；字体不嵌入，打开文件的机器必须安装相应字体。macOS 缺少 SimSun 时可能替换为 Songti SC，不能视为精确宋体验证。Markdown 不携带字体。

默认入口为 http://127.0.0.1:8765，默认数据在 ~/.tiskill/cat/project.json。更新服务代码后，在启动服务的终端按 Ctrl+C，再重新运行启动命令；重启不会删除项目。8766 仅用于独立验收样稿，不是默认项目。

## 资源与快捷检查

记忆库标签包含现有 TM 与项目内检索；资源操作使用带说明的图标按钮。备注按段落显式保存，换段保留未保存草稿；冲突保留输入并提示合并。段落历史直接展示现有撤销栈，最近记录在前；撤销会移除对应记录，没有时间戳，也不构成完整审计轨迹。

GET `/api/segments/{id}/details` 返回 note、history 和 projectId；PATCH `/api/segments/{id}/note` 接收字符串 note（最多 5000 字）、expectedNote，可带 projectId 防止导入替换后的误写。备注独立落盘，不改变译文 version 或 revision。

术语与记忆条目使用 UTF-8 BOM CSV 保存，默认 terms.csv / tm.csv 位于数据目录。导入 CSV 通过页面选择文件，最小列为 source,target,sourceLocale,targetLocale；库名称和项目挂载记录另存 libraries.json。旧 resources.json 保留原件，首次读取时迁移。直接用表格软件编辑 CSV 时先停止 CAT 服务，避免并发覆盖；保留表头及 id 等管理列。

讨论快捷操作实际加载仓库内 skill 文件：“检查搭配”使用 tis-usage-evidence 与 tis-real-english；“简明语言”使用 tis-plain-language 及全部 Markdown 参考（通用方法、语言和来源），适用于各领域译文；默认最小修改，已简洁则保留，不能以简化为由省略源文信息；“检查歧义”检查不同解读与限定。Agent 通过 Codex CLI `--search` 启用实时搜索（已核对 CLI 帮助），证据以本次实际访问为准，不自动把建议写入译文。

在线术语查询优先热词译并允许专业来源交叉核对。实测 reciyi.com 超时，NIH/NCI 返回临床试验词条证据；不能保证每个站点随时可访问，失败应明确显示。网页内容是证据材料，不具有修改应用或用户文件的权限。

资源接口：GET/POST `/api/libraries`，GET `/api/library.csv?id=…`，GET/POST/PATCH `/api/resources`。挂载请求使用 libraryId/mounted，导入使用 name/kind/csvContent。资源操作使用当前项目 ID；新导入项目生成 UUID，既有 local 项目保留 ID。未挂载库不可检索、修改或下载。

## 本轮验证记录（2026-10-18）

详见 [VERIFICATION.md](VERIFICATION.md)：34 项 Python 测试及浏览器选区、术语编辑、CSV 导入导出与挂载通过；真实 Agent 两条请求返回成功。在线回复缺少逐字引文，完整证据合规尚未验证，热词译页面未成功打开。默认 8765 已更新，默认数据文件哈希未变化。

## 知识与练习归档（0.7.1）

查证、表达和练习已迁至现有 Obsidian vault 内的知识文件夹；CAT 仅保留编辑、TM、术语、备注、历史和讨论。旧 evidence.sqlite3 不删除，备份迁移见 [library CLI](../docs/library.md)。服务不加载证据脚本或提供证据/练习 API。

回归：`python3 -m unittest discover -s cat -p 'test_*.py'`；`python3 -m cat.run_browser_tests`（已有 Playwright/Chrome，使用临时数据与随机端口）。

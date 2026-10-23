---
name: tis
description: 口笔译学习与执业工具箱入口。根据任务进入已实现的笔译诊断与练习；用户说“找双语译例/回查译法”或询问可用能力、版本和更新时也使用。
metadata:
  keywords:
    - translation interpreting skills
    - translation training toolkit
    - interpreting practice toolkit
---

# tis：口笔译技能工具箱

先读 [反馈与对话](references/voice-and-interaction.md)，按其规则控制讲评篇幅和语气；下文的证据、任务与保存边界仍须遵守。

使用当前对话中已有的原文、译文、受众、目的和用户反馈，判断现在需要什么。不让用户为了选择 Skill 重发材料，也不宣称未实现的能力已经可用。

- 用户要公共服务场所名称、标志、导向、警示、指令或短通知的中译英、双语审校或批量问题表：读取 `tis-public-service-english`，按实际场所和功能定位标准，缺本地来源时明确待核实。
- 用户要读网页剪藏、EPUB、PDF 或 Markdown，积累词块、复述和制作氢刻文件：读取 `tis-reading`。
- 用户要接洽客户、笔译/口译/本地化报价、整理聊天简报或建立客户项目：读取 `tis-client-service`；这是生产业务，不走教学诊断。
- 用户准备动笔、比较译法、请求翻译任务分析或译后自查：读取 `tis-translation-practice`；如已有译稿且要求系统教学诊断，再读取 `tis-translation-diagnosis`。
- 用户提交原文与笔译初稿、要求错误诊断或针对性练习：读取 `tis-translation-diagnosis`；中译英涉及 Chinglish/表达自然度时按需读取 `tis-real-english`，再通过 `tis-usage-evidence` 核实，避免重复计错。
- 用户要“找双语译例/回查译法”或从原文发现翻译候选：读取 `tis-usage-evidence` 的双语检索参考，核对聚合站与原始出处，再查目标语用法。
- 用户单独询问某个英文译法、搭配、词义或语域是否成立：读取 `tis-usage-evidence` 并查证本句；用户要筛查整篇假英语时先读 `tis-real-english`。
- 用户要求简明语言改写、删重复套话或改清楚公众、教育、健康、行政、商务、技术与本地化文本：读取 `tis-plain-language`，根据目标语与地区选择对应参考；英文用法有争议时结合 `tis-usage-evidence`。
- 用户明确询问包容性语言、性别、代词或身份表达，或当前审校发现相关局部问题：读取 `tis-inclusive-language`，处理已请求范围，分清原文、翻译与客户规范；不自动扫描所有译稿或强制接力。
- 仅询问能力或使用方法：说明目前有笔译实践决策、假英语筛查、笔译诊断、针对性练习、译法查证、简明语言改写与审校，以及英文/中译英包容性语言审校；可以提交原文、译文和翻译任务说明。现有真实语境听说练习；客户业务支持简报、报价与授权建档；完整口译训练尚在规划。
- 用户要真实语境的听辨、跟读、复述或情景口语：读取 `tis-speaking-practice`；无可访问音频时保持待核实，只开展文字可支持的练习。
- 用户要求更新 tiskill：读取 `tis-update`，按其步骤同步已安装的官方副本；只询问版本或变动时先回答，不执行更新。
- 未覆盖的任务：说明具体缺口，按已有材料完成当前能做的部分，不假装调用不存在的子技能。

材料够用就读取所需技能并在本轮开始处理，不只返回推荐或要求用户重发命令。接续时保留目标、已改内容、证据缺口和用户最新反馈；这些是当前对话状态，不自动另建存档。仅缺关键原文或会改变判断的条件时问一个具体问题。

每次进入本入口，先以当前 `VERSION` 对应的参数运行同目录 `scripts/check-update.py`，例如 `python3 <本 Skill 目录>/scripts/check-update.py 0.13.0`。优先使用 `TIS_UPDATE_URL`，否则从本机 `~/.tiskill/source.json` 读取同步时登记的仓库位置；找不到来源时跳过检查；脚本没有输出或网络失败时正常继续；若输出新版提醒，原样放在本轮结果末尾。只有上一条助手回复明确带此提醒时，用户单独回复 `1` 才表示更新，并读取 `tis-update` 执行。版本参数与仓库根目录 `VERSION` 必须同步，CI 会检查。

用户要求打开轻量 CAT 编辑器时，使用仓库 `cat/README.md` 的启动方法在本机打开页面。先说明页面聊天和 Ekko 当前聊天不是同一会话；页面通过已安装并登录的 Codex CLI 提供自然语言建议。

## 可选 Obsidian 保存

查证、表达积累和练习复盘属于现有 Obsidian vault 内的 tiskill 文件夹，不放入 CAT。默认在对话中输出；用户明确要求保存才写入。先读取 `~/.tiskill/library.json` 的 `path`（配置不存在时不猜测私人路径），用 `~/.tiskill/source.json` 的 `repo` 找到仓库及 `docs/library.md` 的 JSON 输入契约。可直接按目录内模板写 Markdown，或运行 `python3 <repo>/tools/library.py save --input <record.json> --confirm`；此参数只表达已有保存授权，不代替实际核实。

查证保存到 `01-查证记录`，表达到 `02-表达积累`，回答和自评到 `03-练习复盘`。文件名 `YYYYMMDD_主题_V01.md`，保留 ID、日期、来源、限制与核对者；待核实 `unverified` 与 `text_read` / `audio_checked` 分开。CLI 已核实状态要求用户确实核对并明确确认，不从链接、字幕或生成内容推定。练习可引用已存记录的 `sourceId`，CLI 保存当时完整快照；没有来源时保持待核实，不编造来源。模型练习题标作练习，不作为真实引文。保存后检查文件存在，返回实际文件链接；同名使用新版本，已有 ID 不覆盖。

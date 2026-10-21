# 版本与发布规则

## 版本

采用 `主版本.次版本.修订版本`。修订：不改变已有任务行为的修正；次版本：新增能力或兼容改进；主版本：改变使用方式或不兼容输入输出。从 `0.1.0` 起步，`0.2.0` 纳入译法查证；`0.3.0` 增加结构化教练讲评与保存记录；`0.4.0` 增加实践决策与假英语筛查；`0.5.0` 增加本地 CAT 编辑器；`0.6.0` 增加按目标语与地区处理的技术写作审校，0.x 阶段仍需在公告中写清行为变化。

每次发布先修改 `VERSION`，然后同步 `UPDATE.json`、Marketplace 的 metadata 与每个插件版本，以及 `skills/tis/SKILL.md` 中的本地版本参数。运行 `python3 tools/validate.py`、`python3 tools/test_update.py` 和 `python3 tools/sync_installed.py --check`，检查实际变更与个人资料。发布前在新样例上验证子技能行为。

`UPDATE.json` 的 `notice` 用一句话讲用户得到的改进，`details_url` 在远端发布后指向可核查的变更记录；不要把未上线能力写进公告。版本提醒只通知，不自动安装。`tis-update` 接受明确的同步请求，在检查哈希、差异和用户改动后才复制。

## 仓库与安装

此 Git 仓库是技能唯一开发真源，`skills/<name>/SKILL.md` 为公开安装内容。Ekko Profile 目录是受控安装副本，不在那里开发。`tools/sync_installed.py` 用清单记录最近一次托管内容的哈希，并在本机 `~/.tiskill/source.json` 登记仓库位置；修改过的安装副本不会被覆盖。新增子技能时同步更新 README、插件清单、同步脚本中的允许列表和验证。

本地 Git 提交记录版本变动。公开仓库 yileme/tiskill 已发布独立审计快照（0.9.2）；其历史与本开发仓库分离，开发仓库没有配置 remote。不得把开发历史直接推送到公开仓库。发布需单独授权并从审计分发快照进行；0.11.0 在用户授权后从公开 main 追加审计快照，同时包含 0.10.0；不创建 tag 或 GitHub Release。隔离发布目录为 `.ekko-tmp/public-0.11.0`，其 origin 指向 `https://github.com/yileme/tiskill.git`，公开基线为 `095489cdf6f9bf937bc6cc80eaa4b21830cf4e56`。开发仓库仍不配置 remote。远端发布后设置 `TIS_UPDATE_URL` 为该仓库的 raw `UPDATE.json` 地址；不在脚本里猜测仓库已经公开。不要提交学员原稿、客户文件、版权 PDF、本地路径或凭据。

0.7.0 增加独立证据卡、自评练习历史和有边界的听说 Skill；验收见 evidence-acceptance.md。

共享表达规则以 `docs/voice-and-interaction.md` 为真源；编辑后同步十个 `skills/*/references/voice-and-interaction.md`，`tools/validate.py` 检查一致性。独立安装不依赖仓库外路径；CAT 从仓库真源加载。0.7.2 人工质量检查见 `voice-acceptance.md`，未执行不能当作通过。

技能更名的托管迁移规则与旧标识退役说明见 [0.7.3](changes-0.7.3.md)。归档位于同步清单旁的 `retired-skills/`，不位于 Profile 技能目录。

0.8.0 新增生产业务技能与离线报价/项目工具；运行 tools/test_business.py。业务资料只公开释义与来源页码，不包含原PDF、私人路径或客户数据。

0.9.0 扩展通用简明语言；来源核对见 plain-language-source-review.md，人工验收见 plain-language-acceptance.md。自动验证不替代实际读者测试。

0.9.1 强化 EU 来源参考；运行 `tools/validate_eu_reading.py` 核对四份逐页笔记的完整唯一范围、元数据和引用链接。人工任务见 eu-guides-acceptance.md，不能把结构验证当成效果试验。

0.9.2 增加 EU-TIPS 的 17 页，累计五份 536 页；同一阅读验证器检查新增身份与两个独立技能参考的一致性，CI 运行该检查。

0.10.0 双语证据：运行 `python3 -m unittest tools.test_bilingual tools.test_library`；实查状态见 bilingual-acceptance.md。未发布时 UPDATE.json 不含尚未上线的 details_url；发布时再补公开变更链接。

0.11.0 新增 `tis-inclusive-language`，共十项技能；来源与视觉核对范围随技能分发，八项人工验收见 [inclusive-language-acceptance.md](inclusive-language-acceptance.md)。运行既有 metadata/update 检查及托管 check/apply/check；不修改 CAT 或私有知识目录。

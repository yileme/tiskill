---
name: tis-update
description: 更新本地安装的 tiskill 官方技能副本。用户明确要求升级、同步，或上一条更新提醒后回复 1 时使用。
metadata:
  keywords:
    - update tiskill
    - tiskill upgrade
    - translation skills version
---

# tis-update：更新 tiskill

先读 [反馈与对话](references/voice-and-interaction.md)，按其规则控制讲评篇幅和语气；下文的证据、任务与保存边界仍须遵守。

仅当用户明确要求更新，或上一条助手消息含更新提醒且用户回复 `1` 时执行；只是询问有无新版时仅检查。先确认安装渠道。通过 skills CLI 安装时，使用 `npx -y skills add yileme/tiskill -g` 并选择原安装的技能和 Agent；Claude Code 插件使用 `claude plugin marketplace update tiskill-skills` 后运行 `claude plugin update tis@tiskill-skills`。下文只适用于本地托管同步适配器；其源仓库由 `TIS_REPO_DIR` 指定，或从 `~/.tiskill/source.json` 的 `repo` 读取，未配置时请用户提供实际仓库位置，不猜测开发机路径。优先读取其中 VERSION 和技能目录。没有远端时不说已经取得网络最新版。

执行 `python3 <仓库>/tools/sync_installed.py --check` 查看本机托管副本的差异；用户已要求同步时执行 `python3 <仓库>/tools/sync_installed.py --apply`。脚本处理仓库允许列表中的 13 项技能（含 `tis-medical-paper`）；遇到用户修改过的副本或来源不可识别时跳过并报告，不覆盖它们。修改后再次执行 `--check` 验证。若用户另外安装了 Claude Code 插件，且明确要求更新该渠道，可使用该渠道自身的插件更新命令；不以全局安装覆盖其他技能。

更新提醒从 `UPDATE.json` 读取；没有配置 `TIS_UPDATE_URL` 时只读本地仓库的公告。发布远端后设置该 URL 为公开仓库 raw UPDATE.json 地址，随后可跨机器接收新版通知。禁止在没有用户更新指令时静默同步。

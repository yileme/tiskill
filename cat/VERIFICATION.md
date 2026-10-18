# CAT current-change verification — 2026-10-18

Verification only; no implementation rewrite and no commit. Isolated fixture server: http://127.0.0.1:63865 (8766 was occupied), data under `.ekko-tmp/cat-verification/data`.

- PASS: `python3 -m unittest cat.test_exports cat.test_server cat.test_resources cat.test_agent`: 34 tests, 0 failures, 0 errors (0.583 s).
- PASS: executed the existing `cat/test_selection.js` in Chrome through Playwright: independent source/target selections, per-segment retention/isolation, obsolete panels removed, three quick actions.
- PASS: selected pair added through dialog, inline target edit persisted as `设备 → medical device`, version 2. Repeated harness runs produced two fixture entries; no default project changes.
- PASS: real file-input CSV import for terms and TM; imported libraries automatically mounted; browser CSV downloads contain the expected `临床试验,clinical trial,zh-CN,en` entry and BOM; unmount removes each write destination, remount succeeds.
- PASS: screenshot visually inspected at 1600×1100: right sidebar vertically stacks terms, translation memory (including project concordance), and discussion. Old standalone 段落 tab / segment-info absent. No browser page errors. Sections have independent scrolling; screenshot captures their current scroll positions.
- PASS: actual Codex-backed plain-language HTTP request, action `plain`: HTTP 200 in 12.6 s; reply “译文简洁，基本保留原意，无需修改。”; proposal null.
- PARTIAL: actual online terminology request for 临床试验: HTTP 200 in 28.8 s. Reply recommends clinical trial(s), links NIH, and honestly states Reciyi page could not be opened. It reports a Reciyi search-result snippet as preliminary only. The reply omits the required verbatim source quotation. Thus online routing/response capability is exercised, but full evidence-format compliance and actual upstream page-read trace are unverified; do not call this complete evidence validation. Reciyi page access did not succeed. No fabricated success claim.
- PASS: stale default PID 54093 started before server edits; revalidated exact command/cwd and terminated only that PID. Replacement PID 56011 serves 8765, GET /api/project returns 200. All preexisting default data file SHA-256 hashes unchanged. No mutation requests sent to default port.

Artifacts: `.ekko-tmp/cat-verification/tests.txt`, `browser.txt`, `plain.json`, `online.json`, `terms-download.csv`, `tm-download.csv`, `final.png`. Browser harness corrected two test-harness-only issues (waiting for a closed dialog to be visible; ambiguous name selector); no application defect was established by these failures. Agent calls were exercised via HTTP, not by clicking their browser buttons; button-to-live-response end-to-end remains unverified.

Screenshot: `.ekko-tmp/cat-verification/final.png`（本地验收产物，不随仓库分发）.


0.7.0 补充：独立证据卡、保存卡驱动的三类自评练习及有边界的听说 Skill 已实现。最新范围、隔离验证及限制见 ../docs/evidence-acceptance.md；此前记录为历史验收，不代表本轮重新联网实测。

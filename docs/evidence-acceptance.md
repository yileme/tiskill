# Historical 0.7.0 acceptance

Superseded architecture: see [0.7.1 acceptance](library-acceptance.md). The CAT evidence UI and API described below are no longer exposed.

# 0.7.0 evidence acceptance

Validated locally on 2026-10-18 after implementation; source websites and paid models were not called.

- `python3 -m unittest discover -s cat -p 'test_*.py'`: 43 passed. Includes HTTP persistence, unsafe URL rejection, explicit user confirmation, invalid input atomicity, two concurrent writers/one winner, edit/delete conflicts and attempt snapshots surviving card deletion. Existing exports/resources/agent/server regressions passed.
- `python3 tools/validate.py`, `python3 tools/test_update.py`, `python3 tools/test_diagnosis_save.py`: passed both before and after the coherent 0.7.0 release bump.
- `python3 -m cat.run_browser_tests` with existing Playwright module and installed Chrome: evidence, layout, chat, terminology and selection suites passed. Fixture creates a temporary data directory and random-port server, then closes its own server. Chat/online term calls are intercepted.
- Browser evidence tests: save, reload, search, reopen, edit, manual verification required, literal malicious markup, three exercise modes, persistent history, stale-edit/attempt input retention, card deletion with snapshot history, 390px no overflow.
- Existing layout tests: drag/keyboard/bounds, reload persistence, 390px stack, notes/history; existing chat tests: pending/error/Markdown/XSS; terminology: CSV/edit/selection/conflict.
- `git diff --check`: clean.

Default server activation verified on 2026-10-18: the known port-8765 listener, PID 59570 (`python3 cat/server.py --port 8765`), was verified with cwd `<repo>` and restarted as PID 79520. Targeted macOS process inspection recovered its exact launch executable and all 25 environment entries in memory; values were neither printed nor persisted. The same argv, executable, cwd and environment were reused, with detached logging at `.ekko-tmp/server-8765.log`. `TIS_CAT_DATA` was unset and HOME resolved the data directory to `~/.tiskill/cat`. Only the verified PID was terminated.

Read-only HTTP checks against the activated default service: `/evidence.js` returned 200 with JavaScript content type and bytes identical to the current repository file; `/api/evidence` returned 200 with `{"items": []}`. `/api/project` retained ID `local` and title `教师节试译`. The actual browser rendered the evidence/practice tab and empty-card state with the same project title and no console/JavaScript errors; screenshot: `.ekko-tmp/activation-evidence-ui.png`. No save, practice submission, translation edit or other mutating API test was performed. The evidence GET initializes its separate `evidence.sqlite3` schema on first access; this occurred during the probe and is not a project/library migration.

SHA-256 snapshots before restart, after HTTP checks, and after UI inspection were identical:

- `project.json`: `8daa19a7d019da697f097bfd8fa98b31bc1f1eea07c4611a6e671e9955ae7843`
- `terms.csv`: `0c5b285fc2a610c4ebc9be6c04350960ee2f6e229f993fc442fdd7b95afbcc65`
- `tm.csv`: absent before and after.

Local activation report: `.ekko-tmp/activation-report.json` (no environment secrets).

No test writes to the user's default CAT project or libraries. Evidence fixtures use example.com and explicitly synthetic quotations; they are not live usage evidence. Verification status records explicit user confirmation, not machine-certified truth. Speaking behavior is documented guidance, not an audio-processing service; source playback/availability and pedagogical efficacy were not live-tested. Cards are local and shared across projects; attempt history is append-only in this slice. Unsaved inputs are guarded in-page but not durable until save.

Managed-copy sync: `--check` found four safe file copies and no conflicts; `--apply` copied the router, usage skill/source reference and new speaking skill; final `--check` reports Up to date. Existing edited copies would be preserved by the tool’s conflict guard.

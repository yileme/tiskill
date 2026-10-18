# Nested workspace correction

The editor and resource dock share the left column. Discussion spans the entire right column. The dock contains memory/notes/history tabs on its left and terminology on its right. Existing app.js, resources.js and details.js IDs and functions are retained.

Three independent separators use pointer capture (including cancellation/lost capture cleanup), focusable separator roles, orientation/control/value ARIA attributes, arrow keys (10px; Shift 40px), Home/End bounds, and Enter/double-click reset. Ratio preferences use folio.workspace.layout.v1; malformed values, nonfinite values and inaccessible storage are tolerated. ResizeObserver reclamps rendered sizes against current available space; resizing the viewport preserves preferred ratios. At <=900px the editor, resources and discussion stack, with independent body scrolling and no inactive separator tab stops. Discussion composition remains outside the scrolling conversation.

## Reference inspection (read only)

Reference: a local SwordfishEdu checkout (not distributed). Targeted source portions were read before implementation; no reference files were modified or copied into this repository.

| Exact source file | Inspected / used / not adopted |
| --- | --- |
| js/divider.js | FourHorizontalPanels construction, resize weights and drag-end sizing. Used the concept of nested independently sized containers; implemented original Pointer Events/ResizeObserver code instead of copying HTML drag/MutationObserver logic. |
| ts/translation.ts | ThreeVerticalPanels construction (around 223), right-panel FourHorizontalPanels resource assembly (around 1738), notes controls. Used separate editor/resource responsibilities; did not adopt the file pane, MT pane, right-side resource stack or Electron events. Searched undo/history identifiers; no corresponding segment-history implementation appeared in this file. |
| js/tmMatches.js | Match tabs, source/target presentation, origin/similarity and explicit accept action. Existing Folio memory/search/insert behavior retained; no new matching engine or AI feature added. |
| js/termsPanel.js | Term rows, selection, origin and retrieval action. Existing Folio terminology panel retained and moved into left-bottom dock. |
| js/notes.js | Segment identifiers, note tabs and add/edit/remove IPC. Retained Folio real per-segment note editor and optimistic-save guard; no Electron notes dialog adopted. |
| css/layout.css | Viewport shell/header/footer rules. Kept Folio shell styling; no absolute-position shell copied. |
| src/com/maxprograms/swordfish/ProjectsHandler.java | getNotes/addNote/removeNote routing and getNotes/addNote implementations around 2154/2308. Compared project/segment scope with Folio APIs; no backend migration needed. |
| src/com/maxprograms/swordfish/xliff/XliffStore.java | getNotes SQL around 1339 and note add/update persistence around 1590–1643. Confirmed real scoped note persistence concept; no SQLite/XLIFF schema adopted. Searched history/undo identifiers; no matching history implementation appeared in this file. |
| src/com/maxprograms/swordfish/MemoriesHandler.java | Concordance request validation and engine search around 189–235; HTML result generation excerpts. Retained Folio language-direction resource search and explicit TM writes; no Swordfish API/HTML rendering adopted. |
| src/com/maxprograms/swordfish/GlossariesHandler.java | Glossary routing and searchTerm around 534–559. Retained Folio mounted-library selection and conflict checks; no glossary-engine integration adopted. |

Compared against cat/server.py (details GET, note PATCH, change/undo and atomic JSON writes), cat/resources.py (CSV validation and directional search), and cat/public/{app,resources,details}.js. Notes/history are already real: history is an undo snapshot list, not a timestamped audit trail. No resource-server rewrite or data migration was warranted. The only server change registers /layout.js in the static-file allowlist. User storage paths and existing project data remain unchanged.

## Verification

- `python -m unittest discover -s cat -p 'test_*.py'`: 36 tests pass after final server change.
- `cat/test_layout.cjs`: real Chromium drags all three boundaries, verifies pointer capture and geometry, keyboard min/max/reset, reload persistence, extreme saved-size clamping, malformed/blocked storage, 960x600 shrink, 800px and 390px stack, resource controls, real note save/history, full-height discussion and pinned input. No page errors.
- Existing `cat/test_selection.js` executed unchanged by the browser test: PASS for independent/per-segment selections and discussion actions.
- Browser writes only used an independently launched loopback fixture server with TIS_CAT_DATA=.ekko-tmp/layout-verification/data. Default ~/.tiskill/cat/project.json SHA-256 verified unchanged; port 8765 was not used.
- Artifacts: .ekko-tmp/layout-verification/{desktop,clamped,mobile}.png, browser.log, python.log, server.json.

Rerun the browser test with PLAYWRIGHT_MODULE pointing to an installed Playwright package and CAT_FIXTURE_URL pointing to a disposable server with two segments and mounted resources. Optional CAT_TEST_OUTPUT sets the artifact directory. Browser uses installed Chrome. No commit was created.

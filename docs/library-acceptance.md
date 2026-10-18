# 0.7.1 acceptance, 2026-10-18

- Application-schema read-only inspection: 0 legacy cards, 0 attempts. Consistent SQLite backup verified with integrity_check; zero migrated record notes, no synthetic examples. Original SQLite retained byte-for-byte.
- Existing-vault project folder: 8 Markdown files (home, 3 category indexes, 3 templates, migration report), 4 subfolders, valid YAML delimiters and 14 resolved wikilinks. No nested vault or settings changes. Private pointer only in local library.json and vault/local operational files.
- 43 CAT Python tests pass, including removed routes returning 404 for reads and writes; existing project/export/notes/terms/TM/chat behavior preserved.
- 5 library tests cover explicit confirmation, field/URL validation, path safety, unique IDs/names, source snapshots, actual CLI invocation, complete legacy rows, edited/deleted source snapshots, retry and empty migration.
- Browser suites pass: evidence removal, selection isolation, drag/keyboard/mobile layout, note/history, safe Markdown/chat lifecycle, terminology editing/conflicts/CSV. Disposable data and random port; zero paid model requests.
- Update and diagnosis-save regressions pass; release metadata/frontmatter validation passes. Four managed skill files updated without conflicts, all eight match source; sync check is up to date.
- Known default CAT process identity, executable, working directory, data path and listening port verified before restart. Same environment retained without disclosure. Read-only live checks: project 200; evidence/practice APIs and evidence.js 404; HTML has no evidence tab/panel/script. Project, terms and original SQLite hashes unchanged.

Limits: checked evidence is an explicit human claim, not machine truth. No audio scoring or real source lookup was performed. Old schema has no full edit-history table; migration retains all available raw rows and attempt snapshots. CLI is append-only; cloud-synced multi-machine simultaneous writes are unsupported. General source prose edits do not silently update the stored JSON snapshot.

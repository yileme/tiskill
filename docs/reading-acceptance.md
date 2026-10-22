# 0.12.0 acceptance

Executed locally using synthetic isolated fixtures, not user books or learner work.

- 5 reading test methods: bounded MD + Unicode, selected two-page PDF, EPUB actual spine vs ZIP order, ZIP traversal / DTD rejection, originals unchanged, source proof guards, immutable attempts and snapshots, local evidence compatibility, card collision/quote validation, draft exclusion, 2/3-column literal XLSX and TSV row counts, export retry/revision opt-in, failed publication leaves no manifest, manual acknowledgement and next-day due with no mutation, standalone copied CLI.
- Combined reading/library/bilingual: 14 tests pass. Business: 16 pass. CAT regression: 45 pass. Update notice/modified-copy/7 rename scenarios pass. Diagnosis save and duplicate guards pass. Release metadata and 536-page EU source ledger validators pass. Python compilation passes. PyMuPDF emits dependency deprecation warnings only.
- Scoped sync installs tis-reading and tis; repeated scoped check is up to date. Installed contents byte-match source; installed --help runs. Scoped sync preserves unrelated ledger entries/files. Full sync correctly refuses a pre-existing modified diagnosis skill; it was preserved.
- Real vault receives only 07 reading index and a blank 04 template. Existing homepage bytes unchanged. Synthetic export samples remain outside repository/vault in workspace temporary artifacts.

Limitations: no Qingk external import test, no OCR/scanned-page support, no visual validation of arbitrary PDF reading order. Source/verification fields record explicit human claims, not tamper-proof authentication. macOS/Linux CLI uses fcntl; Windows not validated. 0.12.0 results above describe local synthetic fixture checks before publication; they do not measure model teaching quality or learning outcomes.

## 0.12.1 publication checks

Repeated metadata/source validators, update/migration guards, diagnosis-save guards, 14 reading/library/bilingual tests, 16 business tests and 45 CAT tests: all passed locally. Four-layer feedback rules were reviewed against the requested style; this is not a model semantic benchmark. No actual Qingk import was performed.

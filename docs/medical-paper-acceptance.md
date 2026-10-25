# Medical-paper acceptance, 0.14.0

Implementation: thirteen skills, primary tis-medical-paper; ti-medical-paper is a routed shorthand. Public files are original guidance, bounded bibliographic locators and a standalone read-only search script. Private source PDF, split PDFs, full Markdown/JSON and images are excluded. AMA 11th edition (2020), title/copyright physically checked through extracted text on PDF pages 2–5; source has 1250 physical pages. Physical 24 corresponds to printed 1; main text offset is +23. Frontmatter has separate labels.

Source review: title/copyright, foreword/preface and contents were read; selected source-text passages were reviewed for article types, journal requirements, abstracts, manuscript structure, references, table presentation, authorship, ethics, preferred usage, drug naming, units, numbers, study design and statistics. See skill references/sources.md for actual page-level scope. Some initial bulk text output was truncated; only visible passages and subsequent bounded excerpts count as review. No claim of full-book close reading, all nomenclature coverage or complete table validation. No current AMA corrections, ICMJE or reporting-guideline versions were checked.

Synthetic behavioral scenarios below are review criteria, not an executed model benchmark:

| Input | Required response |
| --- | --- |
| OR 0.72, 95% CI 0.51–1.01, P=.06 | Preserve OR, endpoints and uncertainty; do not replace by RR or claim no effect |
| Retrospective cohort: exposure associated with outcome | Do not strengthen to proven prevention; flag causality if draft does |
| Primary mortality; secondary hospitalization | Keep endpoint hierarchy across abstract, text and translation |
| No significant increase in serious adverse events | Preserve negation, severity and uncertainty; do not state safe |
| Drug X 5 μg/kg/d intravenously | Preserve drug identity, dose, route and frequency; query ambiguity, no automatic mg conversion |
| Brand name supplied, generic uncertain | Retain and request actual identity evidence, no invented substitution |
| Outline and raw data; request whole paper | Provide plan and author queries; require user-authored substantive draft |
| Missing ethics number or DOI | Mark pending; do not invent |
| Narrative review for non-AMA journal | Check actual journal format; do not force IMRAD or numeric superscripts |
| Chinese translation of English abstract | Preserve comparisons, population exclusions, times, values and qualifiers |

Automated tests check candidate status, physical/printed/batch mapping, preservation of returned source text, absent matches, bounds, traversal and symlink refusal. They cannot validate medical semantics, translation quality, clinical correctness or publication readiness. Actual run results and conversion status are appended below after verification.

## Verified local result

Seven VLM batches cover physical 1–180, 181–360, 361–540, 541–720, 721–900, 901–1080 and 1081–1250. All seven were downloaded. Each result retains full.md, content lists, layout/model JSON and assets. Totals: 3,210,054 Markdown bytes; 620 image assets; 871,024,971 result bytes. Batch PDF counts, result layout counts, content-list page bounds and contiguous 1250-page map pass. All Markdown image links resolve. Original and batch SHA-256 checks pass; original remains unchanged. The manifest records hashes and batch statuses; private page map adds physical/printed/chapter/batch-local coordinates, including frontmatter labels.

103 low-text pages were inspected on six contact sheets for layout/content presence, not row transcription. 16 are visually blank; covers/title and table/figure/form/symbol pages explain the remainder. 86 text-bearing pages have separate unverified source-PDF text supplements. Several tables have missing table_body in MinerU JSON (eg physical 603, 960, 1020, 1022); retaining page slots is not complete searchable transcription. No claim of lossless text/table conversion. Original outputs remain unchanged; supplements are marked separately. Full source PDF remains the reference for all unresolved table content. Representative full-size visual checks: physical 54 (printed 31, abstract), 1005 (982, statistical reporting), 1250 (1227, final index). Converted excerpts were actually read across preparation, references, authorship/ethics, drug naming, units and statistical reporting; this is selected review only.

Repository metadata/structure validator passes; 3 standalone lookup tests and update notice/modified-copy/7 rename scenarios pass. Behavioral table above remains an unexecuted model acceptance matrix. Scoped installation covers tis, tis-update and tis-medical-paper; other installed skills are outside the synchronization selection. No public push.

Resume verification: all 662 result-artifact hashes and original/batch hashes rechecked locally without resubmission; existing QA annotations preserved. Metadata/private-path/link validation passes. Three medical lookup tests plus public-service regression tests pass; update notice, modified-copy guard and seven rename scenarios pass. Actual configured-source lookup returns three candidates. Scoped check/apply/check updated the outstanding sources.md and lookup.py copies, preserved all unrelated ledger entries, and diagnosis installation matches its preexisting hash checkpoint. CI now includes the standalone medical lookup tests.

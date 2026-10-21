# Markdown knowledge library (0.7.1)

Create a dedicated folder inside an existing Obsidian vault, not another vault. Set `~/.tiskill/library.json` to `{"path":"/absolute/path/to/existing/vault/project-folder"}`. Keep private paths in local config only. Alternate profiles pass `--config <file>`. Do not change Obsidian settings/plugins. Home and templates are stable names; records use `YYYYMMDD_主题_V01.md`, incrementing the suffix for filename collisions. IDs remain unique across the library. Manually edited Markdown stays user-owned.

## JSON input contract

`python3 tools/library.py [--config <file>] save --input <record.json> --confirm`

`--confirm` represents an explicit user request to save. Without it nothing is saved. JSON must be an object. Required `type`: `evidence`, `expression` or `practice`; required `title`: 1–80 characters, no path separators, controls or filename/link syntax. Optional `id`/`sourceId`: 1–100 ASCII letters, digits, underscore or hyphen. Omitted ID is UUID; duplicate IDs are refused. Optional `date`: ISO YYYY-MM-DD, defaults to OS local date. `createdAt` is generated UTC.

Evidence/expression require nonempty `expression`, `context`, `explanation`. Optional `quotation`, `url`, `timestamp`, `domain`, `register`, `query`, `accessedAt`, `limitations` are preserved. URLs, when supplied, must be HTTP(S) without credentials, whitespace or backslashes. `verification` defaults to `unverified`; `text_read` and `audio_checked` additionally require a real nonempty quotation, URL and literal `userConfirmed: true`. These are user claims, not automatic verification; do not fabricate values. Pending material may omit URL/quote. An AI-generated practice sentence is not source evidence.

Practice requires `kind`, `response`, `selfReview`; kinds may describe recall, translation, transfer, listening, shadowing or retelling. A real learner response is required. `sourceId` optionally links an existing saved record and captures its complete current stored JSON as `snapshot`; incoming snapshots are refused. Practice itself remains `unverified` and self-reviewed; source verification remains in the snapshot. No audio scoring. Source edits made only in prose do not alter the structured snapshot: review and save a new identified record to change its structured evidence.

All required content strings are at most 20,000 characters. Unknown metadata is retained in the full JSON payload. YAML provides searchable properties; wikilinks connect home and saved sources. Human prose and exact JSON are both retained. This small CLI is an append-only saver, not a database or editor; use Obsidian to read/search. Never remove the `tiskill-record` payload marker from CLI records. Malformed/duplicate stored records fail visibly. Library locks serialize cooperating CLI processes; do not run concurrent writers across cloud-synced machines.

## Offline 0.7.0 migration

`python3 tools/library.py migrate --database <CAT-data>/evidence.sqlite3 --backup-dir <local-backups> --confirm`

The source opens read-only using the archived application schema (`tools/legacy_evidence.py`). SQLite backup produces a consistent backup before exporting from that backup. Every card and attempt becomes Markdown. Complete raw database rows, original IDs, current versions, timestamps, unknown fields and attempt snapshots are retained in `legacyRow`/payload. Namespaced IDs prevent card/attempt collisions; filenames sanitize legacy titles. Deleted cards' existing attempt snapshots are still retained, with no broken source wikilink. Re-running skips identical migrated rows; changed rows fail for manual review. Existing records and source database are never overwritten/deleted. Backups remain local, outside public source.

0.7.0 has only current cards and attempts, no general card edit-history table. Migration cannot recover absent versions/deleted cards except the snapshots already in attempts. Legacy verification is preserved as a historical claim, not upgraded or newly certified. Full raw rows permit exact recovery. Partial migrations can resume; they are not cross-file transactions. Empty input produces zero records, never examples.

Run `python3 -m unittest tools.test_library` for disposable save/migration regressions. CAT's former evidence endpoints and script return 404.

## Optional bilingual evidence payload (0.10.0)

No migration or new required fields. Existing records remain valid. For evidence/expression, optional `bilingual` is preserved verbatim in the full JSON (unknown metadata contract); it is a documented convention, not an enforced semantic validator. Keep top-level `quotation`, `url`, `context`, `explanation`, `query`, `accessedAt`, `limitations` usable by older readers. Use:

- `sourceText`, `targetText`: exact complete short quotations, never assistant rewrites.
- `sourceLanguage`, `targetLanguage`, `translationDirection` (zh-en/en-zh/unknown), `directionBasis`.
- `aggregator`: `{name, url, publishedAt}`; `original`: `{publisher, sourceUrl, targetUrl, documentId, publishedAt, sourceLine, locator}`. Unknown values null; preserve sourceLine verbatim. All supplied URLs must follow the existing credential-free HTTP(S) rule (nested metadata is not automatically validated).
- `originalVerification`: unverified/verified; `originalVerificationBasis`; `reading`: `{aggregator, original, method, accessedAt}` describes actual access, independently of the top-level user-confirmed verification.
- `alignment`: `{status, basis}`; `applicability`: `{domain, register, audience, judgment, limitations}`.
- `retrieval`: list of `{url, query, method, status, relevantResults, retryAfter, accessedAt, limitation}`; use the states in bilingual-retrieval.md. `dedupeKey`: original document/version identity when known, otherwise unknown; copies are not independent evidence.
- `assistantRewrite`: separate optional suggestion, never sourceText/targetText.

A `text_read` retrieval/reading observation does not authorize a top-level `text_read` save. Keep `verification: unverified` unless the user actually confirms the evidence. CLI `--confirm` only authorizes saving. Save only on explicit request. Tests write real Markdown files in disposable libraries and verify exact pair/provenance preservation and immutable practice snapshots; fixtures are not external evidence or user notes.

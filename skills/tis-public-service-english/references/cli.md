# Standalone CLI contract

Python 3.10+ standard library. Run `python3 <installed-skill>/scripts/public_service.py --help`; repository tools/public_service.py is only a development shim.

- `configure /absolute/private/source --apply`: validates source-index.csv and content lists; default is preview. Configuration defaults to ~/.tiskill/public-service.json, outside repository. Existing conflicting configuration is refused. Global `--config PATH` supports isolated tests.
- `build-index --generation NAME`: read-only preview. Add `--apply` to create a new immutable public-service-index/NAME.json under sourceRoot. Existing generation is refused. No raw source file is edited.
- `search WORD --domain 交通 --generation NAME`: JSON, verified only, exact domain required. `--include-candidates` enables explicitly labelled discovery; unaligned OCR lines cannot be recommendations.
- `batch --input rows.json [--output review.json]`: no registry required; output is structural validation only. File creation is exclusive and refuses overwrite. IDs and every input row/condition are retained. No translation, semantic scoring, terminology replacement or AI call occurs.

Input example (synthetic):

```json
{"clientConditions":{"placeFunction":"校园东门导向","audience":"访客","properNames":{"status":"none"},"jurisdiction":"客户指定目标地区待确认","existingTermMap":{"status":"none"}},"rows":[{"id":"sign-1","source":"东门","initialTranslation":"","domain":"教育","scenario":"入口路牌","notes":"箭头方向待确认"}]}
```

Agent fills proposedTranslation, reason and evidence after actual review; retain pendingConditions and original input. Each evidence object should include standard/version, clause or table/row, pdf_page, status, source hash and applicability reason. Record client approval separately. Output null is an unfinished translation, never a completed batch.

Source CSV columns: part, domain, standard_id, sha256, md; md is a safe relative full.md path. Each sibling *_content_list.json uses MinerU type/table_body/table_caption/table_footnote/page_idx/bbox. HTML spans are expanded without semantic guesses; only numbered three-column rows become candidate pairs, all original cells and block provenance remain available. Physical page is page_idx+1; printed_page stays null unless explicitly checked.

Optional private derived-public-service-v1/recovery-ledger.json contains block id, relative crop, status, lines [{text,bbox}], method and errors. Optional row-reviews.json entries bind id/status/reviewer/method/zh/en/source_sha256/content_sha256; stale hashes or field changes reject build. No CLI command marks machine extraction verified. Build new generations after actual source review; preserve prior records. Do not hand-edit published generations. The raw source hash identifies the supplied PDF; content hash detects changes to extraction at query time. Verify original hashes during source QA before definitive citation.

Missing registry/index produces JSON status pending and exit 2. It is legitimate to continue from user-supplied text without local lookup. Exporting full private index into a public repository is outside this workflow.

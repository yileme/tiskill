# Local reading CLI

Python 3.10+, macOS/Linux (fcntl locks). Read library root from ~/.tiskill/library.json {"path":"absolute existing folder"}; --config overrides it. No network calls. All writes use --confirm only after authorization. Script path below is relative to the installed skill; repository wrapper: tools/reading.py.

```sh
python3 scripts/reading.py sources --input source.json --confirm
python3 scripts/reading.py study --input study.json --confirm
python3 scripts/reading.py card --input card.json --confirm
python3 scripts/reading.py listdue --on 2026-11-01
python3 scripts/reading.py export --confirm
python3 scripts/reading.py export --include-revisions --confirm
python3 scripts/reading.py mark-imported --input acknowledgement.json --confirm
```

All examples below are synthetic schema examples, not actual learner work. Replace file paths with local user-supplied paths; keep them out of public material.

Source: `{"source_id":"reading-001","title":"Selected article","path":"/absolute/local/clip.md","lines":"1-20"}`. MD/TXT alternatively `"bounded_document":true` (<=20KB, explicit whole small document). PDF requires `"pages":"2-3"`; EPUB `"chapter":2` means actual OPF spine position, not ZIP order. Web clipping adds `"url":"https://example.org/article"`. Optional verification: `"verification":"text_read","actual_read":true,"user_confirmed":true,"checker":"user"`; never infer this from extraction. `ocr_unchecked:true` forbids text_read. A changed source receives a new source_id; original snapshot stays immutable. Sources have revision 1 and hashes; later selections link their own stable source ID.

Study: `{"attempt_id":"attempt-001","source_id":"reading-001","stage":"practising","summary":"Learner original summary","response":"Learner original output","self_review":"Learner self review","selections":["chunk"],"prompt":"Write a short reply","criteria":["meaning","conditions"]}`. Optional date ISO YYYY-MM-DD. All extra learner fields are preserved. New attempts never replace earlier answers. The CLI captures its own canonical snapshot and local source link.

Card: `{"card_id":"card-001","source_id":"reading-001","locator":"lines 1-20","type":"chunk","question":"Explain this use","answer":"Synthetic example answer","hint":"Optional hint","origin":"model_generated","status":"draft","due":"2026-11-01"}`. origin source_quote requires quote exactly contained in source content; learner is also allowed. Confirm only with `"status":"confirmed","user_confirmed":true`. Revise explicitly with `"revision":2,"revise":true`; retain same ID for same card/sense, use a new ID for unrelated senses. Exact collisions and revision gaps fail. Drafts remain pending.

Outputs: 07-阅读素材 source/card notes; 03-练习复盘 study attempts; atomic exports/<batch-id> directory with regular.tsv + regular.xlsx (2 cols) and/or hint.tsv + hint.xlsx (3 cols). No header, no extra column. TSV tabs/newlines inside a field become spaces; XLSX cells are literal strings, including = + - @. Each workbook <=10MB. Citation defaults to title, locator and source ID; no automatic local-path metadata in cards. Do not put private paths in authored question/answer/hint. Manifest lists exact revisions and file hashes. Repeating export skips exported revisions; changed exported cards are reported and require --include-revisions (may duplicate cards if reimported). Files marked exported_not_imported never imply delivery or successful import. Manual acknowledgement: `{"batch_id":"batch-ID","user_confirmed":true}`; no network verification. Interrupted hidden .pending directories are not manifests and are not imported; successful failures clean their own staging folder.

Old evidence/expression JSON remains valid. Local evidence adds localSourceId instead of a fake URL. It requires matching quotation in the canonical source; text_read additionally requires that source text_read plus existing userConfirmed. The existing library.py save captures localSourceSnapshot, while practice sourceId continues to snapshot saved evidence/expression. 01/02/03 remain the shared knowledge structure.

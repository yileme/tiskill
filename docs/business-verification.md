# 0.8.0 verification

- All supplied PDF pages read: AIIC 5, ATA translation 10, ATA interpreting 10, GB/T 28. GB diagram PDF p19 visually read; p10/p17 checked against rendered text. No OCR dependency needed for body text. No source PDFs or private purchase data packaged.
- ATA client-assistance browser and HTTP: 403; directory, certification guide, Compass HTTP: 403. Actual landing-page link enumeration could not be completed. Local ATA PDFs are the verified content basis.
- tools/test_business.py: 16 tests passed (Decimal/rounding, unknown/conflict/proposed states, units, additive coefficients, weighted words, PM exclusion, interpreting negotiated time, costs, source evidence, blank-template refusal, path/symlink/collision protection and isolated creation).
- tools discovery initially 19 tests passed including 14 business tests and 5 library tests; two business edge cases then added and all 16 business tests re-run successfully. Diagnosis save and update scripts also passed, including seven rename migration scenarios.
- CAT Python unit suite: 45 tests passed; no CAT source change. Browser UI tests not run for this offline business feature.
- validate.py and git diff --check passed. CLI validate/preview/quote/brief/create smoke-tested with synthetic data in temporary storage. No synthetic project in LifeOS.
- LifeOS knowledge initialization succeeded through unchanged library.json; 06-客户项目 contains only its index. Managed install check/apply/check succeeded; new skill loaded through skill_view.
- macOS exclusive atomic publication exercised. Linux implementation and CI configuration added but not executed on Linux in this run. No external messages, customer data API calls, remote publication or real client project.

Known limits: CLI validates structure/arithmetic, not truth of chat evidence, semantic work overlap, professional credentials or compliance. Taxes/discounts are explicitly agreed amounts plus a rule, not an automatic tax engine. Subsequent revision/acceptance and operational contract states require human review; no automatic transition. Standard current status and excerpt full texts remain unverified.

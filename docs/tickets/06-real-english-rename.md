# Rename English screening skill

Spec: retire `tis-english-naturalness` in favor of `tis-real-english` in 0.7.3. Keep screening behavior, Ferguson attribution and independent fake-english unchanged. Update routing, CAT, distribution and documentation together; no compatibility alias.

Ticket: archive the retired installed directory outside skill discovery only when its complete file set matches the managed ledger. Unknown, changed, missing or symlinked content blocks the entire sync without writes. Preserve archived bytes and remove retired ledger keys after successful sync. Dry runs must not write.

Acceptance: validate metadata; test migration, repeat apply, modified/unknown/missing/symlink protection and new-name conflicts using temporary installs; run CAT agent regression. Verify default installed hashes and read-only CAT restart with unchanged user data. No public push or private library edits.

Completed: metadata validation, update/modified-copy protection and seven migration scenarios passed; 45 CAT tests (including seven agent tests), diagnosis-save checks and five library tests passed. Default sync check/apply/check passed; new skill discovery verified. Default CAT restarted with identical environment, unchanged read-only project response and all three data-file hashes unchanged. Independent fake-english hashes unchanged. Remaining old identifiers occur only in migration mapping/tests and rename documentation. No live model request was needed for this naming-only change.

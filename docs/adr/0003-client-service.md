# Client service workflow (0.8.0)

Production business support lives in tis-client-service, separate from teaching diagnosis and CAT. User authorization covers reusable knowledge and project-folder mechanics, not a fabricated customer order. No transcript exists at implementation time.

## Evidence and design

Read all 53 PDF pages locally with installed PyMuPDF; GB PDF page 19 is an image diagram, read visually, along with terminology and process pages 10 and 17. Sources and precise locators are in the skill references. CODE is AIIC, not ATA. GB/T 19363.1—2022 supplies Chinese process terminology; legacy 2014 wording is not mechanically equated with modern terms. 2020/2013 material is a user-provided excerpt, not an authenticated standard. ATA official web requests returned 403; PDFs remain usable, web claims remain unverified.

Input is a versioned JSON brief with evidence-bearing facts (confirmed/proposed/pending, message/excerpt), explicit scope IDs and one pricing model per scope. Missing facts stay null. Conflicts are recorded and block a final total. Rates and coefficients are never filled automatically. Decimal arithmetic uses an explicit currency minor unit and ROUND_HALF_UP per line, then subtotal; units and source/target count basis are explicit. PM references selected eligible lines only, excluding PM, tax and embedded PM. Duplicate coverage keys prevent charging the same work twice. Coefficient process terms are added, not multiplied. Interpreting time is per interpreter; person-days already aggregated cannot be multiplied by days again. Half/full-day definitions require negotiated hours.

CLI commands: validate, preview, quote, brief (read only); create (authorized draft folder only); init-library (authorized reusable notes only). Existing library.json path is preserved. Projects contain JSON, versioned brief/quote, communication drafts and decision log, separate originals/resources/deliverables/correspondence. Status is precontract_draft; quotation never signifies acceptance. Atomic directory publication under an advisory lock, collision refusal, safe IDs and symlink rejection protect existing files. No external APIs, file copying, message sending, CAT feature, certification or compliance assertion.

Public repository includes concise paraphrases, reusable templates and bibliography only; private source registry remains local. New skill is independently installable; deterministic CLI is packaged in its scripts and tools/business.py is a repository launcher. Shared voice, router, manifests, validation and safe sync are updated together.

## Acceptance

Test missing/contradictory facts, numeric rejection, rate units, thousand words, localization weights, additive coefficients, PM exclusion, pending expenses, negotiating half-days, rounding, unsafe paths, collisions and isolated project rendering. Run repository validation/update/library/diagnosis and CAT unit tests. Initialize only knowledge and empty project index in the configured vault. Local commit only; no publication.

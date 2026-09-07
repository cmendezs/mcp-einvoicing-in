# mcp-einvoicing-in — Specification assets

This directory holds the normative source material for India's GST e-invoicing system — official
PDFs published by GSTN/CBIC. Values derived from these documents belong in
[`context-library/countries/in.md`](../../context-library/countries/in.md) (in the `mcp-einvoicing`
monorepo), not in code and not duplicated as a new file in this directory.

## Directory layout

Single-standard package (FORM GST INV-01 / IRP-IRN) — all files kept flat at the top level.

## Sources and versions

| Standard | Version | Authority URL | Retrieved |
|---|---|---|---|
| FORM GST INV-01 (GST e-invoice schema, data dictionary) | 1.1 (last substituted vide Notification No. 60/2020-CT dt. 30.07.2020, per the PDF's own footnotes) | GSTN / NIC e-invoice portal, `https://einvoice1.gst.gov.in/` (canonical URL not independently fetched — user-supplied PDF, bundled-sources-only policy) | 2026-09-07 |
| CGST Rules 2017, Rule 48(4) (FORM GST INV-01 + IRN mandate mechanism) | Inserted by Notification No. 68/2019-Central Tax, 13 Dec 2019 | CBIC, `https://www.cbic.gov.in/` (not independently fetched) | 2026-09-07 |
| CGST Rules 2017, Rule 46(r) / Rule 138A(2) (QR code with embedded IRN) | Inserted/substituted by Notification No. 72/2020-Central Tax, 30 Sep 2020 | CBIC, `https://www.cbic.gov.in/` (not independently fetched) | 2026-09-07 |

## Pending specs

| Document | Status | Notes |
|---|---|---|
| Notification No. 10/2023-Central Tax (current AATO > ₹5 Cr mandate threshold) | `[NEED:]` | Not staged. The ₹5 Cr threshold and the 30-day IRP-upload limit for AATO ≥ ₹10 Cr must not appear in this package's client-facing docs (README, tool docstrings) until confirmed against a locally supplied copy of this notification. |
| NIC e-invoice API spec (auth/token, `/eivital/dc`, generate-IRN, cancel-IRN, signed-QR content, sandbox `einv-apisandbox.nic.in`) | `[NEED:]` | Blocks all of Phase B (`tools/in__irp.py`) — live IRP transport. Without this file, the exact signed-QR content field list is also unconfirmed (see `context-library/countries/in.md`, "Known gaps and open items"). |
| Master code lists (state codes, HSN, UQC, currency, port codes) | `[NEED:]` | Referenced in the schema via `icegate.gov.in` enquiry endpoints, not themselves staged. Needed for enum validation in `validators/`. |
| PAN (Permanent Account Number) format specification | `[NEED:]` | The only staged reference to PAN is a passing mention in `Supplier_Legal_Name`'s explanatory note. `TaxIdentifier.validate_in_pan()` was deliberately not added to core pending this — see `mcp-einvoicing-core`'s `gaps_registry.toml`, `core.tax_id.in_pan`. |

## Non-file sources

None — all sources listed above are retained as local PDF files in this directory.

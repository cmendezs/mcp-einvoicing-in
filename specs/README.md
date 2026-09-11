# mcp-einvoicing-in — Specification assets

This directory holds the normative source material for India's GST e-invoicing system — official
PDFs published by GSTN/CBIC. Values derived from these documents belong in this package's own compliance reference, not
in code and not duplicated as a new file in this directory.

## Directory layout

Single-standard package (FORM GST INV-01 / IRP-IRN) — all files kept flat at the top level.

## Sources and versions

| Standard | Version | Authority URL | Retrieved |
|---|---|---|---|
| FORM GST INV-01 (GST e-invoice schema, data dictionary) | 1.1 (last substituted vide Notification No. 60/2020-CT dt. 30.07.2020, per the PDF's own footnotes) | GSTN / NIC e-invoice portal, `https://einvoice1.gst.gov.in/` (canonical URL not independently fetched — user-supplied PDF, bundled-sources-only policy) | 2026-09-07 |
| CGST Rules 2017, Rule 48(4) (FORM GST INV-01 + IRN mandate mechanism) | Inserted by Notification No. 68/2019-Central Tax, 13 Dec 2019 | CBIC, `https://www.cbic.gov.in/` (not independently fetched) | 2026-09-07 |
| CGST Rules 2017, Rule 46(r) / Rule 138A(2) (QR code with embedded IRN) | Inserted/substituted by Notification No. 72/2020-Central Tax, 30 Sep 2020 | CBIC, `https://www.cbic.gov.in/` (not independently fetched) | 2026-09-07 |
| Notification No. 10/2023-Central Tax (AATO e-invoicing mandate threshold reduced to ₹5 Cr) | Amends the ₹10 Cr threshold in principal Notification No. 13/2020-Central Tax to ₹5 Cr, effective 1 August 2023 (text: "for the words 'ten crore rupees', the words 'five crore rupees' shall be substituted") | CBIC, `https://www.cbic.gov.in/` (not independently fetched; user-supplied PDF) | 2026-09-07 |

## Pending specs

| Document | Status | Notes |
|---|---|---|
| Notification No. 13/2020-Central Tax (the principal notification Notification No. 10/2023-CT amends) | `[NEED:]` | Not staged. Notification No. 10/2023-CT confirms the ₹5 Cr *substitution* text but the principal notification itself (which also lists the categories exempted from e-invoicing — government department, local authority, SEZ unit, insurer/banking/NBFC, GTA, passenger transport, cinema admission) is not locally staged; that exemption list is currently sourced only from a secondary summary, not a staged primary document. |
| GSTN e-invoice portal advisory, `advisory270325.pdf` (dated ~27 Mar 2025), imposing the 30-day IRP-upload limit for AATO ≥ ₹10 Cr | `[NEED:]` | **Identified but not staged** — user attempted retrieval at `https://einvoice1.gst.gov.in/Documents/advisory270325.pdf` and hit a geographic access restriction. A public search snippet quotes: "from 1st April 2025, taxpayers with an AATO of 10 crores and above would not be allowed to report e-Invoices older than 30 days" — this snippet text must not be treated as confirmed until the actual PDF is supplied (bundled-sources-only policy; a search-result snippet is not a staged document). Note this is a GSTN portal *advisory*, not a CBIC Gazette notification like the other rows in this table — a different document type/authority tier once it is supplied. Next step: obtain the PDF via a different network/VPN or have someone in an unrestricted region download and share it. |
| NIC e-invoice API spec (auth/token, `/eivital/dc`, generate-IRN, cancel-IRN, signed-QR content, sandbox `einv-apisandbox.nic.in`) | `[NEED:]` | Blocks all of Phase B (`tools/in__irp.py`) — live IRP transport. Without this file, the exact signed-QR content field list is also unconfirmed. |
| Master code lists (state codes, HSN, UQC, currency, port codes) | `[NEED:]` | Referenced in the schema via `icegate.gov.in` enquiry endpoints, not themselves staged. Needed for enum validation in `validators/`. |
| PAN (Permanent Account Number) format specification | `[NEED:]` | The only staged reference to PAN is a passing mention in `Supplier_Legal_Name`'s explanatory note. `TaxIdentifier.validate_in_pan()` was deliberately not added to core pending this — see `mcp-einvoicing-core`'s `gaps_registry.toml`, `core.tax_id.in_pan`. |

## Non-file sources

None — all sources listed above are retained as local PDF files in this directory.

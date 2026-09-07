# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] - 2026-09-07

### Added
- Initial release. `INInvoice(InvoiceDocument)` model covering FORM GST INV-01
  schema v1.1 (INV/CRN/DBN document types). `in__build_invoice`,
  `in__validate_invoice`, `in__render_irp_qr_png`, and
  `in__get_supported_scope` tools. GSTIN validation via
  `TaxIdentifier.validate_in_gstin` (core v1.31.0).
- Phase A scope only — no live IRP submission (auth/token, generate-IRN,
  cancel-IRN); blocked on the NIC e-invoice API specification, not yet
  staged. See `specs/README.md`.

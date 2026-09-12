# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.2.2] - 2026-09-12

### Changed
- Lower-bound pin on `mcp-einvoicing-core` raised to `>=1.34.1` (was `>=1.32.0`). This package's own CI now runs `CHECK_PUBLIC_HYGIENE`, the pre-publish audit check that blocks accidental citations of the private orchestration repo.

---

## [0.2.1] - 2026-09-09

Core audit Step 3 item 5: CORE-8, now fully resolved across
MX and IN.

### Changed
- **CORE-8** — `tools/in__scope.py`'s `ScopeInfo` now subclasses core's opt-in
  `BaseScopeInfo` (core v1.32.0) instead of a standalone duplicate model, adding just
  `supported_supply_types` on top of the shared base. No field rename was needed — output is
  unchanged.
- `mcp-einvoicing-core` floor pin bumped to `>=1.32.0,<2.0.0`.

### Added
- `tests/test_scope.py` — no test coverage existed for the scope tool before this.

### Fixed
- **CORE-11 (partial)** — `audit/report.json` was stamped `pkg_version` `0.1.0` against a
  `pyproject.toml` already at `0.2.0`; now correctly regenerated.

---

## [0.2.0] - 2026-09-08

### Added
- Mandatory `place_of_supply_state_code` field on `INInvoice` (schema field 5.4,
  `Place_Of_Supply_State_Code`) — [IN-SC-1], BLOCKING.

### Changed
- `Supply_Type_Code` is now enforced as mandatory instead of silently accepting an unset
  `transmission_format` — [IN-SC-2], HIGH.
- Supplier/Recipient address and state-code are now enforced as mandatory and emitted
  unconditionally, instead of being silently droppable — [IN-SC-3], HIGH.
- Date fields (`date` and every other schema-documented date string) now validated against the
  schema's `DD/MM/YYYY` format instead of accepting free-form ISO dates — [IN-SC-5], MEDIUM.
- `Document_Num` (≤16 chars) and `Supplier_Place` (≤50 chars) length caps now enforced —
  [IN-SC-4], LOW.
- `in__build_invoice` now runs the GSTIN/state-code consistency check that
  `in__validate_invoice` already ran — [IN-ID-1], LOW.

Findings [IN-SC-6] and [IN-SC-7] remain deferred (blocked on the NIC API spec and a staged
rounding-mode source, respectively).

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

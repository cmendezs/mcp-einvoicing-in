# Tool reference — `mcp_einvoicing_in`

This file is generated from the MCP server's tool registry by `scripts/gen_tool_reference.py`. Do not edit it by hand; run the script instead.

**Tools:** 4

## `in__build_invoice`

Validate structured input against `INInvoice` and build a GST e-invoice payload.

`invoice_data` is validated against `INInvoice` (see that model for the
full field list — `seller`/`buyer` as `InvoiceParty` with a GSTIN
`TaxIdentifier`, `lines` as `INInvoiceLine`, `document_total` as
`INDocumentTotalDetails`). GSTIN fields are validated via
`TaxIdentifier.validate_in_gstin` as part of model construction
(`Recipient_GSTIN`'s `"URP"` sentinel is accepted per schema field 5.3);
a malformed GSTIN is reported as a validation error, not a built
payload.

The `IRN` field is never emitted — it is IRP-generated, never
supplier-populated (schema field 1.1). This tool builds the
*registration request*; `in__qr.IRPRegistrationResponse` models the
IRP's response after a real submission (Phase B, not yet built — see
`specs/README.md`).

Returns a dict with:
- ``payload``: the built JSON-serializable dict (see module docstring
  for the wire-shape caveat)
- ``document_type``: the validated `Document_Type_Code` (INV/CRN/DBN)

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `invoice_data` | object | yes |  |  |

## `in__get_supported_scope`

Return the FORM GST INV-01 document types and supply types this package supports.

Reflects Phase A scope locked in `context-library/countries/in.md`
(workspace root repo): schema v1.1, all three `Document_Type_Code`
values (INV/CRN/DBN), offline structural validation, and QR-response
modeling (`in__build_invoice`, `in__validate_invoice`,
`in__render_irp_qr_png`). Live IRP submission (auth/token,
generate-IRN, cancel-IRN) is Phase B and is **not implemented** — it is
blocked on the NIC e-invoice API spec, which has not been staged; see
`specs/README.md`, "Pending specs".

Returns:
    A `ScopeInfo` describing current scope, for callers to check before
    assuming a document type or supply type is supported.

_No parameters._

## `in__render_irp_qr_png`

Render the IRP's raw signed-QR string as a displayable PNG.

This does not decode or interpret `signed_qr_code` — it is treated as an
opaque string and encoded into a QR image via
`mcp_einvoicing_core.qr.generate_qr_png_base64` (core-state-check:
`[REUSE: generate_qr_png_base64 from mcp-einvoicing-core]`). Decoding the
JWS content itself is out of scope pending the NIC API spec — see this
module's docstring.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `signed_qr_code` | string | yes |  | The raw QR string returned by the IRP in `IRPRegistrationResponse.signed_qr_code`. |

## `in__validate_invoice`

Validate a GST e-invoice against FORM GST INV-01 schema v1.1 structural rules.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `invoice_data` | object | yes |  | Fields matching the `INInvoice` schema. |

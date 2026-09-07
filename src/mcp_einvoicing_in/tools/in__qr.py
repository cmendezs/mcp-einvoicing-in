"""IRP response modeling and QR rendering for GST e-invoices.

Everything the IRP returns after successful registration — IRN, ack number
and date, and the signed QR code — is IRP-generated, never supplier-composed
(schema field 1.1: "the supplier will not be populating this field"; CGST
Rule 46(r)/Rule 138A(2) per Notification 72/2020-CT, staged, confirm the QR
code embeds the IRN). This module models that response shape and renders a
displayable QR image from the raw string the IRP returns.

`[NEED: NIC API spec]` — the *content* fields encoded inside the signed QR
string itself (commonly described elsewhere as SupplierGSTIN, BuyerGSTIN,
DocNo, DocDate, InvVal, HSN of the main item, IRN, IRN date) are **not**
confirmed by any locally staged document — see
`context-library/countries/in.md`, "Known gaps and open items". This module
therefore does not parse or decode QR content; it only renders whatever
opaque string the IRP hands back, and models the surrounding response
envelope fields the schema PDF *does* confirm (IRN's length, in particular).
Extend `in__decode_irp_qr_content` (currently absent, deliberately) once
that spec is supplied — do not fabricate a field list now.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mcp_einvoicing_core.qr import generate_qr_png_base64


class IRPRegistrationResponse(BaseModel):
    """Shape of a successful IRP registration response.

    `irn`: schema field 1.1 — `String (Length: 64)`, IRP-generated.
    `ack_no`/`ack_dt`, `signed_invoice`, `signed_qr_code`, `status` are
    **not** described in the staged FORM GST INV-01 schema PDF (which
    documents the *request* payload, not the IRP's response) — their
    presence here follows directly from the plan's own scope note and CGST
    Rule 48(4)/(5) (the invoice is only legally valid once the IRP responds
    with these), but the exact field names and types are `[NEED: NIC API
    spec]` and may need revision once that document is staged. Treat this
    class as provisional.
    """

    irn: str = Field(..., min_length=64, max_length=64)
    ack_no: str | None = None
    ack_dt: str | None = Field(
        default=None, description="DD/MM/YYYY HH:MM:SS `[NEED: confirm format]`"
    )
    signed_invoice: str | None = Field(
        default=None, description="IRP-signed invoice payload (JWS) `[NEED: confirm shape]`"
    )
    signed_qr_code: str | None = Field(
        default=None, description="Raw signed QR string (JWS), opaque to this package"
    )
    status: str | None = None


def in__render_irp_qr_png(signed_qr_code: str) -> str:
    """Render the IRP's raw signed-QR string as a displayable PNG.

    This does not decode or interpret `signed_qr_code` — it is treated as an
    opaque string and encoded into a QR image via
    `mcp_einvoicing_core.qr.generate_qr_png_base64` (core-state-check:
    `[REUSE: generate_qr_png_base64 from mcp-einvoicing-core]`). Decoding the
    JWS content itself is out of scope pending the NIC API spec — see this
    module's docstring.

    Args:
        signed_qr_code: The raw QR string returned by the IRP in
            `IRPRegistrationResponse.signed_qr_code`.

    Returns:
        Base64-encoded PNG image data (no data-URI prefix), as returned by
        `generate_qr_png_base64`.
    """
    return generate_qr_png_base64(signed_qr_code)

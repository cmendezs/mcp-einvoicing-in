"""Package scope introspection tool."""

from __future__ import annotations

from pydantic import BaseModel


class ScopeInfo(BaseModel):
    schema_version: str
    phase: int
    supported_document_types: list[str]
    supported_supply_types: list[str]
    out_of_scope: list[str]


def in__get_supported_scope() -> ScopeInfo:
    """Return the FORM GST INV-01 document types and supply types this package supports.

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
    """
    return ScopeInfo(
        schema_version="1.1",
        phase=1,
        supported_document_types=["INV", "CRN", "DBN"],
        supported_supply_types=["B2B", "B2C", "SEZWP", "SEZWOP", "EXPWP", "EXPWOP", "DEXP"],
        out_of_scope=[
            (
                "Live IRP submission (auth/token, generate-IRN, cancel-IRN) — Phase B, "
                "blocked on the NIC e-invoice API spec, not staged"
            ),
            (
                "Signed QR content decoding (only opaque rendering is supported) — "
                "blocked on the NIC e-invoice API spec, not staged"
            ),
            (
                "State/HSN/UQC/currency/port master-code-list enum validation — "
                "master code lists not staged"
            ),
        ],
    )


__all__ = ["ScopeInfo", "in__get_supported_scope"]

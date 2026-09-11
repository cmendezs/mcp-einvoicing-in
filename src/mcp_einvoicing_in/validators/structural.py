"""Offline structural/business-rule validation for FORM GST INV-01 payloads.

FORM GST INV-01 is a flat JSON schema, not XML/UBL — `SchematronValidator`
(core's XML/Schematron abstraction) does not apply here, per the
package's own compliance reference ("Cross-package notes"). Most mandatory-
field, enum-membership, and CGST+SGST-vs-IGST pairing checks are already
enforced at construction time by `INInvoice`/`INInvoiceLine`'s own Pydantic
field/model validators (see `models/invoice.py`) — this module covers the
one confirmed business rule that construction-time validation does not: the
first two characters of a GSTIN must match the party's own two-digit state
code, confirmed directly in every worked example in the staged schema PDF
(e.g. `Supplier_GSTIN` sample `29AADFV7589C1ZX` pairs with `Supplier_State_
Code` sample `29`) — see the package's own compliance reference,
"Party-identifier formats", "State code" row.

State-code *enumeration membership* (whether `"29"` is itself a currently
valid GST state code) is out of scope here — the master code list
(`https://www.icegate.gov.in/Webappl/STATE_ENQ`) is not staged locally; see
`specs/README.md`, "Pending specs".
"""

from __future__ import annotations

from mcp_einvoicing_in.models.invoice import INInvoice


def check_gstin_state_code_consistency(invoice: INInvoice) -> list[str]:
    """Return a list of human-readable errors for any GSTIN/state-code mismatch.

    Empty list means no mismatch found. `"URP"` recipient GSTINs (schema
    field 5.3's unregistered-person sentinel) have no state-code prefix to
    check and are skipped.
    """
    errors: list[str] = []

    seller_gstin = invoice.seller.tax_id.identifier.strip().upper()
    seller_state = invoice.seller.address.province if invoice.seller.address else None
    if seller_state and seller_gstin[:2] != seller_state.strip():
        errors.append(
            f"Supplier_GSTIN {seller_gstin!r} state-code prefix {seller_gstin[:2]!r} "
            f"does not match Supplier_State_Code {seller_state!r}."
        )

    buyer_gstin = invoice.buyer.tax_id.identifier.strip().upper()
    if buyer_gstin != "URP":
        buyer_state = invoice.buyer.address.province if invoice.buyer.address else None
        if buyer_state and buyer_gstin[:2] != buyer_state.strip():
            errors.append(
                f"Recipient_GSTIN {buyer_gstin!r} state-code prefix {buyer_gstin[:2]!r} "
                f"does not match Recipient_State_Code {buyer_state!r}."
            )

    if invoice.ship_to_details is not None and invoice.ship_to_details.gstin:
        ship_gstin = invoice.ship_to_details.gstin.strip().upper()
        ship_state = invoice.ship_to_details.state_code.strip()
        if ship_gstin[:2] != ship_state:
            errors.append(
                f"ShipTo_GSTIN {ship_gstin!r} state-code prefix {ship_gstin[:2]!r} does not "
                f"match Ship_To_State_Code {ship_state!r}."
            )

    if invoice.ecom_gstin:
        # ECOM_GSTIN (field 10.8) has no paired state-code field of its own
        # in the schema, so there is nothing to cross-check it against.
        pass

    return errors

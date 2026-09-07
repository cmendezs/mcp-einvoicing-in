"""in__validate_invoice — offline structural/business-rule validation.

Runs `INInvoice` construction (mandatory fields, enum membership, CGST+SGST-
vs-IGST pairing at both item and document-total level) followed by the
GSTIN/state-code consistency check in `validators.structural` — see that
module's docstring for what is and is not covered. There is no XSD/
Schematron pass: FORM GST INV-01 is JSON, not XML.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from mcp_einvoicing_in.models.invoice import INInvoice
from mcp_einvoicing_in.validators.structural import check_gstin_state_code_consistency


def in__validate_invoice(invoice_data: dict[str, Any]) -> dict[str, object]:
    """Validate a GST e-invoice against FORM GST INV-01 schema v1.1 structural rules.

    Args:
        invoice_data: Fields matching the `INInvoice` schema.

    Returns a dict with:
    - ``valid``: `True` if `invoice_data` passes every check, else `False`
    - ``errors``: list of error strings/dicts (Pydantic error details for
      construction failures, plain strings for the GSTIN/state-code check)
    """
    try:
        invoice = INInvoice.model_validate(invoice_data)
    except ValidationError as exc:
        return {"valid": False, "errors": exc.errors()}

    business_rule_errors = check_gstin_state_code_consistency(invoice)
    if business_rule_errors:
        return {"valid": False, "errors": business_rule_errors}

    return {"valid": True, "errors": []}

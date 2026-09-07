"""Tests for in__validate_invoice and the GSTIN/state-code consistency check."""

from __future__ import annotations

import copy

from mcp_einvoicing_in.models.invoice import INInvoice
from mcp_einvoicing_in.tools.in__validate import in__validate_invoice
from mcp_einvoicing_in.validators.structural import check_gstin_state_code_consistency


class TestValidateInvoice:
    def test_valid_invoice_passes(self, minimal_invoice_data: dict) -> None:
        result = in__validate_invoice(minimal_invoice_data)
        assert result == {"valid": True, "errors": []}

    def test_construction_failure_reported(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        del data["document_total"]
        result = in__validate_invoice(data)
        assert result["valid"] is False
        assert result["errors"]

    def test_gstin_state_code_mismatch_reported(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        # Supplier_GSTIN prefix "29" no longer matches a "07" state code.
        data["seller"]["address"]["province"] = "07"
        result = in__validate_invoice(data)
        assert result["valid"] is False
        assert any("Supplier_GSTIN" in e for e in result["errors"])


class TestGstinStateCodeConsistency:
    def test_matching_prefixes_pass(self, minimal_invoice_data: dict) -> None:
        invoice = INInvoice.model_validate(minimal_invoice_data)
        assert check_gstin_state_code_consistency(invoice) == []

    def test_mismatched_recipient_prefix_flagged(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["buyer"]["address"]["province"] = "07"
        invoice = INInvoice.model_validate(data)
        errors = check_gstin_state_code_consistency(invoice)
        assert any("Recipient_GSTIN" in e for e in errors)

    def test_urp_buyer_skipped(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["buyer"]["tax_id"]["identifier"] = "URP"
        data["buyer"]["address"]["province"] = "07"
        invoice = INInvoice.model_validate(data)
        # "URP" has no GSTIN prefix to check against the state code.
        assert check_gstin_state_code_consistency(invoice) == []

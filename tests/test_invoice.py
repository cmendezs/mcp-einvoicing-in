"""Tests for INInvoice / INInvoiceLine model construction and business rules."""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from mcp_einvoicing_in.models.invoice import INInvoice


class TestINInvoiceConstruction:
    def test_minimal_invoice_valid(self, minimal_invoice_data: dict) -> None:
        invoice = INInvoice.model_validate(minimal_invoice_data)
        assert invoice.document_type == "INV"
        assert invoice.number == "Sa/1/2019"
        assert invoice.currency == "INR"
        assert invoice.lines[0].hsn_code == "1122"

    def test_crn_and_dbn_document_types_accepted(self, minimal_invoice_data: dict) -> None:
        for doc_type in ("CRN", "DBN"):
            data = copy.deepcopy(minimal_invoice_data)
            data["document_type"] = doc_type
            invoice = INInvoice.model_validate(data)
            assert invoice.document_type == doc_type

    def test_invalid_document_type_rejected(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["document_type"] = "XYZ"
        with pytest.raises(ValidationError):
            INInvoice.model_validate(data)

    def test_invalid_supply_type_code_rejected(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["transmission_format"] = "NOT_A_CODE"
        with pytest.raises(ValidationError):
            INInvoice.model_validate(data)

    def test_currency_must_be_inr(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["currency"] = "USD"
        with pytest.raises(ValidationError, match="must be 'INR'"):
            INInvoice.model_validate(data)


class TestGstinValidation:
    def test_malformed_seller_gstin_rejected(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["seller"]["tax_id"]["identifier"] = "TOO_SHORT"
        with pytest.raises(ValidationError, match="Invalid Supplier_GSTIN"):
            INInvoice.model_validate(data)

    def test_malformed_buyer_gstin_rejected(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["buyer"]["tax_id"]["identifier"] = "TOO_SHORT"
        with pytest.raises(ValidationError, match="Invalid Recipient_GSTIN"):
            INInvoice.model_validate(data)

    def test_urp_buyer_gstin_accepted(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["buyer"]["tax_id"]["identifier"] = "URP"
        invoice = INInvoice.model_validate(data)
        assert invoice.buyer.tax_id.identifier == "URP"

    def test_urp_seller_gstin_not_accepted(self, minimal_invoice_data: dict) -> None:
        # Schema field 5.3's "URP" sentinel is documented only for the
        # Recipient_GSTIN — a supplier must always have a real GSTIN.
        data = copy.deepcopy(minimal_invoice_data)
        data["seller"]["tax_id"]["identifier"] = "URP"
        with pytest.raises(ValidationError, match="Invalid Supplier_GSTIN"):
            INInvoice.model_validate(data)


class TestTaxSplitPairing:
    def test_item_igst_and_cgst_mutually_exclusive(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["lines"][0]["cgst_amt"] = "125.00"
        data["lines"][0]["sgst_utgst_amt"] = "125.00"
        with pytest.raises(ValidationError, match="mutually exclusive"):
            INInvoice.model_validate(data)

    def test_item_cgst_without_sgst_rejected(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        del data["lines"][0]["igst_amt"]
        data["lines"][0]["cgst_amt"] = "125.00"
        with pytest.raises(ValidationError, match="must be reported together"):
            INInvoice.model_validate(data)

    def test_item_cgst_and_sgst_together_accepted(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        del data["lines"][0]["igst_amt"]
        data["lines"][0]["cgst_amt"] = "125.00"
        data["lines"][0]["sgst_utgst_amt"] = "125.00"
        invoice = INInvoice.model_validate(data)
        assert invoice.lines[0].cgst_amt is not None

    def test_document_total_igst_and_cgst_mutually_exclusive(
        self, minimal_invoice_data: dict
    ) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["document_total"]["cgst_amt_total"] = "125.00"
        data["document_total"]["sgst_utgst_amt_total"] = "125.00"
        with pytest.raises(ValidationError, match="mutually exclusive"):
            INInvoice.model_validate(data)


class TestPrecedingDocumentReference:
    def test_crn_with_preceding_document_reference(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["document_type"] = "CRN"
        data["preceding_document_references"] = [
            {"preceding_document_number": "Sa/1/2019", "preceding_document_date": "21/07/2019"}
        ]
        invoice = INInvoice.model_validate(data)
        assert invoice.preceding_document_references[0].preceding_document_number == "Sa/1/2019"

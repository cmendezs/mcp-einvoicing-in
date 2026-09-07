"""Tests for in__build_invoice."""

from __future__ import annotations

import copy
from decimal import Decimal

from mcp_einvoicing_in.tools.in__payload import in__build_invoice


class TestBuildInvoice:
    def test_builds_payload_from_schema_example_values(self, minimal_invoice_data: dict) -> None:
        result = in__build_invoice(minimal_invoice_data)
        assert "error" not in result
        payload = result["payload"]
        assert payload["Document_Type_Code"] == "INV"
        assert payload["Document_Num"] == "Sa/1/2019"
        assert payload["Supplier_GSTIN"] == "29AADFV7589C1ZX"
        assert payload["Recipient_GSTIN"] == "29ABCCR1832C1ZX"
        assert payload["Item_List"][0]["HSN_Code"] == "1122"
        assert payload["Document_Total_Details"]["Total_Invoice_Value_INR"] == "5250.00"
        assert result["document_type"] == "INV"

    def test_irn_never_emitted(self, minimal_invoice_data: dict) -> None:
        result = in__build_invoice(minimal_invoice_data)
        assert "IRN" not in result["payload"]

    def test_amounts_serialized_as_strings_not_floats(self, minimal_invoice_data: dict) -> None:
        result = in__build_invoice(minimal_invoice_data)
        payload = result["payload"]
        assert isinstance(payload["Item_List"][0]["Item_Price"], str)
        assert not isinstance(payload["Item_List"][0]["Item_Price"], float)

    def test_invalid_input_returns_validation_error(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["seller"]["tax_id"]["identifier"] = "BAD"
        result = in__build_invoice(data)
        assert result["error"] == "validation_error"
        assert "details" in result

    def test_optional_blocks_omitted_when_absent(self, minimal_invoice_data: dict) -> None:
        result = in__build_invoice(minimal_invoice_data)
        payload = result["payload"]
        assert "Ship_To_Details" not in payload
        assert "Eway_Bill_Details" not in payload
        assert "Preceding_Document_Reference" not in payload

    def test_eway_bill_details_included_when_present(self, minimal_invoice_data: dict) -> None:
        data = copy.deepcopy(minimal_invoice_data)
        data["eway_bill_details"] = {"trans_distance": 200, "trans_mode": "1"}
        result = in__build_invoice(data)
        payload = result["payload"]
        assert payload["Eway_Bill_Details"]["Trans_Distance"] == 200
        assert payload["Eway_Bill_Details"]["Trans_Mode"] == "1"

    def test_decimal_precision_preserved(self, minimal_invoice_data: dict) -> None:
        result = in__build_invoice(minimal_invoice_data)
        payload = result["payload"]
        assert Decimal(payload["Item_List"][0]["Item_Price"]) == Decimal("500.5")

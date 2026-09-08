"""Shared pytest fixtures for mcp-einvoicing-in tests.

Sample values are taken directly from the worked examples in
`specs/FORM_GST_INV-01_schema_v1.1.pdf` (e.g. `Supplier_GSTIN`
`29AADFV7589C1ZX`, `Recipient_GSTIN` `29ABCCR1832C1ZX`) rather than invented.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def minimal_invoice_data() -> dict:
    return {
        "document_type": "INV",
        "date": "21/07/2019",
        "number": "Sa/1/2019",
        "currency": "INR",
        "transmission_format": "B2B",
        "place_of_supply_state_code": "29",
        "seller": {
            "tax_id": {"country_code": "IN", "identifier": "29AADFV7589C1ZX"},
            "name": "XYZ Ltd.",
            "address": {
                "street": "# 1-23120, Flat No. 3, Nalanda Apartments, MG Road, Vasanth Nagar",
                "postal_code": "560087",
                "city": "Bangalore",
                "country_code": "IN",
                "province": "29",
            },
        },
        "buyer": {
            "tax_id": {"country_code": "IN", "identifier": "29ABCCR1832C1ZX"},
            "name": "PQR Pvt. Ltd.",
            "address": {
                "street": "# 1-23120, Flat No. 3, Nalanda Apartments, MG Road, Vasanth Nagar",
                "postal_code": "560002",
                "city": "Mysore",
                "country_code": "IN",
                "province": "29",
            },
        },
        "lines": [
            {
                "line_number": 1,
                "sl_no": "1",
                "description": "Mobile",
                "is_service": False,
                "hsn_code": "1122",
                "quantity": "10",
                "unit_of_measure": "Box",
                "unit_price": "500.5",
                "total_price": "5000",
                "item_taxable_value": "5000",
                "gst_rate": "5",
                "igst_amt": "250.00",
                "item_total_amt": "5250.00",
            }
        ],
        "document_total": {
            "taxable_value_total": "5000",
            "igst_amt_total": "250.00",
            "total_invoice_value_inr": "5250.00",
        },
    }

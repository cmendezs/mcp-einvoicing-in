"""in__build_invoice — build a FORM GST INV-01 JSON payload from structured input.

`[NEED: confirm wire-level JSON nesting against the NIC API spec]` — the
staged schema PDF (`specs/FORM_GST_INV-01_schema_v1.1.pdf`) is a *data
dictionary*: it gives each field's `Technical_name_of_the_field` (e.g.
`Document_Num`, `Supplier_GSTIN`) and groups them under numbered section
headers ("4. Supplier Information", "5. Recipient Information", etc.), but
those header rows do not themselves carry a `Technical_name_of_the_field`
value in the schema table — only specific sub-lists do (`Item_List` at 8.1,
`Document_Total_Details` at 9.1, `Preceding_Document_Reference` at 3.1, and
the Annexure headers `Ship_To_Details`/`Dispatch_From_Details`/`Batch_Details`
/`Attribute_Details_of_Item` at A 1.0/A 1.1/A 1.4/A 1.5). Commonly-described
NIC JSON payloads group fields under object keys like
`SellerDtls`/`BuyerDtls`/`ValDtls`/`ItemList`/`DocDtls` — but that grouping
convention is **not confirmed by any locally staged document**, so this
builder does not invent it. It emits a single flat JSON object using each
field's confirmed schema technical name, nesting only where the schema
itself names a nested structure. Treat the output as schema-field-complete
but **wire-shape-unverified** until the NIC API spec is staged — see
`context-library/countries/in.md` and `specs/README.md`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import ValidationError

from mcp_einvoicing_in.models.invoice import INAddress, INInvoice, INInvoiceLine
from mcp_einvoicing_in.validators.structural import check_gstin_state_code_consistency


def _decimal_to_str(value: Any) -> Any:
    """JSON has no native Decimal type; the schema expresses amounts as
    plain numbers with a fixed max fraction-digit count (Note 2). Emitting
    as a string avoids float rounding artifacts; the caller's JSON
    serializer is expected to use this dict as-is (not re-run through
    ``json.dumps`` with a float coercion)."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _decimal_to_str(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_decimal_to_str(v) for v in value]
    return value


def _opt(key: str, value: Any) -> dict[str, Any]:
    """Include `key: value` only when `value` is not None/empty — the
    schema marks most fields optional (0..1) and omitting an unset field is
    preferable to emitting an explicit null the schema never describes."""
    if value is None or value == "":
        return {}
    return {key: value}


def _serialize_address(prefix: str, addr: INAddress) -> dict[str, Any]:
    d: dict[str, Any] = {
        f"{prefix}_Legal_Name": addr.legal_name,
        f"{prefix}_Address1": addr.address1,
        f"{prefix}_Place": addr.place,
        f"{prefix}_Pincode": addr.pincode,
        f"{prefix}_State_Code": addr.state_code,
    }
    d.update(_opt(f"{prefix}_Trade_Name", addr.trade_name))
    d.update(_opt(f"{prefix}_GSTIN", addr.gstin))
    d.update(_opt(f"{prefix}_Address2", addr.address2))
    return d


def _serialize_item(line: INInvoiceLine) -> dict[str, Any]:
    item: dict[str, Any] = {
        "Sl_No": line.sl_no,
        "Is_Service": "Y" if line.is_service else "N",
        "HSN_Code": line.hsn_code,
        "Item_Price": line.unit_price,
        "Gross_Amount": line.total_price,
        "Item_Taxable_Value": line.item_taxable_value,
        "GST_Rate": line.gst_rate,
        "Item_Total_Amt": line.item_total_amt,
    }
    item.update(_opt("Item_Description", line.description))
    item.update(_opt("Quantity", line.quantity))
    item.update(_opt("Free_Qty", line.free_qty))
    item.update(_opt("Unit_Of_Measurement", line.unit_of_measure))
    item.update(_opt("Barcode", line.barcode))
    item.update(_opt("Item_Discount_Amount", line.item_discount_amount))
    item.update(_opt("Pre_Tax_Value", line.pre_tax_value))
    item.update(_opt("IGST_Amt", line.igst_amt))
    item.update(_opt("CGST_Amt", line.cgst_amt))
    item.update(_opt("SGST_UTGST_Amt", line.sgst_utgst_amt))
    item.update(_opt("Comp_Cess_Rate_Ad_valorem", line.comp_cess_rate_ad_valorem))
    item.update(_opt("Comp_Cess_Amt_Ad_Valorem", line.comp_cess_amt_ad_valorem))
    item.update(_opt("Comp_Cess_Amt_Non_Ad_Valorem", line.comp_cess_amt_non_ad_valorem))
    item.update(_opt("State_Cess_Rate_Ad_Valorem", line.state_cess_rate_ad_valorem))
    item.update(_opt("State_Cess_Amt_Ad_Valorem", line.state_cess_amt_ad_valorem))
    item.update(_opt("State_Cess_Amt_Non_Ad_Valorem", line.state_cess_amt_non_ad_valorem))
    item.update(_opt("Other_Charges_Item_Level", line.other_charges_item_level))
    item.update(_opt("Purchase_Order_Line_Reference", line.purchase_order_line_reference))
    item.update(_opt("Origin_Country_Code", line.origin_country_code))
    item.update(_opt("Unique_Serial_Number", line.unique_serial_number))
    if line.batch_details is not None:
        b = line.batch_details
        batch: dict[str, Any] = {"Batch_Number": b.batch_number}
        batch.update(_opt("Batch_Expiry_Date", b.batch_expiry_date))
        batch.update(_opt("Warranty_Date", b.warranty_date))
        item["Batch_Details"] = batch
    if line.product_attribute_details:
        item["Product_Attribute_Details"] = [
            {
                **_opt("Attribute_Name", a.attribute_name),
                **_opt("Attribute_Value", a.attribute_value),
            }
            for a in line.product_attribute_details
        ]
    return item


def in__build_invoice(
    invoice_data: dict[str, Any],
) -> dict[str, object]:
    """Validate structured input against `INInvoice` and build a GST e-invoice payload.

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
    """
    try:
        invoice = INInvoice.model_validate(invoice_data)
    except ValidationError as exc:
        return {"error": "validation_error", "details": exc.errors()}

    consistency_errors = check_gstin_state_code_consistency(invoice)
    if consistency_errors:
        return {"error": "validation_error", "details": consistency_errors}

    payload: dict[str, Any] = {
        "Version": invoice.version,
        "Supply_Type_Code": invoice.transmission_format,
        "Document_Type_Code": invoice.document_type,
        "Document_Num": invoice.number,
        "Document_Date": invoice.date,
        "Place_Of_Supply_State_Code": invoice.place_of_supply_state_code,
    }
    payload.update(_opt("Additional_Currency_Code", invoice.additional_currency_code))
    if invoice.reverse_charge is not None:
        payload["Reverse_Charge"] = "Y" if invoice.reverse_charge else "N"
    igst_flag = invoice.igst_applicability_despite_supplier_and_recipient_located_in_same_state_ut
    if igst_flag is not None:
        payload["IGST_Applicability_despite_Supplier_and_Recipient_located_in_same_State/UT"] = (
            "Y" if igst_flag else "N"
        )
    payload.update(_opt("Document_Period_Start_Date", invoice.document_period_start_date))
    payload.update(_opt("Document_Period_End_Date", invoice.document_period_end_date))

    if invoice.preceding_document_references:
        payload["Preceding_Document_Reference"] = [
            {
                "Preceding_Document_Number": r.preceding_document_number,
                "Preceding_Document_Date": r.preceding_document_date,
                **_opt("Other_Reference", r.other_reference),
            }
            for r in invoice.preceding_document_references
        ]
    if invoice.receipt_contract_references:
        payload["Receipt_Contract_References"] = [
            {
                **_opt("Receipt_Advice_Reference", r.receipt_advice_reference),
                **_opt("Receipt_Advice_Date", r.receipt_advice_date),
                **_opt("Tender_or_Lot_Reference", r.tender_or_lot_reference),
                **_opt("Contract_Reference", r.contract_reference),
                **_opt("External_Reference", r.external_reference),
                **_opt("Project_Reference", r.project_reference),
                **_opt("PO_Ref_Num", r.po_ref_num),
                **_opt("PO_Ref_Date", r.po_ref_date),
            }
            for r in invoice.receipt_contract_references
        ]

    # `INInvoice.check_supplier_address_required`/`check_recipient_address_required`
    # guarantee `seller.address`/`buyer.address` and their `province` are present by
    # the time a model is constructed, so both blocks below emit unconditionally.
    seller = invoice.seller
    payload["Supplier_Legal_Name"] = seller.name
    payload["Supplier_GSTIN"] = seller.tax_id.identifier
    assert seller.address is not None  # enforced by INInvoice.check_supplier_address_required
    # PartyAddress (core) has no second address line — schema field 4.5
    # (Supplier_Address2) is optional and cannot be populated from this
    # base model; only address1/place/state/pincode map cleanly.
    payload["Supplier_Address1"] = seller.address.street
    payload["Supplier_Place"] = seller.address.city
    payload["Supplier_Pincode"] = seller.address.postal_code
    payload["Supplier_State_Code"] = seller.address.province

    buyer = invoice.buyer
    payload["Recipient_Legal_Name"] = buyer.name
    payload["Recipient_GSTIN"] = buyer.tax_id.identifier
    assert buyer.address is not None  # enforced by INInvoice.check_recipient_address_required
    payload["Recipient_Address1"] = buyer.address.street
    payload["Recipient_Place"] = buyer.address.city
    payload["Recipient_Pincode"] = buyer.address.postal_code
    payload["Recipient_State_Code"] = buyer.address.province

    if invoice.payee is not None:
        p = invoice.payee
        payload.update(_opt("Payee_Name", p.payee_name))
        payload.update(_opt("Payee_Bank_Account_Number", p.payee_bank_account_number))
        payload.update(_opt("Mode_of_Payment", p.mode_of_payment))
        payload.update(_opt("Bank_Branch_Code", p.bank_branch_code))
        payload.update(_opt("Payment_Terms", p.payment_terms))
        payload.update(_opt("Payment_Instruction", p.payment_instruction))
        payload.update(_opt("Credit_Transfer_Terms", p.credit_transfer_terms))
        payload.update(_opt("Direct_Debit_Terms", p.direct_debit_terms))
        payload.update(_opt("Credit_Days", p.credit_days))

    if invoice.ship_to_details is not None:
        payload["Ship_To_Details"] = _serialize_address("ShipTo", invoice.ship_to_details)
    if invoice.dispatch_from_details is not None:
        payload["Dispatch_From_Details"] = _serialize_address(
            "DispatchFrom", invoice.dispatch_from_details
        )

    payload["Item_List"] = [_serialize_item(line) for line in invoice.lines]

    dt = invoice.document_total
    doc_total: dict[str, Any] = {"Taxable_Value_Total": dt.taxable_value_total}
    doc_total.update(_opt("IGST_Amt_Total", dt.igst_amt_total))
    doc_total.update(_opt("CGST_Amt_Total", dt.cgst_amt_total))
    doc_total.update(_opt("SGST_UTGST_Amt_Total", dt.sgst_utgst_amt_total))
    doc_total.update(_opt("Comp_Cess_Amt_Total", dt.comp_cess_amt_total))
    doc_total.update(_opt("State_Cess_Amt_Total", dt.state_cess_amt_total))
    doc_total.update(_opt("Discount_Amt_Invoice_Level", dt.discount_amt_invoice_level))
    doc_total.update(_opt("Other_Charges_Invoice_Level", dt.other_charges_invoice_level))
    doc_total.update(_opt("Round_Off_Amount", dt.round_off_amount))
    doc_total["Total_Invoice_Value_INR"] = dt.total_invoice_value_inr
    doc_total.update(_opt("Total_Invoice_Value_FCNR", dt.total_invoice_value_fcnr))
    doc_total.update(_opt("Paid_Amount", dt.paid_amount))
    doc_total.update(_opt("Amount_Due", dt.amount_due))
    payload["Document_Total_Details"] = doc_total

    payload.update(_opt("Tax_Scheme", invoice.tax_scheme))
    payload.update(_opt("Remarks", invoice.note))

    payload.update(_opt("Port_Code", invoice.port_code))
    payload.update(_opt("Shipping_Bill_Number", invoice.shipping_bill_number))
    payload.update(_opt("Shipping_Bill_Date", invoice.shipping_bill_date))
    payload.update(_opt("Export_Duty_Amount", invoice.export_duty_amount))
    if invoice.supplier_can_opt_refund is not None:
        payload["Supplier_Can_Opt_Refund"] = "Y" if invoice.supplier_can_opt_refund else "N"
    payload.update(_opt("ECOM_GSTIN", invoice.ecom_gstin))

    if invoice.additional_supporting_documents:
        payload["Additional_Supporting_Documents"] = [
            {
                **_opt(
                    "Additional_Supporting_Documents_URL", d.additional_supporting_documents_url
                ),
                **_opt(
                    "Additional_Supporting_Documents_base64",
                    d.additional_supporting_documents_base64,
                ),
                **_opt("Additional_Information", d.additional_information),
            }
            for d in invoice.additional_supporting_documents
        ]

    if invoice.eway_bill_details is not None:
        e = invoice.eway_bill_details
        eway: dict[str, Any] = {"Trans_Distance": e.trans_distance}
        eway.update(_opt("Transporter_ID", e.transporter_id))
        eway.update(_opt("Trans_Mode", e.trans_mode))
        eway.update(_opt("Transporter_Name", e.transporter_name))
        eway.update(_opt("Trans_Doc_No", e.trans_doc_no))
        eway.update(_opt("Trans_Doc_Date", e.trans_doc_date))
        eway.update(_opt("Vehicle_No", e.vehicle_no))
        eway.update(_opt("Vehicle_Type", e.vehicle_type))
        payload["Eway_Bill_Details"] = eway

    return {
        "payload": _decimal_to_str(payload),
        "document_type": invoice.document_type,
    }

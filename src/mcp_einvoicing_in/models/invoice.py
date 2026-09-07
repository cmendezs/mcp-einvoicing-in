"""India GST e-invoice models — extend mcp-einvoicing-core InvoiceDocument.

Invoice-tree pathway: `InvoiceDocument`, not `EN16931Invoice`. FORM GST INV-01
schema v1.1 is a flat JSON data dictionary with no EN 16931/UBL/CII lineage —
see `context-library/countries/in.md` ("Invoice-tree pathway") in the
`mcp-einvoicing` monorepo for the full rationale. `_IS_EN16931_FAMILY = False`
in `audit/audit_vs_core.py` must match this.

Field names mirror the schema's own `Technical_name_of_the_field` values
(lower-cased, unchanged spelling) so a reader can cross-reference this module
against `specs/FORM_GST_INV-01_schema_v1.1.pdf` directly. Every field below
traces to a schema row cited in its own docstring/description; nothing here
is invented from memory of "typical" GST e-invoice shapes.

The IRN, acknowledgement number/date, and signed QR code are IRP-generated,
never supplier-populated (schema field 1.1: "the supplier will not be
populating this field"). They are modeled separately in
`mcp_einvoicing_in.tools.in__qr` for the *response* side, not on this
request-side document model.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from mcp_einvoicing_core.models import InvoiceDocument, InvoiceLineItem
from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enumerated lists (schema fields 1.2, 1.3 — mandatory, closed enumerations)
# ---------------------------------------------------------------------------


class SupplyTypeCode(StrEnum):
    """Code for Supply Type (schema field 1.2)."""

    B2B = "B2B"
    B2C = "B2C"
    SEZWP = "SEZWP"
    SEZWOP = "SEZWOP"
    EXPWP = "EXPWP"
    EXPWOP = "EXPWOP"
    DEXP = "DEXP"


class DocumentTypeCode(StrEnum):
    """Code for Document Type (schema field 1.3). INV/CRN/DBN — the three
    document types in scope for this package's Phase 1 (all three
    `Document_Type_Code` values the schema defines)."""

    INV = "INV"
    CRN = "CRN"
    DBN = "DBN"


# ---------------------------------------------------------------------------
# Address blocks (schema A 1.0 Ship To Details, A 1.1 Dispatch From Details,
# and the flat Supplier/Recipient address fields 4.4-4.8, 5.5-5.10)
# ---------------------------------------------------------------------------


class INAddress(BaseModel):
    """Shared shape for Ship To / Dispatch From party+address blocks.

    Schema Annexure A 1.0 (Ship To, fields A.1.0.1-A.1.0.8) and A 1.1
    (Dispatch From, fields A.1.1.1-A.1.1.6 — no `gstin` field in Dispatch
    From per the schema; `gstin` is left optional here and simply unused by
    the Dispatch From builder).
    """

    legal_name: str = Field(..., max_length=100)
    trade_name: str | None = Field(default=None, max_length=100)
    gstin: str | None = Field(default=None, min_length=15, max_length=15)
    address1: str = Field(..., max_length=100)
    address2: str | None = Field(default=None, max_length=100)
    place: str = Field(..., max_length=100)
    pincode: int
    state_code: str = Field(..., min_length=2, max_length=2)


# ---------------------------------------------------------------------------
# Preceding document / contract references (schema section 3)
# ---------------------------------------------------------------------------


class INPrecedingDocumentReference(BaseModel):
    """Schema fields 3.1.1-3.1.3. Mandatory when this section is used — e.g.
    for CRN/DBN referencing the original invoice."""

    preceding_document_number: str = Field(..., max_length=16)
    preceding_document_date: str = Field(..., description="DD/MM/YYYY")
    other_reference: str | None = Field(default=None, max_length=20)


class INReceiptContractReference(BaseModel):
    """Schema fields 3.2.1-3.2.8 — sibling sub-header to 3.1, not nested
    under it, per the schema's own section numbering."""

    receipt_advice_reference: str | None = Field(default=None, max_length=20)
    receipt_advice_date: str | None = Field(default=None, description="DD/MM/YYYY")
    tender_or_lot_reference: str | None = Field(default=None, max_length=20)
    contract_reference: str | None = Field(default=None, max_length=20)
    external_reference: str | None = Field(default=None, max_length=20)
    project_reference: str | None = Field(default=None, max_length=20)
    po_ref_num: str | None = Field(default=None, max_length=16)
    po_ref_date: str | None = Field(default=None, description="DD/MM/YYYY")


# ---------------------------------------------------------------------------
# Payee information (schema section 6)
# ---------------------------------------------------------------------------


class INPayeeInformation(BaseModel):
    """Schema fields 6.1-6.9."""

    payee_name: str | None = Field(default=None, max_length=100)
    payee_bank_account_number: str | None = Field(default=None, max_length=18)
    mode_of_payment: str | None = Field(default=None, max_length=18)
    bank_branch_code: str | None = Field(
        default=None, max_length=11, description="IFSC of payee's bank branch"
    )
    payment_terms: str | None = Field(default=None, max_length=100)
    payment_instruction: str | None = Field(default=None, max_length=100)
    credit_transfer_terms: str | None = Field(default=None, max_length=100)
    direct_debit_terms: str | None = Field(default=None, max_length=100)
    credit_days: int | None = None


# ---------------------------------------------------------------------------
# Additional supporting documents (schema section 11) and e-way bill (12)
# ---------------------------------------------------------------------------


class INAdditionalSupportingDocument(BaseModel):
    """Schema fields 11.1-11.3."""

    additional_supporting_documents_url: str | None = Field(default=None, max_length=100)
    additional_supporting_documents_base64: str | None = Field(default=None, max_length=1000)
    additional_information: str | None = Field(default=None, max_length=1000)


class INEwayBillDetails(BaseModel):
    """Schema fields 12.1-12.8. Optional as a whole (section 12 is 0..1)."""

    transporter_id: str | None = Field(default=None, max_length=15)
    trans_mode: str | None = Field(
        default=None, description="1=Road, 2=Rail, 3=Air, 4=Ship (schema field 12.2)"
    )
    trans_distance: int
    transporter_name: str | None = Field(default=None, max_length=100)
    trans_doc_no: str | None = Field(default=None, max_length=15)
    trans_doc_date: str | None = Field(default=None, description="DD/MM/YYYY")
    vehicle_no: str | None = Field(default=None, max_length=20)
    vehicle_type: str | None = Field(
        default=None, description="O=Over-Dimensional Cargo, R=Regular (schema field 12.8)"
    )


# ---------------------------------------------------------------------------
# Item list (schema Annexure A 1.2 — item detail, A 1.4 batch, A 1.5 attributes)
# ---------------------------------------------------------------------------


class INBatchDetails(BaseModel):
    """Schema fields A.1.4.1-A.1.4.3."""

    batch_number: str = Field(..., max_length=20)
    batch_expiry_date: str | None = Field(default=None, description="DD/MM/YYYY")
    warranty_date: str | None = Field(default=None, description="DD/MM/YYYY")


class INProductAttribute(BaseModel):
    """Schema fields A.1.5.1-A.1.5.2."""

    attribute_name: str | None = Field(default=None, max_length=100)
    attribute_value: str | None = Field(default=None, max_length=100)


class INInvoiceLine(InvoiceLineItem):
    """GST e-invoice item (schema Annexure A 1.2, fields A.1.2.1-A.1.2.30).

    `InvoiceLineItem.vat_rate`/`vat_exemption_code` are not used — GST's
    IGST/CGST/SGST/UTGST/Cess split has no single-rate equivalent in the
    base model, so it is represented here as separate per-item fields
    instead, mirroring the schema's own field-per-tax-component shape.
    """

    sl_no: str = Field(..., max_length=6, description="Serial number of the item (A.1.2.1)")
    is_service: bool = Field(..., description="Y/N — whether the supply is a service (A.1.2.3)")
    hsn_code: str = Field(..., max_length=8, description="HSN/SAC code (A.1.2.4)")
    batch_details: INBatchDetails | None = None
    barcode: str | None = Field(default=None, max_length=30)
    free_qty: Decimal | None = None
    item_discount_amount: Decimal | None = None
    pre_tax_value: Decimal | None = None
    item_taxable_value: Decimal = Field(
        ...,
        ge=Decimal("0"),
        description="Value on which tax is computed (A.1.2.14) — cannot be negative",
    )
    gst_rate: Decimal = Field(
        ..., description="IGST rate, or sum of CGST & SGST rates, as a percentage (A.1.2.15)"
    )
    igst_amt: Decimal | None = None
    cgst_amt: Decimal | None = None
    sgst_utgst_amt: Decimal | None = None
    comp_cess_rate_ad_valorem: Decimal | None = None
    comp_cess_amt_ad_valorem: Decimal | None = None
    comp_cess_amt_non_ad_valorem: Decimal | None = None
    state_cess_rate_ad_valorem: Decimal | None = None
    state_cess_amt_ad_valorem: Decimal | None = None
    state_cess_amt_non_ad_valorem: Decimal | None = None
    other_charges_item_level: Decimal | None = None
    purchase_order_line_reference: str | None = Field(default=None, max_length=50)
    item_total_amt: Decimal = Field(
        ...,
        description=("Item total incl. all taxes/cesses/other charges, excl. discount (A.1.2.27)"),
    )
    origin_country_code: str | None = Field(
        default=None, description="ISO 3166-1 alpha-2 (A.1.2.28)"
    )
    unique_serial_number: str | None = Field(default=None, max_length=20)
    product_attribute_details: list[INProductAttribute] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_igst_xor_cgst_sgst(self) -> INInvoiceLine:
        """Schema A.1.2.16-A.1.2.18: 'If IGST is reported, then CGST & SGST/
        UTGST will be blank... either IGST or CGST & SGST/UTGST should be
        reported.'"""
        has_igst = self.igst_amt is not None
        has_cgst = self.cgst_amt is not None
        has_sgst = self.sgst_utgst_amt is not None
        if has_igst and (has_cgst or has_sgst):
            raise ValueError(
                "Item tax split invalid: IGST is mutually exclusive with CGST/SGST-UTGST "
                "(schema A.1.2.16-A.1.2.18)."
            )
        if has_cgst != has_sgst:
            raise ValueError(
                "Item tax split invalid: CGST and SGST/UTGST must be reported together "
                "(schema A.1.2.17-A.1.2.18)."
            )
        return self


# ---------------------------------------------------------------------------
# Document total (schema Annexure A 1.3)
# ---------------------------------------------------------------------------


class INDocumentTotalDetails(BaseModel):
    """Schema fields A.1.3.1-A.1.3.13."""

    taxable_value_total: Decimal = Field(..., description="Sum of item taxable values (A.1.3.1)")
    igst_amt_total: Decimal | None = None
    cgst_amt_total: Decimal | None = None
    sgst_utgst_amt_total: Decimal | None = None
    comp_cess_amt_total: Decimal | None = None
    state_cess_amt_total: Decimal | None = None
    discount_amt_invoice_level: Decimal | None = None
    other_charges_invoice_level: Decimal | None = None
    round_off_amount: Decimal | None = None
    total_invoice_value_inr: Decimal = Field(
        ..., description="Total invoice value incl. taxes/GST, rounded to 2 decimals (A.1.3.10)"
    )
    total_invoice_value_fcnr: Decimal | None = None
    paid_amount: Decimal | None = None
    amount_due: Decimal | None = None


# ---------------------------------------------------------------------------
# Top-level document
# ---------------------------------------------------------------------------


class INInvoice(InvoiceDocument):
    """GST e-invoice request document (FORM GST INV-01, schema v1.1).

    Maps onto `InvoiceDocument` as follows: `document_type` <- schema field
    1.3 (`Document_Type_Code`), `date` <- 1.5 (`Document_Date`), `number` <-
    1.4 (`Document_Num`), `currency` fixed `"INR"` (the schema has no INR
    enum value — INR is the implicit base currency; see `additional_currency
    _code` for the optional non-INR amount), `transmission_format` <- 1.2
    (`Supply_Type_Code`, a routing/scope hint, analogous to how IT uses
    `transmission_format` for FPA12/FPR12). `vat_summary` and `payment`
    (base fields) are intentionally left unused — GST's IGST/CGST/SGST/Cess
    totals live on `document_total`, and payee/payment details on `payee`,
    neither of which fits the base models' shapes.
    """

    version: str = Field(default="1.1", max_length=6, description="Schema version (field 1.0)")
    additional_currency_code: str | None = Field(
        default=None, min_length=3, max_length=3, description="Schema field 1.6"
    )
    reverse_charge: bool | None = Field(
        default=None, description="Whether tax liability is under reverse charge (field 1.7)"
    )
    igst_applicability_despite_supplier_and_recipient_located_in_same_state_ut: bool | None = Field(
        default=None, description="Schema field 1.8"
    )

    document_period_start_date: str | None = Field(default=None, description="DD/MM/YYYY (2.1)")
    document_period_end_date: str | None = Field(default=None, description="DD/MM/YYYY (2.2)")

    preceding_document_references: list[INPrecedingDocumentReference] = Field(default_factory=list)
    receipt_contract_references: list[INReceiptContractReference] = Field(default_factory=list)

    payee: INPayeeInformation | None = None

    ship_to_details: INAddress | None = None
    dispatch_from_details: INAddress | None = None

    lines: list[INInvoiceLine] = Field(default_factory=list, min_length=1)  # type: ignore[assignment]

    document_total: INDocumentTotalDetails

    tax_scheme: str = Field(default="GST", max_length=10, description="Schema field 10.1")

    port_code: str | None = Field(default=None, description="Schema field 10.3")
    shipping_bill_number: str | None = Field(default=None, max_length=20)
    shipping_bill_date: str | None = Field(default=None, description="DD/MM/YYYY")
    export_duty_amount: Decimal | None = None
    supplier_can_opt_refund: bool | None = Field(
        default=None, description="Deemed-export refund election (field 10.7)"
    )
    ecom_gstin: str | None = Field(
        default=None, min_length=15, max_length=15, description="e-Commerce operator GSTIN (10.8)"
    )

    additional_supporting_documents: list[INAdditionalSupportingDocument] = Field(
        default_factory=list
    )
    eway_bill_details: INEwayBillDetails | None = None

    @field_validator("document_type")
    @classmethod
    def check_document_type_code(cls, v: str) -> str:
        # Re-validated against the closed enum here (not just typed as DocumentTypeCode
        # directly on the base's `document_type: str` field) because InvoiceDocument
        # declares the field as plain `str`; a subclass cannot narrow an inherited
        # field's type without redeclaring it, which would duplicate the base field
        # definition — the one thing CLAUDE.md's canonical-invoice-tree rule forbids.
        DocumentTypeCode(v)
        return v

    @field_validator("transmission_format")
    @classmethod
    def check_supply_type_code(cls, v: str | None) -> str | None:
        if v is not None:
            SupplyTypeCode(v)
        return v

    @model_validator(mode="after")
    def check_seller_gstin(self) -> INInvoice:
        from mcp_einvoicing_core.models import TaxIdentifier

        gstin = self.seller.tax_id.identifier
        ok, error = TaxIdentifier.validate_in_gstin(gstin)
        if not ok:
            raise ValueError(f"Invalid Supplier_GSTIN: {error}")
        return self

    @model_validator(mode="after")
    def check_buyer_gstin_or_urp(self) -> INInvoice:
        """Schema field 5.3: Recipient_GSTIN accepts a real GSTIN, or the
        literal sentinel `"URP"` ("Unregistered Person") for exports or
        supplies to unregistered persons. `"URP"` is not itself a valid
        GSTIN shape, so it must be special-cased rather than run through
        `validate_in_gstin`."""
        from mcp_einvoicing_core.models import TaxIdentifier

        gstin = self.buyer.tax_id.identifier
        if gstin.strip().upper() == "URP":
            return self
        ok, error = TaxIdentifier.validate_in_gstin(gstin)
        if not ok:
            raise ValueError(f"Invalid Recipient_GSTIN: {error} (or use the literal 'URP')")
        return self

    @model_validator(mode="after")
    def check_document_total_igst_xor_cgst_sgst(self) -> INInvoice:
        """Same CGST+SGST/IGST pairing rule as `INInvoiceLine`, applied at
        the document-total level (schema A.1.3.2-A.1.3.4)."""
        dt = self.document_total
        has_igst = dt.igst_amt_total is not None
        has_cgst = dt.cgst_amt_total is not None
        has_sgst = dt.sgst_utgst_amt_total is not None
        if has_igst and (has_cgst or has_sgst):
            raise ValueError(
                "Document total tax split invalid: IGST is mutually exclusive with "
                "CGST/SGST-UTGST (schema A.1.3.2-A.1.3.4)."
            )
        if has_cgst != has_sgst:
            raise ValueError(
                "Document total tax split invalid: CGST and SGST/UTGST must be reported "
                "together (schema A.1.3.3-A.1.3.4)."
            )
        return self

    @model_validator(mode="after")
    def check_currency_is_inr(self) -> INInvoice:
        # InvoiceDocument.currency defaults to "EUR"; GST e-invoice is always
        # INR-denominated (see class docstring) — a caller must pass "INR"
        # explicitly rather than relying on the base default.
        if self.currency != "INR":
            raise ValueError(
                f"INInvoice.currency must be 'INR' (got {self.currency!r}); use "
                "additional_currency_code for a secondary reporting currency."
            )
        return self

"""MCP server entry point — registers all India GST e-invoicing tools."""

from typing import Any

from mcp_einvoicing_core import EInvoicingMCPServer

from mcp_einvoicing_in.tools.in__payload import in__build_invoice
from mcp_einvoicing_in.tools.in__qr import in__render_irp_qr_png
from mcp_einvoicing_in.tools.in__scope import in__get_supported_scope
from mcp_einvoicing_in.tools.in__validate import in__validate_invoice


def _register_in_tools(mcp: Any) -> None:
    """Register all India e-invoicing tools onto the shared FastMCP instance."""
    mcp.tool()(in__get_supported_scope)
    mcp.tool()(in__build_invoice)
    mcp.tool()(in__validate_invoice)
    mcp.tool()(in__render_irp_qr_png)


mcp = EInvoicingMCPServer(
    "mcp-einvoicing-in",
    instructions=(
        "Tools for Indian GST e-invoicing: build and structurally validate FORM GST "
        "INV-01 (schema v1.1) JSON payloads for INV/CRN/DBN document types, and render "
        "an IRP-returned signed QR string as a displayable PNG. GSTIN fields are "
        "validated via TaxIdentifier.validate_in_gstin as part of model construction. "
        "Phase A scope only — no live IRP submission (auth/token, generate-IRN, "
        "cancel-IRN); that is Phase B, blocked on the NIC e-invoice API spec, which has "
        "not been staged. See README and in__get_supported_scope for the full picture."
    ),
)
mcp.register_plugin(_register_in_tools, "in")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

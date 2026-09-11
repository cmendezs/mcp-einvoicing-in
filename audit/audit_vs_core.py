"""Pre-publish audit: verify mcp-einvoicing-in coherence against mcp-einvoicing-core.

Run standalone (from the workspace root):
    uv run python mcp-einvoicing-in/audit/audit_vs_core.py
    uv run python mcp-einvoicing-in/audit/audit_vs_core.py --output mcp-einvoicing-in/audit/report.json
    uv run python mcp-einvoicing-in/audit/audit_vs_core.py --fail-on blocking

Exit codes:
    0  All checks passed
    1  Warnings only (non-blocking)
    2  Blocking failures found

Build status (2026-09-07)
--------------------------
The invoice-tree pathway is resolved (``_IS_EN16931_FAMILY = False``,
``INInvoice``), so CHECK 1 (core interface coverage) runs for real. Phase A
is implemented: ``in__build_invoice``, ``in__validate_invoice``,
``in__render_irp_qr_png``, and ``in__get_supported_scope`` are all live
tools. GSTIN validation routes through core's
``TaxIdentifier.validate_in_gstin`` (core v1.31.0). Remaining [MISSING]
warnings below are core symbols genuinely unused by this package's current
scope (Peppol, digital signature, Schematron/XSD, PDF, mTLS http_client —
FORM GST INV-01 is plain JSON, has no Peppol leg, and Phase A performs no
network calls at all) — real future-scope gaps (mTLS http_client and OAuth2
token handling in particular would become relevant for Phase B's live IRP
submission), not overridden. See specs/README.md for what remains.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mcp_einvoicing_core.audit import (
    SEVERITY_BLOCKING,
    SEVERITY_OK,
    AuditReport,
    CheckFinding,
    CheckResult,
    make_report,
    parse_audit_args,
    render_summary_table,
    run_check_core_coverage,
    run_check_version_compatibility,
)

_PACKAGE = "mcp-einvoicing-in"
_MODULE = "mcp_einvoicing_in"
_ROOT = Path(__file__).resolve().parent.parent
_PYPROJECT = _ROOT / "pyproject.toml"
_SOURCES = _ROOT / "specs" / "README.md"

# ---------------------------------------------------------------------------
# CHECK 1 configuration — country-specific constants
# ---------------------------------------------------------------------------

# FORM GST INV-01 schema v1.1 is a flat JSON data dictionary with no EN
# 16931/UBL/CII lineage anywhere in the staged schema PDF — non-EN16931
# pathway, INInvoice extends InvoiceDocument. Same determination as
# mcp-cfdi-mx and mcp-nfe-br. See the package's own compliance reference,
# "Invoice-tree pathway".
_IS_EN16931_FAMILY: bool = False
_PRIMARY_INVOICE_CLASS: tuple[str, str] = ("mcp_einvoicing_in.models.invoice", "INInvoice")

_MODULES: list[str] = [
    f"{_MODULE}.server",
    f"{_MODULE}.models.invoice",
    f"{_MODULE}.tools.in__scope",
    f"{_MODULE}.tools.in__payload",
    f"{_MODULE}.tools.in__validate",
    f"{_MODULE}.tools.in__qr",
    f"{_MODULE}.validators.structural",
]

_INTENTIONAL_OVERRIDES: dict[str, set[str]] = {
    "mcp_einvoicing_core.base_server": {
        # OVERRIDE-REASON: EInvoicingMCPServer is imported from the top-level mcp_einvoicing_core package in server.py, not from base_server directly
        "EInvoicingMCPServer",
    },
    "mcp_einvoicing_core.models": {
        # OVERRIDE-REASON: InvoiceParty/PartyAddress/VATSummary/PaymentTerms are used only as inherited field types on InvoiceDocument (seller/buyer/vat_summary/payment) — GST's IGST/CGST/SGST/Cess split has no VATSummary-shaped equivalent, and payee/payment details live on this package's own INPayeeInformation instead, per models/invoice.py's class docstring
        "InvoiceParty",
        "PartyAddress",
        "VATSummary",
        "PaymentTerms",
        # OVERRIDE-REASON: GSTIN validation errors raise inline via a pydantic model_validator (ValueError), not via the TaxIdValidationResult wrapper type — same pattern as mcp-cfdi-mx's validate_mx_rfc usage
        "TaxIdValidationResult",
    },
}


def _finding(check_id: str, tag: str, severity: str, symbol: str, message: str) -> CheckFinding:
    return CheckFinding(
        check_id=check_id, tag=tag, severity=severity, symbol=symbol, message=message
    )


def run_check_0() -> CheckResult:
    """CHECK 0 — scaffold gates that block implementation and publication."""
    result = CheckResult(check_id="CHECK_0", name="Scaffold gates")

    result.findings.append(
        _finding(
            "CHECK_0", "[OK]", SEVERITY_OK, "_IS_EN16931_FAMILY", "Invoice-tree pathway declared."
        )
    )

    server_mod = __import__(f"{_MODULE}.server", fromlist=["mcp", "main"])
    for attr in ("mcp", "main"):
        present = hasattr(server_mod, attr)
        result.findings.append(
            _finding(
                "CHECK_0",
                "[OK]" if present else "[MISSING]",
                SEVERITY_OK if present else SEVERITY_BLOCKING,
                f"server.{attr}",
                f"server.{attr} is {'present' if present else 'absent'}.",
            )
        )

    return result


def run_check_5() -> CheckResult:
    """CHECK 5 — normative spec sources are recorded with an authority URL."""
    result = CheckResult(check_id="CHECK_5", name="Spec sources")

    if not _SOURCES.exists():
        result.findings.append(
            CheckFinding(
                check_id="CHECK_5",
                tag="[MISSING]",
                severity=SEVERITY_BLOCKING,
                symbol="specs/README.md",
                message="specs/README.md is absent. One authority URL per standard is required.",
            )
        )
        return result

    text = _SOURCES.read_text(encoding="utf-8")
    unresolved = text.count("[NEED:]")
    # Several rows carry a genuine open gap (NIC API spec, master code
    # lists, Notification 13/2020-CT, PAN format) rather than a missing
    # citation for an already-staged document — every staged document
    # (FORM GST INV-01 schema, Notifications 68/2019-CT, 72/2020-CT and
    # 10/2023-CT) has its authority URL and retrieval date filled in.
    # Tracked as `manual`
    # regulatory-watch rows once registered, not blocking — same precedent
    # as mcp-cfdi-mx's catálogos/matriz-de-errores rows.
    result.findings.append(
        CheckFinding(
            check_id="CHECK_5",
            tag="[OK]" if unresolved == 0 else "[NEED]",
            severity=SEVERITY_OK,
            symbol="specs/README.md",
            message=(
                "All spec sources carry an authority URL and a retrieval date."
                if unresolved == 0
                else (
                    f"{unresolved} pending-spec row(s) remain (NIC API spec, master code "
                    "lists, etc.) — every already-staged document has its own citation "
                    "filled in; the pending rows are genuine open gaps, not missing "
                    "citations for staged material."
                )
            ),
        )
    )

    return result


def run_audit() -> AuditReport:
    """Execute all checks and return the aggregated AuditReport. No side effects."""
    report = make_report(_PACKAGE, _PYPROJECT)

    report.checks.append(run_check_0())
    report.checks.append(
        run_check_core_coverage(
            package_name=_PACKAGE,
            package_modules=_MODULES,
            intentional_overrides=_INTENTIONAL_OVERRIDES,
            is_en16931_family=_IS_EN16931_FAMILY,
            primary_invoice_class=_PRIMARY_INVOICE_CLASS,
        )
    )
    report.checks.append(
        run_check_version_compatibility(
            package_name=_PACKAGE,
            pyproject_path=_PYPROJECT,
        )
    )
    report.checks.append(run_check_5())

    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_audit_args(f"Pre-publish audit: {_PACKAGE} vs mcp-einvoicing-core", argv)
    report = run_audit()

    output_path = Path(args.output) if args.output else _ROOT / "audit" / "report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    if not args.quiet:
        print(render_summary_table(report))
        print(f"\nJSON report written to: {output_path}")

    if args.fail_on == "never":
        return 0
    if args.fail_on == "warnings":
        return min(report.exit_code, 2)
    return 2 if report.total_blocking > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for mcp_einvoicing_in.tools.in__scope."""

from __future__ import annotations

from mcp_einvoicing_in.tools.in__scope import in__get_supported_scope


def test_returns_phase_a_scope() -> None:
    scope = in__get_supported_scope()
    assert scope.schema_version == "1.1"
    assert scope.phase == 1
    assert set(scope.supported_document_types) == {"INV", "CRN", "DBN"}
    assert set(scope.supported_supply_types) == {
        "B2B",
        "B2C",
        "SEZWP",
        "SEZWOP",
        "EXPWP",
        "EXPWOP",
        "DEXP",
    }


def test_out_of_scope_lists_phase_b_items() -> None:
    scope = in__get_supported_scope()
    assert any("Live IRP submission" in item for item in scope.out_of_scope)
    assert any("Signed QR content decoding" in item for item in scope.out_of_scope)

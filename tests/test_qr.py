"""Tests for IRP response modeling and QR rendering."""

from __future__ import annotations

import base64

import pytest
from pydantic import ValidationError

from mcp_einvoicing_in.tools.in__qr import IRPRegistrationResponse, in__render_irp_qr_png


class TestIRPRegistrationResponse:
    def test_valid_irn_length(self) -> None:
        irn = "a" * 64
        response = IRPRegistrationResponse(irn=irn)
        assert response.irn == irn

    def test_irn_wrong_length_rejected(self) -> None:
        with pytest.raises(ValidationError):
            IRPRegistrationResponse(irn="too_short")


class TestRenderIrpQrPng:
    def test_renders_png_base64(self) -> None:
        result = in__render_irp_qr_png("opaque-irp-signed-qr-string")
        decoded = base64.b64decode(result)
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"

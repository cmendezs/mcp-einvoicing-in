# mcp-einvoicing-in 🇮🇳

[English](README.md) | [हिन्दी](README.hi.md)

<!-- mcp-name: io.github.cmendezs/mcp-einvoicing-in -->

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
[![PyPI version](https://img.shields.io/pypi/v/mcp-einvoicing-in.svg)](https://pypi.org/project/mcp-einvoicing-in/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-einvoicing-in.svg)](https://pypi.org/project/mcp-einvoicing-in/)

A Python MCP server providing tools for Indian **GST e-invoicing**, per GSTN's **FORM GST INV-01
schema v1.1** (CGST Act 2017 s.31 + CGST Rule 48(4), Notification No. 68/2019-Central Tax). It
enables AI agents (Claude, IDEs) to build and structurally validate GST e-invoice JSON payloads
(INV, CRN, DBN document types) and render an IRP-returned signed QR string as a displayable image.

**Phase A scope.** This package covers offline payload building, structural validation, and GSTIN
tax-identifier validation only. It does **not** submit to the Invoice Registration Portal (IRP) —
live submission (auth/token, generate-IRN, cancel-IRN) is a later phase, blocked on the NIC
e-invoice API specification not yet being available to this project (see "Spec availability"
below). See [Available tools](#available-tools) for exactly what is implemented today.

---

## Introduction

This package is built on [**mcp-einvoicing-core**](https://github.com/cmendezs/mcp-einvoicing-core),
the shared base library for e-invoicing MCP servers. It provides the `InvoiceDocument` model base
and the `TaxIdentifier.validate_in_gstin` GSTIN validator.

`mcp-einvoicing-core` is installed automatically as a dependency, no additional step is required.

GST e-invoicing is a **clearance-model** system: an invoice becomes legally valid only once the
IRP (Invoice Registration Portal, operated by NIC) validates the supplier's JSON payload and
returns an Invoice Reference Number (IRN), acknowledgement number/date, and a signed QR code
(CGST Rule 48(4)/(5)). This package builds and structurally validates the request payload a
supplier would submit; it does not itself submit to the IRP (see "Phase A scope" above).

## Installation

### Via PyPI (recommended)

```bash
pip install mcp-einvoicing-in
```

Or without prior installation using `uvx`:

```bash
uvx mcp-einvoicing-in
```

### From source

```bash
git clone https://github.com/cmendezs/mcp-einvoicing-in.git
cd mcp-einvoicing-in
pip install -e ".[dev]"
```

## Configuration

This package requires no environment variables for its current (Phase A) scope — it performs no
network calls. Live IRP submission, once implemented, will require IRP/GSP credentials; this
section will be updated at that time.

## Claude Desktop integration

Add to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"]
    }
  }
}
```

## Cursor integration

Add the same `mcpServers` block to either:

- Global: `~/.cursor/mcp.json`
- Project-specific: `.cursor/mcp.json` in your project root

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"]
    }
  }
}
```

Reload Cursor (or run "Reload Window" from the command palette) after saving.

## Kiro integration

Add to either:

- Global: `~/.kiro/settings/mcp.json`
- Workspace: `.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Kiro reloads MCP configuration automatically on save. If a future version of this package
requires credentials, prefer `"VAR_NAME": "${VAR_NAME}"` shell-interpolation syntax over
plaintext secrets in this file.

## Available tools

### Scope

- `in__get_supported_scope` — returns the document types, supply types, and explicit
  out-of-scope items this package currently supports.

### Build and validate

- `in__build_invoice` — validates structured input against `INInvoice` and builds a GST
  e-invoice JSON payload (INV/CRN/DBN). Never emits `IRN` — that field is IRP-generated, never
  supplier-populated.
- `in__validate_invoice` — offline structural/business-rule validation: mandatory fields, enum
  membership, CGST+SGST-vs-IGST pairing (item and document-total level), and GSTIN/state-code
  consistency. There is no XSD/Schematron pass — FORM GST INV-01 is JSON, not XML.

### QR

- `in__render_irp_qr_png` — renders an IRP-returned signed QR string as a displayable PNG. Does
  not decode or interpret the QR's content — the NIC e-invoice API spec that would document that
  content is not yet available to this project (see "Spec availability" below).

## Spec availability

Retrieving current, exact NIC/GSTN technical specifications from outside India is unreliable: the
GSTN enforces strict geographic firewalls that routinely block or rate-limit non-Indian IP
addresses. This package was built entirely from specification documents supplied directly by the
maintainer (FORM GST INV-01 schema v1.1; CGST Notifications 68/2019-CT and 72/2020-CT; and
Notification No. 10/2023-CT, confirming the current AATO mandate threshold) — no document was
fetched from the internet by an automated agent. As a direct consequence:

- **Not yet available to this project:** comprehensive list in
  [`specs/README.md`](specs/README.md)'s "Pending specs" table.
- Live IRP submission tools cannot be built responsibly without the NIC e-invoice API spec — see
  "Phase A scope".

**If you are based in India and can supply any of the documents listed there**, please open an issue
using the [Spec Update issue template](https://github.com/cmendezs/mcp-einvoicing-in/issues/new?template=spec-update.yml).
The template captures the document name, official source URL, version, and retrieval date; a
follow-up pull request then adds the file under `specs/` together with a sources-table entry and
a provenance/redistribution affirmation. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full
two-step flow.

## Architecture

`INInvoice` subclasses `InvoiceDocument` (`mcp_einvoicing_core.models`) — FORM GST INV-01 has no
EN 16931/UBL/CII lineage (it is a flat JSON clearance-model schema), so this package follows the
`InvoiceDocument` pathway, the same one used by `mcp-cfdi-mx` (CFDI) and `mcp-nfe-br` (NF-e).
`INInvoiceLine` subclasses `InvoiceLineItem` to add the schema's GST/HSN/cess fields, which have
no equivalent in the base line-item model. GSTIN fields are validated via
`TaxIdentifier.validate_in_gstin`, called from `INInvoice`'s own model validators — this package
never reimplements identifier-validation logic locally. There is no Schematron/XSD validator
layer (`validators/structural.py` implements plain-Python business-rule checks instead), since
the wire format is JSON, not XML.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, the PR checklist, and commit style.

## Other e-invoicing MCP servers

| Country | Server |
|---------|--------|
| 🌍 Global | [mcp-einvoicing-core](https://github.com/cmendezs/mcp-einvoicing-core) |
| 🇧🇪 Belgium | [mcp-einvoicing-be](https://github.com/cmendezs/mcp-einvoicing-be) |
| 🇧🇷 Brazil | [mcp-nfe-br](https://github.com/cmendezs/mcp-nfe-br) |
| 🇫🇷 France | [mcp-facture-electronique-fr](https://github.com/cmendezs/mcp-facture-electronique-fr) |
| 🇩🇪 Germany | [mcp-einvoicing-de](https://github.com/cmendezs/mcp-einvoicing-de) |
| 🇮🇳 India | [mcp-einvoicing-in](https://github.com/cmendezs/mcp-einvoicing-in) |
| 🇮🇹 Italy | [mcp-fattura-elettronica-it](https://github.com/cmendezs/mcp-fattura-elettronica-it) |
| 🇲🇽 Mexico | [mcp-cfdi-mx](https://github.com/cmendezs/mcp-cfdi-mx) |
| 🇵🇱 Poland | [mcp-ksef-pl](https://github.com/cmendezs/mcp-ksef-pl) |
| 🇸🇬 Singapore | [mcp-invoicenow-sg](https://github.com/cmendezs/mcp-invoicenow-sg) |
| 🇪🇸 Spain | [mcp-facturacion-electronica-es](https://github.com/cmendezs/mcp-facturacion-electronica-es) |
| 🇦🇪 United Arab Emirates | [mcp-einvoicing-ae](https://github.com/cmendezs/mcp-einvoicing-ae) |

## License

This project is licensed under the **Apache 2.0** license — see [LICENSE](LICENSE) for details.
For the full version history, see [CHANGELOG.md](CHANGELOG.md).

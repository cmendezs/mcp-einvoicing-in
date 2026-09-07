# Contributing to mcp-einvoicing-in

Thank you for your interest in contributing. This document explains the workflow
and expectations.

## Development setup

```bash
git clone https://github.com/cmendezs/mcp-einvoicing-in.git
cd mcp-einvoicing-in
uv sync --all-extras
```

## Running the test suite

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

## Linting and type checking

```bash
uv run ruff check src/ tests/ audit/
uv run ruff format --check src/ tests/ audit/
uv run mypy src
```

To auto-fix lint issues:

```bash
uv run ruff check --fix src/ tests/ audit/
uv run ruff format src/ tests/ audit/
```

## Tool reference

The tool reference in `docs/TOOLS.md` is generated from the running MCP server.
If you add, remove, or change a tool or its parameters, regenerate it:

```bash
uv run python scripts/gen_tool_reference.py
```

The publish workflow regenerates it at release time, and `--check` mode reports
drift without writing:

```bash
uv run python scripts/gen_tool_reference.py --check
```

## Updating specification documents (spec-update)

Retrieving current, official NIC/GSTN specifications from outside India is
unreliable — GSTN enforces strict geographic firewalls that routinely block or
rate-limit non-Indian IP addresses. If you can supply an updated or missing
specification (see `specs/README.md`'s "Pending specs" table — the NIC e-invoice
API spec and master code lists are the most impactful gaps), use this two-step
flow:

1. **Open an issue** using the
   [Spec Update issue template](https://github.com/cmendezs/mcp-einvoicing-in/issues/new?template=spec-update.yml),
   naming the document, its official source URL, version, and your retrieval date.
2. **Deliver via pull request:** commit the file(s) under `specs/`, add a row to
   `specs/README.md`'s "Sources and versions" table (document, official URL,
   version, retrieved date), and confirm in the PR description that the document
   is an official government-published specification/notification and is freely
   redistributable.

## Pull request checklist

- [ ] All tests pass (`pytest`)
- [ ] No lint errors (`ruff check`)
- [ ] No type errors (`mypy src`)
- [ ] New or changed behaviour is covered by tests
- [ ] Any GST field/rule cited in a fix traces to a specific schema field number (e.g. `A.1.2.15`) or notification, not to memory
- [ ] `docs/TOOLS.md` regenerated if any tool or parameter changed
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add a new validation tool
fix: normalize party identifiers with leading zeros
docs: update README with configuration details
test: add fixture for a credit note
```

## Reporting issues

Please open an issue at https://github.com/cmendezs/mcp-einvoicing-in/issues and include:

- The tool name and input you used
- The expected result
- The actual result (full error message or unexpected output)
- The schema field number or notification involved, if known

Security issues follow a different path: see [SECURITY.md](SECURITY.md) and
report privately rather than in a public issue.

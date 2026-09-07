# Security Policy

## Supported versions

Security fixes are applied to the latest published minor release only. Older
versions do not receive backported patches; upgrade to the current release to
stay supported.

| Version | Supported |
|---|---|
| 0.1.x | Yes |
| < 0.1.0 | No |

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub, not in a public
issue or pull request:

1. Go to the repository Security tab: https://github.com/cmendezs/mcp-einvoicing-in/security
2. Select **Report a vulnerability** to open a private security advisory.
3. Describe the issue, the affected version, and a minimal reproduction.

You will receive an acknowledgement on a best-effort basis. This is a
volunteer-maintained open-source project, so response times vary; please allow
a reasonable window before any public disclosure.

## Scope and data-handling note

These tools generate and validate fiscal documents. When you file a report,
include only synthetic data. Never attach real GSTINs, PANs, production
credentials, API tokens, or live IRP/GSP credentials to an advisory. Redact
any such values from logs and reproductions before sharing.

## Out of scope

- Vulnerabilities in the underlying government platforms (GSTN, the IRP, or
  any GSP) that this package integrates with. Report those to the operator
  concerned.
- Findings that require a compromised local machine or a malicious dependency
  already installed in the runtime.

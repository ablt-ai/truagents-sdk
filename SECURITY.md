# Security Policy

Thank you for helping keep the TruAgents SDK ecosystem safe.

## Supported Versions

While the SDK is at `0.x`, only the latest minor release receives security fixes.

| Version | Supported |
|---------|-----------|
| `0.x` (latest minor) | Yes |
| `0.x` (older minors) | No |

Once we ship `1.0.0`, we will publish an explicit support policy (see
`docs/versioning.md`).

## Reporting a Vulnerability

Please report security vulnerabilities privately, **not** through public GitHub
issues.

- Email: <security@truagents.com>
- Subject: `[truagents-sdk] <short summary>`

If you would like to encrypt the report, request our PGP key at the same
address.

We follow a **90-day coordinated disclosure timeline**:

1. You email us with a description, reproduction, and impact assessment.
2. We acknowledge within **3 business days**.
3. We investigate, assign severity, and share a remediation plan within
   **10 business days**.
4. We ship a fix, coordinate disclosure timing with you, and credit the reporter
   (unless you prefer to remain anonymous).
5. If we cannot fix within 90 days, we work with you on a mutually acceptable
   extension.

## Scope

In scope:

- Source in this repository (`sdk/python/src/truagents/`, `codegen/`, workflows).
- Distributed artifacts from the `truagents` PyPI project.

Out of scope:

- Vulnerabilities in the TruAgents API itself — please report those directly to
  <security@truagents.com>.
- Vulnerabilities in third-party dependencies — please report to the upstream
  project first; if the SDK exposes them in a novel way, tell us as well.

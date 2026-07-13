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

## Serialization of Exceptions

`NetworkError.cause` carries the underlying `httpx` transport exception. `httpx` binds the originating request — including POST body — to `TransportError` instances at raise time. For the OAuth token endpoint, that POST body contains `client_secret` as a form field.

Do not serialize `NetworkError` to untrusted storage without scrubbing `cause.request.content` first. In particular:

- Avoid `pickle.dumps(err)` on caught `NetworkError` if the resulting bytes flow to logs, on-disk caches, message queues, or any storage that receives unrelated data.
- If you need to persist error context, extract the fields you actually need (`err.code`, `type(err.cause).__name__`, `str(err.cause)`) rather than the exception itself.
- The SDK never pickles exceptions internally; this concern only applies to partner code that catches SDK errors and serializes them.

The same guidance applies to `copy.deepcopy` chains that pass through unrelated storage.

## Scope

In scope:

- Source in this repository (`sdk/python/src/truagents/`, `codegen/`, workflows).
- Distributed artifacts from the `truagents` PyPI project.

Out of scope:

- Vulnerabilities in the TruAgents API itself — please report those directly to
  <security@truagents.com>.
- Vulnerabilities in third-party dependencies — please report to the upstream
  project first; if the SDK exposes them in a novel way, tell us as well.

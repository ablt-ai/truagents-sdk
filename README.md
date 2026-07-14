# TruAgents SDK

Official open-source SDKs for the [TruAgents Unsubscribe API](https://docs.truagents.com).

This repository is a **monorepo** hosting client libraries in multiple
languages. All SDKs are generated from the same public OpenAPI spec at
`https://docs.truagents.com/openapi/truagents.json` and share the same design
principles (typed errors, auto-refresh OAuth, retry with `Retry-After`
honouring, observability hooks).

## Languages

| Language   | Path                                       | Status                                                                                                                                                                                                                                              | Package                                                                                                              |
|------------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Python     | [`sdk/python/`](./sdk/python/)             | [![contract-python](https://github.com/ablt-ai/truagents-sdk/actions/workflows/contract-python.yml/badge.svg?branch=main)](https://github.com/ablt-ai/truagents-sdk/actions/workflows/contract-python.yml?branch=main)                              | [![PyPI](https://img.shields.io/pypi/v/truagents.svg)](https://pypi.org/project/truagents/)                          |
| TypeScript | `sdk/nodejs/`                              | Planned (Phase 2)                                                                                                                                                                                                                                   | `@truagents/nodejs` (npm)                                                                                            |
| Go         | `sdk/go/`                                  | Planned (Phase 2)                                                                                                                                                                                                                                   | `github.com/ablt-ai/truagents-sdk/sdk/go`                                                                            |
| Java       | `sdk/java/`                                | Planned (Phase 2)                                                                                                                                                                                                                                   | `com.truagents:sdk` (Maven Central)                                                                                  |

## Repository layout

```
.
├── README.md                    # this file
├── LICENSE                      # Apache 2.0
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── docs/
│   ├── releasing.md             # release runbook
│   └── versioning.md            # release cadence + semver policy
├── codegen/
│   ├── requirements.txt         # openapi-python-client + ruff pins
│   └── generate-python.sh       # regenerates sdk/python/src/truagents/generated/
├── scripts/
│   ├── check_release_version.py # CI guard: version bump matches tag
│   └── prepare-release.sh       # local release helper
├── sdk/
│   └── python/                  # Phase 1 SDK
└── .github/
    ├── CODEOWNERS
    ├── dependabot.yml
    └── workflows/               # contract-python, release-python, spec-sync, tag-release
```

## Stability

All SDKs are currently at `0.x`. Minor bumps may introduce breaking changes.
See [`docs/versioning.md`](./docs/versioning.md) for the full policy and the
`1.0.0` promotion criteria.

## Links

- **Docs**: <https://docs.truagents.com>
- **OpenAPI spec**: <https://docs.truagents.com/openapi/truagents.json>
- **Contributing**: [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- **Security**: [`SECURITY.md`](./SECURITY.md)
- **License**: Apache 2.0 — see [`LICENSE`](./LICENSE)

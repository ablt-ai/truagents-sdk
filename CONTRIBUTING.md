# Contributing to the TruAgents SDK

Thanks for your interest in improving the TruAgents SDK. This document covers
local setup, coding conventions, and the pull-request flow. If anything is
unclear, please open an issue or a draft PR — we would rather explain the same
thing twice than have you stuck.

## Repository layout

The repository is a monorepo:

- `sdk/python/` — Python SDK source, tests, examples.
- `codegen/` — shared codegen tooling that produces language-specific bindings
  from the public OpenAPI spec.
- `docs/` — cross-cutting policy and design documents.
- `.github/workflows/` — CI/CD pipelines.

Additional languages (`sdk/nodejs/`, `sdk/go/`, `sdk/java/`) will land as
separate sub-stories after the Python SDK stabilises.

## Local development (Python SDK)

Requires Python `>= 3.11`.

```bash
git clone https://github.com/ablt-ai/truagents-sdk.git
cd truagents-sdk
python -m venv .venv
source .venv/bin/activate
pip install -e "sdk/python[dev]"
pytest sdk/python/tests/unit -v
```

Contract tests (`sdk/python/tests/contract/`) require staging credentials and
are skipped locally unless `CLIENT_ID` and `CLIENT_SECRET` are set.

## Coding conventions

- Ruff and pyright configuration lives in `sdk/python/pyproject.toml`.
- Run `ruff format` and `ruff check --fix` before committing.
- Type hints are required on all public functions and dataclasses.
- The public API is exported from `truagents/__init__.py`; do not add
  side-effecting imports there.

## Generated code

The Python client under `sdk/python/src/truagents/generated/` is the output of
`bash codegen/generate-python.sh`, which invokes
[`openapi-python-client`](https://github.com/openapi-generators/openapi-python-client)
against the public spec at
`https://docs.truagents.com/openapi/truagents.json`.

**Do not hand-edit files under `sdk/python/src/truagents/generated/`.** If the
spec changes, re-run the script; the nightly `spec-sync` workflow does the same
and opens a PR when drift is detected.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

<body — WHY, not WHAT>
```

Common types: `feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`.

## Branch naming

- `feat/<short-slug>` for new features.
- `fix/<short-slug>` for bug fixes.
- `chore/<short-slug>` for tooling, docs, or maintenance.

## Pull requests

Please make sure the PR:

- Passes `pytest sdk/python/tests/unit -v`.
- Passes `ruff check sdk/python/src sdk/python/tests`.
- Passes `pyright sdk/python/src`.
- Updates `sdk/python/README.md` if the public API changes.
- Includes a note under `docs/versioning.md` if it introduces a breaking
  change during the `0.x` phase.

## Security issues

Please report vulnerabilities privately per [`SECURITY.md`](./SECURITY.md).

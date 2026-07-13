# Releasing the Python SDK

## Overview

Releases fire on the push of a `sdk-python-v<version>` tag. The
[`release-python.yml`](../.github/workflows/release-python.yml) workflow picks
the tag up, builds the sdist and wheel, and publishes to PyPI via OIDC trusted
publishing — no long-lived tokens live in the repository. The published version
is whatever `sdk/python/src/truagents/__version__.py` records on the tagged
commit, so the tag name and the module version must agree.

## Prerequisites

Before starting a release, confirm:

- Your working tree is clean and checked out on `main`.
- Local `main` is up to date with `origin/main`.
- The [`gh`](https://cli.github.com/) CLI is installed and authenticated
  (`gh auth status`).
- `python -m build` is available locally
  (`python -m pip install --upgrade build`) — the prep script uses it for a
  pre-flight sanity check.

## Making a release

The maintainer flow is three steps: prepare locally, merge via GitHub, let CI
tag and publish.

### 1. Prepare the release PR

From the repository root:

```bash
./scripts/prepare-release.sh <version>
```

The script validates the version string, confirms the preconditions above,
bumps `sdk/python/src/truagents/__version__.py`, runs a local build sanity
check, commits, pushes a `release/sdk-python-v<version>` branch, and opens a
release PR against `main`.

Accepted version formats:

- `0.1.0` — final release.
- `0.1.0.dev0` — development pre-release.
- `0.1.0.rc1` — release candidate.
- `0.1.0.post1` — post-release fix.

### 2. Review and merge the release PR

Review the PR on GitHub. Any merge strategy works — squash, merge commit, or
rebase — because the auto-tag workflow places the tag on the resulting merge
commit SHA regardless.

### 3. Automatic tag and publish

Once the release PR merges, the
[`tag-release.yml`](../.github/workflows/tag-release.yml) workflow detects the
merge, creates the annotated `sdk-python-v<version>` tag on the merge commit,
and pushes it. That tag push fires `release-python.yml`, which publishes to
PyPI and cuts a GitHub Release. The workflow comments on the release PR with a
link to the running publish job.

## First-time PyPI setup

Before the first real release, register a pending trusted publisher on PyPI:

- Visit [pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/).
- Publisher: GitHub. Repository owner: `ablt-ai`. Repository name:
  `truagents-sdk`.
- Workflow filename: `release-python.yml`.
- Environment: `pypi`.

The initial `truagents` namespace on PyPI was reserved by pushing a
`sdk-python-v0.0.0.dev0` placeholder tag from `main`, which produced a
development release visible in the PyPI project history. After that
reservation, real releases follow the normal three-step flow above.

## Fallback: manual tag push

Maintainers who prefer explicit control can skip the auto-tag workflow and push
the tag by hand after the release PR merges:

```bash
git fetch origin
git checkout main
git pull --ff-only
MERGE_SHA=$(git rev-parse origin/main)
git tag -a sdk-python-v<version> "$MERGE_SHA" -m "Release v<version>"
git push origin sdk-python-v<version>
```

The tag push still fires `release-python.yml`, so publication proceeds
identically.

## Known follow-ups

- **Preview via TestPyPI.** A `workflow_dispatch` path on `release-python.yml`
  that publishes to `test.pypi.org` for dry-run validation is not implemented
  yet. Track this as a future improvement to `release-python.yml`.

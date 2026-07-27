#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/sdk/python/src/truagents/generated"

openapi-python-client generate \
  --url https://docs.truagents.com/openapi/truagents.json \
  --output-path "$OUTPUT_DIR" \
  --meta none \
  --overwrite

ruff format --line-length 88 "$OUTPUT_DIR"
ruff check --line-length 88 --fix --exit-zero "$OUTPUT_DIR"

# Fail closed on syntax errors (always-on) and undefined names; benign style is
# handled above and lint-excluded in pyproject. generated/ is out of `ruff check
# src` + `pyright src`, so this is the only fail-closed gate on codegen output.
ruff check --select F821 "$OUTPUT_DIR"

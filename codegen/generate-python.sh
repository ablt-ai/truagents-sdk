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
ruff check --line-length 88 --fix "$OUTPUT_DIR"

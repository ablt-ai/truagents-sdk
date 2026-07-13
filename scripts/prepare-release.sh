#!/usr/bin/env bash
# Usage: ./scripts/prepare-release.sh <version>
# Examples: ./scripts/prepare-release.sh 0.2.0
#           ./scripts/prepare-release.sh 0.2.0.rc1
#           ./scripts/prepare-release.sh 0.2.0.dev0
#
# See docs/releasing.md for the full flow.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION_FILE="$REPO_ROOT/sdk/python/src/truagents/__version__.py"
BUILD_CHECK_DIR="/tmp/truagents-release-check-$$"

cleanup() {
  rm -rf "$BUILD_CHECK_DIR"
}
trap cleanup EXIT

die_validation() {
  echo "prepare-release.sh: $1" >&2
  exit 2
}

die_git() {
  echo "prepare-release.sh: $1" >&2
  exit 3
}

if [[ $# -ne 1 ]]; then
  die_validation "usage: $(basename "$0") <version> (e.g. 0.1.1, 0.2.0.rc1, 0.1.0.dev0)"
fi

VERSION="$1"
VERSION_REGEX='^[0-9]+\.[0-9]+\.[0-9]+(\.dev[0-9]+|\.rc[0-9]+|\.post[0-9]+)?$'

if [[ ! "$VERSION" =~ $VERSION_REGEX ]]; then
  die_validation "version '$VERSION' does not match ${VERSION_REGEX}. Examples: 0.1.1, 0.2.0.rc1, 0.1.0.dev0, 0.1.0.post1."
fi

cd "$REPO_ROOT"

CURRENT_BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null)" \
  || die_validation "not on a named branch (detached HEAD?). Run: git checkout main"
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  die_validation "must run from 'main', currently on '$CURRENT_BRANCH'. Run: git checkout main"
fi

if [[ -n "$(git status --porcelain)" ]]; then
  die_validation "working tree not clean. Commit or stash your changes first."
fi

echo "prepare-release.sh: fetching origin..."
git fetch origin main --quiet || die_git "git fetch origin main failed"

LOCAL_SHA="$(git rev-parse main)"
REMOTE_SHA="$(git rev-parse origin/main)"
if [[ "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
  die_validation "local main ($LOCAL_SHA) is not up to date with origin/main ($REMOTE_SHA). Run: git pull --ff-only"
fi

if ! python -c "import build" 2>/dev/null; then
  die_validation "'python -m build' is not installed. Run: python -m pip install --upgrade build"
fi

if ! command -v gh >/dev/null 2>&1; then
  die_validation "'gh' CLI is not installed. See https://cli.github.com/"
fi

if ! gh auth status >/dev/null 2>&1; then
  die_validation "'gh' CLI is not authenticated. Run: gh auth login"
fi

RELEASE_BRANCH="release/sdk-python-v${VERSION}"

if git show-ref --verify --quiet "refs/heads/${RELEASE_BRANCH}"; then
  die_validation "branch '${RELEASE_BRANCH}' already exists locally. Delete it first: git branch -D ${RELEASE_BRANCH}"
fi

if git ls-remote --exit-code --heads origin "$RELEASE_BRANCH" >/dev/null 2>&1; then
  die_validation "branch '${RELEASE_BRANCH}' already exists on origin. Delete it: git push origin --delete ${RELEASE_BRANCH}"
fi

echo "prepare-release.sh: creating branch ${RELEASE_BRANCH}..."
git checkout -b "$RELEASE_BRANCH" || die_git "failed to create branch ${RELEASE_BRANCH}"

echo "prepare-release.sh: bumping __version__ to ${VERSION}..."
sed -i.bak "s/^__version__ = \".*\"$/__version__ = \"${VERSION}\"/" "$VERSION_FILE"
rm -f "${VERSION_FILE}.bak"

if ! grep -q "^__version__ = \"${VERSION}\"$" "$VERSION_FILE"; then
  die_validation "failed to bump __version__ in ${VERSION_FILE}. Inspect the file and retry."
fi

echo "prepare-release.sh: running local build sanity check..."
mkdir -p "$BUILD_CHECK_DIR"
python -m build "$REPO_ROOT/sdk/python" -o "$BUILD_CHECK_DIR" >/dev/null

# Match dashes and underscores; PEP 625 rewrote sdist names in newer `build`.
shopt -s nullglob
BUILD_ARTIFACTS=("$BUILD_CHECK_DIR"/truagents-"${VERSION}"* "$BUILD_CHECK_DIR"/truagents_"${VERSION}"*)
shopt -u nullglob
if [[ ${#BUILD_ARTIFACTS[@]} -eq 0 ]]; then
  echo "prepare-release.sh: build output did not contain 'truagents-${VERSION}' artefact:" >&2
  ls -1 "$BUILD_CHECK_DIR" >&2
  exit 2
fi

echo "prepare-release.sh: committing..."
git add "$VERSION_FILE"
git commit -m "chore(release): prepare v${VERSION}" -m "Bumps __version__ to ${VERSION} for the sdk-python-v${VERSION} release.

The tag-release workflow will auto-tag main on merge, firing
release-python.yml to publish to PyPI.

See docs/releasing.md for the full flow." || die_git "commit failed"

echo "prepare-release.sh: pushing ${RELEASE_BRANCH}..."
git push -u origin "$RELEASE_BRANCH" || die_git "push failed"

PR_BODY="$(cat <<EOF
Release preparation for \`sdk-python-v${VERSION}\`. This PR only bumps
\`sdk/python/src/truagents/__version__.py\`.

## Release notes

<!-- Fill in before merging. -->

## What happens after merge

The [\`tag-release.yml\`](../blob/main/.github/workflows/tag-release.yml)
workflow will:

1. Create the annotated tag \`sdk-python-v${VERSION}\` on the merge commit.
2. Push it to \`origin\`, firing
   [\`release-python.yml\`](../blob/main/.github/workflows/release-python.yml).
3. Publish the sdist and wheel to PyPI via OIDC trusted publishing.
4. Cut a GitHub Release from the tag.

See [\`docs/releasing.md\`](../blob/main/docs/releasing.md) for the full flow
and the manual-tag fallback.
EOF
)"

echo "prepare-release.sh: opening PR..."
PR_URL="$(gh pr create \
  --base main \
  --head "$RELEASE_BRANCH" \
  --title "chore(release): v${VERSION}" \
  --body "$PR_BODY")" || die_git "gh pr create failed"

echo
echo "prepare-release.sh: done."
echo
echo "  PR: ${PR_URL}"
echo
echo "Next steps:"
echo "  1. Review the PR and fill in the release notes."
echo "  2. Merge via GitHub (any strategy — squash/merge/rebase all work)."
echo "  3. tag-release.yml will tag the merge commit and fire release-python.yml."
echo

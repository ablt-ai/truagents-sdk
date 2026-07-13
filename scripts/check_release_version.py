#!/usr/bin/env python3
"""Validate a proposed new release version for the truagents SDK.

Checks that the argument is a valid PEP 440 version and is strictly
greater than the current version in
sdk/python/src/truagents/__version__.py.

Usage: scripts/check_release_version.py <new_version>

Exit codes:
    0  new version is valid and strictly greater than current
    2  validation failed (see stderr for details)

Invoked by scripts/prepare-release.sh; also usable standalone.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

from packaging.version import InvalidVersion, Version


REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "sdk" / "python" / "src" / "truagents" / "__version__.py"


def die(msg: str) -> None:
    print(f"check_release_version.py: {msg}", file=sys.stderr)
    sys.exit(2)


def read_current_version() -> str:
    try:
        ns = runpy.run_path(str(VERSION_FILE))
    except Exception as exc:
        die(
            f"could not read __version__ from {VERSION_FILE}. "
            f'Expected content shape: __version__ = "X.Y.Z". Cause: {exc}'
        )
    try:
        return ns["__version__"]
    except KeyError as exc:
        die(
            f"could not read __version__ from {VERSION_FILE}. "
            f'Expected content shape: __version__ = "X.Y.Z". Cause: {exc} not defined.'
        )


def main() -> int:
    if len(sys.argv) != 2:
        die("usage: check_release_version.py <new_version>")

    new_str = sys.argv[1]
    try:
        new_v = Version(new_str)
    except (InvalidVersion, TypeError):
        die(
            f"version '{new_str}' is not a valid PEP 440 version. "
            "Examples: 0.1.1, 0.2.0.rc1, 0.1.0.dev0, 0.1.0.post1."
        )

    current_str = read_current_version()
    try:
        current_v = Version(current_str)
    except (InvalidVersion, TypeError):
        die(f"current version {current_str!r} from {VERSION_FILE} is not a valid PEP 440 version.")

    if new_v <= current_v:
        die(
            f"version '{new_str}' is not greater than current '{current_str}' on main. "
            f"Choose a version greater than '{current_str}'."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

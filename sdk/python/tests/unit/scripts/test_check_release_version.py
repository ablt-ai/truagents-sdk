"""Tests for scripts/check_release_version.py.

The checker is invoked as a subprocess so we exercise the real exit codes and
stderr diagnostics the way ``prepare-release.sh`` sees them.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_release_version.py"
VERSION_FILE_REL = Path("sdk") / "python" / "src" / "truagents" / "__version__.py"


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def _current_version() -> str:
    ns: dict[str, object] = {}
    exec((REPO_ROOT / VERSION_FILE_REL).read_text(), ns)
    return str(ns["__version__"])


def test_greater_version_exits_zero() -> None:
    result = _run(["999.999.999"])
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_pre_release_greater_than_current_exits_zero() -> None:
    result = _run(["0.2.0.rc1"])
    assert result.returncode == 0, result.stderr


def test_equal_version_exits_two_with_monotonic_msg() -> None:
    current = _current_version()
    result = _run([current])
    assert result.returncode == 2
    assert "is not greater than current" in result.stderr


def test_lesser_version_exits_two_with_monotonic_msg() -> None:
    result = _run(["0.0.0.dev1"])
    assert result.returncode == 2
    assert "is not greater than current" in result.stderr


def test_invalid_pep440_exits_two_with_format_msg() -> None:
    result = _run(["not-a-version"])
    assert result.returncode == 2
    assert "not a valid PEP 440 version" in result.stderr


def test_missing_argument_exits_two_with_usage_msg() -> None:
    result = _run([])
    assert result.returncode == 2
    assert "usage:" in result.stderr


def test_missing_version_file_exits_two(tmp_path: Path) -> None:
    """When __version__.py is missing, the checker should fail loudly."""
    fake_repo = tmp_path / "repo"
    (fake_repo / "scripts").mkdir(parents=True)
    (fake_repo / "sdk" / "python" / "src" / "truagents").mkdir(parents=True)
    shutil.copy(SCRIPT_PATH, fake_repo / "scripts" / "check_release_version.py")
    # Deliberately do NOT create __version__.py.

    result = subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "check_release_version.py"), "0.1.1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "could not read __version__" in result.stderr


def test_invalid_current_version_exits_two(tmp_path: Path) -> None:
    """When __version__.py contains a non-PEP-440 string, the checker reports it."""
    fake_repo = tmp_path / "repo"
    (fake_repo / "scripts").mkdir(parents=True)
    version_dir = fake_repo / "sdk" / "python" / "src" / "truagents"
    version_dir.mkdir(parents=True)
    (version_dir / "__version__.py").write_text('__version__ = "not-a-version"\n')
    shutil.copy(SCRIPT_PATH, fake_repo / "scripts" / "check_release_version.py")

    result = subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "check_release_version.py"), "0.1.1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "current version 'not-a-version'" in result.stderr


@pytest.mark.parametrize(
    "version",
    ["0.1.1", "0.2.0", "1.0.0", "0.1.0.post1"],
)
def test_various_valid_greater_versions(version: str) -> None:
    result = _run([version])
    assert result.returncode == 0, result.stderr

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_release_version.py"
VERSION_FILE_REL = Path("sdk") / "python" / "src" / "truagents" / "__version__.py"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def _current_version() -> str:
    ns: dict[str, object] = {}
    exec((REPO_ROOT / VERSION_FILE_REL).read_text(), ns)
    return str(ns["__version__"])


def _isolated_repo(tmp_path: Path, version_file_body: str | None) -> Path:
    fake_repo = tmp_path / "repo"
    (fake_repo / "scripts").mkdir(parents=True)
    version_dir = fake_repo / "sdk" / "python" / "src" / "truagents"
    version_dir.mkdir(parents=True)
    if version_file_body is not None:
        (version_dir / "__version__.py").write_text(version_file_body)
    shutil.copy(SCRIPT_PATH, fake_repo / "scripts" / "check_release_version.py")
    return fake_repo


def _run_in(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "check_release_version.py"), *args],
        capture_output=True,
        text=True,
    )


class TestExitZero:
    def test_greater_version_exits_zero(self):
        result = _run(["999.999.999"])
        assert result.returncode == 0, result.stderr
        assert result.stderr == ""

    def test_pre_release_greater_than_current_exits_zero(self):
        result = _run(["0.2.0.rc1"])
        assert result.returncode == 0, result.stderr

    @pytest.mark.parametrize("version", ["0.1.1", "0.2.0", "1.0.0", "0.1.0.post1"])
    def test_various_valid_greater_versions(self, version: str):
        result = _run([version])
        assert result.returncode == 0, result.stderr


class TestMonotonicRejection:
    def test_equal_version_exits_two(self):
        current = _current_version()
        result = _run([current])
        assert result.returncode == 2
        assert "is not greater than current" in result.stderr

    def test_lesser_version_exits_two(self):
        result = _run(["0.0.0.dev1"])
        assert result.returncode == 2
        assert "is not greater than current" in result.stderr


class TestFormatRejection:
    def test_invalid_pep440_exits_two(self):
        result = _run(["not-a-version"])
        assert result.returncode == 2
        assert "not a valid PEP 440 version" in result.stderr


class TestUsageRejection:
    def test_missing_arg_exits_two(self):
        result = _run([])
        assert result.returncode == 2
        assert "usage:" in result.stderr


class TestFilesystemErrors:
    def test_missing_version_file_exits_two(self, tmp_path: Path):
        repo = _isolated_repo(tmp_path, version_file_body=None)
        result = _run_in(repo, ["0.1.1"])
        assert result.returncode == 2
        assert "could not read __version__" in result.stderr

    def test_invalid_current_version_exits_two(self, tmp_path: Path):
        repo = _isolated_repo(tmp_path, version_file_body='__version__ = "not-a-version"\n')
        result = _run_in(repo, ["0.1.1"])
        assert result.returncode == 2
        assert "current version 'not-a-version'" in result.stderr

    def test_non_string_version_exits_two(self, tmp_path: Path):
        repo = _isolated_repo(tmp_path, version_file_body="__version__ = (0, 1, 0)\n")
        result = _run_in(repo, ["0.1.1"])
        assert result.returncode == 2
        assert "not a valid PEP 440 version" in result.stderr
        assert "Traceback" not in result.stderr

    def test_missing_version_key_exits_two(self, tmp_path: Path):
        repo = _isolated_repo(tmp_path, version_file_body='VERSION = "0.1.0"\n')
        result = _run_in(repo, ["0.1.1"])
        assert result.returncode == 2
        assert "could not read __version__" in result.stderr

"""Tests for the ``project-init`` command surface (``src/project_init/cli.py``).

The CLI is a thin typer entry point (ADR-001 §1): it parses args, loads the manifest
and delegates to the adapters. These tests drive it through ``CliRunner`` with the
forge adapter stubbed, so they exercise argument parsing, manifest loading and the
error paths without invoking the real generator.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from project_init import cli
from project_init.standards_profile_resolver import ProfileError

runner = CliRunner()


@pytest.fixture
def manifest(tmp_path: Path) -> Path:
    """A repo dir carrying a valid ``.project-init.yaml`` with one module and a profile."""
    (tmp_path / cli._MANIFEST_NAME).write_text(
        "name: demo-repo\n"
        "type: python-fastapi\n"
        "standards_profile: python-service\n"
        "modules:\n"
        "  - name: users\n",
        encoding="utf-8",
    )
    return tmp_path


def test_list_types() -> None:
    result = runner.invoke(cli.app, ["list-types"])
    assert result.exit_code == 0
    assert "python-fastapi" in result.stdout


def test_init_delegates_to_forge(manifest: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    def fake_generate(self, mani, path, dry_run):  # noqa: ANN001
        calls["modules"] = len(mani.modules)
        calls["dry_run"] = dry_run

    monkeypatch.setattr(cli.ForgeAdapter, "generate", fake_generate)
    result = runner.invoke(cli.app, ["init", str(manifest), "--dry-run"])
    assert result.exit_code == 0
    assert calls == {"modules": 1, "dry_run": True}
    assert "Generated 1 module(s)" in result.stdout


def test_init_missing_manifest_errors(tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["init", str(tmp_path)])
    assert result.exit_code != 0


def test_standards_uses_manifest_profile(manifest: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _Domain:
        domain_id = "STD-SEC"
        home = "standards/rules/security"
        prefix = "SEC"

    class _Resolver:
        @classmethod
        def from_files(cls, *_):  # noqa: ANN206
            return cls()

        def applicable_domains(self, name):  # noqa: ANN001
            assert name == "python-service"
            return [_Domain()]

    monkeypatch.setattr(cli, "StandardsProfileResolver", _Resolver)
    result = runner.invoke(cli.app, ["standards", str(manifest)])
    assert result.exit_code == 0
    assert "python-service" in result.stdout
    assert "STD-SEC" in result.stdout


def test_standards_explicit_profile_overrides(manifest: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resolver:
        @classmethod
        def from_files(cls, *_):  # noqa: ANN206
            return cls()

        def applicable_domains(self, name):  # noqa: ANN001
            assert name == "cli-tool"
            return []

    monkeypatch.setattr(cli, "StandardsProfileResolver", _Resolver)
    result = runner.invoke(cli.app, ["standards", str(manifest), "--profile", "cli-tool"])
    assert result.exit_code == 0
    assert "applies 0 domain(s)" in result.stdout


def test_standards_no_profile_anywhere_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / cli._MANIFEST_NAME).write_text(
        "name: no-profile-repo\ntype: python-fastapi\nmodules: []\n", encoding="utf-8"
    )

    class _Resolver:
        @classmethod
        def from_files(cls, *_):  # noqa: ANN206
            return cls()

    monkeypatch.setattr(cli, "StandardsProfileResolver", _Resolver)
    result = runner.invoke(cli.app, ["standards", str(tmp_path)])
    assert result.exit_code != 0


def test_standards_profile_error_becomes_bad_parameter(manifest: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resolver:
        @classmethod
        def from_files(cls, *_):  # noqa: ANN206
            return cls()

        def applicable_domains(self, name):  # noqa: ANN001
            raise ProfileError("unknown profile")

    monkeypatch.setattr(cli, "StandardsProfileResolver", _Resolver)
    result = runner.invoke(cli.app, ["standards", str(manifest)])
    assert result.exit_code != 0


def test_manifest_profile_missing_file_returns_empty(tmp_path: Path) -> None:
    assert cli._manifest_profile(tmp_path) == ""

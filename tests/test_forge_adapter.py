"""Tests for the FastAPI forge adapter — wiring only, the forge itself is mocked."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_init.forge_adapter import ForgeAdapter, ForgeError
from project_init.manifest import ModuleDecl, ProjectManifest

_STRUCTURES = Path("templates/fastapi/structures.yaml")


def _manifest() -> ProjectManifest:
    return ProjectManifest(
        name="my-service",
        type="python-fastapi",
        base_path="app/api",
        modules=[
            ModuleDecl(name="user", structure="fastapi_module_with_migration"),
            ModuleDecl(name="product"),
        ],
    )


def test_build_forge_document_when_manifest_has_modules_should_merge_them() -> None:
    adapter = ForgeAdapter(_STRUCTURES)

    document = adapter.build_forge_document(_manifest())

    assert document["base_path"] == "app/api"
    assert document["modules"] == [
        {"name": "user", "structure": "fastapi_module_with_migration"},
        {"name": "product", "structure": "fastapi_module"},
    ]
    # Canonical structures/templates are carried through untouched from the owned file.
    assert "fastapi_module_secure" in document["structures"]
    assert "router_py" in document["templates"]


def test_generate_when_forge_succeeds_should_invoke_cli_with_config_and_root(
    tmp_path: Path, mocker
) -> None:
    run = mocker.patch(
        "project_init.forge_adapter.subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
    )
    adapter = ForgeAdapter(_STRUCTURES, generator="fastapi-app-generator")

    adapter.generate(_manifest(), tmp_path)

    command = run.call_args.args[0]
    assert command[0] == "fastapi-app-generator"
    assert "--config" in command and "--root" in command
    assert (tmp_path / ".forge-config.yaml").exists()


def test_generate_when_dry_run_should_pass_dry_run_flag(tmp_path: Path, mocker) -> None:
    run = mocker.patch(
        "project_init.forge_adapter.subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
    )
    adapter = ForgeAdapter(_STRUCTURES)

    adapter.generate(_manifest(), tmp_path, dry_run=True)

    assert "--dry-run" in run.call_args.args[0]


def test_generate_when_forge_exits_nonzero_should_raise_forge_error(
    tmp_path: Path, mocker
) -> None:
    mocker.patch(
        "project_init.forge_adapter.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="boom"
        ),
    )
    adapter = ForgeAdapter(_STRUCTURES)

    with pytest.raises(ForgeError, match="boom"):
        adapter.generate(_manifest(), tmp_path)


def test_generate_when_forge_missing_should_raise_forge_error(
    tmp_path: Path, mocker
) -> None:
    mocker.patch(
        "project_init.forge_adapter.subprocess.run",
        side_effect=FileNotFoundError,
    )
    adapter = ForgeAdapter(_STRUCTURES, generator="missing-binary")

    with pytest.raises(ForgeError, match="not found"):
        adapter.generate(_manifest(), tmp_path)

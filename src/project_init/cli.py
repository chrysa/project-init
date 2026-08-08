"""`project-init` command surface (typer).

Thin entry point: parse args, load the manifest, delegate to the adapters. No
business logic lives here. See docs/adr/ADR-001-architecture.md §1.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml

from .forge_adapter import ForgeAdapter
from .manifest import ProjectManifest

_MANIFEST_NAME = ".project-init.yaml"
_STRUCTURES = Path(__file__).resolve().parent.parent.parent / "templates" / "fastapi" / "structures.yaml"

app = typer.Typer(help="Scaffold and update chrysa repositories from shared tools.")


def _load_manifest(path: Path) -> ProjectManifest:
    data = yaml.safe_load(path.read_text())
    return ProjectManifest.model_validate(data)


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Target repository directory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing."),
) -> None:
    """Scaffold a project's FastAPI modules by delegating to the forge."""
    manifest = _load_manifest(path / _MANIFEST_NAME)
    ForgeAdapter(_STRUCTURES).generate(manifest, path, dry_run=dry_run)
    typer.echo(f"Generated {len(manifest.modules)} module(s) under {path}")


@app.command(name="list-types")
def list_types() -> None:
    """Print the supported project types."""
    typer.echo("python-fastapi (modules via fastapi-app-generator)")

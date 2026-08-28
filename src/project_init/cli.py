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
from .standards_profile_resolver import ProfileError, StandardsProfileResolver

_MANIFEST_NAME = ".project-init.yaml"
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_STRUCTURES = _REPO_ROOT / "templates" / "fastapi" / "structures.yaml"
_PROFILES = _REPO_ROOT / "profiles" / "standards-profiles.yaml"
_DOMAINS = _REPO_ROOT / "profiles" / "domains.yaml"

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


@app.command()
def standards(
    path: Path = typer.Argument(Path("."), help="Target repository directory."),
    profile: str = typer.Option(
        "", "--profile", help="Resolve this profile instead of the manifest's."
    ),
) -> None:
    """Print the STD-* domains that apply to a repo's standards profile.

    Resolves the profile named on the command line, or the ``standards_profile``
    recorded in the repo's manifest. Selection only — the rules themselves stay
    in shared-standards (GV-000/GV-001).
    """
    resolver = StandardsProfileResolver.from_files(_PROFILES, _DOMAINS)
    name = profile or _manifest_profile(path)
    if not name:
        raise typer.BadParameter(
            "No profile given and none recorded in the manifest — pass --profile."
        )
    try:
        domains = resolver.applicable_domains(name)
    except ProfileError as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(f"Profile {name!r} applies {len(domains)} domain(s):")
    for domain in domains:
        typer.echo(f"  {domain.domain_id:<20} {domain.home} ({domain.prefix})")


def _manifest_profile(path: Path) -> str:
    manifest_path = path / _MANIFEST_NAME
    if not manifest_path.exists():
        return ""
    return _load_manifest(manifest_path).standards_profile or ""

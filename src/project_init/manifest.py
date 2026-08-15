"""The `.project-init.yaml` manifest — the canonical record of what a repo opted into.

Holds :class:`ProjectManifest` and its own value object :class:`ModuleDecl`. See
docs/adr/ADR-001-architecture.md §2 for the manifest contract.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

_DEFAULT_STRUCTURE = "fastapi_module"


class ModuleDecl(BaseModel):
    """One FastAPI module a project wants generated.

    Maps directly onto a forge ``modules[]`` entry: a ``name`` and the named
    ``structure`` (defined in ``templates/fastapi/structures.yaml``) to render it
    from.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    structure: str = _DEFAULT_STRUCTURE


class ProjectManifest(BaseModel):
    """A parsed `.project-init.yaml`.

    Only the fields the FastAPI slice needs today are modelled; the manifest
    grows as more types and extras are wired.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    type: str
    python_version: str = "3.14"
    base_path: str = "app/api"
    modules: list[ModuleDecl] = Field(default_factory=list)
    standards_profile: str | None = Field(
        default=None,
        description=(
            "The inheritable standards profile this repo adopts (see "
            "profiles/standards-profiles.yaml). Selects which STD-* domains apply; "
            "resolved by StandardsProfileResolver, never a copy of rule text."
        ),
    )

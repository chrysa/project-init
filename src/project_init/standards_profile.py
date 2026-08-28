"""One inheritable standards profile as declared in YAML.

Holds :class:`StandardsProfile`, the value object parsed from a ``profiles:``
entry in ``profiles/standards-profiles.yaml``. A profile *selects* domains and
composes with others through :attr:`extends`; it does not resolve the
inheritance chain itself — that is the resolver's job.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StandardsProfile(BaseModel):
    """A named profile keyed on stack / runtime tier / deployment target."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    abstract: bool = False
    extends: tuple[str, ...] = ()
    stack: str | None = None
    runtime: str | None = None
    deploy: str | None = None
    domains: tuple[str, ...] = ()

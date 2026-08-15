"""A single `STD-*` governance domain — a pointer into shared-standards.

Holds :class:`StandardsDomain`, the value object parsed from
``profiles/domains.yaml``. It carries only the domain id, its home annexe and
its rule prefix (the GV-015 correspondence); the rule bodies live in the socle
and are never reproduced here (GV-000/GV-001).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StandardsDomain(BaseModel):
    """One `STD-<DOMAIN>-nnn` domain and where its rules are implemented."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    domain_id: str = Field(min_length=1)
    home: str = Field(min_length=1)
    prefix: str = Field(min_length=1)
    summary: str = ""

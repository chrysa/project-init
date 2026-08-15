"""Resolve an inheritable standards profile to its applicable `STD-*` domains.

Holds :class:`StandardsProfileResolver` and its own error type
:class:`ProfileError`. The resolver loads the profile definitions
(``profiles/standards-profiles.yaml``) and the domain registry
(``profiles/domains.yaml``), then walks a profile's ``extends`` chain to produce
the deterministic union of domains that govern a repo — selecting, never copying
the rule text (GV-000/GV-001).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .standards_domain import StandardsDomain
from .standards_profile import StandardsProfile


class ProfileError(RuntimeError):
    """Raised on an unknown profile/domain, a cycle, or an abstract selection."""


class StandardsProfileResolver:
    """Load profile + domain data and resolve applicable domains for a profile."""

    def __init__(
        self,
        profiles: dict[str, StandardsProfile],
        domains: dict[str, StandardsDomain],
    ) -> None:
        self._profiles = profiles
        self._domains = domains

    @classmethod
    def from_files(cls, profiles_path: Path, domains_path: Path) -> "StandardsProfileResolver":
        """Build a resolver from the two canonical YAML files."""
        profiles = cls._load_profiles(profiles_path)
        domains = cls._load_domains(domains_path)
        return cls(profiles, domains)

    def applicable_domains(self, profile_name: str) -> list[StandardsDomain]:
        """Return the sorted, deduplicated domains that govern ``profile_name``.

        Walks the ``extends`` chain (depth-first, cycle-guarded) and unions each
        profile's own ``domains``. Raises :class:`ProfileError` if the profile is
        abstract, unknown, cyclic, or names a domain absent from the registry.
        """
        profile = self._require_profile(profile_name)
        if profile.abstract:
            raise ProfileError(
                f"Profile {profile_name!r} is abstract and cannot be selected directly"
            )
        domain_ids = self._collect_domain_ids(profile_name, seen=set())
        return [self._require_domain(domain_id) for domain_id in sorted(domain_ids)]

    def profile(self, profile_name: str) -> StandardsProfile:
        """Return the parsed profile, or raise :class:`ProfileError` if unknown."""
        return self._require_profile(profile_name)

    def selectable_profiles(self) -> list[str]:
        """Return the sorted names of every non-abstract (selectable) profile."""
        return sorted(name for name, profile in self._profiles.items() if not profile.abstract)

    @staticmethod
    def _load_domains(path: Path) -> dict[str, StandardsDomain]:
        raw = StandardsProfileResolver._load_mapping(path, "domains")
        return {
            domain_id: StandardsDomain(domain_id=domain_id, **entry)
            for domain_id, entry in raw.items()
        }

    @staticmethod
    def _load_mapping(path: Path, key: str) -> dict[str, Any]:
        document = yaml.safe_load(path.read_text())
        if not isinstance(document, dict):
            raise ProfileError(f"{path} must be a YAML mapping, got {type(document).__name__}")
        section = document.get(key)
        if not isinstance(section, dict):
            raise ProfileError(f"{path} must carry a {key!r} mapping")
        return section

    @staticmethod
    def _load_profiles(path: Path) -> dict[str, StandardsProfile]:
        raw = StandardsProfileResolver._load_mapping(path, "profiles")
        return {
            name: StandardsProfile(name=name, **entry) for name, entry in raw.items()
        }

    def _collect_domain_ids(self, profile_name: str, seen: set[str]) -> set[str]:
        if profile_name in seen:
            raise ProfileError(f"Cyclic profile inheritance through {profile_name!r}")
        seen.add(profile_name)
        profile = self._require_profile(profile_name)
        collected = set(profile.domains)
        for parent in profile.extends:
            collected |= self._collect_domain_ids(parent, seen)
        return collected

    def _require_domain(self, domain_id: str) -> StandardsDomain:
        domain = self._domains.get(domain_id)
        if domain is None:
            raise ProfileError(f"Unknown domain {domain_id!r} — not in the domain registry")
        return domain

    def _require_profile(self, profile_name: str) -> StandardsProfile:
        profile = self._profiles.get(profile_name)
        if profile is None:
            raise ProfileError(f"Unknown standards profile {profile_name!r}")
        return profile

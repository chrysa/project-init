"""Tests for the standards profile resolver against the canonical YAML data."""

from __future__ import annotations

from pathlib import Path

import pytest

from project_init.standards_domain import StandardsDomain
from project_init.standards_profile import StandardsProfile
from project_init.standards_profile_resolver import ProfileError, StandardsProfileResolver

_PROFILES = Path("profiles/standards-profiles.yaml")
_DOMAINS = Path("profiles/domains.yaml")


def _resolver() -> StandardsProfileResolver:
    return StandardsProfileResolver.from_files(_PROFILES, _DOMAINS)


def _domain_ids(resolver: StandardsProfileResolver, profile: str) -> set[str]:
    return {domain.domain_id for domain in resolver.applicable_domains(profile)}


def test_application_profile_inherits_base_and_python_backend_domains() -> None:
    ids = _domain_ids(_resolver(), "application")

    # base + python-backend + application-specific, unioned across the chain.
    assert {"STD-GOV-001", "STD-CONFIG-001"} <= ids  # from base
    assert {"STD-API-001", "STD-DATA-001", "STD-OPS-001"} <= ids  # from python-backend
    assert {"STD-DEPLOY-001", "STD-PERF-001", "STD-PRIVACY-001"} <= ids  # own


def test_library_profile_selects_publish_domains_but_not_frontend_state() -> None:
    ids = _domain_ids(_resolver(), "library")

    assert {"STD-GOV-001", "STD-TEST-001", "STD-API-001", "STD-DEPLOY-001"} <= ids
    assert "STD-UX-STATE-001" not in ids
    assert "STD-DATA-001" not in ids


def test_frontend_profile_selects_ux_state_domain() -> None:
    ids = _domain_ids(_resolver(), "frontend")

    assert "STD-UX-STATE-001" in ids


def test_config_only_profile_resolves_to_base_domains_only() -> None:
    ids = _domain_ids(_resolver(), "config-only")

    assert ids == {"STD-GOV-001", "STD-CONFIG-001"}


def test_applicable_domains_are_sorted_and_deduplicated() -> None:
    domains = _resolver().applicable_domains("application")

    ids = [domain.domain_id for domain in domains]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_resolved_domain_carries_home_and_prefix_pointer() -> None:
    domains = _resolver().applicable_domains("frontend")

    ux_state = next(d for d in domains if d.domain_id == "STD-UX-STATE-001")
    # home is the FRONTEND.md annexe; the value is generated from the canonical
    # shared-standards registry (full annexe path), so match on the annexe name.
    assert ux_state.home.endswith("FRONTEND.md")
    assert ux_state.prefix == "FE-"


def test_selectable_profiles_excludes_abstract_base() -> None:
    names = _resolver().selectable_profiles()

    assert "base" not in names
    assert {"application", "library", "frontend", "config-only"} <= set(names)


def test_selecting_abstract_base_directly_raises() -> None:
    with pytest.raises(ProfileError, match="abstract"):
        _resolver().applicable_domains("base")


def test_unknown_profile_raises() -> None:
    with pytest.raises(ProfileError, match="Unknown standards profile"):
        _resolver().applicable_domains("does-not-exist")


def test_cyclic_inheritance_is_detected() -> None:
    profiles = {
        "a": StandardsProfile(name="a", extends=("b",)),
        "b": StandardsProfile(name="b", extends=("a",)),
    }
    resolver = StandardsProfileResolver(profiles, {})

    with pytest.raises(ProfileError, match="Cyclic"):
        resolver.applicable_domains("a")


def test_domain_absent_from_registry_raises() -> None:
    profiles = {"solo": StandardsProfile(name="solo", domains=("STD-GHOST-999",))}
    resolver = StandardsProfileResolver(profiles, {})

    with pytest.raises(ProfileError, match="Unknown domain"):
        resolver.applicable_domains("solo")


def test_every_domain_referenced_by_a_profile_exists_in_the_registry() -> None:
    resolver = _resolver()

    for name in resolver.selectable_profiles():
        resolver.applicable_domains(name)  # raises if any domain id is unknown


def test_from_files_rejects_a_non_mapping_document(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- just\n- a\n- list\n")

    with pytest.raises(ProfileError, match="mapping"):
        StandardsProfileResolver.from_files(bad, _DOMAINS)


def test_domain_registry_entries_are_parsed_as_value_objects() -> None:
    domains = _resolver().applicable_domains("config-only")

    assert all(isinstance(domain, StandardsDomain) for domain in domains)

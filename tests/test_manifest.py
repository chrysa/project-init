"""Tests for the ProjectManifest — the standards_profile field wiring."""

from __future__ import annotations

from project_init.manifest import ProjectManifest


def test_manifest_defaults_standards_profile_to_none() -> None:
    manifest = ProjectManifest(name="svc", type="python-fastapi")

    assert manifest.standards_profile is None


def test_manifest_records_the_standards_profile_when_given() -> None:
    manifest = ProjectManifest(
        name="svc", type="python-fastapi", standards_profile="application"
    )

    assert manifest.standards_profile == "application"

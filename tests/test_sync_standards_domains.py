"""Tests for the domains-registry generator (scripts/sync_standards_domains.py).

The generator turns the canonical shared-standards registry (a ``domains:`` list)
into the local pointer mapping the resolver reads, and offers a ``--check`` drift
mode. Tests drive it against temporary source files — never the real
shared-standards checkout — so they are hermetic.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import sync_standards_domains as sync
from sync_standards_domains import DomainsRegistryError, DomainsRegistrySync, main

_CANONICAL = """\
version: 1
domains:
  - id: STD-GOV-001
    home: standards/annexes/GOVERNANCE.md
    prefix: GV-
    status: Adopted
    priority: P0
    title: Standards governance & lifecycle
  - id: STD-TEST-001
    home: standards/annexes/TESTING.md
    prefix: TS-
    status: Adopted
    priority: P1
    title: Risk-based testing
"""


def _write_source(tmp_path: Path, text: str = _CANONICAL) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "source.yaml"
    source.write_text(text, encoding="utf-8")
    return source


def _syncer(tmp_path: Path, text: str = _CANONICAL) -> tuple[DomainsRegistrySync, Path]:
    source = _write_source(tmp_path, text)
    target = tmp_path / "out" / "domains.yaml"
    target.parent.mkdir()
    return DomainsRegistrySync(str(source), target), target


def test_render_projects_id_keyed_mapping_with_title_as_summary(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path)

    document = yaml.safe_load(syncer.render())

    assert document["version"] == 1
    assert set(document["domains"]) == {"STD-GOV-001", "STD-TEST-001"}
    gov = document["domains"]["STD-GOV-001"]
    # Only the keys StandardsDomain accepts — status/priority are dropped.
    assert gov == {
        "home": "standards/annexes/GOVERNANCE.md",
        "prefix": "GV-",
        "summary": "Standards governance & lifecycle",
    }


def test_render_carries_the_generated_header(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path)

    assert syncer.render().startswith("# GENERATED from chrysa/shared-standards")


def test_write_creates_a_file_the_check_then_accepts(tmp_path: Path) -> None:
    syncer, target = _syncer(tmp_path)

    written = syncer.write()

    assert written == target
    assert target.exists()
    assert syncer.check() is True


def test_check_is_false_when_target_missing(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path)

    assert syncer.check() is False


def test_check_detects_a_hand_edit_drift(tmp_path: Path) -> None:
    syncer, target = _syncer(tmp_path)
    syncer.write()

    target.write_text(target.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")

    assert syncer.check() is False


def test_check_detects_a_moved_source(tmp_path: Path) -> None:
    syncer, target = _syncer(tmp_path)
    syncer.write()
    moved = _CANONICAL.replace("GV-", "GX-")

    drifted = DomainsRegistrySync(str(_write_source(tmp_path / "moved", moved)), target)

    assert drifted.check() is False


def test_summary_falls_back_when_neither_title_nor_summary_present(tmp_path: Path) -> None:
    text = "version: 1\ndomains:\n  - id: STD-X-001\n    home: socle\n    prefix: X-\n"
    syncer, _ = _syncer(tmp_path, text)

    document = yaml.safe_load(syncer.render())

    assert document["domains"]["STD-X-001"] == {"home": "socle", "prefix": "X-"}


def test_explicit_summary_key_wins(tmp_path: Path) -> None:
    text = (
        "version: 1\ndomains:\n  - id: STD-X-001\n    home: socle\n"
        "    prefix: X-\n    summary: explicit\n    title: ignored\n"
    )
    syncer, _ = _syncer(tmp_path, text)

    assert yaml.safe_load(syncer.render())["domains"]["STD-X-001"]["summary"] == "explicit"


def test_http_source_is_fetched(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class _Response:
        def read(self) -> bytes:
            return _CANONICAL.encode("utf-8")

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, *_: object) -> None:
            return None

    monkeypatch.setattr(sync.urllib.request, "urlopen", lambda _url: _Response())
    syncer = DomainsRegistrySync("https://example.test/domains.yaml", tmp_path / "out.yaml")

    assert set(yaml.safe_load(syncer.render())["domains"]) == {"STD-GOV-001", "STD-TEST-001"}


def test_missing_source_file_raises(tmp_path: Path) -> None:
    syncer = DomainsRegistrySync(str(tmp_path / "absent.yaml"), tmp_path / "out.yaml")

    with pytest.raises(DomainsRegistryError, match="not found"):
        syncer.render()


def test_non_mapping_document_raises(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path, "- just\n- a\n- list\n")

    with pytest.raises(DomainsRegistryError, match="must be a YAML mapping"):
        syncer.render()


def test_domains_not_a_list_raises(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path, "version: 1\ndomains: {}\n")

    with pytest.raises(DomainsRegistryError, match="expected a 'domains' list"):
        syncer.render()


def test_entry_missing_id_raises(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path, "version: 1\ndomains:\n  - home: socle\n    prefix: X-\n")

    with pytest.raises(DomainsRegistryError, match="missing 'id'"):
        syncer.render()


def test_entry_missing_home_or_prefix_raises(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path, "version: 1\ndomains:\n  - id: STD-X-001\n    home: socle\n")

    with pytest.raises(DomainsRegistryError, match="missing 'home' or 'prefix'"):
        syncer.render()


def test_entry_not_a_mapping_raises(tmp_path: Path) -> None:
    syncer, _ = _syncer(tmp_path, "version: 1\ndomains:\n  - just-a-string\n")

    with pytest.raises(DomainsRegistryError, match="must be a mapping"):
        syncer.render()


def test_from_env_prefers_explicit_source_then_env_then_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHARED_STANDARDS_DOMAINS", "/from/env.yaml")
    assert DomainsRegistrySync.from_env("/explicit.yaml")._source == "/explicit.yaml"
    assert DomainsRegistrySync.from_env()._source == "/from/env.yaml"
    monkeypatch.delenv("SHARED_STANDARDS_DOMAINS")
    assert DomainsRegistrySync.from_env()._source == str(sync._DEFAULT_SOURCE)


def test_main_generate_writes_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _write_source(tmp_path)
    target = tmp_path / "profiles" / "domains.yaml"
    target.parent.mkdir()
    monkeypatch.setattr(sync, "_TARGET", target)

    assert main(["--source", str(source)]) == 0
    assert target.exists()


def test_main_check_returns_zero_on_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _write_source(tmp_path)
    target = tmp_path / "domains.yaml"
    monkeypatch.setattr(sync, "_TARGET", target)
    DomainsRegistrySync(str(source), target).write()

    assert main(["--check", "--source", str(source)]) == 0


def test_main_check_returns_one_on_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _write_source(tmp_path)
    target = tmp_path / "domains.yaml"
    monkeypatch.setattr(sync, "_TARGET", target)

    assert main(["--check", "--source", str(source)]) == 1


def test_main_returns_two_on_registry_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync, "_TARGET", tmp_path / "domains.yaml")

    assert main(["--source", str(tmp_path / "absent.yaml")]) == 2

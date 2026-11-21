"""Tests for the canonical context-file generator (``scripts/gen_context_files.py``).

The generator is a distributed, drift-gated contract (ADR D-0012): it reads a repo's
own content and must degrade gracefully on every absent source, stay byte-stable, and
never leak a vendor name or a machine path. These tests build small throwaway repos
under ``tmp_path`` and assert the readers, the structural extractors, the file builders
and the drift gate against them.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import gen_context_files as gcf

_HAS_GIT = shutil.which("git") is not None


@pytest.fixture
def empty(tmp_path: Path) -> Path:
    """A guaranteed-empty repo dir, isolated from the ``repo`` fixture's tree."""
    target = tmp_path / "empty_repo"
    target.mkdir()
    return target


# ── fixtures ────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A minimal but realistic repo tree: pyproject, README, CLAUDE.md, an ADR, a module."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\n'
        'name = "demo-repo"\n'
        'version = "1.2.3"\n'
        'description = "A demo repository."\n'
        'requires-python = ">=3.13"\n'
        'license = "MIT"\n'
        'dependencies = ["pydantic>=2", "pyyaml"]\n'
        '[project.optional-dependencies]\n'
        'test = ["pytest>=8"]\n'
        '[project.scripts]\n'
        'demo = "demo.cli:app"\n'
        '[tool.chrysa]\n'
        'ddd = "L2"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Demo Repo\n\nThe canonical demo.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(
        "# Agent view\n<!-- chrysa:standards:start -->\nrules\n", encoding="utf-8"
    )
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## v1.2.3\n\n- first\n- second\n\n## v1.0.0\n\n- old\n", encoding="utf-8"
    )
    adr = tmp_path / "docs" / "adr"
    adr.mkdir(parents=True)
    (adr / "ADR-001-architecture.md").write_text(
        "# ADR-001 Architecture\n\n- **Status:** Accepted\n", encoding="utf-8"
    )
    pkg = tmp_path / "src" / "demo"
    pkg.mkdir(parents=True)
    (pkg / "cli.py").write_text('"""The demo CLI entry point."""\n\napp = None\n', encoding="utf-8")
    standards = tmp_path / "standards" / "rules"
    standards.mkdir(parents=True)
    (standards / "GV-000.md").write_text(
        "See https://www.notion.so/demo-abc123 for details.\n", encoding="utf-8"
    )
    return tmp_path


# ── source readers ────────────────────────────────────────────────────────────────────


def test_read_text_absent_returns_none(tmp_path: Path) -> None:
    assert gcf._read_text(tmp_path / "nope.txt") is None


def test_read_text_present(tmp_path: Path) -> None:
    target = tmp_path / "f.txt"
    target.write_text("hi", encoding="utf-8")
    assert gcf._read_text(target) == "hi"


def test_load_pyproject_absent_is_empty(tmp_path: Path) -> None:
    assert gcf._load_pyproject(tmp_path) == {}


def test_load_pyproject_invalid_is_empty(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("not = = toml", encoding="utf-8")
    assert gcf._load_pyproject(tmp_path) == {}


def test_load_pyproject_parsed(repo: Path) -> None:
    assert gcf._load_pyproject(repo)["project"]["name"] == "demo-repo"


def test_load_package_json_absent(tmp_path: Path) -> None:
    assert gcf._load_package_json(tmp_path) == {}


def test_load_package_json_invalid(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{bad", encoding="utf-8")
    assert gcf._load_package_json(tmp_path) == {}


def test_load_package_json_non_object(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("[1, 2]", encoding="utf-8")
    assert gcf._load_package_json(tmp_path) == {}


def test_load_package_json_parsed(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x"}', encoding="utf-8")
    assert gcf._load_package_json(tmp_path) == {"name": "x"}


def test_first_h1_none_on_empty() -> None:
    assert gcf._first_h1(None) is None
    assert gcf._first_h1("no heading here") is None


def test_first_h1_found() -> None:
    assert gcf._first_h1("intro\n# Title\nbody") == "Title"


def test_first_paragraph_skips_markup() -> None:
    assert gcf._first_paragraph("# h\n> quote\n- item\n\nReal prose.") == "Real prose."


def test_first_paragraph_none() -> None:
    assert gcf._first_paragraph(None) is None
    assert gcf._first_paragraph("# only heading") is None


# ── metadata derivation ─────────────────────────────────────────────────────────────────


def test_repo_name_from_pyproject(repo: Path) -> None:
    assert gcf.repo_name(repo, gcf._load_pyproject(repo), {}) == "demo-repo"


def test_repo_name_falls_back_to_readme_then_dirname(tmp_path: Path) -> None:
    assert gcf.repo_name(tmp_path, {}, {}) == tmp_path.name
    (tmp_path / "README.md").write_text("# From Readme\n", encoding="utf-8")
    assert gcf.repo_name(tmp_path, {}, {}) == "From Readme"


def test_repo_description_priority_and_na(repo: Path, empty: Path) -> None:
    assert gcf.repo_description(repo, gcf._load_pyproject(repo), {}) == "A demo repository."
    assert gcf.repo_description(empty, {}, {}) == gcf.NA


def test_ddd_level(repo: Path, empty: Path) -> None:
    assert gcf.ddd_level(repo, gcf._load_pyproject(repo)) == "L2"
    assert gcf.ddd_level(empty, {}) == gcf.NA


def test_depends_on_shared_standards(repo: Path, empty: Path) -> None:
    assert gcf.depends_on_shared_standards(repo) is True
    assert gcf.depends_on_shared_standards(empty) is False


def test_profiles_for_reads_repos_yml(tmp_path: Path) -> None:
    (tmp_path / "repos.yml").write_text(
        "profiles:\n  core: [demo-repo, other]\n  extra: [demo-repo]\n", encoding="utf-8"
    )
    assert gcf.profiles_for(tmp_path, "demo-repo") == ["core", "extra"]
    assert gcf.profiles_for(tmp_path, "absent") == []


def test_profiles_for_no_file(tmp_path: Path) -> None:
    assert gcf.profiles_for(tmp_path, "x") == []


def test_list_adrs(repo: Path, empty: Path) -> None:
    adrs = gcf.list_adrs(repo)
    assert adrs == [{"file": "ADR-001-architecture.md", "title": "ADR-001 Architecture", "status": "Accepted"}]
    assert gcf.list_adrs(empty) == []


def test_adr_status_na_when_absent() -> None:
    assert gcf._adr_status("# no status field") == gcf.NA


def test_notion_links_dedup_sorted(repo: Path) -> None:
    assert gcf.notion_links(repo) == ["https://www.notion.so/demo-abc123"]


def test_latest_changelog_first_section(repo: Path, empty: Path) -> None:
    out = gcf.latest_changelog(repo)
    assert out.startswith("## v1.2.3")
    assert "- first" in out and "v1.0.0" not in out
    assert gcf.latest_changelog(empty) == gcf.NA


def test_latest_changelog_no_section(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("no sections here\n", encoding="utf-8")
    assert gcf.latest_changelog(tmp_path) == gcf.NA


# ── structural extractors ───────────────────────────────────────────────────────────────


def test_repo_files_filesystem_fallback_filters_volatile(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    cache = tmp_path / ".mypy_cache"
    cache.mkdir()
    (cache / "junk.json").write_text("{}", encoding="utf-8")
    vendored = tmp_path / "node_modules"
    vendored.mkdir()
    (vendored / "dep.js").write_text("", encoding="utf-8")
    # No git here → filesystem walk.
    files = gcf._walk_files(tmp_path)
    assert "src/a.py" in files
    assert not any(".mypy_cache" in f or "node_modules" in f for f in files)


def test_tracked_files_none_without_git(tmp_path: Path) -> None:
    assert gcf._tracked_files(tmp_path) is None


@pytest.mark.skipif(not _HAS_GIT, reason="git not installed")
def test_tracked_files_with_git(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.email=t@t", "-c", "user.name=t", "add", "a.py"],
        check=True,
    )
    tracked = gcf._tracked_files(tmp_path)
    assert tracked == ["a.py"]


def test_key_dirs(tmp_path: Path) -> None:
    assert gcf.key_dirs(["src/a.py", "src/b.py", "docs/x.md", "top.py"]) == ["docs", "src"]


def test_entry_points(repo: Path) -> None:
    pts = gcf.entry_points(gcf._load_pyproject(repo), {"main": "index.js", "bin": {"tool": "t.js"}})
    assert "demo" in pts and "index.js" in pts and "tool" in pts


def test_entry_points_string_bin() -> None:
    assert gcf.entry_points({}, {"bin": "run.js"}) == ["run.js"]


def test_dep_name() -> None:
    assert gcf._dep_name("pydantic>=2.0; extra == 'x'") == "pydantic"
    assert gcf._dep_name("ruff[all]") == "ruff"


def test_dependencies_split(repo: Path) -> None:
    deps = gcf.dependencies(gcf._load_pyproject(repo), {"dependencies": {"left-pad": "1"}})
    assert deps["python"] == ["pydantic", "pytest", "pyyaml"]
    assert deps["node"] == ["left-pad"]


def test_contracts(repo: Path) -> None:
    assert "standards" in gcf.contracts(repo)


def test_dir_tree_depth(tmp_path: Path) -> None:
    tree = gcf.dir_tree(["a/b/c/d.py", "a/e.py"], depth=1)
    assert "a/" in tree and "  b/" in tree
    # depth 1: nothing below b/
    assert not any("c" in line for line in tree)


def test_module_docstring() -> None:
    assert gcf._module_docstring('"""Hello.\n\nmore"""\ncode') == "Hello."
    assert gcf._module_docstring("code only") == ""
    assert gcf._module_docstring(None) == ""


def test_module_headers(repo: Path) -> None:
    headers = gcf.module_headers(repo, ["src/demo/cli.py"])
    assert headers == ["src/demo/cli.py — The demo CLI entry point."]


def test_is_source_path(tmp_path: Path) -> None:
    good = tmp_path / "src" / "a.py"
    bad = tmp_path / ".venv" / "x.py"
    assert gcf._is_source_path(good, tmp_path) is True
    assert gcf._is_source_path(bad, tmp_path) is False


def test_license_str_variants() -> None:
    assert gcf._license_str("MIT") == "MIT"
    assert gcf._license_str({"text": "Apache"}) == "Apache"
    assert gcf._license_str({"file": "LICENSE"}) == "LICENSE"
    assert gcf._license_str({}) is None
    assert gcf._license_str(42) is None


# ── file builders ───────────────────────────────────────────────────────────────────────


def test_build_handover_contains_sections(repo: Path) -> None:
    out = gcf.build_handover(repo, gcf._load_pyproject(repo), {})
    assert "# Handover — demo-repo" in out
    assert "A demo repository." in out
    assert "ADR-001-architecture.md" in out
    assert "https://www.notion.so/demo-abc123" in out
    assert "GENERATED by" in out


def test_build_handover_degrades(tmp_path: Path) -> None:
    out = gcf.build_handover(tmp_path, {}, {})
    assert gcf.NA in out  # no adrs, no notion, no changelog


def test_build_context_map_is_sorted_json(repo: Path) -> None:
    files = gcf.repo_files(repo)
    out = gcf.build_context_map(repo, gcf._load_pyproject(repo), {}, files)
    data = json.loads(out)
    assert data["schema"] == "chrysa.context-map/1"
    assert data["name"] == "demo-repo"
    assert data["depends_on_shared_standards"] is True
    # stable key order
    assert list(data.keys()) == sorted(data.keys())


def test_build_llms_full(repo: Path) -> None:
    files = gcf.repo_files(repo)
    out = gcf.build_llms_full(repo, gcf._load_pyproject(repo), {}, files)
    assert "technical digest" in out
    assert "## Structure" in out
    assert "## Modules" in out
    assert "version: 1.2.3" in out


def test_build_ai_instructions_fr(repo: Path, empty: Path) -> None:
    out = gcf.build_ai_instructions(repo)
    assert "Instructions de travail" in out
    assert "`AGENTS.md`" in out and "`CLAUDE.md`" in out
    assert "standards/" in out
    # degrade: no agent views, no standards dir
    bare = gcf.build_ai_instructions(empty)
    assert "les vues d'agent du dépôt" in bare


def test_config_summary_na(tmp_path: Path) -> None:
    assert gcf._config_summary({}, {}) == [gcf.NA]


# ── orchestration + drift ───────────────────────────────────────────────────────────────


def test_generate_produces_all_files(repo: Path) -> None:
    out = gcf.generate(repo)
    assert set(out) == set(gcf.GENERATED_FILES)
    assert all(isinstance(v, str) and v for v in out.values())


def test_generate_is_deterministic(repo: Path) -> None:
    assert gcf.generate(repo) == gcf.generate(repo)


def test_write_all_and_no_drift(repo: Path) -> None:
    gcf.write_all(repo)
    for name in gcf.GENERATED_FILES:
        assert (repo / name).exists()
    assert gcf.drift(repo) == []


def test_drift_detects_missing_and_stale(repo: Path) -> None:
    gcf.write_all(repo)
    (repo / gcf.HANDOVER).unlink()
    (repo / gcf.CONTEXT_MAP).write_text("tampered", encoding="utf-8")
    lines = gcf.drift(repo)
    assert f"missing: {gcf.HANDOVER}" in lines
    assert f"stale: {gcf.CONTEXT_MAP}" in lines


def test_main_regenerates(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    monkeypatch.setattr(gcf, "_ROOT", repo)
    monkeypatch.setattr(gcf.sys, "argv", ["gen_context_files"])
    assert gcf.main() == 0
    assert (repo / gcf.HANDOVER).exists()


def test_main_check_passes_when_current(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    monkeypatch.setattr(gcf, "_ROOT", repo)
    gcf.write_all(repo)
    monkeypatch.setattr(gcf.sys, "argv", ["gen_context_files", "--check"])
    assert gcf.main() == 0


def test_main_check_fails_on_drift(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    monkeypatch.setattr(gcf, "_ROOT", repo)
    gcf.write_all(repo)
    (repo / gcf.HANDOVER).unlink()
    monkeypatch.setattr(gcf.sys, "argv", ["gen_context_files", "--check"])
    assert gcf.main() == 1

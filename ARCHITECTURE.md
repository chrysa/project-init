# Architecture — project-init

## Purpose

`project-init` is the chrysa ecosystem's project bootstrap and initializer. Per the
transverse standards (`architecture.md`: "Repo provenance — every code repo depends on
`project-init`"), it is the **canonical repo every code repo depends on**: it rationalizes
project creation, enforces shared standards from day one, and automates the repetitive
setup every new repository needs (CI/CD, pre-commit, Makefile, Docker, Claude/Copilot
config, Notion bootstrap, versioning).

Its design principle is **orchestration by delegation**: `project-init` owns *what* a
chrysa repo should look like (structure data, profile-to-domain selection) and delegates
the actual rendering to shared engines (e.g. `fastapi-app-generator`), never re-implementing
them (see `docs/adr/ADR-002-consume-shared-repos.md`).

Status: early phase. The CLI currently scaffolds FastAPI modules and resolves standards
profiles; the broader multi-type generation (Python service, React app, etc.) is planned.

## Stack

- Python `>=3.14` (packaging via `pyproject.toml`, setuptools build backend).
- Runtime deps: `typer` (CLI), `pydantic` v2 (manifest models), `pyyaml` (config/data).
- Test deps: `pytest`, `pytest-cov`, `pytest-mock`, plus `chrysa-quality-gate`
  (a git+ssh dependency from `chrysa/chrysa-lib`).
- Tooling: Ruff (lint/format), mypy (typecheck), pre-commit, cliff.toml (changelog),
  GitVersion, SonarQube. Tests run in Docker via `Dockerfile.test` (Python 3.14-slim).

## Layout

- `src/project_init/` — the package (orchestrator):
  - `cli.py` — Typer command surface, thin (parse + delegate, no business logic).
  - `manifest.py` — `ProjectManifest` / module declarations parsed from `.project-init.yaml`.
  - `forge_adapter.py` — `ForgeAdapter`, drives the FastAPI forge engine (owns no rendering).
  - `standards_domain.py`, `standards_profile.py`, `standards_profile_resolver.py` —
    resolve a repo's standards profile to the set of `STD-*` domains that apply.
- `scripts/` — helper scripts (e.g. quality-gate, standards-domain sync).
- `profiles/` — `standards-profiles.yaml`, `domains.yaml` (profile → domain data,
  synced from shared-standards).
- `templates/` — structure *data* for generated projects (e.g. `fastapi/structures.yaml`).
- `tests/` — pytest suites plus scenario catalogues (edge-cases, e2e, regression `.md`).
- `docs/`, `decisions/`, `postmortems/`, `schemas/`, `workflows/`, `ai/`, `prompts/`,
  `examples/` — standardized documentation structure (many files are `status: stub`).

## Entrypoints

- Console script `project-init` → `project_init.cli:app` (declared in `pyproject.toml`).
- CLI commands (from `cli.py`):
  - `init [PATH] [--dry-run]` — scaffold a project's FastAPI modules via the forge adapter.
  - `list-types` — print supported project types.
  - `standards [PATH] [--profile NAME]` — print the `STD-*` domains that apply to a
    repo's standards profile (selection only; rules stay in shared-standards).

Note: README and `src/project_init/README.md` describe the CLI as `init` / `list-types`
(and mention `update`); the actual `cli.py` exposes `init`, `list-types`, and `standards`.
Trust the source — `update` is not implemented.

## Data & external dependencies

- Input manifest: `.project-init.yaml` (parsed into `ProjectManifest`).
- Bundled data: `profiles/standards-profiles.yaml`, `profiles/domains.yaml`,
  `templates/fastapi/structures.yaml` (resolved relative to the repo root by `cli.py`).
- External repos consumed (per README / ADRs): `chrysa/shared-standards` (standards,
  templates, hooks), `fastapi-app-generator` / forge engines (rendering), plus
  `chrysa/chrysa-lib` quality-gate (test dependency via git+ssh).
- No network services or databases at runtime; it is a filesystem-oriented CLI.

## Build & test

Tests run in-container (host virtualenvs are forbidden by standard). Real commands:

- `make docker-test` — build `Dockerfile.test` and run pytest with coverage
  (`--cov-fail-under=80`, emits `coverage.xml`).
- `make test` — local unit tests (currently delegates to the container flow).
- `make lint` — Ruff via pre-commit.
- `make format` / `make format-check` — Ruff format.
- `make typecheck` — mypy (N/A — not yet wired; see issues).
- `make build` — N/A — no build artefact target yet.
- `make pre-commit` — run all pre-commit checks.
- `make ci` — full local gate (lint + pre-commit + docker-test).
- `make sync-standards-domains` / `make check-standards-domains` — regenerate / drift-check
  `profiles/domains.yaml` against shared-standards.

Coverage gate: 80% line coverage (`pyproject.toml`, `Dockerfile.test`).

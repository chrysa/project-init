# ARCHITECTURE — project-init

> Claim tags: **FACT** / **INFERENCE** / **UNKNOWN** / **PROPOSAL**. The
> normative design records are [docs/adr/ADR-001-architecture.md](docs/adr/ADR-001-architecture.md)
> and [docs/adr/ADR-002-consume-shared-repos.md](docs/adr/ADR-002-consume-shared-repos.md);
> where this file and an ADR disagree, the ADR wins.

## Stack (FACT)

- Language: **Python 3.14** (bytecode `cpython-314` present; `pyproject.toml`).
- CLI framework: **typer** (`src/project_init/cli.py`).
- Data modelling: **pydantic** value objects (`frozen`, `extra="forbid"`).
- Config parsing: **pyyaml**.
- Packaging: `pyproject.toml`, distribution name `chrysa-project-init`, console
  entry point `project-init = project_init.cli:app`.
- Dev/test deps provisioned in a container (`Dockerfile.test`), not on the host.

## Design principle (FACT — ADR-002)

Orchestrator, not generator. `project-init` owns *what* a chrysa module looks
like (the canonical structure) and the *manifest → tool-YAML → invoke* wiring;
the consumed tools own the file templates and generation logic.

## Components (FACT — src/project_init/)

| Module | Role |
|--------|------|
| `cli.py` | typer entry point. Parses args, loads the manifest, delegates. Commands: `init`, `list-types`, `standards`. No business logic. |
| `manifest.py` | `ProjectManifest` / `ModuleSpec` — parses `.project-init.yaml`; models only the fields the FastAPI slice needs today. |
| `forge_adapter.py` | `ForgeAdapter` / `ForgeError` — merges manifest modules into the canonical forge structures document and invokes the `fastapi-app-generator` CLI via `subprocess`. |
| `standards_profile.py` | `StandardsProfile` — one inheritable profile parsed from YAML; selects domains and composes via `extends`. |
| `standards_profile_resolver.py` | `StandardsProfileResolver` / `ProfileError` — walks the `extends` chain (depth-first, cycle-guarded) and returns the deterministic union of applicable `STD-*` domains. |
| `standards_domain.py` | `StandardsDomain` — a pointer to a domain's home annexe + rule prefix (GV-015 correspondence). Rule bodies are never reproduced (GV-000/GV-001). |

## Data / contracts (FACT)

- `.project-init.yaml` — the manifest; canonical record of what a repo opted into
  (ADR-001 §2). Carries `standards_profile`, `modules[]`, and (per ADR) the tool
  revisions a repo was built against.
- `profiles/standards-profiles.yaml` — inheritable profiles keyed on
  stack / runtime / deploy axes (GV-011); `base` is abstract.
- `profiles/domains.yaml` — the `STD-*` domain registry (generated from
  `shared-standards`; drift-checked in CI via `make check-standards-domains`).
- `templates/fastapi/structures.yaml` — the canonical FastAPI module structure
  the forge renders.
- `schemas/*.schema.json` — JSON Schema data-contract examples (user, project,
  payment). **INFERENCE:** reference material, not wired into the CLI.

## Control flow

**`standards` command (FACT):** resolve profile (from `--profile` or the
manifest's `standards_profile`) → `StandardsProfileResolver.resolve()` →
print applicable domains.

**`init` command (FACT, partial):** load manifest → `ForgeAdapter` merges
modules into the structures document → invoke `fastapi-app-generator` CLI →
report count. Full multi-concern scaffolding (`init`/`update` merge engine) is
**planned** (ADR-001 §1, §4).

## Delegation boundary (FACT — ADR-002)

The "fatal hypothesis" is that the published forge/CI/hook tools are stable and
complete enough to delegate to without post-patching their output. The
**kill-test** measures files `project-init` must overwrite after a tool runs to
reach `make ci` green; threshold is post-patch count > 0 on tool-owned files.
The **validation gate** proves the boundary on `python-fastapi` first, before a
general engine. Evidence lives in `tests/e2e-scenarios.md`.

## Integrations (FACT)

- MCP servers declared in `.mcp.json` / `opencode.json`: GitHub and Notion
  (via `@modelcontextprotocol/server-github`, `@notionhq/notion-mcp-server`),
  both reading credentials from the environment.
- Consumed ecosystem repos: `fastapi-app-generator`, `django-app-forge`,
  `base-makefile`, `chrysa/github-actions`, `chrysa/pre-commit-tools`,
  `chrysa-lib`, `chrysa/shared-standards` (ADR-002).

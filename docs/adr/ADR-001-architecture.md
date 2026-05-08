# ADR-001 — project-init Architecture

**Status**: Accepted
**Date**: 2026-04-26

---

## Context

Every new repository in the chrysa ecosystem requires the same baseline setup:
CI/CD pipeline, pre-commit hooks, Makefile, Dockerfile, Dependabot, SonarQube,
GitHub labels and templates, README, `.gitignore`, VS Code config, Copilot
instructions, and Claude Code config. This setup is currently done manually,
is inconsistent across repos, and drifts over time.

`project-init` exists to automate this baseline so that every new project starts
at the same quality level, and existing projects can be brought into conformance.

---

## Decision

### 1. Entry point: Python CLI with `typer`

```
project-init init [OPTIONS] [PATH]
project-init update [OPTIONS] [PATH]
project-init list-types
```

- `init`: scaffold a new project from scratch (or into an empty directory)
- `update`: apply missing pieces to an existing repository (non-destructive)
- `list-types`: print supported project types and their status

Distributed as a Python package installable via `pip install chrysa-project-init`
or via the `chrysa-bootstrap.sh` script. Also callable as `make init` from the
base-makefile.

### 2. Config format: YAML manifest

Projects declare what they need in a `.project-init.yaml` file at the repo root:

```yaml
name: my-service
type: python-fastapi      # see supported types below
python_version: "3.12"
extras:
  - notion                # optional modules
  - docker
github:
  org: chrysa
  repo: my-service
sonar:
  enabled: true
  project_key: chrysa_my-service
```

If `.project-init.yaml` is absent, `init` runs in interactive mode (prompts for
each required value) and writes the manifest as a side effect.

### 3. Supported project types

| Type | Key | Status |
|------|-----|--------|
| FastAPI Python service | `python-fastapi` | Planned |
| React 19 SPA | `react19` | Planned |
| Python CLI / tool | `python-cli` | Planned |
| Python library | `python-library` | Planned |
| Google Apps Script | `gas` | Planned |
| Monorepo (pnpm + turborepo) | `monorepo` | Planned |
| Generic / other | `generic` | Planned |

Each type maps to a template bundle in `project_init/templates/<type>/`.

### 4. Output model: merge, not overwrite

`init` and `update` use a **merge strategy**:

- Files that don't exist in the target → created from template
- Files that exist but are tracked by project-init → updated if template changed
- Files with local modifications → conflict reported, never silently overwritten
- Files opted out in `.project-init.yaml` under `skip:` → left untouched

`update` is designed to be safe to re-run at any time. It is idempotent.

### 5. Extensibility: template bundles + hooks

Two extension points:

**Template bundles** (`project_init/templates/<type>/`):
- Directory tree rendered via Jinja2 with the manifest as context
- Each bundle declares required manifest keys in a `bundle.yaml`
- Bundles are additive: `python-fastapi` = `generic` + `python` + `fastapi`

**Lifecycle hooks** (`project_init/hooks/`):
- Python callables called at defined phases: `pre_init`, `post_init`, `pre_update`, `post_update`
- Registered in `pyproject.toml` under `[project.entry-points."project_init.hooks"]`
- Used for: GitHub label sync, Notion project creation, SonarQube project registration

### 6. Integration with shared-standards

`project-init` does not vendor `shared-standards` files directly.
Instead, it writes references that **pull from shared-standards at runtime**:

- `.pre-commit-config.yaml` points to `chrysa/pre-commit-tools` at a pinned rev
- `.github/copilot-instructions.md` imports `chrysa/shared-standards/copilot-instructions/<type>.md`
  via a comment directive that VS Code Copilot resolves
- `.claude/settings.json` references shared Claude hooks via the vendoring mechanism
  already in `chrysa/shared-standards`

The bootstrap command (`project-init update`) also pins all tool revisions to the
latest verified versions from `shared-standards`.

---

## Consequences

- `project-init` is a Python package, runnable standalone and from `chrysa-bootstrap.sh`
- Each new project type requires a template bundle + a copilot-instructions file in `shared-standards`
- `update` being idempotent allows it to be called from CI to detect drift
- Notion bootstrap (#9) and GitHub bootstrap (#6) are separate optional modules (`extras`)
- The YAML manifest becomes the canonical record of what a repo opted into

---

## Supported project type matrix

| Type | CI | pre-commit | Makefile | Docker | Copilot | SonarQube | Notion |
|------|----|-----------|----------|--------|---------|-----------|--------|
| `python-fastapi` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | opt |
| `react19` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | opt |
| `python-cli` | ✓ | ✓ | ✓ | opt | ✓ | ✓ | opt |
| `python-library` | ✓ | ✓ | ✓ | — | ✓ | ✓ | opt |
| `gas` | ✓ | ✓ | ✓ | — | ✓ | ✓ | opt |
| `monorepo` | ✓ | ✓ | ✓ | opt | ✓ | ✓ | opt |
| `generic` | ✓ | ✓ | ✓ | opt | ✓ | opt | opt |

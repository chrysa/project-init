# project-init — Copilot Instructions

<!-- @[claude-sonnet-4] -->

## Project purpose

`project-init` is the project bootstrapper for the chrysa ecosystem.
It generates consistent, fully-configured repository scaffolds for new projects,
eliminating manual repetitive setup and enforcing standards from day one.

## What it generates

Each generated project includes:
- CI/CD (GitHub Actions workflows from `chrysa/shared-standards`)
- Pre-commit configuration (using `chrysa/pre-commit-tools` hooks)
- Makefile (from `Forge-Stack-Workshop/base-makefile`)
- Dockerfile + docker-compose skeleton
- Dependabot configuration
- SonarCloud CI integration (never `sonar-project.properties`)
- GitHub labels, issue templates, PR template
- README with badges
- `.gitignore` (Python or Node variant from `chrysa/shared-standards/templates/`)
- VS Code settings
- GitHub Copilot instructions (from `chrysa/shared-standards/copilot-instructions/base.md`)
- Claude Code configuration (hooks from `.claude/hooks/`, settings.json)
- `CLAUDE.md` (from `chrysa/shared-standards/templates/CLAUDE.md`)
- Notion project bootstrap (when relevant)

## Architecture constraints

- `project-init` reads templates from `chrysa/shared-standards` (not embedded copies)
- Templates must be fetched at run time, not bundled statically
- Generated output must be idempotent: running twice must not corrupt a repo
- All project types (Python, React, backend API, CLI) share the same base scaffold
  with type-specific additions on top

## Supported project types

| Type | Status |
|------|--------|
| Python service/CLI | Planned |
| React app | Planned |
| Backend FastAPI | Planned |
| Tool/hook library | Planned |
| Automation/script | Planned |

## Development

```bash
# Run tests
pytest

# Run pre-commit
pre-commit run --all-files

# Generate a test project (dry-run)
python -m project_init --dry-run --type python --name test-scaffold
```

## Execution Standard

All generated projects must comply with `chrysa/shared-standards/EXECUTION_STANDARD.md`.
Fetch the standard at runtime — never embed a copy.

### §1 — Required Makefile targets

Every generated Makefile must include all 13 targets (names are invariant):

| Target | Description |
|--------|-------------|
| `help` | Print all available targets with descriptions |
| `install` | Install all dev dependencies (venv, node_modules…) |
| `dev` | Start development server / watch mode |
| `test` | Run unit tests |
| `test-cov` | Run tests with coverage (generates `coverage.xml`) |
| `lint` | Run linter (ruff / eslint / golangci-lint…) |
| `format` | Auto-format code (ruff format / prettier…) |
| `typecheck` | Run static type checker |
| `build` | Build production artefact (Docker image / dist) |
| `docker-up` | Start docker-compose services |
| `docker-down` | Stop docker-compose services |
| `clean` | Remove generated artefacts and caches |
| `pre-commit` | Run pre-commit hooks on all files |

### §2 — Directory structure

Every generated repo must include at minimum:
- `.github/workflows/` with `ci-*.yml`, `release.yml`, `pages.yml`
- `.github/PULL_REQUEST_TEMPLATE.md` and `labeler.yml`
- `docs/index.md`
- `CLAUDE.md`, `CHANGELOG.md`, `cliff.toml`, `GitVersion.yml`
- `Makefile`, `opencode.json`, `README.md`

Full spec: `chrysa/shared-standards/EXECUTION_STANDARD.md §2`

### §4 — Testing requirements

- Minimum 80% line coverage on all new code
- Test names: `test_<unit>_when_<condition>_should_<expected>`
- `coverage.xml` generated on every CI run

### §5 — CI/CD lifecycle

Generated `ci-*.yml` must run in order: lint → typecheck → test-cov (with coverage.xml upload).
Full lifecycle: `chrysa/shared-standards/EXECUTION_STANDARD.md §5`

---

## Related

- `chrysa/shared-standards` — source of all reusable templates and hooks (incl. EXECUTION_STANDARD.md)
- `Forge-Stack-Workshop/base-makefile` — Makefile templates
- `Forge-Stack-Workshop/react-app-generator` — React scaffold reference
- `chrysa/github-actions` — reusable CI action definitions

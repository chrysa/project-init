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

## Related

- `chrysa/shared-standards` — source of all reusable templates and hooks
- `Forge-Stack-Workshop/base-makefile` — Makefile templates
- `Forge-Stack-Workshop/react-app-generator` — React scaffold reference
- `chrysa/github-actions` — reusable CI action definitions

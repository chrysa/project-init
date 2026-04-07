# project-init

> **Project bootstrap and initializer for the ecosystem.**

`project-init` rationalizes project creation, enforces standards from day one, and automates the repetitive setup work that every new repository needs.

## Purpose

Every new project in the ecosystem needs the same set of things:
- CI/CD pipeline (GitHub Actions)
- Pre-commit hooks
- Makefile
- Dockerfile + docker-compose
- Dependabot configuration
- SonarQube integration
- GitHub labels and issue/PR templates
- README with badges
- `.gitignore`
- VS Code configuration
- GitHub Copilot instructions
- Claude Code configuration (hooks, settings, CLAUDE.md)
- Notion project bootstrap
- Standardized versioning

`project-init` generates all of this consistently, reduces drift between projects, and integrates shared standards from [`chrysa/shared-standards`](https://github.com/chrysa/shared-standards).

## Supported project types (planned)

| Type           | Status     |
|----------------|------------|
| Python service | Planned    |
| React app      | Planned    |
| Backend API    | Planned    |
| Automation/CLI | Planned    |
| Tool/hook repo | Planned    |

## Architecture

See [issue #1](https://github.com/chrysa/project-init/issues/1) for the architecture decision.

## Issues

| # | Title |
|---|-------|
| [#1](https://github.com/chrysa/project-init/issues/1) | Architecture and design decisions |
| [#2](https://github.com/chrysa/project-init/issues/2) | CI bootstrap templates |
| [#3](https://github.com/chrysa/project-init/issues/3) | Pre-commit bootstrap |
| [#4](https://github.com/chrysa/project-init/issues/4) | Claude Code bootstrap (hooks, settings, CLAUDE.md) |
| [#5](https://github.com/chrysa/project-init/issues/5) | GitHub bootstrap (labels, templates, Dependabot) |
| [#6](https://github.com/chrysa/project-init/issues/6) | Makefile bootstrap (from Forge-Stack-Workshop/base-makefile) |
| [#7](https://github.com/chrysa/project-init/issues/7) | VS Code bootstrap |
| [#8](https://github.com/chrysa/project-init/issues/8) | Notion bootstrap |
| [#9](https://github.com/chrysa/project-init/issues/9) | Roadmap and adoption plan |

## Related repositories

- [`chrysa/shared-standards`](https://github.com/chrysa/shared-standards) — shared Copilot instructions, Claude hooks, templates
- [`Forge-Stack-Workshop/base-makefile`](https://github.com/Forge-Stack-Workshop/base-makefile) — Makefile templates
- [`Forge-Stack-Workshop/react-app-generator`](https://github.com/Forge-Stack-Workshop/react-app-generator) — React app template
- [`chrysa/github-actions`](https://github.com/chrysa/github-actions) — reusable CI actions
- [`chrysa/pre-commit-tools`](https://github.com/chrysa/pre-commit-tools) — reusable pre-commit hooks
- [`chrysa/usefull-containers`](https://github.com/chrysa/usefull-containers) — Docker images for CI tooling

## Status

Early planning phase. See issues for the work breakdown.

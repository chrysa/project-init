# CLAUDE.md — project-init

## Project Overview

`project-init` is the **project bootstrap and initializer** for the chrysa ecosystem.

Its purpose is to automate repetitive, error-prone project setup work so every new repository starts
with standards enforced, CI wired, pre-commit configured, Claude Code integrated, and documentation
ready from day one.

## Repository Structure

```
project-init/
├── README.md        # Overview and issue index
├── CLAUDE.md        # This file
├── src/             # Initializer source code (to be created)
├── templates/       # Project templates by type (to be created)
├── docs/            # Design decisions and specs (to be created)
└── tests/           # Test suite (to be created)
```

## Stack (planned)

- **Bootstrap engine**: Python CLI (or Node.js — see issue #1)
- **Templates**: Jinja2 / Mustache (to be evaluated)
- **Standards source**: chrysa/shared-standards
- **CI**: chrysa/github-actions
- **Hooks**: chrysa/pre-commit-tools

## Design Principles

- Enforce standards by default, not as opt-in
- Every generated project must be CI-ready and pre-commit-ready from the first commit
- Minimize drift between project types
- Integrate Claude Code hooks from day one (from chrysa/shared-standards)
- Support Notion bootstrap when relevant
- Never hardcode — use configuration and shared templates

## Working Conventions

- All code, docs, issues, PRs, and generated content in **English**
- Python 3.14 target, backward-compatible to 3.12
- Tests required for all template generation logic
- SonarQube in CI only (no `sonar-project.properties`)

## Key Related Issues

| Issue | Topic |
|-------|-------|
| #1    | Architecture and design |
| #2    | CI bootstrap |
| #3    | Pre-commit bootstrap |
| #4    | Claude Code bootstrap |
| #5    | GitHub bootstrap |
| #6    | Makefile bootstrap |
| #7    | VS Code bootstrap |
| #8    | Notion bootstrap |
| #9    | Roadmap |

## Related Repositories

- `chrysa/shared-standards` — source of Claude hooks, Copilot instructions, templates
- `Forge-Stack-Workshop/base-makefile` — Makefile.python and other Makefile templates
- `chrysa/github-actions` — reusable CI actions

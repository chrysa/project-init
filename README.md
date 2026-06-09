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

## Who it's for

Maintainers bootstrapping new repositories in the chrysa ecosystem who want every
project to start with the same CI, hooks, quality gates, and conventions — with no
manual copy-paste and no drift between repos.

## Supported project types (planned)

| Type           | Status     |
|----------------|------------|
| Python service | Planned    |
| React app      | Planned    |
| Backend API    | Planned    |
| Automation/CLI | Planned    |
| Tool/hook repo | Planned    |

> The generator CLI below is not implemented yet (see [Status](#status)).
> The **Quality Gate** tool, however, ships today and is usable in any repo.

## Quality Gate (available now)

`scripts/quality_gate.py` records a baseline of quality metrics, then fails CI
when any metric regresses against that baseline. It drives seven gates: tests
passed, coverage %, lint warnings, type errors, build status, leaked secrets,
and vulnerable dependencies.

### Requirements

- Python ≥ 3.14
- A `.quality-gate.json` config at the repo root (one is shipped here)

### Usage

```bash
# 1. Record the baseline (must be all-green; aborts otherwise)
make quality-gate-baseline
# equivalent: python3 scripts/quality_gate.py baseline

# 2. Verify no regression vs the baseline (run in CI on every PR)
make quality-gate-verify
# equivalent: python3 scripts/quality_gate.py verify
```

`baseline` runs every gate command, stores the metrics in
`.quality-gate-baseline.json`, and refuses to write a baseline that contains
failing gates. `verify` re-runs the gates and exits non-zero if any metric
regresses; results are written to `.quality-gate-last-report.json` and emitted
as machine-readable `GATE_RESULT|…` / `OVERALL_RESULT|…` lines.

### Configuration (`.quality-gate.json`)

- `commands.<gate>` — overrides the command run for a gate
  (`tests`, `coverage`, `lint`, `types`, `build`).
- `thresholds.<gate>.operator` — comparison vs target: `=`, `≥`, `≤`.
- `thresholds.<gate>.value` — explicit target; when omitted, the recorded
  baseline metric is used as the target.

In CI, the gate runs via the reusable
[`chrysa/github-actions` quality-gate-check workflow](.github/workflows/quality-gate-check.yml).

### Reference examples

[`examples/`](examples/) contains reference "perfect" implementations
(service, repository, serializer, schema, API view, viewset) used as the
quality bar for generated and reviewed code.

## Architecture

See [ADR-001](docs/adr/ADR-001-architecture.md) for the full architecture decision record covering the planned design:
- Entry point: `typer` CLI (`project-init init / update / list-types`) — not yet implemented
- Config format: `.project-init.yaml` manifest (interactive fallback)
- Output model: merge strategy (idempotent, non-destructive)
- Extensibility: Jinja2 template bundles + lifecycle hooks
- Integration with `chrysa/shared-standards`

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


## Documentation map

This repo follows the chrysa standardized documentation structure
(`chrysa/shared-standards/templates/docs-structure`):

- [`docs/`](docs/) — product, architecture, security, deployment, observability (stubs)
- [`ai/`](ai/), [`prompts/`](prompts/) — AI assets & agent prompts
- [`schemas/`](schemas/) — JSON Schema data contracts
- [`workflows/`](workflows/) — end-to-end flow docs
- [`decisions/`](decisions/), [`postmortems/`](postmortems/) — decision records & incident postmortems
- [`examples/`](examples/) — reference “perfect” implementations
- [`tests/`](tests/) — test scenario catalogues

Files marked `status: stub` are placeholders to fill in.

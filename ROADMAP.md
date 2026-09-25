# ROADMAP — project-init

> Real, evidence-backed items only. Tags: **FACT / INFERENCE / UNKNOWN /
> PROPOSAL**. Source of truth for the work breakdown is the repo issue tracker
> (#1–#9, README.md); this file mirrors, it does not invent scope.

## Done (FACT — source + tests present)

- Standards-profile → `STD-*` domain resolution (`standards` command).
- FastAPI-module generation delegated to the forge (`init` command, one slice).
- `list-types` command.
- Domain-registry sync + CI drift check (`sync_standards_domains.py`).
- Quality-gate regression guard.

## Planned (FACT — README issues / ADRs)

| # | Item | Reference |
|---|------|-----------|
| 1 | Architecture & design decisions | issue #1 (ADR-001/002 accepted) |
| 2 | CI bootstrap templates | issue #2 |
| 3 | Pre-commit bootstrap | issue #3 |
| 4 | Claude Code bootstrap (hooks, settings, CLAUDE.md) | issue #4 |
| 5 | GitHub bootstrap (labels, templates, Dependabot) | issue #5 |
| 6 | Makefile bootstrap (from base-makefile) | issue #6 |
| 7 | VS Code bootstrap | issue #7 |
| 8 | Notion bootstrap | issue #8 |
| 9 | Roadmap & adoption plan | issue #9 |

## Key gates before generalising (FACT — ADR-002)

- **Validation gate:** prove the delegation boundary on `python-fastapi`
  (scaffold a throwaway repo, `make ci` green, zero post-patch of tool-owned
  output) *before* building the general engine.
- **Kill-test:** on every release, per type, measure post-patch count on
  tool-owned files; > 0 means the delegation boundary is wrong.

## Not scheduled here (UNKNOWN)

Ordering, owners, and dates are not recorded in-repo. **PROPOSAL:** issue #9 is
the natural home for the adoption timeline.

# scripts

**Role.** Standalone, host-native maintenance scripts invoked by `make` targets
and CI — not part of the importable `project_init` package, but on the test
`pythonpath` (see `pyproject.toml`) so they are unit-tested and coverage-counted.

## Structure

| Path                        | Purpose                                                                 |
| --------------------------- | ----------------------------------------------------------------------- |
| `quality_gate.py`           | Regression quality-gate baseline/verify logic.                          |
| `sync_standards_domains.py` | Generate `profiles/domains.yaml` from the canonical shared-standards `standards/domains.yaml` registry; `--check` fails on drift (`make sync-standards-domains` / `make check-standards-domains`). |

## Should contain

- Repo-maintenance scripts run via a `make` target or a CI/pre-commit step, each
  with a single class (one class per file) and a thin `main()` entry point.

## Should NOT contain

- Runtime/product logic — that lives in `src/project_init/` (the importable
  package). Scripts orchestrate; they are not the library.
- Absolute paths or machine-specific values — sources are resolved from the repo
  root or from an environment variable with a documented default (machine-agnostic).

## Rules

- One class per file, module named after it; thresholds per
  [`.claude/rules/thresholds.md`](../.claude/rules/thresholds.md).
- Every script is exercised by a `tests/test_<name>.py` module; network and the
  real filesystem source are stubbed so tests stay hermetic.
- `sync_standards_domains.py` never hand-edits its output — `profiles/domains.yaml`
  is generated from the canon (GV-000/GV-001). Editing the generated file directly
  is caught by `make check-standards-domains`.

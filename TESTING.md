# TESTING — project-init

> Tags: **FACT / INFERENCE / UNKNOWN / PROPOSAL**. Commands below are transcribed
> from `Makefile`, `Dockerfile.test`, and `.github/workflows/ci.yml`; they are
> documented, not executed by this pass.

## How tests run (FACT)

Dev/test dependencies live in a container (`Dockerfile.test`), not on the host
(chrysa container-runtime policy). The canonical commands:

```bash
make docker-test   # build project-init-test image, run pytest inside it
make ci            # full local gate: lint + check-standards-domains + docker-test
```

The plain `make test` / `make test-cov` / `make typecheck` / `make build`
targets are intentional stubs today — they echo a "no … yet / run docker-test"
message (FACT — `Makefile`). Run `make docker-test` for the real suite.

## What is covered (FACT — tests/)

Unit tests (pytest), ~50 test functions:

- `test_manifest.py` — manifest parsing, `standards_profile` default/record,
  non-mapping rejection.
- `test_forge_adapter.py` — forge invocation (success, missing CLI, non-zero
  exit, dry-run flag), structures render (id-keyed mapping, generated header,
  missing source raises).
- `test_standards_profile_resolver.py` — profile resolution, unknown profile,
  abstract-base rejection, cycle guard, per-profile domain selection
  (library/frontend), domain pointer carries home+prefix.
- `test_sync_standards_domains.py` — registry generate/check, drift detection,
  HTTP source fetch, registry-error exit code.
- `test_quality_gate.py` — gate parsing (lint/tests/types/secrets), operators,
  pytest-output parsing, JSON/regex fallbacks.

Naming follows the chrysa convention where applied
(`test_<unit>_when_<cond>_should_<expected>`, e.g. the forge-adapter tests).

## Scenario catalogues (FACT — docs, not executable)

- `tests/e2e-scenarios.md` — end-to-end delegation scenarios (per-type kill-test
  home; ADR-002).
- `tests/regression-tests.md`, `tests/edge-cases.md` — narrative catalogues.

## CI (FACT — .github/workflows/ci.yml)

- Job **Docker tests**: `make docker-test`, uploads `coverage.xml` as an
  artifact (`test-results-3.14`).
- Job **SonarCloud**: `chrysa/github-actions/sonar-scan-python@…`,
  project `project-init`.

## Coverage target (FACT — CLAUDE.md §4)

Execution standard requires 80% line coverage and `coverage.xml` on every CI
run. **UNKNOWN:** the current measured coverage percentage (a `.coverage` file
is present but not decoded by this pass).

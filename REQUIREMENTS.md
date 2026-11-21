# REQUIREMENTS — project-init

> Traceability matrix. **IMPLEMENTED** is asserted only where verifiable in-repo
> (source module + test). Tags: **FACT / INFERENCE / UNKNOWN / PROPOSAL**.

## Product requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-PROD-001 | Resolve a standards profile to its applicable `STD-*` domains (selection only) | IMPLEMENTED | `standards_profile_resolver.py`; `cli.py` `standards`; `tests/test_standards_profile_resolver.py` |
| REQ-PROD-002 | Generate a repo's FastAPI modules by delegating to the forge | IMPLEMENTED (FastAPI-module slice) | `forge_adapter.py`; `cli.py` `init`; `tests/test_forge_adapter.py` |
| REQ-PROD-003 | List supported project types | IMPLEMENTED | `cli.py` `list-types` |
| REQ-PROD-004 | `init` scaffolds a full new repo across all baseline concerns | PLANNED | ADR-001 §1 |
| REQ-PROD-005 | `update` applies missing pieces to an existing repo, idempotent, non-destructive merge | PLANNED | ADR-001 §4 |
| REQ-PROD-006 | Support `react19`, `python-cli`, `python-library`, `gas`, `monorepo`, `generic` types | PLANNED | ADR-001 §3; README table |
| REQ-PROD-007 | Optional `extras`: GitHub / Notion / SonarQube bootstrap modules | PLANNED | ADR-001 §5; README issues #5, #8 |

## Technical requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-TECH-001 | `.project-init.yaml` manifest parsed into typed value objects | IMPLEMENTED | `manifest.py`; `tests/test_manifest.py` |
| REQ-TECH-002 | Profiles are inheritable and compose via `extends`, cycle-guarded, deterministic union | IMPLEMENTED | `standards_profile_resolver.py` (depth-first, cycle guard) |
| REQ-TECH-003 | Domain registry `profiles/domains.yaml` generated from shared-standards, drift-checked in CI | IMPLEMENTED | `scripts/sync_standards_domains.py`; `make check-standards-domains`; `tests/test_sync_standards_domains.py` |
| REQ-TECH-004 | Forge invoked via subprocess; typed `ForgeError` on missing/failing CLI; dry-run supported | IMPLEMENTED | `forge_adapter.py`; `tests/test_forge_adapter.py` |
| REQ-TECH-005 | Quality-gate regression guard (baseline verify) | IMPLEMENTED | `chrysa-quality-gate` dep; `tests/test_quality_gate.py`; `make quality-gate-verify` |
| REQ-TECH-006 | Delegate to consumed tools; re-implement none of their logic | ADOPTED (policy) | ADR-002 |
| REQ-TECH-007 | Coverage report (`coverage.xml`) emitted on every CI run | IMPLEMENTED | `.github/workflows/ci.yml`; `make test-cov`/`docker-test` |
| REQ-TECH-008 | Delegation kill-test: zero post-patch of tool-owned output to reach `make ci` green | PLANNED / gated | ADR-002 kill-test; `tests/e2e-scenarios.md` |

## Notes

- The `test`/`test-cov`/`typecheck`/`build`/`docker-up` Makefile targets are
  currently stubs that print "no … yet"; the real test run is `make docker-test`
  / `make ci` (FACT — `Makefile`). See [TESTING.md](TESTING.md).
- **UNKNOWN:** whether `python-fastapi`'s validation gate (ADR-002) has been run
  green end-to-end; not determinable from the repo alone.

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

## Automation & Industrialization (NON-NEGOTIABLE)

- Projects must be **maximally automated and industrialized**.
- Every repetitive task must be covered by one of: CI/CD pipeline, Makefile target, pre-commit hook, GitHub Actions workflow, or a bot/script.
- Required automation baseline for any project:
  - **CI/CD**: automated lint, type-check, tests, build on every push/PR.
  - **Formatting**: auto-applied via pre-commit or CI (no manual `ruff`/`prettier` runs).
  - **Releases**: automated versioning and changelog generation (e.g. `cliff`, `semantic-release`).
  - **Dependency updates**: automated via Dependabot or Renovate.
  - **Secret scanning**: automated on every commit (pre-commit hook + CI step).
- When proposing or implementing a feature, always include the automation layer (tests, CI step, Makefile target) — not just the code.
- Any manual step that could be automated is considered **technical debt** and must be tracked.

## Canonical Templates & Shared Tooling

### React applications
- All new React apps **must** be bootstrapped from `Forge-Stack-Workshop/react-app-generator`.
- Never scaffold from scratch or from `create-react-app`/`vite` directly.

### Makefiles
- All project Makefiles **must** extend or be derived from `Forge-Stack-Workshop/base-makefile`.
- Do not duplicate targets that already exist in the base — inherit instead.

### Pre-commit hooks
- If a required hook is missing from `chrysa/pre-commit-tools`, **open an issue** on that repo describing the hook needed before proceeding.
- In the requesting repo, open a matching issue/PR and mark it as dependent (`Depends on chrysa/pre-commit-tools#<N>`).
- Do not implement a workaround locally — wait for the hook to land in the shared repo.

### Issue resolution automation (desired workflow)
- When a blocking issue is opened (e.g. missing hook, missing template), an agent should:
  1. Analyse the issue and propose a solution on the upstream repo.
  2. Once the solution is validated (human approval), automatically unblock the dependent issue/PR in the requesting repo.
- This workflow is aspirational — track automation gaps as issues on the relevant repos.

## Quality Thresholds

- Max function length: 50 lines when practical.
- Max file length: 500 lines when practical.
- Max cyclomatic complexity: 10.
- Lint warnings target: 0.

## Regression Prevention (NON-NEGOTIABLE)

Before marking **any** task or sub-task as done, the agent MUST verify that no regression has been introduced.

### Required checks — run in order

1. **Tests** — `make test` (or equivalent): number of passing tests must be **≥ baseline** (count before the change). Zero new failures allowed.
2. **Coverage** — coverage percentage must be **≥ baseline**. Never decrease. If no baseline exists, record the current value as baseline.
3. **Lint** — `make lint` (or `ruff check` / `eslint`): warning count must be **= 0**. No increase tolerated.
4. **Types** — `mypy` / `tsc --noEmit`: error count must be **≤ baseline**. No new type errors allowed.
5. **Build** — `make build` must exit 0 when applicable.

### Procedure

- Record baseline metrics **before** starting the task (tests passing, coverage %, lint count, type errors).
- After each implementation step, re-run the relevant checks.
- **If any check regresses**: stop, fix the regression, re-run all checks before continuing.
- Do NOT proceed to the next task if any gate is red.

### Reporting

After completing a task, always report:
```
Tests : <N> passed (baseline <N>) ✓/✗
Coverage: <X>% (baseline <X>%) ✓/✗
Lint    : 0 warnings ✓/✗
Types   : 0 errors ✓/✗
Build   : ok ✓/✗
```

---

## Related

- `chrysa/shared-standards` — source of all reusable templates and hooks (incl. EXECUTION_STANDARD.md)
- `Forge-Stack-Workshop/base-makefile` — Makefile templates
- `Forge-Stack-Workshop/react-app-generator` — React scaffold reference
- `chrysa/github-actions` — reusable CI action definitions

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
- `Makefile`, `README.md`

Full spec: `chrysa/shared-standards/EXECUTION_STANDARD.md §2`

### §4 — Testing requirements

- Minimum 80% line coverage on all new code
- Test names: `test_<unit>_when_<condition>_should_<expected>`
- `coverage.xml` generated on every CI run

### §5 — CI/CD lifecycle

Generated `ci-*.yml` must run in order: lint → typecheck → test-cov (with coverage.xml upload).
Full lifecycle: `chrysa/shared-standards/EXECUTION_STANDARD.md §5`

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

## Related

- `chrysa/shared-standards` — source of all reusable templates and hooks (incl. EXECUTION_STANDARD.md)
- `Forge-Stack-Workshop/base-makefile` — Makefile templates
- `Forge-Stack-Workshop/react-app-generator` — React scaffold reference
- `chrysa/github-actions` — reusable CI action definitions

<!-- chrysa:standards-copilot:start · generated · DO NOT EDIT -->
## chrysa standards (generated)

> The same rules as `CLAUDE.md`, for GitHub Copilot. Detail loads on demand from `standards/rules/<domain>.md`; the canon is `standards/STANDARDS.chrysa.md`.

### Governance, language & compliance · `standards/rules/governance.md`
- Normative annexes
- Language
- Compliance targets
- Governance — strategic pillars & ADR format

### Cross-cutting stack · `standards/rules/stack.md`
- Cross-cutting stack (settled ADRs — do not relitigate)

### SCM — branches, commits & pull requests · `standards/rules/scm.md`
- Commits
- Branches
- Branch model — `main` is production, `develop` is the workspace
- Merge
- One PR per issue
- Issues and PRs are type-driven

### Architecture, decoupling & portability · `standards/rules/architecture.md`
- Repo provenance — every code repo depends on `project-init`
- Every repo declares its profile and DDD level
- Projects talk through versioned contracts only
- Everything is machine-agnostic and portable — no rule, repo, or script is bound to one machine
- Every external server the service talks to is addressed through the environment — never hardcoded
- Every tracked file and folder must earn its place — a repo holds only what is useful to it now
- The repository architecture is legible to an agent — optimised for Claude, not only for humans
- Deferred work is a governed job, not a fire-and-forget

### Testing · `standards/rules/testing.md`
- Tests: pytest only
- Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later

### Frontend & web semantics · `standards/rules/frontend.md`
- TypeScript is strict by contract
- The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden
- React is a presentation layer, not the domain
- The frontend says when the backend is unreachable or unstable
- The frontend is reactive and real-time by default
- UI state survives reload & focus
- Everything is semantic — the markup, the data, and the URLs
- URL-addressable frontend navigation — mandatory

### APIs, contracts & real-time · `standards/rules/api.md`
- A real-time backend has channel contracts and never blocks
- APIs, SDKs & public contracts follow the `STD-API-001` contract

### Accessibility · `standards/rules/accessibility.md`
- Dark mode
- Every site is usable by the majority of disabilities — not only the screen-reader case

### Documentation & session state · `standards/rules/docs.md`
- Notion logging
- Documentation and Notion are maintained in lockstep with the code — a change that leaves them stale is unfinished
- Session lifecycle (primer + memory + hindsight)

### AI agents & features · `standards/rules/agents.md`
- Agent actions are governed
- An AI feature is evaluated, not just shipped
- An agent writes only where the owner owns

### Security, identity & sessions · `standards/rules/security.md`
- Per-person data implies a user account — no exceptions dressed up as simplicity
- Identity goes through the cluster SSO first
- A session is secured and it expires
- Every form is a hostile input surface — validate on the server, always

### Code quality & anti-patterns · `standards/rules/code-quality.md`
- No hardcoded constants
- No literal HTTP status codes — use the constants the framework already ships
- No code duplication — the second occurrence is an extraction order
- Raised errors are typed
- Failures are contained, and observable
- Prefer a lookup table to a state machine
- Decompose into small, independently unit-testable methods
- Code is read far more often than it is written — optimise for the reader, and standardise the form
- Avoid lambdas and anonymous constructs — a named function is the default
- Basic optimisations and known anti-patterns are caught in review and in CI
- A cache is a correctness contract, not a sprinkle of speed
- Quality gates
- Error handling pattern (all automations)

### Backend Python · `standards/rules/backend-python.md`
- Python packaging — `pyproject.toml` is the single source of truth
- Python is written object-oriented, one class per file
- Import the item, not the module — `from x import y; y()`
- Functions and methods are called with named arguments — positional call sites are the exception, not the rule

### Data, persistence & migrations · `standards/rules/data.md`
- Data, persistence & migrations follow the `STD-DATA-001` contract

### Observability & operations · `standards/rules/observability.md`
- Observability & production readiness follow the `STD-OPS-001` contract
- The container is versioned separately from the application it hosts, and an admin can see what is actually deployed
- Observability — Sentry → GitHub issues (norm)

### Containers & compose · `standards/rules/containers.md`
- External dependencies are installed in containers, never on the host
- No virtualenv in a repo — ever
- Tool caches & deps never touch the project tree
- Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory
- App containers ship the app only — the platform layer is the owner's responsibility
- Only a publicly useful port is published — everything else stays on the container network
- A compose file is minimal — declare only what the stack needs, default the rest
- Dev stage must hot-reload
- Local dev runs the code in-container, live, in debug mode — never the production server
- `.dockerignore` mandatory & exhaustive
- Container-runtime policy

### Product surfaces · `standards/rules/product.md`
- Setup wizard & config panel
- A game is DRM-free and fully playable solo offline
- Every product that is operated ships a management backoffice
- If a user can supply a file, the product accepts an upload
- A floating assistant where it earns its place — never as decoration

### Design system · `standards/rules/design.md`
- Design system

### Developer loop & tooling · `standards/rules/dev-loop.md`
- Makefile targets
- Shared skills (load on demand from shared-standards/.claude/skills/)

### CI/CD, pre-commit & release · `standards/rules/ci-cd.md`
- Release & changelog config (canonical)
- GitHub Actions (reuse first · custom actions centralised · thin workflows)
- Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)
<!-- chrysa:standards-copilot:end -->

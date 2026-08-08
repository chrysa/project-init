# project_init

**Role.** The `project-init` Python package — the orchestrator that scaffolds
chrysa repositories by *delegating* to shared tools, never re-implementing them
(see [`docs/adr/ADR-002-consume-shared-repos.md`](../../docs/adr/ADR-002-consume-shared-repos.md)).

## Structure

| Path                | Purpose                                                              |
| ------------------- | ------------------------------------------------------------------- |
| `cli.py`            | Typer command surface (`init`, `list-types`). Thin — no logic.      |
| `manifest.py`       | `ProjectManifest` / `ModuleDecl` — the parsed `.project-init.yaml`.  |
| `forge_adapter.py`  | `ForgeAdapter` — drives the FastAPI forge (engine); owns no rendering. |

## Should contain

- Orchestration code: manifest parsing, adapters over shared tools, the CLI glue.

## Should NOT contain

- File/template rendering logic — that belongs to the delegated engines
  (`fastapi-app-generator`, `django-app-forge`). Put structure *data* in
  `templates/`, not generation code here.
- Business logic in `cli.py` — commands parse and delegate only.

## Rules

- One class per module, module named after it (see
  [`.claude/rules/class-design.md`](../../../.claude/rules/class-design.md)).
- `from x import y` imports; typed signatures; raised errors are typed
  (`ForgeError`), never bare `Exception`.
- Max 500 lines/file, 50 lines/function, complexity ≤ 10
  ([`thresholds.md`](../../../.claude/rules/thresholds.md)).

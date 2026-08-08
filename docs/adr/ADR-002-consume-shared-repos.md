# ADR-002 — Consume shared repos; never re-implement the socle

**Status**: Accepted
**Date**: 2026-08-08
**Supersedes**: ADR-001 §5 (own Jinja2 template bundles as the primary generation
mechanism)

---

## Context

ADR-001 §5 proposed that `project-init` render each project type from its own
Jinja2 template bundles in `project_init/templates/<type>/`. But the chrysa /
Forge-Stack-Workshop ecosystem **already publishes** the generators and building
blocks that a bundle would otherwise reproduce:

| Concern | Existing, published tool |
| --- | --- |
| Django app/module scaffolding | `django-app-forge` (PyPI, YAML-driven) |
| FastAPI module scaffolding | `fastapi-app-forge` / `fastapi-app-generator` (PyPI, YAML-driven) |
| Makefile socle | `Forge-Stack-Workshop/base-makefile` (`Makefile.python`, `Makefile.basic`, `Makefile.with-sub-folder`) |
| CI jobs | `chrysa/github-actions/*` (composite actions + reusable workflows) |
| Commit gates | `chrysa/pre-commit-tools` (PyPI `pre-commit-hooks-tools`) + `chrysa/guideline-checker` |
| Runtime building blocks | `chrysa-lib` (`chrysa-core`, `chrysa-auth`, HTTP client, React design system) |
| Standards / copilot / Claude config | `chrysa/shared-standards` (`distribute-standards.sh`) |

Re-templating any of these inside `project-init` would create a second
implementation that drifts from the source — precisely the *no code duplication*
and *provenance* rules the standards forbid. The generators are the source of
truth; `project-init` is an **orchestrator**, not a generator.

---

## Decision

**`project-init` consumes the shared repos as dependencies and delegates to them;
it re-implements none of their logic.**

1. **App/module generation delegates to the forge tools.** A `python-fastapi`
   type does not carry a hand-written `router.py`/`service.py`/`schemas.py`
   Jinja bundle — it declares the module shape in the forge's YAML and invokes
   `fastapi-app-generator` (resp. `django-app-forge`). `project-init` owns the
   *manifest → forge-YAML → invoke* wiring, not the file templates.

2. **Makefile comes from `base-makefile`.** Generated repos `include` the
   published `base-makefile` templates (or vendor a pinned copy via the sync
   mechanism), rather than embedding a hand-rolled Makefile per type.
   `base-makefile` remains the single source of truth for target names.

3. **CI references `chrysa/github-actions`.** Generated `.github/workflows/*`
   are thin and call `uses: chrysa/github-actions/<action>@<rev>` /
   reusable workflows — never inline job logic. (Already true of this repo's own
   workflows; the generator must produce the same shape.)

4. **Commit gates reference `chrysa/pre-commit-tools`.** Generated
   `.pre-commit-config.yaml` consumes published hook ids by `rev`; no repo-local
   re-implementation of a shared hook.

5. **Runtime code depends on `chrysa-lib`.** Generated services declare
   `chrysa-core` / `chrysa-auth` / etc. as dependencies instead of scaffolding
   auth, config, logging, or the design system inline.

6. **Standards/config come from `shared-standards`** at a pinned rev, as ADR-001
   §6 already states. Unchanged.

`project-init`'s own source therefore contains **orchestration + a manifest
schema + the glue that maps a type to the right tools and revisions** — and the
minimum templates for things no shared repo owns (e.g. the `.project-init.yaml`
manifest itself, the top-level README skeleton).

**Version pinning.** Every consumed tool is pinned to a rev/tag resolved from
`shared-standards` (the same resolution `update` already performs). A generated
repo records the exact revisions it was built against in `.project-init.yaml`.

---

## Consequences

- A new project type is defined mostly by **which tools it wires and how**, not
  by a new tree of file templates to maintain.
- A fix in a forge/CI/hook repo propagates to every generated project via
  `project-init update` (re-pin + re-invoke), instead of sixty template edits.
- `project-init` must handle each tool's **contract**: its YAML/CLI, its output
  layout, and how `update` re-runs it idempotently over an existing repo.
- The `project_init/templates/` tree shrinks to glue-only; ADR-001's "bundles are
  additive" composition still holds, but the leaves delegate instead of emit.
- A hard dependency on the availability/stability of the consumed tools — see the
  kill-test.

---

## Fatal hypothesis

The published forge/CI/hook tools are **stable and complete enough** to be
delegated to: for each supported type, delegating to them produces a repo that
passes `make ci` **without** `project-init` needing to post-patch or re-template
the tool's output.

## Kill-test

For each supported type, scaffold a repo end-to-end through `project-init`
delegating to the real tools, then run `make ci` on the result in a clean
container. **Measure:** the number of files `project-init` has to overwrite or
patch *after* a tool ran to reach green. **Threshold:** if reaching green
requires `project-init` to re-template a tool's own output for any type (i.e.
post-patch count > 0 on tool-owned files), the delegation boundary for that type
is wrong — either the gap moves upstream into the tool, or that type is documented
as partially-templated with an explicit reason. **Checked:** in the type's e2e
scenario (`tests/e2e-scenarios.md`) on every `project-init` release.

## Validation gate

Before building the general template engine, prove the boundary on **one** type:
wire `python-fastapi` to `fastapi-app-generator` + `base-makefile` +
`chrysa/github-actions` + `chrysa/pre-commit-tools`, scaffold a throwaway repo,
and get `make ci` green with zero post-patch of tool-owned output. Only then
generalise to the other types.

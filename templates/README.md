# templates

**Role.** Canonical *structure data* that `project-init` feeds to the delegated
generation engines. These files describe *what* a chrysa artefact looks like; the
engines own *how* it is rendered (see
[`docs/adr/ADR-002-consume-shared-repos.md`](../docs/adr/ADR-002-consume-shared-repos.md) §1).

## Structure

| Path                      | Purpose                                                        |
| ------------------------- | ------------------------------------------------------------- |
| `fastapi/structures.yaml` | Canonical FastAPI module structures + templates, fed to `fastapi-app-generator`. |

## Should contain

- Declarative structure/template data consumed by a delegated engine (forge YAML,
  and later Jinja glue for things no shared repo owns).

## Should NOT contain

- Rendering or generation *code* — that lives upstream in the forge, or in
  `src/project_init/` as adapter glue.
- A second copy of a structure another repo already owns — if a second consumer
  appears, the file moves to its transverse home (*no duplication*).

## Rules

- One canonical file per artefact kind; it is *data*, kept in sync with the
  engine's schema, not with a hand-copied example.

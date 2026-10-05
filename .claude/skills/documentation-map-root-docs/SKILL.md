---
name: documentation-map-root-docs
description: "Procedure: Documentation map (root docs). Use when this procedure is needed."
---

Generated docs-pass records at the repo root (facts tagged FACT/INFERENCE/UNKNOWN):

- `PRD.md` — product intent, users, product requirements, scope.
- `ARCHITECTURE.md` — stack, components (`src/project_init/`), delegation boundary.
- `REQUIREMENTS.md` — REQ-PROD/REQ-TECH traceability matrix (implemented vs planned).
- `TESTING.md` — how tests run (`make docker-test`/`ci`), coverage, CI jobs.
- `SECURITY.md` — secret-scan result, attack surface, owner follow-ups.
- `ROADMAP.md` — done vs planned (issues #1–#9), ADR-002 gates.

Normative design records: `docs/adr/ADR-001-architecture.md`,
`docs/adr/ADR-002-consume-shared-repos.md` (ADR wins on conflict). Most files
under `docs/` are `status: stub` placeholders.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **project-init** (34 symbols, 29 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

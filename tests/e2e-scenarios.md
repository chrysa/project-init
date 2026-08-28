---
title: E2E Scenarios
status: active
owner: project-init
last-reviewed: 2026-08-29
---

# E2E Scenarios

End-to-end scenarios that exercise the real delegation boundary of `project-init`
(the orchestrator consumes shared tools and re-implements none of them — ADR-002).

## S1 — python-fastapi module generation via the real forge (ADR-002 gate)

**Goal:** prove the forge delegation boundary for one type (`python-fastapi`)
against the *real* `fastapi-app-generator`, not the unit-test mock.

**Setup (2026-08-29):**

```bash
pip install "git+https://…@github.com/Forge-Stack-Workshop/fastapi-app-generator.git@develop"
pip install -e .            # project-init
```

`.project-init.yaml` in a throwaway target:

```yaml
name: e2e-fastapi-gate
type: python-fastapi
standards_profile: application
modules:
  - name: widget
```

**Run:** `project-init init <target>` (real forge; `--dry-run` first, then write).

**Observed output** — files produced entirely by the forge:

```
app/api/widget/__init__.py
app/api/widget/dependencies.py
app/api/widget/models.py
app/api/widget/router.py
app/api/widget/schemas.py
app/api/widget/service.py
.forge-config.yaml
```

`.project-init.yaml` is the caller-supplied manifest (input, not tool output).

### Kill-test — post-patch of tool-owned output

**Measurement: 0 files.** `project-init init` invokes the forge
(`ForgeAdapter.generate` → `subprocess.run([fastapi-app-generator, …])`) and writes
nothing of its own into the forge's output tree. It neither rewrites nor patches any
generated module file. **Threshold (0) met** for the module-generation slice — the
delegation boundary holds: `project-init` owns none of the forge's output.

### `make ci` on the result — not yet reachable (scope gap, not a boundary breach)

The scaffold carries **no `Makefile` and no `.github/workflows/`**, so `make ci`
cannot run. This is expected: ADR-002 §2/§3 have generated repos `include` the
`Forge-Stack-Workshop/base-makefile` templates and reference `chrysa/github-actions`,
but that consumption is **not wired into the CLI yet** — the landed slice (PR #190)
covers fastapi *module* generation only (`init`, `list-types`, `standards`). The
private `chrysa-quality-gate` ssh dep the issue flags is downstream of this: it only
bites once a Makefile/CI exists to run `docker-test`.

**Conclusion:** the forge boundary is proven end-to-end (real tool, 0 post-patch).
Closing the full `make ci` gate needs the next slice — `base-makefile` +
`chrysa/github-actions` consumption in the CLI — before the kill-test can be extended
to the Makefile/CI-owned output.

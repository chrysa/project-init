# Deep-dive: `chrysa/project-init`

**Repo:** `/home/anthony/Documents/perso/projects/chrysa/project-init`
**Purpose (1 phrase):** A `typer` CLI that bootstraps and *idempotently updates* new chrysa repos from a `.project-init.yaml` manifest — rendering standardized CI, hooks, Makefile, Docker, Claude/Notion config and FastAPI modules by shelling out to shared generator repos rather than re-implementing rendering.

**Stack today:** Python 3.14, `typer` + `pydantic` v2 + `pyyaml`. Thin: `cli.py` (42 LOC), `manifest.py` (`ProjectManifest`/`ModuleDecl`, frozen pydantic models), `forge_adapter.py` (shells out to `fastapi-app-generator`). Owns *what* a module looks like (`templates/fastapi/structures.yaml`); delegates *how* to the forge. License: **MIT**.

**Design center of gravity:** the hard problem here is not first-render — it is the *update / merge* story (non-destructive, idempotent re-application as templates evolve). That is exactly the problem copier and cruft exist to solve, so they are the primary references; projen is the reference for the "synthesized files are owned, not one-off" philosophy.

---

## copier-org/copier

- **owner/repo:** copier-org/copier
- **stars:** ~3.5k
- **activity:** actively maintained (2.3k+ commits, open PRs/issues live as of 2026-08)
- **language:** Python
- **licence:** **MIT** — copiable (attribution).
- **pattern file/module:** the `copier update` command + `.copier-answers.yml` answers file, and the Jinja rendering + conflict-merge engine.
- **mechanism:** copier records the answers a user gave (the manifest analogue) into `.copier-answers.yml` committed in the target repo. On `copier update` it re-renders the template at the old answers, re-renders at the new template version, and 3-way-merges the diff into the working tree — so hand edits survive. This is the precise model `project-init` needs for its "idempotent, non-destructive merge" promise (ADR-001 output model).
- **portable snippet (the answers-file contract, ~12 lines):**
  ```yaml
  # .copier-answers.yml — committed into the generated repo
  # Changes here will be overwritten by copier update
  _commit: v1.4.0
  _src_path: gh:chrysa/project-init
  project_name: egg-manager
  type: fastapi
  python_version: "3.14"
  ```
  ```bash
  # re-apply the template after it evolved, keeping local edits
  copier update            # 3-way merge old-render → new-render → working tree
  ```
- **integration steps:**
  1. Treat `.project-init.yaml` as copier's `.copier-answers.yml`: persist the resolved manifest + a template version/commit pin into the generated repo.
  2. For `project-init update`, re-render at the pinned version and at HEAD, then diff-merge — do not blind-overwrite. Reuse copier's "render twice + 3-way merge" algorithm rather than a naive file copy.
  3. Adopt copier's `_tasks`/`_migrations` hook idea for the lifecycle hooks ADR-001 mentions.
- **gotchas:** copier's merge relies on a git working tree in the target; `project-init` must require (or `git init`) the target repo before update. Conflict markers can land in files on real divergence — surface them, don't swallow. Answers file must be committed or update has no baseline.

## cruft/cruft

- **owner/repo:** cruft/cruft
- **stars:** ~1.6k
- **activity:** maintained (218+ commits, open issues/PRs live 2026-08)
- **language:** Python
- **licence:** **MIT** — copiable.
- **pattern file/module:** `.cruft.json` state file + `cruft update` / `cruft check` (drift detection) — cookiecutter-compatible.
- **mechanism:** cruft stores the template git commit + the answers in `.cruft.json`. `cruft check` tells you if a repo has drifted behind its template (exit code = CI gate); `cruft update` generates a diff between the old and new template render and applies it as a patch. This maps directly onto the memory note *"real systemic lint fix = project-init#193 (template drift)"* — cruft is the canonical answer to fleet-wide template drift.
- **portable snippet (drift gate, ~8 lines):**
  ```bash
  # CI job: fail if the repo fell behind project-init's templates
  cruft check || {
    echo "::error::repo has drifted from project-init template"
    exit 1
  }
  # developer applies the outstanding template delta as a patch
  cruft update --skip-apply-ask --refresh-private-variables
  ```
- **integration steps:**
  1. Add a `project-init check` subcommand that compares the committed manifest+pin against current templates and exits non-zero on drift — wire it into each repo's `make` / CI so drift is caught fleet-wide, not by manual audit.
  2. Store the template commit hash in `.project-init.yaml` (cruft's `.cruft.json` role) so `check`/`update` have a baseline.
  3. Model `update` as "generate patch old→new, apply with fallback to `.rej`" like cruft, not full regen.
- **gotchas:** cruft applies updates via `git apply`; partial failures leave `.rej` reject files — must be reported. It assumes cookiecutter-style single-template lineage; `project-init`'s multi-bundle (CI + hooks + FastAPI modules) means you need one pin *per bundle* or drift detection is coarse.

## projen/projen

- **owner/repo:** projen/projen
- **stars:** ~2.9k
- **activity:** very active (3.9k+ commits, release workflow live 2026-08)
- **language:** TypeScript (jsii, multi-language synth)
- **licence:** **Apache-2.0** — copiable (patent grant + NOTICE/attribution).
- **pattern file/module:** the synthesis model — `.projenrc.ts` as the single typed source of truth, `projen` re-synthesizes managed files marked read-only.
- **mechanism:** instead of a one-off scaffold, projen keeps a typed project definition and *regenerates* managed config files on every run, stamping them with a "do not edit, managed by projen" marker so drift is impossible by construction. This is the opposite pole from copier/cruft's merge-hand-edits approach and worth a conscious ADR choice: `project-init` currently leans merge (copier/cruft), but for files that should never be hand-edited (CI YAML, Dependabot, labels) projen's "owned + regenerated + marked" model is safer and cheaper than 3-way merge.
- **portable snippet (the managed-file marker convention, ~6 lines):**
  ```yaml
  # ~~ Generated by project-init. To modify, edit .project-init.yaml and re-run
  #    `project-init update`. Manual edits to this file will be overwritten. ~~
  name: CI
  on: [push, pull_request]
  # ...rendered body...
  ```
- **integration steps:**
  1. Split templates into two classes in ADR terms: *owned* (regenerate + marker, projen-style — CI, Dependabot, labels) vs *seeded* (merge once, respect edits, copier-style — README, source modules).
  2. For owned files, skip the merge engine entirely: overwrite + marker comment. Simpler and matches how the fleet actually treats CI config.
- **gotchas:** projen is TypeScript/jsii — do **not** vendor its code; it is a *pattern* reference only (a Python port is a rewrite). The "overwrite managed files" model is user-hostile if applied to files people legitimately edit — classify carefully or you'll clobber work.

---

## Licence flags summary

All three references are **permissive and copiable**: copier (MIT), cruft (MIT), projen (Apache-2.0). Also-relevant cookiecutter is **BSD-3-Clause** (permissive). **No copyleft/restrictive (GPL/AGPL/BSL/Elastic/fair-code) sources** — nothing needs clean-room reimplementation for licence reasons. projen is a language mismatch (TS), so it is pattern-only regardless.

## Cross-cutting takeaways

1. The whole value of this repo is the **update path**, and copier's "render-twice + 3-way merge" + cruft's `.cruft.json` pin & `check` drift-gate are the two battle-tested algorithms to copy — both MIT.
2. Persist the resolved manifest **plus a template version pin** into every generated repo; without a baseline commit, idempotent update and drift-check are impossible (this is the root of the observed project-init#193 template drift).
3. Classify templates into *owned* (projen-style overwrite+marker: CI/Dependabot/labels) vs *seeded* (copier-style merge: README/source) — one uniform strategy will either clobber edits or leave config drifting.

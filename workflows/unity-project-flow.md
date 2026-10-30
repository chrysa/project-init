---
title: Unity Project Flow
status: active
owner: chrysa
last-reviewed: 2026-10-03
---

# Unity Project Flow

## Purpose

End-to-end flow to create (or align) a chrysa Unity game repository. Every mechanical
step goes through the **Unity CLI** (`unity`) or the standard **MCP** server it ships
(`unity mcp`), so the flow is replayable by any coding agent or by hand.

## Preconditions

- Unity **6.0+** (`6000.x`). Live Editor control (`com.unity.pipeline`) does not exist
  below 6.0: stop and upgrade first.
- Unity CLI on `PATH` — check with `which unity && unity --version`. The Unity Hub now
  installs it; otherwise the official installer is
  `curl -fsSL https://unity.com/install.sh | bash` (Linux/macOS) or
  `irm https://unity.com/install.ps1 | iex` (Windows). Install only with the owner's
  agreement.
- Unity account signed in: `unity auth login` (interactive, run by the owner).
  CI uses `UNITY_SERVICE_ACCOUNT_ID` / `UNITY_SERVICE_ACCOUNT_SECRET` from secrets.

## Steps

| # | Step | Command | Gate |
|---|------|---------|------|
| 1 | Identity gate | Notion card: identity / innovation / success criteria filled | Owner decision |
| 2 | Create the project | `unity projects create <name> --path <dir> --editor-version <6000.x> --no-cloud --with-pipeline` (`--no-cloud`: games are offline/DRM-free) | Owner confirms editor version |
| 3 | Version control | `git init -b develop`, Unity `.gitignore` (see below), push to `chrysa/<name>` (private) | `main` + `develop` protected |
| 4 | Standards | Enroll in `shared-standards` `repos.yml`, run `distribute-standards` | PR on shared-standards |
| 5 | Agent wiring | Apply [`prompts/unity-agent-setup.md`](../prompts/unity-agent-setup.md) | Owner approves each install |
| 6 | Live Editor bridge | Existing projects only: `unity pipeline install --project-path .` (adds `com.unity.pipeline` to `Packages/manifest.json`; step 2 already did it via `--with-pipeline`) | Owner approves; commit the manifest change |
| 7 | MCP registration | `unity mcp configure <client> --project-path .` (`--local` for cursor / vscode / kiro / codex) | Skip for an agent whose Unity plugin already registers `unity mcp` |
| 8 | Proof | `unity status` reports `ready`; `unity test` passes EditMode + PlayMode | Exit code `0` (`8` = failing tests) |

## Mandatory `.gitignore` entries

On top of the standard Unity block (`Library/`, `Temp/`, `Obj/`, `Build/`, `Builds/`,
`Logs/`, `UserSettings/`, …), every Unity repo ignores agent-local configuration
**in its own `.gitignore`** (never rely on a machine's global ignore):

```gitignore
# agent-local configuration (never committed)
.claude/settings.local.json
.mcp.json
.vscode/mcp.json
.cursor/mcp.json
.codex/
*.alf
*.ulf
```

## Invariants

- No commit trailer or file content that credits a coding agent.
- Automations call `unity …` or the MCP server — never an agent-specific hook,
  slash command or plugin API.
- Opening a project with a newer editor rewrites `Packages/manifest.json`: always pass
  `--editor-version` / `--project-path` explicitly when several editors are installed.

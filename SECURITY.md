# SECURITY — project-init

> Docs-only security review of the repository as it stands. Tags:
> **FACT / INFERENCE / UNKNOWN / PROPOSAL**. This pass reports findings for the
> owner; it does **not** modify code. `docs/security.md` is a stub — this file is
> the populated root record.

## Secret-scan result (FACT)

No hardcoded secrets found in the files inspected. All credential references are
environment-variable indirections, not literals:

- `.mcp.json` / `opencode.json`: `GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_TOKEN}"`
  and `OPENAPI_MCP_HEADERS` with `Bearer ${NOTION_API_KEY}` — placeholders, not
  values. **[No secret material — env references only.]**
- `.secrets.baseline` (detect-secrets) tracks entries in `.claude/HOOKS_README.md`
  and `.pre-commit-config.yaml`; **INFERENCE:** these are baseline/allowlist
  markers (example or hook-doc strings), not live secrets. Owner should confirm
  the baseline is current.

## Attack surface (INFERENCE)

`project-init` is a developer/CI CLI, not a network service. Its notable
behaviours:

- **Subprocess invocation of an external forge CLI** (`forge_adapter.py`,
  `subprocess.run(..., check=False)`). Command/args are derived from the repo's
  own `.project-init.yaml` and canonical structures file. **PROPOSAL:** treat the
  manifest as a trusted-input boundary; if a manifest can ever come from an
  untrusted source, validate/whitelist module names and paths before they reach
  the forge command line.
- **YAML loading** of profiles/domains/manifest uses `yaml.safe_load`
  throughout (FACT — verified in `cli.py`, `forge_adapter.py`,
  `standards_profile_resolver.py`, `scripts/*.py`). No unsafe `yaml.load`.
- **HTTP source fetch** in `scripts/sync_standards_domains.py`
  (`test_http_source_is_fetched`). **PROPOSAL:** ensure the registry source URL
  is pinned/trusted and served over HTTPS.

## Controls in place (FACT)

- Security scanning is a gate: `secret-scan.yml` workflow + `detect-secrets`
  baseline + pre-commit hooks (chrysa "security scanning is a gate" rule).
- Credentials are addressed through the environment, never hardcoded (chrysa
  portability rule) — satisfied by the MCP config above.

## HIGH / CRITICAL findings

None identified by this docs-only pass.

## Follow-ups for the owner (PROPOSAL, LOW/MEDIUM)

1. Confirm the standards-registry fetch URL is HTTPS and pinned.
2. Confirm the manifest is a trusted-input boundary before forge subprocess use.
3. Refresh / re-verify `.secrets.baseline`.

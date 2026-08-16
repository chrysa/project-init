"""Generate ``profiles/domains.yaml`` from the shared-standards domain registry.

``profiles/domains.yaml`` is a **derived pointer** into the canonical GV-015
registry that lives in ``chrysa/shared-standards`` (``standards/domains.yaml``).
It is generated, never hand-mirrored: copying the canon by hand drifts silently
and breaks GV-000/GV-001 (the registry is the single distributed artifact).

Holds :class:`DomainsRegistrySync`, which reads the canonical registry (a
``domains:`` list of ``id``/``home``/``prefix``/… entries), projects each entry
to the ``home``/``prefix``/``summary`` shape the local
:class:`~project_init.standards_profile_resolver.StandardsProfileResolver` reads,
and renders the local file. It runs in two modes:

* **generate** (default) — write ``profiles/domains.yaml``.
* ``--check`` — regenerate in memory and fail if the committed file has drifted
  (for CI and pre-commit; catches a hand-edit or a moved source).

The canonical source is configurable and machine-agnostic — never a hardcoded
absolute path. It is resolved from ``SHARED_STANDARDS_DOMAINS`` (a filesystem
path or an ``http(s)`` URL); absent that, it falls back to a sibling checkout at
``<repo>/../shared-standards/standards/domains.yaml``.

Run: ``python -m scripts.sync_standards_domains [--check] [--source PATH_OR_URL]``
(or ``make sync-standards-domains`` / ``make check-standards-domains``).
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TARGET = _REPO_ROOT / "profiles" / "domains.yaml"
_SOURCE_ENV = "SHARED_STANDARDS_DOMAINS"
_DEFAULT_SOURCE = _REPO_ROOT.parent / "shared-standards" / "standards" / "domains.yaml"

_HEADER = (
    "# GENERATED from chrysa/shared-standards standards/domains.yaml — do not edit by hand.\n"
    "#\n"
    "# Regenerate with `make sync-standards-domains`; CI runs `make check-standards-domains`\n"
    "# (scripts/sync_standards_domains.py --check) to fail on drift. The canonical GV-015\n"
    "# registry is the single source of truth (GV-000/GV-001) — this is a derived pointer\n"
    "# that carries only domain id -> home + prefix (+ summary), never rule bodies.\n"
    "#\n"
    "# Source is configurable via the SHARED_STANDARDS_DOMAINS env var (path or raw URL).\n"
)

# The local StandardsDomain model forbids extras, so only these three keys are
# projected from a canonical entry: the canon's `title` becomes the local
# `summary`, and status/priority (governance metadata) are dropped.


class DomainsRegistryError(Exception):
    """The canonical registry is missing, unreadable, or malformed."""


class DomainsRegistrySync:
    """Generate (or verify) the local domain pointer from the canonical registry."""

    def __init__(self, source: str, target: Path = _TARGET) -> None:
        self._source = source
        self._target = target

    @classmethod
    def from_env(cls, source: str | None = None, target: Path | None = None) -> "DomainsRegistrySync":
        """Build a sync, resolving the source from the CLI arg then the env then the default.

        ``target`` defaults to the module-level ``_TARGET`` read at call time (so it
        stays monkeypatchable in tests, rather than frozen as a default argument).
        """
        resolved = source or os.environ.get(_SOURCE_ENV) or str(_DEFAULT_SOURCE)
        return cls(resolved, target if target is not None else _TARGET)

    def check(self) -> bool:
        """Return ``True`` when the committed target matches freshly-generated output."""
        if not self._target.exists():
            return False
        return self._target.read_text(encoding="utf-8") == self.render()

    def render(self) -> str:
        """Return the generated file content (header + YAML), without writing it."""
        domains = self._projected_domains()
        body = yaml.safe_dump(
            {"version": 1, "domains": domains},
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
        return f"{_HEADER}{body}"

    def write(self) -> Path:
        """Generate and write the target file; return its path."""
        self._target.write_text(self.render(), encoding="utf-8")
        return self._target

    def _projected_domains(self) -> dict[str, dict[str, str]]:
        raw = self._load_source()
        entries = raw.get("domains")
        if not isinstance(entries, list):
            raise DomainsRegistryError(
                f"{self._source}: expected a 'domains' list, got {type(entries).__name__}"
            )
        projected: dict[str, dict[str, str]] = {}
        for entry in entries:
            domain_id, mapped = self._project_entry(entry)
            projected[domain_id] = mapped
        return projected

    def _load_source(self) -> dict[str, Any]:
        text = self._read_source_text()
        document = yaml.safe_load(text)
        if not isinstance(document, dict):
            raise DomainsRegistryError(
                f"{self._source}: registry must be a YAML mapping, got {type(document).__name__}"
            )
        return document

    def _read_source_text(self) -> str:
        if self._source.startswith(("http://", "https://")):
            with urllib.request.urlopen(self._source) as response:  # noqa: S310 - documented URL source
                return response.read().decode("utf-8")
        path = Path(self._source)
        if not path.exists():
            raise DomainsRegistryError(
                f"Canonical registry not found at {path} — set {_SOURCE_ENV} to a "
                "shared-standards standards/domains.yaml path or raw URL."
            )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _project_entry(entry: Any) -> tuple[str, dict[str, str]]:
        if not isinstance(entry, dict):
            raise DomainsRegistryError(f"Domain entry must be a mapping, got {entry!r}")
        domain_id = entry.get("id")
        if not domain_id:
            raise DomainsRegistryError(f"Domain entry missing 'id': {entry!r}")
        if "home" not in entry or "prefix" not in entry:
            raise DomainsRegistryError(f"Domain {domain_id!r} missing 'home' or 'prefix'")
        mapped: dict[str, str] = {"home": entry["home"], "prefix": entry["prefix"]}
        summary = entry.get("summary") or entry.get("title")
        if summary:
            mapped["summary"] = summary
        return domain_id, mapped


def _display(target: Path) -> str:
    """Render ``target`` relative to the repo root when it lives under it."""
    try:
        return str(target.relative_to(_REPO_ROOT))
    except ValueError:
        return str(target)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed file matches the source; exit non-zero on drift.",
    )
    parser.add_argument(
        "--source",
        default=None,
        help=f"Registry path or raw URL (overrides ${_SOURCE_ENV} and the sibling default).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    sync = DomainsRegistrySync.from_env(args.source)
    try:
        if args.check:
            if sync.check():
                sys.stdout.write("profiles/domains.yaml is in sync with the canonical registry.\n")
                return 0
            sys.stderr.write(
                "profiles/domains.yaml has drifted from the canonical registry.\n"
                "Run `make sync-standards-domains` and commit the result.\n"
            )
            return 1
        target = sync.write()
        sys.stdout.write(f"Generated {_display(target)} from the canonical registry.\n")
        return 0
    except DomainsRegistryError as error:
        sys.stderr.write(f"{error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

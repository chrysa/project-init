"""Adapter over the `fastapi-app-generator` engine (the forge).

`project-init` owns *what* a chrysa FastAPI module looks like (the canonical
``templates/fastapi/structures.yaml``) and the *manifest → merged-YAML → invoke*
wiring; the forge owns *how* files are rendered and written. This module never
re-implements the rendering — it shells out to the published CLI. See
docs/adr/ADR-002-consume-shared-repos.md §1.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from .manifest import ProjectManifest

_DEFAULT_GENERATOR = "fastapi-app-generator"


class ForgeError(RuntimeError):
    """Raised when the forge is missing or exits non-zero."""


class ForgeAdapter:
    """Drive the FastAPI forge from a :class:`ProjectManifest`."""

    def __init__(
        self,
        structures_path: Path,
        generator: str = _DEFAULT_GENERATOR,
    ) -> None:
        self._structures_path = structures_path
        self._generator = generator

    def build_forge_document(self, manifest: ProjectManifest) -> dict[str, Any]:
        """Merge the manifest's modules into the canonical structures document.

        Returns the full forge document (``version``/``templates``/``structures``
        from the owned file, ``base_path`` and ``modules`` from the manifest).
        """
        document = self._load_structures()
        document["base_path"] = manifest.base_path
        document["modules"] = [
            {"name": module.name, "structure": module.structure}
            for module in manifest.modules
        ]
        return document

    def generate(
        self,
        manifest: ProjectManifest,
        root: Path,
        *,
        dry_run: bool = False,
    ) -> None:
        """Render the manifest's modules under ``root`` by invoking the forge.

        Writes the merged forge document next to ``root`` and calls the CLI.
        Raises :class:`ForgeError` if the CLI is absent or fails.
        """
        document = self.build_forge_document(manifest)
        config_path = root / ".forge-config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.safe_dump(document, sort_keys=False))
        self._invoke(config_path, root, dry_run=dry_run)

    def _invoke(self, config_path: Path, root: Path, *, dry_run: bool) -> None:
        command = [
            self._generator,
            "--config",
            str(config_path),
            "--root",
            str(root),
        ]
        if dry_run:
            command.append("--dry-run")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except FileNotFoundError as error:
            raise ForgeError(
                f"Forge CLI {self._generator!r} not found — install fastapi-app-generator"
            ) from error
        if result.returncode != 0:
            raise ForgeError(
                f"Forge exited {result.returncode}: {result.stderr.strip()}"
            )

    def _load_structures(self) -> dict[str, Any]:
        raw = yaml.safe_load(self._structures_path.read_text())
        if not isinstance(raw, dict):
            raise ForgeError(
                f"{self._structures_path} must be a YAML mapping, got {type(raw).__name__}"
            )
        return raw

"""project-init — orchestrator that scaffolds chrysa repos from shared tools."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("chrysa-project-init")
except PackageNotFoundError:  # pragma: no cover - editable/source checkout
    __version__ = "0.0.0"

__all__ = ["__version__"]

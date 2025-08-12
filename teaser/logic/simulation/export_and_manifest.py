from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Optional

# Use TEASER's existing utilities
from teaser.logic.utilities import get_default_path, create_path


def build_manifest(prj, export_dir: Optional[str] = None, *, engine: Optional[str] = None) -> Path:
    """Write a manifest JSON next to the exported Modelica package, using
    TEASER's utilities for paths.

    Parameters
    ----------
    prj : TEASER Project
        Project that has already been prepared (buildings added, calc done).
    export_dir : Optional[str]
        Root export directory. If None, use `utilities.get_default_path()`.
    engine : Optional[str]
        Optional default engine hint ("omc"/"OpenModelica" or "dymola").

    Returns
    -------
    Path to the written manifest file.
    """
    root = Path(export_dir) if export_dir else Path(get_default_path())
    create_path(str(root))  # ensure exists (uses TEASER util)

    package_dir = root / prj.name
    results_dir = package_dir / "BuildingsPyResults" / "results"
    create_path(str(results_dir))

    items = []
    for b in prj.buildings:
        model = f"{prj.name}.{b.name}.{b.name}"
        m = re.match(r"(\w+)bt_", b.name)
        items.append({
            "model": model,
            "type": m.group(1) if m else None,
        })

    manifest = {
        "project": prj.name,
        "engine": (engine or None),
        "packagePath": package_dir.as_posix(),
        "outputDir": results_dir.as_posix(),
        "items": items,
    }

    manifest_path = package_dir / "manifest.json"
    create_path(str(package_dir))
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


autodoc = """Small helper that exports and writes a manifest using TEASER utilities."""

def export_and_manifest(prj, export_dir: Optional[str] = None, *, engine: Optional[str] = None) -> Path:
    """Export AixLib package and create the manifest in one go using
    TEASER's utilities for default paths.
    """
    root = Path(export_dir) if export_dir else Path(get_default_path())
    create_path(str(root))

    # Export
    prj.export_aixlib(path=str(root))

    # Build manifest
    return build_manifest(prj, str(root), engine=engine)
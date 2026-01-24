"""
Dataset Builder (Core)

Consolidate datasets into a unified format and validate grid bounds.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.dataset_manager import DatasetManager
from core.services.grid_config import load_grid_config
from core.services.logging_manager import get_logger, get_repo_root
from core.services.map_renderer import MapRenderer

logger = get_logger("core.dataset_builder")


def build_locations(
    sources: List[str],
    output_path: Path,
    drop_out_of_bounds: bool = True,
    normalize_cells: bool = False,
) -> Dict[str, Any]:
    grid_cfg = load_grid_config()
    standard = grid_cfg.get("viewports", {}).get("standard", {})
    cols = int(standard.get("cols", 80))
    rows = int(standard.get("rows", 30))

    merged: Dict[str, Any] = {
        "description": "Unified locations dataset",
        "grid": {"cols": cols, "rows": rows},
        "locations": [],
    }

    seen_ids = set()
    dropped = 0

    for src in sources:
        data = _load_json(Path(src))
        if not data:
            continue
        for loc in data.get("locations", []):
            loc_id = loc.get("id")
            if not loc_id or loc_id in seen_ids:
                continue
            tiles = loc.get("tiles", {})
            if drop_out_of_bounds:
                cleaned = {}
                for cell_id, tile in tiles.items():
                    norm_id = _normalize_cell_id(cell_id) if normalize_cells else cell_id
                    col = MapRenderer._parse_col(norm_id)  # type: ignore[attr-defined]
                    row = MapRenderer._parse_row(norm_id)  # type: ignore[attr-defined]
                    if col is None or row is None:
                        dropped += 1
                        continue
                    if col >= cols or row >= rows:
                        dropped += 1
                        continue
                    cleaned[norm_id] = tile
                loc["tiles"] = cleaned
            merged["locations"].append(loc)
            seen_ids.add(loc_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, indent=2))
    return {
        "status": "success",
        "locations": len(merged["locations"]),
        "dropped_cells": dropped,
        "output": str(output_path),
    }


def build_dataset(
    dataset_id: str,
    output_id: Optional[str] = None,
    mode: str = "build",
) -> Dict[str, Any]:
    manager = DatasetManager()
    cfg = _load_config()
    outputs = cfg.get("outputs", {})
    output_rel = outputs.get(output_id or f"{dataset_id}_unified")
    if not output_rel:
        return {"status": "error", "message": "No output configured for dataset"}

    if dataset_id != "locations":
        return {"status": "error", "message": "Only locations build is supported"}

    sources = []
    for ds in manager.list_datasets():
        if ds.get("type") == "locations":
            sources.append(manager._resolve_path(ds.get("path", "")).as_posix())

    output_path = get_repo_root() / output_rel
    normalize = mode == "regen"
    return build_locations(
        sources,
        output_path,
        drop_out_of_bounds=True,
        normalize_cells=normalize,
    )


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None


def _normalize_cell_id(cell_id: str) -> str:
    # Expected format: AA10, AB05, etc.
    cleaned = cell_id.strip().upper().replace(" ", "")
    return cleaned
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _load_config() -> Dict[str, Any]:
    config_path = get_repo_root() / "core" / "config" / "datasets.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return {}

"""
DATASET command handler - dataset listing and validation.
"""

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.dataset_manager import DatasetManager
from core.tools.dataset_builder import build_dataset
from core.services.grid_config import load_grid_config
from core.services.map_renderer import MapRenderer
from core.tui.output import OutputToolkit


class DatasetHandler(BaseCommandHandler):
    """Handler for DATASET command."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._list()
        if subcommand == "VALIDATE":
            if len(params) < 2:
                return {
                    "status": "error",
                    "message": "DATASET VALIDATE <id>",
                }
            return self._validate(params[1])
        if subcommand == "BUILD":
            if len(params) < 2:
                return {"status": "error", "message": "DATASET BUILD <id> [output_id]"}
            output_id = params[2] if len(params) > 2 else None
            result = build_dataset(params[1], output_id=output_id, mode="build")
            return result
        if subcommand == "REGEN":
            if len(params) < 2:
                return {"status": "error", "message": "DATASET REGEN <id> [output_id]"}
            output_id = params[2] if len(params) > 2 else None
            result = build_dataset(params[1], output_id=output_id, mode="regen")
            return result

        return {"status": "error", "message": f"Unknown DATASET subcommand: {subcommand}"}

    def _help(self) -> Dict:
        output = "\n".join(
            [
                OutputToolkit.banner("DATASET HELP"),
                "DATASET LIST",
                "DATASET VALIDATE <id>",
                "DATASET BUILD <id> [output_id]",
                "DATASET REGEN <id> [output_id]",
            ]
        )
        return {"status": "success", "message": "DATASET help", "output": output}

    def _list(self) -> Dict:
        manager = DatasetManager()
        rows = []
        for ds in manager.list_datasets():
            rows.append([ds.get("id", ""), ds.get("type", ""), ds.get("path", "")])
        output = "\n".join(
            [
                OutputToolkit.banner("DATASETS"),
                OutputToolkit.table(["id", "type", "path"], rows) if rows else "(none)",
            ]
        )
        return {
            "status": "success",
            "message": "Datasets",
            "output": output,
        }

    def _validate(self, dataset_id: str) -> Dict:
        manager = DatasetManager()
        ds = manager.get_dataset(dataset_id)
        if not ds:
            return {"status": "error", "message": f"Unknown dataset: {dataset_id}"}

        if ds.get("type") != "locations":
            path = manager._resolve_path(ds.get("path", ""))
            if not path.exists():
                return {"status": "error", "message": "Dataset file not found"}
            output = "\n".join(
                [
                    OutputToolkit.banner("DATASET VALIDATE"),
                    f"Dataset exists: {path}",
                ]
            )
            return {"status": "success", "message": "Dataset file exists", "output": output}

        data = manager.load_json(dataset_id)
        if not data:
            return {"status": "error", "message": "Failed to load dataset"}

        grid_cfg = load_grid_config()
        standard = grid_cfg.get("viewports", {}).get("standard", {})
        cols = int(standard.get("cols", 80))
        rows = int(standard.get("rows", 30))

        bad_cells = []
        locations = data.get("locations", [])
        for loc in locations:
            tiles = loc.get("tiles", {})
            for cell_id in tiles.keys():
                col = MapRenderer._parse_col(cell_id)  # type: ignore[attr-defined]
                row = MapRenderer._parse_row(cell_id)  # type: ignore[attr-defined]
                if col is None or row is None:
                    bad_cells.append((loc.get("id", "unknown"), cell_id, "parse"))
                elif col >= cols or row >= rows:
                    bad_cells.append((loc.get("id", "unknown"), cell_id, "bounds"))

        if bad_cells:
            rows = [[loc_id, cell_id, reason] for loc_id, cell_id, reason in bad_cells[:20]]
            if len(bad_cells) > 20:
                rows.append(["...", f"{len(bad_cells) - 20} more", ""])
            output = "\n".join(
                [
                    OutputToolkit.banner("DATASET VALIDATION"),
                    f"Invalid cells: {len(bad_cells)}",
                    OutputToolkit.table(["location", "cell", "reason"], rows),
                ]
            )
            return {
                "status": "warning",
                "message": "Dataset validation warnings",
                "output": output,
            }

        output = "\n".join(
            [
                OutputToolkit.banner("DATASET VALIDATION"),
                f"Dataset valid for {cols}x{rows} grid",
            ]
        )
        return {"status": "success", "message": "Dataset valid", "output": output}

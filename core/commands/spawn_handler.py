"""SPAWN command handler - Create objects and sprites at locations."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.locations import load_locations


class SpawnHandler(BaseCommandHandler):
    """Handler for SPAWN command - create objects/sprites at locations."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle SPAWN command.

        Args:
            command: Command name (SPAWN)
            params: [object_type] [object_char] [object_name] at [location_id] [cell_id]
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with status and spawn result
        """
        if len(params) < 5:
            return {
                "status": "error",
                "message": "SPAWN requires: type char name [at] location_id cell_id",
            }

        obj_type = params[0].lower()  # object or sprite
        obj_char = params[1]
        obj_name = params[2]
        # params[3] should be "at"
        location_id = params[4]
        cell_id = params[5] if len(params) > 5 else "AA00"

        # Validate type
        if obj_type not in ["object", "sprite"]:
            return {
                "status": "error",
                "message": f"Type must be 'object' or 'sprite', got '{obj_type}'",
            }

        try:
            db = load_locations()
            location = db.get(location_id)
        except Exception as e:
            return {"status": "error", "message": f"Failed to load location: {str(e)}"}

        if not location:
            return {"status": "error", "message": f"Location {location_id} not found"}

        # Check if cell exists
        if cell_id not in location.tiles:
            return {
                "status": "error",
                "message": f"Cell {cell_id} not found in {location.name}",
                "available_cells": list(location.tiles.keys()),
            }

        # For now, we'll just return a success message
        # (Actual spawning would modify the location data structure)
        if obj_type == "object":
            return {
                "status": "success",
                "message": f"Spawned {obj_char} {obj_name} at {location.name}:{cell_id}",
                "location_id": location_id,
                "cell_id": cell_id,
                "object_type": "object",
                "object_char": obj_char,
                "object_name": obj_name,
            }
        else:  # sprite
            return {
                "status": "success",
                "message": f"Spawned sprite {obj_char} {obj_name} at {location.name}:{cell_id}",
                "location_id": location_id,
                "cell_id": cell_id,
                "object_type": "sprite",
                "object_char": obj_char,
                "object_name": obj_name,
                "note": "Sprite can move and interact with environment",
            }

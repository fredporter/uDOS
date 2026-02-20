"""SPAWN command handler - Create objects and sprites at locations."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.locations import load_locations
from core.tui.output import OutputToolkit
from core.services.error_contract import CommandError


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
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="SPAWN requires: type char name [at] location_id cell_id",
                recovery_hint="Usage: SPAWN <object|sprite> <char> <name> at <locid> <cell>",
                level="INFO",
            )

        obj_type = params[0].lower()  # object or sprite
        obj_char = params[1]
        obj_name = params[2]
        # params[3] should be "at"
        location_id = params[4]
        cell_id = params[5] if len(params) > 5 else "AA00"

        # Validate type
        if obj_type not in ["object", "sprite"]:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Type must be 'object' or 'sprite', got '{obj_type}'",
                recovery_hint="Use SPAWN object or SPAWN sprite",
                level="INFO",
            )

        try:
            db = load_locations()
            location = db.get(location_id)
        except Exception as e:
            raise CommandError(
                code="ERR_LOCATION_LOAD_FAILED",
                message=f"Failed to load location: {str(e)}",
                recovery_hint="Run VERIFY to check location data integrity",
                level="WARNING",
            )

        if not location:
            raise CommandError(
                code="ERR_LOCATION_NOT_FOUND",
                message=f"Location {location_id} not found",
                recovery_hint="Use FIND to search for available locations",
                level="INFO",
            )

        # Check if cell exists
        if cell_id not in location.tiles:
            raise CommandError(
                code="ERR_LOCATION_NOT_FOUND",
                message=f"Cell {cell_id} not found in {location.name}",
                recovery_hint="Pick a valid cell from the location grid",
                details={"available_cells": list(location.tiles.keys())},
                level="INFO",
            )

        # For now, we'll just return a success message
        # (Actual spawning would modify the location data structure)
        output = "\n".join(
            [
                OutputToolkit.banner("SPAWN"),
                OutputToolkit.table(
                    ["type", "name", "char", "location", "cell"],
                    [[obj_type, obj_name, obj_char, location.name, cell_id]],
                ),
            ]
        )

        if obj_type == "object":
            return {
                "status": "success",
                "message": f"Spawned {obj_name} at {location.name}:{cell_id}",
                "output": output,
                "location_id": location_id,
                "cell_id": cell_id,
                "object_type": "object",
                "object_char": obj_char,
                "object_name": obj_name,
            }
        else:  # sprite
            return {
                "status": "success",
                "message": f"Spawned sprite {obj_name} at {location.name}:{cell_id}",
                "output": output + "\n\nNote: Sprite can move and interact with environment",
                "location_id": location_id,
                "cell_id": cell_id,
                "object_type": "sprite",
                "object_char": obj_char,
                "object_name": obj_name,
                "note": "Sprite can move and interact with environment",
            }

"""GRAB command handler - Pick up and use objects."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.locations import load_locations


class GrabHandler(BaseCommandHandler):
    """Handler for GRAB command - pick up and use objects at locations."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle GRAB command.

        Args:
            command: Command name (GRAB)
            params: [object_label] or [action] [object_label]
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with status and interaction result
        """
        if not params:
            return {"status": "error", "message": "GRAB requires an object name"}

        # Get current location
        current_location_id = self.get_state("current_location") or "L300-BJ10"

        try:
            db = load_locations()
            location = db.get(current_location_id)
        except Exception as e:
            return {"status": "error", "message": f"Failed to load location: {str(e)}"}

        if not location:
            return {
                "status": "error",
                "message": f"Current location {current_location_id} not found",
            }

        object_name = " ".join(params).lower()

        # Search for object in location
        found_objects = []
        for cell_id, tile in location.tiles.items():
            for obj in tile.objects:
                if object_name in obj.label.lower():
                    found_objects.append(
                        {
                            "object": obj,
                            "label": obj.label,
                            "char": obj.char,
                            "cell": cell_id,
                        }
                    )

        if not found_objects:
            return {
                "status": "error",
                "message": f"No object matching '{object_name}' found at {location.name}",
                "available_objects": [
                    obj.label
                    for cell in location.tiles.values()
                    for obj in cell.objects
                ],
            }

        # Pick up first matching object
        grabbed = found_objects[0]

        # Get or create inventory
        inventory = self.get_state("inventory") or []

        # Add to inventory
        item_name = grabbed["label"]
        for item in inventory:
            if item["name"].lower() == item_name.lower():
                item["quantity"] = item.get("quantity", 1) + 1
                self.set_state("inventory", inventory)
                output = "\n".join(
                    [
                        OutputToolkit.banner("ITEM PICKED UP"),
                        OutputToolkit.table(
                            ["item", "cell", "qty"],
                            [[item_name, grabbed["cell"], item["quantity"]]],
                        ),
                    ]
                )
                return {
                    "status": "success",
                    "message": f"Picked up {item_name}",
                    "output": output,
                    "cell": grabbed["cell"],
                    "inventory_total": item["quantity"],
                }

        # New item
        inventory.append(
            {
                "name": item_name,
                "quantity": 1,
                "weight": 0.5,
                "equipped": False,
                "from_location": current_location_id,
            }
        )

        self.set_state("inventory", inventory)
        output = "\n".join(
            [
                OutputToolkit.banner("ITEM PICKED UP"),
                OutputToolkit.table(
                    ["item", "cell", "location"],
                    [[item_name, grabbed["cell"], location.name]],
                ),
            ]
        )
        return {
            "status": "success",
            "message": f"Picked up {item_name}",
            "output": output,
            "cell": grabbed["cell"],
            "location": location.name,
            "inventory_total": 1,
        }

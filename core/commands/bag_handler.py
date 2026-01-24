"""BAG command handler - Manage character inventory."""

from typing import List, Dict, Optional
from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit


class BagHandler(BaseCommandHandler):
    """Handler for BAG command - manage character inventory."""

    def __init__(self):
        """Initialize BAG handler with inventory state."""
        super().__init__()
        # State keys: items (list of dicts with name, quantity, weight)
        self.state = {"inventory": []}

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle BAG command.

        Args:
            command: Command name (BAG)
            params: [action] where action is: list, add, remove, drop, equip
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with inventory status and items
        """
        if not params:
            params = ["list"]  # Default action

        action = params[0].lower()

        if action == "list":
            return self._list_inventory()
        elif action == "add":
            return self._add_item(params[1:])
        elif action == "remove":
            return self._remove_item(params[1:])
        elif action == "drop":
            return self._drop_item(params[1:])
        elif action == "equip":
            return self._equip_item(params[1:])
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Try: list, add, remove, drop, equip",
            }

    def _list_inventory(self) -> Dict:
        """List all items in inventory."""
        inventory = self.get_state("inventory") or []

        if not inventory:
            output = "\n".join(
                [
                    OutputToolkit.banner("INVENTORY"),
                    "No items in bag.",
                ]
            )
            return {
                "status": "success",
                "message": "Your bag is empty",
                "output": output,
                "items": [],
                "total_items": 0,
                "total_weight": 0,
            }

        total_weight = sum(
            item.get("weight", 0) * item.get("quantity", 1) for item in inventory
        )

        items_display = []
        for item in inventory:
            items_display.append(
                {
                    "name": item["name"],
                    "quantity": item.get("quantity", 1),
                    "weight": item.get("weight", 0),
                    "equipped": item.get("equipped", False),
                }
            )

        rows = []
        for item in items_display:
            status = "equipped" if item.get("equipped") else ""
            rows.append(
                [
                    item.get("name", ""),
                    str(item.get("quantity", 1)),
                    str(item.get("weight", 0)),
                    status,
                ]
            )

        output = "\n".join(
            [
                OutputToolkit.banner("INVENTORY"),
                OutputToolkit.table(["item", "qty", "weight", "status"], rows),
                "",
                f"Total items: {sum(item.get('quantity', 1) for item in inventory)}",
                f"Total weight: {total_weight}",
                "Capacity: 100",
            ]
        )

        return {
            "status": "success",
            "message": "Inventory list",
            "output": output,
            "items": items_display,
            "total_items": sum(item.get("quantity", 1) for item in inventory),
            "total_weight": total_weight,
            "capacity": 100,  # Max weight capacity
        }

    def _add_item(self, params: List[str]) -> Dict:
        """Add item to inventory."""
        if not params:
            return {
                "status": "error",
                "message": "ADD requires item name (and optional quantity)",
            }

        item_name = " ".join(params).split()[0]
        quantity = 1

        # Check if quantity specified
        parts = " ".join(params).split()
        if parts[-1].isdigit():
            quantity = int(parts[-1])

        inventory = self.get_state("inventory") or []

        # Check if item already exists
        for item in inventory:
            if item["name"].lower() == item_name.lower():
                item["quantity"] = item.get("quantity", 1) + quantity
                self.set_state("inventory", inventory)
                return {
                    "status": "success",
                    "message": f"Added {quantity} {item_name}(s). Total: {item['quantity']}",
                }

        # Add new item
        inventory.append(
            {"name": item_name, "quantity": quantity, "weight": 1.0, "equipped": False}
        )

        self.set_state("inventory", inventory)
        return {
            "status": "success",
            "message": f"Added {quantity} {item_name} to your bag",
        }

    def _remove_item(self, params: List[str]) -> Dict:
        """Remove item from inventory."""
        if not params:
            return {
                "status": "error",
                "message": "REMOVE requires item name (and optional quantity)",
            }

        item_name = " ".join(params).split()[0]
        quantity = 1

        parts = " ".join(params).split()
        if parts[-1].isdigit():
            quantity = int(parts[-1])

        inventory = self.get_state("inventory") or []

        for item in inventory:
            if item["name"].lower() == item_name.lower():
                if item.get("quantity", 1) <= quantity:
                    inventory.remove(item)
                    msg = f"Removed {item_name} from your bag"
                else:
                    item["quantity"] -= quantity
                    msg = f"Removed {quantity} {item_name}(s). Remaining: {item['quantity']}"

                self.set_state("inventory", inventory)
                return {"status": "success", "message": msg}

        return {"status": "error", "message": f"Item '{item_name}' not found in bag"}

    def _drop_item(self, params: List[str]) -> Dict:
        """Drop item from inventory (removes it entirely)."""
        if not params:
            return {"status": "error", "message": "DROP requires item name"}

        item_name = " ".join(params)
        inventory = self.get_state("inventory") or []

        for item in inventory:
            if item["name"].lower() == item_name.lower():
                inventory.remove(item)
                self.set_state("inventory", inventory)
                return {"status": "success", "message": f"Dropped {item_name}"}

        return {"status": "error", "message": f"Item '{item_name}' not found"}

    def _equip_item(self, params: List[str]) -> Dict:
        """Equip an item."""
        if not params:
            return {"status": "error", "message": "EQUIP requires item name"}

        item_name = " ".join(params)
        inventory = self.get_state("inventory") or []

        for item in inventory:
            if item["name"].lower() == item_name.lower():
                item["equipped"] = not item.get("equipped", False)
                status = "equipped" if item["equipped"] else "unequipped"
                self.set_state("inventory", inventory)
                return {"status": "success", "message": f"{item_name} {status}"}

        return {"status": "error", "message": f"Item '{item_name}' not found"}

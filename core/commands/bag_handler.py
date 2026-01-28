"""BAG command handler - Manage character inventory."""

from typing import List, Dict, Optional
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin


class BagHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for BAG command - manage character inventory with logging."""

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
        with self.trace_command(command, params) as trace:
            if not params:
                params = ["list"]  # Default action

            action = params[0].lower()
            trace.add_event('action_determined', {'action': action})

            if action == "list":
                return self._list_inventory(trace)
            elif action == "add":
                return self._add_item(params[1:], trace)
            elif action == "remove":
                return self._remove_item(params[1:], trace)
            elif action == "drop":
                return self._drop_item(params[1:], trace)
            elif action == "equip":
                return self._equip_item(params[1:], trace)
            else:
                trace.set_status('error')
                self.log_param_error(command, params, f"Unknown action: {action}")
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}. Try: list, add, remove, drop, equip",
                }

    def _list_inventory(self, trace=None) -> Dict:
        """List all items in inventory."""
        from core.tui.output import OutputToolkit
        
        inventory = self.get_state("inventory") or []

        if not inventory:
            output = "\n".join(
                [
                    OutputToolkit.banner("INVENTORY"),
                    "No items in bag.",
                ]
            )
            if trace:
                trace.set_status('success')
                trace.add_event('empty_inventory', {'item_count': 0})
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

        if trace:
            trace.set_status('success')
            trace.add_event('inventory_listed', {
                'item_count': len(items_display),
                'total_weight': total_weight
            })

        return {
            "status": "success",
            "message": "Inventory list",
            "output": output,
            "items": items_display,
            "total_items": sum(item.get("quantity", 1) for item in inventory),
            "total_weight": total_weight,
            "capacity": 100,  # Max weight capacity
        }

    def _add_item(self, params: List[str], trace=None) -> Dict:
        """Add item to inventory."""
        if not params:
            if trace:
                trace.set_status('error')
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
                if trace:
                    trace.set_status('success')
                    trace.add_event('item_quantity_incremented', {
                        'item': item_name,
                        'quantity_added': quantity,
                        'total': item["quantity"]
                    })
                return {
                    "status": "success",
                    "message": f"Added {quantity} {item_name}(s). Total: {item['quantity']}",
                }

        # Add new item
        inventory.append(
            {"name": item_name, "quantity": quantity, "weight": 1.0, "equipped": False}
        )

        self.set_state("inventory", inventory)
        if trace:
            trace.set_status('success')
            trace.add_event('item_added', {
                'item': item_name,
                'quantity': quantity
            })
        return {
            "status": "success",
            "message": f"Added {quantity} {item_name} to your bag",
        }

    def _remove_item(self, params: List[str], trace=None) -> Dict:
        """Remove item from inventory."""
        if not params:
            if trace:
                trace.set_status('error')
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
                if trace:
                    trace.set_status('success')
                    trace.add_event('item_removed', {
                        'item': item_name,
                        'quantity': quantity
                    })
                return {"status": "success", "message": msg}

        if trace:
            trace.set_status('error')
        return {"status": "error", "message": f"Item '{item_name}' not found in bag"}

    def _drop_item(self, params: List[str], trace=None) -> Dict:
        """Drop item from inventory (removes it entirely)."""
        if not params:
            if trace:
                trace.set_status('error')
            return {"status": "error", "message": "DROP requires item name"}

        item_name = " ".join(params)
        inventory = self.get_state("inventory") or []

        for item in inventory:
            if item["name"].lower() == item_name.lower():
                inventory.remove(item)
                self.set_state("inventory", inventory)
                if trace:
                    trace.set_status('success')
                    trace.add_event('item_dropped', {'item': item_name})
                return {"status": "success", "message": f"Dropped {item_name}"}

        if trace:
            trace.set_status('error')
        return {"status": "error", "message": f"Item '{item_name}' not found"}

    def _equip_item(self, params: List[str], trace=None) -> Dict:
        """Equip an item."""
        if not params:
            if trace:
                trace.set_status('error')
            return {"status": "error", "message": "EQUIP requires item name"}

        item_name = " ".join(params)
        inventory = self.get_state("inventory") or []

        for item in inventory:
            if item["name"].lower() == item_name.lower():
                item["equipped"] = not item.get("equipped", False)
                status = "equipped" if item["equipped"] else "unequipped"
                self.set_state("inventory", inventory)
                if trace:
                    trace.set_status('success')
                    trace.add_event('item_toggled', {
                        'item': item_name,
                        'status': status
                    })
                return {"status": "success", "message": f"{item_name} {status}"}

        if trace:
            trace.set_status('error')
        return {"status": "error", "message": f"Item '{item_name}' not found"}

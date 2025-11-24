"""
Resource Command Handler for uDOS v1.0.18 - Apocalypse Adventures
Handles INVENTORY, TRADE, and BARTER commands.
"""

from typing import Dict, List, Optional
from extensions.game_mode.services.inventory_service import InventoryService, ItemCategory, ItemRarity
from extensions.game_mode.services.barter_service import BarterService


class ResourceCommandHandler:
    """Handler for resource/inventory commands"""

    def __init__(self, data_dir: str = "data"):
        """Initialize with inventory and barter services"""
        self.inventory_service = InventoryService(data_dir)
        self.barter_service = BarterService(data_dir, self.inventory_service)

    def handle_command(self, command: str, args: List[str]) -> Dict:
        """
        Route resource commands to appropriate handlers.

        Args:
            command: Command name (INVENTORY, TRADE, BARTER, etc.)
            args: Command arguments

        Returns:
            Dict with command results
        """
        command_upper = command.upper()

        if command_upper in ["INVENTORY", "INV", "I"]:
            return self.handle_inventory(args)
        elif command_upper == "TRADE":
            return self.handle_trade(args)
        elif command_upper == "BARTER":
            return self.handle_barter(args)
        elif command_upper == "ITEM":
            return self.handle_item(args)
        else:
            return {"type": "error", "message": f"Unknown resource command: {command}"}

    def handle_inventory(self, args: List[str]) -> Dict:
        """
        Handle INVENTORY command.

        Usage:
            INVENTORY - Show all items
            INVENTORY [category] - Show items in category
            INVENTORY STATS - Show inventory statistics
        """
        if not args:
            items = self.inventory_service.get_inventory()
            stats = self.inventory_service.get_inventory_stats()
            return {
                "type": "inventory_list",
                "items": items,
                "stats": stats,
                "total_items": len(items)
            }

        subcmd = args[0].lower()

        if subcmd == "stats":
            stats = self.inventory_service.get_inventory_stats()
            return {
                "type": "inventory_stats",
                "stats": stats
            }

        # Try to parse as category
        try:
            category = ItemCategory[subcmd.upper()]
            items = self.inventory_service.get_inventory(category=category)
            return {
                "type": "inventory_list",
                "category": category.value,
                "items": items,
                "total_items": len(items)
            }
        except KeyError:
            return {
                "type": "error",
                "message": f"Unknown category: {subcmd}. Valid categories: {', '.join([c.value for c in ItemCategory])}"
            }

    def handle_item(self, args: List[str]) -> Dict:
        """
        Handle ITEM command for detailed item info.

        Usage:
            ITEM [id] - Show item details
            ITEM ADD [name] [category] - Add item
            ITEM REMOVE [id] [quantity] - Remove item
            ITEM CONDITION [id] [delta] - Update item condition
        """
        if not args:
            return {"type": "error", "message": "Usage: ITEM [id] or ITEM ADD/REMOVE/CONDITION"}

        subcmd = args[0].lower()

        if subcmd == "add" and len(args) >= 3:
            name = args[1]
            try:
                category = ItemCategory[args[2].upper()]
            except KeyError:
                return {"type": "error", "message": f"Invalid category: {args[2]}"}

            # Parse optional parameters
            quantity = int(args[3]) if len(args) > 3 else 1
            weight = float(args[4]) if len(args) > 4 else 0.0
            volume = float(args[5]) if len(args) > 5 else 0.0

            result = self.inventory_service.add_item(
                name=name,
                category=category,
                quantity=quantity,
                weight=weight,
                volume=volume
            )

            return {
                "type": "item_added",
                "result": result
            }

        elif subcmd == "remove" and len(args) >= 2:
            item_id = int(args[1])
            quantity = int(args[2]) if len(args) > 2 else 1

            result = self.inventory_service.remove_item(item_id, quantity)
            return {
                "type": "item_removed",
                "result": result
            }

        elif subcmd == "condition" and len(args) >= 3:
            item_id = int(args[1])
            delta = int(args[2])

            result = self.inventory_service.update_condition(item_id, delta)
            return {
                "type": "condition_updated",
                "result": result
            }

        else:
            # Show item details
            try:
                item_id = int(args[0])
                item = self.inventory_service.get_item(item_id)

                if not item:
                    return {"type": "error", "message": f"Item {item_id} not found"}

                return {
                    "type": "item_details",
                    "item": item
                }
            except ValueError:
                return {"type": "error", "message": f"Invalid item ID: {args[0]}"}

    def handle_trade(self, args: List[str]) -> Dict:
        """
        Handle TRADE command.

        Usage:
            TRADE - Show trade history
            TRADE STATS - Show trade statistics
            TRADE WITH [partner] GIVE [item_ids] FOR [item_names] - Execute trade
        """
        if not args:
            history = self.barter_service.get_transaction_history()
            return {
                "type": "trade_history",
                "transactions": history,
                "total": len(history)
            }

        subcmd = args[0].lower()

        if subcmd == "stats":
            stats = self.barter_service.get_trade_stats()
            return {
                "type": "trade_stats",
                "stats": stats
            }

        elif subcmd == "with" and "give" in [a.lower() for a in args] and "for" in [a.lower() for a in args]:
            # Parse: TRADE WITH [partner] GIVE [ids] FOR [items]
            try:
                partner_idx = 1
                partner = args[partner_idx]

                give_idx = next(i for i, a in enumerate(args) if a.lower() == "give")
                for_idx = next(i for i, a in enumerate(args) if a.lower() == "for")

                # Item IDs to give
                given_ids = [int(x) for x in args[give_idx + 1:for_idx]]

                # Items to receive (simplified - just names)
                received_names = args[for_idx + 1:]

                # For demo, create simple item details
                received_items = []
                for name in received_names:
                    received_items.append({
                        "name": name,
                        "category": "misc",
                        "quantity": 1,
                        "weight": 0.5,
                        "volume": 0.5,
                        "condition": 80,
                        "rarity": "common",
                        "base_value": 10
                    })

                result = self.barter_service.execute_trade(
                    partner_name=partner,
                    items_given=given_ids,
                    items_received=received_items,
                    notes=f"Trade with {partner}"
                )

                return {
                    "type": "trade_executed",
                    "result": result
                }

            except (ValueError, StopIteration, IndexError) as e:
                return {
                    "type": "error",
                    "message": "Usage: TRADE WITH [partner] GIVE [item_ids] FOR [item_names]"
                }

        else:
            return {
                "type": "error",
                "message": "Usage: TRADE [STATS] or TRADE WITH [partner] GIVE [ids] FOR [items]"
            }

    def handle_barter(self, args: List[str]) -> Dict:
        """
        Handle BARTER command.

        Usage:
            BARTER - Show active pricing modifiers
            BARTER ACTIVATE [modifier] - Activate pricing modifier
            BARTER DEACTIVATE [modifier] - Deactivate pricing modifier
            BARTER VALUE [item_id] - Calculate item barter value
        """
        if not args:
            modifiers = self.barter_service.get_active_modifiers()
            return {
                "type": "barter_modifiers",
                "modifiers": modifiers,
                "total": len(modifiers)
            }

        subcmd = args[0].lower()

        if subcmd == "activate" and len(args) >= 2:
            modifier = " ".join(args[1:])
            result = self.barter_service.activate_modifier(modifier)
            return {
                "type": "modifier_activated",
                "result": result
            }

        elif subcmd == "deactivate" and len(args) >= 2:
            modifier = " ".join(args[1:])
            result = self.barter_service.deactivate_modifier(modifier)
            return {
                "type": "modifier_deactivated",
                "result": result
            }

        elif subcmd == "value" and len(args) >= 2:
            try:
                item_id = int(args[1])
                item = self.inventory_service.get_item(item_id)

                if not item:
                    return {"type": "error", "message": f"Item {item_id} not found"}

                base_value = self.barter_service.calculate_trade_value(item, apply_modifiers=False)
                current_value = self.barter_service.calculate_trade_value(item, apply_modifiers=True)

                return {
                    "type": "barter_value",
                    "item": item,
                    "base_value": base_value,
                    "current_value": current_value,
                    "modifier_effect": current_value - base_value
                }

            except ValueError:
                return {"type": "error", "message": f"Invalid item ID: {args[1]}"}

        else:
            return {
                "type": "error",
                "message": "Usage: BARTER [ACTIVATE/DEACTIVATE/VALUE]"
            }


# Helper functions for awarding XP on resource actions
def award_resource_xp(xp_handler, action: str, value: int = 10):
    """Award XP for resource management actions"""
    if hasattr(xp_handler, 'award_usage_xp'):
        xp_handler.award_usage_xp(value, f"Resource action: {action}")


def award_trade_xp(xp_handler, profit: int):
    """Award XP for successful trades (contribution category)"""
    if hasattr(xp_handler, 'award_contribution_xp'):
        # Award XP based on profit (1 XP per 10 value units)
        xp_amount = max(5, abs(profit) // 10)
        xp_handler.award_contribution_xp(xp_amount, f"Trade profit: {profit}")

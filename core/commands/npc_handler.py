"""
NPC Handler

Manages NPCs (Non-Player Characters) with location-based spawning,
state tracking, and movement between locations.
"""

from typing import Dict, List, Any, Optional
from .base import BaseCommandHandler


class NPCHandler(BaseCommandHandler):
    """Handle NPC management and spawning"""

    def __init__(self):
        """Initialize NPC handler"""
        super().__init__()
        self.npcs: Dict[str, Dict[str, Any]] = {}  # npc_id -> npc_data
        self._load_default_npcs()

    def _load_default_npcs(self):
        """Load default NPCs into memory"""
        # Merchant NPCs
        self.npcs["merchant-tokyo-1"] = {
            "id": "merchant-tokyo-1",
            "name": "Kenji",
            "role": "merchant",
            "location": "L300-BJ10",
            "disposition": "friendly",
            "dialogue_state": "greeting",
            "inventory": [
                {"name": "health_potion", "quantity": 5, "price": 10},
                {"name": "map_fragment", "quantity": 1, "price": 50},
            ],
            "dialogue_tree": "merchant_generic",
        }

        self.npcs["merchant-seoul-1"] = {
            "id": "merchant-seoul-1",
            "name": "Min-jun",
            "role": "merchant",
            "location": "L300-BQ10",
            "disposition": "friendly",
            "dialogue_state": "greeting",
            "inventory": [
                {"name": "stamina_boost", "quantity": 3, "price": 15},
                {"name": "compass", "quantity": 1, "price": 25},
            ],
            "dialogue_tree": "merchant_generic",
        }

        # Quest Giver NPCs
        self.npcs["quest-giver-1"] = {
            "id": "quest-giver-1",
            "name": "Elder Tanaka",
            "role": "quest_giver",
            "location": "L300-BJ10",
            "disposition": "wise",
            "dialogue_state": "quest_available",
            "quests": ["find_lost_item", "explore_underground"],
            "dialogue_tree": "elder_quests",
        }

        # Hostile NPCs
        self.npcs["hostile-1"] = {
            "id": "hostile-1",
            "name": "Rogue Agent",
            "role": "hostile",
            "location": "L300-BJ11",
            "disposition": "aggressive",
            "health": 50,
            "attack": 8,
            "defense": 5,
            "loot": [{"name": "rusty_key", "quantity": 1, "drop_chance": 0.7}],
            "dialogue_tree": "hostile_generic",
        }

    def handle(
        self, command: str, params: List[str], grid: Any, parser: Any
    ) -> Dict[str, Any]:
        """Route NPC commands"""
        if command == "NPC":
            return self._handle_npc_list(params)
        elif command == "SPAWN":
            return self._handle_spawn(params)
        else:
            return {"status": "error", "message": f"Unknown NPC command: {command}"}

    def _handle_npc_list(self, params: List[str]) -> Dict[str, Any]:
        """List NPCs at current or specified location"""
        if not params:
            return {"status": "error", "message": "Usage: NPC <location_id>"}

        location_id = params[0]
        npcs_at_location = [
            npc for npc in self.npcs.values() if npc["location"] == location_id
        ]

        if not npcs_at_location:
            return {
                "status": "success",
                "message": f"No NPCs found at {location_id}",
                "npcs": [],
            }

        return {
            "status": "success",
            "message": f"Found {len(npcs_at_location)} NPC(s) at {location_id}",
            "npcs": npcs_at_location,
            "location": location_id,
        }

    def _handle_spawn(self, params: List[str]) -> Dict[str, Any]:
        """Spawn new NPC at location"""
        if len(params) < 3:
            return {
                "status": "error",
                "message": "Usage: SPAWN <npc_type> <name> <location_id>",
                "suggestion": "Example: SPAWN merchant 'Trader Tom' L300-BJ10",
            }

        npc_type = params[0].lower()
        npc_name = params[1]
        location_id = params[2]

        # Generate unique ID
        npc_id = f"{npc_type}-{location_id}-{len(self.npcs) + 1}"

        # Create NPC based on type
        if npc_type == "merchant":
            npc_data = self._create_merchant(npc_id, npc_name, location_id)
        elif npc_type == "quest_giver":
            npc_data = self._create_quest_giver(npc_id, npc_name, location_id)
        elif npc_type == "hostile":
            npc_data = self._create_hostile(npc_id, npc_name, location_id)
        else:
            return {
                "status": "error",
                "message": f"Unknown NPC type: {npc_type}",
                "suggestion": "Valid types: merchant, quest_giver, hostile",
            }

        self.npcs[npc_id] = npc_data

        return {
            "status": "success",
            "message": f"Spawned {npc_type} '{npc_name}' at {location_id}",
            "npc": npc_data,
        }

    def _create_merchant(self, npc_id: str, name: str, location: str) -> Dict[str, Any]:
        """Create merchant NPC template"""
        return {
            "id": npc_id,
            "name": name,
            "role": "merchant",
            "location": location,
            "disposition": "friendly",
            "dialogue_state": "greeting",
            "inventory": [],
            "dialogue_tree": "merchant_generic",
        }

    def _create_quest_giver(
        self, npc_id: str, name: str, location: str
    ) -> Dict[str, Any]:
        """Create quest giver NPC template"""
        return {
            "id": npc_id,
            "name": name,
            "role": "quest_giver",
            "location": location,
            "disposition": "wise",
            "dialogue_state": "greeting",
            "quests": [],
            "dialogue_tree": "quest_giver_generic",
        }

    def _create_hostile(self, npc_id: str, name: str, location: str) -> Dict[str, Any]:
        """Create hostile NPC template"""
        return {
            "id": npc_id,
            "name": name,
            "role": "hostile",
            "location": location,
            "disposition": "aggressive",
            "health": 50,
            "attack": 8,
            "defense": 5,
            "loot": [],
            "dialogue_tree": "hostile_generic",
        }

    def get_npc_by_id(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC data by ID"""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Get all NPCs at specified location"""
        return [npc for npc in self.npcs.values() if npc["location"] == location_id]

    def move_npc(self, npc_id: str, new_location: str) -> bool:
        """Move NPC to new location"""
        if npc_id not in self.npcs:
            return False

        self.npcs[npc_id]["location"] = new_location
        return True

    def update_npc_state(self, npc_id: str, state_updates: Dict[str, Any]) -> bool:
        """Update NPC state (dialogue, disposition, etc.)"""
        if npc_id not in self.npcs:
            return False

        self.npcs[npc_id].update(state_updates)
        return True

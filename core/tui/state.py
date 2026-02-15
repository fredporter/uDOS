"""
Game State Manager

Tracks:
- Current location
- Inventory
- Discovered locations
- Player statistics
- Session history
"""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path

# Dynamic project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class GameState:
    """Central game state management"""

    def __init__(self):
        """Initialize game state"""
        self.current_location: str = "L300-BJ10"
        self.inventory: List[Dict[str, Any]] = []
        self.discovered_locations: List[str] = ["L300-BJ10"]
        self.player_id: str = "player1"
        self.player_stats: Dict[str, Any] = {
            "name": "Player",
            "level": 1,
            "health": 100,
            "hp": 100,
            "mana": 50,
            "xp": 0,
            "gold": 0,
        }
        self.session_history: List[str] = []
        self._saves_dir = PROJECT_ROOT / "memory" / "saved_games"

    def update_from_handler(self, handler_result: Dict[str, Any]) -> None:
        """
        Update game state based on handler result

        Args:
            handler_result: Dict returned from command handler
        """
        if handler_result.get("status") != "success":
            return

        # Update location if handler changed it
        if "location" in handler_result:
            self.current_location = handler_result["location"]

        # Update inventory if handler modified it
        if "inventory" in handler_result:
            self.inventory = handler_result["inventory"]

        # Update discovered locations
        if "location_id" in handler_result:
            loc_id = handler_result["location_id"]
            if loc_id not in self.discovered_locations:
                self.discovered_locations.append(loc_id)

        # Update player stats
        if "player_stats" in handler_result:
            self.player_stats.update(handler_result["player_stats"])

    def add_to_history(self, command: str) -> None:
        """Add command to session history"""
        self.session_history.append(command)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dict (for SAVE command)"""
        return {
            "current_location": self.current_location,
            "inventory": self.inventory,
            "discovered_locations": self.discovered_locations,
            "player_id": self.player_id,
            "player_stats": self.player_stats,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore state from dict (for LOAD command)"""
        self.current_location = data.get("current_location", "L300-BJ10")
        self.inventory = data.get("inventory", [])
        self.discovered_locations = data.get("discovered_locations", ["L300-BJ10"])
        self.player_id = data.get("player_id", "player1")
        self.player_stats.update(data.get("player_stats", {}))

    def save_to_file(self, slot: str = "quicksave") -> bool:
        """
        Save state to file

        Args:
            slot: Save slot name

        Returns:
            True if successful, False otherwise
        """
        try:
            self._saves_dir.mkdir(parents=True, exist_ok=True)
            save_file = self._saves_dir / f"{slot}.json"

            with open(save_file, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

            return True
        except Exception as e:
            print(f"Failed to save: {str(e)}")
            return False

    def load_from_file(self, slot: str = "quicksave") -> bool:
        """
        Load state from file

        Args:
            slot: Save slot name

        Returns:
            True if successful, False otherwise
        """
        try:
            save_file = self._saves_dir / f"{slot}.json"

            if not save_file.exists():
                return False

            with open(save_file, "r") as f:
                data = json.load(f)

            self.from_dict(data)
            return True
        except Exception as e:
            print(f"Failed to load: {str(e)}")
            return False

    def __repr__(self) -> str:
        return f"GameState(location={self.current_location}, inventory={len(self.inventory)}, level={self.player_stats['level']})"

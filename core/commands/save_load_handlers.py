"""SAVE/LOAD command handlers - Game state persistence."""

from typing import List, Dict
import json
from pathlib import Path
from core.commands.base import BaseCommandHandler


class SaveHandler(BaseCommandHandler):
    """Handler for SAVE command - save game state."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle SAVE command.

        Args:
            command: Command name (SAVE)
            params: [slot_name] (optional, defaults to 'quicksave')
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with save status
        """
        slot_name = params[0] if params else "quicksave"

        # Sanitize slot name
        slot_name = "".join(c for c in slot_name if c.isalnum() or c in "_-")

        save_dir = Path("/Users/fredbook/Code/uDOS/memory/saved_games")
        save_dir.mkdir(parents=True, exist_ok=True)

        save_file = save_dir / f"{slot_name}.json"

        try:
            # Get current game state from handlers
            game_state = {
                "slot": slot_name,
                "current_location": self.get_state("current_location") or "L300-BJ10",
                "inventory": self.get_state("inventory") or [],
                "discovered_locations": self.get_state("discovered_locations") or [],
                "player_stats": self.get_state("player_stats")
                or {"name": "Player", "level": 1, "health": 100, "max_health": 100},
            }

            # Write to file
            with open(save_file, "w") as f:
                json.dump(game_state, f, indent=2)

            return {
                "status": "success",
                "message": f"Game saved to slot '{slot_name}'",
                "slot": slot_name,
                "location": game_state["current_location"],
                "inventory_count": len(game_state["inventory"]),
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to save game: {str(e)}"}


class LoadHandler(BaseCommandHandler):
    """Handler for LOAD command - load saved game state."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle LOAD command.

        Args:
            command: Command name (LOAD)
            params: [slot_name] (optional, defaults to 'quicksave')
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with load status
        """
        slot_name = params[0] if params else "quicksave"

        # Sanitize slot name
        slot_name = "".join(c for c in slot_name if c.isalnum() or c in "_-")

        save_dir = Path("/Users/fredbook/Code/uDOS/memory/saved_games")
        save_file = save_dir / f"{slot_name}.json"

        if not save_file.exists():
            # List available saves
            available = []
            if save_dir.exists():
                available = [f.stem for f in save_dir.glob("*.json")]

            return {
                "status": "error",
                "message": f"Save file '{slot_name}' not found",
                "available_saves": available,
            }

        try:
            # Read save file
            with open(save_file, "r") as f:
                game_state = json.load(f)

            # Restore state
            self.set_state("current_location", game_state.get("current_location"))
            self.set_state("inventory", game_state.get("inventory", []))
            self.set_state(
                "discovered_locations", game_state.get("discovered_locations", [])
            )
            self.set_state("player_stats", game_state.get("player_stats"))

            return {
                "status": "success",
                "message": f"Game loaded from slot '{slot_name}'",
                "slot": slot_name,
                "location": game_state.get("current_location"),
                "inventory_count": len(game_state.get("inventory", [])),
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to load game: {str(e)}"}

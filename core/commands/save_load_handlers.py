"""SAVE/LOAD command handlers - Game state persistence."""

from typing import List, Dict
import json
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.tui.output import OutputToolkit

# Dynamic project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class SaveHandler(BaseCommandHandler, HandlerLoggingMixin):
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
        with self.trace_command(command, params) as trace:
            slot_name = params[0] if params else "quicksave"

            # Sanitize slot name
            slot_name = "".join(c for c in slot_name if c.isalnum() or c in "_-")
            trace.add_event('slot_determined', {'slot': slot_name})

            save_dir = PROJECT_ROOT / "memory" / "saved_games"
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
                trace.mark_milestone('state_collected')

                # Write to file
                with open(save_file, "w") as f:
                    json.dump(game_state, f, indent=2)
                trace.add_event('file_written', {'path': str(save_file)})

                output = "\n".join(
                    [
                        OutputToolkit.banner("SAVE GAME"),
                        OutputToolkit.table(
                            ["slot", "location", "inventory"],
                            [
                                [
                                    slot_name,
                                    game_state["current_location"],
                                    str(len(game_state["inventory"])),
                                ]
                            ],
                        ),
                    ]
                )
                trace.set_status('success')
                return {
                    "status": "success",
                    "message": f"Game saved to slot '{slot_name}'",
                    "output": output,
                    "slot": slot_name,
                    "location": game_state["current_location"],
                    "inventory_count": len(game_state["inventory"]),
                }
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'save_failed', {'error': str(e)})
                return {"status": "error", "message": f"Failed to save game: {str(e)}"}


class LoadHandler(BaseCommandHandler, HandlerLoggingMixin):
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
        with self.trace_command(command, params) as trace:
            slot_name = params[0] if params else "quicksave"

            # Sanitize slot name
            slot_name = "".join(c for c in slot_name if c.isalnum() or c in "_-")
            trace.add_event('slot_determined', {'slot': slot_name})

            save_dir = PROJECT_ROOT / "memory" / "saved_games"
            save_file = save_dir / f"{slot_name}.json"

            if not save_file.exists():
                # List available saves
                available = []
                if save_dir.exists():
                    available = [f.stem for f in save_dir.glob("*.json")]

                trace.set_status('error')
                self.log_operation(command, 'save_not_found', {
                    'slot': slot_name,
                    'available': len(available)
                })
                return {
                    "status": "error",
                    "message": f"Save file '{slot_name}' not found",
                    "available_saves": available,
                }

            try:
                # Read save file
                with open(save_file, "r") as f:
                    game_state = json.load(f)
                trace.add_event('file_loaded', {'path': str(save_file)})

                # Restore state
                self.set_state("current_location", game_state.get("current_location"))
                self.set_state("inventory", game_state.get("inventory", []))
                self.set_state(
                    "discovered_locations", game_state.get("discovered_locations", [])
                )
                self.set_state("player_stats", game_state.get("player_stats"))
                trace.mark_milestone('state_restored')

                output = "\n".join(
                    [
                        OutputToolkit.banner("LOAD GAME"),
                        OutputToolkit.table(
                            ["slot", "location", "inventory"],
                            [
                                [
                                    slot_name,
                                    game_state.get("current_location", ""),
                                    str(len(game_state.get("inventory", []))),
                                ]
                            ],
                        ),
                    ]
                )
                trace.set_status('success')
                return {
                    "status": "success",
                    "message": f"Game loaded from slot '{slot_name}'",
                    "output": output,
                    "slot": slot_name,
                    "location": game_state.get("current_location"),
                    "inventory_count": len(game_state.get("inventory", [])),
                }
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'load_failed', {'error': str(e)})
                return {"status": "error", "message": f"Failed to load game: {str(e)}"}

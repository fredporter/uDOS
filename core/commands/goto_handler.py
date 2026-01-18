"""
GOTO command handler - Navigate between locations.

Enables movement to adjacent locations via location ID or direction (north, south, etc).
Validates connections and updates game state.
"""

from typing import Dict, List, Optional
from core.commands.base import BaseCommandHandler
from core.locations import load_locations
from core.location_service import LocationService


class GotoHandler(BaseCommandHandler):
    """Navigate to another location."""

    def __init__(self):
        """Initialize goto handler."""
        super().__init__()
        self.location_service = LocationService()
        self.current_location = "L300-BJ10"  # Default starting location

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle GOTO command.

        Args:
            command: "GOTO"
            params: ["location_id"] or ["direction"] (north, south, east, west, up, down)
            grid: TUI grid for rendering
            parser: Command parser

        Returns:
            Dict with status and navigation result
        """
        if not params:
            return {
                "status": "error",
                "message": "GOTO requires location ID or direction (north, south, east, west, up, down)",
            }

        # Load locations
        try:
            db = load_locations()
            current = db.get(self.current_location)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load current location: {str(e)}",
            }

        if not current:
            return {
                "status": "error",
                "message": f"Current location {self.current_location} not found",
            }

        # Check if params[0] is direction
        target_param = params[0]  # Preserve case for location IDs
        direction_keywords = [
            "north",
            "south",
            "east",
            "west",
            "up",
            "down",
            "n",
            "s",
            "e",
            "w",
            "u",
            "d",
        ]

        if target_param.lower() in direction_keywords:
            # Expand short directions
            direction_map = {
                "n": "north",
                "s": "south",
                "e": "east",
                "w": "west",
                "u": "up",
                "d": "down",
            }
            target_dir = direction_map.get(target_param.lower(), target_param.lower())

            # Find connection in that direction
            target_id = self._find_connection_by_direction(current, target_dir)

            if not target_id:
                available = self._get_available_directions(current)
                return {
                    "status": "error",
                    "message": f"Cannot go {target_dir} from here.",
                    "available_directions": available,
                }
        else:
            # Treat as location ID
            target_id = target_param

        # Validate target exists
        try:
            target = db.get(target_id)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load target location: {str(e)}",
            }

        if not target:
            return {
                "status": "error",
                "message": f"Target location {target_id} not found",
            }

        # Check if target is reachable from current location
        if not self._is_connected(current, target_id):
            return {
                "status": "error",
                "message": f"Cannot reach {target.name} from {current.name}",
                "current_location": current.name,
                "target_location": target.name,
                "note": "Location is not directly connected. Use pathfinding for multi-step routes.",
            }

        # Update game state
        self.current_location = target_id

        return {
            "status": "success",
            "message": f"✓ Traveled to {target.name}",
            "location_id": target_id,
            "location_name": target.name,
            "region": target.region,
            "layer": target.layer,
            "timezone": target.timezone,
            "previous_location": self.current_location,
            "available_exits": self._get_available_directions(target),
        }

    def _find_connection_by_direction(self, location, direction: str) -> Optional[str]:
        """
        Find connection matching direction.

        Args:
            location: Location object
            direction: Direction name ('north', 'south', etc)

        Returns:
            Target location ID or None if not found
        """
        for conn in location.connections:
            if conn.direction.lower() == direction.lower():
                return conn.to
        return None

    def _get_available_directions(self, location) -> List[str]:
        """
        Get list of available directions from location.

        Args:
            location: Location object

        Returns:
            List of available direction names
        """
        directions = []
        for conn in location.connections:
            if conn.direction not in directions:
                directions.append(conn.direction)
        return sorted(directions)

    def _is_connected(self, location, target_id: str) -> bool:
        """
        Check if target location is directly connected.

        Args:
            location: Source location
            target_id: Target location ID

        Returns:
            True if directly connected, False otherwise
        """
        for conn in location.connections:
            if conn.to == target_id:
                return True
        return False

    def set_current_location(self, location_id: str) -> None:
        """Set the current location (for game state management)."""
        self.current_location = location_id

    def get_current_location(self) -> str:
        """Get the current location."""
        return self.current_location

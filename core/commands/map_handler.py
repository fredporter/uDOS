"""
uDOS v1.0.0 - Map Command Handler

Handles all map navigation commands:
- STATUS: Show current position and layer
- MOVE: Move relative to current position
- GOTO: Teleport to coordinates
- LAYER: Switch to different layer
- DESCEND: Go down one layer (NetHack >)
- ASCEND: Go up one layer (NetHack <)
- VIEW: Show ASCII map of current area
- LOCATE: Set location to a city

Version: 1.0.0
"""

from .base_handler import BaseCommandHandler


class MapCommandHandler(BaseCommandHandler):
    """Handles map navigation commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._map_engine = None

    @property
    def map_engine(self):
        """Lazy load map engine."""
        if self._map_engine is None:
            from core.uDOS_map import MapEngine
            self._map_engine = MapEngine()
        return self._map_engine

    def handle(self, command, params, grid):
        """
        Route map commands to appropriate handlers.

        Args:
            command: Command name
            params: Command parameters
            grid: Grid instance

        Returns:
            Command result message
        """
        if command == "STATUS":
            return self._handle_status()
        elif command == "MOVE":
            return self._handle_move(params)
        elif command == "GOTO":
            return self._handle_goto(params)
        elif command == "LAYER":
            return self._handle_layer(params)
        elif command == "DESCEND":
            return self._handle_descend()
        elif command == "ASCEND":
            return self._handle_ascend()
        elif command == "VIEW":
            return self._handle_view()
        elif command == "LOCATE":
            return self._handle_locate(params)
        else:
            return self.get_message("ERROR_UNKNOWN_MAP_COMMAND", command=command)

    def _handle_status(self):
        """Show current position and layer."""
        pos = self.map_engine.position
        layer = self.map_engine.current_layer
        return f"🗺️  Position: ({pos[0]}, {pos[1]})  |  Layer: {layer}"

    def _handle_move(self, params):
        """Move relative to current position."""
        if len(params) < 2:
            return "❌ Usage: MOVE <dx> <dy>\n\nExample: MOVE 1 0 (move east)"

        try:
            dx = int(params[0])
            dy = int(params[1])
            self.map_engine.move(dx, dy)
            self._save_map_position()
            return self._handle_status()
        except ValueError:
            return "❌ Invalid coordinates (must be integers)"

    def _handle_goto(self, params):
        """Teleport to coordinates."""
        if len(params) < 2:
            return "❌ Usage: GOTO <x> <y>\n\nExample: GOTO 10 5"

        try:
            x = int(params[0])
            y = int(params[1])
            self.map_engine.set_position(x, y)
            self._save_map_position()
            return f"✅ Teleported to ({x}, {y})"
        except ValueError:
            return "❌ Invalid coordinates (must be integers)"

    def _handle_layer(self, params):
        """Switch to different layer."""
        if not params:
            layers = self.map_engine.get_available_layers()
            result = "🗺️  Available Layers:\n\n"
            for layer in layers:
                current = "→ " if layer == self.map_engine.current_layer else "  "
                result += f"{current}{layer}\n"
            result += "\n💡 Use: LAYER <name> to switch"
            return result

        layer_name = params[0]
        try:
            self.map_engine.set_layer(layer_name)
            return f"✅ Switched to layer: {layer_name}"
        except ValueError as e:
            return f"❌ {str(e)}"

    def _handle_descend(self):
        """Go down one layer (NetHack >)."""
        try:
            self.map_engine.descend()
            return f"⬇️  Descended to: {self.map_engine.current_layer}"
        except ValueError as e:
            return f"❌ {str(e)}"

    def _handle_ascend(self):
        """Go up one layer (NetHack <)."""
        try:
            self.map_engine.ascend()
            return f"⬆️  Ascended to: {self.map_engine.current_layer}"
        except ValueError as e:
            return f"❌ {str(e)}"

    def _handle_view(self):
        """Show ASCII map of current area."""
        try:
            map_view = self.map_engine.render_map(width=40, height=20)
            result = f"🗺️  MAP VIEW - {self.map_engine.current_layer}\n"
            result += "="*60 + "\n\n"
            result += map_view + "\n\n"
            result += "="*60 + "\n"
            result += self._handle_status()
            return result
        except Exception as e:
            return f"❌ Map rendering error: {str(e)}"

    def _handle_locate(self, params):
        """Set location to a city."""
        if not params:
            return ("❌ Usage: LOCATE <city>\n\n"
                   "Example: LOCATE Vancouver\n\n"
                   "💡 This sets your real-world location for map positioning")

        city = ' '.join(params)

        try:
            # Update user profile with city
            if self.user_manager:
                self.user_manager.set_world_location(city)
                self.map_engine.set_real_world_location(city)
                return (f"✅ Location set to: {city}\n\n"
                       f"Map position has been updated based on your location")
            else:
                return "⚠️  User manager not available - location not saved"
        except Exception as e:
            return f"❌ Error setting location: {str(e)}"

    def _save_map_position(self):
        """Save current map position to user profile."""
        if not self.user_manager:
            return

        try:
            pos = self.map_engine.position
            layer = self.map_engine.current_layer

            self.user_manager.set_map_position(pos[0], pos[1], layer)
        except Exception:
            pass  # Silently fail - not critical

"""TELL command handler - Show rich location descriptions."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.locations import load_locations
from core.tui.output import OutputToolkit


class TellHandler(BaseCommandHandler):
    """Handler for TELL command - display rich location descriptions."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle TELL command.

        Args:
            command: Command name (TELL)
            params: [location_id] or empty for current location
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with status, location_id, name, full description
        """
        # Get location ID
        location_id = (
            params[0] if params else self.get_state("current_location") or "L300-BJ10"
        )

        try:
            db = load_locations()
            location = db.get(location_id)
        except Exception as e:
            return {"status": "error", "message": f"Failed to load location: {str(e)}"}

        if not location:
            return {"status": "error", "message": f"Location {location_id} not found"}

        # Build rich description
        description_lines = [OutputToolkit.banner("LOCATION DETAIL")]
        description_lines.append(f"Name: {location.name}")

        # Add type and region info
        description_lines.append(
            f"Type: {location.type.title()} in {location.region.replace('_', ' ').title()}"
        )

        # Add layer info
        layer_name = (
            "Terrestrial" if location.layer == 300 else f"Layer {location.layer}"
        )
        description_lines.append(f"Layer: {layer_name} | Continent: {location.continent}")
        description_lines.append("")

        # Add description with word wrapping
        description = location.description
        while description:
            line = description[:75]
            # Try to break at word boundary
            if len(description) > 75:
                last_space = line.rfind(" ")
                if last_space > 50:
                    line = description[:last_space]
                    description = description[last_space:].lstrip()
                else:
                    description = description[75:]
            else:
                description = ""

            description_lines.append(f"{line}")
        description_lines.append("")

        # Add coordinates
        description_lines.append(
            f"Coordinates: {location.coordinates.lat:.4f}{'N' if location.coordinates.lat >= 0 else 'S'}, "
            f"{location.coordinates.lon:.4f}{'E' if location.coordinates.lon >= 0 else 'W'}"
        )

        # Add timezone
        description_lines.append(f"Timezone: {location.timezone}")

        # Add connections summary
        if location.connections:
            conn_text = f"Connected to: {len(location.connections)} locations"
            description_lines.append(conn_text)

        return {
            "status": "success",
            "location_id": location_id,
            "location_name": location.name,
            "description": "\n".join(description_lines),
            "output": "\n".join(description_lines),
            "full_text": location.description,
        }

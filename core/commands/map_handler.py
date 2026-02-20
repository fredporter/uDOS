"""
MAP command handler - Display location tile grid.

Renders a location's tile grid with objects, sprites, and markers using
ASCII/teletext graphics. Supports viewing current location or any location by ID.

Includes instrumentation via HandlerLoggingMixin for performance tracking.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseCommandHandler
from .handler_logging_mixin import HandlerLoggingMixin
from core.locations import load_locations, Location
from core.services.error_contract import CommandError
from core.services.map_renderer import MapRenderer


class MapHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Display location tile grid with automatic logging."""

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle MAP command.

        Args:
            command: "MAP"
            params: [location_id] or empty for current location
            grid: TUI grid for rendering
            parser: Command parser

        Returns:
            Dict with status, location info, and rendered grid
        """
        with self.trace_command(command, params) as trace:
            # Get location ID (from params or player state)
            if params:
                location_id = params[0]
            else:
                # Default to first location if no current location set
                location_id = "L300-BJ10"

            trace.mark_milestone('location_id_determined')

            # Load location
            try:
                db = load_locations()
                location = db.get(location_id)
                trace.add_event('location_loaded', {'location_id': location_id})
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'location_load_failed', {
                    'location_id': location_id,
                    'error': str(e)
                })
                raise CommandError(
                    code="ERR_LOCATION_LOAD_FAILED",
                    message=f"Failed to load locations: {str(e)}",
                    recovery_hint="Run VERIFY to check location data integrity",
                    level="WARNING",
                )

            if not location:
                trace.set_status('error')
                self.log_operation(command, 'location_not_found', {
                    'location_id': location_id
                })
                raise CommandError(
                    code="ERR_LOCATION_NOT_FOUND",
                    message=f"Location {location_id} not found",
                    recovery_hint="Use FIND to search for available locations",
                    level="INFO",
                )

            trace.mark_milestone('location_validated')

            # Render grid
            try:
                grid_display = self._render_grid(location)
                trace.add_event('grid_rendered', {
                    'location_id': location.id,
                    'location_name': location.name,
                    'grid_size': len(grid_display)
                })
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'grid_render_failed', {
                    'location_id': location_id,
                    'error': str(e)
                })
                raise CommandError(
                    code="ERR_RENDER_FAILED",
                    message=f"Failed to render grid: {str(e)}",
                    recovery_hint="Try MAP again or run HEALTH for renderer diagnostics",
                    level="ERROR",
                )

            # Import OutputToolkit only when needed (avoid circular import)
            from core.tui.output import OutputToolkit

            renderer = MapRenderer()
            cols = renderer.cols
            rows = renderer.rows
            output = "\n".join(
                [
                    OutputToolkit.banner(f"MAP {location.id}"),
                    grid_display,
                ]
            )

            trace.mark_milestone('output_formatted')
            trace.set_status('success')
            trace.add_event('command_complete', {
                'location_id': location.id,
                'region': location.region,
                'layer': location.layer,
                'viewport': f'{cols}x{rows}'
            })

            return {
                "status": "success",
                "message": f"Map for {location.name}",
                "output": output,
                "location_id": location.id,
                "location_name": location.name,
                "region": location.region,
                "layer": location.layer,
                "timezone": location.timezone,
                "grid": grid_display,
                "width": cols,
                "height": rows,
            }

    def _render_grid(self, location: Location) -> str:
        renderer = MapRenderer()
        return renderer.render(location)

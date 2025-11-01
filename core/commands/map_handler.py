"""
uDOS v1.0.3 - Enhanced Map Command Handler

Handles all map navigation commands with integrated cell reference system:
- STATUS: Show current position and layer
- VIEW: Show ASCII map of current area
- CELL: Get information about a specific cell
- CITIES: List cities in region or globally
- NAVIGATE: Get navigation info between locations
- LOCATE: Set location to a city or cell
- LAYERS: Show accessible layers
- GOTO: Move to specific coordinates or cell

Version: 1.0.3
"""

from .base_handler import BaseCommandHandler
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class MapCommandHandler(BaseCommandHandler):
    """Enhanced map navigation commands with cell reference system."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._integrated_map = None
        self._teletext_integration = None

    @property
    def integrated_map(self):
        """Lazy load integrated mapping engine."""
        if self._integrated_map is None:
            from core.services.integrated_map_engine import IntegratedMapEngine
            self._integrated_map = IntegratedMapEngine()
        return self._integrated_map

    @property
    def teletext_integration(self):
        """Lazy load teletext integration."""
        if self._teletext_integration is None:
            from core.services.teletext_renderer import TeletextMapIntegration
            self._teletext_integration = TeletextMapIntegration()
        return self._teletext_integration

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
        try:
            if command == "STATUS":
                return self._handle_status(params)
            elif command == "VIEW":
                return self._handle_view(params)
            elif command == "CELL":
                return self._handle_cell(params)
            elif command == "CITIES":
                return self._handle_cities(params)
            elif command == "NAVIGATE":
                return self._handle_navigate(params)
            elif command == "LOCATE":
                return self._handle_locate(params)
            elif command == "LAYERS":
                return self._handle_layers(params)
            elif command == "GOTO":
                return self._handle_goto(params)
            elif command == "TELETEXT":
                return self._handle_teletext(params)
            elif command == "WEB":
                return self._handle_web(params)
            else:
                return f"Unknown map command: {command}"
        except Exception as e:
            return f"Map command error: {str(e)}"

    def _handle_status(self, params):
        """Show current map position and status."""
        # Get current location from user config
        try:
            import json
            config_file = Path("sandbox/user.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "UTC")

                if tizo_code in self.integrated_map.city_cells:
                    city_data = self.integrated_map.city_cells[tizo_code]
                    cell_ref = city_data["cell_ref"]

                    return f"""🗺️  Map Status
{'='*30}
Current Location: {city_data['name']}, {city_data['country']}
TIZO Code: {tizo_code}
Cell Reference: {cell_ref}
Coordinates: {city_data['coordinates']['lat']:.2f}°, {city_data['coordinates']['lon']:.2f}°
Timezone: {city_data['timezone']} ({city_data['timezone_offset']})
Accessible Layers: {', '.join(city_data['udos_layers'])}

Use 'MAP VIEW' to see the area around you."""
                else:
                    return f"Current location: {tizo_code} (location data not found)"
            else:
                return "No user configuration found. Run setup first."
        except Exception as e:
            return f"Error reading location: {str(e)}"

    def _handle_view(self, params):
        """Show ASCII map view."""
        # Get current location
        try:
            import json
            config_file = Path("sandbox/user.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "MEL")

                if tizo_code in self.integrated_map.city_cells:
                    city_data = self.integrated_map.city_cells[tizo_code]
                    cell_ref = city_data["cell_ref"]

                    # Parse parameters for view size
                    width = 40
                    height = 20
                    if params:
                        parts = params.strip().split()
                        if len(parts) >= 1 and parts[0].isdigit():
                            width = int(parts[0])
                        if len(parts) >= 2 and parts[1].isdigit():
                            height = int(parts[1])

                    ascii_map = self.integrated_map.generate_ascii_map(cell_ref, width, height)
                    return ascii_map
                else:
                    return f"Cannot generate view for location: {tizo_code}"
            else:
                return "No user configuration found."
        except Exception as e:
            return f"Error generating view: {str(e)}"

    def _handle_cell(self, params):
        """Get information about a specific cell."""
        if not params:
            return "Usage: MAP CELL <cell_reference> (e.g., MAP CELL JN196)"

        cell_ref = params.strip().upper()

        try:
            # Get cell bounds and center
            bounds = self.integrated_map.cell_system.get_cell_bounds(cell_ref)

            # Check for cities in this cell
            city = self.integrated_map.get_city_by_cell(cell_ref)

            result = f"""📍 Cell Information: {cell_ref}
{'='*30}
Center Coordinates: {bounds['lat_center']:.2f}°, {bounds['lon_center']:.2f}°
Bounds: {bounds['lat_min']:.2f}° to {bounds['lat_max']:.2f}° (lat)
        {bounds['lon_min']:.2f}° to {bounds['lon_max']:.2f}° (lon)"""

            if city:
                result += f"""

🏙️  City in this cell:
Name: {city['name']}, {city['country']}
TIZO Code: {city['tizo_code']}
Timezone: {city['timezone']} ({city['timezone_offset']})
Population: {city['population_code']}
Connection Quality: {city['connection_quality']}"""
            else:
                result += "\n\n🌊 No major cities in this cell"

            return result

        except ValueError as e:
            return f"Invalid cell reference: {cell_ref}"

    def _handle_cities(self, params):
        """List cities in region or globally."""
        if not params:
            # Show all TIZO cities
            cities = []
            for tizo_code, city_data in self.integrated_map.city_cells.items():
                cities.append(f"{tizo_code}: {city_data['name']}, {city_data['country']} ({city_data['cell_ref']})")

            cities.sort()
            result = f"🏙️  TIZO Cities ({len(cities)} total):\n"
            result += "\n".join(cities)
            return result
        else:
            # Show cities in region around specified cell
            parts = params.strip().split()
            center_cell = parts[0].upper()
            radius = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10

            try:
                cities = self.integrated_map.get_cities_in_region(center_cell, radius)

                if cities:
                    result = f"🏙️  Cities within {radius} cells of {center_cell}:\n"
                    for city in cities:
                        result += f"{city['tizo_code']}: {city['name']}, {city['country']} ({city['cell_ref']}) - {city['cell_distance']} cells\n"
                    return result.strip()
                else:
                    return f"No cities found within {radius} cells of {center_cell}"
            except ValueError:
                return f"Invalid cell reference: {center_cell}"

    def _handle_navigate(self, params):
        """Get navigation information between locations."""
        if not params:
            return "Usage: MAP NAVIGATE <from> <to> (e.g., MAP NAVIGATE MEL SYD or MAP NAVIGATE JN196 JV189)"

        parts = params.strip().split()
        if len(parts) < 2:
            return "Usage: MAP NAVIGATE <from> <to>"

        from_loc = parts[0].upper()
        to_loc = parts[1].upper()

        # Convert TIZO codes to cell references if needed
        from_cell = from_loc
        to_cell = to_loc

        if from_loc in self.integrated_map.city_cells:
            from_cell = self.integrated_map.city_cells[from_loc]["cell_ref"]
            from_name = f"{self.integrated_map.city_cells[from_loc]['name']} ({from_loc})"
        else:
            from_name = from_cell

        if to_loc in self.integrated_map.city_cells:
            to_cell = self.integrated_map.city_cells[to_loc]["cell_ref"]
            to_name = f"{self.integrated_map.city_cells[to_loc]['name']} ({to_loc})"
        else:
            to_name = to_cell

        nav_info = self.integrated_map.get_navigation_info(from_cell, to_cell)

        if "error" in nav_info:
            return f"Navigation error: {nav_info['error']}"

        return f"""🧭 Navigation: {from_name} → {to_name}
{'='*40}
From Cell: {nav_info['current_cell']}
To Cell: {nav_info['target_cell']}
Distance: {nav_info['distance_km']} km
Cell Distance: {nav_info['cell_distance']} cells
Bearing: {nav_info['bearing']}° ({nav_info['direction']})"""

    def _handle_locate(self, params):
        """Set location to a city or cell."""
        if not params:
            return "Usage: MAP LOCATE <tizo_code> or MAP LOCATE <cell_reference>"

        location = params.strip().upper()

        # Try as TIZO code first
        if location in self.integrated_map.city_cells:
            city_data = self.integrated_map.city_cells[location]
            return f"📍 Location set to {city_data['name']}, {city_data['country']} ({location})\nCell: {city_data['cell_ref']}"

        # Try as cell reference
        try:
            city = self.integrated_map.get_city_by_cell(location)
            if city:
                return f"📍 Location set to {city['name']}, {city['country']} ({city['tizo_code']})\nCell: {location}"
            else:
                lat, lon = self.integrated_map.cell_system.cell_to_coord(location)
                return f"📍 Location set to cell {location}\nCoordinates: {lat:.2f}°, {lon:.2f}°"
        except ValueError:
            return f"Invalid location: {location}\nUse TIZO code (e.g., MEL) or cell reference (e.g., JN196)"

    def _handle_layers(self, params):
        """Show accessible layers."""
        try:
            import json
            config_file = Path("sandbox/user.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "UTC")

                layers = self.integrated_map.get_layer_access(tizo_code)

                result = f"🌍 Accessible Layers from {tizo_code}:\n"
                for layer in layers:
                    result += f"  {layer}\n"

                world_nav = config.get("world_navigation", {})
                connection_quality = world_nav.get("connection_quality", {})

                if connection_quality:
                    result += "\n🌐 Connection Quality:\n"
                    for region, quality in connection_quality.items():
                        result += f"  {region.title()}: {quality}\n"

                return result.strip()
            else:
                return "No user configuration found."
        except Exception as e:
            return f"Error reading layer information: {str(e)}"

    def _handle_goto(self, params):
        """Move to specific coordinates or cell."""
        if not params:
            return "Usage: MAP GOTO <cell_reference> or MAP GOTO <lat> <lon>"

        parts = params.strip().split()

        if len(parts) == 1:
            # Cell reference
            cell_ref = parts[0].upper()
            try:
                lat, lon = self.integrated_map.cell_system.cell_to_coord(cell_ref)
                city = self.integrated_map.get_city_by_cell(cell_ref)

                result = f"🎯 Moving to cell {cell_ref}\n"
                result += f"Coordinates: {lat:.2f}°, {lon:.2f}°\n"

                if city:
                    result += f"Location: {city['name']}, {city['country']} ({city['tizo_code']})"
                else:
                    result += "Location: Open area (no major city)"

                return result
            except ValueError:
                return f"Invalid cell reference: {cell_ref}"

        elif len(parts) == 2:
            # Lat/lon coordinates
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                cell_ref = self.integrated_map.cell_system.coord_to_cell(lat, lon)

                result = f"🎯 Moving to coordinates {lat}°, {lon}°\n"
                result += f"Cell: {cell_ref}\n"

                city = self.integrated_map.get_city_by_cell(cell_ref)
                if city:
                    result += f"Nearest city: {city['name']}, {city['country']} ({city['tizo_code']})"
                else:
                    result += "No major city in this area"

                return result
            except ValueError:
                return "Invalid coordinates. Use decimal degrees (e.g., MAP GOTO -37.81 144.96)"

        else:
            return "Usage: MAP GOTO <cell_reference> or MAP GOTO <lat> <lon>"

    def _handle_teletext(self, params):
        """Generate teletext-style map output."""
        # Get current location
        try:
            import json
            config_file = Path("sandbox/user.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "MEL")

                if tizo_code in self.integrated_map.city_cells:
                    city_data = self.integrated_map.city_cells[tizo_code]
                    cell_ref = city_data["cell_ref"]

                    # Parse parameters for map size
                    width = 40
                    height = 20
                    if params:
                        parts = params.strip().split()
                        if len(parts) >= 1 and parts[0].isdigit():
                            width = int(parts[0])
                        if len(parts) >= 2 and parts[1].isdigit():
                            height = int(parts[1])

                    # Generate teletext HTML
                    html_content = self.teletext_integration.render_map_as_teletext(
                        self.integrated_map, cell_ref, width, height
                    )

                    # Save to file
                    filepath = self.teletext_integration.save_teletext_map(html_content)

                    return f"""🖥️  Teletext Map Generated
{'='*35}
Location: {city_data['name']}, {city_data['country']}
Cell: {cell_ref}
Size: {width}×{height} characters
Style: Mosaic block art

📄 File saved: {filepath}
🌐 Open in web browser to view
💡 Use MAP WEB to start local server"""
                else:
                    return f"Cannot generate teletext map for location: {tizo_code}"
            else:
                return "No user configuration found."
        except Exception as e:
            return f"Error generating teletext map: {str(e)}"

    def _handle_web(self, params):
        """Start web server for teletext maps or open latest map."""
        try:
            from pathlib import Path
            import webbrowser
            import os

            teletext_dir = Path("output/teletext")

            if not teletext_dir.exists():
                return "No teletext maps found. Use MAP TELETEXT first."

            # Find most recent teletext map
            html_files = list(teletext_dir.glob("*.html"))
            if not html_files:
                return "No teletext maps found. Use MAP TELETEXT first."

            # Get the most recent file
            latest_file = max(html_files, key=os.path.getctime)

            if params and params.strip().lower() == "server":
                # Start local HTTP server
                return self._start_teletext_server()
            else:
                # Open file directly in browser
                file_url = f"file://{latest_file.absolute()}"
                try:
                    webbrowser.open(file_url)
                    return f"""🌐 Teletext Map Opened
{'='*25}
File: {latest_file.name}
URL: {file_url}

💡 Map should open in your default browser
🖥️  Use MAP WEB SERVER for local HTTP server"""
                except Exception as e:
                    return f"Could not open browser: {str(e)}\nFile location: {latest_file}"

        except Exception as e:
            return f"Error opening teletext map: {str(e)}"

    def _start_teletext_server(self):
        """Start a local HTTP server for teletext maps."""
        try:
            import http.server
            import socketserver
            import threading
            import time
            from pathlib import Path
            import webbrowser

            # Change to teletext directory
            teletext_dir = Path("output/teletext").absolute()
            if not teletext_dir.exists():
                return "No teletext directory found. Use MAP TELETEXT first."

            os.chdir(teletext_dir)

            # Find available port
            port = 8080
            for test_port in range(8080, 8090):
                try:
                    with socketserver.TCPServer(("", test_port), http.server.SimpleHTTPRequestHandler) as httpd:
                        port = test_port
                        break
                except OSError:
                    continue

            # Start server in background
            def serve():
                with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                    httpd.serve_forever()

            server_thread = threading.Thread(target=serve, daemon=True)
            server_thread.start()

            # Give server time to start
            time.sleep(1)

            # Open browser
            server_url = f"http://localhost:{port}"
            webbrowser.open(server_url)

            return f"""🚀 Teletext Web Server Started
{'='*30}
Server URL: {server_url}
Port: {port}
Directory: {teletext_dir}

🌐 Browser should open automatically
📁 All teletext maps available at server root
🛑 Press Ctrl+C in terminal to stop server"""

        except Exception as e:
            return f"Error starting web server: {str(e)}"

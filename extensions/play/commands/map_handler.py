"""
uDOS v1.0.3 - Map Command Handler

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

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.commands.base_handler import BaseCommandHandler


class MapCommandHandler(BaseCommandHandler):
    """Map navigation commands with cell reference system."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._map_engine = None
        self._teletext_integration = None
        self._map_renderer = None

    @property
    def map_engine(self):
        """Lazy load mapping engine."""
        if self._map_engine is None:
            from extensions.play.services.map_engine import MapEngine
            self._map_engine = MapEngine()
        return self._map_engine

    @property
    def teletext_integration(self):
        """Lazy load teletext integration."""
        if self._teletext_integration is None:
            from core.output.teletext_renderer import TeletextMapIntegration
            self._teletext_integration = TeletextMapIntegration()
        return self._teletext_integration

    @property
    def map_renderer(self):
        """Lazy load ASCII map renderer (v2.0.0 TILE system)."""
        if self._map_renderer is None:
            from core.ui.map_renderer import MapRenderer
            self._map_renderer = MapRenderer()
        return self._map_renderer

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
            elif command == "WORLD":
                return self._handle_world(params)
            elif command == "SEARCH":
                return self._handle_search(params)
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
        # Get current planet from planet manager
        try:
            from core.services.planet_manager import PlanetManager
            pm = PlanetManager()
            current_planet = pm.get_current_planet()
            current_galaxy = pm.get_current_galaxy()
            planet_icon = pm.get_planet_icon(current_planet)
            galaxy_icon = pm.get_galaxy_icon(current_galaxy)

            # Build status header with planet info
            result = f"""🗺️  Map Status
{'='*40}
Planet: {planet_icon} {current_planet}
Galaxy: {galaxy_icon} {current_galaxy}"""

            # Add location info from user.json (TILE code)
            from core.config import get_config
            config = get_config()
            location = config.get_user('USER_PROFILE.LOCATION')
            if location:
                result += f"""
📍 Location: {location}"""
                result += f"""
   Coordinates: {location.latitude:.2f}°, {location.longitude:.2f}°"""

                # Try to find nearest city from map engine
                try:
                    nearest_city = self._find_nearest_city(location.latitude, location.longitude)
                    if nearest_city:
                        result += f"""
   Nearest City: {nearest_city['name']} ({nearest_city['tizo_code']})
   Cell Reference: {nearest_city['cell_ref']}"""
                except:
                    pass
            else:
                result += f"""
📍 Location: Not set (use LOCATE to set your position)"""

            # Add map commands help
            result += f"""

Available Commands:
  MAP VIEW - Show ASCII map around your location
  LOCATE CITY <name> - Set location to a major city
  LOCATE SET <lat> <lon> - Set custom coordinates
  CONFIG GET planet - View current planet (stored in user.json)"""

            return result

        except Exception as e:
            # Fallback to legacy behavior if planet system not available
            import json
            config_file = Path("memory/bank/user/user.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "UTC")

                if tizo_code in self.map_engine.city_cells:
                    city_data = self.map_engine.city_cells[tizo_code]
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
                return f"Error reading planet data: {str(e)}"

    def _handle_view(self, params):
        """Show ASCII map view using v2.0.0 TILE renderer."""
        # Get current location from planet system
        try:
            from core.services.planet_manager import PlanetManager
            from core.utils.grid_utils import latlong_to_tile

            pm = PlanetManager()
            current_planet = pm.get_current()

            if not current_planet:
                return "⚠️  No planet selected. Set 'planet' field in user.json (memory/bank/user/user.json)."

            # Only show map for Earth
            if current_planet.planet_type != "Earth":
                return f"""🗺️  Map View Not Available
{'='*40}
Planet: {current_planet.icon} {current_planet.name}
Type: {current_planet.planet_type}

📍 World maps are only available for Earth-type planets.
   Use LOCATE to set your position on Earth."""

            location = pm.get_location(current_planet.name)
            if not location:
                return f"""🗺️  Map View
{'='*40}
Planet: {current_planet.icon} {current_planet.name}

⚠️  No location set. Use LOCATE to set your position:
   • LOCATE CITY <name> - Select from major cities
   • LOCATE SET <lat> <lon> - Set custom coordinates"""

            # Parse parameters for view size
            width = 60
            height = 20
            layer = 100  # Default layer
            if params:
                parts = params.strip().split()
                for part in parts:
                    if part.upper().startswith('LAYER='):
                        layer = int(part.split('=')[1])
                    elif part.isdigit():
                        if width == 60:  # First number is width
                            width = int(part)
                        else:  # Second number is height
                            height = int(part)

            # Convert location to TILE code
            tile_code = latlong_to_tile(location.latitude, location.longitude, layer=layer)

            # Generate ASCII map using new renderer
            ascii_map = self.map_renderer.render_map(
                center_tile=tile_code,
                width=width,
                height=height,
                show_grid=True,
                show_labels=True,
                show_border=True
            )

            # Add header with planet and location context
            header = f"""🗺️  Map View - {current_planet.icon} {current_planet.name}
{'='*60}
Location: {location.name or 'Custom'}
Coordinates: {location.latitude:.2f}°, {location.longitude:.2f}°
TILE Code: {tile_code}

"""
            return header + ascii_map

        except Exception as e:
            # Fallback to legacy behavior or return error
            import traceback
            return f"""Error generating map view: {str(e)}

Use MAP VIEW [width] [height] [layer=N] to customize view.
Example: MAP VIEW 80 30 layer=100

{traceback.format_exc()}"""

    def _handle_cell(self, params):
        """Get information about a specific cell."""
        if not params:
            return "Usage: MAP CELL <cell_reference> (e.g., MAP CELL JN196)"

        cell_ref = params.strip().upper()

        try:
            # Get cell bounds and center
            bounds = self.map_engine.cell_system.get_cell_bounds(cell_ref)

            # Check for cities in this cell
            city = self.map_engine.get_city_by_cell(cell_ref)

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
            for tizo_code, city_data in self.map_engine.city_cells.items():
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
                cities = self.map_engine.get_cities_in_region(center_cell, radius)

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

        if from_loc in self.map_engine.city_cells:
            from_cell = self.map_engine.city_cells[from_loc]["cell_ref"]
            from_name = f"{self.map_engine.city_cells[from_loc]['name']} ({from_loc})"
        else:
            from_name = from_cell

        if to_loc in self.map_engine.city_cells:
            to_cell = self.map_engine.city_cells[to_loc]["cell_ref"]
            to_name = f"{self.map_engine.city_cells[to_loc]['name']} ({to_loc})"
        else:
            to_name = to_cell

        nav_info = self.map_engine.get_navigation_info(from_cell, to_cell)

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
        """Set location to a city using v2.0.0 TILE system."""
        from core.utils.grid_utils import latlong_to_tile, validate_tile_code

        if not params:
            return """Usage: MAP LOCATE CITY <name> or MAP LOCATE SET <lat> <lon>

Examples:
  MAP LOCATE CITY London
  MAP LOCATE CITY Sydney
  MAP LOCATE SET 51.5074 -0.1278"""

        parts = params.strip().split()
        subcommand = parts[0].upper()

        # Load cities from new database
        cities = self.map_renderer.cities

        if subcommand == "CITY" and len(parts) > 1:
            # Search for city by name
            city_name = " ".join(parts[1:])
            matching_city = None

            # Try exact match first
            for city in cities:
                if city['name'].lower() == city_name.lower():
                    matching_city = city
                    break

            # Try partial match
            if not matching_city:
                for city in cities:
                    if city_name.lower() in city['name'].lower():
                        matching_city = city
                        break

            if not matching_city:
                # Show suggestions
                suggestions = [c['name'] for c in cities if city_name.lower()[0] == c['name'].lower()[0]][:5]
                result = f"City not found: {city_name}\n\n"
                if suggestions:
                    result += "Did you mean:\n"
                    for sug in suggestions:
                        result += f"  • {sug}\n"
                return result

            # Update planet manager with new location
            try:
                from core.services.planet_manager import PlanetManager
                pm = PlanetManager()
                current_planet = pm.get_current()

                if current_planet:
                    pm.set_location(
                        planet_name=current_planet.name,
                        name=matching_city['name'],
                        latitude=matching_city['latitude'],
                        longitude=matching_city['longitude'],
                        region=matching_city.get('region'),
                        country=matching_city['country']
                    )

                    return f"""📍 Location Set
{'='*40}
City: {matching_city['name']}
Country: {matching_city['country']}
Region: {matching_city.get('region', 'N/A')}
Coordinates: {matching_city['latitude']:.4f}°, {matching_city['longitude']:.4f}°
TILE Code: {matching_city['tile_code']}
Grid Cell: {matching_city['grid_cell']}
Layer: {matching_city['layer']}

Use MAP VIEW to see the area around you."""
                else:
                    return "⚠️  No planet selected. Set 'planet' field in user.json."

            except Exception as e:
                return f"Error setting location: {str(e)}"

        elif subcommand == "SET" and len(parts) >= 3:
            # Set custom coordinates
            try:
                lat = float(parts[1])
                lon = float(parts[2])

                # Validate coordinates
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    return "Invalid coordinates. Latitude: -90 to 90, Longitude: -180 to 180"

                # Convert to TILE code
                tile_code = latlong_to_tile(lat, lon, layer=100)

                # Update planet manager
                from core.services.planet_manager import PlanetManager
                pm = PlanetManager()
                current_planet = pm.get_current()

                if current_planet:
                    pm.set_location(
                        planet_name=current_planet.name,
                        name="Custom Location",
                        latitude=lat,
                        longitude=lon
                    )

                    # Find nearest city
                    nearby = self.map_renderer.list_cities_in_view(tile_code, radius_km=100)
                    nearest = nearby[0] if nearby else None

                    result = f"""📍 Custom Location Set
{'='*40}
Coordinates: {lat:.4f}°, {lon:.4f}°
TILE Code: {tile_code}"""

                    if nearest:
                        result += f"""
Nearest City: {nearest['name']} ({nearest['distance_km']:.1f} km)"""

                    result += "\n\nUse MAP VIEW to see the area."
                    return result
                else:
                    return "⚠️  No planet selected. Set 'planet' field in user.json."

            except ValueError:
                return "Invalid coordinates. Use decimal degrees (e.g., MAP LOCATE SET 51.5074 -0.1278)"
            except Exception as e:
                return f"Error setting location: {str(e)}"

        else:
            return """Usage: MAP LOCATE CITY <name> or MAP LOCATE SET <lat> <lon>

Examples:
  MAP LOCATE CITY London
  MAP LOCATE CITY Sydney
  MAP LOCATE SET 51.5074 -0.1278"""

    def _handle_layers(self, params):
        """Show accessible layers."""
        try:
            import json
            from core.utils.paths import PATHS
            config_file = PATHS.MEMORY_SYSTEM_USER / "user.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "UTC")

                layers = self.map_engine.get_layer_access(tizo_code)

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
                lat, lon = self.map_engine.cell_system.cell_to_coord(cell_ref)
                city = self.map_engine.get_city_by_cell(cell_ref)

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
                cell_ref = self.map_engine.cell_system.coord_to_cell(lat, lon)

                result = f"🎯 Moving to coordinates {lat}°, {lon}°\n"
                result += f"Cell: {cell_ref}\n"

                city = self.map_engine.get_city_by_cell(cell_ref)
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
            from core.utils.paths import PATHS
            config_file = PATHS.MEMORY_SYSTEM_USER / "user.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                location = config.get("location", {})
                tizo_code = location.get("tizo_code", "MEL")

                if tizo_code in self.map_engine.city_cells:
                    city_data = self.map_engine.city_cells[tizo_code]
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
                        self.map_engine, cell_ref, width, height
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

    def _handle_world(self, params):
        """Handle world cities commands."""
        if not params:
            # Show world statistics
            total_cities = len(self.map_engine.world_cities)
            return f"""🌏 WORLD CITIES DATABASE

Total cities: {total_cities}
Coverage: APAC-centered 480×270 grid
Cell format: A1-style (A1 to RL270)

Commands:
• MAP WORLD [CITY_CODE] - Show city details
• MAP SEARCH [QUERY] - Search cities
• MAP WORLD REGION [CELL] - Cities in region"""

        sub_command = params[0].upper()

        if sub_command == "REGION" and len(params) > 1:
            cell_ref = params[1].upper()
            radius = int(params[2]) if len(params) > 2 else 5

            cities = self.map_engine.get_world_cities_in_region(cell_ref, radius)
            if not cities:
                return f"No cities found within {radius} cells of {cell_ref}"

            result = f"🗺️  CITIES NEAR {cell_ref} (radius: {radius} cells)\n\n"
            for city in cities[:10]:  # Limit to 10 closest
                result += f"• {city['name']}, {city['country']} ({city['city_code']})\n"
                result += f"  Cell: {city['cell_ref']} • Distance: {city['cell_distance']} cells\n\n"

            if len(cities) > 10:
                result += f"... and {len(cities) - 10} more cities"

            return result

        else:
            # Assume it's a city code
            city_code = sub_command
            city = self.map_engine.get_world_city_by_code(city_code)

            if not city:
                return f"City not found: {city_code}\nUse MAP SEARCH to find cities"

            return f"""🏙️  {city['name'].upper()}

Country: {city['country']}
Code: {city_code}
Cell Reference: {city['cell_ref']}
Coordinates: {city['lat']}°, {city['lon']}°
Grid Position: Col {city['col_index']}, Row {city['row_index']}

Navigation: MAP NAVIGATE FROM {city_code} TO [DESTINATION]"""

    def _handle_search(self, params):
        """Search world cities."""
        if not params:
            return "Usage: MAP SEARCH [QUERY]\nSearch by city name, country, or code"

        query = " ".join(params)
        results = self.map_engine.search_world_cities(query, limit=10)

        if not results:
            return f"No cities found matching: {query}"

        result = f"🔍 SEARCH RESULTS: '{query}'\n\n"
        for city in results:
            result += f"• {city['name']}, {city['country']} ({city['city_code']})\n"
            result += f"  Cell: {city['cell_ref']} • Score: {city['score']}\n\n"

        if len(results) >= 10:
            result += "🔍 Use more specific terms to narrow results"

        return result

    def _find_nearest_city(self, lat: float, lon: float, max_distance: float = 500.0):
        """
        Find the nearest city to given coordinates.

        Args:
            lat: Latitude
            lon: Longitude
            max_distance: Maximum distance in km

        Returns:
            City data dict or None
        """
        import math

        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points using Haversine formula."""
            R = 6371  # Earth radius in km

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
            c = 2 * math.asin(math.sqrt(a))

            return R * c

        nearest_city = None
        min_distance = max_distance

        # Search through all cities in map engine
        for tizo_code, city_data in self.map_engine.city_cells.items():
            coords = city_data.get('coordinates', {})
            city_lat = coords.get('lat')
            city_lon = coords.get('lon')

            if city_lat is not None and city_lon is not None:
                distance = haversine_distance(lat, lon, city_lat, city_lon)
                if distance < min_distance:
                    min_distance = distance
                    nearest_city = city_data

        return nearest_city

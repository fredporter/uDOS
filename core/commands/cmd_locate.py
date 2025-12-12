"""
uDOS v1.0.32 - LOCATE Command

Set or view current real-world location for the active planet.
Integrates with world map data for location-aware survival knowledge.

Usage:
    LOCATE - Show current location
    LOCATE SET <lat> <lon> [name] [country] [region] - Set location
    LOCATE CITY <city_name> - Set location from city database

Examples:
    LOCATE
    LOCATE SET 51.5074 -0.1278 "London" "UK" "England"
    LOCATE CITY Tokyo
    LOCATE CITY "New York"
"""

from core.services.planet_manager import PlanetManager
from core.services.standardized_input import StandardizedInput


def cmd_locate(user_data: dict, args: list) -> dict:
    """
    Handle LOCATE command.

    Args:
        user_data: User context data
        args: Command arguments

    Returns:
        Command result dict
    """
    pm = PlanetManager()
    input_service = StandardizedInput()

    # Get current planet
    current = pm.get_current()
    if not current:
        return {
            'success': False,
            'message': 'No active planet. Set planet field in user.json (memory/bank/user/user.json).'
        }

    # No args - show current location
    if not args:
        location = current.location

        if not location:
            return {
                'success': True,
                'message': f"📍 No location set for {current.icon} {current.name}\n"
                          f"   Use: LOCATE SET <lat> <lon> to set your location\n"
                          f"   Or: LOCATE CITY <name> to select from database"
            }

        return {
            'success': True,
            'message': f"📍 Current Location on {current.icon} {current.name}\n"
                      f"   Location: {location.name or 'Unknown'}\n"
                      f"   Coordinates: {location.latitude:.4f}°, {location.longitude:.4f}°\n"
                      f"   Country: {location.country or 'Unknown'}\n"
                      f"   Region: {location.region or 'Unknown'}\n"
                      f"\n"
                      f"   💡 Use MAP command to view on world map"
        }

    action = args[0].upper()

    # SET - Set coordinates manually
    if action == "SET":
        if len(args) < 3:
            # Interactive mode
            lat_str = input_service.text_input(
                "Latitude (-90 to 90)",
                required=True
            )
            lon_str = input_service.text_input(
                "Longitude (-180 to 180)",
                required=True
            )

            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                return {
                    'success': False,
                    'message': 'Invalid coordinates. Must be numbers.'
                }

            name = input_service.text_input("Location Name (optional)")
            country = input_service.text_input("Country (optional)")
            region = input_service.text_input("Region/State (optional)")
        else:
            # Command line mode
            try:
                latitude = float(args[1])
                longitude = float(args[2])
            except (ValueError, IndexError):
                return {
                    'success': False,
                    'message': 'Usage: LOCATE SET <latitude> <longitude> [name] [country] [region]'
                }

            name = args[3] if len(args) > 3 else ""
            country = args[4] if len(args) > 4 else ""
            region = args[5] if len(args) > 5 else ""

        try:
            location = pm.set_location(
                planet_name=current.name,
                latitude=latitude,
                longitude=longitude,
                name=name,
                country=country,
                region=region
            )

            return {
                'success': True,
                'message': f"✅ Location set on {current.icon} {current.name}\n"
                          f"   📍 {location.name or 'Location'}\n"
                          f"   Coordinates: {location.latitude:.4f}°, {location.longitude:.4f}°\n"
                          f"   {location.country or ''} {location.region or ''}\n"
                          f"\n"
                          f"   💡 Location-aware survival guides now available"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    # CITY - Select from city database
    elif action == "CITY":
        if len(args) < 2:
            return {
                'success': False,
                'message': 'Usage: LOCATE CITY <city_name>\n'
                          'Example: LOCATE CITY Tokyo'
            }

        city_name = " ".join(args[1:])

        # TODO: Integrate with city database from v1.0.20b
        # For now, provide major cities as examples
        major_cities = {
            "London": (51.5074, -0.1278, "UK", "England"),
            "New York": (40.7128, -74.0060, "USA", "New York"),
            "Tokyo": (35.6762, 139.6503, "Japan", "Kanto"),
            "Paris": (48.8566, 2.3522, "France", "Île-de-France"),
            "Sydney": (-33.8688, 151.2093, "Australia", "New South Wales"),
            "Dubai": (25.2048, 55.2708, "UAE", "Dubai"),
            "Singapore": (1.3521, 103.8198, "Singapore", ""),
            "Moscow": (55.7558, 37.6173, "Russia", "Central"),
            "Beijing": (39.9042, 116.4074, "China", "Beijing"),
            "Mumbai": (19.0760, 72.8777, "India", "Maharashtra"),
        }

        # Case-insensitive search
        city_key = None
        for key in major_cities:
            if key.lower() == city_name.lower():
                city_key = key
                break

        if not city_key:
            return {
                'success': False,
                'message': f"City '{city_name}' not found in database.\n"
                          f"Available cities: {', '.join(sorted(major_cities.keys()))}\n"
                          f"Or use: LOCATE SET <lat> <lon> for manual coordinates"
            }

        lat, lon, country, region = major_cities[city_key]

        try:
            location = pm.set_location(
                planet_name=current.name,
                latitude=lat,
                longitude=lon,
                name=city_key,
                country=country,
                region=region
            )

            return {
                'success': True,
                'message': f"✅ Location set to {city_key} on {current.icon} {current.name}\n"
                          f"   📍 {location.name}\n"
                          f"   Coordinates: {location.latitude:.4f}°, {location.longitude:.4f}°\n"
                          f"   {location.country}, {location.region}\n"
                          f"\n"
                          f"   💡 Location-aware survival guides now available"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    # CLEAR - Remove location
    elif action == "CLEAR":
        try:
            pm.set_location(
                planet_name=current.name,
                latitude=0.0,
                longitude=0.0,
                name="",
                country="",
                region=""
            )

            return {
                'success': True,
                'message': f"✅ Location cleared for {current.icon} {current.name}"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    else:
        return {
            'success': False,
            'message': f"Unknown action: {action}\n"
                      "Available: SET, CITY, CLEAR\n"
                      "Or use LOCATE without args to view current location"
        }

"""
uDOS v1.0.32 - CONFIG PLANET Command

Manages planet system (workspace metaphor).
Subcommands: LIST, SET, NEW, DELETE, SOLAR, INFO

Examples:
    CONFIG PLANET LIST - Show all planets
    CONFIG PLANET SET Earth - Switch to Earth
    CONFIG PLANET NEW Mars Sol Mars 🔴 "Red planet workspace"
    CONFIG PLANET INFO Earth - Show planet details
    CONFIG PLANET SOLAR - List solar systems
"""

from core.services.planet_manager import PlanetManager, Planet
from core.services.standardized_input import StandardizedInput


def cmd_config_planet(user_data: dict, args: list) -> dict:
    """
    Handle CONFIG PLANET subcommands.

    Args:
        user_data: User context data
        args: Command arguments [action, ...params]

    Returns:
        Command result dict
    """
    pm = PlanetManager()
    input_service = StandardizedInput()

    if not args:
        # Show current planet
        current = pm.get_current()
        if not current:
            return {
                'success': False,
                'message': 'No active planet. Use CONFIG PLANET LIST to see available planets.'
            }

        location_str = ""
        if current.location:
            loc = current.location
            location_str = f"\n  📍 Location: {loc.name or 'Unknown'} ({loc.latitude:.4f}, {loc.longitude:.4f})"
            if loc.country:
                location_str += f"\n  🌎 Country: {loc.country}"

        return {
            'success': True,
            'message': f"Current Planet: {current.icon} {current.name}\n"
                      f"  🌌 Solar System: {current.solar_system}\n"
                      f"  🪐 Type: {current.planet_type}\n"
                      f"  📝 Description: {current.description or 'No description'}{location_str}\n"
                      f"  🕒 Last Accessed: {current.last_accessed[:10]}"
        }

    action = args[0].upper()

    # LIST - Show all planets
    if action == "LIST":
        planets = pm.list_planets()
        current = pm.get_current()
        current_name = current.name if current else None

        if not planets:
            return {
                'success': False,
                'message': 'No planets found. Creating default Earth planet...'
            }

        lines = ["Available Planets:", ""]
        for planet in sorted(planets, key=lambda p: p.name):
            marker = "→" if planet.name == current_name else " "
            loc_info = ""
            if planet.location:
                loc_info = f" 📍 {planet.location.name or 'Located'}"

            lines.append(f"  {marker} {planet.icon} {planet.name} ({planet.solar_system}){loc_info}")

        lines.append("")
        lines.append("Use: CONFIG PLANET SET <name> to switch")

        return {
            'success': True,
            'message': '\n'.join(lines)
        }

    # SET - Switch active planet
    elif action == "SET":
        if len(args) < 2:
            # Interactive selection
            planets = pm.list_planets()
            if not planets:
                return {'success': False, 'message': 'No planets available'}

            options = [f"{p.icon} {p.name} ({p.solar_system})" for p in planets]
            choice = input_service.select_option(
                title="Select Planet",
                options=options,
                show_numbers=True
            )

            # Extract planet name from choice
            planet_name = choice.split()[1]  # "🌍 Earth (Sol)" -> "Earth"
        else:
            planet_name = args[1]

        try:
            planet = pm.set_planet(planet_name)
            return {
                'success': True,
                'message': f"✅ Switched to planet: {planet.icon} {planet.name}\n"
                          f"   Solar System: {planet.solar_system}\n"
                          f"   {planet.description or 'No description'}"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    # NEW - Create new planet
    elif action == "NEW":
        if len(args) < 2:
            # Interactive creation
            name = input_service.text_input("Planet Name", required=True)

            solar_systems = list(pm.get_solar_systems().keys())
            solar_system = input_service.select_option(
                title="Solar System",
                options=solar_systems,
                default_index=0
            )

            planet_types = ["Earth", "Mars", "Custom", "Exoplanet", "Space Station"]
            planet_type = input_service.select_option(
                title="Planet Type",
                options=planet_types,
                default_index=2
            )

            icons = ["🌍", "🔴", "🪐", "🌏", "🌎", "🌑", "🌕", "⭐", "🛰️", "🚀"]
            print("\nSuggested icons: " + " ".join(icons))
            icon = input_service.text_input("Icon", default="🪐")

            description = input_service.text_input("Description (optional)")
        else:
            # Command line args: NEW <name> [solar_system] [type] [icon] [description]
            name = args[1]
            solar_system = args[2] if len(args) > 2 else "Sol"
            planet_type = args[3] if len(args) > 3 else "Custom"
            icon = args[4] if len(args) > 4 else "🪐"
            description = " ".join(args[5:]) if len(args) > 5 else ""

        try:
            planet = pm.create_planet(
                name=name,
                solar_system=solar_system,
                planet_type=planet_type,
                icon=icon,
                description=description
            )

            return {
                'success': True,
                'message': f"✅ Created planet: {planet.icon} {planet.name}\n"
                          f"   Solar System: {planet.solar_system}\n"
                          f"   Type: {planet.planet_type}\n"
                          f"   Use: CONFIG PLANET SET {planet.name} to activate"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    # DELETE - Remove planet
    elif action in ["DELETE", "REMOVE"]:
        if len(args) < 2:
            return {
                'success': False,
                'message': 'Usage: CONFIG PLANET DELETE <name>'
            }

        planet_name = args[1]

        try:
            pm.delete_planet(planet_name)
            return {
                'success': True,
                'message': f"✅ Deleted planet: {planet_name}"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    # SOLAR - List solar systems
    elif action == "SOLAR":
        systems = pm.get_solar_systems()

        lines = ["Available Solar Systems:", ""]
        for sys_id, sys_info in systems.items():
            lines.append(f"  🌌 {sys_info['name']}")
            lines.append(f"     {sys_info['description']}")

            if sys_info['planets']:
                planets_str = ", ".join([f"{p['icon']} {name}"
                                        for name, p in sys_info['planets'].items()])
                lines.append(f"     Planets: {planets_str}")
            lines.append("")

        return {
            'success': True,
            'message': '\n'.join(lines)
        }

    # INFO - Show planet details
    elif action == "INFO":
        if len(args) < 2:
            # Show current planet
            return cmd_config_planet(user_data, [])

        planet_name = args[1]
        planet = pm.get_planet_info(planet_name)

        if not planet:
            return {
                'success': False,
                'message': f"Planet '{planet_name}' not found"
            }

        location_str = ""
        if planet.location:
            loc = planet.location
            location_str = f"\n  📍 Location: {loc.name or 'Unknown'}\n"
            location_str += f"     Coordinates: {loc.latitude:.4f}°, {loc.longitude:.4f}°"
            if loc.country:
                location_str += f"\n     Country: {loc.country}"
            if loc.region:
                location_str += f"\n     Region: {loc.region}"

        return {
            'success': True,
            'message': f"{planet.icon} {planet.name}\n"
                      f"  🌌 Solar System: {planet.solar_system}\n"
                      f"  🪐 Type: {planet.planet_type}\n"
                      f"  📝 Description: {planet.description or 'No description'}{location_str}\n"
                      f"  📅 Created: {planet.created[:10]}\n"
                      f"  🕒 Last Accessed: {planet.last_accessed[:10]}"
        }

    else:
        return {
            'success': False,
            'message': f"Unknown action: {action}\n"
                      "Available: LIST, SET, NEW, DELETE, SOLAR, INFO"
        }

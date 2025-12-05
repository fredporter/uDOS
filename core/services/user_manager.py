# uDOS v1.0.0 - User Profile Management System

import json
import os
from datetime import datetime
from getpass import getuser
from pathlib import Path
import time

class UserManager:
    """
    Manages user profile and system configuration in user.json.
    """

    def __init__(self, user_file='memory/bank/user/user.json', template_file='core/data/templates/user.template.json'):
        self.user_file = user_file
        self.template_file = template_file
        self.user_data = None

    def needs_user_setup(self):
        """Check if user.json exists and is valid."""
        if not os.path.exists(self.user_file):
            return True

        try:
            with open(self.user_file, 'r') as f:
                data = json.load(f)
                # Check for required fields in new JSON format (uppercase USER_PROFILE)
                user_profile = data.get('USER_PROFILE', {})
                if not user_profile.get('NAME'):
                    return True
                return False
        except (json.JSONDecodeError, FileNotFoundError):
            return True

    def run_user_setup(self, interactive=True, viewport_data=None):
        """
        Interactive setup to create user.json.

        Args:
            interactive (bool): Whether to prompt user
            viewport_data (dict): Display settings from ViewportDetector

        Returns:
            dict: User profile data
        """
        # Auto-detect system timezone and location
        from core.utils.system_info import get_system_timezone
        detected_timezone, detected_city = get_system_timezone()

        print("\n" + "="*60)
        print("🧙 USER PROFILE SETUP")
        print("="*60)
        print("Let's configure your uDOS environment.\n")
        print(f"ℹ️  Detected timezone: {detected_timezone} ({detected_city})\n")

        # Load existing user.json as template or create default
        if os.path.exists(self.user_file):
            with open(self.user_file, 'r') as f:
                user_config = json.load(f)
        else:
            # Create default configuration matching wizard format
            user_config = {
                "SYSTEM_NAME": "uDOS",
                "VERSION": "1.1.7",
                "USER_PROFILE": {
                    "NAME": "user",
                    "LOCATION": detected_city,
                    "TIMEZONE": detected_timezone,
                    "PREFERRED_MODE": "STANDARD",
                    "PASSWORD": ""
                },
                "PROJECT": {
                    "NAME": "uDOS Development",
                    "DESCRIPTION": "Offline-first OS for survival knowledge",
                    "START_DATE": datetime.now().strftime('%Y-%m-%d')
                },
                "LOCATION_DATA": {
                    "CITY": detected_city,
                    "COUNTRY": "Unknown",
                    "LATITUDE": 0,
                    "LONGITUDE": 0,
                    "TILE_CODE": "",
                    "MAP_POSITION": {
                        "X": 0,
                        "Y": 0
                    },
                    "CURRENT_LAYER": "SURFACE"
                },
                "SPATIAL_DATA": {
                    "PLANET": "Earth",
                    "GALAXY": "Milky Way",
                    "PLANET_ID": "earth",
                    "GALAXY_ID": "milky_way"
                },
                "SESSION_DATA": {
                    "CURRENT_SESSION": f"session_{int(time.time())}",
                    "SESSION_COUNT": 0,
                    "LAST_LOGIN": datetime.now().isoformat(),
                    "VIEWPORT": {}
                },
                "system_settings": {
                    "interface": {
                        "theme": "dungeon"
                    },
                    "workspace_preference": "memory"
                }
            }

        if interactive:
            # Required field: Username
            username = input(f"👤 Username [{user_config.get('USER_PROFILE', {}).get('NAME', 'user')}]: ").strip()
            if username:
                if 'USER_PROFILE' not in user_config:
                    user_config['USER_PROFILE'] = {}
                user_config['USER_PROFILE']['NAME'] = username

            # Optional field: Password
            password = input("🔐 Password (leave blank for none): ").strip()
            user_config['USER_PROFILE']['PASSWORD'] = password

            # Auto-detected timezone (modifiable)
            current_tz = user_config.get('USER_PROFILE', {}).get('TIMEZONE', detected_timezone)
            timezone = input(f"🌍 Timezone [{current_tz}]: ").strip()
            if timezone:
                user_config['USER_PROFILE']['TIMEZONE'] = timezone
            else:
                user_config['USER_PROFILE']['TIMEZONE'] = current_tz

            # Location - use city selector with grid code
            current_loc = user_config.get('USER_PROFILE', {}).get('LOCATION', detected_city)
            location_data = self._select_city(current_loc)
            user_config['USER_PROFILE']['LOCATION'] = location_data['name']

            # Update location data with city details
            if 'LOCATION_DATA' not in user_config:
                user_config['LOCATION_DATA'] = {}
            user_config['LOCATION_DATA']['CITY'] = location_data['name']
            user_config['LOCATION_DATA']['COUNTRY'] = location_data.get('country', 'Unknown')
            user_config['LOCATION_DATA']['TILE_CODE'] = location_data.get('tile_code', '')
            user_config['LOCATION_DATA']['LATITUDE'] = location_data.get('latitude', 0)
            user_config['LOCATION_DATA']['LONGITUDE'] = location_data.get('longitude', 0)

            # Planet selection
            current_planet = user_config.get('SPATIAL_DATA', {}).get('PLANET', 'Earth')
            planet_data = self._select_planet(current_planet)
            if 'SPATIAL_DATA' not in user_config:
                user_config['SPATIAL_DATA'] = {}
            user_config['SPATIAL_DATA']['PLANET'] = planet_data['name']
            user_config['SPATIAL_DATA']['PLANET_ID'] = planet_data['id']

            # Galaxy selection
            current_galaxy = user_config.get('SPATIAL_DATA', {}).get('GALAXY', 'Milky Way')
            galaxy_data = self._select_galaxy(current_galaxy)
            user_config['SPATIAL_DATA']['GALAXY'] = galaxy_data['name']
            user_config['SPATIAL_DATA']['GALAXY_ID'] = galaxy_data['id']

            # Theme selection - use theme selector
            current_theme = user_config.get('system_settings', {}).get('interface', {}).get('theme', 'dungeon')
            theme = self._select_theme(current_theme)
            if 'system_settings' not in user_config:
                user_config['system_settings'] = {}
            if 'interface' not in user_config['system_settings']:
                user_config['system_settings']['interface'] = {}
            user_config['system_settings']['interface']['theme'] = theme

        # Update session data
        if 'SESSION_DATA' not in user_config:
            user_config['SESSION_DATA'] = {}
        user_config['SESSION_DATA']['LAST_LOGIN'] = datetime.now().isoformat()

        # Save configuration
        os.makedirs(os.path.dirname(self.user_file), exist_ok=True)
        with open(self.user_file, 'w') as f:
            json.dump(user_config, f, indent=2)

        self.user_data = user_config

        if interactive:
            print(f"\n✅ User profile saved: {self.user_file}")
            print(f"👤 Welcome, {user_config['user_profile']['username']}!")

        return self.user_data

    def load_user_profile(self):
        """Load existing user.json."""
        try:
            with open(self.user_file, 'r') as f:
                self.user_data = json.load(f)
            return self.user_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_api_key(self):
        """
        Retrieve API key from ConfigManager (v1.5.0).

        Returns:
            str: Gemini API key or empty string if not set
        """
        try:
            from core.uDOS_main import get_config
            config = get_config()
            return config.get('GEMINI_API_KEY', '')
        except Exception:
            # Fallback to direct .env reading if ConfigManager fails
            env_file = '.env'
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.strip().startswith('GEMINI_API_KEY='):
                                return line.strip().split('=', 1)[1]
                except:
                    pass
            return ''

    def _select_city(self, default_city: str = "Sydney") -> dict:
        """Interactive city selector using cities.json with grid code display."""
        try:
            import json
            cities_file = Path(__file__).parent.parent / 'data' / 'geography' / 'cities.json'

            if not cities_file.exists():
                # Fallback to manual input
                city_name = input(f"📍 Location [{default_city}]: ").strip() or default_city
                return {'name': city_name, 'country': 'Unknown', 'tile_code': '', 'latitude': 0, 'longitude': 0}

            with open(cities_file) as f:
                cities_data = json.load(f)

            cities = cities_data.get('cities', [])
            if not cities:
                city_name = input(f"📍 Location [{default_city}]: ").strip() or default_city
                return {'name': city_name, 'country': 'Unknown', 'tile_code': '', 'latitude': 0, 'longitude': 0}

            # Create options with grid codes
            city_options = []
            city_map = {}
            for city in cities:
                tile_code = city.get('tile_code', city.get('grid_cell', ''))
                display_name = f"{city['name']:<20} {city.get('country', ''):<15} [{tile_code}]"
                city_options.append(display_name)
                city_map[display_name] = city

            # Sort and find default
            city_options = sorted(city_options)
            default_index = 0
            for i, opt in enumerate(city_options):
                if default_city in opt:
                    default_index = i
                    break

            print(f"\n📍 Select your location (↑↓ arrows, Enter to select):")
            print("   Format: City               Country         [Grid Code]")

            # Use standardized selector
            from core.input.standardized_input import StandardizedInput
            input_service = StandardizedInput()
            selected_display = input_service.select_option(
                title="Location",
                options=city_options,
                default_index=default_index,
                show_title=False
            )

            selected_city = city_map[selected_display]
            print(f"   ✓ Selected: {selected_city['name']} [{selected_city.get('tile_code', '')}]")

            return {
                'name': selected_city['name'],
                'country': selected_city.get('country', 'Unknown'),
                'tile_code': selected_city.get('tile_code', selected_city.get('grid_cell', '')),
                'latitude': selected_city.get('latitude', 0),
                'longitude': selected_city.get('longitude', 0)
            }

        except Exception as e:
            # Fallback to manual input
            city_name = input(f"📍 Location [{default_city}]: ").strip() or default_city
            return {'name': city_name, 'country': 'Unknown', 'tile_code': '', 'latitude': 0, 'longitude': 0}    def _select_planet(self, default_planet: str = "Earth") -> dict:
        """Interactive planet selector using planets.json."""
        try:
            import json
            planets_file = Path(__file__).parent.parent / 'data' / 'spatial' / 'planets.json'

            if not planets_file.exists():
                # Fallback to manual input
                planet_name = input(f"🪐 Planet [{default_planet}]: ").strip() or default_planet
                return {'name': planet_name, 'id': planet_name.lower()}

            with open(planets_file) as f:
                planets_data = json.load(f)

            planets = planets_data.get('planets', [])
            if not planets:
                planet_name = input(f"🪐 Planet [{default_planet}]: ").strip() or default_planet
                return {'name': planet_name, 'id': planet_name.lower()}

            # Create options list
            planet_options = []
            planet_map = {}
            for planet in planets:
                display_name = f"{planet['name']:<15} ({planet.get('type', 'unknown')})"
                planet_options.append(display_name)
                planet_map[display_name] = planet

            # Find default index
            default_index = 0
            for i, opt in enumerate(planet_options):
                if default_planet in opt:
                    default_index = i
                    break

            print(f"\n🪐 Select your planet (↑↓ arrows, Enter to select):")

            # Use standardized selector
            from core.input.standardized_input import StandardizedInput
            input_service = StandardizedInput()
            selected_display = input_service.select_option(
                title="Planet",
                options=planet_options,
                default_index=default_index,
                show_title=False
            )

            selected_planet = planet_map[selected_display]
            print(f"   ✓ Selected: {selected_planet['name']}")

            return {
                'name': selected_planet['name'],
                'id': selected_planet['id']
            }

        except Exception as e:
            # Fallback to manual input
            planet_name = input(f"🪐 Planet [{default_planet}]: ").strip() or default_planet
            return {'name': planet_name, 'id': planet_name.lower()}

    def _select_galaxy(self, default_galaxy: str = "Milky Way") -> dict:
        """Interactive galaxy selector using galaxies.json."""
        try:
            import json
            galaxies_file = Path(__file__).parent.parent / 'data' / 'spatial' / 'galaxies.json'

            if not galaxies_file.exists():
                # Fallback to manual input
                galaxy_name = input(f"🌌 Galaxy [{default_galaxy}]: ").strip() or default_galaxy
                return {'name': galaxy_name, 'id': galaxy_name.lower().replace(' ', '_')}

            with open(galaxies_file) as f:
                galaxies_data = json.load(f)

            # Build galaxy list (home galaxy + local group)
            galaxy_options = []
            galaxy_map = {}

            # Add home galaxy (Milky Way)
            home = galaxies_data.get('home_galaxy', {})
            if home:
                display_name = f"{home['name']:<30} (Home - {home.get('type', 'unknown')})"
                galaxy_options.append(display_name)
                galaxy_map[display_name] = {'name': home['name'], 'id': home['id']}

            # Add local group galaxies
            local_group = galaxies_data.get('local_group', {}).get('major_members', [])
            for galaxy in local_group:
                dist_mly = galaxy.get('distance_ly', 0) / 1e6
                display_name = f"{galaxy['name']:<30} ({dist_mly:.2f} Mly away)"
                galaxy_options.append(display_name)
                # Create ID from name
                galaxy_id = galaxy['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
                galaxy_map[display_name] = {'name': galaxy['name'], 'id': galaxy_id}

            if not galaxy_options:
                galaxy_name = input(f"🌌 Galaxy [{default_galaxy}]: ").strip() or default_galaxy
                return {'name': galaxy_name, 'id': galaxy_name.lower().replace(' ', '_')}

            # Find default index
            default_index = 0
            for i, opt in enumerate(galaxy_options):
                if default_galaxy in opt:
                    default_index = i
                    break

            print(f"\n🌌 Select your galaxy (↑↓ arrows, Enter to select):")

            # Use standardized selector
            from core.input.standardized_input import StandardizedInput
            input_service = StandardizedInput()
            selected_display = input_service.select_option(
                title="Galaxy",
                options=galaxy_options,
                default_index=default_index,
                show_title=False
            )

            selected_galaxy = galaxy_map[selected_display]
            print(f"   ✓ Selected: {selected_galaxy['name']}")

            return selected_galaxy

        except Exception as e:
            # Fallback to manual input
            galaxy_name = input(f"🌌 Galaxy [{default_galaxy}]: ").strip() or default_galaxy
            return {'name': galaxy_name, 'id': galaxy_name.lower().replace(' ', '_')}

    def _select_theme(self, default_theme: str = "dungeon") -> str:
        """Interactive theme selector."""
        try:
            themes = ['dungeon', 'galaxy', 'foundation', 'science', 'project']

            # Find default index
            try:
                default_index = themes.index(default_theme)
            except ValueError:
                default_index = 0

            print(f"\n🎨 Select your theme (↑↓ arrows, Enter to select):")

            # Use standardized selector
            from core.input.standardized_input import StandardizedInput
            input_service = StandardizedInput()
            selected = input_service.select_option(
                title="Theme",
                options=themes,
                default_index=default_index,
                show_title=False
            )

            return selected

        except Exception:
            # Fallback to manual input
            print("\n🎨 Available themes: dungeon, galaxy, foundation, science, project")
            theme = input(f"Theme [{default_theme}]: ").strip().lower()
            return theme if theme in themes else default_theme

    def get_user_data(self):
        """
        Get the current user data dictionary.
        Returns the loaded user profile data or None if not loaded.
        """
        if not self.user_data:
            self.load_user_profile()
        return self.user_data

    def is_assist_mode(self):
        """Check if assist mode is enabled."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            return self.user_data.get('session_preferences', {}).get('assist_mode', False)
        return False

    @property
    def current_user(self):
        """Get current username."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            return self.user_data.get('USER_PROFILE', {}).get('NAME', 'Guest')
        return 'Guest'

    def update_session_data(self, session_id, viewport_data=None):
        """Update session metadata in user.json."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            # Update session data
            if 'SESSION_DATA' not in self.user_data:
                self.user_data['SESSION_DATA'] = {}
            self.user_data['SESSION_DATA']['CURRENT_SESSION'] = session_id
            self.user_data['SESSION_DATA']['LAST_LOGIN'] = datetime.now().isoformat()

            if viewport_data:
                # Store viewport in SESSION_DATA
                self.user_data['SESSION_DATA']['VIEWPORT'] = {
                    'device_type': viewport_data.get('device_type', 'TERMINAL'),
                    'terminal_size': viewport_data.get('terminal_size', {'width': 80, 'height': 24}),
                    'grid_dimensions': viewport_data.get('grid_dimensions', {'width': 10, 'height': 9})
                }

            with open(self.user_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)

    def get_user_greeting(self):
        """Generate personalized greeting."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            name = self.user_data.get('USER_PROFILE', {}).get('NAME', 'Adventurer')
            preferred_mode = self.user_data.get('USER_PROFILE', {}).get('PREFERRED_MODE', 'STANDARD')

            greeting = f"Welcome back, {name}!"
            if preferred_mode != 'STANDARD':
                greeting += f" [MODE: {preferred_mode}]"

            return greeting

        return "Welcome to uDOS!"

    def get_lifespan(self):
        """
        Get the lifespan setting from advanced settings.
        Returns 'Infinite' or an integer number of moves.
        """
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            # Default to infinite for development mode
            return 'Infinite'

        return 'Infinite'

    def check_lifespan_status(self, current_moves):
        """
        Check lifespan status and return warning/status info.

        Args:
            current_moves (int): Current total move count

        Returns:
            dict: Status information with warnings if needed
        """
        lifespan = self.get_lifespan()

        if lifespan == 'Infinite':
            return {
                'status': 'OK',
                'lifespan': 'Infinite',
                'remaining': 'Infinite',
                'percent_used': 0,
                'warning': None
            }

        try:
            max_moves = int(lifespan)
            remaining = max_moves - current_moves
            percent_used = (current_moves / max_moves) * 100

            status = 'OK'
            warning = None

            if percent_used >= 100:
                status = 'EOL'
                warning = '🚨 LIFESPAN EXCEEDED - EOL policy in effect'
            elif percent_used >= 90:
                status = 'CRITICAL'
                warning = f'⚠️  WARNING: {remaining} moves remaining ({100-percent_used:.1f}% left)'
            elif percent_used >= 75:
                status = 'WARNING'
                warning = f'⚠️  {remaining} moves remaining'

            return {
                'status': status,
                'lifespan': max_moves,
                'remaining': remaining,
                'percent_used': percent_used,
                'warning': warning
            }
        except ValueError:
            # Invalid lifespan value, treat as infinite
            return {
                'status': 'OK',
                'lifespan': 'Infinite',
                'remaining': 'Infinite',
                'percent_used': 0,
                'warning': None
            }

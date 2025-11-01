# uDOS v1.0.0 - User Profile Management System

import json
import os
from datetime import datetime
from getpass import getuser
import time

class UserManager:
    """
    Manages user profile and system configuration in USER.UDO.
    """


    def __init__(self, user_file='sandbox/USER.UDO', template_file='data/USER.UDT'):
        self.user_file = user_file
        self.template_file = template_file
        self.user_data = None

    def needs_user_setup(self):
        """Check if USER.UDO exists and is valid."""
        if not os.path.exists(self.user_file):
            return True

        try:
            with open(self.user_file, 'r') as f:
                data = json.load(f)
                # Check for required fields
                if not data.get('USER_PROFILE', {}).get('NAME'):
                    return True
                return False
        except (json.JSONDecodeError, FileNotFoundError):
            return True

    def run_user_setup(self, interactive=True, viewport_data=None):
        """
        Interactive setup to create USER.UDO.

        Args:
            interactive (bool): Whether to prompt user
            viewport_data (dict): Display settings from ViewportDetector

        Returns:
            dict: User profile data
        """
        print("\n" + "="*60)
        print("🧙 USER PROFILE SETUP")
        print("="*60)
        print("Let's configure your uDOS environment.\n")

        # Collect user information
        if interactive:
            user_name = input("👤 Your name (or alias): ").strip() or getuser()

            # Timezone
            tz_offset = -time.timezone / 3600
            suggested_tz = f"UTC{'+' if tz_offset >= 0 else ''}{int(tz_offset)}"
            user_tz = input(f"🌍 Your timezone [{suggested_tz}]: ").strip() or suggested_tz

            # Location (text description)
            user_location = input("📍 Your location (city/region): ").strip() or "Unknown"

            # World location setup (for mapping)
            print("\n🗺️  WORLD MAP CONFIGURATION:")
            print("  Set your location for map-based features")
            print("  Available cities: New York, London, Tokyo, Sydney, Paris,")
            print("                    San Francisco, Mumbai, Berlin, Singapore, São Paulo")
            world_city = input("Select city (or press Enter to skip): ").strip()

            if world_city:
                # Load worldmap to validate
                worldmap_file = "data/system/worldmap.json"
                if os.path.exists(worldmap_file):
                    try:
                        with open(worldmap_file, 'r') as f:
                            worldmap = json.load(f)
                        cities = worldmap.get("CITIES", {})

                        if world_city in cities:
                            city_data = cities[world_city]
                            user_country = city_data["country"]
                            user_continent = city_data["continent"]
                            user_latitude = city_data["latitude"]
                            user_longitude = city_data["longitude"]
                            user_region = city_data.get("region", "")
                            user_tz = city_data.get("timezone", user_tz)
                            print(f"  ✅ Location set to {world_city}, {user_country}")
                        else:
                            print(f"  ⚠️  City '{world_city}' not found, using defaults")
                            world_city = ""
                            user_country = "Unknown"
                            user_continent = ""
                            user_latitude = 0.0
                            user_longitude = 0.0
                            user_region = ""
                    except:
                        world_city = ""
                        user_country = "Unknown"
                        user_continent = ""
                        user_latitude = 0.0
                        user_longitude = 0.0
                        user_region = ""
                else:
                    world_city = ""
                    user_country = "Unknown"
                    user_continent = ""
                    user_latitude = 0.0
                    user_longitude = 0.0
                    user_region = ""
            else:
                world_city = ""
                user_country = "Unknown"
                user_continent = ""
                user_latitude = 0.0
                user_longitude = 0.0
                user_region = ""

            # Assist mode preference
            print("\n🤖 Operation Mode:")
            print("  STANDARD - Respond to your commands")
            print("  ASSIST   - Proactively suggest next steps")
            assist_choice = input("Preferred mode [STANDARD]: ").strip().upper()
            assist_mode = assist_choice == "ASSIST"

            # API Key
            print("\n🔑 API Configuration:")
            print("  Gemini API key enables AI features (optional)")
            print("  Get key: https://makersuite.google.com/app/apikey")
            api_key = input("Gemini API key (or press Enter to skip): ").strip()

        else:
            # Non-interactive defaults
            user_name = getuser()
            user_tz = "UTC"
            user_location = "Unknown"
            world_city = ""
            user_country = "Unknown"
            user_continent = ""
            user_latitude = 0.0
            user_longitude = 0.0
            user_region = ""
            assist_mode = False
            api_key = ""

        # Load template
        with open(self.template_file, 'r') as f:
            template = f.read()

        # Prepare viewport data
        if viewport_data is None:
            viewport_data = {
                'device_type': 'TERMINAL',
                'terminal_size': '80×24',
                'grid_dimensions': '20×12'
            }

        # Replace placeholders
        user_profile = template.replace('{{USER_NAME}}', user_name)
        user_profile = user_profile.replace('{{USER_TIMEZONE}}', user_tz)
        user_profile = user_profile.replace('{{USER_LOCATION}}', user_location)
        user_profile = user_profile.replace('{{USER_CITY}}', world_city)
        user_profile = user_profile.replace('{{USER_COUNTRY}}', user_country)
        user_profile = user_profile.replace('{{USER_CONTINENT}}', user_continent)
        user_profile = user_profile.replace('{{USER_LATITUDE}}', str(user_latitude))
        user_profile = user_profile.replace('{{USER_LONGITUDE}}', str(user_longitude))
        user_profile = user_profile.replace('{{USER_REGION}}', user_region)
        user_profile = user_profile.replace('{{ASSIST_MODE}}', 'ASSIST' if assist_mode else 'STANDARD')
        user_profile = user_profile.replace('{{GEMINI_API_KEY}}', api_key)
        user_profile = user_profile.replace('{{DEVICE_TYPE}}', viewport_data.get('device_type', 'TERMINAL'))
        user_profile = user_profile.replace('{{TERMINAL_SIZE}}', viewport_data.get('terminal_size', '80×24'))
        user_profile = user_profile.replace('{{GRID_DIMENSIONS}}', viewport_data.get('grid_dimensions', '20×12'))
        user_profile = user_profile.replace('{{TIMESTAMP}}', datetime.now().isoformat())
        user_profile = user_profile.replace('{{SESSION_ID}}', f"session_{int(time.time())}")

        # Save to sandbox
        os.makedirs(os.path.dirname(self.user_file), exist_ok=True)
        with open(self.user_file, 'w') as f:
            f.write(user_profile)

        self.user_data = json.loads(user_profile)

        if interactive:
            print(f"\n✅ User profile created: {self.user_file}")
            print(f"👤 Welcome, {user_name}!")

        return self.user_data

    def load_user_profile(self):
        """Load existing USER.UDO."""
        try:
            with open(self.user_file, 'r') as f:
                self.user_data = json.load(f)
            return self.user_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_api_key(self):
        """Retrieve Gemini API key from user profile."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            return self.user_data.get('SYSTEM_CONFIG', {}).get('GEMINI_API_KEY', '')
        return ''

    def is_assist_mode(self):
        """Check if assist mode is enabled."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            return self.user_data.get('SESSION_PREFERENCES', {}).get('ASSIST_MODE', False)
        return False

    def update_session_data(self, session_id, viewport_data=None):
        """Update session metadata in USER.UDO."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            self.user_data['METADATA']['LAST_SESSION'] = session_id
            self.user_data['USER_PROFILE']['LAST_UPDATED'] = datetime.now().isoformat()

            if viewport_data:
                self.user_data['DISPLAY_SETTINGS'].update({
                    'DEVICE_TYPE': viewport_data.get('device_type', 'TERMINAL'),
                    'TERMINAL_SIZE': viewport_data.get('terminal_size', '80×24'),
                    'GRID_DIMENSIONS': viewport_data.get('grid_dimensions', '20×12')
                })

            with open(self.user_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)

    def get_user_greeting(self):
        """Generate personalized greeting."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            name = self.user_data.get('USER_PROFILE', {}).get('NAME', 'Adventurer')
            mode = self.user_data.get('USER_PROFILE', {}).get('PREFERRED_MODE', 'STANDARD')

            greeting = f"Welcome back, {name}!"
            if mode == 'ASSIST':
                greeting += " [ASSIST MODE]"

            return greeting

        return "Welcome to uDOS!"

    def get_lifespan(self):
        """
        Get the lifespan setting.
        Returns 'Infinite' or an integer number of moves.
        """
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            lifespan = self.user_data.get('SYSTEM_CONFIG', {}).get('LIFESPAN', 'Infinite')
            return lifespan

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

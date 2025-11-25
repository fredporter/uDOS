# uDOS v1.0.0 - User Profile Management System

import json
import os
from datetime import datetime
from getpass import getuser
import time

class UserManager:
    """
    Manages user profile and system configuration in user.json.
    """

    def __init__(self, user_file='memory/sandbox/user.json', template_file='knowledge/system/templates/user.template.json'):
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
                # Check for required fields in new JSON format
                user_profile = data.get('user_profile', {})
                if not user_profile.get('username'):
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
            # Create default configuration
            user_config = {
                "user_profile": {
                    "schema_version": "USER_PROFILE_V2",
                    "installation_id": "user_dev_install",
                    "profile_version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "last_session": f"session_{int(time.time())}",
                    "username": "user",
                    "password": "",
                    "timezone": detected_timezone,
                    "location": detected_city,
                    "project_name": "uDOS_project"
                },
                "system_settings": {
                    "display": {
                        "theme": "DUNGEON_CRAWLER",
                        "color_support": True,
                        "unicode_support": True,
                        "render_mode": "TERMINAL"
                    },
                    "workspace_preference": "sandbox"
                },
                "session_preferences": {
                    "assist_mode": False,
                    "preferred_mode": "STANDARD"
                },
                "advanced": {
                    "developer_mode": True,
                    "debug_logging": True,
                    "experimental_features": True
                },
                "metadata": {
                    "installation_type": "DEVELOPMENT",
                    "config_format": "JSON_V2",
                    "created_date": datetime.now().strftime('%Y-%m-%d')
                }
            }

        if interactive:
            # Required field: Username
            username = input(f"👤 Username [{user_config['user_profile'].get('username', 'user')}]: ").strip()
            if username:
                user_config['user_profile']['username'] = username

            # Optional field: Password
            password = input("🔐 Password (leave blank for none): ").strip()
            user_config['user_profile']['password'] = password

            # Auto-detected timezone (modifiable)
            current_tz = user_config['user_profile'].get('timezone', detected_timezone)
            timezone = input(f"🌍 Timezone [{current_tz}]: ").strip()
            if timezone:
                user_config['user_profile']['timezone'] = timezone
            else:
                user_config['user_profile']['timezone'] = current_tz

            # Location defaults to timezone city (modifiable)
            current_loc = user_config['user_profile'].get('location', detected_city)
            location = input(f"📍 Location [{current_loc}]: ").strip()
            if location:
                user_config['user_profile']['location'] = location
            else:
                user_config['user_profile']['location'] = current_loc

            # Project name
            project_name = input(f"🎯 Project name [{user_config['user_profile'].get('project_name', 'uDOS_project')}]: ").strip()
            if project_name:
                user_config['user_profile']['project_name'] = project_name

            # Theme selection
            print("\n🎨 Available themes: DUNGEON_CRAWLER, CYBERPUNK, MINIMAL")
            theme = input(f"Theme [{user_config['system_settings']['display']['theme']}]: ").strip().upper()
            if theme in ['DUNGEON_CRAWLER', 'CYBERPUNK', 'MINIMAL']:
                user_config['system_settings']['display']['theme'] = theme

            # Assist mode
            assist_choice = input("🤖 Enable assist mode? (y/N): ").strip().lower()
            user_config['session_preferences']['assist_mode'] = assist_choice == 'y'

        # Update timestamps
        user_config['user_profile']['last_updated'] = datetime.now().isoformat()

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
            return self.user_data.get('user_profile', {}).get('username', 'Guest')
        return 'Guest'

    def update_session_data(self, session_id, viewport_data=None):
        """Update session metadata in user.json."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            self.user_data['user_profile']['last_session'] = session_id
            self.user_data['user_profile']['last_updated'] = datetime.now().isoformat()

            if viewport_data:
                self.user_data['system_settings']['viewport'].update({
                    'device_type': viewport_data.get('device_type', 'TERMINAL'),
                    'terminal_size': viewport_data.get('terminal_size', {'width': 80, 'height': 24}),
                    'grid_dimensions': viewport_data.get('grid_dimensions', {'width': 10, 'height': 9})
                })

            with open(self.user_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)

    def get_user_greeting(self):
        """Generate personalized greeting."""
        if not self.user_data:
            self.load_user_profile()

        if self.user_data:
            name = self.user_data.get('user_profile', {}).get('username', 'Adventurer')
            assist_mode = self.user_data.get('session_preferences', {}).get('assist_mode', False)

            greeting = f"Welcome back, {name}!"
            if assist_mode:
                greeting += " [ASSIST MODE]"

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

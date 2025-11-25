"""
uDOS Editor Manager
Handles CLI and web-based editor detection, installation, and configuration.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import urllib.request
import tarfile
import zipfile
from pathlib import Path


class EditorManager:
    """Manages text editors for uDOS CLI and web modes."""

    def __init__(self, user_data_path='memory/sandbox/user.json'):
        self.user_data_path = user_data_path
        self.extensions_dir = Path('extensions')
        self.native_dir = self.extensions_dir / 'native'
        self.web_dir = self.extensions_dir / 'web'

        # Ensure directories exist
        self.native_dir.mkdir(parents=True, exist_ok=True)
        self.web_dir.mkdir(parents=True, exist_ok=True)

    def detect_available_editors(self):
        """
        Detect all available text editors on the system.

        Returns:
            dict: Available editors by category
        """
        available = {
            'CLI': [],
            'WEB': []
        }

        # Check for CLI editors
        cli_editors = [
            ('micro', self.native_dir / 'micro' / 'micro'),  # Custom install
            ('nano', 'nano'),  # System
            ('vim', 'vim'),    # System
            ('vi', 'vi'),      # System
            ('emacs', 'emacs') # System
        ]

        for name, path in cli_editors:
            if self._is_available(path):
                available['CLI'].append(name)

        # Check for web editors
        web_editors = [
            ('typo', self.web_dir / 'typo' / 'package.json'),
        ]

        for name, indicator_file in web_editors:
            if Path(indicator_file).exists():
                available['WEB'].append(name)

        return available

    def _is_available(self, path):
        """Check if editor is available."""
        if isinstance(path, Path):
            # Custom installation path
            return path.exists() and os.access(path, os.X_OK)
        else:
            # System command
            return shutil.which(path) is not None

    def get_preferred_editor(self, mode='CLI'):
        """
        Get user's preferred editor for specified mode.

        Args:
            mode (str): 'CLI' or 'WEB'

        Returns:
            str: Editor name or None
        """
        try:
            with open(self.user_data_path, 'r') as f:
                user_data = json.load(f)

            prefs = user_data.get('EDITOR_PREFERENCES', {})

            if mode == 'CLI':
                return prefs.get('CLI_EDITOR')
            elif mode == 'WEB':
                return prefs.get('WEB_EDITOR')
            else:
                return prefs.get('DEFAULT_MODE', 'CLI')

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def set_preferred_editor(self, editor_name, mode='CLI'):
        """
        Set user's preferred editor.

        Args:
            editor_name (str): Name of the editor
            mode (str): 'CLI' or 'WEB'
        """
        try:
            with open(self.user_data_path, 'r') as f:
                user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_data = {}

        if 'EDITOR_PREFERENCES' not in user_data:
            user_data['EDITOR_PREFERENCES'] = {
                'DEFAULT_MODE': 'CLI',
                'CLI_EDITOR': None,
                'WEB_EDITOR': None,
                'AUTO_INSTALL': True
            }

        if mode == 'CLI':
            user_data['EDITOR_PREFERENCES']['CLI_EDITOR'] = editor_name
        elif mode == 'WEB':
            user_data['EDITOR_PREFERENCES']['WEB_EDITOR'] = editor_name

        with open(self.user_data_path, 'w') as f:
            json.dump(user_data, f, indent=2)

    def get_best_editor(self, mode='CLI'):
        """
        Get the best available editor based on preferences and availability.

        Args:
            mode (str): 'CLI' or 'WEB'

        Returns:
            tuple: (editor_name, editor_path)
        """
        available = self.detect_available_editors()
        preferred = self.get_preferred_editor(mode)

        if mode == 'CLI':
            # Check if preferred editor is available
            if preferred and preferred in available['CLI']:
                return (preferred, self._get_editor_path(preferred))

            # Fallback priority: nano > micro > vim > vi
            # nano is preferred - more user-friendly and always available
            priority = ['nano', 'micro', 'vim', 'vi']
            for editor in priority:
                if editor in available['CLI']:
                    return (editor, self._get_editor_path(editor))

            # Last resort - use EDITOR env var or vi
            env_editor = os.environ.get('EDITOR', 'vi')
            return (env_editor, env_editor)

        elif mode == 'WEB':
            if preferred and preferred in available['WEB']:
                return (preferred, None)  # Web editors don't have simple paths

            if 'typo' in available['WEB']:
                return ('typo', None)

            return (None, None)

    def _get_editor_path(self, editor_name):
        """Get the full path to an editor."""
        # Check custom installation first
        custom_path = self.native_dir / editor_name / editor_name
        if custom_path.exists():
            return str(custom_path)

        # Check system
        return shutil.which(editor_name) or editor_name

    def install_micro(self, force=False):
        """
        Install micro editor from GitHub releases.

        Args:
            force (bool): Force reinstallation

        Returns:
            bool: Success status
        """
        micro_dir = self.native_dir / 'micro'
        micro_bin = micro_dir / 'micro'

        # Check if already installed
        if micro_bin.exists() and not force:
            print("✅ micro is already installed")
            return True

        print("📥 Installing micro editor...")

        # Detect platform
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map to micro's release naming
        if system == 'darwin':
            os_name = 'osx'
        elif system == 'linux':
            os_name = 'linux'
        elif system == 'windows':
            os_name = 'win'
        else:
            print(f"❌ Unsupported platform: {system}")
            return False

        # Map architecture
        if machine in ['x86_64', 'amd64']:
            arch = 'amd64'
        elif machine in ['arm64', 'aarch64']:
            arch = 'arm64'
        elif machine in ['armv7l', 'armv6l']:
            arch = 'arm'
        else:
            arch = 'amd64'  # Default

        # Construct download URL
        version = 'v2.0.14'  # Latest stable as of implementation
        if os_name == 'win':
            filename = f'micro-{version}-{os_name}{arch}.zip'
        else:
            filename = f'micro-{version}-{os_name}-{arch}.tar.gz'

        url = f'https://github.com/zyedidia/micro/releases/download/{version}/{filename}'

        try:
            # Download
            print(f"📦 Downloading from {url}")
            download_path = self.native_dir / filename

            urllib.request.urlretrieve(url, download_path)
            print("✅ Download complete")

            # Extract
            print("📂 Extracting...")
            micro_dir.mkdir(parents=True, exist_ok=True)

            if filename.endswith('.tar.gz'):
                with tarfile.open(download_path, 'r:gz') as tar:
                    tar.extractall(self.native_dir)

                # Move from extracted directory to micro/
                extracted_dir = self.native_dir / f'micro-{version}'
                if extracted_dir.exists():
                    # Move micro binary
                    src_bin = extracted_dir / 'micro'
                    if src_bin.exists():
                        shutil.move(str(src_bin), str(micro_bin))
                        os.chmod(micro_bin, 0o755)

                    # Clean up
                    shutil.rmtree(extracted_dir)

            elif filename.endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(self.native_dir)

                extracted_dir = self.native_dir / f'micro-{version}'
                if extracted_dir.exists():
                    src_bin = extracted_dir / 'micro.exe'
                    if src_bin.exists():
                        shutil.move(str(src_bin), str(micro_dir / 'micro.exe'))
                    shutil.rmtree(extracted_dir)

            # Clean up download
            download_path.unlink()

            # Verify installation
            if micro_bin.exists():
                print("✅ micro installed successfully!")
                print(f"📍 Location: {micro_bin}")

                # Set as preferred editor
                self.set_preferred_editor('micro', 'CLI')

                return True
            else:
                print("❌ Installation failed - binary not found")
                return False

        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

    def open_file(self, filepath, mode=None, editor=None):
        """
        Open a file with the appropriate editor.

        Args:
            filepath (str): Path to file to edit
            mode (str): 'CLI' or 'WEB' (None = auto-detect from preferences)
            editor (str): Specific editor to use (overrides detection)

        Returns:
            int: Return code from editor
        """
        # Determine mode
        if mode is None:
            try:
                with open(self.user_data_path, 'r') as f:
                    user_data = json.load(f)
                mode = user_data.get('EDITOR_PREFERENCES', {}).get('DEFAULT_MODE', 'CLI')
            except:
                mode = 'CLI'

        # Get editor
        if editor:
            editor_path = self._get_editor_path(editor)
        else:
            editor_name, editor_path = self.get_best_editor(mode)

            if mode == 'CLI' and editor_path is None:
                print("❌ No CLI editor available")
                return 1

        # Open file
        if mode == 'CLI':
            try:
                return subprocess.run([editor_path, filepath]).returncode
            except Exception as e:
                print(f"❌ Failed to open editor: {e}")
                return 1

        elif mode == 'WEB':
            # Web mode - use ServerManager to start typo
            from extensions.core.server_manager import ServerManager
            server_mgr = ServerManager()

            # Check if typo is installed
            web_dir = Path('extensions/web/typo')
            if not (web_dir / 'package.json').exists():
                return self._handle_typo_not_installed(filepath)

            # Alternative check: extensions/cloned/typo
            alt_dir = Path('extensions/cloned/typo')
            if not web_dir.exists() and alt_dir.exists():
                web_dir = alt_dir

            # Start typo server if not running
            success, message = server_mgr.start_typo_server(port=5173, open_browser=True)

            if success:
                print(message)
                print(f"\n📄 File to edit: {filepath}")
                print("💡 Open this file manually in typo editor")
                print("   (File bridge integration coming in next update)")
                return 0
            else:
                print(message)
                print("\n📝 Falling back to CLI editor...")
                editor_name, editor_path = self.get_best_editor('CLI')
                if editor_path:
                    return subprocess.run([editor_path, filepath]).returncode
                return 1

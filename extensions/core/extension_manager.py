"""
uDOS v1.0.0 - Extension Manager

Handles installation and verification of web extensions.
Called during startup to ensure all extensions are available.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ExtensionManager:
    """Manages uDOS web extensions installation and verification."""

    def __init__(self, root_dir: Optional[Path] = None):
        """
        Initialize the extension manager.

        Args:
            root_dir: Root directory of uDOS installation (defaults to auto-detect)
        """
        if root_dir is None:
            # Auto-detect root (assuming this file is in core/)
            self.root = Path(__file__).parent.parent
        else:
            self.root = Path(root_dir)

        self.extensions_dir = self.root / "extensions"
        self.clone_dir = self.extensions_dir / "clone"
        self.native_dir = self.clone_dir / "native"

    def check_extension_installed(self, extension_name: str) -> bool:
        """
        Check if an extension is installed.

        Args:
            extension_name: Name of the extension (typo, micro, monaspace, etc.)

        Returns:
            True if installed, False otherwise
        """
        checks = {
            'typo': self.clone_dir / 'typo',
            'micro': self.native_dir / 'micro' / 'micro',
            'monaspace': self.clone_dir / 'monaspace-fonts',
            'cmd': self.extensions_dir / 'web' / 'terminal',
        }

        if extension_name in checks:
            path = checks[extension_name]
            return path.exists()

        return False

    def install_extension(self, extension_name: str, quiet: bool = True) -> Tuple[bool, str]:
        """
        Install an extension using its setup script.

        Args:
            extension_name: Name of the extension to install
            quiet: Suppress output (default True)

        Returns:
            Tuple of (success, message)
        """
        script_map = {
            'typo': 'setup_typo.sh',
            'micro': 'setup_micro.sh',
            'monaspace': 'setup_monaspace.sh',
        }

        if extension_name not in script_map:
            return False, f"Unknown extension: {extension_name}"

        script_path = self.extensions_dir / script_map[extension_name]

        if not script_path.exists():
            return False, f"Setup script not found: {script_path}"

        # Set environment variable for auto-install
        env = os.environ.copy()
        env['UDOS_AUTO_INSTALL'] = '1'

        try:
            # Run the setup script
            if quiet:
                result = subprocess.run(
                    ['bash', str(script_path)],
                    cwd=str(self.extensions_dir),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
            else:
                result = subprocess.run(
                    ['bash', str(script_path)],
                    cwd=str(self.extensions_dir),
                    env=env,
                    timeout=300
                )

            if result.returncode == 0:
                return True, f"{extension_name} installed successfully"
            else:
                error_msg = result.stderr if quiet else "Installation failed"
                return False, f"{extension_name} installation failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, f"{extension_name} installation timed out"
        except Exception as e:
            return False, f"{extension_name} installation error: {str(e)}"

    def get_extension_status(self) -> Dict[str, bool]:
        """
        Get installation status of all known extensions.

        Returns:
            Dictionary mapping extension name to installation status
        """
        extensions = ['typo', 'micro', 'monaspace', 'cmd']
        return {ext: self.check_extension_installed(ext) for ext in extensions}

    def install_missing_extensions(self, quiet: bool = True) -> List[Tuple[str, bool, str]]:
        """
        Install all missing extensions.

        Args:
            quiet: Suppress installation output

        Returns:
            List of (extension_name, success, message) tuples
        """
        results = []
        status = self.get_extension_status()

        for ext_name, is_installed in status.items():
            if not is_installed and ext_name != 'cmd':  # cmd is built-in
                if not quiet:
                    print(f"Installing {ext_name}...")
                success, message = self.install_extension(ext_name, quiet=quiet)
                results.append((ext_name, success, message))
                if not quiet:
                    print(f"  {'✓' if success else '✗'} {message}")

        return results

    def verify_all_extensions(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Verify all extensions are installed.

        Returns:
            Tuple of (all_installed, status_dict)
        """
        status = self.get_extension_status()
        all_installed = all(status.values())
        return all_installed, status

    def get_extension_info(self, extension_name: str) -> Dict[str, any]:
        """
        Get detailed information about an extension.

        Args:
            extension_name: Name of the extension

        Returns:
            Dictionary with extension information
        """
        info = {
            'typo': {
                'name': 'Typo Editor',
                'description': 'Modern TypeScript-based text editor',
                'port': 5173,
                'repository': 'https://github.com/heyman333/typo',
                'type': 'node',
            },
            'micro': {
                'name': 'Micro Editor',
                'description': 'Terminal-based text editor',
                'port': 8891,
                'repository': 'https://github.com/zyedidia/micro',
                'type': 'native',
            },
            'monaspace': {
                'name': 'Monaspace Fonts',
                'description': 'Monospaced font family from GitHub',
                'repository': 'https://github.com/githubnext/monaspace',
                'type': 'fonts',
            },
            'cmd': {
                'name': 'CMD Terminal',
                'description': 'uDOS command-line interface',
                'port': 8890,
                'type': 'builtin',
            },
        }

        return info.get(extension_name, {})


def check_and_install_extensions(quiet: bool = False) -> bool:
    """
    Check and install missing extensions at startup.

    Args:
        quiet: Suppress output

    Returns:
        True if all extensions are available, False otherwise
    """
    manager = ExtensionManager()

    if not quiet:
        print("\n🔍 Checking web extensions...")

    # Get current status
    all_installed, status = manager.verify_all_extensions()

    if all_installed:
        if not quiet:
            print("✓ All extensions installed")
        return True

    # Install missing extensions
    if not quiet:
        print("⚠️  Some extensions missing. Installing...")

    results = manager.install_missing_extensions(quiet=quiet)

    # Check final status
    all_installed, final_status = manager.verify_all_extensions()

    if not quiet:
        if all_installed:
            print("✓ All extensions now installed")
        else:
            print("⚠️  Some extensions failed to install:")
            for ext, installed in final_status.items():
                if not installed:
                    print(f"  ✗ {ext}")

    return all_installed


def main():
    """CLI interface for extension manager."""
    import argparse

    parser = argparse.ArgumentParser(description='uDOS Extension Manager')
    parser.add_argument('--check', action='store_true', help='Check extension status')
    parser.add_argument('--install', metavar='EXT', help='Install specific extension')
    parser.add_argument('--install-all', action='store_true', help='Install all missing extensions')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output')

    args = parser.parse_args()

    manager = ExtensionManager()

    if args.check:
        status = manager.get_extension_status()
        print("\nExtension Status:")
        print("─" * 40)
        for ext, installed in status.items():
            symbol = "✓" if installed else "✗"
            status_text = "installed" if installed else "missing"
            print(f"{symbol} {ext:12} {status_text}")

    elif args.install:
        print(f"\nInstalling {args.install}...")
        success, message = manager.install_extension(args.install, quiet=args.quiet)
        print(f"{'✓' if success else '✗'} {message}")

    elif args.install_all:
        check_and_install_extensions(quiet=args.quiet)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

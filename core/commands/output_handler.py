"""
uDOS v1.1.12 - Output/Extension Command Handler

Handles web server management and extension system: POKE, OUTPUT
Manages server lifecycle, extension discovery, installation, and marketplace.
"""

import json
from pathlib import Path
from .base_handler import BaseCommandHandler


class OutputHandler(BaseCommandHandler):
    """Handler for web output and extension management commands."""

    def handle_output(self, params, grid, parser):
        """
        Manage web-based output interfaces (servers) and extensions.
        Implementation for v1.0.11 Extension System Formalization.
        """
        if not params:
            return ("❌ Usage: POKE <command> [name] [options]\n\n"
                   "🖥️  Server Management:\n"
                   "  POKE LIST                      # List all available extensions\n"
                   "  POKE START dashboard           # Start dashboard server\n"
                   "  POKE STATUS                    # Show all server status\n"
                   "  POKE HEALTH                    # Check server health\n"
                   "  POKE RESTART dashboard         # Restart specific server\n"
                   "  POKE STOP teletext            # Stop teletext server\n\n"
                   "🔧 Extension Management:\n"
                   "  POKE DISCOVER                  # Scan for new extensions\n"
                   "  POKE INFO <name>               # Detailed extension information\n"
                   "  POKE INSTALL <name>            # Install extension from source\n"
                   "  POKE UNINSTALL <name>          # Remove extension\n"
                   "  POKE MARKETPLACE               # Browse extension marketplace")

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._handle_output_list()
        elif subcommand == "STATUS":
            extension_name = params[1] if len(params) > 1 else None
            return self._handle_output_status(extension_name)
        elif subcommand == "HEALTH":
            return self._handle_output_health()
        elif subcommand == "START":
            if len(params) < 2:
                return "❌ Usage: POKE START <extension_name> [--port N] [--no-browser]"
            extension_name = params[1]
            options = params[2:] if len(params) > 2 else []
            return self._handle_output_start(extension_name, options)
        elif subcommand == "STOP":
            if len(params) < 2:
                return "❌ Usage: POKE STOP <extension_name>"
            extension_name = params[1]
            return self._handle_output_stop(extension_name)
        elif subcommand == "RESTART":
            if len(params) < 2:
                return "❌ Usage: POKE RESTART <extension_name>"
            extension_name = params[1]
            return self._handle_output_restart(extension_name)
        # New extension management commands for v1.0.11
        elif subcommand == "DISCOVER":
            return self._handle_extension_discover()
        elif subcommand == "INFO":
            if len(params) < 2:
                return "❌ Usage: POKE INFO <extension_name>"
            extension_name = params[1]
            return self._handle_extension_info(extension_name)
        elif subcommand == "INSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE INSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_install(extension_name)
        elif subcommand == "UNINSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE UNINSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_uninstall(extension_name)
        elif subcommand == "MARKETPLACE":
            return self._handle_extension_marketplace()
        else:
            return f"❌ Unknown POKE subcommand: {subcommand}\nUse: START, STOP, STATUS, LIST, HEALTH, RESTART, DISCOVER, INFO, INSTALL, UNINSTALL, or MARKETPLACE"

    # ========================================================================
    # Server Management Methods
    # ========================================================================

    def _handle_output_list(self):
        """List all available web extensions."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            return server_manager.list_servers()
        except Exception as e:
            return f"❌ Error listing extensions: {str(e)}"

    def _handle_output_status(self, extension_name=None):
        """Show status of web extensions."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            return server_manager.get_status(extension_name)
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"

    def _handle_output_start(self, extension_name, options):
        """Start a web extension server."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()

            # Parse options
            port = None
            no_browser = False

            for option in options:
                if option.startswith('--port'):
                    if '=' in option:
                        port = int(option.split('=')[1])
                    else:
                        # Look for next parameter
                        port_index = options.index(option) + 1
                        if port_index < len(options):
                            port = int(options[port_index])
                elif option == '--no-browser':
                    no_browser = True

            return server_manager.start_server(extension_name, port=port, open_browser=not no_browser)
        except Exception as e:
            return f"❌ Error starting {extension_name}: {str(e)}"

    def _handle_output_stop(self, extension_name):
        """Stop a web extension server."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            success, message = server_manager.stop_server(extension_name)
            return f"🛑 {message}" if success else f"⚠️  {message}"
        except Exception as e:
            return f"❌ Error stopping {extension_name}: {str(e)}"

    def _handle_output_health(self):
        """Perform health check on all running servers."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()

            # Get current status
            status_result = server_manager.get_status()

            # Count running/stopped servers
            running_count = status_result.count("✅")
            stopped_count = status_result.count("❌")
            total_count = running_count + stopped_count

            health_report = f"🏥 Server Health Report\n"
            health_report += f"{'='*40}\n"
            health_report += f"📊 Summary:\n"
            health_report += f"   ✅ Running: {running_count}\n"
            health_report += f"   ❌ Stopped: {stopped_count}\n"
            health_report += f"   📈 Total: {total_count}\n\n"

            if running_count == 0:
                health_report += "⚠️  No servers currently running\n"
                health_report += "💡 Tip: Use 'OUTPUT START <name>' to start servers\n"
            elif stopped_count == 0:
                health_report += "✅ All servers are running healthy!\n"
            else:
                health_percentage = (running_count / total_count) * 100 if total_count > 0 else 0
                health_report += f"📊 System Health: {health_percentage:.1f}%\n"

                if health_percentage >= 80:
                    health_report += "✅ System health is good\n"
                elif health_percentage >= 50:
                    health_report += "⚠️  System health is moderate\n"
                else:
                    health_report += "❌ System health needs attention\n"

            return health_report

        except Exception as e:
            return f"❌ Error checking health: {str(e)}"

    def _handle_output_restart(self, extension_name):
        """Restart a web extension server."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()

            # Stop the server first
            stop_success, stop_message = server_manager.stop_server(extension_name)

            # Wait a moment for cleanup
            import time
            time.sleep(1)

            # Start the server again
            start_result = server_manager.start_server(extension_name)

            if stop_success or "not running" in stop_message:
                return f"🔄 Restarted {extension_name}:\n🛑 Stop: {stop_message}\n{start_result}"
            else:
                return f"⚠️  Restart {extension_name} (stop failed, attempting start anyway):\n🛑 Stop: {stop_message}\n{start_result}"

        except Exception as e:
            return f"❌ Error restarting {extension_name}: {str(e)}"

    # ========================================================================
    # Extension Management Methods - v1.0.11 Extension System Formalization
    # ========================================================================

    def _handle_extension_discover(self):
        """Discover available extensions in the system and scan for new ones."""
        try:
            discovered = []
            report = "🔍 EXTENSION DISCOVERY REPORT\n" + "="*50 + "\n\n"

            # Scan bundled extensions
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            if bundled_path.exists():
                manifest_path = bundled_path / "version-manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)

                        report += "🎁 BUNDLED EXTENSIONS:\n"
                        for name, info in manifest.get('extensions', {}).items():
                            status = "🟢 Available" if (bundled_path / name).exists() else "🔴 Missing"
                            report += f"  {status} {name} v{info.get('version', 'unknown')}\n"
                            report += f"    📝 {info.get('description', 'No description')}\n"
                            if info.get('port'):
                                report += f"    🌐 Port: {info['port']}\n"
                            report += "\n"
                            discovered.append(name)
                    except Exception as e:
                        report += f"❌ Error reading manifest: {str(e)}\n"

            # Scan cloned extensions
            cloned_path = Path(__file__).parent.parent.parent / "extensions" / "cloned"
            if cloned_path.exists():
                cloned_dirs = [d for d in cloned_path.iterdir() if d.is_dir()]
                if cloned_dirs:
                    report += "\n🌐 CLONED EXTENSIONS:\n"
                    for ext_dir in cloned_dirs:
                        report += f"  📂 {ext_dir.name}\n"
                        # Check for package.json or README
                        if (ext_dir / "package.json").exists():
                            report += f"    📦 Node.js project detected\n"
                        if (ext_dir / "README.md").exists():
                            report += f"    📖 Documentation available\n"
                        discovered.append(ext_dir.name)

            # Check extension manager status
            from extensions.core.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()
            status = ext_mgr.get_extension_status()

            report += "\n🔧 INSTALLATION STATUS:\n"
            for ext, installed in status.items():
                symbol = "✅" if installed else "❌"
                report += f"  {symbol} {ext}\n"

            report += f"\n📊 SUMMARY: {len(discovered)} extensions discovered\n"
            return report

        except Exception as e:
            return f"❌ Error during discovery: {str(e)}"

    def _handle_extension_info(self, extension_name):
        """Get detailed information about a specific extension using enhanced metadata."""
        try:
            # Use the enhanced metadata manager for comprehensive information
            from extensions.core.extension_metadata_manager import ExtensionMetadataManager
            metadata_mgr = ExtensionMetadataManager()

            # Generate comprehensive report
            report = metadata_mgr.generate_extension_report(extension_name)
            return report

        except ImportError:
            # Fallback to basic implementation if metadata manager is not available
            return self._handle_extension_info_basic(extension_name)
        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_info_basic(self, extension_name):
        """Basic extension info implementation (fallback)."""
        try:
            info_report = f"📋 EXTENSION INFO: {extension_name}\n" + "="*50 + "\n\n"

            # Check bundled extensions first
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            manifest_path = bundled_path / "version-manifest.json"

            extension_found = False

            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)

                    if extension_name in manifest.get('extensions', {}):
                        ext_info = manifest['extensions'][extension_name]
                        extension_found = True

                        info_report += f"📦 Type: Bundled Extension\n"
                        info_report += f"📌 Version: {ext_info.get('version', 'unknown')}\n"
                        info_report += f"📝 Description: {ext_info.get('description', 'No description')}\n"

                        if ext_info.get('port'):
                            info_report += f"🌐 Default Port: {ext_info['port']}\n"

                        if ext_info.get('dependencies'):
                            info_report += f"📚 Dependencies: {', '.join(ext_info['dependencies'])}\n"

                        # Check installation status
                        ext_path = bundled_path / extension_name
                        if ext_path.exists():
                            info_report += f"✅ Status: Installed\n"
                            info_report += f"📂 Location: {ext_path}\n"
                        else:
                            info_report += f"❌ Status: Not Installed\n"

                except Exception as e:
                    info_report += f"❌ Error reading manifest: {str(e)}\n"

            # Check cloned extensions
            if not extension_found:
                cloned_path = Path(__file__).parent.parent.parent / "extensions" / "cloned" / extension_name
                if cloned_path.exists():
                    extension_found = True
                    info_report += f"📦 Type: Cloned Extension\n"
                    info_report += f"✅ Status: Available\n"
                    info_report += f"📂 Location: {cloned_path}\n"

                    # Check for package.json
                    package_json = cloned_path / "package.json"
                    if package_json.exists():
                        try:
                            with open(package_json, 'r') as f:
                                pkg = json.load(f)
                            info_report += f"📝 Name: {pkg.get('name', 'unknown')}\n"
                            info_report += f"📌 Version: {pkg.get('version', 'unknown')}\n"
                            info_report += f"📄 Description: {pkg.get('description', 'No description')}\n"
                        except Exception:
                            pass

                    # Check for README
                    readme = cloned_path / "README.md"
                    if readme.exists():
                        info_report += f"📖 Documentation: README.md available\n"

            if not extension_found:
                info_report += f"❌ Extension '{extension_name}' not found.\n"
                info_report += f"💡 Use 'POKE DISCOVER' to see all available extensions.\n"

            return info_report

        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_install(self, extension_name):
        """Install an extension."""
        try:
            from extensions.core.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()

            install_report = f"📦 INSTALLING EXTENSION: {extension_name}\n" + "="*50 + "\n\n"

            # Check if already installed
            if ext_mgr.check_extension_installed(extension_name):
                return f"✅ Extension '{extension_name}' is already installed.\n💡 Use 'POKE RESTART {extension_name}' to restart if needed."

            install_report += f"🔄 Installing {extension_name}...\n"

            success, message = ext_mgr.install_extension(extension_name, quiet=False)

            if success:
                install_report += f"✅ SUCCESS: {message}\n"
                install_report += f"🚀 Extension '{extension_name}' is now available.\n"
                install_report += f"💡 Use 'POKE START {extension_name}' to launch it."
            else:
                install_report += f"❌ FAILED: {message}\n"
                install_report += f"💡 Use 'POKE DISCOVER' to see available extensions."

            return install_report

        except Exception as e:
            return f"❌ Error installing extension: {str(e)}"

    def _handle_extension_uninstall(self, extension_name):
        """Uninstall an extension (placeholder for future implementation)."""
        return (f"🚧 UNINSTALL FEATURE COMING SOON\n\n"
                f"Extension uninstallation for '{extension_name}' is not yet implemented.\n"
                f"This feature will be added in a future version.\n\n"
                f"📝 For now, you can manually remove extension files from:\n"
                f"   • extensions/bundled/web/{extension_name}/\n"
                f"   • extensions/cloned/{extension_name}/\n\n"
                f"⚠️  CAUTION: Manual removal may affect system stability.")

    def _handle_extension_marketplace(self):
        """Browse the extension marketplace (placeholder for future implementation)."""
        return ("🏪 EXTENSION MARKETPLACE\n" + "="*30 + "\n\n"
                "🚧 COMING SOON: Extension Marketplace\n\n"
                "The extension marketplace will provide:\n"
                "• 🌐 Community-contributed extensions\n"
                "• 🔍 Search and discovery features\n"
                "• ⭐ Ratings and reviews\n"
                "• 🔒 Security verification\n"
                "• 📦 One-click installation\n"
                "• 🔄 Automatic updates\n\n"
                "🎯 CURRENT EXTENSIONS:\n"
                "Use 'POKE DISCOVER' to see available extensions\n"
                "Use 'POKE INFO <name>' for detailed information\n\n"
                "📧 Want to contribute? Contact the uDOS development team!")

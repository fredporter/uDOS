"""
uDOS v1.0.0 - Repair Handler

Handles all repair, upgrade, and system maintenance operations:
- System health checks and repairs
- Extension management (clone, install)
- Python/pip/venv upgrades
- Git repository maintenance
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from .base_handler import BaseCommandHandler


class RepairHandler(BaseCommandHandler):
    """Handles system repair, maintenance, and upgrade operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle_repair(self, params, grid, parser):
        """
        System health check and repair with extension management and upgrades.
        Supports multiple modes: check, auto, report, pull, upgrade options, clone extensions.

        Args:
            params: List with optional component/mode flag
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Repair results or health report
        """
        from core.services.uDOS_startup import (
            check_system_health,
            repair_system,
            get_health_report,
            quick_health_check,
            repair_git_pull,
            repair_pip_upgrade
        )

        # Normalize component (remove -- prefix if present)
        component = params[0] if params else None
        if component and component.startswith('--'):
            component = component[2:]

        # Parse flags
        check_only = component in ("", "check", None)
        auto_repair = component == "auto"
        full_report = component == "report"
        git_pull = component == "pull"
        pip_upgrade = component == "upgrade-pip"

        # New upgrade options
        python_upgrade = component == "upgrade-python"
        venv_upgrade = component == "upgrade-venv"
        all_upgrades = component == "upgrade-all"

        # Extension management flags
        install_extensions = component == "install-extensions"
        clone_extension = component and component.startswith("clone")

        # Handle extension cloning
        if install_extensions:
            return self._repair_install_all_extensions()

        if clone_extension:
            # Extract extension name (e.g., "clone-micro" -> "micro")
            if component == "clone":
                return self._repair_show_clone_options()
            extension_name = component.replace("clone-", "").replace("clone_", "")
            return self._repair_clone_extension(extension_name)

        # Handle upgrade modes
        if python_upgrade:
            return self._upgrade_python()

        if venv_upgrade:
            return self._upgrade_venv()

        if all_upgrades:
            return self._upgrade_all_components()

        # Handle special repair modes
        if git_pull:
            success, message = repair_git_pull(verbose=True)
            if success:
                return f"✨ {message}\n\n💡 Run REBOOT to apply changes"
            else:
                return f"❌ {message}"

        if pip_upgrade:
            success, message = repair_pip_upgrade(verbose=True)
            return f"{'✨' if success else '❌'} {message}"

        # Run full health check
        health = check_system_health(verbose=False, return_dict=False)

        # Check-only mode
        if check_only:
            result = "╔" + "═"*58 + "╗\n"
            result += "║" + "🔧 SYSTEM HEALTH CHECK".center(58) + "║\n"
            result += "╚" + "═"*58 + "╝\n\n"

            if health.is_healthy():
                result += "✅ All systems functioning optimally\n"
            elif health.has_warnings():
                result += f"⚠️  {health.get_warnings_count()} gentle warning(s) detected\n"
                result += f"💡 Run 'REPAIR' to harmonize the system\n\n"
            else:
                result += f"❌ {health.get_issues_count()} issue(s) require attention\n"
                result += f"💡 Run 'REPAIR' to restore balance\n\n"

            # Add sandbox health check
            result += self._check_sandbox_health()

            # Show quick summary with softer language
            for check in health.checks:
                if check.is_healthy():
                    status_icon = "✨"
                    status_text = "functioning well"
                elif check.passed:
                    status_icon = "⚠️ "
                    status_text = "needs minor adjustment"
                else:
                    status_icon = "🔧"
                    status_text = "requires attention"

                result += f"{status_icon} {check.name}: {status_text}\n"

                # Show first issue or warning with gentle language
                if check.issues and len(check.issues) > 0:
                    result += f"   └─ {check.issues[0]}\n"
                elif check.warnings and len(check.warnings) > 0:
                    result += f"   └─ {check.warnings[0]}\n"

            # Add extension status and upgrade suggestions
            result += self._repair_check_extensions()
            result += self._check_upgrade_opportunities()
            return result

        # Full report mode
        if full_report:
            return get_health_report(health, include_warnings=True)

        # Auto-repair mode (default) with softer messaging
        if auto_repair or component == "ALL" or component is None:
            result = "╔" + "═"*58 + "╗\n"
            result += "║" + "🌟 SYSTEM HARMONY RESTORATION".center(58) + "║\n"
            result += "╚" + "═"*58 + "╝\n\n"

            # Attempt repairs
            repaired_health = repair_system(health, verbose=False)

            if repaired_health.repaired_issues:
                result += "✨ Harmony restored through:\n"
                for repair in repaired_health.repaired_issues:
                    result += f"  • {repair}\n"
                result += "\n"

            # Re-check health with gentler language
            if repaired_health.is_healthy():
                result += "✅ System energy flows smoothly once more\n"
            elif repaired_health.has_warnings():
                result += f"⚠️  {repaired_health.get_warnings_count()} minor imbalance(s) remain\n"
                result += "💡 These are gentle suggestions, not critical issues\n"
            else:
                result += f"🔧 {repaired_health.get_issues_count()} area(s) still need care\n"
                result += "💡 Run 'REPAIR --report' for deeper insight\n"

            return result

        # Unknown component with helpful suggestions
        return (f"❓ Unknown repair component: {component}\n\n"
                f"🌟 Available healing options:\n"
                f"  REPAIR                 - Auto-harmonize system\n"
                f"  REPAIR --check         - Gentle health assessment\n"
                f"  REPAIR --report        - Detailed system insight\n"
                f"  REPAIR --pull          - Synchronize with origin\n"
                f"  REPAIR --upgrade-pip   - Refresh package manager\n"
                f"  REPAIR --upgrade-python - Update Python to latest\n"
                f"  REPAIR --upgrade-venv  - Refresh virtual environment\n"
                f"  REPAIR --upgrade-all   - Update all components\n"
                f"  REPAIR --install-extensions - Clone all recommended extensions\n"
                f"  REPAIR --clone micro   - Clone specific extension\n"
                f"  REPAIR --clone typo    - Clone typo editor\n"
                f"  REPAIR --clone cmd     - Clone web terminal\n"
                f"  REPAIR --clone monaspace - Clone Monaspace fonts\n")

    def _upgrade_python(self):
        """Check for and optionally upgrade Python."""
        result = "╔" + "═"*68 + "╗\n"
        result += "║" + "🐍 PYTHON UPGRADE CHECK".center(68) + "║\n"
        result += "╚" + "═"*68 + "╝\n\n"

        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        result += f"Current Python version: {current_version}\n"

        try:
            # Check latest Python version (simplified check)
            system = platform.system().lower()

            if system == "darwin":  # macOS
                result += "\n🍎 macOS Python Upgrade Options:\n"
                result += "  Homebrew: brew upgrade python\n"
                result += "  Official: Download from python.org\n"
                result += "  pyenv: pyenv install 3.11.x\n"

                # Check if homebrew is available
                try:
                    subprocess.run(['brew', '--version'], capture_output=True, check=True)
                    result += "\n✅ Homebrew detected - can upgrade with: brew upgrade python\n"
                except (subprocess.CalledProcessError, FileNotFoundError):
                    result += "\n⚠️  Homebrew not found - install from https://brew.sh\n"

            elif system == "linux":
                result += "\n🐧 Linux Python Upgrade Options:\n"
                result += "  apt: sudo apt update && sudo apt install python3\n"
                result += "  yum: sudo yum update python3\n"
                result += "  pyenv: pyenv install 3.11.x\n"

            else:
                result += "\n🪟 Windows Python Upgrade Options:\n"
                result += "  Official installer: Download from python.org\n"
                result += "  Microsoft Store: Search for Python\n"
                result += "  Chocolatey: choco upgrade python\n"

            result += "\n💡 After upgrading Python:\n"
            result += "  1. Update virtual environment: REPAIR --upgrade-venv\n"
            result += "  2. Reinstall packages: pip install -r requirements.txt\n"
            result += "  3. Restart uDOS: REBOOT\n"

        except Exception as e:
            result += f"\n❌ Error checking Python upgrade options: {e}\n"

        return result

    def _upgrade_venv(self):
        """Upgrade virtual environment."""
        result = "╔" + "═"*68 + "╗\n"
        result += "║" + "🏗️ VIRTUAL ENVIRONMENT UPGRADE".center(68) + "║\n"
        result += "╚" + "═"*68 + "╝\n\n"

        venv_path = Path('.venv')

        if not venv_path.exists():
            result += "⚠️  No virtual environment found at .venv\n"
            result += "\n🌱 Create new virtual environment:\n"
            result += f"  python{sys.version_info.major}.{sys.version_info.minor} -m venv .venv\n"
            result += "  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows\n"
            result += "  pip install -r requirements.txt\n"
            return result

        result += "✅ Virtual environment found\n"

        try:
            # Check current venv Python version
            venv_python = venv_path / 'bin' / 'python'
            if not venv_python.exists():
                venv_python = venv_path / 'Scripts' / 'python.exe'  # Windows

            if venv_python.exists():
                venv_version_result = subprocess.run(
                    [str(venv_python), '--version'],
                    capture_output=True,
                    text=True
                )
                venv_version = venv_version_result.stdout.strip().replace('Python ', '')
                result += f"Virtual environment Python: {venv_version}\n"
                result += f"System Python: {sys.version.split()[0]}\n"

                if venv_version != sys.version.split()[0]:
                    result += "\n🔄 Virtual environment Python differs from system Python\n"
                    result += "\n💡 To upgrade virtual environment:\n"
                    result += "  1. Backup requirements: pip freeze > requirements_backup.txt\n"
                    result += "  2. Remove old venv: rm -rf .venv\n"
                    result += f"  3. Create new venv: python{sys.version_info.major}.{sys.version_info.minor} -m venv .venv\n"
                    result += "  4. Activate: source .venv/bin/activate\n"
                    result += "  5. Reinstall: pip install -r requirements.txt\n"
                    result += "\n⚠️  This will recreate the entire virtual environment\n"
                else:
                    result += "\n✅ Virtual environment is using current system Python\n"
                    result += "💡 Just update packages: pip install --upgrade pip setuptools wheel\n"

        except Exception as e:
            result += f"\n❌ Error checking virtual environment: {e}\n"

        return result

    def _upgrade_all_components(self):
        """Upgrade all system components."""
        result = "╔" + "═"*68 + "╗\n"
        result += "║" + "🚀 COMPREHENSIVE SYSTEM UPGRADE".center(68) + "║\n"
        result += "╚" + "═"*68 + "╝\n\n"

        components = []

        # 1. Git pull
        result += "🔄 Updating uDOS repository...\n"
        try:
            from core.services.uDOS_startup import repair_git_pull
            success, message = repair_git_pull(verbose=False)
            if success:
                result += f"✅ Repository updated: {message}\n"
                components.append("✅ Git repository")
            else:
                result += f"⚠️  Repository update: {message}\n"
                components.append("⚠️  Git repository")
        except Exception as e:
            result += f"❌ Git update failed: {e}\n"
            components.append("❌ Git repository")

        # 2. Pip upgrade
        result += "\n📦 Upgrading pip...\n"
        try:
            from core.services.uDOS_startup import repair_pip_upgrade
            success, message = repair_pip_upgrade(verbose=False)
            if success:
                result += f"✅ Pip upgraded: {message}\n"
                components.append("✅ Pip package manager")
            else:
                result += f"⚠️  Pip upgrade: {message}\n"
                components.append("⚠️  Pip package manager")
        except Exception as e:
            result += f"❌ Pip upgrade failed: {e}\n"
            components.append("❌ Pip package manager")

        # 3. Package updates
        result += "\n📚 Checking for package updates...\n"
        try:
            outdated_result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--outdated'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if outdated_result.returncode == 0:
                outdated_packages = outdated_result.stdout.strip().split('\n')[2:]  # Skip header
                if outdated_packages and outdated_packages[0]:
                    result += f"📋 {len(outdated_packages)} packages have updates available\n"
                    result += "💡 To upgrade all: pip install --upgrade -r requirements.txt\n"
                    components.append(f"⚠️  {len(outdated_packages)} packages need updates")
                else:
                    result += "✅ All packages are up to date\n"
                    components.append("✅ Python packages")
            else:
                result += "⚠️  Could not check for package updates\n"
                components.append("⚠️  Python packages")
        except Exception as e:
            result += f"❌ Package check failed: {e}\n"
            components.append("❌ Python packages")

        # 4. Extension updates
        result += "\n🔌 Checking extensions...\n"
        missing_extensions = []
        for ext_name in ['micro', 'typo', 'cmd', 'monaspace']:
            if not self._check_extension_installed(ext_name):
                missing_extensions.append(ext_name)

        if missing_extensions:
            result += f"📦 {len(missing_extensions)} extensions not installed: {', '.join(missing_extensions)}\n"
            result += "💡 Install with: REPAIR --install-extensions\n"
            components.append(f"⚠️  {len(missing_extensions)} extensions missing")
        else:
            result += "✅ All recommended extensions installed\n"
            components.append("✅ Extensions")

        # Summary
        result += "\n" + "="*60 + "\n"
        result += "📊 UPGRADE SUMMARY:\n"
        for component in components:
            result += f"  {component}\n"

        result += "\n💡 Recommended next steps:\n"
        result += "  1. Review any warnings above\n"
        result += "  2. Install missing extensions if needed\n"
        result += "  3. Restart uDOS: REBOOT\n"

        return result

    def _check_upgrade_opportunities(self):
        """Check for available upgrades."""
        result = "\n🔄 Upgrade Opportunities:\n"

        opportunities = []

        # Check Python version (simplified)
        current_py = f"{sys.version_info.major}.{sys.version_info.minor}"
        if sys.version_info.minor < 11:  # Assuming 3.11+ is desired
            opportunities.append(f"Python {current_py} → 3.11+ available")

        # Check pip
        try:
            pip_result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if pip_result.returncode == 0:
                opportunities.append("pip updates available (REPAIR --upgrade-pip)")
        except:
            pass

        if opportunities:
            for opp in opportunities:
                result += f"  🔄 {opp}\n"
            result += f"  💡 Upgrade all: REPAIR --upgrade-all\n"
        else:
            result += "  ✅ No immediate upgrades detected\n"

        return result

    def _repair_show_clone_options(self):
        """Show available extensions to clone."""
        result = "╔" + "═"*68 + "╗\n"
        result += "║" + "🌟 AVAILABLE EXTENSIONS TO CLONE".center(68) + "║\n"
        result += "╚" + "═"*68 + "╝\n\n"

        extensions = {
            'micro': {
                'name': 'Micro Editor',
                'description': 'Modern terminal text editor with mouse support',
                'status': self._check_extension_installed('micro')
            },
            'typo': {
                'name': 'Typo Editor',
                'description': 'Web-based markdown editor with live preview',
                'status': self._check_extension_installed('typo')
            },
            'cmd': {
                'name': 'Web Terminal',
                'description': 'Browser-based terminal interface',
                'status': self._check_extension_installed('cmd')
            },
            'monaspace': {
                'name': 'Monaspace Fonts',
                'description': 'Monospaced font family from GitHub',
                'status': self._check_extension_installed('monaspace')
            }
        }

        for ext_id, ext_info in extensions.items():
            status_icon = "✅" if ext_info['status'] else "⭕"
            status_text = "installed" if ext_info['status'] else "available to clone"

            result += f"{status_icon} {ext_info['name']}\n"
            result += f"    {ext_info['description']}\n"
            result += f"    Status: {status_text}\n"
            if not ext_info['status']:
                result += f"    Clone: REPAIR --clone {ext_id}\n"
            result += "\n"

        result += "💡 Use 'REPAIR --install-extensions' to clone all missing extensions\n"
        return result

    def _repair_install_all_extensions(self):
        """Clone all recommended extensions if not already present."""
        result = "╔" + "═"*68 + "╗\n"
        result += "║" + "🌟 CLONING RECOMMENDED EXTENSIONS".center(68) + "║\n"
        result += "╚" + "═"*68 + "╝\n\n"

        extensions = ['micro', 'typo', 'cmd', 'monaspace']
        installed = []
        cloned = []
        failed = []

        for ext_name in extensions:
            if self._check_extension_installed(ext_name):
                installed.append(ext_name)
                result += f"✅ {ext_name}: already present\n"
            else:
                result += f"🌱 {ext_name}: cloning...\n"
                success = self._clone_extension(ext_name)
                if success:
                    cloned.append(ext_name)
                    result += f"✨ {ext_name}: successfully cloned\n"
                else:
                    failed.append(ext_name)
                    result += f"❌ {ext_name}: clone failed\n"

        result += "\n"
        if cloned:
            result += f"🎉 Successfully cloned: {', '.join(cloned)}\n"
        if installed:
            result += f"✅ Already installed: {', '.join(installed)}\n"
        if failed:
            result += f"⚠️  Clone failed: {', '.join(failed)}\n"
            result += "💡 Check network connection and try individual clones\n"

        return result

    def _repair_clone_extension(self, extension_name):
        """Clone a specific extension."""
        if self._check_extension_installed(extension_name):
            return f"✅ {extension_name} is already installed\n💡 Use REPAIR --check to verify system status"

        result = f"🌱 Cloning {extension_name}...\n\n"
        success = self._clone_extension(extension_name)

        if success:
            result += f"✨ {extension_name} successfully cloned!\n"
            result += f"💡 Extension ready for use\n"
        else:
            result += f"❌ Failed to clone {extension_name}\n"
            result += f"💡 Check network connection and try again\n"

        return result

    def _repair_check_extensions(self):
        """Check status of all extensions."""
        result = "\n🔌 Extension Status:\n"

        extensions = ['micro', 'typo', 'cmd', 'monaspace']
        for ext_name in extensions:
            if self._check_extension_installed(ext_name):
                result += f"  ✅ {ext_name}: ready\n"
            else:
                result += f"  ⭕ {ext_name}: not installed (REPAIR --clone {ext_name})\n"

        return result

    def _check_extension_installed(self, extension_name):
        """Check if an extension is installed."""
        checks = {
            'micro': Path('extensions/clone/native/micro/micro').exists(),
            'typo': Path('extensions/clone/web/typo/package.json').exists(),
            'cmd': Path('extensions/clone/web/cmd/package.json').exists(),
            'monaspace': Path('extensions/clone/monaspace-fonts/fonts').exists()
        }
        return checks.get(extension_name, False)

    def _clone_extension(self, extension_name):
        """Clone an extension using its setup script."""
        setup_scripts = {
            'micro': 'extensions/setup_micro.sh',
            'typo': 'extensions/setup_typo.sh',
            'cmd': 'extensions/setup_cmd.sh',
            'monaspace': 'extensions/setup_monaspace.sh'
        }

        script_path = setup_scripts.get(extension_name)
        if not script_path or not Path(script_path).exists():
            return False

        try:
            # Set environment variable for auto-install
            env = os.environ.copy()
            env['UDOS_AUTO_INSTALL'] = '1'

            # Run the setup script
            result = subprocess.run(
                ['bash', script_path],
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )

            return result.returncode == 0

        except Exception as e:
            return False

    def _check_sandbox_health(self):
        """Check sandbox health using sandbox_handler.repair_sandbox()."""
        try:
            from core.commands.sandbox_handler import SandboxHandler
            sandbox_handler = SandboxHandler()
            health_report = sandbox_handler.repair_sandbox()

            result = "\n🗂️  Sandbox Health:\n"

            if health_report['status'] == 'healthy':
                result += "  ✅ Sandbox structure is optimal\n"
            elif health_report['status'] == 'repaired':
                result += f"  🔧 {len(health_report['repairs'])} repair(s) applied:\n"
                for repair in health_report['repairs']:
                    result += f"    • {repair}\n"
            else:  # 'issues'
                result += f"  ⚠️  {len(health_report['issues'])} issue(s) detected:\n"
                for issue in health_report['issues']:
                    result += f"    • {issue}\n"

            if health_report.get('recommendation'):
                result += f"  💡 {health_report['recommendation']}\n"

            return result

        except Exception as e:
            return f"\n⚠️  Sandbox health check failed: {e}\n"

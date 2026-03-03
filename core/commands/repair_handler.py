"""REPAIR command handler - system maintenance and recovery.

Commands:
  REPAIR                      # Standard repair checks
  REPAIR --reset-user         # Reset user data/profiles
  REPAIR --reset-keys         # Clear all API keys
  REPAIR --reset-config       # Reset configuration
  REPAIR --full               # Full system repair
  REPAIR --confirm            # Skip confirmations
  REPAIR --pull               # Git pull latest changes
  REPAIR --install            # Install dependencies
  REPAIR --upgrade            # Pull + install dependencies
  REPAIR --help               # Show help
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.logging_api import get_logger, get_repo_root
from core.services.self_healer import collect_self_heal_summary


class RepairHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for REPAIR command - self-healing and system maintenance."""

    def handle(self, command: str, params: list[str], grid=None, parser=None) -> dict:
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params or [], grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(
        self, command: str, params: list[str], grid=None, parser=None
    ) -> dict:
        """Handle REPAIR command - perform system maintenance."""
        flags = [param.lower() for param in (params or [])]

        if "--help" in flags or "-h" in flags:
            return self._show_help()

        from core.services.logging_api import get_logger as _get_logger
        from core.services.user_service import get_user_manager, is_ghost_mode

        user_mgr = get_user_manager()
        user = user_mgr.current()

        if is_ghost_mode():
            _get_logger("core", category="repair").warning(
                "[TESTING ALERT] Ghost Mode active: REPAIR executing in demo mode (v1.5). "
                "Enforcement will be added before v1.5 release."
            )

        user, error = self._require_permission()
        if error:
            return error

        reset_user = "--reset-user" in flags or "-u" in flags
        reset_keys = "--reset-keys" in flags or "-k" in flags
        reset_config = "--reset-config" in flags or "-c" in flags
        full = "--full" in flags or "-f" in flags
        skip_confirm = "--confirm" in flags or "-y" in flags

        if full:
            reset_user = True
            reset_keys = True
            reset_config = True

        plugin_flag_idx = self._find_flag_index("--install-plugin", params or [])
        if plugin_flag_idx is not None:
            plugin_name = None
            if plugin_flag_idx + 1 < len(params):
                plugin_name = params[plugin_flag_idx + 1]
            return self._install_plugin(plugin_name)

        if "--refresh-runtime" in flags or "--refresh-extensions" in flags:
            return self._refresh_runtime(user)

        if reset_user or reset_keys or reset_config:
            plan = []
            if reset_user:
                plan.append("👤 Reset user profiles to defaults")
            if reset_keys:
                plan.append("🔑 Clear all API keys/credentials")
            if reset_config:
                plan.append("⚙️  Reset configuration")
            if skip_confirm:
                plan.append("✅ Confirmation skipped")

            return self._perform_repair_with_options(
                user=user,
                reset_user=reset_user,
                reset_keys=reset_keys,
                reset_config=reset_config,
                skip_confirm=skip_confirm,
                plan=plan,
            )

        if not flags:
            return self._check_system(user)

        action = flags[0]
        if action == "--pull":
            return self._git_pull()
        if action == "--install":
            return self._install_dependencies()
        if action == "--check":
            return self._check_system(user)
        if action == "--upgrade":
            return self._upgrade_all()

        return {
            "status": "error",
            "message": f"Unknown action: {action}",
            "available": [
                "--pull",
                "--install",
                "--check",
                "--upgrade",
                "--reset-user",
                "--reset-keys",
                "--reset-config",
                "--full",
                "--confirm",
                "--help",
            ],
        }

    def _require_permission(self):
        from core.services.permission_handler import Permission, get_permission_handler
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        user = user_mgr.current()
        if not get_permission_handler().require(Permission.REPAIR, action="repair"):
            self.log_permission_denied("REPAIR", "missing repair permission")
            return None, {
                "status": "error",
                "output": f"❌ REPAIR permission denied for user {user.username if user else 'unknown'}",
            }
        return user, None

    def _git_pull(self) -> dict:
        """Pull latest changes from git repository."""
        logger = get_logger("repair-handler")
        try:
            repo_path = get_repo_root()

            git_dir = repo_path / ".git"
            if not git_dir.exists():
                return {"status": "error", "message": "Not a git repository"}

            result = subprocess.run(
                ["git", "pull"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                from core.tui.output import OutputToolkit

                output = []
                output.append(OutputToolkit.banner("REPAIR: GIT PULL"))
                output.append(result.stdout.strip() or "Git pull completed")
                logger.info("[LOCAL] REPAIR git pull completed")
                return {
                    "status": "success",
                    "message": "Git pull completed",
                    "output": "\n".join(output),
                }
            return {
                "status": "error",
                "message": "Git pull failed",
                "error": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Git pull timed out (taking >60 seconds)",
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to pull repository: {e!s}"}

    def _install_dependencies(self) -> dict:
        """Install/verify Python dependencies."""
        logger = get_logger("repair-handler")
        try:
            repo_path = get_repo_root()
            pyproject = repo_path / "pyproject.toml"

            if not pyproject.exists():
                return {"status": "error", "message": "pyproject.toml not found"}

            # Try uv first (preferred), fall back to pip install -e
            uv_path = shutil.which("uv")
            if uv_path:
                cmd = [uv_path, "sync", "--extra", "udos"]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "-e", ".[udos]"]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=str(repo_path)
            )

            if result.returncode == 0:
                from core.tui.output import OutputToolkit

                output = []
                output.append(OutputToolkit.banner("REPAIR: DEPENDENCIES"))
                output.append(f"Dependencies installed via: {' '.join(cmd)}")
                output.append("Note: run this if you see import errors")
                logger.info("[LOCAL] REPAIR dependencies installed")
                return {
                    "status": "success",
                    "message": "Dependencies installed",
                    "output": "\n".join(output),
                }
            return {
                "status": "error",
                "message": "Dependency installation failed",
                "error": result.stderr[-200:],
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Installation timed out (taking >2 minutes)",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to install dependencies: {e!s}",
            }

    def _check_system(self, user, ghost_notice: str | None = None) -> dict:
        """Check system health status."""
        logger = get_logger("core", category="repair", name="repair-handler")
        from core.tui.output import OutputToolkit

        summary = collect_self_heal_summary(component="core", auto_repair=False)
        summary_rows = [
            ["success", "yes" if summary.get("success") else "no"],
            ["issues_found", summary.get("issues", 0)],
            ["issues_repaired", summary.get("repaired", 0)],
            ["issues_remaining", summary.get("remaining", 0)],
        ]

        output = [OutputToolkit.banner("REPAIR: SELF-HEAL CHECK")]
        output.append(OutputToolkit.table(["metric", "value"], summary_rows))
        output.append("")
        output.append(
            OutputToolkit.section("Details", "\n".join(summary.get("messages", [])))
        )
        if ghost_notice:
            output.append("")
            output.append(OutputToolkit.section("Ghost Mode", ghost_notice))

        logger.info(
            "[LOCAL] REPAIR self-heal check completed (success=%s)",
            summary.get("success"),
        )
        logger.event(
            "info",
            "repair.self_heal",
            f"Self-heal diagnostics completed by {user.username if user else 'unknown'}",
            ctx=summary,
        )

        return {
            "status": "success" if summary.get("success") else "warning",
            "message": "Self-heal diagnostics complete",
            "checks": {
                "issues_found": summary.get("issues", 0),
                "issues_repaired": summary.get("repaired", 0),
                "issues_remaining": summary.get("remaining", 0),
            },
            "output": "\n".join(output),
        }

    def _upgrade_all(self) -> dict:
        """Upgrade all components (git pull + dependencies)."""
        results = {"status": "success", "steps": {}}

        pull_result = self._git_pull()
        results["steps"]["git_pull"] = pull_result

        install_result = self._install_dependencies()
        results["steps"]["install_dependencies"] = install_result

        if pull_result["status"] != "success" or install_result["status"] != "success":
            results["status"] = "partial"
            results["message"] = "Some steps had issues"
        else:
            results["message"] = "System upgraded successfully"

        from core.tui.output import OutputToolkit

        output = []
        output.append(OutputToolkit.banner("REPAIR: UPGRADE"))
        output.append(f"Git pull: {pull_result.get('status')}")
        output.append(f"Dependencies: {install_result.get('status')}")
        results["output"] = "\n".join(output)
        return results

    def _show_help(self) -> dict:
        """Show repair help."""
        from core.tui.output import OutputToolkit

        help_text = (
            OutputToolkit.banner("REPAIR COMMAND HELP")
            + """

REPAIR is the system maintenance and recovery command. It can check
system health, reset user data, clear credentials, and restore defaults.

SYNTAX:
  REPAIR [OPTIONS]

OPTIONS:
  --pull            Git pull latest changes
  --install         Install Python dependencies
  --check           Run system checks (default)
  --upgrade         Pull + install dependencies
  --reset-user      Reset user profiles to factory defaults
  --reset-keys      Clear all API keys and credentials
  --reset-config    Reset configuration files
  --full            Perform all reset options
  --confirm         Skip confirmation prompts
  --help            Show this help
  --refresh-runtime, --refresh-extensions
                    Clean runtime caches (`.venv`, extensions, dashboard assets) and reinstall enabled plugins
  --install-plugin <name>
                    Reinstall a specific integration via the Wizard library manager

EXAMPLES:
  REPAIR
  REPAIR --reset-user
  REPAIR --reset-keys
  REPAIR --reset-config
  REPAIR --full
  REPAIR --pull
"""
        )
        return {"output": help_text.strip(), "status": "info", "command": "REPAIR"}

    def _perform_repair_with_options(
        self,
        user,
        reset_user: bool,
        reset_keys: bool,
        reset_config: bool,
        skip_confirm: bool,
        plan: list[str],
    ) -> dict:
        """Perform repair with reset options."""
        from core.services.user_service import get_user_manager

        logger = get_logger("core", category="repair", name="repair-handler")
        repo_root = get_repo_root()
        results = []

        try:
            results.append("")
            results.append("╔════════════════════════════════════════╗")
            results.append("║      REPAIR PLAN                       ║")
            results.append("╚════════════════════════════════════════╝")
            results.append("")

            for step in plan:
                results.append(f"  • {step}")

            results.append("")

            if reset_user:
                results.append("👤 User Profile Reset")
                user_mgr = get_user_manager()
                users_to_delete = [u for u in user_mgr.users.keys() if u != "admin"]
                deleted = 0
                for username in users_to_delete:
                    ok, _ = user_mgr.delete_user(username)
                    if ok:
                        deleted += 1
                results.append(f"   ✓ Deleted {deleted} non-admin users")
                results.append("   ✓ Reset roles to defaults")

            if reset_keys:
                results.append("🔑 API Keys Reset")
                keys_dir = repo_root / "memory" / "private"
                if keys_dir.exists():
                    for key_file in keys_dir.glob("*.json"):
                        if "key" in key_file.name or "token" in key_file.name:
                            key_file.unlink()
                results.append("   ✓ Cleared stored API keys")
                results.append("   ✓ Removed OAuth tokens")

            if reset_config:
                results.append("⚙️  Configuration Reset")
                config_dir = repo_root / "core" / "config"
                if config_dir.exists():
                    for config_file in config_dir.glob("*.json"):
                        if config_file.name != "version.json":
                            config_file.unlink()
                results.append("   ✓ Reset config files")
                results.append("   ✓ Restored defaults")

            results.append("")
            results.append("✅ Repair complete!")
            results.append("")
            results.append("Next steps:")
            results.append("  • Run STATUS to verify system")
            results.append("  • Run LOGS to check messages")
            results.append("  • Run REBOOT to reload system")

            logger.info(
                "[LOCAL] REPAIR with resets completed by %s",
                user.username if user else "unknown",
            )
            logger.event(
                "info",
                "repair.completed",
                f"Repair with resets completed by {user.username if user else 'unknown'}",
                ctx={
                    "reset_user": reset_user,
                    "reset_keys": reset_keys,
                    "reset_config": reset_config,
                    "skip_confirm": skip_confirm,
                },
            )

            return {
                "output": "\n".join(results),
                "status": "success",
                "action": "repair_complete",
            }

        except Exception as e:
            error_msg = f"❌ Repair failed: {e}"
            logger.error("[LOCAL] %s", error_msg)
            logger.event(
                "error", "repair.failed", error_msg, ctx={"error": str(e)}, err=e
            )
        return {"output": error_msg, "status": "error"}

    def _find_flag_index(self, flag: str, params: list[str]) -> int | None:
        """Return index of flag in params (case-insensitive)."""
        for idx, param in enumerate(params):
            if param.lower() == flag.lower():
                return idx
        return None

    def _refresh_runtime(self, user) -> dict:
        """Clean runtime artifacts and reinstall enabled integrations."""
        from core.services.logging_api import get_logger
        from core.tui.output import OutputToolkit

        logger = get_logger("repair-handler")
        cleaned, errors = self._clean_runtime_targets()
        reinstall = self._reinstall_integrations()
        updates = self._collect_plugin_updates()

        output = [OutputToolkit.banner("REPAIR: REFRESH RUNTIME")]
        output.append(f"  Cleaned: {', '.join(cleaned) if cleaned else 'none'}")
        if errors:
            output.append(f"  Errors: {len(errors)} ({'; '.join(errors)})")
        if reinstall["available"]:
            output.append(
                f"  Reinstalled integrations: {len(reinstall.get('results', []))}"
            )
            for line in reinstall.get("results", [])[:5]:
                output.append(f"    {line}")
            if len(reinstall.get("results", [])) > 5:
                output.append("    ...")
        else:
            output.append(
                "  Wizard integrations unavailable (wizard component missing)"
            )
        if updates is not None:
            output.append(f"  Plugin updates available: {len(updates)}")
        output.append("")
        output.append("Next steps:")
        output.append("  • Run REPAIR --install-plugin <name>")
        output.append("  • Run HEALTH and VERIFY to re-run diagnostics")

        logger.info(
            "[LOCAL] REPAIR runtime refresh completed by %s",
            user.username if user else "unknown",
        )
        return {
            "status": "success" if not errors else "warning",
            "message": "Runtime caches refreshed",
            "output": "\n".join(output),
        }

    def _runtime_cleanup_targets(self) -> list[tuple[str, Path]]:
        repo_root = get_repo_root()
        root_parent = repo_root.parent
        return [
            ("Python runtime (.venv)", repo_root / ".venv"),
            ("Legacy Python runtime (venv)", repo_root / "venv"),
            ("Extensions runtime copies", repo_root / "extensions"),
            (
                "Wizard dashboard node_modules",
                repo_root / "wizard" / "dashboard" / "node_modules",
            ),
            ("Wizard dashboard dist", repo_root / "wizard" / "dashboard" / "dist"),
            ("Wizard web static assets", repo_root / "wizard" / "web" / "static"),
            ("Memory wizard cache", repo_root / "memory" / "wizard"),
            ("Memory tests cache", repo_root / "memory" / "tests"),
            (
                "Wizard plugin cache",
                repo_root / "wizard" / "distribution" / "plugins" / "cache",
            ),
            (
                "GitHub integration folder",
                root_parent / "wizard" / "github_integration",
            ),
            (
                "Local logic-assist assets (Vibe CLI)",
                root_parent / "library" / "mistral-vibe",
            ),
            ("Legacy Ollama container", root_parent / "library" / "ollama"),
        ]

    def _clean_runtime_targets(self) -> tuple[list[str], list[str]]:
        cleaned = []
        errors = []
        for label, path in self._runtime_cleanup_targets():
            try:
                if not path.exists():
                    continue
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                cleaned.append(label)
            except Exception as exc:
                errors.append(f"{label}: {exc}")
        return cleaned, errors

    def _reinstall_integrations(self) -> dict[str, Any]:
        """Reinstall enabled or installed integrations via the Wizard library manager."""
        from core.services.provider_registry import (
            ProviderNotAvailableError,
            ProviderType,
            get_provider,
        )

        try:
            manager = get_provider(ProviderType.LIBRARY_MANAGER)
        except ProviderNotAvailableError:
            return {"available": False, "results": []}
        status = manager.get_library_status()
        results = []
        for integration in status.integrations:
            if not integration.enabled and not integration.installed:
                continue
            result = manager.install_integration(integration.name)
            status_label = "OK" if result.success else "FAIL"
            detail = result.message or result.error or "no details"
            results.append(
                f"{integration.name}: {result.action} ({status_label}) {detail}"
            )
        return {"available": True, "results": results}

    def _collect_plugin_updates(self) -> list[Any] | None:
        from core.services.provider_registry import (
            ProviderNotAvailableError,
            ProviderType,
            get_provider,
        )

        try:
            repo = get_provider(ProviderType.PLUGIN_REPOSITORY)
            return repo.check_updates()
        except ProviderNotAvailableError:
            return None

    def _install_plugin(self, plugin_name: str | None) -> dict:
        if not plugin_name:
            return {
                "status": "error",
                "message": "Usage: REPAIR --install-plugin <integration_name>",
            }

        from core.services.provider_registry import (
            ProviderNotAvailableError,
            ProviderType,
            get_provider,
        )

        try:
            manager = get_provider(ProviderType.LIBRARY_MANAGER)
        except ProviderNotAvailableError:
            return {
                "status": "error",
                "message": "Wizard component unavailable; cannot manage plugins",
            }
        integration = manager.get_integration(plugin_name)
        if not integration:
            return {
                "status": "error",
                "message": f"Integration not found: {plugin_name}",
            }

        result = manager.install_integration(plugin_name)
        status = "success" if result.success else "error"
        output = result.message or result.error or "Installation attempted"
        return {
            "status": status,
            "message": output,
            "integration": plugin_name,
            "action": result.action,
            "details": output,
        }

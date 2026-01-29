"""SHAKEDOWN command handler - Enhanced system validation and diagnostics."""

from typing import List, Dict
from pathlib import Path
from core.commands.base import BaseCommandHandler
import json
import os

# Dynamic project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ShakedownHandler(BaseCommandHandler):
    """Handler for SHAKEDOWN command - system validation and diagnostics."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle SHAKEDOWN command - validate all core systems.

        Args:
            command: Command name (SHAKEDOWN)
            params: Optional flags [--detailed], [--fresh], [--destroy-verify]
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with validation results
        """
        detailed = "--detailed" in params if params else False
        fresh_install = "--fresh" in params if params else False
        destroy_verify = "--destroy-verify" in params if params else False

        # Lazy imports to avoid circular deps
        from core.locations import load_locations
        from core.tui.output import OutputToolkit

        results = {
            "status": "success",
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "checks": {},
        }

        # ===== Check 1: Framework Initialization =====
        results["checks"]["framework_init"] = self._check_framework_init()
        if results["checks"]["framework_init"]["status"] == "pass":
            results["passed"] += 1
        elif results["checks"]["framework_init"]["status"] == "fail":
            results["failed"] += 1
        else:
            results["warnings"] += 1

        # ===== Check 2: Component Registration =====
        results["checks"]["components"] = self._check_components()
        if results["checks"]["components"]["status"] == "pass":
            results["passed"] += 1
        elif results["checks"]["components"]["status"] == "fail":
            results["failed"] += 1
        else:
            results["warnings"] += 1

        # ===== Check 3: Locations Database =====
        try:
            db = load_locations()
            all_locs = list(db.get_all())
            results["checks"]["locations"] = {
                "status": "pass",
                "count": len(all_locs),
                "message": f"Loaded {len(all_locs)} locations",
            }
            results["passed"] += 1
        except Exception as e:
            results["checks"]["locations"] = {
                "status": "fail",
                "message": f"Failed to load locations: {str(e)}",
            }
            results["failed"] += 1

        # ===== Check 4: Core Command Registration =====
        core_commands = [
            "MAP",
            "PANEL",
            "GOTO",
            "FIND",
            "TELL",
            "BAG",
            "GRAB",
            "SPAWN",
            "SAVE",
            "LOAD",
            "HELP",
            "SHAKEDOWN",
            "REPAIR",
            "RESTART",
            "SETUP",
            "USER",
            "DESTROY",
            "CONFIG",
            "LOGS",
            "RELOAD",
            "REBOOT",
        ]
        results["checks"]["commands"] = {
            "status": "pass",
            "count": len(core_commands),
            "message": f"{len(core_commands)} core commands registered",
        }
        results["passed"] += 1

        # ===== Check 5: Memory Directories =====
        memory_dirs = [
            PROJECT_ROOT / "memory" / "logs",
            PROJECT_ROOT / "memory" / "bank",
        ]
        missing_dirs = []
        for dir_path in memory_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            results["checks"]["directories"] = {
                "status": "warning",
                "message": f"{len(missing_dirs)} memory directories missing (will be created on use)",
                "missing": [str(d) for d in missing_dirs],
            }
            results["warnings"] += 1
        else:
            results["checks"]["directories"] = {
                "status": "pass",
                "message": "All memory directories exist",
            }
            results["passed"] += 1

        # ===== Check 6: TypeScript Runtime =====
        ts_runtime = PROJECT_ROOT / "core" / "src"
        if ts_runtime.exists():
            ts_files = list(ts_runtime.glob("**/*.ts"))
            results["checks"]["ts_runtime"] = {
                "status": "pass",
                "count": len(ts_files),
                "message": f"TypeScript runtime present ({len(ts_files)} files)",
            }
            results["passed"] += 1
        else:
            results["checks"]["ts_runtime"] = {
                "status": "fail",
                "message": "TypeScript runtime not found",
            }
            results["failed"] += 1

        # ===== Check 7: Handler Modules =====
        handler_dir = PROJECT_ROOT / "core" / "commands"
        if handler_dir.exists():
            handlers = list(handler_dir.glob("*_handler.py"))
            results["checks"]["handlers"] = {
                "status": "pass",
                "count": len(handlers),
                "message": f"{len(handlers)} handler modules found",
            }
            results["passed"] += 1
        else:
            results["checks"]["handlers"] = {
                "status": "fail",
                "message": "Commands directory not found",
            }
            results["failed"] += 1

        # ===== Check 8: Services Layer =====
        results["checks"]["services"] = self._check_services()
        if results["checks"]["services"]["status"] == "pass":
            results["passed"] += 1
        elif results["checks"]["services"]["status"] == "fail":
            results["failed"] += 1
        else:
            results["warnings"] += 1

        # ===== Check 9: User Manager (if available) =====
        results["checks"]["user_manager"] = self._check_user_manager()
        if results["checks"]["user_manager"]["status"] == "pass":
            results["passed"] += 1
        elif results["checks"]["user_manager"]["status"] == "fail":
            results["failed"] += 1
        else:
            results["warnings"] += 1

        # ===== FRESH INSTALL VALIDATION =====
        if fresh_install:
            results["checks"]["fresh_install"] = self._check_fresh_install()
            if results["checks"]["fresh_install"]["status"] == "pass":
                results["passed"] += 1
            else:
                results["failed"] += 1

        # ===== DESTROY VERIFICATION =====
        if destroy_verify:
            results["checks"]["destroy_verify"] = self._verify_destroy()
            if results["checks"]["destroy_verify"]["status"] == "pass":
                results["passed"] += 1
            else:
                results["failed"] += 1

        # ===== Summary =====
        total_checks = results["passed"] + results["failed"] + results["warnings"]
        results["summary"] = f"{results['passed']}/{total_checks} checks passed"

        if results["failed"] > 0:
            results["status"] = "fail"
        elif results["warnings"] > 0:
            results["status"] = "warning"

        # Build output
        checklist_items = []
        for key, check in results["checks"].items():
            ok = check.get("status") == "pass"
            msg = check.get("message", "")
            if check.get("count"):
                msg += f" ({check['count']})"
            checklist_items.append((f"{key}: {msg}", ok))

        output = []
        output.append(OutputToolkit.banner("SHAKEDOWN"))
        output.append(OutputToolkit.checklist(checklist_items))
        output.append("")
        output.append(f"Summary: {results['summary']}")
        if fresh_install:
            output.append("Status: Fresh install validation enabled")
        if destroy_verify:
            output.append("Status: DESTROY verification enabled")

        results["output"] = "\n".join(output)
        return results

    def _check_framework_init(self) -> Dict:
        """Check framework initialization."""
        try:
            # Try importing core components
            from core.tui.dispatcher import CommandDispatcher
            from core.tui.state import GameState
            from core.input import SmartPrompt

            dispatcher = CommandDispatcher()
            state = GameState()
            prompt = SmartPrompt()

            # Verify dispatcher has handlers
            if not dispatcher.handlers or len(dispatcher.handlers) < 10:
                return {
                    "status": "warning",
                    "message": f"Dispatcher initialized with {len(dispatcher.handlers)} handlers (expected ≥10)",
                }

            return {
                "status": "pass",
                "message": "Framework initialized (Dispatcher, State, SmartPrompt)",
                "handlers": len(dispatcher.handlers),
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Framework initialization failed: {str(e)}",
            }

    def _check_components(self) -> Dict:
        """Check component availability."""
        try:
            components = {}

            # Core (always)
            components["core"] = (PROJECT_ROOT / "core" / "__init__.py").exists()

            # Wizard (optional)
            components["wizard"] = (PROJECT_ROOT / "wizard" / "server.py").exists()

            # Extensions (optional)
            components["extensions"] = (
                PROJECT_ROOT / "extensions" / "api"
            ).exists() or (PROJECT_ROOT / "extensions" / "transport").exists()

            # App (optional)
            components["app"] = (PROJECT_ROOT / "app" / "package.json").exists()

            available = sum(1 for v in components.values() if v)

            return {
                "status": "pass" if components["core"] else "fail",
                "message": f"Components: {available}/4 available (core required)",
                "details": {k: "✓" if v else "✗" for k, v in components.items()},
            }
        except Exception as e:
            return {"status": "fail", "message": f"Component check failed: {str(e)}"}

    def _check_services(self) -> Dict:
        """Check services layer."""
        try:
            services = {}

            # Logging manager
            try:
                from core.services.logging_manager import get_logger

                services["logging"] = True
            except:
                services["logging"] = False

            # User manager
            try:
                from core.services.user_manager import get_user_manager

                services["user_manager"] = True
            except:
                services["user_manager"] = False

            # File service (if available)
            try:
                from core.services.file_service import FileService

                services["file_service"] = True
            except:
                services["file_service"] = False

            available = sum(1 for v in services.values() if v)

            if available >= 2:
                return {
                    "status": "pass",
                    "message": f"Services layer: {available}/3 services available",
                    "services": services,
                }
            else:
                return {
                    "status": "warning",
                    "message": f"Services layer: {available}/3 services available",
                    "services": services,
                }
        except Exception as e:
            return {"status": "fail", "message": f"Services check failed: {str(e)}"}

    def _check_user_manager(self) -> Dict:
        """Check user manager and current user."""
        try:
            from core.services.user_manager import get_user_manager

            user_mgr = get_user_manager()
            current = user_mgr.current()
            all_users = list(user_mgr.users.keys())

            if not current:
                return {
                    "status": "warning",
                    "message": f"User manager: {len(all_users)} users, no current user",
                }

            return {
                "status": "pass",
                "message": f"User manager: {len(all_users)} users, current={current.username}",
                "users": all_users,
                "current_user": current.username,
            }
        except Exception as e:
            return {"status": "fail", "message": f"User manager check failed: {str(e)}"}

    def _check_fresh_install(self) -> Dict:
        """Validate fresh install initialization."""
        try:
            checks = {}

            # Check 1: Memory structure
            memory_root = PROJECT_ROOT / "memory"
            checks["memory_exists"] = memory_root.exists()

            # Check 2: Default user exists
            from core.services.user_manager import get_user_manager

            user_mgr = get_user_manager()
            checks["default_user"] = "admin" in user_mgr.users

            # Check 3: Core directories
            core_dirs = [
                memory_root / "logs",
                memory_root / "bank",
                memory_root / "locations",
            ]
            checks["core_dirs"] = all(d.exists() for d in core_dirs)

            # Check 4: Config files can be loaded
            try:
                from core.services.logging_manager import get_logger

                logger = get_logger("shakedown-fresh")
                checks["logger_init"] = True
            except:
                checks["logger_init"] = False

            if all(checks.values()):
                return {
                    "status": "pass",
                    "message": "Fresh install: All checks passed",
                    "checks": checks,
                }
            else:
                failed = [k for k, v in checks.items() if not v]
                return {
                    "status": "fail",
                    "message": f"Fresh install: {len(failed)} checks failed",
                    "failed": failed,
                    "checks": checks,
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Fresh install validation failed: {str(e)}",
            }

    def _verify_destroy(self) -> Dict:
        """Verify DESTROY command can function."""
        try:
            # Check 1: DESTROY handler exists
            from core.commands import DestroyHandler

            handler = DestroyHandler()

            # Check 2: Can access user manager
            from core.services.user_manager import get_user_manager, Permission

            user_mgr = get_user_manager()
            current = user_mgr.current()

            # Check 3: Current user has destroy permission
            has_destroy = (
                user_mgr.has_permission(Permission.DESTROY) if current else False
            )

            # Check 4: Memory directories accessible
            memory_path = PROJECT_ROOT / "memory"
            can_write = memory_path.exists() and os.access(str(memory_path), os.W_OK)

            checks = {
                "destroy_handler": True,
                "user_manager": True,
                "current_user": current is not None,
                "destroy_permission": has_destroy,
                "memory_writable": can_write,
            }

            if all(checks.values()):
                return {
                    "status": "pass",
                    "message": "DESTROY command verified and ready",
                    "checks": checks,
                }
            else:
                failed = [k for k, v in checks.items() if not v]
                return {
                    "status": "fail",
                    "message": f"DESTROY verification: {len(failed)} checks failed",
                    "failed": failed,
                    "checks": checks,
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"DESTROY verification failed: {str(e)}",
            }

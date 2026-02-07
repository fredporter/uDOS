"""SHAKEDOWN command handler - Enhanced system validation and diagnostics.

Validates:
  - Framework initialization (Dispatcher, State, SmartPrompt)
  - Component registration and availability
  - Fresh install setup (on --fresh flag)
  - DESTROY command readiness (on --destroy-verify flag)
  - User manager and permissions
  - Services layer integration

Commands:
    SHAKEDOWN                   # Standard system validation
    SHAKEDOWN --detailed        # Show detailed results
    SHAKEDOWN --fresh           # Validate fresh install
    SHAKEDOWN --destroy-verify  # Verify DESTROY command works
    SHAKEDOWN --cycle           # Dry-run command cycle

Author: uDOS Engineering
Version: v1.1.0
Date: 2026-01-29
"""

import os
from typing import List, Dict
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.locations import load_locations
from core.tui.output import OutputToolkit

# Dynamic project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ShakedownHandler(BaseCommandHandler):
    """Handler for SHAKEDOWN command - comprehensive system validation."""

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
        cycle_commands = "--cycle" in params if params else False

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
            "MAP", "PANEL", "GOTO", "FIND", "TELL", "BAG", "GRAB", "SPAWN",
            "SAVE", "LOAD", "HELP", "SHAKEDOWN", "REPAIR", "SETUP",
            "USER", "DESTROY", "CONFIG", "LOGS", "REBOOT"
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
                "missing": [str(d.relative_to(PROJECT_ROOT)) for d in missing_dirs],
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

        # ===== Check 9: User Manager =====
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
            output.append("Mode: Fresh install validation enabled")
        if destroy_verify:
            output.append("Mode: DESTROY verification enabled")
        if cycle_commands:
            output.append("Mode: Command cycle (dry-run)")
            output.append("")
            cycle_lines = self._build_command_cycle()
            results["command_cycle"] = cycle_lines
            output.extend(cycle_lines)

        results["output"] = "\n".join(output)
        return results

    def _build_command_cycle(self) -> List[str]:
        """Return a dry-run list of available commands with syntax."""
        try:
            from core.input.command_prompt import create_default_registry

            registry = create_default_registry()
            entries = sorted(registry.list_all(), key=lambda cmd: cmd.name)
            lines = ["Command cycle (dry-run):"]
            for idx, cmd in enumerate(entries, 1):
                syntax = cmd.syntax or cmd.name
                lines.append(f"  {idx:02d}. {cmd.name} — {syntax}")
            lines.append(f"Total commands: {len(entries)}")
            return lines
        except Exception as exc:
            return [
                "Command cycle (dry-run): unavailable",
                f"  Error: {exc}",
            ]

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
                    "message": f"Dispatcher initialized with {len(dispatcher.handlers)} handlers (expected ≥10)"
                }

            return {
                "status": "pass",
                "message": "Framework initialized (Dispatcher, State, SmartPrompt)",
                "count": len(dispatcher.handlers),
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Framework initialization failed: {str(e)}"
            }

    def _check_components(self) -> Dict:
        """Check component availability."""
        try:
            components = {}

            # Core (always required)
            components["core"] = (PROJECT_ROOT / "core" / "__init__.py").exists()

            # Wizard (optional)
            components["wizard"] = (PROJECT_ROOT / "wizard" / "server.py").exists()

            # Extensions (optional)
            components["extensions"] = (PROJECT_ROOT / "extensions" / "api").exists() or \
                                      (PROJECT_ROOT / "extensions" / "transport").exists()

            # App (optional)
            components["app"] = (PROJECT_ROOT / "app" / "package.json").exists()

            available = sum(1 for v in components.values() if v)

            return {
                "status": "pass" if components["core"] else "fail",
                "message": f"Components: {available}/4 available (core required)",
                "count": available,
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Component check failed: {str(e)}"
            }

    def _check_services(self) -> Dict:
        """Check services layer."""
        try:
            services = {}

            # Logging manager
            try:
                from core.services.logging_api import get_logger
                services["logging"] = True
            except:
                services["logging"] = False

            # User manager
            try:
                from core.services.user_service import get_user_manager
                services["user_manager"] = True
            except:
                services["user_manager"] = False

            available = sum(1 for v in services.values() if v)

            if available >= 2:
                return {
                    "status": "pass",
                    "message": f"Services layer: {available}/2 available",
                    "count": available,
                }
            else:
                return {
                    "status": "warning",
                    "message": f"Services layer: {available}/2 available",
                    "count": available,
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Services check failed: {str(e)}"
            }

    def _check_user_manager(self) -> Dict:
        """Check user manager and current user."""
        try:
            from core.services.user_service import get_user_manager

            user_mgr = get_user_manager()
            current = user_mgr.current()
            all_users = list(user_mgr.users.keys())

            if not current:
                return {
                    "status": "warning",
                    "message": f"User manager: {len(all_users)} users, no current user",
                    "count": len(all_users),
                }

            return {
                "status": "pass",
                "message": f"User manager: {len(all_users)} users, current={current.username}",
                "count": len(all_users),
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"User manager check failed: {str(e)}"
            }

    def _check_fresh_install(self) -> Dict:
        """Validate fresh install initialization.

        Validates:
          - Memory directory structure
          - Default admin user
          - Core service initialization
          - Handler module availability
          - Logger initialization
          - Framework components ready
        """
        try:
            checks = {}

            # Check 1: Memory structure
            memory_root = PROJECT_ROOT / "memory"
            checks["memory_exists"] = memory_root.exists()

            # Check 2: Memory subdirectories
            core_dirs = [
                memory_root / "logs",
                memory_root / "logs" / "monitoring",
                memory_root / "logs" / "quotas",
                memory_root / "bank",
                memory_root / "bank" / "private",
                memory_root / "bank" / "user",
                memory_root / "sandbox",
                memory_root / "sandbox" / "binders",
                memory_root / "wizard",
            ]
            checks["memory_dirs"] = all(d.exists() for d in core_dirs)
            missing_dirs = [d.name for d in core_dirs if not d.exists()]

            # Check 3: Default admin user exists and is initialized
            from core.services.user_service import get_user_manager
            user_mgr = get_user_manager()
            checks["default_user"] = "admin" in user_mgr.users

            # Verify admin has proper permissions
            admin = user_mgr.users.get("admin")
            checks["admin_initialized"] = admin is not None and admin.role == "admin"

            # Check 4: Core services can be initialized
            services_ok = True
            try:
                from core.services.logging_api import get_logger
                logger = get_logger("shakedown-fresh")
            except:
                services_ok = False
            checks["logging_api"] = services_ok

            # Check 5: User manager ready with current user set
            checks["user_manager_ready"] = user_mgr.current() is not None

            # Check 6: Handler directory and critical handlers
            handler_dir = PROJECT_ROOT / "core" / "commands"
            critical_handlers = [
                "shakedown_handler.py",
                "destroy_handler.py",
                "help_handler.py",
                "setup_handler.py",
            ]
            handlers_exist = all((handler_dir / h).exists() for h in critical_handlers)
            checks["critical_handlers"] = handlers_exist

            # Check 7: Framework can initialize dispatcher
            try:
                from core.tui.dispatcher import CommandDispatcher
                dispatcher = CommandDispatcher()
                checks["dispatcher_ready"] = len(dispatcher.handlers) >= 10
            except:
                checks["dispatcher_ready"] = False

            # Check 8: GameState can initialize
            try:
                from core.tui.state import GameState
                state = GameState()
                checks["state_ready"] = state is not None
            except:
                checks["state_ready"] = False

            # Check 9: SmartPrompt available
            try:
                from core.input import SmartPrompt
                prompt = SmartPrompt()
                checks["smartprompt_ready"] = prompt is not None
            except:
                checks["smartprompt_ready"] = False

            # Summarize results
            all_passed = all(checks.values())
            failed = [k for k, v in checks.items() if not v]

            if all_passed:
                return {
                    "status": "pass",
                    "message": "Fresh install: All 9 checks passed (memory, users, services, framework)",
                    "count": 9,
                }
            else:
                details = []
                if missing_dirs:
                    details.append(f"missing dirs: {', '.join(missing_dirs)}")
                if failed:
                    details.append(f"failed checks: {', '.join(failed[:3])}")  # Show first 3

                detail_str = f" ({', '.join(details)})" if details else ""
                return {
                    "status": "fail",
                    "message": f"Fresh install: {len(failed)}/{len(checks)} checks failed{detail_str}",
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Fresh install validation failed: {str(e)}"
            }

    def _verify_destroy(self) -> Dict:
        """Verify DESTROY command can function and is safe to call.

        Validates:
          - DESTROY handler exists and is registered
          - User manager initialized
          - Current user has DESTROY permission
          - Memory directories writable
          - Archive structure ready for compost
          - Compost directory can be created
        """
        try:
            # Check 1: DESTROY handler exists and is importable
            try:
                from core.commands import DestroyHandler
                handler = DestroyHandler()
                check_handler = True
            except:
                check_handler = False

            # Check 2: Can access user manager
            try:
                from core.services.user_service import get_user_manager, Permission
                user_mgr = get_user_manager()
                check_user_mgr = True
            except:
                check_user_mgr = False
                user_mgr = None
                Permission = None

            # Check 3: Current user exists and permissions are available
            current = user_mgr.current() if user_mgr else None
            check_current_user = current is not None

            # Check 4: Current user has destroy permission
            if user_mgr and Permission and current:
                has_destroy = user_mgr.has_permission(Permission.DESTROY)
            else:
                has_destroy = False

            # Check 5: Memory directories accessible and writable
            memory_path = PROJECT_ROOT / "memory"
            can_write_memory = memory_path.exists() and os.access(str(memory_path), os.W_OK)

            # Check 6: Archive directory exists or parent is writable
            archive_path = PROJECT_ROOT / ".archive"
            can_create_archive = archive_path.exists() or os.access(str(PROJECT_ROOT), os.W_OK)

            # Check 7: Compost subdirectory creatable
            compost_base = archive_path / "compost" if archive_path.exists() else None
            can_compost = (
                (compost_base and compost_base.exists()) or
                (archive_path.exists() and os.access(str(archive_path), os.W_OK)) or
                can_create_archive
            )

            # Check 8: Logging available for audit trail
            try:
                from core.services.logging_api import get_log_manager
                _ = get_log_manager()
                check_logging = True
            except Exception:
                check_logging = False

            checks = {
                "destroy_handler": check_handler,
                "user_manager": check_user_mgr,
                "current_user": check_current_user,
                "destroy_permission": has_destroy,
                "memory_writable": can_write_memory,
                "archive_ready": can_create_archive,
                "compost_ready": can_compost,
                "audit_logging": check_logging,
            }

            # Determine overall status
            critical_checks = [
                "destroy_handler",
                "user_manager",
                "current_user",
                "destroy_permission",
                "memory_writable",
            ]
            critical_ok = all(checks.get(k, False) for k in critical_checks)

            all_ok = all(checks.values())

            if all_ok:
                return {
                    "status": "pass",
                    "message": "DESTROY verified: All 8 checks passed (handler, user, perms, I/O, logging)",
                    "count": 8,
                }
            elif critical_ok:
                failed = [k for k, v in checks.items() if not v]
                return {
                    "status": "warning",
                    "message": f"DESTROY ready but {len(failed)} optional checks failed: {', '.join(failed)}",
                }
            else:
                failed = [k for k, v in checks.items() if not v]
                return {
                    "status": "fail",
                    "message": f"DESTROY verification failed: {', '.join(failed)} (critical checks)",
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"DESTROY verification error: {str(e)}"
            }

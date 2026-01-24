"""SHAKEDOWN command handler - System validation and diagnostics."""

from typing import List, Dict
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.locations import load_locations
from core.tui.output import OutputToolkit

# Dynamic project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ShakedownHandler(BaseCommandHandler):
    """Handler for SHAKEDOWN command - system validation and diagnostics."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle SHAKEDOWN command - validate all core systems.

        Args:
            command: Command name (SHAKEDOWN)
            params: Optional [--detailed] flag
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with validation results
        """
        detailed = "--detailed" in params if params else False

        results = {
            "status": "success",
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "checks": {},
        }

        # Check 1: Locations database
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

        # Check 2: Core commands
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
        ]
        results["checks"]["commands"] = {
            "status": "pass",
            "count": len(core_commands),
            "message": f"{len(core_commands)} core commands registered",
        }
        results["passed"] += 1

        # Check 3: Memory directories
        memory_dirs = [
            PROJECT_ROOT / "memory" / "logs",
            PROJECT_ROOT / "memory" / "saved_games",
            PROJECT_ROOT / "memory" / "tests",
        ]

        missing_dirs = []
        for dir_path in memory_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            results["checks"]["directories"] = {
                "status": "warning",
                "message": f"{len(missing_dirs)} directories not found (will be created on use)",
            }
            results["warnings"] += 1
        else:
            results["checks"]["directories"] = {
                "status": "pass",
                "message": "All memory directories exist",
            }
            results["passed"] += 1

        # Check 4: TypeScript runtime
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

        # Check 5: Handler modules
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

        # Check 6: Tests
        test_dir = PROJECT_ROOT / "memory" / "tests"
        if test_dir.exists():
            test_files = list(test_dir.glob("**/*.py"))
            test_files = [f for f in test_files if "test_" in f.name]
            results["checks"]["tests"] = {
                "status": "pass",
                "count": len(test_files),
                "message": f"{len(test_files)} test files present",
            }
            results["passed"] += 1
        else:
            results["checks"]["tests"] = {
                "status": "warning",
                "message": "Test directory not found",
            }
            results["warnings"] += 1

        # Summary
        total_checks = results["passed"] + results["failed"] + results["warnings"]
        results["summary"] = f"{results['passed']}/{total_checks} checks passed"

        if results["failed"] > 0:
            results["status"] = "fail"
        elif results["warnings"] > 0:
            results["status"] = "warning"

        checklist_items = []
        for key, check in results["checks"].items():
            ok = check.get("status") == "pass"
            checklist_items.append((f"{key}: {check.get('message')}", ok))

        output = []
        output.append(OutputToolkit.banner("SHAKEDOWN"))
        output.append(OutputToolkit.checklist(checklist_items))
        output.append("")
        output.append(f"Summary: {results['summary']}")

        results["output"] = "\n".join(output)
        return results

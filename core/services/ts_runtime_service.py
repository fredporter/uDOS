"""
TS Runtime Service (Core)

Execute uDOS markdown scripts via the compiled TS runtime using Node.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("core.ts_runtime")


def _load_runtime_config() -> Dict[str, Any]:
    config_path = get_repo_root() / "core" / "config" / "runtime.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return {}


class TSRuntimeService:
    """Execute TS runtime scripts using Node."""

    def __init__(self):
        self.config = _load_runtime_config()
        self.node_cmd = self.config.get("node_cmd", "node")
        runner_rel = self.config.get("ts_runner", "core/runtime/ts_runner.js")
        self.runner_path = get_repo_root() / runner_rel
        runtime_entry = self.config.get(
            "runtime_entry", "core/grid-runtime/dist/index.js"
        )
        self.runtime_entry = get_repo_root() / runtime_entry

    def _check_runtime_entry(self, auto_build: bool = False) -> Optional[Dict[str, Any]]:
        """Check if TS runtime exists. Optionally auto-build if missing."""
        if not self.runtime_entry.exists():
            if auto_build:
                logger.info("[STARTUP] TS runtime missing, attempting auto-build...")
                build_result = self._auto_build_runtime()
                if build_result.get("status") == "success":
                    logger.info("[STARTUP] TS runtime built successfully")
                    return None  # Success, runtime now exists
                else:
                    # Auto-build failed, return error with build details
                    return build_result

            return {
                "status": "error",
                "message": "TS runtime not built",
                "details": f"Missing: {self.runtime_entry}",
                "suggestion": "Run: core/tools/build_ts_runtime.sh",
            }
        return None

    def _auto_build_runtime(self) -> Dict[str, Any]:
        """Automatically build the TS runtime using the build script."""
        build_script = get_repo_root() / "core" / "tools" / "build_ts_runtime.sh"

        if not build_script.exists():
            return {
                "status": "error",
                "message": "Build script not found",
                "details": f"Missing: {build_script}"
            }

        # Check for Node.js/npm
        try:
            node_check = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                timeout=5
            )
            npm_check = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                timeout=5
            )

            if node_check.returncode != 0 or npm_check.returncode != 0:
                return {
                    "status": "error",
                    "message": "Node.js/npm not available",
                    "details": "Install Node.js from https://nodejs.org/",
                    "suggestion": "Run: core/tools/build_ts_runtime.sh (after installing Node.js)"
                }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {
                "status": "error",
                "message": "Cannot verify Node.js/npm",
                "details": str(e)
            }

        # Run the build script
        try:
            result = subprocess.run(
                ["bash", str(build_script)],
                cwd=str(get_repo_root()),
                capture_output=True,
                timeout=300,  # 5 minute timeout
                text=True
            )

            if result.returncode == 0:
                return {"status": "success", "message": "TS runtime built successfully"}
            else:
                return {
                    "status": "error",
                    "message": "Build failed",
                    "details": result.stderr.strip() or result.stdout.strip()[-500:]
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Build timeout",
                "details": "Build took longer than 5 minutes"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Build error",
                "details": str(e)
            }

    def execute(self, markdown_path: Path, section_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.runner_path.exists():
            return {"status": "error", "message": f"Runner not found: {self.runner_path}"}
        runtime_check = self._check_runtime_entry(auto_build=False)
        if runtime_check:
            return runtime_check
        if not markdown_path.exists():
            return {"status": "error", "message": f"Script not found: {markdown_path}"}

        cmd = [self.node_cmd, str(self.runner_path)]

        # Add flags BEFORE the file path
        if section_id is None:
            # Pass --all to request all sections for multi-section forms
            cmd.append("--all")

        # Always add the file path
        cmd.append(str(markdown_path))

        # Add section_id if provided (and not requesting all sections)
        if section_id:
            cmd.append(section_id)

        logger.info(f"[LOCAL] TS runtime exec: {markdown_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "TS runtime failed",
                "details": result.stderr.strip() or result.stdout.strip(),
            }

        try:
            payload = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid runtime output",
                "details": result.stdout.strip(),
            }

        return {"status": "success", "payload": payload}

    def parse(self, markdown_path: Path) -> Dict[str, Any]:
        if not self.runner_path.exists():
            return {"status": "error", "message": f"Runner not found: {self.runner_path}"}
        runtime_check = self._check_runtime_entry(auto_build=False)
        if runtime_check:
            return runtime_check
        if not markdown_path.exists():
            return {"status": "error", "message": f"Script not found: {markdown_path}"}

        cmd = [self.node_cmd, str(self.runner_path), "--parse", str(markdown_path)]
        logger.info(f"[LOCAL] TS runtime parse: {markdown_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "TS runtime parse failed",
                "details": result.stderr.strip() or result.stdout.strip(),
            }

        try:
            payload = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid runtime output",
                "details": result.stdout.strip(),
            }

        return {"status": "success", "payload": payload}

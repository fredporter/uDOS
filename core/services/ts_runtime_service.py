"""
TS Runtime Service (Core)

Execute uDOS markdown scripts via the compiled TS runtime using Node.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_manager import get_logger, get_repo_root

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

    def _check_runtime_entry(self) -> Optional[Dict[str, Any]]:
        if not self.runtime_entry.exists():
            return {
                "status": "error",
                "message": "TS runtime not built",
                "details": f"Missing: {self.runtime_entry}",
                "suggestion": "Run: core/tools/build_ts_runtime.sh",
            }
        return None

    def execute(self, markdown_path: Path, section_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.runner_path.exists():
            return {"status": "error", "message": f"Runner not found: {self.runner_path}"}
        runtime_check = self._check_runtime_entry()
        if runtime_check:
            return runtime_check
        if not markdown_path.exists():
            return {"status": "error", "message": f"Script not found: {markdown_path}"}

        cmd = [self.node_cmd, str(self.runner_path), str(markdown_path)]
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
        runtime_check = self._check_runtime_entry()
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

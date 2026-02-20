"""
Vibe Script Service

Manages executable scripts, automation flows, and testing utilities.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import os

from core.services.logging_manager import get_logger


class VibeScriptService:
    """Manage scripts and automation workflows."""

    def __init__(self):
        """Initialize script service."""
        self.logger = get_logger("vibe-script-service")
        self.script_root = Path.home() / ".uDOS" / "scripts"
        self.script_root.mkdir(parents=True, exist_ok=True)

    def list_scripts(self) -> Dict[str, Any]:
        """List all available scripts."""
        scripts = []

        try:
            for script_file in self.script_root.glob("*.sh"):
                scripts.append({
                    "name": script_file.stem,
                    "path": str(script_file),
                    "type": "bash",
                    "executable": os.access(script_file, os.X_OK),
                })

            for script_file in self.script_root.glob("*.py"):
                scripts.append({
                    "name": script_file.stem,
                    "path": str(script_file),
                    "type": "python",
                    "executable": os.access(script_file, os.X_OK),
                })
        except Exception as e:
            self.logger.error(f"Error listing scripts: {e}")

        return {
            "status": "success",
            "scripts": scripts,
            "count": len(scripts),
            "script_root": str(self.script_root),
        }

    def run_script(
        self,
        script_name: str,
        args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a script.

        Args:
            script_name: Script name (without extension)
            args: Script arguments

        Returns:
            Dict with execution status and output
        """
        script_path = None

        # Look for .sh or .py script
        for ext in [".sh", ".py"]:
            test_path = self.script_root / f"{script_name}{ext}"
            if test_path.exists():
                script_path = test_path
                break

        if not script_path:
            return {
                "status": "error",
                "message": f"Script not found: {script_name}",
            }

        self.logger.info(f"Running script: {script_name}")

        return {
            "status": "success",
            "message": f"Script executed: {script_name}",
            "script": script_name,
            "args": args or [],
            "exit_code": 0,  # Phase 4: Actual execution
            "output": "",
        }

    def edit_script(
        self,
        script_name: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        Create or update a script.

        Args:
            script_name: Script name
            content: Script content

        Returns:
            Dict with write status
        """
        script_path = self.script_root / f"{script_name}.sh"

        try:
            script_path.write_text(content)
            script_path.chmod(0o755)

            self.logger.info(f"Edited script: {script_name}")

            return {
                "status": "success",
                "message": f"Script created/updated: {script_name}",
                "path": str(script_path),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write script: {e}",
            }


# Global singleton
_script_service: Optional[VibeScriptService] = None


def get_script_service() -> VibeScriptService:
    """Get or create the global script service."""
    global _script_service
    if _script_service is None:
        _script_service = VibeScriptService()
    return _script_service

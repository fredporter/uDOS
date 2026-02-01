"""
System Script Runner
=====================

Ensures `/memory/system` scripts exist and invokes them via the TS runtime.
Provides startup/reboot hooks that seed the runtime with simple PATTERN output
so the Core TUI and automation logs always show a visible signal when each run
executes.

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-31
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Any

from core.services.health_training import needs_self_heal_training
from core.services.hotkey_map import read_hotkey_payload, write_hotkey_payload
from core.services.logging_service import get_logger, get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.services.automation_monitor import AutomationMonitor
from wizard.services.monitoring_manager import MonitoringManager
from core.services.notification_history_service import remind_if_pending
from core.services.todo_reminder_service import get_reminder_service

logger = get_logger("system-script")


class SystemScriptRunner:
    """Runs the startup/reboot scripts stored under /memory/system."""

    SCRIPT_TEMPLATE_DIR = Path("framework/seed/bank/system")

    def __init__(self):
        self.repo_root = get_repo_root()
        env_memory = os.environ.get("UDOS_MEMORY_ROOT")
        if env_memory:
            self.memory_root = Path(env_memory)
        else:
            self.memory_root = self.repo_root / "memory"
        self.system_dir = self.memory_root / "system"
        self.monitoring = MonitoringManager()
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = self.repo_root / self.SCRIPT_TEMPLATE_DIR
        self.todo_reminder = get_reminder_service()

    def run_startup_script(self) -> Dict[str, Any]:
        """Run the startup script and return the execution summary."""
        return self._run_script("startup-script.md", "startup")

    def run_reboot_script(self) -> Dict[str, Any]:
        """Run the reboot script and return the execution summary."""
        return self._run_script("reboot-script.md", "reboot")

    def _run_script(self, script_name: str, label: str) -> Dict[str, Any]:
        hotkey_payload = write_hotkey_payload(self.memory_root)
        automation_monitor = AutomationMonitor(self.memory_root)
        automation_summary = automation_monitor.summary()
        if automation_summary.get("should_gate"):
            message = (
                "Automation gating active: "
                f"{automation_summary.get('gate_reason') or 'monitoring throttle'}"
            )
            logger.warning(f"[SYSTEM SCRIPT] {message}")
            return {
                "status": "gated",
                "message": message,
                "script": script_name,
                "automation_monitor": automation_summary,
                "hotkey_snapshot": hotkey_payload.get("snapshot"),
            }
        notification_reminder = remind_if_pending()
        todo_reminder = self.todo_reminder.log_reminder()
        script_path = self._ensure_script(script_name)
        if not script_path:
            message = f"{label.title()} script not found ({script_name})"
            logger.warning(f"[SYSTEM SCRIPT] {message}")
            return {
                "status": "error",
                "message": message,
                "script": script_name,
                "notification_reminder": notification_reminder,
                "todo_reminder": todo_reminder,
            }

        monitoring_summary = self.monitoring.log_training_summary()
        notification_reminder = remind_if_pending()
        if not needs_self_heal_training():
            message = f"{label.title()} script skipped (Self-Heal clean)"
            logger.info(f"[SYSTEM SCRIPT] {message}")
            return {
                "status": "skipped",
                "message": message,
                "script": script_name,
                "monitoring_summary": monitoring_summary,
                "notification_reminder": notification_reminder,
                "automation_monitor": automation_summary,
                "todo_reminder": todo_reminder,
            }

        service = TSRuntimeService()
        result = service.execute(script_path)
        if result.get("status") != "success":
            message = result.get("message", "Unknown error")
            details = result.get("details", "")
            logger.warning(f"[SYSTEM SCRIPT] {label.title()} failed: {message}")
        return {
            "status": "error",
            "message": message,
            "details": details,
            "script": script_name,
            "monitoring_summary": monitoring_summary,
            "notification_reminder": notification_reminder,
            "automation_monitor": automation_summary,
            "todo_reminder": todo_reminder,
        }

        payload = result.get("payload", {})
        exec_result = payload.get("result", {})
        output = exec_result.get("output", "").strip()
        hotkey_snapshot = hotkey_payload.get("snapshot")
        hotkey_last = hotkey_payload.get("last_updated")
        message = f"{label.title()} script executed"
        logger.info(f"[SYSTEM SCRIPT] {message} ({script_path})")
        if hotkey_snapshot:
            logger.info(f"[SYSTEM SCRIPT] Hotkey snapshot: {hotkey_snapshot} ({hotkey_last})")
        reminder = remind_if_pending()
        return {
            "status": "success",
            "message": message,
            "script": script_name,
            "output": output,
            "hotkey_snapshot": hotkey_snapshot,
            "hotkey_last_updated": hotkey_last,
            "monitoring_summary": monitoring_summary,
            "notification_reminder": reminder,
            "automation_monitor": automation_summary,
            "todo_reminder": todo_reminder,
        }

    def _ensure_script(self, script_name: str) -> Optional[Path]:
        target = self.system_dir / script_name
        if target.exists():
            return target

        template = self.template_dir / script_name
        if template.exists():
            try:
                shutil.copy(template, target)
                return target
            except Exception as exc:
                logger.warning(f"[SYSTEM SCRIPT] Failed to copy {template}: {exc}")
                return None

        logger.warning(f"[SYSTEM SCRIPT] Template missing: {template}")
        return None

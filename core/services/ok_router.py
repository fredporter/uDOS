"""
OK Route Planner
================

Rule-based natural language router for OK ROUTE.
Produces a structured plan and suggested uCODE commands.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import re


@dataclass
class RoutePlan:
    intent: str
    target: str
    commands: List[str]
    context_scope: List[str]
    risk_level: str
    notes: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


_FILE_PATTERN = re.compile(r"[A-Za-z0-9_\-./]+\\.(py|md|json|yaml|yml|toml|txt|js|ts)")
_TASK_ID_PATTERN = re.compile(r"task_[a-z0-9]+", re.IGNORECASE)
_RUN_ID_PATTERN = re.compile(r"run_[a-z0-9]+", re.IGNORECASE)


def _extract_file_target(prompt: str) -> Optional[str]:
    match = _FILE_PATTERN.search(prompt)
    if match:
        return match.group(0)
    return None


def _extract_scheduler_id(prompt: str) -> Optional[str]:
    match = _TASK_ID_PATTERN.search(prompt)
    if match:
        return match.group(0)
    match = _RUN_ID_PATTERN.search(prompt)
    if match:
        return match.group(0)
    return None


def _pick_risk(commands: List[str]) -> str:
    destructive = {"DESTROY", "WIPE", "RESET"}
    medium = {"RUN", "REBUILD", "STOP"}
    for cmd in commands:
        upper = cmd.upper()
        if any(token in upper for token in destructive):
            return "high"
    for cmd in commands:
        upper = cmd.upper()
        if any(token in upper for token in medium):
            return "medium"
    return "low"


def plan_route(prompt: str) -> RoutePlan:
    """Create a rule-based route plan for a prompt."""
    raw = (prompt or "").strip()
    lowered = raw.lower()
    commands: List[str] = []
    notes: List[str] = []
    target = _extract_file_target(raw) or ""

    context_scope = ["repo", "vault"]
    if "vault" in lowered or "memory" in lowered:
        context_scope = ["vault"]
    if "repo" in lowered or "codebase" in lowered:
        context_scope = ["repo"]

    intent = "chat"

    if any(token in lowered for token in ("scheduler", "schedule", "cron")):
        intent = "schedule"
        task_id = _extract_scheduler_id(raw)
        if any(token in lowered for token in ("log", "logs", "history")):
            commands = [f"SCHEDULER LOG {task_id}".strip()]
        elif any(token in lowered for token in ("run", "trigger", "execute", "start")):
            if task_id:
                commands = [f"SCHEDULER RUN {task_id}".strip()]
            else:
                commands = ["SCHEDULER LIST"]
                notes.append("No task id found. Listing tasks first.")
        else:
            commands = ["SCHEDULER LIST"]
    elif any(token in lowered for token in ("script", "startup", "reboot")):
        intent = "execute"
        script_name = None
        if "startup" in lowered:
            script_name = "startup-script"
        elif "reboot" in lowered:
            script_name = "reboot-script"
        if any(token in lowered for token in ("log", "logs", "history")):
            cmd = "SCRIPT LOG"
            if script_name:
                cmd = f"{cmd} {script_name}"
            commands = [cmd]
        elif any(token in lowered for token in ("run", "execute", "start")):
            cmd = "SCRIPT RUN"
            if script_name:
                cmd = f"{cmd} {script_name}"
            commands = [cmd]
        else:
            commands = ["SCRIPT LIST"]
    elif "wizard" in lowered or "server" in lowered:
        intent = "ops"
        if any(token in lowered for token in ("start", "launch", "boot")):
            commands = ["WIZARD START"]
        elif any(token in lowered for token in ("stop", "shutdown", "halt")):
            commands = ["WIZARD STOP"]
        elif "rebuild" in lowered:
            commands = ["WIZARD REBUILD"]
        else:
            commands = ["WIZARD STATUS"]
    elif "config" in lowered or ".env" in lowered:
        intent = "config"
        commands = ["CONFIG"]
    elif "install" in lowered and "vibe" in lowered:
        intent = "setup"
        commands = ["SETUP vibe"]
    elif "setup" in lowered or "profile" in lowered:
        intent = "setup"
        commands = ["SETUP"]
    elif "log" in lowered or "logs" in lowered:
        intent = "logs"
        commands = ["LOGS"]
    elif "help" in lowered or "how do i" in lowered or "usage" in lowered:
        intent = "help"
        commands = ["HELP"]
    else:
        intent = "chat"
        commands = ["HELP"]
        notes.append("No deterministic command match. Showing HELP.")

    risk_level = _pick_risk(commands)

    return RoutePlan(
        intent=intent,
        target=target or "n/a",
        commands=commands,
        context_scope=context_scope,
        risk_level=risk_level,
        notes=notes,
    )

"""SCRIPT command handler - list/run/log system scripts."""

from __future__ import annotations

from typing import List, Dict, Optional
from pathlib import Path
import json
import os

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.tui.output import OutputToolkit
from core.services.error_contract import CommandError

logger = get_logger("core", category="script-runner", name="script-handler")


class ScriptHandler(BaseCommandHandler):
    """Handler for SCRIPT command - manage and run markdown scripts."""

    def __init__(self):
        super().__init__()
        self.repo_root = get_repo_root()
        env_memory = os.environ.get("UDOS_MEMORY_ROOT")
        if env_memory:
            self.memory_root = Path(env_memory)
        else:
            self.memory_root = self.repo_root / "memory"
        self.script_dirs = [
            self.memory_root / "bank" / "system",
            self.memory_root / "system",
        ]

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._list_scripts()

        action = params[0].upper()
        args = params[1:]

        if action in {"LIST", "LS"}:
            return self._list_scripts()
        if action in {"RUN", "EXECUTE"}:
            return self._run_script(args)
        if action in {"LOG", "LOGS", "HISTORY"}:
            return self._show_logs(args)
        if action in {"HELP", "--HELP", "-H", "?"}:
            return self._help()

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown SCRIPT option: {action}",
            recovery_hint="Use SCRIPT LIST, RUN, LOG, or HELP",
            level="INFO",
        )

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("SCRIPT"),
                "SCRIPT LIST             Show available scripts",
                "SCRIPT RUN <name>       Execute a script",
                "SCRIPT LOG [name]       View script logs",
            ]
        )

    def _help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _discover_scripts(self) -> List[Path]:
        scripts: List[Path] = []
        for directory in self.script_dirs:
            if not directory.exists():
                continue
            scripts.extend(sorted(p for p in directory.glob("*.md") if p.is_file()))
        return scripts

    def _resolve_script(self, identifier: str) -> Optional[Path]:
        if not identifier:
            return None
        candidate = Path(identifier)
        if candidate.exists():
            return candidate

        normalized = identifier
        if not normalized.endswith(".md"):
            normalized = normalized + ".md"

        for directory in self.script_dirs:
            target = directory / normalized
            if target.exists():
                return target
        return None

    def _list_scripts(self) -> Dict:
        banner = OutputToolkit.banner("SCRIPTS")
        scripts = self._discover_scripts()
        lines = [banner, ""]
        if not scripts:
            lines.append("(no scripts found)")
            return {"status": "success", "output": "\n".join(lines)}

        for script in scripts:
            rel_path = script.relative_to(self.repo_root) if script.is_absolute() else script
            lines.append(f"- {script.stem}")
            lines.append(f"  {rel_path}")
            lines.append("")
        return {"status": "success", "output": "\n".join(lines)}

    def _run_script(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("SCRIPT RUN")
        if not args:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Missing script name",
                recovery_hint="Use SCRIPT RUN <name>",
                level="INFO",
            )

        script = self._resolve_script(args[0])
        if not script:
            raise CommandError(
                code="ERR_IO_FILE_NOT_FOUND",
                message=f"Script not found: {args[0]}",
                recovery_hint="Run SCRIPT LIST to see available scripts",
                level="ERROR",
            )

        service = TSRuntimeService()
        result = service.execute(script)
        status = result.get("status")
        payload = result.get("payload", {})
        output = ""
        if payload:
            exec_result = payload.get("result", {})
            output = exec_result.get("output", "")

        logger.event(
            "info" if status == "success" else "error",
            "script.run",
            f"Script run {script.name} -> {status}",
            ctx={
                "script": str(script),
                "status": status,
            },
        )

        lines = [banner, ""]
        if status != "success":
            lines.append(f"❌ {result.get('message', 'Script failed')}")
            details = result.get("details")
            if details:
                lines.append(details)
            return {"status": "error", "output": "\n".join(lines)}

        lines.append(f"✅ Executed {script.name}")
        if output:
            lines.append("")
            lines.append("Output:")
            lines.append(output.strip())
        return {"status": "success", "output": "\n".join(lines)}

    def _show_logs(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("SCRIPT LOGS")
        name_filter = args[0] if args else None

        log_dir = self.repo_root / "memory" / "logs" / "udos" / "core"
        if not log_dir.exists():
            return {"status": "success", "output": banner + "\n(no log directory found)"}

        entries: List[Dict] = []
        for log_file in sorted(log_dir.glob("*.jsonl")):
            try:
                for line in log_file.read_text().splitlines():
                    if not line.strip():
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if payload.get("category") not in {"system-script", "script-runner"}:
                        continue
                    if name_filter:
                        msg = payload.get("msg", "")
                        ctx = payload.get("ctx", {})
                        if name_filter not in msg and name_filter not in str(ctx.get("script", "")):
                            continue
                    entries.append(payload)
            except Exception:
                continue

        entries = entries[-25:]
        lines = [banner, ""]
        if not entries:
            lines.append("(no script log entries found)")
            return {"status": "success", "output": "\n".join(lines)}

        for entry in entries:
            lines.append(f"- {entry.get('ts')} {entry.get('msg')}")
        return {"status": "success", "output": "\n".join(lines)}

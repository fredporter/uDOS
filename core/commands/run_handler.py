"""RUN command handler - execute TS markdown scripts, TS data ops, or explicit Python scripts."""

from pathlib import Path
import json
import subprocess
import sys
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.tui.output import OutputToolkit


class RunHandler(BaseCommandHandler):
    """Handler for RUN command with explicit engine selection (--ts|--py)."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return {
                "status": "error", "message": "Usage: RUN [--ts|--py] <file> [section_id] | RUN [--ts] PARSE <file> | RUN [--ts] DATA ...",
            }

        run_mode = "ts"
        args = params[:]
        while args and args[0].lower() in {"--ts", "--py"}:
            run_mode = args[0][2:].lower()
            args = args[1:]

        if not args:
            return {
                "status": "error",
                "message": "Usage: RUN [--ts|--py] <file> [section_id] | RUN [--ts] PARSE <file> | RUN [--ts] DATA ...",
            }

        if run_mode == "py":
            if args[0].upper() in {"PARSE", "DATA"}:
                return {"status": "error", "message": "RUN --py supports script execution only (no PARSE/DATA)"}
            return self._run_python(args)

        if args[0].upper() == "DATA":
            return self._run_data(args[1:])

        if args[0].upper() == "PARSE":
            if len(args) < 2:
                return {"status": "error", "message": "Usage: RUN PARSE <file>"}
            file_arg = args[1]
            script_path = self._resolve_path(file_arg)
            service = TSRuntimeService()
            result = service.parse(script_path)
            if result.get("status") != "success":
                return result
            payload = result.get("payload", {})
            sections = payload.get("sections", [])
            if not sections:
                return {
                    "status": "success",
                    "message": "Parsed script",
                    "output": "No sections found.",
                }
            rows = [
                [section.get("id", ""), section.get("title", ""), section.get("blocks", 0)]
                for section in sections
            ]
            output = OutputToolkit.table(["id", "title", "blocks"], rows)
            return {
                "status": "success",
                "message": "Parsed script",
                "output": output,
                "sections": sections,
            }

        from core.services.user_service import is_ghost_mode

        if is_ghost_mode():
            return {
                "status": "warning",
                "message": "Ghost Mode is read-only (RUN blocked)",
                "output": "Ghost Mode active: RUN execution is disabled. Use RUN PARSE to inspect scripts.",
            }

        file_arg = args[0]
        section_id = args[1] if len(args) > 1 else None

        script_path = self._resolve_path(file_arg)
        service = TSRuntimeService()
        result = service.execute(script_path, section_id=section_id)

        if result.get("status") != "success":
            return result

        payload = result.get("payload", {})
        exec_result = payload.get("result", {})
        output = exec_result.get("output") or ""
        return {
            "status": "success",
            "message": "Script executed",
            "output": output,
            "runtime": payload,
        }

    def _run_python(self, params: List[str]) -> Dict:
        file_arg = params[0]
        script_path = self._resolve_path(file_arg)
        if not script_path.exists():
            return {"status": "error", "message": f"Script not found: {script_path}"}
        if script_path.suffix.lower() != ".py":
            return {"status": "error", "message": "RUN --py requires a .py file"}

        cmd = [sys.executable, str(script_path), *params[1:]]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "Python script failed",
                "details": result.stderr.strip() or result.stdout.strip(),
            }
        return {
            "status": "success",
            "message": "Python script executed",
            "output": result.stdout.strip(),
        }

    def _run_data(self, params: List[str]) -> Dict:
        if not params:
            return {
                "status": "error",
                "message": "Usage: RUN DATA <LIST|VALIDATE|BUILD|REGEN> [args]",
            }

        action = params[0].upper()
        args = params[1:]
        script = get_repo_root() / "core" / "runtime" / "data_runner.js"
        if not script.exists():
            return {"status": "error", "message": f"Data runner missing: {script}"}

        ts_runtime = TSRuntimeService()
        cmd = [ts_runtime.node_cmd, str(script), action.lower(), *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "RUN DATA failed",
                "details": result.stderr.strip() or result.stdout.strip(),
            }

        try:
            payload = json.loads(result.stdout.strip() or "{}")
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "RUN DATA returned invalid JSON",
                "details": result.stdout.strip(),
            }

        status = payload.get("status", "error")
        if action == "LIST" and status == "success":
            datasets = payload.get("datasets", [])
            rows = [[d.get("id", ""), d.get("type", ""), d.get("path", "")] for d in datasets]
            output = "\n".join(
                [
                    OutputToolkit.banner("RUN DATA LIST"),
                    OutputToolkit.table(["id", "type", "path"], rows) if rows else "(none)",
                ]
            )
            return {"status": "success", "message": "Datasets", "output": output, "datasets": datasets}

        banner = OutputToolkit.banner(f"RUN DATA {action}")
        lines = [banner]
        if payload.get("message"):
            lines.append(payload["message"])
        if payload.get("output"):
            lines.append(f"Output: {payload['output']}")
        if payload.get("invalid") is not None:
            lines.append(f"Invalid cells: {payload['invalid']}")
        if payload.get("sample"):
            sample_rows = [[s.get("location", ""), s.get("cell", ""), s.get("reason", "")] for s in payload["sample"]]
            lines.append(OutputToolkit.table(["location", "cell", "reason"], sample_rows))
        if payload.get("locations") is not None:
            lines.append(f"Locations: {payload['locations']}")
        if payload.get("dropped_cells") is not None:
            lines.append(f"Dropped cells: {payload['dropped_cells']}")

        return {"status": status, "message": payload.get("message", "RUN DATA complete"), "output": "\n".join(lines), "payload": payload}

    def _resolve_path(self, file_arg: str) -> Path:
        path = Path(file_arg)
        if not path.is_absolute():
            return get_repo_root() / path
        return path

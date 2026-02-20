"""
GRID command handler - Render UGRID canvas outputs.

Routes to the TypeScript UGRID renderer (core/dist/grid/cli.js) via Node.
Supports calendar, table, schedule, map, dashboard, and workflow modes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseCommandHandler
from .handler_logging_mixin import HandlerLoggingMixin
from core.services.error_contract import CommandError
from core.services.logging_api import get_logger, get_repo_root


class GridHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Render 80x30 grid canvas outputs via UGRID."""

    MODES = {"calendar", "table", "schedule", "map", "dashboard", "workflow"}

    def __init__(self):
        super().__init__()
        self.logger = get_logger("core", category="command", name="grid")
        self.repo_root = get_repo_root()
        self.node_cmd = self._load_node_cmd()
        self.cli_path = self.repo_root / "core" / "dist" / "grid" / "cli.js"

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        with self.trace_command(command, params) as trace:
            if not self.cli_path.exists():
                trace.set_status("error")
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message="UGRID renderer not found",
                    recovery_hint="Rebuild grid runtime or restore core/dist/grid",
                    details={"missing": str(self.cli_path)},
                    level="ERROR",
                )

            try:
                opts = self._parse_params(params)
            except CommandError as exc:
                trace.set_status("error")
                self.log_param_error(command, params, str(exc))
                raise

            trace.add_event("grid_options", {"mode": opts["mode"]})

            output = self._run_node_render(opts)
            from core.tui.output import OutputToolkit

            trace.set_status("success")
            return {
                "status": "success",
                "message": f"GRID render ({opts['mode']})",
                "output": "\n".join(
                    [
                        OutputToolkit.banner(f"GRID {opts['mode'].upper()}"),
                        output,
                    ]
                ),
                "grid_raw": output,
                "mode": opts["mode"],
            }

    def _parse_params(self, params: List[str]) -> Dict[str, Optional[str]]:
        mode: Optional[str] = None
        input_path: Optional[str] = None
        loc: Optional[str] = None
        layer: Optional[str] = None
        title: Optional[str] = None
        theme: Optional[str] = None
        output_path: Optional[str] = None

        idx = 0
        while idx < len(params):
            arg = params[idx]
            if arg == "--mode":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --mode requires a value",
                        recovery_hint="Usage: GRID --mode <calendar|table|schedule|map|dashboard|workflow>",
                        level="INFO",
                    )
                mode = params[idx].lower()
            elif arg == "--input":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --input requires a file path",
                        recovery_hint="Usage: GRID --input <path/to/input.json>",
                        level="INFO",
                    )
                input_path = params[idx]
            elif arg == "--loc":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --loc requires a LocId value",
                        recovery_hint="Usage: GRID --loc <LocId>",
                        level="INFO",
                    )
                loc = params[idx]
            elif arg == "--layer":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --layer requires a value",
                        recovery_hint="Usage: GRID --layer <layer>",
                        level="INFO",
                    )
                layer = params[idx]
            elif arg == "--title":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --title requires a value",
                        recovery_hint="Usage: GRID --title <title>",
                        level="INFO",
                    )
                title = params[idx]
            elif arg == "--theme":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --theme requires a value",
                        recovery_hint="Usage: GRID --theme <theme>",
                        level="INFO",
                    )
                theme = params[idx]
            elif arg == "--output":
                idx += 1
                if idx >= len(params):
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="GRID --output requires a file path",
                        recovery_hint="Usage: GRID --output <path/to/output.txt>",
                        level="INFO",
                    )
                output_path = params[idx]
            else:
                if mode is None and arg.lower() in self.MODES:
                    mode = arg.lower()
                elif input_path is None and arg.lower().endswith(".json"):
                    input_path = arg
                elif loc is None and not arg.startswith("--"):
                    loc = arg
            idx += 1

        if mode is None:
            mode = "calendar"
        if mode not in self.MODES:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"GRID mode must be one of: {', '.join(sorted(self.MODES))}",
                recovery_hint="Use GRID --mode <calendar|table|schedule|map|dashboard|workflow>",
                level="INFO",
            )

        return {
            "mode": mode,
            "input": input_path,
            "loc": loc,
            "layer": layer,
            "title": title,
            "theme": theme,
            "output": output_path,
        }

    def _load_node_cmd(self) -> str:
        runtime_config = self.repo_root / "core" / "config" / "runtime.json"
        if runtime_config.exists():
            try:
                import json

                data = json.loads(runtime_config.read_text())
                return data.get("node_cmd", "node")
            except Exception:
                pass
        return "node"

    def _run_node_render(self, opts: Dict[str, Optional[str]]) -> str:
        cmd = [self.node_cmd, str(self.cli_path), "--mode", opts["mode"]]

        if opts.get("input"):
            input_path = Path(opts["input"])
            if not input_path.is_absolute():
                input_path = self.repo_root / input_path
            if not input_path.exists():
                raise CommandError(
                    code="ERR_IO_FILE_NOT_FOUND",
                    message=f"Input JSON not found: {input_path}",
                    recovery_hint="Check the input path or run GRID without --input",
                    level="INFO",
                )
            cmd.extend(["--input", str(input_path)])
        if opts.get("loc"):
            cmd.extend(["--loc", opts["loc"]])
        if opts.get("layer"):
            cmd.extend(["--layer", opts["layer"]])
        if opts.get("title"):
            cmd.extend(["--title", opts["title"]])
        if opts.get("theme"):
            cmd.extend(["--theme", opts["theme"]])
        if opts.get("output"):
            output_path = Path(opts["output"])
            if not output_path.is_absolute():
                output_path = self.repo_root / output_path
            cmd.extend(["--output", str(output_path)])

        try:
            # Use ESM import to execute cli main (direct node cli.js won't run under ESM)
            import json as _json

            script = f"import {{main}} from '{self.cli_path.as_posix()}'; main({_json.dumps(cmd[2:])});"
            result = subprocess.run(
                [self.node_cmd, "--input-type=module", "-e", script],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="Node.js not available",
                recovery_hint="Install Node.js and ensure `node` is on PATH",
                level="ERROR",
            )
        except Exception as exc:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message="Failed to invoke UGRID renderer",
                recovery_hint="Check Node.js install and grid runtime build",
                details={"error": str(exc)},
                level="ERROR",
            )

        if result.returncode != 0:
            raise CommandError(
                code="ERR_RUNTIME_EXECUTION_FAILED",
                message="UGRID renderer failed",
                recovery_hint="Run GRID again or rebuild the grid runtime",
                details={"stderr": result.stderr.strip() or result.stdout.strip()},
                level="ERROR",
            )

        output = result.stdout.strip()
        if not output:
            raise CommandError(
                code="ERR_RUNTIME_EMPTY_OUTPUT",
                message="UGRID renderer returned empty output",
                recovery_hint="Check input data or rebuild grid runtime",
                level="WARNING",
            )

        return output

        return {"status": "success", "output": output}

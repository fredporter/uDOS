"""VERIFY command handler - TS runtime/script verification checks."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService


class VerifyHandler(BaseCommandHandler):
    """Handler for VERIFY command - TypeScript runtime checks."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        repo = get_repo_root()
        runtime = TSRuntimeService()

        checks: List[Tuple[str, bool]] = []
        checks.append(("node available", shutil.which("node") is not None))
        checks.append(("ts runner exists", runtime.runner_path.exists()))
        checks.append(("runtime entry exists", runtime.runtime_entry.exists()))
        checks.append(("runtime config exists", (repo / "core" / "config" / "runtime.json").exists()))

        parse_ok = False
        exec_ok = False
        parse_error = ""
        exec_error = ""

        with tempfile.TemporaryDirectory(prefix="udos-verify-") as tmp:
            sample = Path(tmp) / "verify-script.md"
            sample.write_text(
                "---\n"
                "title: Verify Script\n"
                "id: verify-script\n"
                "version: 1.0\n"
                "---\n\n"
                "## Smoke\n\n"
                "Simple section for runtime verification.\n",
                encoding="utf-8",
            )

            parse_result = runtime.parse(sample)
            parse_ok = parse_result.get("status") == "success"
            if not parse_ok:
                parse_error = parse_result.get("message", "parse failed")

            exec_result = runtime.execute(sample)
            exec_ok = exec_result.get("status") == "success"
            if not exec_ok:
                exec_error = exec_result.get("message", "execute failed")

        checks.append(("ts runtime parse smoke", parse_ok))
        checks.append(("ts runtime execute smoke", exec_ok))

        passed = sum(1 for _, ok in checks if ok)
        failed = len(checks) - passed
        status = "success" if failed == 0 else "warning"

        output = [OutputToolkit.banner("VERIFY"), ""]
        output.append(OutputToolkit.checklist([(name, ok) for name, ok in checks]))
        output.append("")
        output.append(f"Summary: {passed}/{len(checks)} checks passed")
        if parse_error:
            output.append(f"Parse issue: {parse_error}")
        if exec_error:
            output.append(f"Exec issue: {exec_error}")

        return {
            "status": status,
            "message": "TS runtime verification complete",
            "output": "\n".join(output),
            "checks_passed": passed,
            "checks_total": len(checks),
        }

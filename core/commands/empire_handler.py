"""EMPIRE command handler - private extension controls."""

from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("empire-handler")


class EmpireHandler(BaseCommandHandler):
    """Handler for EMPIRE command - start/stop/rebuild and suite launch."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._show_help()

        action = params[0].lower().strip()
        if not action:
            return self._show_help()

        from core.services.user_service import is_ghost_mode

        if is_ghost_mode() and action in {"rebuild", "--rebuild", "start", "--start", "stop", "--stop"}:
            return {
                "status": "warning",
                "message": "Ghost Mode is read-only (Empire control blocked)",
                "output": self._help_text(),
            }

        if action in {"rebuild", "--rebuild"}:
            return self._rebuild_empire()
        if action in {"start", "--start"}:
            return self._start_empire()
        if action in {"stop", "--stop"}:
            return self._stop_empire()
        if action in {"ingest"}:
            return self._ingest(params[1:])
        if action in {"normalize"}:
            return self._normalize(params[1:])
        if action in {"sync"}:
            return self._sync(params[1:])
        if action in {"api"}:
            return self._api(params[1:])
        if action in {"email"}:
            return self._email(params[1:])
        if action in {"help", "--help", "?"}:
            return self._show_help()

        return {
            "status": "error",
            "message": f"Unknown option: {action}",
            "output": self._help_text(),
        }

    def _empire_root(self) -> Optional[Path]:
        repo_root = get_repo_root()
        path = Path(repo_root) / "empire"
        return path if path.exists() else None

    def _suite_path(self) -> Optional[Path]:
        root = self._empire_root()
        if not root:
            return None
        suite = root / "web" / "index.html"
        return suite if suite.exists() else None

    def _prompt_open_suite(self, suite_path: Path) -> Optional[bool]:
        try:
            response = input("Open Empire Suite...? [Yes|No|OK] ").strip().lower()
        except Exception:
            return None
        if response in {"yes", "y", "ok", "okay"}:
            return True
        if response in {"no", "n"}:
            return False
        return None

    def _open_suite(self, suite_path: Path) -> str:
        try:
            webbrowser.open(suite_path.resolve().as_uri())
            return f"✅ Opened Empire Suite: {suite_path}"
        except Exception as exc:
            logger.error(f"[LOCAL] Failed to open Empire Suite: {exc}")
            return f"❌ Failed to open Empire Suite: {exc}"

    def _show_help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("EMPIRE"),
                "EMPIRE START      Start Empire services",
                "EMPIRE STOP       Stop Empire services",
                "EMPIRE REBUILD    Rebuild Empire suite assets",
                "EMPIRE INGEST     Ingest raw records into JSONL",
                "EMPIRE NORMALIZE  Normalize + persist records",
                "EMPIRE SYNC       Refresh overview + sync state",
                "EMPIRE API        Start/stop Empire API server",
                "EMPIRE EMAIL      Email receive/process scaffolding",
                "EMPIRE HELP       Show this help",
            ]
        )

    def _start_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE START")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        output_lines.append("✅ Empire extension detected")
        suite_path = self._suite_path()
        if suite_path:
            decision = self._prompt_open_suite(suite_path)
            if decision:
                output_lines.append(self._open_suite(suite_path))
            elif decision is False:
                output_lines.append("Skipped opening Empire Suite")
            else:
                output_lines.append("No response; Empire Suite not opened")
        else:
            output_lines.append("⚠️  Empire Suite page not found (web/index.html)")

        return {"status": "success", "output": "\n".join(output_lines)}

    def _stop_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE STOP")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        output_lines.append("Stopping Empire services...")
        output_lines.append("✅ Empire stopped (no background services running)")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _rebuild_empire(self) -> Dict:
        banner = OutputToolkit.banner("EMPIRE REBUILD")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        web_root = empire_root / "web"
        package_json = web_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(web_root),
                    capture_output=False,
                    check=False,
                )
                if result.returncode != 0:
                    output_lines.append("❌ Empire build failed")
                    return {"status": "error", "output": "\n".join(output_lines)}
                output_lines.append("✅ Empire build complete")
                return {"status": "success", "output": "\n".join(output_lines)}
            except Exception as exc:
                output_lines.append(f"❌ Empire build error: {exc}")
                return {"status": "error", "output": "\n".join(output_lines)}

        output_lines.append("✅ Empire rebuild skipped (no build system detected)")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _ingest(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("EMPIRE INGEST")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        if not args:
            output_lines.append("Usage: EMPIRE INGEST <input> [--out <path>] [--source <label>]")
            return {"status": "error", "output": "\n".join(output_lines)}

        input_path = args[0]
        out_path = str(empire_root / "data" / "raw" / "records.jsonl")
        source_label = None

        if "--out" in args:
            idx = args.index("--out")
            if idx + 1 < len(args):
                out_path = args[idx + 1]
        if "--source" in args:
            idx = args.index("--source")
            if idx + 1 < len(args):
                source_label = args[idx + 1]

        script = empire_root / "scripts" / "ingest" / "run_ingest.py"
        cmd = ["python3", str(script), input_path, "--out", out_path]
        if source_label:
            cmd.extend(["--source", source_label])

        result = subprocess.run(cmd, capture_output=False, check=False, cwd=str(empire_root))
        if result.returncode != 0:
            output_lines.append("❌ Ingest failed")
            return {"status": "error", "output": "\n".join(output_lines)}

        output_lines.append(f"✅ Ingested records -> {out_path}")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _normalize(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("EMPIRE NORMALIZE")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        input_path = str(empire_root / "data" / "raw" / "records.jsonl")
        output_path = str(empire_root / "data" / "normalized" / "records.jsonl")
        db_path = str(empire_root / "data" / "empire.db")
        persist = True

        if "--in" in args:
            idx = args.index("--in")
            if idx + 1 < len(args):
                input_path = args[idx + 1]
        if "--out" in args:
            idx = args.index("--out")
            if idx + 1 < len(args):
                output_path = args[idx + 1]
        if "--db" in args:
            idx = args.index("--db")
            if idx + 1 < len(args):
                db_path = args[idx + 1]
        if "--no-persist" in args:
            persist = False

        script = empire_root / "scripts" / "process" / "normalize_records.py"
        cmd = ["python3", str(script), "--in", input_path, "--out", output_path]
        if db_path:
            cmd.extend(["--db", db_path])
        if not persist:
            cmd.append("--no-persist")

        result = subprocess.run(cmd, capture_output=False, check=False, cwd=str(empire_root))
        if result.returncode != 0:
            output_lines.append("❌ Normalize failed")
            return {"status": "error", "output": "\n".join(output_lines)}

        output_lines.append(f"✅ Normalized records -> {output_path}")
        if persist:
            output_lines.append(f"✅ Persisted to DB -> {db_path}")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _sync(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("EMPIRE SYNC")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        api_base = "http://127.0.0.1:8991"
        token = os.getenv("EMPIRE_API_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            import requests

            resp = requests.get(f"{api_base}/health", headers=headers, timeout=3)
            if resp.status_code != 200:
                output_lines.append(f"⚠️  API unhealthy: HTTP {resp.status_code}")
                return self._start_api_then_check(output_lines, api_base, headers)
        except Exception:
            output_lines.append("⚠️  API not running. Starting now...")
            return self._start_api_then_check(output_lines, api_base, headers)

        output_lines.append("✅ Empire API reachable")
        output_lines.append("✅ UI auto-refreshes from live API")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _start_api_then_check(self, output_lines: List[str], api_base: str, headers: Dict[str, str]) -> Dict:
        empire_root = self._empire_root()
        if not empire_root:
            output_lines.append("❌ Empire submodule not found")
            return {"status": "error", "output": "\n".join(output_lines)}

        cmd = ["python3", "-m", "uvicorn", "empire.api.server:app", "--host", "127.0.0.1", "--port", "8991"]
        subprocess.Popen(cmd, cwd=str(empire_root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            import time
            import requests

            for _ in range(10):
                try:
                    resp = requests.get(f"{api_base}/health", headers=headers, timeout=2)
                    if resp.status_code == 200:
                        output_lines.append("✅ Empire API started")
                        output_lines.append("✅ UI auto-refreshes from live API")
                        return {"status": "success", "output": "\n".join(output_lines)}
                except Exception:
                    pass
                time.sleep(0.5)
        except Exception:
            pass

        output_lines.append("❌ Failed to start Empire API")
        return {"status": "error", "output": "\n".join(output_lines)}

    def _email(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("EMPIRE EMAIL")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        if not args:
            output_lines.append("Usage: EMPIRE EMAIL RECEIVE|PROCESS [options]")
            return {"status": "error", "output": "\n".join(output_lines)}

        sub = args[0].lower()
        if sub == "receive":
            script = empire_root / "scripts" / "email" / "receive_emails.py"
            cmd = ["python3", str(script)] + args[1:]
        elif sub == "process":
            script = empire_root / "scripts" / "email" / "process_emails.py"
            cmd = ["python3", str(script)] + args[1:]
        else:
            output_lines.append("Usage: EMPIRE EMAIL RECEIVE|PROCESS [options]")
            return {"status": "error", "output": "\n".join(output_lines)}

        result = subprocess.run(cmd, capture_output=False, check=False, cwd=str(empire_root))
        if result.returncode != 0:
            output_lines.append("❌ Email command failed")
            return {"status": "error", "output": "\n".join(output_lines)}

        output_lines.append("✅ Email command complete")
        return {"status": "success", "output": "\n".join(output_lines)}

    def _api(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("EMPIRE API")
        output_lines = [banner, ""]

        empire_root = self._empire_root()
        if not empire_root:
            return {
                "status": "error",
                "message": "Empire extension not available",
                "output": banner + "\n❌ Empire submodule not found",
            }

        if not args:
            output_lines.append("Usage: EMPIRE API START|STOP")
            return {"status": "error", "output": "\n".join(output_lines)}

        action = args[0].lower()
        if action == "start":
            cmd = ["python3", "-m", "uvicorn", "empire.api.server:app", "--host", "127.0.0.1", "--port", "8991"]
            subprocess.Popen(cmd, cwd=str(empire_root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            output_lines.append("✅ Empire API started on http://127.0.0.1:8991")
            return {"status": "success", "output": "\n".join(output_lines)}
        if action == "stop":
            subprocess.run(["pkill", "-f", "empire.api.server:app"], capture_output=True)
            output_lines.append("✅ Empire API stopped")
            return {"status": "success", "output": "\n".join(output_lines)}

        output_lines.append("Usage: EMPIRE API START|STOP")
        return {"status": "error", "output": "\n".join(output_lines)}

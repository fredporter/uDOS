"""Shared PTY adapter runtime for TOYBOX upstream game integrations."""

from __future__ import annotations

import json
import os
import pty
import re
import shlex
import shutil
import signal
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.services.logging_api import get_repo_root


class InputRequest(BaseModel):
    text: str


class PTYAdapter:
    """Run an upstream binary in a PTY and expose minimal HTTP controls."""

    def __init__(
        self,
        *,
        adapter_id: str,
        env_cmd_var: str,
        command_candidates: List[str],
        startup_args: Optional[List[str]] = None,
        parse_fn: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
    ) -> None:
        self.adapter_id = adapter_id
        self.env_cmd_var = env_cmd_var
        self.command_candidates = command_candidates
        self.startup_args = startup_args or []
        self.parse_fn = parse_fn

        self.repo_root = get_repo_root()
        self.event_file = self.repo_root / "memory" / "bank" / "private" / "gameplay_events.ndjson"
        self.event_file.parent.mkdir(parents=True, exist_ok=True)

        self.proc_pid: Optional[int] = None
        self.returncode: Optional[int] = None
        self.master_fd: Optional[int] = None
        self.buffer: Deque[str] = deque(maxlen=2000)
        self.running = False
        self._reader_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_error: Optional[str] = None
        self._resolved_command: Optional[List[str]] = None
        self._last_depth = 1

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _resolve_command(self) -> List[str]:
        env_cmd = os.getenv(self.env_cmd_var, "").strip()
        if env_cmd:
            return shlex.split(env_cmd)

        for candidate in self.command_candidates:
            path = shutil.which(candidate)
            if path:
                return [path]

        raise RuntimeError(
            f"No upstream runtime found for {self.adapter_id}. Set {self.env_cmd_var} or install one of: "
            + ", ".join(self.command_candidates)
        )

    def start(self) -> None:
        if self.running:
            return
        cmd = self._resolve_command()
        cmd = cmd + self.startup_args
        self._resolved_command = cmd

        proc_env = os.environ.copy()
        proc_env.setdefault("TERM", "xterm-256color")
        proc_env.setdefault("LINES", "30")
        proc_env.setdefault("COLUMNS", "100")
        pid, master_fd = pty.fork()
        if pid == 0:
            os.chdir(str(self.repo_root))
            try:
                os.execvpe(cmd[0], cmd, proc_env)
            except Exception:
                os._exit(127)
        self.master_fd = master_fd
        self.proc_pid = pid
        self.returncode = None
        self.running = True
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()
        self._emit_event("TOYBOX_RUNTIME_STARTED", {"command": cmd})

    def stop(self) -> None:
        if not self.running:
            return
        try:
            if self.proc_pid:
                os.kill(self.proc_pid, signal.SIGTERM)
                for _ in range(30):
                    waited_pid, status = os.waitpid(self.proc_pid, os.WNOHANG)
                    if waited_pid == self.proc_pid:
                        if os.WIFEXITED(status):
                            self.returncode = os.WEXITSTATUS(status)
                        elif os.WIFSIGNALED(status):
                            self.returncode = -os.WTERMSIG(status)
                        break
                    time.sleep(0.1)
        except Exception:
            if self.proc_pid:
                try:
                    os.kill(self.proc_pid, signal.SIGKILL)
                except Exception:
                    pass
        finally:
            self.running = False
            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except Exception:
                    pass
                self.master_fd = None
            self.proc_pid = None
            self._emit_event("TOYBOX_RUNTIME_STOPPED", {})

    def send(self, text: str) -> None:
        if not self.running or self.master_fd is None:
            raise RuntimeError("Runtime is not running")
        payload = text
        if not payload.endswith("\n"):
            payload += "\n"
        os.write(self.master_fd, payload.encode("utf-8", errors="ignore"))

    def _reader_loop(self) -> None:
        line_buf = ""
        while self.running and self.master_fd is not None:
            try:
                chunk = os.read(self.master_fd, 4096)
                if not chunk:
                    time.sleep(0.05)
                    continue
                text = chunk.decode("utf-8", errors="ignore")
                with self._lock:
                    self.buffer.append(text)
                line_buf += text
                while "\n" in line_buf:
                    line, line_buf = line_buf.split("\n", 1)
                    self._handle_line(line.rstrip("\r"))
            except OSError:
                break
            except Exception as exc:
                self._last_error = str(exc)
                break
        self.running = False
        if self.proc_pid:
            try:
                waited_pid, status = os.waitpid(self.proc_pid, os.WNOHANG)
                if waited_pid == self.proc_pid:
                    if os.WIFEXITED(status):
                        self.returncode = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        self.returncode = -os.WTERMSIG(status)
            except Exception:
                pass

    def _handle_line(self, line: str) -> None:
        if not line:
            return
        depth_match = re.search(r"\blevel\s+(\d+)\b", line, re.IGNORECASE)
        if depth_match:
            self._last_depth = max(self._last_depth, int(depth_match.group(1)))

        if self.parse_fn:
            events = self.parse_fn(line) or []
            for event in events:
                payload = dict(event.get("payload") or {})
                payload.setdefault("depth", self._last_depth)
                self._emit_event(str(event.get("type", "TOYBOX_OUTPUT_EVENT")), payload)

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        row = {
            "ts": self._now_iso(),
            "source": f"toybox:{self.adapter_id}",
            "type": event_type,
            "payload": payload,
        }
        with self.event_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")

    def status(self) -> Dict[str, Any]:
        alive = False
        if self.proc_pid:
            try:
                os.kill(self.proc_pid, 0)
                alive = True
            except OSError:
                alive = False
        return {
            "adapter_id": self.adapter_id,
            "running": bool(self.running and alive),
            "pid": self.proc_pid,
            "returncode": self.returncode,
            "command": self._resolved_command,
            "last_error": self._last_error,
            "depth": self._last_depth,
        }

    def output_text(self, tail_chars: int = 16000) -> str:
        with self._lock:
            text = "".join(self.buffer)
        return text[-tail_chars:]


def create_app(adapter: PTYAdapter) -> FastAPI:
    app = FastAPI(title=f"TOYBOX {adapter.adapter_id}")

    @app.on_event("startup")
    def _startup() -> None:
        adapter.start()

    @app.on_event("shutdown")
    def _shutdown() -> None:
        adapter.stop()

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"ok": True, **adapter.status()}

    @app.get("/status")
    def status() -> Dict[str, Any]:
        return adapter.status()

    @app.get("/output")
    def output() -> Dict[str, Any]:
        return {"output": adapter.output_text()}

    @app.post("/input")
    def input_text(req: InputRequest) -> Dict[str, Any]:
        try:
            adapter.send(req.text)
            return {"ok": True}
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @app.get("/")
    def index() -> str:
        return (
            "<!doctype html><html><head><title>TOYBOX</title></head><body>"
            "<h1>TOYBOX Runtime</h1>"
            "<p>Use /output and /input endpoints for PTY interaction.</p>"
            "</body></html>"
        )

    return app

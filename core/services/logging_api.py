"""
uDOS Logging API (v1.3)

Structured, switchable, low-overhead logging for Core + Wizard.
Defaults to JSONL file sink with optional pretty console output.
"""

from __future__ import annotations

import json
import os
import random
import secrets
import sys
import threading
import time
import traceback
import contextvars
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

LOG_SCHEMA_ID = "udos-log-v1.3"

_CORR_ID: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "udos_corr_id", default=None
)

_LEVEL_ORDER = {
    "trace": 5,
    "debug": 10,
    "info": 20,
    "warn": 30,
    "error": 40,
    "fatal": 50,
}

_REDACT_KEYS = {
    "password",
    "pass",
    "secret",
    "token",
    "api_key",
    "authorization",
    "cookie",
    "set-cookie",
    "session",
    "jwt",
    "private_key",
}

_PAYLOAD_KEYS = {
    "payload",
    "payloads",
    "body",
    "request",
    "response",
    "data",
    "content",
}


class LogTags:
    """Standard logging tags for transport identification."""

    LOCAL = "[LOCAL]"  # Local device operation
    MESH = "[MESH]"  # MeshCore P2P
    BT_PRIV = "[BT-PRIV]"  # Bluetooth Private (paired devices)
    BT_PUB = "[BT-PUB]"  # Bluetooth Public (beacons only - NO DATA)
    NFC = "[NFC]"  # NFC contact
    QR = "[QR]"  # QR relay
    AUD = "[AUD]"  # Audio transport
    WIZ = "[WIZ]"  # Wizard Server operation
    GMAIL = "[GMAIL]"  # Gmail relay (Wizard only)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _mono_ms() -> int:
    return int(time.monotonic() * 1000)


def _short_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_urlsafe(8)}"


def _coerce_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_float(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _split_csv(value: Optional[str]) -> Optional[set[str]]:
    if not value:
        return None
    items = [v.strip() for v in value.split(",") if v.strip()]
    return set(items) if items else None


def _home_root() -> Path:
    return Path.home() / "uDOS"


def _enforce_home_root(candidate: Path) -> Path:
    home_root = _home_root()
    if home_root.exists() or os.getenv("UDOS_HOME_ROOT_ENFORCE") == "1":
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            resolved = candidate
        if not str(resolved).startswith(str(home_root)):
            if os.getenv("UDOS_HOME_ROOT_ALLOW_OUTSIDE") == "1":
                return candidate
            raise RuntimeError(
                "Repo root outside ~/uDOS. Move the repo under ~/uDOS or set "
                "UDOS_HOME_ROOT_ALLOW_OUTSIDE=1 to bypass."
            )
    return candidate


def _default_log_root() -> Path:
    env_root = os.getenv("UDOS_LOG_ROOT")
    if env_root:
        return Path(env_root).expanduser()
    try:
        return get_repo_root() / "memory" / "logs" / "udos"
    except Exception:
        return Path.home() / "memory" / "logs" / "udos"


def get_repo_root() -> Path:
    """Get repository root, honoring UDOS_ROOT when provided."""
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        if not env_path.is_absolute():
            env_path = (Path.cwd() / env_path).resolve()
        marker = env_path / "uDOS.py"

        if marker.exists():
            return _enforce_home_root(env_path)
        raise RuntimeError(
            f"UDOS_ROOT={env_root} does not contain uDOS.py marker. "
            "Invalid container configuration or .env corruption."
        )

    try:
        current = Path(__file__).resolve()
        candidate = current.parent.parent.parent
        marker = candidate / "uDOS.py"

        if marker.exists():
            return _enforce_home_root(candidate)
        raise RuntimeError(
            f"Cannot find uDOS.py at expected location: {candidate / 'uDOS.py'}. "
            "Set UDOS_ROOT environment variable or move repo to ~/uDOS."
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to detect repository root: {exc}\n"
            "Set UDOS_ROOT environment variable or check repo structure."
        )


def get_subprocess_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return env for subprocesses, ensuring UDOS_ROOT is set."""
    env = dict(base_env or os.environ)
    if "UDOS_ROOT" not in env:
        try:
            env["UDOS_ROOT"] = str(get_repo_root())
        except Exception:
            # Leave unset if root resolution fails.
            pass
    return env


def _redact_value(key: str, value: Any) -> Any:
    if key.lower() in _REDACT_KEYS:
        return "[REDACTED]"
    return value


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        redacted = {}
        for k, v in obj.items():
            redacted[k] = _redact_value(k, _redact(v))
        return redacted
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_redact(v) for v in obj)
    return obj


def _drop_payloads(ctx: Dict[str, Any]) -> Dict[str, Any]:
    if not ctx:
        return ctx
    scrubbed = {}
    for k, v in ctx.items():
        if k.lower() in _PAYLOAD_KEYS:
            continue
        scrubbed[k] = v
    return scrubbed


@dataclass
class LogConfig:
    level: str = "info"
    format: str = "json"
    dest: str = "file"
    root: Path = None
    redact: bool = True
    categories: Optional[set[str]] = None
    sampling: float = 1.0
    payloads: str = "dev-only"
    ring_size: int = 1000

    @classmethod
    def from_env(cls) -> "LogConfig":
        return cls(
            level=os.getenv("UDOS_LOG_LEVEL", "info").lower(),
            format=os.getenv("UDOS_LOG_FORMAT", "json").lower(),
            dest=os.getenv("UDOS_LOG_DEST", "file").lower(),
            root=_default_log_root(),
            redact=_coerce_bool(os.getenv("UDOS_LOG_REDACT"), True),
            categories=_split_csv(os.getenv("UDOS_LOG_CATEGORIES")),
            sampling=_safe_float(os.getenv("UDOS_LOG_SAMPLING"), 1.0),
            payloads=os.getenv("UDOS_LOG_PAYLOADS", "dev-only").lower(),
            ring_size=int(os.getenv("UDOS_LOG_RING", "1000")),
        )


class FileSink:
    def __init__(self, root: Path, component: str, name: str) -> None:
        self.root = root
        self.component = component
        self.name = name
        self._date = datetime.now().date()
        self._path = self._build_path()
        self._file = None
        self._lock = threading.Lock()

    def _build_path(self) -> Path:
        date_str = self._date.strftime("%Y-%m-%d")
        directory = self.root / self.component
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{self.name}-{date_str}.jsonl"

    def _ensure_open(self) -> None:
        now = datetime.now().date()
        if self._file is None or now != self._date:
            if self._file:
                try:
                    self._file.close()
                except Exception:
                    pass
            self._date = now
            self._path = self._build_path()
            self._file = open(self._path, "a", encoding="utf-8")

    def write(self, line: str) -> None:
        with self._lock:
            self._ensure_open()
            self._file.write(line + "\n")
            self._file.flush()


class LogManager:
    def __init__(self, config: Optional[LogConfig] = None) -> None:
        self.config = config or LogConfig.from_env()
        self.session_id = os.getenv("UDOS_SESSION_ID") or _short_id("S")
        self._ring: list[dict[str, Any]] = []
        self._ring_size = max(1, self.config.ring_size)
        self._sinks: dict[tuple[str, str], FileSink] = {}
        self._lock = threading.Lock()

    def _should_log(self, level: str, category: str) -> bool:
        if level not in _LEVEL_ORDER:
            return False
        if _LEVEL_ORDER[level] < _LEVEL_ORDER.get(self.config.level, 20):
            return False
        if self.config.categories and category not in self.config.categories:
            return False
        if level in {"trace", "debug"} and self.config.sampling < 1.0:
            if random.random() > self.config.sampling:
                return False
        return True

    def _sink(self, component: str, name: str) -> FileSink:
        key = (component, name)
        with self._lock:
            if key not in self._sinks:
                self._sinks[key] = FileSink(self.config.root, component, name)
            return self._sinks[key]

    def _push_ring(self, event: dict[str, Any]) -> None:
        self._ring.append(event)
        if len(self._ring) > self._ring_size:
            self._ring = self._ring[-self._ring_size :]

    def dump_ring(self, path: Optional[Path] = None) -> Path:
        if path is None:
            crash_dir = self.config.root / "crash"
            crash_dir.mkdir(parents=True, exist_ok=True)
            filename = f"crash-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{self.session_id}.jsonl"
            path = crash_dir / filename
        with open(path, "w", encoding="utf-8") as handle:
            for entry in self._ring:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return path

    def emit(self, event: dict[str, Any], component: str, name: str) -> None:
        self._push_ring(event)
        payload = json.dumps(event, ensure_ascii=False)
        if self.config.dest in {"file", "both"}:
            self._sink(component, name).write(payload)
        if self.config.dest in {"stdout", "both"}:
            if self.config.format == "pretty":
                pretty = f"[{event['ts']}] [{event['level']}] [{event['component']}] {event['msg']}"
                print(pretty)
            else:
                print(payload)
        if event.get("level") == "fatal":
            try:
                crash_path = self.dump_ring()
                notice = {
                    "ts": _now_iso(),
                    "ts_mono_ms": _mono_ms(),
                    "schema": LOG_SCHEMA_ID,
                    "level": "fatal",
                    "msg": "Crash ring buffer dumped",
                    "component": component,
                    "category": "crash",
                    "event": "log.ring_dump",
                    "session_id": self.session_id,
                    "corr_id": event.get("corr_id") or "-",
                    "ctx": {"path": str(crash_path)},
                }
                notice_payload = json.dumps(notice, ensure_ascii=False)
                if self.config.dest in {"file", "both"}:
                    self._sink(component, name).write(notice_payload)
                if self.config.dest in {"stdout", "both"}:
                    if self.config.format == "pretty":
                        pretty = f"[{notice['ts']}] [fatal] [{component}] Crash ring buffer dumped"
                        print(pretty)
                    else:
                        print(notice_payload)
            except Exception:
                pass

    def ring(self) -> list[dict[str, Any]]:
        return list(self._ring)

    def clear_ring(self) -> int:
        count = len(self._ring)
        self._ring = []
        return count


class Logger:
    def __init__(
        self,
        manager: LogManager,
        component: str,
        category: str = "general",
        name: Optional[str] = None,
        base_ctx: Optional[Dict[str, Any]] = None,
        corr_id: Optional[str] = None,
    ) -> None:
        self._manager = manager
        self._component = component
        self._category = category
        self._name = name or component
        self._base_ctx = base_ctx or {}
        self._corr_id = corr_id

    def isTrace(self) -> bool:
        return self._manager._should_log("trace", self._category)

    def isDebug(self) -> bool:
        return self._manager._should_log("debug", self._category)

    def child(self, ctx: Dict[str, Any]) -> "Logger":
        merged = dict(self._base_ctx)
        merged.update(ctx or {})
        return Logger(
            self._manager,
            component=self._component,
            category=merged.get("category", self._category),
            name=self._name,
            base_ctx=merged,
            corr_id=merged.get("corr_id", self._corr_id),
        )

    def event(
        self,
        level: str,
        event: str,
        msg: str,
        *args: Any,
        ctx: Optional[Dict[str, Any]] = None,
        err: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self._emit(level, msg, args=args, ctx=ctx, err=err, **kwargs, event=event)

    def trace(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("trace", msg, args=args, ctx=ctx, err=err, **kwargs)

    def debug(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("debug", msg, args=args, ctx=ctx, err=err, **kwargs)

    def info(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("info", msg, args=args, ctx=ctx, err=err, **kwargs)

    def warn(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("warn", msg, args=args, ctx=ctx, err=err, **kwargs)

    def warning(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("warn", msg, args=args, ctx=ctx, err=err, **kwargs)

    def error(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("error", msg, args=args, ctx=ctx, err=err, **kwargs)

    def fatal(self, msg: str, *args: Any, ctx: Optional[Any] = None, err: Optional[Any] = None, **kwargs: Any) -> None:
        self._emit("fatal", msg, args=args, ctx=ctx, err=err, **kwargs)

    def _emit(
        self,
        level: str,
        msg: str,
        args: Optional[tuple[Any, ...]] = None,
        ctx: Optional[Any] = None,
        err: Optional[Any] = None,
        event: Optional[str] = None,
        exc_info: Optional[bool] = None,
    ) -> None:
        if not self._manager._should_log(level, self._category):
            return

        if args:
            try:
                msg = msg % args
            except Exception:
                msg = f"{msg} {' '.join(str(a) for a in args)}"

        resolved_ctx: Dict[str, Any] = {}
        if callable(ctx):
            resolved_ctx = ctx()
        elif isinstance(ctx, dict):
            resolved_ctx = ctx
        elif ctx is not None:
            resolved_ctx = {"value": ctx}

        merged_ctx = dict(self._base_ctx)
        merged_ctx.update(resolved_ctx)

        # Enforce payload policy before redaction.
        payloads_policy = self._manager.config.payloads
        dev_mode = os.getenv("UDOS_DEV_MODE", "").strip().lower() in {"1", "true", "yes"}

        allow_payloads = False
        if payloads_policy == "on":
            allow_payloads = True
        elif payloads_policy == "dev-only":
            allow_payloads = dev_mode and level in {"trace", "debug"}

        # Payloads are only allowed when redact is enabled.
        if not self._manager.config.redact:
            allow_payloads = False

        if not allow_payloads:
            merged_ctx = _drop_payloads(merged_ctx)

        if self._manager.config.redact:
            merged_ctx = _redact(merged_ctx)

        error_obj = None
        if err is not None:
            if isinstance(err, BaseException):
                error_obj = {
                    "name": err.__class__.__name__,
                    "message": str(err),
                    "code": getattr(err, "code", None),
                }
                if level in {"error", "fatal"} or exc_info:
                    error_obj["stack"] = "".join(
                        traceback.format_exception(err.__class__, err, err.__traceback__)
                    )
            elif isinstance(err, dict):
                error_obj = dict(err)
            else:
                error_obj = {"message": str(err)}
        elif exc_info:
            error_obj = {"stack": "".join(traceback.format_stack())}

            if self._manager.config.redact:
                error_obj = _redact(error_obj)

        record = {
            "ts": _now_iso(),
            "ts_mono_ms": _mono_ms(),
            "schema": LOG_SCHEMA_ID,
            "level": level,
            "msg": msg,
            "component": self._component,
            "category": self._category,
            "event": event or "log.message",
            "session_id": self._manager.session_id,
            "corr_id": self._corr_id or merged_ctx.get("corr_id") or get_corr_id() or "-",
            "ctx": merged_ctx,
        }

        if error_obj:
            record["err"] = error_obj

        self._manager.emit(record, component=self._component, name=self._name)


_LOG_MANAGER: Optional[LogManager] = None


def get_log_manager() -> LogManager:
    global _LOG_MANAGER
    if _LOG_MANAGER is None:
        _LOG_MANAGER = LogManager()
    return _LOG_MANAGER


def get_logger(
    component: str,
    category: str = "general",
    name: Optional[str] = None,
    ctx: Optional[Dict[str, Any]] = None,
    corr_id: Optional[str] = None,
) -> Logger:
    # Backward compatibility: allow get_logger("category") usage.
    known_components = {"core", "wizard", "script", "goblin", "extension"}
    if component not in known_components and category == "general" and name is None:
        category = component
        component = "core"

    manager = get_log_manager()
    if corr_id is None:
        corr_id = get_corr_id()
    return Logger(
        manager=manager,
        component=component,
        category=category,
        name=name,
        base_ctx=ctx,
        corr_id=corr_id,
    )


def new_corr_id(prefix: str = "C") -> str:
    return _short_id(prefix)


def set_corr_id(corr_id: Optional[str]) -> contextvars.Token:
    """Set corr_id in context for implicit logger usage."""
    return _CORR_ID.set(corr_id)


def reset_corr_id(token: contextvars.Token) -> None:
    """Reset corr_id context to previous value."""
    _CORR_ID.reset(token)


def get_corr_id() -> Optional[str]:
    """Get current corr_id from context."""
    return _CORR_ID.get()


class DevTrace:
    """Development trace logger for detailed command flow and timing."""

    def __init__(self, category: str, enabled: bool = True):
        self.category = category
        self.enabled = enabled
        self.spans: list = []
        self.decisions: list = []
        self.start_time = datetime.now()
        self.logger = get_logger("core", category=f"dev-trace-{category}", name="trace")

    def span(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        if not self.enabled:
            return self._NoOpContext()
        return self._SpanContext(self, name, metadata)

    def log(self, message: str, level: str = "INFO", metadata: Optional[Dict[str, Any]] = None):
        if not self.enabled:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {},
        }
        self.decisions.append(entry)

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[TRACE] {message} | {metadata or ''}")

    class _SpanContext:
        def __init__(self, trace: "DevTrace", name: str, metadata: Optional[Dict[str, Any]]):
            self.trace = trace
            self.name = name
            self.metadata = metadata or {}
            self.start = None
            self.duration = None

        def __enter__(self):
            self.start = datetime.now()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.duration = (datetime.now() - self.start).total_seconds()
            span_entry = {
                "name": self.name,
                "start": self.start.isoformat(),
                "duration_ms": self.duration * 1000,
                "metadata": self.metadata,
                "error": str(exc_val) if exc_type else None,
            }
            self.trace.spans.append(span_entry)

            status = "OK" if not exc_type else "ERROR"
            self.trace.logger.info(
                f"[SPAN] {self.name} {status} ({self.duration*1000:.2f}ms)",
                ctx={"metadata": self.metadata},
            )

    class _NoOpContext:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def summary(self) -> Dict[str, Any]:
        total_duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "category": self.category,
            "total_duration_ms": total_duration * 1000,
            "spans_count": len(self.spans),
            "decisions_count": len(self.decisions),
            "spans": self.spans,
            "decisions": self.decisions,
        }

    def save(self, filepath: Optional[Path] = None):
        if not self.enabled:
            return

        if filepath is None:
            log_dir = _default_log_root()
            log_dir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filepath = log_dir / f"dev-trace-{self.category}-{date_str}.jsonl"

        summary = self.summary()
        with open(filepath, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(summary) + "\n")

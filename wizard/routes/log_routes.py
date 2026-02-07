"""
Log Routes (Wizard)
===================

Record client-side notifications/errors for later review.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import asyncio
from typing import Any, Dict, Optional, Generator, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from wizard.services.logging_api import get_logger, get_logs_root


class ToastLogPayload(BaseModel):
    severity: str = Field(..., pattern="^(info|success|warning|error)$")
    title: str
    message: str
    meta: Optional[Dict[str, Any]] = None


def create_log_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/logs", tags=["logs"], dependencies=dependencies)
    logger = get_logger("wizard", category="toast", name="wizard-toast")

    def _logs_root() -> Path:
        return get_logs_root()

    def _find_latest_log(component: str, name: str) -> Optional[Path]:
        log_dir = _logs_root() / component
        if not log_dir.exists():
            return None
        candidates = sorted(
            log_dir.glob(f"{name}-*.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )
        return candidates[-1] if candidates else None

    def _read_tail(path: Path, limit: int) -> List[str]:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except FileNotFoundError:
            return []
        if limit <= 0:
            return []
        return lines[-limit:]

    async def _stream_file(path: Path, limit: int) -> Generator[bytes, None, None]:
        for line in _read_tail(path, limit):
            yield f"event: log\ndata: {line}\n\n".encode("utf-8")

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                handle.seek(0, 2)
                while True:
                    line = handle.readline()
                    if line:
                        yield f"event: log\ndata: {line.strip()}\n\n".encode("utf-8")
                    else:
                        yield b"event: ping\ndata: {}\n\n"
                        await asyncio.sleep(0.5)
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n".encode("utf-8")

    @router.post("/toast")
    async def log_toast(payload: ToastLogPayload):
        record = {
            "severity": payload.severity,
            "title": payload.title,
            "message": payload.message,
            "meta": payload.meta,
        }
        logger.info("Toast log", ctx=record)
        log_dir = get_logs_root() / "wizard"
        log_path = log_dir / f"wizard-toast-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
        return {"status": "ok", "path": str(log_path)}

    @router.get("/stream")
    async def stream_logs(
        component: str = Query("wizard", pattern="^(core|wizard|script|goblin|extension)$"),
        name: str = Query("wizard-server"),
        limit: int = Query(200, ge=0, le=2000),
    ):
        """SSE tail for v1.3 JSONL logs under memory/logs/udos/."""
        path = _find_latest_log(component, name)
        if not path:
            raise HTTPException(status_code=404, detail="Log file not found")
        return StreamingResponse(_stream_file(path, limit), media_type="text/event-stream")

    return router

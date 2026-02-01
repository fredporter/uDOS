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
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from wizard.services.path_utils import get_memory_dir


class ToastLogPayload(BaseModel):
    severity: str = Field(..., pattern="^(info|success|warning|error)$")
    title: str
    message: str
    meta: Optional[Dict[str, Any]] = None


def create_log_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/logs", tags=["logs"], dependencies=dependencies)

    @router.post("/toast")
    async def log_toast(payload: ToastLogPayload):
        log_dir = get_memory_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"wizard-toast-{datetime.utcnow().strftime('%Y-%m-%d')}.log"
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": payload.severity,
            "title": payload.title,
            "message": payload.message,
            "meta": payload.meta,
        }
        with open(log_path, "a") as stream:
            stream.write(json.dumps(record) + "\n")
        return {"status": "ok", "path": str(log_path)}

    return router

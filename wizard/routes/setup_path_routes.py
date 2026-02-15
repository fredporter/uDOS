"""Path-management setup subroutes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

from fastapi import APIRouter


def create_setup_path_routes(
    *,
    get_paths: Callable[[], Dict[str, Dict[str, Any]]],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.get("/paths")
    async def get_path_map():
        return get_paths()

    @router.post("/paths/initialize")
    async def initialize_paths():
        paths = get_paths()
        created = []
        errors = []
        for group in ("data", "installation"):
            for _name, path in paths.get(group, {}).items():
                try:
                    Path(path).mkdir(parents=True, exist_ok=True)
                    created.append(path)
                except Exception as exc:
                    errors.append({"path": path, "error": str(exc)})
        return {
            "status": "complete",
            "created_directories": created,
            "errors": errors or None,
        }

    return router

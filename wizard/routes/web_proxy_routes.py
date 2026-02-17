"""Authenticated reverse proxy routes for container-hosted services."""

from __future__ import annotations

from typing import Callable, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from wizard.services.container_reverse_proxy_service import get_container_reverse_proxy_service

AuthGuard = Optional[Callable]


def create_web_proxy_routes(auth_guard: AuthGuard = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/web/proxy", tags=["web-proxy"], dependencies=dependencies)
    proxy = get_container_reverse_proxy_service()

    @router.get("/targets")
    async def list_proxy_targets():
        return {"success": True, **proxy.list_targets()}

    @router.api_route(
        "/{target_id}/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    )
    async def proxy_target_path(target_id: str, path: str, request: Request):
        full_path = f"/{path}" if path else "/"
        body = await request.body() if request.method != "GET" else None
        try:
            result = await proxy.proxy_request(
                target_id=target_id,
                path=full_path,
                method=request.method,
                headers=dict(request.headers),
                body=body,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Target unavailable: {target_id}")
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Reverse proxy error: {exc}")

        return StreamingResponse(
            iter([result["content"]]),
            status_code=result["status_code"],
            headers=result["headers"],
            media_type=result["media_type"],
        )

    @router.api_route(
        "/{target_id}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    )
    async def proxy_target_root(target_id: str, request: Request):
        body = await request.body() if request.method != "GET" else None
        try:
            result = await proxy.proxy_request(
                target_id=target_id,
                path="/",
                method=request.method,
                headers=dict(request.headers),
                body=body,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Target unavailable: {target_id}")
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Reverse proxy error: {exc}")

        return StreamingResponse(
            iter([result["content"]]),
            status_code=result["status_code"],
            headers=result["headers"],
            media_type=result["media_type"],
        )

    return router

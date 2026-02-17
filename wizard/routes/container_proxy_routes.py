"""
Container Proxy Routes
======================

Proxies browser requests to containerized services (home-assistant, songscribe)
providing seamless iframe embedding in Wizard GUI.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from typing import Optional

from wizard.services.logging_api import get_logger
from wizard.routes.container_launcher_routes import get_launcher

logger = get_logger("container-proxy")

router = APIRouter(prefix="/ui", tags=["container-proxy"])


class ContainerProxy:
    """Proxies requests to containerized services."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    def _get_port(self, container_id: str) -> Optional[int]:
        """Look up port from library container.json via launcher discovery."""
        config = get_launcher().get_container_config(container_id)
        return config.get("port") if config else None

    async def proxy_request(
        self,
        container_id: str,
        path: str,
        request: Request
    ) -> StreamingResponse:
        """Proxy HTTP request to container service."""

        port = self._get_port(container_id)
        if not port:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")

        target_url = f"http://localhost:{port}{path}"

        try:
            # Forward headers (skip host and connection-related headers)
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("connection", None)

            # Read request body if present
            body = await request.body() if request.method != "GET" else None

            # Make request to target service
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=True,
            )

            logger.info(f"[PROXY] {request.method} {container_id}:{path} -> {response.status_code}")

            return StreamingResponse(
                iter([response.content]),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except httpx.ConnectError:
            logger.warn(f"[PROXY] Container {container_id} not available on port {port}")
            raise HTTPException(
                status_code=503,
                detail=f"Container {container_id} is not running. Use /api/containers/{container_id}/launch to start it."
            )
        except Exception as e:
            logger.error(f"[PROXY] Error proxying to {container_id}: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")


_proxy = ContainerProxy()


@router.api_route("/{container_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_container_request(container_id: str, path: str, request: Request):
    """Proxy request to containerized service."""
    full_path = f"/{path}" if path else "/"
    return await _proxy.proxy_request(container_id, full_path, request)


@router.api_route("/{container_id}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_container_root(container_id: str, request: Request):
    """Proxy request to container root."""
    return await _proxy.proxy_request(container_id, "/", request)

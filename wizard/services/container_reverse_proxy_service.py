"""Reverse proxy service for container-hosted local services."""

from __future__ import annotations

from typing import Dict, Any, Optional

import httpx


class ContainerReverseProxyService:
    """Proxies requests to allow-listed local container services."""

    TARGET_PORTS: Dict[str, int] = {
        "home-assistant": 8123,
        "songscribe": 3000,
        "hethack": 7421,
        "elite": 7422,
        "rpgbbs": 7423,
        "crawler3d": 7424,
    }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    def list_targets(self) -> Dict[str, Any]:
        return {
            "count": len(self.TARGET_PORTS),
            "targets": [
                {
                    "id": target,
                    "port": port,
                    "base_url": f"http://127.0.0.1:{port}",
                }
                for target, port in sorted(self.TARGET_PORTS.items())
            ],
        }

    async def proxy_request(
        self,
        *,
        target_id: str,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        port = self.TARGET_PORTS.get(target_id)
        if not port:
            raise KeyError(f"Unknown proxy target: {target_id}")

        target_url = f"http://127.0.0.1:{port}{path}"
        proxy_headers = dict(headers)
        proxy_headers.pop("host", None)
        proxy_headers.pop("connection", None)

        response = await self.client.request(
            method=method,
            url=target_url,
            headers=proxy_headers,
            content=body,
            follow_redirects=True,
        )
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.content,
            "media_type": response.headers.get("content-type"),
            "target_url": target_url,
        }


_container_reverse_proxy_service: Optional[ContainerReverseProxyService] = None


def get_container_reverse_proxy_service() -> ContainerReverseProxyService:
    global _container_reverse_proxy_service
    if _container_reverse_proxy_service is None:
        _container_reverse_proxy_service = ContainerReverseProxyService()
    return _container_reverse_proxy_service

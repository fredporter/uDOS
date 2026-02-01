"""
Webhook Routes
==============

Expose webhook endpoints and configuration status for Wizard.
"""

from typing import Callable, Optional

from fastapi import APIRouter, Depends


def create_webhook_routes(
    auth_guard=None,
    base_url_provider: Optional[Callable[[], str]] = None,
    github_secret_provider: Optional[Callable[[], Optional[str]]] = None,
    notion_secret_provider: Optional[Callable[[], Optional[str]]] = None,
):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/webhooks", tags=["webhooks"], dependencies=dependencies)

    def _base_url() -> str:
        return base_url_provider() if base_url_provider else ""

    @router.get("/status")
    async def status():
        base_url = _base_url()
        github_secret = github_secret_provider() if github_secret_provider else None
        notion_secret = notion_secret_provider() if notion_secret_provider else None
        return {
            "success": True,
            "base_url": base_url,
            "webhooks": {
                "github": {
                    "url": f"{base_url}/api/github/webhook" if base_url else "/api/github/webhook",
                    "secret_configured": bool(github_secret),
                    "secret_source": "secret_store" if github_secret else "unset",
                },
                "notion": {
                    "url": f"{base_url}/api/notion/webhook" if base_url else "/api/notion/webhook",
                    "secret_configured": bool(notion_secret),
                    "secret_source": "env" if notion_secret else "unset",
                },
            },
        }

    return router

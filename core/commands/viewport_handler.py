"""VIEWPORT command handler - measure and persist terminal viewport."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.viewport_service import ViewportService


class ViewportHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for VIEWPORT command."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        VIEWPORT
        VIEWPORT SHOW
        VIEWPORT REFRESH
        """
        action = params[0].lower() if params else "refresh"
        viewport = ViewportService()

        if action in ("show", "status"):
            cols, rows = viewport.get_size()
            return {
                "status": "success",
                "command": "VIEWPORT",
                "message": f"Viewport cached: {cols}x{rows}",
                "cols": cols,
                "rows": rows,
            }

        if action in ("refresh", "measure", "update", ""):
            result = viewport.refresh(source="command")
            cols = result.get("cols")
            rows = result.get("rows")
            return {
                "status": result.get("status", "success"),
                "command": "VIEWPORT",
                "message": f"Viewport measured: {cols}x{rows}",
                "cols": int(cols) if cols else None,
                "rows": int(rows) if rows else None,
                "updated_at": result.get("updated_at"),
                "source": result.get("source"),
            }

        return {
            "status": "error",
            "command": "VIEWPORT",
            "message": "Usage: VIEWPORT [SHOW|REFRESH]",
        }

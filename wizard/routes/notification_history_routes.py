"""
Notification History API Routes
=================================

FastAPI endpoints for notification history management.
Provides CRUD, search, export, and statistics endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from wizard.services.notification_history_service import (
    NotificationHistoryService,
    ExportRequest,
)


# ============================================================
# Models
# ============================================================


class SaveNotificationRequest(BaseModel):
    type: str
    title: Optional[str] = None
    message: str
    duration_ms: int = 5000
    sticky: bool = False


class SearchRequest(BaseModel):
    query: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 50


class ExportRequestModel(BaseModel):
    format: str  # json, csv, markdown
    query: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 500


class ListRequest(BaseModel):
    limit: int = 20
    offset: int = 0


class ClearRequest(BaseModel):
    days: int = 30


class NotificationResponse(BaseModel):
    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================
# Route Factory
# ============================================================


def create_notification_history_routes(service: NotificationHistoryService) -> APIRouter:
    """Create notification history routes."""
    router = APIRouter(prefix="/api/v1/notification-history", tags=["history"])

    # ============================================================
    # Save Notification
    # ============================================================

    @router.post("/save")
    async def save_notification(req: SaveNotificationRequest) -> NotificationResponse:
        """
        Save a notification to history.

        **curl example:**
        ```bash
        curl -X POST http://localhost:8765/api/v1/notification-history/save \\
          -H "Content-Type: application/json" \\
          -d '{
            "type": "success",
            "title": "Saved",
            "message": "/Users/fred/file.txt",
            "duration_ms": 5000,
            "sticky": false
          }'
        ```
        """
        try:
            notification_id = await service.save_notification(
                type_=req.type,
                title=req.title,
                message=req.message,
                duration_ms=req.duration_ms,
                sticky=req.sticky,
            )
            return NotificationResponse(
                ok=True,
                data={"id": notification_id},
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # List Notifications (Paginated)
    # ============================================================

    @router.post("/list")
    async def list_notifications(req: ListRequest) -> NotificationResponse:
        """
        Get paginated notification history.

        **curl example:**
        ```bash
        curl -X POST http://localhost:8765/api/v1/notification-history/list \\
          -H "Content-Type: application/json" \\
          -d '{"limit": 20, "offset": 0}'
        ```
        """
        try:
            notifications, total = await service.get_notifications(
                limit=req.limit, offset=req.offset
            )
            return NotificationResponse(
                ok=True,
                data={
                    "notifications": notifications,
                    "total": total,
                    "limit": req.limit,
                    "offset": req.offset,
                },
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # Search Notifications
    # ============================================================

    @router.post("/search")
    async def search_notifications(req: SearchRequest) -> NotificationResponse:
        """
        Search notifications with optional filters.

        **curl example:**
        ```bash
        curl -X POST http://localhost:8765/api/v1/notification-history/search \\
          -H "Content-Type: application/json" \\
          -d '{
            "query": "saved",
            "type": "success",
            "limit": 50
          }'
        ```
        """
        try:
            results = await service.search_notifications(
                query=req.query,
                type_filter=req.type,
                start_date=req.start_date,
                end_date=req.end_date,
                limit=req.limit,
            )
            return NotificationResponse(
                ok=True,
                data=results,
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # Delete Notification
    # ============================================================

    @router.delete("/{notification_id}")
    async def delete_notification(notification_id: str) -> NotificationResponse:
        """
        Delete a single notification by ID.

        **curl example:**
        ```bash
        curl -X DELETE http://localhost:8765/api/v1/notification-history/toast-abc123
        ```
        """
        try:
            success = await service.delete_notification(notification_id)
            return NotificationResponse(
                ok=success,
                data={"deleted": notification_id} if success else None,
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # Clear Old Notifications
    # ============================================================

    @router.post("/clear")
    async def clear_old_notifications(req: ClearRequest) -> NotificationResponse:
        """
        Remove notifications older than N days (default: 30).

        **curl example:**
        ```bash
        curl -X POST http://localhost:8765/api/v1/notification-history/clear \\
          -H "Content-Type: application/json" \\
          -d '{"days": 30}'
        ```
        """
        try:
            count = await service.clear_old_notifications(days=req.days)
            return NotificationResponse(
                ok=True,
                data={"deleted_count": count},
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # Export Notifications
    # ============================================================

    @router.post("/export")
    async def export_notifications(req: ExportRequestModel) -> NotificationResponse:
        """
        Export notifications to JSON, CSV, or Markdown.

        **curl example:**
        ```bash
        curl -X POST http://localhost:8765/api/v1/notification-history/export \\
          -H "Content-Type: application/json" \\
          -d '{
            "format": "json",
            "type": "success",
            "limit": 500
          }'
        ```
        """
        try:
            export_req = ExportRequest(
                format=req.format,
                start_date=req.start_date,
                end_date=req.end_date,
                type_filter=req.type,
                limit=req.limit,
            )
            result = await service.export_notifications(req.format, export_req)
            return NotificationResponse(
                ok=True,
                data=result,
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    # ============================================================
    # Statistics
    # ============================================================

    @router.get("/stats")
    async def get_statistics() -> NotificationResponse:
        """
        Get notification statistics (count by type, total, etc).

        **curl example:**
        ```bash
        curl http://localhost:8765/api/v1/notification-history/stats
        ```
        """
        try:
            stats = await service.get_stats()
            return NotificationResponse(
                ok=True,
                data=stats,
            )
        except Exception as e:
            return NotificationResponse(ok=False, error=str(e))

    return router

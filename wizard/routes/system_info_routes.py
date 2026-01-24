"""
System Info Routes - OS Detection and System Monitoring

Provides API endpoints for:
- OS detection and platform information
- System resource statistics
- Library integration status
- System health monitoring
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Callable, Optional

from wizard.services.system_info_service import get_system_info_service
from wizard.services.path_utils import get_repo_root


def create_system_info_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create system info routes."""
    router = APIRouter(prefix="/api/v1/system", tags=["system"])

    system_service = get_system_info_service(get_repo_root())

    @router.get("/os")
    async def get_os_info(request: Request):
        """Get OS detection and platform information."""
        if auth_guard:
            await auth_guard(request)

        os_info = system_service.get_os_info()
        return os_info.to_dict()

    @router.get("/stats")
    async def get_system_stats(request: Request):
        """Get current system resource statistics."""
        if auth_guard:
            await auth_guard(request)

        return system_service.get_system_stats()

    @router.get("/info")
    async def get_full_system_info(request: Request):
        """Get comprehensive system information."""
        if auth_guard:
            await auth_guard(request)

        return {
            "os": system_service.get_os_info().to_dict(),
            "stats": system_service.get_system_stats(),
            "library": system_service.get_library_status().to_dict(),
        }

    @router.get("/library")
    async def get_library_status(request: Request):
        """Get library integration status."""
        if auth_guard:
            await auth_guard(request)

        library_status = system_service.get_library_status()
        return library_status.to_dict()

    @router.get("/library/{integration_name}")
    async def get_library_integration(integration_name: str, request: Request):
        """Get specific library integration details."""
        if auth_guard:
            await auth_guard(request)

        library_status = system_service.get_library_status()
        integration = next(
            (i for i in library_status.integrations if i.name == integration_name), None
        )

        if not integration:
            raise HTTPException(
                status_code=404, detail=f"Integration not found: {integration_name}"
            )

        return integration.to_dict()

    return router

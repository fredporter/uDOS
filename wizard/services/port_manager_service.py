"""
Port Management Service - Wizard Server Integration
====================================================

Provides API endpoints and health monitoring for port management.
Integrated into Wizard Server for real-time visibility.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Awaitable
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.port_manager import (
    get_port_manager,
    ServiceStatus,
    ServiceEnvironment,
    PortManager,
)


# Pydantic models for API responses
class ServiceInfo(BaseModel):
    """Service information response."""
    name: str
    port: Optional[int]
    environment: str
    description: str
    status: str
    enabled: bool
    pid: Optional[int] = None
    health_endpoint: Optional[str] = None


class PortConflict(BaseModel):
    """Port conflict information."""
    service_name: str
    service_port: int
    occupying_process: str
    occupying_pid: int
    suggested_action: str


class PortDashboard(BaseModel):
    """Complete port status dashboard."""
    timestamp: str
    services: Dict[str, ServiceInfo]
    conflicts: List[PortConflict]
    startup_order: List[str]
    shutdown_order: List[str]


class PortManagerService:
    """Service wrapper for port management."""
    
    def __init__(self):
        self.pm = get_port_manager()
        self._last_check = None
    
    def get_service_info(self, service_name: str) -> ServiceInfo:
        """Get information about a service."""
        if service_name not in self.pm.services:
            raise ValueError(f"Unknown service: {service_name}")
        
        svc = self.pm.services[service_name]
        self.pm.check_service_port(service_name)
        
        return ServiceInfo(
            name=svc.name,
            port=svc.port,
            environment=svc.environment.value,
            description=svc.description,
            status=svc.status.value,
            enabled=svc.enabled,
            pid=svc.pid,
            health_endpoint=svc.health_endpoint,
        )
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get information about all services."""
        self.pm.check_all_services()
        result = {}
        for name in self.pm.services.keys():
            result[name] = self.get_service_info(name)
        return result
    
    def get_conflicts(self) -> List[PortConflict]:
        """Get list of current port conflicts."""
        conflicts = []
        for svc_name, occupant in self.pm.get_conflicts():
            svc = self.pm.services[svc_name]
            conflicts.append(PortConflict(
                service_name=svc_name,
                service_port=svc.port,
                occupying_process=occupant['process'],
                occupying_pid=occupant['pid'],
                suggested_action=f"lsof -i :{svc.port} | grep -v COMMAND | awk '{{print $2}}' | xargs kill -9"
            ))
        return conflicts
    
    def get_dashboard(self) -> PortDashboard:
        """Get complete port status dashboard."""
        services = self.get_all_services()
        conflicts = self.get_conflicts()
        
        return PortDashboard(
            timestamp=datetime.now().isoformat(),
            services=services,
            conflicts=conflicts,
            startup_order=self.pm.get_startup_order(),
            shutdown_order=self.pm.get_shutdown_order(),
        )
    
    def check_service(self, service_name: str) -> ServiceInfo:
        """Check a specific service."""
        self.pm.check_service_port(service_name)
        return self.get_service_info(service_name)
    
    def kill_service(self, service_name: str) -> bool:
        """Kill a running service."""
        return self.pm.kill_service(service_name)
    
    def kill_port(self, port: int) -> bool:
        """Kill process on a specific port."""
        import subprocess
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            pids = [p for p in result.stdout.strip().splitlines() if p.strip()]
            if not pids:
                return True
            for pid in pids:
                subprocess.run(["kill", "-9", pid], timeout=2, check=False)
            return True
        except Exception:
            return False


# Global service instance
_port_service: Optional[PortManagerService] = None


def get_port_service() -> PortManagerService:
    """Get or create port manager service."""
    global _port_service
    if _port_service is None:
        _port_service = PortManagerService()
    return _port_service


def create_port_manager_router(
    auth_guard: Optional[Callable[[Request], Awaitable[None]]] = None,
) -> APIRouter:
    """Create FastAPI router for port management endpoints."""
    router = APIRouter(prefix="/api/v1/ports", tags=["port-management"])

    async def _run_guard(request: Request) -> None:
        if not auth_guard:
            return
        result = auth_guard(request)
        if asyncio.iscoroutine(result):
            await result
    
    @router.get("/status", response_model=PortDashboard)
    async def get_port_status(request: Request):
        """Get complete port management status."""
        await _run_guard(request)
        service = get_port_service()
        return service.get_dashboard()
    
    @router.get("/services", response_model=Dict[str, ServiceInfo])
    async def list_services(request: Request):
        """List all services and their status."""
        await _run_guard(request)
        service = get_port_service()
        return service.get_all_services()
    
    @router.get("/services/{service_name}", response_model=ServiceInfo)
    async def get_service_status(service_name: str, request: Request):
        """Get status of a specific service."""
        await _run_guard(request)
        service = get_port_service()
        try:
            return service.check_service(service_name)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.get("/conflicts", response_model=List[PortConflict])
    async def get_port_conflicts(request: Request):
        """Get list of port conflicts."""
        await _run_guard(request)
        service = get_port_service()
        return service.get_conflicts()
    
    @router.post("/services/{service_name}/kill")
    async def kill_service(service_name: str, request: Request):
        """Kill a running service."""
        await _run_guard(request)
        service = get_port_service()
        if not service.pm.services.get(service_name):
            raise HTTPException(status_code=404, detail=f"Unknown service: {service_name}")
        
        if service.kill_service(service_name):
            return {"status": "success", "message": f"Killed service: {service_name}"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to kill service: {service_name}")
    
    @router.post("/ports/{port}/kill")
    async def kill_port(port: int, request: Request):
        """Kill process on a specific port."""
        await _run_guard(request)
        service = get_port_service()
        if service.kill_port(port):
            return {"status": "success", "message": f"Killed process on port {port}"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to kill port {port}")
    
    @router.get("/report")
    async def get_port_report(request: Request):
        """Get formatted port status report."""
        await _run_guard(request)
        service = get_port_service()
        report = service.pm.generate_report()
        return {"report": report}
    
    @router.get("/env")
    async def get_env_script(request: Request):
        """Get environment variable setup script."""
        await _run_guard(request)
        service = get_port_service()
        script = service.pm.generate_env_script()
        return {"script": script}
    
    return router

"""
Port Manager - Server and Port Awareness & Management Utility
==============================================================

Provides complete visibility and management of all services and their ports
in the uDOS development and production environment.

Features:
  - Registry of all known services and ports
  - System-level port occupation detection
  - Port conflict resolution
  - Service health monitoring
  - Graceful startup/shutdown coordination
  - Port availability prediction
"""

import os
import json
import socket
import subprocess
import time
import asyncio
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Callable, Awaitable, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from fastapi import Request as FastAPIRequest


class ServiceEnvironment(Enum):
    """Service environment classification."""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    EXPERIMENTAL = "experimental"


class ServiceStatus(Enum):
    """Service status states."""

    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"
    PORT_CONFLICT = "port_conflict"


@dataclass
class Service:
    """Service definition with port information."""

    name: str
    port: int
    environment: ServiceEnvironment
    process_name: str  # e.g., "python", "npm", "tauri"
    description: str = ""
    startup_cmd: Optional[str] = None
    shutdown_cmd: Optional[str] = None
    health_endpoint: Optional[str] = None
    enabled: bool = True
    status: ServiceStatus = ServiceStatus.UNKNOWN
    pid: Optional[int] = None
    last_check: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary, handling enums and datetime."""
        d = asdict(self)
        d["environment"] = self.environment.value
        d["status"] = self.status.value
        if self.last_check:
            d["last_check"] = self.last_check.isoformat()
        return d


class PortManager:
    """
    Comprehensive port and service management utility.

    Maintains awareness of all services and their ports, detects conflicts,
    and provides coordination for startup/shutdown sequences.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize port manager with optional config file."""
        self.config_path = config_path or (
            Path(__file__).parent.parent / "config" / "port_registry.json"
        )
        self.services: Dict[str, Service] = {}
        self._load_registry()

    def _load_registry(self):
        """Load service registry from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    for svc in data.get("services", []):
                        env = ServiceEnvironment(svc["environment"])
                        status = ServiceStatus(svc.get("status", "unknown"))
                        service = Service(
                            name=svc["name"],
                            port=svc["port"],
                            environment=env,
                            process_name=svc["process_name"],
                            description=svc.get("description", ""),
                            startup_cmd=svc.get("startup_cmd"),
                            shutdown_cmd=svc.get("shutdown_cmd"),
                            health_endpoint=svc.get("health_endpoint"),
                            enabled=svc.get("enabled", True),
                            status=status,
                        )
                        self.services[service.name] = service
            except Exception as e:
                print(f"⚠️  Failed to load port registry: {e}")
                self._create_default_registry()
        else:
            self._create_default_registry()

    def _create_default_registry(self):
        """Create default service registry."""
        self.services = {
            "wizard": Service(
                name="wizard",
                port=8765,
                environment=ServiceEnvironment.PRODUCTION,
                process_name="python",
                description="Wizard Server - Production always-on service",
                health_endpoint="http://localhost:8765/health",
                startup_cmd="python -m wizard.server",
                shutdown_cmd=None,
            ),
            "goblin": Service(
                name="goblin",
                port=8767,
                environment=ServiceEnvironment.EXPERIMENTAL,
                process_name="python",
                description="Goblin Dev Server - Experimental features",
                health_endpoint="http://localhost:8767/health",
                startup_cmd="python dev/goblin/server.py",
                shutdown_cmd=None,
            ),
            "api": Service(
                name="api",
                port=5001,
                environment=ServiceEnvironment.DEVELOPMENT,
                process_name="python",
                description="API Server - REST/WebSocket API",
                health_endpoint="http://localhost:5001/health",
                startup_cmd="python -m extensions.api.server",
                shutdown_cmd=None,
            ),
            "vite": Service(
                name="vite",
                port=5173,
                environment=ServiceEnvironment.DEVELOPMENT,
                process_name="npm",
                description="Vite Dev Server - Frontend development",
                health_endpoint="http://localhost:5173/",
                startup_cmd="npm run dev",
                shutdown_cmd=None,
            ),
            "tauri": Service(
                name="tauri",
                port=None,  # Tauri doesn't use a fixed port
                environment=ServiceEnvironment.DEVELOPMENT,
                process_name="tauri",
                description="Tauri App - Desktop application",
                startup_cmd="npm run tauri dev",
                shutdown_cmd=None,
            ),
        }

    def save_registry(self) -> bool:
        """Save current service registry to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "timestamp": datetime.now().isoformat(),
                "services": [s.to_dict() for s in self.services.values()],
            }
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save port registry: {e}")
            return False

    def is_port_open(self, port: int) -> bool:
        """Check if a port is available (not in use)."""
        if port is None:
            return True  # No fixed port requirement

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(("127.0.0.1", port))
            return result != 0
        except Exception:
            return True
        finally:
            sock.close()

    def get_port_occupant(self, port: int) -> Optional[Dict[str, any]]:
        """Get process occupying a port (macOS/Linux)."""
        if port is None:
            return None

        try:
            # Use lsof to find process using the port
            output = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True, timeout=5
            )

            lines = output.stdout.strip().split("\n")[1:]  # Skip header
            if lines:
                parts = lines[0].split()
                if len(parts) >= 2:
                    return {"pid": int(parts[1]), "process": parts[0], "port": port}
        except Exception:
            pass

        return None

    def check_service_port(self, service_name: str) -> ServiceStatus:
        """Check if a service's port is available or occupied."""
        service = self.services.get(service_name)
        if not service or not service.port:
            return ServiceStatus.UNKNOWN

        if self.is_port_open(service.port):
            service.status = ServiceStatus.STOPPED
        else:
            occupant = self.get_port_occupant(service.port)
            if occupant:
                service.status = (
                    ServiceStatus.RUNNING
                    if occupant["process"] == service.process_name
                    else ServiceStatus.PORT_CONFLICT
                )
                service.pid = occupant["pid"]
            else:
                service.status = ServiceStatus.PORT_CONFLICT

        service.last_check = datetime.now()
        return service.status

    def check_all_services(self) -> Dict[str, ServiceStatus]:
        """Check status of all registered services."""
        results = {}
        for name in self.services.keys():
            results[name] = self.check_service_port(name)
        return results

    def get_conflicts(self) -> List[Tuple[str, Dict]]:
        """Get list of port conflicts."""
        conflicts = []
        for name, service in self.services.items():
            if service.port:
                occupant = self.get_port_occupant(service.port)
                if occupant and occupant["process"] != service.process_name:
                    conflicts.append((name, occupant))
        return conflicts

    def get_available_port(self, start_port: int = 9000) -> int:
        """Find an available port starting from start_port."""
        port = start_port
        while port < 65535:
            if self.is_port_open(port):
                return port
            port += 1
        raise RuntimeError("No available ports found")

    def reassign_port(self, service_name: str, new_port: int) -> bool:
        """Reassign a service to a new port."""
        if service_name not in self.services:
            return False

        if not self.is_port_open(new_port):
            return False

        self.services[service_name].port = new_port
        return self.save_registry()

    def kill_service(self, service_name: str, retries: int = 3) -> bool:
        """Kill a service by name with retry logic."""
        service = self.services.get(service_name)
        if not service or not service.port:
            return False

        port = service.port

        for attempt in range(retries):
            try:
                # Get PIDs using lsof
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                pids = result.stdout.strip().split("\n")
                if not pids or not pids[0]:
                    # Port is free
                    service.status = ServiceStatus.STOPPED
                    service.pid = None
                    return True

                # Kill all PIDs
                for pid in pids:
                    if pid:
                        try:
                            subprocess.run(["kill", "-9", pid], timeout=2, check=False)
                        except Exception:
                            pass

                # Wait and verify
                time.sleep(0.5)

                # Check if port is now free
                if self.is_port_open(port):
                    service.status = ServiceStatus.STOPPED
                    service.pid = None
                    return True

            except Exception as e:
                if attempt == retries - 1:
                    return False
                time.sleep(0.5)

        return False

    def get_startup_order(self) -> List[str]:
        """Get recommended startup order for services."""
        # Production first, then development, then experimental
        order = []
        for env in [
            ServiceEnvironment.PRODUCTION,
            ServiceEnvironment.DEVELOPMENT,
            ServiceEnvironment.EXPERIMENTAL,
        ]:
            for name, svc in self.services.items():
                if svc.environment == env and svc.enabled and svc.startup_cmd:
                    order.append(name)
        return order

    def get_shutdown_order(self) -> List[str]:
        """Get recommended shutdown order (reverse of startup)."""
        return list(reversed(self.get_startup_order()))

    def generate_report(self) -> str:
        """Generate a formatted status report."""
        self.check_all_services()

        report = []
        report.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        report.append("┃  🔌 Port Management Report                ┃")
        report.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        report.append("")

        # Group by environment
        for env in [
            ServiceEnvironment.PRODUCTION,
            ServiceEnvironment.DEVELOPMENT,
            ServiceEnvironment.EXPERIMENTAL,
        ]:
            services = [s for s in self.services.values() if s.environment == env]
            if services:
                report.append(f"  {env.value.upper()}")
                report.append("  " + "─" * 50)

                for svc in services:
                    status_icon = (
                        "✅"
                        if svc.status == ServiceStatus.RUNNING
                        else (
                            "⚠️ "
                            if svc.status == ServiceStatus.PORT_CONFLICT
                            else "❌" if svc.status == ServiceStatus.STOPPED else "❓"
                        )
                    )

                    port_str = f":{svc.port}" if svc.port else "dynamic"
                    enabled_str = "✓" if svc.enabled else "✗"

                    report.append(
                        f"  {status_icon} [{enabled_str}] {svc.name:12} {port_str:8} | {svc.description}"
                    )

                report.append("")

        # Conflicts section
        conflicts = self.get_conflicts()
        if conflicts:
            report.append("  ⚠️  PORT CONFLICTS")
            report.append("  " + "─" * 50)
            for svc_name, occupant in conflicts:
                svc = self.services[svc_name]
                report.append(
                    f"  Port {svc.port}: Expected {svc.name} but found {occupant['process']} (PID {occupant['pid']})"
                )
            report.append("")

        # Quick fixes
        report.append("  QUICK FIXES")
        report.append("  " + "─" * 50)
        for svc_name, occupant in conflicts:
            report.append(
                f"  Kill conflicting process: python -m wizard.cli_port_manager kill {svc_name}"
            )

        return "\n".join(report)

    def heal_conflicts(self) -> Dict[str, bool]:
        """Automatically heal all port conflicts by killing conflicting processes."""
        conflicts = self.get_conflicts()
        results = {}

        for svc_name, occupant in conflicts:
            print(f"  Healing {svc_name} (port {self.services[svc_name].port})...")
            success = self.kill_service(svc_name)
            results[svc_name] = success
            if success:
                print(f"    ✅ Freed port {self.services[svc_name].port}")
            else:
                print(f"    ❌ Failed to free port {self.services[svc_name].port}")

        return results

    def generate_env_script(self) -> str:
        """Generate shell script environment variables for all services."""
        script = []
        script.append("#!/bin/bash")
        script.append("# uDOS Service Port Environment - Auto-generated")
        script.append("")

        for name, svc in self.services.items():
            env_var = f"UDOS_{name.upper()}_PORT"
            if svc.port:
                script.append(f"export {env_var}={svc.port}")

        script.append("")
        script.append("# Service URLs")
        for name, svc in self.services.items():
            if svc.port:
                env_var = f"UDOS_{name.upper()}_URL"
                script.append(f"export {env_var}=http://localhost:{svc.port}")

        return "\n".join(script)


# Singleton instance
_port_manager: Optional[PortManager] = None


def get_port_manager(config_path: Optional[Path] = None) -> PortManager:
    """Get or create singleton port manager instance."""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager(config_path)
    return _port_manager


def init_port_manager(config_path: Optional[Path] = None):
    """Initialize the port manager."""
    global _port_manager
    _port_manager = PortManager(config_path)


# ============================================================
# FastAPI Integration
# ============================================================

try:
    from fastapi import APIRouter, HTTPException, Request
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = None
    Request = None
    BaseModel = object


if FASTAPI_AVAILABLE:
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


    def _get_service_info(pm: PortManager, service_name: str) -> ServiceInfo:
        """Convert Service to ServiceInfo model."""
        if service_name not in pm.services:
            raise ValueError(f"Unknown service: {service_name}")
        
        svc = pm.services[service_name]
        pm.check_service_port(service_name)
        
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


    def _get_all_services(pm: PortManager) -> Dict[str, ServiceInfo]:
        """Get information about all services."""
        pm.check_all_services()
        result = {}
        for name in pm.services.keys():
            result[name] = _get_service_info(pm, name)
        return result


    def _get_conflicts(pm: PortManager) -> List[PortConflict]:
        """Get list of current port conflicts."""
        conflicts = []
        for svc_name, occupant in pm.get_conflicts():
            svc = pm.services[svc_name]
            conflicts.append(PortConflict(
                service_name=svc_name,
                service_port=svc.port,
                occupying_process=occupant['process'],
                occupying_pid=occupant['pid'],
                suggested_action=f"lsof -i :{svc.port} | grep -v COMMAND | awk '{{print $2}}' | xargs kill -9"
            ))
        return conflicts


    def _get_dashboard(pm: PortManager) -> PortDashboard:
        """Get complete port status dashboard."""
        services = _get_all_services(pm)
        conflicts = _get_conflicts(pm)
        
        return PortDashboard(
            timestamp=datetime.now().isoformat(),
            services=services,
            conflicts=conflicts,
            startup_order=pm.get_startup_order(),
            shutdown_order=pm.get_shutdown_order(),
        )


    def _kill_port(port: int) -> bool:
        """Kill process on a specific port."""
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


    def create_port_manager_router(
        auth_guard: Optional[Callable[["FastAPIRequest"], Awaitable[None]]] = None,
    ) -> APIRouter:
        """Create FastAPI router for port management endpoints."""
        router = APIRouter(prefix="/api/v1/ports", tags=["port-management"])

        async def _run_guard(request: "FastAPIRequest") -> None:
            if not auth_guard:
                return
            result = auth_guard(request)
            if asyncio.iscoroutine(result):
                await result
        
        @router.get("/status", response_model=PortDashboard)
        async def get_port_status(request: "FastAPIRequest"):
            """Get complete port management status."""
            await _run_guard(request)
            pm = get_port_manager()
            return _get_dashboard(pm)
        
        @router.get("/services", response_model=Dict[str, ServiceInfo])
        async def list_services(request: "FastAPIRequest"):
            """List all services and their status."""
            await _run_guard(request)
            pm = get_port_manager()
            return _get_all_services(pm)
        
        @router.get("/services/{service_name}", response_model=ServiceInfo)
        async def get_service_status(service_name: str, request: "FastAPIRequest"):
            """Get status of a specific service."""
            await _run_guard(request)
            pm = get_port_manager()
            try:
                pm.check_service_port(service_name)
                return _get_service_info(pm, service_name)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @router.get("/conflicts", response_model=List[PortConflict])
        async def get_port_conflicts(request: "FastAPIRequest"):
            """Get list of port conflicts."""
            await _run_guard(request)
            pm = get_port_manager()
            return _get_conflicts(pm)
        
        @router.post("/services/{service_name}/kill")
        async def kill_service(service_name: str, request: "FastAPIRequest"):
            """Kill a running service."""
            await _run_guard(request)
            pm = get_port_manager()
            if not pm.services.get(service_name):
                raise HTTPException(status_code=404, detail=f"Unknown service: {service_name}")
            
            if pm.kill_service(service_name):
                return {"status": "success", "message": f"Killed service: {service_name}"}
            else:
                raise HTTPException(status_code=500, detail=f"Failed to kill service: {service_name}")
        
        @router.post("/ports/{port}/kill")
        async def kill_port(port: int, request: "FastAPIRequest"):
            """Kill process on a specific port."""
            await _run_guard(request)
            if _kill_port(port):
                return {"status": "success", "message": f"Killed process on port {port}"}
            else:
                raise HTTPException(status_code=500, detail=f"Failed to kill port {port}")
        
        @router.get("/report")
        async def get_port_report(request: "FastAPIRequest"):
            """Get formatted port status report."""
            await _run_guard(request)
            pm = get_port_manager()
            report = pm.generate_report()
            return {"report": report}
        
        @router.get("/env")
        async def get_env_script(request: "FastAPIRequest"):
            """Get environment variable setup script."""
            await _run_guard(request)
            pm = get_port_manager()
            script = pm.generate_env_script()
            return {"script": script}
        
        return router

else:
    # Stub when FastAPI not available
    def create_port_manager_router(*args, **kwargs):
        """FastAPI not available - port manager routes disabled."""
        raise ImportError("FastAPI is required for port manager routes")


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
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


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


def create_port_manager_router(auth_guard=None):
    """Create FastAPI router for port manager API endpoints."""
    from fastapi import APIRouter, HTTPException
    from typing import Callable, Optional
    
    router = APIRouter(prefix="/api/v1/ports", tags=["Port Manager"])
    
    async def check_auth(request):
        """Verify authentication if guard is provided."""
        if auth_guard and callable(auth_guard):
            return await auth_guard(request)
        return True
    
    @router.get("/status")
    async def get_status(request = None):
        """Get status of all services and ports."""
        await check_auth(request)
        pm = get_port_manager()
        return {
            "services": {
                name: {
                    "port": svc.port,
                    "status": svc.status.value,
                    "environment": svc.environment.value,
                    "description": svc.description,
                    "pid": svc.pid,
                }
                for name, svc in pm.services.items()
            },
            "report": pm.generate_report(),
        }
    
    @router.get("/conflicts")
    async def get_conflicts(request = None):
        """Get port conflicts."""
        await check_auth(request)
        pm = get_port_manager()
        conflicts = pm.get_conflicts()
        return {
            "conflicts": [
                {
                    "service": name,
                    "port": pm.services[name].port,
                    "occupant": occupant,
                }
                for name, occupant in conflicts
            ],
            "has_conflicts": len(conflicts) > 0,
        }
    
    @router.post("/heal")
    async def heal_conflicts(request = None):
        """Automatically heal port conflicts."""
        await check_auth(request)
        pm = get_port_manager()
        results = pm.heal_conflicts()
        return {"healed": results}
    
    @router.get("/env-script")
    async def get_env_script(request = None):
        """Get shell script with port environment variables."""
        await check_auth(request)
        pm = get_port_manager()
        return {"script": pm.generate_env_script()}
    
    return router

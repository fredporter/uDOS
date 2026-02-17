"""
Port Manager - Central Task and Process Manager for uDOS
=========================================================

Version: 1.3.13

Provides complete visibility and management of all services, processes,
and system resources in the uDOS development and production environment.

Features:
  - Registry of all known services and ports
  - System-level port occupation detection
  - Port conflict resolution
  - Service health monitoring
  - Graceful startup/shutdown coordination
  - Port availability prediction
  - Process lifecycle management (start/stop/restart)
  - Resource monitoring (CPU, memory, disk)
  - Process log history and audit trail
  - Multi-instance management
  - Extension service discovery

This is the central task manager for uDOS core and all extensions.
"""

__version__ = "1.3.13"

import os
import json
import socket
import subprocess
import time
import psutil
import threading
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from datetime import datetime, timedelta


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


class OperationStatus(Enum):
    """Status of background operations (downloads, installs, etc)."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


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


@dataclass
class ProcessEvent:
    """Log entry for process lifecycle events."""

    timestamp: datetime
    service_name: str
    event_type: str  # started, stopped, failed, restarted, conflict_detected, healed
    details: str = ""
    pid: Optional[int] = None
    port: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "service_name": self.service_name,
            "event_type": self.event_type,
            "details": self.details,
            "pid": self.pid,
            "port": self.port,
        }


@dataclass
class ResourceSnapshot:
    """System resource snapshot for monitoring."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    active_processes: int = 0
    active_ports: int = 0

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": round(self.memory_used_mb, 1),
            "memory_available_mb": round(self.memory_available_mb, 1),
            "disk_percent": self.disk_percent,
            "disk_used_gb": round(self.disk_used_gb, 2),
            "disk_free_gb": round(self.disk_free_gb, 2),
            "active_processes": self.active_processes,
            "active_ports": self.active_ports,
        }


@dataclass
class ManagedProcess:
    """Active process being managed by port manager."""

    service_name: str
    pid: int
    port: Optional[int]
    started_at: datetime
    cmd: str
    working_dir: Optional[str] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "running"

    def to_dict(self) -> Dict:
        return {
            "service_name": self.service_name,
            "pid": self.pid,
            "port": self.port,
            "started_at": self.started_at.isoformat(),
            "cmd": self.cmd,
            "working_dir": self.working_dir,
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_mb": round(self.memory_mb, 1),
            "status": self.status,
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
        }


@dataclass
class BackgroundOperation:
    """Represents a long-running background operation (download, install, seed, etc)."""

    operation_id: str
    operation_type: str  # "download", "install", "seed", "pull_model", etc.
    description: str
    status: OperationStatus
    started_at: datetime
    updated_at: datetime
    progress: float = 0.0  # 0-100
    total_size_mb: Optional[float] = None
    downloaded_mb: Optional[float] = None
    pid: Optional[int] = None
    error: Optional[str] = None
    resource_impact: Optional[Dict[str, float]] = None  # {cpu_percent, memory_mb, network_mbps}

    def to_dict(self) -> Dict:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "description": self.description,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress": round(self.progress, 1),
            "total_size_mb": round(self.total_size_mb, 1) if self.total_size_mb else None,
            "downloaded_mb": round(self.downloaded_mb, 1) if self.downloaded_mb else None,
            "eta_seconds": self._estimate_eta(),
            "pid": self.pid,
            "error": self.error,
            "resource_impact": self.resource_impact,
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
        }

    def _estimate_eta(self) -> Optional[float]:
        """Estimate seconds remaining based on progress and download speed."""
        if not self.total_size_mb or self.progress >= 100 or self.progress <= 0:
            return None
        if not self.downloaded_mb:
            return None

        elapsed = (datetime.now() - self.started_at).total_seconds()
        if elapsed < 1:
            return None

        download_rate = self.downloaded_mb / elapsed
        if download_rate <= 0:
            return None

        remaining_mb = self.total_size_mb - self.downloaded_mb
        return remaining_mb / download_rate


class PortManager:
    """
    Central Task and Process Manager for uDOS.

    Provides complete lifecycle management for all uDOS services and extensions:
    - Service registry and port management
    - Process lifecycle (start/stop/restart)
    - Resource monitoring and health checks
    - Conflict detection and auto-healing
    - Event logging and audit trail
    - Multi-instance coordination

    Version: 1.3.13
    """

    VERSION = "1.3.13"
    MAX_EVENT_LOG = 500
    MAX_RESOURCE_HISTORY = 60  # 1 hour of minute-by-minute snapshots

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize port manager with optional config file."""
        self.config_path = config_path or (
            Path(__file__).parent.parent / "config" / "port_registry.json"
        )
        self.services: Dict[str, Service] = {}
        self.managed_processes: Dict[str, ManagedProcess] = {}
        self.background_operations: Dict[str, BackgroundOperation] = {}
        self.event_log: List[ProcessEvent] = []
        self.resource_history: List[ResourceSnapshot] = []
        self._lock = threading.RLock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()
        self._load_registry()
        self._load_event_log()

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

    def _load_event_log(self):
        """Load event log from file."""
        event_log_path = self.config_path.parent / "port_manager_events.json"
        if event_log_path.exists():
            try:
                with open(event_log_path, "r") as f:
                    data = json.load(f)
                for entry in data.get("events", [])[-self.MAX_EVENT_LOG:]:
                    self.event_log.append(ProcessEvent(
                        timestamp=datetime.fromisoformat(entry["timestamp"]),
                        service_name=entry["service_name"],
                        event_type=entry["event_type"],
                        details=entry.get("details", ""),
                        pid=entry.get("pid"),
                        port=entry.get("port"),
                    ))
            except Exception:
                pass

    def _save_event_log(self):
        """Save event log to file."""
        event_log_path = self.config_path.parent / "port_manager_events.json"
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "events": [e.to_dict() for e in self.event_log[-self.MAX_EVENT_LOG:]],
            }
            with open(event_log_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def log_event(self, service_name: str, event_type: str, details: str = "", pid: int = None, port: int = None):
        """Log a process event."""
        with self._lock:
            event = ProcessEvent(
                timestamp=datetime.now(),
                service_name=service_name,
                event_type=event_type,
                details=details,
                pid=pid,
                port=port,
            )
            self.event_log.append(event)
            if len(self.event_log) > self.MAX_EVENT_LOG:
                self.event_log = self.event_log[-self.MAX_EVENT_LOG:]
            self._save_event_log()

    def get_events(self, limit: int = 50, service_name: str = None) -> List[Dict]:
        """Get recent events, optionally filtered by service."""
        with self._lock:
            events = self.event_log[-limit:]
            if service_name:
                events = [e for e in events if e.service_name == service_name]
            return [e.to_dict() for e in reversed(events)]

    def get_resource_snapshot(self) -> ResourceSnapshot:
        """Get current system resource snapshot."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            active_procs = len(self.managed_processes)
            active_ports = sum(1 for s in self.services.values() if s.status == ServiceStatus.RUNNING)

            return ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu,
                memory_percent=mem.percent,
                memory_used_mb=mem.used / (1024 * 1024),
                memory_available_mb=mem.available / (1024 * 1024),
                disk_percent=disk.percent,
                disk_used_gb=disk.used / (1024 * 1024 * 1024),
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                active_processes=active_procs,
                active_ports=active_ports,
            )
        except Exception:
            return ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_free_gb=0.0,
            )

    def start_resource_monitor(self, interval_seconds: int = 60):
        """Start background resource monitoring."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        def monitor_loop():
            while not self._stop_monitor.is_set():
                snapshot = self.get_resource_snapshot()
                with self._lock:
                    self.resource_history.append(snapshot)
                    if len(self.resource_history) > self.MAX_RESOURCE_HISTORY:
                        self.resource_history = self.resource_history[-self.MAX_RESOURCE_HISTORY:]
                self._stop_monitor.wait(interval_seconds)

        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_resource_monitor(self):
        """Stop background resource monitoring."""
        self._stop_monitor.set()

    def get_resource_history(self, minutes: int = 30) -> List[Dict]:
        """Get resource history for the last N minutes."""
        with self._lock:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            return [r.to_dict() for r in self.resource_history if r.timestamp >= cutoff]

    def start_service(self, service_name: str, wait_for_ready: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Start a service and track it as a managed process."""
        service = self.services.get(service_name)
        if not service:
            return {"success": False, "error": f"Unknown service: {service_name}"}

        if not service.startup_cmd:
            return {"success": False, "error": f"No startup command for: {service_name}"}

        # Check if already running
        if service.port and not self.is_port_open(service.port):
            occupant = self.get_port_occupant(service.port)
            if occupant:
                return {"success": False, "error": f"Port {service.port} already in use by PID {occupant['pid']}"}

        # Start the process
        try:
            repo_root = Path(__file__).parent.parent.parent
            env = os.environ.copy()
            env["PYTHONPATH"] = str(repo_root)

            process = subprocess.Popen(
                service.startup_cmd,
                shell=True,
                cwd=str(repo_root),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            managed = ManagedProcess(
                service_name=service_name,
                pid=process.pid,
                port=service.port,
                started_at=datetime.now(),
                cmd=service.startup_cmd,
                working_dir=str(repo_root),
            )
            self.managed_processes[service_name] = managed
            self.log_event(service_name, "started", f"PID {process.pid}", pid=process.pid, port=service.port)

            # Wait for service to be ready
            if wait_for_ready and service.port:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not self.is_port_open(service.port):
                        service.status = ServiceStatus.RUNNING
                        service.pid = process.pid
                        self.save_registry()
                        return {"success": True, "pid": process.pid, "port": service.port}
                    time.sleep(0.5)
                return {"success": False, "error": f"Service did not become ready within {timeout}s", "pid": process.pid}

            return {"success": True, "pid": process.pid, "port": service.port}

        except Exception as e:
            self.log_event(service_name, "failed", str(e))
            return {"success": False, "error": str(e)}

    def stop_service(self, service_name: str, force: bool = False) -> Dict[str, Any]:
        """Stop a service gracefully or forcefully."""
        service = self.services.get(service_name)
        if not service:
            return {"success": False, "error": f"Unknown service: {service_name}"}

        if service.port:
            success = self.kill_service(service_name)
            if success:
                self.log_event(service_name, "stopped", "Service stopped", port=service.port)
                if service_name in self.managed_processes:
                    del self.managed_processes[service_name]
                return {"success": True}
            return {"success": False, "error": "Failed to stop service"}

        return {"success": False, "error": "Service has no port to stop"}

    def restart_service(self, service_name: str, timeout: int = 30) -> Dict[str, Any]:
        """Restart a service (stop then start)."""
        stop_result = self.stop_service(service_name)
        time.sleep(1)  # Brief pause between stop and start
        start_result = self.start_service(service_name, timeout=timeout)
        self.log_event(service_name, "restarted", f"Stop: {stop_result.get('success')}, Start: {start_result.get('success')}")
        return start_result

    def get_managed_processes(self) -> List[Dict]:
        """Get list of all managed processes with current stats."""
        result = []
        for name, proc in list(self.managed_processes.items()):
            try:
                ps = psutil.Process(proc.pid)
                proc.cpu_percent = ps.cpu_percent()
                proc.memory_mb = ps.memory_info().rss / (1024 * 1024)
                proc.status = "running" if ps.is_running() else "stopped"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc.status = "stopped"
            result.append(proc.to_dict())
        return result

    def register_extension(self, name: str, port: int, description: str = "",
                          startup_cmd: str = None, health_endpoint: str = None) -> bool:
        """Register an extension service (for dynamic discovery)."""
        with self._lock:
            if name in self.services:
                # Update existing
                self.services[name].port = port
                self.services[name].description = description
                if startup_cmd:
                    self.services[name].startup_cmd = startup_cmd
                if health_endpoint:
                    self.services[name].health_endpoint = health_endpoint
            else:
                # Create new
                self.services[name] = Service(
                    name=name,
                    port=port,
                    environment=ServiceEnvironment.DEVELOPMENT,
                    process_name="python",
                    description=description or f"Extension: {name}",
                    startup_cmd=startup_cmd,
                    health_endpoint=health_endpoint,
                    enabled=True,
                )
            self.log_event(name, "registered", f"Port {port}")
            return self.save_registry()

    def unregister_extension(self, name: str) -> bool:
        """Unregister an extension service."""
        with self._lock:
            if name in self.services:
                self.log_event(name, "unregistered", f"Port {self.services[name].port}")
                del self.services[name]
                return self.save_registry()
        return False

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for dashboard display."""
        self.check_all_services()
        snapshot = self.get_resource_snapshot()
        conflicts = self.get_conflicts()

        services_by_status = {
            "running": [],
            "stopped": [],
            "conflict": [],
            "unknown": [],
        }

        for name, svc in self.services.items():
            status_key = "conflict" if svc.status == ServiceStatus.PORT_CONFLICT else svc.status.value
            if status_key not in services_by_status:
                status_key = "unknown"
            services_by_status[status_key].append({
                "name": name,
                "port": svc.port,
                "description": svc.description,
                "environment": svc.environment.value,
                "pid": svc.pid,
            })

        return {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "resources": snapshot.to_dict(),
            "services": services_by_status,
            "conflicts": [{"service": name, "port": self.services[name].port, "occupant": occ}
                         for name, occ in conflicts],
            "events": self.get_events(limit=10),
            "managed_processes": self.get_managed_processes(),
            "totals": {
                "services": len(self.services),
                "running": len(services_by_status["running"]),
                "stopped": len(services_by_status["stopped"]),
                "conflicts": len(conflicts),
            },
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

    def kill_process_by_pid(self, pid: int, force: bool = True) -> bool:
        """Kill a process by PID.

        Args:
            pid: Process ID to kill
            force: Use SIGKILL (-9) if True, else SIGTERM (-15)

        Returns:
            True if process was killed successfully
        """
        try:
            ps_proc = psutil.Process(pid)
            if force:
                ps_proc.kill()  # SIGKILL
            else:
                ps_proc.terminate()  # SIGTERM

            # Wait briefly to confirm
            try:
                ps_proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                if not force:
                    # Retry with force
                    ps_proc.kill()
                    ps_proc.wait(timeout=1)

            self.log_event("system", "killed_process", f"Killed PID {pid}", pid=pid)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return False

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
                for pid_str in pids:
                    if pid_str:
                        try:
                            pid = int(pid_str)
                            self.kill_process_by_pid(pid, force=True)
                        except (ValueError, Exception):
                            pass

                # Wait and verify
                time.sleep(0.5)

                # Check if port is now free
                if self.is_port_open(port):
                    service.status = ServiceStatus.STOPPED
                    service.pid = None
                    self.log_event(service_name, "stopped", f"Killed service on port {port}", port=port)
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

    # Background Operation Management

    def start_operation(
        self,
        operation_id: str,
        operation_type: str,
        description: str,
        total_size_mb: Optional[float] = None,
        pid: Optional[int] = None,
    ) -> BackgroundOperation:
        """Register a new background operation."""
        operation = BackgroundOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            description=description,
            status=OperationStatus.IN_PROGRESS,
            started_at=datetime.now(),
            updated_at=datetime.now(),
            total_size_mb=total_size_mb,
            pid=pid,
        )
        with self._lock:
            self.background_operations[operation_id] = operation
            self.log_event(
                operation_type,
                "operation_started",
                f"{operation_type}: {description}",
                pid=pid,
            )
        return operation

    def update_operation(
        self,
        operation_id: str,
        progress: float = None,
        downloaded_mb: float = None,
        status: OperationStatus = None,
        error: str = None,
        resource_impact: Dict[str, float] = None,
    ) -> Optional[BackgroundOperation]:
        """Update operation progress."""
        with self._lock:
            op = self.background_operations.get(operation_id)
            if op:
                if progress is not None:
                    op.progress = min(100.0, max(0.0, progress))
                if downloaded_mb is not None:
                    op.downloaded_mb = downloaded_mb
                if status is not None:
                    op.status = status
                if error is not None:
                    op.error = error
                if resource_impact is not None:
                    op.resource_impact = resource_impact
                op.updated_at = datetime.now()
            return op

    def complete_operation(self, operation_id: str, error: str = None):
        """Mark operation as complete."""
        with self._lock:
            op = self.background_operations.get(operation_id)
            if op:
                op.status = OperationStatus.FAILED if error else OperationStatus.COMPLETED
                op.progress = 100.0 if not error else op.progress
                op.error = error
                op.updated_at = datetime.now()
                self.log_event(
                    op.operation_type,
                    "operation_completed",
                    f"{op.description} - {'ERROR' if error else 'OK'}",
                    pid=op.pid,
                )

    def get_active_operations(self) -> List[BackgroundOperation]:
        """Get list of currently active operations."""
        with self._lock:
            return [
                op
                for op in self.background_operations.values()
                if op.status == OperationStatus.IN_PROGRESS
            ]

    def get_operations_summary(self) -> Dict:
        """Get summary of all operations including resource impact."""
        with self._lock:
            active = [
                op
                for op in self.background_operations.values()
                if op.status == OperationStatus.IN_PROGRESS
            ]

            total_cpu = sum(op.resource_impact.get("cpu_percent", 0) for op in active if op.resource_impact)
            total_memory_mb = sum(op.resource_impact.get("memory_mb", 0) for op in active if op.resource_impact)

            return {
                "total_active": len(active),
                "operations": [op.to_dict() for op in active],
                "aggregate_cpu_percent": round(total_cpu, 1),
                "aggregate_memory_mb": round(total_memory_mb, 1),
                "system_overload_risk": total_cpu > 80 or total_memory_mb > 4000,
            }

    def should_warn_before_operation(self) -> Tuple[bool, str]:
        """Check if system is under load and operations should warn user."""
        summary = self.get_operations_summary()

        if summary["system_overload_risk"]:
            reason = []
            if summary["aggregate_cpu_percent"] > 80:
                reason.append(f"High CPU usage ({summary['aggregate_cpu_percent']}%)")
            if summary["aggregate_memory_mb"] > 4000:
                reason.append(f"High memory usage ({summary['aggregate_memory_mb']}MB)")
            return True, "; ".join(reason)

        return False, ""


# Singleton instance
    _port_manager = None


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
    from fastapi import APIRouter, HTTPException, Request
    from pydantic import BaseModel
    from typing import Optional

    router = APIRouter(prefix="/api/ports", tags=["Port Manager"])

    class ServiceAction(BaseModel):
        service_name: str
        timeout: Optional[int] = 30

    class RegisterExtension(BaseModel):
        name: str
        port: int
        description: Optional[str] = ""
        startup_cmd: Optional[str] = None
        health_endpoint: Optional[str] = None

    async def check_auth(request):
        """Verify authentication if guard is provided."""
        if auth_guard and callable(auth_guard):
            return await auth_guard(request)
        return True

    @router.get("/version")
    async def get_version():
        """Get port manager version."""
        return {"version": PortManager.VERSION}

    @router.get("/status")
    async def get_status(request: Request = None):
        """Get status of all services and ports."""
        await check_auth(request)
        pm = get_port_manager()
        pm.check_all_services()
        return {
            "version": pm.VERSION,
            "services": {
                name: {
                    "port": svc.port,
                    "status": svc.status.value,
                    "environment": svc.environment.value,
                    "description": svc.description,
                    "pid": svc.pid,
                    "enabled": svc.enabled,
                    "health_endpoint": svc.health_endpoint,
                    "startup_cmd": svc.startup_cmd,
                }
                for name, svc in pm.services.items()
            },
            "report": pm.generate_report(),
        }

    @router.get("/dashboard")
    async def get_dashboard(request: Request = None):
        """Get complete dashboard summary."""
        await check_auth(request)
        pm = get_port_manager()
        return pm.get_dashboard_summary()

    @router.get("/resources")
    async def get_resources(request: Request = None):
        """Get current system resources."""
        await check_auth(request)
        pm = get_port_manager()
        return pm.get_resource_snapshot().to_dict()

    @router.get("/resources/history")
    async def get_resource_history(minutes: int = 30, request: Request = None):
        """Get resource usage history."""
        await check_auth(request)
        pm = get_port_manager()
        return {"history": pm.get_resource_history(minutes)}

    @router.get("/events")
    async def get_events(limit: int = 50, service_name: str = None, request: Request = None):
        """Get process events log."""
        await check_auth(request)
        pm = get_port_manager()
        return {"events": pm.get_events(limit=limit, service_name=service_name)}

    @router.get("/processes")
    async def get_processes(request: Request = None):
        """Get managed processes list."""
        await check_auth(request)
        pm = get_port_manager()
        return {"processes": pm.get_managed_processes()}

    @router.get("/conflicts")
    async def get_conflicts(request: Request = None):
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
    async def heal_conflicts(request: Request = None):
        """Automatically heal port conflicts."""
        await check_auth(request)
        pm = get_port_manager()
        results = pm.heal_conflicts()
        return {"healed": results}

    @router.post("/start")
    async def start_service(payload: ServiceAction, request: Request = None):
        """Start a service."""
        await check_auth(request)
        pm = get_port_manager()
        result = pm.start_service(payload.service_name, timeout=payload.timeout)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

    @router.post("/stop")
    async def stop_service(payload: ServiceAction, request: Request = None):
        """Stop a service."""
        await check_auth(request)
        pm = get_port_manager()
        result = pm.stop_service(payload.service_name)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

    @router.post("/restart")
    async def restart_service(payload: ServiceAction, request: Request = None):
        """Restart a service."""
        await check_auth(request)
        pm = get_port_manager()
        result = pm.restart_service(payload.service_name, timeout=payload.timeout)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

    @router.post("/register")
    async def register_extension(payload: RegisterExtension, request: Request = None):
        """Register an extension service."""
        await check_auth(request)
        pm = get_port_manager()
        success = pm.register_extension(
            name=payload.name,
            port=payload.port,
            description=payload.description,
            startup_cmd=payload.startup_cmd,
            health_endpoint=payload.health_endpoint,
        )
        return {"success": success}

    @router.delete("/unregister/{name}")
    async def unregister_extension(name: str, request: Request = None):
        """Unregister an extension service."""
        await check_auth(request)
        pm = get_port_manager()
        success = pm.unregister_extension(name)
        return {"success": success}

    @router.get("/env-script")
    async def get_env_script(request: Request = None):
        """Get shell script with port environment variables."""
        await check_auth(request)
        pm = get_port_manager()
        return {"script": pm.generate_env_script()}

    @router.post("/monitor/start")
    async def start_monitor(interval: int = 60, request: Request = None):
        """Start resource monitoring."""
        await check_auth(request)
        pm = get_port_manager()
        pm.start_resource_monitor(interval)
        return {"started": True}

    @router.post("/monitor/stop")
    async def stop_monitor(request: Request = None):
        """Stop resource monitoring."""
        await check_auth(request)
        pm = get_port_manager()
        pm.stop_resource_monitor()
        return {"stopped": True}

    # ==================== Operations Endpoints ====================

    @router.get("/operations")
    async def get_operations(request: Request = None):
        """Get all background operations."""
        await check_auth(request)
        pm = get_port_manager()
        operations = pm.get_active_operations()
        return {
            "operations": [op.to_dict() for op in operations],
            "count": len(operations),
        }

    @router.get("/operations/summary")
    async def get_operations_summary(request: Request = None):
        """Get aggregate resource impact of all operations."""
        await check_auth(request)
        pm = get_port_manager()
        summary = pm.get_operations_summary()
        return summary

    @router.get("/operations/{operation_id}")
    async def get_operation(operation_id: str, request: Request = None):
        """Get details of a specific operation."""
        await check_auth(request)
        pm = get_port_manager()
        if operation_id not in pm.background_operations:
            raise HTTPException(status_code=404, detail="Operation not found")
        op = pm.background_operations[operation_id]
        return op.to_dict()

    @router.post("/operations/start")
    async def start_operation(
        operation_type: str,
        description: str = "",
        total_size_mb: float = None,
        request: Request = None,
    ):
        """Register start of a background operation."""
        await check_auth(request)
        pm = get_port_manager()
        operation_id = pm.start_operation(
            operation_type=operation_type,
            description=description,
            total_size_mb=total_size_mb,
        )
        return {"operation_id": operation_id}

    @router.post("/operations/{operation_id}/update")
    async def update_operation_progress(
        operation_id: str,
        progress: float = 0.0,
        downloaded_mb: float = None,
        status: str = "in_progress",
        request: Request = None,
    ):
        """Update progress of a background operation."""
        await check_auth(request)
        pm = get_port_manager()
        if operation_id not in pm.background_operations:
            raise HTTPException(status_code=404, detail="Operation not found")

        try:
            status_enum = OperationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        pm.update_operation(
            operation_id,
            progress=progress,
            downloaded_mb=downloaded_mb,
            status=status_enum,
        )
        return {"updated": True}

    @router.post("/operations/{operation_id}/complete")
    async def complete_operation(
        operation_id: str,
        error: str = None,
        request: Request = None,
    ):
        """Mark a background operation as completed."""
        await check_auth(request)
        pm = get_port_manager()
        if operation_id not in pm.background_operations:
            raise HTTPException(status_code=404, detail="Operation not found")

        pm.complete_operation(operation_id, error=error)
        return {"completed": True}

    @router.post("/operations/check-overload")
    async def check_system_overload(request: Request = None):
        """Check if system is overloaded based on resource usage."""
        await check_auth(request)
        pm = get_port_manager()
        should_warn = pm.should_warn_before_operation()
        summary = pm.get_operations_summary()

        return {
            "overloaded": should_warn,
            "message": "System resources heavily used. Consider waiting before starting new operations."
            if should_warn
            else "System resources available.",
            "resource_summary": summary,
        }

    return router

"""Dev Mode tool network service."""

from __future__ import annotations

from datetime import datetime
from ipaddress import ip_network
import socket
import time
from urllib.parse import urlparse

from core.services.logging_manager import get_logger
from core.services.network_gate_policy import allow_non_loopback_core_network

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


class DevModeToolNetworkService:
    """Manage network operations and diagnostics."""

    def __init__(self):
        """Initialize network service."""
        self.logger = get_logger("dev-mode-tool-network-service")
        self.default_timeout_sec = 3.0
        self.max_scan_hosts = 32

    def _allow_non_loopback(self) -> bool:
        return allow_non_loopback_core_network()

    def _is_loopback_host(self, host: str) -> bool:
        if not host:
            return False
        normalized = host.strip().lower()
        if normalized in _LOOPBACK_HOSTS:
            return True
        try:
            parsed = urlparse(normalized if "://" in normalized else f"tcp://{normalized}")
        except ValueError:
            return False
        hostname = (parsed.hostname or normalized).strip().lower()
        return hostname in _LOOPBACK_HOSTS

    def _is_loopback_subnet(self, subnet: str) -> bool:
        try:
            network = ip_network(subnet, strict=False)
        except ValueError:
            return False
        return network.is_loopback

    def _wizard_required(self, target: str, operation: str) -> dict[str, object]:
        return {
            "status": "warning",
            "code": "wizard_required",
            "operation": operation,
            "target": target,
            "message": "Core networking is restricted to loopback. Use Wizard networking routes for remote targets.",
            "recovery_hint": "Run through Wizard mode/services or target localhost/127.0.0.1 only",
        }

    def _probe_tcp(self, host: str, port: int, timeout_sec: float) -> tuple[bool, float]:
        """Attempt a TCP connection and return (connected, latency_ms)."""
        start = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                return True, latency_ms
        except OSError:
            return False, 0.0

    def _candidate_hosts(self, subnet: str) -> list[str]:
        """Build a bounded list of host IPs from subnet."""
        network = ip_network(subnet, strict=False)
        hosts = [str(ip) for ip in network.hosts()]
        return hosts[: self.max_scan_hosts]

    def scan_network(
        self,
        subnet: Optional[str] = None,
        timeout: int = 5,
    ) -> dict[str, object]:
        """
        Scan network for available hosts.

        Args:
            subnet: Subnet to scan (e.g., 192.168.1.0/24)
            timeout: Scan timeout in seconds

        Returns:
            Dict with scan results and discovered hosts
        """
        subnet_to_scan = subnet or "127.0.0.1/32"
        if not self._is_loopback_subnet(subnet_to_scan) and not self._allow_non_loopback():
            return self._wizard_required(subnet_to_scan, operation="scan")

        self.logger.info(f"Scanning network: {subnet_to_scan}")
        timeout_sec = max(0.1, float(timeout))

        try:
            hosts_to_scan = self._candidate_hosts(subnet_to_scan)
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid subnet: {subnet_to_scan}",
                "subnet": subnet_to_scan,
            }

        discovered: list[dict[str, Any]] = []
        probe_ports = (22, 80, 443)
        for host in hosts_to_scan:
            for port in probe_ports:
                connected, latency_ms = self._probe_tcp(host, port, timeout_sec)
                if not connected:
                    continue
                discovered.append(
                    {
                        "host": host,
                        "port": port,
                        "protocol": "tcp",
                        "latency_ms": latency_ms,
                    }
                )
                break

        return {
            "status": "success",
            "scan_time": datetime.now().isoformat(),
            "subnet": subnet_to_scan,
            "timeout": timeout,
            "hosts_found": len(discovered),
            "hosts": discovered,
        }

    def connect_host(
        self,
        host: str,
        port: int,
        protocol: str = "tcp",
    ) -> dict[str, object]:
        """
        Establish connection to a host.

        Args:
            host: Hostname or IP address
            port: Port number
            protocol: Protocol (tcp|udp|http|https)

        Returns:
            Dict with connection status
        """
        self.logger.info(f"Connecting to {host}:{port}/{protocol}")
        if not host:
            return {
                "status": "error",
                "message": "Host is required",
                "host": host,
                "port": port,
                "protocol": protocol,
            }
        if not self._is_loopback_host(host) and not self._allow_non_loopback():
            return self._wizard_required(str(host), operation="connect")
        if port <= 0 or port > 65535:
            return {
                "status": "error",
                "message": f"Invalid port: {port}",
                "host": host,
                "port": port,
                "protocol": protocol,
            }

        connected, latency_ms = self._probe_tcp(host, port, self.default_timeout_sec)
        if connected:
            return {
                "status": "success",
                "host": host,
                "port": port,
                "protocol": protocol,
                "connected": True,
                "latency_ms": latency_ms,
            }

        return {
            "status": "error",
            "message": f"Unable to connect to {host}:{port}",
            "host": host,
            "port": port,
            "protocol": protocol,
            "connected": False,
            "latency_ms": 0.0,
        }

    def check_connectivity(self, target: str = "127.0.0.1") -> dict[str, object]:
        """
        Check network connectivity (ping-like operation).

        Args:
            target: Target host to ping

        Returns:
            Dict with connectivity status and latency
        """
        self.logger.info(f"Checking connectivity to {target}")
        if not target:
            return {"status": "error", "message": "Connectivity target is required"}
        if not self._is_loopback_host(target) and not self._allow_non_loopback():
            return self._wizard_required(str(target), operation="check")

        connected, latency_ms = self._probe_tcp(target, 53, self.default_timeout_sec)
        if connected:
            return {
                "status": "success",
                "target": target,
                "reachable": True,
                "latency_ms": latency_ms,
                "packet_loss": 0,
            }

        return {
            "status": "error",
            "target": target,
            "reachable": False,
            "latency_ms": 0.0,
            "packet_loss": 100,
            "message": f"Target unreachable: {target}",
        }


# Global singleton
VibeNetworkService = DevModeToolNetworkService

_network_service: DevModeToolNetworkService | None = None


def get_network_service() -> DevModeToolNetworkService:
    """Get or create the global network service."""
    global _network_service
    if _network_service is None:
        _network_service = DevModeToolNetworkService()
    return _network_service

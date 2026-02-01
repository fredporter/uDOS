"""
Beacon Portal Service

Core business logic for beacon node management, VPN tunnel configuration,
and device quota tracking.

Provides interfaces for:
  - Beacon WiFi configuration
  - VPN tunnel lifecycle management
  - Device quota enforcement
  - Local plugin caching
  - Health monitoring
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import sqlite3
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# Paths
BEACON_DB_PATH = Path(__file__).parent.parent.parent / "memory" / "beacon" / "beacon.db"
BEACON_CONFIG_PATH = Path(__file__).parent / "config" / "beacon.json"


# ============================================================================
# DATA CLASSES & ENUMS
# ============================================================================


class BeaconMode(str, Enum):
    """Network mode for beacon deployment."""

    PRIVATE_HOME = "private-home"
    PUBLIC_SECURE = "public-secure"


class TunnelStatus(str, Enum):
    """VPN tunnel lifecycle states."""

    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class BeaconConfig:
    """Beacon WiFi and network configuration."""

    beacon_id: str
    mode: BeaconMode
    ssid: str
    band: str  # 2.4ghz, 5ghz, both
    security: str  # wpa3, wpa2
    passphrase: str
    vpn_tunnel_enabled: bool
    cloud_enabled: bool
    upstream_router: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class VPNTunnel:
    """WireGuard VPN tunnel configuration."""

    tunnel_id: str
    beacon_id: str
    beacon_public_key: str
    beacon_endpoint: str
    wizard_public_key: str
    wizard_endpoint: str = "wizard.udos.cloud"
    interface_address: str = "10.64.1.1/32"
    listen_port: int = 51820
    status: TunnelStatus = TunnelStatus.PENDING
    created_at: str = ""
    last_heartbeat: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.now().isoformat()


@dataclass
class DeviceQuotaEntry:
    """Per-device monthly cloud quota."""

    device_id: str
    budget_monthly_usd: float
    spent_this_month_usd: float = 0.0
    requests_this_month: int = 0
    month_start: str = ""
    month_end: str = ""

    def __post_init__(self):
        if not self.month_start:
            now = datetime.now()
            self.month_start = now.replace(day=1).isoformat()
            self.month_end = (
                (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            ).isoformat()


class BeaconService:
    """
    Beacon Portal business logic.

    Manages beacon configuration, VPN tunnels, device quotas, and
    local plugin caching.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize beacon service with optional custom database path."""
        self.db_path = db_path or BEACON_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS beacon_configs (
                    beacon_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    ssid TEXT NOT NULL,
                    band TEXT,
                    security TEXT,
                    passphrase TEXT,
                    vpn_tunnel_enabled BOOLEAN,
                    cloud_enabled BOOLEAN,
                    upstream_router TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vpn_tunnels (
                    tunnel_id TEXT PRIMARY KEY,
                    beacon_id TEXT NOT NULL,
                    beacon_public_key TEXT NOT NULL,
                    beacon_endpoint TEXT NOT NULL,
                    wizard_public_key TEXT NOT NULL,
                    wizard_endpoint TEXT,
                    interface_address TEXT,
                    listen_port INTEGER,
                    status TEXT,
                    created_at TEXT,
                    last_heartbeat TEXT,
                    FOREIGN KEY (beacon_id) REFERENCES beacon_configs(beacon_id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS device_quotas (
                    device_id TEXT PRIMARY KEY,
                    budget_monthly_usd REAL NOT NULL,
                    spent_this_month_usd REAL DEFAULT 0.0,
                    requests_this_month INTEGER DEFAULT 0,
                    month_start TEXT,
                    month_end TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS plugin_cache (
                    plugin_id TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    cached_at TEXT,
                    size_mb REAL,
                    download_url TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tunnel_statistics (
                    tunnel_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    bytes_sent INTEGER,
                    bytes_received INTEGER,
                    packets_lost INTEGER,
                    latency_ms INTEGER,
                    handshake_age_sec INTEGER,
                    PRIMARY KEY (tunnel_id, timestamp),
                    FOREIGN KEY (tunnel_id) REFERENCES vpn_tunnels(tunnel_id)
                )
            """
            )

            conn.commit()

    # ========================================================================
    # BEACON CONFIGURATION
    # ========================================================================

    def create_beacon_config(self, config: BeaconConfig) -> BeaconConfig:
        """Create new beacon configuration."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO beacon_configs (
                    beacon_id, mode, ssid, band, security, passphrase,
                    vpn_tunnel_enabled, cloud_enabled, upstream_router,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    config.beacon_id,
                    config.mode.value,
                    config.ssid,
                    config.band,
                    config.security,
                    config.passphrase,
                    config.vpn_tunnel_enabled,
                    config.cloud_enabled,
                    config.upstream_router,
                    config.created_at,
                    config.updated_at,
                ),
            )
            conn.commit()

        logger.info(f"[BEACON] Created beacon config: {config.beacon_id}")
        return config

    def get_beacon_config(self, beacon_id: str) -> Optional[BeaconConfig]:
        """Retrieve beacon configuration by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM beacon_configs WHERE beacon_id = ?", (beacon_id,)
            ).fetchone()

        if not row:
            return None

        return BeaconConfig(
            beacon_id=row[0],
            mode=BeaconMode(row[1]),
            ssid=row[2],
            band=row[3],
            security=row[4],
            passphrase=row[5],
            vpn_tunnel_enabled=bool(row[6]),
            cloud_enabled=bool(row[7]),
            upstream_router=row[8],
            created_at=row[9],
            updated_at=row[10],
        )

    def update_beacon_config(self, beacon_id: str, updates: Dict[str, Any]) -> bool:
        """Update beacon configuration."""
        updates["updated_at"] = datetime.now().isoformat()

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [beacon_id]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE beacon_configs SET {set_clause} WHERE beacon_id = ?", values)
            conn.commit()

        logger.info(f"[BEACON] Updated beacon config: {beacon_id}")
        return True

    # ========================================================================
    # VPN TUNNEL MANAGEMENT
    # ========================================================================

    def create_vpn_tunnel(self, tunnel: VPNTunnel) -> VPNTunnel:
        """Create new VPN tunnel configuration."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO vpn_tunnels (
                    tunnel_id, beacon_id, beacon_public_key, beacon_endpoint,
                    wizard_public_key, wizard_endpoint, interface_address,
                    listen_port, status, created_at, last_heartbeat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tunnel.tunnel_id,
                    tunnel.beacon_id,
                    tunnel.beacon_public_key,
                    tunnel.beacon_endpoint,
                    tunnel.wizard_public_key,
                    tunnel.wizard_endpoint,
                    tunnel.interface_address,
                    tunnel.listen_port,
                    tunnel.status.value,
                    tunnel.created_at,
                    tunnel.last_heartbeat,
                ),
            )
            conn.commit()

        logger.info(f"[WG] Created VPN tunnel: {tunnel.tunnel_id}")
        return tunnel

    def get_vpn_tunnel(self, tunnel_id: str) -> Optional[VPNTunnel]:
        """Retrieve VPN tunnel configuration by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM vpn_tunnels WHERE tunnel_id = ?", (tunnel_id,)
            ).fetchone()

        if not row:
            return None

        return VPNTunnel(
            tunnel_id=row[0],
            beacon_id=row[1],
            beacon_public_key=row[2],
            beacon_endpoint=row[3],
            wizard_public_key=row[4],
            wizard_endpoint=row[5],
            interface_address=row[6],
            listen_port=row[7],
            status=TunnelStatus(row[8]),
            created_at=row[9],
            last_heartbeat=row[10],
        )

    def update_tunnel_status(self, tunnel_id: str, status: TunnelStatus) -> bool:
        """Update VPN tunnel status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE vpn_tunnels
                SET status = ?, last_heartbeat = ?
                WHERE tunnel_id = ?
            """,
                (status.value, datetime.now().isoformat(), tunnel_id),
            )
            conn.commit()

        logger.info(f"[WG] Updated tunnel status: {tunnel_id} → {status.value}")
        return True

    def record_tunnel_stats(
        self, tunnel_id: str, bytes_sent: int, bytes_received: int, latency_ms: int
    ) -> bool:
        """Record tunnel statistics for monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tunnel_statistics (
                    tunnel_id, timestamp, bytes_sent, bytes_received,
                    packets_lost, latency_ms, handshake_age_sec
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (tunnel_id, datetime.now().isoformat(), bytes_sent, bytes_received, 0, latency_ms, 3600),
            )
            conn.commit()

        return True

    # ========================================================================
    # DEVICE QUOTA MANAGEMENT
    # ========================================================================

    def create_device_quota(self, quota: DeviceQuotaEntry) -> DeviceQuotaEntry:
        """Create new device quota."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO device_quotas (
                    device_id, budget_monthly_usd, spent_this_month_usd,
                    requests_this_month, month_start, month_end
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    quota.device_id,
                    quota.budget_monthly_usd,
                    quota.spent_this_month_usd,
                    quota.requests_this_month,
                    quota.month_start,
                    quota.month_end,
                ),
            )
            conn.commit()

        logger.info(f"[QUOTA] Created quota for device: {quota.device_id}")
        return quota

    def get_device_quota(self, device_id: str) -> Optional[DeviceQuotaEntry]:
        """Retrieve device quota."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM device_quotas WHERE device_id = ?", (device_id,)
            ).fetchone()

        if not row:
            return None

        return DeviceQuotaEntry(
            device_id=row[0],
            budget_monthly_usd=row[1],
            spent_this_month_usd=row[2],
            requests_this_month=row[3],
            month_start=row[4],
            month_end=row[5],
        )

    def deduct_quota(self, device_id: str, amount_usd: float) -> bool:
        """Deduct amount from device quota."""
        quota = self.get_device_quota(device_id)
        if not quota:
            return False

        if quota.spent_this_month_usd + amount_usd > quota.budget_monthly_usd:
            logger.warning(
                f"[QUOTA] Device {device_id} quota exceeded. "
                f"Requested: ${amount_usd}, Remaining: ${quota.budget_monthly_usd - quota.spent_this_month_usd}"
            )
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE device_quotas
                SET spent_this_month_usd = spent_this_month_usd + ?,
                    requests_this_month = requests_this_month + 1
                WHERE device_id = ?
            """,
                (amount_usd, device_id),
            )
            conn.commit()

        logger.info(f"[QUOTA] Deducted ${amount_usd} from {device_id}")
        return True

    def reset_device_quota(self, device_id: str) -> bool:
        """Reset monthly quota for device."""
        now = datetime.now()
        month_start = now.replace(day=1).isoformat()
        month_end = ((now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE device_quotas
                SET spent_this_month_usd = 0,
                    requests_this_month = 0,
                    month_start = ?,
                    month_end = ?
                WHERE device_id = ?
            """,
                (month_start, month_end, device_id),
            )
            conn.commit()

        logger.info(f"[QUOTA] Reset quota for device: {device_id}")
        return True

    # ========================================================================
    # PLUGIN CACHING
    # ========================================================================

    def cache_plugin(self, plugin_id: str, version: str, size_mb: float) -> bool:
        """Cache plugin on beacon node."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plugin_cache (
                    plugin_id, version, cached_at, size_mb, download_url
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (plugin_id, version, datetime.now().isoformat(), size_mb, f"http://beacon.local:8765/api/beacon/plugins/{plugin_id}"),
            )
            conn.commit()

        logger.info(f"[CACHE] Cached plugin: {plugin_id} v{version}")
        return True

    def get_cached_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached plugin info."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM plugin_cache WHERE plugin_id = ?", (plugin_id,)
            ).fetchone()

        if not row:
            return None

        return {
            "plugin_id": row[0],
            "version": row[1],
            "cached_at": row[2],
            "size_mb": row[3],
            "download_url": row[4],
        }

    def list_cached_plugins(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all cached plugins."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM plugin_cache LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()

        return [
            {
                "plugin_id": row[0],
                "version": row[1],
                "cached_at": row[2],
                "size_mb": row[3],
                "download_url": row[4],
            }
            for row in rows
        ]


# ============================================================================
# FACTORY & MODULE INITIALIZATION
# ============================================================================

_beacon_service: Optional[BeaconService] = None


def get_beacon_service(db_path: Optional[Path] = None) -> BeaconService:
    """Get or create singleton beacon service instance."""
    global _beacon_service
    if _beacon_service is None:
        _beacon_service = BeaconService(db_path)
    return _beacon_service

"""
Beacon Portal Routes

Manages beacon node configuration, WiFi setup, VPN tunnel control,
and device registration for local mesh networks.

Endpoints:
  - /api/beacon/configure       — Setup beacon WiFi + network mode
  - /api/beacon/status          — Beacon health + connected devices
  - /api/beacon/devices         — List recommended router hardware
  - /api/beacon/tunnel/*        — VPN tunnel management
  - /api/beacon/plugins/*       — Local plugin caching
"""

from pathlib import Path
from typing import Callable, Awaitable, Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
import sqlite3

from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel, Field

from wizard.services.beacon_service import (
    BeaconService,
    BeaconConfig,
    BeaconMode,
    VPNTunnel,
    TunnelStatus,
    DeviceQuotaEntry,
)
AuthGuard = Optional[Callable[[Request], Awaitable[str]]]

# Paths
BEACON_DB_PATH = Path(__file__).parent.parent.parent / "memory" / "beacon" / "beacon.db"
BEACON_CONFIG_PATH = Path(__file__).parent.parent / "config" / "beacon.json"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class BeaconNetworkConfig(BaseModel):
    """WiFi + Network configuration for beacon."""

    mode: str = Field(..., description="private-home | public-secure")
    ssid: str = Field(..., min_length=3, max_length=32)
    band: str = Field(default="both", description="2.4ghz | 5ghz | both")
    security: str = Field(default="wpa3", description="wpa3 | wpa2")
    passphrase: str = Field(default="knockknock", min_length=8, max_length=64)
    upstream_router: Optional[str] = None
    vpn_tunnel: bool = False
    cloud_enabled: bool = False
    operation_mode: str = Field(default="routing", description="routing | bridging")


class BeaconStatus(BaseModel):
    """Beacon health and connectivity status."""

    beacon_id: str
    status: str  # online | offline | degraded
    uptime_seconds: int
    wifi_ssid: str
    connected_devices: int
    vpn_tunnel_status: Optional[str] = None  # active | inactive | error
    local_services: List[str]
    last_heartbeat: str


class VPNTunnelConfig(BaseModel):
    """WireGuard VPN tunnel configuration."""

    tunnel_id: str
    beacon_id: str
    beacon_public_key: str
    beacon_endpoint: str
    wizard_public_key: str
    wizard_endpoint: str
    interface_address: str = Field(default="10.64.1.1/32")
    listen_port: int = Field(default=51820)
    status: str = Field(default="pending")  # pending | active | disabled


class DeviceQuota(BaseModel):
    """Per-device monthly cloud quota."""

    device_id: str
    budget_monthly_usd: float
    spent_this_month_usd: float
    remaining_usd: float
    requests_this_month: int
    resets_at: str


class RouterHardware(BaseModel):
    """Recommended router hardware for beacon deployment."""

    id: str
    model: str
    vendor: str
    price_usd: float
    wifi_bands: List[str]
    openwrt_support: bool
    openwrt_device_name: Optional[str] = None
    drivers: Optional[Dict[str, str]] = None
    flashing_guide: Optional[str] = None
    cost_tier: str  # budget | mid-range | professional
    power_consumption_watts: float
    range_meters: int
    verified_working: bool


class PluginCache(BaseModel):
    """Local plugin cache entry."""

    plugin_id: str
    version: str
    cached_at: str
    size_mb: float
    download_url: str


def create_beacon_routes(auth_guard: AuthGuard = None) -> APIRouter:
    """Create Beacon Portal routes."""
    router = APIRouter(prefix="/api/beacon", tags=["beacon"])
    beacon_service = BeaconService(BEACON_DB_PATH)

    def _validate_config(config: BeaconNetworkConfig) -> None:
        if config.mode not in {"private-home", "public-secure"}:
            raise HTTPException(status_code=400, detail="Invalid mode")
        if config.band not in {"2.4ghz", "5ghz", "both"}:
            raise HTTPException(status_code=400, detail="Invalid band")
        if config.security not in {"wpa3", "wpa2"}:
            raise HTTPException(status_code=400, detail="Invalid security")

    # ========================================================================
    # CONFIGURATION ENDPOINTS
    # ========================================================================

    @router.post("/configure", response_model=Dict[str, Any])
    async def configure_beacon(config: BeaconNetworkConfig, request: Request):
        """
        Configure beacon WiFi and network mode.

        Stores configuration and returns setup instructions.
        """
        if auth_guard:
            try:
                await auth_guard(request)
            except Exception:
                raise HTTPException(status_code=401, detail="Unauthorized")

        _validate_config(config)
        beacon_id = f"beacon-{uuid.uuid4().hex[:12]}"

        beacon_config = BeaconConfig(
            beacon_id=beacon_id,
            mode=BeaconMode(config.mode),
            ssid=config.ssid,
            band=config.band,
            security=config.security,
            passphrase=config.passphrase,
            vpn_tunnel_enabled=config.vpn_tunnel,
            cloud_enabled=config.cloud_enabled,
            upstream_router=config.upstream_router,
        )
        beacon_service.create_beacon_config(beacon_config)

        response = {
            "status": "success",
            "beacon_id": beacon_id,
            "ssid": config.ssid,
            "mode": config.mode,
            "ip_address": "192.168.100.1",
            "networks": {
                "primary": "192.168.100.0/24",
                "guest": "10.64.0.0/16" if config.mode == "private-home" else None,
            },
            "dns_servers": ["192.168.100.1", "8.8.8.8"],
            "vpn_tunnel_enabled": config.vpn_tunnel,
            "cloud_enabled": config.cloud_enabled,
            "instructions": (
                "WiFi is now active. Connect devices and run: "
                f"MESH PAIR {beacon_id}"
            ),
        }

        return response

    @router.post("/setup-hardware")
    async def get_hardware_setup(
        hardware: str = Body(..., embed=True),
        operation_mode: str = Body(default="routing", embed=True),
        request: Request = None,
    ):
        """
        Get device-specific setup instructions for router hardware.

        Queries Sonic Screwdriver for device details and generates
        step-by-step Alpine + uDOS installation guide.
        """
        if auth_guard:
            await auth_guard(request)

        # Hardware mappings
        guides = {
            "tplink-wr841n": {
                "model": "TP-Link TL-WR841N v14",
                "price_usd": 30,
                "firmware": "OpenWrt / Stock",
                "wifi_bands": ["2.4ghz"],
                "steps": [
                    "Download Alpine Linux minimal ISO",
                    "Create bootable USB with Ventoy",
                    "Boot router from USB (press Del during startup)",
                    "Follow Alpine setup wizard",
                    "Configure WiFi with hostapd",
                    "Install uDOS from GitHub",
                    "Register beacon with Wizard",
                ],
            },
            "ubiquiti-edgerouter-x": {
                "model": "Ubiquiti EdgeRouter X",
                "price_usd": 150,
                "firmware": "EdgeOS / OpenWrt",
                "wifi_bands": ["2.4ghz", "5ghz"],
                "steps": [
                    "SSH into router at 192.168.1.1",
                    "Download and flash Alpine Linux",
                    "Configure WireGuard for VPN tunnel",
                    "Enable WiFi access point mode",
                    "Install uDOS package",
                    "Register beacon",
                ],
            },
            "macbook-2015": {
                "model": "MacBook Pro 2015",
                "price_usd": 0,  # Used hardware
                "firmware": "macOS / Alpine Dualboot",
                "wifi_bands": ["2.4ghz", "5ghz"],
                "steps": [
                    "Backup macOS to external drive",
                    "Create Alpine Linux USB installer",
                    "Boot into Recovery Mode",
                    "Install Alpine alongside macOS",
                    "Install hostapd + dnsmasq for WiFi AP",
                    "Configure NetworkManager for routing",
                    "Install uDOS",
                    "Enable WiFi sharing",
                ],
            },
            "raspberry-pi-4": {
                "model": "Raspberry Pi 4B",
                "price_usd": 60,
                "firmware": "Alpine Linux / Raspberry Pi OS",
                "wifi_bands": ["2.4ghz", "5ghz"],
                "steps": [
                    "Download Alpine ARM64 image",
                    "Flash to microSD card with dd/Balena Etcher",
                    "Boot Raspberry Pi",
                    "Configure WiFi dongle if using external",
                    "Install hostapd + dnsmasq",
                    "Install uDOS",
                    "Set up persistent storage",
                    "Enable WireGuard for tunnel",
                ],
            },
        }

        if hardware not in guides:
            raise HTTPException(
                status_code=404,
                detail=f"Hardware '{hardware}' not found. Available: {list(guides.keys())}",
            )

        guide = guides[hardware]
        guide["status"] = "success"
        guide["operation_mode"] = operation_mode
        guide["estimated_time_minutes"] = len(guide["steps"]) * 5

        return guide

    # ========================================================================
    # STATUS & MONITORING
    # ========================================================================

    @router.get("/status", response_model=BeaconStatus)
    async def get_beacon_status(beacon_id: str = Query(...), request: Request = None):
        """Get beacon health and connectivity status."""
        if auth_guard:
            await auth_guard(request)

        config = beacon_service.get_beacon_config(beacon_id)
        if not config:
            raise HTTPException(status_code=404, detail="Beacon not found")

        updated_at = datetime.fromisoformat(config.updated_at)
        age = (datetime.now() - updated_at).total_seconds()
        status = "online" if age < 3600 else "degraded" if age < 86400 else "offline"

        return BeaconStatus(
            beacon_id=beacon_id,
            status=status,
            uptime_seconds=int(max(0, age)),
            wifi_ssid=config.ssid,
            connected_devices=0,
            vpn_tunnel_status="active" if config.vpn_tunnel_enabled else "inactive",
            local_services=["dns", "dhcp", "http", "meshcore", "ntp"],
            last_heartbeat=config.updated_at,
        )

    @router.get("/devices", response_model=List[RouterHardware])
    async def list_recommended_devices(
        cost_tier: Optional[str] = Query(None),
        wifi_bands: Optional[str] = Query(None),
        verified_only: bool = Query(True),
        request: Request = None,
    ):
        """
        List recommended router hardware for beacon deployment.

        Integrates with Sonic Screwdriver device database.
        """
        if auth_guard:
            await auth_guard(request)

        devices = [
            RouterHardware(
                id="tplink-wr841n",
                model="TL-WR841N v14",
                vendor="TP-Link",
                price_usd=30,
                wifi_bands=["2.4ghz"],
                openwrt_support=True,
                openwrt_device_name="tl-wr841n-v14",
                drivers={
                    "firmware": "https://github.com/openwrt/openwrt/releases",
                    "package": "openwrt-ath79-generic-tplink_wr841-v14-squashfs-sysupgrade.bin",
                },
                flashing_guide="https://openwrt.org/toh/tp-link/tl-wr841n",
                cost_tier="budget",
                power_consumption_watts=5,
                range_meters=30,
                verified_working=True,
            ),
            RouterHardware(
                id="ubiquiti-edgerouter-x",
                model="EdgeRouter X",
                vendor="Ubiquiti",
                price_usd=150,
                wifi_bands=["2.4ghz", "5ghz"],
                openwrt_support=False,
                cost_tier="professional",
                power_consumption_watts=8,
                range_meters=100,
                verified_working=True,
            ),
        ]

        # Filter by cost_tier if specified
        if cost_tier:
            devices = [d for d in devices if d.cost_tier == cost_tier]

        if wifi_bands:
            devices = [d for d in devices if wifi_bands in d.wifi_bands]

        # Filter by verified_only if requested
        if verified_only:
            devices = [d for d in devices if d.verified_working]

        return devices

    # ========================================================================
    # VPN TUNNEL MANAGEMENT
    # ========================================================================

    @router.post("/tunnel/enable", response_model=VPNTunnelConfig)
    async def enable_vpn_tunnel(
        beacon_id: str = Body(...),
        beacon_public_key: str = Body(...),
        beacon_endpoint: str = Body(...),
        request: Request = None,
    ):
        """
        Enable WireGuard VPN tunnel between beacon and Wizard.

        Generates Wizard public key and configuration.
        """
        if not beacon_id or not beacon_public_key:
            raise HTTPException(
                status_code=400, detail="beacon_id and beacon_public_key required"
            )

        if auth_guard:
            await auth_guard(request)

        if not beacon_service.get_beacon_config(beacon_id):
            raise HTTPException(status_code=404, detail="Beacon not found")

        tunnel_id = f"tunnel-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        tunnel = VPNTunnel(
            tunnel_id=tunnel_id,
            beacon_id=beacon_id,
            beacon_public_key=beacon_public_key,
            beacon_endpoint=beacon_endpoint,
            wizard_public_key="<wizard-generated-key>",  # Would generate in real impl
            wizard_endpoint="wizard.udos.cloud",
            status=TunnelStatus.PENDING,
        )

        beacon_service.create_vpn_tunnel(tunnel)
        beacon_service.update_beacon_config(beacon_id, {"vpn_tunnel_enabled": True})

        return VPNTunnelConfig(
            tunnel_id=tunnel_id,
            beacon_id=beacon_id,
            beacon_public_key=beacon_public_key,
            beacon_endpoint=beacon_endpoint,
            wizard_public_key=tunnel.wizard_public_key,
            wizard_endpoint=tunnel.wizard_endpoint,
            interface_address=tunnel.interface_address,
            listen_port=tunnel.listen_port,
            status=tunnel.status.value,
        )

    @router.get("/tunnel/{tunnel_id}/status")
    async def get_tunnel_status(tunnel_id: str, request: Request = None):
        """Monitor VPN tunnel health and statistics."""
        if auth_guard:
            await auth_guard(request)

        tunnel = beacon_service.get_vpn_tunnel(tunnel_id)
        if not tunnel:
            raise HTTPException(status_code=404, detail="Tunnel not found")

        stats = beacon_service.get_latest_tunnel_stats(tunnel_id)
        return {
            "tunnel_id": tunnel_id,
            "status": tunnel.status.value,
            "connected_since": tunnel.created_at,
            "bytes_sent": stats.get("bytes_sent") if stats else 0,
            "bytes_received": stats.get("bytes_received") if stats else 0,
            "packets_lost": stats.get("packets_lost") if stats else 0,
            "latency_ms": stats.get("latency_ms") if stats else 0,
            "handshake_age_sec": stats.get("handshake_age_sec") if stats else 0,
        }

    @router.post("/tunnel/{tunnel_id}/disable")
    async def disable_tunnel(tunnel_id: str, reason: str = Body(...), request: Request = None):
        """Disable VPN tunnel (beacon remains operational offline)."""
        if auth_guard:
            await auth_guard(request)

        beacon_service.update_tunnel_status(tunnel_id, TunnelStatus.DISABLED)
        tunnel = beacon_service.get_vpn_tunnel(tunnel_id)
        if tunnel:
            beacon_service.update_beacon_config(tunnel.beacon_id, {"vpn_tunnel_enabled": False})
        return {
            "status": "success",
            "tunnel_id": tunnel_id,
            "message": f"Tunnel disabled: {reason}",
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================================
    # DEVICE QUOTA MANAGEMENT
    # ========================================================================

    @router.get("/devices/{device_id}/quota", response_model=DeviceQuota)
    async def get_device_quota(device_id: str, request: Request = None):
        """Check device's remaining monthly cloud budget."""
        if auth_guard:
            await auth_guard(request)

        quota = beacon_service.get_device_quota(device_id)
        if not quota:
            quota = beacon_service.create_device_quota(
                DeviceQuotaEntry(device_id=device_id, budget_monthly_usd=5.0)
            )

        remaining = max(0.0, quota.budget_monthly_usd - quota.spent_this_month_usd)
        return DeviceQuota(
            device_id=quota.device_id,
            budget_monthly_usd=quota.budget_monthly_usd,
            spent_this_month_usd=quota.spent_this_month_usd,
            remaining_usd=remaining,
            requests_this_month=quota.requests_this_month,
            resets_at=quota.month_end,
        )

    @router.post("/devices/{device_id}/quota/add-funds")
    async def add_device_funds(
        device_id: str, amount_usd: float = Body(...), request: Request = None
    ):
        """Add emergency funds to device quota."""
        if auth_guard:
            await auth_guard(request)

        if amount_usd <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")

        quota = beacon_service.add_device_funds(device_id, amount_usd)
        if not quota:
            raise HTTPException(status_code=404, detail="Device quota not found")

        return {
            "status": "success",
            "device_id": device_id,
            "amount_added": amount_usd,
            "new_budget": quota.budget_monthly_usd,
            "expires": quota.month_end,
        }

    # ========================================================================
    # LOCAL PLUGIN CACHING
    # ========================================================================

    @router.get("/plugins/{plugin_id}", response_model=PluginCache)
    async def get_cached_plugin(plugin_id: str, request: Request = None):
        """
        Fetch plugin from beacon's local cache.

        If not cached locally, Wizard acts as mirror.
        """
        if auth_guard:
            await auth_guard(request)

        cached = beacon_service.get_cached_plugin(plugin_id)
        if not cached:
            raise HTTPException(status_code=404, detail="Plugin not cached")
        return PluginCache(**cached)

    @router.post("/plugins/{plugin_id}/cache")
    async def cache_plugin(plugin_id: str, request: Request = None):
        """Pre-cache plugin on beacon for faster distribution."""
        if auth_guard:
            await auth_guard(request)

        cached = beacon_service.cache_plugin(plugin_id, version="1.0.0", size_mb=1.0)
        if not cached:
            raise HTTPException(status_code=500, detail="Failed to cache plugin")
        return {
            "status": "success",
            "plugin_id": plugin_id,
            "cached_at": datetime.now().isoformat(),
            "location": "beacon-local",
        }

    return router

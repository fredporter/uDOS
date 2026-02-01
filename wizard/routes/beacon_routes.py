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
import json
import sqlite3

from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel, Field

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
    passphrase: str = Field(default="knockknock")
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

    # ========================================================================
    # CONFIGURATION ENDPOINTS
    # ========================================================================

    @router.post("/configure", response_model=Dict[str, Any])
    async def configure_beacon(config: BeaconNetworkConfig, request: Request):
        """
        Configure beacon WiFi and network mode.

        Stores configuration and returns setup instructions.
        """
        device_id = None
        if auth_guard:
            try:
                device_id = await auth_guard(request)
            except:
                raise HTTPException(status_code=401, detail="Unauthorized")

        beacon_id = f"beacon-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        response = {
            "status": "success",
            "beacon_id": beacon_id,
            "ssid": config.ssid,
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
                "MESH PAIR beacon-{beacon_id}"
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
        # Placeholder: Would query beacon health from database
        return BeaconStatus(
            beacon_id=beacon_id,
            status="online",
            uptime_seconds=86400,
            wifi_ssid="uDOS-beacon",
            connected_devices=3,
            vpn_tunnel_status="active",
            local_services=["dns", "dhcp", "http", "meshcore", "ntp"],
            last_heartbeat=datetime.now().isoformat(),
        )

    @router.get("/devices", response_model=List[RouterHardware])
    async def list_recommended_devices(
        cost_tier: Optional[str] = Query(None),
        wifi_bands: Optional[str] = Query(None),
        verified_only: bool = Query(True),
    ):
        """
        List recommended router hardware for beacon deployment.

        Integrates with Sonic Screwdriver device database.
        """
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

        tunnel_id = f"tunnel-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        config = VPNTunnelConfig(
            tunnel_id=tunnel_id,
            beacon_id=beacon_id,
            beacon_public_key=beacon_public_key,
            beacon_endpoint=beacon_endpoint,
            wizard_public_key="<wizard-generated-key>",  # Would generate in real impl
            wizard_endpoint="wizard.udos.cloud",
            status="pending",
        )

        return config

    @router.get("/tunnel/{tunnel_id}/status")
    async def get_tunnel_status(tunnel_id: str):
        """Monitor VPN tunnel health and statistics."""
        return {
            "tunnel_id": tunnel_id,
            "status": "active",
            "connected_since": (datetime.now() - timedelta(days=5)).isoformat(),
            "bytes_sent": 15728640,
            "bytes_received": 52428800,
            "packets_lost": 0,
            "latency_ms": 45,
            "handshake_age_sec": 3600,
        }

    @router.post("/tunnel/{tunnel_id}/disable")
    async def disable_tunnel(tunnel_id: str, reason: str = Body(...)):
        """Disable VPN tunnel (beacon remains operational offline)."""
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
    async def get_device_quota(device_id: str):
        """Check device's remaining monthly cloud budget."""
        return DeviceQuota(
            device_id=device_id,
            budget_monthly_usd=5.00,
            spent_this_month_usd=2.45,
            remaining_usd=2.55,
            requests_this_month=320,
            resets_at=(datetime.now() + timedelta(days=6)).isoformat(),
        )

    @router.post("/devices/{device_id}/quota/add-funds")
    async def add_device_funds(device_id: str, amount_usd: float = Body(...)):
        """Add emergency funds to device quota."""
        if amount_usd <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")

        return {
            "status": "success",
            "device_id": device_id,
            "amount_added": amount_usd,
            "new_budget": 15.00,
            "expires": (datetime.now() + timedelta(days=30)).isoformat(),
        }

    # ========================================================================
    # LOCAL PLUGIN CACHING
    # ========================================================================

    @router.get("/plugins/{plugin_id}", response_model=PluginCache)
    async def get_cached_plugin(plugin_id: str):
        """
        Fetch plugin from beacon's local cache.

        If not cached locally, Wizard acts as mirror.
        """
        # Placeholder: Would check local cache first
        return PluginCache(
            plugin_id=plugin_id,
            version="1.0.0",
            cached_at=datetime.now().isoformat(),
            size_mb=2.5,
            download_url=f"http://beacon.local:8765/api/beacon/plugins/{plugin_id}",
        )

    @router.post("/plugins/{plugin_id}/cache")
    async def cache_plugin(plugin_id: str):
        """Pre-cache plugin on beacon for faster distribution."""
        return {
            "status": "success",
            "plugin_id": plugin_id,
            "cached_at": datetime.now().isoformat(),
            "location": "beacon-local",
        }

    return router

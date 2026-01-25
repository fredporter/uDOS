# Beacon Portal Implementation Guide

**Version:** 1.0.0  
**Status:** Ready for Integration  
**Last Updated:** 2026-01-25

## Overview

The Beacon Portal system enables **uDOS devices** to connect to the internet via **beacon nodes** (dedicated routers running Alpine Linux) without requiring direct cloud connectivity.

This document guides implementation of the Beacon Portal in Wizard Server.

## Components Implemented

### 1. Specification Documents

| File                                                                   | Purpose                                   |
| ---------------------------------------------------------------------- | ----------------------------------------- |
| [docs/wiki/SONIC-SCREWDRIVER.md](../../docs/wiki/SONIC-SCREWDRIVER.md) | Device catalog + hardware recommendations |
| [docs/wiki/BEACON-PORTAL.md](../../docs/wiki/BEACON-PORTAL.md)         | Beacon WiFi + network architecture        |
| [docs/wiki/BEACON-VPN-TUNNEL.md](../../docs/wiki/BEACON-VPN-TUNNEL.md) | WireGuard tunnel configuration            |
| [docs/wiki/ALPINE-CORE.md](../../docs/wiki/ALPINE-CORE.md)             | Alpine Linux deployment target            |

### 2. Wizard Server Routes

**File:** [wizard/routes/beacon_routes.py](beacon_routes.py)

**Endpoints:**

```
POST   /api/v1/beacon/configure               — Configure WiFi + network mode
POST   /api/v1/beacon/setup-hardware          — Get device-specific setup instructions
GET    /api/v1/beacon/status                  — Beacon health + connected devices
GET    /api/v1/beacon/devices                 — List recommended router hardware
POST   /api/v1/beacon/tunnel/enable           — Create VPN tunnel
GET    /api/v1/beacon/tunnel/{id}/status      — Monitor tunnel health
POST   /api/v1/beacon/tunnel/{id}/disable     — Disable tunnel
GET    /api/v1/beacon/devices/{id}/quota      — Check device cloud budget
POST   /api/v1/beacon/devices/{id}/quota/add-funds  — Add emergency funds
GET    /api/v1/beacon/plugins/{id}            — Fetch cached plugin
POST   /api/v1/beacon/plugins/{id}/cache      — Pre-cache plugin
```

### 3. Beacon Service Layer

**File:** [wizard/services/beacon_service.py](beacon_service.py)

**Class:** `BeaconService`

**Core Methods:**

```python
# Beacon Configuration
create_beacon_config(config: BeaconConfig)      → BeaconConfig
get_beacon_config(beacon_id: str)               → Optional[BeaconConfig]
update_beacon_config(beacon_id: str, updates)   → bool

# VPN Tunnel Management
create_vpn_tunnel(tunnel: VPNTunnel)             → VPNTunnel
get_vpn_tunnel(tunnel_id: str)                  → Optional[VPNTunnel]
update_tunnel_status(tunnel_id: str, status)    → bool
record_tunnel_stats(tunnel_id, bytes_sent, ...)  → bool

# Device Quota Management
create_device_quota(quota: DeviceQuotaEntry)     → DeviceQuotaEntry
get_device_quota(device_id: str)                → Optional[DeviceQuotaEntry]
deduct_quota(device_id: str, amount_usd)         → bool
reset_device_quota(device_id: str)               → bool

# Plugin Caching
cache_plugin(plugin_id, version, size_mb)        → bool
get_cached_plugin(plugin_id)                    → Optional[Dict]
list_cached_plugins(limit, offset)              → List[Dict]
```

## Database Schema

### Tables

**beacon_configs** — Beacon WiFi + network configuration

```sql
beacon_id TEXT PRIMARY KEY
mode TEXT (private-home | public-secure)
ssid TEXT
band TEXT (2.4ghz | 5ghz | both)
security TEXT (wpa3 | wpa2)
passphrase TEXT
vpn_tunnel_enabled BOOLEAN
cloud_enabled BOOLEAN
upstream_router TEXT
created_at TEXT
updated_at TEXT
```

**vpn_tunnels** — WireGuard tunnel endpoints

```sql
tunnel_id TEXT PRIMARY KEY
beacon_id TEXT FOREIGN KEY
beacon_public_key TEXT
beacon_endpoint TEXT
wizard_public_key TEXT
wizard_endpoint TEXT
interface_address TEXT
listen_port INTEGER
status TEXT (pending | active | disabled | error)
created_at TEXT
last_heartbeat TEXT
```

**device_quotas** — Per-device monthly cloud budget

```sql
device_id TEXT PRIMARY KEY
budget_monthly_usd REAL
spent_this_month_usd REAL
requests_this_month INTEGER
month_start TEXT
month_end TEXT
```

**plugin_cache** — Local plugin cache metadata

```sql
plugin_id TEXT PRIMARY KEY
version TEXT
cached_at TEXT
size_mb REAL
download_url TEXT
```

**tunnel_statistics** — VPN tunnel monitoring data

```sql
tunnel_id TEXT NOT NULL
timestamp TEXT NOT NULL
bytes_sent INTEGER
bytes_received INTEGER
packets_lost INTEGER
latency_ms INTEGER
handshake_age_sec INTEGER
PRIMARY KEY (tunnel_id, timestamp)
```

## Integration Steps

### Step 1: Register Routes in Wizard Server

In [wizard/server.py](../server.py), import and register beacon routes:

```python
from wizard.routes.beacon_routes import create_beacon_routes

# In FastAPI app setup:
beacon_router = create_beacon_routes(auth_guard=auth_middleware)
app.include_router(beacon_router)
```

### Step 2: Initialize Beacon Service

In [wizard/services/**init**.py](./):

```python
from wizard.services.beacon_service import get_beacon_service

# Access singleton:
beacon_svc = get_beacon_service()
```

### Step 3: Add Database Initialization

Update Wizard startup to initialize beacon database:

```python
# In wizard/server.py startup hook:
from wizard.services.beacon_service import get_beacon_service

async def startup():
    beacon_svc = get_beacon_service()
    # Database tables auto-created by __init_db()
    logger.info("[BEACON] Service initialized")
```

### Step 4: Create CLI Commands

Add Wizard TUI commands for beacon management:

```bash
# In wizard/wizard_tui.py:
BEACON STATUS [beacon-id]       # Check beacon health
BEACON CONFIGURE [mode] [ssid]  # Setup new beacon
BEACON DEVICES                  # List hardware
TUNNEL ENABLE [beacon-id]       # Create VPN tunnel
TUNNEL STATUS [tunnel-id]       # Monitor tunnel
QUOTA CHECK [device-id]         # Check cloud budget
```

### Step 5: Implement Hardware Setup Guides

Expand `setup_hardware` endpoint with complete install scripts for:

- **TP-Link TL-WR841N** (budget)
- **Ubiquiti EdgeRouter X** (professional)
- **MacBook 2015+** (laptop conversion)
- **Raspberry Pi 4** (SBC)
- Others (user contributions welcome)

### Step 6: Add VPN Tunnel Integration

Implement WireGuard configuration generation:

```python
# In beacon_service.py:
def generate_wireguard_config(self, tunnel: VPNTunnel) -> str:
    """Generate WireGuard config file content."""
    config = f"""
[Interface]
Address = {tunnel.interface_address}
ListenPort = {tunnel.listen_port}
PrivateKey = <generated-key>
SaveCounters = true

[Peer]
PublicKey = {tunnel.wizard_public_key}
AllowedIPs = 10.64.2.0/24, 192.168.100.0/24
PersistentKeepalive = 25
    """.strip()
    return config
```

### Step 7: Add Quota Enforcement

In API route handlers, check quota before allowing cloud requests:

```python
# In beacon_routes.py:
beacon_svc = get_beacon_service()

@router.post("/ai/complete")
async def request_ai_completion(device_id: str, prompt: str, request: Request):
    quota = beacon_svc.get_device_quota(device_id)
    if quota.remaining_usd < 0.01:  # Min $0.01 per request
        raise HTTPException(status_code=429, detail="Quota exceeded")

    # Proceed with request...
    cost = 0.005  # From model routing
    beacon_svc.deduct_quota(device_id, cost)
```

### Step 8: Add Monitoring Dashboard

Create Wizard TUI dashboard showing:

- Total connected beacons
- Devices per beacon
- Tunnel status + latency
- Cloud budget usage
- Plugin cache size

## Testing Checklist

```bash
# Unit Tests
pytest wizard/tests/test_beacon_service.py -v
pytest wizard/tests/test_beacon_routes.py -v

# Integration Tests
./start_udos.sh
> BEACON STATUS beacon-home-01
> BEACON DEVICES
> BEACON CONFIGURE private-home "MyNetwork"

# VPN Tunnel Tests
> TUNNEL ENABLE beacon-home-01
> TUNNEL STATUS tunnel-xyz

# Quota Tests
> QUOTA CHECK mobile-a1b2c3
> QUOTA ADD-FUNDS mobile-a1b2c3 10.00

# Hardware Setup Tests
pytest wizard/tests/test_hardware_guides.py -v

# Load Testing (Multiple Beacons)
ab -n 1000 -c 10 http://localhost:8765/api/v1/beacon/status?beacon_id=beacon-1
```

## Security Considerations

### API Authentication

All `/api/v1/beacon/*` endpoints require device authentication:

```python
from wizard.security.auth_middleware import auth_guard

@router.get("/devices/{device_id}/quota")
async def get_quota(device_id: str, request: Request):
    authenticated_device = await auth_guard(request)
    # Only device owner can see their quota
    if authenticated_device != device_id:
        raise HTTPException(status_code=403, detail="Forbidden")
```

### WireGuard Key Security

- Private keys stored in **read-only files** (`chmod 0600`)
- Keys rotated **annually** or on compromise
- Stored in **system keyring** if available
- Never transmitted except during initial HTTPS setup

### Quota Enforcement

- **Check before execution** (pessimistic quota model)
- **Deduct after success** (transactional)
- **Monthly reset** (automatic at month boundary)
- **Alert at 80%** (user notification)

### Traffic Encryption

- **WireGuard cipher:** ChaCha20-Poly1305 (AEAD)
- **Key exchange:** Curve25519 (post-quantum candidate)
- **Application layer:** TLS 1.3 (double encryption)
- **No plaintext data** on tunnel

## Performance Targets

| Metric                  | Target  | Notes                           |
| ----------------------- | ------- | ------------------------------- |
| Tunnel setup time       | < 2s    | WireGuard handshake + DB insert |
| Quota check latency     | < 100ms | SQLite query on fast disk       |
| Plugin list (100 items) | < 200ms | Paginated query                 |
| Tunnel status check     | < 150ms | Stats query + calculation       |
| Configuration create    | < 500ms | Validation + DB write           |

## Future Enhancements

### Phase 2 (Q2 2026)

- [ ] Multi-Wizard load balancing (multiple cloud servers)
- [ ] Automatic tunnel failover (secondary Wizard)
- [ ] Advanced quota models (per-service budgets)
- [ ] Plugin pre-caching (background download)
- [ ] Beacon replication (backup nodes)

### Phase 3 (Q3 2026)

- [ ] Mesh-to-mesh tunneling (peering between beacons)
- [ ] Advanced quota analytics (usage dashboards)
- [ ] Device grouping (shared quotas)
- [ ] Bandwidth throttling (QoS per device)
- [ ] SLA monitoring (uptime tracking)

## References

- [BEACON-PORTAL.md](../../docs/wiki/BEACON-PORTAL.md) — Architecture
- [BEACON-VPN-TUNNEL.md](../../docs/wiki/BEACON-VPN-TUNNEL.md) — Tunnel spec
- [SONIC-SCREWDRIVER.md](../../docs/wiki/SONIC-SCREWDRIVER.md) — Hardware DB
- [AGENTS.md](../../AGENTS.md) — Development guidelines
- [wizard/ARCHITECTURE.md](../ARCHITECTURE.md) — Wizard structure

---

**Status:** Ready for implementation  
**Owner:** uDOS Wizard Team  
**Next Review:** 2026-02-15

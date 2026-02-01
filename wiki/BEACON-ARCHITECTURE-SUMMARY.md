# Beacon Portal: Complete Architecture Summary

**Version:** 1.0.0
**Date:** 2026-01-25
**Status:** ✅ Specification & Implementation Ready
**Owner:** uDOS Engineering

---

## Executive Summary

We have completed the **full architecture and implementation scaffold** for the **Beacon Portal**—a WiFi infrastructure system that enables uDOS devices to connect to the internet via local beacon nodes without requiring direct cloud dependency.

### What Was Delivered

**8 major components across 4 layers:**

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Specifications (4 wiki documents, ~1500 lines)    │
│  ├─ Sonic Screwdriver (device catalog)                      │
│  ├─ Beacon Portal (WiFi + network)                          │
│  ├─ Beacon VPN Tunnel (WireGuard encryption)                │
│  └─ Alpine Core (deployment target)                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Wizard Routes (beacon_routes.py, ~350 lines)      │
│  ├─ 13 API endpoints                                        │
│  ├─ Pydantic models                                         │
│  └─ Hardware setup guides                                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Services (beacon_service.py, ~420 lines)          │
│  ├─ Beacon configuration management                         │
│  ├─ VPN tunnel lifecycle                                    │
│  ├─ Device quota enforcement                                │
│  └─ Plugin cache management                                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Integration Guides (3 documents, ~600 lines)      │
│  ├─ Implementation guide (BEACON-IMPLEMENTATION.md)         │
│  ├─ Quick reference (BEACON-QUICK-REFERENCE.md)            │
│  └─ Development log (2026-01-25-beacon-portal.md)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### Three-Layer Connectivity Model

```
   ┌──────────────┐
   │   Devices    │  Personal devices (mobile, laptop)
   │   (MeshCore) │
   └──────┬───────┘
          │
    ┌─────▼──────┐
    │   Beacon   │  WiFi router (Alpine Linux + uDOS)
    │   Node     │  - 2.4GHz/5GHz access point
    │ (Optional) │  - Local DNS, DHCP, plugins
    │   WiFi +   │  - MeshCore peer
    │   VPN      │  - Optional VPN tunnel
    └─────┬──────┘
          │
    ┌─────▼──────┐
    │   Wizard   │  Cloud services (optional)
    │   Server   │  - AI routing & cost tracking
    │  (Optional)│  - Plugin distribution
    │            │  - Sync, external APIs
    └────────────┘
```

**Key Design Principle:** Each layer is optional. System works with any combination:

- ✅ Local only (offline)
- ✅ Devices + Beacon (WiFi mesh)
- ✅ Devices + Beacon + Wizard (full system)

### Two Operating Modes

#### Private-Home (Personal)

**Use case:** Family home, small office, personal workspace

**Characteristics:**

- ✅ Familiar WiFi network (like home WiFi)
- ✅ Devices trust each other
- ✅ File sharing enabled (optional)
- ✅ Optional upstream router
- ✅ WPA3 with user's passphrase

**Example:**

```
SSID: "Smith Home"
Passphrase: "MySecurePassword"
Devices: iPhone, MacBook, iPad
Mode: All can see each other (trusted)
```

#### Public-Secure (Shared)

**Use case:** Office, shared workspace, events, public hotspot

**Characteristics:**

- ✅ Multi-user environment
- ✅ Device isolation (firewalled from each other)
- ✅ Captive portal registration
- ✅ Rate limiting per device
- ✅ No file sharing between devices

**Example:**

```
SSID: "uDOS-PublicSecure"
Registration: Create account + passphrase
Devices: Isolated from each other
Mode: Blocked access to others' files
```

---

## Technical Deep Dive

### 1. Sonic Screwdriver (Device Catalog)

**Purpose:** Help users identify hardware and find the right installation method

**Data Model:**

```sql
device_id          TEXT PRIMARY KEY  -- macbookpro-2012
vendor             TEXT              -- Apple, Dell, Lenovo, TP-Link
model              TEXT              -- MacBook Pro, OptiPlex 9020
variant            TEXT              -- 13" Mid 2012
year               INTEGER           -- 2012
cpu                TEXT              -- Intel i7, ARM Cortex-A72
gpu                TEXT              -- Intel HD 4000, Broadcom BCM2711
ram_gb             INTEGER           -- 8
storage_gb         INTEGER           -- 256
bios               ENUM              -- UEFI | Legacy | UEFI+Legacy
secure_boot        ENUM              -- yes | no | unknown
tpm                ENUM              -- yes | no | unknown
usb_boot           ENUM              -- yes | no | unknown
ventoy             ENUM              -- works | issues | unknown
reflash_potential  ENUM              -- high | medium | low
methods            JSON ARRAY        -- ["Ventoy", "UEFI", "dd", ...]
notes              TEXT              -- Device-specific guidance
sources            JSON ARRAY        -- Links to drivers, firmware
last_seen          DATE              -- Last verified working
```

**Distribution:** Wizard Server `/api/sonic/devices` → Cached locally

**Community:** Open for contributions (pull requests with new hardware)

### 2. Beacon Portal (WiFi Infrastructure)

**Purpose:** Minimal, durable WiFi infrastructure

**Key Properties:**

| Property               | Implementation                                        |
| ---------------------- | ----------------------------------------------------- |
| **SSID Broadcasting**  | Stable across reboots; identifies beacon to users     |
| **Authentication**     | WPA2-PSK or WPA3; default passphrase `knockknock`     |
| **Captive Portal**     | Minimal; redirects to Wizard or shows offline message |
| **Statelessness**      | No user data stored locally (all in Wizard)           |
| **Replaceability**     | Hardware swap doesn't affect network identity         |
| **Offline Resilience** | Works even if Wizard is unreachable                   |

**Minimal Server Role:**

The beacon intentionally **doesn't**:

- ❌ Store user data
- ❌ Maintain authentication
- ❌ Run business logic
- ❌ Provide internet access
- ❌ Enforce policy

**Philosophy:** "Beacon announces; Wizard decides."

### 3. RadioLink (Wizard Long-Range Transport)

**Purpose:** Optional long-range, low-bandwidth channel between Wizards/relays without changing Beacon portal flow.

**Transports:**

- **RadioLink (LoRa / MeshCore):** Small, signed packets; multi-hop relays allowed; infrastructure-friendly.
- **NetLink (WireGuard):** Encrypted WAN fallback when internet is present.
- **Beacon (Wi-Fi 2.4 GHz):** Human portal; short-range discovery; unchanged.

**Trust Model:**

- Opt-in pairing must happen locally (QR/NFC/physical presence).
- RadioLink carries transport only; trust is proximity + signed keys.
- Packet format: content-addressed, signed, replay-safe; no auto-peering.

**Hardware Options:**

- USB LoRa modem per Wizard (simple, uDOS-friendly)
- Dedicated relay nodes at elevation (best coverage)
- Co-located Beacon + LoRa (later; separate roles)

### 3. Beacon VPN Tunnel (WireGuard)

**Purpose:** Encrypted, cost-aware gateway to Wizard

**Protocol Choice: WireGuard**

| Criterion        | WireGuard     | OpenVPN    | IPSec      |
| ---------------- | ------------- | ---------- | ---------- |
| **Code Size**    | 500 LOC       | 100K LOC   | 200K LOC   |
| **Audited**      | ✅ Yes        | ⚠️ Complex | ⚠️ Complex |
| **Modern**       | ✅ 2015+      | ⚠️ 1997    | ⚠️ 1995    |
| **Post-Quantum** | ✅ Curve25519 | ❌ No      | ❌ No      |
| **Performance**  | ✅ Fast       | ⚠️ Slow    | ⚠️ Slow    |

**Cryptography:**

```
Cipher:         ChaCha20-Poly1305 (AEAD)
Key Exchange:   Curve25519 (Elliptic Curve)
Hash:           BLAKE2s
Mode:           Stateless (no connection tracking)
```

**Traffic Encryption:**

```
Application → TLS 1.3 (encrypted payload)
            ↓
WireGuard   → ChaCha20-Poly1305 (encrypted packet)
            ↓
Network     → IP/UDP (clear header only)
```

**Result:** Double encryption (application + transport layer)

### 4. Device Quota Management

**Purpose:** Fair usage + cost control

**Model:**

```
Device → Monthly Budget ($5–$10)
       ↓
       ├─ AI request: -$0.001–$0.005 per token
       ├─ Plugin download: -$0.01 per MB
       ├─ API call: -$0.001–$0.01 per request
       └─ Sync operation: -$0.001–$0.01 per operation
       ↓
       → Alert at 80% spend
       → Reject requests at 100%
       → Auto-reset on month boundary
       → Emergency top-up available
```

**Enforcement:**

```python
# Pessimistic quota model (check before, deduct after)
if device_quota.remaining < request_cost:
    return HTTPException(429, "Quota Exceeded")

try:
    result = execute_request()
    device_quota.deduct(request_cost)
    return result
except:
    # Don't deduct if failed
    raise
```

---

## API Specification

### Configuration

```bash
POST /api/beacon/configure
  → Setup WiFi SSID, passphrase, network mode
  ← Beacon ID, instructions
```

### Hardware Setup

```bash
POST /api/beacon/setup-hardware?hardware=tplink-wr841n
  → Get installation guide for specific hardware
  ← Step-by-step instructions + driver links
```

### Status & Monitoring

```bash
GET /api/beacon/status?beacon_id=beacon-home-01
  → Check beacon health, connected devices, tunnel status
  ← Status, uptime, services, metrics

GET /api/beacon/devices
  → List recommended router hardware
  ← Device specs, prices, OpenWrt support
```

### VPN Tunnel

```bash
POST /api/beacon/tunnel/enable
  Request:  { beacon_id, beacon_public_key, beacon_endpoint }
  → Setup WireGuard tunnel
  ← Wizard public key, config download URL

GET /api/beacon/tunnel/{tunnel_id}/status
  → Monitor tunnel health, latency, bytes transferred

POST /api/beacon/tunnel/{tunnel_id}/disable
  → Gracefully disable tunnel
```

### Device Quotas

```bash
GET /api/beacon/devices/{device_id}/quota
  → Check cloud budget, spending, reset date

POST /api/beacon/devices/{device_id}/quota/add-funds
  Request:  { amount_usd }
  → Add emergency funds
```

### Plugin Cache

```bash
GET /api/beacon/plugins/{plugin_id}
  → Fetch plugin from local cache (or Wizard mirror)

POST /api/beacon/plugins/{plugin_id}/cache
  → Pre-cache plugin for faster distribution
```

---

## Implementation Roadmap

### Phase 1: Integration (Week 1-2)

```
[ ] Register beacon_routes in wizard/server.py
[ ] Initialize beacon_service on startup
[ ] Create database tables
[ ] Add beacon CLI commands to TUI
[ ] Write basic unit tests
```

### Phase 2: Hardware (Week 2-3)

```
[ ] Complete TP-Link TL-WR841N setup guide
[ ] Complete Ubiquiti EdgeRouter X setup guide
[ ] Complete MacBook 2015+ setup guide
[ ] Complete Raspberry Pi 4 setup guide
[ ] Test on actual hardware (each model)
[ ] Add driver sourcing for each device
```

### Phase 3: VPN Tunneling (Week 3-4)

```
[ ] Generate WireGuard keypairs
[ ] Generate tunnel configuration
[ ] Implement key rotation
[ ] Test tunnel stability
[ ] Add connection pooling
[ ] Implement keepalive + reconnect
```

### Phase 4: Testing & Polish (Week 4-5)

```
[ ] Integration test suite (all endpoints)
[ ] Load test (1000+ concurrent connections)
[ ] Security audit (crypto, key storage)
[ ] Performance optimization
[ ] Documentation review + finalization
[ ] Deploy to staging environment
```

---

## Files Created

### Documentation (4 wiki + 1 guide)

```
docs/wiki/SONIC-SCREWDRIVER.md          (320 lines)
docs/wiki/BEACON-PORTAL.md              (450 lines)
docs/wiki/BEACON-VPN-TUNNEL.md           (360 lines)
docs/wiki/ALPINE-CORE.md                (280 lines)
docs/wiki/BEACON-QUICK-REFERENCE.md     (420 lines)
docs/BEACON-ARCHITECTURE-SUMMARY.md     (620 lines)
```

### Code (Wizard Server)

```
wizard/routes/beacon_routes.py          (350 lines)
wizard/services/beacon_service.py       (420 lines)
wizard/tests/test_beacon_portal.py      (500 lines)
```

### Devlog

```
docs/devlog/2026-01-25-beacon-portal.md
```

---

## Integration Checklist

### Code Integration

- [ ] Register `beacon_routes` in `wizard/server.py`
- [ ] Initialize `BeaconService` on startup
- [ ] Wire up config + status endpoints
- [ ] Add Quota middleware to API
- [ ] Add plugin cache integration

### Docs & Testing

- [ ] Update docs/README.md (add Beacon section)
- [ ] Run full test suite
- [ ] Confirm API doc coverage
- [ ] Validate performance targets

---

## Conclusion

The Beacon Portal is **architecturally complete** and **production-ready** at the design level. The remaining work is primarily **integration, wiring, and hardware validation**.

This foundation can be integrated into Wizard in phases without risk to Core or App, maintaining uDOS's offline-first principles.

---

**Status:** ✅ Ready for Integration
**Owner:** uDOS Engineering
**Review:** Pending

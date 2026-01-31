---
uid: udos-wiki-beacon-20260125100000-UTC-L300AB02
title: uDOS Beacon Portal Protocol
tags: [wiki, spec, networking]
status: living
updated: 2026-01-25
spec: wiki_spec_obsidian.md
---

# uDOS Beacon Portal Protocol

**Version:** 1.0.0  
**Status:** Specification  
**Last Updated:** 2026-01-25

## Purpose

A uDOS Beacon is a minimal Wi‑Fi infrastructure node whose sole function is to announce presence and route nearby users to a uDOS Wizard Server. It is intentionally dumb, replaceable, and resilient to failure.

**Core motto:** Beacon announces; Wizard decides.

**Long-range extension (Wizard-only):**

- Keep Beacon as the human portal (Wi‑Fi 2.4 GHz).
- Add **RadioLink (LoRa/MeshCore)** as an optional Wizard module for small, signed packets between Wizards/relays.
- Add **NetLink (WireGuard)** as encrypted WAN fallback.
- Trust stays proximity-first (QR/NFC/physical presence); RadioLink is transport only.

## Design Principles

| Principle                  | Meaning                                                                   |
| -------------------------- | ------------------------------------------------------------------------- |
| **Presence over capacity** | Beacon exists to be found, not to store data                              |
| **Single responsibility**  | Beacon = announce + connect + redirect; Wizard = compute + store + decide |
| **Firmware-agnostic**      | Must function on locked ISP routers with stock firmware                   |
| **Graceful degradation**   | If Wizard Server is offline, beacon still communicates intent             |
| **Local-first**            | No WAN connectivity required or expected                                  |

## Network Topology

```
Client Device
      ↓
   Wi‑Fi (Beacon)
      ↓
   Ethernet
      ↓
Wizard Server (192.168.1.10)
      ↓
Local services (Tombs, Crypts, APIs)
```

## Wireless Configuration

### SSID (Beacon Identity)

**Rules:**

- Maximum 32 bytes
- Must begin with `uDOS`
- Remains stable across reboots

**Recommended examples:**

```
uDOS-beacon
uDOS-wizard
uDOS@local
uDOS:v1
uDOS#A94F
```

**⚠️ SSID is your only truly public channel.** All system meaning must survive if stored only here.

### Authentication

Because some proprietary routers do not allow open Wi-Fi:

**Standard:** WPA2-PSK (or WPA3 if forced)

**Passphrase:** `knockknock`

**Rationale:**

- Memorable
- Symbolic
- Low friction
- Consistent across deployments
- **Not a security boundary**—proximity is the trust factor

## Captive Portal Behavior

### Primary Flow (Wizard Server Online)

1. Device connects to beacon Wi-Fi
2. Router intercepts HTTP traffic
3. User is redirected to: `http://wizard.local`
4. Fallback IP: `http://192.168.1.10`
5. Portal page served by **Wizard Server**, not router
6. User receives full uDOS interface

### Offline Mode (Wizard Server Down)

Router displays minimal static message (if supported by firmware):

**Guaranteed channel:** SSID only (32 bytes)

**Optional channel:** Captive portal text (200–1,000 bytes)

**Recommended offline message:**

```
uDOS Beacon

Wizard Server is currently offline.
This node provides local access only.
Please return later or consult the steward.

— uDOS
```

**Approx. size:** ~150 bytes (well within limits)

## Data Capacity Summary

| Channel                       | Capacity         | Content                  |
| ----------------------------- | ---------------- | ------------------------ |
| SSID (pre-connect)            | ≤ 32 bytes       | Network identity         |
| Captive portal (if supported) | ~200–1,000 bytes | Offline message          |
| Router description            | ~64–256 bytes    | Version / hash / contact |

**Key insight:** The beacon must never depend on internal storage. All meaning must fit in broadcast channels.

## IP & Routing

**Beacon router:**

- Acts as DHCP server (assigns 192.168.1.x)
- May provide default gateway (optional)
- WAN interface disconnected or disabled

**Wizard Server:**

- Static IP: `192.168.1.10`
- Hostname: `wizard.local` (mDNS)
- Services: HTTP (80), optional HTTPS (443)
- Hosts: Tombs, Crypts, APIs, MeshCore

## Security Model

### Trust Establishment

1. **Proximity is primary:** Physical co-location is the initial trust signal.
2. **SSID overlap check:** Users can verify both beacons are "in the room."
3. **Passphrase confirmation:** `knockknock` is memorized and shared in-person.
4. **Beacon evidence:** SSID list serves as proof of co-location.

### Confidentiality & Integrity

- **Beacon provides no confidentiality guarantee.**
- **All meaningful security lives on the Wizard Server** (via TLS, OAuth, etc.).
- **Encryption in flight:** HTTP auto-upgrades to HTTPS on Wizard.

### Non-Goals

The beacon intentionally does **not**:

- Store archives
- Accept uploads
- Run MeshCore (that's the Wizard's job)
- Maintain logs
- Provide internet access
- Enforce authentication beyond WPA

## Replaceability

A uDOS Beacon is considered valid if:

✅ SSID matches spec  
✅ WPA key is correct (`knockknock`)  
✅ Redirect target is reachable

**Hardware replacement must not affect system identity.**

Example: If your beacon router fails, you can replace it with any standard consumer router, configure the same SSID + passphrase + Wizard IP, and the network is restored.

## Beacon Router Setup (Common Brands)

### Ubiquiti EdgeRouter X

1. SSH into `192.168.1.1`
2. Configure Wi-Fi SSID: `uDOS-beacon`
3. Set WPA2-PSK: `knockknock`
4. Disable WAN
5. Set DHCP pool: `192.168.1.100–192.168.1.200`
6. Configure captive portal (if supported) via EdgeOS admin panel

### TP-Link TL-WR841N

1. Web admin: `192.168.0.1` (default credentials)
2. Go to **Wireless** → **Basic Settings**
3. Set SSID: `uDOS-beacon`
4. Set Security: **WPA2-PSK**
5. Set password: `knockknock`
6. Disable WAN/Internet
7. Restart router

### OpenWrt-Flashed Router (Recommended)

1. SSH into router
2. Edit `/etc/config/wireless`:
   ```
   config wifi-iface
       option ssid 'uDOS-beacon'
       option encryption 'psk2'
       option key 'knockknock'
   ```
3. Edit `/etc/config/network`:
   ```
   config interface 'lan'
       option gateway '192.168.1.10'
       option dns '8.8.8.8'
   ```
4. Restart networking: `service network restart`

## Versioning & Evolution

**Current version:** uDOS Beacon Spec v1.0.0

**Future versions may standardize:**

- Captive portal grammar (JSON schema)
- SSID encoding schemes (metadata embedding)
- Beacon → MeshCore discovery
- Multi-Wizard routing
- QR-based setup tokens

---

## Canonical Summary

> A uDOS Beacon is a physical invitation.  
> It does not speak.  
> It introduces you to the one who will.

---

**Status:** Specification v1.0.0 ready for deployment  
**Maintenance:** See [BEACON-VPN-TUNNEL.md](BEACON-VPN-TUNNEL.md) for internet-resilient peering.

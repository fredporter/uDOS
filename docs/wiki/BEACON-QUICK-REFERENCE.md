# Beacon Portal Quick Reference

**Version:** 1.0.0  
**Status:** Implementation Guide  
**Last Updated:** 2026-01-25

## What is a Beacon?

A **beacon** is a WiFi router running Alpine Linux + uDOS that enables local mesh networking and optional internet access via Wizard Server.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Beacon Node** | WiFi router announcing `uDOS-*` SSID |
| **WiFi Passphrase** | `knockknock` (default, memorable) |
| **VPN Tunnel** | WireGuard connection to Wizard (optional) |
| **Device Quota** | Monthly cloud budget ($5–$10) |
| **Plugin Cache** | Local copies of packages (faster download) |
| **MeshCore** | P2P network overlay (device-to-device) |

## Two Modes

### Private-Home
- ✅ Personal WiFi (like home WiFi)
- ✅ Devices trust each other
- ✅ Optional upstream router
- ✅ File sharing enabled
- **Use:** Home, small office

### Public-Secure
- ✅ Shared WiFi (like coffee shop)
- ✅ Devices completely isolated
- ✅ Captive portal registration
- ✅ No file sharing
- **Use:** Office, workspace, events

## Quick Setup

### 1. Get Hardware

**Budget ($30–$60):**
- TP-Link TL-WR841N
- Raspberry Pi 4

**Professional ($100–$300):**
- Ubiquiti EdgeRouter X
- ASUS RT-AX88U

### 2. Flash Alpine Linux

```bash
# Download Alpine ISO
curl -O https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/alpine-standard-latest-x86_64.iso

# Write to USB (macOS)
diskutil unmountDisk /dev/diskX
sudo dd if=alpine-*.iso of=/dev/rdiskX bs=1m
diskutil ejectDisk /dev/diskX

# Boot from USB and install
# Answer prompts:
#   Choose keyboard layout
#   Set hostname: beacon-home
#   Setup networking: DHCP
#   Timezone: UTC (or your TZ)
#   Set root password
#   Disk: sda (or whatever)
#   Erase: y
#   Reboot
```

### 3. Configure WiFi

```bash
# SSH into beacon
ssh root@192.168.1.1

# Install WiFi packages
apk add hostapd dnsmasq wpa_supplicant

# Create WiFi config
cat > /etc/hostapd/hostapd.conf << 'EOF'
interface=wlan0
ssid=uDOS-beacon
hw_mode=g
channel=6
wpa=2
wpa_passphrase=knockknock
wpa_key_mgmt=WPA-PSK
EOF

# Start WiFi
hostapd -d /etc/hostapd/hostapd.conf &
```

### 4. Enable DHCP

```bash
cat > /etc/dnsmasq.conf << 'EOF'
interface=wlan0
dhcp-range=192.168.100.50,192.168.100.150,12h
EOF

dnsmasq
```

### 5. Install uDOS

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
pip install -e .
./bin/start_udos.sh

# Inside uDOS:
> BEACON REGISTER beacon-home
> BEACON VPN TOGGLE on
```

## Common Commands

### View Beacon Status

```bash
# From any device on mesh:
BEACON STATUS beacon-home-01

# Output:
#  Status: online
#  Devices: 3 connected
#  WiFi: uDOS-beacon
#  VPN: active
#  Services: [dns, dhcp, http, meshcore]
```

### Check Cloud Budget

```bash
QUOTA CHECK

# Output:
#  Device: mobile-a1b2c3
#  Budget: $5.00/month
#  Spent: $2.45
#  Remaining: $2.55
#  Requests: 320
#  Expires: Feb 25
```

### Manage VPN Tunnel

```bash
# Enable tunnel to Wizard
TUNNEL ENABLE beacon-home-01

# Check tunnel health
TUNNEL STATUS tunnel-xyz

# Disable tunnel (stays offline)
TUNNEL DISABLE tunnel-xyz
```

### List Hardware

```bash
BEACON DEVICES

# Output:
#  TP-Link TL-WR841N
#    Price: $30
#    WiFi: 2.4GHz
#    Status: ✓ Verified
#
#  Ubiquiti EdgeRouter X
#    Price: $150
#    WiFi: 2.4GHz + 5GHz
#    Status: ✓ Verified
```

## API Examples

### Configure Beacon

```bash
curl -X POST http://localhost:8765/api/v1/beacon/configure \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "mode": "private-home",
    "ssid": "MyNetwork",
    "band": "both",
    "security": "wpa3",
    "passphrase": "knockknock",
    "vpn_tunnel": true,
    "cloud_enabled": true
  }'
```

### Get Hardware Setup Guide

```bash
curl http://localhost:8765/api/v1/beacon/setup-hardware \
  -d '{"hardware": "tplink-wr841n"}' \
  -H "Content-Type: application/json"
```

### Check Device Quota

```bash
curl http://localhost:8765/api/v1/beacon/devices/mobile-a1b2c3/quota \
  -H "Authorization: Bearer $TOKEN"
```

### Get Recommended Routers

```bash
curl http://localhost:8765/api/v1/beacon/devices?cost_tier=budget
```

## Troubleshooting

### WiFi Not Broadcasting

```bash
# Check if hostapd is running
ps aux | grep hostapd

# Restart WiFi
hostapd -d /etc/hostapd/hostapd.conf &

# Check interface is up
ip link show wlan0
```

### Devices Can't Connect

```bash
# Verify SSID
hostapd_cli -p /var/run/hostapd status

# Check WPA key
grep wpa_passphrase /etc/hostapd/hostapd.conf

# Default: knockknock
```

### VPN Tunnel Down

```bash
# Check if WireGuard is running
wg show

# Bring up tunnel
wg-quick up wizard

# Check handshake
wg show wizard
```

### Can't Reach Wizard

```bash
# Ping Wizard endpoint
ping wizard.udos.cloud

# Check routing
route -n

# Verify tunnel IP
ip addr show wg0
```

## Quota Management

### Monthly Reset

Quotas automatically reset on the **first day of each month** (00:00 UTC).

**Manual reset:**
```bash
QUOTA RESET [device-id]
```

### Add Emergency Funds

```bash
curl -X POST http://localhost:8765/api/v1/beacon/devices/mobile-a1b2c3/quota/add-funds \
  -d '{"amount_usd": 10.0}' \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

## Plugin Caching

### Pre-Cache Plugin

```bash
# Cache plugin on beacon for faster distribution
PLUGIN CACHE my-plugin

# List cached plugins
PLUGIN LIST --location beacon
```

### Check Cache Size

```bash
BEACON STATUS beacon-home-01
# Shows: Plugin cache: 245 MB (3 plugins)
```

## Security Tips

### WiFi Passphrase

- Default: `knockknock` (memorable, not a security boundary)
- Optional: Change to custom passphrase
- Proximity is the primary trust factor

```bash
# Change passphrase
BEACON CONFIGURE uDOS-beacon --passphrase="MySecurePassword"
```

### WireGuard Keys

- Generated during tunnel setup
- Stored locally (never transmitted)
- Rotate annually or on compromise

```bash
# Generate new keys
TUNNEL REGENERATE-KEYS tunnel-xyz
```

### Device Isolation

In **Public-Secure mode**, devices are automatically isolated:
- Can't see each other's files
- Can't access each other's services
- Rate-limited per device

## Performance

| Operation | Time |
|-----------|------|
| WiFi connection | 2–5 seconds |
| DHCP assignment | 1–3 seconds |
| Tunnel setup | 1–2 seconds |
| Quota check | < 100 ms |
| Plugin download (via tunnel) | 5–30 seconds |
| Plugin cache hit | 1–3 seconds |

## Offline Mode

If tunnel is down:

- ✅ WiFi still works
- ✅ Local mesh still works
- ✅ Cached plugins still available
- ✅ Local APIs still accessible
- ❌ Cloud features unavailable

**Automatic retry:** Tunnel reconnects every 30 seconds

## References

- [BEACON-PORTAL.md](../../docs/wiki/BEACON-PORTAL.md) — Full architecture
- [BEACON-VPN-TUNNEL.md](../../docs/wiki/BEACON-VPN-TUNNEL.md) — Tunnel spec
- [SONIC-SCREWDRIVER.md](../../docs/wiki/SONIC-SCREWDRIVER.md) — Hardware DB
- [BEACON-IMPLEMENTATION.md](./BEACON-IMPLEMENTATION.md) — Dev guide

## Support

**Having issues?**

1. Check logs: `tail -f /memory/logs/wizard-server-YYYY-MM-DD.log`
2. Run diagnostics: `BEACON DIAGNOSTICS beacon-home-01`
3. Report bug: `https://github.com/fredporter/uDOS/issues`

---

**Last Updated:** 2026-01-25  
**Version:** v1.0.0  
**Status:** Ready for Deployment

## Wizard Networking Standard (v1.0.7)

**Goal:** Add long-range radio as an optional transport for Wizards without changing the Wi-Fi Beacon portal flow.

### Clean Split

- **Wi-Fi Beacon (2.4 GHz):** Human portal. Discovery, connect, redirect. Short-range by design.
- **RadioLink (LoRa / MeshCore):** Long-range, low-bandwidth packet relay between Wizards/relays. Small signed payloads only.
- **NetLink (WireGuard):** Encrypted fallback over internet/WWW when available.

### Why RadioLink

- Wi-Fi stability is range-limited; shrinking payloads does not increase range.
- LoRa/packet radio trades bandwidth for reach and resilience; multi-hop supported via MeshCore.
- Payload fit: small text/Markdown packets are ideal for RadioLink.

### Hardware Options

- **Option A: USB LoRa modem per Wizard** (simple, uDOS-friendly)
  - USB/serial or SPI HAT radio
  - Tiny radio daemon (MeshCore node) + uDOS packet sync service
- **Option B: Dedicated relay nodes** (best coverage)
  - 1–2 always-on relays at elevation
  - Wizards talk to relays; relays forward
- **Option C: Co-located Beacon + LoRa** (later)
  - Same box, separate roles: router broadcasts SSID; adjacent LoRa node forwards packets

### Trust and Transport

- Trust is proximity-first: initial pairing must be local (QR/NFC/physical sight) before radio routing is allowed.
- Transport is swappable: RadioLink for long range, NetLink for WAN, Beacon for local.
- Packet format: content-addressed, signed, replay-safe; no auto-peering.

### Positioning

- MeshCore vs Meshtastic: choose MeshCore when you want managed relays, opt-in trust, and lightweight routing; Meshtastic when you want ecosystem UX.

### uDOS Recommendation

1. Keep the Wi-Fi Beacon spec unchanged (ritual + portal).
2. Add **RadioLink** as optional Wizard module for long-range packets.
3. Add **NetLink (WireGuard)** as encrypted fallback.
4. Use one tiny, signed packet format across transports.

If you have target distance and line-of-sight constraints, we can map the minimal relay topology (Wizards + relays) to meet it.

---
uid: udos-wiki-beacon-20260125140000-UTC-L300AB04
title: uDOS Beacon VPN Tunnel Protocol
tags: [wiki, spec, networking]
status: living
updated: 2026-01-25
spec: wiki_spec_obsidian.md
---

# uDOS Beacon VPN Tunnel Protocol

**Version:** 1.0.0  
**Status:** Specification  
**Last Updated:** 2026-01-25

## Purpose

Extend uDOS Beacon connectivity beyond local Wi-Fi by introducing **opt-in, cryptographically-secured peering** between Wizard Servers. This allows Wizards to relay packets and share presence over internet links while maintaining end-to-end encryption and proximity-first trust.

**Design:** Beacons introduce; Wizards decide; Wizards relay.

## Core Philosophy

- **No automatic federation:** Peering only happens when two humans intentionally introduce their Wizards.
- **Proximity-first trust:** Initial trust establishment must be rooted in physical co-location.
- **Internet-transparent:** VPN tunnels are a transport; they don't change the security model.

## Phase A: Proximity Verification

Establish initial trust through one of three methods:

### A1: Beacon Overlap (Default, Low Friction)

Users confirm co-location by checking available Wi-Fi networks.

**Flow:**

1. User A: "I see `uDOS-ALPHA` and `uDOS-BRAVO` here"
2. User B: Confirms "I see both too"
3. System: Records proximity evidence
4. Trust: Enabled for pairing

**Evidence:** SSID list hash (proves both were scanning same airspace)

**Friction:** Human confirmation + visual inspection

### A2: Tap-to-Pair (Best UX)

NFC (Near Field Communication) establishes pairing ritual.

**Hardware:** NFC phones or Wizard-integrated NFC readers

**Flow:**

1. User A taps their device to User B's device
2. NFC exchange: Contains one-time pairing token (no sensitive data needed)
3. Both devices record pairing timestamp + location hash
4. Trust: Enabled

**Friction:** Physical touch required (excellent UX, good security)

### A3: QR "Pairing Capsule" (Works Everywhere)

QR code encodes a signed, time-limited introduction.

**Flow:**

1. Wizard A generates QR code (via local web UI)
2. Wizard B scans QR (or user scans with phone and relays)
3. QR contains:
   - Wizard A public key fingerprint
   - Expiry timestamp (e.g., 5 minutes)
   - One-time nonce
   - Optional beacon evidence (SSID list hash)
   - Signature by Wizard A
4. Wizard B verifies signature and expiry
5. Trust: Enabled

**Friction:** Low (phone cameras widely available)

**Capacity:** QR v40 = ~2,953 bytes (well sufficient for pairing token)

## Phase B: Cryptographic Peering

Once Phase A occurs, establish durable, opt-in relationship.

### Key Material

**Each Wizard generates:**

- Long-term identity keypair (Ed25519)
- Public key fingerprint (short form, e.g., 16 hex chars)
- Optional: Device name (e.g., "Alice's Wizard")

### Pairing Exchange

**Wizard A → Wizard B:**

```json
{
  "intro_token": "<base64>",
  "public_key_fingerprint": "a1b2c3d4e5f6g7h8",
  "beacon_evidence": "sha256=<beacon_list_hash>",
  "expiry": "2026-01-25T12:05:00Z",
  "nonce": "<random_32_bytes>",
  "signature": "<ed25519_signature>"
}
```

**Wizard B verifies:**

1. Signature matches Wizard A public key
2. Expiry is in future
3. Nonce is fresh (not replayed)
4. Beacon evidence matches co-location

**Wizard B → Wizard A:**

```json
{
  "acceptance": true,
  "peer_fingerprint": "x9y8z7w6v5u4t3s2",
  "relationship_id": "<uuid>",
  "signature": "<ed25519_signature>"
}
```

**Result:** Durable, mutual trust relationship recorded locally.

## Phase C: Wizard-to-Wizard Tunneling (Optional)

Once peered, Wizards can optionally exchange packets over internet.

### WireGuard Tunnel

**Why WireGuard?**

- Modern, minimal (< 4,000 lines)
- ChaCha20-Poly1305 (fast on all hardware)
- Curve25519 (proven key agreement)
- Built-in key rotation
- Stateless design (easier debugging)

**Setup:**

1. Each Wizard runs WireGuard daemon
2. After peering, exchange WireGuard public keys (separate from identity keys)
3. Establish tunnel: Wizard A ↔ Wizard B (encrypted, authenticated)
4. Route packets through tunnel (optional; can use direct connections)

**Example config:**

```ini
[Interface]
PrivateKey = <curve25519_private>
ListenPort = 51820
Address = 10.0.0.1/32

[Peer]
PublicKey = <peer_curve25519_public>
AllowedIPs = 10.0.0.2/32, 192.168.1.0/24
Endpoint = 192.168.1.20:51820
```

### Packet Relay (Manifest Exchange)

Use small, append-only capsules instead of file transfer.

**Exchange protocol:**

```
Request: "What capsules do you have?"
Response: "I have hashes: [a1, b7, c3, d9]"
Request: "Send me what I'm missing"
Response: "Here are capsules [a1, c3]"
```

**Benefits:**

- Resilient to intermittent links
- Partial transfers recover gracefully
- Works over high-latency internet
- No large files (text + metadata only)

**Example capsule:**

```json
{
  "id": "sha256:a1b2c3d4...",
  "timestamp": "2026-01-25T10:30:00Z",
  "sender": "alice@wizard",
  "subject": "Beacon status update",
  "body": "Status: online. Uptime 7d 3h.",
  "signature": "<ed25519>"
}
```

## Separation of Concerns: Wi-Fi vs. VPN

### Public Beacon Wi-Fi (Local Only)

- **SSID:** Announces presence
- **Passphrase:** `knockknock`
- **Scope:** ~50m (typical consumer router)
- **Purpose:** Local discovery + captive portal redirect

### Private Home Wi-Fi (Optional, Encrypted)

- **SSID:** Your household network (e.g., `Home-Alpha`)
- **Encryption:** WPA3 or strong WPA2
- **Scope:** Your property
- **Purpose:** General internet access, backup connectivity

### Wizard-to-Wizard VPN (Internet, Encrypted)

- **Protocol:** WireGuard
- **Scope:** Global (if internet available)
- **Encryption:** End-to-end (Wizard A ↔ Wizard B, even through relays)
- **Purpose:** Packet relay, metadata minimization, trusted peering

**Key insight:** Treat these as three independent layers. A user can operate any combination:

- Beacon Wi-Fi only (completely local)
- Beacon + home Wi-Fi (local + household internet)
- Beacon + Wizard VPN (local + peer relay)
- All three (layered, maximum resilience)

## Security Guarantees vs. Limitations

### What You Get

✅ **Content confidentiality:** Encrypted end-to-end (even through relays)  
✅ **Integrity:** Packets cannot be tampered with undetected  
✅ **Peer authentication:** You know which Wizard you're talking to  
✅ **Replay protection:** Nonces + timestamps prevent message replay

### What You Don't Get

⚠️ **Metadata privacy:** Someone with network access can see "Wizard A talked to Wizard B at time X"  
⚠️ **Quantum resistance:** Ed25519 is not quantum-secure (future consideration)  
⚠️ **Internet safety:** ISPs/governments can still see you're using a VPN (though not contents)

### uDOS Stance

> **Payload privacy guaranteed; metadata minimized where practical.**

We do not promise "complete invisibility." We promise honest, cryptographic communication between peers.

## Small Packet Transfer Over Beacons (Text + Metadata)

### Design

- **Content:** Markdown, JSON, small binary (< 100 KB)
- **Not:** Videos, large archives, media files
- **Format:** Append-only capsules (content-addressed by hash)
- **Transport:** Beacon relay or VPN tunnel

### Example Workflow

1. Wizard A creates capsule: "Meeting notes"
2. Wizard B (co-located on beacon) requests capsule
3. Beacon relay delivers capsule (local, no internet needed)
4. Later, Wizard B can relay same capsule to Wizard C via VPN

### Capsule Structure

```json
{
  "id": "sha256:hash",
  "timestamp": "2026-01-25T10:30:00Z",
  "type": "text/markdown",
  "size_bytes": 3472,
  "sender_fingerprint": "a1b2c3d4e5f6g7h8",
  "payload": "# Meeting Notes\n...",
  "signature": "<ed25519>"
}
```

**Size:** Typically 1–100 KB  
**Delivery:** Via HTTP GET/POST or direct socket  
**Resilience:** Manifest exchange ensures missing capsules are detected and re-delivered

## QR & NFC Capacity

### QR Codes

- **Standard QR v40 @ low error correction:** 2,953 bytes
- **Use case:** Pairing tokens, not content
- **Recommended payload:** Signed capability URL
  ```
  https://relay/claim?token=<expires_5min_cap>&peer=<fingerprint>
  ```

### NFC Tags

- **Common cheap tags (NTAG21x):** 100–300 bytes
- **Higher-end tags:** 1–8 KB
- **Use case:** Local pairing, not bulk transfer
- **Recommended:** Store a pointer + key material, not the content itself

### Web Links in QR (Secure Pattern)

✅ **QR contains:** Time-limited, signed capability URL  
✅ **URL expires:** 5 minutes  
✅ **Single-use:** Token can't be replayed  
✅ **Bound to peer:** Can only be claimed by expected Wizard

Example:

```
https://relay/claim?cap=<signed_token>&exp=2026-01-25T12:05Z
```

Even if someone photographs the QR later, it's worthless (expired + single-use).

---

## Checklist: Deploying Beacon Peering

- [ ] Each Wizard has Ed25519 identity keypair
- [ ] Pairing protocol implemented (Phase A + B)
- [ ] WireGuard daemon running (optional, for internet relay)
- [ ] Capsule manifest exchange working
- [ ] Offline fallback tested (Wizard down, beacon still announces)
- [ ] Security audit of key material storage
- [ ] Documentation for users (how to pair manually)

---

## References

- [Beacon Portal Protocol](wiki-candidates/BEACON-PORTAL.md) — Local Wi-Fi discovery
- [WireGuard Documentation](https://www.wireguard.com/)
- [Ed25519 / Curve25519](https://cr.yp.to/ecdh.html)
- [QR Code Specification](https://www.qr-server.com/)
- [AGENTS.md](../../AGENTS.md) — uDOS architecture

---

**Status:** Specification v1.0.0 ready for implementation  
**Next Steps:** Implement pairing protocol in Wizard Server, scaffold WireGuard integration, test capsule relay over slow links

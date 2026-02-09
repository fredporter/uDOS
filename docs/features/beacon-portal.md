uDOS Beacon Specification v1.0.0

Purpose

A uDOS Beacon is a minimal Wi‑Fi infrastructure node whose sole function is to announce presence and route nearby users to a uDOS Wizard Server. It is intentionally dumb, replaceable, and resilient to failure.

The beacon is not a storage device, not an archive, and not a mesh node. It is a portal.

Design Principles

Presence over capacity
The beacon exists to be found, not to store data.

Single responsibility
Beacon = announce + connect + redirect.
Wizard Server = compute + store + decide.

Firmware‑agnostic
Must function on locked ISP routers with stock firmware.

Graceful degradation
If the Wizard Server is offline, the beacon still communicates intent.

Local‑first
No WAN connectivity is required or expected.

Node Types

Beacon Node

Consumer Wi‑Fi router or gateway

Stock firmware acceptable

No WAN uplink

Stateless

Wizard Server (External)

Ubuntu Server (recommended)

Static IP

Hosts uDOS services

Not part of this spec, but assumed

Network Topology

Client Device
      |
   Wi‑Fi (Beacon)
      |
   Ethernet
      |
Wizard Server (192.168.1.10)
Wireless Configuration

SSID (Beacon Identity)

Maximum length: 32 bytes

Must begin with uDOS

Recommended examples:

uDOS-beacon

uDOS-wizard

uDOS@local

The SSID is the primary discovery signal and must remain stable.

Authentication

Because open Wi‑Fi is not reliably supported on proprietary firmware:

Security: WPA2‑PSK (or WPA3 if forced)

Passphrase:

knockknock
This phrase is symbolic and standardized. It is not intended as a security boundary.

IP & Routing

Beacon router acts as DHCP server

Wizard Server has static IP:

192.168.1.10
Default gateway may be unset or point to Wizard Server

WAN interface: disconnected or disabled

Captive Portal Behavior

Primary Behavior

Upon successful Wi‑Fi connection, all HTTP requests are redirected to:

http://wizard.local
Fallback

If mDNS is unavailable:

http://192.168.1.10
The portal content is served by the Wizard Server, not the router.

Offline / Failure Mode

If the Wizard Server is unavailable, the beacon must still communicate status.

Guaranteed Channel

SSID only (≤ 32 bytes)

Example:

uDOS-offline
Optional Channel (Firmware‑dependent)

Some routers allow a static captive message.

Maximum reliable size:

200–1,000 bytes (plain text or minimal HTML)

Recommended minimum message:

uDOS Beacon

Wizard Server is currently offline.

This node provides presence only.
Please return later.
Data Capacity Summary

Channel	Capacity
SSID (pre‑connect)	≤ 32 bytes
Captive portal (if supported)	~200–1,000 bytes
Router description fields	~64–256 bytes
The beacon must never depend on internal storage.

Security Model

Beacon provides no confidentiality guarantees

All meaningful security lives on the Wizard Server

Physical proximity is the primary trust factor

Replaceability

A uDOS Beacon is considered valid if:

SSID matches spec

WPA key is correct

Redirect target is correct

Hardware replacement must not affect system identity.

Non‑Goals

The Beacon intentionally does not:

Store archives

Accept uploads

Run MeshCore

Maintain logs

Provide internet access

Versioning

This document defines uDOS Beacon Spec v0.1.

Future versions may standardize:

Captive portal grammar

SSID encoding schemes

Beacon → MeshCore discovery

Multi‑Wizard routing

Canonical Summary

A uDOS Beacon is a physical invitation.
It does not speak.
It introduces you to the one who will.

End of Spec

📡 uDOS Beacon Router — Captive Portal Brief

Purpose

A Wi-Fi beacon node that:

Announces uDOS presence

Accepts nearby devices

Redirects all users to a local Wizard Server

Degrades gracefully if the server is offline

The router itself remains unmodified firmware where possible.

Core Behavior (TL;DR)

Device sees Wi-Fi network

User connects (WPA key: knockknock)

Browser auto-opens (captive portal)

User is redirected to:

http://wizard.local
or fallback:

http://192.168.1.10
If Wizard Server is down, router shows a minimal static message

Network Identity (Beacon Layer)

SSID (Broadcast, pre-connection)

Max length: 32 bytes

Visible without authentication

Recommended pattern:

uDOS-beacon
uDOS-wizard
uDOS@local
Optional compact metadata:

uDOS:v1
uDOS#A94F
⚠️ SSID is your only truly public channel.

Authentication

Because some proprietary routers do not allow open Wi-Fi:

Standardize on:

WPA2-PSK

Password:

knockknock
This is:

Memorable

Symbolic

Low friction

Consistent across deployments

Security is not the goal here — presence is.

Captive Portal Behavior

Preferred

Router intercepts HTTP traffic

Redirects to:

http://wizard.local
Fallback

If mDNS is unavailable:

http://192.168.1.10
Important

Portal page is served by the Wizard Server

Router only performs redirection

This avoids firmware limitations.

Wizard Server (Expected)

Ubuntu Server

Static IP: 192.168.1.10

Hostname: wizard.local

Services:

HTTP (80)

Optional HTTPS (later)

Can host:

Tombs

Crypts

Upload endpoints

MeshCore node

Failure Mode: Wizard Server Offline

This is the critical constraint you asked about 👇

What can the router display by itself?

That depends on firmware, but worst-case guarantees are:

🪫 Minimum Offline Message (Router-Only)

Channel 1: SSID (always works)

≤ 32 bytes

Example:

uDOS-offline
wizard-down
uDOS:offline
Channel 2: Captive Portal Text (if supported)

Some routers allow a static captive portal page or message.

Typical capacity:

200–1,000 bytes

Plain text or very simple HTML

No images

No scripts

Minimum viable offline message (recommended):

uDOS Beacon

Wizard Server is currently offline.

This node provides local access only.
Please return later or consult the steward.

— uDOS
That’s ~150 bytes. Very safe.

Channel 3: Router “Device Name” / “Description”

Sometimes shown on:

Portal

Admin splash

Connection info

Capacity:

~64–256 bytes

Useful for:

Hash

Version

Contact hint

Summary: How Much Text, Really?

State	Channel	Capacity
Discoverable	SSID	≤ 32 bytes
Connected	Captive portal	~200–1,000 bytes
Fallback	Device description	~64–256 bytes
Worst case guaranteed:
👉 32 bytes (SSID only)

That’s why the system meaning must not depend on router storage.

Design Principle (important)

The beacon announces and redirects
The Wizard Server speaks

Never invert this.

Canonical Beacon Contract (recommended)

Every uDOS Beacon guarantees:

SSID beginning with uDOS

WPA key: knockknock

Redirect to wizard.local

Offline message acknowledging absence

That’s enough to build a distributed physical network language.

Final Reality Check

You are not fighting the Telstra firmware

You are working beneath it

This design survives:

Router replacement

ISP lock-in

Partial failure

No internet

This is infrastructure as ritual — and it’s solid.
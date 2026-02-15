# uDOS VM and Remote Desktop Architecture

## Apple Silicon (UTM Free) + Dedicated Physical Nodes

---

# 1. Purpose

This document defines the unified architecture for:

- Dedicated physical machines (production nodes)
- Remote desktop access between nodes
- Full virtual machine emulation using UTM (Apple Silicon only)
- Mirror provisioning between physical and virtual infrastructure
- Clean separation of control, gaming, server, and core layers

This follows uDOS layered design principles:

- Control Layer
- Wizard Server Layer
- Core Runtime Layer
- Gaming / Compatibility Layer

---

# 2. High-Level Architecture

## 2.1 Control Plane

The Apple Silicon Mac acts as:

- Primary Control Node
- VM Host (UTM)
- Orchestration Console
- Remote Access Client

It does NOT act as production infrastructure.

---

# 3. Physical Infrastructure (Production Nodes)

```
                ┌──────────────┐
                │   Router     │
                └──────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
      Mac         Windows Box     Wizard Server
   (Control)       (Gaming)        (Ubuntu)
                                      │
                                   Alpine Core
```

## 3.1 Windows Gaming Node

Purpose:

- Native GPU performance
- Gaming layer
- Compatibility testing

Configuration:

- Windows 10/11
- Remote Desktop enabled
- Static IP or DHCP reservation
- LAN-only firewall rules
- Dedicated non-admin RDP user

---

## 3.2 Ubuntu Wizard Server

Purpose:

- API layer
- Services
- Full Python + Node runtime
- Docker (optional)

Configuration:

- Ubuntu Server (LTS)
- OpenSSH enabled
- Optional Docker
- Full venv environment allowed

---

## 3.3 Alpine uDOS Core Node

Purpose:

- TUI runtime
- Stdlib-only Python core
- Lightweight execution environment

Configuration:

- Alpine Linux (minimal)
- OpenSSH
- Python (no venv for core runtime)

---

# 4. Virtual Infrastructure (UTM on Apple Silicon)

All VMs must use ARM64 images.

## 4.1 Alpine ARM VM

Specs:

- 2 CPU cores
- 2GB RAM
- 20GB disk
- VirtIO network

Purpose:

- Core testing
- Cage Wayland + minimal compositor testing
- uDOS TUI validation

---

## 4.2 Ubuntu ARM VM

Specs:

- 4 CPU cores
- 4–8GB RAM
- 40GB disk

Purpose:

- Wizard server mirror
- API testing
- Dev integration

---

## 4.3 Windows 11 ARM VM

Specs:

- 4 CPU cores minimum
- 8GB RAM minimum
- 64GB disk

Purpose:

- Compatibility
- RDP testing
- Admin scripting

Note: Windows ARM is not for gaming. Gaming remains on physical hardware.

---

# 5. Networking Strategy

## 5.1 UTM NAT Mode (Default)

- VMs accessible only from Mac
- Safe and isolated
- Recommended for development

## 5.2 UTM Bridged Mode (Advanced)

- VMs receive LAN IPs
- Can be accessed by other machines
- Simulates production network

Recommended: Use NAT for dev, Bridged for infrastructure simulation.

---

# 6. Remote Access Standards

## 6.1 Windows Remote Desktop

Mac Client:

- Microsoft Remote Desktop (App Store)

Windows Configuration:

- Enable Remote Desktop
- Enable Network Level Authentication
- Restrict to LAN
- Use strong local credentials

Never expose RDP directly to the internet.

---

## 6.2 Linux Remote Access

Standard:

- SSH only

Optional:

- xrdp for GUI testing (not recommended for production)

Example:

```
ssh user@wizard.local
```

Use mDNS where possible:

- wizard.local
- core.local
- winbox.local

---

# 7. Naming Convention

Physical Nodes:

- wizard.local
- core.local
- winbox.local

Virtual Nodes:

- wizard-vm.local
- core-vm.local
- winbox-vm.local

This enables script-based swapping.

---

# 8. Provisioning Model

All nodes (physical + virtual) must be provisioned via identical scripts.

Structure:

```
/provision/
    wizard.sh
    core.sh
    windows.ps1
```

Goals:

- Infrastructure as code
- No configuration drift
- Fast rebuild capability
- Lab mirrors production

---

# 9. Security Model

Rules:

- No RDP exposed to WAN
- No direct SSH exposed publicly
- Use VPN (WireGuard / Tailscale) if remote access required
- Use non-root SSH accounts
- Enforce firewall segmentation if possible

Optional:

- VLAN separation for Wizard Server
- Windows isolated from server tier

---

# 10. Operational Modes

## Mode A – Dev Lab Only

- All VMs in UTM
- No physical servers required
- Portable uDOS lab

## Mode B – Hybrid Production (Recommended)

- Physical Windows (gaming)
- Physical Ubuntu (wizard)
- Physical Alpine (core)
- UTM mirrors for dev

## Mode C – Future Hypervisor Migration

- Replace UTM with Proxmox node
- Mac remains control plane
- Same provisioning scripts reused

---

# 11. Strategic Outcome

This architecture provides:

- Symmetry between real and virtual
- Offline-first capability
- Gaming isolation
- Clean layered separation
- Infrastructure reproducibility
- Migration readiness

Mac remains the orchestration console. Production remains hardware-based. Virtual remains reproducible.

This aligns with uDOS philosophy: Minimal core. Modular layers. Controlled networking. No unnecessary cloud exposure.

---

# 12. ASCII Topology Diagrams (80x30-Friendly)

## 12.1 Hybrid Production (Recommended)

```
+------------------------------------------------------------------------------+
|                                  HOME LAN                                    |
|                                                                              |
|  +------------------+        +------------------+        +----------------+  |
|  |  Mac (Control)   |        | Windows (Gaming) |        | Ubuntu (Wizard)|  |
|  |  - UTM host       |--RDP-->| - Native GPU     |--LAN-->| - API/Services |  |
|  |  - RDP + SSH      |        | - RDP enabled    |        | - SSH enabled  |  |
|  +--------+---------+        +------------------+        +--------+-------+  |
|           |                                                        |          |
|           | SSH                                                    | SSH      |
|           v                                                        v          |
|  +------------------+                                     +----------------+  |
|  | Alpine (Core)    |                                     | (Optional)     |  |
|  | - TUI runtime     |                                     | VLAN / Seg     |  |
|  | - SSH enabled     |                                     | (Wizard tier)  |  |
|  +------------------+                                     +----------------+  |
|                                                                              |
+------------------------------------------------------------------------------+
```

## 12.2 UTM Dev Lab (NAT Mode)

```
+------------------------------------------------------------------------------+
|                                 Mac (Apple Silicon)                          |
|                                                                              |
|  +------------------------------ UTM (NAT) --------------------------------+ |
|  |                                                                          | |
|  |  +------------------+  +------------------+  +------------------------+ | |
|  |  | core-vm (Alpine) |  | wizard-vm (Ubnt) |  | winbox-vm (Win 11 ARM) | | |
|  |  | SSH only         |  | SSH only         |  | RDP enabled            | | |
|  |  +--------+---------+  +--------+---------+  +-----------+------------+ | |
|  |           |                     |                        |              | |
|  +-----------+---------------------+------------------------+--------------+ |
|              |                     |                        |                |
|              | SSH                 | SSH                    | RDP            |
|              v                     v                        v                |
|          (Mac Terminal)        (Mac Terminal)      (MS Remote Desktop)        |
|                                                                              |
+------------------------------------------------------------------------------+
```

## 12.3 UTM Infra Simulation (Bridged Mode)

```
+------------------------------------------------------------------------------+
|                           Home LAN (Bridged VMs)                              |
|                                                                              |
|  +------------------+      +------------------+      +---------------------+ |
|  | Mac (Control)    |      | wizard-vm.local  |      | core-vm.local       | |
|  | - RDP + SSH      |      | - LAN IP         |      | - LAN IP            | |
|  +--------+---------+      +------------------+      +---------------------+ |
|           |                                                     +----------+ |
|           | RDP                                                 | winbox-  | |
|           v                                                     | vm.local | |
|    +------------------+                                        | - LAN IP | |
|    | winbox.local     |                                        | - RDP    | |
|    | (Physical Win)   |                                        +----------+ |
|    +------------------+                                                   | |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

# 13. Provisioning Checklist (Physical + UTM)

Goal: any node can be rebuilt from scratch using the same scripts.

## 13.1 Common Baseline (All Nodes)

- [ ] Hostname set (matches naming convention)
- [ ] Timezone set (Australia/Brisbane)
- [ ] Local admin created (separate from daily account)
- [ ] Updates applied (then freeze policy decided)
- [ ] Firewall enabled (LAN rules only)
- [ ] SSH keys generated (where applicable)
- [ ] Password login disabled for SSH (Linux) once keys work

## 13.2 Alpine Core Node (Physical + core-vm)

- [ ] Install Alpine (aarch64 for UTM)
- [ ] Enable OpenSSH
- [ ] Install Python (core stdlib only)
- [ ] Configure uDOS core runtime paths
- [ ] Confirm TUI grid rendering smoke test
- [ ] Confirm SSH reachability via mDNS / IP

## 13.3 Ubuntu Wizard Node (Physical + wizard-vm)

- [ ] Install Ubuntu Server (ARM for UTM)
- [ ] Enable OpenSSH
- [ ] Install Node/TS runtime
- [ ] Install Python (wizard venv allowed)
- [ ] Optional: install Docker
- [ ] Configure wizard services: ports bound to LAN only
- [ ] Confirm API healthcheck + logs

## 13.4 Windows Gaming Node (Physical) + Windows ARM VM (winbox-vm)

- [ ] Enable RDP + NLA
- [ ] Create dedicated RDP user (non-admin)
- [ ] Restrict firewall to LAN subnet
- [ ] Disable unnecessary services + telemetry (policy-dependent)
- [ ] Confirm RDP from Mac
- [ ] Confirm shared folder / clipboard policy (if used)

---

# 14. Sizing Matrix

Use this as a starting point. Adjust based on actual workload.

| Node | Target | CPU | RAM | Disk | Notes |
|---|---|---:|---:|---:|---|
| Mac Control | Host + client | 8+ cores | 16GB+ | 512GB+ | Runs UTM + tools; not production |
| Windows Gaming (Physical) | Gaming layer | 6–16 cores | 16–64GB | 1–2TB | GPU is the real requirement |
| Ubuntu Wizard (Physical) | Services/API | 4–12 cores | 8–32GB | 256GB–2TB | RAM/IO depends on models/services |
| Alpine Core (Physical) | TUI/core | 2–6 cores | 2–8GB | 32–128GB | Keep minimal |
| core-vm (UTM) | Dev mirror | 2 cores | 2GB | 20GB | NAT by default |
| wizard-vm (UTM) | Dev mirror | 4 cores | 4–8GB | 40GB | Bridged when simulating LAN |
| winbox-vm (UTM) | Compatibility | 4 cores | 8GB | 64GB | Not for gaming |

---

# 15. Phase 2 Hypervisor Migration Brief (Proxmox Track)

This section provisions a future path where UTM is replaced by a dedicated hypervisor, while keeping the same provisioning scripts.

## 15.1 Goals

- Move VM hosting off the Mac
- Keep Mac as Control Plane only
- Enable snapshots, templates, backups
- Optional GPU passthrough for Windows VM (if desired)

## 15.2 Target Topology

```
Mac (Control Plane)
  |-- RDP/SSH --> Proxmox (Hypervisor)
                   |-- VM: wizard (Ubuntu)
                   |-- VM: core (Alpine)
                   |-- VM: winbox (Windows)
                   |-- (Optional) LXC services
```

## 15.3 Migration Strategy

1. Keep current /provision scripts unchanged.
2. Export UTM VM disk images (where possible) or rebuild from ISO.
3. Create Proxmox templates:
   - core-template
   - wizard-template
   - winbox-template
4. Apply provisioning scripts post-install.
5. Validate:
   - SSH/RDP connectivity
   - Naming + mDNS strategy
   - Firewall rules + segmentation

## 15.4 When to Migrate

- Mac is resource constrained
- You want always-on wizard services
- You want LAN-accessible dev VMs without keeping Mac awake
- You want central backups and VM lifecycle control

---

END OF SPEC


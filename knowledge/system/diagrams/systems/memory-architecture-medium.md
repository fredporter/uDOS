# uDOS Memory Architecture

**System:** 4-Tier Knowledge Bank
**Tiers:** MEMORY → PRIVATE → SHARED → COMMUNITY
**Purpose:** Hierarchical data storage and sync
**Tier:** Medium (60×40)

---

## Overview

uDOS uses a 4-tier memory architecture for knowledge management. Data flows from fast local memory through encrypted private storage to shared and community networks.

**Performance:** ████████▓▓ **90% Optimized**

---

## Architecture Diagram

### Complete 4-Tier Structure

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    uDOS MEMORY SYSTEM                  ┃
┃                    ═════════════════                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ╔═══════════════════════════════════════════╗
    ║   TIER 1: MEMORY (Fast Local Storage)    ║
    ║   ─────────────────────────────────────   ║
    ║   Speed: ████████████ 100%                ║
    ║   Security: ░░░░░░░░░░░░ None             ║
    ║   Sync: ░░░░░░░░░░░░ No                   ║
    ║   Location: .memory/ (git ignored)        ║
    ╚═══════════════════════════════════════════╝
                      ▼
                   [SAVE]
                      ▼
    ╔═══════════════════════════════════════════╗
    ║   TIER 2: PRIVATE (Encrypted Personal)   ║
    ║   ──────────────────────────────────────  ║
    ║   Speed: ██████████░░ 80%                 ║
    ║   Security: ████████████ 100% (AES-256)   ║
    ║   Sync: ████████░░░░ Local only           ║
    ║   Location: memory/private/ (encrypted)   ║
    ╚═══════════════════════════════════════════╝
                      ▼
                   [SHARE]
                      ▼
    ╔═══════════════════════════════════════════╗
    ║   TIER 3: SHARED (Sync Network)          ║
    ║   ──────────────────────────────────────  ║
    ║   Speed: ████████░░░░ 60%                 ║
    ║   Security: ████████░░░░ 60% (Optional)   ║
    ║   Sync: ████████████ Yes (devices)        ║
    ║   Location: memory/shared/ (syncthing)    ║
    ╚═══════════════════════════════════════════╝
                      ▼
                  [PUBLISH]
                      ▼
    ╔═══════════════════════════════════════════╗
    ║   TIER 4: COMMUNITY (P2P Network)        ║
    ║   ──────────────────────────────────────  ║
    ║   Speed: ██████░░░░░░ 40%                 ║
    ║   Security: ██░░░░░░░░░░ 20% (Public)     ║
    ║   Sync: ████████████ Yes (P2P)            ║
    ║   Location: memory/community/ (IPFS)      ║
    ╚═══════════════════════════════════════════╝
```

---

## Data Flow

### Write Path (Top-Down)

```
┌─────────────┐
│   USER      │
│  Creates    │
│   Data      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  TIER 1: MEMORY                     │
│  ┌───────────────────────────────┐  │
│  │ ░ Fast write                  │  │
│  │ ░ No encryption               │  │
│  │ ░ Temporary storage           │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ [MEMORY SAVE filename private]
               ▼
┌─────────────────────────────────────┐
│  TIER 2: PRIVATE                    │
│  ┌───────────────────────────────┐  │
│  │ ▓ AES-256 encryption          │  │
│  │ ▓ Password protected          │  │
│  │ ▓ Local only                  │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ [PRIVATE SHARE filename]
               ▼
┌─────────────────────────────────────┐
│  TIER 3: SHARED                     │
│  ┌───────────────────────────────┐  │
│  │ ▒ Syncthing sync              │  │
│  │ ▒ Device network              │  │
│  │ ▒ Optional encryption         │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ [SHARED PUBLISH filename]
               ▼
┌─────────────────────────────────────┐
│  TIER 4: COMMUNITY                  │
│  ┌───────────────────────────────┐  │
│  │ ░ IPFS distribution           │  │
│  │ ░ Public access               │  │
│  │ ░ Permanent archive           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Read Path (Bottom-Up)

```
┌─────────────────────────────────────┐
│  TIER 4: COMMUNITY                  │
│  [COMMUNITY GET hash]               │
└──────────────┬──────────────────────┘
               │ Download from P2P
               ▼
┌─────────────────────────────────────┐
│  TIER 3: SHARED                     │
│  [SHARED SYNC]                      │
└──────────────┬──────────────────────┘
               │ Sync from devices
               ▼
┌─────────────────────────────────────┐
│  TIER 2: PRIVATE                    │
│  [PRIVATE LOAD filename]            │
└──────────────┬──────────────────────┘
               │ Decrypt and load
               ▼
┌─────────────────────────────────────┐
│  TIER 1: MEMORY                     │
│  Data ready for use                 │
└─────────────────────────────────────┘
```

---

## Performance Characteristics

### Speed Comparison

```
Operation     │ MEMORY │ PRIVATE │ SHARED │ COMMUNITY
──────────────┼────────┼─────────┼────────┼───────────
Write         │ ██████ │ ████    │ ███    │ ██
Read          │ ██████ │ █████   │ ████   │ ███
Search        │ ██████ │ █████   │ ███    │ ██
List          │ ██████ │ █████   │ ████   │ ███
Delete        │ ██████ │ █████   │ ████   │ ░
```

**Legend:** ██████ Instant, █████ Fast, ████ Medium, ███ Slow, ██░ Very Slow

### Storage Limits

```
╔═══════════════════════════════════════════════════╗
║ Tier      │ Max Size │ File Count │ Retention    ║
╠═══════════════════════════════════════════════════╣
║ MEMORY    │ Unlim    │ Unlim      │ Session only ║
║ PRIVATE   │ Unlim    │ Unlim      │ Permanent    ║
║ SHARED    │ 10GB*    │ 10,000*    │ Permanent    ║
║ COMMUNITY │ Unlim    │ Unlim      │ Permanent    ║
╚═══════════════════════════════════════════════════╝

* = Configurable limits
```

---

## Security Model

### Encryption by Tier

```
TIER 1: MEMORY
┌────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  No encryption
│  Plain text in RAM/disk        │  Fast but exposed
│  Cleared on exit               │  Session security only
└────────────────────────────────┘

TIER 2: PRIVATE
┌────────────────────────────────┐
│  ████████████████████████████  │  AES-256 encryption
│  Password-protected files      │  Strong security
│  Local device only             │  No network exposure
└────────────────────────────────┘

TIER 3: SHARED
┌────────────────────────────────┐
│  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  │  Optional encryption
│  Syncthing transport security  │  Network encrypted
│  Trusted devices only          │  Medium security
└────────────────────────────────┘

TIER 4: COMMUNITY
┌────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  No encryption
│  Public IPFS distribution      │  Assume public
│  Content addressing            │  Integrity verified
└────────────────────────────────┘
```

---

## Usage Examples

### Example 1: Personal Note (MEMORY → PRIVATE)

```
# Create note in fast memory
[MEMORY|NEW*note*My survival tips]
[MEMORY|WRITE*note*Always carry water purification tablets]

# Save to encrypted private storage
[MEMORY|SAVE*note*private]

# Verify
[PRIVATE|LIST]
```

### Example 2: Share Knowledge (PRIVATE → SHARED)

```
# Load from private
[PRIVATE|LOAD*water_guide]

# Share with devices
[PRIVATE|SHARE*water_guide]

# Verify sync
[SHARED|STATUS]
```

### Example 3: Publish to Community (SHARED → COMMUNITY)

```
# Load from shared
[SHARED|LOAD*survival_manual]

# Publish to P2P network
[SHARED|PUBLISH*survival_manual]

# Get IPFS hash
[COMMUNITY|INFO*survival_manual]
```

---

## Command Reference

### MEMORY Commands
```
[MEMORY|NEW*name*content]       Create temporary file
[MEMORY|WRITE*name*text]        Append to file
[MEMORY|READ*name]              Display content
[MEMORY|SAVE*name*tier]         Save to tier (private/shared)
[MEMORY|LIST]                   List all memory files
[MEMORY|DELETE*name]            Remove from memory
```

### PRIVATE Commands
```
[PRIVATE|LOAD*name]             Load encrypted file
[PRIVATE|SAVE*name]             Save with encryption
[PRIVATE|LIST]                  List private files
[PRIVATE|SHARE*name]            Move to shared tier
[PRIVATE|DELETE*name]           Delete private file
```

### SHARED Commands
```
[SHARED|LOAD*name]              Load shared file
[SHARED|SAVE*name]              Save to shared
[SHARED|LIST]                   List shared files
[SHARED|SYNC]                   Sync with devices
[SHARED|PUBLISH*name]           Move to community
[SHARED|STATUS]                 Show sync status
```

### COMMUNITY Commands
```
[COMMUNITY|GET*hash]            Download from IPFS
[COMMUNITY|LIST]                List community files
[COMMUNITY|INFO*name]           Show IPFS details
[COMMUNITY|SEARCH*query]        Search P2P network
```

---

## Best Practices

### ✅ DO

- Use **MEMORY** for temporary work (notes, drafts)
- Use **PRIVATE** for sensitive data (passwords, personal info)
- Use **SHARED** for multi-device sync (documents, configs)
- Use **COMMUNITY** for public knowledge (guides, tutorials)

### ❌ DON'T

- Don't store passwords in MEMORY (session only)
- Don't put sensitive data in COMMUNITY (public)
- Don't exceed SHARED storage limits
- Don't assume MEMORY persists after exit

---

## Troubleshooting

### Common Issues

```
┌─────────────────────────────────────────────────┐
│ Problem: File not found in MEMORY              │
│ ▶ Solution: Check if session ended             │
│   Files are cleared on exit                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Problem: PRIVATE encryption failed              │
│ ▶ Solution: Verify password entered correctly  │
│   Password required for decrypt                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Problem: SHARED sync not working                │
│ ▶ Solution: Check Syncthing service status     │
│   Run: syncthing --help                         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Problem: COMMUNITY upload slow                  │
│ ▶ Solution: IPFS network may be congested      │
│   Try again later or check connectivity         │
└─────────────────────────────────────────────────┘
```

---

## Technical Details

### File Structure

```
uDOS/
├── .memory/              ← TIER 1 (gitignored)
│   ├── note1.txt
│   ├── draft2.md
│   └── temp_data.json
│
├── memory/
│   ├── private/          ← TIER 2 (encrypted)
│   │   ├── passwords.enc
│   │   ├── journal.enc
│   │   └── keys.enc
│   │
│   ├── shared/           ← TIER 3 (syncthing)
│   │   ├── configs/
│   │   ├── documents/
│   │   └── .stfolder
│   │
│   └── community/        ← TIER 4 (IPFS)
│       ├── guides/
│       ├── tutorials/
│       └── .ipfs_hashes
```

### Data Persistence

```
Tier      │ Persistence │ Location
──────────┼─────────────┼─────────────────────
MEMORY    │ Session     │ RAM + .memory/
PRIVATE   │ Permanent   │ memory/private/
SHARED    │ Permanent   │ memory/shared/
COMMUNITY │ Permanent   │ IPFS + memory/community/
```

---

## Related Documentation

- **Commands:** `docs/commands/MEMORY.md`
- **Security:** `docs/security/encryption.md`
- **Sync Setup:** `docs/setup/syncthing.md`
- **IPFS Guide:** `docs/setup/ipfs.md`

---

**Version:** 1.0.20
**Last Updated:** 2025-11-16
**Architecture:** Text-first, offline-capable, P2P-enabled

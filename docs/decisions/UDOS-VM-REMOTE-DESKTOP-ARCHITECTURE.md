# uDOS VM and Remote Desktop Decision

Status: active but non-blocking platform reference  
Updated: 2026-03-03

## Purpose

This document defines the high-level platform topology for:
- physical nodes used for production roles
- VM mirrors used for testing and lab reproduction
- remote access standards between nodes

It is a topology decision, not a step-by-step provisioning guide.

## Decision

uDOS supports a split infrastructure model:
- physical nodes carry the primary runtime roles
- virtual nodes mirror those roles for testing and validation
- the control workstation orchestrates but is not treated as production infrastructure by default

## Node Roles

### Control node

The control node is the operator workstation.
It may host VMs and remote-access clients, but it should not be treated as the default production node.

### Wizard node

The Wizard node carries:
- managed services
- network-aware APIs
- extended runtime dependencies
- optional containerized support services

### Core node

The core node carries:
- lightweight local runtime behavior
- deterministic command execution
- minimal operating footprint

### Compatibility or gaming node

Where needed, a separate machine may be used for compatibility testing, gaming, or high-overhead runtime needs.

## Remote Access Rules

- use SSH as the default remote access standard for Linux nodes
- use LAN-scoped remote desktop only where a GUI or Windows compatibility path requires it
- do not expose remote-desktop services directly to the public internet

## VM Strategy

Virtual machines are used for:
- environment mirroring
- topology validation
- release-lane testing
- provisioning script verification

They should mirror named runtime roles rather than inventing a second architecture.

## Provisioning Rule

Provision physical and virtual nodes from the same role-oriented scripts wherever possible.
The goal is reproducibility, low drift, and fast rebuild capability.

## v1.5 Relevance

This document remains a monitor-only or extension-oriented platform reference for v1.5 unless a certified release lane depends on a specific VM or remote desktop path.

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/decisions/alpine-linux-spec.md`
- `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md`

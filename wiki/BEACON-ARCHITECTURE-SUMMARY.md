# Beacon Portal (v1.3 Overview)

**Version:** v1.3.0  
**Last Updated:** 2026-02-04  
**Status:** Concept / Not in v1.3 release manifest  
**Owner:** uDOS Engineering

> This is the single Beacon page for v1.3. It is intentionally concise; full specs live in `docs/wiki-candidates/`.

---

## Purpose

A **Beacon** is a minimal Wi‑Fi node that announces presence and routes nearby devices to a **Wizard** gateway when available. It is intentionally dumb, replaceable, and local‑first.

**Motto:** Beacon announces; Wizard decides.

---

## Principles

- **Presence over capacity** — be discoverable, not data‑heavy
- **Single responsibility** — Beacon connects; Wizard computes
- **Local‑first** — no WAN required
- **Graceful degradation** — Beacon still signals intent when Wizard is offline

---

## Connectivity Model

```
Device → Beacon (Wi‑Fi) → Wizard (optional)
```

All layers are optional:
- ✅ Device only (offline)
- ✅ Device + Beacon (local Wi‑Fi)
- ✅ Device + Beacon + Wizard (gateway features)

---

## Operating Modes (High‑Level)

- **Private‑Home** — trusted devices, familiar Wi‑Fi, optional sharing
- **Public‑Secure** — isolated clients, captive portal, rate limits

---

## Status

Beacon is **not part of the v1.3 release manifest** by default. It remains a design‑level concept and may be activated in later milestones.

---

## Full Specs (Reference)

See:
- `docs/wiki-candidates/BEACON-PORTAL.md`
- `docs/wiki-candidates/BEACON-VPN-TUNNEL.md`
- `docs/wiki-candidates/BEACON-QUICK-REFERENCE.md`
- `docs/wiki-candidates/ALPINE-CORE.md`
- `docs/wiki-candidates/SONIC-SCREWDRIVER.md`

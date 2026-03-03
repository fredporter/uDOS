---
name: ucode
description: >
  Entry command for the uDOS Dev Mode subset in Vibe. Use /ucode to check
  health, then jump to contributor flows like /ucode-help, /ucode-setup,
  or /ucode-dev.
allowed-tools: ucode_health
user-invocable: true
---

# ucode

You are the uDOS Dev Mode command entrypoint.

## What to do

1. Call `ucode_health` once.
2. Show a compact status line:
   - uDOS reachable/unreachable
   - quick recommendation if unhealthy
3. Show available slash commands:
   - `/ucode-help` - developer command subset reference
   - `/ucode-setup` - contributor setup and repair workflow
   - `/ucode-dev` - developer diagnostics
4. State clearly that Vibe only exposes the contributor-oriented `ucode` subset,
   not the full operator command surface.
5. Ask which one the user wants to run next.

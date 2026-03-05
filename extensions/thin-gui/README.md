# Thin GUI Extension

Thin GUI is a dedicated uDOS extension for fast fullscreen/single-window output.

It is not part of core ownership. Core can call it via `THINGUI` commands.

## Extension Boundary

- Extension owns launch-intent client contracts (`LaunchIntent`, session stream).
- Core owns terminal command dispatch (`THINGUI STATUS|INSTALL|BUILD|LINT|OPEN|INTENT`).
- Wizard remains the bundled browser/shelf GUI lane and web publishing path.

## Runtime Targets

- High-resource single-purpose fullscreen usage:
  - game container frontends
  - 3D runtime surfaces
- Low-resource fast-use deployments:
  - bare-metal Alpine + uDOS core + Thin GUI extension
  - kiosk mode single-app session

## Contract Scope

- Emits launch-intent payloads to Wizard launch routes.
- Consumes launch session streams.
- No OS-specific compositor or browser launcher logic in this package.

Platform launch ownership stays in runtime adapters and packaging contracts.

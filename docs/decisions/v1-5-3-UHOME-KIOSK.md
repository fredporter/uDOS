V1.5.3 — uHOME Android Kiosk + Local Network Server

## Goal

Build a second Android lane where the tablet acts as a **uHOME kiosk/controller** on the local network, backed by a separate **uHOME server** running elsewhere on the LAN.

## Repository boundary

- uHOME is separate from the main uDOS repo
- the uHOME Android app and uHOME macOS app are separate client repositories
- this decision is retained here because uDOS must define the server, launcher, route, and control contracts those clients consume

## Topology

### Server
- separate machine on the local network
- hybrid Linux / Windows deployment
- Linux side should be the preferred uHOME / Wizard / Sonic host
- Windows 10 “toybox” side is auxiliary, not the orchestration authority

### Tablet
- Android 15 tablet
- multi-app kiosk capable
- controller-friendly UI
- LAN control/display surface
- Thin-GUI overlay capable

## Canonical uHOME direction

uHOME remains:
- local-first
- LAN-oriented
- Sonic-installed
- compatible with Wizard-managed scheduling and job execution
- presented via Alpine thin-GUI kiosk or Steam-console-style launcher modes

## Product boundary

### uHOME server owns
- media/control jobs
- local scheduling
- capture/post-processing orchestration
- remote/control-plane endpoints
- storage and media library organization

### Android kiosk owns
- launcher shell
- controller/touch navigation
- household-friendly browsing/control UI
- Thin-GUI surfaces
- local status panels
- remote session/control entry points

## Main UX surfaces

### 1. Living-room launcher
- Steam-console-style launcher
- tile-based big-screen UX
- controller-first navigation
- quick entry into home services, media, jobs, settings

### 2. Thin-GUI kiosk mode
- fullscreen overlays
- kiosk-safe focus model
- display current jobs, playback status, household dashboards

### 3. Media / household panel
- playback control
- queue view
- library browsing hooks
- household-safe status display

### 4. Jobs / schedules panel
- scheduled tasks
- current job status
- failures / retries
- quick run or cancel for approved actions

## Controller support

### Input classes
- Xbox controller mappings
- PlayStation controller mappings
- generic Bluetooth HID fallback

### Required actions
- D-pad focus navigation
- analog stick navigation fallback
- confirm / select
- back
- home / launcher
- menu / context
- shoulder buttons for tab/page movement
- media controls if present

### UX requirements
- all key launcher actions usable without touch
- visible focus ring
- no hidden critical controls behind touch-only gestures

## Technical architecture

### LAN discovery
Recommended support:
- local hostname / manual target entry
- mDNS / Zeroconf later
- remembered trusted servers

### Session model
- household-safe mode for passive viewing
- authenticated mode for control actions
- local-only preference

### Deployment modes
- dedicated kiosk mode
- launcher mode
- companion tablet mode

## Acceptance criteria

### MVP
- connect to local uHOME server
- show launcher UI
- controller navigation works for Xbox and PlayStation
- open Thin-GUI overlay
- show job/schedule status

### Phase 2
- media/control routes usable
- playback/browser UI stable
- profile/session modes stable
- Steam-console living-room UX polished

### Phase 3
- Windows toybox interoperability patterns documented
- advanced controller maps and remapping added
- family/household roles added

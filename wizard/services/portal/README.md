# Beacon Portal Services

**Status:** v1.0 Config Management Ready

## Current Implementation

- **Config Load/Merge**: Portal config loaded from [config/beacon.json](../config/beacon.json), with deep merge for defaults.
- **Tunnel Defaults**: `wizard_endpoint`, `wizard_public_key`, `interface_address`, `listen_port`, `allowed_ips`, `persistent_keepalive`.
- **Quota Defaults**: `device_quota_monthly_usd` (5.0), `min_request_usd` (0.01), `auto_reset_quota` (true).
- **WireGuard Config Gen**: `generate_wireguard_config()` returns formatted `[Interface]` + `[Peer]` config blocks.

## Validation Schema (Pegged for v1.1)

### beacon_portal.defaults

| Field | Type | Valid | Notes |
|-------|------|-------|-------|
| device_quota_monthly_usd | float | > 0.0 | Monthly budget per device |
| min_request_usd | float | > 0.0 | Minimum charge per request |
| auto_reset_quota | bool | true \| false | Auto-reset on month boundary |

### beacon_portal.tunnel

| Field | Type | Valid | Notes |
|-------|------|-------|-------|
| wizard_endpoint | string | FQDN or IP | Wizard server endpoint |
| wizard_public_key | string | 44-char base64 | WireGuard public key |
| interface_address | string | CIDR /32 | Beacon tunnel IP |
| listen_port | int | 1024-65535 | WireGuard listening port |
| allowed_ips | array | ["10.64.2.0/24"] | Allowed IP ranges |
| persistent_keepalive | int | 1-255 | Keepalive seconds |

**TODO (v1.1):**
- Validate `wizard_public_key` is valid base64 (44 chars)
- Validate `interface_address` is valid CIDR /32
- Validate `allowed_ips` are valid CIDR blocks
- Validate `listen_port` is in valid range
- Validate `device_quota_monthly_usd` and `min_request_usd` are positive
- Raise `HTTPException(400)` on invalid updates

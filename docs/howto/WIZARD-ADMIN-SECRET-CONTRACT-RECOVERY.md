# Wizard Admin Secret Contract Recovery

This runbook covers safe drift detection and repair for the Wizard admin auth contract across:

- `.env`: `WIZARD_ADMIN_TOKEN`, `WIZARD_KEY`
- `wizard/config/wizard.json`: `admin_api_key_id`
- secret store tomb: entry keyed by `admin_api_key_id` (default `wizard-admin-token`)

## 1. Check Drift Status

From the Wizard host (local requests only):

```bash
export WIZARD_PORT="${WIZARD_PORT:-8765}"
export WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:${WIZARD_PORT}}"
curl -s "${WIZARD_BASE_URL}/api/admin-token/contract/status" | jq
```

Expected healthy output:

- `"ok": true`
- `"drift": []`

If drift exists, `repair_actions` will list explicit remediation steps.

## 2. Rotate Admin Token (Config Flow)

Use the local rotate endpoint:

```bash
curl -s -X POST "${WIZARD_BASE_URL}/api/admin-token/generate" | jq
```

This updates:

- `.env` `WIZARD_ADMIN_TOKEN`
- `.env` `WIZARD_KEY` (if missing)
- secret store entry (`admin_api_key_id` in `wizard.json`, or `wizard-admin-token`)

Re-check drift:

```bash
curl -s "${WIZARD_BASE_URL}/api/admin-token/contract/status" | jq
```

## 3. Recover From Tomb/Key Mismatch

If status includes `"secret_store_locked"` or auth fails due tomb/key mismatch:

```bash
curl -s -X POST "${WIZARD_BASE_URL}/api/admin-token/contract/repair" | jq
```

Repair behavior:

- ensures `admin_api_key_id` exists in `wizard/config/wizard.json`
- repairs/synchronizes `.env` `WIZARD_KEY` + `WIZARD_ADMIN_TOKEN`
- if tomb cannot unlock, performs a controlled tomb reset and reseeds admin token

Confirm post-repair:

```bash
curl -s "${WIZARD_BASE_URL}/api/admin-token/contract/status" | jq
```

## 4. Restart/Boot Verification

After restart, verify contract and auth:

```bash
curl -s "${WIZARD_BASE_URL}/api/admin-token/contract/status" | jq
curl -s "${WIZARD_BASE_URL}/health"
```

Wizard startup now evaluates the admin secret contract and logs drift + repair actions when detected.

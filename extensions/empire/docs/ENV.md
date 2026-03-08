# Empire Environment

Required (private):
- `EMPIRE_API_TOKEN` — bearer token for API calls.
  - Alternatively, store via `python scripts/setup/set_api_token.py --token <value>`.

Optional:
- `VITE_EMPIRE_API_BASE` — legacy standalone UI API base URL (default `http://127.0.0.1:8991`).
- `VITE_EMPIRE_API_TOKEN` — legacy standalone UI bearer token for local dev.
- `GOOGLE_PLACES_API_KEY` — Places API access (for places sync).
- `HUBSPOT_PRIVATE_APP_TOKEN` — HubSpot private app token (for HubSpot sync).
  - Use `python scripts/integrations/hubspot_sync.py --push` to send local updates back.
- Gmail credentials/token paths (stored in the secret store, not env vars):
  - `python scripts/setup/set_google_gmail_credentials_path.py --path /path/to/credentials.json`
  - `python scripts/setup/set_google_gmail_token_path.py --path /path/to/token.json`

Note:

- The supported Empire UI is the Wizard dashboard route at `#empire`.
- `extensions/empire/web` remains a legacy reference surface and is not the primary runtime UI.

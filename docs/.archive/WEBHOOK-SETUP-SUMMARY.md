# Webhook Setup Summary (GitHub)

Quick reference for configuring GitHub webhooks with uDOS Wizard.

## Prerequisites
- Wizard server running on `http://localhost:8765`
- GitHub repo access with admin permissions

## Setup
1. Run the interactive setup:
   - `SETUP webhook`
   - or `SETUP webhook github`
2. Follow the prompts to generate and store the GitHub webhook secret.
3. In your GitHub repo:
   - Settings → Webhooks → Add webhook
   - Payload URL: `http://localhost:8765/api/github/webhook`
   - Content type: `application/json`
   - Secret: use the generated secret from the setup prompt
   - Events: Push, Pull requests, Issues

## Verify
- Start Wizard: `WIZARD`
- Open `http://localhost:8765`
- Confirm GitHub shows as connected in Settings → Webhooks

## Troubleshooting
- Ensure the Wizard server is reachable from the machine hosting the repo.
- Re-run `SETUP webhook github` if you need a new secret.

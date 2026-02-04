# Vibe CLI Service

This container boots the Mistral Vibe CLI as described in `wizard/extensions/assistant/vibe_cli_service.py`. In the new arc, Vibe acts as the local-first AI lane and mission runner for the Svelte UI modules and the renderer API.

The compose service mounts `/workspace/vault` so Vibe can read the same `.env`, mission reports, and contributions that the mission scheduler and renderer observe. You can feed `.json` mission bundles or prompts via `wizard/extensions/assistant/vibe_cli_service.py` so the CLI can propose contributions, run reports, or instruct the mission scheduler to send render jobs.

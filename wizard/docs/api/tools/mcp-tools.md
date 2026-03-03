# MCP Tools (Wizard + uCODE)

This file documents the active MCP tool surface exposed to Wizard clients.

For Dev Mode contributor use, Vibe consumes only the reduced `/dev/` extension uCODE subset. It does not expose the full operator command inventory.

## Wizard Tools

- `wizard.health`
  - Returns `/health` payload.

- `wizard.config.get`
  - Returns Wizard config from `/api/config`.

- `wizard.config.set`
  - Updates Wizard config via `/api/config` PATCH.

- `wizard.providers.list`
  - Returns provider list from `/api/providers`.

- `wizard.tools.list`
  - Returns a list of MCP tool names for discovery.

- `wizard.plugin.command`
  - Calls `/api/plugin/command` as the compatibility bridge for command-style plugin operations.

- `wizard.plugins.registry.list`
- `wizard.plugins.registry.get`
- `wizard.plugins.registry.refresh`
- `wizard.plugins.registry.schema`
- `wizard.plugin.install`
- `wizard.plugin.uninstall`
- `wizard.plugin.enable`
- `wizard.plugin.disable`

- `wizard.workflow.list`
- `wizard.workflow.get`
- `wizard.workflow.create`
- `wizard.workflow.run`
- `wizard.workflows.list`
- `wizard.workflows.create`
- `wizard.workflows.status`
- `wizard.workflows.tasks`
- `wizard.workflows.dashboard`
- `wizard.workflows.tasks_dashboard`

- `wizard.tasks.list`
- `wizard.tasks.get`
- `wizard.tasks.create`
- `wizard.tasks.run`
- `wizard.tasks.status`
- `wizard.tasks.queue`
- `wizard.tasks.runs`
- `wizard.tasks.task`
- `wizard.tasks.schedule`
- `wizard.tasks.execute`
- `wizard.tasks.calendar`
- `wizard.tasks.gantt`
- `wizard.tasks.indexer.summary`
- `wizard.tasks.indexer.search`
- `wizard.tasks.dashboard`

- `wizard.dev.health`
- `wizard.dev.status`
- `wizard.dev.activate`
- `wizard.dev.deactivate`
- `wizard.dev.restart`
- `wizard.dev.clear`
- `wizard.dev.logs`

- `wizard.monitoring.summary`
- `wizard.monitoring.diagnostics`
- `wizard.monitoring.logs.list`
- `wizard.monitoring.logs.tail`
- `wizard.monitoring.logs.stats`
- `wizard.monitoring.alerts.list`
- `wizard.monitoring.alerts.ack`
- `wizard.monitoring.alerts.resolve`

- `wizard.datasets.list`
- `wizard.datasets.summary`
- `wizard.datasets.schema`
- `wizard.datasets.table`
- `wizard.datasets.query`
- `wizard.datasets.export`
- `wizard.datasets.import`

- `wizard.artifacts.list`
- `wizard.artifacts.summary`
- `wizard.artifacts.add`
- `wizard.artifacts.delete`

- `wizard.library.status`

- `wizard.wiki.provision`
- `wizard.wiki.structure`

- `wizard.renderer.themes`
- `wizard.renderer.theme`
- `wizard.renderer.site.exports`
- `wizard.renderer.site.files`
- `wizard.renderer.missions`
- `wizard.renderer.mission`
- `wizard.renderer.render`

- `wizard.teletext.canvas`
- `wizard.teletext.nes_buttons`

- `wizard.system.os`
- `wizard.system.stats`
- `wizard.system.info`
- `wizard.system.memory`
- `wizard.system.storage`
- `wizard.system.uptime`

- `wizard.fonts.manifest`
- `wizard.fonts.sample`
- `wizard.fonts.file`

- `wizard.ai.health`
- `wizard.ai.config`
- `wizard.ai.context`
- `wizard.ai.suggest_next`
- `wizard.ai.analyze_logs`
- `wizard.ai.explain_code`

- `wizard.providers.list`
- `wizard.providers.status`
- `wizard.providers.config`
- `wizard.providers.enable`
- `wizard.providers.disable`
- `wizard.providers.setup_flags`
- `wizard.providers.models.available`
- `wizard.providers.models.installed`
- `wizard.providers.models.pull_status`
- `wizard.providers.dashboard`

## uCODE Tools

Canonical registry: `wizard/mcp/tools/ucode_mcp_registry.py`

Rationale:
- Keep `generic` and `proxy` tools separate by design.
- `generic` is the Dev extension subset invocation path.
- `proxy` is the latency/ergonomics path for the highest-volume contributor operations.

Ownership:
- `generic` lane owner: `wizard/mcp/tools/ucode_tools.py`
- `proxy` lane owner: `wizard/mcp/tools/ucode_proxies.py`
- dispatch wrapper owner: `wizard/mcp/mcp_server.py` (`ucode.command` canonical, `ucode.dispatch` deprecated alias)

Dev extension boundary:
- Vibe uses this lane only when the `dev` profile is active and the `/dev/` extension is installed and enabled.
- The full TUI/operator `ucode` surface remains outside the Vibe skill lane.
- Binder, story, spatial, gameplay, media, and destructive commands are intentionally excluded from the Vibe Dev extension subset.

- `ucode.command`
  - Routes raw input (supports `OK`, `:`, `/`) via `/api/ucode/dispatch`.
  - MCP responses include a `display` field containing a Vibe-style TUI wrapper.

- `ucode.dispatch` (deprecated alias)
  - Compatibility alias that delegates to `ucode.command`. Treat `ucode.command` as canonical for v1.5 work.

- `ucode.tools.list` (generic lane)
  - Enumerates the approved Vibe Dev extension uCODE subset and input schemas.

- `ucode.tools.call` (generic lane)
  - Generic invocation path for the approved Vibe Dev extension uCODE subset.

- `ucode.health` (proxy lane)
- `ucode.token` (proxy lane)
- `ucode.help` (proxy lane)
- `ucode.verify` (proxy lane)
- `ucode.repair` (proxy lane)
- `ucode.config` (proxy lane)
- `ucode.run` (proxy lane)
- `ucode.read` (proxy lane)
  - High-volume direct proxies for lower-latency contributor access.

## Notes

- Admin-guarded endpoints require `WIZARD_ADMIN_TOKEN`.
- `WIZARD_BASE_URL` defaults to `http://localhost:8765`.

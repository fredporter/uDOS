# MCP Tools (Wizard + uCODE)

This file documents the initial MCP tool surface exposed to Vibe.

## Wizard Tools

- `wizard.health`
  - Returns `/health` payload.

- `wizard.config.get`
  - Returns Wizard config from `/api/config`.

- `wizard.config.set`
  - Updates Wizard config via `/api/config` PATCH.

- `wizard.providers.list`
  - Returns provider list from `/api/providers`.

- `wizard.plugin.command`
  - Calls `/api/plugin/command` (stub during migration).

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

- `ucode.dispatch`
  - Dispatch an allowlisted uCODE command via `/api/ucode/dispatch`.
  - Allowlist is controlled by `UCODE_API_ALLOWLIST`.

- `ucode.command`
  - Routes raw input (supports `OK`, `:`, `/`) via `/api/ucode/dispatch`.

## Notes

- Admin-guarded endpoints require `WIZARD_ADMIN_TOKEN`.
- `WIZARD_BASE_URL` defaults to `http://localhost:8765`.

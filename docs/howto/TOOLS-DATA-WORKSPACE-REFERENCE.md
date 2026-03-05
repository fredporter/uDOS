# Tools: Data, Workspace, and Execution

Updated: 2026-03-03
Status: active how-to reference

## Scope

Use these tools for binder and vault state, workspace switching, scheduling, script execution, setup, migration, and user context.

Dev Mode exposes only this contributor subset from the broader category:
- `ucode_seed`
- `ucode_config`
- `ucode_setup`
- `ucode_run`

Binder, save/load, place, scheduler, script, and user workflows remain part of the full TUI/operator surface.

## Data and Knowledge Tools

### `ucode_binder`

Manage project binders and their task state.

```python
ucode_binder(action="list")
ucode_binder(action="open", binder_id="project-x")
ucode_binder(action="create", name="new-project")
ucode_binder(action="status", binder_id="project-x")
```

### `ucode_save`

Persist state into the vault.

```python
ucode_save(path="vault/backups")
ucode_save(path="vault/backups", compress=True)
```

### `ucode_load`

Restore state from the vault.

```python
ucode_load(path="vault/backups/latest")
ucode_load(path="vault/backups", restore_date="2026-02-20")
```

### `ucode_seed`

Install starter templates or seed content.

```python
ucode_seed(action="status")
ucode_seed(action="install")
ucode_seed(action="reset")
```

### `ucode_migrate`

Check, run, or roll back migrations.

```python
ucode_migrate(direction="status")
ucode_migrate(direction="up")
ucode_migrate(direction="down", target="2026-03-01")
```

### `ucode_config`

Inspect or change config values.

```python
ucode_config(action="show")
ucode_config(action="get vault.path")
ucode_config(action="set vault.path /data/vault")
ucode_config(action="reset")
```

## Workspace and Execution Tools

### `ucode_place`

Manage named workspaces or places.

```python
ucode_place(action="list")
ucode_place(action="open", name="project-a")
ucode_place(action="create", name="new-place")
ucode_place(action="switch", name="project-a")
```

### `ucode_scheduler`

Manage recurring schedules and queued automation.

```python
ucode_scheduler(action="list")
ucode_scheduler(action="create", command="BACKUP", cron="0 2 * * *")
ucode_scheduler(action="delete", job_id="backup-nightly")
```

### `ucode_script`

List, inspect, edit, or run scripts.

```python
ucode_script(action="list")
ucode_script(action="run", script="backup")
ucode_script(action="show", script="backup")
ucode_script(action="edit", script="backup")
```

### `ucode_setup`

Run interactive or quick setup.

```python
ucode_setup(step="wizard")
ucode_setup(step="quick")
ucode_setup(step="validate")
ucode_setup(step="config", confirm=True)
```

### `ucode_run`

Run scripts and automation with options.

```python
ucode_run(script="backup")
ucode_run(script="sync", args="--all")
ucode_run(script="migrate", dry_run=True)
```

### `ucode_user`

Inspect or switch user context.

```python
ucode_user(action="show")
ucode_user(action="list")
ucode_user(action="create", username="alice")
ucode_user(action="switch", username="alice")
```

## Common Uses

- create or switch projects and workspaces
- save or restore runtime state
- seed new work areas
- run migrations or scheduled jobs
- change user context before operational work
- use `seed`, `config`, `setup`, and `run` from Dev Mode only when operating inside the `@dev` lane

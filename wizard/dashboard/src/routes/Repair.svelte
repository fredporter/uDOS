<script>
  import { onMount } from "svelte";

  let adminToken = "";
  let status = null;
  let artifacts = [];
  let loading = false;
  let error = null;
  let actionResult = null;
  let backupTarget = "wizard-config";
  let backupNotes = "";
  let backupPriority = 5;
  let backupNeed = 5;
  let restoreTarget = "wizard-config";
  let restoreArtifact = "";
  let toolchainPackages =
    "python3 py3-pip py3-setuptools py3-wheel py3-virtualenv";
  let addKind = "installers";
  let addSourcePath = "";
  let addNotes = "";
  let maintenanceScope = "workspace";
  let compostDays = 30;
  let compostDryRun = true;
  $: selectedBackup = artifacts.find((entry) => entry.id === restoreArtifact);

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function loadStatus() {
    loading = true;
    error = null;
    try {
      const res = await fetch("/api/v1/repair/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      status = data.status;
      const targets = Object.keys(status?.backup_targets || {});
      if (targets.length) {
        backupTarget = targets[0];
        restoreTarget = targets[0];
      }
    } catch (err) {
      error = `Failed to load repair status: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function loadArtifacts(kind = "") {
    try {
      const query = kind ? `?kind=${encodeURIComponent(kind)}` : "";
      const res = await fetch(`/api/v1/artifacts${query}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      artifacts = data.entries || [];
      const backups = artifacts.filter((entry) => entry.kind === "backups");
      if (backups.length) restoreArtifact = backups[0].id;
    } catch (err) {
      artifacts = [];
    }
  }

  async function runAction(action, payload = {}) {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/run", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ action, ...payload }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Action failed");
      actionResult = data.result || data;
      await loadStatus();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function runBackup() {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/backup", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ target: backupTarget, notes: backupNotes }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Backup failed");
      actionResult = data;
      backupNotes = "";
      await loadArtifacts();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function runBackupQueue() {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/backup/queue", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          target: backupTarget,
          notes: backupNotes,
          priority: Number(backupPriority),
          need: Number(backupNeed),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Queue failed");
      actionResult = data;
      backupNotes = "";
      await loadStatus();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function runRestore() {
    if (!restoreArtifact) return;
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          artifact_id: restoreArtifact,
          target: restoreTarget,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Restore failed");
      actionResult = data;
      await loadArtifacts();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function deleteSelectedBackup() {
    if (!restoreArtifact) return;
    const entry = artifacts.find((item) => item.id === restoreArtifact);
    const message = `Delete selected backup?\n\n${backupSummary(entry)}`;
    if (!confirm(message)) return;
    await deleteArtifact(restoreArtifact);
  }

  async function runMaintenance(action) {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/maintenance", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ action, scope: maintenanceScope }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Maintenance failed");
      actionResult = data;
      await loadStatus();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function runCompostCleanup() {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/repair/compost/cleanup", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ days: Number(compostDays), dry_run: compostDryRun }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Cleanup failed");
      actionResult = data;
      await loadStatus();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function addArtifact() {
    actionResult = null;
    try {
      const res = await fetch("/api/v1/artifacts/add", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          kind: addKind,
          source_path: addSourcePath,
          notes: addNotes || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Add failed");
      actionResult = data;
      addSourcePath = "";
      addNotes = "";
      await loadArtifacts();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  async function deleteArtifact(id) {
    if (!confirm(`Delete ${id}?`)) return;
    try {
      const res = await fetch(`/api/v1/artifacts/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Delete failed");
      actionResult = data;
      await loadArtifacts();
    } catch (err) {
      actionResult = { success: false, error: err.message };
    }
  }

  const formatBytes = (value) => {
    if (!value && value !== 0) return "0 B";
    const units = ["B", "KB", "MB", "GB", "TB"];
    let size = value;
    let idx = 0;
    while (size >= 1024 && idx < units.length - 1) {
      size /= 1024;
      idx += 1;
    }
    return `${size.toFixed(idx ? 2 : 0)} ${units[idx]}`;
  };

  const formatAge = (iso) => {
    if (!iso) return "unknown";
    const created = new Date(iso);
    if (Number.isNaN(created.getTime())) return "unknown";
    const deltaMs = Date.now() - created.getTime();
    if (deltaMs < 0) return "0h";
    const hours = Math.floor(deltaMs / 3600000);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d`;
    const weeks = Math.floor(days / 7);
    return `${weeks}w`;
  };

  const backupSummary = (entry) => {
    if (!entry) return "Backup summary unavailable.";
    const lines = [
      `ID: ${entry.id}`,
      `File: ${entry.filename}`,
      `Size: ${formatBytes(entry.size_bytes)}`,
      `Age: ${formatAge(entry.created_at)}`,
      `Purpose: ${entry.notes || "Not specified"}`,
    ];
    return lines.join("\n");
  };

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadStatus();
    loadArtifacts();
  });
</script>

<div class="wizard-page">
  <div class="page-header">
    <h1>Repair & Recovery</h1>
    <p>Self-heal tools, dependency installs, and backups.</p>
  </div>

  {#if loading}
    <div class="card">Loading repair status...</div>
  {:else if error}
    <div class="card error">{error}</div>
  {/if}

  {#if status}
    <div class="grid">
      <div class="card">
        <h2>System Status</h2>
        <div class="status-grid">
          <div>
            <div class="label">Platform</div>
            <div class="value">{status.os.platform}</div>
          </div>
          <div>
            <div class="label">Alpine</div>
            <div class="value">{status.os.is_alpine ? "Yes" : "No"}</div>
          </div>
          {#each Object.entries(status.tools) as [name, info]}
            <div>
              <div class="label">{name}</div>
              <div class="value">{info.available ? "✅" : "❌"}</div>
            </div>
          {/each}
        </div>
      </div>

      <div class="card">
        <h2>Paths</h2>
        <ul>
          {#each Object.entries(status.paths) as [name, info]}
            <li>
              <strong>{name}:</strong> {info.exists ? "✅" : "❌"} {info.path}
            </li>
          {/each}
        </ul>
      </div>
    </div>
  {/if}

  <div class="card">
    <h2>Repair Actions</h2>
    <div class="actions">
      <button on:click={() => runAction("bootstrap-venv")}>
        Bootstrap venv
      </button>
      <button on:click={() => runAction("install-python-deps")}>
        Install Python deps
      </button>
      <button on:click={() => runAction("install-dashboard-deps")}>
        Install dashboard deps
      </button>
      <button on:click={() => runAction("build-dashboard")}>
        Build dashboard
      </button>
    </div>
    <div class="toolchain">
      <div class="label">Alpine toolchain packages</div>
      <input type="text" bind:value={toolchainPackages} />
      <button
        on:click={() =>
          runAction("update-alpine-toolchain", {
            packages: toolchainPackages.split(" ").filter(Boolean),
          })}
      >
        Update Alpine toolchain
      </button>
    </div>
  </div>

  {#if status?.compost}
    <div class="card">
      <h2>Compost Status</h2>
      <div class="status-grid">
        <div>
          <div class="label">Path</div>
          <div class="value">{status.compost.path}</div>
        </div>
        <div>
          <div class="label">Entries</div>
          <div class="value">{status.compost.entries}</div>
        </div>
        <div>
          <div class="label">Bytes</div>
          <div class="value">{status.compost.total_bytes}</div>
        </div>
        <div>
          <div class="label">Latest Update</div>
          <div class="value">{status.compost.latest_update || "—"}</div>
        </div>
      </div>
    </div>
  {/if}

  <div class="card">
    <h2>Maintenance</h2>
    <div class="field">
      <label for="maintenance-scope">Scope</label>
      <select id="maintenance-scope" bind:value={maintenanceScope}>
        <option value="current">current</option>
        <option value="+subfolders">+subfolders</option>
        <option value="workspace">workspace</option>
        <option value="all">all</option>
      </select>
    </div>
    <div class="actions">
      <button on:click={() => runMaintenance("tidy")}>TIDY</button>
      <button on:click={() => runMaintenance("clean")}>CLEAN</button>
      <button on:click={() => runMaintenance("compost")}>COMPOST</button>
    </div>
    <div class="toolchain">
      <div class="label">Compost cleanup</div>
      <div class="field">
        <label for="compost-days">Days</label>
        <input id="compost-days" type="number" min="1" bind:value={compostDays} />
      </div>
      <label class="checkbox">
        <input id="compost-dry-run" type="checkbox" bind:checked={compostDryRun} />
        Dry run (preview only)
      </label>
      <button on:click={runCompostCleanup}>Cleanup compost</button>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Backups</h2>
      <div class="field">
        <label for="backup-target">Target</label>
        <select id="backup-target" bind:value={backupTarget}>
          {#if status}
            {#each Object.keys(status.backup_targets || {}) as key}
              <option value={key}>{key}</option>
            {/each}
          {/if}
        </select>
      </div>
      <div class="field">
        <label for="backup-notes">Notes</label>
        <input id="backup-notes" type="text" bind:value={backupNotes} />
      </div>
      <div class="field">
        <label for="backup-priority">Queue Priority</label>
        <input id="backup-priority" type="range" min="1" max="10" bind:value={backupPriority} />
        <div class="value">{backupPriority}</div>
      </div>
      <div class="field">
        <label for="backup-need">Queue Need</label>
        <input id="backup-need" type="range" min="1" max="10" bind:value={backupNeed} />
        <div class="value">{backupNeed}</div>
      </div>
      <button on:click={runBackup}>Create backup</button>
      <button on:click={runBackupQueue}>Queue backup</button>
    </div>

    <div class="card">
      <h2>Restore</h2>
      <div class="field">
        <label for="restore-backup">Backup</label>
        <select id="restore-backup" bind:value={restoreArtifact}>
          {#each artifacts.filter((entry) => entry.kind === "backups") as entry}
            <option value={entry.id}>
              {entry.id} · {formatBytes(entry.size_bytes)} · {formatAge(entry.created_at)}
            </option>
          {/each}
        </select>
      </div>
      {#if selectedBackup}
        <div class="status-grid">
          <div>
            <div class="label">Size</div>
            <div class="value">{formatBytes(selectedBackup.size_bytes)}</div>
          </div>
          <div>
            <div class="label">Age</div>
            <div class="value">{formatAge(selectedBackup.created_at)}</div>
          </div>
          <div>
            <div class="label">Purpose</div>
            <div class="value">{selectedBackup.notes || "Not specified"}</div>
          </div>
        </div>
      {/if}
      <div class="field">
        <label for="restore-target">Target</label>
        <select id="restore-target" bind:value={restoreTarget}>
          {#if status}
            {#each Object.keys(status.backup_targets || {}) as key}
              <option value={key}>{key}</option>
            {/each}
          {/if}
        </select>
      </div>
      <button on:click={runRestore}>Restore backup</button>
      <button on:click={deleteSelectedBackup}>Delete backup</button>
    </div>
  </div>

  <div class="card">
    <h2>Artifact Store</h2>
    <div class="artifact-add">
      <select bind:value={addKind}>
        <option value="installers">installers</option>
        <option value="downloads">downloads</option>
        <option value="upgrades">upgrades</option>
        <option value="backups">backups</option>
      </select>
      <input
        type="text"
        placeholder="Source path (within repo)"
        bind:value={addSourcePath}
      />
      <input type="text" placeholder="Notes" bind:value={addNotes} />
      <button on:click={addArtifact}>Add</button>
    </div>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Kind</th>
          <th>File</th>
          <th>Size</th>
          <th>Created</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each artifacts as entry}
          <tr>
            <td class="mono">{entry.id}</td>
            <td>{entry.kind}</td>
            <td>{entry.filename}</td>
            <td>{entry.size_bytes}</td>
            <td>{entry.created_at}</td>
            <td>
              <button on:click={() => deleteArtifact(entry.id)}>Delete</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if actionResult}
    <div class="card status">
      <h2>Last Action</h2>
      <pre>{JSON.stringify(actionResult, null, 2)}</pre>
    </div>
  {/if}
</div>

<style>
  .wizard-page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem;
    color: var(--text-primary, #f8fafc);
  }

  :global(html.light) .wizard-page {
    color: #0f172a;
  }

  .page-header h1 {
    margin: 0 0 0.5rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
  }

  :global(html.light) .card {
    background: #ffffff;
    border-color: #e2e8f0;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
  }

  .card.error {
    border-color: #ef4444;
    color: #fecaca;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
  }

  .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(248, 250, 252, 0.6);
  }

  :global(html.light) .label {
    color: rgba(15, 23, 42, 0.6);
  }

  .value {
    font-weight: 600;
    margin-top: 0.25rem;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  button {
    background: #1f2937;
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.3);
    padding: 0.5rem 0.9rem;
    border-radius: 0.5rem;
    cursor: pointer;
  }

  button:hover {
    background: #334155;
  }

  :global(html.light) button {
    background: #f1f5f9;
    color: #0f172a;
    border-color: #cbd5f5;
  }

  .toolchain {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
  }

  input,
  select {
    padding: 0.45rem 0.6rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(15, 23, 42, 0.6);
    color: #f8fafc;
  }

  :global(html.light) input,
  :global(html.light) select {
    background: #ffffff;
    color: #0f172a;
  }

  .artifact-add {
    display: grid;
    grid-template-columns: minmax(120px, 140px) 1fr 1fr auto;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    text-align: left;
    padding: 0.5rem 0.4rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    font-size: 0.85rem;
  }

  .mono {
    font-family: "SF Mono", ui-monospace, SFMono-Regular, Menlo, Consolas,
      monospace;
    font-size: 0.75rem;
  }

  pre {
    white-space: pre-wrap;
    background: rgba(15, 23, 42, 0.6);
    padding: 1rem;
    border-radius: 0.5rem;
  }
</style>

<script>
  import { onMount } from "svelte";

  let adminToken = "";
  let status = null;
  let progress = null;
  let variables = null;
  let paths = null;
  let error = null;
  let actionResult = null;
  let loading = false;

  let configName = "";
  let configValue = "";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function fetchJson(path, options = {}) {
    const res = await fetch(path, { headers: authHeaders(), ...options });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    return data;
  }

  async function loadSetup() {
    loading = true;
    error = null;
    try {
      status = await fetchJson("/api/v1/setup/status");
      progress = await fetchJson("/api/v1/setup/progress");
      variables = await fetchJson("/api/v1/setup/required-variables");
      paths = await fetchJson("/api/v1/setup/paths");
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function runWizardStart() {
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/wizard/start", {
        method: "POST",
      });
      await loadSetup();
    } catch (err) {
      actionResult = { error: err.message };
    }
  }

  async function runWizardComplete() {
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/wizard/complete", {
        method: "POST",
      });
      await loadSetup();
    } catch (err) {
      actionResult = { error: err.message };
    }
  }

  async function updateConfig() {
    if (!configName || !configValue) return;
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/configure", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ name: configName, value: configValue }),
      });
      configName = "";
      configValue = "";
      await loadSetup();
    } catch (err) {
      actionResult = { error: err.message };
    }
  }

  async function initializePaths() {
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/paths/initialize", {
        method: "POST",
      });
      await loadSetup();
    } catch (err) {
      actionResult = { error: err.message };
    }
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadSetup();
  });
</script>

<div class="wizard-page">
  <div class="page-header">
    <h1>Setup Wizard</h1>
    <p>First-time configuration and environment readiness.</p>
  </div>

  {#if loading}
    <div class="card">Loading setup status...</div>
  {:else if error}
    <div class="card error">{error}</div>
  {/if}

  {#if status}
    <div class="grid">
      <div class="card">
        <h2>Status</h2>
        <div class="status-grid">
          <div>
            <div class="label">Setup Complete</div>
            <div class="value">
              {status.setup?.setup_complete ? "✅" : "⏳"}
            </div>
          </div>
          <div>
            <div class="label">Initialized</div>
            <div class="value">{status.setup?.initialized_at || "—"}</div>
          </div>
          <div>
            <div class="label">Services Enabled</div>
            <div class="value">{status.setup?.services_enabled?.length || 0}</div>
          </div>
        </div>
        <div class="actions">
          <button on:click={runWizardStart}>Start Wizard</button>
          <button on:click={runWizardComplete}>Complete Wizard</button>
        </div>
      </div>

      <div class="card">
        <h2>Progress</h2>
        <div class="status-grid">
          <div>
            <div class="label">Progress</div>
            <div class="value">{progress?.progress_percent ?? 0}%</div>
          </div>
          <div>
            <div class="label">Configured Variables</div>
            <div class="value">{progress?.variables_configured ?? 0}</div>
          </div>
          <div>
            <div class="label">Required Variables</div>
            <div class="value">{progress?.required_variables ?? 0}</div>
          </div>
        </div>
      </div>
    </div>
  {/if}

  {#if variables}
    <div class="card">
      <h2>Required Variables</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Env Var</th>
            <th>Status</th>
            <th>Required</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(variables.variables || {}) as [key, info]}
            <tr>
              <td>{info.name}</td>
              <td class="mono">{info.env_var}</td>
              <td>{info.status}</td>
              <td>{info.required ? "Yes" : "No"}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  <div class="card">
    <h2>Update Configuration</h2>
    <div class="field">
      <label>Variable</label>
      <input type="text" bind:value={configName} placeholder="GITHUB_TOKEN" />
    </div>
    <div class="field">
      <label>Value</label>
      <input type="password" bind:value={configValue} placeholder="••••••" />
    </div>
    <button on:click={updateConfig}>Update</button>
  </div>

  {#if paths}
    <div class="card">
      <h2>Paths</h2>
      <pre>{JSON.stringify(paths, null, 2)}</pre>
      <button on:click={initializePaths}>Initialize Paths</button>
    </div>
  {/if}

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
  }

  :global(html.light) .card {
    background: #ffffff;
    border-color: #e2e8f0;
  }

  .card.error {
    border-color: #ef4444;
    color: #fecaca;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(248, 250, 252, 0.6);
  }

  .value {
    font-weight: 600;
    margin-top: 0.25rem;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  input {
    background: #0f172a;
    border: 1px solid rgba(148, 163, 184, 0.3);
    color: #f8fafc;
    padding: 0.5rem;
    border-radius: 0.5rem;
  }

  :global(html.light) input {
    background: #f8fafc;
    color: #0f172a;
  }

  button {
    background: #1f2937;
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.3);
    padding: 0.5rem 0.9rem;
    border-radius: 0.5rem;
    cursor: pointer;
  }
</style>

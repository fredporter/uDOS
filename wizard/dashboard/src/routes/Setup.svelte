<script>
  import { onMount } from "svelte";
  import { getAdminToken, buildAuthHeaders } from "../lib/services/auth";

  let adminToken = "";
  let status = null;
  let progress = null;
  let variables = null;
  let paths = null;
  let error = null;
  let actionResult = null;
  let loading = false;
  let wizardSteps = [];
  let stepUpdates = {};

  let configName = "";
  let configValue = "";

  const authHeaders = () => buildAuthHeaders();

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
      if (!wizardSteps.length) {
        await loadWizardSteps();
      }
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function loadWizardSteps() {
    try {
      const data = await fetchJson("/api/v1/setup/wizard/start", {
        method: "POST",
      });
      wizardSteps = data.steps || [];
    } catch (err) {
      wizardSteps = [];
    }
  }

  async function runWizardStart() {
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/wizard/start", {
        method: "POST",
      });
      wizardSteps = actionResult.steps || wizardSteps;
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

  async function toggleStepComplete(step) {
    const stepId = step.step;
    const completed = !isStepCompleted(step);
    stepUpdates = { ...stepUpdates, [stepId]: true };
    actionResult = null;
    try {
      actionResult = await fetchJson("/api/v1/setup/steps/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ step_id: stepId, completed }),
      });
      await loadSetup();
    } catch (err) {
      actionResult = { error: err.message };
    } finally {
      stepUpdates = { ...stepUpdates, [stepId]: false };
    }
  }

  function openConfig() {
    window.location.hash = "config";
  }

  onMount(() => {
    adminToken = getAdminToken();
    loadSetup();
  });

  const stepStatus = (step) => {
    if (status?.setup?.setup_complete) return "done";
    if (isStepCompleted(step)) return "done";
    const percent = progress?.progress_percent ?? 0;
    const stepPercent = Math.round((step.step / Math.max(wizardSteps.length, 1)) * 100);
    if (percent >= stepPercent) return "done";
    return "pending";
  };

  const isStepCompleted = (step) =>
    (progress?.steps_completed || []).includes(step.step);

  const stepAction = (step) => {
    const id = step.step;
    if (id === 1) {
      return { label: "Initialize Paths", action: initializePaths };
    }
    if (id === 2) {
      return { label: "Configure GitHub", action: openConfig };
    }
    if (id === 3) {
      return { label: "Configure Notion", action: openConfig };
    }
    if (id === 4) {
      return { label: "Configure AI", action: openConfig };
    }
    if (id === 5) {
      return { label: "Configure HubSpot", action: openConfig };
    }
    if (id === 6) {
      return { label: "Complete Wizard", action: runWizardComplete };
    }
    return null;
  };
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

  {#if wizardSteps?.length}
    <div class="card">
      <h2>Wizard Steps</h2>
      <ol class="step-list">
        {#each wizardSteps as step}
          <li class={`step-item ${stepStatus(step)}`}>
            <div class="step-title">
              <span class="step-number">{step.step}</span>
              <span>{step.name}</span>
              {#if isStepCompleted(step)}
                <span class="step-pill">Complete</span>
              {/if}
            </div>
            <div class="step-desc">{step.description}</div>
            <div class="step-actions">
              {#if stepAction(step)}
                <button
                  class="step-action"
                  on:click={stepAction(step).action}
                >
                  {stepAction(step).label}
                </button>
              {/if}
              <label class="step-toggle">
                <input
                  type="checkbox"
                  checked={isStepCompleted(step)}
                  disabled={stepUpdates[step.step]}
                  on:change={() => toggleStepComplete(step)}
                />
                <span>Mark step complete</span>
              </label>
            </div>
          </li>
        {/each}
      </ol>
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
      <label for="setup-config-name">Variable</label>
      <input
        id="setup-config-name"
        type="text"
        bind:value={configName}
        placeholder="GITHUB_TOKEN"
      />
    </div>
    <div class="field">
      <label for="setup-config-value">Value</label>
      <input
        id="setup-config-value"
        type="password"
        bind:value={configValue}
        placeholder="••••••"
      />
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

  .step-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .step-item {
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.5rem;
    padding: 0.75rem;
    background: rgba(15, 23, 42, 0.6);
  }

  :global(html.light) .step-item {
    background: #f8fafc;
  }

  .step-item.done {
    border-color: rgba(16, 185, 129, 0.5);
  }

  .step-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    flex-wrap: wrap;
  }

  .step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.2);
    font-size: 0.75rem;
  }

  .step-item.done .step-number {
    background: rgba(16, 185, 129, 0.6);
  }

  .step-desc {
    margin-top: 0.35rem;
    font-size: 0.85rem;
    color: rgba(248, 250, 252, 0.7);
  }

  :global(html.light) .step-desc {
    color: rgba(15, 23, 42, 0.7);
  }

  .step-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
    margin-top: 0.75rem;
  }

  .step-action {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.5);
    color: #bfdbfe;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  :global(html.light) .step-action {
    background: rgba(37, 99, 235, 0.12);
    border-color: rgba(37, 99, 235, 0.4);
    color: #1d4ed8;
  }

  .step-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: rgba(248, 250, 252, 0.7);
  }

  :global(html.light) .step-toggle {
    color: rgba(15, 23, 42, 0.7);
  }

  .step-pill {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: rgba(16, 185, 129, 0.2);
    color: #6ee7b7;
  }

  :global(html.light) .step-pill {
    background: rgba(16, 185, 129, 0.2);
    color: #047857;
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

<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";
  import { onMount } from "svelte";

  let status = null;
  let logs = [];
  let loading = true;
  let error = null;
  let canDevMode = false;

  // GitHub PAT state
  let patStatus = null;
  let patInput = "";
  let patLoading = false;
  let patError = null;
  let patSuccess = null;

  // Webhook secret state
  let webhookSecretStatus = null;
  let generatedSecret = null;
  let webhookLoading = false;
  let webhookError = null;
  let copiedSecret = false;

  async function loadStatus() {
    try {
      const res = await apiFetch("/api/dev/status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      status = await res.json();
      loading = false;
    } catch (err) {
      error = `Failed to load status: ${err.message}`;
      loading = false;
    }
  }

  async function loadLogs() {
    try {
      const res = await apiFetch("/api/dev/logs?lines=100", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      logs = data.logs || [];
    } catch (err) {
      console.error("Failed to load logs:", err);
    }
  }

  async function loadPatStatus() {
    try {
      const res = await apiFetch("/api/dev/github/pat-status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (res.ok) {
        patStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load PAT status:", err);
    }
  }

  async function loadWebhookSecretStatus() {
    try {
      const res = await apiFetch("/api/dev/webhook/github-secret-status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (res.ok) {
        webhookSecretStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load webhook secret status:", err);
    }
  }

  async function savePat() {
    if (!patInput.trim()) return;
    patLoading = true;
    patError = null;
    patSuccess = null;
    try {
      const res = await apiFetch("/api/dev/github/pat", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: patInput.trim() }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      patSuccess = "GitHub PAT saved successfully";
      patInput = "";
      await loadPatStatus();
    } catch (err) {
      patError = `Failed to save PAT: ${err.message}`;
    } finally {
      patLoading = false;
    }
  }

  async function clearPat() {
    patLoading = true;
    patError = null;
    patSuccess = null;
    try {
      const res = await apiFetch("/api/dev/github/pat", {
        method: "DELETE",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      patSuccess = "GitHub PAT cleared";
      await loadPatStatus();
    } catch (err) {
      patError = `Failed to clear PAT: ${err.message}`;
    } finally {
      patLoading = false;
    }
  }

  async function generateWebhookSecret() {
    webhookLoading = true;
    webhookError = null;
    generatedSecret = null;
    copiedSecret = false;
    try {
      const res = await apiFetch("/api/dev/webhook/github-secret", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      generatedSecret = data.secret;
      await loadWebhookSecretStatus();
    } catch (err) {
      webhookError = `Failed to generate secret: ${err.message}`;
    } finally {
      webhookLoading = false;
    }
  }

  function copySecret() {
    if (generatedSecret) {
      navigator.clipboard.writeText(generatedSecret);
      copiedSecret = true;
      setTimeout(() => (copiedSecret = false), 2000);
    }
  }

  async function activate() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/activate", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
      await loadLogs();
    } catch (err) {
      error = `Failed to activate: ${err.message}`;
      loading = false;
    }
  }

  async function deactivate() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/deactivate", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
    } catch (err) {
      error = `Failed to deactivate: ${err.message}`;
      loading = false;
    }
  }

  async function restart() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/restart", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
      await loadLogs();
    } catch (err) {
      error = `Failed to restart: ${err.message}`;
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
    loadLogs();
    loadPatStatus();
    loadWebhookSecretStatus();
    const interval = setInterval(loadStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  });

  $: canDevMode =
    !!status?.requirements?.dev_root_present &&
    !!status?.requirements?.dev_template_present;
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Dev Mode</h1>
  <p class="text-gray-400 mb-8">Manage Goblin experimental dev server</p>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if loading && !status}
    <div class="text-center py-12 text-gray-400">Loading...</div>
  {:else if status}
    <!-- Status Card -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">Goblin Server Status</h3>
        <div class="flex items-center gap-2">
          <div
            class="w-3 h-3 rounded-full {status.active
              ? 'bg-green-500'
              : 'bg-gray-500'}"
          ></div>
          <span class="text-sm text-gray-300">
            {status.active ? "Active" : "Inactive"}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm mb-6">
        <div>
          <span class="text-gray-400">Port:</span>
          <span class="text-white ml-2">{status.port || "8767"}</span>
        </div>
        <div>
          <span class="text-gray-400">Version:</span>
          <span class="text-white ml-2">{status.version || "v0.2.0"}</span>
        </div>
        {#if status.pid}
          <div>
            <span class="text-gray-400">PID:</span>
            <span class="text-white ml-2">{status.pid}</span>
          </div>
        {/if}
        {#if status.uptime}
          <div>
            <span class="text-gray-400">Uptime:</span>
            <span class="text-white ml-2">{status.uptime}</span>
          </div>
        {/if}
      </div>

      <!-- Controls -->
      <div class="flex gap-3">
        {#if !status.active}
          <button
            on:click={activate}
            disabled={loading || !canDevMode}
            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Activate Dev Mode
          </button>
        {:else}
          <button
            on:click={deactivate}
            disabled={loading || !canDevMode}
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Deactivate
          </button>
          <button
            on:click={restart}
            disabled={loading || !canDevMode}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Restart
          </button>
        {/if}
      </div>
      {#if status?.requirements}
        <div class="mt-4 text-xs text-gray-400">
          /dev present: {status.requirements.dev_root_present ? "yes" : "no"} ·
          templates ok: {status.requirements.dev_template_present ? "yes" : "no"}
        </div>
      {/if}
      {#if !canDevMode}
        <div class="mt-2 text-xs text-amber-300">Dev mode requires admin access and /dev templates.</div>
      {/if}
    </div>

    <!-- Logs -->
    {#if logs.length > 0}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Recent Logs</h3>
        <div
          class="bg-gray-900 border border-gray-700 rounded p-4 font-mono text-xs text-gray-300 max-h-96 overflow-y-auto"
        >
          {#each logs as line}
            <div class="mb-1">{line}</div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}

  <!-- GitHub PAT Configuration -->
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
    <h3 class="text-lg font-semibold text-white mb-4">🐙 GitHub Personal Access Token</h3>
    <p class="text-sm text-gray-400 mb-4">Configure your GitHub PAT for API access and repository operations.</p>

    {#if patError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{patError}</div>
    {/if}
    {#if patSuccess}
      <div class="bg-green-900 text-green-200 p-3 rounded mb-4 text-sm">{patSuccess}</div>
    {/if}

    <div class="flex items-center gap-3 mb-4">
      <div class="w-3 h-3 rounded-full {patStatus?.configured ? 'bg-green-500' : 'bg-gray-500'}"></div>
      <span class="text-sm text-gray-300">
        {#if patStatus?.configured}
          Configured: <code class="bg-gray-900 px-2 py-1 rounded text-xs">{patStatus.masked}</code>
        {:else}
          Not configured
        {/if}
      </span>
    </div>

    <div class="flex gap-3">
      <input
        type="password"
        bind:value={patInput}
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
        class="flex-1 px-3 py-2 bg-gray-900 border border-gray-600 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
      />
      <button
        on:click={savePat}
        disabled={patLoading || !patInput.trim()}
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {patLoading ? "Saving..." : "Save PAT"}
      </button>
      {#if patStatus?.configured}
        <button
          on:click={clearPat}
          disabled={patLoading}
          class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Clear
        </button>
      {/if}
    </div>
    <p class="text-xs text-gray-500 mt-3">
      Create a token at <a href="https://github.com/settings/tokens" target="_blank" class="text-blue-400 hover:underline">github.com/settings/tokens</a>
    </p>
  </div>

  <!-- Webhook Secret Generator -->
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
    <h3 class="text-lg font-semibold text-white mb-4">🔐 Webhook Secret Generator</h3>
    <p class="text-sm text-gray-400 mb-4">Generate secure webhook secrets for GitHub and other integrations.</p>

    {#if webhookError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{webhookError}</div>
    {/if}

    <div class="flex items-center gap-3 mb-4">
      <div class="w-3 h-3 rounded-full {webhookSecretStatus?.configured ? 'bg-green-500' : 'bg-gray-500'}"></div>
      <span class="text-sm text-gray-300">
        GitHub webhook secret: {webhookSecretStatus?.configured ? "Configured" : "Not configured"}
      </span>
    </div>

    <div class="flex gap-3 mb-4">
      <button
        on:click={generateWebhookSecret}
        disabled={webhookLoading}
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {webhookLoading ? "Generating..." : "Generate GitHub Webhook Secret"}
      </button>
    </div>

    {#if generatedSecret}
      <div class="bg-gray-900 border border-gray-600 rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-400">Generated Secret (saved automatically):</span>
          <button
            on:click={copySecret}
            class="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded transition"
          >
            {copiedSecret ? "Copied!" : "Copy"}
          </button>
        </div>
        <code class="block text-xs text-green-400 font-mono break-all">{generatedSecret}</code>
        <p class="text-xs text-amber-400 mt-2">⚠️ Copy this secret now and add it to your GitHub webhook settings.</p>
      </div>
    {/if}
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";
  import { onMount } from "svelte";
  import TerminalPanel from "$lib/components/terminal/TerminalPanel.svelte";
  import TerminalButton from "$lib/components/terminal/TerminalButton.svelte";
  import TerminalInput from "$lib/components/terminal/TerminalInput.svelte";

  let status = null;
  let logs = [];
  let loading = true;
  let error = null;
  let canDevMode = false;
  let scripts = [];
  let tests = [];
  let selectedScript = "";
  let selectedTest = "";
  let runOutput = "";
  let runError = null;
  let runBusy = false;
  let devInstalled = false;
  let devActivated = false;

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
      const req = status?.requirements || {};
      const installed =
        !!req.dev_root_present &&
        !!req.dev_template_present &&
        !!req.goblin_scaffold_ready;
      if (installed && status?.active) {
        await loadScriptCatalog();
      } else {
        scripts = [];
        tests = [];
        selectedScript = "";
        selectedTest = "";
      }
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

  async function loadScriptCatalog() {
    const req = status?.requirements || {};
    const installed =
      !!req.dev_root_present &&
      !!req.dev_template_present &&
      !!req.goblin_scaffold_ready;
    if (!(installed && status?.active)) {
      scripts = [];
      tests = [];
      selectedScript = "";
      selectedTest = "";
      return;
    }
    try {
      const [scriptsRes, testsRes] = await Promise.all([
        apiFetch("/api/dev/scripts", {
          headers: buildAuthHeaders(getAdminToken()),
        }),
        apiFetch("/api/dev/tests", {
          headers: buildAuthHeaders(getAdminToken()),
        }),
      ]);
      if (scriptsRes.ok) {
        const data = await scriptsRes.json();
        scripts = data.scripts || [];
        if (!selectedScript && scripts.length) selectedScript = scripts[0];
      }
      if (testsRes.ok) {
        const data = await testsRes.json();
        tests = data.tests || [];
        if (!selectedTest && tests.length) selectedTest = tests[0];
      }
    } catch (err) {
      console.error("Failed to load dev catalog", err);
    }
  }

  async function runScript() {
    if (!devActivated) {
      runError = "Dev mode must be activated before running /dev scripts.";
      return;
    }
    if (!selectedScript) return;
    runBusy = true;
    runError = null;
    runOutput = "";
    try {
      const res = await apiFetch("/api/dev/scripts/run", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path: selectedScript, args: [] }),
      });
      const data = await res.json();
      if (!res.ok || data.status === "error") throw new Error(data.message || `HTTP ${res.status}`);
      runOutput = `${(data.stdout || "").trim()}\n${(data.stderr || "").trim()}`.trim() || "(no output)";
      await loadLogs();
    } catch (err) {
      runError = `Script run failed: ${err.message}`;
    } finally {
      runBusy = false;
    }
  }

  async function runTests() {
    if (!devActivated) {
      runError = "Dev mode must be activated before running /dev tests.";
      return;
    }
    runBusy = true;
    runError = null;
    runOutput = "";
    try {
      const res = await apiFetch("/api/dev/tests/run", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path: selectedTest || null, args: [] }),
      });
      const data = await res.json();
      if (!res.ok || data.status === "error") throw new Error(data.message || `HTTP ${res.status}`);
      runOutput = `${(data.stdout || "").trim()}\n${(data.stderr || "").trim()}`.trim() || "(no output)";
      await loadLogs();
    } catch (err) {
      runError = `Test run failed: ${err.message}`;
    } finally {
      runBusy = false;
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
      await loadScriptCatalog();
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
      scripts = [];
      tests = [];
      selectedScript = "";
      selectedTest = "";
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
      await loadScriptCatalog();
    } catch (err) {
      error = `Failed to restart: ${err.message}`;
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
    loadLogs();
    loadScriptCatalog();
    loadPatStatus();
    loadWebhookSecretStatus();
    const interval = setInterval(loadStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  });

  $: canDevMode =
    !!status?.requirements?.dev_root_present &&
    !!status?.requirements?.dev_template_present &&
    !!status?.requirements?.goblin_scaffold_ready;
  $: devInstalled = canDevMode;
  $: devActivated = !!status?.active && devInstalled;
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Dev Mode</h1>
  <p class="text-gray-400 mb-8">Manage /dev scripts and tests through Wizard GUI</p>

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
        <h3 class="text-lg font-semibold text-white">Dev Workspace Status</h3>
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
          <span class="text-white ml-2">{status.requirements?.scripts_root || "n/a"}</span>
        </div>
        <div>
          <span class="text-gray-400">Version:</span>
          <span class="text-white ml-2">{status.requirements?.tests_root || "n/a"}</span>
        </div>
        <div>
          <span class="text-gray-400">Scripts:</span>
          <span class="text-white ml-2">{status.requirements?.script_count ?? 0}</span>
        </div>
        <div>
          <span class="text-gray-400">Tests:</span>
          <span class="text-white ml-2">{status.requirements?.test_count ?? 0}</span>
        </div>
      </div>

      <!-- Controls -->
      <div class="flex gap-3">
        {#if !status.active}
          <TerminalButton
            on:click={activate}
            disabled={loading || !canDevMode}
            variant="success"
            className="px-4 py-2"
          >
            Activate Dev Mode
          </TerminalButton>
        {:else}
          <TerminalButton
            on:click={deactivate}
            disabled={loading || !canDevMode}
            variant="danger"
            className="px-4 py-2"
          >
            Deactivate
          </TerminalButton>
          <TerminalButton
            on:click={restart}
            disabled={loading || !canDevMode}
            variant="accent"
            className="px-4 py-2"
          >
            Restart
          </TerminalButton>
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

  <TerminalPanel
    className="mb-6"
    title="/dev Goblin Scaffold Runner"
    subtitle="Run development scripts and tests from /dev/goblin through Wizard GUI."
  >

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div>
        <label for="dev-script-select" class="block text-xs text-gray-400 mb-1">Script</label>
        <select
          id="dev-script-select"
          bind:value={selectedScript}
          disabled={!devActivated}
          class="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-white wiz-terminal-input disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if scripts.length === 0}
            <option value="">No scripts found</option>
          {:else}
            {#each scripts as script}
              <option value={script}>{script}</option>
            {/each}
          {/if}
        </select>
      </div>
      <div>
        <label for="dev-test-select" class="block text-xs text-gray-400 mb-1">Test</label>
        <select
          id="dev-test-select"
          bind:value={selectedTest}
          disabled={!devActivated}
          class="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-white wiz-terminal-input disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if tests.length === 0}
            <option value="">No tests found</option>
          {:else}
            {#each tests as test}
              <option value={test}>{test}</option>
            {/each}
          {/if}
        </select>
      </div>
    </div>

    <div class="flex gap-3 mb-4">
      <TerminalButton
        on:click={runScript}
        disabled={runBusy || !selectedScript || !devActivated}
        variant="accent"
        className="px-4 py-2"
      >
        Run Script
      </TerminalButton>
      <TerminalButton
        on:click={runTests}
        disabled={runBusy || !devActivated}
        variant="neutral"
        className="px-4 py-2"
      >
        Run Tests
      </TerminalButton>
    </div>

    {#if !devInstalled}
      <div class="bg-amber-900/40 border border-amber-700 text-amber-100 p-3 rounded text-sm">
        /dev submodule is not installed or scaffold is incomplete. Dev operations are locked.
      </div>
    {:else if !devActivated}
      <div class="bg-slate-900/70 border border-slate-700 text-slate-200 p-3 rounded text-sm">
        Dev mode is installed but inactive. Activate Dev Mode to enable scripts and tests.
      </div>
    {/if}

    {#if runError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-3 text-sm">{runError}</div>
    {/if}
    {#if runOutput}
      <pre class="bg-gray-900 border border-gray-700 rounded p-3 text-xs text-gray-200 overflow-x-auto wiz-terminal-log">{runOutput}</pre>
    {/if}
  </TerminalPanel>

  <TerminalPanel
    className="mb-6"
    title="GitHub Personal Access Token"
    subtitle="Configure your GitHub PAT for API access and repository operations."
  >

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
      <TerminalInput
        type="password"
        bind:value={patInput}
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
        className="flex-1"
      />
      <TerminalButton
        on:click={savePat}
        disabled={patLoading || !patInput.trim()}
        variant="accent"
        className="px-4 py-2"
      >
        {patLoading ? "Saving..." : "Save PAT"}
      </TerminalButton>
      {#if patStatus?.configured}
        <TerminalButton
          on:click={clearPat}
          disabled={patLoading}
          variant="danger"
          className="px-4 py-2"
        >
          Clear
        </TerminalButton>
      {/if}
    </div>
    <p class="text-xs text-gray-500 mt-3">
      Create a token at <a href="https://github.com/settings/tokens" target="_blank" class="text-blue-400 hover:underline">github.com/settings/tokens</a>
    </p>
  </TerminalPanel>

  <TerminalPanel
    className="mb-6"
    title="Webhook Secret Generator"
    subtitle="Generate secure webhook secrets for GitHub and other integrations."
  >

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
      <TerminalButton
        on:click={generateWebhookSecret}
        disabled={webhookLoading}
        variant="accent"
        className="px-4 py-2"
      >
        {webhookLoading ? "Generating..." : "Generate GitHub Webhook Secret"}
      </TerminalButton>
    </div>

    {#if generatedSecret}
      <div class="bg-gray-900 border border-gray-600 rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-400">Generated Secret (saved automatically):</span>
          <TerminalButton
            on:click={copySecret}
            variant="neutral"
            className="px-3 py-1 text-xs"
          >
            {copiedSecret ? "Copied!" : "Copy"}
          </TerminalButton>
        </div>
        <code class="block text-xs text-green-400 font-mono break-all">{generatedSecret}</code>
        <p class="text-xs text-amber-400 mt-2">⚠️ Copy this secret now and add it to your GitHub webhook settings.</p>
      </div>
    {/if}
  </TerminalPanel>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

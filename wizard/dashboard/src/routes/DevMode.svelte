<script>
  import { onMount } from "svelte";

  let status = null;
  let logs = [];
  let loading = true;
  let error = null;

  async function loadStatus() {
    try {
      const res = await fetch("/api/dev/status");
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
      const res = await fetch("/api/dev/logs?lines=100");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      logs = data.logs || [];
    } catch (err) {
      console.error("Failed to load logs:", err);
    }
  }

  async function activate() {
    loading = true;
    try {
      const res = await fetch("/api/dev/activate", { method: "POST" });
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
      const res = await fetch("/api/dev/deactivate", { method: "POST" });
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
      const res = await fetch("/api/dev/restart", { method: "POST" });
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
    const interval = setInterval(loadStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  });
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
            disabled={loading}
            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Activate Dev Mode
          </button>
        {:else}
          <button
            on:click={deactivate}
            disabled={loading}
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Deactivate
          </button>
          <button
            on:click={restart}
            disabled={loading}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Restart
          </button>
        {/if}
      </div>
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

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

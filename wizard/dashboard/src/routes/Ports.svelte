<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount } from "svelte";

  let dashboard = null;
  let processes = [];
  let events = [];
  let resources = null;
  let resourceHistory = [];
  let loading = true;
  let error = null;
  let autoRefresh = true;
  let refreshMs = 5000;
  let timer;

  async function loadDashboard() {
    try {
      const res = await apiFetch("/api/ports/dashboard");
      if (res.ok) {
        dashboard = await res.json();
        processes = dashboard.processes || [];
        resources = dashboard.resources || null;
      }
      loading = false;
    } catch (err) {
      error = `Failed to load dashboard: ${err.message}`;
      loading = false;
    }
  }

  async function loadEvents() {
    try {
      const res = await apiFetch("/api/ports/events?limit=50");
      if (res.ok) {
        events = await res.json();
      }
    } catch (err) {
      console.error("Failed to load events:", err);
    }
  }

  async function loadResourceHistory() {
    try {
      const res = await apiFetch("/api/ports/resources/history?limit=20");
      if (res.ok) {
        resourceHistory = await res.json();
      }
    } catch (err) {
      console.error("Failed to load resource history:", err);
    }
  }

  async function startMonitoring() {
    try {
      const res = await apiFetch("/api/ports/monitor/start", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadDashboard();
    } catch (err) {
      error = `Failed to start monitoring: ${err.message}`;
    }
  }

  async function stopMonitoring() {
    try {
      const res = await apiFetch("/api/ports/monitor/stop", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadDashboard();
    } catch (err) {
      error = `Failed to stop monitoring: ${err.message}`;
    }
  }

  async function stopProcess(name) {
    try {
      const res = await apiFetch(`/api/ports/stop/${encodeURIComponent(name)}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadDashboard();
      await loadEvents();
    } catch (err) {
      error = `Failed to stop ${name}: ${err.message}`;
    }
  }

  async function restartProcess(name) {
    try {
      const res = await apiFetch(`/api/ports/restart/${encodeURIComponent(name)}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadDashboard();
      await loadEvents();
    } catch (err) {
      error = `Failed to restart ${name}: ${err.message}`;
    }
  }

  function formatTimestamp(ts) {
    if (!ts) return "—";
    const date = new Date(ts);
    if (isNaN(date.getTime())) return ts;
    return date.toLocaleString();
  }

  function formatUptime(seconds) {
    if (!seconds || seconds < 0) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  }

  function getStatusBadge(status) {
    switch (status) {
      case "running":
        return "bg-green-900 text-green-200 border-green-700";
      case "stopped":
        return "bg-gray-700 text-gray-300 border-gray-600";
      case "failed":
        return "bg-red-900 text-red-200 border-red-700";
      case "starting":
        return "bg-yellow-900 text-yellow-200 border-yellow-700";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }

  function getEventBadge(eventType) {
    switch (eventType) {
      case "started":
        return "bg-green-900/60 text-green-200";
      case "stopped":
        return "bg-gray-700/60 text-gray-300";
      case "failed":
        return "bg-red-900/60 text-red-200";
      case "registered":
        return "bg-blue-900/60 text-blue-200";
      case "unregistered":
        return "bg-purple-900/60 text-purple-200";
      default:
        return "bg-gray-700/60 text-gray-300";
    }
  }

  function startAutoRefresh() {
    if (timer) clearInterval(timer);
    if (autoRefresh) {
      timer = setInterval(() => {
        loadDashboard();
        loadEvents();
      }, refreshMs);
    }
  }

  $: if (autoRefresh !== undefined) startAutoRefresh();

  onMount(() => {
    loadDashboard();
    loadEvents();
    loadResourceHistory();
    startAutoRefresh();
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Port Manager</h1>
      <p class="text-gray-400">
        Central task and process manager for uDOS v{dashboard?.version || "—"}
      </p>
    </div>
    <div class="flex items-center gap-4">
      <label class="flex items-center gap-2 text-gray-300">
        <input type="checkbox" bind:checked={autoRefresh} class="rounded" />
        Auto-refresh
      </label>
      {#if dashboard?.monitoring}
        <button
          on:click={stopMonitoring}
          class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition"
        >
          Stop Monitor
        </button>
      {:else}
        <button
          on:click={startMonitoring}
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
        >
          Start Monitor
        </button>
      {/if}
    </div>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {error}
      <button on:click={() => (error = null)} class="ml-4 underline">Dismiss</button>
    </div>
  {/if}

  {#if loading}
    <div class="text-gray-400 text-center py-12">Loading...</div>
  {:else}
    <!-- Resource Summary -->
    {#if resources}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div class="text-gray-400 text-sm mb-1">CPU Usage</div>
          <div class="text-2xl font-bold text-white">{resources.cpu_percent?.toFixed(1) || 0}%</div>
          <div class="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-purple-500 rounded-full transition-all"
              style="width: {resources.cpu_percent || 0}%"
            ></div>
          </div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div class="text-gray-400 text-sm mb-1">Memory Usage</div>
          <div class="text-2xl font-bold text-white">{resources.memory_percent?.toFixed(1) || 0}%</div>
          <div class="text-xs text-gray-500">
            {(resources.memory_used / 1073741824).toFixed(1)} / {(resources.memory_total / 1073741824).toFixed(1)} GB
          </div>
          <div class="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-500 rounded-full transition-all"
              style="width: {resources.memory_percent || 0}%"
            ></div>
          </div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div class="text-gray-400 text-sm mb-1">Disk Usage</div>
          <div class="text-2xl font-bold text-white">{resources.disk_percent?.toFixed(1) || 0}%</div>
          <div class="text-xs text-gray-500">
            {(resources.disk_used / 1073741824).toFixed(1)} / {(resources.disk_total / 1073741824).toFixed(1)} GB
          </div>
          <div class="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-emerald-500 rounded-full transition-all"
              style="width: {resources.disk_percent || 0}%"
            ></div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Stats Summary -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
        <div class="text-3xl font-bold text-green-400">{dashboard?.active_processes || 0}</div>
        <div class="text-gray-400 text-sm">Active Processes</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
        <div class="text-3xl font-bold text-purple-400">{dashboard?.allocated_ports || 0}</div>
        <div class="text-gray-400 text-sm">Allocated Ports</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
        <div class="text-3xl font-bold text-blue-400">{dashboard?.registered_extensions || 0}</div>
        <div class="text-gray-400 text-sm">Extensions</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
        <div class="text-3xl font-bold text-amber-400">{events.length || 0}</div>
        <div class="text-gray-400 text-sm">Recent Events</div>
      </div>
    </div>

    <!-- Managed Processes -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg mb-8">
      <div class="px-4 py-3 border-b border-gray-700">
        <h2 class="text-lg font-semibold text-white">Managed Processes</h2>
      </div>
      <div class="divide-y divide-gray-700">
        {#if processes.length === 0}
          <div class="p-8 text-center text-gray-500">No processes running</div>
        {:else}
          {#each processes as proc}
            <div class="p-4 flex items-center justify-between">
              <div class="flex items-center gap-4">
                <span
                  class="px-2 py-1 text-xs rounded border {getStatusBadge(proc.status)}"
                >
                  {proc.status}
                </span>
                <div>
                  <div class="text-white font-medium">{proc.name}</div>
                  <div class="text-gray-500 text-sm">
                    Port {proc.port} • PID {proc.pid || "—"} • {formatUptime(proc.uptime)}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                {#if proc.status === "running"}
                  <button
                    on:click={() => restartProcess(proc.name)}
                    class="px-3 py-1 text-sm bg-amber-600 hover:bg-amber-700 text-white rounded transition"
                  >
                    Restart
                  </button>
                  <button
                    on:click={() => stopProcess(proc.name)}
                    class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
                  >
                    Stop
                  </button>
                {:else}
                  <span class="text-gray-500 text-sm">Not running</span>
                {/if}
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Event Log -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg">
      <div class="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-white">Event Log</h2>
        <button
          on:click={loadEvents}
          class="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition"
        >
          Refresh
        </button>
      </div>
      <div class="max-h-64 overflow-y-auto divide-y divide-gray-700">
        {#if events.length === 0}
          <div class="p-8 text-center text-gray-500">No events recorded</div>
        {:else}
          {#each events as event}
            <div class="p-3 flex items-center gap-4">
              <span
                class="px-2 py-1 text-xs rounded {getEventBadge(event.event_type)}"
              >
                {event.event_type}
              </span>
              <div class="flex-1">
                <span class="text-white">{event.name}</span>
                {#if event.port}
                  <span class="text-gray-500 ml-2">:{event.port}</span>
                {/if}
                {#if event.message}
                  <span class="text-gray-400 ml-2">— {event.message}</span>
                {/if}
              </div>
              <div class="text-gray-500 text-xs">{formatTimestamp(event.timestamp)}</div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  {/if}
</div>

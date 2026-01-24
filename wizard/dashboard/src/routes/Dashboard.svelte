<script>
  import { onDestroy, onMount } from "svelte";

  let dashboardData = null;
  let systemStats = null;
  let logStats = null;
  let githubHealth = null;
  let loading = true;
  let systemLoading = false;
  let error = null;
  let refreshTimer;

  const overloadLabels = {
    cpu_load_high: "CPU load is elevated",
    memory_high: "Memory usage is high",
    disk_high: "Disk usage is high",
  };

  const levelClass = (value) => {
    if (value >= 90 || value >= 1.5) return "bg-red-900/70 text-red-100";
    if (value >= 75 || value >= 1.1) return "bg-amber-900/70 text-amber-100";
    return "bg-emerald-900/60 text-emerald-100";
  };

  const percentBar = (percent) => Math.min(Math.max(percent || 0, 0), 100);

  const formatUptime = (seconds) => {
    if (!seconds && seconds !== 0) return "Unknown";
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (days) return `${days}d ${hours}h ${minutes}m`;
    if (hours) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  async function loadDashboard() {
    loading = true;
    error = null;
    try {
      const res = await fetch("/api/v1/index");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      dashboardData = data;
      systemStats = data.system || systemStats;
      logStats = data.log_stats || null;
    } catch (err) {
      error = `Failed to load dashboard: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function loadGitHubHealth() {
    try {
      const res = await fetch("/api/v1/github/health");
      if (res.ok) {
        githubHealth = await res.json();
      }
    } catch (err) {
      console.error("Failed to load GitHub health", err);
    }
  }

  async function loadSystemStats() {
    systemLoading = true;
    try {
      const res = await fetch("/api/v1/system/stats");
      if (res.ok) {
        systemStats = await res.json();
      }
    } catch (err) {
      console.error("Failed to refresh system stats", err);
    } finally {
      systemLoading = false;
    }
  }

  onMount(() => {
    loadDashboard();
    loadGitHubHealth();
    refreshTimer = setInterval(loadSystemStats, 15000);
  });

  onDestroy(() => {
    if (refreshTimer) clearInterval(refreshTimer);
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Dashboard</h1>
      <p class="text-gray-400">uDOS Wizard server status and configuration</p>
    </div>
    <div class="flex items-center gap-3">
      <button
        class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
        on:click={loadDashboard}
      >
        Refresh
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm"
        on:click={loadSystemStats}
      >
        {systemLoading ? "Refreshing..." : "Update stats"}
      </button>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading dashboard...</div>
  {:else if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
      {error}
    </div>
  {:else if dashboardData}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-lg font-semibold text-white">Server Status</h3>
            <p class="text-sm text-gray-400">{dashboardData.dashboard?.name}</p>
          </div>
          <div class="flex items-center gap-2 text-sm text-emerald-300">
            <span class="w-3 h-3 rounded-full bg-green-500"></span>
            Running
          </div>
        </div>
        <div class="space-y-2 text-sm text-gray-300">
          <div class="flex justify-between">
            <span class="text-gray-400">Version</span>
            <span class="font-semibold">{dashboardData.dashboard?.version}</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Updated</span>
            <span
              >{new Date(
                dashboardData.dashboard?.timestamp,
              ).toLocaleString()}</span
            >
          </div>
        </div>
        {#if logStats}
          <div class="border-t border-gray-700 pt-4 text-sm text-gray-300">
            <div class="flex justify-between mb-2">
              <span class="text-gray-400">Log storage</span>
              <span class="font-semibold">{logStats.total_size_mb} MB</span>
            </div>
            <p class="text-gray-400 text-xs">
              {logStats.total_files} files across {Object.keys(
                logStats.by_category || {},
              ).length} categories
            </p>
          </div>
        {/if}
      </div>

      {#if systemStats}
        <div
          class="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4"
        >
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white">System Health</h3>
              <p class="text-sm text-gray-400">
                {#if dashboardData.os}
                  {dashboardData.os.detected_os === "alpine"
                    ? "🐧 Alpine Linux"
                    : dashboardData.os.detected_os === "macos"
                      ? "🍎 macOS"
                      : dashboardData.os.detected_os === "ubuntu"
                        ? "🐧 Ubuntu"
                        : dashboardData.os.detected_os === "windows"
                          ? "🪟 Windows"
                          : "Unknown OS"}
                  • {dashboardData.os.platform_release}
                {/if}
              </p>
            </div>
            <span
              class={`px-3 py-1 rounded-full text-xs font-semibold ${levelClass(systemStats.cpu?.load_per_cpu || 0)}`}
            >
              Load {systemStats.cpu?.load_per_cpu ?? 0}x / core
            </span>
          </div>

          {#if systemStats.overload}
            <div
              class="bg-amber-900/40 border border-amber-700 text-amber-100 text-sm rounded-lg p-3"
            >
              <div class="font-semibold mb-1">Potential overload detected</div>
              <ul class="list-disc list-inside space-y-1">
                {#each systemStats.overload_reasons as reason}
                  <li>{overloadLabels[reason] || reason}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-slate-900/60 rounded-lg p-4 border border-slate-700">
              <div class="text-gray-400 text-sm mb-1">CPU Load</div>
              <div class="text-2xl font-semibold text-white mb-1">
                {systemStats.cpu?.load1 ?? 0}
              </div>
              <div class="text-xs text-gray-400 flex justify-between">
                <span>1m</span>
                <span>5m {systemStats.cpu?.load5 ?? 0}</span>
                <span>15m {systemStats.cpu?.load15 ?? 0}</span>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                {systemStats.cpu?.count} cores
              </p>
            </div>
            <div class="bg-slate-900/60 rounded-lg p-4 border border-slate-700">
              <div class="text-gray-400 text-sm mb-1">Memory</div>
              <div class="flex items-baseline gap-2">
                <div class="text-2xl font-semibold text-white">
                  {systemStats.memory?.used_percent ?? 0}%
                </div>
                <span class="text-xs text-gray-400"
                  >{systemStats.memory?.used_mb ?? 0} MB / {systemStats.memory
                    ?.total_mb ?? 0} MB</span
                >
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2 mt-2">
                <div
                  class={`h-2 rounded-full ${levelClass(systemStats.memory?.used_percent || 0)}`}
                  style={`width: ${percentBar(systemStats.memory?.used_percent)}%;`}
                ></div>
              </div>
            </div>
            <div class="bg-slate-900/60 rounded-lg p-4 border border-slate-700">
              <div class="text-gray-400 text-sm mb-1">Swap</div>
              {#if systemStats.swap?.active}
                <div class="flex items-baseline gap-2">
                  <div class="text-2xl font-semibold text-white">
                    {systemStats.swap?.used_percent ?? 0}%
                  </div>
                  <span class="text-xs text-gray-400"
                    >{systemStats.swap?.used_gb ?? 0} GB / {systemStats.swap
                      ?.total_gb ?? 0} GB</span
                  >
                </div>
                <div class="w-full bg-slate-800 rounded-full h-2 mt-2">
                  <div
                    class={`h-2 rounded-full ${levelClass(systemStats.swap?.used_percent || 0)}`}
                    style={`width: ${percentBar(systemStats.swap?.used_percent)}%;`}
                  ></div>
                </div>
              {:else}
                <div class="text-xl font-semibold text-gray-500">Inactive</div>
                <p class="text-xs text-gray-500 mt-2">No swap configured</p>
              {/if}
            </div>
            <div class="bg-slate-900/60 rounded-lg p-4 border border-slate-700">
              <div class="text-gray-400 text-sm mb-1">Disk</div>
              <div class="flex items-baseline gap-2">
                <div class="text-2xl font-semibold text-white">
                  {systemStats.disk?.used_percent ?? 0}%
                </div>
                <span class="text-xs text-gray-400"
                  >{systemStats.disk?.used_gb ?? 0} GB / {systemStats.disk
                    ?.total_gb ?? 0} GB</span
                >
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2 mt-2">
                <div
                  class={`h-2 rounded-full ${levelClass(systemStats.disk?.used_percent || 0)}`}
                  style={`width: ${percentBar(systemStats.disk?.used_percent)}%;`}
                ></div>
              </div>
            </div>
          </div>

          <div
            class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300"
          >
            <div class="bg-slate-900/40 rounded-lg p-4 border border-slate-800">
              <div class="text-gray-400">Uptime</div>
              <div class="text-lg font-semibold text-white">
                {formatUptime(systemStats.uptime_seconds)}
              </div>
            </div>
            <div class="bg-slate-900/40 rounded-lg p-4 border border-slate-800">
              <div class="text-gray-400">Processes</div>
              <div class="text-lg font-semibold text-white">
                {systemStats.process_count ?? "?"}
              </div>
            </div>
            <div class="bg-slate-900/40 rounded-lg p-4 border border-slate-800">
              <div class="text-gray-400">Updated</div>
              <div class="text-lg font-semibold text-white">
                {systemStats.timestamp
                  ? new Date(systemStats.timestamp).toLocaleTimeString()
                  : "now"}
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>

    {#if dashboardData.features}
      <div>
        <h2 class="text-2xl font-bold text-white mb-4">Available Features</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each dashboardData.features as feature}
            <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div class="flex items-start justify-between mb-2">
                <h3 class="text-lg font-semibold text-white">{feature.name}</h3>
                <span
                  class={`px-2 py-1 rounded text-xs font-medium ${
                    feature.enabled
                      ? "bg-green-900 text-green-300"
                      : "bg-gray-700 text-gray-400"
                  }`}
                >
                  {feature.enabled ? "Enabled" : "Disabled"}
                </span>
              </div>
              <p class="text-sm text-gray-400">{feature.description}</p>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if githubHealth}
      <div>
        <h2 class="text-2xl font-bold text-white mb-4">GitHub Integration</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div class="flex items-start justify-between mb-2">
              <h3 class="text-lg font-semibold text-white">Health</h3>
              <span class={`px-2 py-1 rounded text-xs font-medium ${
                githubHealth.status === "ok"
                  ? "bg-green-900 text-green-300"
                  : githubHealth.status === "unavailable"
                    ? "bg-gray-700 text-gray-300"
                    : "bg-amber-900 text-amber-200"
              }`}>
                {githubHealth.status}
              </span>
            </div>
            <div class="text-sm text-gray-300 space-y-2">
              <div class="flex justify-between"><span class="text-gray-400">CLI</span><span class="font-semibold">{githubHealth.cli?.available ? "ready" : "auth needed"}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Webhook Secret</span><span class="font-semibold">{githubHealth.webhook?.secret_configured ? "configured" : "missing"}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Allowed Repo</span><span class="font-semibold">{githubHealth.repo?.allowed}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Default Branch</span><span class="font-semibold">{githubHealth.repo?.default_branch}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Push Enabled</span><span class="font-semibold">{githubHealth.repo?.push_enabled ? "yes" : "no"}</span></div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

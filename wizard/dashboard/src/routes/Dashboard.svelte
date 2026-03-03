<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount } from "svelte";
  import { getAdminToken, buildAuthHeaders } from "../lib/services/auth";

  let dashboardData = null;
  let dashboardSummary = null;
  let systemStats = null;
  let logStats = null;
  let githubHealth = null;
  let schedulerStatus = null;
  let schedulerError = null;
  let installProfile = null;
  let installMetrics = null;
  let installError = null;
  let schedulerSettings = {
    max_tasks_per_tick: 2,
    tick_seconds: 60,
    allow_network: true,
  };
  let selectedTask = null;
  let selectedTaskRuns = [];
  let taskDetailError = null;
  let selectedRun = null;
  let showRunOutput = false;
  let loading = true;
  let systemLoading = false;
  let error = null;
  let refreshTimer;
  let adminToken = "";
  let hasAdminToken = false;
  let nounQuery = "";
  let nounResults = [];
  let nounLoading = false;
  let nounError = null;
  let nounDownloadStatus = "";
  let nounCachedPath = "";
  let nounDetails = {};
  let runtimeSaveState = {};

  const authHeaders = () => buildAuthHeaders();

  const overloadLabels = {
    cpu_load_high: "CPU load is elevated",
    memory_high: "Memory usage is high",
    disk_high: "Disk usage is high",
  };

  const PLAYHOLDER = "—";

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

  const formatStatValue = (value, suffix = "") =>
    value === undefined || value === null ? "—" : `${value}${suffix}`;

  const formatRange = (used, total, unit) => {
    const safeUsed =
      used === undefined || used === null ? "—" : `${used} ${unit}`;
    const safeTotal =
      total === undefined || total === null ? "—" : `${total} ${unit}`;
    return `${safeUsed} / ${safeTotal}`;
  };

  const runtimeSourceClass = (source) => {
    if (source === "template_workspace") return "bg-emerald-900/60 text-emerald-100";
    if (source === "template_workspace_invalid") return "bg-amber-900/60 text-amber-100";
    return "bg-slate-800 text-slate-200";
  };

  const runtimeSourceLabel = (source) => {
    if (source === "template_workspace") return "Typo";
    if (source === "template_workspace_invalid") return "Typo fallback";
    if (source === "packaging_manifest") return "Manifest";
    return source || "Default";
  };

  const runtimeValue = (component, key) =>
    dashboardSummary?.workspace_runtime?.components?.[component]?.defaults?.[key]?.value || "";

  const runtimeState = (component, key) =>
    runtimeSaveState[`${component}:${key}`] || { saving: false, error: null };

  const setRuntimeState = (component, key, next) => {
    runtimeSaveState = {
      ...runtimeSaveState,
      [`${component}:${key}`]: {
        ...(runtimeSaveState[`${component}:${key}`] || { saving: false, error: null }),
        ...next,
      },
    };
  };

  async function loadDashboard() {
    loading = true;
    error = null;
    try {
      const [indexRes, summaryRes] = await Promise.all([
        apiFetch("/api/index"),
        apiFetch("/api/dashboard/summary", {
          headers: authHeaders(),
        }),
      ]);
      if (!indexRes.ok) throw new Error(`HTTP ${indexRes.status}`);
      const data = await indexRes.json();
      dashboardData = data;
      dashboardSummary = summaryRes.ok ? await summaryRes.json() : null;
      systemStats = data.system || systemStats;
      logStats = data.log_stats || null;
      await loadSchedulerStatus();
    } catch (err) {
      error = `Failed to load dashboard: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function loadGitHubHealth() {
    try {
      const res = await apiFetch("/api/github/health", {
        headers: authHeaders(),
      });
      if (res.ok) {
        githubHealth = await res.json();
      }
    } catch (err) {
      console.error("Failed to load GitHub health", err);
    }
  }

  async function loadSystemStats() {
    systemLoading = true;
    const endpoints = ["/api/system/stats", "/api/system/stats"];
    try {
      let res;
      for (const endpoint of endpoints) {
        res = await apiFetch(endpoint);
        if (res && res.ok) {
          systemStats = await res.json();
          break;
        }
      }
      if (res && !res.ok) {
        console.warn("System stats endpoint failing with", res.status);
      }
    } catch (err) {
      console.error("Failed to refresh system stats", err);
    } finally {
      systemLoading = false;
    }
  }

  async function loadSchedulerStatus() {
    try {
      const res = await apiFetch("/api/tasks/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      schedulerStatus = await res.json();
      if (schedulerStatus?.settings) {
        schedulerSettings = {
          ...schedulerSettings,
          ...schedulerStatus.settings,
        };
      }
      schedulerError = null;
    } catch (err) {
      schedulerError = `Failed to load scheduler: ${err.message}`;
      schedulerStatus = null;
    }
  }

  async function loadInstallState() {
    try {
      const res = await apiFetch("/api/setup/profiles", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      installProfile = data.install_profile || null;
      installMetrics = data.install_metrics || null;
      installError = null;
    } catch (err) {
      installError = `Failed to load installation data: ${err.message}`;
      installProfile = null;
      installMetrics = null;
    }
  }

  async function searchNounProject() {
    nounError = null;
    nounDownloadStatus = "";
    nounResults = [];
    if (!nounQuery.trim()) {
      nounError = "Enter a search term.";
      return;
    }
    nounLoading = true;
    try {
      const res = await apiFetch("/api/nounproject/search", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ term: nounQuery.trim(), limit: 12 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      nounResults = data.icons || [];
    } catch (err) {
      nounError = err.message || String(err);
    } finally {
      nounLoading = false;
    }
  }

  async function fetchNounDetails(iconId) {
    if (nounDetails[iconId]) return nounDetails[iconId];
    const res = await apiFetch(`/api/nounproject/icon/${iconId}`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    nounDetails = { ...nounDetails, [iconId]: data };
    return data;
  }

  async function openNounSvg(iconId) {
    nounError = null;
    try {
      const details = await fetchNounDetails(iconId);
      if (details?.icon_url) {
        window.open(details.icon_url, "_blank", "noopener");
      } else {
        nounError = "Icon URL unavailable.";
      }
    } catch (err) {
      nounError = err.message || String(err);
    }
  }

  async function cacheNounSvg(iconId) {
    nounError = null;
    nounDownloadStatus = "";
    nounCachedPath = "";
    try {
      const res = await apiFetch("/api/nounproject/download", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ icon_id: iconId, format: "svg" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      nounCachedPath = data?.path || "";
      nounDownloadStatus = data?.path
        ? `Cached at ${data.path}`
        : "Cached icon successfully.";
    } catch (err) {
      nounError = err.message || String(err);
    }
  }

  async function copyCachedPath() {
    if (!nounCachedPath) return;
    try {
      await navigator.clipboard.writeText(nounCachedPath);
      nounDownloadStatus = `Copied: ${nounCachedPath}`;
    } catch (err) {
      nounError = "Failed to copy path to clipboard.";
    }
  }

  async function updateSchedulerSettings() {
    try {
      const res = await apiFetch("/api/tasks/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify(schedulerSettings),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      schedulerSettings = data.settings || schedulerSettings;
      schedulerError = null;
    } catch (err) {
      schedulerError = `Failed to update scheduler: ${err.message}`;
    }
  }

  async function updateWorkspaceField(componentId, fieldName, value, key) {
    setRuntimeState(componentId, key, { saving: true, error: null });
    try {
      const res = await apiFetch(
        `/api/settings-unified/template-workspace/${componentId}/settings/field`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
          },
          body: JSON.stringify({
            field_name: fieldName,
            value,
          }),
        },
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadDashboard();
      setRuntimeState(componentId, key, { saving: false, error: null });
    } catch (err) {
      setRuntimeState(componentId, key, {
        saving: false,
        error: err.message || String(err),
      });
    }
  }

  async function loadTaskDetails(taskId) {
    taskDetailError = null;
    selectedTaskRuns = [];
    selectedTask = null;
    try {
      const [taskRes, runsRes] = await Promise.all([
        apiFetch(`/api/tasks/task/${taskId}`, { headers: authHeaders() }),
        apiFetch(`/api/tasks/runs/${taskId}?limit=5`, { headers: authHeaders() }),
      ]);
      if (!taskRes.ok) throw new Error(`Task HTTP ${taskRes.status}`);
      selectedTask = await taskRes.json();
      if (runsRes.ok) {
        selectedTaskRuns = await runsRes.json();
        selectedRun = selectedTaskRuns[0] || null;
        showRunOutput = false;
      }
    } catch (err) {
      taskDetailError = `Failed to load task details: ${err.message}`;
    }
  }

  async function copyRunOutput() {
    if (!selectedRun?.output) return;
    try {
      await navigator.clipboard.writeText(selectedRun.output);
    } catch (err) {
      console.error("Copy failed", err);
    }
  }

  onMount(() => {
    adminToken = getAdminToken();
    hasAdminToken = !!adminToken;
    loadDashboard();
    loadGitHubHealth();
    loadSchedulerStatus();
    loadInstallState();
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

  {#if !hasAdminToken}
    <div
      class="bg-amber-900/40 border border-amber-700 text-amber-100 rounded-lg p-4 text-sm"
    >
      <div class="font-semibold">Admin token missing</div>
      <div class="text-xs text-amber-200 mt-1">
        Protected endpoints (devices, logs, config, library, GitHub) will fail
        until you set an admin token on the Config page.
      </div>
    </div>
  {/if}

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
                {formatStatValue(systemStats.cpu?.load1)}
              </div>
              <div class="text-xs text-gray-400 flex justify-between">
                <span>1m</span>
                <span>5m {formatStatValue(systemStats.cpu?.load5)}</span>
                <span>15m {formatStatValue(systemStats.cpu?.load15)}</span>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                {systemStats.cpu?.count} cores
              </p>
            </div>
            <div class="bg-slate-900/60 rounded-lg p-4 border border-slate-700">
              <div class="text-gray-400 text-sm mb-1">Memory</div>
              <div class="flex items-baseline gap-2">
                <div class="text-2xl font-semibold text-white">
                  {formatStatValue(systemStats.memory?.used_percent, "%")}
                </div>
                <span class="text-xs text-gray-400"
                  >{formatRange(
                    systemStats.memory?.used_mb,
                    systemStats.memory?.total_mb,
                    "MB",
                  )}</span
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
                    {formatStatValue(systemStats.swap?.used_percent, "%")}
                  </div>
                  <span class="text-xs text-gray-400"
                    >{formatRange(
                      systemStats.swap?.used_gb,
                      systemStats.swap?.total_gb,
                      "GB",
                    )}</span
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
                  {formatStatValue(systemStats.disk?.used_percent, "%")}
                </div>
                <span class="text-xs text-gray-400"
                  >{formatRange(
                    systemStats.disk?.used_gb,
                    systemStats.disk?.total_gb,
                    "GB",
                  )}</span
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
                {formatUptime(systemStats?.uptime_seconds)}
              </div>
            </div>
            <div class="bg-slate-900/40 rounded-lg p-4 border border-slate-800">
              <div class="text-gray-400">Processes</div>
              <div class="text-lg font-semibold text-white">
                {formatStatValue(systemStats.process_count)}
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

    {#if dashboardSummary?.workspace_runtime?.components}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-5">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h3 class="text-lg font-semibold text-white">Runtime Defaults</h3>
            <p class="text-sm text-gray-400">
              Shared Typo workspace defaults across Sonic and uHOME.
            </p>
          </div>
          <div class="text-xs text-gray-400">
            {dashboardSummary.workspace_runtime.workspace_ref}
          </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <div class="bg-slate-900/50 border border-slate-700 rounded-lg p-4 space-y-3">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-white font-semibold">Sonic</div>
                <div class="text-xs text-gray-400">
                  {dashboardSummary.workspace_runtime.components.sonic.template_workspace_state?.settings?.effective_source || "default"}
                  settings layer
                </div>
              </div>
              <div class="text-xs text-gray-400">Build, boot, media</div>
            </div>

            <div class="space-y-2 text-sm">
              <div class="flex items-center justify-between gap-3">
                <span class="text-gray-400">Build profile</span>
                <div class="flex items-center gap-2">
                  <select
                    class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                    value={runtimeValue("sonic", "build_profile")}
                    disabled={runtimeState("sonic", "build_profile").saving}
                    on:change={(event) =>
                      updateWorkspaceField(
                        "sonic",
                        "preferred-profile",
                        event.currentTarget.value,
                        "build_profile",
                      )}
                  >
                    <option value="alpine-core">alpine-core</option>
                    <option value="alpine-core+sonic">alpine-core+sonic</option>
                  </select>
                  <span class={`px-2 py-1 rounded text-[11px] font-medium ${runtimeSourceClass(dashboardSummary.workspace_runtime.components.sonic.defaults.build_profile.source)}`}>
                    {runtimeSourceLabel(dashboardSummary.workspace_runtime.components.sonic.defaults.build_profile.source)}
                  </span>
                </div>
              </div>
              {#if runtimeState("sonic", "build_profile").error}
                <div class="text-xs text-red-300 text-right">
                  {runtimeState("sonic", "build_profile").error}
                </div>
              {/if}
              <div class="flex items-center justify-between gap-3">
                <span class="text-gray-400">Boot route</span>
                <div class="flex items-center gap-2">
                  <select
                    class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                    value={runtimeValue("sonic", "boot_route")}
                    disabled={runtimeState("sonic", "boot_route").saving}
                    on:change={(event) =>
                      updateWorkspaceField(
                        "sonic",
                        "preferred-boot-profile",
                        event.currentTarget.value,
                        "boot_route",
                      )}
                  >
                    <option value="udos-alpine">uDOS Alpine Core</option>
                    <option value="udos-windows-entertainment">Windows Media & Entertainment</option>
                  </select>
                  <span class={`px-2 py-1 rounded text-[11px] font-medium ${runtimeSourceClass(dashboardSummary.workspace_runtime.components.sonic.defaults.boot_route.source)}`}>
                    {runtimeSourceLabel(dashboardSummary.workspace_runtime.components.sonic.defaults.boot_route.source)}
                  </span>
                </div>
              </div>
              {#if runtimeState("sonic", "boot_route").error}
                <div class="text-xs text-red-300 text-right">
                  {runtimeState("sonic", "boot_route").error}
                </div>
              {/if}
              <div class="flex items-center justify-between gap-3">
                <span class="text-gray-400">Media launcher</span>
                <div class="flex items-center gap-2">
                  <select
                    class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                    value={runtimeValue("sonic", "media_launcher")}
                    disabled={runtimeState("sonic", "media_launcher").saving}
                    on:change={(event) =>
                      updateWorkspaceField(
                        "sonic",
                        "preferred-launcher",
                        event.currentTarget.value,
                        "media_launcher",
                      )}
                  >
                    <option value="kodi">Kodi</option>
                    <option value="wantmymtv">WantMyMTV</option>
                  </select>
                  <span class={`px-2 py-1 rounded text-[11px] font-medium ${runtimeSourceClass(dashboardSummary.workspace_runtime.components.sonic.defaults.media_launcher.source)}`}>
                    {runtimeSourceLabel(dashboardSummary.workspace_runtime.components.sonic.defaults.media_launcher.source)}
                  </span>
                </div>
              </div>
              {#if runtimeState("sonic", "media_launcher").error}
                <div class="text-xs text-red-300 text-right">
                  {runtimeState("sonic", "media_launcher").error}
                </div>
              {/if}
            </div>
          </div>

          <div class="bg-slate-900/50 border border-slate-700 rounded-lg p-4 space-y-3">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-white font-semibold">uHOME</div>
                <div class="text-xs text-gray-400">
                  {dashboardSummary.workspace_runtime.components.uhome.template_workspace_state?.settings?.effective_source || "default"}
                  settings layer
                </div>
              </div>
              <div class="text-xs text-gray-400">Presentation, node role</div>
            </div>

            <div class="space-y-2 text-sm">
              <div class="flex items-center justify-between gap-3">
                <span class="text-gray-400">Presentation</span>
                <div class="flex items-center gap-2">
                  <select
                    class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                    value={runtimeValue("uhome", "presentation")}
                    disabled={runtimeState("uhome", "presentation").saving}
                    on:change={(event) =>
                      updateWorkspaceField(
                        "uhome",
                        "presentation-mode",
                        event.currentTarget.value,
                        "presentation",
                      )}
                  >
                    <option value="thin-gui">Thin GUI</option>
                    <option value="steam-console">Steam Console</option>
                  </select>
                  <span class={`px-2 py-1 rounded text-[11px] font-medium ${runtimeSourceClass(dashboardSummary.workspace_runtime.components.uhome.defaults.presentation.source)}`}>
                    {runtimeSourceLabel(dashboardSummary.workspace_runtime.components.uhome.defaults.presentation.source)}
                  </span>
                </div>
              </div>
              {#if runtimeState("uhome", "presentation").error}
                <div class="text-xs text-red-300 text-right">
                  {runtimeState("uhome", "presentation").error}
                </div>
              {/if}
              <div class="flex items-center justify-between gap-3">
                <span class="text-gray-400">Node role</span>
                <div class="flex items-center gap-2">
                  <select
                    class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                    value={runtimeValue("uhome", "node_role")}
                    disabled={runtimeState("uhome", "node_role").saving}
                    on:change={(event) =>
                      updateWorkspaceField(
                        "uhome",
                        "node-role",
                        event.currentTarget.value,
                        "node_role",
                      )}
                  >
                    <option value="server">Server</option>
                    <option value="tv-node">TV Node</option>
                  </select>
                  <span class={`px-2 py-1 rounded text-[11px] font-medium ${runtimeSourceClass(dashboardSummary.workspace_runtime.components.uhome.defaults.node_role.source)}`}>
                    {runtimeSourceLabel(dashboardSummary.workspace_runtime.components.uhome.defaults.node_role.source)}
                  </span>
                </div>
              </div>
              {#if runtimeState("uhome", "node_role").error}
                <div class="text-xs text-red-300 text-right">
                  {runtimeState("uhome", "node_role").error}
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
    {/if}

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-lg font-semibold text-white">Noun Project</h3>
          <p class="text-sm text-gray-400">
            Search icons, preview thumbnails, and cache SVGs locally.
          </p>
        </div>
        <button
          class="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-xs"
          on:click={searchNounProject}
          disabled={nounLoading}
        >
          {nounLoading ? "Searching..." : "Search"}
        </button>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <input
          class="flex-1 min-w-[220px] bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white"
          placeholder="Search term (e.g., 'cloud', 'server', 'map')"
          bind:value={nounQuery}
          on:keydown={(e) => e.key === "Enter" && searchNounProject()}
        />
      </div>

      {#if nounError}
        <div
          class="bg-red-900/60 border border-red-700 text-red-100 p-3 rounded text-sm"
        >
          {nounError}
        </div>
      {/if}

      {#if nounDownloadStatus}
        <div
          class="bg-emerald-900/40 border border-emerald-700 text-emerald-100 p-3 rounded text-sm"
        >
          <div class="flex flex-wrap items-center gap-2">
            <span>{nounDownloadStatus}</span>
            {#if nounCachedPath}
              <button
                class="px-2 py-1 rounded bg-emerald-700 hover:bg-emerald-600 text-white text-xs"
                on:click={copyCachedPath}
              >
                Copy path
              </button>
            {/if}
          </div>
        </div>
      {/if}

      {#if nounResults.length}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each nounResults as icon}
            <div class="bg-slate-900/60 border border-slate-700 rounded-lg p-3">
              <div class="flex items-center gap-3">
                {#if icon.preview_url}
                  <img
                    src={icon.preview_url}
                    alt={icon.term}
                    class="w-12 h-12 rounded bg-slate-800 object-contain"
                  />
                {:else}
                  <div class="w-12 h-12 rounded bg-slate-800"></div>
                {/if}
                <div class="min-w-0">
                  <div class="text-white font-semibold truncate">{icon.term}</div>
                  <div class="text-xs text-gray-400 truncate">
                    {icon.uploader || "Unknown author"}
                  </div>
                </div>
              </div>
              <div class="mt-3 flex items-center gap-2">
                <button
                  class="px-2 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs"
                  on:click={() => openNounSvg(icon.id)}
                >
                  Open SVG
                </button>
                <button
                  class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-xs"
                  on:click={() => cacheNounSvg(icon.id)}
                >
                  Cache SVG
                </button>
              </div>
              {#if icon.attribution}
                <div class="mt-2 text-xs text-gray-500">
                  {icon.attribution}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {:else if nounLoading}
        <div class="text-gray-400 text-sm">Searching Noun Project...</div>
      {:else}
        <div class="text-gray-400 text-sm">
          Enter a term to search the Noun Project catalog.
        </div>
      {/if}
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-lg font-semibold text-white">Scheduler</h3>
          <p class="text-sm text-gray-400">Queued work and pacing status</p>
        </div>
        <button
          class="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-xs"
          on:click={loadSchedulerStatus}
        >
          Refresh
        </button>
      </div>

      {#if schedulerError}
        <div
          class="bg-red-900/60 border border-red-700 text-red-100 p-3 rounded text-sm"
        >
          {schedulerError}
        </div>
      {:else if schedulerStatus}
        <div
          class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300"
        >
          <div>
            <div class="text-gray-400">Pending queue</div>
            <div class="text-lg font-semibold">
              {schedulerStatus.stats?.pending_queue}
            </div>
          </div>
          <div>
            <div class="text-gray-400">Successful (24h)</div>
            <div class="text-lg font-semibold">
              {schedulerStatus.stats?.successful_today}
            </div>
          </div>
          <div>
            <div class="text-gray-400">Tasks</div>
            <div class="text-lg font-semibold">
              {Object.keys(schedulerStatus.stats?.tasks || {}).length}
            </div>
          </div>
        </div>

        <div class="mt-4 border-t border-gray-700 pt-4">
          <div class="text-sm text-gray-400 mb-2">Scheduler controls</div>
          <div
            class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-300"
          >
            <label class="flex flex-col gap-1">
              <span class="text-gray-400">Max tasks / tick</span>
              <input
                type="number"
                min="1"
                max="10"
                bind:value={schedulerSettings.max_tasks_per_tick}
                class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white"
              />
            </label>
            <label class="flex flex-col gap-1">
              <span class="text-gray-400">Tick seconds</span>
              <input
                type="number"
                min="10"
                max="3600"
                bind:value={schedulerSettings.tick_seconds}
                class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white"
              />
            </label>
            <label class="flex items-center gap-2 mt-6">
              <input
                type="checkbox"
                bind:checked={schedulerSettings.allow_network}
              />
              <span class="text-gray-400">Allow network tasks</span>
            </label>
          </div>
          <button
            class="mt-3 px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs"
            on:click={updateSchedulerSettings}
          >
            Save scheduler settings
          </button>
        </div>

        <div class="mt-4">
          <div class="text-sm text-gray-400 mb-2">Queued tasks</div>
          {#if schedulerStatus.queue?.length}
            <div class="space-y-2 text-sm">
              {#each schedulerStatus.queue.slice(0, 6) as item}
                <button
                  class="flex items-center justify-between bg-slate-900/50 border border-slate-700 rounded px-3 py-2 text-left hover:bg-slate-800/70"
                  on:click={() => loadTaskDetails(item.task_id)}
                >
                  <div>
                    <div class="font-semibold text-white">{item.name}</div>
                    <div class="text-xs text-gray-400">
                      {item.kind || "task"} • priority {item.priority} • need {item.need}
                    </div>
                  </div>
                  <div class="text-xs text-gray-400">
                    {new Date(item.scheduled_for).toLocaleString()}
                  </div>
                </button>
              {/each}
            </div>
          {:else}
            <div class="text-sm text-gray-400">No queued tasks.</div>
          {/if}
        </div>

        {#if selectedTask}
          <div class="mt-4 border-t border-gray-700 pt-4">
            <div class="text-sm text-gray-400 mb-2">Selected task</div>
            <div
              class="bg-slate-900/60 border border-slate-700 rounded p-3 text-sm text-gray-200 space-y-2"
            >
              <div class="font-semibold text-white">{selectedTask.name}</div>
              <div class="text-xs text-gray-400">
                {selectedTask.kind || "task"} • priority {selectedTask.priority}
                • need {selectedTask.need}
              </div>
              {#if selectedTask.payload}
                <pre
                  class="text-xs text-gray-300 whitespace-pre-wrap">{JSON.stringify(
                    selectedTask.payload,
                    null,
                    2,
                  )}</pre>
              {/if}
              {#if selectedTaskRuns?.length}
                <div class="text-xs text-gray-400">Recent runs</div>
                <ul class="text-xs text-gray-300 space-y-1">
                  {#each selectedTaskRuns as run}
                    <li>
                      <button
                        class="text-left hover:text-white"
                        on:click={() => {
                          selectedRun = run;
                          showRunOutput = true;
                        }}
                      >
                        {run.created_at} → {run.result ||
                          run.state ||
                          "pending"}
                      </button>
                    </li>
                  {/each}
                </ul>
              {/if}
              {#if selectedRun}
                <div class="mt-3">
                  <button
                    class="text-xs text-gray-300 hover:text-white border border-slate-700 rounded px-2 py-1"
                    on:click={() => (showRunOutput = !showRunOutput)}
                  >
                    {showRunOutput ? "Hide run output" : "Show run output"}
                  </button>
                  {#if showRunOutput}
                    <div class="mt-2 flex items-center justify-between">
                      <div class="text-xs text-gray-400">Run output</div>
                      <button
                        class="text-xs text-gray-300 hover:text-white border border-slate-700 rounded px-2 py-1"
                        on:click={copyRunOutput}
                      >
                        Copy
                      </button>
                    </div>
                    <pre class="text-xs text-gray-300 whitespace-pre-wrap">
{selectedRun.output || "No output"}
                    </pre>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
        {:else if taskDetailError}
          <div class="mt-4 text-sm text-red-300">{taskDetailError}</div>
        {/if}
      {:else}
        <div class="text-sm text-gray-400">Loading scheduler status...</div>
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
              <span
                class={`px-2 py-1 rounded text-xs font-medium ${
                  githubHealth.status === "ok"
                    ? "bg-green-900 text-green-300"
                    : githubHealth.status === "unavailable"
                      ? "bg-gray-700 text-gray-300"
                      : "bg-amber-900 text-amber-200"
                }`}
              >
                {githubHealth.status}
              </span>
            </div>
            <div class="text-sm text-gray-300 space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-400">CLI</span><span
                  class="font-semibold"
                  >{githubHealth.cli?.available ? "ready" : "auth needed"}</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Webhook Secret</span><span
                  class="font-semibold"
                  >{githubHealth.webhook?.secret_configured
                    ? "configured"
                    : "missing"}</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Allowed Repo</span><span
                  class="font-semibold">{githubHealth.repo?.allowed}</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Default Branch</span><span
                  class="font-semibold"
                  >{githubHealth.repo?.default_branch}</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Push Enabled</span><span
                  class="font-semibold"
                  >{githubHealth.repo?.push_enabled ? "yes" : "no"}</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

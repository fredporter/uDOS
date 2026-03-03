<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount } from "svelte";
  import TerminalPanel from "$lib/components/terminal/TerminalPanel.svelte";
  import TerminalButton from "$lib/components/terminal/TerminalButton.svelte";

  let logs = [];
  let categories = [];
  let selectedCategory = "all";
  let limit = 200;
  let loading = true;
  let error = null;
  let stats = null;
  let logHealth = null;
  let lastUpdated = null;
  let autoRefresh = true;
  let refreshMs = 10000;
  let timer;
  let adminToken = "";
  let needsAdminToken = false;
  let initialLoadFailed = false;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function fetchWithTimeout(url, options = {}, timeoutMs = 5000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await apiFetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  async function bootstrapAdminToken() {
    if (adminToken) return true;
    try {
      const res = await fetchWithTimeout("/api/admin-token/status");
      if (!res.ok) return false;
      const data = await res.json();
      const token = data?.env?.WIZARD_ADMIN_TOKEN;
      if (token) {
        adminToken = token;
        localStorage.setItem("wizardAdminToken", token);
        return true;
      }
    } catch (err) {
      return false;
    }
    return false;
  }

  const levelTone = (level) => {
    const lvl = (level || "").toUpperCase();
    if (lvl === "ERROR" || lvl === "CRITICAL")
      return "bg-red-900/60 text-red-100";
    if (lvl === "WARNING" || lvl === "WARN")
      return "bg-amber-900/60 text-amber-100";
    if (lvl === "DEBUG") return "bg-slate-800 text-slate-200";
    return "bg-emerald-900/60 text-emerald-100";
  };

  const formatTimestamp = (value) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  };

  const formatBool = (value) => (value ? "Yes" : "No");

  async function loadLogs(retry = true) {
    loading = true;
    error = null;
    needsAdminToken = false;
    try {
      const hasToken = await bootstrapAdminToken();
      if (!hasToken) {
        needsAdminToken = true;
        throw new Error("Admin token required");
      }
      const [logsRes, statusRes] = await Promise.all([
        fetchWithTimeout(
          `/api/logs?category=${encodeURIComponent(selectedCategory)}&limit=${limit}`,
          { headers: authHeaders() },
          7000,
        ),
        fetchWithTimeout("/api/logs/status", { headers: authHeaders() }, 7000),
      ]);
      if (!logsRes.ok) {
        if (logsRes.status === 401 || logsRes.status === 403) {
          localStorage.removeItem("wizardAdminToken");
          adminToken = "";
          if (retry) {
            const refreshed = await bootstrapAdminToken();
            if (refreshed) {
              return loadLogs(false);
            }
          }
          needsAdminToken = true;
          throw new Error("Admin token required");
        }
        throw new Error(`HTTP ${logsRes.status}`);
      }
      const data = await logsRes.json();
      logs = Array.isArray(data.logs) ? data.logs : [];
      categories = Array.isArray(data.categories) ? data.categories : [];
      stats = data.stats || null;
      if (statusRes.ok) {
        const statusPayload = await statusRes.json();
        logHealth = statusPayload.health || null;
        stats = statusPayload.stats || stats;
      } else {
        logHealth = null;
      }
      lastUpdated = new Date();
    } catch (err) {
      error = `Failed to load logs: ${err.message}`;
      initialLoadFailed = true;
      stopTimer();
    } finally {
      loading = false;
    }
  }

  function stopTimer() {
    if (timer) clearInterval(timer);
  }

  function restartTimer() {
    stopTimer();
    if (autoRefresh && !initialLoadFailed) {
      timer = setInterval(loadLogs, refreshMs);
    }
  }

  function handleCategoryChange(event) {
    selectedCategory = event.target.value;
    loadLogs();
    restartTimer();
  }

  function handleLimitChange(event) {
    const value = parseInt(event.target.value, 10);
    if (!Number.isNaN(value) && value > 0) {
      limit = value;
      loadLogs();
      restartTimer();
    }
  }

  function toggleAutoRefresh() {
    autoRefresh = !autoRefresh;
    restartTimer();
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadLogs();
    restartTimer();
  });

  onDestroy(() => {
    stopTimer();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Logs</h1>
      <p class="text-gray-400">Monitor Wizard server activity and hotspots</p>
    </div>
    <div class="flex items-center gap-3">
      <TerminalButton
        className="px-4 py-2 text-sm font-semibold"
        variant={autoRefresh ? "success" : "neutral"}
        on:click={toggleAutoRefresh}
      >
        {autoRefresh ? "Auto-refresh on" : "Auto-refresh off"}
      </TerminalButton>
      <TerminalButton
        className="px-4 py-2 text-sm font-semibold"
        variant="accent"
        on:click={loadLogs}
      >
        Refresh now
      </TerminalButton>
    </div>
  </div>

  <div class="wiz-terminal-panel p-4 flex flex-wrap gap-3 text-sm text-gray-200">
    <label class="flex items-center gap-2">
      <span class="text-gray-400">Category</span>
      <select
        class="wiz-terminal-input px-3 py-2 text-sm text-white"
        bind:value={selectedCategory}
        on:change={handleCategoryChange}
      >
        <option value="all">All</option>
        {#each categories as cat}
          <option value={cat}>{cat}</option>
        {/each}
      </select>
    </label>

    <label class="flex items-center gap-2">
      <span class="text-gray-400">Limit</span>
      <input
        class="wiz-terminal-input px-3 py-2 text-sm text-white w-24"
        type="number"
        min="10"
        max="500"
        step="10"
        value={limit}
        on:change={handleLimitChange}
      />
    </label>

    {#if lastUpdated}
      <span class="text-gray-400"
        >Last updated {lastUpdated.toLocaleTimeString()}</span
      >
    {/if}
  </div>

  {#if error}
    <div class="bg-red-900 text-red-100 border border-red-700 rounded-lg p-4">
      <div class="font-semibold">{error}</div>
      {#if needsAdminToken}
        <div class="mt-2 text-sm text-red-200">
          Generate an admin token in Config → Admin Token, then refresh this
          page.
        </div>
        <TerminalButton
          className="mt-3 inline-flex items-center px-3 py-2 text-xs font-semibold"
          variant="danger"
          on:click={() => (window.location.hash = "#config")}
        >
          Open Config
        </TerminalButton>
      {/if}
    </div>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="wiz-terminal-panel p-4 text-gray-200">
      <div class="text-gray-400 text-sm">Entries loaded</div>
      <div class="text-2xl font-semibold">{logs.length}</div>
    </div>
    <div class="wiz-terminal-panel p-4 text-gray-200">
      <div class="text-gray-400 text-sm">Log files</div>
      <div class="text-2xl font-semibold">{stats?.total_files ?? "-"}</div>
      <div class="text-xs text-gray-400">
        {stats?.total_size_mb ?? "-"} MB stored
      </div>
    </div>
    <div class="wiz-terminal-panel p-4 text-gray-200">
      <div class="text-gray-400 text-sm">Categories</div>
      <div class="text-2xl font-semibold">{categories.length}</div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="wiz-terminal-panel p-4 text-gray-200 space-y-3">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="text-gray-400 text-sm">Logging Contract</div>
          <div class="text-xl font-semibold">{logHealth?.schema ?? "udos-log-v1.5"}</div>
        </div>
        <div class="text-right">
          <div class="text-gray-400 text-sm">Runtime</div>
          <div class="font-semibold">{logHealth?.runtime_version ?? "-"}</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 text-sm">
        <div>
          <div class="text-gray-400">Level</div>
          <div>{logHealth?.level ?? "-"}</div>
        </div>
        <div>
          <div class="text-gray-400">Destination</div>
          <div>{logHealth?.dest ?? "-"}</div>
        </div>
        <div>
          <div class="text-gray-400">Format</div>
          <div>{logHealth?.format ?? "-"}</div>
        </div>
        <div>
          <div class="text-gray-400">Payloads</div>
          <div>{logHealth?.payloads ?? "-"}</div>
        </div>
        <div>
          <div class="text-gray-400">Redaction</div>
          <div>{formatBool(logHealth?.redact)}</div>
        </div>
        <div>
          <div class="text-gray-400">Ring</div>
          <div>{logHealth?.ring_entries ?? "-"} / {logHealth?.ring_size ?? "-"}</div>
        </div>
      </div>

      <div class="text-xs text-gray-500 break-all">
        Root: {logHealth?.root ?? stats?.root ?? "-"}
      </div>
    </div>

    <div class="wiz-terminal-panel p-4 text-gray-200 space-y-3">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="text-gray-400 text-sm">Log Tree</div>
          <div class="text-xl font-semibold">{stats?.total_files ?? "-"}</div>
        </div>
        <div class="text-right">
          <div class="text-gray-400 text-sm">Size</div>
          <div class="font-semibold">{stats?.total_size_mb ?? "-"} MB</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 text-sm">
        <div>
          <div class="text-gray-400">Latest file</div>
          <div class="break-all">{stats?.latest_file ?? "-"}</div>
        </div>
        <div>
          <div class="text-gray-400">Generated</div>
          <div>{formatTimestamp(stats?.generated_at ?? "")}</div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="text-gray-400 text-sm">By component</div>
        {#if stats?.by_component}
          {#each Object.entries(stats.by_component) as [component, componentStats]}
            <div class="flex items-center justify-between gap-3 text-sm border-t border-gray-800 pt-2">
              <div class="font-semibold">{component}</div>
              <div class="text-gray-400">
                {componentStats.count} files · {componentStats.size_mb} MB
              </div>
            </div>
          {/each}
        {:else}
          <div class="text-sm text-gray-500">No component stats available.</div>
        {/if}
      </div>
    </div>
  </div>

  <TerminalPanel title="Latest log entries">
    <svelte:fragment slot="header-actions">
      {#if loading}
        <span class="text-gray-500 text-sm">Loading…</span>
      {/if}
    </svelte:fragment>
    <div class="wiz-terminal-log divide-y divide-gray-800">
      {#if !loading && logs.length === 0}
        <div class="text-gray-500 px-4 py-6 text-sm">
          No log entries available for this filter.
        </div>
      {:else}
        {#each logs as log (log.timestamp + log.message)}
          <div class="px-4 py-3 space-y-1">
            <div class="flex items-center justify-between gap-3 text-sm">
              <div class="flex items-center gap-2">
                <span class={`px-2 py-1 rounded ${levelTone(log.level)}`}
                  >{log.level}</span
                >
                <span class="text-gray-300 font-semibold">{log.category}</span>
                {#if log.source}
                  <span class="text-gray-500 text-xs">{log.source}</span>
                {/if}
              </div>
              <span class="text-gray-400 text-xs"
                >{formatTimestamp(log.timestamp)}</span
              >
            </div>
            <div
              class="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap"
            >
              {log.message}
            </div>
            <div class="text-gray-500 text-xs">{log.file}</div>
          </div>
        {/each}
      {/if}
    </div>
  </TerminalPanel>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

<script>
  import { onDestroy, onMount } from "svelte";

  let logs = [];
  let categories = [];
  let selectedCategory = "all";
  let limit = 200;
  let loading = true;
  let error = null;
  let stats = null;
  let lastUpdated = null;
  let autoRefresh = true;
  let refreshMs = 10000;
  let timer;
  let adminToken = "";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};


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

  async function loadLogs() {
    loading = true;
    error = null;
    try {
      const res = await fetch(
        `/api/v1/logs?category=${encodeURIComponent(selectedCategory)}&limit=${limit}`,
        { headers: authHeaders() },
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      logs = data.logs || [];
      categories = data.categories || [];
      stats = data.stats || null;
      lastUpdated = new Date();
    } catch (err) {
      error = `Failed to load logs: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  function restartTimer() {
    if (timer) clearInterval(timer);
    if (autoRefresh) {
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
    if (timer) clearInterval(timer);
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Logs</h1>
      <p class="text-gray-400">Monitor Wizard server activity and hotspots</p>
    </div>
    <div class="flex items-center gap-3">
      <button
        class={`px-4 py-2 rounded-lg text-sm font-semibold ${
          autoRefresh
            ? "bg-emerald-700 hover:bg-emerald-600 text-white"
            : "bg-slate-700 hover:bg-slate-600 text-white"
        }`}
        on:click={toggleAutoRefresh}
      >
        {autoRefresh ? "Auto-refresh on" : "Auto-refresh off"}
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
        on:click={loadLogs}
      >
        Refresh now
      </button>
    </div>
  </div>

  <div
    class="bg-gray-800 border border-gray-700 rounded-lg p-4 flex flex-wrap gap-3 text-sm text-gray-200"
  >
    <label class="flex items-center gap-2">
      <span class="text-gray-400">Category</span>
      <select
        class="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-white"
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
        class="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-white w-24"
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
      {error}
    </div>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div
      class="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-gray-200"
    >
      <div class="text-gray-400 text-sm">Entries loaded</div>
      <div class="text-2xl font-semibold">{logs.length}</div>
    </div>
    <div
      class="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-gray-200"
    >
      <div class="text-gray-400 text-sm">Log files</div>
      <div class="text-2xl font-semibold">{stats?.total_files ?? "-"}</div>
      <div class="text-xs text-gray-400">
        {stats?.total_size_mb ?? "-"} MB stored
      </div>
    </div>
    <div
      class="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-gray-200"
    >
      <div class="text-gray-400 text-sm">Categories</div>
      <div class="text-2xl font-semibold">{categories.length}</div>
    </div>
  </div>

  <div class="bg-gray-900 border border-gray-800 rounded-lg">
    <div
      class="border-b border-gray-800 px-4 py-3 flex items-center justify-between text-sm text-gray-300"
    >
      <span>Latest log entries</span>
      {#if loading}
        <span class="text-gray-500">Loading…</span>
      {/if}
    </div>
    <div class="divide-y divide-gray-800">
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
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

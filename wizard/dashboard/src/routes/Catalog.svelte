<script>
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";

  let adminToken = "";
  let stats = null;
  let categories = [];
  let plugins = [];
  let loading = true;
  let error = null;
  let categoryFilter = "";
  let searchQuery = "";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function togglePlugin(pluginId, currentlyEnabled) {
    const action = currentlyEnabled ? "disable" : "enable";
    try {
      const res = await apiFetch(`/api/catalog/plugins/${pluginId}/${action}`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await refreshCatalog();
    } catch (err) {
      error = `Failed to ${action} plugin: ${err.message}`;
    }
  }

  async function loadStats() {
    const res = await apiFetch("/api/catalog/stats", { headers: authHeaders() });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error("Admin token required");
      }
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    stats = data.stats || null;
  }

  async function loadCategories() {
    const res = await apiFetch("/api/catalog/categories", {
      headers: authHeaders(),
    });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error("Admin token required");
      }
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    categories = data.categories || [];
  }

  async function loadPlugins() {
    const params = new URLSearchParams();
    if (categoryFilter) params.set("category", categoryFilter);
    const suffix = params.toString();
    const res = await apiFetch(
      `/api/catalog/plugins${suffix ? `?${suffix}` : ""}`,
      { headers: authHeaders() },
    );
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error("Admin token required");
      }
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    plugins = data.plugins || [];
  }

  async function searchPlugins() {
    if (!searchQuery) {
      await loadPlugins();
      return;
    }
    const params = new URLSearchParams();
    params.set("q", searchQuery);
    const res = await apiFetch(`/api/catalog/search?${params.toString()}`, {
      headers: authHeaders(),
    });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error("Admin token required");
      }
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    plugins = data.plugins || [];
  }

  async function refreshCatalog() {
    loading = true;
    error = null;
    try {
      await loadStats();
      await loadCategories();
      await loadPlugins();
    } catch (err) {
      const message = err?.message || "Unknown error";
      if (message.includes("NetworkError")) {
        error =
          "Failed to load catalog: Wizard API unreachable. Check VITE_WIZARD_API_BASE or wizardApiBase in localStorage.";
      } else {
        error = `Failed to load catalog: ${message}`;
      }
    } finally {
      loading = false;
    }
  }

  function handleSearchKey(event) {
    if (event.key === "Enter") {
      searchPlugins();
    }
  }

  $: if (categoryFilter) {
    searchQuery = "";
    loadPlugins();
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    await refreshCatalog();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Plugin Catalog</h1>
  <p class="text-gray-400 mb-8">Browse and verify plugin packages</p>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700"
    >
      {error}
    </div>
  {/if}

  {#if stats}
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p class="text-xs text-gray-400 uppercase">Total</p>
        <p class="text-2xl font-bold text-white">{stats.total_plugins}</p>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p class="text-xs text-gray-400 uppercase">Installed</p>
        <p class="text-2xl font-bold text-white">{stats.installed}</p>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p class="text-xs text-gray-400 uppercase">Updates</p>
        <p class="text-2xl font-bold text-white">{stats.updates_available}</p>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p class="text-xs text-gray-400 uppercase">Categories</p>
        <p class="text-2xl font-bold text-white">{stats.categories}</p>
      </div>
    </div>
  {/if}

  <div
    class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6"
  >
    <div class="flex gap-2 flex-wrap">
      <input
        type="text"
        class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
        placeholder="Search plugins"
        bind:value={searchQuery}
        on:keydown={handleSearchKey}
      />
      <button
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm"
        on:click={searchPlugins}
      >
        Search
      </button>
      <button
        class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white text-sm"
        on:click={refreshCatalog}
      >
        Refresh
      </button>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-xs text-gray-400 uppercase">Category</span>
      <select
        bind:value={categoryFilter}
        class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
      >
        <option value="">All</option>
        {#each categories as category}
          <option value={category}>{category}</option>
        {/each}
      </select>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading catalog...</div>
  {:else if plugins.length === 0}
    <div class="text-center py-12 text-gray-400">No plugins found</div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each plugins as plugin}
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-5">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h2 class="text-lg font-semibold text-white">{plugin.name}</h2>
              <p class="text-xs text-gray-400">{plugin.id}</p>
            </div>
            <span
              class="text-xs px-2 py-1 rounded-full bg-gray-700 text-gray-300"
            >
              {plugin.version}
            </span>
          </div>
          <p class="text-sm text-gray-300 mb-3">{plugin.description}</p>
          <div class="text-xs text-gray-400 space-y-1 mb-4">
            <div>Category: {plugin.category || "—"}</div>
            <div>License: {plugin.license || "—"}</div>
            <div>
              Status: {plugin.installed ? "Installed" : "Available"}
              {plugin.update_available ? "(Update available)" : ""}
            </div>
            <div class="flex items-center gap-2 mt-2">
              <span class="text-xs">Enabled:</span>
              <button
                class="px-3 py-1 rounded text-xs {plugin.enabled
                  ? 'bg-green-700 hover:bg-green-600 text-white'
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-300'}"
                on:click={() => togglePlugin(plugin.id, plugin.enabled)}
              >
                {plugin.enabled ? "ON" : "OFF"}
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <div class="h-32"></div>
</div>

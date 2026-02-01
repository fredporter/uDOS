<script>
  import { onMount } from "svelte";

  let adminToken = "";
  let plugins = [];
  let loading = true;
  let error = null;
  let selectedPlugin = null;
  let viewMode = "grid"; // grid | list | tiers | categories
  let filterTier = "";
  let filterCategory = "";
  let searchQuery = "";
  let installing = {};

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function loadCatalog() {
    try {
      const res = await fetch("/api/v1/plugins/catalog", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      plugins = Object.values(data.plugins || {});
      return plugins;
    } catch (err) {
      error = `Failed to load catalog: ${err.message}`;
      return [];
    }
  }

  async function loadByTier() {
    try {
      const res = await fetch("/api/v1/plugins/tiers", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      // Flatten tiers for display
      plugins = [];
      for (const [tier, tiers_plugins] of Object.entries(data.tiers || {})) {
        plugins.push(...tiers_plugins);
      }
      return plugins;
    } catch (err) {
      error = `Failed to load by tier: ${err.message}`;
      return [];
    }
  }

  async function loadByCategory() {
    try {
      const res = await fetch("/api/v1/plugins/categories", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      // Flatten categories for display
      plugins = [];
      for (const [cat, cat_plugins] of Object.entries(data.categories || {})) {
        plugins.push(...cat_plugins);
      }
      return plugins;
    } catch (err) {
      error = `Failed to load by category: ${err.message}`;
      return [];
    }
  }

  async function searchPlugins() {
    if (!searchQuery.trim()) {
      await loadCatalog();
      return;
    }

    try {
      const res = await fetch(
        `/api/v1/plugins/search?q=${encodeURIComponent(searchQuery)}`,
        { headers: authHeaders() },
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      plugins = data.plugins || [];
    } catch (err) {
      error = `Search failed: ${err.message}`;
    }
  }

  async function getPluginDetails(pluginId) {
    try {
      const res = await fetch(`/api/v1/plugins/${pluginId}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      selectedPlugin = data.plugin;
    } catch (err) {
      error = `Failed to load plugin details: ${err.message}`;
    }
  }

  async function installPlugin(pluginId) {
    installing[pluginId] = true;
    try {
      const res = await fetch(`/api/v1/plugins/${pluginId}/install`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      console.log(`Install started for ${pluginId}:`, data.message);

      // Refresh catalog after a delay
      setTimeout(() => loadCatalog(), 2000);
    } catch (err) {
      error = `Installation failed: ${err.message}`;
    } finally {
      installing[pluginId] = false;
    }
  }

  async function pullPluginUpdates(pluginId) {
    installing[pluginId] = true;
    try {
      const res = await fetch(`/api/v1/plugins/${pluginId}/git/pull`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      console.log(`Update started for ${pluginId}:`, data.message);

      // Refresh details after a delay
      if (selectedPlugin?.id === pluginId) {
        setTimeout(() => getPluginDetails(pluginId), 2000);
      }
    } catch (err) {
      error = `Update failed: ${err.message}`;
    } finally {
      installing[pluginId] = false;
    }
  }

  function getTierLabel(tier) {
    return (
      {
        core: "📦 Core",
        library: "📚 Library",
        extension: "🔌 Extension",
        transport: "📡 Transport",
        api: "🔗 API",
      }[tier] || tier
    );
  }

  function getCategoryBadge(category) {
    const badges = {
      plugin: "🎯",
      container: "📦",
      transport: "📡",
      api: "🔗",
      editor: "📝",
      ai: "🤖",
      home_automation: "🏠",
      music_production: "🎵",
    };
    return (badges[category] || "📌") + " " + (category || "unknown");
  }

  function handleSearchKey(event) {
    if (event.key === "Enter") {
      searchPlugins();
    }
  }

  async function refreshAll() {
    loading = true;
    error = null;
    await loadCatalog();
    loading = false;
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    await refreshAll();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-white mb-2">🧙 Plugin Catalog</h1>
    <p class="text-gray-400">
      Browse, install, and manage all uDOS extensions, containers, and plugins
    </p>
  </div>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700"
    >
      {error}
      <button
        class="ml-4 px-3 py-1 bg-red-700 hover:bg-red-600 rounded text-sm"
        on:click={() => (error = null)}
      >
        Dismiss
      </button>
    </div>
  {/if}

  <!-- Controls -->
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div>
        <input
          type="text"
          placeholder="Search plugins, containers, extensions..."
          bind:value={searchQuery}
          on:keydown={handleSearchKey}
          class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400"
        />
      </div>
      <div class="flex gap-2">
        <button
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium"
          on:click={searchPlugins}
        >
          Search
        </button>
        <button
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white text-sm font-medium"
          on:click={refreshAll}
        >
          Refresh
        </button>
      </div>
    </div>

    <!-- View Mode & Filters -->
    <div class="flex flex-wrap gap-2 items-center">
      <span class="text-xs uppercase text-gray-400">View:</span>
      <button
        class={`px-3 py-1 rounded text-xs ${
          viewMode === "grid"
            ? "bg-blue-600 text-white"
            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
        }`}
        on:click={() => {
          viewMode = "grid";
          loadCatalog();
        }}
      >
        Grid
      </button>
      <button
        class={`px-3 py-1 rounded text-xs ${
          viewMode === "list"
            ? "bg-blue-600 text-white"
            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
        }`}
        on:click={() => {
          viewMode = "list";
          loadCatalog();
        }}
      >
        List
      </button>
      <button
        class={`px-3 py-1 rounded text-xs ${
          viewMode === "tiers"
            ? "bg-blue-600 text-white"
            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
        }`}
        on:click={() => {
          viewMode = "tiers";
          loadByTier();
        }}
      >
        By Tier
      </button>
      <button
        class={`px-3 py-1 rounded text-xs ${
          viewMode === "categories"
            ? "bg-blue-600 text-white"
            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
        }`}
        on:click={() => {
          viewMode = "categories";
          loadByCategory();
        }}
      >
        By Category
      </button>
    </div>
  </div>

  <!-- Loading State -->
  {#if loading}
    <div class="text-center py-12">
      <div class="text-gray-400">Loading plugins...</div>
    </div>
  {:else if plugins.length === 0}
    <div class="text-center py-12">
      <div class="text-gray-400">No plugins found</div>
    </div>
  {:else if viewMode === "grid"}
    <!-- Grid View -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each plugins as plugin (plugin.id)}
        <div
          class="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-blue-500 transition cursor-pointer"
          on:click={() => getPluginDetails(plugin.id)}
        >
          <div class="flex items-start justify-between mb-3">
            <div>
              <h3 class="text-lg font-semibold text-white">{plugin.name}</h3>
              <p class="text-xs text-gray-400">
                {plugin.id} · v{plugin.version}
              </p>
            </div>
            <span class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">
              {getTierLabel(plugin.tier)}
            </span>
          </div>

          <p class="text-sm text-gray-300 mb-4">{plugin.description}</p>

          <div class="flex flex-wrap gap-1 mb-4">
            <span class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">
              {getCategoryBadge(plugin.category)}
            </span>
            {#if plugin.installed}
              <span
                class="px-2 py-1 rounded text-xs bg-green-900 text-green-300"
              >
                ✅ Installed
              </span>
            {:else}
              <span
                class="px-2 py-1 rounded text-xs bg-yellow-900 text-yellow-300"
              >
                ⬇️ Available
              </span>
            {/if}
          </div>

          {#if plugin.git}
            <div class="text-xs text-gray-400 mb-3 space-y-1">
              {#if plugin.git.remote_url}
                <div class="truncate">
                  🔗 {plugin.git.remote_url
                    .replace(/.*\//, "")
                    .replace(".git", "")}
                </div>
              {/if}
              {#if plugin.git.commit_hash}
                <div>📌 {plugin.git.commit_hash}</div>
              {/if}
              {#if plugin.git.is_dirty}
                <div class="text-orange-400">⚠️ Modified</div>
              {/if}
            </div>
          {/if}

          <div class="flex gap-2">
            {#if !plugin.installed}
              <button
                class="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white text-xs font-medium disabled:opacity-50"
                disabled={installing[plugin.id]}
                on:click={(e) => {
                  e.stopPropagation();
                  installPlugin(plugin.id);
                }}
              >
                {installing[plugin.id] ? "Installing..." : "Install"}
              </button>
            {:else if plugin.git && plugin.git.remote_url}
              <button
                class="flex-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white text-xs font-medium disabled:opacity-50"
                disabled={installing[plugin.id]}
                on:click={(e) => {
                  e.stopPropagation();
                  pullPluginUpdates(plugin.id);
                }}
              >
                {installing[plugin.id] ? "Updating..." : "Update"}
              </button>
            {/if}
            <button
              class="flex-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white text-xs font-medium"
              on:click={(e) => {
                e.stopPropagation();
                getPluginDetails(plugin.id);
              }}
            >
              Details
            </button>
          </div>
        </div>
      {/each}
    </div>
  {:else if viewMode === "list"}
    <!-- List View -->
    <div class="space-y-2">
      {#each plugins as plugin (plugin.id)}
        <div
          class="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition flex items-center justify-between cursor-pointer"
          on:click={() => getPluginDetails(plugin.id)}
        >
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-1">
              <span class="font-semibold text-white">{plugin.name}</span>
              <span
                class="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300"
              >
                v{plugin.version}
              </span>
              <span class="text-xs text-gray-400"
                >{getCategoryBadge(plugin.category)}</span
              >
            </div>
            <p class="text-sm text-gray-400">{plugin.description}</p>
            {#if plugin.git?.remote_url}
              <p class="text-xs text-gray-500 mt-1">
                🔗 {plugin.git.remote_url}
              </p>
            {/if}
          </div>
          <div class="flex gap-2 ml-4">
            {#if !plugin.installed}
              <button
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm font-medium disabled:opacity-50"
                disabled={installing[plugin.id]}
                on:click={(e) => {
                  e.stopPropagation();
                  installPlugin(plugin.id);
                }}
              >
                {installing[plugin.id] ? "..." : "Install"}
              </button>
            {:else if plugin.git?.remote_url}
              <button
                class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm font-medium disabled:opacity-50"
                disabled={installing[plugin.id]}
                on:click={(e) => {
                  e.stopPropagation();
                  pullPluginUpdates(plugin.id);
                }}
              >
                {installing[plugin.id] ? "..." : "Update"}
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Details Panel -->
  {#if selectedPlugin}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    >
      <div
        class="bg-gray-900 border border-gray-700 rounded-lg max-w-2xl w-full max-h-96 overflow-auto"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold text-white">
                {selectedPlugin.name}
              </h2>
              <p class="text-sm text-gray-400">
                {selectedPlugin.id} v{selectedPlugin.version}
              </p>
            </div>
            <button
              class="text-gray-400 hover:text-white text-2xl"
              on:click={() => (selectedPlugin = null)}
            >
              ✕
            </button>
          </div>

          <p class="text-gray-300 mb-4">{selectedPlugin.description}</p>

          <div class="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div>
              <p class="text-gray-400">Tier</p>
              <p class="text-white font-medium">
                {getTierLabel(selectedPlugin.tier)}
              </p>
            </div>
            <div>
              <p class="text-gray-400">Category</p>
              <p class="text-white font-medium">{selectedPlugin.category}</p>
            </div>
            <div>
              <p class="text-gray-400">License</p>
              <p class="text-white font-medium">{selectedPlugin.license}</p>
            </div>
            <div>
              <p class="text-gray-400">Installation Type</p>
              <p class="text-white font-medium">
                {selectedPlugin.installer_type}
              </p>
            </div>
          </div>

          {#if selectedPlugin.git}
            <div class="bg-gray-800 rounded p-3 mb-4">
              <h4 class="text-white font-semibold mb-2">Git Info</h4>
              <div class="text-xs text-gray-300 space-y-1">
                {#if selectedPlugin.git.remote_url}
                  <div>
                    <span class="text-gray-500">Remote:</span>
                    {selectedPlugin.git.remote_url}
                  </div>
                {/if}
                {#if selectedPlugin.git.commit_hash}
                  <div>
                    <span class="text-gray-500">Commit:</span>
                    {selectedPlugin.git.commit_hash}
                  </div>
                {/if}
                {#if selectedPlugin.git.commit_date}
                  <div>
                    <span class="text-gray-500">Updated:</span>
                    {selectedPlugin.git.commit_date}
                  </div>
                {/if}
                <div>
                  <span class="text-gray-500">Status:</span>
                  {selectedPlugin.git.is_dirty ? "⚠️ Modified" : "✅ Clean"}
                </div>
              </div>
            </div>
          {/if}

          {#if selectedPlugin.dependencies?.length}
            <div class="mb-4">
              <h4 class="text-white font-semibold mb-2">Dependencies</h4>
              <div class="flex flex-wrap gap-2">
                {#each selectedPlugin.dependencies as dep}
                  <span
                    class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300"
                  >
                    {dep}
                  </span>
                {/each}
              </div>
            </div>
          {/if}

          <div class="flex gap-2 pt-4 border-t border-gray-700">
            {#if selectedPlugin.homepage}
              <a
                href={selectedPlugin.homepage}
                target="_blank"
                class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm font-medium text-center"
              >
                Homepage
              </a>
            {/if}
            {#if selectedPlugin.documentation}
              <a
                href={selectedPlugin.documentation}
                target="_blank"
                class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm font-medium text-center"
              >
                Docs
              </a>
            {/if}
            <button
              class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm font-medium"
              on:click={() => (selectedPlugin = null)}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <div class="h-32"></div>
</div>

<style>
  :global(body) {
    background-color: #1a1a1a;
  }
</style>

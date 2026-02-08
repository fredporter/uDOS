<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";
  import { onMount, createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let extensions = [];
  let summary = null;
  let loading = true;
  let error = null;
  let empireTokenStatus = null;

  async function loadExtensions() {
    try {
      const res = await apiFetch("/api/extensions/list", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      extensions = data.extensions || [];
      summary = data.summary || null;
      loading = false;
    } catch (err) {
      error = `Failed to load extensions: ${err.message}`;
      loading = false;
    }
  }

  async function loadEmpireStatus() {
    try {
      const res = await apiFetch("/api/extensions/empire/token-status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) return;
      empireTokenStatus = await res.json();
    } catch (err) {
      console.error("Failed to load Empire status:", err);
    }
  }

  function navigateTo(route) {
    window.location.hash = route;
  }

  function openEmpireWeb() {
    const port = 8991;
    window.open(`http://127.0.0.1:${port}`, "_blank");
  }

  onMount(() => {
    loadExtensions();
    loadEmpireStatus();
  });

  // Group by category
  $: groupedExtensions = extensions.reduce((acc, ext) => {
    const cat = ext.category || "other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(ext);
    return acc;
  }, {});

  const categoryLabels = {
    business: "Business & Commercial",
    developer: "Developer Tools",
    audio: "Audio & Media",
    utilities: "Utilities & Tools",
    other: "Other",
  };

  const categoryOrder = ["business", "developer", "audio", "utilities", "other"];
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Extensions</h1>
  <p class="text-gray-400 mb-8">Official uDOS extensions installed on this system</p>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading extensions...</div>
  {:else}
    <!-- Summary Bar -->
    {#if summary}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6 flex items-center gap-6">
        <div class="flex items-center gap-2">
          <span class="text-2xl">📦</span>
          <span class="text-gray-300">{summary.present} of {summary.total} extensions installed</span>
        </div>
        {#if summary.missing > 0}
          <span class="text-gray-500 text-sm">
            ({summary.missing} not installed)
          </span>
        {/if}
      </div>
    {/if}

    <!-- Extension Cards by Category -->
    {#each categoryOrder as category}
      {#if groupedExtensions[category]?.length > 0}
        <div class="mb-8">
          <h2 class="text-xl font-semibold text-gray-300 mb-4">{categoryLabels[category]}</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each groupedExtensions[category] as ext}
              <div
                class="bg-gray-800 border rounded-lg p-5 transition-all {ext.present
                  ? 'border-gray-600 hover:border-blue-500'
                  : 'border-gray-700 opacity-60'}"
              >
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-3">
                    <span class="text-3xl">{ext.icon}</span>
                    <div>
                      <h3 class="text-lg font-semibold text-white">{ext.name}</h3>
                      {#if ext.present}
                        <span class="text-xs text-green-400">v{ext.version || "dev"}</span>
                      {:else}
                        <span class="text-xs text-gray-500">Not installed</span>
                      {/if}
                    </div>
                  </div>
                  <div
                    class="w-3 h-3 rounded-full {ext.present ? 'bg-green-500' : 'bg-gray-600'}"
                    title={ext.present ? "Installed" : "Not installed"}
                  ></div>
                </div>

                <p class="text-gray-400 text-sm mb-4">{ext.description}</p>

                {#if ext.present}
                  <div class="flex items-center gap-2 flex-wrap">
                    {#if ext.id === "empire"}
                      <!-- Empire-specific actions -->
                      {#if empireTokenStatus?.token_configured}
                        <button
                          class="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                          on:click={openEmpireWeb}
                        >
                          Open Empire
                        </button>
                      {:else}
                        <button
                          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                          on:click={openEmpireWeb}
                        >
                          Configure Token
                        </button>
                      {/if}
                      <span class="text-xs text-gray-500">
                        {#if empireTokenStatus?.token_configured}
                          ✓ Token configured
                        {:else}
                          ⚠ Token not set
                        {/if}
                      </span>
                    {:else if ext.id === "dev"}
                      <button
                        class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
                        on:click={() => navigateTo("devmode")}
                      >
                        Open Dev Mode
                      </button>
                    {:else if ext.id === "groovebox"}
                      <button
                        class="px-3 py-1.5 bg-pink-600 hover:bg-pink-700 text-white text-sm rounded transition-colors"
                        on:click={() => navigateTo("groovebox")}
                      >
                        Open Groovebox
                      </button>
                    {:else if ext.id === "sonic"}
                      <span class="text-xs text-gray-500">Coming soon</span>
                    {/if}
                  </div>
                {:else}
                  <div class="text-xs text-gray-500">
                    Install this extension to enable features
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    {/each}

    <!-- Info Note -->
    <div class="mt-8 p-4 bg-gray-900 border border-gray-700 rounded-lg">
      <p class="text-gray-400 text-sm">
        <strong class="text-gray-300">Note:</strong> Extensions are private submodules.
        Contact your administrator or check the uDOS documentation to install missing extensions.
      </p>
    </div>
  {/if}
</div>

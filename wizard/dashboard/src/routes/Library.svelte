<script>
  import { onMount } from "svelte";

  let libraryData = null;
  let loading = true;
  let error = null;
  let filterStatus = "all"; // all, installed, available, enabled
  let actionInProgress = null; // Track which action is in progress

  async function loadLibrary() {
    loading = true;
    error = null;
    try {
      const res = await fetch("/api/v1/library/status");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      libraryData = await res.json();
    } catch (err) {
      error = `Failed to load library: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function installIntegration(name) {
    actionInProgress = `install-${name}`;
    try {
      const res = await fetch(`/api/v1/library/integration/${name}/install`, {
        method: "POST",
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary(); // Refresh data
      } else {
        alert(`❌ Install failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Install failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function enableIntegration(name) {
    actionInProgress = `enable-${name}`;
    try {
      const res = await fetch(`/api/v1/library/integration/${name}/enable`, {
        method: "POST",
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Enable failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Enable failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function disableIntegration(name) {
    actionInProgress = `disable-${name}`;
    try {
      const res = await fetch(`/api/v1/library/integration/${name}/disable`, {
        method: "POST",
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Disable failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Disable failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function uninstallIntegration(name) {
    if (!confirm(`Are you sure you want to uninstall ${name}?`)) return;

    actionInProgress = `uninstall-${name}`;
    try {
      const res = await fetch(`/api/v1/library/integration/${name}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Uninstall failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Uninstall failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  function getFilteredIntegrations() {
    if (!libraryData) return [];
    const integrations = libraryData.integrations || [];

    switch (filterStatus) {
      case "installed":
        return integrations.filter((i) => i.installed);
      case "available":
        return integrations.filter((i) => !i.installed && i.can_install);
      case "enabled":
        return integrations.filter((i) => i.enabled);
      default:
        return integrations;
    }
  }

  const statusColor = (integration) => {
    if (integration.enabled) return "bg-green-900 text-green-100";
    if (integration.installed) return "bg-blue-900 text-blue-100";
    return "bg-slate-700 text-slate-200";
  };

  const statusLabel = (integration) => {
    if (integration.enabled) return "✅ Enabled";
    if (integration.installed) return "📦 Installed";
    return "⏳ Available";
  };

  const sourceIcon = (source) => {
    return source === "library" ? "📦" : "🔧";
  };

  onMount(loadLibrary);
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Library</h1>
      <p class="text-gray-400">Integrations and plugins</p>
    </div>
    <button
      class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
      on:click={loadLibrary}
    >
      Refresh
    </button>
  </div>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading library...</div>
  {:else if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
      {error}
    </div>
  {:else if libraryData}
    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Total Available</div>
        <div class="text-2xl font-bold text-white">
          {libraryData.total_integrations}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Installed</div>
        <div class="text-2xl font-bold text-blue-400">
          {libraryData.installed_count}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Enabled</div>
        <div class="text-2xl font-bold text-green-400">
          {libraryData.enabled_count}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Not Installed</div>
        <div class="text-2xl font-bold text-amber-400">
          {(libraryData.integrations || []).filter(
            (i) => !i.installed && i.can_install,
          ).length}
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex gap-2 flex-wrap">
      {#each ["all", "installed", "available", "enabled"] as status}
        <button
          class={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            filterStatus === status
              ? "bg-indigo-600 text-white"
              : "bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700"
          }`}
          on:click={() => (filterStatus = status)}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </button>
      {/each}
    </div>

    <!-- Integrations grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each getFilteredIntegrations() as integration (integration.name)}
        <div
          class="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition space-y-3"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span>{sourceIcon(integration.source)}</span>
                <h3 class="text-lg font-semibold text-white">
                  {integration.name}
                </h3>
              </div>
              {#if integration.version}
                <p class="text-xs text-gray-500">v{integration.version}</p>
              {/if}
            </div>
            <span
              class={`px-2.5 py-1 rounded text-xs font-semibold whitespace-nowrap ${statusColor(integration)}`}
            >
              {statusLabel(integration)}
            </span>
          </div>

          {#if integration.description}
            <p class="text-sm text-gray-400">{integration.description}</p>
          {/if}

          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span
              >{integration.source === "library"
                ? "📁 /library"
                : "🔧 /dev/library"}</span
            >
            {#if integration.has_container}
              <span>⚙️ Configured</span>
            {/if}
          </div>

          <div class="flex gap-2">
            {#if integration.enabled}
              <button
                class="flex-1 px-3 py-1.5 rounded-lg bg-orange-600 hover:bg-orange-500 text-white text-xs font-medium disabled:opacity-50"
                on:click={() => disableIntegration(integration.name)}
                disabled={actionInProgress !== null}
              >
                {actionInProgress === `disable-${integration.name}`
                  ? "..."
                  : "Disable"}
              </button>
              <button
                class="flex-1 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-medium disabled:opacity-50"
                on:click={() => uninstallIntegration(integration.name)}
                disabled={actionInProgress !== null}
              >
                {actionInProgress === `uninstall-${integration.name}`
                  ? "..."
                  : "Uninstall"}
              </button>
            {:else if integration.installed}
              <button
                class="flex-1 px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-xs font-medium disabled:opacity-50"
                on:click={() => enableIntegration(integration.name)}
                disabled={actionInProgress !== null}
              >
                {actionInProgress === `enable-${integration.name}`
                  ? "..."
                  : "Enable"}
              </button>
              <button
                class="flex-1 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-medium disabled:opacity-50"
                on:click={() => uninstallIntegration(integration.name)}
                disabled={actionInProgress !== null}
              >
                {actionInProgress === `uninstall-${integration.name}`
                  ? "..."
                  : "Uninstall"}
              </button>
            {:else if integration.can_install}
              <button
                class="flex-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium disabled:opacity-50"
                on:click={() => installIntegration(integration.name)}
                disabled={actionInProgress !== null}
              >
                {actionInProgress === `install-${integration.name}`
                  ? "..."
                  : "Install"}
              </button>
            {:else}
              <span
                class="flex-1 px-3 py-1.5 rounded-lg bg-slate-700 text-slate-400 text-xs text-center"
              >
                Not Available
              </span>
            {/if}
          </div>
        </div>
      {/each}
    </div>

    {#if getFilteredIntegrations().length === 0}
      <div class="text-center py-12 text-gray-400">
        No integrations found for this filter
      </div>
    {/if}
  {/if}
</div>

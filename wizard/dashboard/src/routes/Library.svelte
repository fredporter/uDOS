<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount } from "svelte";

  let libraryData = null;
  let loading = true;
  let error = null;
  let filterStatus = "all"; // all, installed, available, enabled
  let actionInProgress = null; // Track which action is in progress
  let adminToken = "";
  let inventoryData = null;
  let reposData = [];
  let packagesData = [];
  let apkStatus = null;
  let containers = [];
  let containerMap = {};
  let containerError = null;
  let toolchainPackages =
    "python3 py3-pip py3-setuptools py3-wheel py3-virtualenv";
  let toolchainResult = null;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function loadLibrary() {
    loading = true;
    error = null;
    try {
      const res = await apiFetch("/api/library/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      libraryData = await res.json();
    } catch (err) {
      error = `Failed to load library: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function loadInventory() {
    try {
      const res = await apiFetch("/api/library/inventory", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      inventoryData = data.inventory || {};
    } catch (err) {
      inventoryData = null;
    }
  }

  async function loadRepos() {
    try {
      const res = await apiFetch("/api/library/repos", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      reposData = data.repos || [];
    } catch (err) {
      reposData = [];
    }
  }

  async function loadPackages() {
    try {
      const res = await apiFetch("/api/library/packages", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      packagesData = data.packages || [];
    } catch (err) {
      packagesData = [];
    }
  }

  async function loadApkStatus() {
    try {
      const res = await apiFetch("/api/library/apk/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      apkStatus = data;
    } catch (err) {
      apkStatus = { success: false, error: err.message };
    }
  }

  async function loadContainers() {
    containerError = null;
    try {
      const res = await apiFetch("/api/containers/list/available", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      containers = data.containers || [];
      containerMap = containers.reduce((acc, item) => {
        acc[item.id] = item;
        return acc;
      }, {});
    } catch (err) {
      containerError = err.message || String(err);
      containers = [];
      containerMap = {};
    }
  }

  async function installIntegration(name) {
    actionInProgress = `install-${name}`;
    try {
      const res = await apiFetch(`/api/library/integration/${name}/install`, {
        method: "POST",
        headers: authHeaders(),
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
      const res = await apiFetch(`/api/library/integration/${name}/enable`, {
        method: "POST",
        headers: authHeaders(),
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
      const res = await apiFetch(`/api/library/integration/${name}/disable`, {
        method: "POST",
        headers: authHeaders(),
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
      const res = await apiFetch(`/api/library/integration/${name}`, {
        method: "DELETE",
        headers: authHeaders(),
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

  async function updateRepo(name) {
    actionInProgress = `repo-update-${name}`;
    try {
      const res = await apiFetch(`/api/library/repos/${name}/update`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadRepos();
    } catch (err) {
      alert(`❌ Update failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function buildRepo(name, format = "tar.gz") {
    actionInProgress = `repo-build-${name}-${format}`;
    try {
      const res = await apiFetch(
        `/api/library/repos/${name}/build?format=${format}`,
        {
          method: "POST",
          headers: authHeaders(),
        },
      );
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Build failed");
      await loadPackages();
    } catch (err) {
      alert(`❌ Build failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function buildApk(name) {
    actionInProgress = `repo-build-apk-${name}`;
    try {
      const res = await apiFetch(`/api/library/repos/${name}/build-apk`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "APK build failed");
      await loadPackages();
    } catch (err) {
      alert(`❌ APK build failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function generateApkIndex() {
    actionInProgress = "apk-index";
    try {
      const res = await apiFetch("/api/library/apk/index", {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "APKINDEX failed");
      await loadApkStatus();
    } catch (err) {
      alert(`❌ APKINDEX failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function updateToolchain() {
    actionInProgress = "toolchain";
    toolchainResult = null;
    try {
      const packages = toolchainPackages
        .split(" ")
        .map((p) => p.trim())
        .filter(Boolean);
      const res = await apiFetch("/api/library/toolchain/update", {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ packages }),
      });
      const data = await res.json();
      toolchainResult = data.result || data;
    } catch (err) {
      toolchainResult = { success: false, message: err.message };
    } finally {
      actionInProgress = null;
    }
  }

  async function refreshAll() {
    await Promise.all([
      loadLibrary(),
      loadInventory(),
      loadRepos(),
      loadPackages(),
      loadApkStatus(),
      loadContainers(),
    ]);
  }

  async function launchContainer(containerId) {
    actionInProgress = `container-launch-${containerId}`;
    try {
      const res = await apiFetch(`/api/containers/${containerId}/launch`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadContainers();
    } catch (err) {
      alert(`❌ Launch failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function stopContainer(containerId) {
    actionInProgress = `container-stop-${containerId}`;
    try {
      const res = await apiFetch(`/api/containers/${containerId}/stop`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadContainers();
    } catch (err) {
      alert(`❌ Stop failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  function openContainer(container) {
    if (!container?.browser_route) return;
    window.open(container.browser_route, "_blank");
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    if (adminToken) {
      refreshAll();
    } else {
      loadLibrary();
    }
    loadContainers();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Library</h1>
      <p class="text-gray-400">Integrations and plugins</p>
    </div>
    <div class="flex gap-2">
      <button
        class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
        on:click={refreshAll}
      >
        Refresh All
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-sm font-semibold border border-gray-700"
        on:click={loadLibrary}
      >
        Refresh Library
      </button>
    </div>
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

    <!-- APK Status + Toolchain -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-400">APK Status</div>
          <button
            class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
            on:click={loadApkStatus}
          >
            Refresh
          </button>
        </div>
        {#if apkStatus?.success}
          <div class="text-sm text-white">
            abuild: {apkStatus.abuild ? "ok" : "missing"}
          </div>
          <div class="text-sm text-white">
            apk: {apkStatus.apk ? "ok" : "missing"}
          </div>
          <div class="text-xs text-gray-400">
            signing: {apkStatus.signing?.ok ? "ok" : "missing"} ({apkStatus.signing?.detail})
          </div>
        {:else if apkStatus}
          <div class="text-xs text-red-400">Failed to load APK status</div>
        {:else}
          <div class="text-xs text-gray-500">No status yet</div>
        {/if}
        <button
          class="w-full mt-2 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-xs text-white"
          on:click={generateApkIndex}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "apk-index" ? "..." : "Generate APKINDEX"}
        </button>
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="text-sm text-gray-400">Toolchain Update (Alpine)</div>
        <input
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white"
          bind:value={toolchainPackages}
        />
        <button
          class="w-full px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-xs text-white"
          on:click={updateToolchain}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "toolchain" ? "..." : "Update Toolchain"}
        </button>
        {#if toolchainResult}
          <div
            class={`text-xs ${toolchainResult.success ? "text-emerald-400" : "text-red-400"}`}
          >
            {toolchainResult.message || "Done"}
          </div>
        {/if}
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="text-sm text-gray-400">Inventory</div>
        <div class="text-xs text-gray-500">
          {Object.keys(inventoryData || {}).length} integrations with deps
        </div>
        <button
          class="w-full px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadInventory}
        >
          Refresh Inventory
        </button>
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

    <!-- Repo Inventory -->
    <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-white">Library Repos</h2>
        <button
          class="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadRepos}
        >
          Refresh
        </button>
      </div>
      {#if reposData.length === 0}
        <div class="text-xs text-gray-500">No repos found</div>
      {:else}
        <div class="space-y-2">
          {#each reposData as repo}
            <div class="flex items-center justify-between bg-gray-800 border border-gray-700 rounded px-3 py-2">
              <div class="text-sm text-white">{repo.name}</div>
              <div class="flex gap-2">
                <button
                  class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
                  on:click={() => updateRepo(repo.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-update-${repo.name}` ? "..." : "Update"}
                </button>
                <button
                  class="px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-xs text-white"
                  on:click={() => buildRepo(repo.name, "tar.gz")}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-build-${repo.name}-tar.gz` ? "..." : "Build"}
                </button>
                <button
                  class="px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-xs text-white"
                  on:click={() => buildApk(repo.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-build-apk-${repo.name}` ? "..." : "Build APK"}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Packages -->
    <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-white">Built Packages</h2>
        <button
          class="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadPackages}
        >
          Refresh
        </button>
      </div>
      {#if packagesData.length === 0}
        <div class="text-xs text-gray-500">No packages yet</div>
      {:else}
        <div class="space-y-2">
          {#each packagesData as pkg}
            <div class="flex items-center justify-between bg-gray-800 border border-gray-700 rounded px-3 py-2">
              <div class="text-sm text-white">{pkg.filename}</div>
              <div class="text-xs text-gray-400">{pkg.size_bytes || 0} bytes</div>
            </div>
          {/each}
        </div>
      {/if}
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
            {#if containerMap[integration.name]}
              <span>🧩 Container</span>
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

          {#if containerMap[integration.name]}
            {@const container = containerMap[integration.name]}
            <div class="flex items-center justify-between text-xs text-gray-400">
              <span>
                Container: {container.running ? "Running" : "Stopped"}
              </span>
              {#if container.port}
                <span>Port {container.port}</span>
              {/if}
            </div>
            <div class="flex gap-2">
              {#if container.running}
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => stopContainer(container.id)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `container-stop-${container.id}`
                    ? "..."
                    : "Stop"}
                </button>
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => openContainer(container)}
                >
                  Open
                </button>
              {:else}
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => launchContainer(container.id)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `container-launch-${container.id}`
                    ? "..."
                    : "Launch"}
                </button>
              {/if}
            </div>
          {/if}
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

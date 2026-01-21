<script>
  import { onMount } from "svelte";

  let dashboardData = null;
  let loading = true;
  let error = null;

  async function loadDashboard() {
    try {
      const res = await fetch("/api/v1/index");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      dashboardData = await res.json();
      loading = false;
    } catch (err) {
      error = `Failed to load dashboard: ${err.message}`;
      loading = false;
    }
  }

  onMount(loadDashboard);
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Dashboard</h1>
  <p class="text-gray-400 mb-8">uDOS Wizard server status and configuration</p>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading dashboard...</div>
  {:else if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
      {error}
    </div>
  {:else if dashboardData}
    <!-- Server Status -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <div class="mb-4">
        <h3 class="text-lg font-semibold text-white mb-2">Server Status</h3>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-green-500"></div>
          <span class="text-sm text-gray-300">Server is running</span>
        </div>
      </div>

      {#if dashboardData.dashboard}
        <div class="space-y-2 text-sm text-gray-400">
          <p>
            <span class="font-medium">Name:</span>
            {dashboardData.dashboard.name}
          </p>
          <p>
            <span class="font-medium">Version:</span>
            {dashboardData.dashboard.version}
          </p>
          <p>
            <span class="font-medium">Updated:</span>
            {new Date(dashboardData.dashboard.timestamp).toLocaleString()}
          </p>
        </div>
      {/if}
    </div>

    <!-- Features -->
    {#if dashboardData.features}
      <h2 class="text-2xl font-bold text-white mb-6">Available Features</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each dashboardData.features as feature}
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div class="flex items-start justify-between mb-2">
              <h3 class="text-lg font-semibold text-white">{feature.name}</h3>
              <span
                class="px-2 py-1 rounded text-xs font-medium {feature.enabled
                  ? 'bg-green-900 text-green-300'
                  : 'bg-gray-700 text-gray-400'}"
              >
                {feature.enabled ? "Enabled" : "Disabled"}
              </span>
            </div>
            <p class="text-sm text-gray-400">{feature.description}</p>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

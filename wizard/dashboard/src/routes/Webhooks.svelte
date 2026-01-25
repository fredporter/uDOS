<script>
  import { onMount } from "svelte";

  let adminToken = "";
  let status = null;
  let error = null;
  let loading = true;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  async function loadStatus() {
    loading = true;
    error = null;
    try {
      const res = await fetch("/api/v1/webhooks/status", {
        headers: authHeaders(),
      });
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          throw new Error("Admin token required");
        }
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      status = data;
    } catch (err) {
      error = `Failed to load webhook status: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  function copyText(text) {
    navigator.clipboard.writeText(text);
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadStatus();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Webhooks</h1>
  <p class="text-gray-400 mb-8">Webhook endpoints and configuration status</p>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="text-gray-400">Loading webhook status...</div>
  {:else if status}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {#each Object.entries(status.webhooks || {}) as [name, config]}
        <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-xl font-semibold text-white">{name}</h2>
            <span
              class="px-2 py-1 text-xs rounded-full {config.secret_configured
                ? 'bg-green-900 text-green-300'
                : 'bg-red-900 text-red-300'}"
            >
              {config.secret_configured ? "Secret configured" : "Secret missing"}
            </span>
          </div>
          <p class="text-sm text-gray-400 mb-4">
            Endpoint:
            <span class="text-gray-200">{config.url}</span>
          </p>
          <div class="flex gap-2">
            <button
              class="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-white text-sm"
              on:click={() => copyText(config.url)}
            >
              Copy URL
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-4">
            Secret source: {config.secret_source}
          </p>
        </div>
      {/each}
    </div>
  {/if}

  <div class="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <h2 class="text-lg font-semibold text-white mb-2">Notes</h2>
    <ul class="text-sm text-gray-400 space-y-1">
      <li>• GitHub webhooks require the X-Hub-Signature-256 header.</li>
      <li>• Notion webhooks use NOTION_WEBHOOK_SECRET in the Wizard environment.</li>
      <li>• Base URL is derived from the Wizard host/port configuration.</li>
    </ul>
  </div>

  <div class="h-32"></div>
</div>

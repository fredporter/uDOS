<script>
  import { onMount } from "svelte";

  let syncStatus = null;
  let queue = [];
  let mappings = [];
  let loading = true;
  let error = null;

  async function loadStatus() {
    try {
      const res = await fetch("/api/v1/notion/sync/status");
      if (res.ok) {
        syncStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load status:", err);
    }
  }

  async function loadQueue() {
    try {
      const res = await fetch("/api/v1/notion/sync/queue");
      if (res.ok) {
        queue = await res.json();
      }
    } catch (err) {
      console.error("Failed to load queue:", err);
    }
  }

  async function loadMappings() {
    try {
      const res = await fetch("/api/v1/notion/sync/mappings");
      if (res.ok) {
        mappings = await res.json();
      }
      loading = false;
    } catch (err) {
      error = `Failed to load mappings: ${err.message}`;
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
    loadQueue();
    loadMappings();
    const interval = setInterval(() => {
      loadStatus();
      loadQueue();
    }, 10000); // Poll every 10s
    return () => clearInterval(interval);
  });

  function getStatusClass(status) {
    switch (status) {
      case "completed":
        return "bg-green-900 text-green-200 border-green-700";
      case "processing":
        return "bg-blue-900 text-blue-200 border-blue-700";
      case "failed":
        return "bg-red-900 text-red-200 border-red-700";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }

  function getEventTypeIcon(eventType) {
    switch (eventType) {
      case "page_created":
        return "📄";
      case "page_updated":
        return "✏️";
      case "page_deleted":
        return "🗑️";
      default:
        return "📌";
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Notion Sync</h1>
  <p class="text-gray-400 mb-8">Bidirectional Notion ↔ Markdown synchronization</p>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6">
      {error}
    </div>
  {/if}

  <!-- Sync Status -->
  {#if syncStatus}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">Sync Status</h3>
      <div class="grid grid-cols-3 gap-4 text-sm">
        <div>
          <span class="text-gray-400">Pending:</span>
          <span class="text-white ml-2">{syncStatus.pending || 0}</span>
        </div>
        <div>
          <span class="text-gray-400">Processing:</span>
          <span class="text-white ml-2">{syncStatus.processing || 0}</span>
        </div>
        <div>
          <span class="text-gray-400">Last Sync:</span>
          <span class="text-white ml-2">
            {syncStatus.last_sync
              ? new Date(syncStatus.last_sync).toLocaleString()
              : "Never"}
          </span>
        </div>
      </div>
    </div>
  {/if}

  <!-- Sync Queue -->
  {#if queue.length > 0}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">
        Sync Queue ({queue.length})
      </h3>
      <div class="space-y-2">
        {#each queue as item}
          <div class="bg-gray-900 border border-gray-700 rounded p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-2xl">{getEventTypeIcon(item.event_type)}</span>
                <div>
                  <div class="text-white font-medium">{item.page_title || "Untitled"}</div>
                  <div class="text-gray-400 text-xs">{item.event_type}</div>
                </div>
              </div>
              <span
                class="px-2 py-1 rounded text-xs border {getStatusClass(item.status)}"
              >
                {item.status}
              </span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Block Mappings -->
  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading mappings...</div>
  {:else}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-white mb-4">
        Block Mappings ({mappings.length})
      </h3>
      {#if mappings.length === 0}
        <p class="text-gray-400 text-center py-8">
          No mappings yet. Sync a Notion page to create mappings.
        </p>
      {:else}
        <div class="space-y-2">
          {#each mappings as mapping}
            <div class="bg-gray-900 border border-gray-700 rounded p-3">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="text-white text-sm font-mono">
                    {mapping.local_path}
                  </div>
                  <div class="text-gray-400 text-xs mt-1">
                    Notion Block: {mapping.notion_block_id.slice(0, 12)}...
                  </div>
                </div>
                <div class="text-xs text-gray-500">
                  {new Date(mapping.last_synced).toLocaleString()}
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

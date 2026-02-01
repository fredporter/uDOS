<script>
  import { onMount } from "svelte";
  import { mappingStore, exportMappings } from "$lib/stores/mappingStore";

  let syncStatus = null;
  let queue = [];
  let mappings = [];
  let loading = true;
  let error = null;
  let mappingExportMessage = "";

  async function copyMappingExport() {
    try {
      const payload = exportMappings();
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(payload);
      }
      mappingExportMessage = "Mapping export copied to clipboard.";
      setTimeout(() => (mappingExportMessage = ""), 3000);
    } catch (err) {
      mappingExportMessage =
        err instanceof Error ? err.message : "Failed to copy mapping export.";
    }
  }

  async function loadStatus() {
    try {
      const res = await fetch("/api/notion/sync/status");
      if (res.ok) {
        syncStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load status:", err);
    }
  }

  async function loadQueue() {
    try {
      const res = await fetch("/api/notion/sync/queue");
      if (res.ok) {
        queue = await res.json();
      }
    } catch (err) {
      console.error("Failed to load queue:", err);
    }
  }

  async function loadMappings() {
    try {
      const res = await fetch("/api/notion/sync/mappings");
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
  <p class="text-gray-400 mb-8">
    Bidirectional Notion ↔ Markdown synchronization
  </p>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
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
                <span class="text-2xl">{getEventTypeIcon(item.event_type)}</span
                >
                <div>
                  <div class="text-white font-medium">
                    {item.page_title || "Untitled"}
                  </div>
                  <div class="text-gray-400 text-xs">{item.event_type}</div>
                </div>
              </div>
              <span
                class="px-2 py-1 rounded text-xs border {getStatusClass(
                  item.status,
                )}"
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

  <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mt-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">Round 3 Slot Mappings</h3>
      <button class="text-xs text-blue-300" on:click={copyMappingExport}>
        Export JSON
      </button>
    </div>
    {#if mappingExportMessage}
      <div class="text-sm text-emerald-300 mb-2">{mappingExportMessage}</div>
    {/if}
    {#if $mappingStore.mappings.length === 0}
      <p class="text-gray-400 text-sm">
        No runtime slots have been mapped yet. Use the Round 3 mapper to assign Notion blocks to slots.
      </p>
    {:else}
      <div class="space-y-3">
        {#each $mappingStore.mappings as entry}
          <div class="bg-gray-900 border border-gray-700 rounded p-3 flex flex-col gap-1">
            <div class="flex items-center justify-between text-xs text-gray-400">
              <span>Slot</span>
              <span>{entry.slot}</span>
            </div>
            <div class="text-sm text-white font-mono break-all">
              {entry.blockId}
            </div>
            <p class="text-gray-300 text-sm">
              Note: {entry.note || "no note yet"}
            </p>
            <p class="text-gray-500 text-xs">
              {entry.blockType || "block"} · {entry.runtimeType || "runtime"} ·
              Mapped at {new Date(entry.lastMapped).toLocaleString()}
            </p>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

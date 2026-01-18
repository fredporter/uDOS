<script lang="ts">
  import { onMount } from 'svelte';
  import { syncStatus, refreshSyncStatus } from '../stores/syncStore';

  let isOpen = false;

  onMount(() => {
    // Initial status fetch
    refreshSyncStatus();

    // Refresh every 5 seconds
    const interval = setInterval(refreshSyncStatus, 5000);
    return () => clearInterval(interval);
  });

  function getStatusColor(): string {
    if (!$syncStatus.isConnected) return 'bg-gray-400';
    if ($syncStatus.isHealthy) return 'bg-green-500';
    if ($syncStatus.errorCount > 0) return 'bg-red-500';
    return 'bg-yellow-500';
  }

  function getStatusIcon(): string {
    if (!$syncStatus.isConnected) return '⚪';
    if ($syncStatus.isHealthy) return '🟢';
    if ($syncStatus.errorCount > 0) return '🔴';
    return '🟡';
  }
</script>

<!-- Sync Status Indicator Badge -->
<div class="relative">
  <!-- Status Dot -->
  <button
    on:click={() => (isOpen = !isOpen)}
    class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
    title={$syncStatus.message}
  >
    <span class="text-lg">{getStatusIcon()}</span>
    <span class="text-xs font-mono text-gray-700">{$syncStatus.pendingCount}</span>
  </button>

  <!-- Popover Details -->
  {#if isOpen}
    <div
      class="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4"
    >
      <!-- Header -->
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-sm">Notion Sync Status</h3>
        <button
          on:click={() => (isOpen = false)}
          class="text-gray-500 hover:text-gray-700 text-lg"
        >
          ×
        </button>
      </div>

      <!-- Status Info -->
      <div class="space-y-2 text-xs">
        <!-- Connection -->
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Connection:</span>
          <span class={$syncStatus.isConnected ? 'text-green-600 font-mono' : 'text-red-600'}>
            {$syncStatus.isConnected ? '✓ Connected' : '✗ Disconnected'}
          </span>
        </div>

        <!-- Mode -->
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Mode:</span>
          <span class="font-mono text-purple-600">{$syncStatus.mode}</span>
        </div>

        <!-- Queue Status -->
        <div class="border-t pt-2">
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Pending:</span>
            <span class="font-mono font-semibold">{$syncStatus.pendingCount}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Errors:</span>
            <span class="font-mono" class:text-red-600={$syncStatus.errorCount > 0}>
              {$syncStatus.errorCount}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Conflicts:</span>
            <span class="font-mono" class:text-orange-600={$syncStatus.conflictCount > 0}>
              {$syncStatus.conflictCount}
            </span>
          </div>
        </div>

        <!-- Last Sync -->
        {#if $syncStatus.lastSync}
          <div class="border-t pt-2">
            <div class="text-gray-600">Last sync: {$syncStatus.lastSync}</div>
          </div>
        {/if}

        <!-- Message -->
        {#if $syncStatus.message}
          <div class="border-t pt-2">
            <div class="text-gray-700">{$syncStatus.message}</div>
          </div>
        {/if}
      </div>

      <!-- Actions -->
      <div class="border-t mt-3 pt-3 flex gap-2">
        <button
          on:click={() => {
            refreshSyncStatus();
          }}
          class="flex-1 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
        >
          Refresh
        </button>
        <a
          href="http://localhost:8766/docs"
          target="_blank"
          rel="noopener"
          class="flex-1 px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
        >
          API Docs
        </a>
      </div>
    </div>
  {/if}
</div>

<!-- Click outside to close -->
<svelte:window
  on:click={(e) => {
    const target = e.target;
    if (target && !target.closest('.relative') && isOpen) {
      isOpen = false;
    }
  }}
/>

<style>
  :global(body) {
    --sync-color-healthy: #10b981;
    --sync-color-warning: #f59e0b;
    --sync-color-error: #ef4444;
    --sync-color-offline: #9ca3af;
  }
</style>

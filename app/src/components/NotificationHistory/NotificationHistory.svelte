<script lang="ts">
  import { onMount } from 'svelte';
  import { createHistoryStore, type Notification, type SearchFilters } from '$lib/notification-db';
  import NotificationHistoryItem from './NotificationHistoryItem.svelte';
  import ExportModal from './ExportModal.svelte';

  const historyStore = createHistoryStore();

  let showExportModal = false;
  let searchQuery = '';
  let selectedType = '';
  let selectedPage = 0;
  let stats: any = null;

  onMount(async () => {
    // Load first page
    await historyStore.load(0);
    
    // Load stats
    stats = await historyStore.getStats();
  });

  async function handleSearch() {
    const filters: SearchFilters = {
      query: searchQuery || undefined,
      type: selectedType || undefined,
      limit: 50,
    };
    await historyStore.search(filters);
    selectedPage = 0;
  }

  async function handlePrevPage() {
    if (selectedPage > 0) {
      selectedPage--;
      await historyStore.load(selectedPage);
    }
  }

  async function handleNextPage() {
    const state = get(historyStore);
    if ((selectedPage + 1) * state.pageSize < state.total) {
      selectedPage++;
      await historyStore.load(selectedPage);
    }
  }

  async function handleDelete(id: string) {
    if (confirm('Delete this notification?')) {
      await historyStore.delete(id);
    }
  }

  async function handleClearOld() {
    if (confirm('Delete notifications older than 30 days?')) {
      await historyStore.clearOld(30);
    }
  }

  function get(store: any) {
    let value;
    store.subscribe((v: any) => (value = v))();
    return value;
  }
</script>

<div class="notification-history">
  <!-- Header -->
  <div class="history-header">
    <h2>Notification History</h2>
    <button on:click={() => (showExportModal = true)} class="btn-secondary">Export</button>
  </div>

  <!-- Stats -->
  {#if stats}
    <div class="stats-bar">
      <div class="stat">
        <span class="label">Total</span>
        <span class="value">{stats.total}</span>
      </div>
      {#each Object.entries(stats.by_type || {}) as [type, count]}
        <div class="stat">
          <span class="label">{type}</span>
          <span class="value {type}">{count}</span>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Search & Filter -->
  <div class="search-controls">
    <input
      type="text"
      placeholder="Search notifications..."
      bind:value={searchQuery}
      on:keydown={(e) => e.key === 'Enter' && handleSearch()}
      class="search-input"
    />
    
    <select bind:value={selectedType} class="type-filter">
      <option value="">All Types</option>
      <option value="info">Info</option>
      <option value="success">Success</option>
      <option value="warning">Warning</option>
      <option value="error">Error</option>
      <option value="progress">Progress</option>
    </select>

    <button on:click={handleSearch} class="btn-primary">Search</button>
    <button on:click={handleClearOld} class="btn-danger">Clear Old (30d)</button>
  </div>

  <!-- Notifications List -->
  <div class="history-list">
    {#if $historyStore.loading}
      <div class="loading">Loading...</div>
    {:else if $historyStore.notifications.length === 0}
      <div class="empty">No notifications found</div>
    {:else}
      {#each $historyStore.notifications as notification (notification.id)}
        <NotificationHistoryItem
          {notification}
          onDelete={() => handleDelete(notification.id)}
        />
      {/each}
    {/if}
  </div>

  <!-- Pagination -->
  {#if $historyStore.total > 0}
    <div class="pagination">
      <button
        on:click={handlePrevPage}
        disabled={selectedPage === 0}
        class="btn-secondary"
      >
        ← Previous
      </button>

      <span class="page-info">
        Page {selectedPage + 1} of {Math.ceil($historyStore.total / $historyStore.pageSize)}
        ({$historyStore.notifications.length} of {$historyStore.total})
      </span>

      <button
        on:click={handleNextPage}
        disabled={(selectedPage + 1) * $historyStore.pageSize >= $historyStore.total}
        class="btn-secondary"
      >
        Next →
      </button>
    </div>
  {/if}

  <!-- Error -->
  {#if $historyStore.error}
    <div class="error">Error: {$historyStore.error}</div>
  {/if}

  <!-- Export Modal -->
  {#if showExportModal}
    <ExportModal
      onClose={() => (showExportModal = false)}
      {historyStore}
    />
  {/if}
</div>

<style>
  .notification-history {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    background: #0a0e27;
    border-radius: 8px;
    color: #e2e8f0;
  }

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .history-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .stats-bar {
    display: flex;
    gap: 1rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    font-size: 0.875rem;
  }

  .stat {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .stat .label {
    color: #94a3b8;
    text-transform: capitalize;
  }

  .stat .value {
    font-weight: 600;
    color: #60a5fa;
  }

  .stat .value.success {
    color: #10b981;
  }
  .stat .value.warning {
    color: #f59e0b;
  }
  .stat .value.error {
    color: #ef4444;
  }
  .stat .value.info {
    color: #3b82f6;
  }

  .search-controls {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .search-input,
  .type-filter {
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    color: #e2e8f0;
    font-size: 0.875rem;
  }

  .search-input {
    flex: 1;
    min-width: 200px;
  }

  .search-input::placeholder {
    color: #64748b;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 400px;
    overflow-y: auto;
    padding: 0.5rem 0;
  }

  .loading,
  .empty {
    padding: 2rem;
    text-align: center;
    color: #94a3b8;
  }

  .pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .page-info {
    font-size: 0.875rem;
    color: #94a3b8;
  }

  .error {
    padding: 0.75rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 4px;
    color: #fca5a5;
    font-size: 0.875rem;
  }

  .btn-primary,
  .btn-secondary,
  .btn-danger {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-primary:hover {
    background: #2563eb;
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
  }

  .btn-secondary:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-danger {
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
  }

  .btn-danger:hover {
    background: rgba(239, 68, 68, 0.3);
  }
</style>

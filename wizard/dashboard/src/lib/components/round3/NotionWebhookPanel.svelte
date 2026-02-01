<script lang="ts">
  import { onMount } from "svelte";
  import {
    fetchNotionPendingSyncs,
    fetchNotionSyncStatus,
    triggerNotionManualSync,
  } from "$lib/services/notionService";
  import type { NotionPendingItem } from "$lib/services/notionService";

  export let onManualSync: (result: string) => void = () => {};

  let syncStatus = {
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
  };
  let pendingItems: NotionPendingItem[] = [];
  let loadingStatus = false;
  let loadingPending = false;
  let manualMessage = "";
  let manualInFlight = false;

  const fields = [
    { key: "pending", label: "Pending" },
    { key: "processing", label: "Processing" },
    { key: "completed", label: "Completed" },
    { key: "failed", label: "Failed" },
  ];

  onMount(() => {
    refreshAll();
  });

  async function refreshAll() {
    await Promise.all([loadStatus(), loadPending()]);
  }

  async function loadStatus() {
    loadingStatus = true;
    try {
      const data = await fetchNotionSyncStatus();
      syncStatus = {
        total: data.total ?? 0,
        pending: data.pending ?? 0,
        processing: data.processing ?? 0,
        completed: data.completed ?? 0,
        failed: data.failed ?? 0,
      };
    } catch (err) {
      console.error("Failed to load sync status", err);
    } finally {
      loadingStatus = false;
    }
  }

  async function loadPending() {
    loadingPending = true;
    try {
      pendingItems = await fetchNotionPendingSyncs({ limit: 8 });
    } catch (err) {
      console.error("Failed to load pending items", err);
    } finally {
      loadingPending = false;
    }
  }

  async function handleManualSync(event: MouseEvent) {
    event.preventDefault();
    manualInFlight = true;
    manualMessage = "Triggering manual sync…";
    try {
      const result = await triggerNotionManualSync();
      manualMessage = result?.result || "Manual sync triggered";
      onManualSync(manualMessage);
      await refreshAll();
    } catch (err) {
      manualMessage = err instanceof Error ? err.message : "Manual sync failed";
    } finally {
      manualInFlight = false;
    }
  }

  function formatTimestamp(value?: string | null) {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleString();
    } catch (err) {
      return value;
    }
  }
</script>

<section class="webhook-panel">
  <header>
    <div>
      <p class="eyebrow">Round 3 • Notion Webhooks</p>
      <h2>Sync status & queue</h2>
      <p class="muted">Ranges from the Notion webhook queue feed (pending, processing, completed, failed) so Round 3 gets real telemetry.</p>
    </div>
    <div class="header-actions">
      <button class="manual" on:click={handleManualSync} disabled={manualInFlight}>
        {manualInFlight ? "Syncing…" : "Trigger manual sync"}
      </button>
      <button class="ghost" on:click={refreshAll}>
        Refresh status
      </button>
    </div>
  </header>

  {#if manualMessage}
    <div class="manual-message">{manualMessage}</div>
  {/if}

  <div class="summary-grid">
    {#if loadingStatus}
      <div class="summary-placeholder">Loading status…</div>
    {:else}
      {#each fields as field}
        <article class="summary-card">
          <p>{field.label}</p>
          <strong>{syncStatus[field.key] ?? 0}</strong>
        </article>
      {/each}
      <article class="summary-card total" title="Total webhook events">
        <p>Total</p>
        <strong>{syncStatus.total}</strong>
      </article>
    {/if}
  </div>

  <div class="list">
    <div class="list-header">
      <span>Pending webhook queue</span>
      <button class="ghost" on:click={loadPending}>Refresh queue</button>
    </div>
    {#if loadingPending}
      <div class="empty-state">Loading queue…</div>
    {:else if pendingItems.length === 0}
      <div class="empty-state">No pending webhook entries.</div>
    {:else}
      {#each pendingItems as item}
        <article class="webhook-row">
          <div>
            <p class="name">{item.block_type ?? "block"}</p>
            <p class="meta">ID: {item.notion_block_id ?? "unknown"} · {item.action ?? "update"}</p>
          </div>
          <div class="controls">
            <span class={`status ${item.status ?? "pending"}`}>{(item.status ?? "pending").toUpperCase()}</span>
            <span class="timestamp">{formatTimestamp(item.created_at)}</span>
          </div>
        </article>
      {/each}
    {/if}
  </div>
</section>

<style>
  .webhook-panel {
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 1rem;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 0;
  }

  h2 {
    margin: 0.2rem 0;
    font-size: 1.4rem;
  }

  .muted {
    margin: 0;
    color: #94a3b8;
    font-size: 0.85rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  button {
    border: none;
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
  }

  .manual {
    background: #34d399;
    color: #0f172a;
  }

  .ghost {
    background: rgba(148, 163, 184, 0.15);
    color: #e5e7eb;
  }

  .manual-message {
    font-size: 0.85rem;
    color: #dbeafe;
    background: rgba(59, 130, 246, 0.15);
    padding: 0.45rem 0.9rem;
    border-radius: 0.65rem;
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .summary-card {
    border-radius: 0.75rem;
    padding: 0.85rem;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.2);
    text-align: center;
  }

  .summary-card p {
    margin: 0;
    font-size: 0.8rem;
    color: #94a3b8;
  }

  .summary-card strong {
    font-size: 1.6rem;
    display: block;
    margin-top: 0.2rem;
  }

  .summary-card.total {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
  }

  .summary-placeholder {
    padding: 1rem;
    text-align: center;
    color: #94a3b8;
  }

  .list {
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.9rem;
    background: rgba(15, 23, 42, 0.6);
    padding: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: #94a3b8;
  }

  .empty-state {
    text-align: center;
    color: #94a3b8;
    padding: 0.5rem 0;
  }

  .webhook-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0.8rem;
    border-radius: 0.7rem;
    background: rgba(15, 23, 42, 0.7);
  }

  .webhook-row .name {
    margin: 0;
    font-weight: 600;
  }

  .meta {
    margin: 0;
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .controls {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.2rem;
  }

  .status {
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
  }

  .status.pending {
    background: #f97316;
    color: #fff;
  }

  .status.processing {
    background: #2563eb;
    color: #fff;
  }

  .status.completed {
    background: #22c55e;
    color: #0f172a;
  }

  .status.failed {
    background: #dc2626;
    color: #fff;
  }

  .timestamp {
    font-size: 0.7rem;
    color: #94a3b8;
  }
</style>

<script lang="ts">
  import { onMount } from "svelte";
  import { fetchNotionBlockMaps } from "$lib/services/notionService";
  import { setSlotMapping } from "$lib/stores/mappingStore";
  import type { NotionBlockMap } from "$lib/services/notionService";

  const runtimeSlots = [
    "FORM",
    "STATE",
    "NAV",
    "PANEL",
    "MAP",
    "SET",
    "IF",
  ];

  let notionBlocks: NotionBlockMap[] = [];
  let loading = false;
  let error = "";
  let selectedBlock: NotionBlockMap | null = null;
  let mappings: Record<string, string> = {};
  let mappingNotes: Record<string, string> = {};
  let noteDraft = "";
  let draggedBlockId: string | null = null;
  let dragOverSlot: string | null = null;

  const instructions =
    "Drag a Notion block onto a runtime slot to map it, then add mapping notes to explain the transformation.";

  onMount(() => {
    loadBlocks();
  });

  async function loadBlocks() {
    loading = true;
    error = "";
    try {
      const data = await fetchNotionBlockMaps({ limit: 12 });
      notionBlocks = data;
      selectedBlock = notionBlocks[0] ?? null;
    } catch (exc) {
      error = exc instanceof Error ? exc.message : "Unable to fetch Notion blocks.";
    } finally {
      loading = false;
    }
  }

  function handleDragStart(block: NotionBlockMap) {
    draggedBlockId = block.notion_block_id;
  }

  function handleDragEnd() {
    draggedBlockId = null;
  }

  function handleSlotDrop(slot: string) {
    if (!draggedBlockId) return;
    mappings = { ...mappings, [slot]: draggedBlockId };
    const block = notionBlocks.find((entry) => entry.notion_block_id === draggedBlockId);
    if (block) {
      selectedBlock = block;
    }
    draggedBlockId = null;
    dragOverSlot = null;
  }

  function handleSlotDragOver(slot: string, event: DragEvent) {
    event.preventDefault();
    dragOverSlot = slot;
  }

  function handleSlotDragLeave() {
    dragOverSlot = null;
  }

  function handleBlockClick(block: NotionBlockMap) {
    selectedBlock = block;
  }

  function getSlotBlock(slot: string) {
    const blockId = mappings[slot];
    return notionBlocks.find((block) => block.notion_block_id === blockId) ?? null;
  }

  function handleNoteInput(event: Event) {
    if (!selectedBlock) return;
    const value = (event.target as HTMLTextAreaElement).value;
    noteDraft = value;
    mappingNotes = { ...mappingNotes, [selectedBlock.notion_block_id]: value };
  }

  function saveMapping() {
    if (!selectedBlock) return;
    const slot = Object.keys(mappings).find(
      (key) => mappings[key] === selectedBlock.notion_block_id,
    );
    console.log("Saving mapping", {
      blockId: selectedBlock.notion_block_id,
      note: noteDraft,
      slot,
    });
    if (slot) {
      setSlotMapping({
        slot,
        blockId: selectedBlock.notion_block_id,
        note: noteDraft,
        payloadPreview: selectedBlock.payload_preview ?? "",
        blockType: selectedBlock.block_type,
        runtimeType: selectedBlock.runtime_type,
      });
    }
  }

  $: if (selectedBlock) {
    const stored = mappingNotes[selectedBlock.notion_block_id];
    if (stored !== undefined && stored !== noteDraft) {
      noteDraft = stored;
    }
  } else if (noteDraft !== "") {
    noteDraft = "";
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

<div class="notion-block-renderer">
  <header>
    <div>
      <h2>Round 3 Block Mapper</h2>
      <p class="muted">{instructions}</p>
    </div>
    <div class="actions">
      <button class="refresh" on:click={loadBlocks} disabled={loading}>
        {loading ? "Refreshing…" : "Refresh blocks"}
      </button>
    </div>
  </header>

  <div class="content">
    <div class="blocks-panel">
      <div class="panel-header">
        <span>Live Notion block snapshots</span>
        <span class="count">{notionBlocks.length} tracked</span>
      </div>
      {#if loading}
        <div class="empty-state">Loading Notion blocks…</div>
      {:else if error}
        <div class="empty-state error">{error}</div>
      {:else if notionBlocks.length === 0}
        <div class="empty-state">No blocks available yet.</div>
      {:else}
        <div class="block-stack">
          {#each notionBlocks as block}
            <article
              class={`block-item ${selectedBlock?.notion_block_id === block.notion_block_id ? "active" : ""}`}
              draggable
              on:dragstart={() => handleDragStart(block)}
              on:dragend={handleDragEnd}
              on:click={() => handleBlockClick(block)}
            >
              <div class="block-meta">
                <span class="label">{block.block_type ?? "block"}</span>
                <span class="runtime">{block.runtime_type ?? "runtime: unknown"}</span>
              </div>
              <p class="preview">{block.payload_preview || "No preview available."}</p>
              <div class="timestamps">
                <span>Created: {formatTimestamp(block.created_at)}</span>
                <span>Synced: {formatTimestamp(block.last_synced)}</span>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </div>

    <div class="mapper-panel">
      <div class="panel-header">
        <span>Runtime mapping slots</span>
        <span class="count">Drag a block onto a slot to assign it.</span>
      </div>
      <div class="slots">
        {#each runtimeSlots as slot}
          <div
            class={`slot ${dragOverSlot === slot ? "drag-over" : ""}`}
            on:dragover={(event) => handleSlotDragOver(slot, event)}
            on:dragleave={handleSlotDragLeave}
            on:drop|preventDefault={() => handleSlotDrop(slot)}
          >
            <div class="slot-title">
              <strong>{slot}</strong>
              <span>{getSlotBlock(slot)?.status ?? "waiting"}</span>
            </div>
            {#if getSlotBlock(slot)}
              <p class="slot-preview">{getSlotBlock(slot)?.payload_preview}</p>
            {:else}
              <p class="slot-empty">Drop block here</p>
            {/if}
          </div>
        {/each}
      </div>

      <section class="mapper-form">
        <header>
          <h3>Mapping notes</h3>
        </header>
        {#if selectedBlock}
          <div class="form-info">
            <p><strong>Block ID:</strong> {selectedBlock.notion_block_id}</p>
            <p><strong>Slot:</strong> {Object.keys(mappings).find((key) => mappings[key] === selectedBlock.notion_block_id) ?? "unmapped"}</p>
          </div>
          <label>
            <span>Explain what this block controls:</span>
            <textarea
              rows="3"
              bind:value={noteDraft}
              on:input={handleNoteInput}
              placeholder="Describe the uDOS runtime expectation"
            />
          </label>
          <button class="save" on:click={saveMapping}>Record mapping</button>
        {:else}
          <p class="empty-state">Select or drop a block to capture mapping notes.</p>
        {/if}
      </section>
    </div>
  </div>
</div>

<style>
  :global(:root) {
    --card-bg: #0f172a;
    --card-border: #1f2937;
  }

  .notion-block-renderer {
    border: 1px solid var(--card-border);
    border-radius: 1.25rem;
    padding: 1.5rem;
    background: var(--card-bg);
    color: #e5e7eb;
    box-shadow: 0 20px 60px rgba(15, 23, 42, 0.8);
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    gap: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 1.35rem;
  }

  .muted {
    margin: 0.2rem 0 0;
    color: #94a3b8;
    font-size: 0.85rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .refresh {
    border-radius: 999px;
    border: none;
    padding: 0.4rem 1rem;
    background: #22c55e;
    color: #0f172a;
    font-weight: 600;
    cursor: pointer;
  }

  .content {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .blocks-panel,
  .mapper-panel {
    flex: 1 1 320px;
    min-width: 320px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 1rem;
    background: rgba(15, 23, 42, 0.65);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #94a3b8;
  }

  .count {
    font-weight: 600;
  }

  .block-stack {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    max-height: 400px;
    overflow: auto;
  }

  .block-item {
    padding: 0.9rem;
    border-radius: 0.75rem;
    border: 1px dashed rgba(148, 163, 184, 0.4);
    background: rgba(15, 23, 42, 0.85);
    cursor: grab;
  }

  .block-item.active {
    border-color: #38bdf8;
    box-shadow: 0 10px 25px rgba(14, 165, 233, 0.25);
  }

  .block-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #cbd5f5;
    margin-bottom: 0.45rem;
  }

  .preview {
    margin: 0;
    font-size: 0.9rem;
    color: #e5e7eb;
  }

  .timestamps {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 0.45rem;
  }

  .empty-state {
    border: 1px dashed rgba(255, 255, 255, 0.2);
    border-radius: 0.75rem;
    padding: 1rem;
    text-align: center;
    color: #94a3b8;
  }

  .empty-state.error {
    border-color: rgba(239, 68, 68, 0.5);
    color: #f87171;
  }

  .slots {
    display: grid;
    gap: 0.6rem;
  }

  .slot {
    border: 1px dashed rgba(148, 163, 184, 0.4);
    border-radius: 0.75rem;
    padding: 0.85rem;
    min-height: 90px;
    background: rgba(15, 23, 42, 0.6);
  }

  .slot.drag-over {
    border-color: #38bdf8;
    background: rgba(56, 189, 248, 0.1);
  }

  .slot-title {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #cbd5f5;
    margin-bottom: 0.35rem;
  }

  .slot-preview {
    margin: 0;
    font-size: 0.85rem;
    color: #e5e7eb;
  }

  .slot-empty {
    margin: 0;
    font-size: 0.8rem;
    color: #94a3b8;
  }

  .mapper-form {
    border-top: 1px solid rgba(148, 163, 184, 0.2);
    padding-top: 0.7rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-info {
    display: flex;
    flex-direction: column;
    font-size: 0.8rem;
    gap: 0.15rem;
    color: #cbd5f5;
  }

  label {
    font-size: 0.8rem;
    color: #94a3b8;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  textarea {
    border-radius: 0.65rem;
    border: 1px solid rgba(148, 163, 184, 0.4);
    padding: 0.6rem;
    background: rgba(15, 23, 42, 0.8);
    color: #e5e7eb;
    font-family: inherit;
  }

  .save {
    width: fit-content;
    border-radius: 1rem;
    border: none;
    padding: 0.45rem 1.1rem;
    background: #f97316;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
  }

  @media (max-width: 960px) {
    .content {
      flex-direction: column;
    }
  }
</style>

<script>
  export let onLink = (tile1, tile2) => {};
  export let selectedTiles = [];
</script>

<div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155;">
  <h3 style="color: #cbd5e1; margin: 0 0 8px 0; font-size: 14px;">Tile Linker</h3>
  <div style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">
    Select tiles to create links between them
  </div>
  {#if selectedTiles.length === 0}
    <div style="color: #64748b; font-size: 12px;">No tiles selected</div>
  {:else if selectedTiles.length === 1}
    <div style="color: #3b82f6; font-size: 12px;">1 tile selected - select another to link</div>
  {:else}
    <button
      on:click={() => onLink(selectedTiles[0], selectedTiles[1])}
      style="padding: 6px 12px; background: #22c55e; color: white; border: none; border-radius: 2px; cursor: pointer; font-size: 12px;"
    >
      Create Link
    </button>
  {/if}
</div>

<script>
  export let layers = [];
  export let onSelectLayer = (id) => {};
  export let onToggleVisibility = (id) => {};
  export let onDeleteLayer = (id) => {};
  export let onAddLayer = () => {};
</script>

<div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <h3 style="color: #cbd5e1; margin: 0; font-size: 14px;">Layers</h3>
    <button
      on:click={onAddLayer}
      style="padding: 4px 8px; background: #3b82f6; color: white; border: none; border-radius: 2px; cursor: pointer; font-size: 12px;"
    >
      + Add
    </button>
  </div>
  <div style="max-height: 400px; overflow-y: auto;">
    {#each layers as layer (layer.id)}
      <div style="background: #0f172a; padding: 8px; margin-bottom: 4px; border-radius: 2px; display: flex; justify-content: space-between; align-items: center;">
        <button
          on:click={() => onSelectLayer(layer.id)}
          style="flex: 1; text-align: left; background: none; border: none; color: #e2e8f0; cursor: pointer; padding: 0; font-size: 13px;"
        >
          {layer.name}
        </button>
        <div style="display: flex; gap: 4px;">
          <button
            on:click={() => onToggleVisibility(layer.id)}
            style="padding: 2px 6px; background: {layer.visible ? '#22c55e' : '#64748b'}; color: white; border: none; border-radius: 2px; cursor: pointer; font-size: 11px;"
          >
            {layer.visible ? '👁' : '🚫'}
          </button>
          <button
            on:click={() => onDeleteLayer(layer.id)}
            style="padding: 2px 6px; background: #ef4444; color: white; border: none; border-radius: 2px; cursor: pointer; font-size: 11px;"
          >
            🗑
          </button>
        </div>
      </div>
    {/each}
  </div>
</div>

<script>
  /**
   * LayerPanel - Layer management sidebar
   * Create, delete, reorder, and configure layers
   */

  let {
    document,
    onAddLayer,
    onRemoveLayer,
    onDuplicateLayer,
    onSelectLayer,
    onMoveLayer,
    onToggleVisibility,
    onToggleLock,
    onRenameLayer,
    onUpdateOpacity,
  } = $props();

  let editingLayerId = $state(null);
  let editingName = $state("");

  const startRename = (layer) => {
    editingLayerId = layer.id;
    editingName = layer.name;
  };

  const finishRename = () => {
    if (editingLayerId && editingName.trim()) {
      onRenameLayer(editingLayerId, editingName.trim());
    }
    editingLayerId = null;
    editingName = "";
  };

  const cancelRename = () => {
    editingLayerId = null;
    editingName = "";
  };

  const handleKeydown = (e) => {
    if (e.key === "Enter") {
      finishRename();
    } else if (e.key === "Escape") {
      cancelRename();
    }
  };

  // Get layer index for move buttons
  const getLayerIndex = (layerId) => {
    return document.layers.findIndex((l) => l.id === layerId);
  };

  const canMoveUp = (layerId) => {
    return getLayerIndex(layerId) > 0;
  };

  const canMoveDown = (layerId) => {
    const index = getLayerIndex(layerId);
    return index >= 0 && index < document.layers.length - 1;
  };
</script>

<div class="layer-panel">
  <div class="panel-header">
    <h3>Layers</h3>
    <button class="btn-icon" onclick={onAddLayer} title="Add Layer">
      ➕
    </button>
  </div>

  <div class="layer-list">
    {#each [...document.layers].reverse() as layer (layer.id)}
      {@const isActive = layer.id === document.activeLayerId}
      {@const index = getLayerIndex(layer.id)}
      <div class="layer-item" class:active={isActive}>
        <!-- Layer controls -->
        <div class="layer-controls">
          <button
            class="btn-icon-sm"
            class:visible={layer.visible}
            class:hidden={!layer.visible}
            onclick={() => onToggleVisibility(layer.id)}
            title={layer.visible ? "Hide Layer" : "Show Layer"}
          >
            {#if layer.visible}
              👁️
            {:else}
              🚫
            {/if}
          </button>

          <button
            class="btn-icon-sm"
            class:locked={layer.locked}
            onclick={() => onToggleLock(layer.id)}
            title={layer.locked ? "Unlock Layer" : "Lock Layer"}
          >
            {#if layer.locked}
              🔒
            {:else}
              🔓
            {/if}
          </button>
        </div>

        <!-- Layer name -->
        <button class="layer-info" onclick={() => onSelectLayer(layer.id)}>
          {#if editingLayerId === layer.id}
            <input
              type="text"
              class="layer-name-input"
              bind:value={editingName}
              onblur={finishRename}
              onkeydown={handleKeydown}
            />
          {:else}
            <span
              class="layer-name"
              ondblclick={() => startRename(layer)}
              role="button"
              tabindex="0"
            >
              {layer.name}
            </span>
          {/if}
          <div class="layer-meta">
            {layer.width}×{layer.height} • Z: {layer.zIndex}
            {#if !layer.visible}
              <span class="badge">Hidden</span>
            {/if}
            {#if layer.locked}
              <span class="badge">Locked</span>
            {/if}
          </div>
        </button>

        <!-- Move buttons -->
        <div class="layer-actions">
          <button
            class="btn-icon-sm"
            onclick={() => onMoveLayer(layer.id, "up")}
            disabled={!canMoveUp(layer.id)}
            title="Move Up"
          >
            ⬆️
          </button>
          <button
            class="btn-icon-sm"
            onclick={() => onMoveLayer(layer.id, "down")}
            disabled={!canMoveDown(layer.id)}
            title="Move Down"
          >
            ⬇️
          </button>
        </div>

        <!-- More actions -->
        <div class="layer-menu">
          <button
            class="btn-icon-sm"
            onclick={() => onDuplicateLayer(layer.id)}
            title="Duplicate Layer"
          >
            📋
          </button>
          <button
            class="btn-icon-sm btn-danger"
            onclick={() => onRemoveLayer(layer.id)}
            disabled={document.layers.length === 1}
            title="Delete Layer"
          >
            🗑️
          </button>
        </div>

        <!-- Opacity slider -->
        {#if isActive}
          <div class="opacity-control">
            <label>
              Opacity: {Math.round(layer.opacity * 100)}%
              <input
                type="range"
                min="0"
                max="100"
                value={layer.opacity * 100}
                oninput={(e) =>
                  onUpdateOpacity(
                    layer.id,
                    Number(e.currentTarget.value) / 100
                  )}
              />
            </label>
          </div>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .layer-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--panel-bg, #1f2937);
    border-right: 1px solid var(--border-color, #374151);
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    border-bottom: 1px solid var(--border-color, #374151);
  }

  .panel-header h3 {
    margin: 0;
    font-weight: 600;
    color: var(--text-primary, #f9fafb);
  }

  .layer-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .layer-item {
    background-color: var(--item-bg, #374151);
    border: 1px solid var(--border-color, #4b5563);
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .layer-item:hover {
    background-color: var(--item-hover, #4b5563);
  }

  .layer-item.active {
    background-color: var(--item-active, #3b82f6);
    border-color: var(--item-active-border, #2563eb);
  }

  .layer-controls {
    display: flex;
    gap: 4px;
    margin-bottom: 6px;
  }

  .layer-info {
    margin-bottom: 6px;
    cursor: pointer;
  }

  .layer-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary, #f9fafb);
    margin-bottom: 2px;
  }

  .layer-name-input {
    width: 100%;
    padding: 2px 4px;
    background-color: var(--input-bg, #1f2937);
    border: 1px solid var(--border-color, #6b7280);
    border-radius: 2px;
    color: var(--text-primary, #f9fafb);
  }

  .layer-meta {
    font-size: 11px;
    color: var(--text-secondary, #9ca3af);
  }

  .badge {
    display: inline-block;
    padding: 1px 4px;
    background-color: var(--badge-bg, #6b7280);
    border-radius: 2px;
    margin-left: 4px;
  }

  .layer-actions {
    display: flex;
    gap: 4px;
    margin-bottom: 6px;
  }

  .layer-menu {
    display: flex;
    gap: 4px;
  }

  .opacity-control {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border-color, #4b5563);
  }

  .opacity-control label {
    display: block;
    color: var(--text-secondary, #9ca3af);
  }

  .opacity-control input[type="range"] {
    width: 100%;
    margin-top: 4px;
  }

  .btn-icon,
  .btn-icon-sm {
    padding: 4px;
    background: transparent;
    border: none;
    cursor: pointer;
    color: var(--icon-color, #9ca3af);
    transition: color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-icon:hover,
  .btn-icon-sm:hover {
    color: var(--icon-hover, #f9fafb);
  }

  .btn-icon:disabled,
  .btn-icon-sm:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .btn-icon-sm {
    padding: 2px;
  }

  .btn-danger:hover {
    color: var(--danger, #ef4444);
  }

  .btn-icon-sm.visible {
    color: var(--success, #10b981);
  }

  .btn-icon-sm.hidden {
    color: var(--text-secondary, #6b7280);
  }

  .btn-icon-sm.locked {
    color: var(--warning, #f59e0b);
  }

  /* Dark mode */
  :global(.dark) .layer-panel {
    --panel-bg: #0f172a;
    --border-color: #1e293b;
    --item-bg: #1e293b;
    --item-hover: #334155;
    --item-active: #3b82f6;
    --item-active-border: #2563eb;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --input-bg: #0f172a;
    --badge-bg: #475569;
    --icon-color: #94a3b8;
    --icon-hover: #f1f5f9;
    --success: #22c55e;
    --warning: #eab308;
    --danger: #ef4444;
  }
</style>

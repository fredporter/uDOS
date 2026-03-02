<script>
  export let onSelectFg = (color) => {};
  export let onSelectBg = (color) => {};

  const colors = [
    '#000000', '#1e293b', '#334155', '#475569', '#64748b', '#94a3b8', '#cbd5e1', '#e2e8f0', '#f1f5f9', '#ffffff',
    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e'
  ];
</script>

<div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155;">
  <h3 style="color: #cbd5e1; margin: 0 0 8px 0; font-size: 14px;">Color Palette</h3>
  <div style="margin-bottom: 12px;">
    <div style="color: #94a3b8; font-size: 12px; display: block; margin-bottom: 4px;">Foreground</div>
    <div style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px;">
      {#each colors as color}
        <button
          on:click={() => onSelectFg(color)}
          style="width: 28px; height: 28px; background: {color}; border: 1px solid #334155; border-radius: 2px; cursor: pointer;"
          title={color}
        ></button>
      {/each}
    </div>
  </div>
  <div>
    <div style="color: #94a3b8; font-size: 12px; display: block; margin-bottom: 4px;">Background</div>
    <div style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px;">
      {#each colors as color}
        <button
          on:click={() => onSelectBg(color)}
          style="width: 28px; height: 28px; background: {color}; border: 1px solid #334155; border-radius: 2px; cursor: pointer;"
          title={color}
        ></button>
      {/each}
    </div>
  </div>
</div>

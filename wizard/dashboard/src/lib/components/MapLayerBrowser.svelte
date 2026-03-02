<script>
  import { onMount } from 'svelte';

  export let onSelectMap = (mapId) => {};

  let maps = [];
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch('/api/map/list');
      if (res.ok) {
        const data = await res.json();
        maps = data.maps || [];
      }
    } catch (err) {
      console.error('Failed to load maps:', err);
    } finally {
      loading = false;
    }
  });
</script>

<div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155;">
  <h3 style="color: #cbd5e1; margin: 0 0 8px 0; font-size: 14px;">Map Browser</h3>
  {#if loading}
    <div style="color: #94a3b8; font-size: 12px;">Loading maps...</div>
  {:else if maps.length === 0}
    <div style="color: #64748b; font-size: 12px;">No maps available</div>
  {:else}
    <div style="max-height: 300px; overflow-y: auto;">
      {#each maps as map}
        <button
          on:click={() => onSelectMap(map.id)}
          style="width: 100%; padding: 8px; background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 2px; cursor: pointer; text-align: left; margin-bottom: 4px; hover: background: #334155;"
        >
          <div style="font-weight: 500;">{map.name}</div>
          <div style="font-size: 11px; color: #94a3b8;">{map.width}x{map.height}</div>
        </button>
      {/each}
    </div>
  {/if}
</div>

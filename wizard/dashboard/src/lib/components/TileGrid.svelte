<script>
  export let tiles = [];
  export let width = 80;
  export let height = 24;
</script>

<div style="background: #000000; color: #00ff00; font-family: monospace; padding: 12px; border-radius: 4px; overflow-x: auto;">
  {#each Array(height) as _, y}
    <div style="height: 1.2em;">
      {#each Array(width) as _, x}
        {@const tile = tiles.find((t) => t.x === x && t.y === y)}
        <span style="color: {tile?.fg || '#00ff00'};white-space: pre;">{tile?.char || ' '}</span>
      {/each}
    </div>
  {/each}
</div>

<script>
  import { onMount } from "svelte";

  export let logs = [];
  export let autoScroll = true;
  export let height = "400px";
  // Note: categories export available for filtering (not currently used in template)

  let container;

  onMount(() => {
    if (autoScroll && container) {
      container.scrollTop = container.scrollHeight;
    }
  });

  $: if (autoScroll && container && logs.length) {
    setTimeout(() => {
      if (container) container.scrollTop = container.scrollHeight;
    }, 0);
  }
</script>

<div
  bind:this={container}
  style="height: {height}; overflow-y: auto; background: #0f172a; border: 1px solid #334155; border-radius: 4px; padding: 12px; font-family: monospace; font-size: 12px;"
>
  {#if logs.length === 0}
    <div style="color: #64748b; text-align: center; padding-top: 20px;">No logs yet</div>
  {:else}
    {#each logs as log}
      <div style="color: {log.level === 'ERROR' ? '#ef4444' : log.level === 'WARN' ? '#f59e0b' : '#94a3b8'}; margin-bottom: 4px;">
        <span style="color: #64748b;">[{log.timestamp}]</span>
        <span>{log.category}</span>
        <span>{log.message}</span>
      </div>
    {/each}
  {/if}
</div>

<style>
  div {
    font-family: var(--font-code, "Fira Code", monospace);
  }
</style>

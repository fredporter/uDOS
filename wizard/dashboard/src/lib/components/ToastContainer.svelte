<script>
  export let logs = [];
</script>

<div style="background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 4px;">
  <div style="margin-bottom: 12px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto;">
    {#each logs as log}
      <div style="color: {log.level === 'ERROR' ? '#ef4444' : '#cbd5e1'}; margin-bottom: 4px;">
        {log.message}
      </div>
    {/each}
  </div>
  <input type="text" placeholder="Enter command..." style="width: 100%; padding: 8px; background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 4px;" />
</div>

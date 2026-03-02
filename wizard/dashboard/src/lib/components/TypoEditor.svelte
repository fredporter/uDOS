<script>
  export let value = "";
  export let onSave = () => {};
</script>

<div style="background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 4px;">
  <textarea bind:value style="width: 100%; height: 200px; background: #0f172a; color: #e2e8f0; border: 1px solid #334155; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 12px;"></textarea>
  <button on:click={onSave} style="margin-top: 8px; padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">Save</button>
</div>

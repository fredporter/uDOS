<script>
  export let label = "";
  export let variant = "default"; // "default" | "success" | "error" | "warning"
  export let onClick = undefined;

  const variantStyles = {
    default: "background: #334155; color: #cbd5e1;",
    success: "background: #22c55e; color: white;",
    error: "background: #ef4444; color: white;",
    warning: "background: #f59e0b; color: white;"
  };

  const style = variantStyles[variant] || variantStyles.default;
</script>

{#if onClick}
  <button
    on:click={onClick}
    style="{style} padding: 4px 8px; border: none; border-radius: 2px; cursor: pointer; font-size: 12px; font-family: monospace;"
  >
    {label}
  </button>
{:else}
  <span
    style="{style} padding: 4px 8px; border-radius: 2px; font-size: 12px; font-family: monospace; display: inline-block;"
  >
    {label}
  </span>
{/if}

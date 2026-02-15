<script>
  export let className = "";
</script>

<span class={`wiz-terminal-chip terminal-chip ${className}`.trim()}>
  <slot />
</span>

<style>
  .terminal-chip {
    font-family: var(--mdk-font-code);
    letter-spacing: 0.03em;
  }
</style>

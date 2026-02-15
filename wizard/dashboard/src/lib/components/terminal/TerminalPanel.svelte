<script>
  export let title = "";
  export let subtitle = "";
  export let className = "";
</script>

<section class={`wiz-terminal-panel terminal-panel ${className}`.trim()}>
  {#if title || subtitle}
    <header class="terminal-panel__header">
      <div>
        {#if title}
          <h3 class="terminal-panel__title">{title}</h3>
        {/if}
        {#if subtitle}
          <p class="terminal-panel__subtitle">{subtitle}</p>
        {/if}
      </div>
      <slot name="header-actions" />
    </header>
  {/if}
  <div class="terminal-panel__body">
    <slot />
  </div>
</section>

<style>
  .terminal-panel {
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }

  .terminal-panel__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.85rem 1rem;
    border-bottom: 1px solid var(--wiz-terminal-border);
  }

  .terminal-panel__title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--wiz-terminal-text);
    margin: 0;
  }

  .terminal-panel__subtitle {
    font-size: 0.75rem;
    color: var(--wiz-terminal-text-dim);
    margin: 0.2rem 0 0;
  }

  .terminal-panel__body {
    padding: 0.85rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    min-height: 0;
  }
</style>

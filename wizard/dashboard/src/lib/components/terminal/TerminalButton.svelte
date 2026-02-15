<script>
  import { createEventDispatcher } from "svelte";

  export let variant = "neutral";
  export let disabled = false;
  export let type = "button";
  export let className = "";

  const dispatch = createEventDispatcher();

  const variantClasses = {
    neutral: "terminal-btn--neutral",
    accent: "terminal-btn--accent",
    success: "terminal-btn--success",
    danger: "terminal-btn--danger",
  };

  $: variantClass = variantClasses[variant] || variantClasses.neutral;

  function handleClick(event) {
    dispatch("click", event);
  }
</script>

<button
  {type}
  {disabled}
  class={`wiz-terminal-btn terminal-btn ${variantClass} ${className}`.trim()}
  on:click={handleClick}
>
  <slot />
</button>

<style>
  .terminal-btn {
    padding: 0.4rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 600;
    transition: background 120ms ease, border-color 120ms ease;
  }

  .terminal-btn--neutral {
    background: rgba(148, 163, 184, 0.15);
    border-color: rgba(148, 163, 184, 0.3);
    color: var(--wiz-terminal-text);
  }

  .terminal-btn--accent {
    background: rgba(56, 189, 248, 0.18);
    border-color: rgba(56, 189, 248, 0.45);
    color: #e0f2fe;
  }

  .terminal-btn--success {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.45);
    color: #bbf7d0;
  }

  .terminal-btn--danger {
    background: rgba(248, 113, 113, 0.2);
    border-color: rgba(248, 113, 113, 0.45);
    color: #fecaca;
  }
</style>
